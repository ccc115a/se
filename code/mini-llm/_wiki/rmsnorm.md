# RMSNorm — Root Mean Square Normalization

## 概述

**RMSNorm**（Root Mean Square Normalization）是一種神經網路的正規化（normalization）技術，由 Zhang 與 Sennrich 在 2019 年提出。它是 Layer Normalization (LayerNorm) 的簡化變體，在現代大型語言模型中廣泛取代 LayerNorm，因為它在維持相近效果的前提下顯著降低計算開銷。mini-llm 專案的 v1（mini-llm.py）、v2/v3（model.py）全部使用 RMSNorm 作為標準正規化層。

## 動機：為什麼需要正規化？

深度神經網路在訓練過程中，每一層的輸入分布會隨著前一層參數的更新而持續變化，這種現象稱為 **Internal Covariate Shift**。這導致：

1. **訓練不穩定** — 網路必須不斷適應新的輸入分布，使得收斂困難
2. **梯度消失/爆炸** — 深層網路的活化值或梯度可能指數級增長或衰減
3. **對學習率敏感** — 需要精細調整學習率來補償分布變化

正規化層的作用是將每一層的輸入重新調整為穩定的分布（均值接近 0、方差接近 1），從而緩解上述問題。

## Layer Normalization 回顧

LayerNorm 對每個樣本在特徵維度上計算均值與標準差，然後進行正規化：

```
LayerNorm(x) = (x - μ) / σ * γ + β
```

其中：
- `μ = (1/d) * Σᵢ xᵢ` — 特徵維度的均值
- `σ = sqrt((1/d) * Σᵢ (xᵢ - μ)²)` — 特徵維度的標準差
- `γ` — 可學習的縮放參數（增益）
- `β` — 可學習的平移參數（偏置）

LayerNorm 的關鍵計算在於 **均值和標準差都需要計算**，這涉及兩次過資料的歸約運算，在硬體上不是最有效率的。

## RMSNorm 的原理

RMSNorm 的核心洞察是：**LayerNorm 中的均值中心化（減去 μ）可能不是必要的**。對於 Transformer 模型，真正重要的是將活化值的方差控制在一定範圍內，而非強制均值為 0。

因此 RMSNorm 完全移除均值計算，僅使用 **均方根（Root Mean Square）** 來正規化：

```
RMSNorm(x) = x / RMS(x) * γ
```

其中：
- `RMS(x) = sqrt((1/d) * Σᵢ xᵢ²)` — 特徵維度的均方根
- `γ` — 可學習的縮放參數（無偏置項 β）

### 與 LayerNorm 的比較

| 特性 | LayerNorm | RMSNorm |
|------|-----------|---------|
| 均值中心化 | μ = mean(x) | 無 |
| 方差正規化 | σ = std(x) | RMS(x)（包含均值資訊） |
| 可學習參數 | γ（縮放）+ β（平移） | γ（縮放） |
| 計算量 | 2 次歸約（mean + variance） | 1 次歸約（x² 的均值） |
| 訓練速度 | 基準 | 快 7%–15% |
| 效果 | 基準 | 接近或略優於 LayerNorm |

RMSNorm 節省了計算均值的一次全局歸約操作，這在 GPU 上意味著減少了一次 `all-reduce` 通訊，對訓練吞吐量有正面影響。

## 數學推導

設輸入向量 `x ∈ ℝᵈ`，RMSNorm 的計算步驟：

**Step 1: 計算均方根**
```
RMS(x) = sqrt( (1/d) * Σᵢ xᵢ² + ε )
```
其中 `ε`（epsilon）是一個極小的常數（如 1e-6），防止分母為 0。

**Step 2: 正規化**
```
x̂ = x / RMS(x)
```
這將向量的 scale 調整至接近 1，但**不改變向量方向**。

**Step 3: 仿射變換**
```
y = x̂ * γ
```
其中 `γ ∈ ℝᵈ` 是可學習的參數，允許模型恢復原本需要的縮放。

### 梯度分析

RMSNorm 的梯度計算也比 LayerNorm 更簡單。對於損失 `L`，對輸入 `xᵢ` 的梯度為：

```
∂L/∂xᵢ = (1 / RMS(x)) * [∂L/∂ŷᵢ - (ŷᵢ / d) * Σⱼ (∂L/∂ŷⱼ * ŷⱼ)]
```

相比之下，LayerNorm 的梯度因為涉及均值項而多了一個修正項。RMSNorm 的梯度計算約省去 10%–20% 的運算量。

## 實作細節

