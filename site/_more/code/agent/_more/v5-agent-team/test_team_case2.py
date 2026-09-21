#!/usr/bin/env python3
# test_team_case2.py - 測試個案 2: 伊朗戰情報告
import agent0team
import asyncio
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


async def test_iran_war_report():
    # 端到端測試：要求 Agent 團隊搜集網路資訊並產出報告
    # 使用 3 個 Generator + 2 個 Evaluator 的較大規模團隊配置
    print("=" * 60)
    print("測試個案 2: 伊朗戰情報告")
    print("=" * 60)
    
    user_input = "請搜集今日的伊朗戰情，寫一份報告放在 _doc/report_war.md 中"
    
    response, team_log = await agent0team.run_team_loop(
        user_input,
        num_generators=3,
        num_evaluators=2,
        max_iterations=2,
        debug=True
    )
    
    print("\n" + "=" * 60)
    print("執行結果:")
    print("=" * 60)
    print(f"回覆: {response[:500]}...")
    print(f"\n迭代次數: {len(team_log)}")
    
    for i, log in enumerate(team_log):
        print(f"\n--- 迭代 {i+1} ---")
        plan = log.get("plan", {})
        print(f"Planner 分析: {plan.get('analysis', '')[:200]}...")
        print(f"Planner 步驟數: {len(plan.get('steps', []))}")
        
        print(f"Generator 數量: {len(log.get('generator_outputs', []))}")
        for gen in log.get("generator_outputs", []):
            print(f"  Generator {gen['generator_id']}: {gen['output'][:150] if gen['output'] else '（無）'}...")
        
        print(f"Evaluator 數量: {len(log.get('evaluators_results', []))}")
        for ev in log.get("evaluators_results", []):
            print(f"  Evaluator {ev['evaluator_id']}: PASS={ev['passed']}")
        
        print(f"Planner 決定: {log.get('review', {}).get('decision', 'unknown')}")
    
    report_path = os.path.join(PROJECT_DIR, "_doc", "report_war.md")
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            content = f.read()
        print(f"\n✓ 報告已建立: {report_path}")
        print(f"  字數: {len(content)}")
    else:
        print(f"\n✗ 報告尚未建立: {report_path}")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_iran_war_report())
    sys.exit(0 if success else 1)
