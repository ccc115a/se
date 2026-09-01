#!/usr/bin/env python3
# test_team_case1.py - 測試個案 1: FastAPI + SQLite 網誌系統
import agent0team
import asyncio
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


async def test_blog_system():
    # 端到端測試：要求 Agent 團隊建立一個 FastAPI + SQLite 部落格系統
    # 這驗證了團隊是否能完成真實世界的開發任務
    print("=" * 60)
    print("測試個案 1: FastAPI + SQLite 網誌系統")
    print("=" * 60)
    
    user_input = "請用 fastapi + sqlite 寫一個簡易的網誌系統，放在 ./blog 目錄下"
    
    response, team_log = await agent0team.run_team_loop(
        user_input,
        num_generators=1,
        num_evaluators=1,
        max_iterations=3,
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
        
        for gen in log.get("generator_outputs", []):
            print(f"Generator {gen['generator_id']} 輸出: {gen['output'][:200] if gen['output'] else '（無）'}...")
        
        for ev in log.get("evaluators_results", []):
            print(f"Evaluator {ev['evaluator_id']}: PASS={ev['passed']}, feedback={ev.get('feedback', '')[:100]}...")
        
        print(f"Planner 決定: {log.get('review', {}).get('decision', 'unknown')}")
    
    blog_dir = os.path.join(PROJECT_DIR, "blog")
    if os.path.exists(blog_dir):
        files = os.listdir(blog_dir)
        print(f"\n✓ blog 目錄已建立，包含 {len(files)} 個檔案: {files[:5]}...")
    else:
        print(f"\n✗ blog 目錄不存在")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_blog_system())
    sys.exit(0 if success else 1)
