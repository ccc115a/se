# ex3-xor.py — 多層感知器 (MLP) 訓練 XOR

## 概述

ex3-xor.py 展示如何使用多層感知器（MLP）解決 XOR 問題。

XOR 是神經網路的經典測試，因為單層感知器無法解決 XOR。

## 執行方式

```bash
python ex3-xor.py
```

## XOR 問題

| 輸入 A | 輸入 B | 輸出 |
|-------|-------|------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

這是一個非線性問題，單層網路無法解決。

## 程式碼詳解

### 1. 網路架構 (2-4-1)

```
輸入 (2)
   |
   v
隱藏層 (4, ReLU)
   |
   v
輸出層 (1)
   |
   v
輸出
```

### 2. 參數初始化

```python
# Layer 1: 輸入 2 -> 隱藏 4
w1 = [[random... for _ in range(2)] for _ in range(4)]
b1 = [random... for _ in range(4)]

# Layer 2: 隱藏 4 -> 輸出 1
w2 = [[random... for _ in range(4)] for _ in range(1)]
b2 = [random... for _ in range(1)]
```

### 3. 前向傳播

```python
def mlp(x):
    # 隱藏層：線性 + ReLU
    h = [sum(wi*xi for wi,xi in zip(wr,x)) + bi for wr,bi in zip(w1,b1)]
    h = [hi.relu() for hi in h]
    
    # 輸出層：線性
    out = [sum(wi*hi for wi,hi in zip(wr,h)) + bi for wr,bi in zip(w2,b2)]
    return out[0]
```

ReLU 是關鍵：提供非線性變換。

### 4. 訓練

```python
for epoch in range(101):
    total_loss = Value(0)
    for x, y in zip(X_data, Y_data):
        pred = mlp(x)
        total_loss += (pred - y) ** 2
    
    loss = total_loss / len(X_data)
    loss.backward()
    optimizer.step()
```

## 數學原理

### 為何需要多層？

單層感知器：$y = w \cdot x + b$ 是線性函數，只能學習線性分割。

XOR 是非線性的，需要非線性激活函數（ReLU）。

### ReLU 激活

$$\text{ReLU}(x) = \max(0, x)$$

這將線性函數轉換為非線性，可以學習複雜的決策邊界。

### MLP 的表达能力

具有一個隱藏層的網路可以逼近任何連續函數（通用逼近定理）。

## 輸出範例

```
=== 3. 多層感知器 (XOR) ===
Epoch   0 | Loss: 0.7365
Epoch  20 | Loss: 0.1128
Epoch  40 | Loss: 0.0025
Epoch  60 | Loss: 0.0002
Epoch  80 | Loss: 0.0000
Epoch 100 | Loss: 0.0000
預測結果:
輸入 [0, 0] -> 預測: 0.0003 (目標: 0)
輸入 [0, 1] -> 預測: 1.0004 (目標: 1)
輸入 [1, 0] -> 預測: 1.0002 (目標: 1)
輸入 [1, 1] -> 預測: -0.0004 (目標: 0)
```

模型成功學習了 XOR！

## 學習重點

1. **非線性激活**：ReLU 提供非線性
2. **隱藏層**：增加模型的表達能力
3. **通用逼近**：多層網路可以學習複雜函數

---

本文件結束