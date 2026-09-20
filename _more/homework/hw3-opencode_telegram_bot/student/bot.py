#!/usr/bin/env python3
"""Telegram Bot for opencode (student edition, cross-platform).

Run via run.sh (it loads config.env and exports env vars).
Required env: BOT_TOKEN, ALLOWED_USER_ID, WORK_DIR
Optional env: OPENCODE_BIN (default: opencode from PATH),
              OPENCODE_MODEL (default: opencode default model)

Design notes (each one is a lesson learned, see ../_doc/telegram-bot.md):
1. opencode MUST run with `--agent build`, otherwise it defaults to plan mode
   which only writes plans and never creates files.
2. No MarkdownV2 parse_mode: special chars raise BadRequest and kill the reply.
   Plain text + 4096-char chunking instead.
3. opencode writes progress to stderr ("Wrote file successfully"), so merge the
   useful stderr lines back into the Telegram reply.
4. Free-tier policy: OpenCode free allowance is interactive-TUI only.
   Headless `opencode run` needs a Go subscription or your own provider key
   (BYOK). Never bypass this (e.g. no header spoofing). If the provider says
   "free tier", the bot replies with a hint instead of failing silently.
"""
import os
import re
import shutil
import subprocess
import sys
import traceback

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
try:
    ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
except ValueError:
    ALLOWED_USER_ID = 0
WORK_DIR = os.getenv("WORK_DIR", "")
OPENCODE_BIN = os.getenv("OPENCODE_BIN", "").strip() or shutil.which("opencode") or "opencode"
OPENCODE_MODEL = os.getenv("OPENCODE_MODEL", "").strip()

CHUNK = 3800  # safety margin under Telegram's 4096-char limit
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]")
STATUS_LINE_RE = re.compile(r"^\s*>\s*(plan|build)\b")


def split_text(s, n=CHUNK):
    return [s[i:i + n] for i in range(0, len(s), n)] or [""]


def clean_output(s):
    """Strip ANSI colors and opencode status lines like `> build ...`."""
    s = ANSI_RE.sub("", s or "")
    lines = [ln for ln in s.splitlines() if not STATUS_LINE_RE.match(ln)]
    return "\n".join(lines).strip()


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ 無存取權限。")
        return
    await update.message.reply_text(
        "✅ Bot 連線正常。\n"
        f"WORK_DIR={WORK_DIR}\n"
        f"MODEL={OPENCODE_MODEL or '<opencode 預設>'}\n"
        "直接傳一句話就會丟給 opencode 執行（例如：幫我寫一個 hello.py）。"
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
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
        out = clean_output(proc.stdout)
        err = clean_output(proc.stderr)
        if out.strip():
            output = out
            hits = [
                ln.strip() for ln in err.splitlines()
                if ("Wrote file" in ln or re.search(r"(^|\s)Write\s+\S", ln)) and ln.strip()
            ]
            if hits:
                output += "\n\n" + "\n".join(hits)
        else:
            output = err or "✅ 指令執行完畢，無輸出內容。"
        if "free tier" in output.lower():
            output += (
                "\n\n💡 這是 opencode 授權/額度問題（免費額度只能在互動式視窗用，"
                "自動化需 Go 訂閱或自備 provider key）：\n"
                "1) 執行 `opencode auth login` 登入有額度的帳號\n"
                "2) 或在 config.env 設定 OPENCODE_MODEL=<自備 key 的模型> 後重啟 Bot"
            )
        parts = split_text(output.strip())
        await status_msg.edit_text(parts[0][:4096])
        for p in parts[1:]:
            await update.message.reply_text(p[:4096])
        print(f"[done] rc={proc.returncode} bytes={len(output)}", flush=True)
    except subprocess.TimeoutExpired:
        await status_msg.edit_text("⚠️ 執行逾時（超過 5 分鐘）。")
    except FileNotFoundError as e:
        print(f"[ERR] {e}\n{traceback.format_exc()}", flush=True)
        await status_msg.edit_text(f"❌ 找不到 opencode：{OPENCODE_BIN}\n請檢查安裝步驟。")
    except Exception as e:  # noqa: BLE001 - must report back to Telegram no matter what
        print(f"[ERR] {e}\n{traceback.format_exc()}", flush=True)
        await status_msg.edit_text(f"❌ 執行失敗：{e}"[:4096])


def main():
    if not BOT_TOKEN or not ALLOWED_USER_ID or not WORK_DIR:
        print("❌ 缺少 BOT_TOKEN / ALLOWED_USER_ID / WORK_DIR，請用 run.sh 啟動。", flush=True)
        sys.exit(1)
    if not os.path.isdir(WORK_DIR):
        print(f"❌ WORK_DIR 不存在：{WORK_DIR}", flush=True)
        sys.exit(1)
    print(
        f"Bot 啟動中... user={ALLOWED_USER_ID} workdir={WORK_DIR} "
        f"opencode={OPENCODE_BIN} model={OPENCODE_MODEL or '<default>'}",
        flush=True,
    )
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
