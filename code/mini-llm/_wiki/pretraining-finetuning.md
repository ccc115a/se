# Pretraining + Fine-tuning — 預訓練與微調範式

## 概述

**Pretraining + Fine-tuning（預訓練 + 微調）** 是現代自然語言處理中最核心的訓練範式。其理念為：先在大量通用未標註資料上進行預訓練（pretraining），讓模型學習通用的語言知識；然後在特定任務的小量標註資料上進行微調（fine-tuning），讓模型適應特定任務。mini-llm 專案 v2 和 v3 都實現了這個兩階段流程。

## 動機：為什麼需要兩階段？

### 資料困境

傳統的監督學習需要大量標註資料，而標註資料的獲取成本極高：
- 一個英文問答資料集的構建可能需要數百人時
- 專業領域（醫學、法律）的標註成本更高

與此同時，**未標註的文字資料**在網路上極其豐富（互聯網內容、書籍、論文等）。

### 遷移學習的合理假設

預訓練 + 微調建立在一個核心假設上：**語言知識是可以遷移的**。模組在預訓練階段學會的語言理解能力（語法、語義、世界知識）可以作為良好起點，只需少量調整就能適應特定任務。

這類似於人類學習：先大量閱讀理解語言（預訓練），然後學習特定的寫作風格（微調）。

## 預訓練（Pre-training）

### 目標

預訓練的訓練目標是**自監督學習（Self-supervised Learning）**— 從文字本身的結構中自動產生訓練標籤，不需要人工標註。

最常見的預訓練目標有：
1. **下一 token 預測（Next Token Prediction, NTP）** — 給定前 `t-1` 個 token，預測第 `t` 個（GPT 系列）
2. **遮蓋語言建模（Masked Language Modeling, MLM）** — 隨機遮蓋部分 token，讓模型還原（BERT）
3. **序列到序列去噪（Denoising Autoencoding）** — 對輸入加入雜訊，讓模型恢復（T5）

mini-llm 使用 **NTP**（因果語言建模）：

```python
# 每個位置的目標就是下一個位置的 token
x = data[i:i+seq_len]       # 輸入: [x₁, x₂, ..., x_T]
y = data[i+1:i+seq_len+1]   # 目標: [x₂, x₃, ..., x_{T+1}]

logits, loss = model(x, y)  # 計算 cross-entropy loss
```

### 資料

預訓練使用**大量通用語料**。在 mini-llm 中：
- v1: 使用 `input.txt`（約 1500 字的手寫語句）
- v2: 使用合成產生的資料（約 20 萬字的隨機排列句子）
- v3: 使用知識蒸餾產生的資料（約 10 萬字的事實敘述）

### 訓練配置

預訓練通常使用較高的學習率和更多的訓練步數：

```python
# mini-llm v2/v3 預訓練
max_iters = 500
learning_rate = 5e-4  # 較高
batch_size = 32
seq_len = 64
```

### 保存

預訓練完成後，模型權重保存為 `pretrain.pt`：

```python
torch.save(model.state_dict(), 'pretrain.pt')
```

### 典型損失曲線

以下是 mini-llm v2 一次實際運行的交叉熵損失變化記錄，展示了兩階段的典型行為：

| 階段 | 步驟 | 損失值 | 說明 |
|------|------|--------|------|
| 預訓練 | 0 | 4.89 | 初始隨機預測（均均分佈：ln(112)≈4.72） |
| 預訓練 | 100 | 0.27 | 快速下降期，模型學習了基本字元分佈 |
| 預訓練 | 500 | 0.22 | 收斂完成，對訓練語料的擬合度很高 |
| 微調開始 | 0 | **6.41** | 注意！資料格式變化導致損失急劇彈回 |
| 微調 | 100 | 0.34 | 快速適應 Q&A 格式 |
| 微調 | 300 | 0.21 | 最終收斂 |

**關鍵觀察**：

