"""
nn0.py — 自動微分引擎 (Value) 與 Adam 優化器

本模組提供純 Python 實現的自動微分（Automatic Differentiation）引擎，是構建神經網路的基礎元件。

功能說明：
  class Value      — 自動微分節點，支援反向傳播（backpropagation）
  class Adam     — Adam 優化器，自適應學習率
  linear()      — 矩陣乘法（全連接層）
  softmax()     — 數值穩定的 Softmax 激活函數
  rmsnorm()     — RMS Normalization 正規化
  cross_entropy() — 數值穩定的交叉熵損失函數
  gd()          — 單步梯度下降訓練

數學原理簡述：
  1. Value 使用鏈式法則（Chain Rule）自動計算梯度
  2. Adam 結合動量（Momentum）和 RMSProp 的優點
  3. Softmax 使用最大值平移防止數值溢位
  4. RMS Norm 比 Layer Norm 更簡單（無需計算均值）
"""

import math


class Value:
    """
    自動微分節點（Autograd Node）

    用於構建計算圖（Computational Graph），支援自動反向傳播。

    設計原理：
      - 每個 Value 節點記錄自己的數值（data）
      - 記錄依賴的子節點（_children）
      - 記錄對每個子節點的局部梯度（_local_grads）
      - 反向傳播時，從輸出開始沿計算圖逆向傳遞梯度

    數學表示：
      - data: 節點的數值（即前向傳播的結果）
      - grad: 節點的梯度（即 loss 對該節點的偏導數）
      - _children: 依賴的父節點（元組）
      - _local_grads: 對每個父節點的局部偏導數（元組）

    使用範例：
      a = Value(2.0)        # 建立節點 a = 2.0
      b = Value(3.0)        # 建立節點 b = 3.0
      c = a + b             # c = a + b = 5.0，自動記錄計算圖
      c.backward()          # 反向傳播，計算 a.grad 和 b.grad
    """

    # 使用 __slots__ 減少內存開銷，不為每個實例創建 __dict__
    __slots__ = ('data', 'grad', '_children', '_local_grads')

    def __init__(self, data, children=(), local_grads=()):
        """
        建構函數

        參數說明：
          data: 節點的數值（float）
          children: 依賴的子節點元組（tuple），預設為空元組
          local_grads: 對每個子節點的局部梯度元組（tuple），預設為空元組

        局部梯度的意義：
          若 y = f(x1, x2, ...)，則 local_grads[i] = ∂y/∂xi
          例如：y = a + b，則 local_grads = (1, 1)
               y = a * b，則 local_grads = (b, a)
        """
        self.data = data             # 節點的數值
        self.grad = 0            # 梯度，初始為 0
        self._children = children   # 依賴的子節點
        self._local_grads = local_grads  # 局部梯度

    def __add__(self, other):
        """
        加法運算：y = a + b

        數學原理（加法規則）：
          y = a + b
          ∂y/∂a = 1（加法對每個操作數的偏導數為 1）
          ∂y/∂b = 1

        魔術方法說明：
          - a + b 調用 a.__add__(b)
          - 3 + a 調用 a.__radd__(3)
        """
        # 將 Python 數字轉換為 Value 對象，支援混合運算（如 2 + Value(3)）
        other = other if isinstance(other, Value) else Value(other)
        # 返回新的 Value 節點，記錄計算圖（包括父子節點和局部梯度）
        return Value(self.data + other.data, (self, other), (1, 1))

    def __mul__(self, other):
        """
        乘法運算：y = a * b

        數學原理（乘積規則）：
          y = a * b
          ∂y/∂a = b（a 改變時，y 的變化等於 b）
          ∂y/���b = a（b 改變時，y 的變化等於 a）
        """
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data * other.data, (self, other), (other.data, self.data))

    def __pow__(self, other):
        """
        冪運算：y = a^n

        數學原理（冪規則）：
          y = a^n
          ∂y/∂a = n * a^(n-1)

        參數說明：
          other: 指數 n（通常為常數）
        """
        return Value(self.data**other, (self,), (other * self.data**(other - 1),))

    def log(self):
        """
        對數運算：y = log(a) = ln(a)

        數學原理：
          y = log(a)
          ∂y/∂a = 1/a
        """
        return Value(math.log(self.data), (self,), (1 / self.data,))

    def exp(self):
        """
        指數運算：y = e^a

        數學原理：
          y = e^a
          ∂y/∂a = e^a = y（重要性質：導數等於本身）

        這是 e 的指數次方的自然對數。
        """
        return Value(math.exp(self.data), (self,), (math.exp(self.data),))

    def relu(self):
        """
        ReLU 激活函數：y = max(0, a)

        數學原理：
          y = max(0, a)
          ∂y/∂a = 1 if a > 0 else 0

        這是深度學習中最常用的激活函數之一：
        - 計算簡單高效
        - 可以緩解梯度消失問題
        - 產生稀疏激活（輸出為 0 的神經元）
        """
        return Value(max(0, self.data), (self,), (float(self.data > 0),))

    # -------------------- 以下是反向運算，確保混合運算正常工作 --------------------

    def __neg__(self):
        """負號：y = -a 等價於 y = a * (-1)"""
        return self * -1

    def __radd__(self, other):
        """右加法：3 + a 轉換為 a + 3"""
        return self + other

    def __sub__(self, other):
        """減法：a - b 等價於 a + (-b)"""
        return self + (-other)

    def __rsub__(self, other):
        """右減法：3 - a 轉換為 3 + (-a)"""
        return other + (-self)

    def __rmul__(self, other):
        """右乘法：3 * a 轉換為 a * 3"""
        return self * other

    def __truediv__(self, other):
        """除法：a / b 等價於 a * b^(-1)"""
        return self * other**-1

    def __rtruediv__(self, other):
        """右除法：3 / a 轉換為 3 * a^(-1)"""
        return other * self**-1

    def backward(self):
        """
        反向傳播（Backpropagation）

        這是自動微分的核心算法，沿計算圖逆向計算所有節點的梯度。

        算法步驟：
          1. 建立拓撲排序，確保子節點先被處理
          2. 初始化輸出梯度為 1（d_loss/d_loss = 1）
          3. 逆序遍歷，將梯度傳遞給每個子節點

        數學原理（鏈式法則）：
          對於節點 v，設其輸出梯度為 ∂L/∂v
          對於每個子節點 c，局部梯度為 ∂v/∂c
          傳遞：c.grad += ∂v/∂c * ∂L/∂v

        注意：
          - 使用 += 是因為一個節點可能被多個父節點依賴
          - 梯度需要累加（如殘差連接的情況）
        """
        # -------------------- 第一步：建立拓撲排序 --------------------
        # 拓撲排序確保：處理節點前，其所有依賴節點已處理
        topo = []           # 存儲排序後的節點列表
        visited = set()    # 記錄已訪問的節點

        def build_topo(v):
            """
            遞迴建構拓撲排序

            使用深度優先搜索（DFS）：
            - 先訪問所有子節點
            - 然後將當前節點添加到 topo
            - 結果：topo 是從葉節點到根節點的順序
            """
            if v not in visited:
                visited.add(v)
                for child in v._children:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        # -------------------- 第二步：初始化輸出梯度 --------------------
        # 對 loss 本身求導，∂L/∂L = 1
        self.grad = 1

        # -------------------- 第三步：逆序傳播梯度 --------------------
        # 逆序遍歷：從輸出到輸入
        for v in reversed(topo):
            # 對每個節點 v，將梯度傳給其依賴的子節點
            for child, local_grad in zip(v._children, v._local_grads):
                # 鏈式法則：∂L/∂c = ∂v/∂c * ∂L/∂v
                child.grad += local_grad * v.grad

    def __repr__(self):
        """除錯用：顯示節點的數值"""
        return f"Value({self.data:.4f})"


