# Knowledge Distillation — 知識蒸餾

## 概述

**知識蒸餾（Knowledge Distillation）** 是一種模型壓縮與訓練技術，由 Hinton 等人在 2015 年的論文「Distilling the Knowledge in a Neural Network」中系統性提出。核心想法是讓一個小型模型（student）學習模仿大型模型（teacher）的行為，從而將大模型的「知識」濃縮到小模型中。mini-llm v3 使用知識蒸餾來產生訓練資料：呼叫 NVIDIA API（使用 Minimax 模型）生成關於太陽系行星的教育資料，再用這些資料訓練小模型。

## 動機：為什麼需要知識蒸餾？

### 大小模型的權衡

大型語言模型（如 GPT-4、Claude）能力強大，但：
- **計算成本極高** — 每次推論需要大量 GPU 資源
- **部署困難** — 需要數百 GB 的記憶體和高頻寬 GPU
- **回應延遲高** — 大模型的前向傳播需要更多時間

小模型（如 mini-llm 的 ~0.8M 參數）效率極高，但能力有限。

知識蒸餾提供一個橋樑：**用大模型的能力來提升小模型的訓練效果**，讓小模型在特定任務上表現接近大模型。

## 知識蒸餾的類型

### 1. Logit 蒸餾（Response-Based Distillation）

最經典的形式：學生模型學習模仿教師模型的輸出機率分布（softmax 後的 logits）。

```
Loss = α · CrossEntropy(student_logits, hard_target)
     + β · KL(student_logits/T || teacher_logits/T) · T²
```

其中：
- `hard_target` — 真實標籤（one-hot）
- `T` — 溫度參數（Temperature），控制 softmax 的平滑度
- `KL` — KL 散度，衡量兩個分布的差異
- `α, β` — 加權係數

**高溫的作用**：當 `T` 較高時，softmax 輸出更平滑，保留了更多「類別間相似性」資訊（例如，貓的圖片被誤判為狗的機率遠高於被誤判為汽車的機率）。這些相對關係是知識蒸餾的關鍵。

### 2. 特徵蒸餾（Feature-Based Distillation）

學生模型學習匹配教師模型的中間層特徵表示。這要求學生具有與教師相似的架構，或至少能透過投影層對齊。

### 3. 資料蒸餾（Data Distillation / On-Policy Distillation）

這是 mini-llm 使用的方式：**教師模型生成合成訓練資料**，然後學生模型在這個資料上訓練。

```
教師模型 → 生成大量 (輸入, 輸出) 對 → 學生模型在該資料上訓練
```

這種方法的優點：
- 不需要存取教師模型的內部狀態（logits 或中間層）
- 可以透過 API 呼叫（不需要模型開源）
- 資料可以篩選和清洗

## mini-llm 的資料蒸餾實作

### 流程

```
NVIDIA API (Minimax M2.7)         ← Teacher
    ↓ 回應 [FACT] 和 [QA] 格式文字
解析器提取知識條目與問答對
    ↓ 擴增（重複打亂拼接）
訓練資料（pretrain_data.pt, finetune_data.pt）
    ↓ 訓練
學生模型（~0.8M 參數）              ← Student
```

### Prompt 設計

資料蒸餾的關鍵是設計合適的 **Prompt** 來引導教師模型生成高品質的訓練資料：

```python
prompt = """
請扮演一個嚴格的資料生成器。我要訓練一個微型語言模型，
請幫我生成關於「太陽系八大行星」的訓練資料。
請使用極度簡單的繁體中文，並且嚴格遵守以下兩種格式：

格式1 (知識敘述): [FACT] 敘述句。
格式2 (問答訓練): [QA] <Q>問題？<A>答案

請生成 50 句 [FACT] 和 50 句對應的 [QA]。
"""
```

設計要點：
1. **角色設定** — 要求模型扮演「嚴格的資料生成器」，減少不必要的解釋
2. **語言限制** — 「極度簡單的繁體中文」避免生成超出小模型詞表範圍的字詞
3. **嚴格格式** — `[FACT]` 和 `[QA]` 前綴方便解析
4. **對應關係** — 要求 FACT 和 QA 相互對應，確保資料一致性

### 回應解析

