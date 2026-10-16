// Node.js 服務：留言板 CRUD（讀寫 PostgreSQL）
const express = require("express");
const { Pool } = require("pg");

const pool = new Pool(); // 讀取 PGHOST / PGUSER / PGPASSWORD / PGDATABASE
const app = express();
app.use(express.json());

app.get("/health", async (_req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({ service: "node", runtime: process.version, db: "ok" });
  } catch (e) {
    res.status(503).json({ service: "node", db: "down", error: e.message });
  }
});

app.get("/messages", async (_req, res) => {
  const { rows } = await pool.query(
    "SELECT id, author, body, created_at FROM messages ORDER BY id DESC LIMIT 20"
  );
  res.json(rows);
});

app.post("/messages", async (req, res) => {
  const author = String(req.body.author || "anonymous").slice(0, 40);
  const body = String(req.body.body || "").slice(0, 280);
  if (!body.trim()) return res.status(400).json({ error: "body is required" });
  const { rows } = await pool.query(
    "INSERT INTO messages (author, body) VALUES ($1, $2) RETURNING *",
    [author, body]
  );
  res.status(201).json(rows[0]);
});

app.listen(3000, () => console.log("node service on :3000"));
