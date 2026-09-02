# Weight Tying — 權重共享

## 概述

**Weight Tying（權重共享）** 是一種模型壓縮技術，在 Transformer 語言模型中將 **Token 嵌入層（token embedding）** 與 **輸出投影層（output projection layer）** 的權重設為共享。這兩個層在本質上處理相同的詞彙空間：嵌入層將離散 token ID 映射到連續向量空間，輸出層將隱藏狀態映射回詞彙表上的機率分布。mini-llm 專案的所有模型版本都使用了權重共享。

## 直觀理解

在一個語言模型中：
- **嵌入層（我們在哪裡開始）**：`Embedding: vocab_size → d_model`，每個 token 有一個向量表示
- **輸出層（我們要去哪裡）**：`Linear: d_model → vocab_size`，將隱藏狀態投影回詞彙表

這兩個層的權重形狀分別為 `(vocab_size, d_model)` 和 `(d_model, vocab_size)`，它們是彼此的轉置關係（形狀互為轉置，但沒有內容上的對應關係）。

權重共享的核心洞察是：**「大」的語義與「大」的輸出機率計算應該是相關的**。如果某個 token 在嵌入空間中與其他 token 有特定關係，那麼在預測時也應該反映這種關係。因此讓這兩個層共用同一組參數是合理的。

## 數學形式

### 標準語言模型（無權重共享）

```
給定序列 [x₁, x₂, ..., xₜ]

hₜ = Transformer(h₁, ..., h_{t-1})     ← 隱藏狀態
logitsₜ = W_out · hₜ + b                ← 輸出投影 (W_out ∈ ℝ^V×d)
P(x_{t+1} | x₁...xₜ) = softmax(logitsₜ)
```

其中 `V = vocab_size`，`d = d_model`。

### 權重共享後

```
Embedding:    W_emb ∈ ℝ^{V×d}          ← 可學習的嵌入矩陣
Output:       W_out = W_embᵀ            ← 輸出投影使用嵌入矩陣的轉置

logitsₜ = W_embᵀ · hₜ                  ← 沒有偏置項 b
P(x_{t+1} | x₁...xₜ) = softmax(logitsₜ)
```

關鍵差異：
1. `W_out` 不需要獨立儲存 — 由 `W_embᵀ` 提供
2. 輸出層的偏置項 `b` 通常被移除（因為權重共享後加上偏置會破壞共享的對稱性）
3. 梯度更新時需要特殊處理（見下文）

### mini-llm 的實作

```python
self.tok_emb = nn.Embedding(vocab_size, d_model)
self.output = nn.Linear(d_model, vocab_size, bias=False)

# 權重共享 (Tie weights)
self.tok_emb.weight = self.output.weight
```

這裡的關鍵行 `self.tok_emb.weight = self.output.weight` 將兩個 `nn.Parameter` 設為**同一個張量物件**。PyTorch 中 `nn.Linear` 的權重形狀為 `(out_features, in_features)`，而 `nn.Embedding` 的權重形狀為 `(num_embeddings, embedding_dim)`。在這兩者之間，`output.weight.shape = (vocab_size, d_model)` 與 `tok_emb.weight.shape = (vocab_size, d_model)` 完全一致，因此可以直接共享。

### 具體的張量形狀演練 — mini-llm 實例

以 mini-llm 的 v2/v3 模型為例（`vocab_size ≈ 100`，`d_model = 128`）：

未共享時的張量：
```
tok_emb.weight:  torch.Size([100, 128])    ← nn.Embedding(vocab_size, d_model)
output.weight:   torch.Size([100, 128])    ← nn.Linear(d_model, vocab_size, bias=False)
```
兩者都是 `(100, 128)`，因此可以直接賦值共享。

共享後只有一個 `Parameter` 物件：
```python
shared_weight = output.weight               # shape (100, 128), 12800 個參數
tok_emb.weight = shared_weight              # 指向同一個張量
```

前向傳播中：
```python
x = self.tok_emb(input_ids)            # (B, T) → (B, T, 128)
# ... transformer layers ...
logits = self.output(h)                # (B, T, 128) → (B, T, 100)
# 等價於 logits = h @ W_shared.T
```

雖然 `self.output` 執行 `h @ W.T` 的線性變換，`self.tok_emb` 執行 lookup 操作，但兩者使用的權重張量是同一個。

### 嵌入層的雙重視角

`nn.Embedding(V, d)` 的權重 `W_emb` 大小為 `(V, d)`，它可以被視為兩種不同的運算：

- **查詢表視角**：`x = one_hot(token_ids) @ W_emb` — 根據 token ID 選取對應行
- **線性層視角**：`logits = h @ W_out.T` — 將隱藏狀態投影到詞彙空間

