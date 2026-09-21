#!/bin/bash
# test.sh - 劇本測試：模擬使用者與 self-correcting loop 版 agent 對話
# 用法：cd agent4loop && ./test.sh   （需要 Ollama + qwen3.5:2b）
set -x

PROBE="LOOPPROBE_77"
OUT="$(mktemp)"

# 劇本順序：
#   1) 一般問答（不需工具）
#   2) 要求執行 echo 探針 → 驗證工具正常運作
#   3) 要求執行不存在的指令 → 工具失敗，預期模型反思/重試
#   4) /loop 檢視迴圈狀態與逐字稿
#   5) /quit 結束
printf '你好，請簡單自我介紹\n請用 run_shell 執行 echo %s ，並回報輸出結果\n請用 run_shell 執行 nosuchcommand_xyz123，然後看看是否能修正\n/loop\n/quit\n' "$PROBE" \
    | timeout 300 python3 agent4loop.py > "$OUT" 2>&1

PASS=1

# 1) 探針被執行（工具正常）
if grep -q "$PROBE" "$OUT"; then
    echo "[PASS] run_shell 被執行並回傳預期輸出"
else
    echo "[FAIL] 未偵測到 echo 探針輸出"
    PASS=0
fi

# 2) 失敗指令有觸發反思（出現反思提示或重試描述）
if grep -q "反思" "$OUT" || grep -q "重試" "$OUT"; then
    echo "[PASS] 偵測到失敗後反思/重試"
else
    echo "[FAIL] 未偵測到失敗後的反思/重試"
    PASS=0
fi

# 3) /loop 印出狀態與逐字稿
if grep -q "Self-Correcting Loop 狀態" "$OUT" && grep -q "逐字稿" "$OUT"; then
    echo "[PASS] /loop 印出狀態"
else
    echo "[FAIL] /loop 狀態輸出遺漏"
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