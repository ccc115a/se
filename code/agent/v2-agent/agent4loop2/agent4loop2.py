#!/usr/bin/env python3
# agent4loop2.py - 多角色分工版：planner → executor → evaluator
# Run: python agent4loop2.py
#
# 設計重點（相對於 agent4loop.py）：
#   1. 不再由「同一個 agent」自我反思，而是拆成三個不同角色的模型呼叫：
#      - Planner（規劃者）：無工具，只輸出任務的執行計畫
#      - Executor（執行者）：擁有 run_shell，按計畫實際執行工具呼叫
#      - Evaluator（評估者）：檢視執行結果，判斷任務是否完成；
#        完成 -> 呼叫 task_done 提交最終答案；未完成 -> 給 Planner 修正意見
#   2. 循環：Planner 出計畫 → Executor 執行 → Evaluator 評估
#      → 未完成就帶評估回饋回到 Planner 修正計畫，直到完成或預算用罄。
#   3. 三個角色使用不同的 system prompt 與不同的工具集合，
#      由 RoleLoop 統一調度，逐字稿記錄每一位角色的動作。
#   4. 新增 /roles 指令顯示三個角色的職責摘要與本回合調度記錄。

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
MAX_PLAN_CYCLES = 4      # Planner→Executor→Evaluator 最多跑幾輪
MAX_TOOL_TURNS = 6       # Executor 一次任務最多允許幾輪工具呼叫
HISTORY_MESSAGES = 12    # 對話歷史最多保留幾則訊息（不含 system）
SHELL_TIMEOUT = 30       # 單一 shell 指令逾時秒數

GRAY = "\033[90m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# ─── 角色 System Prompt ───

PLANNER_PROMPT = (
    "你是 Planner（規劃者），任務的第一棒。你沒有任何工具，不要嘗試呼叫工具。\n"
    "你的工作：把使用者任務拆解成一份簡潔、可執行的步驟計畫。\n"
    "如果收到 Evaluator 的修正意見，請根據意見調整計畫。\n"
    "輸出格式：\n"
    "  計畫：《一句話說明要做什麼》\n"
    "  步驟：\n"
    "    1. ...\n"
    "    2. ...\n"
    "只輸出計畫本身，不要自行執行。"
)

EXECUTOR_PROMPT = (
    "你是 Executor（執行者），任務的第二棒。你擁有 run_shell 工具。\n"
    "你的工作：嚴格依照 Planner 的計畫，用 run_shell 執行每一步。\n"
    "規則：\n"
    "  - 每一步只發一次工具呼叫；一次可並行發多個獨立指令。\n"
    "  - 指令失敗時不要擅自幻想結果，直接回傳失敗事實即可。\n"
    "  - 不要執行不會自動結束的指令（如 tail -f、啟動伺服器）。\n"
    "執行完計畫的全部步驟後，用一句話總結你做了什麼。"
)

EVALUATOR_PROMPT = (
    "你是 Evaluator（評估者），任務的第三棒。你的任務是檢視 Executor 的執行結果，判斷任務是否已完成。\n"
    "二選一，絕對不要做第三種：\n"
    "  - 若任務已完成：**必須**呼叫 task_done 工具，把最終答案文字填在 final_answer 參數。\n"
    "  - 若任務未完成（失敗、缺步驟、執行結果看不到預期輸出）：**不要**呼叫工具，\n"
    "    直接輸出給 Planner 的修正意見（一句話指出缺了什麼即可）。\n"
    "注意：不要只說「已完成」而不呼叫工具——結束的唯一方式是 task_done。"
)

# ─── 工具定義（Ollama 原生 function calling 格式） ───

# Executor 專用工具：run_shell
EXEC_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "在使用者的電腦上執行一段 shell 指令，回傳 stdout、stderr 與 exit code。"
                           "安全規則會禁止不會自動結束的指令（如伺服器、tail -f）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要執行的完整 shell 指令",
                    }
                },
                "required": ["command"],
            },
        },
    }
]

# Evaluator 專用工具：task_done（任務完成的信號）
EVAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "task_done",
            "description": "任務已完成時呼叫，提交最終答案給使用者。",
            "parameters": {
                "type": "object",
                "properties": {
                    "final_answer": {
                        "type": "string",
                        "description": "給使用者的最終答案文字",
                    }
                },
                "required": ["final_answer"],
            },
        },
    }
]

# ─── Tool Outcome（結構化執行結果） ───

@dataclass
class ToolOutcome:
    text: str
    ok: bool
    exit_code: int | None = None
    reason: str = ""
    command: str = ""
    duration_ms: int = 0

# ─── 調度逐字稿記錄 ───

@dataclass
class TurnRecord:
    role: str              # "planner" | "executor" | "evaluator"
    detail: str
    ok: bool | None = None
    index: int = 0

# ─── Role Loop（planner → executor → evaluator 調度核心） ───

