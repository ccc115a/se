#!/usr/bin/env python3
# https://gist.github.com/dabit3/86ee04a1c02c839409a02b20fe99a492
# mini-openclaw.py - A minimal OpenClaw clone
# Run: uv run --with anthropic --with schedule python mini-openclaw.py
# 
# 這是一個基於 Anthropic Claude API 的最小化 AI Agent 框架，靈感來自 OpenClaw 專案。
# 實現了 ReAct（Reasoning + Acting）循環：LLM 接收輸入後可調用多種工具，
# 根據工具回饋決定下一步行動，直到任務完成。

import anthropic
import subprocess
import json
import os
import re
import threading
import time
import schedule
from collections import defaultdict
from datetime import datetime

client = anthropic.Anthropic()

# ─── Configuration ───

# 工作空間根目錄，存放所有 Agent 相關檔案
WORKSPACE = os.path.expanduser("~/.mini-openclaw")
# 會話目錄，存放每個對話 session 的 JSONL 歷史
SESSIONS_DIR = os.path.join(WORKSPACE, "sessions")
# 長期記憶目錄，存放跨會話的 key-value 記憶
MEMORY_DIR = os.path.join(WORKSPACE, "memory")
# 命令核准檔案，記錄使用者曾核准/拒絕的命令清單
APPROVALS_FILE = os.path.join(WORKSPACE, "exec-approvals.json")

# ─── Agents ───

# 多 Agent 定義，每個 Agent 有獨立的 name、model、soul（system prompt）
AGENTS = {
    "main": {
        "name": "Jarvis",
        "model": "claude-sonnet-4-5-20250929",
        "soul": (
            "You are Jarvis, a personal AI assistant.\n"
            "Be genuinely helpful. Skip the pleasantries. Have opinions.\n"
            "You have tools — use them proactively.\n\n"
            "## Memory\n"
            f"Your workspace is {WORKSPACE}.\n"
            "Use save_memory to store important information across sessions.\n"
            "Use memory_search at the start of conversations to recall context."
        ),
        "session_prefix": "agent:main",
    },
    "researcher": {
        "name": "Scout",
        "model": "claude-sonnet-4-5-20250929",
        "soul": (
            "You are Scout, a research specialist.\n"
            "Your job: find information and cite sources. Every claim needs evidence.\n"
            "Use tools to gather data. Be thorough but concise.\n"
            "Save important findings with save_memory for other agents to reference."
        ),
        "session_prefix": "agent:researcher",
    },
}

# ─── Tools ───

# Anthropic API 格式的工具定義列表
# LLM 根據這些定義決定何時呼叫哪個工具
TOOLS = [
    {
        "name": "run_command",
        "description": "Run a shell command",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command to run"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a file from the filesystem",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file (creates directories if needed)",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "save_memory",
        "description": "Save important information to long-term memory",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short label (e.g. 'user-preferences')"},
                "content": {"type": "string", "description": "The information to remember"}
            },
            "required": ["key", "content"]
        }
    },
    {
        "name": "memory_search",
        "description": "Search long-term memory for relevant information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to search for"}
            },
            "required": ["query"]
        }
    },
]

# ─── Permission Controls ───

# 安全命令白名單，這些命令不需詢問即可執行
SAFE_COMMANDS = {"ls", "cat", "head", "tail", "wc", "date", "whoami",
                 "echo", "pwd", "which", "git", "python", "node", "npm"}

def load_approvals():
    # 從檔案載入使用者曾核准/拒絕的命令清單
    if os.path.exists(APPROVALS_FILE):
        with open(APPROVALS_FILE) as f:
            return json.load(f)
    return {"allowed": [], "denied": []}

def save_approval(command, approved):
    # 將使用者的核准/拒絕決定存入檔案
    approvals = load_approvals()
    key = "allowed" if approved else "denied"
    if command not in approvals[key]:
        approvals[key].append(command)
    with open(APPROVALS_FILE, "w") as f:
        json.dump(approvals, f, indent=2)

def check_command_safety(command):
    # 檢查命令安全性：白名單 / 已核准 / 需核准
    base_cmd = command.strip().split()[0] if command.strip() else ""
    if base_cmd in SAFE_COMMANDS:
        return "safe"
    approvals = load_approvals()
    if command in approvals["allowed"]:
        return "approved"
    return "needs_approval"

