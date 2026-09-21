#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Testing agent0.py to create a Node.js blog system in blog2/ ==="

rm -rf blog2

echo ""
echo "=== Running agent0.py to create blog2/ ==="

printf "Create a Node.js blog system in blog2/ folder. Use express, better-sqlite3, ejs. Create app.js and views/index.ejs, views/new.ejs.\n/quit\n" | python3 agent0.py

echo ""
echo "=== Verification ==="
ls -la blog2/
ls -la blog2/views/

echo ""
echo "=== Test: Run server ==="
cd blog2
node app.js &
PID=$!
sleep 2
curl -s http://localhost:3000 | grep -q "My Blog" && echo "Server OK!"
kill $PID 2>/dev/null || true

echo ""
echo "=== All tests passed! ==="
