# Agent0Team 詳細程式規格書

## 1. 系統概覽

### 1.1 檔案結構

```
v4-agent-team/
├── agent0.py           # 原始單一 agent
├── agent0team.py       # Team 團隊架構（新檔）
├── _doc/
│   ├── team規劃書.md
│   └── team詳細計劃.md  （本檔）
```

### 1.2 模組架構

```
┌─────────────────────────────────────────────────────┐
│                   agent0team.py                     │
├─────────────────────────────────────────────────────┤
│  配置常數                                            │
│  • WORKSPACE, MODEL, MAX_TURNS                       │
│  • NUM_GENERATORS, NUM_EVALUATORS, MAX_ITERATIONS   │
├─────────────────────────────────────────────────────┤
│  共享記憶                                            │
│  • conversation_history, key_info                  │
│  • team_memory                                      │
├─────────────────────────────────────────────────────┤
│  工具模組（agent0.py 沿用）                          │
│  • call_ollama() - Ollama API 調用                   │
│  • review_command() - 安全審查                     │
│  • check_outside_access() - 外部存取檢查             │
│  • ask_outside_access() - 請求用戶授權              │
├─────────────────────────────────────────────────────┤
│  記憶管理                                            │
│  • build_context() - 構建上下文                     │
│  • update_memory() - 更新對話歷史                   │
│  • extract_key_info() - 提取關鍵資訊               │
├─────────────────────────────────────────────────────┤
│  角色模組                                            │
│  • Planner - 規劃者（1 個固定）                      │
│  │   • plan_task() - 分析任務、制定計劃            │
│  │   • review_evaluations() - 匯總評估結果         │
│  │   • decide_next_plan() - 決定下一輪 plan         │
│  ├─ Generator - 生成者（N 個）                      │
│  │   • execute_plan() - 執行計劃                    │
│  │   • run_command() - 執行 shell 命令              │
│  └─ Evaluator - 評估者（N 個）                      │
│  │   • evaluate_output() - 評估輸出                 │
│  │   • provide_feedback() - 提供反饋               │
├─────────────────────────────────────────────────────┤
│  主控制器                                            │
│  • main() - 進入點                                   │
│  • run_teamLoop() - 團隊循環主迴圈                  │
└─────────────────────────────────────────────────────┘
```

---

## 2. 配置常數

```python
# ─── 基本配置（沿用 agent0.py） ───
WORKSPACE = os.path.expanduser("~/.agent0")
MODEL = "minimax-m2.5:cloud"
REVIEWER_MODEL = "minimax-m2.5:cloud"
MAX_TURNS = 5

# ─── Team 特有配置 ───
NUM_GENERATORS = 1      # Generator 數量
NUM_EVALUATORS = 1     # Evaluator 數量
MAX_ITERATIONS = 3     # 最大迭代次數
```

---

## 3. 共享資料結構

### 3.1 對話歷史與記憶

#### 3.1.1 命名規範

```
記憶命名格式：
  {agent_type}.{agent_id}.{timestamp}.{sequence}

共享文件命名格式：
  {type}.{task_id}.{iteration}.{agent_id}.txt
```

#### 3.1.2 記憶體結構

```python
# ═══════════════════════════════════════════
# 全域共享記憶（沿用 agent0.py）
# ═══════════════════════════════════════════
conversation_history: list[str] = []   # 對話歷史
key_info: list[str] = []                # 關鍵資訊

# ═══════════════════════════════════════════
# 各角色獨立記憶（記憶檔案）
# ═══════════════════════════════════════════
# 檔案路徑格式：~/.agent0/team/memory/{role}_{id}.json
# 例如：
#   ~/.agent0/team/memory/planner_0.json     # Planner 0 的記憶
#   ~/.agent0/team/memory/generator_0.json  # Generator 0 的記憶
#   ~/.agent0/team/memory/generator_1.json  # Generator 1 的記憶
#   ~/.agent0/team/memory/evaluator_0.json # Evaluator 0 的記憶

MEMORY_DIR = "~/.agent0/team/memory"

# 記憶檔案格式（JSON）：
# {
#   "agent_type": "generator",
#   "agent_id": 0,
#   "created_at": "2024-01-01T12:00:00",
#   "items": [
#     {"timestamp": "...", "content": "...", "iteration": 1},
#     {"timestamp": "...", "content": "...", "iteration": 2}
#   ]
# }
```