class Adam:
    """
    Adam 優化器（Adaptive Moment Estimation）

    Adam 是深度學習中最常用的優化器之一，結合了：
    - 動量（Momentum）：加速收斂
    - RMSProp：自適應學習率

    數學原理：

    1. 一階矩估計（動量）：
       m_t = β1 * m_{t-1} + (1-β1) * grad

       類似物理中的動量：累加過去的梯度方向
       β1 通常設為 0.9

    2. 二階矩估計（RMSProp）：
       v_t = β2 * v_{t-1} + (1-β2) * grad^2

       記錄梯度平方的加權平均，用於調整學習率
       β2 通常設為 0.999

    3. 偏差修正（解決初期估計偏低的問題）：
       m_hat = m_t / (1 - β1^t)
       v_hat = v_t / (1 - β2^t)

    4. 參數更新：
       p_{t+1} = p_t - lr * m_hat / (sqrt(v_hat) + ε)

    與 SGD 的比較：
    - SGD：lr 是固定的，收斂慢，可能震盪
    - Adam：lr 自適應，收斂快且穩定
    """

    def __init__(self, params, lr=0.01, beta1=0.85, beta2=0.99, eps=1e-8):
        """
        建構函數

        參數說明：
          params: 要優化的參數列表（list of Value）
          lr: 初始學習率（learning rate），預設 0.01
          beta1: 一階矩衰減率（動量），預設 0.85
          beta2: 二階矩衰減率（RMSProp），預設 0.99
          eps: 數值穩定項，防止除零，預設 1e-8
        """
        self.params = params      # 要優化的參數列表
        self.lr = lr             # 初始學習率
        self.beta1 = beta1       # 動量衰減率
        self.beta2 = beta2       # RMSProp 衰減率
        self.eps = eps           # 數值穩定項

        # 初始化一階矩估計（動量）
        self.m = [0.0] * len(params)

        # 初始化二階矩估計（梯度的平方）
        self.v = [0.0] * len(params)

        # 記錄更新步數，用於偏差修正
        self.step_count = 0

    def step(self, lr_override=None):
        """
        執行一步參數更新

        算法步驟：
          1. 計算一階矩（動量）和二階矩（梯度平方）
          2. 偏差修正
          3. 更新參數
          4. 清除梯度，為下一次訓練做準備

        參數說明：
          lr_override: 可選的學習率覆蓋值，用於學習率衰減
        """
        self.step_count += 1

        # 使用覆蓋的學習率（若提供），否則使用初始學習率
        lr = lr_override if lr_override is not None else self.lr

        for i, p in enumerate(self.params):
            # -------------------- 更新一階矩（動量） --------------------
            # m = β1 * m + (1-β1) * grad
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * p.grad

            # -------------------- 更新二階矩（梯度平方） --------------------
            # v = β2 * v + (1-β2) * grad^2
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * p.grad ** 2

            # -------------------- 偏差修正 --------------------
            # m_hat = m / (1 - β1^t)，解決初期 m 偏低的問題
            m_hat = self.m[i] / (1 - self.beta1 ** self.step_count)
            # v_hat = v / (1 - β2^t)，解決初期 v 偏低的問題
            v_hat = self.v[i] / (1 - self.beta2 ** self.step_count)

            # -------------------- 參數更新 --------------------
            # p = p - lr * m_hat / (sqrt(v_hat) + ε)
            p.data -= lr * m_hat / (v_hat ** 0.5 + self.eps)

            # -------------------- 清除梯度 --------------------
            # 每次更新後梯度必須清零，否則會累積
            p.grad = 0


