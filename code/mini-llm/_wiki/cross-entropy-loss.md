# Cross-Entropy Loss — 交叉熵損失函數

## 概述

**Cross-Entropy Loss（交叉熵損失）** 是語言模型及其他分類任務中最常用的損失函數。它衡量模型預測的機率分布與真實分布之間的差異。在語言模型中，交叉熵損失直接對應於**模型對下一個 token 預測的不確定度**。mini-llm 在所有版本的訓練中都使用 cross-entropy loss 作為最佳化目標。

## 資訊理論基礎

### 資訊量（Self-Information）

一個事件 `x` 發生的資訊量定義為：

```
I(x) = -log₂ P(x)
```

- 極不可能發生的事件（`P(x) → 0`）含有極大的資訊量
- 肯定發生的事件（`P(x) = 1`）資訊量為 0

單位取決於對數底數：底數 2 為「位元（bits）」，自然對數為「奈特（nats）」。深度學習中通常使用自然對數 `ln`，單位為 nats。

### 熵（Entropy）

一個隨機變數 `X` 的熵是它的期望資訊量：

```
H(X) = -Σₓ P(x) · log P(x)
```

熵衡量系統的不確定度。例如：
- 公平硬幣的熵 = `-0.5·log 0.5 × 2 = 1 bit`
- 總是正面的硬幣的熵 = `-1·log 1 = 0 bits`

### 交叉熵（Cross-Entropy）

交叉熵衡量用模型分布 `Q` 來編碼真實分布 `P` 所需的平均資訊量：

```
H(P, Q) = -Σₓ P(x) · log Q(x)
```

### KL 散度

交叉熵與熵的差值即為 KL 散度（Kullback-Leibler divergence）：

```
D_KL(P || Q) = H(P, Q) - H(P) = Σₓ P(x) · log(P(x)/Q(x))
```

KL 散度衡量兩個分布的差異，且始終 ≥ 0（只有在 P = Q 時為 0）。

### 交叉熵、熵、KL 散度的關係

```
H(P, Q) = H(P) + D_KL(P || Q)
```

在語言模型中，真實分布 `P` 是訓練資料中 token 的 one-hot 分布（下一個 token 是確定的），因此 `H(P) = 0`，交叉熵等於 KL 散度。

## 語言模型中的交叉熵損失

### 對單一預測的損失

給定序列 `[x₁, x₂, ..., x_T]`，模型在位置 `t` 預測下一個 token：

```
P(x_{t+1} | x₁...xₜ) = softmax(W·hₜ) → 長度為 V 的機率向量
```

真實標籤 `yₜ` 是 one-hot 向量（第 `x_{t+1}` 個位置為 1，其餘為 0）。

```
Lossₜ = -log P(yₜ | x₁...xₜ) = -log(softmax(logits)[yₜ])
```

### 在一個序列上的平均損失

```
Loss = -(1/T) · Σₜ log P(x_{t+1} | x₁...xₜ)
```

這等價於**整個序列的負對數似然（Negative Log-Likelihood, NLL）**。

### mini-llm 的實作

```python
def forward(self, idx, targets=None):
    B, T = idx.shape
    x = self.tok_emb(idx)
    for layer in self.layers:
        x = layer(x, self.freqs_cis)
    logits = self.output(self.norm(x))

    if targets is None:
        loss = None
    else:
        B, T, C = logits.shape
        logits = logits.view(B*T, C)    # (B, T, V) → (B*T, V)
        targets = targets.view(B*T)      # (B, T)    → (B*T,)
        loss = F.cross_entropy(logits, targets)

    return logits, loss
```

PyTorch 的 `F.cross_entropy` 整合了兩個步驟：
1. `log_softmax(logits)` — 對 logits 應用 log-softmax
2. `nll_loss(log_probs, targets)` — 取出目標位置的負對數值

使用 `F.cross_entropy` 而非手動 `softmax + log + indexing` 的原因：
- **數值穩定性**：`log(softmax(x))` 的實作使用 `x - max(x) - log(sum(exp(x - max(x))))`，避免指數運算造成的溢出
- **效率**：一次操作完成，不需要中間張量

### 分解示範與數值穩定性

以下三種等價：

