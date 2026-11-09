# Cikgu handover

This is the durable project context for a fresh Claude/Codex session or another computer.
It records completed work through 20 October 2026. Start with `CLAUDE.md`; installation is in
[SETUP.md](SETUP.md). Chat history, local agent session IDs and installed environments are not
needed to understand the checked-in implementation.

## Packages and architecture

| Package | Content and source | Launch |
|---|---|---|
| `courses/ode/` | `courses/ode/course.json`; second-order linear differential equations; browser and native guides | `launch_browser.ps1` / `launch_native.ps1` |
| `courses/controls/overview/` | Control Bootcamp overview, video `Pi7l8mMjYVE`; textbook Section 8.1 | `launch_control.ps1` |
| `courses/controls/linear-systems/` | Linear Systems, video `nyqJJdhReiA`; textbook Section 8.2 | `launch_linear_systems.ps1` |
| `courses/controls/stability-eigenvalues/` | Stability and Eigenvalues, video `h7nJ6ZL4Lf0`; Section 8.2, pp. 332/334/335 | `launch_stability_eigenvalues.ps1` |
| `courses/controls/linearization/` | Linearizing Around a Fixed Point, video `1YMTkELi3tE`; Section 8.2, pp. 330/335 | `launch_linearization.ps1` |
| `site/` | Unified website: ODE course + Control Bootcamp (4 lectures), shared navigation; Netlify build | `launch_study.ps1` |

The original ODE browser assets are under `courses/ode/browser/dist`; its animations and native application
are under `courses/ode/animation/` and `courses/ode/native/`. Each later package is independent: its `dist/` contains
the HTML/CSS/JS player, local KaTeX and licenses, course content, clip/still manifest and rendered
media. Its standard-library `server.py` serves that package and optional local book/tutor routes.
No frontend compilation or paid API is needed to view the completed browser packages.

The launchers select Python, bind loopback, skip occupied ports and confirm the correct server
using an app identity and launch nonce. Keep their terminal open; Ctrl+C stops the server.
Progress/theme live in browser storage and do not sync through Git. Individual package keys
prevent one course's progress from being applied to another.

## Completed additions

On 20 October 2026 the repository was grouped by subject: all control lectures now live under
`courses/controls/`, and ODE content lives under `courses/ode/`. Shared tools, QA, website,
environments and launchers remain at the root. The site catalog, renderer environment lookup,
servers, launchers and documentation use the new paths. Public URLs and progress keys stay the
same. `tools/scaffold_study.py` creates `courses/controls/<slug>/` by default, or another subject
with `--subject`. Run `python qa/repo_layout_qa.py` to check these path contracts and scaffolding.
Verification after the move: site build and 7 build tests, 79 site browser/HTTP checks, 5 tool
tests, 24 ODE math checks, 47 Linear Systems checks, 14 targeted Stability server/isolation
checks, 76 overview server checks (mocked tutor), 9 ODE launcher checks and both explorer
regressions passed. All 611 existing media/font assets are byte-identical to the prior paths;
no tracked file was lost. Native GUI rendering was not rerun for this folder refactor.

The overview has six sections, seven ManimGL sequences (34 steps), two explorers, worked
examples and a ten-question explanatory quiz. See [its README](../courses/controls/overview/README.md) and
[review](../courses/controls/overview/REVIEW.md).

Linear Systems has six sections covering the 24:47 lecture, six sequences (33 steps), a live
eigenbasis explorer, worked examples and ten quiz questions. Section 6 highlights the requested
22:22 interpretation. `courses/controls/linear-systems/course_source.py` generates `dist/course.json`.
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
made during verification. See [Linear Systems README](../courses/controls/linear-systems/README.md) and
[review](../courses/controls/linear-systems/REVIEW.md) for details.

