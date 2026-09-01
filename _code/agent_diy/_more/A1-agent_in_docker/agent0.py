#!/usr/bin/env python3
# agent0.py - AI Agent with memory and tool feedback
# Run: python agent0.py

import subprocess
import os
import asyncio
import aiohttp
import re

# ─── Configuration ───

# 工作目錄，存放 Agent 相關檔案
WORKSPACE = os.path.expanduser("~/.agent0")
# 沙盒目錄，掛載到 Docker 容器內作為安全執行環境
SANDBOX = os.path.expanduser("~/.agent0_sandbox")
# 主 LLM 模型
MODEL = "minimax-m2.5:cloud"
# 最大工具使用回合數
MAX_TURNS = 5
# Docker 映像檔名稱，使用輕量級的 Alpine Linux
DOCKER_IMAGE = "alpine:latest"

# ─── Memory ───

conversation_history = []
key_info = []

# ─── Docker Security ───

def run_in_docker(cmd):
    # 將所有命令包裝在 docker run 中執行，達到沙盒隔離效果
    timeout = 60
    # 若是啟動伺服器的長期命令，延長 timeout 並使用 nohup 背景執行
    if any(kw in cmd for kw in ["uvicorn", "python.*server", "npm start", "node.*server"]):
        timeout = 300
        cmd = f"nohup {cmd} > /dev/null 2>&1 &"
    
    # 建構 docker run 命令：
    # --rm：容器執行後自動刪除
    # -v SANDBOX:/sandbox：掛載沙盒目錄
    # -p 3000-9000:3000-9000：暴露埠範圍供 Web 服務使用
    # --memory=256m：限制容器記憶體
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{SANDBOX}:/sandbox",
        "-p", "3000-9000:3000-9000",
        "-w", "/sandbox",
        "--memory=256m",
        DOCKER_IMAGE,
        "sh", "-c", cmd
    ]
    result = subprocess.run(
        docker_cmd,
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        return f"錯誤：{result.stderr}"
    return result.stdout

# ─── Ollama API ───

async def call_ollama(prompt: str, system: str = "") -> str:
    """Call Ollama API"""
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

# ─── Memory Management ───

def build_context():
    context_parts = []
    if key_info:
        items_xml = "\n".join(f"  <item>{k}</item>" for k in key_info)
        context_parts.append(f"<memory>\n{items_xml}\n</memory>")
    if conversation_history:
        context_parts.append("<history>\n" + "\n".join(conversation_history[-MAX_TURNS*2:]) + "\n</history>")
    return "\n\n".join(context_parts)

def update_memory(user_input, assistant_response, tool_result=None):
    conversation_history.append(f"  <user>{user_input}</user>")
    conversation_history.append(f"  <assistant>{assistant_response}</assistant>")
    if tool_result:
        conversation_history.append(f"  <tool>{tool_result[:500]}</tool>")
    
    while len(conversation_history) > MAX_TURNS * 4:
        conversation_history.pop(0)

async def extract_key_info(user_input, assistant_response):
    extract_prompt = f"""根據這段對話，有沒有需要長期記憶的關鍵資訊？
如果有，用以下格式輸出（最多 2 項）。如果沒有，輸出 <memory></memory>。

<memory>
  <item>要記憶的資訊 1</item>
  <item>要記憶的資訊 2</item>
</memory>

對話：
<user>{user_input}</user>
<assistant>{assistant_response}</assistant>"""
    
    try:
        result = await call_ollama(extract_prompt, "")
        matches = re.findall(r'<item>(.*?)</item>', result, re.DOTALL)
        for item in matches:
            item = item.strip()
            if item and item not in key_info:
                key_info.append(item)
    except:
        pass

# ─── Agent ───

SYSTEM_PROMPT = """你是 Jarvis，一個有用的 AI 助理。

重要規則：
1. 當你需要執行 shell 命令時，必須用 <shell> 標籤包住命令
2. <shell> 標籤內可以是多行命令（用反斜槓 \\ 或 && 連接）
3. 當你完成所有操作後，用 <end/> 結束你的回覆

流程：
- 如果需要執行命令，輸出 <shell>...</shell>
- 執行完後我會顯示結果
- 如果還需要更多命令，繼續輸出 <shell>
- 當完成所有操作後，輸出 <end/> 表示結束"""

def main():
    os.makedirs(WORKSPACE, exist_ok=True)
    os.makedirs(SANDBOX, exist_ok=True)
    
    print(f"Agent0 - {MODEL}（含記憶功能，Docker 隔離）")
    print(f"工作區：{WORKSPACE}")
    print(f"沙盒目錄：{SANDBOX}")
    print("指令：/quit、/memory（顯示關鍵資訊）\n")
    
    while True:
        try:
            user_input = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！")
            break
        
        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/q"]:
            print("再見！")
            break
        if user_input.lower() == "/memory":
            print(f"關鍵資訊：{key_info}")
            continue
        
        context = build_context()
        full_prompt = f"{context}\n\n<user>{user_input}</user>" if context else f"<user>{user_input}</user>"
        
        response = asyncio.run(call_ollama(full_prompt, SYSTEM_PROMPT))
        
        tool_result = None
        current_response = response
        
        while True:
            if "<end/>" in current_response:
                response = current_response.split("<end/>")[0].strip()
                break
            
            shell_matches = re.findall(r'<shell>(.+?)</shell>', current_response, re.DOTALL)
            if not shell_matches:
                response = current_response
                break
            
            all_outputs = []
            for cmd in shell_matches:
                cmd = cmd.strip()
                try:
                    # === Docker 隔離執行 ===
                    # 所有命令都在 Docker 容器內執行，而非主機
                    output = run_in_docker(cmd)
                    print(f"\n=== 執行命令 ===\n{cmd}\n\n結果：{output if output else '（無輸出）'}\n")
                    all_outputs.append(f"$ {cmd}\n{output if output else '（無輸出）'}")
                except Exception as e:
                    print(f"錯誤：{e}")
                    all_outputs.append(f"$ {cmd}\n錯誤：{e}")
            
            tool_result = (tool_result or "") + "\n" + "\n".join(all_outputs)
            
            follow_up_prompt = f"""<context>{context}</context>

<user>{user_input}</user>
<assistant>{current_response}</assistant>
<output>
{chr(10).join(all_outputs)}
</output>

如果需要更多命令就輸出 <shell>。否則，輸出 <end/> 表示結束："""
            current_response = asyncio.run(call_ollama(follow_up_prompt, SYSTEM_PROMPT))
        
        print(f"\n🤖 {response}\n")
        
        update_memory(user_input, response, tool_result)
        if tool_result:
            asyncio.run(extract_key_info(user_input, response))

if __name__ == "__main__":
    main()
