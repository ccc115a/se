# Causal Self-Attention — 因果自注意力

## 概述

**Causal Self-Attention（因果自注意力，又稱 Masked Self-Attention 或 Autoregressive Attention）** 是解碼器型 Transformer 中的核心計算單元。與編碼器中的雙向注意力不同，因果自注意力強制每個位置只能關注其之前（包含自身）的 token，不能看到未來的 token。這保證了模型的自迴歸特性 — 預測第 `t+1` 個 token 時只能依賴前 `t` 個 token。mini-llm 專案的所有模型版本都使用因果自注意力。

## 動機：為什麼需要因果遮罩？

語言模型的本質是學習 `P(x₁, x₂, ..., xₙ) = Πₜ P(xₜ | x₁, ..., x_{t-1})`。

如果注意力機制在預測第 `t` 個 token 時可以看到第 `t+1` 個 token，則模型相當於在「偷看答案」— 它會學到使用未來資訊來預測當前 token，而不是真正理解語言的序列結構。這在訓練時會讓 loss 很低，但實際上模型完全無法用於生成（因為生成時沒有未來的 token 可以偷看）。

因果遮罩強制模型在訓練時的行為與推論時一致，這個性質稱為 **Teacher Forcing 的完整性**。

## 注意力機制回顧

Scaled Dot-Product Attention 的計算公式：

```
Attention(Q, K, V) = softmax(QKᵀ / √d) · V
```

其中：
- `Q ∈ ℝ^{T × d}` — Query 矩陣
- `K ∈ ℝ^{T × d}` — Key 矩陣
- `V ∈ ℝ^{T × d}` — Value 矩陣
- `T` — 序列長度
- `d` — 每個注意力頭的維度
- `QKᵀ` — 注意力分數矩陣，形狀為 `T × T`

這個 `T × T` 的注意力矩陣中，位置 `(i, j)` 的值表示第 `i` 個 token 對第 `j` 個 token 的關注程度。

## 因果遮罩的實作

### 三角遮罩（Triangular Mask）

因果注意力在注意力分數矩陣上應用一個**下三角矩陣**：

```
Mask(i, j) = 0     if i ≥ j (可以關注自身及過去)
Mask(i, j) = -∞   if i < j (不能關注未來)
```

應用遮罩後：

```
Attention(Q, K, V) = softmax(QKᵀ / √d + Mask) · V
```

當 `Mask = -∞` 時，softmax 的輸出在對應位置變為 0，因此未來位置的貢獻完全被移除。

### mini-llm 的實作

```python
mask = torch.tril(torch.ones(T, T, device=x.device)).view(1, 1, T, T)
att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
att = att.masked_fill(mask == 0, float('-inf'))
att = F.softmax(att, dim=-1)
```

步驟說明：
1. `torch.tril(torch.ones(T, T))` — 建立下三角全 1 矩陣（下三角為 1，上三角為 0）
2. `.view(1, 1, T, T)` — 擴展維度以匹配批次和注意力頭維度
3. `att.masked_fill(mask == 0, float('-inf'))` — 上三角（未來位置）設為 `-inf`
4. `F.softmax(att, dim=-1)` — softmax 後，`-inf` 位置變為 0，形成因果結構

#### 視覺化

```
注意力分數矩陣 (T=5):

    關注 ↓   關注的 token →
             x₁    x₂    x₃    x₄    x₅
    x₁       [✓]   [-∞]  [-∞]  [-∞]  [-∞]
    x₂       [✓]   [✓]   [-∞]  [-∞]  [-∞]
    x₃       [✓]   [✓]   [✓]   [-∞]  [-∞]
    x₄       [✓]   [✓]   [✓]   [✓]   [-∞]
    x₅       [✓]   [✓]   [✓]   [✓]   [✓]

    其中 ✓ = 允許關注 (i ≥ j)
         -∞ = 禁止關注 (i < j)
```

## 數學性質

### 1. 自迴歸機率的實現

因果注意力確保了模型的**方向性**。在每一層 Transformer 中，token `xₜ` 的表示只依賴於 `{x₁, ..., xₜ}`，形成一個鏈式結構：

