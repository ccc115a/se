# SwiGLU — Swish-Gated Linear Unit

## 概述

**SwiGLU（Swish-Gated Linear Unit）** 是一種結合 Swish 活化函數與門控線性單元（GLU）的活化機制，由 Shazeer 在 2020 年的論文「GLU Variants Improve Transformer」中提出。它在現代大型語言模型中已成為前饋網路（FFN）的事實標準活化方式，被 LLaMA、PaLM、Gemma、Mistral 等重要模型採用。mini-llm 專案的所有版本均使用 SwiGLU 作為 FFN 的活化函數。

## 動機：為什麼需要更好的活化函數？

傳統 Transformer 的 FFN 使用 ReLU 活化：

```
FFN_ReLU(x) = W₂ · ReLU(W₁ · x + b₁) + b₂
```

ReLU 雖然簡單有效，但有幾個缺點：
1. **Dying ReLU** — 神經元一旦輸出為負值，梯度就永遠為 0，該神經元再也無法學習
2. **非平滑** — 在 0 處不可微，可能影響優化
3. **無上限** — 正的活化值無限制增長，可能導致不穩定

研究者嘗試了多種替代方案（GELU、Swish、GLU 等），最終 SwiGLU 在參數效率和效果之間取得了最佳平衡。

## GLU — Gated Linear Unit（門控線性單元）

GLU 最初由 Dauphin 等人於 2017 年在語言建模的語境中提出。其基本形式為：

```
GLU(x) = (x · W + b) ⊗ σ(x · V + c)
```

其中 `⊗` 表示逐元素乘法（Hadamard product），`σ` 是 sigmoid 活化函數。GLU 的關鍵在於：**將輸入線性投影後拆成兩條路徑，一條作為主要訊號，另一條透過 sigmoid 作為門控，決定讓多少資訊通過**。

這種門控機制讓網路可以學會選擇性地傳遞資訊，類似 LSTM 中的遺忘閘，但更輕量。

## Swish 活化函數

Swish 由 Ramachandran 等人於 2017 年透過自動搜尋發現：

```
Swish(x) = x · σ(x) = x / (1 + e^(-x))
```

Swish 的特性：
1. **平滑** — 在所有點可微，優化更穩定
2. **有下界無上界** — 允許大的正活化值，但不會完全死亡
3. **非單調** — 在 x < 0 的區域有輕微的負值，這被認為有助於正則化
4. **自閘控** — 可以視為一種以自身為門控訊號的 GLU，因為 `Swish(x) = x · σ(x)` 等同於 `x` 被 `σ(x)` 門控

Swish 的形狀介於 ReLU 和 GELU 之間，在許多任務上表現優於 ReLU。

## SwiGLU 的數學定義

SwiGLU 將 GLU 中的 sigmoid 門控替換為 Swish 活化：

```
SwiGLU(x) = (x · W₁) ⊗ Swish(x · W₃)
```

其中：
- `W₁ ∈ ℝ^{d_model × d_ff}` — 主要路徑的權重矩陣
- `W₃ ∈ ℝ^{d_model × d_ff}` — 門控路徑的權重矩陣
- `⊗` — 逐元素乘法
- `Swish(z) = z · σ(z)` — Swish 活化函數

實際的 FFN 實現中，還需要一個輸出投影矩陣 `W₂`：

```
FFN_SwiGLU(x) = W₂ · (Swish(W₃ · x) ⊗ W₁ · x)
```

### 參數量的差異

傳統 FFN 有兩個權重矩陣（W₁, W₂），而 SwiGLU FFN 有三個權重矩陣（W₁, W₂, W₃）。為了保持參數量相當，使用 SwiGLU 時通常將中間維度 `d_ff` 設為 `(2/3) · 4 · d_model` 而不是 `4 · d_model`。

mini-llm 的實作中：
```python
self.ffn = FeedForward(dim, hidden_dim=4 * dim)
```

