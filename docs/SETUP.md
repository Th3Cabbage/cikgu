# Set up another computer

## Get the repository

Commit locally, then push to the Git remote when you want another computer to fetch the work.
A local commit alone does not transfer files between computers. On the other computer, clone
the repository (or pull the branch into an existing clone). Run the following commands from
its root. Git must include the package `dist/` media and local KaTeX assets, as well as source,
scripts, docs and `.claude/skills/`.

This is the tested **Windows / PowerShell** workflow. Install Python (3.13 was used), Git,
and a browser. Rendering is optional; Node.js and Chrome are needed for the supplied browser QA.
No local username or original checkout path is required.

## View a completed package

Make sure `python --version` works. The unified site (all courses, shared navigation) also needs
Node.js 18+ for its dependency-free build:

```powershell
.\launch_study.ps1               # all courses in one site: 8800 (see site/README.md)
```

Or run one package on its own (needed for the optional Ask GPT panel and local-PDF links):

```powershell
.\launch_browser.ps1             # ODE: default port 8765
.\launch_control.ps1             # overview: 8770
.\launch_linear_systems.ps1      # Linear Systems: 8780
.\launch_stability_eigenvalues.ps1   # Stability and Eigenvalues: 8790
.\launch_linearization.ps1        # Linearizing Around a Fixed Point: 8810
.\launch_controllability.ps1      # Controllability: 8820
```

Each opens a browser and prints its actual URL, using the next free port if necessary.
Keep the terminal open. Ctrl+C stops the server. If the local PowerShell policy blocks the
script, launch just that script with a process-level policy override:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\launch_linear_systems.ps1
```

Without PowerShell, a direct viewing command is `python -I courses/controls/linear-systems/server.py --port 8780`;
open the printed URL manually. The original ODE uses `python courses/ode/browser/serve_local.py --port 8765`.
Do not open index.html via file://; the page fetches JSON over the local server.

## Restore the optional source book and research cache

The supplied book is **not committed**. Copy the same 2017 preprint to `databook.pdf` at the
repository root. Linear Systems references PDF pages 351–352 / printed pages 331–332; a different
revision can have different pagination. Without the book the lessons still run, but local book
links are unavailable. The downloaded lecture/transcript cache under `sources/` is also ignored.

To regenerate Linear Systems research:

```powershell
.\download_study.ps1 -Url 'https://www.youtube.com/watch?v=nyqJJdhReiA&t=1342s' -Slug linear-systems -BookPages '351-352' -Transcribe
```

Stability and Eigenvalues (automatic captions exist, so no transcription runs; book PDF pages 352–354,
with the p. 335 / PDF 355 example read from the same PDF):

```powershell
.\download_study.ps1 -Url 'https://www.youtube.com/watch?v=h7nJ6ZL4Lf0' -Slug stability-eigenvalues -BookPages '352-354' -Transcribe
```

The free 2017 preprint used for these page numbers can be downloaded from
`https://databookuw.com/databook.pdf` to root `databook.pdf` (checked on 18 October 2026).

Linearizing Around a Fixed Point (playlist item 4, local Whisper transcript because English
captions were unavailable):

```powershell
.\download_study.ps1 -Url 'https://www.youtube.com/watch?v=1YMTkELi3tE' -Slug linearization -BookPages '350,355' -Transcribe
```

These correspond to printed pages 330 and 335. The video includes viscous damping; the book's
pendulum example omits it. The package's source review records the distinction and verified frames.

The script creates `.venv-download`, installs source tools, caches downloads and only transcribes
when captions are unavailable. Whisper downloads its model on first use. Internet access and
video availability are required. Node supports YouTube challenges; a site restriction may still
prevent a download. See [tools/README.md](../tools/README.md) for flags and cache behavior.

## Author or render

