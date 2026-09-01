#!/bin/bash
# test_team_case2.sh - 執行測試個案 2

cd "$(dirname "$0")"

echo "========================================"
echo "測試個案 2: 伊朗戰情報告"
echo "========================================"

python test_team_case2.py "$@"

exit $?