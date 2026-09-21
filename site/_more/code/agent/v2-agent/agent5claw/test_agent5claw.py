import socket

import pytest

import agent5claw as A


# ─── ClawMemory：持久化 Markdown 記憶 ───


def test_memory_starts_empty(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    assert all(v == [] for v in mem.data.values())
    assert mem.render() == ""


def test_memory_add_and_render(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    assert mem.add("事實", "使用者叫小明")
    assert mem.data["事實"] == ["使用者叫小明"]
    rendered = mem.render()
    assert "你記得的內容" in rendered
    assert "使用者叫小明" in rendered


def test_memory_save_load_roundtrip(tmp_path):
    path = str(tmp_path / "mem.md")
    mem = A.ClawMemory(path)
    mem.load()
    mem.add("偏好", "喜歡喝咖啡")
    mem.add("專案", "agent5claw 進行中")
    mem2 = A.ClawMemory(path)
    mem2.load()
    assert mem2.data["偏好"] == ["喜歡喝咖啡"]
    assert mem2.data["專案"] == ["agent5claw 進行中"]


def test_memory_dedup(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    assert mem.add("事實", "同一件事")
    assert not mem.add("事實", "同一件事")
    assert mem.add("事實", "另一件事")
    assert len(mem.data["事實"]) == 2


def test_memory_unknown_section_falls_back_facts(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    assert mem.add("不存在", "還是會被放入事實")
    assert "還是會被放入事實" in mem.data["事實"]


def test_memory_save_creates_parent_dir(tmp_path):
    path = str(tmp_path / "a" / "b" / "mem.md")
    mem = A.ClawMemory(path)
    mem.load()
    mem.add("事實", "x")
    assert mem.path.endswith("mem.md")


def test_memory_load_missing_file_is_ok(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "does_not_exist.md"))
    mem.load()  # 不該拋例外


# ─── SecurityPolicy：授權策略（auto / ask / deny） ───


def test_policy_auto_allows_normal_command():
    policy = A.SecurityPolicy(mode="auto")
    allowed, _ = policy.check("echo hello")
    assert allowed


def test_policy_deny_blocks_everything():
    policy = A.SecurityPolicy(mode="deny")
    allowed, reason = policy.check("echo hello")
    assert not allowed
    assert "deny" in reason


def test_policy_ask_yes_allows():
    policy = A.SecurityPolicy(mode="ask")
    allowed, _ = policy.check("echo hello", prompt_fn=lambda p: "y")
    assert allowed


def test_policy_ask_no_blocks():
    policy = A.SecurityPolicy(mode="ask")
    allowed, reason = policy.check("echo hello", prompt_fn=lambda p: "n")
    assert not allowed
    assert "拒絕" in reason


@pytest.mark.parametrize("danger", [
    "rm -rf /",
    "mkfs.ext4 /dev/sda1",
    "tail -f /var/log/syslog",
    "watch ls",
    "python3 -m http.server 8000",
])
def test_policy_deny_patterns_block_never_allowed(danger):
    # 即使 auto 模式，命中禁止模式也封鎖
    policy = A.SecurityPolicy(mode="auto")
    allowed, reason = policy.check(danger)
    assert not allowed
    assert "禁止模式" in reason


# ─── run_shell（受政策管制） ───


def test_run_shell_echo():
    out = A.run_shell("echo CLAWPROBE_1")
    assert "CLAWPROBE_1" in out


def test_run_shell_no_output_fallback():
    out = A.run_shell("true")
    assert "（無輸出）" in out


def test_run_shell_timeout(monkeypatch):
    monkeypatch.setattr(A, "SHELL_TIMEOUT", 1)
    out = A.run_shell("sleep 5")
    assert "逾時" in out


def test_run_shell_blocked_by_deny_pattern():
    out = A.run_shell("rm -rf /")
    assert "封鎖" in out
    assert "禁止模式" in out


def test_run_shell_ask_refused(monkeypatch):
    policy = A.SecurityPolicy(mode="ask")
    out = A.run_shell("echo SHOULD_NOT_RUN", policy=policy, prompt_fn=lambda p: "n")
    assert "拒絕" in out
    assert "SHOULD_NOT_RUN" not in out


# ─── Skills 技能表 ───


def test_skill_sysinfo():
    out = A.run_skill("sysinfo")
    assert "OS" in out
    assert "Python" in out


def test_skill_read_file():
    # 讀取 agent5claw.py 本身
    out = A.run_skill("read_file", {"path": "agent5claw.py"})
    assert "agent5claw" in out


def test_skill_read_file_outside_workspace_denied():
    out = A.run_skill("read_file", {"path": "/etc/hosts"})
    assert "超出 WORKSPACE" in out


def test_skill_search_finds_its_own_source():
    out = A.run_skill("search", {"pattern": "ClawMemory"})
    assert "agent5claw.py" in out
    assert "找到" in out


def test_skill_search_no_hit():
    # 用拼接避免 token 出現在本檔原始碼裡（否則會被 search 掃到）
    token = "zzz_no_such_" + "token_9988_absent"
    out = A.run_skill("search", {"pattern": token})
    assert "找不到" in out


def test_skill_list_files():
    out = A.run_skill("list_files")
    assert "agent5claw.py" in out


def test_skill_unknown():
    out = A.run_skill("no_such_skill")
    assert "未知技能" in out


# ─── TOOLS schema & 註冊 ───


def test_tools_include_core_three():
    names = [t["function"]["name"] for t in A.TOOLS]
    assert "run_shell" in names
    assert "remember" in names
    assert "run_skill" in names


def test_remember_tool_schema_has_sections():
    for t in A.TOOLS:
        if t["function"]["name"] == "remember":
            enum = t["function"]["parameters"]["properties"]["section"]["enum"]
            assert enum == ["事實", "偏好", "專案"]


# ─── trim_history（沿用 v1） ───


def test_trim_history_keeps_system_first():
    msgs = [{"role": "system", "content": "sys"}]
    for i in range(30):
        msgs.append({"role": "user", "content": f"m{i}"})
    trimmed = A.trim_history(msgs)
    assert trimmed[0]["role"] == "system"
    assert len(trimmed) == 1 + A.HISTORY_MESSAGES
    assert trimmed[-1]["content"] == "m29"


# ─── build_system_prompt：記憶灌入 prompt ───


def test_build_system_prompt_includes_memory(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    mem.add("事實", "使用者叫小美")
    prompt = A.build_system_prompt(mem)
    assert "使用者叫小美" in prompt
    assert "Claw" in prompt


def test_build_system_prompt_empty_memory(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    assert A.build_system_prompt(mem) == A.SYSTEM_PROMPT


# ─── handle_turn：注入 fake model 的決定性測試 ───


class FakeModel:
    """依序回傳 script 的 fake model；元素是 {"content":..., "tool_calls":[...]|None}。"""

    def __init__(self, script):
        self.script = list(script)

    def __call__(self, messages):
        return self.script.pop(0)


def make_tool_call(name, args):
    return {"function": {"name": name, "arguments": args}}


def test_handle_turn_direct_answer(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    messages = [{"role": "system", "content": "sys"}]
    fake = FakeModel([{"content": "你好，我是 Claw", "tool_calls": None}])
    answer = A.handle_turn(messages, "嗨", mem, call_ollama_fn=fake)
    assert answer == "你好，我是 Claw"
    assert messages[0]["content"] == A.build_system_prompt(mem)
    assert messages[-1]["role"] == "assistant"


def test_handle_turn_remember_tool_updates_memory(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    messages = [{"role": "system", "content": "sys"}]
    fake = FakeModel([
        {"content": "", "tool_calls": [make_tool_call("remember",
                                                      {"section": "事實", "text": "我很喜歡 coding"})]},
        {"content": "已記住！", "tool_calls": None},
    ])
    answer = A.handle_turn(messages, "記住這件事", mem, call_ollama_fn=fake)
    assert answer == "已記住！"
    assert "我很喜歡 coding" in mem.data["事實"]
    # tool 結果也被加回對話歷史
    assert messages[-1]["role"] == "assistant"  # 最終回覆
    assert any(m.get("name") == "remember" for m in messages)  # tool 訊息


def test_handle_turn_run_skill_tool(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    messages = [{"role": "system", "content": "sys"}]
    fake = FakeModel([
        {"content": "", "tool_calls": [make_tool_call("run_skill",
                                                      {"name": "sysinfo", "arguments": {}})]},
        {"content": "系統資訊如上", "tool_calls": None},
    ])
    answer = A.handle_turn(messages, "查一下系統", mem, call_ollama_fn=fake)
    assert answer == "系統資訊如上"
    tool_msgs = [m for m in messages if m.get("role") == "tool"]
    assert "OS" in tool_msgs[0]["content"]


def test_handle_turn_unknown_tool_reports(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    messages = [{"role": "system", "content": "sys"}]
    fake = FakeModel([
        {"content": "", "tool_calls": [make_tool_call("noop", {})]},
        {"content": "喔", "tool_calls": None},
    ])
    A.handle_turn(messages, "x", mem, call_ollama_fn=fake)
    tool_msgs = [m for m in messages if m.get("role") == "tool"]
    assert "未知工具" in tool_msgs[0]["content"]


def test_handle_turn_max_tool_turns(tmp_path):
    mem = A.ClawMemory(str(tmp_path / "mem.md"))
    mem.load()
    messages = [{"role": "system", "content": "sys"}]
    # 一直要求跑工具，永遠不給最終答案
    fake = FakeModel([
        {"content": "", "tool_calls": [make_tool_call("run_skill", {"name": "sysinfo"})]}
        for _ in range(A.MAX_TOOL_TURNS + 2)
    ])
    answer = A.handle_turn(messages, "x", mem, call_ollama_fn=fake)
    assert "最多" in answer and "工具呼叫" in answer


# ─── live 冒煙測試（需要 Ollama，否則自動略過） ───


def ollama_up(host="localhost", port=11434, timeout=1):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not ollama_up(), reason="Ollama 未在 localhost:11434 執行")
@pytest.mark.asyncio
async def test_live_streaming_smoke():
    messages = [
        {"role": "system", "content": A.SYSTEM_PROMPT},
        {"role": "user", "content": "請用一句話自我介紹。"},
    ]
    result = await A.call_ollama(messages)
    assert isinstance(result, dict)
    assert "content" in result
    assert len(result["content"]) > 0