當 `W_out = W_emb` 時，兩者構成一個編碼-解碼對：嵌入將離散的 one-hot 向量編碼到 d 維連續空間，輸出將隱藏狀態解碼回 V 維詞彙空間。權重共享強制編碼與解碼使用相同的參數，確保了兩個映射方向的一致性。

### 「無偏置項」的設計哲學

`nn.Linear(d_model, vocab_size, bias=False)` 中的 `bias=False` 是權重共享能夠正確工作的前提。如果輸出層有偏置 `b ∈ ℝ^V`：

```
logits = W_embᵀ · h + b
```

偏置項會為每個詞彙添加一個與輸入無關的偏移量，破壞共享的對稱性，因為 `nn.Embedding` 沒有對應的偏置項可供共享。

移除偏置對模型表達能力的影響很小：
1. Transformer 的殘差連接和 LayerNorm 已提供平移不變性
2. `W_embᵀ · h` 雙線性形式本身具有足夠的表達力
3. Softmax 的平移不變性（`softmax(x + c) = softmax(x)`）抵消了部分偏置效應

即使不共享權重，許多現代語言模型也在輸出層使用 `bias=False`，因為移除偏置幾乎不影響 perplexity。

## 為什麼需要權重共享？

### 1. 減少參數量

假設 `vocab_size = 32000`，`d_model = 4096`：
- 無共享：`32000 × 4096 × 2 = 262M` 參數（嵌入 + 輸出層）
- 有共享：`32000 × 4096 = 131M` 參數

這 131M 參數的減少在小型語言模型中佔比可觀。mini-llm 中 `vocab_size ≈ 100`，`d_model = 128`：
- 無共享：`100 × 128 × 2 = 25600`
- 有共享：`100 × 128 = 12800`
雖然絕對值不大，但在 0.8M 總參數的模型中佔了約 3%。

### 2. 強制語義一致性

權重共享隱含了**對偶性假設**：一個 token 作為輸入時嵌入到隱藏空間的方式，應該與預測它時從隱藏空間投影到輸出空間的方式一致。

這在理論上可以理解為：語言模型在學習一個雙線性形式 `x(t) · y(t')` 來表示 token `t` 和 `t'` 之間的關係（點積），而權重共享確保了這個雙線性形式的對稱性。

### 3. 訓練更有效率

梯度更新時，共享權重會同時接收到來自嵌入層和輸出層的梯度，這可以被視為一種自然的正則化 — 兩者的梯度會相互影響，形成更穩定的更新方向。

### 4. 詞彙量大小對權重共享決策的影響

權重共享的收益與 `vocab_size / d_model` 的比例密切相關：

- **小型詞表（vocab_size < d_model）**：嵌入層的參數量少於單個 transformer block，權重共享的參數節省不明顯。此時是否共享更多是架構設計選擇而非參數壓縮需求。

- **中型詞表（d_model < vocab_size < 10 × d_model）**：這是權重共享最有效的區間。參數節省顯著，且語義一致性假設通常成立。mini-llm 的 `vocab_size ≈ 100`、`d_model = 128` 即屬於此類。

- **大型詞表（vocab_size > 10 × d_model）**：嵌入層和輸出層佔總參數的主導地位（如 LLaMA 65B 中嵌入層佔約 16% 參數），權重共享帶來巨大的參數節省。但當詞表極大時，輸出層的 softmax 計算本身已成為瓶頸，此時可能需要搭配 Adaptive Softmax 或分詞層次優化。

## 反向傳播的特殊性

權重共享在反向傳播時需要特別注意：當兩個層共用同一組參數時，梯度會從兩個路徑同時到達。

### 梯度累加

在 PyTorch 中，當兩個不同的操作共享同一個 `nn.Parameter` 物件時，反向傳播會自動累加兩個路徑的梯度：

```
∂L/∂W_shared = ∂L_emb/∂W_emb + ∂L_out/∂W_out
```

其中 `W_emb` 和 `W_out` 實際上是同一個張量。

這意味著 gradient update 時：

```
W_shared ← W_shared - η · (∂L_emb/∂W_shared + ∂L_out/∂W_shared)
```

這個累加是自動發生的（PyTorch 的 autograd 會正確處理），開發者不需要編寫額外程式碼。

### 潛在問題

梯度累加意味著共享權重的**有效學習率**是單獨時的兩倍。這在實務上很少造成問題，因為嵌入層和輸出層的梯度通常在不同的尺度和方向上，但極少數情況下可能需要針對性地調整學習率排程。

### 梯度累積的代碼示例

以下代碼展示權重共享下梯度如何從兩個路徑自動累加：

