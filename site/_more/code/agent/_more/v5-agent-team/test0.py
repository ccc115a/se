#!/usr/bin/env python3
# 從 agent0 模組匯入 Agent0 類別進行互動測試
import agent0
import asyncio

import sys
import os

async def run():
    # 建立 Agent0 實例，設定工作目錄
    agent = agent0.Agent0()
    agent.workspace = os.path.expanduser("~/.agent0")
    os.makedirs(agent.workspace, exist_ok=True)
    
    print(f"Agent0 - {agent.model}")
    print("指令：/quit、/memory\n")
    
    while True:
        # REPL 循環：讀取使用者輸入並委派給 agent.run()
        user_input = input("你：").strip()
        
        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            print("再見！")
            break
        if user_input.lower() == "/memory":
            print(f"關鍵資訊：{agent.key_info}")
            continue
        
        # run() 回傳 (response_text, tool_result) 元組
        response, tool_result = await agent.run(user_input)
        
        print(f"\n🤖 {response}\n")

if __name__ == "__main__":
    asyncio.run(run())
