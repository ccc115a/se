CREATE TABLE IF NOT EXISTS messages (
  id         SERIAL PRIMARY KEY,
  author     TEXT NOT NULL,
  body       TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO messages (author, body) VALUES
  ('system', 'Hello from PostgreSQL! 容器啟動成功。'),
  ('system', 'docker compose makes microservices easy');
