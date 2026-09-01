#!/usr/bin/env python3
"""
Ollama 本地模型 Hello World
前置需求：
1. ollama serve 已在背景執行
2. ollama pull qwen3.5:2b
3. pip install requests
"""

import requests

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen3.5:2b",
        "messages": [{"role": "user", "content": "請說 Hello, World！並簡單自我介紹一句"}],
        "stream": False,
        "think": False,  # 關閉思考模式，回應更快、更直接
    },
)

reply = response.json()["message"]["content"]
print(reply)