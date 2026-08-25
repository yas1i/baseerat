# TACCESS submission checklist

For submitting *Baseerat* to ACM Transactions on Accessible Computing via
Manuscript Central (ScholarOne). Work top to bottom. Items marked **DECISION**
are judgement calls, not mechanical steps; items marked **VERIFY** depend on the
current TACCESS author guidelines, which you should read once before submitting:
https://dl.acm.org/journal/taccess/author-guidelines

Files referenced live in this repo: `paper/baseerat-acmart.tex` (the submission
source), `submission/TACCESS-cover-letter.md`, `submission/human-auditor-protocol.md`.

---

## 0. Two gaps to decide before you submit (read first)

A journal reviewer will almost certainly raise these two. Decide now whether to
close them before submission or to submit and address them in revision.

- [ ] **DECISION: Table 3 has one real language-model row (Sonnet-5).** The
  deterministic reference row plus one frontier-model row makes the core point
  (a strong model is equally fooled through the accessible channel). A reviewer
  may ask for a broader model sweep. Either accept the one-row version as
  honest-and-sufficient, or run more models first (cost is ~£15-30 per model
  over the full corpus; use `--limit` for a cheaper subset). Do not fabricate
  rows.
- [ ] **DECISION: the human expert-auditor arm is a protocol, not a completed
  study** (`submission/human-auditor-protocol.md`). For a full TACCESS paper this
  is the biggest gap; the automated results are a strong short-paper or a strong
  first submission, but the human arm is what anchors the claim. Decide: run the
  study first, or submit the current version and add the human arm in the major
  revision. Be explicit about this in the cover letter.

---

## 1. Anonymity and preprint policy (do this before formatting)

- [ ] **VERIFY: single-blind or double-anonymous review?** Check the TACCESS
  author guidelines. This determines everything below.
- [ ] **If double-anonymous, produce an anonymised build.** The current source
  deanonymises the author in several places that must be masked for review:
  - author name and affiliation (`\author{Yasir Musawar}`, `WAJD AI`, the email)
  - the Zenodo DOI in the abstract/acknowledgements
  - the GitHub URL `github.com/yas1i/baseerat`
  - the "we release ... at an open repository" self-references
  - copyright "WAJD Group" / "Developed by WAJD AI" in the acknowledgements
  Use `\documentclass[acmsmall,review,anonymous]{acmart}` and replace the repo and
  preprint links with "[anonymised repository]" for the review copy. Keep the
  de-anonymised version for the camera-ready.
- [ ] **Disclose the preprint.** ACM permits preprints on non-commercial
  repositories (Zenodo qualifies). State in the cover letter and the ScholarOne
  prior-publication field that a preprint exists at doi:10.5281/zenodo.22080740,
  and that this submission is a substantially complete version, not a duplicate
  publication.
- [ ] **Confirm originality:** not published elsewhere, not under review at any
  other venue.

---

## 2. Manuscript format (acmart)

- [ ] Document class is `acmart` in **acmsmall** (journal) format, with the
  `review` option (adds line numbers for reviewers).
- [ ] **Compile it.** There is no LaTeX compiler on this machine; build
  `paper/baseerat-acmart.tex` on Overleaf (which ships acmart) and fix any
  warnings. Do not submit the HTML-rendered PDF for TACCESS; submit the acmart
  build.
- [ ] **Paste the CCSXML block** generated at https://dl.acm.org/ccs into the
  marked spot in the source (the `\ccsdesc` lines are already present and must
  match the XML).
- [ ] Keywords present and sensible.
- [ ] Abstract is self-contained and within the length the template expects.
- [ ] Word count within scope (TACCESS commonly up to ~11,000 words; longer is
  allowed but justify it).
- [ ] All figures and tables have captions and are referenced in the text.
- [ ] References complete and in **ACM Reference Format**. The current source
  uses a manual `thebibliography`; that compiles, but for the camera-ready move
  the arXiv IDs to proper BibTeX entries with the ACM-Reference-Format style.
- [ ] **House style held:** UK English throughout, no em or en dashes. Grep the
  final source before upload.
- [ ] ORCID added to the author block (register at orcid.org if you do not have
  one) for the non-anonymous version.

---

## 3. Required statements and artifacts

- [ ] **Ethics / accessibility statement** present (the paper has one; confirm it
  covers the human-auditor arm's consent, payment, minimal-risk, and UK-GDPR
  handling with WAJD AI Ltd as controller).
- [ ] **Data and code availability statement:** the corpus, rig, and results are
  in the public repo. For the non-anonymous version, link
  github.com/yas1i/baseerat; for the anonymous version, use an anonymised mirror
  or "[anonymised repository]".
- [ ] **Optional: ACM artifact badging / reproducibility appendix.** The
  benchmark is deterministic and released, which is a strong reproducibility
  story; consider opting into artifact evaluation if TACCESS offers it.
- [ ] **Generative-AI usage statement** if TACCESS requires one (many ACM venues
  now do). Disclose any AI assistance used in producing the work honestly.

---

## 4. Manuscript Central (ScholarOne) submission steps

- [ ] Create or log in to the TACCESS ScholarOne account.
- [ ] Start a new submission; select the correct article type (research paper).
- [ ] Enter title, abstract, keywords, and CCS concepts into the form (they must
  match the manuscript).
- [ ] Add all author metadata and ORCID.
- [ ] Upload the manuscript PDF (the acmart build) and, if requested, the source
  files.
- [ ] Attach the **cover letter** (`submission/TACCESS-cover-letter.md`, filled
  in: reviewer suggestions, the preprint disclosure, and the honest note on the
  human-auditor arm's status).
- [ ] Suggest reviewers with accessibility and AI-safety expertise; list any to
  exclude, with reasons.
- [ ] Answer the originality / not-under-review / preprint declarations.
- [ ] **VERIFY the open-access / APC situation.** ACM is fully open access since
  1 Jan 2026; a TACCESS article may carry an APC unless covered by an ACM Open
  institutional agreement or a waiver. WAJD AI is unlikely to be an ACM Open
  institution, so check the current APC and apply for a waiver or discount if you
  have no funding for it. Do this before you submit, not after acceptance.
- [ ] Review the assembled PDF proof that ScholarOne generates, then submit.
- [ ] Record the manuscript ID and confirmation email.

---

## 5. After submission

- [ ] Note the manuscript ID and expected first-decision timeframe.
- [ ] If you continue the human-auditor arm or add model rows in the meantime,
  keep them ready for the revision rather than emailing updates to the editor.
- [ ] Keep the Zenodo preprint as the citable public version; update it to a new
  Zenodo version if the paper changes materially during review.

---

## Quick pre-flight (the five things most likely to bounce a submission)

1. Wrong review anonymity: submitting a de-anonymised PDF to a double-anonymous
   track (or vice versa). **Verify first.**
2. Missing or malformed CCS concepts.
3. APC surprise at acceptance because it was not checked at submission.
4. The human-auditor arm gap not acknowledged, so a reviewer treats it as an
   oversight rather than scoped future work. **Name it in the cover letter.**
5. Submitting the HTML-rendered PDF instead of the compiled acmart build.
