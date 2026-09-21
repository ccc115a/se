"""
ex3-xor.py — 多層感知器 (MLP) 訓練 XOR

本程式展示如何訓練一個多層感知器（MLP）來解決 XOR 問題：

XOR 問題是神經網路的經典測試：
  - 單層感知器無法解決 XOR
  - 需要隱藏層（非線性變換）

執行方式：
  python ex3-xor.py
"""

import random

# 匯入自動微分引擎
from nn0 import Value, Adam


# ===================== 1. XOR 訓練數據 =====================

# XOR 真值表：
#   輸入 A | 輸入 B | 輸出
#   -------+-------+------
#     0   |   0   |   0
#     0   |   1   |   1
#     1   |   0   |   1
#     1   |   1   |   0

# 訓練數據：x 是輸入向量，y 是目標輸出
X_data = [[0, 0], [0, 1], [1, 0], [1, 1]]
Y_data = [0, 1, 1, 0]

# 打印標題
print("\n=== 3. 多層感知器 (XOR) ===")


# ===================== 2. 初始化網路參數 =====================

# 建立 2-4-1 網路架構：
#   - 輸入層：2 個神經元
#   - 隱藏層：4 個神經元（使用 ReLU 激活）
#   - 輸出層：1 個神經元
#
# 使用隨機初始化 [-1, 1] 範圍
# Layer 1: 2 個輸入 -> 4 個神經元

# w1：隱藏層權重，形狀 (4, 2)
w1 = [[Value(random.uniform(-1, 1)) for _ in range(2)] for _ in range(4)]

# b1：隱藏層偏差，形狀 (4,)
b1 = [Value(random.uniform(-1, 1)) for _ in range(4)]

# Layer 2: 4 個輸入 -> 1 個輸出

# w2：輸出層權重，形狀 (1, 4)
w2 = [[Value(random.uniform(-1, 1)) for _ in range(4)] for _ in range(1)]

# b2：輸出層偏差，形狀 (1,)
b2 = [Value(random.uniform(-1, 1)) for _ in range(1)]


# ===================== 收集參數 =====================

# 將所有參數展平為列表，交給 Adam 優化器
params = ([p for row in w1 for p in row] +  # w1 的所有元素
          b1 +                            # b1 的所有元素
          [p for row in w2 for p in row] +  # w2 的所有元素
          b2)                            # b2 的所有元素

# 建立 Adam 優化器，學習率 0.1
optimizer = Adam(params, lr=0.1)


# ===================== 3. 定義 MLP 前向傳播 =====================

def mlp(x):
    """
    多層感知器前向傳播

    架構：
      x (2 個輸入)
        |
        v
      Hidden Layer (4 個神經元, ReLU)
        |
        v
      Output Layer (1 個神經元)
        |
        v
      output (預測值)
    """
    # -------------------- 隱藏層 --------------------
    # 線性變換：h = W1 * x + b1
    h = [sum(wi * xi for wi, xi in zip(w_row, x)) + bi for w_row, bi in zip(w1, b1)]

    # ReLU 激活函數：ReLU(z) = max(0, z)
    # 這提供非線性變換，是 XOR 必需的
    h = [hi.relu() for hi in h]

    # -------------------- 輸出層 --------------------
    # 線性變換：out = W2 * h + b2
    out = [sum(wi * hi for wi, hi in zip(w_row, h)) + bi for w_row, bi in zip(w2, b2)]

    # 返回單個輸出
    return out[0]


# ===================== 4. 訓練迴圈 =====================

# 訓練 101 個 epoch
for epoch in range(101):
    # 初始化總損失
    total_loss = Value(0.0)

    # 對每個訓練樣本計算損失
    for x, y in zip(X_data, Y_data):
        # 前向傳播
        pred = mlp(x)

        # 計算 MSE 損失：(y_pred - y)^2
        total_loss += (pred - y) ** 2

    # 平均損失
    loss = total_loss / len(X_data)

    # 反向傳播
    loss.backward()

    # Adam 更新
    optimizer.step()

    # 每 20 個 epoch 打印一次
    if epoch % 20 == 0:
        print(f"Epoch {epoch:3d} | Loss: {loss.data:.4f}")


# ===================== 5. 測試訓練結果 =====================

# 打���測試結果
print("預測結果:")

# 對每個輸入模式進行預測
for x, y in zip(X_data, Y_data):
    # 前向傳播得到預測值
    pred = mlp(x)

    # 打印結果
    print(f"輸入 {x} -> 預測: {pred.data:.4f} (目標: {y})")


# ===================== 為何需要多層？ =====================
#
# XOR 問題是非線性的，單層感知器（沒有隱藏層）無法解決
# 因為：
#   - 單層 perceptron 只能學習線性分割
#   - XOR 需要一條曲線來分割
#
# 多層感知器可以學習非線性決策邊界！
#
# 結果應該類似：
#   輸入 [0, 0] -> 預測: ~0.0 (目標: 0)
#   輸入 [0, 1] -> 預測: ~1.0 (目標: 1)
#   輸入 [1, 0] -> 預測: ~1.0 (目標: 1)
#   輸入 [1, 1] -> 預測: ~0.0 (目標: 0)