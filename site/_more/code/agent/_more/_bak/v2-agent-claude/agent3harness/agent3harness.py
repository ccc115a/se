#!/usr/bin/env python3
# agent.py - AI Agent using Ollama native function calling (qwen3.5:4b)
# 這版加上「harness」：防護欄（guardrails）、可觀測性（log）、輸出治理（截斷）
# 注意：這版還沒有 loop engineering（自動重試/驗證/自我修正），下一版再加
# Run: python agent.py

import asyncio
import aiohttp
import base64
import datetime
import json
import os
import re
import subprocess

# ─── Configuration ───

#MODEL = "qwen3.5:4b"
MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()  # 使用執行 python agent.py 當下所在的資料夾
MAX_TOOL_TURNS = 5        # 一次任務最多允許幾輪工具呼叫
HISTORY_MESSAGES = 12     # 對話歷史最多保留幾則訊息（不含 system）
SHELL_TIMEOUT = 30        # 單一 shell 指令逾時秒數
MAX_TOOL_OUTPUT_CHARS = 4000  # 單次工具輸出超過這個長度就截斷，避免塞爆 context
LOG_PATH = os.path.join(WORKSPACE, "agent.log")

GRAY = "\033[90m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

SYSTEM_PROMPT = (
    "你是 Jarvis，一個運行在使用者電腦上的 AI 助理。\n"
    "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。\n"
    "檔案操作（讀取、寫入、列出目錄）請優先使用 read_file / write_file / list_dir，"
    "不要用 run_shell 去做這些事——結構化工具比較安全也比較不容易出錯。\n"
    "只有在真的需要執行程式、跑指令（例如 git、python、npm）時，才使用 run_shell。\n"
    "避免使用不會自動結束的指令（例如 tail -f、持續監聽的伺服器）。\n"
    "注意：工作區以外的路徑，寫入一律會被阻擋，讀取需要使用者手動同意。"
    "如果工具回傳「已阻擋」或「使用者拒絕」，請不要重複嘗試相同操作，改用其他方式或直接告知使用者。"
)

# ══════════════════════════════════════════════════════════
#  Harness：檔案系統邊界（Workspace Sandboxing）
#  設計原則（參考 OpenCode）：
#    - 工作區內：讀寫都直接允許
#    - 工作區外：讀取需要使用者手動同意；寫入一律阻擋，沒有例外
#  這是「白名單 + 資源邊界」，比對指令字串做 regex 黑名單更可靠，
#  因為判斷的是「最終會動到哪個檔案路徑」，而不是「猜測指令意圖」。
# ══════════════════════════════════════════════════════════

def resolve_path(path: str) -> tuple[str, bool]:
    """回傳 (絕對路徑, 是否在工作區內)。使用 realpath 解析 .. 和符號連結，
    避免用 ../../etc/passwd 這種相對路徑技巧繞過邊界檢查。"""
    abs_path = os.path.realpath(os.path.join(WORKSPACE, os.path.expanduser(path)))
    workspace_real = os.path.realpath(WORKSPACE)
    inside = abs_path == workspace_real or abs_path.startswith(workspace_real + os.sep)
    return abs_path, inside

def ask_user_confirm_read(path: str) -> bool:
    print(f"\n{YELLOW}📖 Agent 想讀取工作區以外的檔案：{RESET}")
    print(f"   {path}")
    answer = input("   允許讀取嗎？[y/N]：").strip().lower()
    return answer in ("y", "yes")

# ══════════════════════════════════════════════════════════
#  Harness 1/3：可觀測性（Observability）— 結構化 log
# ══════════════════════════════════════════════════════════

def log_event(event_type: str, data: dict):
    """把每個關鍵事件（使用者輸入、工具呼叫、防護欄動作、最終回覆）
    以 JSON Lines 格式寫進 agent.log，方便事後追蹤 agent 到底做了什麼。"""
    entry = {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "event": event_type,
        **data,
    }
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # log 寫失敗不該讓整個 agent 掛掉

def show_recent_log(n: int = 20):
    if not os.path.isfile(LOG_PATH):
        print("目前還沒有任何 log 紀錄。\n")
        return
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()[-n:]
    print(f"── 最近 {len(lines)} 筆 log ──")
    for line in lines:
        try:
            entry = json.loads(line)
            print(f"[{entry.get('time')}] {entry.get('event')}: "
                  f"{ {k: v for k, v in entry.items() if k not in ('time', 'event')} }")
        except Exception:
            print(line.rstrip())
    print()

