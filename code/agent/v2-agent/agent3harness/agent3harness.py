#!/usr/bin/env python3
# agent3harness.py - agent1 的 harness engineering 版本
# Run: python agent3harness.py
#
# 設計重點（相對於 agent1prompt.py）：
#   1. 把「工具如何執行」抽成一個 ExecutionHarness 類別，集中管管控所有 shell 執行：
#      - 結構化結果：stdout / stderr / exit code / 執行耗時分開記錄
#      - 輸出截斷：超過 MAX_OUTPUT_CHARS 自動截斷，避免巨大輸出淹沒 context
#      - 逾時與保護：SHELL_TIMEOUT、禁止非自動結束指令（tail -f、伺服器等）
#      - 嚴格工作區：固定 cwd = WORKSPACE，並以 allowlist 隔離環境變數
#   2. 保持 Ollama 原生 tools / tool_calls 機制、streaming 與思考顯示與 agent1 相同。
#   3. 新增 /harness 指令，顯示目前 harness 的組態與保護規則。

import asyncio
import aiohttp
import json
import os
import re
import subprocess
import time

# ─── Configuration ───

#MODEL = "qwen3.5:4b"
MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()  # 使用執行當下所在的資料夾
MAX_TOOL_TURNS = 5      # 一次任務最多允許幾輪工具呼叫
HISTORY_MESSAGES = 12   # 對話歷史最多保留幾則訊息（不含 system）
SHELL_TIMEOUT = 30      # 單一 shell 指令逾時秒數
MAX_OUTPUT_CHARS = 2000 # 單一工具結果最多回傳多少字元（超出截斷）

GRAY = "\033[90m"
RESET = "\033[0m"

# ─── Execution Harness（harness engineering 核心） ───

class ExecResult:
    """一次 shell 執行的結構化結果。

    把 stdout / stderr / exit code / 耗時分開記錄，
    再由 to_text() 決定要餵回模型的文字格式——
    這讓模型拿到的不只是「一串輸出」，而是帶脈絡的執行結果。
    """

    def __init__(self, command: str, stdout: str = "", stderr: str = "",
                 exit_code: int | None = None, duration_ms: int = 0,
                 timed_out: bool = False, truncated: bool = False,
                 denied: bool = False, error: str = ""):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.duration_ms = duration_ms
        self.timed_out = timed_out
        self.truncated = truncated
        self.denied = denied
        self.error = error

    @property
    def ok(self) -> bool:
        return not (self.timed_out or self.denied or self.error) and self.exit_code == 0

    def to_text(self) -> str:
        """把執行結果轉成可直接餵回模型的文字。"""
        lines = []
        if self.denied:
            return f"（指令被 harness 安全規則拒絕：{self.error}）"
        if self.timed_out:
            lines.append(f"（指令逾時，已強制中止）")
        if self.error:
            lines.append(f"（執行錯誤：{self.error}）")
        if self.stdout:
            lines.append(f"[stdout]\n{self.stdout}")
        if self.stderr:
            lines.append(f"[stderr]\n{self.stderr}")
        if self.truncated:
            lines.append("（輸出過長，已截斷）")
        if not (self.stdout or self.stderr) and not (self.timed_out or self.error):
            lines.append("（無輸出）")
        if self.exit_code not in (None, 0):
            lines.append(f"（exit code: {self.exit_code}）")
        return "\n".join(lines)

    def __repr__(self):
        return (f"ExecResult(command={self.command!r}, exit_code={self.exit_code}, "
                f"duration_ms={self.duration_ms}, timed_out={self.timed_out}, "
                f"truncated={self.truncated}, denied={self.denied})")

