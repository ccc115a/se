# 記憶功能說明

這次更新在原本的 `agent.py` 上加了三層長期記憶，新增了 `memory_manager.py`。
兩個檔案要放在同一個資料夾。

## 前置需求

除了原本跑 agent 需要的 chat 模型外，RAG 需要一個 embedding 模型：

```bash
ollama pull nomic-embed-text
```

（若想換別的 embedding 模型，改 `memory_manager.py` 裡的 `EMBED_MODEL` 即可。）

Ollama 若沒有裝好這個 embedding 模型，`recall_memory` / 自動檢索只會印出警告
後略過，不會讓程式壞掉，只是少了長期記憶的加值效果。

## 執行後會多出的資料夾

第一次跑 `agent.py` 時，會在**當下工作目錄**建立：

```
memory/
├── AGENT.md              # 長期記憶檔（純文字，可以自己編輯）
├── rag_store.sqlite3      # 每輪對話的向量記憶（自動累積）
└── skills/
    └── system_info/
        └── SKILL.md       # 範例技能，可依樣新增更多資料夾
```

## 三層記憶怎麼運作

1. **AGENT.md**（顯性、常駐）
   - 每次啟動整份讀進 system prompt。
   - 使用者說「記住 XXX」時，模型會呼叫 `remember_fact` 工具把一行寫進去；
     也可以在 REPL 直接打 `/remember XXX` 手動寫，或直接編輯這個檔案。

2. **skills/**（顯性、依需求注入）
   - 每個技能一個資料夾，`SKILL.md` 第一行寫
     `keywords: 關鍵字1, 關鍵字2, ...`，之後全部內容當作技能說明。
   - 每一輪對話會用關鍵字比對使用者輸入，命中的技能才會被塞進當回合的
     「背景資訊」，不會佔用其他無關對話的 context。
   - 新增技能：在 `memory/skills/` 底下建新資料夾＋`SKILL.md` 即可，
     REPL 裡打 `/skills` 可重新載入。

3. **RAG（向量記憶）**（隱性、自動）
   - 每一輪「使用者訊息」與「模型回覆」都會呼叫 embedding API 存進
     `rag_store.sqlite3`。
   - 下一次使用者發言前，會自動用語意相似度（cosine similarity）搜尋
     過去的記憶，相似度夠高（預設 0.55）的前幾筆（預設 4 筆）會附加成
     「背景資訊」一併送給模型，模型看得到但不會被要求逐字複述。
   - 模型也可以主動呼叫 `recall_memory` 工具做語意搜尋，適合「你記得我
     之前說過...嗎？」這類明確想回想的問題。

## REPL 新增指令

- `/memory`   — 顯示 AGENT.md 路徑、已載入技能、RAG 記憶筆數
- `/skills`   — 重新掃描並載入 `memory/skills/`
- `/remember <內容>` — 手動寫一筆進 AGENT.md
- `/clear`    — 清空「對話歷史」，但 AGENT.md 與 RAG 記憶都不會被清掉

## 可以再加強的地方（沒做，先列出來給你參考）

- 目前 RAG 檢索是把全部向量讀進記憶體算 cosine similarity，記憶量大了以後
  （幾萬筆以上）會變慢，屆時可以考慮換成 `sqlite-vec` 之類的向量索引擴充套件。
- `remember_fact` 目前只是單純 append，沒有去重複／整理，用久了 AGENT.md
  可能需要人工偶爾整理一下。
- skill 比對目前是純關鍵字，之後也可以比照 RAG 的方式改成用 embedding
  做語意比對，比較不會漏掉沒寫進 keywords 的說法。
