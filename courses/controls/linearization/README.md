# Linearizing Around a Fixed Point study companion

A browser study guide for Steve Brunton's Control Bootcamp lecture
[Linearizing Around a Fixed Point](https://www.youtube.com/watch?v=1YMTkELi3tE) (30:46) and Brunton & Kutz,
*Data-Driven Science and Engineering* (2017 preprint), Section 8.2: printed p. 330 (PDF 350, Eqs. 8.7–8.10)
and printed p. 335 (PDF 355, Eqs. 8.23–8.25).

From the repository root:

```powershell
.\launch_study.ps1                    # all courses in one browser: Controls -> lesson 4
.\launch_linearization.ps1            # serves courses\controls\linearization\dist on 127.0.0.1:8810 (or the next free port)
```

The combined site's lesson URL is `/controls/linearization/`. The standalone launcher enables
the optional local book and tutor routes; the combined static site uses online book links and disables chat.

Viewing the standalone guide needs only standard-library Python; the combined site's build also needs Node.js.
The optional GPT tutor needs `OPENAI_API_KEY` in the environment of
the launcher; everything else (lessons, animations, explorer, quiz) works without it. Progress is stored in the
browser under `linearization-v1`; the server identifies itself as `Study_linearization`.

## Scope

Seven sections following the lecture (times from a local speech-recognition transcript in 30-second segments,
checked against frames; see `SOURCE_REVIEW.md`):

| # | Section | Lecture | Animation (steps) |
|---|---|---|---|
| 1 | Fixed points, $f(\bar x) = 0$ | 0:00–3:00 | `fixed-points` (5) |
| 2 | The Jacobian, rows $f_i$ / columns $x_j$ | 3:00–6:45 | `jacobian-cells` (5) |
| 3 | Shift, expand, truncate; non-fixed point; book A/B/C/D extension | 6:45–13:00 | `shift-expand` (6), `affine-abcd` (3) |
| 4 | Hyperbolic fixed points; $\dot x = \mp x^3$ | 13:00–16:00 | `hyperbolic` (6) |
| 5 | Pendulum with friction, state form, equilibria | 16:00–22:30 | `pendulum-state` (5) |
| 6 | $A_d$, $A_u$, eigenvalues for $d = 0$ and $d > 0$ | 22:30–27:30 | `two-jacobians` (6) |
| 7 | MATLAB check with $d = 0.1$ | 27:30–30:46 | `matlab-check` (5) |

41 steps in 8 ManimGL sequences, 10 quiz questions (an explanation on every option), a worked example per section.
Labelled companion material (not taught in the lecture): the authored examples ($x(1-x)$, $\mp x^3$, the sin
remainder table, the non-fixed expansion point, all worked examples), the general damping formulas, the
energy argument for the undamped center, the NumPy check, and the book's input/output extension ($B$, $C$, $D$).
Damping **is** taught (board $\delta$, MATLAB `d = 0.1`); the book's example is undamped.

## Explorer

`dist/explorer.js` (UI, `window.StudyExplorer = {restore, stop, render}`) on top of `dist/study_math.js`
(dependency-free; `window.StudyMath` in the browser, `require` in Node). It compares
$\dot\theta = \omega,\ \dot\omega = -q\sin\theta - d\omega + u$ with the linearization at the **zero-input
reference** $\bar\theta = 0$ or $\pi$, $\bar\omega = \bar u = 0$:
$\dot\eta = \nu,\ \dot\nu = -q\cos\bar\theta\,\eta - d\nu + \delta u$, $\eta = \theta - \bar\theta$.

- Initial angle and velocity are offsets from the chosen point; switching down/up keeps that interpretation.
  State values and angle errors are unwrapped; drawings show orientation within one turn.
- Defaults $q = 1$, $d = 0.1$, $\delta u = 0$ reproduce the lecture's MATLAB eigenvalues. Presets: lecture down,
  lecture up, undamped down (book), large swing, overdamped ($d = 3$), exactly at equilibrium.
- $\delta u$ (the book's normalized input) and the angle output $C = [1\ 0]$, $D = 0$ are a labelled extension.
  With $\delta u \neq 0$ the reference is no longer a fixed point; plots become an input-response comparison and
  the verdict stays about the zero-input reference.
- Verdicts: from the Jacobian (hyperbolic cases) and, for the undamped hanging center, from energy conservation;
  never from the plotted window. No universal validity radius is claimed.
- Numerics: nonlinear model by classical RK4 with step ≤ `H_MAX = 0.004`, integrated in offset coordinates with the
  exact identity $\sin(\bar\theta + \eta) = \cos\bar\theta\sin\eta$; linear model by a closed-form $2\times 2$
  matrix exponential plus the constant-input response (no case split at critical damping). Both checked against
  SciPy `solve_ivp`/`expm` (`qa/linearization_math_qa.py`).
- Playback advances by elapsed wall-clock time; `stop()` cancels it on navigation and saves the reached time.
  Saved state `state.explorer = {eq, eta0, nu0, q, du, d, t}` is validated on restore (anything invalid → defaults).

`study_math.js` API: `params`, `f`, `jacobianAt`, `linearization` → `{thetaBar, k, A, B, C, D}`, `eigen2`,
`classify` → `{linear, nonlinear, byLinearization, eig}`, `energy`, `expm2`, `nonlinearState`,
`nonlinearTrajectory`, `linearState`, `linearTrajectory`, `compare` → `{nonlinear, linear, angleError, rateError}`;
constants `PARAMS`, `KEYS`, `PRESETS`, `EQUILIBRIA`, `H_MAX`, `T_MAX = 12`. State/trajectory outputs and constants
are frozen; validated parameter and state functions reject invalid inputs with `RangeError`.

## Files

- `course_source.py` → `dist/course.json` (sections, notes, examples, quiz, explorer `limits`/`tutorContext`).
- `animation/control_specs.py` (step titles, tex, explanations, relations), `animation/sequence_scenes.py`
  (ManimGL scenes), `animation/ctl_common.py` (shared helpers, unchanged), `animation/build_sequences.py` (renderer).
- `dist/` is the deliverable, including about 7.6 MiB of rendered clips/stills and bundled KaTeX.
  No lecture media, transcript or book is bundled.
- `BRIEF.md` and `SOURCE_REVIEW.md` are kept for maintainers; `REVIEW.md` records checks and limitations.

## Maintaining

```powershell
.\.venv\Scripts\python.exe courses\controls\linearization\course_source.py
.\.venv\Scripts\python.exe courses\controls\linearization\animation\build_sequences.py --jobs 1            # all
.\.venv\Scripts\python.exe courses\controls\linearization\animation\build_sequences.py --jobs 1 --only matlab-check
.\.venv\Scripts\python.exe tools\check_study.py --package linearization --decode
.\.venv\Scripts\python.exe qa\linearization_math_qa.py        # explorer math vs SciPy
.\.venv\Scripts\python.exe qa\linearization_qa.py             # lesson math, media, course, server/tutor context, book, isolation
node qa\linearization_explorer_qa.js                          # explorer mounted alone (contract)
node qa\linearization_browser_qa.js                           # full app in Chrome
.\.venv\Scripts\python.exe qa\linearization_contact_sheet.py  # stable-state sheets → qa\screenshots\linearization
```

Master renders go to `animation/masters/` (ignored). Keep step `tex` and the stage in agreement; captions wider than
the stage are shrunk by `fit()` in `sequence_scenes.py`.
