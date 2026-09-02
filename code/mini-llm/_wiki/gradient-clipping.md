# Gradient Clipping — 梯度裁切

## 概述

**Gradient Clipping（梯度裁切）** 是一種訓練穩定技術，在反向傳播計算出梯度後、應用最佳化器更新前，對梯度進行縮放或裁切，限制其大小不超過預設閾值。這能有效防止**梯度爆炸（Gradient Explosion）** — 梯度在深層網路中指數級增長導致訓練不穩定。mini-llm 在所有版本的訓練中都使用了梯度裁切。

## 動機：為什麼需要梯度裁切？

### 梯度爆炸

在深度神經網路中，特別是在 RNN 或深層 Transformer 中，梯度在反向傳播過程中可能指數級增長。原因：

1. **權重矩陣的奇異值** — 如果權重矩陣的最大奇異值 > 1，梯度會隨著層數指數增長
2. **長序列依賴** — 在語言模型中，梯度需要傳播過長序列（因果注意力），可能累積過大
3. **資料中的異常值** — 某些樣本的損失特別大，導致的梯度也特別大

### 梯度爆炸的症狀

- Loss 突然變為 NaN
- Loss 值跳躍不穩定
- 參數更新後模型輸出變成 NaN
- 訓練曲線出現垂直尖峰

### 梯度爆炸的數學解釋

考慮一個簡單的線性鏈：`f(x) = wₙ · w_{n-1} · ... · w₁ · x`

損失對 `w₁` 的梯度包含項 `wₙ · w_{n-1} · ... · w₂`。如果每個 `|w| > 1`，這個乘積會指數增長：

```
如果 |w| = 1.1, n = 100 → |w|¹⁰⁰ ≈ 13780 倍放大
如果 |w| = 0.9, n = 100 → |w|¹⁰⁰ ≈ 0.00003 倍縮小（梯度消失）
```

## 梯度裁切的類型

### 1. 值裁切（Value Clipping）

將梯度逐元素限制在 `[-threshold, threshold]` 範圍內：

```python
torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=1.0)
```

- 每個梯度的每個元素被獨立裁切
- 適合於已知梯度不應超出特定範圍的場景
- 缺點：失去梯度的方向資訊

### 2. 範數裁切（Norm Clipping）— mini-llm 使用

計算所有梯度的 L2 範數，如果超過閾值則對所有梯度進行縮放：

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

所有梯度乘以 `min(1, max_norm / total_norm)`，因此**保留方向但限制大小**：

```
if ||g||₂ > max_norm:
    g' = (max_norm / ||g||₂) · g
else:
    g' = g
```

這是 mini-llm 使用的方式，也是語言模型訓練中最常見的選擇。

## mini-llm 的實作

```python
optimizer.zero_grad(set_to_none=True)
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
optimizer.step()
```

這個順序（backward → clip → step）是標準做法：
1. `loss.backward()`：計算所有參數的梯度
2. `clip_grad_norm_()`：就地修改梯度張量
3. `optimizer.step()`：使用修改後的梯度更新參數

### `set_to_none=True` 的效能優化

在 `optimizer.zero_grad(set_to_none=True)` 中，將梯度設為 `None` 而非零張量：

- PyTorch 直接釋放梯度張量的記憶體，而非將所有元素填零
- 下次 `backward()` 時重新分配新張量
- 減少記憶體寫入操作（zeroing 需要 O(n) 寫入，設為 None 是 O(1) 的指標操作）
- 在大型模型上可節省 5-15% 的訓練時間

效能差異來自：`set_to_none=False`（預設）會遍歷所有參數並將梯度張量原地填零，需要完整的記憶體頻寬寫入；`set_to_none=True` 只是將梯度屬性設為 `None`，舊張量由垃圾回收自動處理。

注意事項：某些舊版最佳化器或自訂程式碼可能依賴 `grad` 始終是張量而非 `None`，此時使用 `set_to_none=True` 可能導致 `AttributeError`。PyTorch 1.7+ 的最佳化器已完全支援此功能。

