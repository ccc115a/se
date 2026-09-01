#!/usr/bin/env python3
# see_image.py - 用 qwen3.5:2b 看圖片
# Run: python see_image.py photo.jpg

import sys
import base64
import requests

image_path = sys.argv[1] if len(sys.argv) > 1 else "picture1.png"

with open(image_path, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen3.5:2b",
        "messages": [
            {
                "role": "user",
                "content": "這張圖片裡有什麼？請用中文描述。",
                "images": [image_base64],
            }
        ],
        "stream": False,
    },
)

print(response.json()["message"]["content"])