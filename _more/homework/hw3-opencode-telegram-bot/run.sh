#!/bin/bash

APP_DIR="$HOME/.opencode-bot"
PLIST_PATH="$HOME/Library/LaunchAgents/com.opencode.telegram.bot.plist"
SERVICE_NAME="opencode-bot"

# 自動判斷作業系統類型
OS_TYPE=$(uname -s)

ACTION=${1:-"start"}

case "$ACTION" in
    start)
        echo "正在啟動 OpenCode Telegram Bot..."
        if [ "$OS_TYPE" = "Darwin" ]; then
            # macOS
            launchctl load "$PLIST_PATH" 2>/dev/null || true
        else
            # Linux (Linux 專用指令)
            sudo systemctl start "$SERVICE_NAME"
        fi
        echo "✅ 服務已啟動！"
        ;;

    stop)
        echo "正在停止 OpenCode Telegram Bot..."
        if [ "$OS_TYPE" = "Darwin" ]; then
            # macOS
            launchctl unload "$PLIST_PATH" 2>/dev/null || true
        else
            # Linux
            sudo systemctl stop "$SERVICE_NAME"
        fi
        echo "🛑 服務已停止。"
        ;;

    restart)
        echo "正在重啟 OpenCode Telegram Bot..."
        if [ "$OS_TYPE" = "Darwin" ]; then
            # macOS
            launchctl unload "$PLIST_PATH" 2>/dev/null || true
            launchctl load "$PLIST_PATH"
        else
            # Linux
            sudo systemctl restart "$SERVICE_NAME"
        fi
        echo "🔄 服務已重啟！"
        ;;

    log)
        echo "顯示實時 Log (按 Ctrl+C 離開):"
        if [ "$OS_TYPE" = "Darwin" ]; then
            # macOS Log 檔案
            tail -f "$APP_DIR/bot.log" "$APP_DIR/bot.err"
        else
            # Linux Systemd Journal 日誌
            sudo journalctl -u "$SERVICE_NAME" -f
        fi
        ;;

    status)
        if [ "$OS_TYPE" = "Darwin" ]; then
            echo "--- macOS 服務狀態 ---"
            launchctl list | grep "com.opencode.telegram.bot" || echo "服務未運行"
        else
            echo "--- Linux 服務狀態 ---"
            sudo systemctl status "$SERVICE_NAME"
        fi
        ;;

    *)
        echo "用法: $0 {start|stop|restart|log|status}"
        exit 1
        ;;
esac