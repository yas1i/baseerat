# Cover letter: ACM TACCESS submission

*Draft. Ready to send once Table 3 (the language-model auditor sweep) is
populated and, ideally, the human expert-auditor arm is complete. Fill the
bracketed fields before sending.*

---

To the Editor-in-Chief,
ACM Transactions on Accessible Computing (TACCESS)

Dear Editor,

I am submitting the manuscript **"Baseerat: Measuring the Oversight Gap When a
Computer-Use Agent's Overseer Cannot See the Screen"** for consideration as a
research article in TACCESS.

Computer-use agents now act on real interfaces on a person's behalf, and their
safety is increasingly benchmarked. Every existing safety benchmark, however,
scores agent behaviour against ground truth read from the screen, and so assumes
the human overseer who would catch a failure can see the screen. For a blind
screen-reader user that assumption fails: the only account of what an agent did
arrives through the agent's narration and the accessibility tree, and a growing
body of work shows that an agent's own account of its actions is unreliable. This
manuscript is, to our knowledge, the first to measure the consequence.

The contribution is threefold and sits squarely within the scope of TACCESS:

1. A problem formulation and a metric, the **oversight parity gap**, that
quantifies how much of an agent failure a non-visual overseer can detect relative
to a sighted one, over the same runs.

2. A live benchmark, released in full, that constructs the adversarial case in a
real browser: an indirect injection that poisons the accessibility tree in step
with the agent's narration, so the attack and its cover story travel down the one
channel a blind user has. We validate the accessible channel against the NVDA
screen reader.

3. A defence, trusted action receipts, that we show closes the gap, giving the
work a constructive result rather than only a warning.

We believe TACCESS is the natural home for this work because it treats
accessibility not as an afterthought to agent safety but as a first-class safety
property that can be measured and improved. The manuscript reports a deterministic
reference-auditor baseline over a 150-task corpus, a language-model auditor
evaluation across [N] models, and a human expert-auditor study with [N]
professional blind accessibility auditors that anchors the automated results.

This work is original, has not been published elsewhere, and is not under review
at another venue. A preprint is archived at doi:10.5281/zenodo.22080740, and the
benchmark, rig, corpus, and results are released as an open repository at
https://github.com/yas1i/baseerat. The author declares no competing interests.

[Optional: We suggest the following reviewers with relevant expertise in agent
safety and accessibility: [names]. We request that [names] be excluded owing to
[reason].]

Thank you for considering this submission. I look forward to the reviewers'
comments.

Yours sincerely,

Yasir Musawar
WAJD AI
baseerat@wajd.co.uk
