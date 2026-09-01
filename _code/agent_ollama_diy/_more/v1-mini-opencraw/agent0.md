# Agent0 — JSON-based Tool Use Agent（OpenClaw 簡化版）

## 原理

這是從 mini-openclaw 簡化而來的 JSON-based 工具使用 Agent。不同於後續版本使用 XML 協議，此版本讓 LLM 以 **JSON 格式** 描述工具呼叫需求，用 `<tool>` 標籤包裹。

### JSON Tool Use 協議

```
LLM 輸出格式：
<tool>
{"name": "run_command", "input": {"command": "ls -la"}}
</tool>
```

系統解析 JSON 後執行對應工具（run_command / read_file / write_file），並將結果繼續餵給 LLM。

### 與 mini-openclaw 的差異

- 移除多 Agent 路由
- 移除會話管理與壓縮
- 移除長期記憶系統
- 使用 Ollama 取代 Anthropic API
- 簡化為單一回合工具執行（無多輪循環）

## 使用場景

- 教學演示 JSON-based function calling
- 輕量級檔案操作助手
- 從純聊天到 Agent 的過渡版本

## 優缺點

| 優點 | 缺點 |
|------|------|
| JSON 格式結構化 | 無多輪工具循環 |
| 支援三種工具 | 無記憶系統 |
| 使用 Ollama 開源 | 無安全審查 |
