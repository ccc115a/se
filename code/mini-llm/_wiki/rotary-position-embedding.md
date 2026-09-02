# Rotary Position Embedding (RoPE)

## 概述

**Rotary Position Embedding（RoPE）** 是一種為 Transformer 模型注入位置資訊的方法，由 Su 等人於 2021 年在論文「RoFormer: Enhanced Transformer with Rotary Position Embedding」中提出。與傳統的加法位置編碼（如原始 Transformer 的 sinusoidal encoding）不同，RoPE 透過**旋轉矩陣**將相對位置資訊直接編碼進注意力計算中。mini-llm 專案在所有版本的模型中都使用 RoPE 作為位置編碼方式。

## 動機：為什麼需要位置編碼？

Transformer 的自注意力機制是**排列不變的（permutation-invariant）** — 它對輸入序列中各 token 的順序不敏感。換句話說，如果不加位置資訊，模型會認為「A 愛 B」和「B 愛 A」是相同的輸入。對於語言這種對順序極度敏感的資料，這顯然是不夠的。因此必須有一種方式讓模型知道 token 在序列中的位置。

位置編碼需要滿足：
1. **唯一性** — 每個位置有獨特的編碼
2. **相對位置感知** — 兩個位置之間的距離關係應能被模型捕捉
3. **泛化到未見過的長度** — 模型訓練時沒看過的序列長度也應能處理
4. **與自注意力相容** — 計算方式應自然融入注意力機制

## RoPE 的直觀理解

RoPE 的核心思想非常優雅：**將位置資訊編碼為一組旋轉角度，然後在 query 和 key 向量上進行旋轉**。

想像你有一組二維向量，如果你希望位置 `i` 和位置 `j` 的 query/key 之間的點積反映它們的距離 `|i-j|`，一個自然的做法是按照位置來旋轉向量 — 位置越遠，旋轉角度越大。兩個向量之間的夾角差異正好反映了它們的相對位置差。

RoPE 將這個概念推廣到高維空間，將 `d` 維向量分成 `d/2` 個二維子空間，每個子空間以不同的旋轉速度進行旋轉。

### 二維旋轉的可視化

```
原始向量 x           位置 m 旋轉後         多頻率旋轉（高維示意）
    ↑                    ↙           dim 0-1 (慢速)  dim 2-3 (中速)  dim 4-5 (快速)
    | x                 / Rot(x,m)    pos 0:  →         →             →
    |                 /               pos 1:  ↗         ↖             ↑
    |               / mθ              pos 2:  ↑         ←             ↓
    +-------→      +-------→          pos 3:  ↖         ↙             →
                                       pos 4:  ←         ↓             ↑
                                       pos 5:  ↙         ↘             ←
低頻維度（小 k）旋轉慢 → 編碼長距離關係；高頻維度（大 k）旋轉快 → 編碼短距離關係
```

## 數學原理

### 二維情況

對於二維向量 `(x₁, x₂)`，位置 `m` 的旋轉變換定義為：

```
Rot(x, m) = (x₁ * cos(mθ) - x₂ * sin(mθ), x₁ * sin(mθ) + x₂ * cos(mθ))
```

這等價於將向量 `x` 旋轉了角度 `mθ`。用矩陣表示：

```
Rot(x, m) = [[cos(mθ), -sin(mθ)],
             [sin(mθ),  cos(mθ)]] · (x₁, x₂)ᵀ
```

### 推廣到 d 維

對於維度 `d` 的向量（`d` 必須為偶數），RoPE 將其視為 `d/2` 個二維子向量的拼接。每個子向量 `(x_{2k}, x_{2k+1})` 使用不同的旋轉速度：

```
θₖ = 10000^(-2k/d)    for k = 0, 1, ..., d/2 - 1
```

位置 `m` 的完整旋轉矩陣為一個塊對角矩陣：

```
R(m) = diag(R₂(mθ₀), R₂(mθ₁), ..., R₂(mθ_{d/2-1}))
```

其中 `R₂(φ)` 是二維旋轉矩陣 `[[cos φ, -sin φ], [sin φ, cos φ]]`。

### 應用於注意力

RoPE 應用於 attention 計算中的 query 和 key 向量：

```
q_m' = R(m) · q_m
k_n' = R(n) · k_n
```

注意力分數計算變為：