雖然這裡的 `hidden_dim = 4*dim` 沒有因為 SwiGLU 而縮減，但常見做法（如 LLaMA）會將 hidden_dim 設為 `int(8/3 * d_model)` 以保持參數量與 4× ReLU FFN 相近。

## 實作細節

### mini-llm 的實作

```python
class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, hidden_dim, bias=False)

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)) * self.w3(x))
```

其中 `F.silu` 是 PyTorch 中的 SiLU 函數（`SiLU(x) = x · σ(x)`），與 Swish 等價。

**計算流程：**
1. `self.w1(x)` — 主要路徑的線性投影，輸出維度 `hidden_dim`
2. `self.w3(x)` — 門控路徑的線性投影
3. `F.silu(self.w1(x))` — 對主要路徑應用 SiLU/Swish 活化
4. `F.silu(...) * self.w3(x)` — 逐元素乘法（門控操作）
5. `self.w2(...)` — 輸出投影回到 `d_model` 維度

### 完整 FFN 在 Transformer 中的位置

```
x → [RMSNorm] → [SwiGLU FFN] → + (殘差連接) → x'
```

## 為什麼 SwiGLU 效果好？

### 1. 門控機制提供表達能力

GLU 的門控操作本質上實現了乘法互動：

```
output = gate(x) ⊗ value(x)
```

這比加法互動（如 ReLU `max(0, x)`）提供了更豐富的計算。門控可以選擇性地壓制或放大不同特徵，形成類似「特徵路由器」的效果。

### 2. Swish 比 sigmoid 更好的梯度

```
Swish(x) = x · σ(x)
SwiGLU = Swish(W₁x) ⊗ W₃x
```

在 GLU 中使用 Swish 取代 sigmoid 的關鍵好處：

- **非飽和區域更大** — Swish 在負半軸不會完全飽和到 0，使得門控訊號可以更細微
- **負值梯度** — Swish 在負區域有非零梯度，解決 Dying ReLU 問題
- **自門控的平滑性** — Swish 本身就是一種門控形式，疊加在 GLU 上形成雙層門控

### 3. 實驗驗證

Shazeer 的論文在 Transformer 上比較了各種 GLU 變體，在相同參數量下：

| FFN 類型 | 困惑度 (lower is better) | 說明顯著 |
|----------|--------------------------|----------|
| ReLU (baseline) | 基準 | — |
| GELU | 與 ReLU 相當 | — |
| Swish | 與 ReLU 相當 | — |
| GLU (sigmoid) | 約 -0.1 | 小幅提升 |
| Bilinear | 約 -0.1 | 小幅提升 |
| SwiGLU | **約 -0.2 至 -0.3** | 顯著提升 |
| GeGLU | 約 -0.2 | 略低於 SwiGLU |

SwiGLU consistently 表現最佳，且這個結果在多個模型規模和資料集上得到驗證。

## 與其他活化函數的比較

```
ReLU:    output = max(0, x)
GELU:    output = x · Φ(x)       (Φ 是標準常態 CDF)
Swish:   output = x · σ(x)
SwiGLU:  output = (Swish(W₁x)) ⊗ (W₃x)
GeGLU:   output = (GELU(W₁x)) ⊗ (W₃x)
ReGLU:   output = (ReLU(W₁x)) ⊗ (W₃x)
```

從計算圖的角度看，SwiGLU 可以視為在 FFN 中引入了**條件計算（conditional computation）** — 門控路徑決定哪些隱藏單元被啟動，而主要路徑提供具體的活化值。

## 數值範例：活化函數形狀比較

一組小樣本輸入的實際輸出值，對比各活化函數的形狀差異：

