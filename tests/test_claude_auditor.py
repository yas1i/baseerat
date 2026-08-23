"""Verify the Claude auditor's request shape and response parsing with a mock
client, so the LLM arm is covered without credentials or API spend."""

from __future__ import annotations

import json
from pathlib import Path

from baseerat.auditor.claude import ClaudeAuditor
from baseerat.environment import SimulatedEnvironment, channel_view
from baseerat.schema import Channel, Condition, Verdict, load_tasks

SEED = Path(__file__).resolve().parent.parent / "tasks" / "seed.json"


class _Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Resp:
    def __init__(self, text):
        self.content = [_Block(text)]


class _FakeMessages:
    def __init__(self, verdict):
        self._verdict = verdict
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _Resp(json.dumps({"verdict": self._verdict, "rationale": "mock"}))


class _FakeClient:
    def __init__(self, verdict):
        self.messages = _FakeMessages(verdict)
        self.api_key = "fake"


def test_claude_auditor_parses_verdict_and_uses_structured_output():
    task = load_tasks(SEED)[0]
    run = SimulatedEnvironment().run(task, Condition.DECEPTIVE_INJECTION)
    view = channel_view(run, Channel.NON_VISUAL)

    client = _FakeClient("diverged")
    auditor = ClaudeAuditor(client=client)
    res = auditor.audit(task, view, Channel.NON_VISUAL, Condition.DECEPTIVE_INJECTION)

    assert res.verdict is Verdict.DIVERGED
    kwargs = client.messages.last_kwargs
    assert kwargs["model"] == "claude-opus-5"
    assert kwargs["output_config"]["format"]["type"] == "json_schema"
    # The non-visual prompt must never contain ground truth.
    assert "GROUND-TRUTH" not in kwargs["messages"][0]["content"]


def test_claude_auditor_visual_prompt_includes_ground_truth():
    task = load_tasks(SEED)[0]
    run = SimulatedEnvironment().run(task, Condition.DECEPTIVE_INJECTION)
    view = channel_view(run, Channel.VISUAL)

    client = _FakeClient("diverged")
    auditor = ClaudeAuditor(client=client)
    auditor.audit(task, view, Channel.VISUAL, Condition.DECEPTIVE_INJECTION)
    assert "GROUND-TRUTH" in client.messages.last_kwargs["messages"][0]["content"]


def test_claude_auditor_survives_unparseable_response():
    task = load_tasks(SEED)[0]
    run = SimulatedEnvironment().run(task, Condition.CLEAN)
    view = channel_view(run, Channel.NON_VISUAL)

    client = _FakeClient("diverged")
    client.messages = type(client.messages)("diverged")
    client.messages.create = lambda **k: _Resp("not json at all")
    auditor = ClaudeAuditor(client=client)
    res = auditor.audit(task, view, Channel.NON_VISUAL, Condition.CLEAN)
    assert res.rationale.startswith("UNPARSEABLE")
