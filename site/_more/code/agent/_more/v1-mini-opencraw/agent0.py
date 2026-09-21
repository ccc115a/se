#!/usr/bin/env python3
# 修改自：
#   https://gist.github.com/dabit3/86ee04a1c02c839409a02b20fe99a492
#   mini-openclaw.py - A minimal OpenClaw clone
# ccc 重新命名為：
#   agent0.py - AI Agent using Ollama
# Run: python agent0.py

import subprocess
import json
import os
import asyncio
import aiohttp
import re

# ─── Configuration ───

# 工作目錄，用於存放 Agent 產生的檔案
WORKSPACE = os.path.expanduser("~/.agent0")
# 使用的 Ollama 模型名稱
MODEL = "minimax-m2.5:cloud"

# ─── Tools ───

# 定義工具列表，每個工具包含名稱、描述和輸入 schema
# LLM 會根據這些描述決定何時呼叫哪個工具
TOOLS = [
    {
        "name": "run_command",
        "description": "Run a shell command",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command to run"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a file from the filesystem",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    },
]

# ─── Ollama API ───

async def call_ollama(prompt: str, system: str = "") -> str:
    """Call Ollama API"""
    # 若有 system prompt，將其附加在使用者 prompt 前方
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as resp:
            result = await resp.json()
            return result.get("response", "").strip()

# ─── Tool Execution ───

def execute_tool(name, tool_input):
    if name == "run_command":
        try:
            # 執行 shell 命令，捕獲 stdout + stderr，30 秒超時
            result = subprocess.run(
                tool_input["command"], shell=True, 
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout + result.stderr
            return output if output else "(no output)"
        except Exception as e:
            return f"Error: {e}"
    
    elif name == "read_file":
        try:
            # 讀取檔案內容，限制前 10000 字元防止上下文爆量
            with open(tool_input["path"], "r") as f:
                return f.read()[:10000]
        except Exception as e:
            return f"Error: {e}"
    
    elif name == "write_file":
        try:
            # 寫入檔案，自動建立父目錄
            os.makedirs(os.path.dirname(tool_input["path"]) or ".", exist_ok=True)
            with open(tool_input["path"], "w") as f:
                f.write(tool_input["content"])
            return f"Wrote to {tool_input['path']}"
        except Exception as e:
            return f"Error: {e}"
    
    return f"Unknown tool: {name}"

# ─── Agent ───

# System prompt 告知 LLM 如何使用工具，採用 <tool>JSON</tool> 格式表達工具呼叫
SYSTEM_PROMPT = """You are Jarvis, a helpful AI assistant.
You have tools - use them to help the user.

Available tools:
- run_command: Run a shell command
- read_file: Read a file
- write_file: Write to a file

When you need to use a tool, output in this format:
<tool>
{"name": "tool_name", "input": {"key": "value"}}
</tool>

Otherwise, just respond directly."""

def main():
    os.makedirs(WORKSPACE, exist_ok=True)
    
    print(f"Agent0 - {MODEL}")
    print(f"Workspace: {WORKSPACE}")
    print("Commands: /quit\n")
    
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
        
        # 呼叫 Ollama 取得回覆（不含對話歷史，無多輪循環）
        response = asyncio.run(call_ollama(user_input, SYSTEM_PROMPT))
        
        # 檢查 LLM 回覆中是否包含 <tool> 標籤（表示需要執行工具）
        tool_match = re.search(r'<tool>(.+?)</tool>', response, re.DOTALL)
        if tool_match:
            try:
                # 解析 JSON 格式的工具呼叫
                tool_data = json.loads(tool_match.group(1))
                tool_name = tool_data.get("name")
                tool_input = tool_data.get("input", {})
                
                print(f"  🔧 {tool_name}: {tool_input}")
                
                # 執行工具並顯示結果（僅顯示前 150 字元）
                result = execute_tool(tool_name, tool_input)
                print(f"     → {result[:150]}")
            except Exception as e:
                print(f"Tool error: {e}")
        else:
            # 無工具呼叫，直接顯示 LLM 回覆
            print(f"\n🤖 {response}\n")

if __name__ == "__main__":
    main()