### 標準實作（PyTorch）

```python
class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm_x = torch.mean(x ** 2, dim=-1, keepdim=True)
        x_normed = x * torch.rsqrt(norm_x + self.eps)
        return self.weight * x_normed
```

核心步驟拆解：
1. `x ** 2` — 逐元素平方
2. `torch.mean(..., dim=-1, keepdim=True)` — 在最後一個維度（特徵維度）上取平均，得到 RMS²
3. `torch.rsqrt(...)` — 計算 `1 / sqrt(RMS² + ε)`，這是 RMS⁻¹
4. `x * rsqrt_result` — 逐元素乘以 RMS⁻¹，完成正規化
5. `self.weight * x_normed` — 應用可學習的縮放參數

### mini-llm 專案的實作

在 mini-llm 中，RMSNorm 用在兩個位置：

**Attention 後的殘差連接前（norm1）：**
```python
x = x + self.attention(self.norm1(x), freqs_cis)
```

**FFN 後的殘差連接前（norm2）：**
```python
x = x + self.ffn(self.norm2(x))
```

**最終輸出層前（final norm）：**
```python
logits = self.output(self.norm(x))
```

這種「Pre-Norm」架構（正規化放在子層之前而非之後）是現代 Transformer 的標準做法，比起原始 Transformer 的「Post-Norm」更穩定，允許訓練更深的模型而不需要 warmup 階段。

### RMSNorm vs Pre-Norm 設計

```
Pre-Norm（現代, mini-llm 使用）:
    x = x + Sublayer(Norm(x))

Post-Norm（原始 Transformer）:
    x = Norm(x + Sublayer(x))
```

Pre-Norm 的優勢在於殘差路徑上的訊號不需要經過正規化層，梯度可以直接流通，因此更適合深層網路。

## 前向傳播逐步詳解

假設輸入形狀為 `(B, T, d) = (2, 4, 8)`，追蹤一個樣本 `x ∈ ℝ⁸` 的 RMSNorm 計算過程：

**Step 1 — 輸入** `x = [1.2, -0.5, 2.1, -1.8, 0.3, -0.9, 1.5, -0.2]`

**Step 2 — 平方** `x² = [1.44, 0.25, 4.41, 3.24, 0.09, 0.81, 2.25, 0.04]`

**Step 3 — 平方均值** `mean(x²) = 12.53 / 8 = 1.56625`

**Step 4 — 倒數平方根** `RMS(x)⁻¹ = 1 / sqrt(1.56625 + 1e-6) ≈ 0.7990`

**Step 5 — 正規化** `x̂ = x · 0.7990 ≈ [0.9588, -0.3995, 1.6779, -1.4382]`，此時 `RMS(x̂) ≈ 1`

**Step 6 — 縮放** 若 `γ = [0.8, 1.2, 0.9, 1.1]`，則 `y = x̂ * γ ≈ [0.7670, -0.4794, 1.5101, -1.5820]`

### 張量視角

實作中輸入形狀為 `(B, T, d)`，RMSNorm 沿 `dim=-1` 計算：

```
x:          (B, T, d)        原始輸入
x ** 2:     (B, T, d)        逐元素平方
mean(...):  (B, T, 1)        在 dim=-1 歸約，保留維度
rsqrt(...): (B, T, 1)        倒數平方根（廣播到 d 維度）
x * rsqrt:  (B, T, d)        廣播乘法完成正規化
weight * :  (B, T, d)        廣播縮放輸出
```

所有操作皆為逐元素運算或歸約，無條件分支，對 GPU 友善。每個 token 在 T 維度上獨立正規化，token 之間不互相影響。

## Pre-Norm 與 Post-Norm 深入比較

### 計算圖對比

```
Post-Norm（原始 Transformer）:
  xₗ ──┬──→ Sublayer ──→ (+)
       │                  │
       └──────────────────┘
                         │
                       Norm(·)
                         │
                         ▼
                       xₗ₊₁

Pre-Norm（mini-llm 使用）:
  xₗ ──┬──→ Norm ──→ Sublayer ──→ (+)
       │                             │
       └─────────────────────────────┘
                                     │
                                     ▼
                                   xₗ₊₁
```

Pre-Norm 的殘差捷徑保持乾淨的單位映射，梯度可直接流通；Post-Norm 的 Norm 則阻擋了這條捷徑。

### Post-Norm 的問題

