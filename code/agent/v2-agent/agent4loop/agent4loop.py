#!/usr/bin/env python3
# agent4loop.py - agent1 的 loop engineering 版本
# Run: python agent4loop.py
#
# 設計重點（相對於 agent1prompt.py）：
#   1. 把「agent 主迴圈」抽成 SelfCorrectingLoop 類別，集中控管：
#      - 明確的回合狀態：模型呼叫 → 工具執行 → 失敗偵測 → 反思注入 → 重試或收束
#      - 自我修正：工具失敗時，把失敗紀錄加上反思提示送回模型，
#        讓模型分析原因並提出修正後的指令（或決定不再重試）
#      - 預算控管：MAX_TOOL_TURNS（工具回合數）與 MAX_REPLANS（反思重試次數）
#      - 回合逐字稿（turn transcript）：所有工具執行與反思都留下記錄
#   2. run_shell 改回傳結構化的 ToolOutcome（文字 + exit code + ok），
#      迴圈才能「知道」工具失敗，進而觸發反思。
#   3. 新增 /loop 指令，顯示目前迴圈的狀態與逐字稿。
#   4. 保留與 agent1 相同的 streaming / thinking 顯示與 Ollama 原生 tool_calls。

import asyncio
import aiohttp
import json
import os
import subprocess
import time
from dataclasses import dataclass, field

# ─── Configuration ───

#MODEL = "qwen3.5:4b"
MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()  # 使用執行當下所在的資料夾
MAX_TOOL_TURNS = 5      # 一次任務最多允許幾輪工具呼叫
MAX_REPLANS = 3         # 工具失敗後最多允許幾次「反思→重試」
HISTORY_MESSAGES = 12   # 對話歷史最多保留幾則訊息（不含 system）
SHELL_TIMEOUT = 30      # 單一 shell 指令逾時秒數

GRAY = "\033[90m"
RESET = "\033[0m"

# ─── Tool Outcome（結構化執行結果） ───

@dataclass
class ToolOutcome:
    """一次工具執行的結構化結果。

    迴圈依賴 .ok 判斷是否失敗；text 是餵回模型看的文字。
    """
    text: str
    ok: bool
    exit_code: int | None = None
    reason: str = ""
    command: str = ""
    duration_ms: int = 0

# ─── 回合逐字稿記錄 ───

@dataclass
class TurnRecord:
    kind: str            # "tool" | "reflect" | "stop"
    detail: str
    ok: bool | None = None
    index: int = 0

# ─── Self-Correcting Loop（loop engineering 核心） ───

class SelfCorrectingLoop:
    """Agent 的主迴圈：模型呼叫 → 工具執行 → 失敗反思 → 重試或收束。

    這是 agent4 的核心：把 agent1 那個「無腦跑 MAX_TOOL_TURNS 圈」的 for 迴圈，
    升級成一個會自我修正的迴圈。工具失敗不會默默吞掉——
    失敗會被偵測、寫進逐字稿、並以反思提示送回模型，讓它修正後再試，
    同時用 MAX_REPLANS 防止無限鬼打牆。
    """

    def __init__(self, max_tool_turns: int = MAX_TOOL_TURNS,
                 max_replans: int = MAX_REPLANS):
        self.max_tool_turns = max_tool_turns
        self.max_replans = max_replans
        self.tool_rounds = 0
        self.replans = 0
        self.records: list[TurnRecord] = []
        self._next_index = 1

    # ── 反思提示 ──

    def reflection_prompt(self, failures: list[ToolOutcome], replan_used: int) -> str:
        detail = "\n".join(
            f"- 指令: {f.command or '(無)'}\n  結果: {f.text[:200]}"
            for f in failures
        )
        return (
            "上一輪的工具呼叫失敗了，請反思並修正。\n\n"
            f"失敗紀錄：\n{detail}\n\n"
            "規則：\n"
            f"1. 先分析失敗原因再動手。\n"
            f"2. 若要修正：直接呼叫 run_shell 執行修正後的指令（這已是第 {replan_used} 次重試，最多 {self.max_replans} 次）。\n"
            "3. 若判斷不需要重試，直接給出最終答案並說明限制；切勿重複相同的失敗指令。"
        )

    def give_up_message(self) -> str:
        return (
            "（上一輪工具失敗且已用盡重試機會。請直接給出最終答案，"
            "不要再呼叫工具，並說明無法完成的原因與限制。）"
        )

    # ── 逐字稿 ──

    def _record(self, kind: str, detail: str, ok: bool | None = None) -> TurnRecord:
        rec = TurnRecord(kind=kind, detail=detail, ok=ok, index=self._next_index)
        self._next_index += 1
        self.records.append(rec)
        return rec

    # ── 主迴圈 ──

    def run(self, messages: list, user_input: str,
            tools: list | None = None, tool_impls: dict | None = None,
            call_ollama_fn=None) -> str:
        """跑完整個工具迴圈，回傳最終答案文字。

        tool_impls / call_ollama_fn 可注入 fake，方便測試（不需要真的 Ollama）。
        """
        tools = tools or TOOLS
        impls = tool_impls or TOOL_IMPLS
        call_fn = call_ollama_fn or (lambda m, t: asyncio.run(call_ollama(m, t)))

        messages.append({"role": "user", "content": user_input})

        final_answer = ""
        while True:
            result = call_fn(messages, tools)

            # 沒有 tool_calls → 最終答案
            if not result["tool_calls"]:
                final_answer = result["content"]
                break

            # 有 tool_calls → 記錄並依序執行
            messages.append({
                "role": "assistant",
                "content": result.get("content", ""),
                "tool_calls": result["tool_calls"],
            })
            self.tool_rounds += 1
            failures: list[ToolOutcome] = []

            for call in result["tool_calls"]:
                fn = call.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
                impl = impls.get(name)
                if not impl:
                    outcome = ToolOutcome(text=f"未知工具：{name}", ok=False,
                                          command=name or "", reason="unknown tool")
                else:
                    outcome = impl(args)
                messages.append({"role": "tool", "content": outcome.text, "name": name})
                self._record(kind="tool", detail=outcome.command or name, ok=outcome.ok)
                if not outcome.ok:
                    failures.append(outcome)

            # 預算檢查：工具回合數用罄 → 收束
            if self.tool_rounds >= self.max_tool_turns:
                final_answer = f"（已達最多 {self.max_tool_turns} 輪工具呼叫，先在此停止。）"
                self._record(kind="stop", detail=final_answer)
                break

            # 失敗 → 反思 + 重試（在 MAX_REPLANS 內）
            if failures and self.replans < self.max_replans:
                self.replans += 1
                prompt = self.reflection_prompt(failures, self.replans)
                self._record(kind="reflect",
                             detail=f"注入反思提示（重試 {self.replans}/{self.max_replans}）",
                             ok=False)
                messages.append({"role": "user", "content": prompt})
                continue

            # 失敗但已用完重試 → 要求直接收束
            if failures:
                messages.append({"role": "user", "content": self.give_up_message()})
                continue

            # 全部成功 → 繼續下一輪

        if final_answer:
            messages.append({"role": "assistant", "content": final_answer})
        return final_answer

    # ── 顯示迴圈狀態（/loop 用） ──

    def describe(self) -> str:
        lines = [
            "===== Self-Correcting Loop 狀態 =====",
            f"工具回合: {self.tool_rounds}/{self.max_tool_turns}",
            f"反思重試: {self.replans}/{self.max_replans}",
            f"逐字稿 ({len(self.records)} 筆):",
        ]
        for r in self.records:
            if r.kind == "tool":
                mark = "✓" if r.ok else "✗"
                lines.append(f"  [{r.index}] {r.kind} {mark} {r.detail}")
            else:
                lines.append(f"  [{r.index}] {r.kind} {r.detail}")
        return "\n".join(lines)

