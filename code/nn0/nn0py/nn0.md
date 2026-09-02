# nn0.py — 自動微分引擎

## 概述

nn0.py 提供純 Python 實現的自動微分（Automatic Differentiation）引擎與 Adam 優化器。這是構建神經網路的基礎元件，允許使用者以計算圖（Computational Graph）的方式定義神經網路，並自動計算梯度進行優化。

本模組提供以下核心功能：
- `Value` 類：自動微分節點，支援反向傳播
- `Adam` 類：自適應學習率優化器
- `linear()` 函式：矩陣乘法
- `softmax()` 函式：數值穩定的 Softmax
- `rmsnorm()` 函式：RMS Normalization
- `cross_entropy()` 函式：數值穩定的 Cross-Entropy Loss
- `gd()` 函式：單步梯度下降

---

## 第一章：Value 類 — 自動微分節點

### 1.1 自動微分簡介

自動微分（Automatic Differentiation，簡稱 Autograd）是一種計算函數導數的技術，廣泛應用於深度學習框架中（如 PyTorch、TensorFlow）。與數值微分和符號微分不同，自動微分通過鏈式法則（Chain Rule）精確計算導數，沒有數值逼近的誤差。

自動微分有兩種模式：
1. **正向模式（Forward Mode）**：從輸入到輸出計算函數值的同時計算導數
2. **反向模式（Reverse Mode）**：從輸出反向傳播梯度到輸入，更適合多輸入少輸出的情況

本實現採用反向模式，這與深度學習中的 Backpropagation（反向傳播）算法相同。

### 1.2 Value 類的設計

`Value` 類是自動微分的基本單元，每個 `Value` 對象代表計算圖中的一個節點。以下是類的定義：

```python
class Value:
    """純 Python 的自動微分節點，支援反向傳播。"""
    __slots__ = ('data', 'grad', '_children', '_local_grads')

    def __init__(self, data, children=(), local_grads=()):
        self.data = data
        self.grad = 0
        self._children = children
        self._local_grads = local_grads
```

#### 屬性說明

| 屬性 | 類型 | 說明 |
|------|------|------|
| `data` | `float` | 節點的數值（正向傳播結果） |
| `grad` | `float` | 節點的梯度（反向傳播時計算） |
| `_children` | `tuple` | 依賴的子節點元組 |
| `_local_grads` | `tuple` | 對每個子節點的局部梯度 |

#### 為何使用 `__slots__`？

使用 `__slots__` 可以顯著減少內存開銷，因為不需要為每個實例創建 `__dict__`。這對於擁有大量參數的神經網路尤為重要。

### 1.3 計算圖的建立

當我們對 `Value` 對象進行運算時，實際上是在建立一個計算圖。例如：

```python
a = Value(2.0)
b = Value(3.0)
c = a + b
```

上述程式碼會創建一個新的 `Value` 對象 `c`，其包含：
- `c.data = 5.0`（2.0 + 3.0）
- `c._children = (a, b)`
- `c._local_grads = (1, 1)`

這裡的局部梯度 (1, 1) 表示：
- $\frac{\partial c}{\partial a} = 1$
- $\frac{\partial c}{\partial b} = 1$

### 1.4 支援的運算

`Value` 類通過魔術方法（Magic Methods）支援多種運算。以下是完整的運算列表：

#### 1.4.1 加法運算

```python
def __add__(self, other):
    other = other if isinstance(other, Value) else Value(other)
    return Value(self.data + other.data, (self, other), (1, 1))
```

數學含義：若 $c = a + b$，則
$$\frac{\partial c}{\partial a} = 1, \quad \frac{\partial c}{\partial b} = 1$$

範例：
```python
a = Value(2.0)
b = Value(3.0)
c = a + b  # c.data = 5.0
```

#### 1.4.2 乘法運算

```python
def __mul__(self, other):
    other = other if isinstance(other, Value) else Value(other)
    return Value(self.data * other.data, (self, other), (other.data, self.data))
```

數學含義：若 $c = a \cdot b$，則根據乘積規則（Product Rule）：
$$\frac{\partial c}{\partial a} = b, \quad \frac{\partial c}{\partial b} = a$$

範例：
```python
a = Value(2.0)
b = Value(3.0)
c = a * b  # c.data = 6.0, local_grads = (3.0, 2.0)
```

