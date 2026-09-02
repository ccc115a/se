#!/bin/bash
# test_team_case1.sh - 執行測試個案 1

cd "$(dirname "$0")"

echo "========================================"
echo "測試個案 1: FastAPI + SQLite 網誌系統"
echo "========================================"

python test_team_case1.py "$@"

exit $?