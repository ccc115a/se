#!/bin/bash

# 當任何指令發生錯誤時立即停止
set -e

echo "=== [1/2] 安裝依賴與配置環境 ==="

# 互動式收集資訊
read -p "請輸入您的 Telegram Bot Token: " BOT_TOKEN
read -p "請輸入您的 Telegram User ID (純數字): " ALLOWED_USER_ID
read -p "請輸入 OpenCode 工作目錄路徑 (預設: $HOME/opencode-workspace): " WORK_DIR

WORK_DIR=${WORK_DIR:-"$HOME/opencode-workspace"}
APP_DIR="$HOME/.opencode-bot"

mkdir -p "$WORK_DIR"
mkdir -p "$APP_DIR"

# 檢查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未檢測到 Homebrew，請先安裝 Homebrew (https://brew.sh)"
    exit 1
fi

# 檢查與安裝依賴
command -v node &> /dev/null || brew install node
command -v python3 &> /dev/null || brew install python3
command -v opencode &> /dev/null || npm install -g opencode-ai

python3 -m pip install python-telegram-bot --break-system-packages 2>/dev/null || python3 -m pip install python-telegram-bot

# 儲存環境變數檔 config.env
cat << EOF > "$APP_DIR/config.env"
BOT_TOKEN="${BOT_TOKEN}"
ALLOWED_USER_ID=${ALLOWED_USER_ID}
WORK_DIR="${WORK_DIR}"
EOF

# 生成 Python 主程式
cat << 'EOF' > "$APP_DIR/bot.py"
import os
import sys
import subprocess
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
WORK_DIR = os.getenv("WORK_DIR")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ 無存取權限。")
        return

    prompt = update.message.text
    status_msg = await update.message.reply_text("🤖 OpenCode 執行中，請稍候...")

    try:
        process = subprocess.run(
            ["opencode", "run", prompt],
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = process.stdout if process.returncode == 0 else process.stderr
        if not output.strip():
            output = "✅ 指令執行完畢，無輸出內容。"

        if len(output) > 4000:
            output = output[:4000] + "\n\n...(長度超過上限已自動截斷)"

        await status_msg.edit_text(f"```\n{output}\n```", parse_mode="MarkdownV2")

    except subprocess.TimeoutExpired:
        await status_msg.edit_text("⚠️ 執行逾時（超過 5 分鐘）。")
    except Exception as e:
        await status_msg.edit_text(f"❌ 執行失敗：{str(e)}")

def main():
    if not BOT_TOKEN or not ALLOWED_USER_ID:
        print("❌ 錯誤：未填寫正確的設定檔。")
        sys.exit(1)
        
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("OpenCode Telegram Bot 已啟動...")
    app.run_polling()

if __name__ == "__main__":
    main()
EOF

# 生成 plist 背景服務檔
PLIST_PATH="$HOME/Library/LaunchAgents/com.opencode.telegram.bot.plist"
PYTHON_PATH=$(which python3)

cat << EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.opencode.telegram.bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${APP_DIR}/bot.py</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>BOT_TOKEN</key>
        <string>${BOT_TOKEN}</string>
        <key>ALLOWED_USER_ID</key>
        <string>${ALLOWED_USER_ID}</string>
        <key>WORK_DIR</key>
        <string>${WORK_DIR}</string>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>${WORK_DIR}</string>
    <key>StandardOutPath</key>
    <string>${APP_DIR}/bot.log</string>
    <key>StandardErrorPath</key>
    <string>${APP_DIR}/bot.err</string>
</dict>
</plist>
EOF

echo "=== ✅ 安裝完畢！請執行 ./run.sh 來啟動服務 ==="