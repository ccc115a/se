# Telegram Bot × opencode 除錯紀錄（2026-09-20）

架構：手機 Telegram → Bot（`run_bot.sh` 前景執行，`~/.opencode-bot/bot_run.py`）→
本機 `opencode run --agent build` → 結果回傳 Telegram。工作目錄 `/Users/Shared/ccc/bot`。

## 1. 帳號錯位＋假啟動（無回應、無檔案）

- 現象：Telegram 完全無回應，`tsmc.py` 沒產生。
- 原因：
  - `install.sh` 用 `cccimac` 跑（設定在家目錄 `~/.opencode-bot`），`run.sh` 卻用 `cccuser` 跑，
    讀到空的 `APP_DIR`；且 `run.sh` 把 `launchctl load` 錯誤吃掉（`2>/dev/null || true`），永遠印 ✅。
  - `launchctl list` 證實服務根本沒註冊。
- 解法：統一用 `cccuser` 跑 Bot；`run_bot.sh` 自檢失敗直接擋下，不再假成功。

## 2. WORK_DIR 寫不進去

- `/Users/Shared/ccc/bot` 擁有者是 `cccuser`，`cccimac` 無 `w`，`opencode` 建檔會失敗。
- 解法：`sudo chown -R cccimac:staff` → 後來統一 `cccuser` 後，以 group `staff` 寫入已通，
  `run_bot.sh` 啟動前會 `touch .write-test` 自檢。

## 3. opencode 預設 plan 模式：只出計畫、不寫檔

- 實測：`opencode run "建檔..."` 只回計畫文；`opencode run --agent build "建檔..."` 才真的寫檔。
- 解法：Bot 固定帶 `--agent build`。注意 `--agent` 在舊版有 bug（1.15.x `InstanceRef`），目前 1.18.31 正常。

## 4. Telegram 回覆炸裂＋輸出遺失

- `edit_text(..., parse_mode="MarkdownV2")` 遇到特殊字元就 `BadRequest` 整段失敗。
- 舊版只看 `stdout`，`Wrote file successfully` 證據在 `stderr` 會遺失。
- 解法：純文字回覆、4096 分段、去 ANSI 色碼、合併 `stderr` 的寫檔證據行。

## 5. 免費額度閘門：Zen 不能 headless（遵守規定，不繞過）

- 現象：`cccimac`（僅 Zen 登入）跑 `opencode run` 噴
  `Error from provider (Console): OpenCode's free tier can only be used from within OpenCode`，
  即使登入後也一樣；同指令 `cccuser`（有 Go）會通。
- 結論：免費額度僅限互動式 TUI，headless 自動化需 Go 訂閱或自備 provider key（BYOK）。
  不採用改 `User-Agent` 等繞過手法。
- 解法：Bot 統一跑 `cccuser`（有 `opencode-go` 授權）。`run_bot.sh` 已支援
  `config.env` 加 `OPENCODE_MODEL="..."` 經 `-m` 覆寫（例：`opencode-go/muse-spark-1.3-contributor`）。

## 目前狀態

- 執行身份：`cccuser`；`opencode`：`/Users/cccuser/.opencode/bin/opencode`（1.18.31）
- 預設模型（實測 log）：`provider=opencode, model=muse-spark-1.3-contributor-free, agent=build`
  （`-free` 掛 `opencode/` 免費池，靠 Go 帳號身份解鎖 headless；Go 版叫 `opencode-go/muse-spark-1.3-contributor`）
- 設定：`/Users/cccuser/.opencode-bot/config.env`（600，只有本人可讀，勿進版控）
- 附帶無害現象：附屬 title 模型 `gpt-5.4-nano` 會噴 `No payment method`，不影響主流程。

## 常用指令

```bash
cd /Users/Shared/ccc/bot && ./run_bot.sh   # 前景啟動（Ctrl+C 停止）
opencode providers list                      # 查授權（cccuser 應有 opencode-go）
opencode run --agent build "say hi"          # 最小驗證， expect "hi"
```

## 待辦

- `cccuser` 的 launchd 背景服務版（開機自啟，現為前景執行，關終端即停）。
- 考慮把 `OPENCODE_MODEL` 釘死為 Go 版，避免免費池政策變動。
- 同一 Bot Token 同一時間只能一個 poller，切換帳號時舊 Bot 務必先 `Ctrl+C`。
