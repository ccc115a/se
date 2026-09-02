# mini-llm — AGENTS.md

Toy LLM pretrain+finetune+distill in pure PyTorch. Three independent stages, each self-contained (run from within its directory).

## Structure

| Directory | What it does |
|-----------|-------------|
| `v1-pretrain/` | Single-stage char LM, monolithic in `mini-llm.py` |
| `v2-finetune/` | Data gen → pretrain → finetune |
| `v3-distill/` | Same as v2 but data via NVIDIA API distillation |
| `_wiki/` | 15 technical reference docs |
| `_doc/` | Provenance links (AI Studio prompt) |

## Commands (run from the subdirectory)

v1: `python mini-llm.py --file input.txt` [--iters N --seq_len N --batch_size N --gen_len N]

v2: `./run.sh` — edit run.sh to swap data generator, then runs pretrain.py → finetune.py

v3: same as v2, but `gen_data_distill.py` needs `NVIDIA_API_KEY` env var

## Workflow

- Order: data gen → `pretrain.py` → `finetune.py` (within each stage)
- `finetune.py` loads `pretrain.pt` weights
- Data generators are mutually exclusive: v2 has `gen_data_wuxia.py`, `gen_data_rule.py`, `gen_data_robot.py`; v3 has only `gen_data_distill.py`. All write `pretrain.txt`, `finetune.txt`
- Character-level tokenizer: `vocab.json` = `{stoi, itos, vocab_size}`, built by `pretrain.py` from `pretrain.txt`
- `vocab.json` (built by `pretrain.py` from `.txt`), `*.pt`, `*.txt` are all gitignored

## Model

Architecture: RoPE, RMSNorm, SwiGLU FFN, weight tying. All training loops use gradient clipping (norm=1.0).

| Param | v1 | v2/v3 |
|-------|-----|-------|
| d_model | 128 | 128 |
| n_heads | 4 | 4 |
| n_layers | 3 | 4 |
| seq_len | 32 | 64 |
| pretrain steps | 2000 | 500 |
| finetune steps | — | 300 |
| batch_size | 16 | 32 |
| lr (pretrain) | 3e-4 | 5e-4 |
| lr (finetune) | — | 1e-4 |

Runs on CPU by default (falls back from CUDA).

## Dependencies

Only `torch` required. `gen_data_distill.py` additionally needs `openai` (v1+ API).

No requirements.txt, no pyproject.toml — `pip install torch` (and `pip install openai` for v3-distill).

## Notes

- v2/v3 share identical `model.py`, `pretrain.py`, `finetune.py` across both dirs
- v1 is standalone (model+training in one file, 3 layers vs 4 in v2/v3)
- No test/lint/type infrastructure exists