# ══════════════════════════════════════════════════════════
#  Harness 2/3：防護欄（Guardrails）— 危險指令攔截 / 需確認清單
# ══════════════════════════════════════════════════════════

# 完全阻擋、不給模型任何重試機會的高危險指令樣式
BLOCKED_PATTERNS = [
    r"rm\s+-rf\s+/(\s|$)",          # rm -rf /
    r"rm\s+-rf\s+~",                # rm -rf ~
    r":\(\)\{.*\};\s*:",            # fork bomb :(){ :|:& };:
    r"\bmkfs\b",                    # 格式化磁碟
    r"\bdd\s+if=.*of=/dev/",        # 直接寫入裝置
    r">\s*/dev/sd[a-z]",            # 覆寫硬碟裝置
    r"chmod\s+-R\s+777\s+/(\s|$)",  # 全系統開權限
    r"\bsudo\b",                    # 提權指令一律阻擋
    r"curl[^|]*\|\s*(sh|bash)\b",   # curl ... | sh（下載即執行）
    r"wget[^|]*\|\s*(sh|bash)\b",   # wget ... | sh
]

# 敏感路徑：涉及這些目錄的指令一律視為危險
SENSITIVE_PATHS = [
    r"/etc(/|\s|$)", r"/System(/|\s|$)", r"/Library(/|\s|$)",
    r"/root(/|\s|$)", r"~/\.ssh", r"C:\\Windows",
]

# 需要使用者互動確認才能執行的指令樣式（比較危險，但不到直接阻擋）
CONFIRM_PATTERNS = [
    r"\brm\s+-rf?\b",     # 刪除檔案/目錄
    r"\bmv\b",            # 搬移／覆蓋檔案
    r"\bgit\s+push\b.*--force",  # 強制推送
    r"\bgit\s+reset\s+--hard\b",
    r">>?\s*/",           # 寫入 / 覆蓋檔案（重導向）
]

def check_command_safety(command: str) -> tuple[str, str]:
    """回傳 (status, reason)，status ∈ {"blocked", "confirm", "ok"}"""
    for pattern in BLOCKED_PATTERNS + SENSITIVE_PATHS:
        if re.search(pattern, command, re.IGNORECASE):
            return "blocked", f"符合高危險樣式：{pattern}"

    for pattern in CONFIRM_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "confirm", f"符合需確認樣式：{pattern}"

    return "ok", ""

def ask_user_confirm(command: str) -> bool:
    print(f"\n{YELLOW}⚠️  Agent 想執行以下指令，可能有風險：{RESET}")
    print(f"   {command}")
    answer = input("   允許執行嗎？[y/N]：").strip().lower()
    return answer in ("y", "yes")

# ══════════════════════════════════════════════════════════
#  Tool Definitions（Ollama 原生 function calling 格式）
# ══════════════════════════════════════════════════════════

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "讀取一個文字檔案的內容。工作區內的檔案直接讀取；"
                           "工作區外的檔案需要使用者手動同意才會讀取。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑（相對或絕對）"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "把內容寫入一個文字檔案（會覆蓋原內容）。"
                           "只允許寫入工作區內的路徑，工作區外一律阻擋。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "檔案路徑（相對或絕對）"},
                    "content": {"type": "string", "description": "要寫入的完整內容"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "列出一個資料夾底下的檔案與子資料夾。工作區內直接列出；"
                           "工作區外需要使用者手動同意。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "資料夾路徑，預設為目前工作區"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "在使用者的電腦上執行一段 shell 指令，回傳 stdout 與 stderr。"
                           "檔案操作請優先用 read_file / write_file / list_dir，"
                           "這個工具留給需要跑程式或指令列工具的情境。"
                           "危險指令會被系統阻擋，部分敏感指令需要使用者手動確認。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要執行的 shell 指令",
                    }
                },
                "required": ["command"],
            },
        },
    },
]

def truncate_output(text: str) -> str:
    if len(text) <= MAX_TOOL_OUTPUT_CHARS:
        return text
    cut = text[:MAX_TOOL_OUTPUT_CHARS]
    return cut + f"\n...(輸出過長，已截斷。原始長度 {len(text)} 字元)"

