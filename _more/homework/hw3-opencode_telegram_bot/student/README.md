# 手機呼叫 opencode：Telegram Bot（學生版）

在 Telegram 傳一句話，你電腦上的 opencode 就會寫程式並回報結果。
Windows（Git 附的 bash）/ macOS / Linux 通用。

## 0. 前置需求

| 系統 | 需要安裝 |
|---|---|
| Windows | Git for Windows（用它的 Git Bash 開終端機）、Python（[python.org](https://www.python.org/downloads/)，安裝時勾選 Add to PATH）、Node.js LTS（[nodejs.org](https://nodejs.org/)） |
| macOS | Python3、Node（`brew install python3 node`，或官網安裝包） |
| Linux | `sudo apt-get install -y python3 python3-pip` ＋ Node.js |

> Windows 注意：不要用 Microsoft Store 版的假 `python3`，請從 python.org 安裝。
> `install.sh` 會自動檢查，缺什麼會告訴你去哪裝。

## 1. 申請 Telegram Bot（約 1 分鐘，全系統通用）

1. 在 Telegram 搜尋 `@BotFather`（認明藍色勾勾），`/newbot`，照指示取名，拿到 **Bot Token**。
2. 搜尋 `@userinfobot`，隨便傳訊息，拿到你的 **User ID（純數字）**。
3. Token 是密碼，不要貼到公開地方、不要上傳 GitHub。

## 2. 一次性安裝

```bash
cd student
bash install.sh
```

它會依序：找 Python → 裝 opencode（缺的話）→ 裝 `python-telegram-bot` →
問你 Token / User ID / 工作目錄 → 驗證 Token → 檢查 opencode 授權 →
問你要不要連線測試。缺東西會停下來告訴你補什麼。

## 3. opencode 授權（重要，政策說明）

- 先跑 `opencode auth login` 登入。
- **政策**：opencode 免費額度只能在「互動式視窗」使用；這種「自動呼叫」
  需要 **Go 訂閱**或**自備 provider key（BYOK）**，否則會看到 `free tier` 錯誤。
  這是官方反濫用規定，**不要用任何繞過手法**（例如偽造 headers）。
- 若你只有免費額度：在 `install.sh` 的「自備模型」欄填你的模型
 （例如 provider key 對應的 model id），或訂閱 Go。

## 4. 啟動 Bot

```bash
bash run.sh
```

看到 `✅ Token 有效` 和 `Bot 啟動中...` 就成功了。
到 Telegram 找到你的 Bot：先發 `/start`（有回 ✅ 才算通），再例如：

```
請用 Python 寫一個 hello.py，印出今天日期
```

檔案會出現在你設的工作目錄，結果回傳到 Telegram。停止按 `Ctrl+C`。

## 5. 常見問題

| 現象 | 原因／解法 |
|---|---|
| 完全無回應 | Bot 沒跑起來。看終端機的 `✅/❌` 自檢行；同一 Token 同一時間只能一個程式在跑，舊的先 `Ctrl+C` |
| 有回應但檔案沒產生 | opencode 跑到 plan 模式了。本包已固定 `--agent build`，若你改過 `bot.py` 請檢查 |
| 回覆亂碼／失敗 | 不要用 `MarkdownV2` 包程式碼（本包已用純文字＋分段） |
| `free tier` 錯誤 | 見第 3 節：換有額度的帳號登入或自備 key |
| `找不到 opencode` | 啟動它的終端機 PATH 跟安裝時不同；重開終端機或重跑 `install.sh` |
| Windows 閃退／報錯 | 確認用的是 Git Bash（不是 cmd），且 `python --version` 是 3.9+ 的 python.org 版 |

## 6. 檔案說明

- `install.sh`：一次性安裝＋設定，產生 `config.env`（Token 住這裡，已被 `.gitignore` 排除）
- `run.sh`：每次啟動用，載入 `config.env` 並做自檢（目錄可寫、套件、opencode 路徑、Token）
- `bot.py`：主程式。只回 `ALLOWED_USER_ID` 的訊息，其他人一律拒絕
- `config.env`：機密！不要上傳、不要截圖外流

## 7. 進階（選做）

- 前景執行關視窗就停；要 24 小時跑：Windows 用工作排程器、macOS 用 launchd、Linux 用 systemd 跑 `run.sh`。
- 練習：改 `bot.py` 的歡迎詞、加一個 `/help` 指令、把 `OPENCODE_MODEL` 釘成固定模型。
- 完整除錯血淚史：`../_doc/telegram-bot.md`。
