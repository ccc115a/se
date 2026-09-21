import random

print("=== 開始生成合成訓練資料 (虛擬武林) ===")

# 1. 角色與專屬設定 (人物: [地點, 武功, 武器])
characters = {
    "郭靖": ["桃花島", "降龍十八掌", "射鵰神弓"],
    "張無忌": ["光明頂", "九陽神功", "屠龍刀"],
    "楊過": ["絕情谷", "黯然銷魂掌", "玄鐵重劍"],
    "令狐沖": ["華山", "獨孤九劍", "青銅劍"],
    "段譽": ["大理", "六脈神劍", "玉骨扇"]
}

# 武功剋制關係
counters = {
    "降龍十八掌": "蛤蟆功",
    "九陽神功": "玄冥神掌",
    "獨孤九劍": "辟邪劍法",
    "六脈神劍": "一陽指"
}

pretrain_facts = []
finetune_qa = []

# 2. 產生知識庫
for name, attrs in characters.items():
    loc, skill, weapon = attrs
    # Pre-train: 敘述句
    pretrain_facts.append(f"{name}在{loc}苦練{skill}。\n")
    pretrain_facts.append(f"{name}的專屬武器是{weapon}。\n")
    pretrain_facts.append(f"如果要尋找{name}，必須前往{loc}。\n")
    
    # Fine-tune: Q&A
    finetune_qa.append(f"<Q>{name}在哪裡練武？<A>{loc}\n")
    finetune_qa.append(f"<Q>{name}的武功是什麼？<A>{skill}\n")
    finetune_qa.append(f"<Q>{name}使用什麼武器？<A>{weapon}\n")
    finetune_qa.append(f"<Q>去哪裡可以找到{name}？<A>{loc}\n")

for strong, weak in counters.items():
    pretrain_facts.append(f"武林傳言，{strong}能夠完美剋制{weak}。")
    pretrain_facts.append(f"{weak}的剋星正是{strong}。")
    
    finetune_qa.append(f"<Q>什麼武功可以剋制{weak}？<A>{strong}\n")
    finetune_qa.append(f"<Q>{strong}是哪種武功的剋星？<A>{weak}\n")

# 3. 擴增資料量
PRETRAIN_TARGET_LENGTH = 200000
FINETUNE_TARGET_LENGTH = 50000

pretrain_text = ""
while len(pretrain_text) < PRETRAIN_TARGET_LENGTH:
    pretrain_text += "".join(random.sample(pretrain_facts, len(pretrain_facts)))

finetune_text = ""
while len(finetune_text) < FINETUNE_TARGET_LENGTH:
    finetune_text += "".join(random.sample(finetune_qa, len(finetune_qa)))

# 4. 儲存純文字檔 (供後續 pretrain.py 建立詞表與張量)
print("-> 儲存純文字檔 (pretrain.txt, finetune.txt)...")
with open('pretrain.txt', 'w', encoding='utf-8') as f:
    f.write(pretrain_text)

with open('finetune.txt', 'w', encoding='utf-8') as f:
    f.write(finetune_text)
    
print("✅ 武林資料產生完成！")