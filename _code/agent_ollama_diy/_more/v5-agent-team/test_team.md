# 團隊功能測試

## 原理

這是一組針對 `Agent0Team` 的自動化測試，驗證團隊循環的各項功能：

### 測試案例

| 測試 | 說明 | 驗證重點 |
|------|------|---------|
| test_basic | 基本團隊循環，1 Generator + 1 Evaluator | 最少配置能否正常運作 |
| test_iteration | 多迭代測試（max_iterations=2） | 迭代次數限制 |
| test_multi_generator | 2 個 Generator | 多執行者平行運作 |
| test_multi_evaluator | 2 個 Evaluator | 多評估者平行運作 |

### 測試設計

每個測試使用 `run_team_loop()` 並驗證：
- 迭代次數在限制範圍內
- Generator/Evaluator 數量正確
- 不拋出例外

## 使用場景

- CI/CD 自動化測試
- 開發階段驗證團隊功能
- 確保重構不破壞既有功能
