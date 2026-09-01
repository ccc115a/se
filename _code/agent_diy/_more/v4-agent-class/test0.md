# Agent0 互動測試 — 匯入 Agent0 類別

## 原理

這是一個使用 `agent0` 模組的互動測試程式。它匯入 `Agent0` 類別，建立實例後進入 REPL 循環與 Agent 互動。

### 與 agent0.py main() 的差異

兩者功能相同，但此測試檔展示瞭如何在外部程式中使用 `Agent0` 類別：
```python
from agent0 import Agent0
agent = Agent0()
response, tool_result = await agent.run(user_input)
```

## 使用場景

- 驗證 Agent0 類別的可匯入性
- 作為使用 Agent0 類別的範例
- 單獨測試 Agent 功能