# ─── 結構化檔案工具（有明確邊界檢查，比 run_shell 更安全） ───

def read_file_tool(path: str) -> str:
    abs_path, inside = resolve_path(path)

    if not inside:
        if not ask_user_confirm_read(abs_path):
            print(f"{YELLOW}已拒絕讀取。{RESET}\n")
            log_event("guardrail_read_rejected", {"path": abs_path})
            return "（使用者拒絕讀取此路徑，未執行）"
        log_event("guardrail_read_confirmed", {"path": abs_path})

    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return f"讀取失敗：{e}"

    content = truncate_output(content)
    print(f"\n📖 讀取：{abs_path}（{len(content)} 字元）\n")
    log_event("tool_call", {"tool": "read_file", "path": abs_path})
    return content

def write_file_tool(path: str, content: str) -> str:
    abs_path, inside = resolve_path(path)

    if not inside:
        print(f"\n{RED}🛑 已阻擋寫入：{abs_path}（工作區外一律禁止寫入）{RESET}\n")
        log_event("guardrail_write_blocked", {"path": abs_path})
        return f"（寫入被阻擋：{abs_path} 不在工作區內，一律禁止寫入。）"

    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return f"寫入失敗：{e}"

    print(f"\n✍️  已寫入：{abs_path}（{len(content)} 字元）\n")
    log_event("tool_call", {"tool": "write_file", "path": abs_path, "length": len(content)})
    return f"已成功寫入 {abs_path}（{len(content)} 字元）"

def list_dir_tool(path: str = ".") -> str:
    abs_path, inside = resolve_path(path)

    if not inside:
        if not ask_user_confirm_read(abs_path):
            print(f"{YELLOW}已拒絕讀取。{RESET}\n")
            log_event("guardrail_read_rejected", {"path": abs_path})
            return "（使用者拒絕讀取此路徑，未執行）"
        log_event("guardrail_read_confirmed", {"path": abs_path})

    try:
        items = sorted(os.listdir(abs_path))
    except Exception as e:
        return f"讀取失敗：{e}"

    listing = "\n".join(items) if items else "（空資料夾）"
    print(f"\n📂 列出：{abs_path}\n")
    log_event("tool_call", {"tool": "list_dir", "path": abs_path})
    return listing

def run_shell(command: str) -> str:
    """實際執行 shell 指令的工具實作。經過 guardrail 檢查後才真正執行。
    注意：這裡的路徑黑名單只是盡力而為的第二道防線，不是真正的沙箱——
    真正的邊界保護在 read_file / write_file / list_dir 這三個結構化工具上。"""
    status, reason = check_command_safety(command)

    if status == "blocked":
        print(f"\n{RED}🛑 已阻擋指令：{command}\n   原因：{reason}{RESET}\n")
        log_event("guardrail_blocked", {"command": command, "reason": reason})
        return f"（此指令已被系統安全機制阻擋，未執行。原因：{reason}）"

    if status == "confirm":
        if not ask_user_confirm(command):
            print(f"{YELLOW}已取消執行。{RESET}\n")
            log_event("guardrail_rejected_by_user", {"command": command, "reason": reason})
            return "（使用者拒絕執行此指令，未執行。）"
        log_event("guardrail_confirmed_by_user", {"command": command, "reason": reason})

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=SHELL_TIMEOUT, cwd=WORKSPACE,
        )
        output = (result.stdout + result.stderr).strip() or "（無輸出）"
    except subprocess.TimeoutExpired:
        output = f"（指令逾時 {SHELL_TIMEOUT} 秒，已強制中止）"
    except Exception as e:
        output = f"執行錯誤：{e}"

    output = truncate_output(output)
    print(f"\n⚙️  執行：{command}\n   結果：{output}\n")
    log_event("tool_call", {"tool": "run_shell", "command": command, "output": output})
    return output

TOOL_IMPLS = {
    "read_file": lambda args: read_file_tool(args.get("path", ".")),
    "write_file": lambda args: write_file_tool(args.get("path", ""), args.get("content", "")),
    "list_dir": lambda args: list_dir_tool(args.get("path", ".")),
    "run_shell": lambda args: run_shell(args.get("command", "")),
}

# ─── Image Input ───

