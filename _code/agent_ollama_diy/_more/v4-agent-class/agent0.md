# Agent0 Class — 物件導向 Agent 框架

## 原理

這是整個 Agent 系列的重大重構——將所有功能封裝為 `Agent0` 類別，使用 Python `@dataclass` 裝飾器。此版本整合了前幾代的所有功能：

- XML 工具協議（來自 v2/v3）
- 雙層安全防護（來自 v3-agent-secure）
- 記憶系統（來自 v2-agent-xml）

### 類別設計

```python
@dataclass
class Agent0:
    workspace: str         # 工作目錄
    model: str             # 主 LLM 模型
    reviewer_model: str    # 審查 LLM 模型
    max_turns: int         # 最大回合數
    conversation_history   # 對話歷史
    key_info              # 長期記憶
    outside_access_granted # 已授權外部路徑
```

### 關鍵方法

- `call_ollama()` — 呼叫 LLM API
- `review_command()` — 安全審查
- `check_outside_access()` — 目錄檢查
- `execute_shell()` — 安全執行命令
- `build_context()` — 建構上下文
- `run()` — 主循環入口

### 與前幾代的差異

- `review_command()` 改為簡化版 prompt（英文）
- 新增 `execute_shell()` 統一命令執行入口
- `run()` 方法整合完整循環
- 支援自訂 `system_prompt`

## 使用場景

- 作為可複用的 Agent 類別庫
- 需要程式化建立多個 Agent 實例
- 擴展和繼承的基礎框架

## 優缺點

| 優點 | 缺點 |
|------|------|
| 類別封裝，可重用性高 | 簡化了審查 prompt |
| 整合所有安全功能 | dataclass 限制部分彈性 |
| 支援自訂 system prompt | 無團隊協作功能 |
| 可作為基礎類別擴展 | 仍依賴 Ollama |
