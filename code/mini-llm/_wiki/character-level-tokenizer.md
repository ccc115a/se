# Character-Level Tokenizer — 字元級分詞器

## 概述

**字元級分詞器（Character-Level Tokenizer）** 是最簡單的文字分詞方式：將文字視為單一字元的序列，每個字元（包括標點符號、空白、換行等）作為一個獨立的 token。mini-llm 專案在所有版本中都使用字元級分詞器，這在玩具語言模型中很常見，因為它避免了子詞分詞（如 BPE、WordPiece）的複雜性，且詞表大小極小（通常 < 200 個字元）。

## 動機：為什麼需要分詞器？

神經網路無法直接處理文字，必須將文字轉換為數字。分詞器（Tokenizer）就是文字和數字之間的橋樑：

```
「小貓坐在桌上」→ [12, 35, 7, 28, 15, 9, 42]（每個數字對應一個 token）
```

分詞器的設計是一個權衡：
- **字元級**：詞表最小，但每個 token 的資訊量少，需要更長的序列來表達語義
- **單詞級**：詞表最大（數萬到數百萬），處理未知詞困難（OOV 問題）
- **子詞級**（BPE/WordPiece/Unigram）：折衷方案，兼顧詞表大小和 token 資訊量

## 字元級 Tokenizer 的原理

### 詞表建構

從所有訓練文字中收集不重複的字元（Unicode 字碼點）：

```python
chars = sorted(list(set(text)))
vocab_size = len(chars)
stoi = {ch: i for i, ch in enumerate(chars)}  # 字元 → 索引
itos = {i: ch for i, ch in enumerate(chars)}  # 索引 → 字元
```

### 編碼（Encoding）

```python
encode = lambda s: [stoi[c] for c in s]
# encode("小貓") → [stoi['小'], stoi['貓']]
```

### 解碼（Decoding）

```python
decode = lambda l: ''.join([itos[i] for i in l])
# decode([12, 35]) → "小貓"
```

### mini-llm 的完整流程

```python
# 1. 從語料庫建立詞表
with open('input.txt', 'r', encoding='utf-8') as f:
    text = f.read()
chars = sorted(list(set(text)))
vocab_size = len(chars)

# 2. 建立雙向映射表
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for i, ch in enumerate(chars)}

# 3. 編碼整個語料庫為 tensor
data = torch.tensor(encode(text), dtype=torch.long)
# data.shape = (total_chars,)
```

### 與其他分詞器的比較

| 特性 | Character-Level | Word-Level | BPE / WordPiece | SentencePiece |
|------|----------------|------------|-----------------|---------------|
| 詞表大小 | ~100-200 | ~50k-500k | ~8k-50k | ~8k-50k |
| OOV 問題 | 無 | 嚴重 | 輕微 | 無 |
| 序列長度 | 長（1 token = 1 char） | 短（1 token = 1 word） | 中 | 中 |
| 語言依賴性 | 語言無關 | 需要詞邊界 | 部分語言敏感 | 語言無關 |
| 實作複雜度 | 極低 | 低 | 高 | 高 |
| 參數效率 | 低（長序列） | 高（短序列） | 中 | 中 |

## 字元級 Tokenizer 的優缺點

### 優點

1. **極簡實作** — 只需 `set()`、`sorted()`、`dict()`，約 3 行程式碼
2. **無 OOV（Out-of-Vocabulary）問題** — 任何文字都可以被編碼，不需要特殊的 `<UNK>` token
3. **跨語言通用** — 不需要語言特定的分割規則（如英文的空白分割、中文的分詞）
4. **詞表可忽略** — 100 個字元的詞表意味著嵌入層只需要 `100 × d_model` 個參數，對小模型友好
5. **絕對可逆** — 解碼永遠不會出錯（每個字元都是獨立的 token）

### 缺點