Stability and Eigenvalues (playlist item 3, added 18 October 2026) covers the whole 19:30 lecture in
six sections, continuous and discrete time: seven sequences (38 steps, two in Section 3), a three-view
explorer, authored worked examples and ten quiz questions. `courses/controls/stability-eigenvalues/course_source.py`
generates `dist/course.json`. YouTube automatic captions were available (no ASR); timestamps were
checked against frames. Book links target printed pp. 332, 334, 335 = PDF pp. 352, 354, 355 of the
2017 preprint downloaded from databookuw.com/databook.pdf (same pagination as the Linear Systems
references). Lecture slips at 12:57 (T⁻¹DT order) and 16:10 ("real part" for magnitude) are flagged.
Boundary cases (imaginary axis / unit circle, semisimple versus Jordan), transient growth and aliasing
are labelled Supplement; the lecture states only the strict criteria. The explorer uses representative
real 2×2 canonical families (real, complex pair, defective Jordan) with bounded sliders and
T = [[1,s],[0,1]]; verdicts come from eigenvalues/Jordan structure, not the plotted window. See its
[README](../courses/controls/stability-eigenvalues/README.md) and [review](../courses/controls/stability-eigenvalues/REVIEW.md).

## Linearizing Around a Fixed Point (20 October 2026)

Playlist item 4, `1YMTkELi3tE` (30:46), is `courses/controls/linearization/`, launched by
`launch_linearization.ps1` on port 8810 and published by the shared build at
`/controls/linearization/`. It has seven sections, eight authored ManimGL sequences (41 steps),
seven worked examples and ten explanatory quiz questions. Topics follow the actual lecture:
fixed points, Jacobian indexing, shifted coordinates and Taylor truncation, hyperbolicity and
its limits, damped pendulum states/equilibria, down/up Jacobians and the MATLAB eigenvalue check.
Input/output matrices are labelled as the book's extension; feedback design is deferred.

Book references are printed 330/PDF 350 (Eqs. 8.7–8.10) and printed 335/PDF 355 (Eqs. 8.23–8.25).
The video adds viscous damping and uses `q=g/L=1`, `d=0.1`; the book's example is undamped.
There were no English captions: local Whisper base.en ASR was checked against board/MATLAB
frames. [Source review](../courses/controls/linearization/SOURCE_REVIEW.md) records timestamps,
ASR corrections and the source distinctions. `course_source.py` regenerates `dist/course.json`.
The section/step counts come from the data, and the shared site tests now accept additional
lectures from the catalog instead of hardcoding three.

The explorer compares nonlinear RK4 trajectories (step at most 0.004 s) with an independent closed-form
linear response over 0–12 s, in offsets from the selected zero-input equilibrium. It validates saved
values, preserves unwrapped angles, clips off-scale plot segments with a notice, and advances
playback by elapsed time. Constant input is a book-supported extension: classifications always
refer to the zero-input equilibrium, which need not remain fixed under a nonzero input. Positive
damping, critical/overdamped cases and the undamped center have distinct conclusions. A zero or
imaginary Jacobian eigenvalue alone is not a nonlinear stability verdict.

Codex reviewed sources and mathematics, Claude Opus 5.5 implemented the explorer, lesson, scenes
and package QA, and Codex independently checked the delivered data, numerical references,
rendered contact sheets, launcher and combined site. Verification: 623 math assertions
(nonlinear vs SciPy solve_ivp max absolute error 3.37e-10; linear vs augmented expm max scaled
error 7.54e-13), 72 package checks (all 41 clips decoded, 49 stills and all math typeset),
127 standalone browser checks, 43 explorer contract checks, the decode audit, 7 build tests,
93 combined-site browser/HTTP checks, repository layout/scaffold
checks and the actual new launcher with Ctrl+C shutdown. No live paid tutor calls were made.
See the package [README](../courses/controls/linearization/README.md) and
[review](../courses/controls/linearization/REVIEW.md) for full commands and final browser results.
The package review also caught misplaced master-render ignore patterns from the folder move.
Every control package now uses `/animation/masters/`; layout QA checks actual Git ignore behaviour
for every course and checks that public viewing assets remain versionable.

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
- `.claude/skills/build-study-package/SKILL.md`: the maintained authoring workflow. Reuse the
  existing scripts rather than duplicating them inside the skill.

