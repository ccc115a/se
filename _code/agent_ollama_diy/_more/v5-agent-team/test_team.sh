#!/bin/bash
# test_team.sh - 執行 Agent0Team 測試

cd "$(dirname "$0")"

echo "========================================"
echo "執行 Agent0Team 測試"
echo "========================================"

python test_team.py "$@"

exit $?