class RoleLoop:
    """三人分工的任務迴圈：Planner 出計畫 → Executor 執行 → Evaluator 評估。

    Evaluator 若呼叫 task_done 就收束；否則把意見交回 Planner 修正計畫，
    最多跑 MAX_PLAN_CYCLES 輪；Executor 工具呼叫受 MAX_TOOL_TURNS 限制。
    三個角色各自使用不同 system prompt 與工具集合。
    """

    def __init__(self, max_plan_cycles: int = MAX_PLAN_CYCLES,
                 max_tool_turns: int = MAX_TOOL_TURNS):
        self.max_plan_cycles = max_plan_cycles
        self.max_tool_turns = max_tool_turns
        self.plan_cycles = 0
        self.tool_rounds = 0
        self.records: list[TurnRecord] = []
        self._next_index = 1
        # 任務期間共享的「事實」：計畫、工具結果、評估意見
        self.plan_text = ""
        self.eval_feedback = ""
        self.tool_log: list[str] = []
        # Executor 工具回合的對話串流（含每次 tool_calls / tool 結果）
        self.exec_history: list[dict] = []

    # ── 逐字稿 ──

    def _record(self, role: str, detail: str, ok: bool | None = None) -> TurnRecord:
        rec = TurnRecord(role=role, detail=detail, ok=ok, index=self._next_index)
        self._next_index += 1
        self.records.append(rec)
        return rec

    # ── 各角色 context 組裝 ──

    def _planner_messages(self, task: str) -> list:
        ctx = f"任務：{task}"
        if self.tool_log:
            ctx += "\n\n已完成的執行結果：\n" + "\n".join(self.tool_log)
        if self.eval_feedback:
            ctx += f"\n\nEvaluator 的修正意見：{self.eval_feedback}"
        if self.plan_text:
            ctx += f"\n\n上一版計畫（供參考）：{self.plan_text}"
        return [{"role": "system", "content": PLANNER_PROMPT},
                {"role": "user", "content": ctx}]

    def _executor_messages(self) -> list:
        msgs = [
            {"role": "system", "content": EXECUTOR_PROMPT},
            {"role": "user", "content": (
                f"請執行這份計畫：\n{self.plan_text}\n\n"
                f"剩餘工具回合：{self.max_tool_turns - self.tool_rounds}"
            )},
        ]
        # 把先前各輪的工具呼叫與結果接上，讓 Executor 能看到失敗並反應
        msgs.extend(self.exec_history)
        return msgs

    def _evaluator_messages(self, task: str) -> list:
        return [
            {"role": "system", "content": EVALUATOR_PROMPT},
            {"role": "user", "content": (
                f"任務：{task}\n"
                f"計畫：{self.plan_text}\n"
                "執行結果：\n" + (("\n".join(self.tool_log)) if self.tool_log else "（無）")
            )},
        ]

    # ── 主迴圈 ──

    def run(self, messages: list, user_input: str,
            tool_impls: dict | None = None,
            call_ollama_fn=None) -> str:
        """跑完整個三人分工迴圈，回傳最終答案文字。

        tool_impls / call_ollama_fn 可注入 fake，方便測試（不需要真的 Ollama）。
        """
        impls = tool_impls or TOOL_IMPLS
        call_fn = call_ollama_fn or (
            lambda m, tools=None, think=True: asyncio.run(call_ollama(m, tools=tools, think=think)))

        messages.append({"role": "user", "content": user_input})

        final_answer = ""
        while self.plan_cycles < self.max_plan_cycles:
            self.plan_cycles += 1
            print(f"\n{CYAN}── [Planner] 第 {self.plan_cycles} 輪 ──{RESET}\n")

            # 1) Planner 出計畫
            planner_result = call_fn(self._planner_messages(user_input), tools=None, think=False)
            self.plan_text = planner_result.get("content", "").strip()
            self._record("planner", self.plan_text[:80], ok=True)

            # 2) Executor 執行（可多輪工具呼叫，受 MAX_TOOL_TURNS 控制）
            print(f"\n{YELLOW}── [Executor] ──{RESET}\n")
            exec_done = False
            while not exec_done and self.tool_rounds < self.max_tool_turns:
                exec_result = call_fn(self._executor_messages(), tools=EXEC_TOOLS, think=False)

                if not exec_result.get("tool_calls"):
                    # Executor 直接給總結（未呼叫工具）
                    self._record("executor", "總結：" + exec_result.get("content", "").strip()[:80], ok=None)
                    exec_done = True
                    break

                messages.append({
                    "role": "assistant",
                    "content": exec_result.get("content", ""),
                    "tool_calls": exec_result["tool_calls"],
                })
                self.exec_history.append({
                    "role": "assistant",
                    "content": exec_result.get("content", ""),
                    "tool_calls": exec_result["tool_calls"],
                })
                # 批次截斷：一次回傳的工具呼叫不得超出剩餘預算
                batch = exec_result["tool_calls"]
                remaining = self.max_tool_turns - self.tool_rounds
                if len(batch) > remaining:
                    self.tool_log.append(f"（工具回合預算剩 {remaining}，批次截斷，捨棄 {len(batch) - remaining} 個）")
                    self._record("executor", f"批次截斷：超過預算，保留 {remaining} 個", ok=None)
                    batch = batch[:remaining]
                for call in batch:
                    self.tool_rounds += 1
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
                    self.exec_history.append({"role": "tool", "content": outcome.text, "name": name})
                    self.tool_log.append(
                        f"$ {outcome.command or name} → {outcome.text[:120]}"
                    )
                    self._record("executor", outcome.command or name, ok=outcome.ok)
                # 工具回合用罄就結束這輪執行
                if self.tool_rounds >= self.max_tool_turns:
                    exec_done = True

            # 3) Evaluator 評估
            print(f"\n{GREEN}── [Evaluator] ──{RESET}\n")
            eval_result = call_fn(self._evaluator_messages(user_input), tools=EVAL_TOOLS,
                                  think=False)

            # 若 Evaluator 呼叫 task_done → 任務完成
            done_answer = None
            if eval_result.get("tool_calls"):
                for call in eval_result["tool_calls"]:
                    fn = call.get("function", {})
                    if fn.get("name") == "task_done":
                        done_answer = fn.get("arguments", {}).get("final_answer", "")
                if done_answer is not None:
                    final_answer = done_answer
                    self._record("evaluator", f"task_done → {done_answer[:80]}", ok=True)
                    break

            # 否則 Evaluator 給修正意見 → 回饋給 Planner
            self.eval_feedback = eval_result.get("content", "").strip()
            self._record("evaluator", f"回饋：{self.eval_feedback[:80]}", ok=False)

        if not final_answer:
            final_answer = f"（已達最多 {self.max_plan_cycles} 輪計畫週期，未得到最終答案。）"
            self._record("evaluator", final_answer, ok=False)

        messages.append({"role": "assistant", "content": final_answer})
        return final_answer

    # ── 顯示角色調度狀態（/roles 用） ──

    def describe(self) -> str:
        lines = [
            "===== Planner → Executor → Evaluator 分工迴圈 =====",
            f"計畫週期: {self.plan_cycles}/{self.max_plan_cycles}",
            f"工具回合: {self.tool_rounds}/{self.max_tool_turns}",
            "",
            "角色職責：",
            "  Planner    出計畫（無工具）",
            "  Executor   執行 run_shell",
            "  Evaluator  呼叫 task_done 收束 / 給回饋",
            "",
            f"調度記錄 ({len(self.records)} 筆):",
        ]
        for r in self.records:
            lines.append(f"  [{r.index}] {r.role:<10} {'✓' if r.ok else '○'} {r.detail}")
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

