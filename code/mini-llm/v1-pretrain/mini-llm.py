# https://aistudio.google.com/prompts/15h0wS5NLXOu5FCitgVVXYof1_vLrth7_
import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import argparse
import os

# ==========================================
# 1. 現代 LLM 核心架構組件
# ==========================================
class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        norm_x = torch.mean(x ** 2, dim=-1, keepdim=True)
        x_normed = x * torch.rsqrt(norm_x + self.eps)
        return self.weight * x_normed

def precompute_freqs_cis(dim: int, end: int, theta: float = 10000.0):
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2)[: (dim // 2)].float() / dim))
    t = torch.arange(end, device=freqs.device)
    freqs = torch.outer(t, freqs).float()
    freqs_cis = torch.polar(torch.ones_like(freqs), freqs)
    return freqs_cis

def apply_rotary_emb(xq, xk, freqs_cis):
    xq_ = torch.view_as_complex(xq.float().reshape(*xq.shape[:-1], -1, 2))
    xk_ = torch.view_as_complex(xk.float().reshape(*xk.shape[:-1], -1, 2))
    freqs_cis = freqs_cis.unsqueeze(0).unsqueeze(2)
    xq_out = torch.view_as_real(xq_ * freqs_cis).flatten(3)
    xk_out = torch.view_as_real(xk_ * freqs_cis).flatten(3)
    return xq_out.type_as(xq), xk_out.type_as(xk)

class FeedForward(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, hidden_dim, bias=False)

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)) * self.w3(x))

class Attention(nn.Module):
    def __init__(self, dim, n_heads):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.wq = nn.Linear(dim, dim, bias=False)
        self.wk = nn.Linear(dim, dim, bias=False)
        self.wv = nn.Linear(dim, dim, bias=False)
        self.wo = nn.Linear(dim, dim, bias=False)

    def forward(self, x, freqs_cis):
        B, T, C = x.shape
        q = self.wq(x).view(B, T, self.n_heads, self.head_dim)
        k = self.wk(x).view(B, T, self.n_heads, self.head_dim)
        v = self.wv(x).view(B, T, self.n_heads, self.head_dim)

        q, k = apply_rotary_emb(q, k, freqs_cis[:T])

        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        mask = torch.tril(torch.ones(T, T, device=x.device)).view(1, 1, T, T)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
        att = att.masked_fill(mask == 0, float('-inf'))
        att = F.softmax(att, dim=-1)

        out = att @ v
        out = out.transpose(1, 2).contiguous().view(B, T, C)
        return self.wo(out)

class TransformerBlock(nn.Module):
    def __init__(self, dim, n_heads):
        super().__init__()
        self.attention = Attention(dim, n_heads)
        self.ffn = FeedForward(dim, hidden_dim=4 * dim)
        self.norm1 = RMSNorm(dim)
        self.norm2 = RMSNorm(dim)

    def forward(self, x, freqs_cis):
        x = x + self.attention(self.norm1(x), freqs_cis)
        x = x + self.ffn(self.norm2(x))
        return x

class ModernLanguageModel(nn.Module):
    def __init__(self, vocab_size, d_model, n_heads, n_layers, seq_len, device):
        super().__init__()
        self.tok_emb = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([TransformerBlock(d_model, n_heads) for _ in range(n_layers)])
        self.norm = RMSNorm(d_model)
        self.output = nn.Linear(d_model, vocab_size, bias=False)
        
        # 權重共享 (Tie weights) - 減少參數量
        self.tok_emb.weight = self.output.weight 
        
        self.freqs_cis = precompute_freqs_cis(d_model // n_heads, seq_len * 2).to(device)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.tok_emb(idx)
        
        for layer in self.layers:
            x = layer(x, self.freqs_cis)
            
        x = self.norm(x)
        logits = self.output(x)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B*T, C)
            targets = targets.view(B*T)
            loss = F.cross_entropy(logits, targets)
            
        return logits, loss

# ==========================================
# 2. 獨立的輔助函式與流程控制
# ==========================================
def get_batch(data, batch_size, seq_len, device):
    """隨機抽樣一組訓練資料 (x, y)"""
    ix = torch.randint(len(data) - seq_len, (batch_size,))
    x = torch.stack([data[i:i+seq_len] for i in ix])
    y = torch.stack([data[i+1:i+seq_len+1] for i in ix])
    return x.to(device), y.to(device)