```python
loss1 = F.cross_entropy(logits, targets)                       # 一步到位（推薦）
loss2 = F.nll_loss(F.log_softmax(logits, dim=-1), targets)     # 分解為兩步
loss3 = -torch.log(F.softmax(logits, dim=-1).gather(1,         # 不穩定做法
         targets.unsqueeze(1))).mean()
```

方法三有數值風險。當 logits 含大值（如 1000）時 `exp(1000)` 溢位為 ∞，softmax 回傳 NaN。**max-subtraction 技巧**解決此問題：

```
log_softmax(z)ᵢ = zᵢ - max(z) - ln(Σⱼ exp(zⱼ - max(z)))
```

先減去 max(z) 確保最大指數為 exp(0) = 1。舉例：z=[1000,0,0] → z'=[0,-1000,-1000] → exp(z')=[1,≈0,≈0] → log_softmax₀ = 0 - ln(1) = 0 ✓。PyTorch 內部實作即採用此技巧。

### 為何展平為 (B*T, C)

logits `(B, T, V)` 和 targets `(B, T)` 需轉為 `F.cross_entropy` 接受的 `(N, C)` 和 `(N,)`：

```python
logits = logits.view(B*T, C)
targets = targets.view(B*T)
```

展平後 B×T 個時間步視為獨立樣本。因損失取平均，數學結果完全相同。

## 具體數值範例（V=5 手算）

以 V=5 逐步手算 softmax、log 與交叉熵。

### 假設 logits 與 softmax

```
z = [2.0, 1.0, 0.5, 0.1, -0.5]

exp:     7.389   2.718   1.649   1.105   0.607    總和 = 13.468
softmax: 0.549   0.202   0.122   0.082   0.045    總和 = 1.000
```

### 計算交叉熵

真實類別 0：`Loss = -ln(0.549) = 0.599 nats`
真實類別 2：`Loss = -ln(0.122) = 2.103 nats`

當正確類別機率低時損失高出 3.5 倍 — 交叉熵對「低機率正確類別」施以強烈懲罰。

## 困惑度（Perplexity）

困惑度是交叉熵損失的指數轉換：`PPL = exp(Loss)`（nats 為單位）。

### 直觀理解

困惑度是**模型預測下一個 token 時的有效平均選擇數**：
- `PPL = 1`：完美預測
- `PPL = V`：完全隨機猜測

### 具體範例

詞表 {「我」, 「吃」, 「飯」, 「了」, 「嗎」}：

| 上下文 | P(我) | P(吃) | P(飯) | P(了) | P(嗎) | 真實 |
|--------|-------|-------|-------|-------|-------|------|
| "我"   | 0.02  | 0.50  | 0.30  | 0.15  | 0.03  | 「吃」 |
| "吃了" | 0.01  | 0.01  | 0.90  | 0.05  | 0.03  | 「飯」 |

「我_」：Loss = -ln(0.50) = 0.693，PPL = 2.0（兩個合理選擇）。

「吃了_」：Loss = -ln(0.90) = 0.105，PPL ≈ 1.11（幾乎確定）。

### Bits Per Character（BPC）

字元級模型常用 BPC：`BPC = Loss / ln(2)`。mini-llm v2 Loss ≈ 0.22 → BPC ≈ 0.32 bits/char（隨機猜測 6.81 bits/char）。

### mini-llm 範例分析

```
v2 預訓練完成：Loss ≈ 0.22 → PPL ≈ 1.25
v2 微調完成：  Loss ≈ 0.21 → PPL ≈ 1.23
```

### 各時期模型比較

| 模型 | Loss（nats） | PPL | 備註 |
|------|-------------|-----|------|
| 隨機猜測（字元級, V=112） | ln(112) ≈ 4.72 | 112 | — |
| mini-llm v1（訓練後） | ~0.09 | ~1.09 | 1500 字語料 |
| mini-llm v2（預訓練後） | ~0.22 | ~1.25 | 20 萬字語料 |
| mini-llm v2（微調後） | ~0.21 | ~1.23 | — |
| GPT-2（~50K BPE） | ~3.0 | ~20 | 大型真實語料 |

PPL ≈ 1.25 表示平均從 ~1.25 個字元中猜測。字元級預測比 BPE 容易（字元分布更集中），不應直接比較。

### 損失值解讀

