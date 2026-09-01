# Express + SQLite 部落格伺服器（Docker 測試目標）

## 原理

與 `_more/v3-agent-reviewer/blog/server.md` 相同的部落格系統，但在 A1-agent_in_docker 的情境中，此伺服器會由 Agent 在 Docker 容器內啟動和操作。

### 在 Docker 中的行為差異

- Agent 透過 `run_in_docker()` 啟動伺服器
- 使用 `nohup` 背景執行保持伺服器運行
- 埠 3000 從容器映射到主機
- 資料庫檔案存在容器內的 `/sandbox/blog.db`

## 使用場景

- 測試 Agent 在容器內管理 Web 服務的能力
- 演示容器埠映射機制
- 驗證多步驟任務的自動化

## 優缺點

| 優點 | 缺點 |
|------|------|
| 容器內運行隔離性佳 | 與主機網路互通有限 |
| 可演示完整 Agent 工作流 | 依賴 Docker 環境 |
