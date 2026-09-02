# Autoregressive Language Model — 自迴歸語言模型

## 概述

**自迴歸語言模型（Autoregressive Language Model）** 是最基礎也最廣泛使用的語言模型形式。它將文字的機率分解為一連串條件機率的乘積：給定之前的所有 token，預測下一個 token。所有 GPT 系列模型都屬於自迴歸語言模型。mini-llm 專案的 v1（字元級）、v2、v3 全部使用自迴歸語言建模作為訓練目標。

## 動機：什麼是語言模型？

一個語言模型的本質是：**為一段文字賦予一個機率**。

```
P("小貓坐在桌上") = ?
P("小貓飛在天空") = ?
```

好的語言模型會給語法正確、語義合理的文字更高的機率。

語言模型不僅可以評估文字（填空、糾錯），更可以**生成新文字**（透過從機率分布中取樣），這是現代生成式 AI 的基石。

## 自迴歸分解

### 鏈式法則（Chain Rule of Probability）

機論中的條件機率鏈式法則：

```
P(x₁, x₂, ..., x_T) = P(x₁) · P(x₂ | x₁) · P(x₃ | x₁, x₂) · ... · P(x_T | x₁, ..., x_{T-1})
```

其中 `xₜ` 是序列中的第 `t` 個 token。

這個分解是**精確的**（沒有資訊損失），它只是將聯合機率重新表達為條件機率的乘積。自迴歸語言模型的核心假設就是：我們可以逐個 token 地建模這個條件機率鏈。

### 具體範例：P("小貓坐") 的鏈式分解

假設詞彙表由「小」、「貓」、「坐」、「在」、「桌」、「上」等字組成。欲計算「小貓坐」的機率：

```
P("小貓坐") = P(x₁="小") · P(x₂="貓" | x₁="小") · P(x₃="坐" | x₁="小", x₂="貓")
```

若語料庫有 1000 字，「小」出現 50 次 → P(小)=0.05
「小貓」出現 5 次 → P(貓|小)=5/50=0.1
「小貓坐」出現 2 次 → P(坐|小,貓)=2/5=0.4

```
P("小貓坐") = 0.05 × 0.1 × 0.4 = 0.002
```

神經語言模型不直接計數，而是學習參數化函數估計這些條件機率。

### 自迴歸的名稱由來

「自迴歸（autoregressive）」來自時間序列分析：

```
y_t = α₁·y_{t-1} + α₂·y_{t-2} + ... + ε_t
```

即 `y_t` 對其自身過去的值進行迴歸。語言模型中的自迴歸本質相同：token `xₜ` 的預測依賴於過去的 token `x₁...x_{t-1}`。

### 馬可夫假設

純粹的鏈式法則需要無限長的歷史。實務中，自迴歸語言模型通常引入有限上下文假設（等價於高階馬可夫鏈）：

```
P(xₜ | x₁, ..., x_{t-1}) ≈ P(xₜ | x_{t-k}, ..., x_{t-1})
```

但 Transformer 的注意力機制理論上可以關注到**所有**歷史 token（因果遮罩限制下不超過 `seq_len`），因此不是嚴格的 k 階馬可夫鏈。

## 訓練目標：下一 Token 預測

### 監督式學習的框架

雖然語言模型是「自監督」的（不需要外部標籤），但在具體的訓練過程中，每個樣本的監督訊號來自於文字本身：

```
輸入序列: [x₁, x₂, x₃, ..., x_T]
目標序列: [x₂, x₃, x₄, ..., x_{T+1}]
```

也就是說，在位置 `t`，給定 `[x₁, ..., xₜ]`，目標是預測 `x_{t+1}`。

### 為什麼這有效？

學習「預測下一個詞」實際上迫使模型學習：

1. **詞彙知識** — 字詞的形、音、義
2. **語法結構** — 怎樣的詞序是合法的（主詞-動詞-賓語）
3. **語義關係** — 哪些詞在語境中合理
4. **世界知識** — 「巴黎」後面常接「法國」或「艾菲爾鐵塔」
5. **長期依賴** — 一段話開頭的主題會影響結尾的用詞

