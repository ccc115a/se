#!/usr/bin/env python3
# chat0.py - AI Chat using Ollama (串流 + 即時顯示思考過程版)
# Run: python chat0.py

import asyncio
import aiohttp
import json
import os

# Ollama 模型名稱
# MODEL = "minimax-m2.5:cloud"
MODEL = "qwen3.5:2b"

async def chat_ollama(messages: list) -> str:
    """Call Ollama API with chat format (streaming)

    一邊收到 chunk 就一邊印出（思考過程與正式回答分開標示）。
    回傳完整的正式回答文字（不含思考過程），供加入對話歷史使用。
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "think": True,  # 開啟思考模式
    }

    full_content = ""
    printed_thinking_header = False
    printed_answer_header = False

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            async for line in resp.content:
                if not line.strip():
                    continue
                chunk = json.loads(line)
                message = chunk.get("message", {})

                thinking_piece = message.get("thinking", "")
                content_piece = message.get("content", "")

                if thinking_piece:
                    if not printed_thinking_header:
                        print("\n============ 💭 思考過程 =================\n")
                        printed_thinking_header = True
                    print(thinking_piece, end="", flush=True)

                if content_piece:
                    if not printed_answer_header:
                        # 思考過程與正式回答之間換行分隔
                        print("\n\n============= 🤖 正式回答 ===============\n", end="", flush=True)
                        printed_answer_header = True
                    print(content_piece, end="", flush=True)
                    full_content += content_piece

                if chunk.get("done"):
                    print()  # 最後換行

    return full_content.strip()

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

        # 呼叫 Ollama 取得回覆（串流即時印出）
        response = asyncio.run(chat_ollama(messages))
        # 將助理回覆加入歷史（只存正式回答，不存思考過程）
        messages.append({"role": "assistant", "content": response})

        print()

if __name__ == "__main__":
    main()