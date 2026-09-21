#!/usr/bin/env python3
# agent0.py - AI Agent with memory and tool feedback (Class version)
# Run: python agent0.py

import subprocess
import os
import asyncio
import aiohttp
import re
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Agent0:
    # === 類別版本 Agent：將所有功能封裝為 dataclass ===
    # 此版本整合了 XML 工具協議、雙層安全防護、記憶系統
    
    # 基本配置
    workspace: str = ""
    model: str = "minimax-m2.5:cloud"
    reviewer_model: str = "minimax-m2.5:cloud"
    max_turns: int = 5
    
    # 記憶狀態
    conversation_history: list = field(default_factory=list)
    key_info: list = field(default_factory=list)
    outside_access_granted: set = field(default_factory=set)
    
    # System prompt（類別屬性，但可以透過實例覆寫）
    SYSTEM_PROMPT = """你是 Jarvis，一個有用的 AI 助理。

重要規則：
1. 當你需要執行 shell 命令時，用 <shell> 標籤包住命令
2. 如果需要多個命令，可以輸出多個 <shell> 標籤
3. 當所以命令都執行完後，用 <end/> 結束

流程：
- 輸出所有需要的 <shell>...</shell> 標籤
- 執行完後你會看到結果
- 當需要更多命令時繼續輸出 <shell>
- 全部完成後輸出 <end/>"""
    
    def __post_init__(self):
        # dataclass 初始化後，若 workspace 為空則設為預設值
        if not self.workspace:
            self.workspace = os.path.expanduser("~/.agent0")
    
    async def call_ollama(self, prompt: str, system: str = "") -> str:
        # 呼叫 Ollama API，使用實例的模型設定
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        payload = {
            "model": self.model,
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
    
    async def review_command(self, cmd: str) -> tuple[bool, str]:
        # === 第一層安全：LLM 審查 ===
        # 簡化版的審查 prompt（英文）
        review_prompt = f"""Review this command: {cmd}

Is it SAFE to run? Reply with SAFE or UNSAFE."""

        payload = {
            "model": self.reviewer_model,
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
    
    def check_outside_access(self, cmd: str, cwd: str) -> tuple[bool, str]:
        # === 第二層安全：目錄存取控制 ===
        def extract_paths(c):
            paths = []
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
            
            if path == '..' or path.startswith('../'):
                return True, abs_path
            
            if not abs_path.startswith(cwd_abs):
                return True, abs_path
        
        return False, ""
    
    def ask_outside_access(self, path: str) -> bool:
        print(f"\n⚠️  命令嘗試存取本資料夾以外的檔案: {path}")
        print("   是否允許？（y/N）：", end=" ")
        try:
            response = input().strip().lower()
            return response in ['y', 'yes']
        except:
            return False
    
    def build_context(self) -> str:
        # 建構 XML 格式的 context（記憶 + 歷史）
        context_parts = []
        if self.key_info:
            items_xml = "\n".join(f"  <item>{k}</item>" for k in self.key_info)
            context_parts.append(f"<memory>\n{items_xml}\n</memory>")
        if self.conversation_history:
            context_parts.append("<history>\n" + "\n".join(self.conversation_history[-self.max_turns*2:]) + "\n</history>")
        return "\n\n".join(context_parts)
    
    def update_memory(self, user_input: str, assistant_response: str, tool_result: str = None):
        self.conversation_history.append(f"  <user>{user_input}</user>")
        self.conversation_history.append(f"  <assistant>{assistant_response}</assistant>")
        if tool_result:
            self.conversation_history.append(f"  <tool>{tool_result[:500]}</tool>")
        
        while len(self.conversation_history) > self.max_turns * 4:
            self.conversation_history.pop(0)
    
    async def extract_key_info(self, user_input: str, assistant_response: str):
        # 用 LLM 自動提取需要長期記憶的關鍵資訊
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
            result = await self.call_ollama(extract_prompt, "")
            matches = re.findall(r'<item>(.*?)</item>', result, re.DOTALL)
            for item in matches:
                item = item.strip()
                if item and item not in self.key_info:
                    self.key_info.append(item)
        except:
            pass
    
    async def execute_shell(self, cmd: str, cwd: str = None) -> tuple[int, str]:
        # 統一的 shell 命令執行入口（含雙層安全檢查）
        print(f"\n执行命令: {cmd}")
        
        # 第一層安全：LLM 審查
        is_safe, reason = await self.review_command(cmd)
        
        if not is_safe:
            print(f"⚠️  被安全審查阻止: {reason}")
            return -1, f"阻止：{reason}"
        
        if cwd is None:
            cwd = os.getcwd()
        
        # 第二層安全：目錄存取控制
        needs_access, path = self.check_outside_access(cmd, cwd)
        if needs_access:
            if path in self.outside_access_granted:
                pass
            else:
                if not self.ask_outside_access(path):
                    print(f"⚠️  已拒絕存取：{path}")
                    return -1, f"拒絕：{path}"
                self.outside_access_granted.add(path)
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
            output = result.stdout + result.stderr
            print(f"結果: {output if output else '（無輸出）'}")
            return result.returncode, output
        except Exception as e:
            print(f"錯誤：{e}")
            return -1, f"錯誤：{e}"
    
    async def run(self, user_input: str, system_prompt: str = "") -> tuple[str, str]:
        # === 主循環入口 ===
        # 整合 context 建構、LLM 呼叫、工具循環、記憶更新
        SYSTEM = system_prompt if system_prompt else self.SYSTEM_PROMPT
        
        context = self.build_context()
        full_prompt = f"{context}\n\n<user>{user_input}</user>" if context else f"<user>{user_input}</user>"
        
        response = await self.call_ollama(full_prompt, SYSTEM)
        
        print(f"\n🤖 回應: {response[:200]}{'...' if len(response) > 200 else ''}")
        
        tool_result = None
        current_response = response
        
        while True:
            if "<end/>" in current_response:
                before_end = current_response.split("<end/>")[0].strip()
                if not before_end:
                    response = "命令已執行。" if tool_result else "完成。"
                else:
                    response = before_end
                break
            
            shell_matches = re.findall(r'<shell>(.+?)</shell>', current_response, re.DOTALL)
            if not shell_matches:
                response = current_response
                break
            
            all_outputs = []
            for cmd in shell_matches:
                cmd = cmd.strip()
                
                returncode, output = await self.execute_shell(cmd)
                
                if returncode != 0:
                    all_outputs.append(f"$ {cmd}\n{output}")
                else:
                    all_outputs.append(f"$ {cmd}\n{output if output else '（無輸出）'}")
            
            tool_result = (tool_result or "") + "\n" + "\n".join(all_outputs)
            
            follow_up_prompt = f"""<context>{context}</context>

<user>{user_input}</user>
<assistant>{current_response}</assistant>
<output>
{chr(10).join(all_outputs)}
</output>

Done. Output <end/> now."""
            current_response = await self.call_ollama(follow_up_prompt, SYSTEM)
        
        self.update_memory(user_input, response, tool_result)
        if tool_result:
            await self.extract_key_info(user_input, response)
        
        return response, tool_result


def main():
    agent = Agent0()
    os.makedirs(agent.workspace, exist_ok=True)
    
    print(f"Agent0 - {agent.model}")
    print(f"工作區：{agent.workspace}")
    print("指令：/quit、/memory\n")
    
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
            print(f"關鍵資訊：{agent.key_info}")
            continue
        
        response, tool_result = asyncio.run(agent.run(user_input))
        
        print(f"\n🤖 {response}\n")


if __name__ == "__main__":
    main()