- **損失彈跳**：微調第一步損失（6.41）遠高於預訓練最後一步（0.22），高達 ln(112)≈4.72 的隨機基線。原因是資料從連續敘述句變成了 Q&A 格式 — 模型從未見過 `<Q>`、`<A>` 和 `？` 這些符號在特定位置的組合，預訓練學到的條件機率分佈在新的上下文下一開始完全失效。

- **快速適應**：微調僅需約 100 步就能將損失從 6.41 降至 0.34。這說明遷移學習確實有效 — 模型已經知道中文的內部結構（主謂賓、常見搭配），只需要學新格式與內容之間的映射。

- **最終損失比預訓練略低**：微調最終損失（0.21）略低於預訓練最終損失（0.22），部分原因是 Q&A 格式比自然敘述更規律（模板化），但也暗示可能有一定程度的過擬合（見後文討論）。

## 微調（Fine-tuning）

### 目標

微調在**相同架構**下使用**不同格式的資料**繼續訓練，讓模型學習特定的輸入輸出行為模式。

mini-llm 的微調資料使用 Q&A 格式：
```
<Q>令狐沖的武功是什麼？<A>獨孤九劍
<Q>段譽在哪裡練武？<A>大理
```

模型學會在看到 `<Q>...<A>` 後自動生成對應的答案。

### 關鍵差異

| 特性 | 預訓練 | 微調 |
|------|--------|------|
| 資料量 | 大（10 萬–20 萬字） | 小（3 萬–5 萬字） |
| 學習率 | 高（5e-4） | 低（1e-4） |
| 訓練步數 | 多（500） | 少（300） |
| 資料格式 | 一般敘述句 | 問答格式 |
| 目標 | 學習語言結構 | 學習特定任務行為 |

### 權重載入

微調的關鍵是**載入預訓練權重**作為初始狀態，而不是從隨機初始化開始：

```python
# 初始化模型架構（必須與預訓練時完全一致）
model = ModernLanguageModel(vocab_size=vocab_size, ...)
# 載入預訓練權重
model.load_state_dict(torch.load('pretrain.pt', map_location=device))
```

**重要限制**：載入的 `pretrain.pt` 與模型架構必須完全匹配。這意味著模型的 `vocab_size`、`d_model`、`n_layers`、`n_heads` 在兩個階段必須一致。如果改變了詞表（如重新生成 `vocab.pkl`），則舊的 `pretrain.pt` 無法使用。

### 為什麼使用較低的學習率？

微調時使用較低的學習率（`1e-4` vs `5e-4`）是為了**避免災難性遺忘（Catastrophic Forgetting）**：

- 如果學習率太高，模型的權重會劇烈變化，忘記預訓練學到的通用語言知識
- 較低的學習率讓模型在已有知識的附近微調，保留語言能力同時學習任務特定模式

### 學習率過高的具體後果

若將微調學習率設為 `5e-4`（與預訓練相同），模型會發生災難性遺忘。原因在於 AdamW 最佳化器在較高學習率下會對權重進行大幅度更新，而微調資料的分布與預訓練資料顯著不同（Q&A vs 敘述句），導致權重偏離預訓練學習到的語言表徵：

```
# 假設執行了錯誤的設定
learning_rate = 5e-4  # 錯誤！使用了預訓練的學習率

# 預期輸出（正常微調）
<Q>令狐沖的武功是什麼？<A>獨孤九劍

# 實際輸出（學習率過高 — 模型崩潰）
<Q>令狐沖的武功是什麼？<A>的武功是什麼武功是什麼武功是什麼武功...
```

模型陷入重複循環，輸出的 token 基本無意義。這是因為權重大幅改變後，模型失去了合理的下一個字元預測能力，注意力模式被破壞，從自然的機率分布退化為簡單的重複模式。這在小型模型中尤為明顯 — 參數量越少，對權重變化的容忍度越低。

### 資料量與過擬合風險

