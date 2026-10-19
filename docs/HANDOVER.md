# Cikgu handover

This is the durable project context for a fresh Claude/Codex session or another computer.
It records completed work through 19 October 2026. Start with `CLAUDE.md`; installation is in
[SETUP.md](SETUP.md). Chat history, local agent session IDs and installed environments are not
needed to understand the checked-in implementation.

## Packages and architecture

| Package | Content and source | Launch |
|---|---|---|
| Original ODE | Root `course.json`; second-order linear differential equations; browser and native guides | `launch_browser.ps1` / `launch_native.ps1` |
| `control/` | Control Bootcamp overview, video `Pi7l8mMjYVE`; textbook Section 8.1 | `launch_control.ps1` |
| `linear-systems/` | Linear Systems, video `nyqJJdhReiA`; textbook Section 8.2 | `launch_linear_systems.ps1` |
| `stability-eigenvalues/` | Stability and Eigenvalues, video `h7nJ6ZL4Lf0`; Section 8.2, pp. 332/334/335 | `launch_stability_eigenvalues.ps1` |
| `site/` | Unified website: ODE course + Control Bootcamp (3 lectures), shared navigation; Netlify build | `launch_study.ps1` |

The original ODE browser assets are under `browser/dist`; its animations and native application
are under `animation/` and `native/`. Each later package is independent: its `dist/` contains
the HTML/CSS/JS player, local KaTeX and licenses, course content, clip/still manifest and rendered
media. Its standard-library `server.py` serves that package and optional local book/tutor routes.
No frontend compilation or paid API is needed to view the completed browser packages.

The launchers select Python, bind loopback, skip occupied ports and confirm the correct server
using an app identity and launch nonce. Keep their terminal open; Ctrl+C stops the server.
Progress/theme live in browser storage and do not sync through Git. Individual package keys
prevent one course's progress from being applied to another.

## Completed additions

The overview has six sections, seven ManimGL sequences (34 steps), two explorers, worked
examples and a ten-question explanatory quiz. See [its README](../control/README.md) and
[review](../control/REVIEW.md).

Linear Systems has six sections covering the 24:47 lecture, six sequences (33 steps), a live
eigenbasis explorer, worked examples and ten quiz questions. Section 6 highlights the requested
22:22 interpretation. `linear-systems/course_source.py` generates `dist/course.json`.
Book links target printed pp. 331–332 / PDF pp. 351–352 in the supplied 2017 preprint,
Eqs. 8.11–8.19. The lecture uses D where the book uses Lambda.

Its example uses T=[[1,1],[0,1]], D=diag(-1,-2), x(0)=[2,1], so z(0)=[1,1] and
x(t)=[exp(-t)+exp(-2t),exp(-2t)]. At t=ln(2), x=[3/4,1/4]. This is an original companion
example, not a claim about the lecturer's numerical example. The explorer chooses
T=[[1,s],[0,1]] and builds A=TDT^-1 exactly. It covers this real diagonalizable family;
defective matrices are a note, not a supported slider preset. Later lectures cover full
stability analysis, discrete-time systems and controllability; they are not taught here.

The optional Ask GPT panel is ready to enable locally. Its server constructs trusted context
from course/section/animation-step IDs, and handles missing keys. No live paid API calls were
made during verification. See [Linear Systems README](../linear-systems/README.md) and
[review](../linear-systems/REVIEW.md) for details.

Stability and Eigenvalues (playlist item 3, added 18 October 2026) covers the whole 19:30 lecture in
six sections, continuous and discrete time: seven sequences (38 steps, two in Section 3), a three-view
explorer, authored worked examples and ten quiz questions. `stability-eigenvalues/course_source.py`
generates `dist/course.json`. YouTube automatic captions were available (no ASR); timestamps were
checked against frames. Book links target printed pp. 332, 334, 335 = PDF pp. 352, 354, 355 of the
2017 preprint downloaded from databookuw.com/databook.pdf (same pagination as the Linear Systems
references). Lecture slips at 12:57 (T⁻¹DT order) and 16:10 ("real part" for magnitude) are flagged.
Boundary cases (imaginary axis / unit circle, semisimple versus Jordan), transient growth and aliasing
are labelled Supplement; the lecture states only the strict criteria. The explorer uses representative
real 2×2 canonical families (real, complex pair, defective Jordan) with bounded sliders and
T = [[1,s],[0,1]]; verdicts come from eigenvalues/Jordan structure, not the plotted window. See its
[README](../stability-eigenvalues/README.md) and [review](../stability-eigenvalues/REVIEW.md).

## Unified study site (19 October 2026)

The user approved one website: a library home with the ODE guide as one course and a Control Bootcamp
course of three ordered lectures, with shared navigation, one Netlify deployment and preserved
teaching features/progress. `site/build.mjs` (Node built-ins only) copies each package `dist/`
byte-for-byte into ignored `site/dist`, injecting only a course bar into each `index.html`; the
registry is `site/catalog.json`. Root `netlify.toml` builds with base `site`, `node build.mjs`,
publish `dist`. It was not deployed or connected to a Netlify account in this work.

Limits: the site is static, so Ask GPT is disabled there (static `api/status`, explanatory panel) and
book links use the online copy; the standalone launchers keep live chat/local PDF. Storage keys are
unchanged, so progress is shared within one site origin, but local ports and the Netlify domain have
separate progress (no migration). Details, Netlify UI settings and adding a lecture:
[site/README.md](../site/README.md).