### 在 mini-llm 中的效果

mini-llm 模型只有 ~0.8M 參數，深度為 3-4 層 Transformer，梯度爆炸的風險較低。但梯度裁切仍然有正面效果：

1. **即使小模型也可能遇到異常梯度** — 隨機批次中的「困難樣本」可能導致梯度異常大
2. **訓練更平滑** — 裁切後的 Loss 曲線波動更小
3. **允許更高的學習率** — 因為知道極端梯度會被限制，可以放心使用較高學習率加速訓練

## 範數裁切的數學細節

### 全域範數計算

`clip_grad_norm_` 計算所有參數梯度的 L2 範數：

```
||g||₂ = sqrt(Σ_{所有參數} ||g_param||₂²)

其中 ||g_param||₂ = sqrt(Σ g_i²) 是每個參數張量的 L2 範數
```

### 縮放因子

```
scale = min(1, max_norm / ||g||₂)
g' = scale · g
```

當 `||g||₂ > max_norm`，縮放因子 `max_norm/||g||₂ < 1`，所有梯度按比例縮小。

### 方向保持性

關鍵性質：範數裁切**保持梯度的方向不變**。

```
g' / ||g'||₂ = (scale·g) / ||scale·g||₂ = g / ||g||₂
```

這與值裁切不同（值裁切會改變方向）。方向保持性意味著最佳化器仍然收到正確的更新方向，只是步長被限制。

## 具體數值範例

假設一個小型 Transformer 有兩個參數張量的梯度：
- W₁ (2×2): `[[0.5, -0.3], [0.8, 0.1]]` → `||g||₂ = sqrt(0.99) ≈ 0.995`
- W₂ (2×1): `[[1.5], [-2.0]]` → `||g||₂ = sqrt(6.25) = 2.5`

全域範數：`||g||₂ = sqrt(0.99 + 6.25) ≈ 2.69`

設定 `max_norm = 1.0`，縮放因子 `scale = 1.0 / 2.69 ≈ 0.372`：

```
g'_W₁ = 0.372 × [[0.5, -0.3], [0.8, 0.1]] ≈ [[0.186, -0.112], [0.298, 0.037]]
g'_W₂ = 0.372 × [[1.5], [-2.0]] ≈ [[0.558], [-0.744]]
```

裁切後 `||g'||₂ = 0.372 × 2.69 = 1.0` ✓。若未裁切（lr=0.01），`W₂` 的更新幅度為 0.02；裁切後降至 0.00744，防止過度更新。

對比值裁切 `clip_value=1.0`：W₂ 的梯度裁為 `[[1.0], [-1.0]]`，方向從約 -53.1° 變成 -45°（方向改變），而範數裁切保留了方向。

## PyTorch 內部實作機制

`clip_grad_norm_` 的實作流程：

1. 將 `parameters` 生成器轉為 list，確保可多次遍歷
2. 對每個參數，若 `p.grad` 非 None，計算其 L2 範數並平方後加總
3. 取總和的平方根得到全域範數 `total_norm`
4. 計算縮放因子 `clip_coef = max_norm / (total_norm + 1e-6)`
5. 若 `clip_coef < 1.0`，遍歷參數並對梯度執行原地縮放 `p.grad.data.mul_(clip_coef)`
6. 返回裁切前的 `total_norm` 供監控使用

實作重點：
- **兩次遍歷**：第一次計算範數，第二次縮放，但在現代 GPU 上開銷 < 1% 訓練時間
- **原地修改**：`mul_()` 直接修改梯度張量，不創建新物件
- **安全除零**：`1e-6` 防止梯度全零時除零錯誤
- **回傳值特性**：無論是否發生裁切，都返回原始的 `total_norm`，可用於監控梯度的真實規模

## 選擇裁切閾值

### 經驗法則