#### 1.4.3 冪運算

```python
def __pow__(self, other):
    return Value(self.data**other, (self,), (other * self.data**(other - 1),))
```

數學含義：若 $c = a^n$，則根據冪規則（Power Rule）：
$$\frac{\partial c}{\partial a} = n \cdot a^{n-1}$$

範例：
```python
a = Value(2.0)
c = a ** 3  # c.data = 8.0, local_grads = (12.0)
```

#### 1.4.4 對數運算

```python
def log(self):
    return Value(math.log(self.data), (self,), (1 / self.data,))
```

數學含義：若 $c = \log(a)$，則
$$\frac{\partial c}{\partial a} = \frac{1}{a}$$

注意：這是自然對數（Natural Logarithm），即 $\ln(a)$。

#### 1.4.5 指數運算

```python
def exp(self):
    return Value(math.exp(self.data), (self,), (math.exp(self.data),))
```

數學含義：若 $c = e^a$，則
$$\frac{\partial c}{\partial a} = e^a = c$$

這是一個重要的恆等式：指數函數的導數等於其本身。

#### 1.4.6 ReLU 激活函數

```python
def relu(self):
    return Value(max(0, self.data), (self,), (float(self.data > 0),))
```

數學含義：
$$\text{ReLU}(a) = \max(0, a)$$

$$\frac{\partial \text{ReLU}}{\partial a} = \begin{cases} 1 & \text{if } a > 0 \\ 0 & \text{if } a \leq 0 \end{cases}$$

這是深度學習中最常用的激活函數之一，因為它可以緩解梯度消失問題，並產生稀疏激活。

### 1.5 反向運算的實現

除了正向運算，`Value` 類還支援反向運算（右操作數）：

```python
def __radd__(self, other): return self + other
def __rsub__(self, other): return other + (-self)
def __rmul__(self, other): return self * other
def __rtruediv__(self, other): return other * self**-1
```

這些方法確保當 `Value` 是右操作數時（如 `3.0 + a`），也能正確處理。

### 1.6 反向傳播算法

#### 1.6.1 為何需要拓撲排序？

在反向傳播時，我們需要確保每個節點的梯度只在所有依賴節點計算完畢後才能計算。這就需要拓撲排序（Topological Sort）。

#### 1.6.2 反向傳播的实现

```python
def backward(self):
    """反向傳播：計算所有參數的梯度。"""
    topo = []
    visited = set()

    def build_topo(v):
        if v not in visited:
            visited.add(v)
            for child in v._children:
                build_topo(child)
            topo.append(v)

    build_topo(self)
    self.grad = 1
    for v in reversed(topo):
        for child, local_grad in zip(v._children, v._local_grads):
            child.grad += local_grad * v.grad
```

#### 1.6.3 算法步驟詳解

**步驟 1：建立拓撲排序**

```python
def build_topo(v):
    if v not in visited:
        visited.add(v)
        for child in v._children:
            build_topo(child)
        topo.append(v)
```

這個遞迴函數確保：
1. 每個子節點先被訪問
2. 當前節點在所有子節點之後被添加到 `topo`
3. 因此 `topo` 是從 leaf 到 root 的順序

**步驟 2：初始化輸出梯度**

```python
self.grad = 1
```

對於 loss function，我們從 $\frac{\partial \mathcal{L}}{\partial \mathcal{L}} = 1$ 開始。

**步驟 3：逆序傳播梯度**

```python
for v in reversed(topo):
    for child, local_grad in zip(v._children, v._local_grads):
        child.grad += local_grad * v.grad
```

對每個節點 $v$，使用鏈式法則：
$$\frac{\partial \mathcal{L}}{\partial child} += \frac{\partial v}{\partial child} \cdot \frac{\partial \mathcal{L}}{\partial v}$$

#### 1.6.4 梯度累加的重要性

注意代碼中使用 `+=` 而非 `=`：

```python
child.grad += local_grad * v.grad
```

這是因為一個 child 節點可能被多個父節點依賴，需要累加來自所有路徑的梯度。這在神經網路的殘差連接（Residual Connection）中特別重要。

#### 1.6.5 完整範例

讓我們通過一個完整範例來說明反向傳播：

