#!/usr/bin/env python3
# agent2context.py - agent1 的 context engineering 版本
# Run: python agent2context.py
#
# 設計重點（相對於 agent1prompt.py）：
#   1. 把「上下文如何組裝」抽成一個 ContextBuilder 類別，集中管理：
#      - 動態系統提示（runtime / workspace / model / 工具政策）
#      - 工具 schema 的撰寫（作為工具脈絡一次餵給模型）
#      - 歷史訊息的管理（token 感知 + 舊訊息摘要，而非直接丟棄）
#   2. 保持 Ollama 原生 tools / tool_calls 機制，工具迴圈邏輯與 agent1 相同。
#   3. 新增 /ctx 指令，讓使用者查看目前組裝出來的完整上下文。

import asyncio
import aiohttp
import json
import os
import subprocess
import sys
import time
from datetime import datetime

# ─── Configuration ───

#MODEL = "qwen3.5:4b"
MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()  # 使用執行當下所在的資料夾
MAX_TOOL_TURNS = 5      # 一次任務最多允許幾輪工具呼叫
HISTORY_MESSAGES = 12   # 對話歷史最多保留幾則訊息（不含 system）
TOKEN_BUDGET = 4096     # context 的 token 預算（粗略估算用）
SHELL_TIMEOUT = 30      # 單一 shell 指令逾時秒數

GRAY = "\033[90m"
RESET = "\033[0m"

# ─── Context Builder（context engineering 核心） ───