# 工具名稱 → 實作函式 的對照表，Executor 用的都是這裡註冊的工具
TOOL_IMPLS = {
    "run_shell": lambda args: run_shell(args.get("command", "")),
}

# ─── Ollama API（streaming + thinking 顯示 + tool_calls） ───

async def call_ollama(messages: list, tools: list | None = None,
                      think: bool = True) -> dict:
    """呼叫 /api/chat（串流），回傳 {"content": str, "tool_calls": list | None}

    思考過程即時以灰色 + '>> ' 前綴印出；tool_calls 由 Ollama 完整送出（非逐字串流片段）。
    think=False 時關閉 thinking 輸出（計算角色用），避免小模型在思考上爆量。
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "think": think,
        # 小模型思考常爆量，限制輸出 token 數避免單次呼叫過久
        "options": {"num_predict": 1200},
    }
    if tools:
        payload["tools"] = tools

    content = ""
    tool_calls = None
    in_thinking = False
    thinking_closed = False

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300),
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
    loop = RoleLoop()
    messages = [{
        "role": "system",
        "content": (
            "你是由 Planner、Executor、Evaluator 三位一體組成的 AI 助理（Jarvis），\n"
            "會依序：規劃 → 執行 → 評估，直到任務完成。\n"
            "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。"
        ),
    }]

    print(f"Agent (roles) - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print(f"RoleLoop：max_plan_cycles={MAX_PLAN_CYCLES}, max_tool_turns={MAX_TOOL_TURNS}")
    print("指令：/quit 結束、/clear 清空對話歷史、/roles 檢視角色調度\n")

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
            loop = RoleLoop()
            print("對話歷史已清空。\n")
            continue
        if user_input.lower() == "/roles":
            print(loop.describe())
            continue

        answer = loop.run(messages, user_input)
        if not answer:
            # 保險：正常情況不該發生，但避免完全沒輸出
            print("🤖 （沒有取得回覆內容）\n")
        else:
            print(f"{GREEN}🤖 {answer}{RESET}\n")
        messages = trim_history(messages)

if __name__ == "__main__":
    main()