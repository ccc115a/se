# docker-bot — MVP 規劃（v0.1）

> 來源：`_doc/chat.md` 對話結論。
> 目標：打造類似 Grok Bot / OpenClaw 的自主 Agent 原型，但第一版只做最小可用驗證。
> 約束：**零付費 API**，LLM 使用本地 `ollama qwen3.5:4b`；Agent 執行環境用 Docker 隔離。

## 1. MVP 一句話定義

Mac 本機跑 Ollama（大腦）+ Docker 跑一個 Python + Playwright 沙盒（手腳），
讓 4B 小模型透過 ReAct + Tool Calling 完成一個端到端瀏覽器任務：
**打開 Google → 搜尋 `NQU ERP` → 截圖存檔**。

呼應 Dropbox 案例的 MVP 思維：不先做完整雲端平台，先證明「本地小模型能指揮瀏覽器做事」。

## 2. 架構決策（已定案）

| 決策 | 選擇 | 理由 |
|---|---|---|
| Ollama 放哪 | **Mac 原生，不進 Docker** | Apple Silicon 上原生 Ollama 可直接用 Metal / Unified Memory；放 Docker（經 Linux VM 轉一層）會慢 10–20% 且易 OOM |
| Agent 放哪 | **Docker 容器 `agent-sandbox`** | 隔離 Playwright / Chromium 依賴，不污染本機；產出物經 volume 掛載回本機 |
| 容器間連線 | `OLLAMA_HOST=http://host.docker.internal:11434` + `extra_hosts: host-gateway` | 讓容器內 Python 能打到 Mac 本機 Ollama |
| 模型 | `qwen3.5:4b`（約 3.4GB） | 免費、本地、`ollama list` 已確認存在；擅長結構化 JSON / Tool Calling，不適合傳高解析截圖做視覺座標 |
| 瀏覽器模式 | `HEADLESS=true` + `--no-sandbox --disable-setuid-sandbox` | 容器內無 X11/GUI，headless 效能最佳；除錯時才切 `false` |
| 編排框架 | **不引入** LangGraph / AutoGen / CrewAI / Temporal | MVP 用 ~100 行手寫 ReAct loop 即可，避免重依賴 |

架構圖：

```text
macOS Host
├── Native Ollama (qwen3.5:4b, :11434, Metal 加速)
│         ▲ HTTP (host.docker.internal:11434)
│         │
└── Docker: agent-sandbox
    ├── Python 3.11 + Playwright + Chromium (headless)
    ├── ReAct Loop (DOM 剪枝 + JSON Tool Calling)
    └── volume .:/app (截圖 / 產出物回寫本機)
```

## 3. MVP 範圍

### In scope（一定要有）
1. `docker-compose.yml`：單一 service `agent-sandbox`。
2. `Dockerfile.agent`：以 `mcr.microsoft.com/playwright/python:v1.42.0-jammy` 為基底。
3. `requirements.txt`：`requests==2.31.0`、`playwright==1.42.0`。
4. `main.py`：ReAct 主迴圈 + 4 個 tool + DOM 剪枝 + 結束截圖。
5. 建置與執行 SOP + 驗收標準（見 §7）。

### Out of scope（明確不做，留給 v0.2+）
- ❌ Teach-a-Task 操作錄製 / Routine 排程
- ❌ 多 Bot 協同 / Message Bus
- ❌ Web UI（FastAPI / React / Electron）、WebSocket 即時串流、VNC
- ❌ 向量記憶（Qdrant/Chroma）、長期 Skill 庫
- ❌ `read_file` / `execute_bash` / Gmail / Notion 等擴充 tool
- ❌ Linux 生產環境 GPU 容器化（nvidia-container-toolkit）
- ❌ Computer Use 視覺座標點擊（等換大模型再做）

## 4. 專案結構

```text
docker-bot/
├── plan.md              # 本文件
├── Dockerfile.agent
├── docker-compose.yml
├── requirements.txt
├── main.py
└── final_screenshot.png # 執行後產出（gitignore，僅本地驗證用）
```

## 5. 技術規格

### 5.1 環境變數
| 變數 | 預設值 | 說明 |
|---|---|---|
| `OLLAMA_HOST` | `http://host.docker.internal:11434` | Mac 本機 Ollama 位址 |
| `HEADLESS` | `true` | 容器內固定 `true`，本地除錯可設 `false` |
| `MODEL_NAME` | `qwen3.5:4b`（寫死在 `main.py`） | 不開放切換，避免 4B 以外未驗證 |

### 5.2 Tool 定義（4 個，JSON Schema）
1. `navigate(url)` — 前往指定 URL。
2. `type_text(selector, text)` — `page.fill()` 填輸入框。
3. `click_element(selector)` — `page.click()` 點擊。
4. `finish_task(result)` — 宣告任務完成/放棄，結束迴圈。

