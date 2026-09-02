#!/usr/bin/env python3
# memory_manager.py - 為 agent.py 提供三層長期記憶
#
#   1. AGENT.md   —— 持久化的「使用者長期記憶」文字檔，每次啟動都會整份載入
#                     system prompt；模型可透過 remember_fact 工具主動寫入。
#   2. skills/    —— 技能庫。每個技能是一個資料夾，內含 SKILL.md，
#                     第一行用 `keywords: xxx, yyy` 宣告觸發關鍵字，
#                     命中時才把該技能內容注入當回合的 prompt（不會常駐，
#                     避免每次對話都塞爆 context）。
#   3. RAG        —— 用 Ollama embedding API 把每一輪「使用者訊息／模型回覆」
#                     都存成向量，之後每次提問前自動做語意相似度搜尋，
#                     把最相關的幾筆歷史記憶餵回模型。另外開放 recall_memory
#                     工具讓模型可以主動查詢。
#
# 需求：Ollama 需要先 pull 一個 embedding 模型，預設用 nomic-embed-text：
#     ollama pull nomic-embed-text

import os
import re
import json
import math
import sqlite3
import aiohttp

# ─── 路徑設定 ───

MEMORY_DIR = os.path.join(os.getcwd(), "memory")
AGENT_MD_PATH = os.path.join(MEMORY_DIR, "AGENT.md")
SKILLS_DIR = os.path.join(MEMORY_DIR, "skills")
RAG_DB_PATH = os.path.join(MEMORY_DIR, "rag_store.sqlite3")

EMBED_MODEL = "nomic-embed-text"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"

RAG_TOP_K = 4          # 每次自動檢索最多帶回幾筆
RAG_MIN_SIM = 0.55     # 相似度門檻，避免帶入不相關的雜訊

DEFAULT_AGENT_MD = """# AGENT.md — 長期記憶

這份檔案會在每次啟動 agent 時整份載入 system prompt，
可以想成是這個 agent 對「使用者」的長期認識。

Agent 可以透過 `remember_fact` 工具，在使用者要求「記住」某件事時，
自動把新的一行加到下面的清單。你也可以直接手動編輯這個檔案。

## 使用者偏好與事實
（目前還沒有記錄）
"""

DEFAULT_SKILL_MD = """keywords: 系統資訊, 系統狀態, cpu, 記憶體, ram, 磁碟, disk, 效能

# 技能：系統資訊查詢

當使用者詢問電腦目前的系統狀態（CPU、記憶體、磁碟空間、執行中的程序等）時：

1. 優先用單一、非互動、會自動結束的指令一次取得需要的資訊
   （例如 Linux 用 `free -h`、`df -h`、`top -bn1 | head -20`）。
2. 不要使用 `top`、`htop` 等預設會持續刷新的指令，除非加上讓它自動結束的參數
   （像 `-bn1`）。
3. 拿到 shell 輸出後，用自然語言摘要重點給使用者看，不要整段貼原始輸出。
"""


# ─── AGENT.md：讀取 / 寫入 ───

def ensure_memory_dirs():
    """確保 memory/、memory/skills/ 存在，AGENT.md 不存在時建立預設版本。"""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    os.makedirs(SKILLS_DIR, exist_ok=True)
    if not os.path.exists(AGENT_MD_PATH):
        with open(AGENT_MD_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_AGENT_MD)