```
h₁ → h₂ → h₃ → ... → hₙ
```

雖然 Transformer 不像 RNN 那樣按順序處理（可以並行計算所有位置），但因果遮罩使得並行計算的結果仍然遵循自迴歸的因果順序。

### 2. 訓練時的全序列並行化

因果注意力的一個關鍵優勢是**訓練時可以完全並行化** — 一個 forward pass 就能計算所有位置的預測：

```
輸入: [x₁, x₂, x₃, x₄, x₅]
預測: [x̂₂|x₁, x̂₃|x₁x₂, x̂₄|x₁x₂x₃, x̂₅|x₁x₂x₃x₄, x̂₆|x₁...x₅]
```

這得益於因果遮罩：雖然位置 `x₄` 在計算時只看到 `{x₁, x₂, x₃}`（因為遮罩），但所有位置的計算在同一批次中完成，充分利用了 GPU 的平行處理能力。

### 3. 推論時的順序生成

在推論（生成）時，因果注意力逐 token 進行：

```
Step 1: [x₁]                     → 預測 x̂₂
Step 2: [x₁, x̂₂]                → 預測 x̂₃
Step 3: [x₁, x̂₂, x̂₃]           → 預測 x̂₄
...
```

這一步驟無法並行化（因為每一步的輸入都依賴前一步的輸出），但因果遮罩確保了訓練與推論之間的行為一致。

## KV Cache：推論時的關鍵最佳化

實際生成時，如果每次從頭計算所有位置的注意力，計算量為 `O(T²·d)`，且隨著序列增長會越來越慢。

**KV Cache** 是一種空間換時間的最佳化：將已經計算過的 Key 和 Value 快取起來，每次生成新 token 時只計算新位置的 Q，並使用快取的 K、V：

```python
# 第一次：計算並快取
k₁, v₁ = project_k(x₁), project_v(x₁)

# 第 t 次：
kₜ, vₜ = project_k(xₜ), project_v(xₜ)
cache_K = [cache_K, kₜ]    # 追加
cache_V = [cache_V, vₜ]
attn = softmax(qₜ @ cache_Kᵀ / √d) · cache_V
```

這將每次生成步驟的計算量從 `O(t²·d)` 降低到 `O(t·d)`，大幅提升推論速度。mini-llm 的 `generate()` 方法沒有顯式實作 KV Cache（為了簡單），但這在生產級推論引擎中是標準配備。

## 因果注意力 vs 雙向注意力

| 特性 | Causal Attention (GPT) | Bidirectional Attention (BERT) |
|------|------------------------|-------------------------------|
| 遮罩 | 下三角 | 無遮罩（全連通） |
| 方向性 | 單向（左→右） | 雙向 |
| 訓練任務 | 下一 token 預測 | MLM（遮蓋語言建模） |
| 生成能力 | 原生支援（自迴歸） | 需特殊處理 |
| 對 context 的理解 | 只看左側 | 看雙側 |
| 典型模型 | GPT, LLaMA, Mistral | BERT, RoBERTa |

## Causal Convolution 的類比

因果注意力可類比於**因果卷積（Causal Convolution）** — 一種在 WaveNet 中用於音頻生成的技術。在因果卷積中，輸出在時間 `t` 只依賴於輸入在時間 `<= t` 的值。因果注意力是這個概念在注意力機制中的對應物。

不過，因果卷積的感受野是固定的（由卷積核大小決定），而因果注意力的感受野是**可變的**（可以關注到序列開頭的任何位置），這使得 Transformer 在捕捉長距離依賴時遠優於卷積模型。

## 具體數值範例 — 逐步計算

以 mini-llm 預設參數爲例（B=2, T=4, d_model=128, n_heads=4, head_dim=32）：

### 步驟 1-2：投影與拆分
```
x: (2, 4, 128)
Q = x @ W_Q, K = x @ W_K, V = x @ W_V  → 各 (2, 4, 128)
```
```python
q = q.view(B, T, n_heads, head_dim).transpose(1, 2)  # (2, 4, 4, 32)
k = k.view(B, T, n_heads, head_dim).transpose(1, 2)
v = v.view(B, T, n_heads, head_dim).transpose(1, 2)
```

