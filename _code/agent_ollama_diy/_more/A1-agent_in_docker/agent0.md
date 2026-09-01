# Agent in Docker — 容器隔離執行 Agent

## 原理

此 Agent 在 v2-agent-xml（XML 協議 + 記憶系統）的基礎上，加入了 **Docker 容器隔離**機制。所有 shell 命令都在 Docker 容器內執行，而非直接在主機上運行，提供更強的沙盒安全性。

### Docker 沙盒架構

```
主機 (Host)
└── Agent 程式
    └── Docker 容器 (alpine:latest)
        ├── 掛載 ~/.agent0_sandbox → /sandbox
        ├── 暴露 3000-9000 埠
        └── 記憶體限制 256m
```

### 關鍵差異

- `run_in_docker()` 將所有命令包裝進 `docker run --rm` 執行
- 沙盒目錄 `~/.agent0_sandbox` 掛載到容器內 `/sandbox`
- 長時間運行的服務（如 Web 伺服器）使用 `nohup` 背景執行並延長 timeout
- 無安全審查模型（相較於 v3-agent-reviewer），但容器本身提供隔離

## 使用場景

- 需要執行不可信任程式碼的場景
- 不希望 Agent 直接影響主機系統
- 需要運行 Web 服務並測試的環境

## 優缺點

| 優點 | 缺點 |
|------|------|
| Docker 容器隔離安全 | 需要 Docker 環境 |
| 可運行 Web 服務 | 每次啟動新容器開銷大 |
| 含記憶系統 | 無安全審查模型 |
| 沙盒目錄管理 | 網路埠衝突風險 |