class ContextBuilder:
    """負責組裝與管理送給模型的完整上下文。

    這是 agent2 的核心：把系統提示、工具 schema、歷史管理
    全部集中在這裡，讓模型在每個 turn 都能拿到一致的、動態且
    足夠完整的脈絡。新增工具或調整提示，只需改這裡。
    """

    def __init__(self, model: str, workspace: str):
        self.model = model
        self.workspace = workspace

    # ── 動態系統提示 ──

    def dynamic_facts(self) -> str:
        """每次呼叫都會重新產生的動態環境事實，避免系統提示過時。"""
        now = datetime.now()
        return (
            f"目前時間：{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Python：{sys.version.split()[0]}\n"
            f"模型：{self.model}"
        )

    def role_frame(self) -> str:
        """模型的角色 / 任務框架（身份、最高指導原則）。"""
        return (
            "你是 Jarvis，一個運行在使用者電腦上的 AI 助理。\n"
            "你的目標是在最小化誤解的前提下，準確地幫助使用者完成任務。\n"
            "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。\n"
            "只有在真的需要操作檔案、查詢系統資訊、執行程式時，才呼叫 run_shell 工具。"
        )

    def tool_policy(self) -> str:
        """工具使用政策：何時 / 如何用工具、以及安全限制。"""
        return (
            "工具使用規則：\n"
            "  - 每個工具呼叫前，先想清楚它符合哪一個工具描述，再填參數。\n"
            "  - 一次可以同時發出多個彼此獨立的工具呼叫，減少往返。\n"
            "  - 工具回傳後，根據結果決定下一步；若結果已足夠，就直接給最終答案，不要重複呼叫。\n"
            "  - 安全限制：禁止使用不會自動結束的指令（如 tail -f、持續監聽的伺服器、無限迴圈）。"
        )

    def output_contract(self) -> str:
        """輸出契約：格式與語氣規範。"""
        return (
            "輸出規範：\n"
            "  - 用繁體中文回答。\n"
            "  - 程式碼、指令、路徑用程式碼區塊標示。\n"
            "  - 執行結果直接陳述事實，不要誇大或腦補。"
        )

    def build_system_prompt(self) -> str:
        """把角色框架 + 動態事實 + 工具政策 + 輸出契約組合成系統提示。"""
        return "\n\n".join([
            self.role_frame(),
            "── 當前環境 ──\n" + self.dynamic_facts(),
            "── 工具政策 ──\n" + self.tool_policy(),
            "── 輸出規範 ──\n" + self.output_contract(),
        ])

    # ── 工具 schema（作為工具脈絡） ──

    def tool_schemas(self) -> list:
        """Ollama 原生 function calling 格式的工具定義。"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "run_shell",
                    "description": "在使用者的電腦上執行一段 shell 指令，回傳 stdout 與 stderr。"
                                   "適用於：建立/讀取/編輯檔案、查詢系統資訊、執行程式、安裝套件。"
                                   "請把完整指令寫在 command 欄位。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要執行的完整 shell 指令（例如 python hello.py）",
                            }
                        },
                        "required": ["command"],
                    },
                },
            }
        ]

    # ── 歷史管理 ──

    def estimate_tokens(self, text: str) -> int:
        """粗略估算 token 數（中文約一字一 token，其餘略估）。"""
        return max(1, len(text) // 2)

    def manage_history(self, messages: list) -> list:
        """管理歷史訊息：保留前綴（system）與後半段，超過 token 預算就，
        把過舊的非 system 訊息摘要成一段，避免直接無腦丟棄。

        messages[0] 是 system 提示，其餘是 user/assistant/tool 混雜。
        """
        if not messages:
            return messages

        system_msg = messages[0]
        rest = messages[1:]

        # 先依數量上限修剪
        if len(rest) > HISTORY_MESSAGES:
            rest = rest[-HISTORY_MESSAGES:]

        # 再依 token 預算修剪：若仍超預算，把那之前的部分收斂成摘要
        total = self.estimate_tokens(system_msg.get("content", ""))
        kept = []
        for m in rest:
            total += self.estimate_tokens(m.get("content", ""))
            if total > TOKEN_BUDGET:
                break
            kept.append(m)

        if len(kept) < len(rest):
            # 超過預算：把放不下的部分合併成一則「先前的對話摘要」
            dropped = rest[: len(rest) - len(kept)]
            summary = "（先前的對話摘要）" + " | ".join(
                f"{m.get('role')}: {m.get('content', '')[:80]}"
                for m in dropped if m.get("role") != "system"
            )
            kept = [{"role": "system", "content": summary}] + kept

        return [system_msg] + kept

    # ── 顯示目前上下文（/ctx 用） ──

    def debug_string(self, messages: list) -> str:
        lines = [
            "===== 組裝出的上下文 =====",
            f"模型: {self.model}",
            f"工作區: {self.workspace}",
            f"MAX_TOOL_TURNS: {MAX_TOOL_TURNS} | HISTORY_MESSAGES: {HISTORY_MESSAGES} | TOKEN_BUDGET: {TOKEN_BUDGET}",
            "",
            f"----- 系統提示 (約 {self.estimate_tokens(messages[0].get('content',''))} token) -----",
            messages[0].get("content", ""),
            "",
            f"----- 工具 schema ({len(self.tool_schemas())}) -----",
            json.dumps(self.tool_schemas(), ensure_ascii=False, indent=2),
            "",
            f"----- 歷史訊息 ({len(messages[1:])} 則) -----",
        ]
        for m in messages[1:]:
            content = str(m.get("content", ""))
            lines.append(f"[{m.get('role')}] {content[:200]}{'…' if len(content) > 200 else ''}")
        return "\n".join(lines)

# ─── Tool Implementations ───

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

async def call_ollama(messages: list, tools: list) -> dict:
    """呼叫 /api/chat（串流），回傳 {"content": str, "tool_calls": list | None}

    思考過程即時以灰色 + '>> ' 前綴印出；tool_calls 由 Ollama 完整送出（非逐字串流片段）。
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "think": True,
        "tools": tools,
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

def handle_turn(messages: list, user_input: str, ctx: ContextBuilder) -> str:
    messages.append({"role": "user", "content": user_input})

    final_answer = ""
    for turn in range(MAX_TOOL_TURNS):
        result = asyncio.run(call_ollama(messages, ctx.tool_schemas()))

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

    ctx = ContextBuilder(MODEL, WORKSPACE)
    messages = [{"role": "system", "content": ctx.build_system_prompt()}]

    print(f"Agent (context) - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print("指令：/quit 結束、/clear 清空對話歷史、/ctx 檢視目前上下文\n")

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
            messages = [{"role": "system", "content": ctx.build_system_prompt()}]
            print("對話歷史已清空。\n")
            continue
        if user_input.lower() == "/ctx":
            print(ctx.debug_string(messages))
            continue

        answer = handle_turn(messages, user_input, ctx)
        if not answer:
            # 保險：正常情況不該發生，但避免完全沒輸出
            print("🤖 （沒有取得回覆內容）\n")
        messages = ctx.manage_history(messages)

if __name__ == "__main__":
    main()
