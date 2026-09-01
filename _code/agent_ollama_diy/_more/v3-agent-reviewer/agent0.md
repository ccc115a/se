# Agent with Security Reviewer — XML-based Tool Use Agent

## 原理

這是一個採用 **XML 標籤協議**的 AI Agent 實作。不同於 JSON-based function calling，此 Agent 讓 LLM 透過 `<shell>`、`<end/>` 等 XML 標籤來表達工具使用意圖，系統端解析標籤後執行對應操作。

### 核心概念：LLM-as-Protocol-Translator

LLM 被指示以 XML 格式輸出操作需求，系統解析 XML 後執行並回饋結果。這是一種輕量級的 function calling 替代方案，不需 API-level 的工具定義支援。

### 安全審查機制（Reviewer Pattern）

使用**第二個 LLM 模型**作為安全審查者：Agent 輸出的每個 shell 命令都會先送給 Reviewer 模型判斷安全性，只有被標記為 SAFE 的命令才會真正執行。

### 記憶系統

- **對話歷史**：以 XML 格式儲存最近的對話回合
- **關鍵資訊提取**：每輪對話後，用 LLM 自動提取需要長期記憶的資訊

### 工作流程

1. 使用者輸入 → 加入 context（含記憶 + 歷史）
2. 呼叫主 LLM → 可能輸出 `<shell>` 命令
3. 對每個 `<shell>` 命令送給 Reviewer LLM 審查
4. 若 SAFE → 執行命令；若 UNSAFE → 跳過並回報
5. 將執行結果送回 LLM，LLM 決定是否繼續或 `<end/>`
6. 更新記憶系統

## 使用場景

- 需要安全執行程式碼或 shell 命令的場景
- 不希望 LLM 直接存取系統的環境
- 教學演示 ReAct 模式的簡化版

## 優缺點

| 優點 | 缺點 |
|------|------|
| 雙模型安全審查 | 需要兩個 LLM 實例 |
| XML 協議直觀易懂 | 無檔案讀寫工具 |
| 輕量無需特殊 API 支援 | 依賴 Ollama 本地部署 |
| 自動關鍵資訊提取 | 審查延遲較高 |
