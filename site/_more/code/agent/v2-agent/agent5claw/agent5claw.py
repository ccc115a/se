#!/usr/bin/env python3
# agent5claw.py - v6: OpenClaw 概念縮小版的「萬用 agent」
# Run: python agent5claw.py
#
# 設計重點（OpenClaw 的三塊核心落到單檔 + Ollama 原生 function calling）：
#   1. ClawMemory——持久化 Markdown 記憶：跨 session 記住「事實/偏好/專案」，
#      開場自動載入並注入 system prompt，模型可用 remember 工具寫入，/memory 檢視。
#   2. SecurityPolicy——執行授權策略：shell 指令執行前先過 policy，
#      auto（直接執行）/ ask（逐條詢問 y/N）/ deny（一律封鎖），
#      並內建禁止模式（tail -f、伺服器、rm -rf / 等危險指令）。
#   3. Skills 技能表——把常見任務（讀檔、搜尋、系統資訊、列檔）做成可註冊技能，
#      模型透過 run_skill 工具叫用，使用者可用 /skills、/skill 直接執行。
#   base 沿用 agent1prompt 的 Ollama streaming + tool_calls 迴圈（v1 機制）。

import asyncio
import aiohttp
import json
import os
import platform
import re
import subprocess
from dataclasses import dataclass, field

# ─── Configuration ───

MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()          # 使用執行當下所在的資料夾
MAX_TOOL_TURNS = 6               # 一次任務最多允許幾輪工具呼叫
HISTORY_MESSAGES = 12            # 對話歷史最多保留幾則訊息（不含 system）
SHELL_TIMEOUT = 30               # 單一 shell 指令逾時秒數
APPROVAL = "auto"                # run_shell 預設授權模式：auto | ask | deny
MEMORY_FILE = os.environ.get("CLAW_MEMORY_FILE") or os.path.join(WORKSPACE, "claw_memory.md")

