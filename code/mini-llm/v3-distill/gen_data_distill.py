import os
import random
from openai import OpenAI

print("=== 開始執行大模型資料蒸餾 (Knowledge Distillation) ===")

# ==========================================
# 1. 初始化 NVIDIA API Client
# ==========================================
# 從環境變數讀取 API KEY
api_key = os.environ.get("NVIDIA_API_KEY")
if not api_key:
    raise ValueError("找不到 NVIDIA_API_KEY！請先在終端機執行: export NVIDIA_API_KEY='你的金鑰'")

client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=api_key
)

# ==========================================
# 2. 設計 Prompt 逼迫大模型產出特定格式的訓練資料
# ==========================================
# 為了避免我們的小模型詞表爆掉，我們要求大模型使用簡單的詞彙，並嚴格限制格式。
prompt = """
請扮演一個嚴格的資料生成器。我要訓練一個微型語言模型，請幫我生成關於「太陽系八大行星」的訓練資料。
請使用極度簡單的繁體中文，並且嚴格遵守以下兩種格式，不要輸出任何其他廢話或解說。

格式1 (知識敘述)：[FACT] 敘述句。
格式2 (問答訓練)：[QA] <Q>問題？<A>答案

請生成 50 句 [FACT] 和 50 句對應的 [QA]。

範例：
[FACT] 地球是太陽系中唯一有生命的行星。
[FACT] 火星的表面是紅色的。
[QA] <Q>哪顆行星有生命？<A>地球
[QA] <Q>火星的表面是什麼顏色？<A>紅色
"""

print("-> 正在呼叫 Minimax 大模型生成教材，請稍候...\n")

completion = client.chat.completions.create(
  model="minimaxai/minimax-m2.7",
  messages=[{"role":"user", "content": prompt}],
  temperature=0.7, # 稍微降低溫度，讓格式更穩定
  top_p=0.95,
  max_tokens=8192,
  stream=True
)

# ==========================================
# 3. 接收 Streaming 回應並解析資料
# ==========================================
teacher_response = ""
print("👨‍🏫 Teacher 產出中：")
for chunk in completion:
    if not getattr(chunk, "choices", None):
        continue
    if chunk.choices[0].delta.content is not None:
        content = chunk.choices[0].delta.content
        print(content, end="")
        teacher_response += content

print("\n\n-> 接收完畢，開始解析資料...")

# 解析大模型的輸出
pretrain_facts = []
finetune_qa = []

for line in teacher_response.split('\n'):
    line = line.strip()
    if line.startswith("[FACT]"):
        pretrain_facts.append(line.replace("[FACT]", "").strip()+"\n")
    elif line.startswith("[QA]"):
        finetune_qa.append(line.replace("[QA]", "").strip() + "\n")

if len(pretrain_facts) == 0 or len(finetune_qa) == 0:
    raise ValueError("大模型沒有按照格式輸出，請重新執行一次。")

print(f"-> 成功解析出 {len(pretrain_facts)} 條知識，{len(finetune_qa)} 條問答。")

# ==========================================
# 4. 擴增資料量以滿足神經網路訓練需求
# ==========================================
# 因為大模型只生成了幾十句，對神經網路來說太少了，我們將它重複打亂拼接
PRETRAIN_TARGET_LENGTH = 100000
FINETUNE_TARGET_LENGTH = 30000

pretrain_text = ""
while len(pretrain_text) < PRETRAIN_TARGET_LENGTH:
    pretrain_text += "".join(random.sample(pretrain_facts, len(pretrain_facts)))

finetune_text = ""
while len(finetune_text) < FINETUNE_TARGET_LENGTH:
    finetune_text += "".join(random.sample(finetune_qa, len(finetune_qa)))

# ==========================================
# 5. 儲存純文字檔 (供後續 pretrain.py 建立詞表與張量)
# ==========================================
print("-> 儲存純文字檔 (pretrain.txt, finetune.txt)...")
with open('pretrain.txt', 'w', encoding='utf-8') as f:
    f.write(pretrain_text)

with open('finetune.txt', 'w', encoding='utf-8') as f:
    f.write(finetune_text)

print("✅ 大模型蒸餾資料準備完成！請繼續執行 pretrain.py 和 finetune.py")