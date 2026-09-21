#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
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

echo "[1] 建置後端..."
cargo build --manifest-path "$ROOT/Cargo.toml" 2>/dev/null

echo "[2] 啟動後端 server..."
pkill -f "target/debug/nqu-erp" 2>/dev/null || true
sleep 1
rm -f "$DB_FILE"
DATABASE_URL="sqlite://$DB_FILE?mode=rwc" "$ROOT/target/debug/nqu-erp" &
PID=$!

echo "    等待 server 就緒（migration 完成）..."
for i in $(seq 1 30); do
  curl -sf "$BASE/health" > /dev/null 2>&1 && break
  sleep 1
done
curl -sf "$BASE/health" > /dev/null || { echo "server 啟動失敗"; exit 1; }

echo "[3] 插入假資料..."
python3 "$ROOT/scripts/seed.py" -o "$ROOT/scripts/seed.sql" --seed 42
sqlite3 "$DB_FILE" < "$ROOT/scripts/seed.sql"

echo "[4] 確認假資料已寫入（課程數 = 15）..."
COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM courses;")
[ "$COUNT" = "15" ] || { echo "seed 失敗（courses=$COUNT）"; exit 1; }

echo "[5] Vitest 單元測試..."
npm test

echo "[6] Playwright E2E 測試..."
npx playwright test "$@"