def linear(x, w):
    """
    矩陣乘法（全連接層）

    實現神經網路中的線性變換：y = W @ x

    數學原理：
      y[i] = Σ_j W[i][j] * x[j]

    這是全連接層（Fully Connected Layer）的核心運算：
      output = input * weights^T

    參數說明：
      x: 輸入向量（list of Value），長度為 nin
      w: 權重矩陣（list of list of Value），形狀為 (nout, nin)

    返回說明：
      y: 輸出向量（list of Value），長度為 nout

    範例：
      x = [Value(1), Value(2), Value(3)]
      w = [[Value(1), Value(0), Value(0)],
           [Value(0), Value(1), Value(0)]]
      y = linear(x, w)
      # y = [1*1 + 2*0 + 3*0, 1*0 + 2*1 + 3*0] = [1, 2]
    """
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]


def softmax(logits):
    """
    數值穩定的 Softmax 激活函數

    Softmax 將任意向量轉換為機率分布：
      softmax(x)[i] = e^x[i] / Σ_j e^x[j]

    數值穩定性問題：
      當 x[i] 很大時（>700），e^x[i] 會溢位（超出 float64 範圍）

    解決方案：最大值平移技巧
      softmax(x)[i] = e^(x[i]-M) / Σ_j e^(x[j]-M)
      其中 M = max(x)

    這是數學等價的變換，但避免了數值溢位：
      e^x = e^(x-M) * e^M，提取公共因子 e^M 到分子分母後消去

    參數說明：
      logits: 輸入的 logits 向量（list of Value）

    返回說明：
      probs: 輸出機率向量（list of Value），和為 1
    """
    # 找出最大值 M，用於平移
    max_val = max(val.data for val in logits)

    # 平移後計算指數：e^(x-M)，此時所有值 ≤ 0，不會溢位
    exps = [(val - max_val).exp() for val in logits]

    # 求和
    total = sum(exps)

    # 歸一化
    return [e / total for e in exps]


