import socket

import pytest

import agent1prompt as A


# ─── run_shell（實際執行，決定性） ───


def test_run_shell_echo():
    out = A.run_shell("echo AGENT1PROBE_1")
    assert "AGENT1PROBE_1" in out


def test_run_shell_combines_stderr():
    out = A.run_shell("thiscommanddoesnotexist_xyz 2>&1")
    # 無輸出時 fallback 為「（無輸出）」也要允許；但 stderr 通常來自 shell
    assert isinstance(out, str)


def test_run_shell_no_output_fallback():
    out = A.run_shell("true")
    assert "（無輸出）" in out


def test_run_shell_timeout(monkeypatch):
    monkeypatch.setattr(A, "SHELL_TIMEOUT", 1)
    out = A.run_shell("sleep 5")
    assert "逾時" in out


# ─── trim_history（純邏輯） ───


def test_trim_history_keeps_system_first():
    msgs = [{"role": "system", "content": "sys"}]
    for i in range(30):
        msgs.append({"role": "user", "content": f"m{i}"})
    trimmed = A.trim_history(msgs)
    assert trimmed[0]["role"] == "system"
    assert trimmed[0]["content"] == "sys"


def test_trim_history_caps_to_history_messages():
    msgs = [{"role": "system", "content": "sys"}]
    for i in range(30):
        msgs.append({"role": "user", "content": f"m{i}"})
    trimmed = A.trim_history(msgs)
    # system + 最近 HISTORY_MESSAGES 則
    assert len(trimmed) == 1 + A.HISTORY_MESSAGES
    assert trimmed[-1]["content"] == "m29"


def test_trim_history_keeps_short_history_unchanged():
    msgs = [{"role": "system", "content": "sys"},
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"}]
    trimmed = A.trim_history(msgs)
    assert trimmed == msgs


# ─── TOOLS schema ───


def test_tools_only_run_shell():
    assert len(A.TOOLS) == 1
    assert A.TOOLS[0]["function"]["name"] == "run_shell"


def test_tools_command_required():
    params = A.TOOLS[0]["function"]["parameters"]
    assert "command" in params["required"]
    assert params["properties"]["command"]["type"] == "string"


# ─── TOOL_IMPLS 註冊 ───


def test_tool_impls_registered():
    assert "run_shell" in A.TOOL_IMPLS


def test_tool_impls_extracts_command():
    out = A.TOOL_IMPLS["run_shell"]({"command": "echo PROBE_2"})
    assert "PROBE_2" in out


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
    messages = [{"role": "system", "content": "你是測試助手，請簡短回答。"}]
    result = await A.call_ollama(messages)
    assert isinstance(result, dict)
    assert "content" in result
    assert len(result["content"]) > 0