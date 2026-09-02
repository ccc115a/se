# ex4-classify.py — Softmax 與 Cross-Entropy Loss

## 概述

ex4-classify.py 展示如何實現數值穩定的 Softmax 和 Cross-Entropy Loss，這是分類任務的核心。

## 執行方式

```bash
python ex4-classify.py
```

## 程式碼詳解

### 1. Softmax

```python
logits = [Value(2.0), Value(1.0), Value(0.1)]
probs = softmax(logits)
```

Softmax 將分數轉換為機率分布：
$$p_i = \frac{e^{x_i}}{\sum_j e^{x_j}}$$

### 2. 數值穩定問題

直接計算 $e^x$ 可能溢位（當 $x > 700$）。解決方案：

$$p_i = \frac{e^{x_i - M}}{\sum_j e^{x_j - M}}$$

其中 $M = \max(x)$。

### 3. Cross-Entropy Loss

```python
loss = -probs[target_idx].log()
```

$$L = -\log(p_{target})$$

當預測正確時（$p \to 1$），$L \to 0$。
當預測錯誤時（$p \to 0$），$L \to \infty$。

### 4. 反向傳播

```python
loss.backward()
```

梯度計算：
$$\frac{\partial L}{\partial x_i} = p_i - \delta_{i,target}$$

- 正確類別梯度：$p_i - 1$（負的，降低輸出）
- 錯誤類別梯度：$p_i - 0$（正的，增加輸出）

## 數學原理

### Softmax

$$p_i = \frac{e^{x_i}}{\sum_j e^{x_j}}$$

### Cross-Entropy

$$L = -\sum_i y_i \log(p_i)$$

對於單一目標：
$$L = -\log(p_{target})$$

### Log-Sum-Exp 技巧

$$L = \log \left( \sum_j e^{x_j} \right) - x_{target}$$

$$= \log \left( \sum_j e^{x_j - M} \right) + M - x_{target}$$

這避免了直接計算 Softmax 可能導致的 $\log(0)$ 錯誤。

## 輸出範例

```
=== 4. Softmax 與 Cross-Entropy Loss ===
Logits    : [2.0, 1.0, 0.1]
Probs     : [0.6590, 0.2420, 0.0990]
Loss      : 0.4170
Logits 梯度: [-0.341, 0.242, 0.099]
```

解釋：
- 第一個類別（正確）的 logit 是 2.0，機率最高
- Loss = $-\log(0.659) = 0.417$
- 梯度：正確類別減少，其他類別增加

## 學習重點

1. **Softmax**：分數到機率的轉換
2. **數值穩定**：最大值平移技巧
3. **Cross-Entropy**：分類任務的標準損失
4. **梯度**：正確類別減少，其他類別增加

---

本文件結束