def rmsnorm(x):
    """
    RMS Normalization（RMS Norm）

    RMS Norm 是一種簡化的 Normalization 方法，比 Layer Norm 更簡單。

    與 Layer Norm 的比較：
    - Layer Norm: 減去均值，除以標準差
    - RMS Norm: 只除以 RMS（均方根），無需計算均值

    數學原理：
      rms = sqrt(Σ x[i]^2 / n + ε)
      output = x / rms

    也就是：
      output = x * (Σ x[i]^2 / n + ε)^(-0.5)

    優點：
    - 計算更簡單（少一次均值計算）
    - 對不同長度的輸入更穩定

    參數說明：
      x: 輸入向量（list of Value）
      ε: 數值穩定項，預設 1e-5，防止除零

    返回說明：
      輸出向量（list of Value），每個元素的 RMS 為 1（忽略 ε）
    """
    # 計算均方值：Σ x[i]^2 / n
    ms = sum(xi * xi for xi in x) / len(x)

    # 計算 scale：（Σ x[i]^2 / n + ε）^ (-0.5)
    scale = (ms + 1e-5) ** -0.5

    # 應用 scale
    return [xi * scale for xi in x]


def cross_entropy(logits, target_id):
    """
    數值穩定的 Cross-Entropy Loss（交叉���損���）

    Cross-Entropy 是分類任務中常用的損失函數：
      Loss = -log(P[target])

    其中 P[target] 是目標類別的預測機率。

    數值穩定性問題：
      直接計算 -log(softmax(x)[target]) 可能導致 log(0) 錯誤

    解決方案：Log-Sum-Exp 技巧
      Loss = log(Σ e^x[j]) - x[target]
           = log(Σ e^(x[j]-M)) + M - x[target]
      其中 M = max(x)

    這避免了直接計算 softmax，導致 log(0) 的問題。

    參數說明：
      logits: 模型的輸出 logits（list of Value）
      target_id: 目標類別的 ID（int）

    返回說明：
      Loss: 交叉熵損失（Value）
    """
    # 找出最大值 M，用於平移（與 Softmax 相同）
    max_val = max(val.data for val in logits)

    # 計算 Σ e^(x[j]-M)
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)

    # 計算 Loss：
    # log(Σ e^(x[j]-M)) - (x[target] - M)
    # = log(total) - (logits[target_id] - max_val)
    return total.log() - (logits[target_id] - max_val)


def gd(model, optimizer, tokens, step, num_steps):
    """
    單步梯度下降（Gradient Descent）

    執行語言模型的一次訓練步驟：
      1. 前向傳播：計算每個位置的 logits
      2. 計算 Loss：Cross-Entropy
      3. 反向傳播：計算梯度
      4. 更新參數：使用 Adam

    這是訓練神經網路的核心循環。

    參數說明：
      model: GPT 模型实例
      optimizer: Adam 優化器实例
      tokens: token IDs 列表（list of int）
      step: 當前步驟（int），用於學習率衰減
      num_steps: 總步驟數（int），用於學習率衰減

    返回說明：
      loss_value: 平均 loss 的數值（float）
    """
    # 計算序列長度：取 block_size 和 tokens-1 的較小值
    # （需要保證有下一個 token 作為目標）
    n = min(model.block_size, len(tokens) - 1)

    # 建立 KV Cache：用於 Causal Attention
    # keys[layer_id] 存儲該層所有位置的 Key 向量
    # values[layer_id] 存儲該層所有位置的 Value 向量
    keys   = [[] for _ in range(model.n_layer)]
    values = [[] for _ in range(model.n_layer)]

    # 收集每個位置的 loss
    losses = []

    # 對每個位置進行前向傳播
    for pos_id in range(n):
        # 獲取輸入 token 和目標 token
        token_id = tokens[pos_id]
        target_id = tokens[pos_id + 1]

        # 前向傳播，獲取 logits
        logits = model(token_id, pos_id, keys, values)

        # Softmax 轉換為機率
        probs = softmax(logits)

        # 計算該位置的 loss：-log(P[target])
        loss_t = -probs[target_id].log()

        losses.append(loss_t)

    # 計算平均 loss
    loss = (1 / n) * sum(losses)

    # 反向傳播，計算所有參數的梯度
    loss.backward()

    # 學習率線性衰減：
    # lr_t = lr_0 * (1 - step / num_steps)
    # 開始時較大（快速收斂），結束時較小（fine-tune）
    lr_t = optimizer.lr * (1 - step / num_steps)

    # Adam 更新
    optimizer.step(lr_override=lr_t)

    # 返回 loss 值（去除 Value 包裝）
    return loss.data