#### 3.1.3 共享文件結構

```python
# ═══════════════════════════════════════════
# 共享文件（所有角色可存取）
# ═══════════════════════════════════════════
# 檔案路徑格式：~/.agent0/team/shared/{type}.txt

SHARED_DIR = "~/.agent0/team/shared"

SHARED_FILES = {
    # 任務總覽：記錄當前任務的狀態
    # 格式：~/.agent0/team/shared/task_{task_id}.txt
    "task": "~/.agent0/team/shared/task_{task_id}.txt",
    
    # 團隊記錄：記錄每次迭代的執行過程
    # 格式：~/.agent0/team/shared/teamlog.txt
    "teamlog": "~/.agent0/team/shared/teamlog.txt",
    
    # 共享上下文：所有 agent 可知的資訊
    # 格式：~/.agent0/team/shared/context.txt
    "context": "~/.agent0/team/shared/context.txt",
    
    # 輸出暫存：Generator 的輸出暫存
    # 格式：~/.agent0/team/shared/output_{generator_id}.txt
    "output": "~/.agent0/team/shared/output_{generator_id}.txt",
    
    # 評估暫存：Evaluator 的評估暫存
    # 格式：~/.agent0/team/shared/evaluation_{evaluator_id}.txt
    "evaluation": "~/.agent0/team/shared/evaluation_{evaluator_id}.txt"
}
```

### 3.2 記憶管理 API

#### 3.2.1 記憶檔案命名規則

```
記憶檔案：
  {MEMORY_DIR}/{agent_type}_{agent_id}.json
  
  例如：
    planner_0.json      # Planner 0
    generator_0.json   # Generator 0
    generator_1.json  # Generator 1
    evaluator_0.json  # Evaluator 0
    evaluator_1.json  # Evaluator 1
```

#### 3.2.2 共享文件命名規則

```
共享檔案：
  {SHARED_DIR}/{type}[_{id}].txt
  
  例如：
    task_{task_id}.txt      # 任務記錄（含 task_id）
    teamlog.txt           # 團隊執行日誌
    context.txt          # 共享上下文
    output_0.txt         # Generator 0 的輸出
    output_1.txt         # Generator 1 的輸出
    evaluation_0.txt    # Evaluator 0 的評估
    evaluation_1.txt    # Evaluator 1 的評估
```

#### 3.2.3 API 函數

```python
# ═══════════════════════════════════════════
# 角色獨立記憶管理
# ═══════════════════════════════════════════

def load_memory(agent_type: str, agent_id: int) -> list[dict]:
    """
    載入指定 agent 的記憶
    
    Args:
        agent_type: "planner" | "generator" | "evaluator"
        agent_id: agent 編號
    
    Returns:
        list[dict]: 記憶項目列表
            [{"timestamp": "...", "content": "...", "iteration": N}, ...]
    
    File: {MEMORY_DIR}/{agent_type}_{agent_id}.json
    """

def save_memory(agent_type: str, agent_id: int, items: list[dict]):
    """
    儲存指定 agent 的記憶
    
    Args:
        agent_type: "planner" | "generator" | "evaluator"
        agent_id: agent 編號
        items: 記憶項目列表
    
    File: {MEMORY_DIR}/{agent_type}_{agent_id}.json
    """

def append_memory(agent_type: str, agent_id: int, content: str, iteration: int):
    """
    附加記憶到指定 agent
    
    Args:
        agent_type: "planner" | "generator" | "evaluator"
        agent_id: agent 編號
        content: 記憶內容
        iteration: 當前迭代次數
    """

def get_memory(agent_type: str, agent_id: int, limit: int = 10) -> list[str]:
    """
    取得指定 agent 的記憶（簡化格式）
    
    Args:
        agent_type: "planner" | "generator" | "evaluator"
        agent_id: agent 編號
        limit: 回傳最近 N 筆
    
    Returns:
        list[str]: 記憶內容列表
    """

# ═══════════════════════════════════════════
# 共享文件管理
# ═══════════════════════════════════════════

def read_shared(filename: str) -> str:
    """
    讀取共享文件
    
    Args:
        filename: 檔案名稱（不含路徑）
    
    Returns:
        str: 文件內容
    
    File: {SHARED_DIR}/{filename}
    """

def write_shared(filename: str, content: str):
    """
    覆寫共享文件
    
    Args:
        filename: 檔案名稱
        content: 檔案內容
    
    File: {SHARED_DIR}/{filename}
    """

def append_shared(filename: str, line: str):
    """
    附加一行到共享文件
    
    Args:
        filename: 檔案名稱
        line: 要附加的行
    
    File: {SHARED_DIR}/{filename}
    """

def get_shared_context() -> str:
    """
    取得所有 agent 可知的共享上下文
    
    包含：
    - 對話歷史（近 MAX_TURNS * 2 筆）
    - 關鍵資訊
    - 各 Generator 的最新輸出摘要
    - 各 Evaluator 的最新評估摘要
    
    Returns:
        str: 格式化的共享上下文
    
    File: {SHARED_DIR}/context.txt
    """

def clear_shared():
    """
    清空所有共享文件
    
    保留 context.txt，僅清空：
    - teamlog.txt
    - output_*.txt
    - evaluation_*.txt
    """
```

