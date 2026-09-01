#!/usr/bin/env python3
# agent0.py - AI Agent with memory and tool feedback（含雙層安全機制）
# Run: python agent0.py

import subprocess
import os
import asyncio
import aiohttp
import re

# ─── Configuration ───

WORKSPACE = os.path.expanduser("~/.agent0")
MODEL = "minimax-m2.5:cloud"
REVIEWER_MODEL = "minimax-m2.5:cloud"
MAX_TURNS = 5

# ─── Memory ───

conversation_history = []
key_info = []
# 已獲使用者授權的外部路徑集合，避免重複詢問
outside_access_granted = set()

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

async def review_command(cmd: str) -> tuple[bool, str]:
    """Use another Ollama model to review if command is safe"""
    # === 第一層安全防護：LLM 安全審查 ===
    # 使用獨立 Reviewer 模型判斷命令是否安全
    review_prompt = f"""你是安全審查者。請判斷以下 shell 命令是否安全可以執行。

安全原則：
1. 允許讀取檔案、瀏覽目錄、搜尋程式碼
2. 允許執行無害的開發工具（git, ls, cat, grep, find, python, node 等）
3. 禁止會刪除資料的命令（rm -rf, dd, mkfs 等）
4. 禁止會修改系統的命令（sudo, chmod 777, 修改系統設定等）
5. 禁止網路相關的危险操作（curl/wget 下載並執行腳本等）
6. 禁止任何可能造成資料洩露或系統傷害的命令

要審查的命令：
{cmd}

請嚴格按照以下格式輸出：
- 如果安全，輸出：SAFE
- 如果不安全，輸出：UNSAFE - 原因

不要輸出其他內容。"""

    payload = {
        "model": REVIEWER_MODEL,
        "prompt": review_prompt,
        "stream": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                result = await resp.json()
                response = result.get("response", "").strip()
                
                if response.startswith("SAFE"):
                    return True, ""
                else:
                    reason = response.replace("UNSAFE", "").strip(" -")
                    return False, reason
    except Exception as e:
        return False, f"審查失敗: {e}"

def check_outside_access(cmd: str, cwd: str) -> tuple[bool, str]:
    # === 第二層安全防護：目錄存取控制 ===
    # 用正則表達式解析命令中的路徑參數，檢查是否試圖存取目前目錄以外
    import os.path
    
    def extract_paths(c):
        paths = []
        # 匹配三種模式：絕對路徑命令參數、../ 開頭、單獨的 ..
        patterns = [
            (r'(?:^|\s)(?:cat|ls|cd|rm|cp|mv|chmod|chown|find|grep)\s+(/[^\s]+)', 1),
            (r'(?:^|\s)\.\./[^\s]*', 0),
            (r'(?:^|\s)\.\.(?:\s|$)', 0),
        ]
        for pattern, group in patterns:
            for match in re.finditer(pattern, c, re.MULTILINE):
                path = match.group(group).strip() if group > 0 else ".."
                if path:
                    paths.append(path)
        return paths
    
    paths = extract_paths(cmd)
    
    cwd_abs = os.path.abspath(cwd)
    
    for path in paths:
        if path.startswith('/'):
            abs_path = path
        else:
            abs_path = os.path.abspath(os.path.join(cwd, path))
        
        # 若路徑為 .. 或以 ../ 開頭，表示試圖離開目前目錄
        if path == '..' or path.startswith('../'):
            return True, abs_path
        
        # 若絕對路徑不在 cwd 底下，表示試圖存取外部檔案
        if not abs_path.startswith(cwd_abs):
            return True, abs_path
    
    return False, ""

def ask_outside_access(path: str) -> bool:
    # 詢問使用者是否允許存取外部目錄
    print(f"\n⚠️  命令嘗試存取本資料夾以外的檔案: {path}")
    print("   是否允許？（y/N）：", end=" ")
    try:
        response = input().strip().lower()
        return response in ['y', 'yes']
    except:
        return False

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
    
    print(f"Agent0 - {MODEL}（含記憶功能）")
    print(f"工作區：{WORKSPACE}")
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
                
                # === 第一層安全檢查：LLM 審查 ===
                is_safe, reason = asyncio.run(review_command(cmd))
                
                if not is_safe:
                    print(f"\n⚠️  命令被安全審查阻止：{cmd}")
                    print(f"   原因：{reason}\n")
                    all_outputs.append(f"$ {cmd}\n阻止：{reason}")
                    continue
                
                # === 第二層安全檢查：目錄存取控制 ===
                needs_access, path = check_outside_access(cmd, os.getcwd())
                if needs_access:
                    if path in outside_access_granted:
                        # 已授權的路徑不再重複詢問
                        pass
                    else:
                        if not ask_outside_access(path):
                            print(f"\n⚠️  已拒絕存取：{path}\n")
                            all_outputs.append(f"$ {cmd}\n拒絕：{path}")
                            continue
                        outside_access_granted.add(path)
                
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=os.getcwd())
                    output = result.stdout + result.stderr
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