所有這些知識都是語言理解所需的，卻不需要任何標註資料。

### Teacher Forcing（教師強迫）

訓練時，位置 `t` 的輸入永遠是**真實 ground-truth token** `xₜ`，而非模型自己在 `t-1` 的預測：

```
xb = data[i:i+seq_len]          # 全部是真實 token
yb = data[i+1:i+seq_len+1]      # 目標右移一位
logits = model(xb)               # 一次前向計算所有位置
loss = CE(logits, yb)            # 與所有目標比較
```

優點：訓練可完全並行化、穩定（輸入始終來自真實分布）、梯度通暢。

### Exposure Bias（曝露偏差）

Teacher Forcing 的根本矛盾：**訓練與推論行為不一致**。

- **訓練時**：輸入始終是 ground-truth token
- **推論時**：輸入包含自己先前生成的 token，可能含有錯誤

模型在訓練時從未見過「錯誤上下文」，推論時卻必須處理這種情況。隨著生成長度增加，誤差逐漸累積。這是導致長文本生成退化的核心原因之一。

緩解方法包括 Scheduled Sampling（訓練中逐步混入模型自己的預測）。mini-llm 保持最簡，僅用標準 Teacher Forcing。

### mini-llm 訓練迴圈的逐步追蹤

以 v1 為例，假設 "abcde" 編碼為 `data=[0,1,2,3,4]`，`seq_len=3`：

```
i=0 → xb=[0,1,2], yb=[1,2,3]

模型在三位置各自預測下一個 token：
  位置 0：給定 [0]      → 預測 1（正確 1）
  位置 1：給定 [0,1]    → 預測 2（正確 2）
  位置 2：給定 [0,1,2]  → 預測 3（正確 3）

Loss = 三個位置 Cross-Entropy 的平均
```

關鍵：位置 2 的預測依賴於位置 0/1 的**真實值**而非**預測值**— 這是 Teacher Forcing 的核心。

## 生成（取樣）

### 自迴歸生成

訓練完成後，模型可以透過反覆取樣來生成文字：

```python
def generate(model, start_tokens, max_new_tokens):
    idx = start_tokens
    for _ in range(max_new_tokens):
        logits, _ = model(idx)               # 模型預測
        probs = softmax(logits[:, -1, :])     # 最後一個位置的機率
        next_token = multinomial(probs)        # 從機率分布取樣
        idx = concat(idx, next_token)          # 追加新 token
    return idx
```

每一步：
1. 將目前所有 token 餵入模型
2. 模型輸出最後一個位置的機率分布（長度 = vocab_size）
3. 從該分布中取樣一個 token
4. 將取樣出的 token 加入序列尾部
5. 回到步驟 1（此時序列長度增加了 1）

### 取樣策略

**貪婪取樣（Greedy Decoding）** — 總是選機率最高的 token：

```python
next_token = argmax(probs)  # 確定性
```

優點：確定性，可重複。
缺點：生成結果可能單調重複。

**隨機取樣（Stochastic Sampling）** — 根據機率分布隨機抽取：

```python
next_token = multinomial(probs)  # 隨機性
```

優點：生成結果多樣，更有創造性。
缺點：可能產生低機率的奇怪結果。

mini-llm 使用後者（`torch.multinomial`），這是最簡單的隨機生成方式。

**溫度參數（Temperature）**

溫度控制取樣的「冒險程度」：

```python
probs = softmax(logits / temperature)
```

- `T = 0`：等於 greedy（最大機率 token 的機率趨近 1）
- `T = 1`：原始機率分布
- `T > 1`：分布更平坦（更多隨機性）
- `T < 1`：分布更尖銳（更確定性）

mini-llm 的 generate 函數沒有實作溫度參數，保持最簡形式。

### Top-K 和 Top-P 取樣

為了在隨機性和生成品質之間取得平衡，大語言模型通常使用：

**Top-K**：只從機率最高的 K 個 token 中取樣（其他設為 0 後重新歸一化）。

