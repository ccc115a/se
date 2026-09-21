#!/bin/bash
# test.sh - 劇本測試：模擬使用者與 v1 (agent1prompt) agent 對話
# 用法：cd agent1prompt && ./test.sh   （需要 Ollama + qwen3.5:2b）
set -x

PROBE="AGENT1PROBE_88"
OUT="$(mktemp)"

printf '你好，請簡單自我介紹\n請用 run_shell 執行 echo %s ，並回報輸出結果\n/quit\n' "$PROBE" \
    | timeout 240 python3 agent1prompt.py > "$OUT" 2>&1

PASS=1

# 1) 工具被執行：echo 探針出現在輸出
if grep -q "$PROBE" "$OUT"; then
    echo "[PASS] run_shell 被執行並回傳預期輸出"
else
    echo "[FAIL] 未偵測到 echo 探針輸出"
    PASS=0
fi

# 2) 工具執行標記
if grep -q "⚙️" "$OUT"; then
    echo "[PASS] 偵測到工具執行標記"
else
    echo "[FAIL] 未偵測到工具執行標記"
    PASS=0
fi

# 3) 所有對話都有回覆
if grep -q "沒有取得回覆內容" "$OUT"; then
    echo "[FAIL] 出現無回覆保險輸出"
    PASS=0
else
    echo "[PASS] 所有對話都有回覆內容"
fi

# 4) /quit 正常結束
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