mini-llm 的微調資料僅約 **50,000 字元**，以字元級模型而言是非常小的資料集（約相當於 8,000–10,000 個中文字）。這種情況下**過擬合（Overfitting）風險**存在：

- **訓練損失不斷下降**但**生成品質可能沒有提升** — 模型背誦了訓練資料中的 Q&A 模式，但對未見過的提問泛化能力有限
- mini-llm 的 Q&A 資料僅圍繞 5 個角色和 4 組武功剋制關係（`gen_data_wuxia.py`），多樣性極低
- 50,000 字元中有大量重複（隨機排列同一組 Q&A 對直到達到目標長度）

在 mini-llm 的規模（4 層，d_model=128，約 40 萬參數）下，50K 字元微調資料尚可接受，因為模型容量有限，不容易記住全部模式。但觀察微調損失曲線：300 步後損失低於 0.21，在 112 個字元的詞表上這非常低 — 如果訓練更多步數，損失可能趨近於 0，意味著模型幾乎完美記住了訓練資料中的 Q&A 配對。此時測試集（用未見過的人名提問）表現會很差。

### 微調 vs Few-shot vs Zero-shot

| 方法 | 需要重新訓練？ | 需要標註資料？ | 適合模型規模 |
|------|--------------|---------------|-------------|
| Zero-shot | 否 | 無 | 大型模型（7B+ 參數） |
| Few-shot | 否 | 少量範例（放入 prompt） | 大型模型（1B+ 參數） |
| Fine-tuning | 是 | 中等量標註資料 | 任意規模 |

**為什麼 mini-llm 必須用微調？** mini-llm 的模型只有約 40 萬參數，遠小於 GPT-3（1,750 億參數）。這種小型模型缺乏從 prompt 中學習新任務模式的**上下文學習（In-Context Learning）**能力 — 其注意力頭數量（4 個）和隱藏維度（128）不足以在推理時從 prompt 範例中提取和應用任務結構。對於這類模型，唯一的選項是微調：直接更新權重，將任務模式寫入模型參數中。

## 兩階段訓練的類比

```
預訓練：讓一個人在圖書館讀 1000 本書（累積知識）
微調：　讓這個人讀一本特定的操作手冊（學習特定技能）

沒有預訓練的微調：讓嬰兒直接讀操作手冊（沒有基礎知識，無法理解）
沒有微調的預訓練：讀了 1000 本書但不會回答具體問題（缺乏任務適配）
```

## 聯合訓練 vs 兩階段訓練

除了預訓練 + 微調這種兩階段方法，還有其他範式：

### 1. 從零開始訓練（Scratch Training）

直接在任務資料上從隨機初始化開始訓練。只有當任務資料極大時才可行，否則效果遠差於預訓練 + 微調。

### 2. 多任務聯合訓練（Multi-task Learning）

同時在多個任務上訓練，共用底層表示。如 T5 和 InstructGPT 的訓練方式。

### 3. 持續預訓練（Continual Pre-training）

在預訓練後加入領域特定語料的額外預訓練階段，再進行微調。例如：通用預訓練 → 醫學語料持續預訓練 → 醫療問答微調。

### 4. 指令微調（Instruction Tuning）

一種特殊的微調，使用大量多樣化的指令資料（instruction + response）進行微調，讓模型學會遵循各種指令。這是 ChatGPT 訓練流程中的關鍵步驟。

## mini-llm 的完整流程