Roles changed in November 2026. Earlier packages were built with Codex as planner/reviewer and
Claude as a restricted implementer launched by `tools/run_claude.py` (now removed). Now the lead
Claude Opus session is the architect for the whole workflow, Sonnet subagents in `.claude/agents/`
(`package-builder`, `render-qa`, `source-reader`) do bounded assigned work, and Codex is the only
reviewer through the Claude Code Codex plugin (`gpt-6.1-sol`, medium effort, `.codex/config.toml`).
Two Codex reviews are required per package (plan/maths, then pre-commit); if Codex is unavailable
the package `REVIEW.md` records "Codex review pending". See CLAUDE.md and the skill.

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

The next bootcamp topic, controllability, is previewed only. YouTube supplied no captions for Linear Systems; local Whisper base.en ASR was generated and
labelled as such. It contains recognition errors, so equations were checked against frames and
the book. The source cache is ignored and must be regenerated or transferred separately.
The user's PDF is also local-only: copy the same revision to root `databook.pdf` to keep page
references correct. Packages remain usable without the PDF; book links need it.

Browser launchers and rendering were tested on Windows with Python 3.13, system Chrome and an
OpenGL-capable GPU. Other operating systems are not verified; direct Python servers can be used
for viewing, but rendering/CLI assumptions must be checked rather than claimed portable.

## Continuing on another computer

The Controls series now also includes playlist item 5, **Controllability** (`u5Sv7YKAkt4`),
under `courses/controls/controllability/`: six sections, six ManimGL sequences / 24 steps,
six worked examples, ten quiz questions and an actuator/coupling explorer. Launch with
`launch_controllability.ps1` (8820), or use the shared library at `/controls/controllability/`.
Sources are textbook printed 336–337 / PDF 356–357 and the 32:29 lecture. Its SOURCE_REVIEW.md
records corrections (full row rank for multi-input systems, SVD versus Gramian energy) and
its REVIEW.md records actual verification and the efficiency trial.

For another Controls lecture, start with **`tools/study_pipeline.py`**, documented at the top of
tools/README.md. A registered playlist selects a subject, and title keywords select a strategy
from tools/study_profiles.json; unrecognized playlists require an explicit configured subject.
Plan/prepare/scaffold/preview/render/check/status are separate stages (brief/author were
removed with the role change in November 2026). Sources and
merged stage checkpoints stay ignored in sources/<slug>. A human reviews transcript equations,
book pages and sparse frames, then writes REVIEW.md in that cache before authoring. Historically
Claude got a fresh compact brief and a CLI budget cap with low effort. The Controllability trial
used medium effort and finished in 13m43s with 87,256 output tokens, vs 323,667 in the previous
lesson's two runs (different scope; excludes Codex/tooling/review usage). No savings are guaranteed.

Reuse tools/contact_sheets.py and qa/study_browser_qa.js for new packages. Lesson-specific browser
assertions plug into the latter through qa/<slug_with_underscores>_explorer_checks.js; independent
math comparisons remain lesson-specific. The reusable audit supports --typeset for all formulas,
including hidden quiz feedback. Scaffolding now uses the corrected serialized renderer. Do not
copy old browser suites or resume a large previous lesson session just to add another lecture.

After pulling the commit and following setup, start Claude Code at the repository root and ask:

> Read CLAUDE.md and docs/HANDOVER.md. Use /build-study-package to create the next study package
> for [video URL], using [book location/pages]. Preserve existing packages and follow the browser
> and ManimGL workflow. Review the actual source scope before authoring.

For a bug fix, identify the affected package and behavior. Read only relevant implementation
and sources, run checks appropriate to the change, and update these docs if conventions change.
Do not rely on historical briefs as current setup instructions: `courses/controls/overview/BRIEF.md` and
`courses/controls/linear-systems/BRIEF.md` describe the original implementation assignment.
