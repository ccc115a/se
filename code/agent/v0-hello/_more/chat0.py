#!/usr/bin/env python3
# chat0.py - AI Chat using Ollama
# Run: python chat0.py

import asyncio
import aiohttp
import os

# Ollama 模型名稱，使用 minimax-m2.5 雲端版本
MODEL = "minimax-m2.5:cloud"

async def chat_ollama(messages: list) -> str:
    """Call Ollama API with chat format"""
    # 使用 Ollama 的 /api/chat 端點（支援 messages 陣列格式）
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            result = await resp.json()
            # 從回應中提取 assistant 的訊息內容
            return result.get("message", {}).get("content", "").strip()

def main():
    print(f"Chat0 - {MODEL}")
    print("Commands: /quit, /clear\n")
    
    # 維護對話歷史列表，每輪依次加入 user 和 assistant 訊息
    messages = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            print("Goodbye!")
            break
        # /clear 指令清除所有對話歷史，重新開始
        if user_input.lower() == "/clear":
            messages = []
            print("Conversation cleared.\n")
            continue
        
        # 將使用者訊息加入歷史
        messages.append({"role": "user", "content": user_input})
        
        # 呼叫 Ollama 取得回覆
        response = asyncio.run(chat_ollama(messages))
        # 將助理回覆加入歷史（維持對話上下文連貫性）
        messages.append({"role": "assistant", "content": response})
        
        print(f"\n🤖 {response}\n")

if __name__ == "__main__":
    main()
