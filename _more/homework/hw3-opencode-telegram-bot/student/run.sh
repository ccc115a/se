#!/bin/bash
# run.sh — 啟動 Telegram Bot（前景執行，Windows git-bash / macOS / Linux 通用）
# 用法：bash run.sh
# 停止：Ctrl+C。關掉視窗 Bot 就停；要 24 小時跑請看 README 的常駐章節。
set -u

START_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$START_DIR/config.env"
OS="$(uname -s)"
echo "=== OpenCode Telegram Bot ===  OS=$OS  user=$(whoami)"

# ---------- 1. 載入設定 ----------
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ 找不到 ${CONFIG_FILE}，請先執行： bash install.sh"
  exit 1
fi
set -a
# shellcheck disable=SC1090
. "$CONFIG_FILE"
set +a
: "${OPENCODE_MODEL:=}"
if [ -z "${BOT_TOKEN:-}" ] || [ -z "${ALLOWED_USER_ID:-}" ] || [ -z "${WORK_DIR:-}" ]; then
  echo "❌ config.env 缺少 BOT_TOKEN / ALLOWED_USER_ID / WORK_DIR，請重跑 install.sh。"
  exit 1
fi

# ---------- 2. 工作目錄可寫檢查 ----------
mkdir -p "$WORK_DIR" 2>/dev/null || { echo "❌ 無法建立 WORK_DIR=$WORK_DIR"; exit 1; }
if ! touch "$WORK_DIR/.write-test" 2>/dev/null; then
  echo "❌ WORK_DIR 無寫入權限：${WORK_DIR}（opencode 會建不出檔案，請換目錄或修權限）"
  exit 1
fi
rm -f "$WORK_DIR/.write-test"
echo "✅ WORK_DIR 可寫：$WORK_DIR"

# ---------- 3. 找 Python（要有 telegram 套件的那個）----------
PYTHON=""
for cand in python3 python /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  case "$cand" in
    /*) P="$cand" ;;
    *)  P="$(command -v "$cand" 2>/dev/null || true)" ;;
  esac
  [ -n "$P" ] && [ -x "$P" ] || continue
  if "$P" -c "import telegram" 2>/dev/null; then PYTHON="$P"; break; fi
done
if [ -z "$PYTHON" ]; then
  echo "❌ 找不到有裝 python-telegram-bot 的 Python。請重跑 bash install.sh。"
  exit 1
fi
echo "✅ PYTHON=$PYTHON ($("$PYTHON" --version 2>&1))"

# ---------- 4. 找 opencode（絕對路徑，避免背景/服務 PATH 問題）----------
OPENCODE_BIN=""
for cand in "$(command -v opencode 2>/dev/null || true)" \
            "$HOME/.opencode/bin/opencode" \
            /opt/homebrew/bin/opencode /usr/local/bin/opencode; do
  [ -n "$cand" ] && [ -x "$cand" ] || continue
  OPENCODE_BIN="$cand"
  break
done
if [ -z "$OPENCODE_BIN" ]; then
  # Windows 上 npm 裝的可能是 opencode.cmd，交給 bot.py 的 shutil.which 再找一次
  if "$PYTHON" -c "import shutil,sys; sys.exit(0 if shutil.which('opencode') else 1)" 2>/dev/null; then
    OPENCODE_BIN="$("$PYTHON" -c "import shutil; print(shutil.which('opencode'))")"
  fi
fi
if [ -z "$OPENCODE_BIN" ]; then
  echo "❌ 找不到 opencode，請先安裝（bash install.sh 會引導）。"
  exit 1
fi
echo "✅ OPENCODE_BIN=$OPENCODE_BIN"
echo "MODEL=${OPENCODE_MODEL:-<opencode 預設>}"

# ---------- 5. Token 快速驗證 ----------
if command -v curl >/dev/null 2>&1; then
  ME="$(curl -s -m 15 "https://api.telegram.org/bot${BOT_TOKEN}/getMe" || true)"
  case "$ME" in
    *'"ok":true'*) echo "✅ Token 有效。" ;;
    *) echo "⚠️  Token 驗證無回應（網路問題或 Token 錯誤），繼續啟動，稍後看 log。" ;;
  esac
fi

# ---------- 6. 啟動（前景）----------
export BOT_TOKEN ALLOWED_USER_ID WORK_DIR OPENCODE_BIN OPENCODE_MODEL
echo "--- 啟動中（前景，Ctrl+C 停止）---"
echo "先在 Telegram 對 Bot 發 /start，有回 ✅ 才算通。"
exec "$PYTHON" "$START_DIR/bot.py"