# ─── Tool Execution ───

def execute_tool(name, tool_input):
    # 執行 LLM 請求的工具，支援五種工具類型
    if name == "run_command":
        cmd = tool_input["command"]
        # 安全檢查：白名單 or 已核准 or 詢問使用者
        safety = check_command_safety(cmd)
        if safety == "needs_approval":
            print(f"\n  ⚠️  Command: {cmd}")
            confirm = input("  Allow? (y/n): ").strip().lower()
            if confirm != "y":
                save_approval(cmd, False)
                return "Permission denied by user."
            save_approval(cmd, True)
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout + result.stderr
            return output if output else "(no output)"
        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error: {e}"

    elif name == "read_file":
        try:
            with open(tool_input["path"], "r") as f:
                return f.read()[:10000]
        except Exception as e:
            return f"Error: {e}"

    elif name == "write_file":
        try:
            os.makedirs(os.path.dirname(tool_input["path"]) or ".", exist_ok=True)
            with open(tool_input["path"], "w") as f:
                f.write(tool_input["content"])
            return f"Wrote to {tool_input['path']}"
        except Exception as e:
            return f"Error: {e}"

    elif name == "save_memory":
        # 將記憶寫入 MEMORY_DIR 下的獨立 Markdown 檔案
        os.makedirs(MEMORY_DIR, exist_ok=True)
        filepath = os.path.join(MEMORY_DIR, f"{tool_input['key']}.md")
        with open(filepath, "w") as f:
            f.write(tool_input["content"])
        return f"Saved to memory: {tool_input['key']}"

    elif name == "memory_search":
        # 在 MEMORY_DIR 中搜尋匹配的記憶
        query = tool_input["query"].lower()
        results = []
        if os.path.exists(MEMORY_DIR):
            for fname in os.listdir(MEMORY_DIR):
                if fname.endswith(".md"):
                    with open(os.path.join(MEMORY_DIR, fname), "r") as f:
                        content = f.read()
                    if any(w in content.lower() for w in query.split()):
                        results.append(f"--- {fname} ---\n{content}")
        return "\n\n".join(results) if results else "No matching memories found."

    return f"Unknown tool: {name}"

# ─── Session Management ───

def get_session_path(session_key):
    # 取得會話檔案的 JSONL 路徑，key 中的特殊字元轉為底線
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    safe_key = session_key.replace(":", "_").replace("/", "_")
    return os.path.join(SESSIONS_DIR, f"{safe_key}.jsonl")

def load_session(session_key):
    # 從 JSONL 檔案載入會話歷史（每個 JSON 物件一行）
    path = get_session_path(session_key)
    messages = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return messages

def append_message(session_key, message):
    # 追加一條訊息到會話歷史（立即寫入磁碟確保持久化）
    with open(get_session_path(session_key), "a") as f:
        f.write(json.dumps(message) + "\n")

def save_session(session_key, messages):
    # 覆寫整個會話歷史（用於壓縮後的更新）
    with open(get_session_path(session_key), "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

# ─── Compaction ───

def estimate_tokens(messages):
    # 粗略估計 token 數量（字元數 / 4）
    return sum(len(json.dumps(m)) for m in messages) // 4

def compact_session(session_key, messages):
    # 若 token 超過 100K，對舊對話進行摘要壓縮
    if estimate_tokens(messages) < 100_000:
        return messages
    split = len(messages) // 2
    old, recent = messages[:split], messages[split:]
    print("\n  📦 Compacting session history...")
    # 使用 LLM 總結舊對話
    summary = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": (
                "Summarize this conversation concisely. Preserve key facts, "
                "decisions, and open tasks:\n\n"
                f"{json.dumps(old, indent=2)}"
            )
        }]
    )
    # 用摘要取代舊對話，保留最近對話
    compacted = [{
        "role": "user",
        "content": f"[Conversation summary]\n{summary.content[0].text}"
    }] + recent
    save_session(session_key, compacted)
    return compacted

# ─── Command Queue ───

# 每個 session 使用獨立的執行緒鎖，避免並發衝突
session_locks = defaultdict(threading.Lock)

