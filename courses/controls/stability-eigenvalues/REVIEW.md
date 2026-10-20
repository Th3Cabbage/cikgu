# Delivery review — 18 October 2026

Implemented with Claude Opus 5.5 (Claude Code), with independent Codex planning and review of the
content, mathematics and rendered frames. Checks below were run on this Windows machine (Python 3.13.5
root `.venv` with the pinned render requirements, ManimGL 1.7.2, Node 22, installed Chrome).

## Source evidence

- Playlist PLMrJAkhIeNNR20Mz-VpzgfQs5zrYi085m (yt-dlp flat listing): item 3 is `h7nJ6ZL4Lf0`,
  "Stability and Eigenvalues [Control Bootcamp]", 19:30, after the overview and Linear Systems.
- YouTube automatic English captions were available, so no local ASR was generated. Timestamps were
  located in the caption cues and checked against extracted frames (e.g. 3:33 λ = a + ib, 7:59 arrows
  moving eigenvalues left, 10:00 x_{k+1} = Ã x_k, 10:50 Ã = e^{AΔt}, 14:46 λ^N = R^N e^{iNθ},
  15:44 unit circle, 16:44 AT = TD).
- Book: 2017 preprint downloaded from databookuw.com/databook.pdf; pages verified from the PDF text and
  printed headers: printed 332/334/335 = PDF 352/354/355.
- Two spoken slips are flagged (12:57 T⁻¹DT order, corrected on the board at 16:44; 16:10 "real part"
  meaning magnitude). Supplement material is labelled; worked examples are authored.

## Checks run (final state)

- `qa/stability_qa.py`: 61/61. Math group: 168 explorer-family systems (real, complex, Jordan) against
  scipy `expm` (840 samples, max relative error ~6e-14), `solve_ivp` DOP853 (42 systems, ~3e-11),
  numpy eigenvalues, and `matrix_power(expm(AΔt), k)` for the iterated samples. All 168 continuous and
  discrete verdicts match an independent NumPy eigenvalue + rank (Jordan-block) reference. A long-horizon
  check with 700-digit mpmath solutions at t = 1500 covers 48 selected systems (the 18 hand-picked
  boundary/special cases and every fifth random case) and confirms both the system verdict and the
  per-start behaviour (decays / bounded / grows / rest) for each of them. Verdict cases include zero eigenvalues, A = 0, A = −I, centers, Jordan at 0
  and ±0.05, and continuous/discrete agreement. All six worked examples are checked numerically, plus
  the boundary facts used in the notes. Also: specs ↔ manifest, all 38 clips decoded as h264 1280×720
  with recorded frame counts and contiguous boundaries, steps+1 stills per sequence, every display
  formula typesets in KaTeX, course timing/sources/book pages, quiz structure, preset verdicts, tutor
  context and missing-key server behaviour, `/book` byte ranges, launcher target and dist isolation.
- `node qa/stability_explorer_regression.js`: 12 verdict cases × 3 sampling steps, 4 special starts,
  240 Hz simulated playback advancing by elapsed time, pause, navigation stop saving the live playback
  time (once), per-eigenvalue colours (saddle in both planes, zero mode, defective and unit-circle
  boundaries), 10 invalid saved states rejected, finite clipped coordinates for extreme growth.
- `node qa/stability_browser_qa.js`: 108/108 in installed Chrome — all six sections and all seven
  sequences (both in Section 3) through every step with the correct stills; Back/Replay/Restart and
  saved step; tutor context label and missing-key message; lecture/book links and the local PDF;
  explorer presets with their verdicts, kind switching, immediate redraw, clipping warnings, play to the
  end, playback cancelled by navigation, the time reached during playback kept through navigation and
  reload (without resuming), saddle eigenvalues coloured per mode in both planes, save/restore, four kinds of invalid saved state; quiz retries
  and first-try scoring; light/dark theme toggle; mobile (390 px) without horizontal overflow on every
  page; reduced motion; no console errors.
- `tools/check_study.py --package stability-eigenvalues --decode`: no errors.
- The real launcher (`-NoBrowser`) served `Study_stability_eigenvalues` on 8790, reported the tutor
  as not configured and the book as available, and stopped cleanly.
- Preservation: `qa.test_study_tools` (5 tests), the Linear Systems explorer regression and its
  `check_study` passed; no tracked file of earlier packages changed.

Visual review: contact sheets of all 45 stable stills and mid-transition frames were inspected; three
rounds of fixes removed overlapping labels (under-bracket captions, eigenvalue labels vs half-plane
captions, a clipped √(g/L) label found by Codex, captions near the chip). Browser screenshots were
inspected in light and dark themes and on mobile.

## Final review corrections (Codex browser review)

Each eigenvalue is now coloured by its own mode (decaying green, growing red, boundary amber, defective
boundary red) while the system verdict is shown separately; cancelling active playback (navigation,
re-render, `pagehide`) saves the latest time; modes-mix step 5 now shows the weights z₁ = 1, z₂ = 0 and
the legend 0·e^{0.6t} = 0. Only modes-mix was re-rendered (`--only modes-mix --jobs 1`); the other six
sequences keep their reviewed media. Because the scene file changed, a later full build without `--only`
would re-render those six from unchanged scene code. Optional test clicks (restart, quiz reset) are now
guarded instead of waiting for a timeout.

## Codex review findings addressed (first round)

Clockwise rotation in the Section 2 example; floating-point excitation of an unstable mode described
as possible rather than inevitable; explorer limits reworded to representative families within slider
ranges; "asymptotically stable" in strict-inequality titles and a qualified upshot (boundary cases need
the Jordan structure); explicit example weights z₁ = 1, z₂ = 0.08 in the modes plot; arg taken modulo
2π and the exponential never reaching 0; right-panel safe margins. Codex's independent check (240
systems, 960 expm and 2640 matrix-power samples, all six examples) agreed with the implementation.

## Limitations

- The explorer covers representative 2×2 canonical families with bounded sliders and a shear basis; it
  is not a general matrix calculator. Discrete systems shown are sampled continuous ones.
- Captions are automatic; wording was paraphrased and equations were checked against frames and book.
- The optional GPT tutor was tested only without a key; no paid API call was made.
- Rendering used `--jobs 1`; parallel renders hit a ManimGL temp-file race for identical text.
- The local PDF is not committed; another revision of the online PDF could paginate differently.
- Later lectures (linearization, controllability) are previewed only, not taught.

No commit, push or deployment was made.