def train(model, data, optimizer, batch_size, seq_len, max_iters, eval_interval, device):
    """獨立的訓練函式"""
    model.train()
    print("開始訓練...")
    
    for iter in range(max_iters):
        xb, yb = get_batch(data, batch_size, seq_len, device)
        
        logits, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        if iter % eval_interval == 0 or iter == max_iters - 1:
            print(f"Step {iter:4d} | Loss: {loss.item():.4f}")


@torch.no_grad()
def generate(model, start_str, encode_fn, decode_fn, seq_len, max_new_tokens, device):
    """獨立的生成函式"""
    model.eval()
    
    # 將開頭字串編碼成 Tensor
    idx = torch.tensor(encode_fn(start_str), dtype=torch.long, device=device).unsqueeze(0)
    
    for _ in range(max_new_tokens):
        # 確保輸入不超過模型支援的最大 seq_len
        idx_cond = idx[:, -seq_len:]
        
        # 進行推理，不計算 Loss
        logits, _ = model(idx_cond)
        
        # 取最後一個時間步的預測
        logits = logits[:, -1, :] 
        probs = F.softmax(logits, dim=-1)
        
        # 根據機率隨機採樣下一個 Token
        idx_next = torch.multinomial(probs, num_samples=1)
        
        # 拼接生成的 Token
        idx = torch.cat((idx, idx_next), dim=1)
        
    return decode_fn(idx[0].tolist())

# ==========================================
# 3. 主程式 Main
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="現代化微型語言模型訓練程式")
    parser.add_argument('--file', '-f', type=str, required=True, help="要訓練的 txt 檔案路徑")
    parser.add_argument('--iters', type=int, default=2000, help="訓練步數 (預設: 2000)")
    parser.add_argument('--seq_len', type=int, default=32, help="上下文長度 (預設: 32)")
    parser.add_argument('--batch_size', type=int, default=16, help="批次大小 (預設: 16)")
    parser.add_argument('--gen_len', type=int, default=100, help="生成字元數 (預設: 100)")
    args = parser.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用硬體: {device}")

    # 1. 讀取與處理資料
    if not os.path.exists(args.file):
        raise FileNotFoundError(f"找不到檔案: {args.file}")
        
    with open(args.file, 'r', encoding='utf-8') as f:
        text = f.read()

    if len(text) <= args.seq_len:
        raise ValueError(f"檔案內容太短！文字長度 ({len(text)}) 必須大於上下文長度 seq_len ({args.seq_len})")

    # 2. 建立簡單字元級 Tokenizer
    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    print(f"成功讀取檔案。總字元數: {len(text)} | 詞表大小: {vocab_size}")

    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])

    data = torch.tensor(encode(text), dtype=torch.long)

    # 3. 初始化模型與優化器
    d_model = 128
    n_heads = 4
    n_layers = 3
    learning_rate = 3e-4

    model = ModernLanguageModel(
        vocab_size=vocab_size, 
        d_model=d_model, 
        n_heads=n_heads, 
        n_layers=n_layers, 
        seq_len=args.seq_len, 
        device=device
    ).to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    print(f"模型參數總數: {sum(p.numel() for p in model.parameters()) / 1e6:.3f} M")

    # 4. 呼叫訓練函式
    eval_interval = max(1, args.iters // 10)
    train(
        model=model, 
        data=data, 
        optimizer=optimizer, 
        batch_size=args.batch_size, 
        seq_len=args.seq_len, 
        max_iters=args.iters, 
        eval_interval=eval_interval, 
        device=device
    )

    # 5. 呼叫生成函式
    start_str = text[:3].replace('\n', ' ') if len(text) >= 3 else text[0]
    print(f"\n=== 生成結果 (Prompt: '{start_str}') ===")
    
    generated_text = generate(
        model=model, 
        start_str=start_str, 
        encode_fn=encode, 
        decode_fn=decode, 
        seq_len=args.seq_len, 
        max_new_tokens=args.gen_len, 
        device=device
    )
    print(generated_text)


if __name__ == "__main__":
    main()