#!/usr/bin/env python3
"""Run the language-model auditor sweep and fill Table 3 of the paper.

This is the turnkey command for the language-model arm. It runs the benchmark
once per auditor model over the 150-task corpus, extracts the four Table 3
figures from each run (visual recall, non-visual recall, narration-only parity
gap, and the residual gap with a trusted receipt), and rewrites the marked Table 3
rows in paper/baseerat.tex and paper/baseerat.html from the real results, then
rebuilds the PDF.

It writes ONLY real, measured numbers. If a model auditor cannot be reached
(no credentials, the run falls back to the heuristic auditor), the row is left as
pending rather than filled with a substitute, and the script reports it, so the
paper never carries a fabricated or mislabelled figure.

Prerequisites: an Anthropic API key resolvable by the SDK
(export ANTHROPIC_API_KEY=... or run `ant auth login`).

Usage:
    python paper/fill_table3.py
    python paper/fill_table3.py --models claude-opus-5 claude-sonnet-5 claude-haiku-4-5
    python paper/fill_table3.py --tasks tasks/generated.json
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from run_benchmark import run  # noqa: E402

TEX = ROOT / "paper" / "baseerat.tex"
HTML = ROOT / "paper" / "baseerat.html"

TEX_START = "% TABLE3-ROWS-START"
TEX_END = "% TABLE3-ROWS-END"
HTML_START = "<!-- TABLE3-ROWS-START"
HTML_END = "<!-- TABLE3-ROWS-END -->"


def _fmt(x: float) -> str:
    return "n/a" if isinstance(x, float) and math.isnan(x) else f"{x:.2f}"


def _sweep(models: list[str], tasks_path: str):
    rows = []
    for model in models:
        print(f"\n>>> auditor model: {model}")
        report = run(tasks_path, "claude", None, "sim", "scripted", model)
        if report["auditor"] != "claude" or report.get("model") != model:
            print(f"[skip] {model}: auditor did not run (no credentials?). "
                  "Leaving this row pending.")
            continue
        d = report["defence"]
        rows.append({
            "model": model,
            "vis": report["visual"]["recall"],
            "nonvis": d["non_visual_recall_narration"],
            "gap": d["gap_narration_only"],
            "gap_receipt": d["gap_with_receipt"],
        })
    return rows


def _tex_rows(rows) -> str:
    lines = [TEX_START + " (auto-filled by paper/fill_table3.py; do not edit by hand)"]
    if not rows:
        lines += [
            r"language model A & \pending & \pending & \pending & \pending \\",
            r"language model B & \pending & \pending & \pending & \pending \\",
            r"language model C & \pending & \pending & \pending & \pending \\",
        ]
    for r in rows:
        name = r["model"].replace("_", r"\_")
        lines.append(f"{name} & {_fmt(r['vis'])} & {_fmt(r['nonvis'])} & "
                     f"{_fmt(r['gap'])} & {_fmt(r['gap_receipt'])} \\\\")
    lines.append(TEX_END)
    return "\n".join(lines)


def _html_rows(rows) -> str:
    lines = [HTML_START + " (auto-filled by paper/fill_table3.py; do not edit by hand) -->"]
    if not rows:
        for tag in ("A", "B", "C"):
            lines.append(
                f'        <tr><td>language model {tag}</td>'
                '<td class="pending">pending</td><td class="pending">pending</td>'
                '<td class="pending">pending</td><td class="pending">pending</td></tr>')
    for r in rows:
        lines.append(
            f'        <tr><td>{r["model"]}</td>'
            f'<td>{_fmt(r["vis"])}</td><td>{_fmt(r["nonvis"])}</td>'
            f'<td>{_fmt(r["gap"])}</td><td>{_fmt(r["gap_receipt"])}</td></tr>')
    lines.append("        " + HTML_END)
    return "\n".join(lines)


def _replace_block(text: str, start: str, end: str, new: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"markers {start!r}..{end!r} not found")
    return pattern.sub(new.replace("\\", "\\\\"), text, count=1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fill Table 3 from a real model sweep.")
    ap.add_argument("--models", nargs="+",
                    default=["claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5"])
    ap.add_argument("--tasks", default="tasks/generated.json")
    args = ap.parse_args()

    rows = _sweep(args.models, str(ROOT / args.tasks))
    if not rows:
        print("\nNo model rows were produced (no credentials, or all runs fell "
              "back to the heuristic). Table 3 left pending. Nothing was "
              "fabricated. Set ANTHROPIC_API_KEY and re-run.")
        return

    tex = TEX.read_text(encoding="utf-8")
    TEX.write_text(_replace_block(tex, TEX_START, TEX_END, _tex_rows(rows)),
                   encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    # Rebuild the HTML block boundary to include the closing marker precisely.
    html_new = re.sub(
        re.escape(HTML_START) + r".*?" + re.escape(HTML_END),
        _html_rows(rows).replace("\\", "\\\\"), html, count=1, flags=re.DOTALL)
    HTML.write_text(html_new, encoding="utf-8")

    print(f"\nFilled Table 3 with {len(rows)} real model row(s) in "
          f"{TEX.name} and {HTML.name}.")
    try:
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "paper" / "build_pdf.py")],
                       check=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[note] PDF rebuild skipped/failed ({exc}); run "
              "python paper/build_pdf.py manually.")


if __name__ == "__main__":
    main()