### 3.2 任務上下文

```python
@dataclass
class TaskContext:
    user_input: str              # 用戶輸入
    current_plan: str | None    # 當前計劃
    generators_outputs: list[dict]  # 各 Generator 的輸出
    evaluators_results: list[dict]  # 各 Evaluator 的結果
    iteration: int              # 當前迭代次數
    team_context: str           # 共享團隊上下文
```

### 3.3 計劃格式

```python
@dataclass
class Plan:
    analysis: str               # 任務分析
    steps: list[str]            # 執行步驟
    decision: str               # 決定：continue / complete / abandon
    feedback: str | None        # 來自上一輪的反饋
```

---

## 4. 工具模組 API

### 4.1 call_ollama()

```python
async def call_ollama(prompt: str, system: str = "", model: str = MODEL) -> str:
    """
    調用 Ollama API
    
    Args:
        prompt: 提示詞
        system: 系統提示詞（可選）
        model: 模型名稱（可選）
    
    Returns:
        str: 模型回覆
    
    Raises:
        Exception: API 調用失敗
    """
```

### 4.2 review_command()

```python
async def review_command(cmd: str) -> tuple[bool, str]:
    """
    安全審查命令
    
    Args:
        cmd: shell 命令
    
    Returns:
        tuple[bool, str]: (是否安全, 原因)
    """
```

### 4.3 execute_shell()

```python
def execute_shell(cmd: str, cwd: str = None) -> tuple[int, str]:
    """
    執行 shell 命令
    
    Args:
        cmd: shell 命令
        cwd: 工作目錄（可選）
    
    Returns:
        tuple[int, str]: (返回碼, 輸出)
    """
```

---

## 5. 角色模組 API

### 5.1 Planner（規劃者）

#### 5.1.1 plan_task()

```python
async def plan_task(user_input: str, context: str, feedback: str = None) -> Plan:
    """
    分析任務並制定計劃
    
    Args:
        user_input: 用戶輸入
        context: 上下文歷史
        feedback: 來自上一輪的反饋（可選）
    
    Returns:
        Plan: 計劃物件
    
    Output Format:
        <plan>
          <analysis>任務分析</analysis>
          <steps>
            <step>步驟 1</step>
            <step>步驟 2</step>
          </steps>
          <decision>continue</decision>
        </plan>
    """
```

#### 5.1.2 review_evaluations()

```python
async def review_evaluations(
    evaluations: list[dict],
    plan: Plan
) -> dict:
    """
    匯總並檢視所有 Evaluator 的評估結果
    
    Args:
        evaluations: 各 Evaluator 的評估結果列表
        plan: 當前計劃
    
    Returns:
        dict: 匯總後的評估結果
            {
                "overall": "PASS/FAIL",
                "all_passed": bool,
                "consensus": str,
                "issues": list[str]
            }
    """
```

#### 5.1.3 decide_next_plan()