```
score(q_m, k_n) = (R(m)·q_m)ᵀ · (R(n)·k_n)
                = q_mᵀ · R(m)ᵀ · R(n) · k_n
                = q_mᵀ · R(n-m) · k_n
```

關鍵性質：**`R(m)ᵀ · R(n) = R(n-m)`** — 旋轉矩陣的正交性使得相對位置 `n-m` 自然出現。這意味著 query 和 key 的點積只依賴於它們的**相對位置差**而非絕對位置。

### 為什麼只旋轉 Q 和 K，不旋轉 V？

`Attention = softmax(Q · Kᵀ / √d) · V` — Q·Kᵀ 決定權重分配，位置資訊必須注入此點積。V 只參與加權平均 `∑ αᵢ vᵢ`，權重 `αᵢ` 已由 Q·Kᵀ 決定；若 V 也旋轉，輸出 `∑ αᵢ R(i) vᵢ` 會引入依賴絕對位置的相位偏移。**位置影響的是「注意力分配給誰」而非「被分配的內容本身」**。

## 頻率選擇的直覺

### 為什麼 θₖ = 10000^(-2k/d) ？

這個公式源自 sinusoidal 位置編碼，背後有兩個關鍵設計：

**1. 幾何級數衰減**

```
θ₀ = 10000^(0/d)   = 1           (最快旋轉)
θ₁ = 10000^(-2/d)
θ₂ = 10000^(-4/d)
...
θ_{d/2-1} = 10000^(-(d-2)/d) ≈ 1/10000  (最慢旋轉)
```

頻率從 `1` 到 `1/10000` 呈幾何級數衰減。這保證了：
- 低維度（小 k，高頻）捕捉短距離的局部依賴
- 高維度（大 k，低頻）捕捉長距離的全局依賴

**2. 基底 10000 的選擇**

10000 是經驗值。增大基底（如 500000）會讓所有頻率降低，使旋轉更慢，等同於在相同位置索引下壓縮了旋轉角度。這正是 **NTK-aware 縮放** 和 **YaRN** 等方法調整基底來擴展上下文長度的理論基礎。

**3. 旋轉速度**

```
維度索引   θₖ         旋轉一圈所需位置數
k=0      1.000        2π ≈ 6 步
k=1      0.021        ~299 步
k=2      0.00046      ~13657 步
k=31     2.1e-7       ~3千萬步（幾乎不轉）
```

前幾個維度幾步就轉完一圈，中間維度幾百步轉一圈，最後的維度幾乎靜止，確保在任意位置範圍內總有一些維度能提供有效的角度差異。

## 具體數值範例

假設 `d=4`、`θ₀=1`、`θ₁=0.01`、位置 `m=2` 的 query `q₂=[1,0,0.5,0]`、位置 `n=5` 的 key `k₅=[0.8,0.6,0.3,0.4]`。

角度：`mθ₀=2.0, mθ₁=0.02, nθ₀=5.0, nθ₁=0.05, Δθ₀=3.0, Δθ₁=0.03`

子空間 1：`Rot(q₂,2)≈[-0.416,0.909]`，`Rot(k₅,5)≈[0.802,-0.597]`
子空間 2：`Rot(q₂,2)≈[0.4999,0.01]`，`Rot(k₅,5)≈[0.2796,0.4145]`

`score = (-0.416×0.802)+(0.909×-0.597)+(0.4999×0.2796)+(0.01×0.4145) = -0.733`

使用 `q₂ᵀ·R(3)·k₅` 可得完全相同結果，驗證了注意力分數只依賴相對距離 `|n-m|`。

## 重要的數學性質

### 1. 相對位置編碼

RoPE 最關鍵的性質是注意力分數只依賴於相對位置 `(n-m)`：

```
score(q_m, k_n) = f(q_m, k_n, n-m)
```

而不是 `f(q_m, k_n, m, n)`（依賴兩個絕對位置）。這與語言的本質一致 — 「第 5 個詞和第 8 個詞的關係」比「第 5 個詞和第 8 個詞的關係」更自然地用 3 步的相對距離來描述。

### 2. 遠距離衰減

由於旋轉基底中的頻率 `θₖ` 呈幾何級數衰減，RoPE 具有**遠距離衰減**的性質：兩個位置相距越遠，它們的 query 和 key 的點積（在隨機向量假設下）的期望值越小。這符合語言中「離得越遠的詞通常關係越弱」的直覺。

