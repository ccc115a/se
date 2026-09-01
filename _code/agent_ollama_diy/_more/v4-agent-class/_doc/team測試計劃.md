# Agent0Team 測試計劃

## 1. 測試目標

驗證 Agent0Team 團隊模型的功能與穩定性，確保：
- Planner、Generator、Evaluator 三種角色正確運作
- 迭代反饋循環正常工作
- 記憶管理與共享文件正確運作
- 多角色配置正確

---

## 2. 測試分類

### 2.1 單元測試

| 模組 | 測試項目 | 預期結果 |
|------|---------|---------|
| 記憶管理 | `load_memory()` | 正確讀取 JSON 檔案 |
| 記憶管理 | `save_memory()` | 正確寫入 JSON 檔案 |
| 記憶管理 | `append_memory()` | 正確附加記憶 |
| 共享文件 | `read_shared()` | 正確讀取檔案 |
| 共享文件 | `write_shared()` | 正確寫入檔案 |
| 共享文件 | `get_shared_context()` | 正確產生上下文 |
| Planner | `plan_task()` | 正確產生計劃 |
| Generator | `execute_plan()` | 正確執行計劃 |
| Evaluator | `evaluate_output()` | 正確評估輸出 |

### 2.2 整合測試

| 測試項目 | 描述 | 預期結果 |
|---------|------|---------|
| 單輪執行 | Planner → Generator → Evaluator → 完成 | 正確完成任務 |
| 雙輪迭代 | 第一次 FAIL → 第二次 PASS | 迭代優化生效 |
| 多 Generator | 2 個 Generator 同時執行 | 正確並行執行 |
| 多 Evaluator | 2 個 Evaluator 同時評估 | 正確匯總結果 |
| 放棄任務 | 多次 FAIL 後選擇放棄 | 正確放棄並回報 |

### 2.3 壓力測試

| 測試項目 | 描述 | 預期結果 |
|---------|------|---------|
| 高迭代次數 | MAX_ITERATIONS = 10 | 穩定執行 |
| 多任務順序 | 連續 5 個任務 | 記憶正確管理 |
| 長時間運行 | 30 分鐘壓測 | 無記憶洩漏 |

---

## 3. 測試案例

### 3.1 單元測試案例

```python
# test_memory.py
def test_load_memory():
    """測試載入記憶"""
    append_memory("planner", 0, "test content", 1)
    items = load_memory("planner", 0)
    assert len(items) == 1
    assert items[0]["content"] == "test content"

def test_shared_file():
    """測試共享文件"""
    write_shared("test.txt", "hello")
    content = read_shared("test.txt")
    assert content == "hello"
    append_shared("test.txt", "world")
    content = read_shared("test.txt")
    assert "hello\nworld" in content
```

### 3.2 整合測試案例

```bash
# test_single_task.sh
#!/bin/bash
echo "list files" | python agent0team.py --debug
# 預期：正確列出檔案

# test_iteration.sh
#!/bin/bash
echo "write a file that will fail then succeed" | python agent0team.py --generators 1 --evaluators 1 --max-iterations 2
# 預期：第一次 FAIL，第二次 PASS
```

---

## 4. 測試腳本

### 4.1 自動化測試腳本

```bash
#!/bin/bash
# test_team.sh - 自動化測試腳本
```

### 4.2 執行方式

```bash
# 執行所有測試
bash test_team.sh

# 執行特定測試
bash test_team.sh unit      # 單元測試
bash test_team.sh integration # 整合測試
bash test_team.sh stress    # 壓力測試
```

---

## 5. 測試資料

### 5.1 測試输入

```python
TEST_CASES = {
    "list_files": {
        "input": "list current directory files",
        "expected": "檔案列表"
    },
    "create_file": {
        "input": "create a test file at /tmp/test_agent0.txt with content 'hello team'",
        "expected": "檔案已建立"
    },
    "read_file": {
        "input": "read /tmp/test_agent0.txt",
        "expected": "hello team"
    }
}
```

---

## 6. 驗收標準

### 6.1 成功標準

- [ ] 單元測試通過率 > 90%
- [ ] 整合測試通過率 > 80%
- [ ] 無記憶洩漏
- [ ] 指令列參數正確運作
- [ ] 錯誤訊息清晰

### 6.2 效能標準

- [ ] 單輪執行時間 < 30 秒
- [ ] 記憶體用量 < 500MB
- [ ] 無阻塞卡死