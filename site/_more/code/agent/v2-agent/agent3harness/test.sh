#!/bin/bash
# test.sh - 劇本測試：模擬使用者與 harness 版 agent 對話，驗證問答結果是否符合預期
# 用法：cd agent3harness && ./test.sh   （需要 Ollama + qwen3.5:2b）
set -x

PROBE="HARNESSPROBE_5150"
OUT="$(mktemp)"

# 劇本順序：
#   1) 一般問答（不需工具）
#   2) 要求執行 echo 探針 → 驗證 harness 真的執行了指令
#   3) 要求執行 tail -f → 驗證 harness 安全規則擋下且不死循環
#   4) /harness 檢視組態
#   5) /quit 結束
printf '你好，請簡單自我介紹\n請用 run_shell 執行 echo %s ，並回報輸出結果\n請用 run_shell 執行 tail -f /dev/null\n/harness\n/quit\n' "$PROBE" \
    | timeout 240 python3 agent3harness.py > "$OUT" 2>&1

PASS=1

# 1) 探針被執行（harness 真的跑出 echo 結果）
if grep -q "$PROBE" "$OUT"; then
    echo "[PASS] run_shell 被執行並回傳預期輸出"
else
    echo "[FAIL] 未偵測到 echo 探針輸出"
    PASS=0
fi

# 2) tail -f 被安全規則擋下（出現拒絕理由，且沒有卡死）
if grep -q "安全規則拒絕" "$OUT"; then
    echo "[PASS] 禁止指令被 harness 擋下"
else
    echo "[FAIL] tail -f 未被子 harness 拒絕"
    PASS=0
fi

# 3) /harness 印出組態（含禁止樣式）
if grep -q "Execution Harness 組態" "$OUT" && grep -q "禁止的指令樣式" "$OUT"; then
    echo "[PASS] /harness 印出組態"
else
    echo "[FAIL] /harness 組態輸出遺漏"
    PASS=0
fi

# 4) 所有對話都有回覆
if grep -q "沒有取得回覆內容" "$OUT"; then
    echo "[FAIL] 出現無回覆保險輸出"
    PASS=0
else
    echo "[PASS] 所有對話都有回覆內容"
fi

# 5) /quit 正常結束
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