"""Microservice demo - Python FastAPI + PostgreSQL."""
import os
import socket
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://demo:demo123@db:5432/demo",
)

DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS visits (
        id SERIAL PRIMARY KEY,
        path TEXT NOT NULL DEFAULT '/',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
]


def get_conn():
    return psycopg.connect(DATABASE_URL)


def init_db(retries: int = 10):
    import time

    last_err = None
    for _ in range(retries):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    for stmt in DDL_STATEMENTS:
                        cur.execute(stmt)
                    conn.commit()
            return
        except Exception as e:  # db not ready yet
            last_err = e
            time.sleep(2)
    raise last_err


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="demo-api (python)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageIn(BaseModel):
    content: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "python-api"}


@app.get("/api/hello")
def hello():
    return {
        "message": "Hello from Python FastAPI!",
        "hostname": socket.gethostname(),
    }


@app.get("/api/db-check")
def db_check():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
        return {"postgres": "up", "version": version}
    except Exception as e:
        return {"postgres": "down", "error": str(e)}


@app.get("/api/visits")
def get_visits():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM visits;")
            total = cur.fetchone()[0]
            cur.execute(
                "SELECT id, path, created_at FROM visits ORDER BY id DESC LIMIT 10;"
            )
            rows = [
                {"id": r[0], "path": r[1], "created_at": str(r[2])}
                for r in cur.fetchall()
            ]
    return {"total": total, "recent": rows}


@app.post("/api/visits")
def add_visit(path: str = "/"):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO visits (path) VALUES (%s) RETURNING id;",
                (path,),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            cur.execute("SELECT count(*) FROM visits;")
            total = cur.fetchone()[0]
    return {"id": new_id, "total": total}


@app.get("/api/messages")
def list_messages():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, content, created_at FROM messages "
                "ORDER BY id DESC LIMIT 20;"
            )
            rows = [
                {"id": r[0], "content": r[1], "created_at": str(r[2])}
                for r in cur.fetchall()
            ]
    return {"messages": rows}


@app.post("/api/messages")
def create_message(msg: MessageIn):
    content = msg.content.strip()
    if not content:
        return {"error": "empty content"}
    if len(content) > 500:
        return {"error": "content too long (max 500)"}
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (content) VALUES (%s) RETURNING id;",
                (content,),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
    return {"id": new_id, "content": content}