```python
# 建立計算圖：f(a, b) = (a + b) * a
a = Value(2.0, label='a')
b = Value(3.0, label='b')

t1 = a + b     # t1.data = 5.0, children = (a, b), grads = (1, 1)
f = t1 * a     # f.data = 10.0, children = (t1, a), grads = (a.data, t1.data) = (5.0, 2.0)

# 反向傳播
f.grad = 1

# 由於 topo 是 [a, b, t1, f]（逆序時），按序處理：
# 處理 f: child.grad += grad * local_grad
#   t1.grad += 1 * 5.0 = 5.0
#   a.grad += 1 * 2.0 = 2.0
# 處理 t1:
#   a.grad += 5.0 * 1 = 5.0
#   b.grad += 5.0 * 1 = 5.0
# 最終結果：a.grad = 7.0, b.grad = 5.0
```

驗證：$f = a^2 + ab$，所以
- $\frac{\partial f}{\partial a} = 2a + b = 4 + 3 = 7$
- $\frac{\partial f}{\partial b} = a = 2$

正確！

---

## 第二章：Adam 優化器

### 2.1 優化器簡介

優化器（Optimizer）是深度學習中的關鍵组件，負責根據梯度更新模型參數。最簡單的優化器是隨機梯度下降（SGD），但收斂速度較慢。Adam（Adaptive Moment Estimation）是一種自適應學習率優化器結合了動量（Momentum）和 RMSProp 的優點。

### 2.2 Adam 的數學原理

Adam 維護兩個估計矩陣：
1. **一階矩估計（First Moment）**：類似動量，捕捉梯度的方向
2. **二階矩估計（Second Moment）**：類似 RMSProp，捕捉梯度的變化幅度

$$m_t = \beta_1 \cdot m_{t-1} + (1 - \beta_1) \cdot g_t$$

$$v_t = \beta_2 \cdot v_{t-1} + (1 - \beta_2) \cdot g_t^2$$

其中：
- $g_t$ 是第 $t$ 步的梯度
- $\beta_1$ 和 $\beta_2$ 是衰減率，通常設為 0.9 和 0.999

#### 2.2.1 偏差修正

在訓練初期，由於 $m_0 = 0$ 和 $v_0 = 0$，估計值會偏向零。Adam 使用偏差修正：

$$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}$$

$$\hat{v}_t = \frac{v_t}{1 - \beta_2^t}$$

這確保在訓練初期有適當的梯度估計。

#### 2.2.2 參數更新

$$p_{t+1} = p_t - lr \cdot \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

其中 $\epsilon$ 是一個很小的數（$10^{-8}$），防止除零錯誤。

### 2.3 Adam 類的實現

```python
class Adam:
    """Adam optimizer，支援 learning rate 線性衰減。"""

    def __init__(self, params, lr=0.01, beta1=0.85, beta2=0.99, eps=1e-8):
        self.params = params
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.m = [0.0] * len(params)
        self.v = [0.0] * len(params)
        self.step_count = 0
```

#### 初始化參數說明

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `params` | - | 要優化的參數列表 |
| `lr` | 0.01 | 初始學習率 |
| `beta1` | 0.85 | 一階矩衰減率（動量） |
| `beta2` | 0.99 | 二階矩衰減率（RMSProp） |
| `eps` | 1e-8 | 數值穩定項 |

注意：本實現使用 $\beta_1 = 0.85$ 和 $\beta_2 = 0.99$，與標準的 0.9/0.999 略有不同，這是為了讓記憶保留更長。

#### 2.3.1 為何使用不同的 beta 值？

標準 Adam 使用 $\beta_1 = 0.9$ 和 $\beta_2 = 0.999$：
- 較高的 $\beta_2$ 意味著二階矩估計會更慢衰減，長期梯度平方的影響更大
- 這對於自然語言處理等複雜任務有好效果

本實現使用較低的 $\beta_1 = 0.85$，讓 momentum 有更強的 forget 特性，這在簡單任務中可能收斂更快。

### 2.4 學習率衰減

