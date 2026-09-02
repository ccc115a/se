# mini-llm — 微型語言模型訓練流程

純 PyTorch 實作的玩具級語言模型，展示**預訓練（Pre-training）+ 微調（Fine-tuning）+ 知識蒸餾（Knowledge Distillation）**。全部程式碼可在 CPU 上執行，不依賴 HuggingFace Transformers、DeepSpeed 等框架。

## 三階段架構

| 目錄 | 說明 |
|------|------|
| `v1-pretrain/` | 單階段字元級語言模型，所有程式碼在 `mini-llm.py` 中 |
| `v2-finetune/` | 合成資料生成 → 預訓練 → 微調 |
| `v3-distill/` | 大模型知識蒸餾產生資料 → 預訓練 → 微調 |
| `_wiki/` | 15 篇技術文件（RoPE、RMSNorm、SwiGLU 等） |

### v1-pretrain：單階段字元級語言模型

讀取 `.txt` 檔案，直接訓練一個三層 Transformer 預測下一個字元：

```bash
cd v1-pretrain
python mini-llm.py --file input.txt
```

支援參數：`--iters`（預設 2000）、`--seq_len`（32）、`--batch_size`（16）、`--gen_len`（100）。

### v2-finetune：預訓練 + 微調

使用合成語料展示遷移學習。編輯 `run.sh` 切換資料生成器：

```bash
cd v2-finetune
./run.sh
```

`run.sh` 預設啟用 `gen_data_robot.py`，可改為 `gen_data_wuxia.py` 或 `gen_data_rule.py`。

### v3-distill：大模型知識蒸餾

透過 NVIDIA API 呼叫 Minimax M2.7 模型，生成太陽系行星相關的訓練資料，再訓練小模型：

```bash
cd v3-distill
export NVIDIA_API_KEY='你的金鑰'
./run.sh
```

需要 `pip install openai`（v1+ API）。

## 資料流程

```
gen_data_xxx.py          pretrain.py                    finetune.py
    │                        │                              │
    ├── pretrain.txt ────────┤                              │
    ├── finetune.txt ────────┼──────────────────────────────┤
    │                        │                              │
    │            建立 vocab.json（stoi, itos, vocab_size）  │
    │            建立 pretrain_data.pt                      │
    │            訓練 → pretrain.pt                        │
    │                                                       │
    │            載入 vocab.json                             │
    │            讀取 finetune.txt → finetune_data.pt       │
    │            載入 pretrain.pt → 微調 → finetune.pt     │
    │            自動測試（從 finetune.txt 取第一題）       │
```

產生過程：
1. `gen_data_xxx.py` 只產生 `pretrain.txt` 與 `finetune.txt`
2. `pretrain.py` 從 `.txt` 建立詞表 `vocab.json` 與預訓練張量 `pretrain_data.pt`，訓練後儲存 `pretrain.pt`
3. `finetune.py` 讀取 `vocab.json`、將 `finetune.txt` 編碼為 `finetune_data.pt`，載入 `pretrain.pt` 權重進行微調

## 資料生成器比較

| 腳本 | 領域 | 目標長度（pretrain/finetune） | 外部依賴 |
|------|------|-----------------------------|---------|
| `gen_data_wuxia.py` | 武俠人物知識 | 200K / 50K 字 | 無 |
| `gen_data_rule.py` | 數學與規律 | 200K / 50K 字 | 無 |
| `gen_data_robot.py` | 智慧家庭助理 | 200K / 50K 字 | 無 |
| `gen_data_distill.py` | 太陽系行星 | 100K / 30K 字 | NVIDIA API Key |

所有生成器使用**重複打亂拼接（Shuffle-and-Repeat）** 將少量種子句擴增至目標資料量。

## 模型架構

核心元件定義在 `model.py` 中的 `ModernLanguageModel`：

```
輸入 Token IDs
    ↓
Token Embedding (vocab_size → d_model)
    ↓
    TransformerBlock × N 層
    ├── RMSNorm → 因果自注意力（RoPE）
    ├── 殘差連接
    ├── RMSNorm → SwiGLU 前饋網路
    └── 殘差連接
    ↓
RMSNorm → 輸出投影 (d_model → vocab_size) ← 權重共享
    ↓
Softmax → 預測機率
```

| 組件 | 說明 |
|------|------|
| RoPE | 無參數旋轉位置編碼，將相對位置注入注意力 |
| RMSNorm | 根均方正規化，無需偏置項 |
| SwiGLU | `silu(w1(x)) * w3(x)` 門控活化 |
| Weight Tying | `tok_emb.weight = output.weight` 共享嵌入與輸出層 |

### 預設超參數

| 參數 | v1 | v2/v3 |
|------|-----|-------|
| d_model | 128 | 128 |
| n_heads | 4 | 4 |
| n_layers | 3 | 4 |
| seq_len | 32 | 64 |
| pretrain 步數 | 2000 | 500 |
| finetune 步數 | — | 300 |
| lr (pretrain) | 3e-4 | 5e-4 |
| lr (finetune) | — | 1e-4 |
| batch_size | 16 | 32 |

所有訓練迴圈使用梯度裁切（norm=1.0）。

## 執行環境

- Python 3.8+、PyTorch 2.0+（CPU 版本即可）
- v3-distill 另需 `openai` 套件
- 無 `requirements.txt`、無 `pyproject.toml`：

```bash
pip install torch
pip install openai   # 僅 v3-distill 需要
```

## 自動產生的檔案（皆已 .gitignore）

| 檔案 | 產生者 | 說明 |
|------|--------|------|
| `pretrain.txt` | gen_data_xxx.py | 預訓練語料純文字 |
| `finetune.txt` | gen_data_xxx.py | 微調語料純文字 |
| `vocab.json` | pretrain.py | 字元級詞表（stoi, itos, vocab_size） |
| `pretrain_data.pt` | pretrain.py | 預訓練張量 |
| `pretrain.pt` | pretrain.py | 預訓練權重 |
| `finetune_data.pt` | finetune.py | 微調張量 |
| `finetune.pt` | finetune.py | 微調權重 |
| `data/` | — | 歷史執行快取 |

## Wiki

[`_wiki/index.md`](_wiki/index.md) 包含 15 篇技術文件，涵蓋專案所有核心概念（自迴歸語言模型、RMSNorm、RoPE、SwiGLU、權重共享、因果遮罩、知識蒸餾等）。

---

**License**: MIT
