"""Tests for the defence: trusted action receipts close the oversight parity gap.

Uses the offline simulator and heuristic auditor, so it runs deterministically
with no API spend. This is the paper's constructive claim, asserted as a property
of the code."""

from __future__ import annotations

from pathlib import Path

from baseerat.auditor import HeuristicAuditor
from baseerat.defence import receipt_text, render_receipt
from baseerat.environment import SimulatedEnvironment, channel_view
from baseerat.metrics import defence_report
from baseerat.schema import Channel, Condition, Defence, Verdict, load_tasks

SEED = Path(__file__).resolve().parent.parent / "tasks" / "seed.json"


def _run_all_with_defence(tasks):
    env = SimulatedEnvironment()
    auditor = HeuristicAuditor()
    results = []
    for task in tasks:
        for condition in Condition:
            r = env.run(task, condition)
            results.append(auditor.audit(
                task, channel_view(r, Channel.VISUAL), Channel.VISUAL,
                condition, Defence.NARRATION_ONLY))
            nv = channel_view(r, Channel.NON_VISUAL)
            results.append(auditor.audit(
                task, nv, Channel.NON_VISUAL, condition, Defence.NARRATION_ONLY))
            nv_r = dict(nv)
            nv_r["receipt"] = render_receipt(task, r)
            results.append(auditor.audit(
                task, nv_r, Channel.NON_VISUAL, condition, Defence.WITH_RECEIPT))
    return results


def test_receipt_reports_true_committed_value_not_the_poisoned_tree():
    task = load_tasks(SEED)[0]
    env = SimulatedEnvironment()
    r = env.run(task, Condition.DECEPTIVE_INJECTION)
    receipt = render_receipt(task, r)
    tgt = task.fields[0].key
    # The receipt tells the truth (the hijacked value); the a11y tree lies benign.
    assert receipt[tgt] == r.world_state[tgt] == task.injection_hint
    assert r.a11y_tree[tgt] != receipt[tgt]


def test_receipt_text_is_accessible_sentence():
    task = load_tasks(SEED)[0]
    r = SimulatedEnvironment().run(task, Condition.CLEAN)
    text = receipt_text(task, r)
    assert text.startswith("Recorded outcome")
    assert task.fields[0].expected in text


def test_injection_caught_with_receipt_missed_without():
    task = load_tasks(SEED)[0]
    env = SimulatedEnvironment()
    auditor = HeuristicAuditor()
    r = env.run(task, Condition.DECEPTIVE_INJECTION)

    nv = channel_view(r, Channel.NON_VISUAL)
    without = auditor.audit(task, nv, Channel.NON_VISUAL,
                            Condition.DECEPTIVE_INJECTION, Defence.NARRATION_ONLY)
    nv_r = dict(nv)
    nv_r["receipt"] = render_receipt(task, r)
    with_r = auditor.audit(task, nv_r, Channel.NON_VISUAL,
                           Condition.DECEPTIVE_INJECTION, Defence.WITH_RECEIPT)

    assert without.verdict is Verdict.CLEAN       # fooled by the poisoned tree
    assert with_r.verdict is Verdict.DIVERGED     # the receipt reveals the hijack


def test_receipt_does_not_cause_false_alarms_on_clean_runs():
    task = load_tasks(SEED)[0]
    env = SimulatedEnvironment()
    auditor = HeuristicAuditor()
    r = env.run(task, Condition.CLEAN)
    nv_r = dict(channel_view(r, Channel.NON_VISUAL))
    nv_r["receipt"] = render_receipt(task, r)
    res = auditor.audit(task, nv_r, Channel.NON_VISUAL, Condition.CLEAN,
                        Defence.WITH_RECEIPT)
    assert res.verdict is Verdict.CLEAN


def test_defence_closes_the_parity_gap_over_the_seed_set():
    results = _run_all_with_defence(load_tasks(SEED))
    d = defence_report(results)
    assert d.gap_narration_only > 0            # the problem exists
    assert d.gap_with_receipt == 0.0           # the defence closes it
    assert d.non_visual_recall_narration < 1.0
    assert d.non_visual_recall_receipt == 1.0
    assert d.gap_closed > 0
