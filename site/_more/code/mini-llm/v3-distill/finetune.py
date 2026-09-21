import json
import torch
from model import ModernLanguageModel

# 參數設定
batch_size = 32
seq_len = 64
max_iters = 300
learning_rate = 1e-4
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 1. 載入詞表與微調資料
with open('vocab.json', 'r', encoding='utf-8') as f:
    vocab = json.load(f)
vocab_size = vocab['vocab_size']
stoi = vocab['stoi']
itos = {int(k): v for k, v in vocab['itos'].items()}  # json keys are strings
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])

with open('finetune.txt', 'r', encoding='utf-8') as f:
    finetune_text = f.read()
data = torch.tensor(encode(finetune_text), dtype=torch.long)
torch.save(data, 'finetune_data.pt')
print(f"Finetune 資料已建立，長度: {len(data)}")

def get_batch(data):
    ix = torch.randint(len(data) - seq_len, (batch_size,))
    x = torch.stack([data[i:i+seq_len] for i in ix])
    y = torch.stack([data[i+1:i+seq_len+1] for i in ix])
    return x.to(device), y.to(device)

# 2. 初始化模型並載入預訓練權重
model = ModernLanguageModel(vocab_size=vocab_size, seq_len=seq_len, device=device).to(device)
model.load_state_dict(torch.load('pretrain.pt', map_location=device))
print("成功載入 pretrain.pt 權重！")

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
print(f"使用硬體: {device} | 開始 Fine-tuning...")

# 3. 微調訓練迴圈
for iter in range(max_iters):
    model.train()
    xb, yb = get_batch(data)
    
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    
    if iter % 100 == 0 or iter == max_iters - 1:
        print(f"Finetune Step {iter:4d} | Loss: {loss.item():.4f}")

torch.save(model.state_dict(), 'finetune.pt')
print("微調完成！模型已儲存為 finetune.pt")

# ==========================================
# 4. 實測 AI 語言模型 (自動從 finetune.txt 抓取測試題)
# ==========================================
print("\n" + "="*50)
print("測試對話 (自動抓取訓練集第一句進行測試)")
print("="*50)

# 讀取剛剛生成的 finetune.txt 的第一行
try:
    with open('finetune.txt', 'r', encoding='utf-8') as f:
        first_line = f.readline().strip() # 讀取第一行並去掉換行符號
except FileNotFoundError:
    raise FileNotFoundError("找不到 finetune.txt，請確定你有修改 gen_data.py 並重新執行。")

# 假設格式是 "<Q>問題？<A>答案"，我們要把它從 <A> 切開
# 這樣我們只餵給模型 prompt，並把答案留著當對照組
if "<A>" in first_line:
    prompt = first_line.split("<A>")[0] + "<A>"  # 組合出: <Q>問題？<A>
    expected_answer = first_line.split("<A>")[1] # 提取出正確答案
else:
    prompt = first_line
    expected_answer = "(無法解析答案)"

print(f"📝 抽取到的題目: {prompt}")
print(f"🎯 預期的解答: {expected_answer}")
print("-" * 50)

# 將 prompt 轉換為 tensor 並餵給模型
idx = torch.tensor(encode(prompt), dtype=torch.long, device=device).unsqueeze(0)

# max_new_tokens 可以設短一點，因為我們的答案通常很短
generated_idx = model.generate(idx, max_new_tokens=100) 
result = decode(generated_idx[0].tolist())

print(f"🤖 AI 實際輸出:\n{result}")
print("="*50)