"""Auditor interface and the expected task specification passed to auditors.

An auditor receives ONLY what its channel is permitted to see (see
`environment.channel_view`) and must return a Verdict: did the task complete as
instructed, or did it diverge? It never sees the Condition label.
"""

from __future__ import annotations

from ..schema import AuditResult, Channel, Condition, Task, Verdict


class Auditor:
    name: str = "base"

    def audit(
        self, task: Task, view: dict, channel: Channel, condition: Condition
    ) -> AuditResult:  # pragma: no cover
        """`condition` is passed only so the result can be labelled for scoring.
        Implementations must NOT use it to decide the verdict."""
        raise NotImplementedError

    def _result(
        self, task: Task, channel: Channel, condition: Condition,
        verdict: Verdict, rationale: str = "",
    ) -> AuditResult:
        return AuditResult(
            task_id=task.task_id,
            condition=condition,
            channel=channel,
            verdict=verdict,
            rationale=rationale,
        )
