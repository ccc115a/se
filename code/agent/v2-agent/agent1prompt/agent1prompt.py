#!/usr/bin/env python3
# agent.py - AI Agent using Ollama native function calling (qwen3.5:4b)
# Run: python agent.py
#
# 設計重點（與舊版最大差異）：
#   1. 不再用 <shell>...</shell> 這種自訂 XML 標籤讓模型「用文字模擬呼叫工具」，
#      改用 Ollama 原生的 tools / tool_calls 機制——模型要呼叫工具時，
#      回傳的是結構化 JSON（message.tool_calls），不需要用 regex 去猜、去解析，
#      也不會有模型自己接續生成假對話的問題。
#   2. 工具迴圈有明確上限（MAX_TOOL_TURNS），並在每輪都印出進度。
#   3. 思考過程（thinking）用淡灰色 + ">> " 前綴即時串流印出。

import asyncio
import aiohttp
import json
import os
import subprocess

# ─── Configuration ───

#MODEL = "qwen3.5:4b"
MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()  # 使用執行 python agent.py 當下所在的資料夾
MAX_TOOL_TURNS = 5      # 一次任務最多允許幾輪工具呼叫
HISTORY_MESSAGES = 12   # 對話歷史最多保留幾則訊息（不含 system）
SHELL_TIMEOUT = 30      # 單一 shell 指令逾時秒數

GRAY = "\033[90m"
RESET = "\033[0m"

SYSTEM_PROMPT = (
    "你是 Jarvis，一個運行在使用者電腦上的 AI 助理。\n"
    "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。\n"
    "只有在真的需要操作檔案、查詢系統資訊、執行程式時，才呼叫 run_shell 工具。\n"
    "避免使用不會自動結束的指令（例如 tail -f、持續監聽的伺服器）。"
)

# ─── Tool Definitions（Ollama 原生 function calling 格式） ───

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "在使用者的電腦上執行一段 shell 指令，回傳 stdout 與 stderr。",
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
    }
]

def run_shell(command: str) -> str:
    """實際執行 shell 指令的工具實作，回傳可以直接餵回模型的文字結果。"""
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

    print(f"\n⚙️  執行：{command}\n   結果：{output}\n")
    return output

# 工具名稱 → 實作函式 的對照表，之後新增工具只要在這裡註冊即可
TOOL_IMPLS = {
    "run_shell": lambda args: run_shell(args.get("command", "")),
}

# ─── Ollama API（streaming + thinking 顯示 + tool_calls） ───

async def call_ollama(messages: list) -> dict:
    """呼叫 /api/chat（串流），回傳 {"content": str, "tool_calls": list | None}

    思考過程即時以灰色 + '>> ' 前綴印出；tool_calls 由 Ollama 完整送出（非逐字串流片段）。
    """
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

# ─── Agent Loop ───

def trim_history(messages: list) -> list:
    """保留 system 訊息 + 最近 HISTORY_MESSAGES 則，避免 context 無限增長。"""
    system_msg = messages[0]
    rest = messages[1:]
    if len(rest) > HISTORY_MESSAGES:
        rest = rest[-HISTORY_MESSAGES:]
    return [system_msg] + rest

def handle_turn(messages: list, user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})

    final_answer = ""
    for turn in range(MAX_TOOL_TURNS):
        result = asyncio.run(call_ollama(messages))

        if result["tool_calls"]:
            # 把模型這輪的 assistant 訊息（含 tool_calls）加回歷史
            messages.append({
                "role": "assistant",
                "content": result["content"],
                "tool_calls": result["tool_calls"],
            })
            # 依序執行每個工具呼叫，並把結果以 role="tool" 加回歷史
            for call in result["tool_calls"]:
                fn = call.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
                impl = TOOL_IMPLS.get(name)
                output = impl(args) if impl else f"未知工具：{name}"
                messages.append({
                    "role": "tool",
                    "content": output,
                    "name": name,
                })
            continue  # 把工具結果送回去，讓模型決定下一步

        # 沒有 tool_calls，代表模型給出最終答案
        final_answer = result["content"]
        break
    else:
        final_answer = f"（已達最多 {MAX_TOOL_TURNS} 輪工具呼叫，先在此停止。）"

    if final_answer:
        messages.append({"role": "assistant", "content": final_answer})
    return final_answer

def main():
    os.makedirs(WORKSPACE, exist_ok=True)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"Agent - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print("指令：/quit 結束、/clear 清空對話歷史\n")

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

        answer = handle_turn(messages, user_input)
        if not answer:
            # 保險：正常情況不該發生，但避免完全沒輸出
            print("🤖 （沒有取得回覆內容）\n")
        messages = trim_history(messages)

if __name__ == "__main__":
    main()