### 步驟 3-5：分數 → 縮放 → 遮罩
```python
score = q @ k.transpose(-2, -1)          # (2, 4, 4, 4)
score = score / math.sqrt(32)
mask = torch.tril(torch.ones(4, 4))
score = score.masked_fill(mask == 0, -inf)
```

### 步驟 6-8：Softmax → 加權和 → 合併
```python
attn = F.softmax(score, dim=-1)          # (2, 4, 4, 4)
out = attn @ v                           # (2, 4, 4, 32)
out = out.transpose(1, 2).contiguous().view(B, T, 128)
out = self.c_proj(out)                   # (2, 4, 128)
```

所有樣本與所有頭同時平行計算，每個 head 的 score 矩陣為 4×4。整批運算中無 Python 迴圈，完全由 GPU 矩陣乘法完成。

## 為什麼遮罩值用 -inf 而不是 0？

Softmax：`softmax(z_i) = exp(z_i) / Σⱼ exp(z_j)`

遮罩設為 0 → `exp(0) = 1`，未來位置仍有非零權重。設為 -inf → `exp(-inf) = 0`，權重嚴格為 0。

數值範例：分數 [2.0, 1.0, 0.0]（位置 2 應被遮擋）：
```
不加遮罩：    softmax = [0.665, 0.245, 0.090]
設為 0：      softmax = [0.659, 0.089, 0.242]  ← 仍有 8.9%
設為 -inf：   softmax = [0.731, 0.000, 0.269]  ← 完全消除
```
只有 -inf 能保證被遮罩位置的注意力權重嚴格為 0。

## 縮放因子 1/√d 的數學必要性

假設 q_i, k_i 是均值 0、變異數 σ² 的獨立隨機變數：`Var(q·k) = d·σ⁴`。點積變異數隨 d 線性增長。

除以 √d 後：`Var((q·k)/√d) = σ⁴`，與 d 無關。

若不縮放，大 d 使點積落入 softmax 飽和區：softmax 接近 one-hot，梯度趨近於 0，導致梯度消失。

為什麼是 √d 而不是 d？標準差與 √d 成正比，除以 √d 將標準差恢復到常數。若除以 d，標準差變為 1/√d，分數過於平坦，失去區分能力。

## 多頭注意力的拆分與合併

多頭注意力將 d_model 分割為 n_heads 個子空間，每個 head 學習不同的關注模式。

### mini-llm 的實作

```python
class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        self.c_attn = nn.Linear(config.d_model, 3 * config.d_model)
        self.c_proj = nn.Linear(config.d_model, config.d_model)
        self.n_heads = config.n_heads
        self.head_dim = config.d_model // config.n_heads

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.c_attn(x)                       # (B, T, 3*C)
        q, k, v = qkv.split(C, dim=2)              # 各 (B, T, C)
        q = q.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        # attention...
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.c_proj(out)
```

`c_attn` 將三次投影合為一次矩陣乘法（3×d_model 輸出），減少 kernel launch。形狀變化：`(B, T, d_model) ↔ (B, n_heads, T, head_dim)`。d_model 必須能被 n_heads 整除。

## Cross-Attention（編碼器-解碼器注意力）

Cross-Attention 的 Query 來自解碼器，Key 和 Value 來自編碼器，不需要因果遮罩：

```
CrossAttn(Q_dec, K_enc, V_enc) = softmax(Q_dec·K_encᵀ/√d)·V_enc
```

注意力矩陣形狀：(B, n_heads, T_dec, T_enc)。

| 特性 | Causal Self-Attention | Cross-Attention |
|------|----------------------|-----------------|
| Q 來源 | 同序列 | 解碼器 |
| K, V 來源 | 同序列 | 編碼器 |
| 遮罩 | 下三角 | 無（全連通） |
| 序列長度 | T_dec = T_enc | 通常不同 |
| 作用 | 序列內部建模 | 序列間傳遞 |

