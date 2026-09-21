#!/bin/bash
# test.sh - 劇本測試：模擬使用者與 agent 對話，驗證問答結果是否符合預期
# 用法：cd agent2context && ./test.sh   （需要 Ollama + qwen3.5:2b）
set -x

PROBE="TOOLPROBE_4242"
OUT="$(mktemp)"

# 劇本：依序扮演使用者丟問題，最後 /ctx 檢視脈絡、/quit 結束
printf '你好，請簡單自我介紹\n請用 run_shell 執行 echo %s ，並回報輸出結果\n/ctx\n/quit\n' "$PROBE" \
    | timeout 180 python3 agent2context.py > "$OUT" 2>&1

PASS=1

# 1) 工具真的有被執行：echo 的探針值要出現在輸出中
if grep -q "$PROBE" "$OUT"; then
    echo "[PASS] run_shell 工具被執行並回傳預期輸出"
else
    echo "[FAIL] 未偵測到 run_shell 執行 ${PROBE}"
    PASS=0
fi

# 2) tool 迴圈有把結果送回模型（探針值同時來自「執行」與「回答」兩處）
if grep -q "⚙️" "$OUT"; then
    echo "[PASS] 偵測到工具執行標記"
else
    echo "[FAIL] 未偵測到工具執行標記（⚙️）"
    PASS=0
fi

# 3) /ctx 有印出組裝好的上下文（工具 schema 與系統提示）
if grep -q "工具 schema" "$OUT" && grep -q "run_shell" "$OUT"; then
    echo "[PASS] /ctx 印出工具 schema"
else
    echo "[FAIL] /ctx 未包含工具 schema"
    PASS=0
fi

# 4) 一般問答有非空回覆（沒有觸發「無回覆」保險）
if grep -q "沒有取得回覆內容" "$OUT"; then
    echo "[FAIL] 出現無回覆的保險輸出"
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