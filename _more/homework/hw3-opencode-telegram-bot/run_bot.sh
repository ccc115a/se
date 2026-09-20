#!/bin/bash
# run_bot.sh — 給 cccimac 用的前景版 Telegram Bot 啟動腳本
# 用法（以 cccimac 身份）：
#   cd /Users/Shared/ccc/bot && ./run_bot.sh
# 說明：前景執行，Ctrl+C 即停止；先驗證環境再跑，log 直接印在終端機。
set -u

SHARED_DIR="/Users/Shared/ccc/bot"
APP_DIR="$HOME/.opencode-bot"
CONFIG_FILE="$APP_DIR/config.env"
BOT_FILE="$APP_DIR/bot_run.py"

echo "=== OpenCode Telegram Bot（前景版）==="
echo "身份: $(whoami)  HOME=$HOME"

# 1. 身份檢查（cccuser 有 Go 授權可跑 headless；cccimac 只有 Zen 免費額度會被擋）
if [ "$(whoami)" != "cccuser" ] && [ "$(whoami)" != "cccimac" ]; then
  echo "⚠️  你現在是 $(whoami)，請用 cccuser（建議，有 Go 授權）或 cccimac 執行。"
  echo "   請改用： su - cccuser  後再執行。"
  exit 1
fi
if [ "$(whoami)" = "cccimac" ]; then
  echo "⚠️  注意：cccimac 只有 Zen 免費額度，opencode 政策不允許 headless 呼叫，"
  echo "   會噴 free-tier 錯誤。強烈建議改用 cccuser 執行。"
fi

# 2. 載入設定
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ 找不到 $CONFIG_FILE"
  echo "   請先以 cccimac 執行 ./imac-install.sh 產生設定。"
  exit 1
fi
set -a
# shellcheck disable=SC1090
. "$CONFIG_FILE"
set +a

if [ -z "${BOT_TOKEN:-}" ] || [ -z "${ALLOWED_USER_ID:-}" ] || [ -z "${WORK_DIR:-}" ]; then
  echo "❌ config.env 缺少 BOT_TOKEN / ALLOWED_USER_ID / WORK_DIR"
  exit 1
fi
# 選填：自備模型（BYOK），避開免費額度限制。例：OPENCODE_MODEL="openrouter/qwen3-coder-plus"
: "${OPENCODE_MODEL:=}"
echo "MODEL=${OPENCODE_MODEL:-<opencode 預設>}"

# 3. 工作目錄可寫檢查（你設的是 /Users/Shared/ccc/bot，擁有人是 cccuser，cccimac 預設寫不進）
mkdir -p "$WORK_DIR" 2>/dev/null || {
  echo "❌ 無法建立 WORK_DIR=$WORK_DIR"
  exit 1
}
if ! touch "$WORK_DIR/.write-test" 2>/dev/null; then
  echo "❌ WORK_DIR 無寫入權限：$WORK_DIR"
  echo "   這就是 tsmc.py 沒產生的原因之一。請擇一修復："
  echo "   A) sudo chown -R cccimac:staff \"$WORK_DIR\" && chmod -R 775 \"$WORK_DIR\""
  echo "   B) 改用家目錄：WORK_DIR=\$HOME/opencode-workspace（重跑 install 時填）"
  exit 1
fi
rm -f "$WORK_DIR/.write-test"
echo "✅ WORK_DIR 可寫：$WORK_DIR"

# 4. 找 python（必須 import telegram 成功的那一個）
PYTHON=""
for cand in "$(command -v python3 2>/dev/null)" /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
  [ -n "$cand" ] && [ -x "$cand" ] || continue
  if "$cand" -c "import telegram" 2>/dev/null; then
    PYTHON="$cand"
    break
  fi
done
if [ -z "$PYTHON" ]; then
  echo "❌ 找不到有裝 python-telegram-bot 的 python3。"
  P3="$(command -v python3)"
  echo "   請執行： ${P3:-python3} -m pip install python-telegram-bot"
  echo "   （你曾用 cccuser 的 pyenv 檢查會顯示未安裝，那是錯的帳號/錯的 python）"
  exit 1
fi
echo "✅ PYTHON=$PYTHON ($("$PYTHON" --version 2>&1))"

# 5. 找 opencode（launchd 下 PATH 找不到是舊版最大坑，這裡用絕對路徑）
OPENCODE_BIN=""
for cand in "$(command -v opencode 2>/dev/null)" "$HOME/.opencode/bin/opencode" /Users/cccimac/.opencode/bin/opencode /opt/homebrew/bin/opencode /usr/local/bin/opencode; do
  [ -n "$cand" ] && [ -x "$cand" ] || continue
  OPENCODE_BIN="$cand"
  break
done
if [ -z "$OPENCODE_BIN" ]; then
  echo "❌ 找不到 opencode 執行檔，請先安裝/登入 opencode。"
  exit 1
fi
echo "✅ OPENCODE_BIN=$OPENCODE_BIN ($("$OPENCODE_BIN" --version 2>&1 | head -n 1))"

# 6. Token 快速驗證（網路失敗則跳過，不擋啟動）
if command -v curl >/dev/null 2>&1; then
  ME="$(curl -s -m 10 "https://api.telegram.org/bot${BOT_TOKEN}/getMe" || true)"
  case "$ME" in
    *'"ok":true'*) echo "✅ Token 有效：$(echo "$ME" | cut -c1-120)" ;;
    *) echo "⚠️  Token 驗證無回應（可能是網路問題），繼續啟動，稍後看 log 確認。" ;;
  esac
