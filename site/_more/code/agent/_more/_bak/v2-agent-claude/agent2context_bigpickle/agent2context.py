#!/usr/bin/env python3
# agent2context.py - AI Agent 的 Context Engineering 版，所有上下文資料全部存在 sqlite
# Run: python agent2context.py
#
# 設計重點（相對於 agent1prompt.py 的新增）：
#   1. 保留 Ollama 原生的 tools / tool_calls 機制、thinking 串流、shell 工具。
#   2. 加入 Context Engineering 的四種機制，全部集中放在單一 sqlite 資料庫
#      （context.sqlite3），不需要再管理散落的 .md 檔案：
#        - AGENT.md ：常駐的長期記憶，每次啟動整份塞進 system prompt。
#        - SKILL    ：技能庫，依關鍵字命中該輪才注入 prompt。
#        - MEMORY   ：每輪對話自動存入資料庫，形成可回想的軌跡。
#        - RAG      ：用 embedding 把記憶變成向量，語意檢索最相關的幾筆。
#   3. 模型本身也可以寫資料庫：remember_fact 記住使用者偏好、
#      add_skill 把「怎麼做事」變成技能存回資料庫、recall_memory 主動回想。
#
# 前置需求：
#   ollama pull qwen3.5:2b        (chat 模型)
#   ollama pull nomic-embed-text  (embedding 模型，純 RAG 用，沒有也能跑)

import asyncio
import aiohttp
import json
import math
import os
import sqlite3
import subprocess

# ─── Configuration ───

MODEL = "qwen3.5:2b"
WORKSPACE = os.getcwd()
DB_PATH = os.path.join(WORKSPACE, "context.sqlite3")
EMBED_MODEL = "nomic-embed-text"
MAX_TOOL_TURNS = 5
HISTORY_MESSAGES = 12
SHELL_TIMEOUT = 30
RAG_TOP_K = 4
RAG_MIN_SIM = 0.5

GRAY = "\033[90m"
RESET = "\033[0m"

BASE_SYSTEM_PROMPT = (
    "你是 Jarvis，一個運行在使用者電腦上的 AI 助理，擁有長期記憶。\n"
    "一般聊天、問答不需要呼叫任何工具，直接自然語言回答即可。\n"
    "只有在真的需要操作檔案、查詢系統資訊、執行程式時，才呼叫 run_shell 工具。\n"
    "不要使用不會自動結束的指令（例如 tail -f、持續監聽的伺服器）。\n"
    "\n"
    "系統會在『使用者訊息』前面附上 [背景資訊] 區塊，這是從長期記憶\n"
    "（AGENT.md、技能庫、過去的對話）自動檢索出來的參考資料，直接當作\n"
    "你已知的知識來用即可，不必在回覆裡特別說『這是背景資訊』。\n"
    "\n"
    "記憶相關工具：\n"
    "- 當使用者明確要你『記住』某件事，或透露重要的個人偏好／事實時，"
    "呼叫 remember_fact。\n"
    "- 當使用者問到過去討論過的事、而背景資訊不夠清楚時，"
    "呼叫 recall_memory 主動搜索。\n"
    "- 當你發現某個『做法／流程』值得保存，可呼叫 add_skill，"
    "之後遇到關鍵字會自動拿出來用。"
)