```
v2-finetune/ 或 v3-distill/ 目錄下：

1. 資料生成
   gen_data_wuxia.py      # 武俠知識資料（合成）
   或 gen_data_rule.py     # 數學/規律資料（合成）
   或 gen_data_robot.py    # 智慧家庭助理資料（合成）
   或 gen_data_distill.py  # 知識蒸餾資料（大模型生成）
   ↓ 輸出
   vocab.pkl              # 字元級詞表
   pretrain_data.pt       # 預訓練語料 tensor
   finetune_data.pt       # 微調語料 tensor
   pretrain.txt           # 純文字版預訓練語料
   finetune.txt           # 純文字版微調語料

2. 預訓練
   python pretrain.py
   ↓ 讀取 vocab.pkl 和 pretrain_data.pt
   ↓ 訓練 500 步
   ↓ 輸出 pretrain.pt

3. 微調
   python finetune.py
   ↓ 讀取 vocab.pkl、finetune_data.pt、pretrain.pt
   ↓ 載入 pretrain.pt 權重
   ↓ 訓練 300 步
   ↓ 輸出 finetune.pt
   ↓ 自動測試（從 finetune.txt 第一句出題）
```

這個流程中的每個腳本都設計成**獨立可執行**的 Python 檔案，沒有任何輔助函式庫或框架的依賴，便於理解和修改。

### 操作順序的嚴格約束

mini-llm 的三個步驟（資料生成 → 預訓練 → 微調）**必須嚴格依序執行**，因為每一步的輸出是下一步的輸入：

```
# 錯誤示範 1：跳過資料生成直接預訓練
$ python pretrain.py
Traceback (most recent call last):
  File "pretrain.py", line 13, in <module>
    with open('vocab.pkl', 'rb') as f:
FileNotFoundError: [Errno 2] No such file or directory: 'vocab.pkl'
# → vocab.pkl 由 gen_data_*.py 產生，缺少它則無法建立詞嵌入層和編碼資料

# 錯誤示範 2：更換資料生成器後不重新預訓練
$ python gen_data_robot.py   # 產生了新的 vocab.pkl（詞表不同）
$ python finetune.py         # 直接執行微調
RuntimeError: Error(s) in loading state_dict for ModernLanguageModel:
    size mismatch for tok_emb.weight: copying a param with shape
    torch.Size([112, 128]) from checkpoint, the current shape
    is torch.Size([98, 128])
# → pretrain.pt 是用舊詞表訓練的，新 vocab.pkl 的詞表大小不同
# → 解決方案：每次更換資料生成器後必須完整執行三步驟

# 正確流程
$ python gen_data_wuxia.py   # 步驟 1: 產生 vocab.pkl, pretrain_data.pt, finetune_data.pt
$ python pretrain.py         # 步驟 2: 使用上述檔案，輸出 pretrain.pt
$ python finetune.py         # 步驟 3: 載入 pretrain.pt 進行微調
```

### 詞表不一致導致權重載入失敗的機制

`torch.load('pretrain.pt')` 恢復的模型權重字典中包含**所有可學習參數**的張量，其中包括詞嵌入層（`tok_emb.weight`）和輸出線性層（`output.weight`）。由於 mini-llm 使用了**權重綁定（weight tying）**，這兩個層共用同一個權重矩陣，形狀為 `[vocab_size, d_model]`。

當 `vocab.pkl` 被重新產生時（例如切換資料生成器或修改資料內容），詞表大小 `vocab_size` 可能改變：

```
# gen_data_wuxia.py 產生的詞表（5 個角色 + 武功描述）：vocab_size=112
# pretrain.pt 中 tok_emb.weight 的形狀: [112, 128]

# gen_data_robot.py 產生的詞表（家電場景，不同字元集合）：vocab_size=98
# 新模型的 tok_emb.weight 形狀: [98, 128]

# load_state_dict() 報錯：
# RuntimeError: size mismatch for tok_emb.weight:
#   copying a param with shape torch.Size([112, 128])
#   from checkpoint, the current shape is torch.Size([98, 128])
```

即使詞表大小相同，如果字元順序改變（同一個字元被賦予不同索引），模型的行為也會完全錯亂 — 因為 `stoi` 映射改變了，但權重矩陣的行對應的是舊索引。解決方案只有一個：**每次更換資料生成器後，重新執行完整的** `gen_data → pretrain → finetune` 三步驟。

### 資料格式轉換步驟

