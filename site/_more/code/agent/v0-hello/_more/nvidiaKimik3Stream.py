# https://build.nvidia.com/moonshotai/kimi-k3
import requests
import os

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = True

# 自動讀取系統環境變數 NVIDIA_API_KEY
api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    raise ValueError("找不到 NVIDIA_API_KEY 環境變數，請先設定！")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "text/event-stream" if stream else "application/json",
}

payload = {
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What is in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1b.jpg"
          }
        }
      ]
    }
  ],
  "model": "moonshotai/kimi-k3",
  "max_tokens": 16384,
  "seed": 0,
  "stream": stream,
  "temperature": 1,
  "reasoning_effort": "max"
}

response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())