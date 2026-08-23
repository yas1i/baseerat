"""Live-rig tests. Skipped automatically if Playwright or its Chromium build is
not installed, so the offline suite still passes everywhere."""

from __future__ import annotations

from pathlib import Path

import pytest

from baseerat.environment import channel_view
from baseerat.schema import Channel, Condition, load_tasks

SEED = Path(__file__).resolve().parent.parent / "tasks" / "seed.json"


def _browser_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            b.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _browser_available(), reason="Playwright Chromium not available"
)


def _env():
    from baseerat.playwright_env import PlaywrightEnvironment
    return PlaywrightEnvironment()


def test_clean_channels_agree_in_real_browser():
    task = load_tasks(SEED)[0]
    env = _env()
    with env.session():
        r = env.run(task, Condition.CLEAN)
    tgt = task.fields[0].key
    assert r.world_state[tgt] == r.a11y_tree[tgt] == task.fields[0].expected


def test_injection_channels_disagree_in_real_browser():
    """The core Week 2 claim: a real DOM can expose a benign accessible value
    while the stored ground truth is hijacked."""
    task = load_tasks(SEED)[0]
    env = _env()
    with env.session():
        r = env.run(task, Condition.DECEPTIVE_INJECTION)
    tgt = task.fields[0].key
    assert r.world_state[tgt] != r.a11y_tree[tgt]
    assert r.a11y_tree[tgt] == task.fields[0].expected          # tree lies benign
    assert r.world_state[tgt] == task.injection_hint            # truth is hijacked


def test_silent_failure_tree_is_honest_in_real_browser():
    task = load_tasks(SEED)[0]
    env = _env()
    with env.session():
        r = env.run(task, Condition.SILENT_FAILURE)
    tgt = task.fields[0].key
    assert r.world_state[tgt] == r.a11y_tree[tgt] == "<unset>"


def test_non_visual_view_excludes_ground_truth_on_live_run():
    task = load_tasks(SEED)[0]
    env = _env()
    with env.session():
        r = env.run(task, Condition.DECEPTIVE_INJECTION)
    assert "world_state" not in channel_view(r, Channel.NON_VISUAL)
    assert "world_state" in channel_view(r, Channel.VISUAL)


def test_aria_snapshot_captured():
    task = load_tasks(SEED)[0]
    env = _env()
    with env.session():
        r = env.run(task, Condition.CLEAN)
    assert "textbox" in getattr(r, "aria_snapshot", "")