mini-llm 的字元級 tokenizer 將每個獨特字元映射為一個整數索引。從原始文字到訓練 tensor 經歷以下轉換：

```
原始資料（gen_data_wuxia.py 產生的中間文字）:

  預訓練文字片段:
  "郭靖在桃花島苦練降龍十八掌。\n令狐沖的專屬武器是青銅劍。\n"

  微調文字片段:
  "<Q>郭靖的武功是什麼？<A>降龍十八掌\n<Q>令狐沖在哪裡練武？<A>華山\n"

步驟 1：掃描所有字元，建立詞表（vocab.pkl）
  stoi = {
    'G': 0, 'u': 1, 'o': 2, 'J': 3, 'i': 4, 'n': 5,
    'g': 6, 'z': 7, 'a': 8, 'i': 9, ...
    '郭': 23, '靖': 24, '在': 25, '桃': 26, '花': 27, '島': 28,
    '苦': 29, '練': 30, ...
    '＜': 87, 'Q': 88, '＞': 89, '？': 90, 'A': 91,
    '\n': 92
  }
  itos = {v: k for k, v in stoi.items()}
  vocab_size = 93  （取決於實際字元集合）

步驟 2：將整段文字轉換為整數序列（pretrain_data.pt / finetune_data.pt）
  "郭靖在桃花島苦練降龍十八掌。" →
  [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]

  最終輸出的 tensor 形狀為 [N]（N = 總字元數），例如 pretrain_data.pt 約 [200160]

步驟 3：訓練時 get_batch() 從長序列中隨機裁切
  ix = torch.randint(len(data) - seq_len, (batch_size,))
  # 例如 ix = [45023, 7891, 120456, ...]
  # 從每個偏移位置取出連續 seq_len=64 個 token 作為 x
  # x[i] 對應的目標是 x[i+1]（右移一位）

  批次範例:
  x = [23, 24, 25, 26, 27, 28, 29, 30, ...]  # 64 個 token
  y = [24, 25, 26, 27, 28, 29, 30, 31, ...]  # 與 x 錯位 1
```

關鍵區別：預訓練資料是自然敘述句的連續串聯，模型學習「下一個字元是什麼」的語言統計規律；微調資料是 Q&A 對的重複排列，模型學習「看到 `<Q>...<A>` 後應該接答案」的任務格式。

### 微調測試機制

`finetune.py` 在訓練結束後會自動進行一次實測，驗證模型是否學會了 Q&A 行為。其實現位於第 54–89 行：

```python
# 1. 從 finetune.txt 讀取第一行
first_line = open('finetune.txt', 'r', encoding='utf-8').readline().strip()
# 範例: "<Q>令狐沖的武功是什麼？<A>獨孤九劍"

# 2. 在 <A> 處切分，提取 prompt 和預期答案
prompt = first_line.split("<A>")[0] + "<A>"
# → "<Q>令狐沖的武功是什麼？<A>"

expected_answer = first_line.split("<A>")[1]
# → "獨孤九劍"

# 3. 將 prompt 編碼為 tensor 並生成
idx = torch.tensor(encode(prompt), dtype=torch.long, device=device).unsqueeze(0)
generated = model.generate(idx, max_new_tokens=100)
result = decode(generated[0].tolist())
```

由於微調資料是大量 Q&A 對的串聯（如 `<Q>A？<A>B\n<Q>C？<A>D\n...`），模型學會了整個格式模式 — 不僅會回答問題，還會在回答完後繼續生成下一個問題。因此實際輸出可能如下：

```
# prompt 輸入
<Q>令狐沖的武功是什麼？<A>

# 模型輸出
<Q>令狐沖的武功是什麼？<A>獨孤九劍
<Q>段譽在哪裡練武？<A>大理
<Q>什麼武功可以剋制玄冥神掌？<A>九陽神功
```