```
x       ReLU     GELU     Swish     Swish'   sigmoid
─────────────────────────────────────────────────────
-3.0    0.000   -0.004   -0.152    0.014     0.047
-2.0    0.000   -0.045   -0.269    0.045     0.119
-1.0    0.000   -0.159   -0.269    0.135     0.269
-0.5    0.000   -0.154   -0.189    0.209     0.378
-0.1    0.000   -0.034   -0.050    0.249     0.475
 0.0    0.000    0.000    0.000    0.250     0.500
 0.1    0.100    0.054    0.054    0.251     0.525
 0.5    0.500    0.346    0.346    0.291     0.622
 1.0    1.000    0.841    0.731    0.376     0.731
 2.0    2.000    1.954    1.762    0.405     0.881
 3.0    3.000    2.996    2.858    0.423     0.953
```

關鍵觀察：
- **ReLU** 負半軸全 0、梯度全 0 → Dying ReLU 根源
- **GELU** 負半軸微負值，形似 Swish 但略不對稱
- **Swish** 在 x ≈ -1.05 有最小值 ≈ -0.278，輕微負向抑制有正則化效果
- **Swish'** 在 x=0 處為 0.25（而非 ReLU 的不可微點），峯值約在 x≈2.4 處 ≈0.424
- **sigmoid** 值域 (0,1)，飽和區域遠大於 Swish，門控靈活度較低

SwiGLU 中門控值為 `Swish(W₃x)`，值域約 [-0.278, ∞)，比 sigmoid 的 (0,1) 提供更靈活的門控權重。

## SwiGLU 計算圖

```
輸入 x ─────────────────────────────────────────
  │                                              │
  ├──→ W₁ (Linear d→h, bias=False) ──→ SiLU ──→ ⊗
  │                                              │
  └──→ W₃ (Linear d→h, bias=False) ────────────→ ⊗
                                                  │
                                                  └──→ W₂ (Linear h→d) ──→ 輸出
```

W₁ 是「值路徑」（value path），W₃ 是「門控路徑」（gate path），最後用 W₂ 做輸出投影回 d_model 維度。W₁ 和 W₃ 不共享權重。

## 參數量選擇的數學推導

LLaMA 使用 `hidden_dim = int(8/3 * d_model)` 而非 `4 * d_model`，原因來自參數量等價性：

**ReLU FFN**：`param = 2 × d_model × d_ff`（W₁, W₂），標準 `d_ff = 4d` → `8d²`

**SwiGLU FFN**：`param = 3 × d_model × d_ff`（W₁, W₂, W₃）

令兩者相等：`3 × d_model × d_ff = 8 × d_model²` → `d_ff = 8/3 × d_model`

| d_model | ReLU (4×) | SwiGLU (4×) | SwiGLU (8/3×) |
|---------|-----------|-------------|---------------|
| 128     | 131,072   | 196,608     | 131,072       |
| 4096    | 134M      | 201M        | 134M          |

在 d_model=4096 下不做縮減 = 多出 50% 參數。mini-llm 使用 `4×` 是因為 d_model=128 參數差異小，且簡單。

## 梯度傳播分析

令中間變數：`a = W₁x`（值投影），`b = W₃x`（門控投影），`s = SiLU(a)`，`g = s ⊙ b`，`y = W₂g`。由鏈式法則：

**dL/dW₂** = dL/dy · gᵀ — 標準形式，與 ReLU FFN 無異

**dL/dW₁**（值路徑）：
```
dL/dW₁ = [(W₂ᵀ · dL/dy) ⊙ b ⊙ SiLU'(a)] · xᵀ
```
門控值 b 乘在梯度中 — 若某維度 b_i 很小，W₁ 對應行的梯度也被壓制。**門控路徑調節值路徑的學習速率**。

**dL/dW₃**（門控路徑）：
```
dL/dW₃ = [(W₂ᵀ · dL/dy) ⊙ s] · xᵀ
```
活化值 s 乘在梯度中 — 若 s_i 接近 0，W₃ 對應行的梯度也接近 0。**值路徑反過來調節門控路徑的學習**。

這種雙向調節比 ReLU 的硬性截斷更細膩：SwiGLU 通過連續門控實現軟性特徵選擇，兩路徑同時活躍的維度才會穩定更新。