```python
for line in teacher_response.split('\n'):
    line = line.strip()
    if line.startswith("[FACT]"):
        pretrain_facts.append(line.replace("[FACT]", "").strip()+"\n")
    elif line.startswith("[QA]"):
        finetune_qa.append(line.replace("[QA]", "").strip() + "\n")
```

解析邏輯非常簡單：根據行首前綴分類，去除前綴後將內容分別存入預訓練知識庫和微調問答庫。

### 資料擴增

由於教師模型只生成了 ~50 條 FACT 和 ~50 條 QA，對於神經網路訓練來說完全不夠（200K 字的目標）。mini-llm 採用**重複打亂拼接**的擴增策略：

```python
PRETRAIN_TARGET_LENGTH = 100000
pretrain_text = ""
while len(pretrain_text) < PRETRAIN_TARGET_LENGTH:
    pretrain_text += "".join(random.sample(pretrain_facts, len(pretrain_facts)))
```

這種方法的假設是：透過隨機重排列順序，模型可以從不同角度反覆學習同樣的事實，最終掌握這些知識。

## 蒸餾框架的 API 呼叫

mini-llm 使用 OpenAI-compatible API（NVIDIA API）進行蒸餾：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

completion = client.chat.completions.create(
    model="minimaxai/minimax-m2.7",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    top_p=0.95,
    max_tokens=8192,
    stream=True
)
```

要點：
- **環境變數** — API key 從 `NVIDIA_API_KEY` 環境變數讀取
- **串流模式** — 使用 `stream=True` 即時顯示教師模型的輸出行為
- **溫度控制** — `temperature=0.7` 在創造性和一致性之間取得平衡

## Self-Distillation（自蒸餾）

一個有趣的變體是**自蒸餾**：將同一個模型在訓練過程中不同階段的檢查點分別作為教師和學生。這在沒有更大模型可用時也是一種有效的正則化方法。mini-llm 沒有使用自蒸餾，但理解這個概念有助於拓展對蒸餾的認識。

## On-Policy Distillation（在線蒸餾）

另一種進階方法是**在線蒸餾**：學生模型生成輸出，教師模型對輸出進行評分或修正，然後學生在修正後的輸出上學習。這與 Reinforcement Learning from Human Feedback (RLHF) 有相似之處。

mini-llm 使用的資料蒸餾屬於**離線蒸餾（Offline Distillation）** — 預先從教師收集靜態資料集，然後學生在該資料集上訓練。

## 資料蒸餾 vs Logit 蒸餾

| 層面 | 資料蒸餾 (mini-llm 使用) | Logit 蒸餾 |
|------|----------------------|------------|
| 教師存取層級 | 僅輸出文字 | logits 分數 |
| 教師可開源性 | 不需要（可透過 API） | 需要 |
| 訓練計算量 | 標準監督訓練 | 需要同時 forward 兩個模型 |
| 知識粒度 | 回答內容 | 回答內容 + 置信度分布 |
| 資料多樣性 | 高（可生成各種輸入） | 受限於現有資料集 |

## 為什麼蒸餾對小模型有效？

知識蒸餾的有效性可以從正則化的角度理解：

1. **軟標籤提供更多資訊** — softmax 輸出中，除了正確答案外，其他類別的相對大小也包含了「學科知識」（例如模型知道「水星」和「金星」的相似性高於「水星」和「屠龍刀」）

2. **資料多樣性** — 教師模型可以從任意 Prompt 生成資料，創造出比人工標註更多樣的訓練樣本

3. **對齊教師的思考方式** — 學生不僅學習答案，還學習教師回答問題的模式和風格

在 mini-llm 的場景中，蒸餾的核心價值是：讓 0.8M 參數的小模型能夠回答關於太陽系行星的結構化問題，而這些知識是透過規則生成（如 v2 中數學規則）難以人工設計的。

## 具體案例：教師生成 vs 學生學到的內容

教師（Minimax）的原始輸出：

```
[FACT] 水星是太陽系中最小的行星。
[FACT] 金星是太陽系中最熱的行星。
[FACT] 地球是太陽系中唯一有生命的行星。
[QA] <Q>太陽系最小的行星是什麼？<A>水星
[QA] <Q>哪顆行星溫度最高？<A>金星
[QA] <Q>哪顆行星有生命？<A>地球
```

學生（mini-llm ~0.8M）訓練後，被問「太陽系最小的行星是什麼？」能輸出「水星」，微調後甚至能生成「太陽系最小的行星是水星。」但學生表現並非完美：事實混淆偶有發生（attribute‑object 配對錯誤）、字詞超出詞表時輸出亂碼、難以進行跨條目推理（如「水星最小且離太陽最近」）。蒸餾的核心價值是：教師用 API 一次呼叫產出事實，學生將這些事實內化為參數權重，後續推論無需再呼叫外部 API。

## API 成本分析

每次 `gen_data_distill.py` 執行消耗約 350 中文字（Prompt）+ 15,000–20,000 字元（輸出），換算約 200 input tokens + 8,000 output tokens。以 NVIDIA Minimax 定價（~$0.2/M input, $0.6/M output）計算：

- Input: 200 / 1M × $0.2 = $0.00004
- Output: 8,000 / 1M × $0.6 = $0.0048
- **每次蒸餾總成本約 $0.005（0.15 台幣）**

若需更多資料，多次呼叫即可，成本與資料量呈線性關係。與每次查詢教師都要花費 token 相比，蒸餾後小模型的**邊際推論成本為零**。

## 溫度參數的數學機制

溫度 `T` 控制 softmax 平滑度：`softmax(xᵢ, T) = exp(xᵢ/T) / Σⱼ exp(xⱼ/T)`。

假設 logits = `[3.0, 1.0, 0.1, -1.0]`（A 為正確答案），不同 T 的 softmax 輸出：

| 類別 | Logit | T=0.5 | T=1.0 | T=2.0 | T=5.0 |
|------|-------|-------|-------|-------|-------|
| A | 3.0 | **0.881** | **0.836** | **0.674** | **0.420** |
| B | 1.0 | 0.117 | 0.114 | 0.175 | 0.215 |
| C | 0.1 | 0.002 | 0.046 | 0.097 | 0.183 |
| D | -1.0 | 0.000 | 0.004 | 0.054 | 0.182 |

T→0 趨近 one-hot（資訊全失），T=1 為標準分布，T>1 使錯誤類別保留相對意義（例如 T=2 時 B=0.175 明顯高於 D=0.054，暗示「B 比 D 更像合理的錯誤答案」），T→∞ 則所有機率均等。mini-llm 使用 `temperature=0.7` 控制教師輸出文字的多樣性（非 logit 蒸餾的溫度），是格式一致性與措辭多樣性的折衷。

## 串流回應處理機制

`gen_data_distill.py` 用 `stream=True` 以 SSE（Server‑Sent Events）接收教師輸出：

```python
teacher_response = ""
for chunk in completion:
    if not getattr(chunk, "choices", None):
        continue
    if chunk.choices[0].delta.content is not None:
        content = chunk.choices[0].delta.content
        print(content, end="")
        teacher_response += content
