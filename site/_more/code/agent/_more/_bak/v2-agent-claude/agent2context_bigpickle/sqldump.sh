set -x
sqlite3 context.sqlite3 ".tables"          # 看有哪些表
sqlite3 context.sqlite3 "SELECT * FROM meta;"
sqlite3 context.sqlite3 "SELECT name, keywords FROM skills;"
sqlite3 context.sqlite3 "SELECT id, role, substr(text,1,40), created_at FROM memories;"