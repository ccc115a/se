import socket

import pytest

import agent2context as A

WORKSPACE = "/tmp"
SYSTEM_MARKERS = ["Jarvis", "run_shell", "工具政策", "輸出規範", "當前環境"]


@pytest.fixture
def ctx():
    return A.ContextBuilder(A.MODEL, WORKSPACE)


def ssys(ctx):
    return ctx.build_system_prompt()


# ─── 語法／可匯入（import 成功即通過） ───


def test_module_importable():
    assert hasattr(A, "ContextBuilder")


# ─── 動態系統提示組裝 ───


def test_system_prompt_contains_all_sections(ctx):
    prompt = ssys(ctx)
    for marker in SYSTEM_MARKERS:
        assert marker in prompt, f"系統提示缺少 {marker}"


def test_system_prompt_has_runtime_facts(ctx):
    prompt = ssys(ctx)
    assert "目前時間" in prompt
    assert "Python" in prompt
    assert ctx.model in prompt


def test_system_prompt_is_dynamic(ctx):
    p1 = ssys(ctx)
    p2 = ssys(ctx)
    assert "目前時間" in p1 and "目前時間" in p2


# ─── 工具 schema ───


def test_tool_schemas_only_run_shell(ctx):
    tools = ctx.tool_schemas()
    assert len(tools) == 1
    assert tools[0]["function"]["name"] == "run_shell"


def test_tool_schema_command_required(ctx):
    tools = ctx.tool_schemas()
    params = tools[0]["function"]["parameters"]
    assert "command" in params["required"]


# ─── token 估算 ───


def test_estimate_tokens_nonzero(ctx):
    assert ctx.estimate_tokens("hello") >= 1
    assert ctx.estimate_tokens("") == 1


def test_estimate_tokens_longer_text_counts_more(ctx):
    assert ctx.estimate_tokens("x" * 100) > ctx.estimate_tokens("x" * 10)


# ─── 歷史管理：數量修剪 ───


def test_manage_history_keeps_system_first(ctx):
    hist = [{"role": "system", "content": ssys(ctx)}]
    for i in range(30):
        hist.append({"role": "user", "content": f"m{i:02d}"})
    managed = ctx.manage_history(hist)
    assert managed[0]["role"] == "system"
    assert len(managed) <= A.HISTORY_MESSAGES + 2


# ─── 歷史管理：token 預算觸發摘要 ───


def test_manage_history_summarizes_over_budget(ctx, monkeypatch):
    monkeypatch.setattr(A, "TOKEN_BUDGET", 800)
    hist = [{"role": "system", "content": ssys(ctx)}]
    for i in range(20):
        hist.append({"role": "user", "content": ("這是一段很長的內容" * 30) + f"#{i}"})
    managed = ctx.manage_history(hist)
    first = [m for m in managed if m.get("role") == "system"]
    assert any("摘要" in m.get("content", "") for m in first), "超預算時應產生摘要"
    assert managed[0]["role"] == "system"


def test_manage_history_prefix_not_part_of_original(ctx):
    hist = [{"role": "system", "content": ssys(ctx)}]
    for i in range(5):
        hist.append({"role": "user", "content": f"q{i}"})
    managed = ctx.manage_history(hist)
    assert len(managed) == 6, "未超預算時不應額外摘要"


# ─── /ctx 除錯輸出 ───


def test_debug_string_sections(ctx):
    hist = [{"role": "system", "content": ssys(ctx)},
            {"role": "user", "content": "你好"}]
    dbg = ctx.debug_string(hist)
    for section in ("工具 schema", "歷史訊息", "系統提示"):
        assert section in dbg


def test_debug_string_quotes_tool_schema(ctx):
    hist = [{"role": "system", "content": ssys(ctx)}]
    dbg = ctx.debug_string(hist)
    assert '"name": "run_shell"' in dbg


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
    ctx = A.ContextBuilder(A.MODEL, WORKSPACE)
    messages = [{"role": "system", "content": ctx.build_system_prompt()}]
    result = await A.call_ollama(messages, ctx.tool_schemas())
    assert isinstance(result, dict)
    assert "content" in result
    assert len(result["content"]) > 0