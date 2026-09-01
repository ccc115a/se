# 修改自 https://build.nvidia.com/moonshotai/kimi-k3 
import os
import requests

invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
stream = False

headers = {
    "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}",
    "Accept": "application/json",
}

# 補上完整的 payload 定義
payload = {
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1b.jpg"
                    },
                },
            ],
        }
    ],
    "model": "moonshotai/kimi-k3",
    "max_tokens": 16384,
    "seed": 0,
    "stream": stream,
    "temperature": 1,
    "reasoning_effort": "max",
}

response = requests.post(invoke_url, headers=headers, json=payload)
data = response.json()

# 直接取出完整回答
print(data["choices"][0]["message"]["content"])