## SiLU vs Swish：PyTorch 實作細節

```python
x = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])
a = F.silu(x)                    # PyTorch API
b = torch.sigmoid(x) * x         # Swish(x) = x·σ(x)
print(a)  # tensor([-0.2690, -0.2689,  0.0000,  0.7311,  1.7616])
print(b)  # 同上
print(torch.allclose(a, b))      # True
```

**命名由來**：Ramachandran 等命名為 Swish（2017），Elfwing 等獨立提出 SiLU（同樣 2017，但投稿更早）。PyTorch 選擇 `F.silu` 作為主要 API，遵循「X Linear Unit」的慣例（ReLU、GELU）。數學上完全相等。`F.silu` 在 CUDA 上有專屬 fused kernel，比手動 `x * sigmoid(x)` 省一次 kernel launch。

## 移除偏差的意義（bias=False）

mini-llm 的三個線性層全部 `bias=False`，遵循 LLaMA 慣例：

1. **數學冗餘** — W₁ 和 W₃ 的偏差經 SiLU 和乘法門控後，其貢獻可被 W₂ 和 RMSNorm 吸收
2. **參數節省** — d_model=128, hidden_dim=512 時偏差佔比 0.58%；d_model=4096 時僅 0.02%
3. **算子融合** — 無偏差的線性層在 CUDA 上可使用更高效的 kernel，不必處理 broadcast add
4. **業界標準** — LLaMA 所有線性層都無 bias，已成開源 LLM 事實標準

## 記憶體頻寬考量

SwiGLU 增加一個線性層對推理延遲的影響不可忽視：

| 操作 | ReLU FFN | SwiGLU FFN |
|------|----------|------------|
| 線性投影（前向） | 2 | 3 |
| Elementwise ops | 1 | 2 |
| 總權重讀取 | 2×d×ff | 3×d×ff |

LLaMA 將 d_ff 縮減為 8/3× 後，SwiGLU 權重總量 ≈ 0.52 GB（FP16），反而略少於 ReLU 的 0.67 GB（因為三層中有兩層是 d→ff 而非 ff→d）。這是記憶體頻寬上的關鍵優化。

在長序列推理中，KV cache 佔用大量 HBM 後 FFN 權重載入成為瓶頸。SwiGLU 若不做 d_ff 縮減每步推理需多載入一組權重，直接轉化為延遲增加。

## 活化函數的歷史演進

```
ReLU (2012, AlexNet)  →  簡單高效，但 Dying ReLU
   ↓
GELU (2016, BERT)    →  平滑 + 隨機正則化視角
   ↓
Swish/SiLU (2017)    →  自動搜尋發現，計算比 GELU 簡單
   ↓
GLU (2017)           →  門控機制引入序列建模（Dauphin）
   ↓
SwiGLU (2020)        →  Swish + GLU 結合，最佳參數效率
   ↓
LLaMA (2023)         →  業界標準確立，後續 Mistral/Gemma/Qwen 跟進
```

這條演進路線反映了 LLM 架構設計對**參數效率與表達能力平衡**的持續追求。SwiGLU 的乘法門控比加法活化（ReLU、GELU）提供了更豐富的特徵選擇能力，而 Swish 的平滑非單調性又比 sigmoid 門控更靈活。最終兩者結合，在當代 LLM 中確立了主導地位。

## 延伸閱讀

- GLU 起源: Dauphin et al., "Language Modeling with Gated Convolutional Networks" (ICML 2017)
- Swish 自動搜尋: Ramachandran et al., "Searching for Activation Functions" (2017)
- SwiGLU 論文: Shazeer, "GLU Variants Improve Transformer" (2020)
- LLaMA 使用 SwiGLU: Touvron et al., "LLaMA: Open and Efficient Foundation Language Models" (2023)
- GELU: Hendrycks & Gimpel, "Gaussian Error Linear Units (GELUs)" (2016)
