# Agent0Team 測試案例 - Case 1

## 1. 測試概述

### 1.1 測試目標

驗證 Agent0Team 在多 Generator（3）、多 Evaluator（3）配置下的協作能力與穩定性。

### 1.2 角色配置

| 角色 | 數量 | 說明 |
|------|------|------|
| Planner | 1 | 統一決策 |
| Generator | 3 | 分工合作 |
| Evaluator | 3 | 多重評估 |

---

## 2. 測試案例

### 2.1 任務描述

```
任務：分析 v4-agent-team 目錄中的 Python 程式碼結構，並產生一份結構報告
```

**具體要求**：
1. 找出所有 `.py` 檔案
2. 分析每個檔案的函數數量
3. 列出主要的類別定義
4. 產生一份摘要報告

### 2.2 預期流程

```
迭代 1：
  ┌─────────────┐
  │   Planner   │ 分析任務，制定計劃
  └──────┬──────┘
         │
    ┌────┴────┬────────────┐
    ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐
│ Gen 0 │ │ Gen 1 │ │ Gen 2 │
│ 列出  │ │ 分析  │ │ 產生  │
│ 檔案  │ │ 函數  │ │ 報告  │
└───┬───┘ └───┬───┘ └───┬───┘
    └────┬────┴────┬────┘
         ▼          ▼          ▼
    ┌───────┐ ┌───────┐ ┌───────┐
    │ Eval 0│ │ Eval 1│ │ Eval 2│
    │ 評估  │ │ 評估  │ │ 評估  │
    └───────┘ └───────┘ └───────┘
         │          │          │
         └──────────┼──────────┘
                    ▼
           ┌───────────────┐
           │    Planner  │
           │ 匯總評估   │
           │ 決定是否終止 │
           └───────────┘

如果評估不通過，進入迭代 2
```

### 2.3 各角色分工

#### Generator 分工

| Generator | 職責 | 輸出 |
|-----------|------|------|
| Generator 0 | 掃描目錄，找出所有 .py 檔案 | 檔案列表 |
| Generator 1 | 分析每個檔案的函數與類別 | 分析結果 |
| Generator 2 | 整合資訊，產生報告 | 最終報告 |

#### Evaluator 分估標準

| Evaluator | 評估面向 | 權重 |
|-----------|---------|------|
| Evaluator 0 | 正確性（檔案列表是否完整） | 30% |
| Evaluator 1 | 準確性（分析是否正確） | 40% |
| Evaluator 2 | 完整性（報告是否滿足要求） | 30% |

---

## 3. 測試步驟

### 3.1 初始化

```bash
# 清理環境
rm -rf ~/.agent0/team/memory/*.json
rm -rf ~/.agent0/team/shared/*.txt

# 啟動 Agent0Team
python agent0team.py --generators 3 --evaluators 3 --max-iterations 3 --debug
```

### 3.2 輸入任務

```
你：分析 v4-agent-team 目錄中的 Python 程式碼結構，並產生一份結構報告
```

### 3.3 預期輸出

報告應包含：
- 所有 `.py` 檔案列表
- 每個檔案的函數數量
- 類別定義列表
- 摘要統計

---

## 4. 驗收標準

### 4.1 成功標準

- [ ] Planner 正確產生計劃並分配任務
- [ ] 3 個 Generator 都正確執行並產生輸出
- [ ] 3 個 Evaluator 都正確評估並給出分數
- [ ] Planner 正確匯總評估結果
- [ ] 最終報告包含所有預期內容

### 4.2 品質標準

- [ ] 檔案列表完整性 > 90%
- [ ] 分析準確率 > 80%
- [ ] 報告可讀性 > 7/10

### 4.3 效能標準

- [ ] 單輪執行時間 < 60 秒
- [ ] 總執行時間 < 180 秒

---

## 5. 測試記錄格式

### 5.1 日誌格式

```
[HH:MM:SS] START: 任務描述
[HH:MM:SS] ITERATION: 1
[HH:MM:SS] PLAN: 分析任務...
[HH:MM:SS] GEN_0: 產出檔案列表
[HH:MM:SS] GEN_1: 產出分析結果
[HH:MM:SS] GEN_2: 產出報告
[HH:MM:SS] EVAL_0: PASS (score: 8)
[HH:MM:SS] EVAL_1: PASS (score: 7)
[HH:MM:SS] EVAL_2: FAIL (score: 5)
[HH:MM:SS] REVIEW: FAIL, issues: [報告不完整]
[HH:MM:SS] DECISION: continue
[HH:MM:SS] ITERATION: 2
...
[HH:MM:SS] COMPLETE: 任務完成
```

### 5.2 輸出格式

```
═══ Agent0Team 測試案例 1 ═══
Generators: 3, Evaluators: 3, Max Iterations: 3
Task: 分析 Python 程式碼結構

═══ 執行過程 ═══
迭代 1：
  • Planner：制定計劃
  • Generator 0：找出 5 個 .py 檔案
  • Generator 1：分析 15 個函數
  • Generator 2：產生報告
  • Evaluator 0：PASS (8/10)
  • Evaluator 1：PASS (7/10)
  • Evaluator 2：PASS (8/10)
  • 結果：PASS

═══ 最終報告 ═══
檔案數量：5
函數數量：15
類別數量：3

═══ 測試結果 ═══
✅ 測試通過
```