"""
ex5-charpredicate.py — 迷你字元預測器演示

本程式展示如何訓練一個簡單的字元級語言模型：
  1. 使用 Embedding 將字元映射到向量
  2. 使用 RMS Norm 進行正規化
  3. 使用線性層預測下一個字元

執行方式：
  python ex5-charpredicate.py
"""

import random

# 匯入自動微分引擎的組件
from nn0 import Value, Adam, softmax, rmsnorm, linear


# ===================== 1. 建立詞彙表與資料 =====================

# 建立簡易詞彙表
# 包含四個字元：a, p, l, e
vocab = ['a', 'p', 'l', 'e']

# 建立字元到 ID 的映射
token_to_id = {ch: i for i, ch in enumerate(vocab)}

# 訓練文本："apple"
text = "apple"

# 將文本轉換為 token ID 序列
# 'a' -> 0, 'p' -> 1, 'p' -> 1, 'l' -> 2, 'e' -> 3
tokens = [token_to_id[c] for c in text]

# 打印標題
print("\n=== 5. 迷你字元預測器 ===")


# ===================== 2. 模型參數設定 =====================

# Embedding 維度：4
# 每個字元被表示為 4 維向量
d_model = 4

# 詞彙表大小
vocab_size = len(vocab)


# ===================== 建立模型權重 =====================

# Embedding 表：vocab_size × d_model
# 將每個字元 ID 映射為 d_model 維向量
#
# 初始化範圍 [-0.1, 0.1]：較小的初始化幫助訓練穩定
emb = [[Value(random.uniform(-0.1, 0.1)) for _ in range(d_model)] for _ in range(vocab_size)]

# Output Projection 權重：d_model × vocab_size
# 將 embedding 向量映射回詞彙表空間
#
# 用於：logits = embedding * W_out
w_out = [[Value(random.uniform(-0.1, 0.1)) for _ in range(d_model)] for _ in range(vocab_size)]


# ===================== 收集參數 =====================

# 收集所有參數
params = ([p for row in emb for p in row] +
          [p for row in w_out for p in row])

# 建立 Adam 優化器
# 學習率 0.1（對於小型模型是合理的）
optimizer = Adam(params, lr=0.1)


# ===================== 3. 訓練迴圈 =====================

# 訓練 101 個 epoch
for epoch in range(101):
    # 初始化總損失
    total_loss = Value(0.0)

    # 對每個位置進行訓練
    # 給定前一個字元，預測下一個字元
    for i in range(len(tokens) - 1):
        # 取得輸入和目標
        x_id = tokens[i]          # 輸入字元的 ID
        y_id = tokens[i + 1]     # 目標字元的 ID

        # -------------------- Forward pass --------------------

        # 1. 取得 Embedding
        # 根據輸入 ID 查詢 embedding 向量
        x_emb = emb[x_id]

        # 2. RMS Normalization
        # 這是正規化的一種，幫助訓練穩定
        x_norm = rmsnorm(x_emb)

        # 3. 輸出層
        # 計算每個詞彙的分數（logits）
        logits = linear(x_norm, w_out)

        # 4. Softmax 轉換為機率分布
        probs = softmax(logits)

        # 5. 計算損失
        # -log(P[目標])
        loss_t = -probs[y_id].log()
        total_loss += loss_t

    # 平均損失
    loss = total_loss / (len(tokens) - 1)

    # -------------------- Backward pass & Update --------------------

    # 反向傳播：計算梯度
    loss.backward()

    # Adam 更新：更新參數並清除梯度
    optimizer.step()

    # 每 20 個 epoch 打印一次
    if epoch % 20 == 0:
        print(f"Epoch {epoch:3d} | Loss: {loss.data:.4f}")


# ===================== 4. 簡易推論測試 =====================

# 測試：輸入 'a' 預期會預測出 'p'
# 因為訓練資料中，"a" 後面跟著 "p"

# 取得 'a' 的 ID
test_id = token_to_id['a']

# 前向傳播
logits = linear(rmsnorm(emb[test_id]), w_out)

# Softmax
probs = softmax(logits)

# 找到最高機率的索引
pred_id = probs.index(max(probs, key=lambda x: x.data))

# 打印結果
print(f"測試輸入 'a' -> 預測下一個字元: '{vocab[pred_id]}'")


# ===================== 模型架構 =====================
#
# 這個模型是一個最簡單的字元級語言模型：
#
#   Token ID
#      |
#      v
#   Embedding (d_model 維)
#      |
#      v
#   RMS Norm
#      |
#      v
#   Linear (vocab_size 輸出)
#      |
#      v
#   Softmax
#      |
#      v
#   下一個字的機率
#
# 雖然很簡單，但展示了語言模型的核心概念！
#
# ===================== 目標學習 =====================
#
# 訓練資料："apple"
# 我們學習模式：
#   'a' -> 'p'（跟著 'p'）
#   'p' -> 'p'（跟著 'l'）
#   'p' -> 'l'（跟著 'l'）
#   'l' -> 'e'（跟著 'e'）
#
# 所以輸入 'a' 應該預測 'p'！