| Loss (nats) | PPL | exp(-Loss) | 解讀 |
|-------------|-----|------------|------|
| 0.01 | 1.01 | 0.990 | 幾乎總是正確 |
| 0.22 | 1.25 | 0.803 | mini-llm v2 預訓練完成 |
| 1.00 | 2.72 | 0.368 | 平均從 2.7 個字元中猜測 |
| 4.72 | 112 | 0.009 | 隨機猜測 |

`exp(-Loss)` 是模型賦予正確字元的平均機率。mini-llm v2 約 80.3%。

## Softmax 與交叉熵的搭配

### Softmax 函數

```
softmax(z)ᵢ = exp(zᵢ) / Σⱼ exp(zⱼ)
```

將 logits 轉換為機率分布（各分量和為 1 的正數）。

### 最大似然估計等價性

最小化交叉熵 = 最大化訓練資料的對數似然（MLE）：

```
θ* = argmax_θ Σₜ log P_θ(x_{t+1} | x₁...xₜ)
   = argmin_θ CrossEntropyLoss(θ)
```

## 梯度特性

交叉熵 + softmax 的梯度計算極簡：`∂L/∂zₖ = softmax(z)ₖ - 1(k==y)`。
- 正確類別 y：梯度 = P(y)-1（負值，提高機率）
- 其他類別：梯度 = P(k)（正值，降低機率）

**梯度就是預測與真實的差距**。

### 梯度推導

令 pᵢ = exp(zᵢ)/Σⱼ exp(zⱼ)，one-hot y 滿足 Σᵢ yᵢ = 1。L = -Σᵢ yᵢ·ln(pᵢ)。

∂L/∂zₖ = Σⱼ (∂L/∂pⱼ)·(∂pⱼ/∂zₖ)，∂L/∂pⱼ = -yⱼ/pⱼ。

Softmax 偏導：j=k → pₖ(1-pₖ)；j≠k → -pⱼ·pₖ。

```
∂L/∂zₖ = (-yₖ/pₖ)·pₖ(1-pₖ) + Σⱼ≠ₖ (-yⱼ/pⱼ)·(-pⱼ·pₖ)
       = -yₖ(1-pₖ) + pₖ·(1-yₖ)   （利用 Σⱼ yⱼ = 1）
       = pₖ - yₖ
```

等價於：

```python
dlogits = F.softmax(logits, dim=-1)
dlogits[range(B*T), targets] -= 1
```

### 交叉熵 vs MSE

MSE 分類梯度含 softmax 縮放因子 pₖ(1-pₖ)：

```
∂L_MSE/∂zₖ = (pₖ - yₖ)·pₖ·(1-pₖ)
```

| 情況 | p_y | CE 梯度 | MSE 梯度 |
|------|-----|---------|----------|
| 完全錯誤 | 0.001 | -0.999 | ≈ -0.001 |
| 部分正確 | 0.500 | -0.500 | -0.125 |
| 高度正確 | 0.990 | -0.010 | -0.010 |

MSE 完全錯誤時梯度消失（p_y→0 時 p_y(1-p_y)→0），最需學習時反而最慢。**分類用 CE，迴歸用 MSE**。

## Label Smoothing（標籤平滑）

將 one-hot 替換為平滑分布：`y' = (1-ε)·onehot(y) + ε/V`（ε 通常 0.1）。

這有助於減少 overfitting、提高泛化能力。mini-llm 沒有使用 label smoothing（保持簡單），但它是現代 LLM 訓練中常見的技巧。

### 梯度分析

∂L/∂zₖ = pₖ - y'_k = pₖ - [(1-ε)·yₖ + ε/V]

- **正確類別**：梯度 ≈ p_y - (1-ε)，絕對值減小 ε，抑制過度自信
- **錯誤類別**：pₖ < ε/V 時梯度由正轉負，防止 logits 極端分化

## 延伸閱讀

- 資訊理論基礎: Shannon, "A Mathematical Theory of Communication" (1948)
- Softmax 與交叉熵的連結: Bridle, "Probabilistic Interpretation of Feedforward Classification Network Outputs, with Relationships to Statistical Pattern Recognition" (1990)
- Label Smoothing: Szegedy et al., "Rethinking the Inception Architecture for Computer Vision" (CVPR 2016)
- 困惑度作為語言模型評估指標: Jelinek et al., "Perplexity—a measure of the difficulty of speech recognition tasks" (JASA 1977)
