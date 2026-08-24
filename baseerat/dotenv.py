"""A tiny, dependency-free .env loader.

Reads KEY=value lines from a .env file in the repo root and puts them into the
process environment, so a key set once in .env is picked up by every run without
needing to export it in each terminal tab. A real exported environment variable
always wins over the .env value (we use setdefault), so .env is a convenience,
not an override.

.env is git-ignored; it never gets committed. Never print the values.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | Path | None = None) -> None:
    if path is None:
        path = Path(__file__).resolve().parent.parent / ".env"
    path = Path(path)
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