# ─── Tool Implementations ───

def run_shell(command: str) -> ToolOutcome:
    """實際執行 shell 指令的工具實作，回傳結構化 ToolOutcome。"""
    start = time.monotonic()
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=SHELL_TIMEOUT, cwd=WORKSPACE,
        )
        output = (result.stdout + result.stderr).strip() or "（無輸出）"
        outcome = ToolOutcome(
            text=output, ok=(result.returncode == 0),
            exit_code=result.returncode, command=command,
            duration_ms=int((time.monotonic() - start) * 1000),
        )
    except subprocess.TimeoutExpired:
        output = f"（指令逾時 {SHELL_TIMEOUT} 秒，已強制中止）"
        outcome = ToolOutcome(text=output, ok=False, command=command, reason="timeout",
                              duration_ms=int((time.monotonic() - start) * 1000))
    except Exception as e:
        output = f"執行錯誤：{e}"
        outcome = ToolOutcome(text=output, ok=False, command=command, reason=str(e),
                              duration_ms=int((time.monotonic() - start) * 1000))

    print(f"\n⚙️  執行：{command}（{outcome.duration_ms}ms, exit={outcome.exit_code}）")
    print(f"   結果：{outcome.text[:200]}")
    return outcome

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

# ─── Tool Definitions（Ollama 原生 function calling 格式） ───

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "在使用者的電腦上執行一段 shell 指令，回傳 stdout、stderr 與 exit code。"
                           "若指令失敗（非零 exit code），agent 會反思並可能以修正後的指令重試。"
                           "適用於：建立/讀取/編輯檔案、查詢系統資訊、執行程式、安裝套件。"
                           "請避免不會自動結束的指令（如 tail -f、啟動伺服器）。"
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

# ─── 歷史管理 ───

def trim_history(messages: list) -> list:
    """保留 system 訊息 + 最近 HISTORY_MESSAGES 則，避免 context 無限增長。"""
    system_msg = messages[0]
    rest = messages[1:]
    if len(rest) > HISTORY_MESSAGES:
        rest = rest[-HISTORY_MESSAGES:]
    return [system_msg] + rest

# ─── Main ───

def main():
    os.makedirs(WORKSPACE, exist_ok=True)
    loop = SelfCorrectingLoop()
    messages = [{
        "role": "system",
        "content": (
            "你是 Jarvis，一個運行在使用者電腦上的 AI 助理。\n"
            "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。\n"
            "只有在真的需要操作檔案、查詢系統資訊、執行程式時，才呼叫 run_shell 工具。\n"
            "若工具呼叫失敗，你會收到反思提示：先分析失敗原因，再以修正後的指令重試；\n"
            "若判斷不需要重試，就直接給出最終答案並說明限制。\n"
            "避免使用不會自動結束的指令（例如 tail -f、持續監聽的伺服器）。"
        ),
    }]

    print(f"Agent (loop) - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print(f"Loop：max_tool_turns={MAX_TOOL_TURNS}, max_replans={MAX_REPLANS}")
    print("指令：/quit 結束、/clear 清空對話歷史、/loop 檢視迴圈狀態\n")

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
            messages = messages[:1]
            loop = SelfCorrectingLoop()
            print("對話歷史已清空。\n")
            continue
        if user_input.lower() == "/loop":
            print(loop.describe())
            continue

        answer = loop.run(messages, user_input)
        if not answer:
            # 保險：正常情況不該發生，但避免完全沒輸出
            print("🤖 （沒有取得回覆內容）\n")
        messages = trim_history(messages)

if __name__ == "__main__":
    main()