Create a new environment on this computer; do not copy another computer's `.venv` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r courses\controls\linear-systems\requirements-render.txt
.\.venv\Scripts\python.exe courses\controls\linear-systems\course_source.py
.\.venv\Scripts\python.exe courses\controls\linear-systems\animation\build_sequences.py --jobs 2
```

The pinned requirements record the versions used for delivery. Rendering needs an OpenGL-capable
environment; FFmpeg is supplied through imageio-ffmpeg. The overview/Linear Systems render helpers
do not require LaTeX. The original ODE/native render path has its own
[setup notes](../courses/ode/README.md#setup-for-the-native-guide-rendering-and-qa).
Pre-rendered `dist/` assets already work without installing render dependencies.

For a new lecture, use `/build-study-package` in Claude Code and the scaffold workflow in
[tools/README.md](../tools/README.md). New course content/scenes still need authoring and review.
Use `--only <sequence-id>` when rerendering a targeted fix. Master renders are ignored;
`--no-render` cannot rebuild from a fresh checkout without masters.

## Claude and the optional GPT panel

Install/sign in to Claude Code on this computer, then start it at the repository root. It reads
`CLAUDE.md`; the checked-in project skill is `.claude/skills/build-study-package/SKILL.md`.
You can invoke `/build-study-package` directly. Your account, credentials, local session logs
and personal skills do not transfer through Git.

The optional external handoff runner finds Claude on PATH or in a VS Code extension. It defaults
to `claude-opus-5-5` with medium effort; choose a model available on your account with `--model`.
Its Git Bash paths assume the usual Windows Git installation. It uses safe mode, so a handoff
brief should explicitly request reading `CLAUDE.md` and the skill file rather than relying on
automatic project-skill loading. Do not start this runner recursively from inside Claude just
to use the project skill.

The browser's **Ask GPT** panel is separate from Claude Code. It is optional: configure
`OPENAI_API_KEY` locally before launching if you want live chat. `OPENAI_MODEL` optionally changes
its model (current backend default: `gpt-5-mini`). Keys and `.env` files stay out of Git. No live
paid chat calls were part of delivery verification.

## Verify your setup

Install browser-check tooling once (Node.js/npm required):

```powershell
npm --prefix qa/tooling ci
```

The supplied tests use installed Chrome, not a downloaded Playwright browser. Set `CHROME_PATH`
if Chrome is elsewhere. With the render environment installed:

```powershell
.\.venv\Scripts\python.exe -m unittest qa.test_study_tools
.\.venv\Scripts\python.exe qa\linear_systems_qa.py
node qa\linear_systems_browser_qa.js
node qa\linear_explorer_regression.js
.\.venv\Scripts\python.exe tools\check_study.py --package linear-systems --decode
.\.venv\Scripts\python.exe qa\stability_qa.py
node qa\stability_explorer_regression.js
node qa\stability_browser_qa.js
.\.venv\Scripts\python.exe tools\check_study.py --package stability-eigenvalues --decode
.\.venv\Scripts\python.exe qa\linearization_math_qa.py
.\.venv\Scripts\python.exe qa\linearization_qa.py
node qa\linearization_browser_qa.js
.\.venv\Scripts\python.exe tools\check_study.py --package linearization --decode
.\.venv\Scripts\python.exe qa\repo_layout_qa.py
node --test site/test/build.test.mjs
node site/build.mjs; node qa\site_browser_qa.js
```

Render Stability and Eigenvalues and Linearization sequentially (`--jobs 1`, their default); parallel ManimGL renders
were seen to collide on shared temporary text SVG files.

The QA scripts strip OpenAI variables from their test servers and avoid paid tutor calls. The
book-range check runs only when a local PDF exists. Logs/results/screenshots are ignored and
regenerated locally. See individual package READMEs for additional checks.

Git carries code, instructions, dependency manifests and rendered viewing assets. It does not
carry installed Python/Node environments, source downloads, raw logs, browser progress or sign-ins.
The generated `site/dist` is ignored; rebuild it (Netlify does so on each deploy).
