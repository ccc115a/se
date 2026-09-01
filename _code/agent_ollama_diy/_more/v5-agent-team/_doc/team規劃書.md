# Agent0 Team 規劃書

## 1. 概述

基於 `agent0.py` 的單一 agent 架構，擴展為團隊協作模型，採用 harness engineering 的核心理念，包含三種角色分工：

- **Planner** - 規劃者（**1 個**）：分析任務、制定計劃、統一決策、協調流程
- **Generator** - 生成者（**N 個**，可設定）：執行實際操作、產生輸出
- **Evaluator** - 評估者（**N 個**，可設定）：審查結果、反饋改進建議

目標：透過角色分離實現關注點分離，提高系統的可維護性與輸出品質。

**角色數量配置**：
- Planner：固定 1 個，統一決策
- Generator：可設定數量（預設 1），透過參數 `NUM_GENERATORS` 控制
- Evaluator：可設定數量（預設 1），透過參數 `NUM_EVALUATORS` 控制

---

## 2. 架構設計

### 2.1 系統架構圖

```
┌─────────────────────────────────────────────────────────┐
│                   Agent0Team                          │
│  （主控制器，協調多角色協作）                         │
│  • Planner x 1（固定）                                │
│  • Generator x N（可設定）                           │
│  • Evaluator x N（可設定）                           │
└────────────────────────┬──────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │ Planner │    │Generator │    │Evaluator │
    │   x 1   │    │   x N    │    │   x N    │
    └─────────┘    └──────────┘    └──────────┘
```

### 2.2 循環流程

```
用戶輸入 → Planner 規劃（統一決策）
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Generator 1  Generator 2  ... Generator N
        │           │           │
        └───────────┼───────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Evaluator 1  Evaluator 2  ... Evaluator N
                    │
                    ▼
              匯總評估結果
                    │
                    ↓
              Planner 決定是否終止
                    │
              不滿意 ←────────────
                    │
              直到滿意或 MAX_ITERATIONS
```

每個循環：
1. Planner 分析任務，產生計劃（統一決策）
2. 多个 Generator 並行或依序執行計劃
3. 多个 Evaluator 分別評估輸出
4. **Planner 匯總並檢視所有 Evaluator 的評估結果**
5. Planner 制定下一輪 plan，包含：
   - **任務已完成**：評估通過，接受當前輸出，结束任务
   - **繼續優化**：根據 feedback 制定改進計劃
   - **放棄任務**：判斷無法完成，终止並回覆用戶
6. 循環直到滿意、選擇放棄或達到最大迭代次數

---

## 3. 各角色職責

### 3.1 Planner（規劃者）

**職責**：
- 分析用戶輸入，理解任務意圖
- 評估任務複雜度與可行性
- 制定執行計劃（步驟列表）
- 根據上一輪 feedback 調整計劃
- 決定是否需要终止循環

**輸入**：
- 用戶原始輸入
- 上下文歷史
- （可選）上一輪 feedback

**輸出**：
- 任務分析
- 執行計劃（步驟清單）
- 預期產出

### 3.2 Generator（生成者）

**職責**：
- 按照 Planner 的計劃執行操作
- 調用工具（shell 命令、API 等）
- 產生實際輸出
- 處理執行過程中的錯誤

**輸入**：
- Planner 的執行計劃
- 上下文歷史

**輸出**：
- 執行結果
- 過程日誌

### 3.3 Evaluator（評估者）

**職責**：
- 評估 Generator 的輸出是否滿足要求
- 檢查輸出正確性與品質
- 提供具體的 feedback
- 決定是否需要重試

**輸入**：
- 用戶原始輸入
- Planner 的計劃
- Generator 的輸出

**輸出**：
- 評估結果（通過/不通過）
- Feedback（如果不通過，說明原因與改進建議）

---

## 4. 技術細節

### 4.1 配置

