"""
ex4-classify.py — Softmax 與 Cross-Entropy Loss 演示

本程式展示：
  1. Softmax 函數的數值穩定實現
  2. Cross-Entropy Loss 的計算
  3. 如何進行反向傳播

執行方式：
  python ex4-classify.py
"""

from nn0 import Value, softmax


# ===================== 1. 建立模型輸出 =====================

# 假設這是神經網路最後一層輸出的三個類別分數 (Logits)
# logits 代表未歸一化的分數，通常稱為分數或分對數機率（log-odds）
#
# 這些值會通過 softmax 轉換為機率
logits = [Value(2.0), Value(1.0), Value(0.1)]

# 假設正確的類別索引是 0
# 也就是說，第一類是正確的類別
target_idx = 0

# 打印標題
print("\n=== 4. Softmax 與 Cross-Entropy Loss ===")


# ===================== 2. 計算 Softmax 機率 =====================

# Softmax 函數：將分數轉換為機率分布
#   softmax(x)[i] = e^x[i] / Σ_j e^x[j]
#
# 使用數值穩定版本：
#   先減去最大值，再計算指數，避免溢位
probs = softmax(logits)


# ===================== 3. 計算 Cross-Entropy Loss =====================

# Cross-Entropy Loss：-log(P[target])
#
# 這是分類任務中標準的損失函數
# 數學意義：
#   Loss = -log(probs[target_idx])
#   = -log(e^logit[target_idx] / Σ_j e^logit[j])
#
# 特性：
#   - 當預測正確時（機率 → 1），Loss → 0
#   - 當預測錯誤時（機率 → 0），Loss → ∞
loss = -probs[target_idx].log()


# ===================== 4. 反向傳播 =====================

# 反向傳播計算梯度
loss.backward()


# ===================== 5. 顯示結果 =====================

# 打印 logits（原始分數）
print("Logits    :", [round(l.data, 4) for l in logits])

# 打印 softmax 機率（歸一化後的機率，總和為 1）
print("Probs     :", [round(p.data, 4) for p in probs])

# 打印 Cross-Entropy Loss
print(f"Loss      : {loss.data:.4f}")

# 打印梯度
# 梯度解釋：
#   - 第一個類別（正確類別）的梯度是負的：網路需要降低這個 logit
#   - 其他類別的梯度是正的：網路需要增加這些 logit
print("Logits 梯度:", [round(l.grad, 4) for l in logits])


# ===================== 數學原理 =====================
#
# Softmax：
#   p_i = e^(x_i - M) / Σ_j e^(x_j - M)
#   其中 M = max(x)，確保數值穩定
#
# Cross-Entropy Loss：
#   L = -log(p_target)
#   = -log(e^(x_target) / Σ_j e^(x_j))
#   = log(Σ_j e^(x_j)) - x_target
#   = log(Σ_j e^(x_j - M)) + M - x_target
#
# 梯度（反向傳播）：
#   ∂L/∂x_i = p_i - δ_i,target
#   - 正確類別 i：梯度 = p_i - 1（負的，降低輸出）
#   - 錯誤類別 i：梯度 = p_i - 0（正的，增加輸出）
#
# 這保證了：
#   - 增加正確類別的機率
#   - 減少錯誤類別的機率