# Delivery review — 20 October 2026

Package: `courses/controls/linearization`. Claude Opus 5.5 implemented the lesson and explorer;
Codex reviewed sources, mathematics and rendered output, checked the launcher and integrated the shared site.

## Source evidence

- Lecture `1YMTkELi3tE`, 30:46. YouTube offers no English captions; the compact local Whisper transcript
  (`sources/linearization/transcript.txt`, 30-second segments, ignored) was read once. All lesson timestamps are
  segment starts (multiples of 30 s) inside their section; the guide says they are accurate to about half a minute.
- Frames inspected by Claude: 6:00 (`0360`, Jacobian entries x2, x1, 2x1, 2x2 with Df/Dx notation), 10:00
  (`0600`, saddle sketch and Taylor series), 26:00 (`1560`, pendulum with −δθ̇, Df/Dx = [[0, 1], [−cos x1, −δ]],
  A_d, A_u), 30:00 (`1800`, MATLAB: eig(Ad) = −0.0500 ± 0.9987i, Au = [0 1; 1 −d], eig(Au) = −1.0512, 0.9512).
  Frames 14:00, 18:00, 22:00 were reviewed by Codex (`SOURCE_REVIEW.md`).
- Book: `sources/linearization/book.txt` extracts of PDF 350 (printed 330, Eqs. 8.7–8.10) and PDF 355 (printed 335,
  Eqs. 8.23–8.25, undamped, u labelled a torque in the figure). `qa/linearization_qa.py` re-reads both pages from
  `databook.pdf` and checks page numbers and equation tags.
- Correction applied from the source review: damping is taught (board δ, MATLAB d = 0.1). Phase 1 had labelled it a
  companion extension; the explorer now defaults to q = 1, d = 0.1 and labels only δu / C / D as the book extension.

## Checks run on the final state (this machine, Windows, 20 October 2026)

| Command | Result |
|---|---|
| `build_sequences.py --jobs 1` (all 8, then `--only` re-renders of 7 after layout fixes) | 8 sequences, 41 steps, 7.6 MB |
| `tools/check_study.py --package linearization --decode` | 7 sections, 8 sequences, 41 steps, 10 questions, decoded, no errors |
| `qa/linearization_math_qa.py` (explorer math vs SciPy) | 623/623 |
| `qa/linearization_qa.py` (lesson math, media, KaTeX, course, server/tutor context, book, isolation) | 72/72 |
| `node qa/linearization_explorer_qa.js` (explorer mounted alone) | 43/43 |
| `node qa/linearization_browser_qa.js` (full app, installed Chrome) | 127/127 |
| `node --test site/test/build.test.mjs` | 7/7 |
| `node qa/site_browser_qa.js` (all five guides in one site) | 93/93; all 455 referenced media files served |
| `qa/repo_layout_qa.py` | Paths, root environments, Git ignores and fresh scaffold passed |
| Actual `launch_linearization.ps1 -NoBrowser` | Correct identity/course/page; Ctrl+C stopped server and released port |

Highlights of what those assert:

- Explorer numerics: nonlinear RK4 vs `solve_ivp` (DOP853) max error 3.4e-10 over 21 cases; linear closed form vs
  augmented `expm` max scaled error 7.5e-13 over 109 cases; small-offset angle error scales as offset³ (orders
  2.90–3.00); presets reproduce the MATLAB eigenvalues to 1e-9.
- Lesson math recomputed independently: Jacobians by central differences (lecture example, pendulum for several q, d),
  fixed points, the x2-axis instability of the A = 0 example, the sin remainder table, ∓x³, the general damping
  formulas against numpy on a 16×17 (q, d) grid, the six-decimal values on screen, the NumPy snippet in the Section 7
  notes evaluated literally, and every worked example.
- Every display formula and every inline `$…$` fragment (course, steps, quiz) typesets in the bundled KaTeX.
- Server: identity/nonce, no-key tutor error without a network call, `/book` byte ranges, no path escape or listing;
  trusted context for Section 7 / `matlab-check` step 2, the opening state, the explorer, and dropped mismatched IDs.
- Browser: all 7 section pages, all 8 sequences played to their final stills, back/replay/restart, saved step after
  reload, failed clip still lands on its still, missing still shows the step formula, tutor missing-key panel and
  context labels (Section 7 step, explorer), source and book links, explorer presets/verdicts, immediate redraw,
  input-extension note, elapsed-time playback (t = 5.84 after 1.03 s at the test-only ×6), navigation cancels playback
  and saves the reached time, restore, six invalid saved states rejected, quiz retry and first-try score (9 of 10),
  progress summary (41 steps), light/dark, mobile (390 px) without overflow and chart text ≥ 8.5 px, reduced motion.
- Visual: stable-state contact sheets for all 8 sequences (`qa/linearization_contact_sheet.py`) were inspected after
  each render; overlaps and right-edge overflow found in the first two renders were fixed (labels moved, `fit()`
  helper), then re-rendered and re-inspected. Desktop light/dark explorer, Section 6 (dark) and mobile Section 6
  screenshots were inspected.

## Fixes found during review

- The scaffold and three older control packages had an incorrect package-relative master-render ignore pattern
  after the folder move. All four now use `/animation/masters/`; the root ODE rule already targeted the correct
  location. Layout QA checks actual `git check-ignore` results for every course and a fresh scaffold, and verifies
  that public manifests remain versionable. Package QA locates Git even when the Windows shell PATH is stale.
- Stale scaffold text: server docstrings named the overview package; `app.js` header named `control_math.js`.
  Comment-only fixes; added one tutor rule (zero-real-part eigenvalues do not decide nonlinear stability).

## Limitations

- Timestamps are ±30 s (no official captions). Spoken ASR errors (e.g. "Hartman-Growman", "0.1" for "[0 1") were
  resolved from frames, not from audio.
- The explorer covers only the planar pendulum about θ̄ = 0 or π with ū = 0; it is not a general nonlinear-system
  tool. With δu ≠ 0 it compares input responses and does not locate the shifted equilibrium.
- The plotted window is 12 s; off-scale linear curves are clipped with a warning. Pendulum drawings wrap within one
  turn; numeric readouts do not.
- The tutor was tested only in its missing-key state; no paid API call was made.
- The combined site includes this as lecture 4 at `/controls/linearization/`. It is static, so it disables chat
  and uses online book links. The standalone guide supports the optional local PDF and tutor routes.