```python
# 沿用 agent0.py 的配置
WORKSPACE = os.path.expanduser("~/.agent0")
MODEL = "minimax-m2.5:cloud"
MAX_TURNS = 5

# Team 特有配置
MAX_ITERATIONS = 3  # 最大迭代次數
NUM_GENERATORS = 1  # Generator 數量（可設定）
NUM_EVALUATORS = 1  # Evaluator 數量（可設定）
```

### 4.2 記憶管理

- **對話歷史**：所有角色共享
- **關鍵資訊**：所有角色共享
- **團隊記憶**：記錄 Planner/Generator/Evaluator 的交互歷史

### 4.3 安全審查

沿用 `agent0.py` 的安全審查機制：
- Generator 執行命令前需通過安全審查
- 外部目錄存取需要用戶���權

### 4.4 標記格式

```xml
<!-- Planner 輸出 -->
<plan>
  <analysis>任務分析</analysis>
  <steps>
    <step>步驟 1</step>
    <step>步驟 2</step>
  </steps>
</plan>

<!-- Generator 輸出 -->
<shell>要執行的命令</shell>
<output>執行結果</output>

<!-- Evaluator 輸出 -->
<evaluation>
  <result>PASS/FAIL</result>
  <feedback>反饋（可選）</feedback>
</evaluation>
```

---

## 5. 對話流程

### 5.1 單輪對話

```
用戶輸入
    │
    ▼
┌──────────────┐
│   Planner    │ 分析任務，產生計劃（統一決策）
└──────┬───────┘
        │ <plan>...</plan>
        ▼
┌──────────────┐      ┌──────────────┐
│  Generator 1 │      │  Generator N│
│  執行計劃    │ ...  │  執行計劃   │
└──────┬───────┘      └──────┬───────┘
        │ <output>          │ <output>
        └────────┬─────────┘
                 ▼
┌──────────────┐      ┌──────────────┐
│  Evaluator 1 │      │  Evaluator N │
│  評估輸出    │ ...  │  評估輸出   │
└──────┬───────┘      └──────┬───────┘
        │ <evaluation>      │ <evaluation>
        └────────┬─────────┘
                 ▼
           匯總評估結果
                 │
                 ▼
              回覆用戶
```

### 5.2 多輪循環

```
用戶輸入 → Planner（統一決策）
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
Generator 1  Generator 2  ... Generator N
    │           │           │
    └───────────┼───────────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
Evaluator 1  Evaluator 2  ... Evaluator N
                │
                ▼
          匯總評估結果
                │
          Planner 決定是否終止
                │
          不滿意 ←────────────
                │
          直到 PASS 或 MAX_ITERATIONS
```

---

## 6. 與 agent0.py 的比較

| 特性 | agent0.py | Agent0Team |
|------|-----------|------------|
| 角色數量 | 1 | 3 |
| 規劃能力 | 無（直接執行） | 有（Planner） |
| 評估能力 | 無 | 有（Evaluator） |
| 迭代優化 | 無 | 有 |
| 代碼複雜度 | 低 | 中 |
| 輸出品質 | 一般 | 較高 |

---

## 7. 預期效益

1. **品質提升**：透過 Evaluator 把關，減少錯誤輸出
2. **可維護性**：角色分離，易於獨立調試與改進
3. **迭代優化**：透過反饋循環，持續改進輸出
4. **透明化**：每個角色的輸出清晰可追蹤

---

## 8. 實作優先順序

1. **Phase 1**：實現基本框架，三角色串行運作
2. **Phase 2**：加入迭代反饋機制
3. **Phase 3**：加入團隊記憶管理
4. **Phase 4**：優化提示詞與角色定義

---

## 9. 檔案結構

```
v4-agent-team/
├── agent0.py        # 原始單一 agent
├── agent0team.py    # 新增：Team 架構
└── _doc/
    └── team規劃書.md
```

---

## 10. 參考資源

- Harness Engineering 概念：透過分工與協作提高 AI 系統品質
- agent0.py：提供基礎的工具調用與安全審查機制