fi

# 7. 產生修好版 bot（重點修：--agent build 才寫檔、合併 stderr 寫檔證據、去 ANSI、訊息分段、/start）
cat > "$BOT_FILE" <<'PYEOF'
import os, subprocess, sys, traceback
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
try:
    ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
except ValueError:
    ALLOWED_USER_ID = 0
WORK_DIR = os.getenv("WORK_DIR", "")
OPENCODE_BIN = os.getenv("OPENCODE_BIN", "opencode")
OPENCODE_MODEL = os.getenv("OPENCODE_MODEL", "").strip()

CHUNK = 3800  # 留安全邊界給 Telegram 4096 上限

def split_text(s, n=CHUNK):
    return [s[i:i+n] for i in range(0, len(s), n)] or [""]

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ 無存取權限。")
        return
    await update.message.reply_text(
        f"✅ Bot 連線正常。\nWORK_DIR={WORK_DIR}\n直接傳一句話就會丟給 opencode 執行（例如：幫我寫 tsmc.py）。"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ 無存取權限。")
        return
    prompt = (update.message.text or "").strip()
    if not prompt:
        return
    print(f"[msg] from={update.effective_user.id} prompt={prompt[:120]}", flush=True)
    status_msg = await update.message.reply_text("🤖 OpenCode 執行中，請稍候... (build mode)")
    try:
        cmd = [OPENCODE_BIN, "run", "--agent", "build"]
        if OPENCODE_MODEL:
            cmd += ["-m", OPENCODE_MODEL]
        cmd.append(prompt)
        print(f"[run] model={OPENCODE_MODEL or '<default>'}", flush=True)
        proc = subprocess.run(
            cmd,
            cwd=WORK_DIR, capture_output=True, text=True, timeout=300,
        )
        import re as _re
        def _clean(s):
            s = s or ""
            s = _re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", s)  # 去 ANSI 色碼
            lines = [ln for ln in s.splitlines() if not _re.match(r"^\s*>\s*(plan|build)\b", ln)]
            return "\n".join(lines).strip()
        out = _clean(proc.stdout)
        err = _clean(proc.stderr)
        if out.strip():
            output = out
            # stderr 內的寫檔證據（Wrote file / Write <path>）一併帶回，否則使用者不知道檔寫了沒
            hits = [ln.strip() for ln in err.splitlines()
                    if ("Wrote file" in ln or _re.search(r"(^|\s)Write\s+\S", ln)) and ln.strip()]
            if hits:
                output += "\n\n" + "\n".join(hits)
        else:
            output = err or "✅ 指令執行完畢，無輸出內容。"
        if "free tier" in output.lower():
            output += ("\n\n💡 這是 cccimac 帳號的 opencode 授權/額度問題："
                       "\n1) 在 cccimac 終端跑 `opencode auth login` 登入"
                       "\n2) 或在 ~/.opencode-bot/config.env 加一行 OPENCODE_MODEL=<自備key的模型> 後重啟 Bot")
        # 純文字回覆：不使用 MarkdownV2，避免特殊字元導致 BadRequest 整段失敗
        parts = split_text(output.strip())
        await status_msg.edit_text(parts[0][:4096])
        for p in parts[1:]:
            await update.message.reply_text(p[:4096])
        print(f"[done] rc={proc.returncode} bytes={len(output)}", flush=True)
    except subprocess.TimeoutExpired:
        await status_msg.edit_text("⚠️ 執行逾時（超過 5 分鐘）。")
    except FileNotFoundError as e:
        print(f"[ERR] {e}\n{traceback.format_exc()}", flush=True)
        await status_msg.edit_text(f"❌ 找不到 opencode：{OPENCODE_BIN}\n請檢查 run_bot.sh 的路徑偵測。")
    except Exception as e:
        print(f"[ERR] {e}\n{traceback.format_exc()}", flush=True)
        # fallback 不用 parse_mode，保證錯誤訊息發得出去
        await status_msg.edit_text(f"❌ 執行失敗：{e}"[:4096])

def main():
    if not BOT_TOKEN or not ALLOWED_USER_ID or not WORK_DIR:
        print("❌ 環境變數缺 BOT_TOKEN / ALLOWED_USER_ID / WORK_DIR", flush=True)
        sys.exit(1)
    if not os.path.isdir(WORK_DIR):
        print(f"❌ WORK_DIR 不存在：{WORK_DIR}", flush=True)
        sys.exit(1)
    print(f"Bot 啟動中... user={ALLOWED_USER_ID} workdir={WORK_DIR} opencode={OPENCODE_BIN} model={OPENCODE_MODEL or '<default>'}", flush=True)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
PYEOF

export BOT_TOKEN ALLOWED_USER_ID WORK_DIR OPENCODE_BIN OPENCODE_MODEL
echo "✅ 已產生 $BOT_FILE"
echo "--- 啟動中（前景，Ctrl+C 停止）---"
echo "請在 Telegram 對 Bot 先發 /start，有回 ✅ 才算通。"
exec "$PYTHON" "$BOT_FILE"
