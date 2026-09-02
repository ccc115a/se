# Agent with Memory — XML-based Tool Use + 記憶系統

## 原理

此版本引入了兩項重要升級：
1. **XML 標籤協議**：以 `<shell>`、`<end/>` 取代 JSON 格式的工具描述
2. **記憶系統**：包含對話歷史管理和關鍵資訊提取

### XML 工具協議

```
LLM 輸出格式：
<shell>ls -la</shell>
<shell>cat file.txt</shell>
<end/>
```

系統解析 `<shell>` 標籤內的命令並執行，LLM 根據執行結果決定下一步。`<end/>` 表示任務完成。

### 記憶管理

- **短期記憶**：以 XML 格式儲存最近 `MAX_TURNS` 輪的對話（user/assistant/tool）
- **長期記憶**：每輪結束後，用 LLM 自動提取關鍵資訊存入 `key_info` 列表
- **Context 構建**：每次呼叫前將記憶和歷史組合成 Context 送給 LLM

### 多輪循環

```
使用者 → Context + User → LLM → <shell> → 執行 → 結果回 LLM → <shell>/<end/>
                                                           ↓
                                                       更新記憶
```

## 使用場景

- 需要記憶能力的對話式 Agent
- 多步驟任務自動化
- 教學 XML-based 工具協議

## 優缺點

| 優點 | 缺點 |
|------|------|
| XML 協議直觀 | 無安全審查 |
| 含短期+長期記憶 | 記憶提取依賴 LLM 品質 |
| 多輪循環直到完成 | 無檔案讀寫專用工具 |