1. **阻斷殘差捷徑** — Norm 作用在殘差和上，梯度須通過 Norm 反向傳播，增加路徑長度
2. **需要 warmup** — 初始分布不穩定時 Post-Norm 容易 diverging，需數千步學習率 warmup
3. **深度退化** — 超過 12 層後 Post-Norm 表現顯著下降

### Pre-Norm 的梯度傳播優勢

殘差更新 `xₗ₊₁ = xₗ + Sublayer(Norm(xₗ))` 的梯度可近似為：

```
∂L/∂x₁ ≈ ∂L/∂xₗ [ 1 + Σⱼ ∂/∂x₁ Sublayerⱼ(Norm(xⱼ)) ]
```

主項 `1` 來自殘差捷徑，確保深層梯度不消失。這是 **ResNet 風格** 的訊號傳播：殘差流保持梯度穩定，正規化僅用於控制子層輸入分布。mini-llm 使用 3–4 層，Pre-Norm 的優勢雖不如百層模型顯著，但作為標準做法仍被採用。

## 為什麼 LLM 偏好 RMSNorm

1. **計算效率** — 少了均值計算，在大型模型中節省的運算量可觀
2. **梯度穩定性** — 移除均值項後，梯度的計算更簡潔，反向傳播更穩定
3. **與 RoPE 的相容性** — RoPE 對注意力分數的影響不涉及均值偏移，RMSNorm 的簡化設計與 RoPE 配合良好
4. **大規模驗證** — LLaMA、Mistral、Gemma 等重要開源模型都使用 RMSNorm，證明了其有效性

## 與 Batch Normalization 對比

雖然本專案未使用 BatchNorm，但理解其差異有助於掌握 RMSNorm 的定位：

| 特性 | BatchNorm | LayerNorm | RMSNorm |
|------|-----------|-----------|---------|
| 正規化維度 | batch 維度 | 特徵維度 | 特徵維度 |
| 依賴 batch size | 是 | 否 | 否 |
| 訓練/推論差異 | 有（使用 running stats） | 無 | 無 |
| 適合序列模型 | 不適合（不同長度 padding） | 適合 | 適合 |
| RNN/Transformer 適用性 | 低 | 高 | 高 |

## RMSNorm 與殘差流的交互作用

深層 Transformer 的殘差流（residual stream）是所有 token 表示的累積通道。RMSNorm 控制子層輸出加入殘差流前的訊號尺度。

### 訊號傳播分析

L 層殘差流更新：`xₗ = x₀ + Σᵢ₌₁ˡ Sublayerᵢ(Norm(xᵢ₋₁))`

- **無正規化**：子層輸出方差 `σ²` 累積，`Var(xₗ) ≈ L · σ²`，隨層數線性增長
- **有 RMSNorm**：Norm 固定輸入 RMS 為 1，每層貢獻方差可控

### LayerNorm vs RMSNorm 對殘差流的影響

LayerNorm 的均值中心化會移除殘差流中的「直流分量」（dc offset）。語言模型的部分語義可能依賴殘差流中的全局偏移訊號。**RMSNorm 保留偏移，僅控制 scale**，對殘差流的干擾更小。在 LLaMA 系列中，中間層的 γ 變化不大，移除均值在 benchmark 上與 LayerNorm 無顯著差異。

## RMSNorm 與 LayerNorm 的梯度比較（實作視角）

### 計算圖差異

```python
class LayerNormManual(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(dim))
        self.beta = nn.Parameter(torch.zeros(dim))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(dim=-1, keepdim=True)
        var = x.var(dim=-1, keepdim=True, unbiased=False)
        return self.gamma * (x - mean) * torch.rsqrt(var + self.eps) + self.beta

class RMSNormManual(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        norm_x = x.pow(2).mean(dim=-1, keepdim=True)
        return self.gamma * x * torch.rsqrt(norm_x + self.eps)
```

LayerNorm 需要 **兩次歸約**（mean + variance），RMSNorm 只需 **一次歸約**（`x²` 的均值）。分散式訓練中，每次歸約對應一次 `all-reduce` 通訊，RMSNorm 省去 50% 的通訊量。

### 梯度公式對比

LayerNorm：
```
∂L/∂xᵢ = (1/σ)[∂L/∂ŷᵢ - mean(∂L/∂ŷ) - ŷᵢ · mean(∂L/∂ŷ · ŷ)]
```

RMSNorm：
```
∂L/∂xᵢ = (1/RMS)[∂L/∂ŷᵢ - (ŷᵢ/d) · Σⱼ(∂L/∂ŷⱼ · ŷⱼ)]
```

