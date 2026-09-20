# 手機呼叫 opencode：Telegram Bot（老師實作區）

本目錄是老師的實作與除錯區：`run_bot.sh`（老師自用前景啟動）、`_doc/`（除錯紀錄）、
`student/`（發給學生的跨平台教材包）。學生請直接看 `student/README.md`。

## student/ 教材包（Windows git-bash / macOS / Linux 通用）

- `bot.py` — 主程式（`--agent build`、純文字分段、`shutil.which` Windows 備援、free-tier 合規提示）
- `install.sh` — 一次設定：找 Python 3.9+ → 裝 opencode → 裝套件 → 問 Token/ID/目錄 →
  curl 驗 Token → 授權檢查＋政策提醒 → 選做連線測試
- `run.sh` — 啟動自檢：config → 目錄可寫 → Python＋套件 → opencode 絕對路徑 → Token 驗證 → 前景執行
- `README.md` — 學生操作手冊（含 Windows 前置需求、BotFather 步驟、FAQ、進階常駐指引）
- `.gitattributes`（`.sh` 強制 LF，Windows 簽出才不會炸）、`.gitignore`（`config.env` 不進版控）

## 驗證結果（含一個意外收穫）

1. `bash -n`＋`py_compile` 全過
2. 無 config 跑 `run.sh` → 乾淨報錯；假 Token 跑 `install.sh` → 驗證擋下且不寫檔；
   假 Token 跑 `run.sh` → 自檢全綠、Telegram 回 `Invalid token`（整條路徑通）
3. **意外**：macOS 內建 bash 是 3.2，`$VAR，`（變數緊貼全形標點）會直接 `unbound variable` —
   已全部改 `${VAR}` 修好。這坑學生用 `./run.sh`（shebang 走 `/bin/bash`）必踩，還好測試抓到了

## 發給學生前請確認兩件事

1. `student/` 目前擁有者是 `cccuser`，若要全班讀取，放共用區或 Git repo 前記得調權限
2. Windows 實機這裡沒有，建議找一台學生機跑一次 `bash install.sh`，有問題把報錯貼回來

## 本目錄其他檔案

- `run_bot.sh` — 老師自用版前景啟動（已驗證通，身份 `cccuser`＋Go 授權）
- `run.sh` / `imac-install.sh` — 早期版本（已被 `run_bot.sh` 取代，留存備查）
- `_doc/install.md` — 初次安裝過程紀錄；`_doc/telegram-bot.md` — 五坑完整除錯血淚史
- `tsmc.py` / `tsmc3.py` — 課堂實測產物（台積電股價腳本）