Checks on 19 October 2026: 7/7 build-invariant tests (`node --test site/test/build.test.mjs`:
determinism, byte-identical copies, public-asset-only output, link resolution, registry validation),
79/79 HTTP/Chrome checks (`qa/site_browser_qa.js`, including all 365 manifest media paths and one
played clip per package), a repeated default rebuild with identical tree hash, and a real
`launch_study.ps1` run (busy-port fallback, nonce health check, server exit when the launcher was
killed). Package content and media were not changed, so math/render suites were not rerun.

## Reusable workflow and design decisions

The user chose browser delivery with the ODE guide's step-controlled ManimGL experience.
Animations show transformations and diagram changes; they are pre-rendered clips with stable
stills, rather than a live ManimGL process running in the browser. The later packages use
mathtext-to-SVG helpers because the tested environment had no LaTeX installation.

- `download_study.ps1` + `tools/prepare_study.py`: cached source downloads, caption compaction,
  optional local Whisper ASR, selected PDF extraction and sparse review frames.
- `tools/scaffold_study.py`: copies the overview's player/server/assets/render helpers into a
  new package, without copying teaching content or media. The author must supply the lesson,
  scenes, explorer and mathematical implementation. It refuses existing targets.
- `tools/check_study.py`: compact content/media checks, optionally decoding every clip.
- `tools/run_claude.py`: optional focused CLI handoff, resumable local logs and configurable
  model/effort. Claude Opus 5.5 was used for the Linear Systems implementation; availability is
  account-dependent and a future model can be selected with `--model`.
- `.claude/skills/build-study-package/SKILL.md`: the maintained authoring workflow. Reuse the
  existing scripts rather than duplicating them inside the skill.

Codex acted as planner/reviewer and Claude as implementer. A new Claude session may do the whole
workflow; it does not require Codex or this collaboration arrangement. External runner sessions
use safe mode: give explicit instructions in their brief to read the repository guidance.
The runner has Windows Git Bash assumptions; direct Claude Code use is also supported.

The current scaffold copies renderer code from the overview. The newer Linear Systems renderer
has a corrected FFmpeg codec probe; when developing another renderer, check metadata against
the actual input stream instead of assuming the copied overview probe reports every field.
Stability and Eigenvalues copied the corrected Linear Systems renderer/server and defaults to
`--jobs 1`: parallel renders collided on ManimGL's shared temporary SVG for identical Text. For a quick
scene error check use `manimgl sequence_scenes.py <Scene> -w -s`; `-s` without `-w` opens an
interactive preview window and does not exit.

## Evidence and known limits

Recorded delivery checks on 14 October 2026:

- Overview: 26 math, 15 media, 79 browser, 76 server and 12 launcher checks passed.
- Linear Systems: 47 math/media/course/server checks and 74 browser checks passed.
- Independent Linear Systems comparison: 128 systems, 640 SciPy exponential samples,
  maximum absolute error 4.27e-14.
- Additional regressions cover zero/positive eigenvalues, elapsed-time playback at simulated
  240 Hz, pause/navigation cancellation and persisted time; five preparation tests cover caption
  handling, page validation and timestamps.

Recorded Stability and Eigenvalues checks on 18 October 2026 (fresh root `.venv` from the pinned
requirements on Python 3.13.5): 61/61 math/media/course/server checks (SciPy expm and solve_ivp,
an eigenvalue/rank verdict reference for all 168 systems, and 700-digit long-horizon solutions for 48
selected systems), the explorer regression, 108/108 browser checks, `check_study --decode` and a real
launcher run. After the final review only modes-mix was re-rendered (`--only modes-mix`).

These are historical results, not a claim about a fresh machine. Commands and dependencies are
in setup/package docs. Numerical checks, actual decoded media and visual browser inspection
serve different purposes. Ignored QA results/screenshots can be regenerated.

Portability review on 18 October 2026: the skill validator, five preparation tests and explorer
regressions passed. A clean export of the staged Git files served both new packages, confirmed
their identities/course data and missing-key state, and contained every clip/still for all
67 steps without a PDF, research cache or virtual environment. Documentation links resolved.
This checks viewing portability; a fresh dependency installation/render was not repeated.

Later bootcamp lectures (linearization, controllability) are previewed only. YouTube supplied no captions for Linear Systems; local Whisper base.en ASR was generated and
labelled as such. It contains recognition errors, so equations were checked against frames and
the book. The source cache is ignored and must be regenerated or transferred separately.
The user's PDF is also local-only: copy the same revision to root `databook.pdf` to keep page
references correct. Packages remain usable without the PDF; book links need it.

Browser launchers and rendering were tested on Windows with Python 3.13, system Chrome and an
OpenGL-capable GPU. Other operating systems are not verified; direct Python servers can be used
for viewing, but rendering/CLI assumptions must be checked rather than claimed portable.

## Continuing on another computer

After pulling the commit and following setup, start Claude Code at the repository root and ask:

> Read CLAUDE.md and docs/HANDOVER.md. Use /build-study-package to create the next study package
> for [video URL], using [book location/pages]. Preserve existing packages and follow the browser
> and ManimGL workflow. Review the actual source scope before authoring.

For a bug fix, identify the affected package and behavior. Read only relevant implementation
and sources, run checks appropriate to the change, and update these docs if conventions change.
Do not rely on historical briefs as current setup instructions: `CONTROL_BRIEF.md` and
`linear-systems/BRIEF.md` describe the original implementation assignment.
