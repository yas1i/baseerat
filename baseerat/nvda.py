"""NVDA cross-check.

The live rig reads the accessibility channel through Playwright's ARIA snapshot.
That is a faithful model of the accessibility TREE, but a real blind user hears a
real screen reader, and screen readers do not always speak the tree verbatim
(they apply their own heuristics, punctuation, and field-boundary rules). Before
the paper claims "the non-visual channel", it must show the ARIA snapshot agrees
with what NVDA, the most-used Windows screen reader, actually announces.

This module does the offline half of that: parse an NVDA Speech Viewer log into
the same {field.key: value} representation the rig produces, then compare. The
live capture runs on the Windows VM (see CAPTURE below); this code, its parser,
and its comparator are testable here against a captured log fixture, so the VM
step is plug-and-play rather than exploratory.

CAPTURE (on the Windows VM, documented in README):
  1. Start NVDA; enable Speech Viewer (NVDA menu > Tools > Speech Viewer).
  2. Open the rig's confirmation page in Chrome/Firefox.
  3. Read the confirmation region field by field (NVDA+DownArrow / Tab).
  4. Save the Speech Viewer contents to results/nvda/<task>-<condition>.log.
  5. Run: baseerat.nvda.cross_check_file(aria_tree, that_log).

NVDA announces a read-only textbox roughly as:
    the recipient  edit  read only  accounts@northgate-legal.co.uk
so each confirmation field appears as a line pairing its label with its value.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# NVDA role words that separate an accessible name from its spoken value.
_ROLE_MARKERS = [
    "edit", "read only", "editable text", "text", "read-only",
]


def parse_nvda_log(text: str, labels: dict[str, str]) -> dict[str, str]:
    """Extract {field.key: spoken_value} from an NVDA Speech Viewer log.

    `labels` maps each field key to its accessible label, so a spoken line can be
    matched back to the field it describes. Matching is label-prefixed and
    role-marker aware; a field whose label is not found in the log maps to
    '<not spoken>'.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    label_to_key = {v.lower(): k for k, v in labels.items()}
    result: dict[str, str] = {k: "<not spoken>" for k in labels}

    for line in lines:
        low = line.lower()
        for label_lc, key in label_to_key.items():
            if low.startswith(label_lc):
                remainder = line[len(label_lc):]
                result[key] = _strip_role_markers(remainder)
                break
    return result


def _strip_role_markers(text: str) -> str:
    """Remove NVDA role/state words and separators, leaving the spoken value."""
    s = text
    # Normalise the common separators NVDA uses between fields.
    s = s.replace("•", " ").replace("  ", " ")
    # Drop leading role/state words, longest first, repeatedly.
    changed = True
    while changed:
        changed = False
        t = s.strip(" \t:-–—")
        for marker in sorted(_ROLE_MARKERS, key=len, reverse=True):
            if t.lower().startswith(marker):
                s = t[len(marker):]
                changed = True
                break
        else:
            s = t
    return s.strip()


@dataclass
class Discrepancy:
    key: str
    aria_value: str
    nvda_value: str


def cross_check(aria_tree: dict[str, str],
                nvda_tree: dict[str, str]) -> list[Discrepancy]:
    """Fields where the ARIA snapshot and NVDA disagree. Empty list == the two
    channels agree, which is what validates the rig's accessibility model."""
    out = []
    for key in aria_tree:
        a = aria_tree.get(key, "<missing>")
        n = nvda_tree.get(key, "<missing>")
        if _norm(a) != _norm(n):
            out.append(Discrepancy(key=key, aria_value=a, nvda_value=n))
    return out


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def cross_check_file(aria_tree: dict[str, str], log_path: str | Path,
                     labels: dict[str, str]) -> list[Discrepancy]:
    text = Path(log_path).read_text(encoding="utf-8")
    return cross_check(aria_tree, parse_nvda_log(text, labels))