```python
V, d = 100, 128
model = nn.ModuleDict({
    'tok_emb': nn.Embedding(V, d),
    'output':  nn.Linear(d, V, bias=False),
})
model.tok_emb.weight = model.output.weight  # 共享

x = torch.randint(0, V, (2, 8))
h = model.tok_emb(x).mean(dim=1)
logits = model.output(h)
loss = logits.sum()
loss.backward()

print(model.output.weight.grad.shape)               # torch.Size([100, 128])
print(model.output.weight.grad is model.tok_emb.weight.grad)  # True
```

在 `backward()` 過程中，autograd 將 `tok_emb.weight` 和 `output.weight` 的梯度累加到同一個 `.grad` 上，因為它們指向同一記憶體位址。

優化器遍歷 `model.parameters()` 時，雖然會遇到 `tok_emb.weight` 和 `output.weight` 兩次，但它們是同一 Python 物件，因此優化器只執行一次更新：

```python
assert id(model.tok_emb.weight) == id(model.output.weight)  # 共享驗證
```

## 歷史背景

### Press & Wolf (2017)

權重共享首次在語言模型中被系統性研究來自 Press 與 Wolf 的論文「Using the Output Embedding to Improve Language Models」。他們在 RNN 語言模型中發現：

- 小型詞表（< 10000）下，權重共享帶來的參數節省效果不明顯，但訓練穩定性提升
- 大型詞表（> 50000）下，參數量節省非常可觀

### Inan et al. (2017)

幾乎同時，Inan 等人提出了「Tying Word Vectors and Word Classifiers: A Loss Framework for Language Modeling」，從理論角度論證了權重共享的有效性，並將其推廣到更廣泛的架構中。

### 現代應用

權重共享已成為語言模型的事實標準：
- **GPT-2**、**BERT**、**RoBERTa** 使用權重共享
- **LLaMA** 使用權重共享
- **T5** 的編碼器與解碼器共享嵌入權重
- **Transformer-XL** 使用權重共享

## 何時不應該使用權重共享？

雖然權重共享在多數情況下有益，但也有例外：

### 1. 不對稱的嵌入與輸出空間

當嵌入空間和輸出空間的語義不同時（如在編碼器-解碼器架構中嵌入使用共享子詞詞表的同時，解碼器輸出的是不同語言的詞彙），權重共享可能不合適。

### 2. 非常大的模型

對於巨型模型，嵌入和輸出層的參數佔比可能已經很小，權重共享帶來的壓縮效果有限，此時取消共享可以讓模型有更多靈活性。

### 3. Adaptive Softmax

當使用 Adaptive Softmax（一種對稀有詞使用較小嵌入維度的技術）時，權重共享不再直接適用，因為嵌入維度不統一。

### 4. 多語言模型

多語言模型中詞彙表通常包含多種語言的子詞單元。嵌入空間需要為每個子詞學習跨語言的對齊表示，但輸出層可能需要對特定語言進行校準。權重共享限制了這種靈活性——如果某個日語 token 的嵌入被更新以更好地編碼日語上下文，但輸出層希望將它投影到一個不同的機率空間，共享就會造成衝突。實務上，多語言 BERT 使用了權重共享且效果良好，但當語言間差異極大時（如中英混合詞表），解除共享有時能提升性能。

### 5. 基於適配器（Adapter）的微調

在參數高效微調（PEFT）場景中，LoRA 和 Adapter 等方法通常不對嵌入層或輸出層添加低秩適配器。如果使用權重共享，微調時無法獨立調整輸出層的行為。部分研究建議在微調階段解除權重共享，讓輸出層有更多自由適應下游任務的標籤空間，尤其是在分類任務中輸出空間與預訓練的詞彙空間差異較大時。

## 分散式訓練中的權重共享

權重共享在分散式訓練中帶來特殊的實作考量。

### FSDP（Fully Sharded Data Parallel）

FSDP 將模型參數分片到不同設備上。權重共享的參數需要被視為**單一參數**而非兩個獨立參數。PyTorch FSDP 在包裝前應確保參數已共享，否則 `nn.Embedding` 和 `nn.Linear` 可能被視為兩個獨立參數而分別分片。解決方案是在 FSDP 包裝前執行共享賦值，並使用 `sync_module_states=True` 正確廣播共享參數。如果使用 `torch.compile`，需要確保編譯後的圖中共享關係仍被維護。

### 張量並行（Tensor Parallelism）

在張量並行中，嵌入層沿詞彙維度（第 0 維）分割，輸出層沿模型維度（第 1 維）分割，兩者分片方式不同，使權重共享難以直接實作。常用解決方案：