```python
def step(self, lr_override=None):
    """執��一步參數更新，並清除梯度。"""
    self.step_count += 1
    lr = lr_override if lr_override is not None else self.lr

    for i, p in enumerate(self.params):
        self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * p.grad
        self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * p.grad ** 2
        m_hat = self.m[i] / (1 - self.beta1 ** self.step_count)
        v_hat = self.v[i] / (1 - self.beta2 ** self.step_count)
        p.data -= lr * m_hat / (v_hat ** 0.5 + self.eps)
        p.grad = 0
```

本實現支援學習率覆蓋（`lr_override`），這實現了學習率衰減。在訓練時：

```python
for step in range(num_steps):
    lr_t = optimizer.lr * (1 - step / num_steps)
    optimizer.step(lr_override=lr_t)
```

這是**線性衰減（Linear Decay）**：
- 開始時：$lr_t = lr_0$
- 結束時：$lr_t \approx 0$

為何要學習率衰減？
1. 開始時較大的學習率可以快速收斂
2. 結束時較小的學習率可以 fine-tune，找到更好的局部最優

---

## 第三章：核心函式

### 3.1 linear — 矩陣乘法

#### 3.1.1 函式簽名

```python
def linear(x, w):
    """矩陣乘法：y = W @ x"""
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]
```

#### 3.1.2 數學含義

$$
y = W \cdot x
$$

其中：
- $x \in \mathbb{R}^{n_{\text{in}}}$ 是輸入向量
- $W \in \mathbb{R}^{n_{\text{out}} \times n_{\text{in}}}$ 是權重矩陣
- $y \in \mathbb{R}^{n_{\text{out}}}$ 是輸出向量

具體元素：
$$y_i = \sum_{j} W_{ij} \cdot x_j$$

#### 3.1.3 實現細節

```python
return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]
```

這是一個雙層列表推导式（Nested List Comprehension）：
1. 內層：`sum(wi * xi for wi, xi in zip(wo, x))` 計算一行輸出
2. 外層：`[... for wo in w]` 對每一行重複

#### 3.1.4 範例

```python
x = [1.0, 2.0, 3.0]
W = [
    [1, 0, 0],  # 第一行
    [0, 1, 0],  # 第二行
]
y = linear(x, W)  # y = [1.0, 2.0]
```

### 3.2 softmax — 數值穩定 Softmax

#### 3.2.1 函式簽名

```python
def softmax(logits):
    """數值穩定的 softmax。"""
    max_val = max(val.data for val in logits)
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)
    return [e / total for e in exps]
```

#### 3.2.2 數學含義

Softmax 將一個向量轉換為機率分布：

$$\text{softmax}(x)_i = \frac{e^{x_i}}{\sum_j e^{x_j}}$$

#### 3.2.3 數值穩定性問題

直接計算 softmax 可能導致數值溢位（Overflow）：

$e^{x_i}$ 當 $x_i > 700$ 時，$e^{x_i}$ 超過 float64 的表示範圍。

#### 3.2.4 最大值平移技巧

我們可以利用以下恆等式：

$$\text{softmax}(x)_i = \frac{e^{x_i - M}}{\sum_j e^{x_j - M}}$$

其中 $M = \max(x)$。

證明：
$$\frac{e^{x_i}}{\sum_j e^{x_j}} = \frac{e^{x_i} \cdot e^{-M}}{\sum_j e^{x_j} \cdot e^{-M}} = \frac{e^{x_i - M}}{\sum_j e^{x_j - M}}$$

這樣確保所有指數輸入都在 $(-\infty, 0]$ 範圍內，不會溢位。

#### 3.2.5 實現步驟

1. **找最大值**：`max_val = max(val.data for val in logits)`
2. **平移並計算指數**：`exps = [(val - max_val).exp() for val in logits]`
3. **求和**：`total = sum(exps)`
4. **歸一化**：`return [e / total for e in exps]`

### 3.3 rmsnorm — RMS Normalization

#### 3.3.1 函式簽名

```python
def rmsnorm(x):
    """RMS Normalization（取代 LayerNorm）。"""
    ms = sum(xi * xi for xi in x) / len(x)
    scale = (ms + 1e-5) ** -0.5
    return [xi * scale for xi in x]
```

#### 3.3.2 數學含義

RMS Normalization 的計算如下：

$$\text{rms} = \sqrt{\frac{1}{n} \sum_i x_i^2 + \epsilon}$$

$$\text{output} = x \cdot \text{rms}^{-1}$$