- **max_norm = 1.0** — 常用於 Transformer 和 RNN（mini-llm 使用）
- **max_norm = 0.5 到 5.0** — 取決於模型大小和架構
- **監控梯度範數** — 理想情況下，大部分步驟的梯度範數應在閾值以下

### 梯度的統計分析

如果能夠監控訓練過程中的梯度範數分布：

- 如果 `||g||₂` 始終低於 `max_norm`，閾值過大（裁切幾乎不發生）
- 如果 `||g||₂` 經常被裁切（> 50% 的步驟），閾值可能過小
- 如果偶爾出現極大值（> 10× 中位數），裁切正在發揮作用

mini-llm 是一個示範專案，沒有實作梯度監控工具，但在生產系統中這是非常有用的診斷資訊。

## 梯度爆炸 ResNet 時代的啟示

在 ResNet 出現之前，非常深的神經網路（如 20+ 層的 plain CNN）在訓練時經常遇到梯度爆炸問題。ResNet 的跳躍連接（skip connections）讓梯度可以繞過權重層直接傳播，大幅緩解了梯度爆炸，但未完全消除：

```
ResNet: y = x + F(x)  →  ∂y/∂x = 1 + ∂F/∂x
```

Transformer 的殘差連接（residual connection）與 ResNet 原理相同，使得深層 Transformer 的梯度爆炸問題比同樣深度的 plain 網路輕微。LLM 仍然使用梯度裁切作為額外的安全機制。

## 梯度消失 vs 梯度爆炸

| 問題 | 梯度消失 | 梯度爆炸 |
|------|---------|---------|
| 現象 | 梯度接近零，參數不更新 | 梯度過大，參數劇烈震盪 |
| 根本原因 | 權重矩陣奇異值 < 1 | 權重矩陣奇異值 > 1 |
| 常見場景 | 深層 Sigmoid 網路 | RNN / 深層 Transformer |
| 解決方案 | 殘差連接、ReLU、初始化 | 梯度裁切、殘差連接 |

梯度裁切只限制梯度的最大值，無法解決梯度消失。後者的解法包括 ReLU/GELU（導數恆為 1）、殘差連接（跳躍路徑讓梯度繞過權重層）、以及 Xavier/Kaiming 初始化。

混合精度訓練使用另一種縮放機制 — `GradScaler` 放大損失再 backward，防止 FP16 梯度下溢（underflow）。裁切必須在 `scaler.unscale_()` 之後進行，否則縮放後的梯度會誤觸閾值：

```python
scaler.scale(loss).backward()
scaler.unscale_(optimizer)
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
scaler.step(optimizer)
scaler.update()
```

## 梯度裁切 vs 梯度累積

| 技術 | 目的 | 機制 |
|------|------|------|
| 梯度裁切 | 防止梯度爆炸 | 縮放過大的梯度 |
| 梯度累積 | 實現有效的較大 batch | 多個 batch 的梯度求和後一次更新 |

### 與梯度累積的組合策略

兩者可以同時使用，但需要注意順序：

```python
accumulation_steps = 4
optimizer.zero_grad(set_to_none=True)
for micro_step in range(accumulation_steps):
    loss = model(x[micro_step]) / accumulation_steps
    loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

關鍵點：
1. **損失除以累積步數**：多個 micro-batch 梯度相加，為保持與單一大 batch 相同的梯度規模，需將損失除以 `accumulation_steps`
2. **裁切在累積後**：全部 micro-batch 完成 backward 後，對總梯度進行一次裁切
3. **閾值調整**：梯度累積後的全域範數約放大 `sqrt(accumulation_steps)` 倍（假設梯度獨立），可能需要適度提高 `max_norm`

## 梯度雜訊與隨機批次

SGD 的 mini-batch 梯度是全域梯度的雜訊估計：`g_batch = g_true + ε, ε ~ N(0, Σ/|B|)`。批次越小雜訊越大，裁剪的作用：

- **抑制極端雜訊** — 含異常樣本的 batch 產生的過大梯度被抑制
- **引入輕微偏差** — 頻繁裁切使梯度估計略低估真實大小，但實務影響很小
- **小 batch 更易觸發** — 梯度波動大，裁切頻率較高；大 batch 反之

裁切發生在動量計算之前（Adam 使用 `g'` 而非 `g` 計算一階動量），因此不僅限制當前更新幅度，也防止異常梯度汙染動量估計。

