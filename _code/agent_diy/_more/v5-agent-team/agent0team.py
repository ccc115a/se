#!/usr/bin/env python3
# agent0team.py - Agent Team with Planner/Generator/Evaluator roles
# Run: python agent0team.py

import subprocess
import os
import asyncio
import aiohttp
import re
import argparse
from dataclasses import dataclass, field
from typing import Optional

# === 全域配置 ===
# 團隊中所有角色共用這些基本設定
WORKSPACE = os.path.expanduser("~/.agent0")
MODEL = "minimax-m2.5:cloud"
MAX_TURNS = 5
MAX_ITERATIONS = 3       # 團隊循環最大迭代次數
NUM_GENERATORS = 1       # 預設 Generator 數量
NUM_EVALUATORS = 1       # 預設 Evaluator 數量


@dataclass
class Agent0:
    # === 基礎 Agent 類別 ===
    # 提供 call_ollama、安全審查、目錄控制、shell 執行等共用功能
    # 與 v4-agent-class/agent0.py 基本相同，但：
    # - 不再使用 extract_key_info（團隊協作中暫不支援記憶）
    # - SYSTEM_PROMPT 改為明確宣告型別
    
    workspace: str = ""
    model: str = "minimax-m2.5:cloud"
    reviewer_model: str = "minimax-m2.5:cloud"
    max_turns: int = 5
    
    conversation_history: list = field(default_factory=list)
    key_info: list = field(default_factory=list)
    outside_access_granted: set = field(default_factory=set)
    
    SYSTEM_PROMPT: str = """你是 Jarvis，一個有用的 AI 助理。

重要規則：
1. 當你需要執行 shell 命令時，用 <shell> 標籤包住命令
2. 如果需要多個命令，可以輸出多個 <shell> 標籤
3. 當所以命令都執行完後，用 <end/> 結束

流程：
- 輸出所有需要的 <shell>...</shell> 標籤
- 執行完後你會看到結果
- 當需要更多命令時繼續輸出 <shell>
- 全部完成後輸出 <end/>"""
    
    def __post_init__(self):
        if not self.workspace:
            self.workspace = os.path.expanduser("~/.agent0")
    
    async def call_ollama(self, prompt: str, system: str = "") -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        # 加入例外處理，避免 API 錯誤中斷團隊循環
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    result = await resp.json()
                    return result.get("response", "").strip()
        except Exception as e:
            return f"[錯誤: {e}]"
    
    async def review_command(self, cmd: str) -> tuple[bool, str]:
        review_prompt = f"""Review this command: {cmd}

Is it SAFE to run? Reply with SAFE or UNSAFE."""

        payload = {
            "model": self.reviewer_model,
            "prompt": review_prompt,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    result = await resp.json()
                    response = result.get("response", "").strip()
                    
                    if response.startswith("SAFE"):
                        return True, ""
                    else:
                        reason = response.replace("UNSAFE", "").strip(" -")
                        return False, reason
        except Exception as e:
            return False, f"審查失敗: {e}"
    
    def check_outside_access(self, cmd: str, cwd: str) -> tuple[bool, str]:
        def extract_paths(c):
            paths = []
            patterns = [
                (r'(?:^|\s)(?:cat|ls|cd|rm|cp|mv|chmod|chown|find|grep)\s+(/[^\s]+)', 1),
                (r'(?:^|\s)\.\./[^\s]*', 0),
                (r'(?:^|\s)\.\.(?:\s|$)', 0),
            ]
            for pattern, group in patterns:
                for match in re.finditer(pattern, c, re.MULTILINE):
                    path = match.group(group).strip() if group > 0 else ".."
                    if path:
                        paths.append(path)
            return paths
        
        paths = extract_paths(cmd)
        cwd_abs = os.path.abspath(cwd)
        
        for path in paths:
            if path.startswith('/'):
                abs_path = path
            else:
                abs_path = os.path.abspath(os.path.join(cwd, path))
            
            if path == '..' or path.startswith('../'):
                return True, abs_path
            
            if not abs_path.startswith(cwd_abs):
                return True, abs_path
        
        return False, ""
    
    def ask_outside_access(self, path: str) -> bool:
        print(f"\n⚠️  命令嘗試存取本資料夾以外的檔案: {path}")
        print("   是否允許？（y/N）：", end=" ")
        try:
            response = input().strip().lower()
            return response in ['y', 'yes']
        except:
            return False
    
    def build_context(self) -> str:
        context_parts = []
        if self.key_info:
            items_xml = "\n".join(f"  <item>{k}</item>" for k in self.key_info)
            context_parts.append(f"<memory>\n{items_xml}\n</memory>")
        if self.conversation_history:
            context_parts.append("<history>\n" + "\n".join(self.conversation_history[-self.max_turns*2:]) + "\n</history>")
        return "\n\n".join(context_parts)
    
    def update_memory(self, user_input: str, assistant_response: str, tool_result: str = None):
        self.conversation_history.append(f"  <user>{user_input}</user>")
        self.conversation_history.append(f"  <assistant>{assistant_response}</assistant>")
        if tool_result:
            self.conversation_history.append(f"  <tool>{tool_result[:500]}</tool>")
        
        while len(self.conversation_history) > self.max_turns * 4:
            self.conversation_history.pop(0)
    
    async def execute_shell(self, cmd: str, cwd: str = None) -> tuple[int, str]:
        # 統一的 shell 命令執行入口（含雙層安全檢查）
        print(f"\n执行命令: {cmd}")
        
        is_safe, reason = await self.review_command(cmd)
        
        if not is_safe:
            print(f"⚠️  被安全審查阻止: {reason}")
            return -1, f"阻止：{reason}"
        
        if cwd is None:
            cwd = os.getcwd()
        
        needs_access, path = self.check_outside_access(cmd, cwd)
        if needs_access:
            if path in self.outside_access_granted:
                pass
            else:
                if not self.ask_outside_access(path):
                    print(f"⚠️  已拒絕存取：{path}")
                    return -1, f"拒絕：{path}"
                self.outside_access_granted.add(path)
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
            output = result.stdout + result.stderr
            print(f"結果: {output if output else '（無輸出）'}")
            return result.returncode, output
        except Exception as e:
            print(f"錯誤：{e}")
            return -1, f"錯誤：{e}"
    
    async def run(self, user_input: str, system_prompt: str = "") -> tuple[str, str]:
        # 基本 run 方法（團隊循環中不使用 extract_key_info）
        SYSTEM = system_prompt if system_prompt else self.SYSTEM_PROMPT
        
        context = self.build_context()
        full_prompt = f"{context}\n\n<user>{user_input}</user>" if context else f"<user>{user_input}</user>"
        
        response = await self.call_ollama(full_prompt, SYSTEM)
        
        print(f"\n🤖 回應: {response[:200]}{'...' if len(response) > 200 else ''}")
        
        tool_result = None
        current_response = response
        
        while True:
            if "<end/>" in current_response:
                before_end = current_response.split("<end/>")[0].strip()
                if not before_end:
                    response = "命令已執行。" if tool_result else "完成。"
                else:
                    response = before_end
                break
            
            shell_matches = re.findall(r'<shell>(.+?)</shell>', current_response, re.DOTALL)
            if not shell_matches:
                response = current_response
                break
            
            all_outputs = []
            for cmd in shell_matches:
                cmd = cmd.strip()
                returncode, output = await self.execute_shell(cmd)
                
                if returncode != 0:
                    all_outputs.append(f"$ {cmd}\n{output}")
                else:
                    all_outputs.append(f"$ {cmd}\n{output if output else '（無輸出）'}")
            
            tool_result = (tool_result or "") + "\n" + "\n".join(all_outputs)
            
            follow_up_prompt = f"""<context>{context}</context>

<user>{user_input}</user>
<assistant>{current_response}</assistant>
<output>
{chr(10).join(all_outputs)}
</output>

Done. Output <end/> now."""
            current_response = await self.call_ollama(follow_up_prompt, SYSTEM)
        
        # 僅更新記憶，不提取關鍵資訊（團隊版本暫不支援）
        self.update_memory(user_input, response, tool_result)
        
        return response, tool_result


# === 角色類別（皆繼承自 Agent0） ===

class Planner(Agent0):
    # Planner（規劃者）：分析任務、制定計劃、綜整評估結果、做出決策
    # 使用 <plan> 標籤輸出計劃，<decision> 標籤輸出決策
    SYSTEM_PROMPT = """你是 Planner，團隊的規劃者。

職責：
1. 分析用戶輸入，理解任務意圖
2. 制定執行計劃（步驟列表）
3. 匯總並檢視所有 Evaluator 的評估結果
4. 決定下一輪 plan（任務已完成 / 繼續優化 / 放棄任務）

重要規則（必須嚴格遵守）：
- 用 <plan> 標籤輸出你的計劃，格式如下：
  <plan>
    <analysis>任務分析...</analysis>
    <steps>
      <step>步驟 1 描述</step>
      <step>步驟 2 描述</step>
    </steps>
  </plan>
- 如果沒有步驟，<steps> 可以為空，但 <plan> 標籤必須存在
- 用 <decision> 標籤輸出你的決定：<decision>complete</decision> 或 <decision>continue</decision> 或 <decision>abandon</decision>
- 任務已完成用 <end/> 結束"""


class Generator(Agent0):
    # Generator（執行者）：按照 Planner 的計劃執行 shell 命令
    # 使用 <shell> 標籤執行命令，<done/> 結束
    SYSTEM_PROMPT = """你是 Generator，團隊的執行者。

職責：
1. 按照 Planner 的計劃執行操作
2. 調用工具完成任務
3. 報告執行結果

重要規則（必須嚴格遵守）：
- 用 <shell> 標籤執行命令，格式：<shell>你的命令</shell>
- 可以輸出多個 <shell> 標籤來執行多個命令
- 用 <output> 標籤報告執行結果：<output>結果描述</output>
- 完成後用 <done/> 結束"""


class Evaluator(Agent0):
    # Evaluator（評估者）：檢查 Generator 輸出是否滿足要求
    # 使用 <evaluation> 標籤輸出 PASS/FAIL、分數和反饋
    SYSTEM_PROMPT = """你是 Evaluator，團隊的評估者。

職責：
1. 評估 Generator 的輸出是否滿足要求
2. 提供具體的反饋
3. 決定是否需要重試

重要規則（必須嚴格遵守）：
- 用 <evaluation> 標籤輸出評估結果，格式如下：
  <evaluation>
    <result>PASS</result>
    <score>8</score>
    <feedback>評估說明...</feedback>
  </evaluation>
- <result> 必須是 PASS 或 FAIL（大小寫不拘）
- 如果是 PASS，用 <end/> 結束
- 如果是 FAIL，必須提供具體的 <feedback> 說明問題和改進建議"""


# === 團隊循環的各個階段函數 ===

async def plan_task(planner: Planner, user_input: str, context: str, feedback: str = None) -> dict:
    # 階段一：Planner 制定計劃
    # 接收使用者輸入、當前 context、上一輪的反饋（可選）
    # 回傳包含 analysis 和 steps 的計劃字典
    feedback_section = f"\n\n<feedback>{feedback}</feedback>" if feedback else ""
    
    prompt = f"""<user_input>{user_input}</user_input>
<context>{context}</context>{feedback_section}

請分析任務並制定執行計劃。嚴格使用以下格式：

<plan>
  <analysis>任務分析...</analysis>
  <steps>
    <step>步驟 1 描述</step>
    <step>步驟 2 描述</step>
  </steps>
</plan>"""

    response = await planner.call_ollama(prompt, planner.SYSTEM_PROMPT)
    print(f"\n📋 Planner 回應: {response[:300]}...")
    
    # 用正則表達式解析 <plan>、<analysis>、<steps>、<step> 標籤
    plan_match = re.search(r'<plan>(.*?)</plan>', response, re.DOTALL)
    analysis_match = re.search(r'<analysis>(.*?)</analysis>', response, re.DOTALL)
    steps_match = re.search(r'<steps>(.*?)</steps>', response, re.DOTALL)
    
    steps = []
    if steps_match:
        steps = [s.strip() for s in re.findall(r'<step>(.*?)</step>', steps_match.group(1), re.DOTALL)]
    
    return {
        "raw": response,
        "analysis": analysis_match.group(1).strip() if analysis_match else "",
        "steps": steps if steps else []
    }


async def execute_plan(generator: Generator, plan: dict, context: str, generator_id: int) -> dict:
    # 階段二：Generator 執行計劃
    # 逐個步驟呼叫 Generator，對每個步驟進行 shell 命令循環
    if not plan.get("steps"):
        return {
            "generator_id": generator_id,
            "success": False,
            "output": "無執行步驟",
            "steps_output": []
        }
    
    steps_output = []
    all_outputs = []
    
    for i, step in enumerate(plan["steps"]):
        print(f"\n  [Generator {generator_id}] 執行步驟 {i+1}: {step}")
        
        step_outputs = []
        
        # 建構 prompt 讓 Generator 知道完整的計劃和當前步驟
        prompt = f"""<context>{context}</context>
<plan>
  <analysis>{plan.get('analysis', '')}</analysis>
  <steps>{''.join(f'<step>{s}</step>' for s in plan['steps'])}</steps>
</plan>
<current_step>{step}</current_step>

執行此步驟。嚴格使用以下格式：
- 用 <shell> 標籤輸出命令：<shell>你的命令</shell>
- 完成後用 <done/> 結束"""

        response = await generator.call_ollama(prompt, generator.SYSTEM_PROMPT)
        
        current_response = response
        
        # 對單一步驟進行 shell 命令循環（類似 Agent0.run 但使用 <done/>）
        while True:
            if "<done/>" in current_response:
                before_done = current_response.split("<done/>")[0].strip()
                if before_done:
                    all_outputs.append(f"步驟 {i+1}: {before_done}")
                break
            
            shell_matches = re.findall(r'<shell>(.+?)</shell>', current_response, re.DOTALL)
            if not shell_matches:
                if current_response.strip():
                    all_outputs.append(f"步驟 {i+1}: {current_response.strip()}")
                break
            
            for cmd in shell_matches:
                cmd = cmd.strip()
                returncode, output = await generator.execute_shell(cmd)
                step_outputs.append({"command": cmd, "output": output, "returncode": returncode})
                all_outputs.append(f"步驟 {i+1}: {cmd}\n{output}")
            
            follow_up = f"""<context>{context}</context>
<previous_response>{current_response}</previous_response>
<output>{chr(10).join([f'{s["command"]}: {s["output"]}' for s in step_outputs[-len(shell_matches):]])}</output>

继续或完成。用 <done/> 结束。"""
            current_response = await generator.call_ollama(follow_up, generator.SYSTEM_PROMPT)
        
        steps_output.append({
            "step": step,
            "response": response,
            "outputs": step_outputs
        })
    
    return {
        "generator_id": generator_id,
        "success": True,
        "output": "\n\n".join(all_outputs),
        "steps_output": steps_output
    }


async def evaluate_output(evaluator: Evaluator, user_input: str, generator_outputs: list, plan: dict, evaluator_id: int) -> dict:
    # 階段三：Evaluator 評估 Generator 的輸出
    # 檢查輸出是否滿足使用者要求，回傳 PASS/FAIL、分數和反饋
    outputs_text = "\n\n---\n\n".join([
        f"Generator {o['generator_id']}:\n{o['output']}"
        for o in generator_outputs
    ])
    
    prompt = f"""<user_input>{user_input}</user_input>
<plan>
  <analysis>{plan.get('analysis', '')}</analysis>
  <steps>{''.join(f'<step>{s}</step>' for s in plan.get('steps', []))}</steps>
</plan>
<generator_outputs>{outputs_text}</generator_outputs>

請評估輸出是否滿足要求。嚴格使用以下格式：

<evaluation>
  <result>PASS</result>
  <score>8</score>
  <feedback>評估說明...</feedback>
</evaluation>

<result> 必須是 PASS 或 FAIL。"""

    response = await evaluator.call_ollama(prompt, evaluator.SYSTEM_PROMPT)
    print(f"\n  [Evaluator {evaluator_id}] 評估結果: {response[:200]}...")
    
    # 用正則表達式解析 <result>、<feedback>、<score> 標籤
    result_match = re.search(r'<result>(PASS|FAIL)</result>', response, re.IGNORECASE)
    feedback_match = re.search(r'<feedback>(.*?)</feedback>', response, re.DOTALL)
    score_match = re.search(r'<score>(\d+)</score>', response)
    
    passed = result_match and result_match.group(1).upper() == "PASS"
    
    return {
        "evaluator_id": evaluator_id,
        "passed": passed,
        "score": int(score_match.group(1)) if score_match else (8 if passed else 0),
        "raw": response,
        "feedback": feedback_match.group(1).strip() if feedback_match else ""
    }


async def review_evaluations(planner: Planner, evaluations: list, plan: dict) -> dict:
    # 階段四：Planner 綜整所有 Evaluator 的評估結果
    # 決定 complete（完成）/ continue（繼續改進）/ abandon（放棄）
    eval_text = "\n\n".join([
        f"Evaluator {e['evaluator_id']}: PASS={e['passed']}, feedback={e['feedback']}"
        for e in evaluations
    ])
    
    prompt = f"""<plan>
  <analysis>{plan.get('analysis', '')}</analysis>
  <steps>{''.join(f'<step>{s}</step>' for s in plan.get('steps', []))}</steps>
</plan>
<evaluations>{eval_text}</evaluations>

請匯總所有評估結果，用 <decision> 標籤輸出決定：
- <decision>complete</decision>：所有 evaluator 通過，任務完成
- <decision>continue</decision>：需要繼續優化
- <decision>abandon</decision>：無法完成

同時用 <summary> 標籤輸出匯總說明。"""

    response = await planner.call_ollama(prompt, planner.SYSTEM_PROMPT)
    
    # 解析 <decision> 和 <summary> 標籤
    decision_match = re.search(r'<decision>(complete|continue|abandon)</decision>', response, re.IGNORECASE)
    summary_match = re.search(r'<summary>(.*?)</summary>', response, re.DOTALL)
    
    decision = decision_match.group(1).lower() if decision_match else "continue"
    
    return {
        "decision": decision,
        "summary": summary_match.group(1).strip() if summary_match else "",
        "raw": response,
        "all_passed": all(e["passed"] for e in evaluations)
    }


async def run_team_loop(user_input: str, num_generators: int = NUM_GENERATORS, num_evaluators: int = NUM_EVALUATORS, max_iterations: int = MAX_ITERATIONS, debug: bool = False) -> tuple[str, list]:
    # === 團隊主循環 ===
    # 建立一個 Planner、多個 Generator、多個 Evaluator
    # 迭代執行：計劃 → 執行 → 評估 → 綜整決定
    planner = Planner(workspace=WORKSPACE, model=MODEL, reviewer_model=MODEL)
    generators = [Generator(workspace=WORKSPACE, model=MODEL, reviewer_model=MODEL) for _ in range(num_generators)]
    evaluators = [Evaluator(workspace=WORKSPACE, model=MODEL, reviewer_model=MODEL) for _ in range(num_evaluators)]
    
    team_log = []
    iteration = 0
    last_feedback = None
    
    print(f"\n{'='*50}")
    print(f"Team Loop 開始 - Generators: {num_generators}, Evaluators: {num_evaluators}")
    print(f"{'='*50}")
    
    while iteration < max_iterations:
        print(f"\n--- 迭代 {iteration + 1}/{max_iterations} ---")
        
        if debug:
            print(f"[DEBUG] Planner 制定計劃...")
        
        # 步驟一：Planner 制定計劃（可選：傳入上一輪的回饋）
        plan = await plan_task(planner, user_input, planner.build_context(), last_feedback)
        
        if debug:
            print(f"[DEBUG] 計劃: {plan.get('analysis', '')[:100]}...")
            print(f"[DEBUG] 步驟數: {len(plan.get('steps', []))}")
        
        # 步驟二：所有 Generator 執行計劃（平行順序執行）
        generator_outputs = []
        for i, gen in enumerate(generators):
            print(f"\n▶ Generator {i} 執行中...")
            output = await execute_plan(gen, plan, gen.build_context(), i)
            generator_outputs.append(output)
            print(f"✓ Generator {i} 完成")
        
        # 步驟三：所有 Evaluator 評估輸出（平行順序執行）
        evaluators_results = []
        for i, ev in enumerate(evaluators):
            print(f"\n▶ Evaluator {i} 評估中...")
            result = await evaluate_output(ev, user_input, generator_outputs, plan, i)
            evaluators_results.append(result)
            print(f"✓ Evaluator {i} 評估: {'PASS' if result['passed'] else 'FAIL'}")
        
        # 步驟四：Planner 綜整評估結果並做出決策
        review = await review_evaluations(planner, evaluators_results, plan)
        
        # 記錄本次迭代的完整日誌
        team_log.append({
            "iteration": iteration + 1,
            "plan": plan,
            "generator_outputs": generator_outputs,
            "evaluators_results": evaluators_results,
            "review": review
        })
        
        print(f"\n📊 Planner 決定: {review['decision']}")
        
        if review["decision"] == "complete":
            # 任務完成：回傳第一個 Generator 的輸出
            final_output = generator_outputs[0]["output"] if generator_outputs else "任務完成"
            return final_output, team_log
        
        if review["decision"] == "abandon":
            # 放棄任務
            return f"任務無法完成：{review['summary']}", team_log
        
        # 繼續迭代：將 Planner 的 summary 作為 feedback 傳入下一輪
        last_feedback = review["summary"]
        iteration += 1
    
    # 達到最大迭代次數仍未完成
    return "達到最大迭代次數", team_log


def main():
    # 命令列參數解析，支援設定 Generator/Evaluator 數量和除錯模式
    parser = argparse.ArgumentParser(description="Agent0 Team")
    parser.add_argument("--generators", "-g", type=int, default=NUM_GENERATORS, help="Generator 數量")
    parser.add_argument("--evaluators", "-e", type=int, default=NUM_EVALUATORS, help="Evaluator 數量")
    parser.add_argument("--max-iterations", "-i", type=int, default=MAX_ITERATIONS, help="最大迭代次數")
    parser.add_argument("--debug", "-d", action="store_true", help="除錯模式")
    args = parser.parse_args()
    
    os.makedirs(WORKSPACE, exist_ok=True)
    
    print(f"Agent0 Team - {MODEL}")
    print(f"Generators: {args.generators}, Evaluators: {args.evaluators}, Max Iterations: {args.max_iterations}")
    print(f"工作區：{WORKSPACE}")
    print("指令：/quit、/memory\n")
    
    while True:
        try:
            user_input = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！")
            break
        
        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            print("再見！")
            break
        if user_input.lower() == "/memory":
            print("團隊記憶功能開發中...")
            continue
        
        # 啟動團隊循環
        response, team_log = asyncio.run(run_team_loop(
            user_input,
            num_generators=args.generators,
            num_evaluators=args.evaluators,
            max_iterations=args.max_iterations,
            debug=args.debug
        ))
        
        print(f"\n{'='*50}")
        print(f"🤖 最終回覆:")
        print(f"{response}")
        print(f"{'='*50}")
        
        if args.debug:
            print(f"\n📊 團隊執行記錄：{len(team_log)} 次迭代")


if __name__ == "__main__":
    main()
