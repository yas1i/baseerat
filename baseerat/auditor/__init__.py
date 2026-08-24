from .base import Auditor
from .heuristic import HeuristicAuditor

__all__ = ["Auditor", "HeuristicAuditor", "get_auditor"]


def get_auditor(name: str, model: str | None = None) -> Auditor:
    """Factory. `claude` is imported lazily so the package works without the SDK
    credentials present. `model` selects the auditor model for the LLM arm's
    across-models sweep (ignored by the heuristic auditor)."""
    if name == "heuristic":
        return HeuristicAuditor()
    if name == "claude":
        from .claude import MODEL, ClaudeAuditor
        return ClaudeAuditor(model=model or MODEL)
    raise ValueError(f"unknown auditor: {name!r} (choices: heuristic, claude)")