### 3. 可外推到更長序列

因為 RoPE 使用連續的旋轉角度而非學習的絕對位置嵌入，模型可以推論時處理比訓練時更長的序列 — 只需將角度繼續旋轉即可。不過實際應用中仍會遇到超出訓練長度時效果下降的問題，這促進了 ALiBi、位置插值等後續研究。

## 實作細節

### mini-llm 的實作

**Step 1: 預計算頻率 (`precompute_freqs_cis`)**

```python
def precompute_freqs_cis(dim: int, end: int, theta: float = 10000.0):
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2)[: (dim // 2)].float() / dim))
    t = torch.arange(end, device=freqs.device)
    freqs = torch.outer(t, freqs).float()
    freqs_cis = torch.polar(torch.ones_like(freqs), freqs)
    return freqs_cis
```

- `theta=10000.0` — 基底頻率，控制旋轉速度的範圍
- `torch.arange(0, dim, 2)` — 取偶數索引 `[0, 2, 4, ..., dim-2]`
- `freqs` — 長度為 `dim//2` 的頻率向量 `[θ₀, θ₁, ..., θ_{d/2-1}]`
- `t` — 位置索引 `[0, 1, 2, ..., end-1]`
- `torch.outer(t, freqs)` — 外積產生形狀 `(end, dim//2)`，每個位置 `m` 對應頻率 `m·θₖ`
- `torch.polar(ones, freqs)` — 轉換為複數表示 `cos(mθₖ) + i·sin(mθₖ)`

**Step 2: 應用旋轉 (`apply_rotary_emb`)**

```python
def apply_rotary_emb(xq, xk, freqs_cis):
    xq_ = torch.view_as_complex(xq.float().reshape(*xq.shape[:-1], -1, 2))
    xk_ = torch.view_as_complex(xk.float().reshape(*xk.shape[:-1], -1, 2))
    freqs_cis = freqs_cis.unsqueeze(0).unsqueeze(2)
    xq_out = torch.view_as_real(xq_ * freqs_cis).flatten(3)
    xk_out = torch.view_as_real(xk_ * freqs_cis).flatten(3)
    return xq_out.type_as(xq), xk_out.type_as(xk)
```

關鍵技巧：使用**複數乘法**來高效實現旋轉。

解釋：
1. `xq.float().reshape(*xq.shape[:-1], -1, 2)` — 將 query 張量的最後一維分成 `(d/2, 2)` 的形狀
2. `torch.view_as_complex(...)` — 將每對 `(a, b)` 視為複數 `a + bi`
3. `xq_ * freqs_cis` — 複數乘法 `(a+bi)·(cos φ + i·sin φ)` 等價於向量旋轉
4. `torch.view_as_real(...).flatten(3)` — 將複數結果轉回實數

**為什麼用複數？**
原本的旋轉矩陣乘法需要顯式構建塊對角矩陣 `R(m)` 並進行矩陣乘法（O(d²) 計算量）。使用複數乘法後，只需要 `d/2` 次複數乘法（O(d) 計算量），並且可以充分利用 GPU 上的向量化運算。

### 張量形狀變化的逐步追蹤（`batch=2, T=4, n_heads=8, head_dim=64`）

```
xq.shape = (2,4,8,64) → reshape(..., -1,2) → (2,4,8,32,2)   [64→32 複數對]
       → view_as_complex → (2,4,8,32)  ×  freqs_cis(1,4,1,32)  [複數乘法]
       → view_as_real → (2,4,8,32,2)  →  flatten(3) → (2,4,8,64) ✓
```

全程無需顯式構建旋轉矩陣，全部透過 PyTorch 原生複數運算完成。

### 在 Attention 中的流程

以 mini-llm 的 `Attention.forward()` 為例：

```python
def forward(self, x, freqs_cis):
    B, T, C = x.shape
    q = self.wq(x).view(B, T, self.n_heads, self.head_dim)
    k = self.wk(x).view(B, T, self.n_heads, self.head_dim)
    v = self.wv(x).view(B, T, self.n_heads, self.head_dim)

    q, k = apply_rotary_emb(q, k, freqs_cis[:T])
    # ... 後續注意力計算 ...
```