移除 `mean(∂L/∂ŷ)` 項不僅省去歸約計算，也消除該項在反向傳播中可能引入的數值噪聲。實測 RMSNorm 反向傳播比 LayerNorm 快 10%–20%。

### 理論上的風險

LayerNorm 的均值中心化在極端活化值時可拉回動態範圍。RMSNorm 缺少這層保護，但 Transformer 的注意力機制與殘差連接設計使極端均值偏移很少發生，因此風險極低。

## 實戰訓練技巧

### Epsilon 調校

| 精度模式 | 建議 ε | 原因 |
|----------|--------|------|
| FP32 | 1e-6 | 預設值，足夠防止除零 |
| FP16 | 1e-4 ~ 1e-3 | 半精度數值範圍小 |
| BF16 | 1e-3 | BF16 精度更低，需更大 epsilon |
| AMP 混合精度 | 1e-5 ~ 1e-4 | 視使用 FP16 還 BF16 而定 |
| 深層模型 (>30層) | 1e-5 ~ 1e-4 | 累積誤差隨層數增加 |

若訓練出現 NaN loss，首先檢查 RMSNorm 的 ε 是否夠大。若 loss curve 正常則無需調整。

### 混合精度注意事項

1. **RSqrt 精度** — `torch.rsqrt` 在 FP16 下精度較差，可先以 FP32 計算 `sqrt(mean(x²)+ε)` 再轉回 FP16
2. **FP32 保留** — 將 RMSNorm 的 forward 設為 `autocast(enabled=False)`，避免精度損失
3. **γ 初始化** — `torch.ones(dim)` 在混合精度下正常工作，無需特殊處理

### 初始化技巧

- **Output Norm**：最終輸出層前的 RMSNorm，γ 可初始化為 `0.1`，防止 logits 過大導致 softmax 飽和
- **γ 降溫**：訓練後期可凍結 γ 梯度（`requires_grad=False`），避免正規化尺度漂移
- **學習率**：γ 通常與主參數使用相同 LR；若正規化尺度不穩定，可降為主 LR 的 0.1 倍

## 正規化在不同規模模型中的角色

### 玩具模型（mini-llm: ~0.8M 參數，3–4 層，d=128）

RMSNorm 的影響不如大型模型顯著：梯度消失/爆炸風險低，計算節省不明顯。但作為教育專案，使用 RMSNorm 可幫助學習者理解業界標準做法。

### 中型模型（LLaMA 13B: ~40 層，d=5120）

每次 forward 省去一次歸約，在數百萬 token 的訓練中累積顯著。殘差流的穩定性成為關鍵——40+ 層 Transformer 對正規化極為敏感，RMSNorm 的簡潔設計在此發揮重要作用。

### 超大型模型（LLaMA 405B: ~126 層，d=16384）

- **通訊瓶頸**：張量並行 + 流水線並行下，減少一次 all-reduce 在 16K+ GPU 集群上可節省數天訓練時間
- **數值穩定性**：BF16/FP8 精度下需更大 ε（如 1e-3），防止精度損失導致的正規化失效
- **QK-Norm**：部分大模型（如 PaLM）對 Q 和 K 分別做 RMSNorm，進一步穩定注意力分布

| 規模 | 模型 | 層數 | d_model | RMSNorm 主要考量 |
|------|------|------|---------|-----------------|
| 玩具 | mini-llm | 3–4 | 128 | 教育示範 |
| 小型 | GPT-2 | 12 | 768 | 穩定性 + 小幅加速 |
| 中型 | LLaMA 13B | 40 | 5120 | 計算效率 + 梯度穩定 |
| 大型 | LLaMA 70B | 80 | 8192 | 通訊瓶頸 |
| 超大型 | LLaMA 405B | 126 | 16384 | 分散式通訊 + BF16/FP8 |

RMSNorm 從玩具到超大型模型的普及，證明了「少即是多」的設計哲學：**移除不必要的計算不僅提升效率，還提升了穩定性**。對於 mini-llm 的學習者而言，理解 RMSNorm 就是理解現代 LLM 架構設計的一個核心環節。

## 延伸閱讀

- 原始論文: Zhang & Sennrich, "Root Mean Square Layer Normalization" (NeurIPS 2019)
- Layer Normalization: Ba et al., "Layer Normalization" (2016)
- LLaMA 報告: Touvron et al., "LLaMA: Open and Efficient Foundation Language Models" (2023) — 首次在大型開源 LLM 中使用 RMSNorm
- Pre-Norm vs Post-Norm 研究: Xiong et al., "On Layer Normalization in the Transformer Architecture" (ICML 2020)