GRAY = "\033[90m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RESET = "\033[0m"

SYSTEM_PROMPT = (
    "你是 Claw，一個運行在使用者電腦上、類似 OpenClaw 的萬用個人 AI 助理。\n"
    "你有三種工具：\n"
    "  - run_shell：執行 shell 指令（受授權策略管制）。\n"
    "  - remember：把關於使用者的事實、偏好、專案狀態記入持久記憶。\n"
    "  - run_skill：叫用技能表（read_file / search / sysinfo / list_files）。\n"
    "使用原則：\n"
    "  - 一般聊天直接回答，不需要工具。\n"
    "  - 得知使用者資訊（名字、職業、偏好、專案細節）時，記得用 remember 存起來。\n"
    "  - 操作檔案、跑程式、查系統資訊時，優先考慮技能，最後才用 run_shell。\n"
    "  - 避免不會自動結束的指令（如 tail -f、啟動伺服器）。"
)

# ─── 禁止模式：命中就封鎖，任何授權模式都不放行 ───

DENY_PATTERNS = [
    r"rm\s+-rf\s+/\s*$",          # 根目錄毀滅
    r"mkfs\.",                     # 格式化磁碟
    r"dd\s+if=.*of=/dev/",         # 覆寫裝置
    r"tail\s+-f",                  # 不結束的監看
    r"\bwatch\b",                  # 監看迴圈
    r"(python|python3)\s+-m\s+http\.server",  # 持續伺服器
    r"\b(flask|uvicorn|ngrok|jupyter)\b",     # 服務類
]

# ─── ClawMemory：持久化 Markdown 記憶 ───

class ClawMemory:
    """把事實/偏好/專案存成 Markdown 檔，跨 session 保留。

    格式：
        # Claw 記憶
        ## 事實 (Facts)
        - ...
        ## 偏好 (Preferences)
        - ...
        ## 專案 (Projects)
        - ...
    """

    SECTIONS = ("事實", "偏好", "專案")

    def __init__(self, path: str = MEMORY_FILE):
        self.path = path
        self.data: dict[str, list[str]] = {s: [] for s in self.SECTIONS}

    def load(self):
        """從 Markdown 檔讀回記憶；檔不存在就是空白記憶。"""
        self.data = {s: [] for s in self.SECTIONS}
        if not os.path.isfile(self.path):
            return
        section = self.SECTIONS[0]
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                m = re.match(r"## (.+)", line)
                if m and m.group(1).strip() in self.data:
                    section = m.group(1).strip()
                    continue
                m = re.match(r"- (.+)", line)
                if m and m.group(1).strip():
                    self.data[section].append(m.group(1).strip())

    def save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("# Claw 記憶\n\n")
            for s in self.SECTIONS:
                f.write(f"## {s}\n")
                for item in self.data[s]:
                    f.write(f"- {item}\n")
                f.write("\n")

    def add(self, section: str, text: str) -> bool:
        """把一則記憶寫入；重複內容不重複存。"""
        if section not in self.data:
            section = self.SECTIONS[0]
        text = text.strip()
        if not text:
            return False
        if text in self.data[section]:
            return False
        self.data[section].append(text)
        self.save()
        return True

    def render(self) -> str:
        """給 system prompt 用的記憶摘要；沒記憶就回空字串。"""
        if not any(self.data[s] for s in self.SECTIONS):
            return ""
        lines = ["## 你記得的內容（持久記憶，跨 session 有效）"]
        for s in self.SECTIONS:
            if self.data[s]:
                lines.append(f"### {s}")
                lines.extend(f"- {item}" for item in self.data[s])
        return "\n".join(lines)

# ─── SecurityPolicy：執行授權策略 ───

class SecurityPolicy:
    """run_shell 的放行閘門。

    - auto:  只要不命中禁止模式就直接執行
    - deny:  所有指令一律封鎖
    - ask:   逐條問使用者 y/N（prompt_fn 可注入，測試用）
    """

    def __init__(self, mode: str = APPROVAL, deny_patterns: list | None = None):
        self.mode = mode
        self.deny_patterns = deny_patterns if deny_patterns is not None else DENY_PATTERNS

    def check(self, command: str, prompt_fn=None) -> tuple[bool, str]:
        """回傳 (是否放行, 原因/說明)。"""
        for pat in self.deny_patterns:
            if re.search(pat, command):
                return False, f"命中禁止模式：{pat}"
        if self.mode == "auto":
            return True, ""
        if self.mode == "deny":
            return False, "授權模式為 deny，所有 shell 指令一律封鎖"
        # ask：預設用 input() 問使用者；測試可注入 prompt_fn
        ask = prompt_fn or (lambda prompt: input(prompt).strip().lower())
        if ask(f"允許執行此指令？ {command} [y/N] ") in ("y", "yes"):
            return True, ""
        return False, "使用者拒絕執行"

POLICY = SecurityPolicy()  # 全域政策，/approval 可切換 mode

# ─── 技能表（Skills）：可註冊的任務模板 ───

@dataclass
class Skill:
    name: str
    description: str
    handler: object  # fn(args: dict) -> str

def _skill_read_file(args: dict) -> str:
    path = (args.get("path") or args.get("input") or "").strip()
    if not path:
        return "缺少 path 參數"
    full = os.path.abspath(os.path.join(WORKSPACE, path))
    if not full.startswith(os.path.abspath(WORKSPACE)):
        return "路徑超出 WORKSPACE，拒絕讀取"
    if not os.path.isfile(full):
        return f"檔案不存在：{path}"
    with open(full, encoding="utf-8", errors="replace") as f:
        return f.read(4000).strip() or "（空檔）"

def _skill_search(args: dict) -> str:
    pattern = (args.get("pattern") or args.get("input") or "").strip()
    if not pattern:
        return "缺少 pattern 參數"
    hits = []
    skipped = {".git", "__pycache__", ".venv", "node_modules"}
    exts = (".py", ".md", ".txt", ".json", ".sh", ".toml")
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in skipped]
        for name in files:
            if not name.endswith(exts):
                continue
            full = os.path.join(root, name)
            try:
                with open(full, encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f, 1):
                        if pattern in line:
                            rel = os.path.relpath(full, WORKSPACE)
                            hits.append(f"{rel}:{i}: {line.strip()[:80]}")
                            break
            except OSError:
                continue
    if not hits:
        return f"在 WORKSPACE 內找不到「{pattern}」"
    body = "\n".join(hits[:20])
    extra = f"（…還有 {len(hits) - 20} 筆）" if len(hits) > 20 else ""
    return f"找到 {len(hits)} 筆：\n{body}\n{extra}"

