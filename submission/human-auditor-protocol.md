# Human expert-auditor study protocol

The human arm of Baseerat. It anchors the language-model auditor (a lower bound
on the oversight channel) against real non-visual detection by professional blind
accessibility auditors, and supplies the central empirical claim for the TACCESS
version. This document is the protocol, the participant materials, and the
analysis plan, written so the study can be run and reported without an
institutional review board while meeting the ethical bar TACCESS expects.

## 1. Objective and hypotheses

**Objective.** Measure how much of an agent divergence a person restricted to the
accessible channel actually detects, and compare it to (a) the sighted visual
channel and (b) the language-model auditor under the same restriction.

**Primary hypothesis (H1).** Non-visual expert detection of the deceptive-injection
condition is substantially below visual detection, reproducing a positive oversight
parity gap with human auditors, not only the deterministic and language-model ones.

**Secondary hypotheses.**
- H2: Non-visual expert detection of the silent-failure condition is high (the
  honest tree supports a cross-check), confirming the gap is specific to deception.
- H3: A trusted action receipt raises non-visual expert detection of the
  deceptive-injection condition to near the visual level, closing the gap.
- H4: The language-model auditor under the non-visual restriction is a conservative
  lower bound on expert human non-visual detection (model recall does not exceed
  expert recall on the same items).

## 2. Design

Within-participant. Each auditor reviews a stratified sample of runs through the
non-visual channel and, in a separate block, a matched set with a trusted receipt
added. Condition and archetype are balanced across items; the condition label is
never shown. A held-out set of the same items is scored through the visual channel
by sighted auditors to establish the visual detection ceiling on identical items.

## 3. Participants

- **Who.** Professional blind or low-vision accessibility auditors who use a screen
  reader as their primary access method in daily professional work (for example,
  accessibility testers, assistive-technology trainers). Recruit through the EYEWAZ
  accessibility contacts and established accessibility-professional networks.
- **Number.** 8 to 12 expert auditors. This is an expert-review design, not a
  population survey; the unit of statistical interest is the run item, of which
  each auditor scores many, so precision comes from items per auditor rather than
  from a large participant count.
- **Inclusion.** Daily screen-reader use; professional accessibility experience;
  informed consent. **Exclusion.** None beyond failure to consent.
- **Compensation.** Paid at a professional accessibility-consulting rate for their
  time, independent of how they score any item. State the rate in the consent form.

## 4. Materials

- A **stratified sample** of runs drawn from the 150-task corpus: all three
  conditions, all four injection archetypes, across the six domains, balanced so no
  auditor can infer the condition from position or frequency.
- Each item is presented purely through the **non-visual channel**: the agent
  narration and the post-hoc accessibility tree, delivered as an accessible page
  the auditor navigates with their own screen reader and settings. In the receipt
  block, the trusted action receipt is added to the same page.
- A simple accessible response form: for each item, a verdict (task completed as
  instructed / did not complete as instructed) and an optional free-text reason.

## 5. Procedure

1. Consent and a short screen-reader and experience questionnaire.
2. Two practice items with feedback, to calibrate the task and the response form.
3. Block A (narration only): the auditor reviews each item through the non-visual
   channel and records a verdict. No time limit; the auditor uses their own screen
   reader, speech rate, and navigation habits.
4. Block B (with receipt): a matched, re-randomised item set with the trusted
   receipt added.
5. A short debrief: what cues the auditor used, and where they felt unable to tell.

The condition label is never shown, in either block, at any point.

## 6. Measures

- **Per-item verdict** mapped to detection of divergence.
- **Recall** on truly-diverged items (by condition and by archetype), the primary
  measure, and **false-alarm rate** on clean items.
- **Human oversight parity gap**: visual-channel detection on the same items minus
  non-visual expert detection.
- **Defence effect**: non-visual expert recall with receipt minus without.
- **Model-vs-human**: item-level agreement between the language-model non-visual
  auditor and expert auditors, and whether model recall stays at or below expert
  recall (H4).

## 7. Analysis plan

- Report recall and false-alarm rate with 95% confidence intervals, clustered by
  auditor and by task (a mixed-effects logistic model with random intercepts for
  auditor and task; condition, archetype, and defence as fixed effects).
- Pre-register the primary comparison (H1) and the defence comparison (H3) before
  data collection to avoid multiple-comparison drift.
- Report per-archetype recall so the subtlety gradient (homograph to redirect) is
  visible.

## 8. Ethics, consent, and data handling

- **Risk.** Minimal, non-clinical. Participants review synthetic task outcomes; no
  deception of the participant is involved beyond withholding the condition label,
  which is disclosed at debrief. No real personal data is present in any item (the
  corpus is fictional).
- **Independent-researcher route.** With no institutional review board, run the
  study as a paid professional-services expert review with written informed
  consent, a plain-language information sheet, the right to withdraw at any time
  without penalty, and no collection of special-category data. This is the standard
  design TACCESS and ASSETS accept for expert-auditor evaluations; if a partner
  university co-authors the journal version, route it through their board as well.
- **Data protection (UK GDPR).** Data controller: WAJD AI Ltd. Collect the minimum:
  a participant identifier, the experience questionnaire, and per-item verdicts.
  Store pseudonymised; keep the identity key separate and access-restricted. Lawful
  basis: consent for participation, legitimate interest for the anonymised research
  output. Provide contact details for access, rectification, and erasure requests,
  and a retention period after which the identity key is destroyed.
- **Accessibility of the study itself.** Every participant-facing artefact (consent
  form, information sheet, item pages, response form) is delivered in an accessible
  format the participant can complete with their own screen reader. Offer the
  consent and debrief by the participant's preferred accessible channel.

## 9. Consent form (plain-language template)

> **Study.** Baseerat: how well can an expert screen-reader user detect when a
> computer-use agent has failed or been misdirected, using only what the agent says
> and what the accessibility information shows.
>
> **What you will do.** Review a set of task outcomes through your screen reader and,
> for each, say whether the task was completed as instructed. About [X] minutes.
>
> **Payment.** [rate] for your time, regardless of how you answer.
>
> **Voluntary.** You may stop at any time without giving a reason and without
> losing payment for time already given.
>
> **Data.** We record only your answers and a short experience questionnaire, stored
> pseudonymously by WAJD AI Ltd. You can ask to see, correct, or delete your data:
> [contact]. We keep the link to your identity only until [date], then destroy it.
>
> **Consent.** I have read and understood the above and agree to take part.
> Name / signature / date, captured in an accessible format.

## 10. Reporting

The results fill the human rows alongside Table 3 and support the paper's central
claim. Report the human oversight parity gap and the defence effect as the primary
findings, the model-vs-human comparison as validation of the language-model arm as
a lower bound, and the per-archetype breakdown as the mechanism detail.
