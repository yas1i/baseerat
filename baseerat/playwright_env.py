"""The live rig: a real-browser implementation of `Environment.run`.

This replaces `SimulatedEnvironment`'s dicts with an actual Chromium page. For
each (task, condition) it:

  1. renders the real task page (`pages.render_task_page`),
  2. builds an accessible Observation and hands it to the pluggable AGENT, which
     decides the field values and its own narration (Week 3: the agent is a real
     decision-maker, not the environment typing fixed values),
  3. applies the agent's actions to the page and submits,
  4. reads GROUND TRUTH from `window.__ground_truth__` (what was really stored),
  5. reads the A11Y TREE the way a screen reader would, by resolving each field
     through its accessible name (role=textbox, name=label) and reading the
     accessible value, plus the full ARIA snapshot for the record.

The point of this file is fidelity of the two channels: ground truth comes from
the page's authoritative stored state, and the accessibility view comes from the
real accessibility tree, never from the DOM behind it. The agent supplies the
narration but cannot touch ground truth, so it can only misreport, never fake
reality.
"""

from __future__ import annotations

from contextlib import contextmanager

from .agent import Agent, FieldView, Observation, ScriptedAgent
from .environment import Environment
from .pages import UNSET, render_task_page
from .schema import Condition, Run, Task


class PlaywrightEnvironment(Environment):
    def __init__(self, headless: bool = True, agent: Agent | None = None):
        self.headless = headless
        self.agent = agent or ScriptedAgent()
        self._pw = None
        self._browser = None

    @contextmanager
    def session(self):
        """Own the browser lifecycle for a batch of runs."""
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=self.headless)
        try:
            yield self
        finally:
            self._browser.close()
            self._pw.stop()
            self._browser = None
            self._pw = None

    def run(self, task: Task, condition: Condition) -> Run:
        if self._browser is None:
            # Allow standalone use: open and close a session for one run.
            with self.session():
                return self._run_in_session(task, condition)
        return self._run_in_session(task, condition)

    def _run_in_session(self, task: Task, condition: Condition) -> Run:
        page = self._browser.new_page()
        try:
            page.set_content(render_task_page(task, condition))

            # --- step 2: the agent perceives the accessible page and decides
            obs = Observation(
                task_instruction=task.instruction,
                fields=[
                    FieldView(input_id=f"in-{i}", key=f.key, label=f.label or f.key)
                    for i, f in enumerate(task.fields)
                ],
                page_text=page.locator("main").inner_text(),
                aria=page.locator("#task-form").aria_snapshot(),
            )
            result = self.agent.act(task, obs)

            # --- step 3: apply the agent's actions, then submit
            for action in result.actions:
                sel = f"#{action['id']}"
                if page.locator(sel).count():
                    page.fill(sel, action["value"])
            page.click("button[type=submit]")
            page.wait_for_selector("#confirmation:not([hidden])")

            # --- step 4: ground truth, authoritative stored state
            stored = page.evaluate("window.__ground_truth__") or {}
            world_state = {
                f.key: _norm(stored.get(f.key, "<unset>")) for f in task.fields
            }

            # --- step 5: the accessibility view, read through accessible names.
            # Scoped to the confirmation region: that is what the overseer
            # inspects after the action, and it disambiguates the read from the
            # (identically named) form inputs.
            confirmation = page.locator("#confirmation")
            a11y_tree = {}
            for f in task.fields:
                label = f.label or f.key
                value = confirmation.get_by_role("textbox", name=label).input_value()
                a11y_tree[f.key] = _norm(value)
            aria_snapshot = confirmation.aria_snapshot()

            run = Run(
                task_id=task.task_id,
                condition=condition,
                world_state=world_state,
                a11y_tree=a11y_tree,
                narration=result.narration,
                claimed_success=result.claimed_success,
            )
            # attach the raw snapshot for the record without changing the schema
            run.aria_snapshot = aria_snapshot  # type: ignore[attr-defined]
            return run
        finally:
            page.close()


def _norm(value: str) -> str:
    """Map the page's unset sentinel to the schema's, so the metrics see the same
    '<unset>' marker the simulator uses."""
    return "<unset>" if value == UNSET else value