def _skill_sysinfo(args: dict) -> str:
    try:
        kernel = subprocess.run(
            "uname -a", shell=True, capture_output=True, text=True,
            timeout=10, cwd=WORKSPACE,
        ).stdout.strip() or "（uname 無輸出）"
    except Exception as e:
        kernel = f"（uname 失敗：{e}）"
    return f"OS: {kernel}\nPython: {platform.python_version()}\n機器: {platform.machine()}"

def _skill_list_files(args: dict) -> str:
    entries = sorted(os.listdir(WORKSPACE))
    lines = []
    for e in entries:
        marker = "📁" if os.path.isdir(os.path.join(WORKSPACE, e)) else "  "
        lines.append(f"{marker} {e}")
    return "\n".join(lines) or "（空資料夾）"

SKILLS: list[Skill] = [
    Skill("read_file", "讀取 WORKSPACE 內的文字檔（path 參數）", _skill_read_file),
    Skill("search", "在 WORKSPACE 原始碼/文件裡搜尋關鍵字（pattern 參數）", _skill_search),
    Skill("sysinfo", "顯示作業系統與執行環境資訊", _skill_sysinfo),
    Skill("list_files", "列出 WORKSPACE 內的檔案與資料夾", _skill_list_files),
]

def run_skill(name: str, args: dict | None = None) -> str:
    for skill in SKILLS:
        if skill.name == name:
            return skill.handler(args or {})
    return f"未知技能：{name}"

# ─── Tool 定義（Ollama 原生 function calling 格式） ───

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "執行一段 shell 指令（受授權策略管制），回傳 stdout/stderr 與 exit code。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "要執行的 shell 指令"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "把關於使用者的事實、偏好或專案狀態記入持久記憶（跨 session 保留）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "section": {"type": "string",
                                "enum": ["事實", "偏好", "專案"],
                                "description": "記憶分類"},
                    "text": {"type": "string", "description": "要記住的內容"},
                },
                "required": ["section", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_skill",
            "description": "叫用技能表中的任務模板。可用：read_file、search、sysinfo、list_files。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string",
                             "enum": [s.name for s in SKILLS],
                             "description": "技能名稱"},
                    "arguments": {"type": "object",
                                  "description": "技能參數，如 read_file 用 {\"path\": \"/tmp/a.py\"}"},
                },
                "required": ["name"],
            },
        },
    },
]

# ─── run_shell（受 SecurityPolicy 管制） ───

def run_shell(command: str, policy: SecurityPolicy | None = None,
              prompt_fn=None) -> str:
    """執行 shell 指令，先過授權閘門；回傳可直接餵回模型的文字結果。"""
    policy = policy or POLICY
    allowed, reason = policy.check(command, prompt_fn=prompt_fn)
    if not allowed:
        print(f"\n🛡️  封鎖：{command}\n   {reason}\n")
        return f"〔被授權策略封鎖〕{reason}"

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

def build_tool_impls(memory: ClawMemory) -> dict:
    """工具名稱 → 實作函式；把共享的 ClawMemory 閉包進去。"""
    return {
        "run_shell": lambda args: run_shell(str(args.get("command", "")).strip()),
        "remember": lambda args: (
            memory.add(str(args.get("section", "事實")), str(args.get("text", "")))
            and "已記入記憶" or "記憶未變更（內容為空或重複）"
        ),
        "run_skill": lambda args: run_skill(str(args.get("name", "")),
                                            args.get("arguments") or {}),
    }

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

# ─── Agent Loop ───

def trim_history(messages: list) -> list:
    """保留 system 訊息 + 最近 HISTORY_MESSAGES 則。"""
    system_msg = messages[0]
    rest = messages[1:]
    if len(rest) > HISTORY_MESSAGES:
        rest = rest[-HISTORY_MESSAGES:]
    return [system_msg] + rest