# ─── Agent Loop ───

def serialize_content(content):
    # 將 Anthropic API 的 content block 序列化為可 JSON 序列化的格式
    serialized = []
    for block in content:
        if hasattr(block, "text"):
            serialized.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            serialized.append({
                "type": "tool_use", "id": block.id,
                "name": block.name, "input": block.input
            })
    return serialized

def run_agent_turn(session_key, user_text, agent_config):
    """Run a full agent turn: load session, call LLM in a loop, save."""
    # 使用執行緒鎖保護會話操作
    with session_locks[session_key]:
        messages = load_session(session_key)
        messages = compact_session(session_key, messages)

        user_msg = {"role": "user", "content": user_text}
        messages.append(user_msg)
        append_message(session_key, user_msg)

        # ReAct 循環：最多 20 次工具使用
        for _ in range(20):  # max tool-use turns
            response = client.messages.create(
                model=agent_config["model"],
                max_tokens=4096,
                system=agent_config["soul"],
                tools=TOOLS,
                messages=messages
            )

            content = serialize_content(response.content)
            assistant_msg = {"role": "assistant", "content": content}
            messages.append(assistant_msg)
            append_message(session_key, assistant_msg)

            # LLM 決定結束對話（無更多工具呼叫）
            if response.stop_reason == "end_turn":
                return "".join(
                    b.text for b in response.content if hasattr(b, "text")
                )

            # LLM 請求使用工具
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"  🔧 {block.name}: {json.dumps(block.input)[:100]}")
                        result = execute_tool(block.name, block.input)
                        display = str(result)[:150]
                        print(f"     → {display}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result)
                        })

                # 將工具執行結果送回 LLM，讓 LLM 決定下一步
                results_msg = {"role": "user", "content": tool_results}
                messages.append(results_msg)
                append_message(session_key, results_msg)

        return "(max turns reached)"

# ─── Multi-Agent Routing ───

def resolve_agent(message_text):
    """Route messages to the right agent based on prefix commands."""
    # 根據前綴 /research 將任務路由到研究員 Agent
    if message_text.startswith("/research "):
        return "researcher", message_text[len("/research "):]
    return "main", message_text

# ─── Cron / Heartbeats ───

def setup_heartbeats():
    # 設定定時任務：每天早上 7:30 喚醒 Agent 執行檢查
    def morning_check():
        print("\n⏰ Heartbeat: morning check")
        result = run_agent_turn(
            "cron:morning-check",
            "Good morning! Check today's date and give me a motivational quote.",
            AGENTS["main"]
        )
        print(f"🤖 {result}\n")

    schedule.every().day.at("07:30").do(morning_check)

    # 背景執行緒每秒檢查是否有排程任務需要執行
    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(60)

    threading.Thread(target=scheduler_loop, daemon=True).start()

# ─── REPL ───

def main():
    # 建立必要的目錄
    for d in [WORKSPACE, SESSIONS_DIR, MEMORY_DIR]:
        os.makedirs(d, exist_ok=True)

    setup_heartbeats()

    session_key = "agent:main:repl"

    print("Mini OpenClaw")
    print(f"  Agents: {', '.join(a['name'] for a in AGENTS.values())}")
    print(f"  Workspace: {WORKSPACE}")
    print("  Commands: /new (reset), /research <query>, /quit\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            print("Goodbye!")
            break
        if user_input.lower() == "/new":
            # /new 指令：建立新的會話（時間戳記作為 session key）
            session_key = f"agent:main:repl:{datetime.now().strftime('%Y%m%d%H%M%S')}"
            print("  Session reset.\n")
            continue

        # 路由：決定由哪個 Agent 處理此訊息
        agent_id, message_text = resolve_agent(user_input)
        agent_config = AGENTS[agent_id]
        # main Agent 使用目前 session_key，其他 Agent 使用獨立 session
        sk = (
            f"{agent_config['session_prefix']}:repl"
            if agent_id != "main" else session_key
        )

        # 執行 Agent 回合
        response = run_agent_turn(sk, message_text, agent_config)
        print(f"\n🤖 [{agent_config['name']}] {response}\n")

if __name__ == "__main__":
    main()
