"""Tests for the agent seam: the scripted baseline and the Claude agent's
request shape and parsing (via a mock client, no credentials needed)."""

from __future__ import annotations

import json
from pathlib import Path

from baseerat.agent import (
    AgentResult,
    ClaudeComputerAgent,
    FieldView,
    Observation,
    ScriptedAgent,
)
from baseerat.schema import load_tasks

SEED = Path(__file__).resolve().parent.parent / "tasks" / "seed.json"


def _obs(task):
    return Observation(
        task_instruction=task.instruction,
        fields=[
            FieldView(input_id=f"in-{i}", key=f.key, label=f.label or f.key)
            for i, f in enumerate(task.fields)
        ],
        page_text="Please complete the form.",
        aria="- form",
    )


def test_scripted_agent_fills_expected_values():
    task = load_tasks(SEED)[0]
    res = ScriptedAgent().act(task, _obs(task))
    assert isinstance(res, AgentResult)
    assert res.claimed_success
    # One action per field, each targeting the right input id with the expected value.
    got = {a["id"]: a["value"] for a in res.actions}
    assert got["in-0"] == task.fields[0].expected
    assert len(res.actions) == len(task.fields)


class _Block:
    type = "text"

    def __init__(self, text):
        self.text = text


class _Resp:
    def __init__(self, text):
        self.content = [_Block(text)]


class _FakeMessages:
    def __init__(self, payload):
        self._payload = payload
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _Resp(json.dumps(self._payload))


class _FakeClient:
    def __init__(self, payload):
        self.messages = _FakeMessages(payload)
        self.api_key = "fake"


def test_claude_agent_parses_actions_and_narration():
    task = load_tasks(SEED)[0]
    payload = {
        "actions": [{"id": "in-0", "value": "accounts@northgate-legal.co.uk"}],
        "narration": "I sent the invoice email to accounts.",
        "claimed_success": True,
    }
    client = _FakeClient(payload)
    agent = ClaudeComputerAgent(client=client)
    res = agent.act(task, _obs(task))

    assert res.actions == payload["actions"]
    assert res.narration == payload["narration"]
    assert res.claimed_success is True

    kwargs = client.messages.last_kwargs
    assert kwargs["model"] == "claude-opus-5"
    assert kwargs["output_config"]["format"]["type"] == "json_schema"
    # The instruction is the authority; page content is labelled untrusted.
    assert "untrusted" in kwargs["messages"][0]["content"].lower()


def test_claude_agent_degrades_on_unparseable_response():
    task = load_tasks(SEED)[0]
    client = _FakeClient({})
    client.messages.create = lambda **k: _Resp("not json")
    agent = ClaudeComputerAgent(client=client)
    res = agent.act(task, _obs(task))
    assert res.actions == []
    assert res.claimed_success is False       # never hand the auditor a false success
    assert res.narration.startswith("UNPARSEABLE")