class ExecutionHarness:
    """所有 shell 執行的唯一入口。

    工具實作不該直接碰 subprocess，一律透過這個 harness——
    這樣逾時、截斷、安全規則、工作區、環境隔離都能集中維護，
    而不是散落在每支工具的 if/else 裡。
    """

    # 禁止的非自動結束指令（正則，小寫比對）
    FORBIDDEN_PATTERNS = [
        r"tail\s+(-f|-F|--follow)",      # tail -f 類
        r"\bwatch\b",                     # watch 迴圈
        # 常駐類伺服器
        r"\buvicorn\b",
        r"\bgunicorn\b",
        r"\bflask run\b",
        r"\bhttp\.server\b",
        r"\bnpm start\b",
        r"\bng serve\b",
        r"python\s+.*(-m\s+)?http\.server",
    ]

    def __init__(self, workspace: str = WORKSPACE, timeout: float = SHELL_TIMEOUT,
                 max_output_chars: int = MAX_OUTPUT_CHARS,
                 env_allowlist: tuple | None = None):
        self.workspace = workspace
        self.timeout = timeout
        self.max_output_chars = max_output_chars
        # 環境變數 allowlist：子程序只會看到白名單內的變數（隔離父子環境）
        self.env_allowlist = env_allowlist or ("PATH", "HOME", "LANG", "LC_ALL", "TERM", "SHELL", "TMPDIR")

    # ── 安全規則 ──

    def check_safe(self, command: str) -> tuple[bool, str]:
        """檢查一條指令是否安全。回傳 (允許與否, 理由)。"""
        if not command or not command.strip():
            return False, "指令為空"
        lowered = command.lower()
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, lowered):
                return False, f"禁止非自動結束指令（匹配: {pattern}）"
        return True, ""

    # ── 隔離環境 ──

    def env(self) -> dict:
        """建立子程序使用的隔離環境（只包含 allowlist 內的變數）。"""
        return {k: v for k, v in os.environ.items() if k in self.env_allowlist}

    # ── 執行 ──

    def _truncate(self, text: str) -> str:
        if len(text) > self.max_output_chars:
            return text[: self.max_output_chars] + "\n…（已截斷）"
        return text

    def execute(self, command: str) -> ExecResult:
        """執行一條指令，永遠回傳 ExecResult（不會 throw）。"""
        safe, reason = self.check_safe(command)
        if not safe:
            return ExecResult(command=command, denied=True, error=reason)

        start = time.monotonic()
        truncated = False
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=self.timeout, cwd=self.workspace, env=self.env(),
            )
            duration = int((time.monotonic() - start) * 1000)
            stdout = self._truncate(result.stdout)
            stderr = self._truncate(result.stderr)
            if stdout != result.stdout or stderr != result.stderr:
                truncated = True
            return ExecResult(
                command=command, stdout=stdout, stderr=stderr,
                exit_code=result.returncode, duration_ms=duration,
                truncated=truncated,
            )
        except subprocess.TimeoutExpired as e:
            duration = int((time.monotonic() - start) * 1000)
            return ExecResult(command=command, timed_out=True, duration_ms=duration,
                              stdout=(e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""))
        except Exception as e:
            duration = int((time.monotonic() - start) * 1000)
            return ExecResult(command=command, error=str(e), duration_ms=duration)

    # ── 顯示 harness 組態 ──

    def describe(self) -> str:
        return (
            "===== Execution Harness 組態 ====="
            f"\n工作區 (cwd): {self.workspace}"
            f"\n逾時: {self.timeout}s | 輸出上限: {self.max_output_chars} chars"
            f"\n環境變數 allowlist: {', '.join(self.env_allowlist)}"
            f"\n禁止的指令樣式 ({len(self.FORBIDDEN_PATTERNS)}):"
            + "".join(f"\n  - {p}" for p in self.FORBIDDEN_PATTERNS)
        )

# ─── Tool Implementations ───

HARNESS = ExecutionHarness()

def run_shell(command: str) -> str:
    """實際執行 shell 指令的工具實作，回傳可以直接餵回模型的文字結果。"""
    result = HARNESS.execute(command)
    print(f"\n⚙️  執行：{result.command}（{result.duration_ms}ms, exit={result.exit_code}）")
    if result.ok:
        print(f"   結果：{result.stdout.strip()[:200] or '(無輸出)'}")
    else:
        print(f"   結果：{result.to_text()[:200]}")
    return result.to_text()

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
                           "適用於：建立/讀取/編輯檔案、查詢系統資訊、執行程式、安裝套件。"
                           "安全規則會自動禁止不會自動結束的指令（如伺服器、tail -f）。"
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
        result = asyncio.run(call_ollama(messages, TOOLS))

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
    messages = [{
        "role": "system",
        "content": (
            "你是 Jarvis，一個運行在使用者電腦上的 AI 助理。\n"
            "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。\n"
            "只有在真的需要操作檔案、查詢系統資訊、執行程式時，才呼叫 run_shell 工具。\n"
            f"工作區（所有指令在此執行）：{WORKSPACE}\n"
            "安全政策：禁止使用不會自動結束的指令（例如 tail -f、啟動伺服器）。"
        ),
    }]

    print(f"Agent (harness) - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print(f"Harness：timeout={SHELL_TIMEOUT}s, max_output={MAX_OUTPUT_CHARS} chars")
    print("指令：/quit 結束、/clear 清空對話歷史、/harness 檢視 harness 組態\n")

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
            print("對話歷史已清空。\n")
            continue
        if user_input.lower() == "/harness":
            print(HARNESS.describe())
            continue

        answer = handle_turn(messages, user_input)
        if not answer:
            # 保險：正常情況不該發生，但避免完全沒輸出
            print("🤖 （沒有取得回覆內容）\n")
        messages = trim_history(messages)

if __name__ == "__main__":
    main()