# ─── SQLite：Context Store ───
# 整個 context engineering 的資料都統一放在一個資料庫裡：
#   AGENT.md   -> meta 表（key='agent.md'）
#   SKILL      -> skills 表
#   MEMORY/RAG -> memories 表（角色、內容、向量）

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skills (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT UNIQUE NOT NULL,
    keywords  TEXT NOT NULL DEFAULT '',
    body      TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS memories (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    role      TEXT NOT NULL,               -- user / assistant / fact
    text      TEXT NOT NULL,
    embedding TEXT,                        -- JSON 陣列，RAG 用
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

DEFAULT_AGENT_MD = (
    "# AGENT.md — 使用者長期記憶\n\n"
    "每輪啟動都會整份載入 system prompt，代表 Agent 對使用者的長期認識。\n"
    "可以透過 remember_fact 工具、或 REPL 的 /remember 指令追加新事實。\n\n"
    "## 使用者偏好與事實\n"
    "（目前還沒有記錄）"
)

DEFAULT_SKILLS = [
    {
        "name": "system_info",
        "keywords": "系統資訊,系統狀態,cpu,記憶體,ram,磁碟,disk,效能,記憶體使用",
        "body": (
            "當使用者詢問電腦目前的系統狀態（CPU、記憶體、磁碟空間、執行中的程序）時：\n"
            "1. 用單一、非互動、會自動結束的指令一次取得資訊\n"
            "   （例如 macOS 用 `top -l 1 | head -15`、`df -h`；Linux 用 `free -h`、`df -h`）。\n"
            "2. 避免 `top`、`htop` 這類會持續刷新的指令，除非加上自動結束的參數。\n"
            "3. 拿到輸出後用自然語言摘要重點，不要把整段原始輸出貼回給使用者。"
        ),
    },
]


def connect() -> sqlite3.Connection:
    os.makedirs(WORKSPACE, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """建立 schema，並在首次啟動時填滿預設的 AGENT.md 與範例技能。"""
    with connect() as conn:
        conn.executescript(SCHEMA)
        if not conn.execute("SELECT 1 FROM meta WHERE key='agent.md'").fetchone():
            conn.execute(
                "INSERT INTO meta (key, value) VALUES ('agent.md', ?)",
                (DEFAULT_AGENT_MD,),
            )
        if conn.execute("SELECT COUNT(*) AS c FROM skills").fetchone()["c"] == 0:
            for sk in DEFAULT_SKILLS:
                conn.execute(
                    "INSERT INTO skills (name, keywords, body) VALUES (?, ?, ?)",
                    (sk["name"], sk["keywords"], sk["body"]),
                )
        conn.commit()


# ═══ AGENT.md：長期記憶 ═══

def load_agent_md() -> str:
    with connect() as conn:
        row = conn.execute(
            "SELECT value FROM meta WHERE key='agent.md'"
        ).fetchone()
        return row["value"].strip() if row else "（空白）"


def append_agent_md(fact: str) -> None:
    """把一則新事實寫進 AGENT.md，之後每次啟動都會自動載入。"""
    fact = fact.strip()
    if not fact:
        return
    with connect() as conn:
        row = conn.execute(
            "SELECT value FROM meta WHERE key='agent.md'"
        ).fetchone()
        value = (row["value"] if row else DEFAULT_AGENT_MD).rstrip()
        conn.execute(
            "UPDATE meta SET value = ? WHERE key = 'agent.md'",
            (value + "\n- " + fact,),
        )
        conn.commit()


# ═══ SKILL：技能庫 ═══

def load_skills() -> list:
    with connect() as conn:
        rows = conn.execute(
            "SELECT name, keywords, body FROM skills ORDER BY name"
        ).fetchall()
    skills = []
    for r in rows:
        keywords = [k.strip() for k in (r["keywords"] or "").split(",") if k.strip()]
        skills.append({"name": r["name"], "keywords": keywords, "body": r["body"]})
    return skills


def save_skill(name: str, keywords: str, body: str) -> str:
    """新增或更新一個技能。keywords 用逗號分隔。"""
    name = (name or "").strip()
    body = (body or "").strip()
    keywords = ",".join([k.strip() for k in (keywords or "").split(",") if k.strip()])
    if not name or not body:
        return "技能需要至少提供 name 與 body。"
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO skills (name, keywords, body) VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                keywords = excluded.keywords,
                body = excluded.body
            """,
            (name, keywords, body),
        )
        conn.commit()
    return f"技能「{name}」已存入資料庫。"


def match_skills(user_input: str, skills: list, max_skills: int = 2) -> list:
    """關鍵字命中就注入本回合 context，沒命中就不佔空間。"""
    hits = []
    low = user_input.lower()
    for sk in skills:
        if any(kw and kw.lower() in low for kw in sk["keywords"]):
            hits.append(sk)
    return hits[:max_skills]


# ═══ MEMORY + RAG：向量化記憶 ═══

async def embed_text(text: str) -> list:
    """呼叫 Ollama /api/embed 把一段文字變成向量。"""
    payload = {"model": EMBED_MODEL, "input": text}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/embed",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            data = await resp.json()
            embs = data.get("embeddings")
            if embs and isinstance(embs, list):
                return embs[0]
            return data.get("embedding", [])


async def add_memory(role: str, text: str, need_embed: bool = True) -> None:
    """把一則訊息（或其向量）存入 memories 表。embedding 失敗時只存文字、不影響對話。"""
    text = (text or "").strip()
    if not text:
        return
    embedding = None
    if need_embed:
        try:
            embedding = await embed_text(text)
            embedding = json.dumps(embedding)
        except Exception as e:
            print(f"⚠️  embedding 失敗（此筆只存文字）：{e}")
    with connect() as conn:
        conn.execute(
            "INSERT INTO memories (role, text, embedding) VALUES (?, ?, ?)",
            (role, text, embedding),
        )
        conn.commit()


def _cosine(a: list, b: list) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def search_memory(query: str) -> list:
    """語意檢索：回傳 [(相似度, role, text), ...] 由高到低。"""
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, text, embedding FROM memories WHERE embedding IS NOT NULL"
        ).fetchall()
    if not rows:
        return []
    try:
        qvec = await embed_text(query)
    except Exception:
        return []
    if not qvec:
        return []

    scored = []
    for r in rows:
        try:
            vec = json.loads(r["embedding"])
        except Exception:
            continue
        sim = _cosine(qvec, vec)
        if sim >= RAG_MIN_SIM:
            scored.append((sim, r["role"], r["text"]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:RAG_TOP_K]


def memory_stats() -> str:
    with connect() as conn:
        mem = conn.execute("SELECT COUNT(*) AS c FROM memories").fetchone()["c"]
        skills = conn.execute("SELECT COUNT(*) AS c FROM skills").fetchone()["c"]
        agent = conn.execute(
            "SELECT length(value) AS l FROM meta WHERE key='agent.md'"
        ).fetchone()["l"]
    return (
        f"資料庫：{DB_PATH}\n"
        f"AGENT.md：{agent} 字元\n"
        f"技能庫：{skills} 個技能\n"
        f"記憶（MEMORY）：{mem} 筆"
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
                    "command": {"type": "string", "description": "要執行的 shell 指令"},
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
                "把使用者明確要求記住的事實或個人偏好寫入長期記憶（AGENT.md）。"
                "寫入後之後每次啟動都會自動載入。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "要記住的一句話事實"},
                },
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": (
                "在過去的對話與事實記憶中做語意搜尋，回傳最相關的幾筆內容。"
                "適合『你記得我之前說...』這類問題。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "想找的關鍵字或問題"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_skill",
            "description": (
                "把一個『做法／流程』儲存成技能到資料庫。之後使用者輸入命中關鍵字時，"
                "該技能內容會自動被注入上下文。keywords 用逗號分隔。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "技能名稱（英文短名）"},
                    "keywords": {"type": "string", "description": "觸發關鍵字，逗號分隔，例如 'git, 版本控制'"},
                    "body": {"type": "string", "description": "技能的操作步驟說明"},
                },
                "required": ["name", "keywords", "body"],
            },
        },
    },
]


def run_shell(command: str) -> str:
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
    fact = (fact or "").strip()
    if not fact:
        return "沒有收到要記住的內容。"
    append_agent_md(fact)
    asyncio.run(add_memory("fact", fact))
    print(f"\n🧠 已寫入 AGENT.md：{fact}\n")
    return f"已記住：「{fact}」已寫入長期記憶。"


def recall_memory(query: str) -> str:
    query = (query or "").strip()
    if not query:
        return "沒有收到要搜尋的內容。"
    hits = asyncio.run(search_memory(query))
    if not hits:
        return "沒有找到相關的歷史記憶。"
    lines = "\n".join(f"- ({role}) {text}" for _sim, role, text in hits)
    print(f"\n🔎 recall_memory({query!r}) 找到 {len(hits)} 筆\n")
    return f"找到以下相關記憶：\n{lines}"


def add_skill(name: str, keywords: str, body: str) -> str:
    msg = save_skill(name, keywords, body)
    print(f"\n🛠️  {msg}\n")
    return msg


TOOL_IMPLS = {
    "run_shell": lambda args: run_shell(args.get("command", "")),
    "remember_fact": lambda args: remember_fact(args.get("fact", "")),
    "recall_memory": lambda args: recall_memory(args.get("query", "")),
    "add_skill": lambda args: add_skill(
        args.get("name", ""), args.get("keywords", ""), args.get("body", "")
    ),
}


# ─── Ollama API（streaming + thinking 顯示 + tool_calls） ───

async def call_ollama(messages: list) -> dict:
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


# ─── Context Engineering：組出 system prompt 與每輪背景資訊 ───

def build_system_message() -> dict:
    agent_md = load_agent_md()
    body = (
        BASE_SYSTEM_PROMPT
        + "\n\n---\n"
        + "# 使用者長期記憶（AGENT.md，儲存於 sqlite）\n"
        + agent_md
    )
    return {"role": "system", "content": body}


async def build_turn_context(user_input: str, skills: list) -> str:
    """把這輪要注入的『背景資訊』組起來：命中的技能 + RAG 相關記憶。"""
    parts = []

    for sk in match_skills(user_input, skills):
        keywords = ", ".join(sk["keywords"])
        parts.append(f"[技能：{sk['name']}（關鍵字：{keywords}）]\n{sk['body']}")

    try:
        hits = await search_memory(user_input)
    except Exception:
        hits = []
    if hits:
        recalled = "\n".join(f"- ({role}) {text}" for _sim, role, text in hits)
        parts.append(f"[可能與過去記憶相關]\n{recalled}")

    return "\n\n".join(parts)


# ─── Agent Loop ───

def trim_history(messages: list) -> list:
    system_msg = messages[0]
    rest = messages[1:]
    if len(rest) > HISTORY_MESSAGES:
        rest = rest[-HISTORY_MESSAGES:]
    return [system_msg] + rest


def handle_turn(messages: list, user_input: str, skills: list) -> str:
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
            messages.append({
                "role": "assistant",
                "content": result["content"],
                "tool_calls": result["tool_calls"],
            })
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
            continue

        final_answer = result["content"]
        break
    else:
        final_answer = f"（已達最多 {MAX_TOOL_TURNS} 輪工具呼叫，先在此停止。）"

    messages[user_msg_index]["content"] = user_input

    if final_answer:
        messages.append({"role": "assistant", "content": final_answer})

    # 把這輪的使用者輸入與回覆存進 sqlite 記憶
    asyncio.run(add_memory("user", user_input))
    if final_answer:
        asyncio.run(add_memory("assistant", final_answer))

    return final_answer


def show_sql(query: str):
    """/sql 指令用：把 sqlite 查詢結果印成簡易表格。"""
    if not query.strip():
        print("用法：/sql SELECT ...\n")
        return
    with connect() as conn:
        try:
            rows = conn.execute(query).fetchall()
        except Exception as e:
            print(f"sql 錯誤：{e}\n")
            return
    if not rows:
        print("（查無結果）\n")
        return
    headers = rows[0].keys() if rows else []
    print(" | ".join(headers))
    for r in rows:
        print(" | ".join(str(r[k]) for k in headers))
    print(f"共 {len(rows)} 列\n")


def main():
    init_db()
    skills = load_skills()
    messages = [build_system_message()]

    print(f"Agent - {MODEL}")
    print(f"工作區：{WORKSPACE}")
    print(f"Context Store：{DB_PATH}")
    print("指令：/quit 結束、/clear 清空對話歷史、/memory 看記憶統計、"
          "/remember <內容> 記住事實、/skills 看技能、/sql <查詢> 查資料庫\n")

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
            print("對話歷史已清空（資料庫記憶不受影響）。\n")
            continue
        if user_input.lower() == "/memory":
            print(memory_stats() + "\n")
            continue
        if user_input.lower() == "/skills":
            names = ", ".join(s["name"] for s in load_skills()) or "（無）"
            print(f"技能庫：{names}\n")
            continue
        if user_input.startswith("/remember "):
            print(remember_fact(user_input[len("/remember "):]) + "\n")
            continue
        if user_input.startswith("/sql"):
            show_sql(user_input[len("/sql"):].strip())
            continue
        if user_input.startswith("/agent"):
            print(load_agent_md() + "\n")
            continue

        answer = handle_turn(messages, user_input, skills)
        if not answer:
            print("🤖 （沒有取得回覆內容）\n")
        messages = trim_history(messages)
        skills = load_skills()  # 模型可能透過 add_skill 新增了技能


if __name__ == "__main__":
    main()