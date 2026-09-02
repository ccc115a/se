#!/usr/bin/env python3
# agent0.py - AI Agent with memory, tool feedback, and streaming thinking display
# Run: python agent0.py

import subprocess
import os
import asyncio
import aiohttp
import json
import re

# ─── Configuration ───

WORKSPACE = os.path.expanduser("~/.agent0")
MODEL = "qwen3.5:2b"
MAX_TOOL_TURNS = 5       # 單次任務內，最多允許幾輪 shell 呼叫
HISTORY_TURNS = 5        # 對話歷史最多保留幾輪（user+assistant 算一輪）
SHELL_TIMEOUT = 30       # 單一 shell 指令逾時秒數

GRAY = "\033[90m"
RESET = "\033[0m"

SYSTEM_PROMPT = """你是 Jarvis，一個有用的 AI 助理。

規則：
1. 一般聊天、問答、閒聊，請直接用自然語言回答，完全不要使用 <shell> 標籤。
2. 只有在真的需要查詢檔案、系統資訊、執行運算等情況，才使用 <shell>指令</shell>。
3. 每次回覆最後，如果不需要再執行更多指令，請輸出 <end/>。
4. 避免使用會卡住不會結束的指令（例如 tail -f、持續監聽的程式）。
5. <shell> 標籤內只能放你要執行的指令，不要輸出假的使用者對話。"""

# ─── Memory ───

conversation_history = []  # [{"role": "user"/"assistant", "content": "..."}]
key_info = []               # 長期記憶（字串列表）

# ─── Ollama API (streaming chat + thinking display) ───

async def call_ollama(messages: list, show_thinking: bool = True) -> str:
    """呼叫 /api/chat，串流輸出。思考過程用灰色 + '>> ' 前綴即時印出，回傳正式回答文字。"""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "think": True,
    }

    full_content = ""
    in_thinking = False
    thinking_closed = False

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            async for line in resp.content:
                if not line.strip():
                    continue
                chunk = json.loads(line)
                msg = chunk.get("message", {})

                thinking_piece = msg.get("thinking", "")
                content_piece = msg.get("content", "")

                if thinking_piece and show_thinking:
                    if not in_thinking:
                        print(GRAY + ">> ", end="", flush=True)
                        in_thinking = True
                    print(thinking_piece.replace("\n", "\n>> "), end="", flush=True)

                if content_piece:
                    if in_thinking and not thinking_closed:
                        print(RESET)
                        thinking_closed = True
                    full_content += content_piece

                if chunk.get("done"):
                    if in_thinking and not thinking_closed:
                        print(RESET)

    return full_content.strip()

# ─── Memory Management ───

def build_messages(user_input: str) -> list:
    """組出送給 LLM 的完整 messages 陣列：system(+記憶) + 歷史 + 這次的使用者輸入"""
    system_content = SYSTEM_PROMPT
    if key_info:
        memory_text = "\n".join(f"- {item}" for item in key_info)
        system_content += f"\n\n【你記得的關鍵資訊】\n{memory_text}"

    messages = [{"role": "system", "content": system_content}]
    messages.extend(conversation_history[-HISTORY_TURNS * 2:])
    messages.append({"role": "user", "content": user_input})
    return messages

def update_memory(user_input: str, assistant_response: str):
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": assistant_response})
    while len(conversation_history) > HISTORY_TURNS * 2:
        conversation_history.pop(0)

async def extract_key_info(user_input: str, assistant_response: str):
    """背景任務：從對話中萃取值得長期記住的資訊（不顯示思考過程）"""
    extract_messages = [
        {"role": "system", "content": "你負責從對話中萃取值得長期記住的關鍵資訊，最多 2 項，"
                                       "只用以下格式回覆，沒有就輸出空的 <memory></memory>：\n"
                                       "<memory>\n  <item>...</item>\n</memory>"},
        {"role": "user", "content": f"<user>{user_input}</user>\n<assistant>{assistant_response}</assistant>"},
    ]
    try:
        result = await call_ollama(extract_messages, show_thinking=False)
        for item in re.findall(r"<item>(.*?)</item>", result, re.DOTALL):
            item = item.strip()
            if item and item not in key_info:
                key_info.append(item)
    except Exception:
        pass

# ─── Tool Execution ───

def run_shell(cmd: str) -> str:
    cmd = cmd.strip()
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=SHELL_TIMEOUT, cwd=os.getcwd()
        )
        output = (result.stdout + result.stderr).strip() or "（無輸出）"
    except subprocess.TimeoutExpired:
        output = f"（指令逾時 {SHELL_TIMEOUT} 秒，已強制中止）"
    except Exception as e:
        output = f"錯誤：{e}"

    print(f"\n=== 執行命令 ===\n{cmd}\n\n結果：{output}\n")
    return f"$ {cmd}\n{output}"

def strip_tags(text: str) -> str:
    """把 <shell>...</shell> 和 <end/> 從最終顯示的回覆中拿掉，只留自然語言部分"""
    text = re.sub(r"<shell>.*?</shell>", "", text, flags=re.DOTALL)
    text = text.replace("<end/>", "")
    return text.strip()

# ─── Main Agent Loop ───

def handle_user_turn(user_input: str):
    messages = build_messages(user_input)
    current_response = asyncio.run(call_ollama(messages))

    tool_outputs = []

    for turn in range(MAX_TOOL_TURNS):
        shell_cmds = re.findall(r"<shell>(.+?)</shell>", current_response, re.DOTALL)
        if not shell_cmds or "<end/>" in current_response:
            break

        for cmd in shell_cmds:
            tool_outputs.append(run_shell(cmd))

        messages.append({"role": "assistant", "content": current_response})
        messages.append({
            "role": "user",
            "content": "指令執行結果：\n" + "\n".join(tool_outputs[-len(shell_cmds):]) +
                       "\n\n如果不需要更多指令，請直接輸出 <end/>。"
        })
        current_response = asyncio.run(call_ollama(messages))
    else:
        print(f"（已達最多 {MAX_TOOL_TURNS} 輪工具呼叫，強制停止）")

    final_text = strip_tags(current_response)
    print(f"\n🤖 {final_text}\n")

    update_memory(user_input, final_text)
    if tool_outputs:
        asyncio.run(extract_key_info(user_input, final_text))

def main():
    os.makedirs(WORKSPACE, exist_ok=True)

    print(f"Agent0 - {MODEL}（含記憶功能）")
    print(f"工作區：{WORKSPACE}")
    print("指令：/quit、/memory（顯示關鍵資訊）\n")

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
        if user_input.lower() == "/memory":
            print(f"關鍵資訊：{key_info}")
            continue

        handle_user_turn(user_input)

if __name__ == "__main__":
    main()