1. **序列長度爆炸** — 英文中一個單詞 ≈ 4-5 個字元，序列長度是子詞級的 4-5 倍
2. **語義稀疏** — 單一字元幾乎沒有語義資訊，「貓」和「狗」共用一個字元「ㄍ」的子部分？（在中文中單字已具有語義，但在拼音文字中問題更嚴重）
3. **自注意力成本** — 注意力計算量是 `O(T²)`，序列長度增加 5 倍意味著計算量增加 25 倍
4. **難以學到高層次模式** — 模型需要從字元層級開始學習所有語言結構（音節、詞素、單詞、片語），需要更深或更大的網路

### 為什麼 mini-llm 使用字元級？

mini-llm 是一個**玩具語言模型**（toy LLM），其設計目標不是極致效能，而是以最簡單的方式展示 LLM 的原理。字元級分詞器讓程式碼核心邏輯清晰，將焦點放在 Transformer 架構而非分詞器的實作細節上。

此外，mini-llm 的語料是繁體中文，中文字元本身就是**語義最小單位**（「貓」是一個字元同時也是一個詞素），不像英文需要從字母組合形成單詞。這使得中文在字元級分詞下的語義密度遠高於英文。

## 詞表儲存格式

在 v2/v3 中，詞表以 `vocab.pkl` 的形式儲存（Pickle 序列化）：

```python
vocab = {
    'stoi': {'小': 0, '貓': 1, '坐': 2, ...},    # 字元→索引
    'itos': {0: '小', 1: '貓', 2: '坐', ...},    # 索引→字元
    'vocab_size': 112                              # 詞表大小
}
```

這個檔案由資料生成腳本（`gen_data_*.py`、`prepare_data.py`）產生，並在後續的 `pretrain.py` 和 `finetune.py` 中被重新載入。

### 跨檔案的一致性要求

**重要**：詞表必須在資料生成、預訓練、微調之間保持一致。每次執行資料生成腳本時都會**重新建立詞表**，如果再次執行資料生成可能產生不同的詞表（因為 Python 的 `set` 排序順序可能不同），這會導致舊的 `.pt` 檔案與新詞表不相容。因此：

1. `vocab.pkl`、`pretrain_data.pt`、`finetune_data.pt` 必須在同一批次中生成
2. 重新生成資料必須從資料生成腳本開始，不能跳過

## 字元級 vs 位元組級

一種相關但不同的方法是用**位元組**（UTF-8 bytes）而非字元作為 token。例如：
- 字元級：`「貓」` → token ID 42
- 位元組級：`「貓」` → [0xE8, 0xB2, 0x93] → [token 232, token 178, token 147]

位元組級（如 GPT-2 的 ByteLevel BPE）的優勢在於詞表固定在 256（一個 byte），但序列長度會增加（中文字元被拆成 3 個位元組）。mini-llm 選擇字元級而非位元組級，以保持簡單性和可讀性。

## 具體範例：中英文序列長度比較

```python
chinese = "貓在墊子上睡覺。"      # 8 個字元 → 8 tokens
english = "The cat sleeps on the mat."  # 26 個字元 → 26 tokens
```

同樣語義，英文序列長度是中文的 3.25 倍。自注意力 O(T²) 下，英文計算量是中文的 10.6 倍。若改用 BPE：英文從 26 tokens 降至約 6 tokens（`["The", " cat", " sleeps", " on", " the", " mat."]`），注意力成本降為字元級的 (6/26)² ≈ 5.3%。

## 程式碼流程追蹤：從文字到嵌入

文字 "小貓睡覺。小狗跑步。" 的完整流程：

```
階段 1 — 詞表建立
  chars = sorted(list(set(text)))  → ['。','上','跑','步','狗','睡','貓','覺']
  stoi = {'。':0,'上':1,'跑':2,'步':3,'狗':4,'睡':5,'貓':6,'覺':7}

階段 2 — 編碼 (字元 → ID)
  ids = [stoi[c] for c in text]    → [6,5,7,0,4,2,3,1]

階段 3 — Tensor 化
  data = torch.tensor(ids, dtype=torch.long)  → shape (8,)

階段 4 — 輸入/目標分割 (下一個字元預測)
  x = data[:-1]  → [6,5,7,0,4,2,3]   y = data[1:] → [5,7,0,4,2,3,1]

階段 5 — 嵌入查表
  embed = nn.Embedding(vocab_size=8, d_model=128)
  tok_emb = embed(x)  → shape (7, 128)
  每個 token ID 查詢對應的 row，本質是學習到的稠密向量

階段 6 — RoPE (旋轉位置編碼)
  q = apply_rotary_emb(query, pos_ids)  # 在注意力內旋轉，不修改嵌入本身

階段 7 — 注意力計算 (O(T²))
  score(t,i) = RoPE(q_t)·RoPE(k_i)/√d_k  → 輸出 shape 維持 (B, S, d_model)
```

