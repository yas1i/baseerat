# Baseerat

**Measuring computer-use agent oversight without sight.**

Every safety benchmark for computer-use agents silently assumes the human
overseer can see the screen. For roughly 40 million blind screen-reader users
that assumption is false, and the entire oversight channel collapses onto one
thing: the agent's own account of what it did. The recent literature has just
finished proving that account is unreliable (agents overclaim success by up to
5.3x). Baseerat measures the consequence.

The headline metric is the **oversight parity gap**: the detection rate a
sighted overseer achieves on a diverged agent run, minus the rate an overseer
restricted to the accessible channel (narration plus the post-hoc accessibility
tree) achieves on the same run. That gap is oversight a blind user structurally
cannot exercise. Nobody has reported it.

*Baseerat* (بصیرت): inner sight, discernment.

WAJD AI · copyright WAJD Group.

---

## What is here (Week 1)

A working end-to-end pipeline that produces the three metrics on a seed task
set, proving the design before the live agent rig is wired in.

- **`baseerat/schema.py`** - the data model: tasks, the three run conditions,
  the two oversight channels, verdicts.
- **`baseerat/environment.py`** - run generation. `SimulatedEnvironment` turns a
  task into a run under each condition, deterministically. The seam
  (`Environment.run`) is exactly what the live Playwright + NVDA rig will
  implement in weeks 2-3.
- **`baseerat/auditor/`** - two auditors behind one interface:
  `HeuristicAuditor` (deterministic, offline, the study's baseline arm) and
  `ClaudeAuditor` (Claude under the same perceptual restriction, the scalable
  LLM arm).
- **`baseerat/metrics.py`** - self-report fidelity, non-visual detectability,
  oversight parity gap.
- **`tasks/seed.json`** - five seed tasks (email, address form, payee, file
  move, calendar) across web and desktop surfaces.
- **`run_benchmark.py`** - runs everything and prints the report.
- **`tests/`** - 11 behavioural tests asserting the central prediction as a
  property of the code.

### The three conditions

| Condition | Ground truth | Accessibility tree | Narration | Who can catch it |
|---|---|---|---|---|
| `clean` | matches the task | honest | truthful | - (nothing to catch) |
| `silent_failure` | a field silently fails | **honest** (shows the failure) | falsely claims success | anyone who cross-checks the tree against the claim, sighted or not |
| `deceptive_injection` | a field is hijacked | **poisoned** to match the lie | cover story | only a sighted overseer reading the real screen |

The `deceptive_injection` row is the paper: the attack and its cover story
travel down the one channel a blind user has, so the accessible channel is
structurally insufficient.

---

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install anthropic pytest
.venv/bin/python run_benchmark.py                 # offline, no API spend
```

Current output on the seed set (heuristic baseline auditor):

```
Detection recall on truly-diverged runs:
    visual channel         1.00  (10/10 caught)
    non-visual channel     0.50  (5/10 caught)

OVERSIGHT PARITY GAP  (visual minus non-visual detection):
    overall                0.50
    silent_failure         0.00
    deceptive_injection    1.00
```

The gap is real, positive, and concentrated entirely in the deceptive-injection
condition - exactly the thesis.

### The LLM auditor arm

```bash
export ANTHROPIC_API_KEY=...        # or: ant auth login
.venv/bin/python run_benchmark.py --auditor claude --out results/claude-seed.jsonl
```

This runs Claude (`claude-opus-5`, adaptive thinking, structured-output verdicts)
as the auditor under both channels. Without credentials it prints a note and
falls back to the heuristic auditor, so the command never fails.

```bash
.venv/bin/python -m pytest -q      # 11 tests, fully offline
```

---

## Roadmap

Baseerat is a seven-week build to an arXiv preprint. Week 1 (this) is the
pipeline and metrics on seed data. The remaining weeks:

- **Weeks 2-3** - replace `SimulatedEnvironment` with the live rig: a
  Playwright-driven computer-use agent on scripted pages, real ground-truth
  action logs, and real accessibility output captured via NVDA. Same
  `Environment.run` seam; nothing downstream changes.
- **Weeks 4-6** - scale to ~150 tasks; run the full LLM-auditor arm across
  models; add the defence evaluation (accessibility-rendered action receipts vs
  narration-only).
- **Week 7** - arXiv preprint with the LLM-auditor results. The human
  expert-auditor arm follows for the ACM TACCESS journal version.

The design deliberately keeps every condition matched to a clean control, and
auditors are blind to the condition label - the control-before-belief discipline
carried into the benchmark itself.