## 實務建議

1. **從小閾值開始** — 建議從 `max_norm = 1.0` 開始
2. **如果訓練不穩定** — 嘗試降低 `max_norm` 到 0.5 或 0.25
3. **與學習率一起調整** — 較高的學習率可能需要更低的裁切閾值
4. **與 weight decay 的互動** — AdamW 的權重衰減在梯度裁切後應用，所以裁切不影響正則化

### 學習率與裁切閾值的關係

裁切閾值和學習率共同決定參數更新的實際步長。有效更新幅度為：

```
Δθ = lr × scale × g, 其中 scale = min(1, max_norm / ||g||₂)
```

若學習率提高而 max_norm 不變，裁切後的更新步長不會超過 `lr × max_norm`，相當於對有效步長施加了上限。這解釋了為什麼高學習率常搭配緊縮的裁切：在學習率 1e-3 時 max_norm=1.0 可接受，但學習率 1e-2 時可能需要 max_norm=0.1。

### 實戰監控：記錄梯度範數

```python
def log_gradient_norm(model, logger, step):
    total_norm = torch.nn.utils.clip_grad_norm_(
        model.parameters(), max_norm=float('inf'))
    logger.info(f"Step {step} | gradient norm: {total_norm:.4f}")
```

`clip_grad_norm_` 回傳裁切前的全域範數，設 `max_norm=inf` 則不回傳、僅回傳數值。逐層監控可診斷異常：

```python
norms = [(n, p.grad.norm().item())
         for n, p in model.named_parameters() if p.grad is not None]
```

Embedding 層和輸出層最易出現極端梯度，若某層持續比其他層大 100× 以上，可能有初始化或架構問題。

## 健康與不健康的梯度分佈

健康訓練的梯度範數特徵：中位數約 0.1-1.0、近似對數常態分佈、隨訓練衰減、層間差距不超過 1-2 個數量級。

不健康的模式：

| 模式 | 現象 | 可能原因 |
|------|------|---------|
| 梯度爆炸 | 範數 > 100，Loss 變 NaN | 學習率過高、資料異常 |
| 梯度消失 | 所有層範數 < 1e-6 | 深度過大、激活函數不當 |
| 梯度不對稱 | 輸出層大但輸入層近乎零 | 梯度消失但局部尚可 |
| 週期性尖峰 | 每固定步數出現尖峰 | 資料順序不均 |
| 裁切觸發率過高 | > 50% 的步驟被裁切 | max_norm 過低 |

透過裁切比率調整策略：

```python
clip_ratio = sum(n > max_norm for n in grad_norms) / len(grad_norms)
if clip_ratio > 0.3:   # 增加 max_norm 或降低 LR
elif clip_ratio < 0.01: # 考慮降低 max_norm 或提高 LR
```

mini-llm 中典型的梯度範數約 0.5-3.0，`max_norm=1.0` 時約 10-20% 步驟被裁切，是合理的比率。

## 延伸閱讀

- 梯度裁切的原始提案: Pascanu et al., "On the difficulty of training Recurrent Neural Networks" (ICML 2013)
- 梯度爆炸的理論分析: Bengio et al., "Learning Long-Term Dependencies with Gradient Descent is Difficult" (IEEE NN 1994)
- ResNet 與跳躍連接: He et al., "Deep Residual Learning for Image Recognition" (CVPR 2016)
- PyTorch 實作: torch.nn.utils.clip_grad_norm_ 文件
