#!/bin/bash
# 金門大學校務系統 MVP 假資料一鍵執行
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_FILE="$PROJECT_DIR/dev.db"

echo "=== 產生假資料 SQL ==="
python3 "$SCRIPT_DIR/seed.py" -o "$SCRIPT_DIR/seed.sql" --seed 42

echo "=== 建立/重置 SQLite 資料庫 ==="
rm -f "$DB_FILE"
sqlite3 "$DB_FILE" < "$PROJECT_DIR/migrations/schema.sql" 2>/dev/null || true

echo "=== 塞入假資料 ==="
sqlite3 "$DB_FILE" < "$SCRIPT_DIR/seed.sql"

echo "=== 完成！ ==="
echo "資料庫位置: $DB_FILE"
echo ""
echo "測試帳號:"
echo "  管理員: admin / admin123"
echo "  教師:   T001 / teacher123"
echo "  學生:   11303001 / student123"
