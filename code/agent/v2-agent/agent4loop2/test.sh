#!/bin/bash
# test.sh - 劇本測試：模擬使用者與 planner→executor→evaluator 分工 agent 對話
# 用法：cd agent4loop2 && ./test.sh   （需要 Ollama + qwen3.5:2b）
set -x

PROBE="ROLESPROBE_66"
OUT="$(mktemp)"

# 劇本順序：
#   1) 要求用 run_shell 執行 echo 探針（驗證 pipeline：規劃→執行→評估→task_done）
#   2) /roles 檢視角色調度
#   3) /quit 結束
printf '請用 run_shell 執行 echo %s ，並回報輸出結果\n/roles\n/quit\n' "$PROBE" \
    | timeout 300 python3 agent4loop2.py > "$OUT" 2>&1

PASS=1

# 1) echo 任務完成：探針內容出現在輸出
if grep -q "$PROBE" "$OUT"; then
    echo "[PASS] echo 任務被執行且內容正確"
else
    echo "[FAIL] 未偵測到探針內容"
    PASS=0
fi

# 2) 三位角色都有出場（Planner / Executor / Evaluator 標記）
if grep -q "Planner" "$OUT" && grep -q "Executor" "$OUT" && grep -q "Evaluator" "$OUT"; then
    echo "[PASS] 三位角色標記都出現"
else
    echo "[FAIL] 角色標記遺漏"
    PASS=0
fi

# 3) 工具真的有被執行（⚙️ 標記 + run_shell）
if grep -q "⚙️" "$OUT"; then
    echo "[PASS] Executor 有執行工具"
else
    echo "[FAIL] 未偵測到工具執行標記"
    PASS=0
fi

# 4) /roles 印出調度記錄
if grep -q "分工迴圈" "$OUT" && grep -q "調度記錄" "$OUT"; then
    echo "[PASS] /roles 印出調度狀態"
else
    echo "[FAIL] /roles 輸出遺漏"
    PASS=0
fi

# 5) 所有對話都有回覆
if grep -q "沒有取得回覆內容" "$OUT"; then
    echo "[FAIL] 出現無回覆保險輸出"
    PASS=0
else
    echo "[PASS] 所有對話都有回覆內容"
fi

# 6) /quit 正常結束
if grep -q "再見" "$OUT"; then
    echo "[PASS] /quit 正常結束"
else
    echo "[FAIL] 未偵測到結束訊息"
    PASS=0
fi

echo "===== 對話輸出 ====="
cat "$OUT"
rm -f "$OUT"

if [ "$PASS" -eq 1 ]; then
    echo "SCENARIO TEST PASSED"
else
    echo "SCENARIO TEST FAILED"
    exit 1
fi