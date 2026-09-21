import random

print("=== 開始生成合成訓練資料 (智慧家庭助理) ===")

# 1. 意圖對應表 (口語 -> [動作, 設備])
intent_map = {
    "太暗了": ["打開", "燈"],
    "太亮了": ["關閉", "燈"],
    "好熱": ["打開", "冷氣"],
    "好冷": ["關閉", "冷氣"],
    "地板好髒": ["啟動", "掃地機器人"],
    "想看新聞": ["打開", "電視"],
    "有點吵": ["關閉", "電視"]
}

locations = ["客廳", "臥室", "廚房"]

pretrain_facts = []
finetune_qa = []

# 2. 產生知識庫
for loc in locations:
    for trigger, action in intent_map.items():
        act, device = action
        # 系統全稱
        sys_cmd = f"系統指令：{act}{loc}{device}"
        
        # Pre-train: 敘述規則
        pretrain_facts.append(f"當主人在{loc}說「{trigger}」時，就是要執行{sys_cmd}。\n")
        pretrain_facts.append(f"人工智慧收到「把{loc}的{device}{act}」的命令時，對應的{sys_cmd}。\n")
        
        # Fine-tune: Q&A (直接轉換)
        # 類型一：口語意圖轉換
        finetune_qa.append(f"<Q>我在{loc}，{trigger}。<A>{sys_cmd}\n")
        # 類型二：明確指令轉換
        finetune_qa.append(f"<Q>請幫我{act}{loc}的{device}。<A>{sys_cmd}\n")

# 加入一些狀態報告
for loc in locations:
    pretrain_facts.append(f"{loc}的環境感測器目前顯示溫度正常。")
    finetune_qa.append(f"<Q>{loc}目前的溫度如何？<A>溫度正常\n")

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
    
print("✅ 機器人指令產生完成！")