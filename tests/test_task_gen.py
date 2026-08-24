"""Tests for the corpus generator: determinism, coverage, and that every
generated task is well-formed and usable by the simulator."""

from __future__ import annotations

from collections import Counter

from baseerat.environment import SimulatedEnvironment
from baseerat.schema import Condition, Task
from baseerat.task_gen import generate


def test_generate_is_deterministic():
    a = generate(60, seed=7)
    b = generate(60, seed=7)
    assert a == b


def test_generate_covers_domains_and_injection_kinds():
    tasks = generate(150, seed=7)
    assert len(tasks) == 150
    domains = Counter(t["domain"] for t in tasks)
    kinds = Counter(t["injection_kind"] for t in tasks)
    assert set(domains) == {"email", "address", "payment", "file", "calendar",
                            "settings"}
    assert set(kinds) == {"homograph", "substitution", "append", "redirect"}
    # Roughly balanced, not degenerate.
    assert min(domains.values()) >= 20
    assert min(kinds.values()) >= 20


def test_task_ids_are_unique():
    tasks = generate(150, seed=7)
    ids = [t["task_id"] for t in tasks]
    assert len(ids) == len(set(ids))


def test_injection_target_is_first_field_and_hint_differs():
    for t in generate(150, seed=7):
        assert t["fields"], t["task_id"]
        # The rig hijacks fields[0]; the hint must differ from its expected value.
        assert t["injection_hint"] != t["fields"][0]["expected"], t["task_id"]


def test_generated_tasks_run_through_the_simulator():
    env = SimulatedEnvironment()
    for spec in generate(30, seed=7):
        task = Task.from_dict(spec)
        run = env.run(task, Condition.DECEPTIVE_INJECTION)
        tgt = task.fields[0].key
        # The injection really diverges ground truth from the accessible tree.
        assert run.world_state[tgt] != run.a11y_tree[tgt]