或者寫成：

$$\text{output} = \frac{x}{\|x\|_rms}$$

其中 $\|x\|_{rms} = \sqrt{\frac{1}{n} \sum_i x_i^2 + \epsilon}$

#### 3.3.3 與 LayerNorm 的比較

LayerNorm 的計算：

$$\mu = \frac{1}{n} \sum_i x_i$$

$$\sigma = \sqrt{\frac{1}{n} \sum_i (x_i - mu)^2 + epsilon}$$

$$\text{output} = \frac{x - mu}{\sigma}$$

優點比較：
- RMS Norm 計算更簡單（無需計算均值）
- RMS Norm 對不同輸入分佈更穩定
- 在某些任務中效果相當或更好

#### 3.3.4 為何需要 epsilon？

`epsilon = 1e-5` 是為了數值穩定，防止除零：

```python
scale = (ms + 1e-5) ** -0.5
```

當輸入為零向量時，$ms = 0$，沒有 epsilon 會導致除零錯誤。

#### 3.3.5 實現步驟

1. **計算均方值**：`ms = sum(xi * xi for xi in x) / len(x)`
2. **計算 scale**：`scale = (ms + 1e-5) ** -0.5`
3. **應用 scale**：`return [xi * scale for xi in x]`

### 3.4 cross_entropy — 數值穩定 Cross-Entropy

#### 3.4.1 函式簽名

```python
def cross_entropy(logits, target_id):
    """
    數值穩定的 Cross-Entropy Loss。
    直接接收 logits，避免先算 softmax 可能導致的 math.log(0) 錯誤。

    使用 Log-Sum-Exp 技巧：
    Loss = -log( e^{x_c} / sum(e^{x_i}) )
         = log(sum(e^{x_i - M})) - (x_c - M)  (其中 M 為 max(logits))
    """
```

#### 3.4.2 數學含義

Cross-Entropy Loss（在分類任務中）：

$$\mathcal{L} = -\log \left( \frac{e^{x_{target}}}{\sum_j e^{x_j}} \right)$$

$$= \log \left( \sum_j e^{x_j} \right) - x_{target}$$

#### 3.4.3 數值穩定性問題

若直接計算 $\log(\sum_j e^{x_j})$，當最大值很大時會溢位。

#### 3.4.4 Log-Sum-Exp 技巧

$$\mathcal{L} = \log \left( \sum_j e^{x_j - M} \right) + M - x_{target}$$

其中 $M = \max(x)$。

證明：
$$\log \left( \sum_j e^{x_j} \right) = \log \left( \sum_j e^{x_j - M} \cdot e^M \right) = \log \left( e^M \sum_j e^{x_j - M} \right) = M + \log \left( \sum_j e^{x_j - M} \right)$$

#### 3.4.5 實現步驟

```python
# 找出最大值以確保數值穩定
max_val = max(val.data for val in logits)

# 計算 sum(exp(x_i - M))
exps = [(val - max_val).exp() for val in logits]
total = sum(exps)

# 計算 Loss: log(total) - (x_target - M)
return total.log() - (logits[target_id] - max_val)
```

### 3.5 gd — 單步梯度下降

#### 3.5.1 函式簽名

```python
def gd(model, optimizer, tokens, step, num_steps):
    """
    一步梯度下降：forward → loss → backward → Adam update。
    回傳 loss 值。
    """
```

#### 3.5.2 數學含義

對於序列建模任務，我們預測下一個 token：

$$\mathcal{L} = -\frac{1}{n} \sum_{t=0}^{n-1} \log P(token_{t+1} | token_t)$$

其中 $n = \min(\text{block\_size}, |\text{tokens}| - 1)$

#### 3.5.3 實現步驟

```python
n = min(model.block_size, len(tokens) - 1)
keys   = [[] for _ in range(model.n_layer)]
values = [[] for _ in range(model.n_layer)]

losses = []
for pos_id in range(n):
    token_id, target_id = tokens[pos_id], tokens[pos_id + 1]
    logits = model(token_id, pos_id, keys, values)
    probs = softmax(logits)
    loss_t = -probs[target_id].log()
    losses.append(loss_t)
loss = (1 / n) * sum(losses)

loss.backward()

lr_t = optimizer.lr * (1 - step / num_steps)
optimizer.step(lr_override=lr_t)

return loss.data
```

