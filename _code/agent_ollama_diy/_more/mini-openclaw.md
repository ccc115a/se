# mini-openclaw — 最小化 AI Agent 框架（OpenClaw 克隆版）

## 原理

mini-openclaw 是一個基於 Anthropic Claude API 的最小化 AI Agent 框架，靈感來自 OpenClaw 專案。它實現了 **ReAct（Reasoning + Acting）循環**：LLM 接收使用者輸入後，可以調用多種工具（執行命令、讀寫檔案、記憶操作），並根據工具回饋決定下一步行動，直到任務完成。

### 核心循環

1. 使用者輸入訊息
2. 將訊息加入對話歷史
3. 呼叫 LLM（含 system prompt 和工具定義）
4. LLM 回覆可能是文字（end_turn）或工具呼叫（tool_use）
5. 如果是工具呼叫，執行工具並將結果返回 LLM
6. 重複 3-5 直到 LLM 回覆 end_turn

### 關鍵特性

- **多 Agent 路由**：支援 `/research` 前綴將任務路由到專門的研究員 Agent
- **會話壓縮**：當 token 超過閾值時，自動總結舊對話以節省上下文空間
- **長期記憶**：Agent 可以儲存和檢索跨會話的關鍵資訊
- **命令安全審查**：基於白名單（SAFE_COMMANDS）和用戶核准機制
- **定時心跳**：支援排程自動喚醒 Agent 執行任務

## 使用場景

- 個人 AI 助手（類似 OpenClaw）
- 自動化研究助理
- 排程定時任務

## 優缺點

| 優點 | 缺點 |
|------|------|
| 支援多 Agent 分工 | 依賴 Anthropic API |
| 會話壓縮節省 token | 安全機制較簡陋 |
| 長期記憶跨會話 | 無並發控制 |
| 定時心跳功能 | 工具列表固定 |
