#!/usr/bin/env python3
# test_team.py - 測試 Agent0Team
import agent0team
import asyncio
import sys

async def test_basic():
    # 測試 1：基本團隊循環（1 Generator + 1 Evaluator，1 次迭代）
    # 驗證最少配置能否正常運作
    print("=== 測試 1: 基本團隊循環 ===")
    user_input = "請說 'Hello World'"
    
    response, team_log = await agent0team.run_team_loop(
        user_input,
        num_generators=1,
        num_evaluators=1,
        max_iterations=1,
        debug=True
    )
    
    print(f"\n回覆: {response[:200]}...")
    print(f"迭代次數: {len(team_log)}")
    
    assert len(team_log) == 1, "應有 1 次迭代"
    print("✓ 測試 1 通過\n")
    return True


async def test_iteration():
    # 測試 2：多迭代測試（max_iterations=2）
    # 驗證迭代次數限制是否能正確生效
    print("=== 測試 2: 多迭代測試 ===")
    user_input = "計算 1+1 等於多少"
    
    response, team_log = await agent0team.run_team_loop(
        user_input,
        num_generators=1,
        num_evaluators=1,
        max_iterations=2,
        debug=False
    )
    
    print(f"迭代次數: {len(team_log)}")
    print(f"回覆: {response[:100]}...")
    
    assert len(team_log) <= 2, "迭代次數應 <= 2"
    print("✓ 測試 2 通過\n")
    return True


async def test_multi_generator():
    # 測試 3：多 Generator 測試
    # 驗證多個執行者是否能正確平行運作
    print("=== 測試 3: 多 Generator ===")
    user_input = "列出目前目錄的檔案"
    
    response, team_log = await agent0team.run_team_loop(
        user_input,
        num_generators=2,
        num_evaluators=1,
        max_iterations=1,
        debug=False
    )
    
    gen_count = len(team_log[0]["generator_outputs"])
    print(f"Generator 數量: {gen_count}")
    
    assert gen_count == 2, "應有 2 個 Generator"
    print("✓ 測試 3 通過\n")
    return True


async def test_multi_evaluator():
    # 測試 4：多 Evaluator 測試
    # 驗證多個評估者是否能正確平行運作
    print("=== 測試 4: 多 Evaluator ===")
    user_input = "說 '測試'"
    
    response, team_log = await agent0team.run_team_loop(
        user_input,
        num_generators=1,
        num_evaluators=2,
        max_iterations=1,
        debug=False
    )
    
    eval_count = len(team_log[0]["evaluators_results"])
    print(f"Evaluator 數量: {eval_count}")
    
    assert eval_count == 2, "應有 2 個 Evaluator"
    print("✓ 測試 4 通過\n")
    return True


async def run_all_tests():
    print("=" * 50)
    print("Agent0Team 測試開始")
    print("=" * 50 + "\n")
    
    tests = [
        test_basic,
        test_iteration,
        test_multi_generator,
        test_multi_evaluator,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"✗ 測試失敗: {e}\n")
            failed += 1
    
    print("=" * 50)
    print(f"測試結果: {passed} 通過, {failed} 失敗")
    print("=" * 50)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
