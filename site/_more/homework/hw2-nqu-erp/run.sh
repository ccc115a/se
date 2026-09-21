#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"
DB_FILE="$ROOT/dev.db"
BASE="http://localhost:8080"
PID=""

cleanup() {
  if [ -n "$PID" ]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  pkill -f "target/debug/nqu-erp" 2>/dev/null || true
}
trap cleanup EXIT

echo "[1] 檢查 port 8080..."
if lsof -i :8080 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "     port 8080 已被佔用，請先停掉其他 nqu-erp process" >&2
  exit 1
fi

echo "[2] 建置後端..."
cargo build

echo "[3] 重置資料庫並啟動後端 server..."
rm -f "$DB_FILE"
"$ROOT/target/debug/nqu-erp" &
PID=$!

echo "[4] 等待 server 就緒（migration 完成）..."
for i in $(seq 1 30); do
  curl -sf "$BASE/health" >/dev/null 2>&1 && break
  sleep 1
done
curl -sf "$BASE/health" >/dev/null || { echo "server 啟動失敗" >&2; exit 1; }

echo "[5] 插入假資料（courses=15, users=42）..."
python3 scripts/seed.py -o scripts/seed.sql --seed 42
sqlite3 "$DB_FILE" < scripts/seed.sql

echo "[6] 啟動前端（http://localhost:5173，Ctrl+C 停止）"
cd frontend
npm run dev