#### 3.5.4 KV Cache 解釋

```python
keys   = [[] for _ in range(model.n_layer)]
values = [[] for _ in range(model.n_layer)]
```

這是 KV Cache（Key-Value Cache），用於 attention 機制：
- 每個位置只存取之前的 Keys 和 Values
- 確保 Causal Masking（單向注意力）

#### 3.5.5 為何不直接用 cross_entropy？

這裡使用 `-probs[target_id].log()` 而非 `cross_entropy(logits, target_id)`：
- 兩者在數學上等價
- 這裡展現了從 logits → softmax → loss 的完整流程

---

## 第四章：進階主題

### 4.1 計算圖的視覺化

雖然本實現沒有內建視覺化，但可以用文字表示計算圖：

```
輸入: a = Value(2.0), b = Value(3.0)
運算: c = a + b → d = c * a

計算圖:
a ──┐
     ├──+──> c ──*──> d
b ───┘     ▲
            │
          a ◄──┘ (重複使用)
```

### 4.2 內存優化

使用 `Value` 類時需要注意內存：

| 優化方式 | 說明 |
|----------|------|
| `__slots__` | 減少實例內存開銷 |
| 梯度清除 | `p.grad = 0` 在每次更新後清除，防止內存洩漏 |
| 引用重用 | KV Cache 重用 keys/values 列表 |

### 4.3 數值精度

本實現使用 Python 的 float（雙精度），精度約為 $10^{-15}$。

若需要更高精度（用于研究）：
- 使用 `decimal.Decimal`
- 使用 arbitrary precision 庫

若需要更低精度用於部署（更快的訓練）：
- 使用 float16（半精度）
- 使用 mixed precision training

### 4.4 性能考量

本實現是純 Python，在以下方面有局限性：

1. **速度**：比 NumPy/PyTorch 慢 10-100 倍
2. **並行化**：無法利用 GPU
3. **自動向量化**：需要手動實現

這是教育目的實現，不適合實際深度學習任務。

---

## 附錄

### A.1 完整運算表

| 運算 | 代碼實現 | 局部梯度 $\frac{\partial y}{\partial x}$ |
|------|----------|----------------------------------------|
| $y = a + b$ | `a + b` | $(1, 1)$ |
| $y = a - b$ | `a - b` | $(1, -1)$ |
| $y = a \cdot b$ | `a * b` | $(b, a)$ |
| $y = a / b$ | `a / b` | $(1/b, -a/b^2)$ |
| $y = a^n$ | `a ** n` | $n \cdot a^{n-1}$ |
| $y = \log(a)$ | `a.log()` | $1/a$ |
| $y = \exp(a)$ | `a.exp()` | $\exp(a)$ |
| $y = \text{ReLU}(a)$ | `a.relu()` | $1$ if $a > 0$ else $0$ |

### A.2 訓練小技巧

1. **梯度裁剪**：防止梯度爆炸
   ```python
   max_grad = 1.0
   for p in params:
       if p.grad > max_grad:
           p.grad = max_grad
       elif p.grad < -max_grad:
           p.grad = -max_grad
   ```

2. **動量調整**：開始時使用較高的動量幫助跳過局部最優

3. **學習率调度**：除線性衰減外，還可以使用：
   - 指數衰減：$lr_t = lr_0 \cdot \gamma^t$
   - 階梯衰減：每 $N$ 步降低一次
   - 余弦退火：$lr_t = lr_{min} + 0.5 \cdot (lr_{max} - lr_{min}) \cdot (1 + \cos(\pi \cdot t / T))$

### A.3 常見錯誤

1. **梯度未初始化**：
   ```python
   # 錯誤
   for p in params:
       p.grad += ...  # 會保留舊的梯度

   # 正確
   p.grad = 0
   p.grad += ...
   ```

2. **忘記清零梯度**：
   ```python
   # 每次 step 後梯度會自動清零
   optimizer.step()
   # 但若有多次 backward，累計梯度會錯誤
   loss.backward()  # 如果不清零，梯度會累加
   ```

3. **學習率設置不當**：
   - 學習率過大：不收斂或震盪
   - 學習率過小：收斂太慢

---

本文件結束