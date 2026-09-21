import socket

import pytest

import agent4loop2 as A


class FakeRoles:
    """依角色分派回傳結果的 fake model。

    by_role 的 key 是角色名（"planner"/"executor"/"evaluator"），
    各自對應一組劇本 (list)。元素：
      - ("content", "文字")
      - ("tools", [(name, args), ...])
    依序消耗；劇本耗盡後回傳該角色的預設收尾（content）。
    """

    DEFAULT = {
        "planner": ("content", "計畫：已完成規劃"),
        "executor": ("content", "執行完畢"),
        "evaluator": ("content", "已評估"),
    }

    def __init__(self, by_role):
        self.by_role = {k: list(v) for k, v in by_role.items()}

    def _role_of(self, tools):
        if tools is None:
            return "planner"
        if tools is A.EXEC_TOOLS:
            return "executor"
        if tools is A.EVAL_TOOLS:
            return "evaluator"
        return "unknown"

    def __call__(self, messages, tools, think=True):
        role = self._role_of(tools)
        seq = self.by_role.get(role, [])
        kind, payload = seq.pop(0) if seq else self.DEFAULT[role]
        if kind == "content":
            return {"content": payload, "tool_calls": None}
        calls = [{"function": {"name": n, "arguments": a}} for n, a in payload]
        return {"content": "", "tool_calls": calls}


@pytest.fixture
def loop():
    return A.RoleLoop(max_plan_cycles=4, max_tool_turns=6)


def fake_run_shell(args):
    return A.run_shell(args.get("command", ""))


def run_with(loop, by_role, user_input="任務：建立 hello.txt"):
    fake = FakeRoles(by_role)
    messages = [{"role": "system", "content": "system"}]
    answer = loop.run(messages, user_input,
                      tool_impls={"run_shell": fake_run_shell},
                      call_ollama_fn=fake)
    return answer, messages


# ─── run_shell 基本 ───


def test_run_shell_success():
    out = A.run_shell("echo rolesprobe")
    assert out.ok
    assert "rolesprobe" in out.text


def test_run_shell_failure():
    out = A.run_shell("exit 3")
    assert not out.ok
    assert out.exit_code == 3


# ─── 一輪成功：planner → executor → evaluator(task_done) ───


def test_loop_single_cycle_done(loop):
    answer, messages = run_with(loop, {
        "planner": [("content", "計畫：建立 hello.txt\n步驟：\n 1. echo hi > hello.txt")],
        # executor：一次工具呼叫後接總結（結束執行階段）
        "executor": [
            ("tools", [("run_shell", {"command": "echo hi > /tmp/roles_hello.txt"})]),
            ("content", "已完成：建立 hello.txt"),
        ],
        "evaluator": [("tools", [("task_done", {"final_answer": "完成，已建立 hello.txt"})])],
    })
    assert answer == "完成，已建立 hello.txt"
    assert loop.plan_cycles == 1
    assert loop.tool_rounds == 1
    # 三位角色都各自出場
    roles = {r.role for r in loop.records}
    assert roles == {"planner", "executor", "evaluator"}
    # executor 的工具呼叫成功
    tool_recs = [r for r in loop.records if r.role == "executor" and r.ok is not None]
    assert [r.ok for r in tool_recs] == [True]
    # 最終 assistant 有答案
    assert messages[-1]["role"] == "assistant"


# ─── 評估未完成 → 回饋 → Planner 修正 → 再執行 → done ───


def test_loop_feedback_then_revision(loop):
    answer, _ = run_with(loop, {
        "planner": [
            ("content", "計畫 v1：建立 hello.txt"),
            ("content", "計畫 v2：修正後建立 hello.txt"),
        ],
        "executor": [
            ("tools", [("run_shell", {"command": "exit 1"})]),   # 第一輪失敗
            ("content", "失敗"),
            ("tools", [("run_shell", {"command": "echo ok > /tmp/roles_ok.txt"})]),  # 修正後成功
            ("content", "成功"),
        ],
        "evaluator": [
            ("content", "尚未完成：建立 hello.txt 失敗"),        # 給回饋
            ("tools", [("task_done", {"final_answer": "完成（經修正）"})]),
        ],
    })
    assert answer == "完成（經修正）"
    assert loop.plan_cycles == 2
    planner_records = [r for r in loop.records if r.role == "planner"]
    assert len(planner_records) == 2
    tool_recs = [r for r in loop.records if r.role == "executor" and r.ok is not None]
    assert [r.ok for r in tool_recs] == [False, True]


# ─── MAX_PLAN_CYCLES 上限：Evaluator 一直不 task_done ───


def test_loop_max_plan_cycles(loop):
    loop = A.RoleLoop(max_plan_cycles=2, max_tool_turns=6)
    answer, _ = run_with(loop, {
        "planner": [("content", f"計畫 v{i}") for i in range(5)],
        "executor": [("content", "執行中") for _ in range(5)],
        "evaluator": [("content", "還沒完成") for _ in range(5)],
    })
    assert loop.plan_cycles == 2
    assert "未得到最終答案" in answer


# ─── MAX_TOOL_TURNS 上限：Executor 一直發工具呼叫 ───


def test_loop_max_tool_turns(loop):
    loop = A.RoleLoop(max_plan_cycles=2, max_tool_turns=2)
    answer, _ = run_with(loop, {
        "planner": [("content", "計畫：跑多個指令")],
        "executor": [("tools", [("run_shell", {"command": "echo a"}),
                                ("run_shell", {"command": "echo b"}),
                                ("run_shell", {"command": "echo c"})])],
        "evaluator": [("tools", [("task_done", {"final_answer": "done"})])],
    })
    assert loop.tool_rounds == 2  # 只允許兩輪工具，第三個不該執行


# ─── 一次回合內多個平行工具呼叫 ───


def test_loop_parallel_tool_calls(loop):
    answer, _ = run_with(loop, {
        "planner": [("content", "計畫：並行執行")],
        "executor": [("tools", [("run_shell", {"command": "echo A"}),
                                ("run_shell", {"command": "echo B"})])],
        "evaluator": [("tools", [("task_done", {"final_answer": "並行完成"})])],
    })
    assert answer == "並行完成"
    tool_recs = [r for r in loop.records if r.role == "executor" and r.ok is not None]
    assert len(tool_recs) == 2


# ─── /roles describe ───


def test_describe_contains_role_frames(loop):
    run_with(loop, {
        "planner": [("content", "計畫 X")],
        "executor": [("tools", [("run_shell", {"command": "echo hi"})])],
        "evaluator": [("tools", [("task_done", {"final_answer": "OK"})])],
    })
    d = loop.describe()
    for token in ("分工迴圈", "Planner", "Executor", "Evaluator",
                  "計畫週期: 1/4", "工具回合: 1/6", "調度記錄"):
        assert token in d, f"describe 缺少 {token}"


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
    result = await A.call_ollama(messages, tools=A.EXEC_TOOLS)
    assert isinstance(result, dict)
    assert "content" in result