"""
gpt0.py — GPT 模型實現

本模組實現簡化版的 GPT-2（Generative Pre-trained Transformer 2）語言模型，
使用純 Python 和自定義自動微分引擎（nn0.py）。

功能說明：
  class Gpt    — GPT 模型（Embedding + Transformer Layers + LM Head）
  train()     — 訓練迴圈
  inference() — 文字生成

數學原理：
  1. Token Embedding + Position Embedding：將離散文字轉為連續向量
  2. Multi-Head Attention：捕捉序列內的依賴關係
  3. MLP：特徵變換和非線性
  4. Cross-Entropy Loss：訓練目標
  5. Temperature Sampling：控制生成多樣性

與 GPT-2 的差異：
  - LayerNorm → RMSNorm：更簡單的正規化
  - GeLU → ReLU：更簡單的激活函數
  - 有 bias → 無 bias：減少參數
"""

import os
import sys
import random

# 讓 import 能找到 nn0.py（位於同目錄）
from nn0 import Value, Adam, linear, softmax, rmsnorm, gd


class Gpt:
    """
    GPT 語言模型

    模型結構：
      1. Token Embedding：將 token ID 轉為向量
      2. Position Embedding：加入位置信息
      3. Transformer Layers：多層 Self-Attention 和 MLP
      4. LM Head：將 hidden state 轉為 vocabulary 的 logits

    這是一個單向語言模型（只關注之前的 token），
    這是 GPT 和雙向 Transformer（如 BERT）的關鍵區別。
    """

    def __init__(self, vocab_size, n_embd=16, n_layer=1, n_head=4, block_size=16):
        """
        建構函數

        參數說明：
          vocab_size: 詞彙表大小，即有多少個不同的 token
          n_embd: Embedding 維度，每個 token 被表示為 n_embd 維向量
          n_layer: Transformer 層數，決定模型深度
          n_head: Attention 頭數，決定模型寬度
          block_size: 最大上下文長度，決定模型能處理的序列長度

        模型大小估算：
          總參數數量取決於這些超參數
          小模型：vocab=256, embd=16, layer=1, head=4 → 幾千參數
          GPT-2 Small：vocab=50257, embd=768, layer=12, head=12 → 1.17 億參數
        """
        # 保存超參數
        self.vocab_size = vocab_size
        self.n_embd = n_embd
        self.n_layer = n_layer
        self.n_head = n_head
        self.block_size = block_size

        # 每個 Attention 頭的維度
        # 必須能整除，所以假設 n_embd 整除 n_head
        self.head_dim = n_embd // n_head

        # 建立並初始化所有參數
        self.state_dict = self._init_params()

        # 將所有參數展平為列表，方便 Adam 優化器使用
        # 注意：這裡需要遍歷所有矩陣的所有元素
        self.params = [p for mat in self.state_dict.values()
                     for row in mat for p in row]

    def _init_params(self, std=0.08):
        """
        初始化所有模型參數

        使用高斯分布初始化：
          w ~ N(0, std^2)

        為何需要初始化？
          - 若全部為 0：對稱問題，所有神經元學習相同
          - 若太大：梯度爆炸
          - 若太小：梯度消失

        參數說明：
          std: 標準差，預設 0.08

        返回說明：
          state_dict: 字典，包含所有權重矩陣
        """
        def matrix(nout, nin):
            """
            建立 nout × nin 的權重矩陣

            返回說明：
              每個元素都是 Value 對象，初始化為高斯分布
            """
            return [[Value(random.gauss(0, std)) for _ in range(nin)]
                    for _ in range(nout)]

        # 建立 state_dict（模型參數存儲）
        sd = {
            # Token Embedding：vocab_size × n_embd
            # 將每個 token ID 映射為 n_embd 維向量
            'wte':     matrix(self.vocab_size, self.n_embd),

            # Position Embedding：block_size × n_embd
            # 將每個位置映射為 n_embd 維向量
            # 注意：可學習的位置編碼，不同於 Transformer 的 Sinusoidal 編碼
            'wpe':     matrix(self.block_size, self.n_embd),

            # Language Model Head：vocab_size × n_embd
            # 將最後的 hidden state 映射回 vocabulary
            # 共享 wte 的權重可以得到更好的效果，但這裡分開
            'lm_head': matrix(self.vocab_size, self.n_embd),
        }

        # 為每層 Transformer 初始化參數
        # 每層包含：
        #   - attn_wq: Query 權重
        #   - attn_wk: Key 權重
        #   - attn_wv: Value 權重
        #   - attn_wo: Attention 輸出權重
        #   - mlp_fc1: MLP 第一層（擴展維度）
        #   - mlp_fc2: MLP 第二層（壓縮維度）
        for i in range(self.n_layer):
            sd[f'layer{i}.attn_wq'] = matrix(self.n_embd, self.n_embd)
            sd[f'layer{i}.attn_wk'] = matrix(self.n_embd, self.n_embd)
            sd[f'layer{i}.attn_wv'] = matrix(self.n_embd, self.n_embd)
            sd[f'layer{i}.attn_wo'] = matrix(self.n_embd, self.n_embd)

            # MLP：先擴展到 4 倍維度，再壓回來
            # 這是 Transformer 的標準設計
            sd[f'layer{i}.mlp_fc1'] = matrix(4 * self.n_embd, self.n_embd)
            sd[f'layer{i}.mlp_fc2'] = matrix(self.n_embd, 4 * self.n_embd)

        return sd

    def forward(self, token_id, pos_id, keys, values):
        """
        單步前向傳播

        給定一個 token 和位置，計算下一個 token 的 logits。

        這是自回歸生成的基礎：每一步只看到之前的 token。

        數學流程：
          1. x = TokenEmb[token_id] + PositionEmb[pos_id]
          2. 對每層 Transformer：
             - x = Attention(x) + x（殘差）
             - x = MLP(x) + x（殘差）
          3. logits = LMHead(x)

        參數說明：
          token_id: 輸入 token 的 ID（int）
          pos_id: 位置 ID（int），從 0 開始
          keys: Key 向量的緩存列表，用於 Causal Attention
          values: Value 向量的緩存列表，用於 Causal Attention

        返回說明：
          logits: 下一個 token 的 logits（list of Value），長度為 vocab_size
        """
        sd = self.state_dict

        # -------------------- 1. Embedding 層 --------------------
        # Token Embedding：將 token ID 轉為向量
        tok_emb = sd['wte'][token_id]

        # Position Embedding：加入位置信息
        pos_emb = sd['wpe'][pos_id]

        # 兩者相加（也可以拼接，但相加更簡單）
        x = [t + p for t, p in zip(tok_emb, pos_emb)]

        # RMS Norm（Pre-LN 結構）
        x = rmsnorm(x)

        # -------------------- 2. Transformer 層 --------------------
        for li in range(self.n_layer):
            # ==================== Multi-Head Attention ====================
            # 殘差連接的輸入（用於後面的相加）
            x_residual = x

            # Pre-LN
            x = rmsnorm(x)

            # 計算 Q, K, V
            # 這是 Self-Attention：Query, Key, Value 都來自同一輸入
            q = linear(x, sd[f'layer{li}.attn_wq'])
            k = linear(x, sd[f'layer{li}.attn_wk'])
            v = linear(x, sd[f'layer{li}.attn_wv'])

            # 存儲 Key 和 Value 到 Cache（用於 Causal Masking）
            # 這樣可以確保每個位置只關注之前的 token
            keys[li].append(k)
            values[li].append(v)

            # ==================== 處理每個 Attention 頭 ====================
            x_attn = []
            for h in range(self.n_head):
                # 計算當前頭的維度範圍
                hs = h * self.head_dim
                q_h = q[hs:hs + self.head_dim]

                # 從 Cache 中獲取之前的 Key 和 Value
                # 注意：這是 Causal Attention，只使用之前的 token
                k_h = [ki[hs:hs + self.head_dim] for ki in keys[li]]
                v_h = [vi[hs:hs + self.head_dim] for vi in values[li]]

                # Scaled Dot-Product Attention
                # attention_logits = (Q @ K^T) / sqrt(d)
                attn_logits = [
                    sum(q_h[j] * k_h[t][j] for j in range(self.head_dim)) / self.head_dim**0.5
                    for t in range(len(k_h))
                ]

                # Softmax 獲得注意力權重
                attn_weights = softmax(attn_logits)

                # 加權求和得到輸出
                # output = attention_weights @ V
                head_out = [
                    sum(attn_weights[t] * v_h[t][j] for t in range(len(v_h)))
                    for j in range(self.head_dim)
                ]

                # 將當前頭的輸出添加到列表
                x_attn.extend(head_out)

            # 線性變換 + 殘差連接
            x = linear(x_attn, sd[f'layer{li}.attn_wo'])
            x = [a + b for a, b in zip(x, x_residual)]

            # ==================== MLP ====================
            # 殘差連接的輸入
            x_residual = x

            # Pre-LN
            x = rmsnorm(x)

            # 第一層：維度擴展
            x = linear(x, sd[f'layer{li}.mlp_fc1'])

            # 激活函數（本實現使用 ReLU，標準 GPT-2 使用 GeLU）
            x = [xi.relu() for xi in x]

            # 第二層：維度壓縮
            x = linear(x, sd[f'layer{li}.mlp_fc2'])

            # 殘差連接
            x = [a + b for a, b in zip(x, x_residual)]

        # -------------------- 3. LM Head --------------------
        # 將 hidden state 映射為 vocabulary 的 logits
        # 這表示下一個 token 的未歸一化概率
        logits = linear(x, sd['lm_head'])

        return logits

    def __call__(self, token_id, pos_id, keys, values):
        """
        調用接口：使模型可以像函數一樣調用

        用法：
          logits = model(token_id, pos_id, keys, values)
        """
        return self.forward(token_id, pos_id, keys, values)