這種「生成多個 QA」行為反映了訓練資料的結構：模型不是在回答單一問題，而是在復現訓練資料中看到的連續 Q&A 序列模式。

### GPT-3 / InstructGPT 的推廣：預訓練 → SFT → RLHF

mini-llm 的兩階段流程可以看作是更大規模訓練管道的簡化版本。OpenAI 的 GPT-3 → InstructGPT → ChatGPT 遵循相似的邏輯，但加入了第三階段：

| 階段 | mini-llm | GPT-3 / InstructGPT |
|------|------|---------------------|
| 1. 預訓練 | `pretrain.py`, 500 步, 通用語料 | GPT-3 預訓練, 數萬億 token, 網路爬蟲 + 書籍 |
| 2. 監督微調 | `finetune.py`, 300 步, Q&A 資料 | SFT（Supervised Fine-Tuning）, 人類編寫的指令 + 回覆 |
| 3. 偏好最佳化 | 無 | RLHF（Reinforcement Learning from Human Feedback） |

**InstructGPT 的 RLHF 階段**在 SFT 之後進行：

1. **收集比較資料**：人類標註員對 SFT 模型的多個輸出進行排序
2. **訓練獎勵模型**：訓練一個模型來預測人類偏好分數
3. **強化學習優化**：使用 PPO（Proximal Policy Optimization）演算法，讓語言模型最大化獎勵模型的評分，同時用 KL 散度懲罰約束權重不要偏離 SFT 模型太遠

mini-llm 雖然沒有實現 RLHF 階段，但核心概念一致 — 先用大量資料學習語言，再用少量任務資料調整行為。從 mini-llm 到 InstructGPT，差異只是規模和階段數量的不同。

### 多任務微調概念

mini-llm 的微調僅覆蓋單一任務（武俠問答），但現代 LLM 的微調通常涵蓋數百到數千個任務。多任務微調使用統一的格式讓模型學習多種行為：

```
# mini-llm — 單一任務微調
<Q>令狐沖的武功是什麼？<A>獨孤九劍

# 現代 LLM — 多任務微調（同一模型學習多種行為）
<翻譯>蘋果<英文>apple
<摘要>台積電昨天股價上漲3%...<摘要完>台積電股價上漲
<分類>這家餐廳的服務很差<情感>負面
<QA>什麼是梯度下降？<A>一種最佳化演算法
```

多任務微調的優勢：

- **共享表示**：模型學會區分不同任務的格式標記，並在底層共用語言理解能力。翻譯任務學到的跨語言知識可以幫助問答任務。
- **泛化到新任務**：如果模型見過足夠多的任務格式，它可以對未見過的任務格式進行類比推廣。例如，如果訓練資料中包含 `<QA>` 和 `<翻譯>`，模型可能對一個新標記 `<摘要>` 也能做出合理回應。
- **低資源任務的遷移增益**：資料量少的任務可以從資料量豐富的任務中獲得表示學習的幫助。

T5（Text-to-Text Transfer Transformer）是這種範式的代表，將所有 NLP 任務統一為「文字到文字」的格式，使用任務前綴區分不同任務。mini-llm 的程式碼架構可以輕鬆擴展支援多任務微調 — 只需在 `finetune_data.pt` 中包含更多樣化的格式即可。

## 延伸閱讀

- 預訓練 + 微調的奠基工作: Dai & Le, "Semi-supervised Sequence Learning" (NeurIPS 2015)
- GPT 的生成式預訓練: Radford et al., "Improving Language Understanding by Generative Pre-Training" (2018)
- BERT 的雙向預訓練: Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding" (NAACL 2019)
- ULMFiT 的遷移學習框架: Howard & Ruder, "Universal Language Model Fine-tuning for Text Classification" (ACL 2018)
- 災難性遺忘: McCloskey & Cohen, "Catastrophic Interference in Connectionist Networks" (1989)
- 指令微調: Chung et al., "Scaling Instruction-Finetuned Language Models" (JMLR 2024)