**Top-P (Nucleus Sampling)**：選擇累積機率達到 P 的最小 token 集合，只從這些 token 中取樣。

mini-llm 沒有實作這些進階取樣策略，但它們在實際的大規模語言模型中至關重要。

### 生成迴圈的逐步追蹤

初始 token `<SOS>`（編碼 3），追蹤張量形狀變化：

```
idx = [[3]]                       # shape: [1, 1]

第 1 步：idx_cond = [[3]]         # [1, 1]
  logits: [1, 1, vocab_size] → logits[:, -1, :]: [1, vocab_size]
  取樣得 7 → idx = [[3, 7]]      # [1, 2]

第 2 步：idx_cond = [[3, 7]]      # [1, 2]
  logits: [1, 2, vocab_size] → logits[:, -1, :]: [1, vocab_size]
  取樣得 4 → idx = [[3, 7, 4]]   # [1, 3]

第 3 步：idx_cond = [[3, 7, 4]]   # [1, 3]
  取樣得 2 → idx = [[3, 7, 4, 2]] # [1, 4]
```

序列超 `seq_len` 時 `idx_cond = idx[:, -seq_len:]` 只取最後 seq_len 個 token。

### 溫度參數的完整計算

logits `[2.0, 1.0, 0.5, 0.1, 0.01]` 在不同溫度下的 softmax：

**T=1.0（原始）**：
```
softmax = [exp(2.0), exp(1.0), exp(0.5), exp(0.1), exp(0.01)] / 13.871
= [0.533, 0.196, 0.119, 0.080, 0.073]
```

**T=0.5（尖銳）**：logits/0.5 = [4.0, 2.0, 1.0, 0.2, 0.02]
```
softmax = [54.598, 7.389, 2.718, 1.221, 1.020] / 66.947
= [0.815, 0.110, 0.041, 0.018, 0.015]
```

**T=2.0（平坦）**：logits/2.0 = [1.0, 0.5, 0.25, 0.05, 0.005]
```
softmax = [2.718, 1.649, 1.284, 1.051, 1.005] / 7.707
= [0.353, 0.214, 0.167, 0.136, 0.130]
```

| 溫度 | 最大機率 | 分布 |
|------|---------|------|
| 0.5 | 0.815 | 尖銳，幾乎確定 |
| 1.0 | 0.533 | 原始分布 |
| 2.0 | 0.353 | 平坦，高隨機性 |

### 自迴歸生成的效能瓶頸

根本限制：**逐 token 生成，不可並行**。長度 T 需 T 次順序前向傳播，生成複雜度 O(T³)（訓練因 Teacher Forcing 僅 O(T²)）。

KV Cache 是實際系統的必備優化：快取歷史 Key/Value 矩陣，每次只計算新 token 的注意力，將每次推論降為 O(T)。

### 投機解碼（Speculative Decoding）

加速方法：用**小型草稿模型**快速生成 K 個候選 token，再以**目標模型**一次性並行驗證。

流程：草稿模型快速自迴歸 K 步 → 目標模型同時計算所有 K 位置的分布 → 逐位比較決定接受/拒絕 → 被拒位置重新取樣。

不改變輸出分布的前提下，速度可提升 2-3 倍。mini-llm 不含此機制。

## 自迴歸模型 vs 雙向模型

| 特性 | 自迴歸模型 (GPT) | 雙向模型 (BERT) |
|------|-----------------|-----------------|
| 訓練目標 | 下一個 token 預測 | MLM（遮蓋語言建模） |
| 注意力 | 因果（只能看左側） | 雙向（看左右兩側） |
| 生成能力 | 原生支援 | 需要特殊技巧 |
| 編碼品質 | 單向 → 對理解任務較弱 | 雙向 → 對理解任務較強 |
| 典型應用 | 文字生成、對話 | 分類、標註、填空 |

### 訓練目標的深層比較

自迴歸 LM 與遮蓋語言模型（MLM）的損失函數本質不同：

**自迴歸 LM**：每個 token 條件於其**左側所有 token**。
```
L_AR = -Σₜ log P(xₜ | x₁, ..., x_{t-1})
```

