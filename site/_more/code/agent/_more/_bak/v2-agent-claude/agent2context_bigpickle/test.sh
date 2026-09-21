#!/bin/bash
# test.sh - 自動測試 agent2context.py
#   測試直接「在目前目錄」執行，測試後 context.sqlite3 會留在這個目錄，
#   方便直接觀察 /sql 查詢的結果。
#   測試項目：
#     1. Python 語法檢查
#     2. sqlite 初始化（schema / AGENT.md seed / SKILL seed）
#     3. AGENT.md 追加事實 + system prompt 組合
#     4. SKILL 儲存 / 載入 / 關鍵字命中
#     5. MEMORY + RAG（stub embedding 語意檢索 + build_turn_context）
#     6. /sql 查詢指令
#     7. 實際 Agent 對話（Ollama 有 qwen3.5:2b 才測）
# Run: ./test.sh
set -x

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# 先刪掉舊的測試資料庫，確保從乾淨狀態開始測試
rm -f context.sqlite3

# 1. Python 語法檢查
python3 -m py_compile agent2context.py || exit 1

# 2. sqlite 初始化：建表 + 預設 AGENT.md + 範例技能
PYTHONPATH="$SCRIPT_DIR" python3 - <<'EOF' || exit 1
import agent2context as a
a.init_db()

assert a.load_agent_md().startswith("# AGENT.md"), "AGENT.md seed 失敗"
names = [s["name"] for s in a.load_skills()]
assert "system_info" in names, "skills seed 失敗"
print("PASS: init_db + AGENT.md seed + skill seed")
EOF

# 3. AGENT.md 追加事實 + system prompt 應包含 AGENT.md
PYTHONPATH="$SCRIPT_DIR" python3 - <<'EOF' || exit 1
import agent2context as a
a.init_db()
a.append_agent_md("使用者喜歡喝咖啡")
assert "喜歡喝咖啡" in a.load_agent_md(), "append_agent_md 失敗"
sys_msg = a.build_system_message()
assert "喜歡喝咖啡" in sys_msg["content"], "system prompt 未含 AGENT.md"
print("PASS: append_agent_md + build_system_message")
EOF

# 4. SKILL：儲存 / 載入 / 關鍵字命中
PYTHONPATH="$SCRIPT_DIR" python3 - <<'EOF' || exit 1
import agent2context as a
a.init_db()
ret = a.save_skill("git_ops", "git,版本控制", "用 git status 看狀態")
assert "已存入" in ret, "save_skill 失敗"
skills = a.load_skills()
assert any(s["name"] == "git_ops" for s in skills), "load_skills 缺新技能"
hits = a.match_skills("幫我看看 git 狀態", skills)
assert any(s["name"] == "git_ops" for s in hits), "match_skills 未命中關鍵字"
print("PASS: save_skill + load_skills + match_skills")
EOF

# 5. MEMORY + RAG（替換成 stub embedding，不依賴 Ollama）
PYTHONPATH="$SCRIPT_DIR" python3 - <<'EOF' || exit 1
import asyncio
import agent2context as a
a.init_db()

async def stub_embed(text):
    return [float(len(text)), 1.0, 0.5]
a.embed_text = stub_embed

asyncio.run(a.add_memory("user", "昨天學了 git rebase 用法", need_embed=True))
asyncio.run(a.add_memory("assistant", "rebase 是把分支重新排列基底", need_embed=True))
hits = asyncio.run(a.search_memory("rebase"))
assert hits, "RAG 檢索無結果"

ctx = asyncio.run(a.build_turn_context("rebase 是什麼", a.load_skills()))
assert "rebase" in ctx, "build_turn_context 未帶入 RAG 記憶"
print("PASS: add_memory + search_memory + build_turn_context (RAG)")
EOF

# 6. /sql 查詢指令
PYTHONPATH="$SCRIPT_DIR" python3 - <<'EOF' || exit 1
import agent2context as a
a.init_db()
a.show_sql("SELECT name, keywords FROM skills")
print("PASS: show_sql")
EOF

# 7. 實際 Agent 對話（只在 Ollama 有模型時測試）
if ollama list 2>/dev/null | grep -q "qwen3.5:2b"; then
    printf '你好\n/memory\n/quit\n' | python3 "$SCRIPT_DIR/agent2context.py" 2>&1 \
        | grep -q "再見" && echo "PASS: agent 對話正常" || echo "WARN: agent 對話異常（查看上方輸出）"
else
    echo "SKIP: Ollama 沒有 qwen3.5:2b，不測實際對話"
fi

set +x
echo
echo "ALL TESTS DONE"
echo "可在這個目錄看到測試用的資料庫：$(ls context.sqlite3 2>/dev/null || echo '（未建立）')"