1. **放棄共享**：在張量並行場景中解除權重共享，每個 GPU 持有完整的嵌入和輸出層。
2. **雙重分片**：嵌入層和輸出層都按詞彙維度分割，透過 all-reduce 聚合 logits。
3. **嵌入並行**：將嵌入層的 lookup 與 all-to-all 通訊結合，實作分散式查詢。

### 流水線並行（Pipeline Parallelism）

若嵌入層和輸出層位於流水線的不同設備上，共享參數需要跨設備拷貝。通常將嵌入層和輸出層放置在同一設備上以避免跨設備共享，或使用 `torch.distributed` 的廣播操作同步參數。

## 與 ALBERT 跨層參數共享的比較

ALBERT 提出了另一種參數共享策略：**跨層共享 Transformer 區塊的權重**。這與 Weight Tying 是不同層次的壓縮技術，但常被混淆。

| 面向 | Weight Tying | ALBERT 跨層共享 |
|------|-------------|-----------------|
| 共享對象 | 嵌入層 ↔ 輸出層 | 所有 Transformer 層之間 |
| 參數節省 | 1 × V × d | (L-1) × block_params |
| 對計算的影響 | 無 | 減少內存使用，計算量不變 |
| 對表達力的影響 | 很小（理論上有益） | 較大（需更大模型補償） |
| 實現複雜度 | 一行程式碼 | 需修改模型建構邏輯 |

ALBERT 的跨層共享基於一個假設：Transformer 各層學到的表示在某種程度上是相似的。實驗表明跨層共享對模型性能的影響比 Weight Tying 更顯著——通常需要更大的 hidden size 來補償表達力損失。

相比之下，Weight Tying 幾乎是「免費的午餐」：參數節省顯著且幾乎不影響困惑度。這也是為什麼 Weight Tying 比跨層共享更廣泛地被採用。兩種共享可以同時使用（如 ALBERT 同時使用了跨層共享和 Weight Tying）。

## 權重共享與模型量化

在模型量化（quantization）的背景下，權重共享的優勢被進一步放大。

### 參數節省的複合效應

量化將權重從浮點數壓縮為低位元整數。由於嵌入層和輸出層共享同一組參數，量化的參數節省也反映在同一組參數上：

```
未共享 FP16：2 × V × d × 2 = 4 × V × d 位元組
共享 FP16：  1 × V × d × 2 = 2 × V × d 位元組
共享 INT4：  1 × V × d × 0.5 = 0.5 × V × d 位元組
```

對於 `vocab_size = 32000`、`d_model = 4096` 的模型：
- FP16 未共享：1024 MB（嵌入 + 輸出）
- FP16 共享：512 MB
- INT4 共享：64 MB

共享與量化的複合效應使嵌入層的記憶體佔用從 1GB 降至 64MB，降幅達 16 倍。

### 量化感知訓練（QAT）中的考量

在量化感知訓練中，共享權重的偽量化（fake quantization）節點只會被插入一次，但兩個路徑的量化誤差都流入同一個權重。這意味著權重需要同時對嵌入查詢和輸出投影的量化誤差保持穩健。實務上這不構成問題，因為兩個操作的量化敏感度相似，且共享參數接收到的雙重梯度有助於量化尺度因子的穩定學習。

## 與其他參數共享的比較

| 方法 | 共享對象 | 參數節省 | 常見應用 |
|------|----------|----------|----------|
| Weight Tying | Embedding ↔ Output | 1 × V × d | 語言模型 |
| 跨層權重共享 | 多個 Transformer Block | (L-1) × block_params | ALBERT, Universal Transformer |
| 深度方向可分卷積 | 卷積核 | kernel_size × in_ch | 高效 CNN |
| 點積注意力 | Q/K/V 投影 | 取決於設計 | 部分輕量 Transformer |

權重共享是最簡單、最常見的參數共享形式，因為它只需一行程式碼即可實現且幾乎沒有負面影響。

## 延伸閱讀

- 原始論文: Press & Wolf, "Using the Output Embedding to Improve Language Models" (EACL 2017)
- 理論框架: Inan et al., "Tying Word Vectors and Word Classifiers: A Loss Framework for Language Modeling" (ICLR 2017)
- ALBERT 的跨層共享: Lan et al., "ALBERT: A Lite BERT for Self-supervised Learning of Language Representations" (ICLR 2020)
- Adaptive Softmax: Grave et al., "Efficient Softmax Approximation for GPUs" (ICML 2017)
- 多語言 BERT 的權重共享分析: Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding" (NAACL 2019)
- FSDP 實作: Zhao et al., "PyTorch FSDP: Experiences on Scaling Fully Sharded Data Parallel" (VLDB 2023)
- 量化中的權重共享: Dettmers et al., "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale" (NeurIPS 2022)
