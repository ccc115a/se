import random

print("=== 開始生成合成訓練資料 (數學與規律) ===")

# ==========================================
# 1. 定義規則與實體
# ==========================================
# 數字對照表 (限制在相加不超過十)
num_map = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 
           6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}

# 星期規律
days = ["一", "二", "三", "四", "五", "六", "日"]

# 大小比較 (由大到小排列)
animals = ["鯨魚", "大象", "老虎", "狗", "貓", "老鼠", "螞蟻"]

# ==========================================
# 2. 產生知識庫 (Fact Pool)
# ==========================================
pretrain_facts = []
finetune_qa = []

# A. 生成數學加法規律 (1+1=2 到 5+5=10)
for a in range(1, 6):
    for b in range(1, 6):
        c = a + b
        pretrain_facts.append(f"{num_map[a]}加{num_map[b]}等於{num_map[c]}。\n")
        finetune_qa.append(f"<Q>{num_map[a]}加{num_map[b]}等於多少？<A>{num_map[c]}\n")

# B. 生成星期循環規律
for i in range(len(days)):
    today = days[i]
    tomorrow = days[(i + 1) % 7]
    yesterday = days[(i - 1) % 7]
    pretrain_facts.append(f"星期{today}的明天是星期{tomorrow}。\n")
    pretrain_facts.append(f"星期{today}的昨天是星期{yesterday}。\n")
    
    finetune_qa.append(f"<Q>星期{today}的明天是星期幾？<A>星期{tomorrow}\n")
    finetune_qa.append(f"<Q>星期{today}的昨天是星期幾？<A>星期{yesterday}\n")

# C. 生成大小比較規律
for i in range(len(animals)):
    for j in range(i + 1, len(animals)):
        big = animals[i]
        small = animals[j]
        pretrain_facts.append(f"{big}比{small}大。\n")
        pretrain_facts.append(f"{small}比{big}小。\n")
        
        finetune_qa.append(f"<Q>{big}和{small}誰比較大？<A>{big}\n")
        finetune_qa.append(f"<Q>{small}和{big}誰比較小？<A>{small}\n")


# ==========================================
# 3. 擴增資料量 (組合成連續文本)
# ==========================================
# 目標：Pre-train 約產生 20 萬字，Fine-tune 約產生 5 萬字
PRETRAIN_TARGET_LENGTH = 200000
FINETUNE_TARGET_LENGTH = 50000

print(f"-> 正在生成 Pre-train 語料 (目標長度: {PRETRAIN_TARGET_LENGTH} 字)...")
pretrain_text = ""
while len(pretrain_text) < PRETRAIN_TARGET_LENGTH:
    # 隨機抽取知識庫中的句子串接，模擬閱讀文章
    sample = random.sample(pretrain_facts, len(pretrain_facts))
    pretrain_text += "".join(sample)

print(f"-> 正在生成 Fine-tune 語料 (目標長度: {FINETUNE_TARGET_LENGTH} 字)...")
finetune_text = ""
while len(finetune_text) < FINETUNE_TARGET_LENGTH:
    sample = random.sample(finetune_qa, len(finetune_qa))
    finetune_text += "".join(sample)

# 印出幾句給你看
print("\n[Pre-train 文本預覽]:")
print(pretrain_text[:100] + "...\n")
print("[Fine-tune 文本預覽]:")
print(finetune_text[:100] + "...\n")


# ==========================================
# 4. 儲存純文字檔 (供後續 pretrain.py 建立詞表與張量)
# ==========================================
print("-> 儲存純文字檔 (pretrain.txt, finetune.txt)...")
with open('pretrain.txt', 'w', encoding='utf-8') as f:
    f.write(pretrain_text)

with open('finetune.txt', 'w', encoding='utf-8') as f:
    f.write(finetune_text)

print("\n✅ 合成資料準備完成！")