def encode_image(path: str) -> str:
    """讀取圖片檔案並轉成 base64 字串，供 Ollama 的 images 欄位使用。"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ─── Ollama API（streaming + thinking 顯示 + tool_calls） ───

async def call_ollama(messages: list) -> dict:
    """呼叫 /api/chat（串流），回傳 {"content": str, "tool_calls": list | None}"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "think": True,
        "tools": TOOLS,
    }

    content = ""
    tool_calls = None
    in_thinking = False
    thinking_closed = False

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            async for line in resp.content:
                if not line.strip():
                    continue
                chunk = json.loads(line)
                msg = chunk.get("message", {})

                thinking_piece = msg.get("thinking", "")
                content_piece = msg.get("content", "")

                if thinking_piece:
                    if not in_thinking:
                        print(GRAY + ">> ", end="", flush=True)
                        in_thinking = True
                    print(thinking_piece.replace("\n", "\n>> "), end="", flush=True)

                if content_piece:
                    if in_thinking and not thinking_closed:
                        print(RESET)
                        thinking_closed = True
                    print(content_piece, end="", flush=True)
                    content += content_piece

                if msg.get("tool_calls"):
                    tool_calls = msg["tool_calls"]

                if chunk.get("done"):
                    if in_thinking and not thinking_closed:
                        print(RESET)
                    if content_piece or content:
                        print()

    return {"content": content.strip(), "tool_calls": tool_calls}

# ─── Agent Loop（單輪 + 有上限的工具呼叫，尚無自動重試/驗證） ───

def trim_history(messages: list) -> list:
    system_msg = messages[0]
    rest = messages[1:]
    if len(rest) > HISTORY_MESSAGES:
        rest = rest[-HISTORY_MESSAGES:]
    return [system_msg] + rest

def handle_turn(messages: list, user_input: str, images: list | None = None) -> str:
    user_msg = {"role": "user", "content": user_input}
    if images:
        user_msg["images"] = images
    messages.append(user_msg)
    log_event("user_input", {"content": user_input, "has_image": bool(images)})

    final_answer = ""
    for turn in range(MAX_TOOL_TURNS):
        result = asyncio.run(call_ollama(messages))

        if result["tool_calls"]:
            messages.append({
                "role": "assistant",
                "content": result["content"],
                "tool_calls": result["tool_calls"],
            })
            for call in result["tool_calls"]:
                fn = call.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
                log_event("tool_call_requested", {"tool": name, "arguments": args})
                impl = TOOL_IMPLS.get(name)
                output = impl(args) if impl else f"未知工具：{name}"
                messages.append({
                    "role": "tool",
                    "content": output,
                    "name": name,
                })
            continue

        final_answer = result["content"]
        break
    else:
        final_answer = f"（已達最多 {MAX_TOOL_TURNS} 輪工具呼叫，先在此停止。）"
        log_event("max_turns_reached", {"max_turns": MAX_TOOL_TURNS})

    if final_answer:
        messages.append({"role": "assistant", "content": final_answer})
    log_event("final_answer", {"content": final_answer})
    return final_answer

def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"Agent - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print(f"Log：{LOG_PATH}")
    print("指令：/quit 結束、/clear 清空對話歷史、"
          "/img <圖片路徑> [問題] 讓模型看圖、/log 查看最近紀錄\n")

    while True:
        try:
            user_input = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("/quit", "/exit", "/q"):
            print("再見！")
            break
        if user_input.lower() == "/clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("對話歷史已清空。\n")
            continue
        if user_input.lower() == "/log":
            show_recent_log()
            continue

        if user_input.startswith("/img"):
            parts = user_input[len("/img"):].strip().split(maxsplit=1)
            if not parts:
                print("用法：/img <圖片路徑> [問題]\n")
                continue

            image_path = os.path.expanduser(parts[0])
            question = parts[1] if len(parts) > 1 else "請描述這張圖片的內容。"

            if not os.path.isfile(image_path):
                print(f"找不到圖片檔案：{image_path}\n")
                continue

            try:
                image_b64 = encode_image(image_path)
            except Exception as e:
                print(f"讀取圖片失敗：{e}\n")
                continue

            answer = handle_turn(messages, question, images=[image_b64])
        else:
            answer = handle_turn(messages, user_input)

        if not answer:
            print("🤖 （沒有取得回覆內容）\n")
        messages = trim_history(messages)

if __name__ == "__main__":
    main()