# ex5-charpredicate.py — 迷你字元預測器

## 概述

ex5-charpredicate.py 展示最簡單的字元級語言模型，概念與 GPT 相同但更簡單。

## 執行方式

```bash
python ex5-charpredicate.py
```

## 程式碼詳解

### 1. 詞彙表

```python
vocab = ['a', 'p', 'l', 'e']
text = "apple"
tokens = [0, 1, 1, 2, 3]
```

字符級Tokenizer。

### 2. 模型架構

```
Token ID
   |
   v
Embedding (4維)
   |
   v
RMS Norm
   |
   v
Linear (vocab_size)
   |
   v
Softmax
   |
   v
下一個字的機率
```

這比完整的 Transformer 簡單得多。

### 3. 訓練

```python
for epoch in range(101):
    total_loss = Value(0)
    for i in range(len(tokens) - 1):
        x_emb = emb[tokens[i]]
        x_norm = rmsnorm(x_emb)
        logits = linear(x_norm, w_out)
        probs = softmax(logits)
        loss_t = -probs[tokens[i+1]].log()
        total_loss += loss_t
    
    loss = total_loss / (len(tokens) - 1)
    loss.backward()
    optimizer.step()
```

目標：給定前一個字元，預測下一個字元。

### 4. 推理

```python
test_id = token_to_id['a']
logits = linear(rmsnorm(emb[test_id]), w_out)
probs = softmax(logits)
pred_id = probs.index(max(probs, key=lambda x: x.data))
```

輸入 'a'，預測下一個字元。

## 數學原理

### Embedding

$$e_i = W_{emb}[i,]$$

將 ID $i$ 映射為向量。

### RMS Norm

$$rms = \sqrt{\frac{1}{n} \sum x_i^2 + \epsilon}$$

$$\text{output} = x / rms$$

### Language Modeling

$$P(w_t | w_{0:t-1}) = \text{softmax}(W \cdot \text{norm}(E[w_{t-1}]))$$

$$\mathcal{L} = -\log P(w_t | w_{0:t-1})$$

## 輸出範例

```
=== 5. 迷你字元預測器 ===
Epoch   0 | Loss: 1.3677
Epoch  20 | Loss: 0.3589
Epoch  40 | Loss: 0.3514
Epoch  60 | Loss: 0.3499
Epoch  80 | Loss: 0.3491
Epoch 100 | Loss: 0.3485
測試輸入 'a' -> 預測下一個字元: 'p'
```

模型成功學習到 'a' -> 'p'！

## 學習重點

1. **字符級Tokenizer**：每個字元對應一個ID
2. **Embedding**：離散到連續的映射
3. **RMSNorm**：正規化
4. **語言模型**：預測下一個 token

這是 GPT 的簡化版本概念！

---

本文件結束