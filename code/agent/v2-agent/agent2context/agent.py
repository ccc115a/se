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
#   4. 【新增】三層長期記憶（見 memory_manager.py）：
#        - AGENT.md：長期記憶檔，每次啟動整份載入 system prompt。
#        - skills/ ：技能庫，依關鍵字比對後才注入當回合 prompt。
#        - RAG     ：用 embedding 把每輪對話存成向量，之後自動語意檢索，
#                     並開放 recall_memory / remember_fact 兩個工具。

import asyncio
import aiohttp
import json
import os
import subprocess

import memory_manager

# ─── Configuration ───

#MODEL = "qwen3.5:4b"
MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()  # 使用執行 python agent.py 當下所在的資料夾
MAX_TOOL_TURNS = 5      # 一次任務最多允許幾輪工具呼叫
HISTORY_MESSAGES = 12   # 對話歷史最多保留幾則訊息（不含 system）
SHELL_TIMEOUT = 30      # 單一 shell 指令逾時秒數

GRAY = "\033[90m"
RESET = "\033[0m"

BASE_SYSTEM_PROMPT = (
    "你是 Jarvis，一個運行在使用者電腦上的 AI 助理，擁有長期記憶。\n"
    "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。\n"
    "只有在真的需要操作檔案、查詢系統資訊、執行程式時，才呼叫 run_shell 工具。\n"
    "避免使用不會自動結束的指令（例如 tail -f、持續監聽的伺服器）。\n"
    "\n"
    "你有以下記憶相關能力：\n"
    "- 使用者訊息前面有時會附上『[背景資訊]』區塊，裡面是系統自動從長期記憶\n"
    "  （過去對話、技能說明）檢索出的相關內容，僅供參考，不必在回覆中提及這是\n"
    "  系統自動附加的，也不需要逐字重複。\n"
    "- 當使用者明確要求「記住」某件事、或講出重要的個人偏好／事實時，呼叫\n"
    "  remember_fact 工具把它寫進 AGENT.md，之後每次啟動都會記得。\n"
    "- 如果背景資訊不夠、但你覺得過去可能討論過相關內容，可以呼叫 recall_memory\n"
    "  工具主動搜尋。"
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
    },
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": (
                "把重要的事實或使用者偏好永久記錄到 AGENT.md，之後每次啟動都會自動載入。"
                "適合用在使用者明確要求「記住」某件事，或透露了重要的個人偏好／背景資訊時。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "要記住的事實，用簡短的一句話描述",
                    }
                },
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "在長期記憶（過去的對話紀錄）中做語意搜尋，回傳最相關的幾筆內容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要搜尋的關鍵字或問題",
                    }
                },
                "required": ["query"],
            },
        },
    },
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


def remember_fact(fact: str) -> str:
    """把事實寫進 AGENT.md，下次啟動就會自動出現在 system prompt。"""
    fact = (fact or "").strip()
    if not fact:
        return "沒有收到要記住的內容。"
    memory_manager.append_agent_md(fact)
    print(f"\n🧠 已寫入長期記憶（AGENT.md）：{fact}\n")
    return f"已將「{fact}」寫入 AGENT.md 長期記憶，之後每次啟動都會記得。"


def recall_memory(query: str) -> str:
    """主動在 RAG 記憶庫中搜尋，給模型自己判斷要不要用結果。"""
    query = (query or "").strip()
    if not query:
        return "沒有收到要搜尋的內容。"
    hits = asyncio.run(memory_manager.search_memory(query))
    if not hits:
        return "沒有找到相關的歷史記憶。"
    lines = [f"- ({role}) {text}" for _sim, role, text, _ts in hits]
    print(f"\n🔎 recall_memory({query!r}) 找到 {len(hits)} 筆\n")
    return "找到以下相關記憶：\n" + "\n".join(lines)