**Masked LM（BERT）**：遮蓋 15% token，每個被遮 token 條件於**雙向上下文**。
```
L_MLM = -Σ_{t∈M} log P(xₜ | x₁, ..., x_{t-1}, x_{t+1}, ..., x_T)
```

這導致學到的表示本質差異：
- AR 擅長**生成**：訓練目標本身模擬了生成過程
- MLM 擅長**理解**：每個位置融合雙向上下文

mini-llm 全部使用自迴歸目標，無遮蓋語言建模。

## 從 N-gram 到神經網路

### N-gram 語言模型

在神經網路流行之前，語言模型使用 N-gram 計數：

```
P(xₜ | x₁, ..., x_{t-1}) ≈ count(x_{t-n+1}, ..., xₜ) / count(x_{t-n+1}, ..., x_{t-1})
```

- N=2（bigram）：只看前一個詞
- N=3（trigram）：看前兩個詞
- 平滑技術（如 Kneser-Ney）處理未見過的 N-gram

N-gram 的侷限：
- 無法處理長距離依賴（N 固定且不大）
- 稀疏性（大多數 N-gram 未在語料中出現過）
- 無法泛化到語義相似但字面不同的表達

### 神經語言模型的優勢

神經語言模型（包括 mini-llm 的 Transformer）從根本上解決了 N-gram 的問題：

1. **連續表示** — 每個 token 被嵌入到連續向量空間，語義相似的 token 在嵌入空間中靠近
2. **泛化能力** — 即使沒見過某個短語，如果它由已知單詞以已知語法組成，模型仍能給出合理預測
3. **長距離處理** — 注意力機制可以直接關注序列中的任何位置（不像 RNN 有梯度消失問題）

## mini-llm 中的自迴歸實現

### v1（完整自含式）

```python
# 訓練
data = torch.tensor(encode(text), dtype=torch.long)
xb = data[i:i+seq_len]      # 輸入
yb = data[i+1:i+seq_len+1]  # 目標

# 生成
idx_cond = idx[:, -seq_len:]    # 只取最後 seq_len 個 token
logits, _ = model(idx_cond)
probs = F.softmax(logits[:, -1, :], dim=-1)
idx_next = torch.multinomial(probs, num_samples=1)
```

### v2/v3（透過 model.generate）

```python
@torch.no_grad()
def generate(self, idx, max_new_tokens):
    self.eval()
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -self.seq_len:]
        logits, _ = self(idx_cond)
        probs = F.softmax(logits[:, -1, :], dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1)
        idx = torch.cat((idx, idx_next), dim=1)
    return idx
```

## Loss 與模型規模的對數線性關係

在 well-trained 大規模語言模型中，Cross-Entropy Loss 與參數量 N 存在對數線性關係：

```
L(N) ≈ A / N^α + L∞
```

其中 α 約 0.05–0.1，L∞ 為資料的不可壓縮熵（Kaplan et al. "Scaling Laws for Neural Language Models" 2020）。

實際含義：
- 模型越大 loss 越低，但邊際效益遞減
- 小模型的 loss 改善可預測大模型的行為
- 同等計算預算下存在最優模型大小與資料量分配

mini-llm 的約 1M 參數遠小於 scaling law 的觀測範圍（10⁶–10¹⁰），但仍展現類似趨勢。

## 延伸閱讀

- 神經語言模型的奠基工作: Bengio et al., "A Neural Probabilistic Language Model" (JMLR 2003)
- GPT 的生成式預訓練: Radford et al., "Improving Language Understanding by Generative Pre-Training" (2018)
- N-gram 語言模型: Katz, "Estimation of Probabilities from Sparse Data for the Language Model Component of a Speech Recognizer" (IEEE ASSP 1987)
- Top-K 與 Top-P 取樣: Holtzman et al., "The Curious Case of Neural Text Degeneration" (ICLR 2020)
- Kneser-Ney 平滑: Kneser & Ney, "Improved Backing-off for M-gram Language Modeling" (ICASSP 1995)