形狀追蹤：`str(N) → list[int](N,) → LongTensor(N,) → (N-1,)輸入+(N-1,)目標 → (B,S)嵌入 → (B,S,d_model) → 注意力 → (B,S,d_model) → Linear(vocab_size) → (B,S,vocab_size)`。

## vocab.pkl 結構詳解

`vocab.pkl` 包含三個 key：`stoi`（字元→索引）、`itos`（索引→字元）、`vocab_size`。以極簡語料 `"ABAB"` 為例：

```python
{'stoi': {'A': 0, 'B': 1}, 'itos': {0: 'A', 1: 'B'}, 'vocab_size': 2}
```

實際武俠語料的詞表約 112 個字元，含 ASCII 標點、英文字母、CJK 漢字。`itos` 的 key 是整數，Pickle 保留型別（JSON 會強轉字串）。讀取方式：

```python
with open('vocab.pkl', 'rb') as f:
    vocab = pickle.load(f)
stoi, itos, vocab_size = vocab['stoi'], vocab['itos'], vocab['vocab_size']
```

**Pickle vs JSON**：Pickle 保留 Python 型別、直接可用，但無法跨語言且有安全風險（不載入來路不明的 `.pkl`）。

## Unicode 考量

Python `str` 以 Unicode 碼位計算長度。同一字元在不同編碼層級的 token 數不同：

| 字元 | 碼位 | UTF-8 | 字元級 token | 位元組級 token |
|------|------|-------|-------------|--------------|
| A | U+0041 | 0x41 | 1 | 1 |
| 貓 | U+8C93 | 0xE8 0xB2 0x93 | 1 | 3 |
| 🌸 | U+1F338 | 0xF0 0x9F 0x8C 0xB8 | 1 | 4 |

**組合字元陷阱**：字元 "é" 可表示為單一碼位 U+00E9 或組合序列 U+0065+U+0301。Python 視為不同字串，詞表中出現兩個 token。解決方案是 Unicode 正規化：

```python
import unicodedata
text = unicodedata.normalize('NFC', text)  # 合併為單一碼位
```

mini-llm 未做正規化，因中文語料極少遇到組合字元。**ZWJ 序列**如 "👨‍👩‍👧‍👦"（7 個碼位）被拆成獨立 token，模型無法學到其單一語義。

## sorted(set(text)) 的非確定性風險

詞表建立 `chars = sorted(list(set(text)))` 在 `sorted()` 下是確定性的（依 Unicode 碼位排序），但有兩個實務風險：

**風險 1：訓練文字變更導致索引偏移**。若在 "ABC" 的語料中加入 "!"（U+0021，碼位在 'A' 之前），新詞表 `{'!':0, 'A':1, 'B':2, 'C':3}` 會使舊 `pretrain_data.pt` 的所有 ID 偏移 1 位，完全無法使用。

**風險 2：若移除 `sorted()`**，`list(set(text))` 的順序在 Python 3.6- 每次執行不同（依賴 hash seed），即使 Python 3.7+ `dict` 保留插入順序，`set` 仍不保證跨執行的一致性。

**這就是 AGENTS.md 強調三個檔案必須在同一批次生成的原因。** 更健壯的做法（mini-llm 未採用）：在 `vocab.pkl` 儲存 chars 清單供驗證，載入 `.pt` 時檢查 hash，或使用固定詞表不重新產生。

## 子詞分詞器（BPE）對比

BPE 從單一字元開始，迭代合併最頻繁的相鄰 token 對：