原始 Transformer 的解碼器有兩層：Masked Self-Attention 接 Cross-Attention。純解碼器模型（GPT, LLaMA, mini-llm）不使用 Cross-Attention。

## 注意力的記憶體複雜度 O(T²)

標準注意力需實體化 T×T 矩陣：B × n_heads × T² × sizeof(dtype)。

| T | 每 head 元素 | 總記憶體 (B=1, n_heads=4, fp32) |
|---|-------------|-------------------------------|
| 512 | 262K | 4 MB |
| 2048 | 4.2M | 64 MB |
| 8192 | 67M | 1 GB |
| 32768 | 1B | 16 GB |

僅一層。32 層、T=32K 時需 ~512 GB。影響：context window 受 GPU 記憶體限制；B 與 T² 成反比。緩解方案包括 Flash Attention、稀疏注意力、線性注意力（O(T)）。

## Flash Attention 高層概念

瓶頸是 HBM 讀寫而非計算：標準注意力需反覆讀寫 T×T 矩陣（讀 QK→寫 score→讀 score→寫 softmax→讀 softmax,V→寫 out），O(T²) 的 HBM 存取遠比 O(T²·d) 的計算慢。

Flash Attention（Dao et al., 2022）在 GPU SRAM 中逐塊計算，避免 HBM 讀寫完整矩陣：

```
for Q_block in Q_blocks:         # 載入 SRAM
    for K_block, V_block in ...:
        局部注意力 → online softmax → 累積
```

效果：記憶體 O(T²)→O(T)，速度 2-4 倍提升，數學等價。PyTorch 2.0+ 內建支援（`F.scaled_dot_product_attention`）。mini-llm 為教學簡潔使用標準實作。

## KV Cache 的完整形狀追蹤

### Prefill（預填充）
並行處理所有 prompt token，初始化 KV Cache：
```
K_cache: (1, n_heads, P, head_dim),  V_cache: (1, n_heads, P, head_dim)
計算量：O(P²·d)
```

### Decode（解碼）
逐 token 生成，每步只處理一個新 token：
```
第 t 步（已生成 N 個 token）：
q_new: (1, n_heads, 1, head_dim)
K_cache: (1, n_heads, P+N, head_dim)

score = q_new @ K_cache.transpose(-2, -1)   # (1, n_heads, 1, P+N)
attn  = F.softmax(score, dim=-1)            # (1, n_heads, 1, P+N)
out   = attn @ V_cache                      # (1, n_heads, 1, head_dim)

# 追加新 KV
K_cache = torch.cat([K_cache, k_new], dim=2)  # (1, n_heads, P+N+1, head_dim)
V_cache = torch.cat([V_cache, v_new], dim=2)
```

### 計算量比較與記憶體負擔
| 方式 | 每步計算量 | 總計 |
|------|-----------|------|
| 無 KV Cache | O(t²·d) | O(T³·d) |
| 有 KV Cache | O(t·d) | O(T²·d) |

KV Cache 將總計算量從立方降為平方。以 L=32, n_heads=32, head_dim=128, T=4096, fp16 為例：
```
每層 KV Cache = 2 × 32 × 4096 × 128 × 2B = 64 MB
總 KV Cache   = 32 × 64 MB = 2 GB
```
最佳化：MQA（所有 q 共享 k/v）、GQA（分組共享，LLaMA 2/3）、KV Cache 量化。mini-llm 為簡潔未實作 KV Cache。

## 延伸閱讀

- 原始 Transformer: Vaswani et al., "Attention Is All You Need" (NeurIPS 2017)
- GPT 的因果語言建模: Radford et al., "Improving Language Understanding by Generative Pre-Training" (2018)
- KV Cache: Pope et al., "Efficiently Scaling Transformer Inference" (2023)
- Causal Convolution: Oord et al., "WaveNet: A Generative Model for Raw Audio" (2016)
- Teacher Forcing: Williams & Zipser, "A Learning Algorithm for Continually Running Fully Recurrent Neural Networks" (1989)