```

`completion` 是 `Stream` 迭代器，每個 chunk 是 SSE 事件。部分 chunk（如結束訊號）無 `choices` 需跳過；`delta.content` 是增量 token，逐字拼接到 `teacher_response`。`print(content, end="")` 讓使用者在終端機即時看到教師生成過程。SSE 是單向 HTTP 長連線，適合 LLM 串流場景。

## 錯誤處理機制

`gen_data_distill.py` 涵蓋幾個關鍵錯誤場景：

1. **API 金鑰缺失** — `if not api_key: raise ValueError(...)` 在執行 API 呼叫前終止
2. **網路錯誤** — OpenAI SDK 底層使用 httpx，可能拋出 `APIConnectionError`、`RateLimitError`、`TimeoutException`。當前腳本未捕獲這些例外，錯誤會向上傳播導致腳本中止
3. **格式解析失敗** — `if len(pretrain_facts) == 0 or len(finetune_qa) == 0: raise ValueError(...)` 確保教師按格式輸出

如果格式檢查不存在且教師輸出為空：`random.sample()` 會拋 `ValueError`，`stoi` 空字典導致 `encode` 出錯。格式檢查實際是對下游的必要防禦。

## 為什麼 50 條 QA 足夠：資料擴增的數學

N 個條目的排列數為 N!。50! ≈ 3.04×10⁶⁴，遠超過目標 100,000 字元所需的 ~250 次拼接。每次 `random.sample(facts, len(facts))` 幾乎保證順序不重複。

每個 FACT 平均 20 字元，100,000 ÷ (50×20) ≈ 100 次重複。每次重複的上下文不同，讓模型：(1) 從不同鄰近文字學習同一事實 (2) 形成隱式隨機遮罩效果 (3) 建立條目間的潛在關聯。對 0.8M 參數的小模型，50 條獨特知識已能覆蓋其容量上限。

## 知識蒸餾 vs 資料擴增

| 層面 | 知識蒸餾 | 資料擴增 |
|------|---------|---------|
| 原始資料 | 從零生成 | 需要少量真實樣本 |
| 核心方法 | 大模型知識遷移 | 對已有資料變換 |
| 事實可靠性 | 依賴教師知識（可能含錯誤） | 不改變事實內容 |

mini-llm 混合使用兩者：蒸餾階段由教師生成 FACT/QA（純蒸餾），擴增階段打亂拼接（純擴增）。這是一個連續光譜，mini-llm 從一端走到另一端。重要區別：資料擴增不改變事實，而蒸餾若教師輸出錯誤（如「冥王星是行星」），錯誤會被內化到學生中。

## 離線 vs 在線蒸餾的權衡

mini-llm 採用**離線蒸餾**（Offline Distillation）：

| | 離線（mini-llm） | 在線 |
|--|------------|------|
| 優點 | 教師只呼叫一次 API；訓練快；資料可反覆檢查 | 可針對學生弱點即時補充樣本；可結合 RLHF |
| 缺點 | 資料分布固定；無法動態調整 | 每次迭代都需呼叫 API；成本線性增長；實作複雜 |

對玩具專案，離線是明確選擇：總成本 $0.005，靜態資料使實驗可重現。若採在線蒸餾（500+300 步，每 10 步呼叫教師一次），約 80 次 API 呼叫 = $0.40，成本高出 80 倍。

## 領域特化考量

| 面向 | 太陽系知識（v3 蒸餾） | 武俠知識（v2 規則生成） |
|------|-------------------|---------------------|
| 範圍 | 封閉（八大行星固定集合） | 開放（門派人物眾多） |
| 事實 | 結構化三元組 | 敘事性，不易拆解 |
| 詞表 | 低挑戰（基本中文字） | 高挑戰（專有名詞） |
| 蒸餾難度 | 低 | 高 |

太陽系是封閉領域，50 條 FACTS 即可覆蓋。武俠知識需要更多種子資料、更細緻的 Prompt 約束，且專有名詞會膨脹詞表。mini-llm v3 選擇太陽系作為蒸餾試驗場，正是因為容易量產高品質訓練資料。

## Prompt 工程在蒸餾中的角色

教師模型只會產生符合 Prompt 約束的輸出，因此 Prompt 設計直接決定蒸餾品質：

1. **角色設定** — 「請扮演一個嚴格的資料生成器」限制行為模式，避免教師插入解釋
2. **Few-shot 範例** — 兩組範例不僅展示格式，還暗示長度、提示 FACT/QA 對應關係
3. **語言限制** — 「極度簡單的繁體中文」確保詞表不膨脹（v3 約 1,800 字元），但犧牲了表述豐富性（如「微小」→「小」）
4. **格式強化** — 前綴標記 `[FACT]`/`[QA]`、負面約束「不要輸出廢話」、數量要求「生成 50 句」，多層機制確保結構化輸出

若教師輸出部分行不符合格式，該行被跳過，資料仍可用；若完全忽略格式，整批廢棄。

## 延伸閱讀

- 奠基論文: Hinton et al., "Distilling the Knowledge in a Neural Network" (NeurIPS 2015)
- 關於蒸餾的綜合調查: Gou et al., "Knowledge Distillation: A Survey" (IJCV 2021)
- TinyBERT: Jiao et al., "TinyBERT: Distilling BERT for Natural Language Understanding" (ICLR 2020)
- DistilBERT: Sanh et al., "DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter" (NeurIPS Workshop 2019)
- 資料蒸餾: Lopes et al., "Data-Free Knowledge Distillation for Deep Neural Networks" (2017)
- 自蒸餾: Zhang et al., "Be Your Own Teacher: Improve the Performance of Convolutional Neural Networks via Self Distillation" (ICCV 2019)
