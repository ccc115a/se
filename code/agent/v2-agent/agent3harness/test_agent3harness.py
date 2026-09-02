import os
import subprocess

import pytest

import agent3harness as A

# ─── ExecResult.to_text 格式化 ───


def test_exec_result_ok_text():
    r = A.ExecResult(command="echo hi", stdout="hi\n", exit_code=0)
    text = r.to_text()
    assert "[stdout]" in text and "hi" in text
    assert r.ok


def test_exec_result_no_output():
    r = A.ExecResult(command="true", stdout="", stderr="", exit_code=0)
    assert "（無輸出）" in r.to_text()


def test_exec_result_nonzero_exit_reported():
    r = A.ExecResult(command="false", stdout="", stderr="boom", exit_code=2)
    text = r.to_text()
    assert "exit code: 2" in text
    assert "boom" in text
    assert not r.ok


def test_exec_result_denied_text():
    r = A.ExecResult(command="tail -f /dev/null", denied=True, error="禁止非自動結束指令")
    text = r.to_text()
    assert "安全規則拒絕" in text
    assert "禁止非自動結束指令" in text
    assert not r.ok


def test_exec_result_timed_out_text():
    r = A.ExecResult(command="sleep 60", timed_out=True)
    text = r.to_text()
    assert "逾時" in text
    assert not r.ok


def test_exec_result_truncated_marker():
    r = A.ExecResult(command="x", stderr="", truncated=True)
    assert "已截斷" in r.to_text()


# ─── ExecutionHarness.check_safe（純邏輯，不需執行） ───


@pytest.fixture
def harness():
    return A.ExecutionHarness(workspace="/tmp", timeout=5, max_output_chars=100)


def test_check_safe_accepts_normal_command(harness):
    ok, reason = harness.check_safe("echo hello")
    assert ok and reason == ""


def test_check_safe_rejects_empty(harness):
    ok, _ = harness.check_safe("   ")
    assert not ok


def test_check_safe_rejects_tail_follow(harness):
    for cmd in ("tail -f /var/log/a.log", "tail -F file", "tail --follow file"):
        ok, _ = harness.check_safe(cmd)
        assert not ok, f"應拒絕 {cmd}"


def test_check_safe_rejects_servers(harness):
    for cmd in ("uvicorn app:app", "python -m http.server 8000", "flask run", "npm start"):
        ok, _ = harness.check_safe(cmd)
        assert not ok, f"應拒絕 {cmd}"


def test_check_safe_rejects_watch(harness):
    ok, _ = harness.check_safe("watch -n 1 ls")
    assert not ok


def test_check_safe_case_insensitive(harness):
    ok, _ = harness.check_safe("TAIL -F log")
    assert not ok


# ─── ExecutionHarness.execute（實際執行） ───


def test_execute_echo(harness):
    r = harness.execute("echo HARNESSPROBE")
    assert r.ok
    assert "HARNESSPROBE" in r.stdout
    assert r.exit_code == 0


def test_execute_runs_in_workspace(tmp_path, here=os.getcwd()):
    h = A.ExecutionHarness(workspace=str(tmp_path), timeout=5, max_output_chars=1000)
    r = h.execute("pwd")
    assert r.ok
    assert r.stdout.strip() == str(tmp_path)


def test_execute_denied_never_runs(harness):
    r = harness.execute("tail -f /dev/null")
    assert r.denied
    assert "安全規則拒絕" in r.to_text()


def test_execute_reports_real_exit_code(harness):
    r = harness.execute("exit 3")
    assert not r.ok
    assert r.exit_code == 3


def test_execute_timeout(tmp_path):
    h = A.ExecutionHarness(workspace=str(tmp_path), timeout=1, max_output_chars=1000)
    import time
    start = time.monotonic()
    r = h.execute("sleep 10")
    assert r.timed_out
    assert time.monotonic() - start < 5
    assert "逾時" in r.to_text()


def test_execute_truncates_long_output(tmp_path):
    h = A.ExecutionHarness(workspace=str(tmp_path), timeout=5, max_output_chars=50)
    r = h.execute("python3 -c 'print(\"x\" * 500)'")
    assert r.truncated
    assert len(r.stdout) <= 60
    assert "已截斷" in r.to_text()


# ─── 環境隔離 ───


def test_execute_env_is_allowlisted(monkeypatch, tmp_path):
    monkeypatch.setenv("HARNESS_SECRET_SENTINEL", "should-not-leak")
    h = A.ExecutionHarness(workspace=str(tmp_path), timeout=5, max_output_chars=1000)
    env = h.env()
    assert "HARNESS_SECRET_SENTINEL" not in env
    assert "PATH" in env
    r = h.execute("python3 -c 'import os; print(os.environ.get(\"HARNESS_SECRET_SENTINEL\", \"none\"))'")
    assert r.ok
    assert "none" in r.stdout.strip()


def test_env_allowlist_override(tmp_path):
    h = A.ExecutionHarness(workspace=str(tmp_path), timeout=5,
                           max_output_chars=1000, env_allowlist=("PATH",))
    assert set(h.env().keys()) == {"PATH"}


# ─── describe（/harness 用） ───


def test_describe_contains_config(harness):
    d = harness.describe()
    for token in ("工作區", "逾時", "allowlist", "禁止的指令樣式"):
        assert token in d


# ─── live 冒煙測試（需要 Ollama，否則自動略過） ───


def ollama_up(host="localhost", port=11434, timeout=1):
    import socket
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