# 工具名稱 → 實作函式 的對照表，之後新增工具只要在這裡註冊即可
TOOL_IMPLS = {
    "run_shell": lambda args: run_shell(args.get("command", "")),
    "remember_fact": lambda args: remember_fact(args.get("fact", "")),
    "recall_memory": lambda args: recall_memory(args.get("query", "")),
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


# ─── 記憶相關輔助函式 ───

def build_system_message() -> dict:
    """組出這次執行期間固定使用的 system 訊息：基本人設 + AGENT.md 全文。"""
    agent_md = memory_manager.load_agent_md()
    text = (
        BASE_SYSTEM_PROMPT
        + "\n\n---\n"
        + "# 使用者長期記憶（AGENT.md，每次啟動自動載入）\n"
        + agent_md
    )
    return {"role": "system", "content": text}


async def build_turn_context(user_input: str, skills: list) -> str:
    """幫這一回合組『背景資訊』：命中的技能 + RAG 檢索到的相關記憶。"""
    parts = []

    matched = memory_manager.match_skills(user_input, skills)
    for sk in matched:
        parts.append(f"[技能：{sk['name']}]\n{sk['body']}")

    hits = await memory_manager.search_memory(user_input)
    if hits:
        recalled = "\n".join(f"- ({role}) {text}" for _sim, role, text, _ts in hits)
        parts.append(f"[可能相關的歷史記憶]\n{recalled}")

    return "\n\n".join(parts)


# ─── Agent Loop ───

def trim_history(messages: list) -> list:
    """保留 system 訊息 + 最近 HISTORY_MESSAGES 則，避免 context 無限增長。"""
    system_msg = messages[0]
    rest = messages[1:]
    if len(rest) > HISTORY_MESSAGES:
        rest = rest[-HISTORY_MESSAGES:]
    return [system_msg] + rest


def handle_turn(messages: list, user_input: str, skills: list) -> str:
    # 先把「原始」使用者訊息放進歷史，之後會把 API 呼叫用的版本暫時替換掉，
    # 回合結束後再換回原始版本，避免每次 trim_history 時，記憶檢索的雜訊被永久保留。
    messages.append({"role": "user", "content": user_input})
    user_msg_index = len(messages) - 1

    context_text = asyncio.run(build_turn_context(user_input, skills))
    if context_text:
        messages[user_msg_index]["content"] = (
            f"[背景資訊，系統自動附加，僅供參考]\n{context_text}\n\n"
            f"[使用者訊息]\n{user_input}"
        )

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

    # 回合結束：把使用者訊息換回原始文字，避免背景資訊在歷史裡越滾越大
    messages[user_msg_index]["content"] = user_input

    if final_answer:
        messages.append({"role": "assistant", "content": final_answer})

    # 把這一輪的使用者訊息／模型回覆存進 RAG，供之後的對話檢索
    asyncio.run(memory_manager.add_memory("user", user_input))
    if final_answer:
        asyncio.run(memory_manager.add_memory("assistant", final_answer))

    return final_answer


def main():
    os.makedirs(WORKSPACE, exist_ok=True)
    memory_manager.ensure_memory_dirs()

    skills = memory_manager.load_skills()
    messages = [build_system_message()]

    print(f"Agent - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print(f"記憶目錄：{memory_manager.MEMORY_DIR}")
    print("指令：/quit 結束、/clear 清空對話歷史、/memory 顯示記憶狀態、"
          "/remember <內容> 手動記一筆、/skills 重新載入技能庫\n")

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
            messages = [build_system_message()]
            print("對話歷史已清空（AGENT.md 長期記憶不受影響）。\n")
            continue
        if user_input.lower() == "/memory":
            print(memory_manager.memory_stats() + "\n")
            continue
        if user_input.lower() == "/skills":
            skills = memory_manager.load_skills()
            names = ", ".join(s["name"] for s in skills) or "（無）"
            print(f"已重新載入技能庫：{names}\n")
            continue
        if user_input.lower().startswith("/remember "):
            fact = user_input[len("/remember "):].strip()
            print(remember_fact(fact) + "\n")
            continue

        answer = handle_turn(messages, user_input, skills)
        if not answer:
            # 保險：正常情況不該發生，但避免完全沒輸出
            print("🤖 （沒有取得回覆內容）\n")
        messages = trim_history(messages)


if __name__ == "__main__":
    main()
