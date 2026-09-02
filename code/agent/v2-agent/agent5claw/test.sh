#!/bin/bash
# test.sh - 劇本測試：模擬使用者與 agent5claw（OpenClaw 式萬用 agent）對話
# 用法：cd agent5claw && ./test.sh   （需要 Ollama + qwen3.5:2b）
set -x

PROBE="CLAWPROBE_88"
MEM="$(mktemp -d)/claw_memory.md"
OUT="$(mktemp)"

export CLAW_MEMORY_FILE="$MEM"

# ─── 第一次會話：工具執行 + 記憶寫入 + 技能 + 授權模式 ───
printf '請用 run_shell 執行 echo %s ，並回報輸出結果\n/remember 事實 使用者的暱稱是小龍\n/memory\n/skills\n/skill sysinfo\n/approval\n/quit\n' "$PROBE" \
    | timeout 300 python3 agent5claw.py > "$OUT" 2>&1

PASS=1

# 1) echo 探針真的有被 run_shell 執行
if grep -q "$PROBE" "$OUT"; then
    echo "[PASS] run_shell 執行 echo 探針"
else
    echo "[FAIL] 未偵測到 echo 探針輸出"
    PASS=0
fi

# 2) /remember 把記憶寫入
if grep -q "已記入" "$OUT" && grep -q "小龍" "$OUT"; then
    echo "[PASS] /remember 寫入記憶"
else
    echo "[FAIL] /remember 未寫入"
    PASS=0
fi

# 3) /memory 顯示持久記憶
if grep -q "使用者的暱稱是小龍" "$OUT"; then
    echo "[PASS] /memory 顯示記憶"
else
    echo "[FAIL] /memory 未顯示記憶"
    PASS=0
fi

# 4) /skills 列出技能
if grep -q "sysinfo" "$OUT" && grep -q "search" "$OUT" && grep -q "read_file" "$OUT"; then
    echo "[PASS] /skills 列出技能表"
else
    echo "[FAIL] /skills 技能表遺漏"
    PASS=0
fi

# 5) /skill sysinfo 真的執行
if grep -q "OS:" "$OUT"; then
    echo "[PASS] /skill sysinfo 執行"
else
    echo "[FAIL] /skill sysinfo 無輸出"
    PASS=0
fi

# 6) /approval 顯示目前授權模式
if grep -q "授權模式" "$OUT"; then
    echo "[PASS] /approval 顯示模式"
else
    echo "[FAIL] /approval 輸出遺漏"
    PASS=0
fi

echo "===== 第一次會話輸出 ====="
cat "$OUT"

# 清除用不到的暫存輸出，重新開一個 session 驗證持久化外掛
OUT2="$(mktemp)"

# ─── 第二次會話（全新 process，同一記憶檔）：記憶要跨 session 存活 ───
printf '/memory\n/quit\n' | timeout 120 python3 agent5claw.py > "$OUT2" 2>&1

if grep -q "使用者的暱稱是小龍" "$OUT2"; then
    echo "[PASS] 記憶跨 session 持久化"
else
    echo "[FAIL] 記憶未在第二個 session 出現"
    PASS=0
fi

echo "===== 第二次會話輸出（持久化驗證） ====="
cat "$OUT2"

rm -f "$OUT" "$OUT2" "$MEM"

if [ "$PASS" -eq 1 ]; then
    echo "SCENARIO TEST PASSED"
else
    echo "SCENARIO TEST FAILED"
    exit 1
fi