```
原文:    t h e _ c a t _ s l e e p s _ o n _ t h e _ m a t
字元級:  25 tokens
BPE:    [the][_][cat][_][sleeps][_][on][_][the][_][mat] = 10 tokens
序列比: 10/25 = 40%, 注意力成本: (10/25)² = 16%
```

中文的 BPE 收益遠小於英文，因中文字元已接近語義最小單位：
- 中文 `"貓在墊子上睡覺。"`：8 tokens（字元）→ 5 tokens（BPE），縮短 37%
- 英文 `"the cat sleeps"`：14 tokens（字元）→ 5 tokens（BPE），縮短 64%

此外 BPE 需要詞頻統計、合併規則學習、規則編碼，與 mini-llm 的「最小化複雜度」設計哲學相悖。

## 特殊 Token：mini-llm 為什麼不需要

| Token | 用途 | 何以 mini-llm 不需要 |
|-------|------|----------------|
| `<UNK>` | 表外詞 | 字元級無 OOV，任何 Unicode 字元皆可編碼 |
| `<PAD>` | 填充不同長度序列 | 固定 seq_len 連續取塊，無需填充 |
| `<BOS>`/`<EOS>` | 標記序列邊界 | 連續文字流的 next-token 預測，無需邊界標記 |

生成時 mini-llm 持續直到 `gen_len`（無 `<EOS>` 停止訊號），對玩具模型是可接受行為。需要特殊 token 的情境：可變長度獨立序列（需 `<BOS>`/`<EOS>`）、批次填充（需 `<PAD>` + attention mask）、雙向編碼器（需 `<CLS>`/`<MASK>`）。

## 記憶體與注意力成本分析

注意力分數矩陣佔用 O(T²) 記憶體。以 mini-llm 設定（n_heads=4, float32）估算：

| seq_len | 單層注意力矩陣 | 記憶體 |
|---------|--------------|-------|
| 64 | 16K 元素 | 65 KB |
| 1024 | 4.2M 元素 | 16.8 MB |
| 4096 | 67M 元素 | 268 MB |

子詞級序列長度約為字元級的 1/5，記憶體差距達 25 倍（O(T²) 特性）。mini-llm 的 `seq_len=64` 使此問題微不足道（65 KB/層），但現代 LLM 的 8K-128K context 下，字元級分詞完全不可行——**這就是所有生產 LLM 都使用子詞分詞的根本原因**。

## 訓練速度的實際影響

**計算量**：注意力 O(B × n_heads × T² × d_head)，FFN O(B × T × d_model × d_ff)。T 增為 k 倍時注意力增 k² 倍，FFN 增 k 倍。英文語料 k≈4-5 時注意力計算量為子詞級的 16-25 倍。

**學習效率**：字元級每 token 語義資訊少，需更多梯度步驟：

```
字元級: t→h→e→[space]→c→a→t (9 步看到 "the cat")
子詞級: [the]→[space]→[cat]  (3 步看到 "the cat")
```

收斂更慢、有效上下文更短（`seq_len=64` 僅容 ~12 英文單詞）、相鄰字元預測過於簡單。

**mini-llm 實務**：中文語料差距小 + seq_len=64 使影響有限。v2/v3 預訓練 500 steps < 1 分鐘完成。但若擴展（d_model=768, n_layers=12, seq_len=2048, 英文），字元級注意力記憶體達 268 MB/層，收斂需 ~100K 步——從玩具到生產的鴻溝正在於此。

## 延伸閱讀

- 字元級語言模型的經典論文: Karpathy, "The Unreasonable Effectiveness of Recurrent Neural Networks" (2015) — 展示字元級 RNN 生成文字
- BPE: Sennrich et al., "Neural Machine Translation of Rare Words with Subword Units" (ACL 2016)
- WordPiece: Schuster & Nakajima, "Japanese and Korean Voice Search" (ICASSP 2012)
- Unigram LM: Kudo, "Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates" (ACL 2018)
- SentencePiece: Kudo & Richardson, "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing" (2018)
- GPT-2 的 ByteLevel BPE: Radford et al., "Language Models are Unsupervised Multitask Learners" (2019)
