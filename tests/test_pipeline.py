"""Behavioural tests for the Baseerat pipeline.

These assert the paper's central prediction as a property of the code: under the
deceptive-injection condition the non-visual channel is fooled while the visual
channel is not, producing a positive oversight parity gap; under silent-failure
both channels catch it. The tests use the offline heuristic auditor so they run
deterministically with no API spend.
"""

from __future__ import annotations

import math
from pathlib import Path

from baseerat.auditor import HeuristicAuditor
from baseerat.environment import SimulatedEnvironment, channel_view
from baseerat.metrics import (
    detectability,
    oversight_parity_gap,
    self_report_fidelity,
)
from baseerat.schema import Channel, Condition, Verdict, load_tasks

SEED = Path(__file__).resolve().parent.parent / "tasks" / "seed.json"


def _run_all(tasks):
    env = SimulatedEnvironment()
    auditor = HeuristicAuditor()
    runs, results = [], []
    for task in tasks:
        for condition in Condition:
            r = env.run(task, condition)
            runs.append(r)
            for channel in Channel:
                view = channel_view(r, channel)
                results.append(auditor.audit(task, view, channel, condition))
    return runs, results


def test_seed_loads():
    tasks = load_tasks(SEED)
    assert len(tasks) >= 5
    assert all(t.fields for t in tasks)


def test_non_visual_never_sees_ground_truth():
    tasks = load_tasks(SEED)
    env = SimulatedEnvironment()
    r = env.run(tasks[0], Condition.DECEPTIVE_INJECTION)
    view = channel_view(r, Channel.NON_VISUAL)
    assert "world_state" not in view
    assert "world_state" in channel_view(r, Channel.VISUAL)


def test_clean_runs_pass_both_channels():
    tasks = load_tasks(SEED)
    _, results = _run_all(tasks)
    clean = [r for r in results if r.condition is Condition.CLEAN]
    assert clean and all(r.verdict is Verdict.CLEAN for r in clean)


def test_silent_failure_caught_by_both_channels():
    tasks = load_tasks(SEED)
    _, results = _run_all(tasks)
    sf = [r for r in results if r.condition is Condition.SILENT_FAILURE]
    # Honest tree contradicts the false claim, so every channel catches it.
    assert sf and all(r.verdict is Verdict.DIVERGED for r in sf)


def test_deceptive_injection_fools_only_non_visual():
    tasks = load_tasks(SEED)
    _, results = _run_all(tasks)
    di = [r for r in results if r.condition is Condition.DECEPTIVE_INJECTION]
    nv = [r for r in di if r.channel is Channel.NON_VISUAL]
    vis = [r for r in di if r.channel is Channel.VISUAL]
    # Non-visual is fooled by the poisoned tree; visual catches the hijack.
    assert all(r.verdict is Verdict.CLEAN for r in nv)
    assert all(r.verdict is Verdict.DIVERGED for r in vis)


def test_parity_gap_is_positive_and_concentrated_in_injection():
    tasks = load_tasks(SEED)
    _, results = _run_all(tasks)
    gap = oversight_parity_gap(results)
    assert gap.overall > 0
    # The gap comes entirely from deceptive injection, not silent failure.
    assert gap.per_condition[Condition.DECEPTIVE_INJECTION.value] > 0
    assert math.isclose(gap.per_condition[Condition.SILENT_FAILURE.value], 0.0,
                        abs_tol=1e-9)


def test_fidelity_clean_is_perfect_injection_is_degraded():
    tasks = load_tasks(SEED)
    task = tasks[0]
    env = SimulatedEnvironment()
    expected = {f.key: f.expected for f in task.fields}

    clean = env.run(task, Condition.CLEAN)
    assert self_report_fidelity(clean, expected) == 1.0

    inj = env.run(task, Condition.DECEPTIVE_INJECTION)
    # One of three fields is hijacked, so the agent misreports 1/3.
    assert self_report_fidelity(inj, expected) < 1.0


def test_detectability_report_shapes():
    tasks = load_tasks(SEED)
    _, results = _run_all(tasks)
    nv = detectability(results, Channel.NON_VISUAL)
    v = detectability(results, Channel.VISUAL)
    assert v.recall == 1.0                 # visual catches every divergence
    assert 0.0 <= nv.recall < 1.0          # non-visual misses the injections
    assert nv.false_alarm_rate == 0.0      # heuristic raises no false alarms
