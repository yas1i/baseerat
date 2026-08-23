from .base import Auditor
from .heuristic import HeuristicAuditor

__all__ = ["Auditor", "HeuristicAuditor", "get_auditor"]


def get_auditor(name: str) -> Auditor:
    """Factory. `claude` is imported lazily so the package works without the SDK
    credentials present."""
    if name == "heuristic":
        return HeuristicAuditor()
    if name == "claude":
        from .claude import ClaudeAuditor
        return ClaudeAuditor()
    raise ValueError(f"unknown auditor: {name!r} (choices: heuristic, claude)")