> 設計原則（配合 4B 模型）：參數只用 `string`，description 用中文短句；不用巢狀 object，避免模型輸出錯誤。

### 5.3 ReAct 主迴圈
```
messages = [system, user_prompt]
step = 0, max_steps = 10
while not done and step < max_steps:
  1. 若 page.url != about:blank → JS 抓取 input/button/a，
     只取 tag/id/name/text/selector，前 15 筆，append 為 user message
  2. POST {OLLAMA_HOST}/api/chat {model, messages, tools, stream:false} (timeout=60s)
  3. 若無 tool_calls → 印出 content，continue
  4. 依序執行 tool，try/except 包住 Playwright 動作，
     回傳 {"status":"executed","detail":...} 為 tool message
  5. 若 finish_task → done = True
page.screenshot(final_screenshot.png); browser.close()
```

### 5.4 DOM 剪枝規則（關鍵：防 4B context 爆掉）
```js
Array.from(document.querySelectorAll('input, button, a'))
  .map(el => ({
    tag: el.tagName,
    id: el.id,
    name: el.name,
    text: (el.innerText || el.value || '').trim(),
    selector: el.id ? '#'+el.id : (el.name ? `[name="${el.name}"]` : el.tagName.toLowerCase())
  })).slice(0, 15)
```
- 不送完整 HTML、不送截圖。
- system prompt 固定一句：「你是自動化 Agent，能呼叫工具操作瀏覽器完成任務，請依當前網頁狀況選工具。」

## 6. 檔案規格摘要

- **requirements.txt**：僅 2 行（見 §3），版本釘死。
- **Dockerfile.agent**：`FROM playwright/python:v1.42.0-jammy` → `WORKDIR /app` → `pip install -r requirements.txt` → `COPY . .` → `CMD ["python","main.py"]`。
- **docker-compose.yml**：單 service，`environment` 帶 `OLLAMA_HOST`/`HEADLESS`，`volumes: - .:/app`，`extra_hosts: host.docker.internal:host-gateway`，`tty/stdin_open: true`。**不含 `ollama-server` service、不掛 `~/.ollama`**（已決議 Ollama 跑本機）。
- **main.py**：約 120 行；`__main__` 預設 prompt：`請幫我打開 https://www.google.com 並在搜尋框輸入 'NQU ERP'，然後完成任務。`

## 7. 建置、執行與驗收

### SOP（3 步）
```bash
# 0. 前置：Mac 本機 Ollama 必須先跑起來
ollama run qwen3.5:4b   # 另開一終端保持運行，或確認 ollama serve 監聽 :11434

# 1. 建置（在 docker-bot/ 下）
docker compose build

# 2. 執行
docker compose run --rm agent-sandbox
```

### 驗收標準（DoD）
- [ ] `docker compose run` 能連上 `OLLAMA_HOST`，log 第一行印出 `Ollama 端點` 且無 `呼叫失敗`。
- [ ] 終端機可見 `Step 1..N` ReAct 日誌，至少出現 1 次 `navigate` + 1 次 `finish_task`。
- [ ] 本機 `docker-bot/final_screenshot.png` 成功生成，打開可見 Google 搜尋結果頁。
- [ ] 連續跑 2 次皆在 `max_steps=10` 內結束（未無限迴圈）。

### 除錯開關
- 連不到 Ollama → 在 Mac 執行 `curl http://localhost:11434/api/tags` 確認服務；容器內改測 `host.docker.internal`。
- 元素點不到 → `HEADLESS=false` 在 Mac 本地（非 Docker）跑一次 `python main.py` 肉眼觀察。
- 模型亂回散文 → 檢查 `tools` 是否正確傳入、`stream: false` 是否設置。

## 8. 風險與限制（4B 模型已知問題）

1. **Tool Calling 不穩**：qwen3.5:4b 偶爾輸出散文而非 tool_calls → 對策：`max_steps` 熔斷 + `continue` 等下一輪狀態補充。
2. **Selector 脆弱**：無 id/name 的元素退化為 `TAG` 會重複 → MVP 接受失敗，v0.2 再引入 `data-testid` / role-based 定位。
3. **無視覺能力**：不处理驗證碼、Canvas、無 API 傳統系統 → 明確列為非目標。
4. **Mac Docker 網路**：`host.docker.internal` 在舊版 Docker 需 `extra_hosts` → 已寫入 compose。

## 9. 下一步（v0.2 候選，不在本次實作）
1. 加 `read_file` / `save_to_json` tool，讓 Agent 能寫檔。
2. FastAPI 輕量 CLI/Web 輸入（取代寫死 prompt）。
3. 成功/失敗 log 存檔，累積為 Skill 範例。

---
*驗收方式： reviewer 只需執行 §7 三行指令 + 檢查截圖，即可判定 MVP 通過。*
