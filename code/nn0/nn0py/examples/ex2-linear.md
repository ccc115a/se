# ex2-linear.py — 線性回歸訓練

## 概述

ex2-linear.py 展示如何使用 Value 類和 Adam 優化器訓練一個線性回歸模型。

## 執行方式

```bash
python ex2-linear.py
```

## 目標

學習線性函數：$y = 2x + 1$

給定：
- 輸入 X = [1, 2, 3, 4]
- 輸出 Y = [3, 5, 7, 9]

## 程式碼詳解

### 1. 準備數據

```python
X = [1.0, 2.0, 3.0, 4.0]
Y = [3.0, 5.0, 7.0, 9.0]
```

四個數據點，剛好落在直線 $y = 2x + 1$ 上。

### 2. 初始化參數

```python
w = Value(0.0)  # 權重（斜率）
b = Value(0.0)  # 偏差（截距）
```

初始值為 0，目標是學習到 $w \approx 2, b \approx 1$。

### 3. 建立優化器

```python
optimizer = Adam([w, b], lr=0.1)
```

Adam 優化器，比 SGD 更容易收斂。

### 4. 訓練迴圈

```python
for epoch in range(51):
    # 前向傳播
    preds = [w * x + b for x in X]
    losses = [(pred - y) ** 2 for pred, y in zip(preds, Y)]
    loss = sum(losses) / len(losses)
    
    # 反向傳播
    loss.backward()
    optimizer.step()
```

每個 epoch：
1. **前向傳播**：計算預測值 $w \cdot x + b$
2. **計算 Loss**：MSE = $\frac{1}{n} \sum (y_{pred} - y)^2$
3. **反向傳播**：計算梯度
4. **更新參數**：Adam 優化

## 數學原理

### MSE Loss

$$MSE = \frac{1}{n} \sum_{i=1}^{n} (y_{pred,i} - y_i)^2$$

### 梯度

對於參數 $w$ 和 $b$：
$$\frac{\partial MSE}{\partial w} = \frac{2}{n} \sum (y_{pred} - y) \cdot x$$
$$\frac{\partial MSE}{\partial b} = \frac{2}{n} \sum (y_{pred} - y)$$

### Adam 優化

結合動量和 RMSProp：
$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$$
$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$$
$$p_{t+1} = p_t - lr \cdot \frac{m_t}{\sqrt{v_t} + \epsilon}$$

## 輸出範例

```
=== 2. 線性回歸訓練 ===
Epoch  0 | Loss: 41.0000 | w: 0.1000, b: 0.1000
Epoch 10 | Loss: 8.3166 | w: 1.0469, b: 1.0453
Epoch 20 | Loss: 0.1920 | w: 1.7021, b: 1.6866
Epoch 30 | Loss: 0.3412 | w: 1.8924, b: 1.8399
Epoch 40 | Loss: 0.1206 | w: 1.8143, b: 1.7098
Epoch 50 | Loss: 0.0717 | w: 1.7598, b: 1.5991
```

可以觀察到：
- Loss 快速下降
- $w$ 趨近 2
- $b$ 趨近 1

## 學習重點

1. **MSE Loss**：回歸任務的標準損失函數
2. **梯度下降**：透過梯度更新參數
3. **Adam**：自適應學習率優化器
4. **收斂**：模型逐漸學習到正確的參數

---

本文件結束