def load_agent_md() -> str:
    """讀出 AGENT.md 全文，供組 system prompt 使用。"""
    ensure_memory_dirs()
    with open(AGENT_MD_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def append_agent_md(fact: str) -> None:
    """把一則新事實加到 AGENT.md 末尾（一行一個項目）。"""
    ensure_memory_dirs()
    fact = fact.strip()
    if not fact:
        return
    with open(AGENT_MD_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n- {fact}")


# ─── skills：載入 / 比對 ───

def _parse_skill(text: str):
    """從 SKILL.md 內容解析出 keywords 清單與正文。

    格式：第一行（或前幾行內任何一行）寫
        keywords: 關鍵字1, 關鍵字2
    之後的全部內容當作技能正文。
    """
    keywords = []
    lines = text.splitlines()
    body_start = 0
    for i, line in enumerate(lines[:5]):  # 只在檔案開頭找 keywords 宣告
        m = re.match(r"^\s*keywords\s*[:：]\s*(.+)$", line, re.IGNORECASE)
        if m:
            keywords = [k.strip() for k in re.split(r"[,，]", m.group(1)) if k.strip()]
            body_start = i + 1
            break
    body = "\n".join(lines[body_start:]).strip() or text.strip()
    return keywords, body


def ensure_example_skill():
    """第一次執行時放一個範例技能，讓使用者知道格式長怎樣。"""
    example_dir = os.path.join(SKILLS_DIR, "system_info")
    example_md = os.path.join(example_dir, "SKILL.md")
    if not os.path.exists(example_md):
        os.makedirs(example_dir, exist_ok=True)
        with open(example_md, "w", encoding="utf-8") as f:
            f.write(DEFAULT_SKILL_MD)


def load_skills() -> list:
    """掃描 memory/skills/*/SKILL.md，回傳 [{name, keywords, body}, ...]。"""
    ensure_memory_dirs()
    ensure_example_skill()
    skills = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, name)
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if os.path.isdir(skill_dir) and os.path.isfile(skill_md):
            with open(skill_md, "r", encoding="utf-8") as f:
                text = f.read()
            keywords, body = _parse_skill(text)
            skills.append({"name": name, "keywords": keywords, "body": body})
    return skills


def match_skills(user_input: str, skills: list, max_skills: int = 2) -> list:
    """用簡單的關鍵字比對（不需要模型），命中就把技能加入本回合 context。"""
    hits = []
    low = user_input.lower()
    for sk in skills:
        for kw in sk["keywords"]:
            if kw and kw.lower() in low:
                hits.append(sk)
                break
    return hits[:max_skills]


# ─── RAG：embedding + sqlite 向量儲存 ───

def _init_db() -> sqlite3.Connection:
    ensure_memory_dirs()
    conn = sqlite3.connect(RAG_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding TEXT NOT NULL,
            ts TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


async def embed_text(text: str) -> list:
    """呼叫 Ollama /api/embed 取得向量。任何錯誤都往外拋，由呼叫端決定怎麼處理。"""
    payload = {"model": EMBED_MODEL, "input": text}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            OLLAMA_EMBED_URL, json=payload, timeout=aiohttp.ClientTimeout(total=30)
        ) as resp:
            data = await resp.json()
            embs = data.get("embeddings")
            if embs and isinstance(embs, list):
                return embs[0]
            # 舊版 API 可能用 "embedding" 這個 key
            return data.get("embedding", [])


async def add_memory(role: str, text: str) -> None:
    """把一則訊息嵌入向量後存進 sqlite。embedding 失敗時安靜略過，不影響主流程。"""
    text = (text or "").strip()
    if not text:
        return
    try:
        vec = await embed_text(text)
    except Exception as e:
        print(f"⚠️  記憶嵌入失敗（略過此筆，不影響對話）：{e}")
        return
    if not vec:
        return
    conn = _init_db()
    try:
        conn.execute(
            "INSERT INTO memories (role, text, embedding) VALUES (?, ?, ?)",
            (role, text, json.dumps(vec)),
        )
        conn.commit()
    finally:
        conn.close()


def _cosine(a: list, b: list) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def search_memory(query: str, top_k: int = RAG_TOP_K, min_sim: float = RAG_MIN_SIM) -> list:
    """回傳最相關的記憶列表：[(sim, role, text, ts), ...]，依相似度由高到低排序。"""
    conn = _init_db()
    try:
        rows = conn.execute("SELECT role, text, embedding, ts FROM memories").fetchall()
    finally:
        conn.close()
    if not rows:
        return []
    try:
        qvec = await embed_text(query)
    except Exception:
        return []
    if not qvec:
        return []

    scored = []
    for role, text, emb_json, ts in rows:
        try:
            emb = json.loads(emb_json)
        except Exception:
            continue
        sim = _cosine(qvec, emb)
        if sim >= min_sim:
            scored.append((sim, role, text, ts))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def memory_stats() -> str:
    """給 /memory 指令用：回傳目前記憶庫的簡單統計。"""
    ensure_memory_dirs()
    conn = _init_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    finally:
        conn.close()
    skills = load_skills()
    return (
        f"AGENT.md：{AGENT_MD_PATH}\n"
        f"技能庫：{len(skills)} 個技能（{', '.join(s['name'] for s in skills) or '無'}）\n"
        f"RAG 記憶筆數：{count} 筆（{RAG_DB_PATH}）"
    )
