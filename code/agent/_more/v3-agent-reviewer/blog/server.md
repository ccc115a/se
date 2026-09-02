# Express + SQLite 部落格伺服器 — Agent 工具測試目標

## 原理

這是一個標準的 Express.js 與 SQLite 部落格系統，作為 AI Agent 的工具執行目標。Agent 可以透過 shell 命令啟動此伺服器、操作資料庫、或修改程式碼來驗證其工具使用能力。

### CRUD 操作

- **C**（Create）：`POST /posts` 新增文章
- **R**（Read）：`GET /` 列表、`GET /post/:id` 單篇
- **U**（Update）：（此實作未包含）
- **D**（Delete）：`POST /delete/:id` 刪除文章

## 使用場景

- 測試 Agent 是否能啟動和管理 Web 服務
- 測試 Agent 是否能操作檔案系統和資料庫
- 教學演示中作為 Agent 的任務目標

## 優缺點

| 優點 | 缺點 |
|------|------|
| 簡單易懂的 CRUD 範例 | 無更新功能 |
| 使用 EJS 模板引擎 | 無安全性防護 |
| SQLite 無需獨立資料庫 | Express 4 回呼風格 |
