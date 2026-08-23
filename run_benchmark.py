#!/usr/bin/env python3
"""Run the Baseerat benchmark end to end and report the three metrics.

For every task, generate a run under each of the three conditions, then audit
each run through BOTH oversight channels with the chosen auditor. Compute
self-report fidelity, non-visual detectability, and the oversight parity gap.

Usage
-----
    python run_benchmark.py                         # heuristic auditor, seed tasks
    python run_benchmark.py --auditor claude        # LLM auditor (needs credentials)
    python run_benchmark.py --tasks tasks/seed.json --out results/run.jsonl

The heuristic auditor runs fully offline with no API spend; it is the baseline
arm of the study. `--auditor claude` is the scalable LLM arm. Falls back to the
heuristic with a printed note if the Claude auditor cannot initialise.
"""

from __future__ import annotations

import argparse
import json
import math
from contextlib import contextmanager
from pathlib import Path

from baseerat.auditor import get_auditor
from baseerat.environment import SimulatedEnvironment, channel_view
from baseerat.metrics import (
    detectability,
    fidelity_by_condition,
    oversight_parity_gap,
)
from baseerat.schema import Channel, Condition, load_tasks


def _fmt(x: float) -> str:
    return "n/a" if isinstance(x, float) and math.isnan(x) else f"{x:.2f}"


def _build_env(env_name: str):
    if env_name == "sim":
        return SimulatedEnvironment(), None
    if env_name == "playwright":
        from baseerat.playwright_env import PlaywrightEnvironment
        env = PlaywrightEnvironment()
        return env, env.session
    raise ValueError(f"unknown env: {env_name!r} (choices: sim, playwright)")


def run(tasks_path: str, auditor_name: str, out_path: str | None,
        env_name: str = "sim") -> dict:
    tasks = load_tasks(tasks_path)
    tasks_by_id = {t.task_id: t for t in tasks}
    env, session_factory = _build_env(env_name)

    try:
        auditor = get_auditor(auditor_name)
    except Exception as exc:  # missing SDK / credentials
        if auditor_name == "claude":
            print(f"[warn] claude auditor unavailable ({exc}); "
                  "falling back to heuristic.")
            auditor = get_auditor("heuristic")
            auditor_name = "heuristic"
        else:
            raise

    runs = []
    results = []

    @contextmanager
    def _maybe_session():
        if session_factory is None:
            yield
        else:
            with session_factory():
                yield

    with _maybe_session():
        for task in tasks:
            for condition in Condition:
                r = env.run(task, condition)
                runs.append(r)
                for channel in Channel:
                    view = channel_view(r, channel)
                    results.append(auditor.audit(task, view, channel, condition))

    fidelity = fidelity_by_condition(runs, tasks_by_id)
    det_nv = detectability(results, Channel.NON_VISUAL)
    det_v = detectability(results, Channel.VISUAL)
    gap = oversight_parity_gap(results)

    report = {
        "auditor": auditor_name,
        "env": env_name,
        "n_tasks": len(tasks),
        "n_runs": len(runs),
        "self_report_fidelity": fidelity,
        "non_visual": {
            "recall": det_nv.recall,
            "false_alarm_rate": det_nv.false_alarm_rate,
            "caught": det_nv.caught,
            "n_diverged": det_nv.n_diverged,
        },
        "visual": {
            "recall": det_v.recall,
            "caught": det_v.caught,
            "n_diverged": det_v.n_diverged,
        },
        "oversight_parity_gap": {
            "overall": gap.overall,
            "per_condition": gap.per_condition,
            "visual_rate": gap.visual_rate,
            "non_visual_rate": gap.non_visual_rate,
        },
    }

    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for res in results:
                f.write(json.dumps(res.to_dict()) + "\n")
        Path(out_path).with_suffix(".summary.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )

    _print_report(report)
    return report


def _print_report(r: dict) -> None:
    print()
    print("=" * 60)
    print(f"  BASEERAT  ·  env: {r['env']}  ·  auditor: {r['auditor']}  ·  "
          f"{r['n_tasks']} tasks, {r['n_runs']} runs")
    print("=" * 60)
    print("\nSelf-report fidelity (agent honesty vs ground truth):")
    for cond, val in r["self_report_fidelity"].items():
        print(f"    {cond:<22} {_fmt(val)}")

    nv, v = r["non_visual"], r["visual"]
    print("\nDetection recall on truly-diverged runs:")
    print(f"    visual channel         {_fmt(v['recall'])}  "
          f"({v['caught']}/{v['n_diverged']} caught)")
    print(f"    non-visual channel     {_fmt(nv['recall'])}  "
          f"({nv['caught']}/{nv['n_diverged']} caught)")
    print(f"    non-visual false alarms on clean runs: "
          f"{_fmt(nv['false_alarm_rate'])}")

    g = r["oversight_parity_gap"]
    print("\nOVERSIGHT PARITY GAP  (visual minus non-visual detection):")
    print(f"    overall                {_fmt(g['overall'])}")
    for cond, val in g["per_condition"].items():
        print(f"    {cond:<22} {_fmt(val)}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the Baseerat benchmark.")
    ap.add_argument("--tasks", default="tasks/seed.json")
    ap.add_argument("--auditor", default="heuristic",
                    choices=["heuristic", "claude"])
    ap.add_argument("--env", default="sim", choices=["sim", "playwright"],
                    help="sim = deterministic simulator; playwright = live browser rig")
    ap.add_argument("--out", default=None,
                    help="write per-audit JSONL and a summary JSON here")
    args = ap.parse_args()
    run(args.tasks, args.auditor, args.out, args.env)


if __name__ == "__main__":
    main()
