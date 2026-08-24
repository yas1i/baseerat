# Submission kit

Two routes to a public, timestamped record of Baseerat, since arXiv endorsement
did not come through. Do them in this order: the preprint deposit first (it
secures the priority date today), the venue submission second (it is stronger
once the language-model results are in).

All of this needs your account and your sign-off to publish, so the steps below
stop at the point where you log in and click. The materials are prepared.

Deliverables in this repo:
- `paper/baseerat.pdf` - the rendered paper (from `paper/baseerat.html`).
- `paper/baseerat.tex` - the LaTeX source, for a later properly typeset build.
- `submission/zenodo-metadata.json` - fill-in metadata for the deposit.

---

## Route 3: preprint deposit (DONE)

Published on Zenodo, 24 August 2026:
[doi:10.5281/zenodo.22080740](https://doi.org/10.5281/zenodo.22080740). Priority
date secured. When the language-model results are added, upload the rebuilt PDF
as a new version of the same Zenodo record (this preserves the concept DOI and
adds a version DOI). Steps for reference below.

## Route 3 steps (for the version-2 upload)

A DOI-minting preprint server needs no endorsement and stamps the claim with a
fixed date. Two good options; Zenodo is the simplest.

### Zenodo (recommended)

1. Go to `https://zenodo.org` and log in (ORCID, GitHub, or email).
2. Click **New upload**.
3. Drag in `paper/baseerat.pdf`.
4. Fill the form from `submission/zenodo-metadata.json`:
   - Resource type: **Publication -> Preprint**
   - Title, Authors (Yasir Musawar, affiliation WAJD AI; add your ORCID if you
     have one), Description (the abstract), Keywords, Language English.
   - License: **CC BY 4.0** (standard for a preprint; lets others cite and build
     on it while you keep authorship). If you would rather restrict reuse, CC
     BY-NC 4.0 is the conservative alternative.
5. Optionally **Reserve DOI** so you can cite it immediately.
6. **Publish.** You now have a permanent DOI and a fixed public date.

Note: leave the GitHub link out of the metadata until the repo is public (it is
private now). Add it as a related identifier once you flip it.

### OSF Preprints (alternative)

`https://osf.io/preprints` -> **Add a preprint** -> choose a provider (for
example MetaArXiv or a general one) -> upload the PDF -> same metadata. OSF also
mints a DOI and a date. Pick one of Zenodo or OSF, not both, to avoid duplicate
DOIs for the same object.

---

## Route 2: venue submission

Realistic note: a venue's reviewers will expect the language-model auditor table
(Table 3) populated. So route 2 is best done after the model sweep runs (one
command per model once an API key is available). The venue choice and the
materials can be locked in now.

### Primary: ACM TACCESS (Transactions on Accessible Computing)

The natural home. It is a rolling journal with no submission deadline, which
suits an independent researcher and lets the human expert-auditor arm be added
before the final version.

- Portal: ACM's ScholarOne / Manuscript Central for TACCESS.
- Format: ACM `acmart` (the current `paper/baseerat.tex` is standard `article`
  and would be reformatted to `acmart` for submission; the content maps over
  unchanged).
- Strengthen first: run the language-model auditor sweep to fill Table 3, and if
  possible add the human expert-auditor arm (Section 7) via the EYEWAZ blind
  auditor contacts.

### Alternative: IEEE SaTML 2027

If the adversarial-injection framing ends up dominating the results, the IEEE
Conference on Secure and Trustworthy Machine Learning is a strong fit.

- Format: IEEE conference template.
- Timing: a 2027 edition deadline typically falls in late 2026; check the current
  call before committing.

### Alternative: ASSETS 2027

The premier accessibility venue; best if the human-auditor study is the
centrepiece.

- Format: ACM `acmart`.
- Timing: deadline typically spring or summer 2027; check the current call.

### Abstract and metadata for any venue

- Title: Baseerat: Measuring the Oversight Gap When a Computer-Use Agent's
  Overseer Cannot See the Screen
- Author: Yasir Musawar, WAJD AI
- Abstract: see the paper.
- Keywords: computer-use agents; AI safety; accessibility; screen readers; blind
  and low-vision users; prompt injection; agent oversight; benchmark.
- ACM CCS concepts (for acmart): Human-centered computing -> Accessibility;
  Security and privacy -> Human and societal aspects of security and privacy;
  Computing methodologies -> Artificial intelligence.

---

## Recommended sequence

1. Deposit on Zenodo today (route 3). Priority date secured, DOI in hand.
2. Run the language-model auditor sweep when an API key is available; fill
   Table 3 in `paper/baseerat.tex` and `paper/baseerat.html`; rebuild the PDF
   (`python paper/build_pdf.py`) and update the Zenodo record with version 2.
3. Add the human expert-auditor arm, reformat to `acmart`, and submit to TACCESS.