def build_system_prompt(memory: ClawMemory) -> str:
    mem = memory.render()
    return SYSTEM_PROMPT + (f"\n\n{mem}" if mem else "")

def handle_turn(messages: list, user_input: str, memory: ClawMemory,
                tool_impls: dict | None = None,
                call_ollama_fn=None) -> str:
    """處理一則使用者訊息，回傳最終答案。

    tool_impls / call_ollama_fn 可注入 fake，方便測試（不需要真的 Ollama）。
    """
    impls = tool_impls or build_tool_impls(memory)
    call_fn = call_ollama_fn or (lambda m: asyncio.run(call_ollama(m)))

    # 每輪開始都把最新記憶灌進 system prompt
    messages[0] = {"role": "system", "content": build_system_prompt(memory)}
    messages.append({"role": "user", "content": user_input})

    final_answer = ""
    for _turn in range(MAX_TOOL_TURNS):
        result = call_fn(messages)

        if result.get("tool_calls"):
            messages.append({
                "role": "assistant",
                "content": result.get("content", ""),
                "tool_calls": result["tool_calls"],
            })
            for call in result["tool_calls"]:
                fn = call.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
                impl = impls.get(name)
                output = impl(args) if impl else f"未知工具：{name}"
                messages.append({"role": "tool", "content": output, "name": name})
            continue

        final_answer = result.get("content", "").strip()
        break
    else:
        final_answer = f"（已達最多 {MAX_TOOL_TURNS} 輪工具呼叫，先在此停止。）"

    if final_answer:
        messages.append({"role": "assistant", "content": final_answer})
    return final_answer

def main():
    os.makedirs(WORKSPACE, exist_ok=True)
    memory = ClawMemory()
    memory.load()
    messages = [{"role": "system", "content": build_system_prompt(memory)}]

    print(f"Agent (claw) - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print(f"記憶檔：{memory.path}（{sum(len(v) for v in memory.data.values())} 筆）")
    print(f"授權模式：{POLICY.mode}（/approval 切換）　技能：{', '.join(s.name for s in SKILLS)}")
    print("指令：/quit 結束、/clear 清空對話、/memory 檢視記憶、/remember 分類 內容、"
          "/approval 模式、/skills、/skill 名稱 參數\n")

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
            messages = [{"role": "system", "content": build_system_prompt(memory)}]
            print("對話歷史已清空（記憶保留）。\n")
            continue
        if user_input.lower() == "/memory":
            print(memory.render() or "（尚無記憶。可用 /remember 記下事實/偏好/專案）\n")
            continue
        if user_input.lower().startswith("/remember "):
            parts = user_input.split(" ", 2)
            if len(parts) < 3:
                print("用法：/remember 事實|偏好|專案 內容\n")
                continue
            section, text = parts[1], parts[2]
            ok = memory.add(section, text)
            print(f"{'已記入' if ok else '未變更'}：{section} → {text}\n")
            messages[0] = {"role": "system", "content": build_system_prompt(memory)}
            continue
        if user_input.lower().startswith("/approval"):
            parts = user_input.split()
            if len(parts) == 2 and parts[1] in ("auto", "ask", "deny"):
                POLICY.mode = parts[1]
                print(f"授權模式已切換為：{parts[1]}\n")
            else:
                print(f"目前授權模式：{POLICY.mode}（可用：auto | ask | deny）\n")
            continue
        if user_input.lower() == "/skills":
            print("可用技能：")
            for skill in SKILLS:
                print(f"  {skill.name} — {skill.description}")
            print()
            continue
        if user_input.lower().startswith("/skill "):
            parts = user_input.split(" ", 2)
            name = parts[1]
            rest = parts[2] if len(parts) > 2 else ""
            print(run_skill(name, {"input": rest if rest else "."}))
            print()
            continue

        answer = handle_turn(messages, user_input, memory)
        if not answer:
            print("🤖 （沒有取得回覆內容）\n")
        messages = trim_history(messages)

if __name__ == "__main__":
    main()