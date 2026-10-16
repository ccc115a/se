# Python 服務：對留言資料做統計分析
import platform
import re
from collections import Counter

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)


def query(sql):
    conn = psycopg2.connect(connect_timeout=3)  # 讀取 PG* 環境變數
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


@app.get("/health")
def health():
    try:
        query("SELECT 1")
        return jsonify(service="python", runtime=platform.python_version(), db="ok")
    except Exception as e:
        return jsonify(service="python", db="down", error=str(e)), 503


@app.get("/stats")
def stats():
    rows = query("SELECT author, body FROM messages")
    words = Counter(
        w.lower() for _, body in rows for w in re.findall(r"[\w']+", body) if len(w) > 2
    )
    authors = Counter(a for a, _ in rows)
    avg = sum(len(b) for _, b in rows) / len(rows) if rows else 0
    return jsonify(
        total=len(rows),
        avg_length=round(avg, 1),
        top_authors=authors.most_common(3),
        top_words=words.most_common(5),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
