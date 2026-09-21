import socket

import pytest

import agent4loop as A

# ─── 測試用 fake：可控的 model 呼叫 ───


class FakeModel:
    """依預先排好的劇本回傳結果。

    script 元素可以是：
      - ("tool", "echo ok")                  單一工具呼叫
      - ("tools", ["echo ok", "exit 3"])     一次多個工具呼叫
      - ("content", "最終答案")               直接給最終答案
    依序消耗，最後呼叫多的回傳最終答案。
    """

    def __init__(self, script):
        self.script = list(script)

    def __call__(self, messages, tools):
        if self.script:
            kind, payload = self.script.pop(0)
        else:
            return {"content": "（劇本耗盡，直接給答案）", "tool_calls": None}

        if kind == "content":
            return {"content": payload, "tool_calls": None}
        if kind == "tools":
            calls = [{"function": {"name": "run_shell", "arguments": {"command": c}}}
                     for c in payload]
            return {"content": "", "tool_calls": calls}
        # kind == "tool"
        calls = [{"function": {"name": "run_shell", "arguments": {"command": payload}}}]
        return {"content": "", "tool_calls": calls}


def fake_run_shell(args):
    cmd = args.get("command", "")
    return A.run_shell(cmd)


@pytest.fixture
def loop():
    return A.SelfCorrectingLoop(max_tool_turns=5, max_replans=3)


def run_with(loop, script, user_input="測試任務"):
    fake = FakeModel(script)
    messages = [{"role": "system", "content": "system"}]
    answer = loop.run(messages, user_input,
                      tool_impls={"run_shell": fake_run_shell},
                      call_ollama_fn=fake)
    return answer, messages


# ─── ToolOutcome 結構化結果 ───


def test_run_shell_success_outcome():
    out = A.run_shell("echo hello")
    assert out.ok
    assert out.exit_code == 0
    assert "hello" in out.text


def test_run_shell_failure_outcome():
    out = A.run_shell("exit 3")
    assert not out.ok
    assert out.exit_code == 3


def test_run_shell_timeout_outcome():
    out = A.run_shell("sleep 60")
    assert not out.ok
    assert out.reason == "timeout"


# ─── 主迴圈：成功路徑（無失敗 → 反思） ───


def test_loop_success_no_reflection(loop):
    answer, messages = run_with(loop, [
        ("tool", "echo hello"),
        ("content", "完成！"),
    ])
    assert answer == "完成！"
    assert loop.replans == 0
    assert loop.tool_rounds == 1
    reflects = [r for r in loop.records if r.kind == "reflect"]
    assert reflects == []


def test_loop_appends_final_assistant(loop):
    _, messages = run_with(loop, [("content", "答案")])
    assert messages[-1] == {"role": "assistant", "content": "答案"}


# ─── 主迴圈：失敗 → 反思 → 修正重試 ───


def test_loop_reflects_on_failure_then_retries(loop):
    answer, messages = run_with(loop, [
        ("tool", "exit 1"),          # 失敗
        ("tools", ["echo fixed"]),   # 反思後，模型用修正指令重試
        ("content", "修好了！"),
    ])
    assert answer == "修好了！"
    assert loop.replans == 1
    assert loop.tool_rounds == 2
    reflects = [r for r in loop.records if r.kind == "reflect"]
    assert len(reflects) == 1
    # 反思提示有被加入 messages（user role）
    reflect_msgs = [m for m in messages
                    if m.get("role") == "user" and "反思" in m.get("content", "")]
    assert len(reflect_msgs) == 1
    # 逐字稿記錄：兩次工具都記下，第一次失敗標 ✗
    tool_records = [r for r in loop.records if r.kind == "tool"]
    assert [r.ok for r in tool_records] == [False, True]


def test_reflection_prompt_contains_failure_detail(loop):
    failures = [A.ToolOutcome(text="command not found", ok=False,
                              exit_code=127, command="nosuchcmd")]
    prompt = loop.reflection_prompt(failures, replan_used=1)
    assert "反思" in prompt
    assert "nosuchcmd" in prompt
    assert "command not found" in prompt
    assert "1 次重試" in prompt and "3 次" in prompt


# ─── 主迴圈：重試預算 MAX_REPLANS 上限 ───


def test_loop_respects_replan_budget(loop):
    # 每次都失敗：replans 不超過 max_replans（3）
    script = [("tool", "exit 1")] * 20
    answer, _ = run_with(loop, script)
    assert loop.replans == loop.max_replans
    reflects = [r for r in loop.records if r.kind == "reflect"]
    assert len(reflects) == loop.max_replans


def test_loop_stops_at_tool_turn_budget():
    # 全部成功的工具呼叫會一直消耗 tool_rounds；MAX_TOOL_TURNS 生效
    loop = A.SelfCorrectingLoop(max_tool_turns=3, max_replans=1)
    script = [("tool", "echo ok")] * 10
    answer, _ = run_with(loop, script)
    assert "已達最多 3 輪" in answer
    assert loop.tool_rounds == 3
    # 成功路徑不觸發反思
    assert loop.replans == 0


# ─── 多個 tool_calls 一次回合 ───


def test_loop_handles_parallel_tool_calls(loop):
    answer, messages = run_with(loop, [
        ("tools", ["echo A", "exit 2"]),   # 一成功一失敗
        ("content", "其中一個失敗了"),
    ])
    assert answer == "其中一個失敗了"
    assert loop.replans == 1
    tool_records = [r for r in loop.records if r.kind == "tool"]
    assert [r.ok for r in tool_records] == [True, False]


# ─── 逐字稿與 /loop describe ───


def test_loop_describe_shows_state(loop):
    run_with(loop, [("tool", "exit 1"), ("tools", ["echo ok"]), ("content", "done")])
    d = loop.describe()
    assert "Self-Correcting Loop 狀態" in d
    assert "工具回合: 2/5" in d
    assert "反思重試: 1/3" in d
    assert "逐字稿" in d
    assert "✗" in d and "✓" in d


def test_loop_record_has_incrementing_index(loop):
    run_with(loop, [("tool", "echo a"), ("content", "done")])
    indexes = [r.index for r in loop.records]
    assert indexes == list(range(1, len(indexes) + 1))


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
    result = await A.call_ollama(messages, A.TOOLS)
    assert isinstance(result, dict)
    assert "content" in result
    assert len(result["content"]) > 0