```python
async def decide_next_plan(
    review_result: dict,
    plan: Plan,
    iteration: int
) -> tuple[str, Plan]:
    """
    根據評估結果決定下一輪 plan
    
    Args:
        review_result: 匯總後的評估結果
        plan: 當前���劃
        iteration: 當前迭代次數
    
    Returns:
        tuple[str, Plan]: (decision, 新計劃)
            - decision: "complete" / "continue" / "abandon"
            - Plan: 新的計劃（如果 continue）
    """
```

### 5.2 Generator（生成者）

#### 5.2.1 execute_plan()

```python
async def execute_plan(plan: Plan, context: str, generator_id: int = 0) -> dict:
    """
    執行計劃
    
    Args:
        plan: 計劃物件
        context: 上下文歷史
        generator_id: Generator 編號
    
    Returns:
        dict: 執行結果
            {
                "generator_id": int,
                "success": bool,
                "outputs": list[dict],  # 每個步驟的輸出
                "error": str | None
            }
    """
```

#### 5.2.2 execute_step()

```python
async def execute_step(step: str, step_index: int, context: str) -> dict:
    """
    執行單一步驟
    
    Args:
        step: 步驟描述
        step_index: 步驟編號
        context: 上下文
    
    Returns:
        dict: 步驟執行結果
            {
                "step_index": int,
                "command": str,
                "output": str,
                "success": bool,
                "error": str | None
            }
    """
```

### 5.3 Evaluator（評估者）

#### 5.3.1 evaluate_output()

```python
async def evaluate_output(
    user_input: str,
    generator_outputs: list[dict],
    plan: Plan,
    evaluator_id: int = 0
) -> dict:
    """
    評估 Generator 的輸出
    
    Args:
        user_input: 用戶輸入
        generator_outputs: 所有 Generator 的輸出
        plan: 計劃
        evaluator_id: Evaluator 編號
    
    Returns:
        dict: 評估結果
            {
                "evaluator_id": int,
                "passed": bool,
                "score": int,  # 0-10
                "feedback": str,
                "issues": list[str]
            }
    
    Output Format:
        <evaluation>
          <result>PASS/FAIL</result>
          <score>8</score>
          <feedback>反饋內容</feedback>
          <issues>
            <issue>問題 1</issue>
          </issues>
        </evaluation>
    """
```

---

## 6. 主控制器 API

### 6.1 run_team_loop()

```python
async def run_team_loop(user_input: str) -> tuple[str, list[dict]]:
    """
    團隊循環主迴圈
    
    Args:
        user_input: 用戶輸入
    
    Returns:
        tuple[str, list[dict]]: (最終回覆, 團隊執行記錄)
    
    Flow:
        1. Planner: plan_task()
        2. Generator(s): execute_plan() × NUM_GENERATORS
        3. Evaluator(s): evaluate_output() × NUM_EVALUATORS
        4. Planner: review_evaluations()
        5. Planner: decide_next_plan()
        6. 循環直到 complete/abandon/MAX_ITERATIONS
    """
```

### 6.2 main()

```python
def main():
    """
    主入口點
    
    Flow:
        1. 初始化 WORKSPACE
        2. 顯示歡迎訊息
        3. 進入主迴圈：
           - 讀取用戶輸入
           - call run_team_loop()
           - 顯示結果
           - 更新記憶
        4. 處理特殊指令（/quit, /memory 等）
    """
```

---

## 7. 提示詞模板

### 7.1 Planner System Prompt

```
你是 Planner，團隊的規劃者。

職責：
1. 分析用戶輸入，理解任務意圖
2. 制定執行計劃（步驟列表）
3. 匯總並檢視所有 Evaluator 的評估結果
4. 決定下一輪 plan（任務已完成 / 繼續優化 / 放棄任務）

重要規則：
- 當需要執行命令時，用 <shell> 標籤包住命令
- 用 <plan> 標籤輸出你的計劃
- 用 <evaluation_summary> 標籤匯總評估結果
- 用 <decision> 標籤輸出你的決定
- 任務已完成用 <end/> 結束
```

### 7.2 Generator System Prompt

```
你是 Generator，團隊的執行者。

職責：
1. 按照 Planner 的計劃執行操作
2. 調用工具完成任務
3. 報告執行結果

重要規則：
- 用 <shell> 標籤執行命令
- 用 <output> 標籤報告結果
- 完成後用 <done/> 結束
```

