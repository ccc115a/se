# mini-llm Wiki

本 wiki 說明 `mini-llm` 專案中使用的技術概念與專有名詞。每個詞項獨立成頁，涵蓋原理說明、數學基礎、實作細節（對應專案程式碼），以及延伸閱讀方向。

## 目錄

| 詞項 | 說明 |
|------|------|
| [Autoregressive Language Model](autoregressive-language-model.md) | 自迴歸語言模型的基本原理 — 逐 token 預測的生成方式與機率分解 |
| [RMSNorm](rmsnorm.md) | Root Mean Square Layer Normalization — 替代 LayerNorm 的輕量正規化層 |
| [Rotary Position Embedding (RoPE)](rotary-position-embedding.md) | 旋轉位置編碼 — 以旋轉矩陣將位置資訊注入注意力計算 |
| [SwiGLU](swiglu.md) | Swish-Gated Linear Unit — 基於門控機制的活化函數 |
| [Weight Tying](weight-tying.md) | 權重共享 — 嵌入層與輸出層共享參數以減少模型大小 |
| [Causal Self-Attention](causal-self-attention.md) | 因果自注意力 — 帶三角遮罩的解碼器注意力機制 |
| [Character-Level Tokenizer](character-level-tokenizer.md) | 字元級分詞器 — 以單一字元為基本單位的最簡 Tokenizer |
| [Pretraining + Fine-tuning](pretraining-finetuning.md) | 預訓練與微調 — 兩階段訓練範式 |
| [Knowledge Distillation](knowledge-distillation.md) | 知識蒸餾 — 用大模型產生訓練資料教小模型 |
| [Cross-Entropy Loss](cross-entropy-loss.md) | 交叉熵損失函數 — 語言模型的標準訓練目標 |
| [AdamW Optimizer](adamw-optimizer.md) | AdamW 最佳化器 — 結合 Adam 與解耦權重衰減 |
| [Gradient Clipping](gradient-clipping.md) | 梯度裁切 — 防止梯度爆炸的訓練穩定技術 |
| [Synthetic Data Augmentation](synthetic-data-augmentation.md) | 合成資料擴增 — 以規則或大模型產生訓練資料 |
| [Gradient Descent](gradient-descent.md) | 梯度下降 — 深度學習的最佳化核心原理 |

## 參照

本 wiki 的說明對應 `mini-llm` 專案的實作位置：

- **v1-pretrain/mini-llm.py** — 單階段字元級語言模型（完整實作）
- **v2-finetune/model.py** — 多層 Transformer 模型定義（v2/v3 共用）
- **v2-finetune/pretrain.py** — 預訓練腳本
- **v2-finetune/finetune.py** — 微調腳本
- **v2-finetune/gen_data_\*.py** — 合成資料生成器
- **v3-distill/gen_data_distill.py** — 知識蒸餾資料生成器
