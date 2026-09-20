#!/bin/bash
# install.sh — 一次性環境安裝與設定（Windows git-bash / macOS / Linux 通用）
# 用法：bash install.sh   （或 ./install.sh）
# 做完後用 bash run.sh 啟動 Bot。
set -u

START_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS="$(uname -s)"
echo "=== [install] OS=$OS ==="

# ---------- 0. 找 Python（3.9+）----------
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
      PY="$(command -v "$cand")"
      break
    else
      echo "⚠️  $cand 版本過舊（需 Python 3.9+），跳過。"
    fi
  fi
done
if [ -z "$PY" ]; then
  echo "❌ 找不到 Python 3.9+。請先安裝："
  case "$OS" in
    MINGW*|MSYS*|CYGWIN*) echo "   Windows: https://www.python.org/downloads/ （安裝時勾選 Add to PATH）" ;;
    Darwin*)              echo "   macOS: brew install python3" ;;
    *)                    echo "   Linux: sudo apt-get install -y python3 python3-pip" ;;
  esac
  exit 1
fi
echo "✅ PYTHON=$PY ($("$PY" --version 2>&1))"

# ---------- 1. 找 opencode ----------
if command -v opencode >/dev/null 2>&1; then
  echo "✅ opencode 已安裝：$(opencode --version 2>&1 | head -n 1)"
else
  echo "opencode 未安裝，嘗試透過 npm 安裝..."
  if command -v npm >/dev/null 2>&1; then
    npm install -g opencode-ai || {
      echo "❌ npm 安裝失敗，請參考 https://opencode.ai/docs 手動安裝後重跑。"
      exit 1
    }
  else
    echo "❌ 找不到 npm。請先安裝 Node.js 再重跑："
    case "$OS" in
      MINGW*|MSYS*|CYGWIN*) echo "   Windows: https://nodejs.org/ （LTS 版）" ;;
      Darwin*)              echo "   macOS: brew install node" ;;
      *)                    echo "   Linux: https://nodejs.org/ 或套件管理員" ;;
    esac
    exit 1
  fi
fi

# ---------- 2. Python 依賴 ----------
echo "安裝 python-telegram-bot..."
"$PY" -m pip install python-telegram-bot || {
  echo "❌ pip 安裝失敗。Windows 常見原因：用了 Microsoft Store 的假 python，請改從 python.org 安裝。"
  exit 1
}

# ---------- 3. 互動式設定 ----------
echo ""
echo "請準備：Telegram Bot Token（問 @BotFather /newbot）與你的 User ID（問 @userinfobot）。"
read -r -p "Telegram Bot Token: " BOT_TOKEN
read -r -p "Telegram User ID（純數字）: " ALLOWED_USER_ID
if ! echo "$ALLOWED_USER_ID" | grep -Eq "^[0-9]+$"; then
  echo "❌ User ID 必須是純數字。"
  exit 1
fi
read -r -p "opencode 工作目錄（預設: $HOME/opencode-workspace）: " WORK_DIR
WORK_DIR=${WORK_DIR:-"$HOME/opencode-workspace"}
read -r -p "自備模型（選填，例 openrouter/qwen3-coder-plus，直接 Enter 跳過）: " OPENCODE_MODEL
OPENCODE_MODEL=${OPENCODE_MODEL:-""}

mkdir -p "$WORK_DIR" || { echo "❌ 無法建立 $WORK_DIR"; exit 1; }
if ! touch "$WORK_DIR/.write-test" 2>/dev/null; then
  echo "❌ $WORK_DIR 無寫入權限，請換目錄或修正權限後重跑。"
  exit 1
fi
rm -f "$WORK_DIR/.write-test"

# ---------- 4. Token 驗證（免費的 Telegram API，不花 opencode 額度）----------
if command -v curl >/dev/null 2>&1; then
  ME="$(curl -s -m 15 "https://api.telegram.org/bot${BOT_TOKEN}/getMe" || true)"
  case "$ME" in
    *'"ok":true'*) echo "✅ Token 有效。" ;;
    *) echo "❌ Token 驗證失敗，請檢查後重跑。"; exit 1 ;;
  esac
else
  echo "⚠️  找不到 curl，跳過 Token 驗證（啟動時會再檢查）。"
fi

# ---------- 5. 寫設定檔 ----------
cat > "$START_DIR/config.env" <<EOF
BOT_TOKEN="${BOT_TOKEN}"
ALLOWED_USER_ID=${ALLOWED_USER_ID}
WORK_DIR="${WORK_DIR}"
OPENCODE_MODEL="${OPENCODE_MODEL}"
EOF
chmod 600 "$START_DIR/config.env" 2>/dev/null || true
echo "✅ 已寫入 $START_DIR/config.env（權限已盡量限縮，請勿上傳到 GitHub）"

# ---------- 6. opencode 授權檢查 ----------
echo ""
echo "檢查 opencode 授權..."
CREDS="$(opencode providers list 2>/dev/null | grep -c "●" || true)"
if [ "${CREDS:-0}" -eq 0 ]; then
  echo "⚠️  opencode 尚無任何登入授權。請執行 \`opencode auth login\` 登入後再啟動 Bot。"
else
  echo "✅ opencode 已有 $CREDS 組授權。"
fi
echo ""
echo "政策提醒（重要）：opencode 免費額度只能在互動式視窗使用，"
echo "自動化（就是這個 Bot）需要 Go 訂閱或自備 provider key（BYOK），"
echo "否則會看到 free-tier 錯誤。請遵守官方規定，不要用繞過手法。"

# ---------- 7. 連線測試（花一次便宜的呼叫，可跳過）----------
read -r -p "要做一次 opencode 連線測試嗎（say hi，約數秒）? [Y/n]: " DO_TEST
DO_TEST=${DO_TEST:-"Y"}
if echo "$DO_TEST" | grep -Eiq "^y"; then
  echo "測試中..."
  OUT="$(opencode run --agent build "say hi" 2>&1 | head -n 10 || true)"
  echo "$OUT" | grep -qi "free tier" && {
    echo "❌ 出現 free-tier 錯誤：目前授權不能跑自動化，請先處理授權（見上）。Bot 先不要啟動。"
    exit 1
  }
  echo "測試輸出："
  echo "$OUT"
  echo "（若上行有回應內容即代表連通）"
fi

echo ""
echo "=== ✅ 安裝完成！啟動 Bot： bash run.sh ==="
