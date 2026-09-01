# Agent Team — Planner/Generator/Evaluator 團隊協作框架

## 原理

這是最進階的 Agent 實作——**多 Agent 團隊協作**。它將單一 Agent 擴展為三個角色組成的團隊：

### 角色架構

```
使用者輸入
    ↓
┌──────────┐
│ Planner  │ ← 分析任務、制定計劃、綜整評估結果
└────┬─────┘
     ↓ 計劃 (steps)
┌──────────┐    ┌──────────┐
│Generator1│    │Generator2│ ← 多個 Generator 平行執行計劃
└────┬─────┘    └────┬─────┘
     ↓ 執行結果        ↓
┌──────────┐    ┌──────────┐
│Evaluator1│    │Evaluator2│ ← 多個 Evaluator 評估結果
└────┬─────┘    └────┬─────┘
     ↓ 評估報告        ↓
┌──────────┐
│ Planner  │ ← 綜整評估，決定 complete/continue/abandon
└──────────┘
```

### 團隊循環（Team Loop）

```
迭代開始
  → Planner 制定計劃（<plan> 含 analysis + steps）
  → 所有 Generator 執行計劃（<shell> 命令）
  → 所有 Evaluator 評估結果（<evaluation> 含 PASS/FAIL + score + feedback）
  → Planner 綜整評估（<decision> complete/continue/abandon）
  → 若 complete → 返回結果
  → 若 continue → 將 feedback 加入下一輪迭代
  → 若 abandon → 返回失敗訊息
  → 達最大迭代次數 → 返回
```

### 角色職責

- **Planner**（規劃者）：分析任務、制定步驟、綜整評估結果、做出決策
- **Generator**（執行者）：按計劃執行 shell 命令，產生輸出
- **Evaluator**（評估者）：檢查 Generator 輸出是否滿足要求，給出評分和回饋

### 類別繼承

所有角色都繼承自 `Agent0` 基礎類別，各自覆寫 `SYSTEM_PROMPT` 來定義角色行為。

## 使用場景

- 複雜任務需要多輪迭代優化
- 需要品質保證的工作流程
- 多角度評估的自動化系統
- 教學演示多 Agent 協作模式

## 優缺點

| 優點 | 缺點 |
|------|------|
| 角色分工明確 | 需要大量 LLM 呼叫 |
| 內建品質評估迴圈 | 迭代次數有限制 |
| 支援多 Generator 平行執行 | Planner 負載最重 |
| Feedback 機制持續改進 | 除錯較複雜 |
| 可設定 Generator/Evaluator 數量 | 無平行處理效能優化 |