def train(model, optimizer, docs, uchars, BOS, num_steps=1000):
    """
    訓練 GPT 模型

    訓練流程：
      1. 對每個文檔進行 tokenize
      2. 反復執行梯度下降
      3. 輸出 loss 監控訓練進度

    數學原理：
      對於序列 [t0, t1, ..., tn]：
        輸入：t0, t1, ..., t(n-1)
        目標：t1, t2, ..., tn
        Loss = -1/n * Σ log(P(t(i+1) | t0,...,ti))

    參數說明：
      model: GPT 模型实例
      optimizer: Adam 優化器实例
      docs: 文檔列表（list of string）
      uchars: 字符集（list of char）
      BOS: Begin Of String 標記的 ID
      num_steps: 訓練步驟數
    """
    print(f"Training for {num_steps} steps ...")
    for step in range(num_steps):
        # 循環選取文檔
        doc = docs[step % len(docs)]

        # Tokenize：將字符轉為 ID
        # 加入 BOS 標記作為序列開始
        tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]

        # 執行一步梯度下降
        loss_val = gd(model, optimizer, tokens, step, num_steps)

        # 打印進度
        print(f"step {step+1:4d} / {num_steps:4d} | loss {loss_val:.4f}", end='\r')
    print()


def inference(model, uchars, BOS, num_samples=20, temperature=0.5):
    """
    文��生成（推理）

    使用自回歸方式生成文字：
      1. 從 BOS 開始
      2. 每一步：根據當前 token 預測下一個
      3. 使用 Temperature Sampling 控制多樣性
      4. 遇到 BOS 停止

    Temperature 的效果：
      - T = 0：總是選擇最可能的 token（貪心解碼）
      - T = 1：原始分布
      - T > 1：更多樣性，可能不太流暢

    參數說明：
      model: GPT 模型实例
      uchars: 字符集（list of char）
      BOS: Begin Of String 標記的 ID
      num_samples: 生成樣本數
      temperature: 溫度參數，控制多樣性（預設 0.5）
    """
    vocab_size = model.vocab_size
    print(f"--- inference ({num_samples} samples, temperature={temperature}) ---")

    # 生成多個樣本
    for sample_idx in range(num_samples):
        # 初始化 KV Cache（每個樣本都是新的）
        keys   = [[] for _ in range(model.n_layer)]
        values = [[] for _ in range(model.n_layer)]

        # 從 BOS 開始
        token_id = BOS
        sample = []

        # 自回歸生成
        for pos_id in range(model.block_size):
            # 前向傳播，獲取 logits
            logits = model(token_id, pos_id, keys, values)

            # 應用 Temperature：logits / T
            # 較低的溫度使分布更尖銳，較高的溫度使分布更均勻
            probs = softmax([l / temperature for l in logits])

            # 按概率加權隨機選擇下一個 token
            token_id = random.choices(range(vocab_size),
                                      weights=[p.data for p in probs])[0]

            # 遇到 BOS 停止
            if token_id == BOS:
                break

            # 添加到樣本
            sample.append(uchars[token_id])

        # 打印生成的樣本
        print(f"sample {sample_idx+1:2d}: {''.join(sample)}")