1. 線性投影取得 q, k, v
2. 對 q 和 k 應用 RoPE（**僅對 q 和 k，不對 v**）
3. 後續的點積注意力計算自動反映相對位置

## 與學習式絕對位置編碼的比較

BERT 使用的**學習式絕對位置編碼（Learned Absolute Position Embedding）** 是 RoPE 出現前最常見的做法。它維護一個可訓練查詢表 `E[pos_idx]`，缺點是最大長度固定（如 512），超出需重新訓練；參數量 `max_len×d`（如 512×768≈400K）；且模型需自行從絕對位置推導相對關係。RoPE 數學上保證只依賴相對距離、0 額外參數、且可連續外推。

後續改進嘗試包括 **ALBERT** 跨層共享、**FLOATER** 用神經 ODE 建模連續嵌入、**T5 相對位置偏置**學習距離→標量的查詢表。但 RoPE 因不需參數且外推能力優越，成為現代 LLM 的事實標準（LLaMA、Mistral、Gemma、Qwen 等均採用）。

## RoPE 的變體與相關技術

### 位置插值（Position Interpolation）

直接使用 m > L 會讓旋轉角度超出訓練分布。位置插值 (Chen et al., 2023) 線性縮小位置索引：`θₖ' = θₖ × L/L'`（等效於 `m` → `m × L/L'`）。例如 2048→8192，位置 m 的旋轉等同於 `m/4` 的原始角度。代價是高頻解析度下降，短距編碼被壓縮。

### NTK-aware 縮放

對高頻和低頻差異化處理：`θₖ' = θₖ × α^(-2k/d)` 其中 `α = (L'/L)^(d/(d-2))`。**高頻幾乎不變**（保持短距解析度），**低頻大幅減慢**（擴展總距離）。實務上通常優於線性插值。

### YaRN

Peng et al. (2023) 結合 NTK 縮放與 attention logits 溫度校正：`θₖ' = θₖ × s^(-2k/d)`（`s=(L'/L)^(d/(d-2))`），同時對注意力 logits 乘以 `√(1/t)` 補償熵偏移。可在微調不到 1000 步下將上下文從 2048 擴展到 65536。

## 主流 LLM 中的 RoPE 實作

| 模型 | theta | 訓練長度 | 特殊處理 |
|------|-------|---------|---------|
| LLaMA 1/2 | 10000 | 2048/4096 | 標準，在 TransformerBlock 預計算 freqs_cis 傳入各層 |
| LLaMA 3 | 500000 | 8192 | 高基底預適配長上下文 |
| Mistral 7B | 10000 | 8192 | + sliding window attention；長上下文用插值非調基底 |
| Gemma 7B | 10000 | 8192 | RoPE + T5 relative bias 混合；部分 head 用 RoPE 部分不用 |
| Gemma 2 | 10000 | 8192 | head_dim=256（LLaMA 的兩倍），更豐富的頻率解析度 |
| Qwen 2 | 1000000 | 32768 | 極高基底 + NTK-aware |
| Yi 34B | 10000 | 4096 | 訓練時使用位置插值 |

基底選擇反映權衡：**小基底（~10000）**短上下文表現更好；**大基底（~500000+）**犧牲短距精度換取長上下文外推能力。

## 與其他位置編碼的比較

| 方法 | 相對位置 | 外推能力 | 計算量 | 參數量 |
|------|----------|----------|--------|--------|
| Sinusoidal (原始 Transformer) | 有限 | 好（連續函數） | O(d) | 0 |
| Learned Absolute (BERT) | 無 | 差（固定長度） | O(d) | O(L·d) |
| Learned Relative (T5) | 是 | 好 | O(L²d) | O(L²) |
| RoPE (mini-llm 使用) | 是 | 好 | O(d) | 0 |
| ALiBi | 是 | 非常好 | O(1) | 0 |

RoPE 在不需要額外參數、計算量低的同時兼具相對位置編碼和外推能力，是現代 LLM 的事實標準。

## 延伸閱讀

- 原始論文: Su et al., "RoFormer: Enhanced Transformer with Rotary Position Embedding" (2021)
- 理論分析: He et al., "Rethinking Positional Encoding in Language Pre-training" (2020)
- 長度外推: Chen et al., "Extending Context Window of Large Language Models via Positional Interpolation" (2023)
- ALiBi: Press et al., "Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation" (2021)