### 7.3 Evaluator System Prompt

```
你是 Evaluator，團隊的評估者。

職責：
1. 評估 Generator 的輸出是否滿足要求
2. 提供具體的反饋
3. 決定是否需要重試

重要規則：
- 用 <evaluation> 標籤輸出評估結果
- <result> 為 PASS 或 FAIL
- <feedback> 提供具體改進建議
- 如果 PASS，用 <end/> 結束
```

---

## 8. 循環流程詳細說明

### 8.1 團隊循環 pseudo-code

```python
async def run_team_loop(user_input: str) -> tuple[str, list[dict]]:
    context = build_context()
    iteration = 0
    team_log = []
    
    while iteration < MAX_ITERATIONS:
        # 1. Planner: 制定計劃
        feedback = None
        if iteration > 0:
            feedback = gather_feedback(evaluators_results)
        
        plan = await plan_task(user_input, context, feedback)
        team_log.append({"iteration": iteration, "plan": plan})
        
        # 2. Generator(s): 執行計劃
        generators_outputs = []
        for gen_id in range(NUM_GENERATORS):
            output = await execute_plan(plan, context, gen_id)
            generators_outputs.append(output)
        
        # 3. Evaluator(s): 評估輸出
        evaluators_results = []
        for eval_id in range(NUM_EVALUATORS):
            result = await evaluate_output(
                user_input, 
                generators_outputs, 
                plan, 
                eval_id
            )
            evaluators_results.append(result)
        
        # 4. Planner: 匯總評估結果
        review_result = await review_evaluations(
            evaluators_results, 
            plan
        )
        
        # 5. Planner: 決定下一輪
        decision, new_plan = await decide_next_plan(
            review_result, 
            plan, 
            iteration
        )
        
        if decision == "complete":
            return format_response(generators_outputs), team_log
        
        if decision == "abandon":
            return f"任務無法完成：{review_result['issues']}", team_log
        
        iteration += 1
    
    return "達到最大迭代次數", team_log
```

---

## 9. 錯誤處理

### 9.1 錯誤類型

| 錯誤類型 | 處理方式 |
|---------|---------|
| API 調用失敗 | 重試 3 次，失敗則回報錯誤 |
| 命令執行失敗 | 記錄錯誤，繼續執行下一步 |
| 評估超時 | 視為失敗，提供反饋 |
| 迭代超時 | 終止循環，返回當前結果 |

### 9.2 各模組錯誤處理

```python
# Generator 錯誤處理
if error:
    return {
        "success": False,
        "error": str(error),
        "partial_outputs": outputs  # 已完成的步驟
    }

# Evaluator 錯誤處理
if evaluation_failed:
    return {
        "passed": False,
        "score": 0,
        "feedback": "評估過程發生錯誤",
        "issues": [str(error)]
    }
```

---

## 10. 輸出格式

### 10.1 使用者回覆格式

```
🤖 [最終回覆]

═══ 團隊執行記錄 ═══
迭代 1：
  • Planner：分析任務...
  • Generator 0：執行步驟 1, 2, 3
  • Evaluator 0：PASS (score: 8)
迭代 2：
  • Planner：根據反饋優化...
  • ...
═══ [任務完成]
```

### 10.2 除錯模式

若有 `--debug` 參數，輸出完整過程：

```
[DEBUG] Iteration 1
[DEBUG] Planner plan: <plan>...</plan>
[DEBUG] Generator 0 output: <output>...</output>
[DEBUG] Evaluator 0 evaluation: <evaluation>...</evaluation>
[DEBUG] Planner decision: continue
```

---

## 11. 指令列參數

```bash
python agent0team.py [--generators N] [--evaluators N] [--max-iterations N] [--debug]

# 範例
python agent0team.py --generators 2 --evaluators 2 --max-iterations 5
```

---

## 12. 測試規劃

### 12.1 單元測試

- `test_plan_task()` - Planner 計劃生成
- `test_execute_plan()` - Generator 執行計劃
- `test_evaluate_output()` - Evaluator 評估輸出

### 12.2 整合測試

- `test_team_loop()` - 完整團隊循環
- `test_iteration_feedback()` - 迭代反饋

### 12.3 壓力測試

- 多 Generator 並行執行
- 高迭代次數穩定性