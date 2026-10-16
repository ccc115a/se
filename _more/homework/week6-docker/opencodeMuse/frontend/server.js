// 簡易 Node.js 前端：提供靜態頁面 + /health
const express = require("express");
const path = require("path");
const os = require("os");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, "public")));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "node-frontend", hostname: os.hostname() });
});

app.get("/frontend-info", (req, res) => {
  res.json({
    service: "node-frontend",
    hostname: os.hostname(),
    node: process.version,
    uptime_sec: Math.floor(process.uptime()),
  });
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`frontend listening on ${PORT}`);
});
