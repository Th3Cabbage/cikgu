# Second-Order Linear Differential Equations

Browser and native versions of the ODE course. Run the commands below from the repository root.
The source course is `courses/ode/course.json`; both delivery versions are kept together here.

## What's in the course

Six lessons, nine animated derivations (63 steps) and an 11-question quiz:

1. **Order and linearity.** `a(t)y'' + b(t)y' + c(t)y = g(t)` with `a(t) ≠ 0`, the normalized
   form, homogeneous vs nonhomogeneous, superposition, two initial conditions.
2. **Constant-coefficient homogeneous equations.** The guess `e^(rt)` gives the characteristic
   equation; distinct, repeated (`t e^(rt)`) and complex roots.
3. **Worked initial value problems:** `y''-3y'+2y=0 → 2e^t - e^(2t)`,
   `y''+2y'+y=0 → (1+t)e^(-t)` and `y''+2y'+5y=0 → e^(-t)(cos 2t + ½ sin 2t)`, all with
   `y(0)=1`, `y'(0)=0`.
4. **Nonhomogeneous equations.** `y = yc + yp`, undetermined coefficients, overlap and the
   `t^s` rule, and resonance in `y''+y=sin t → yp = -(t/2)cos t`.
5. **Springs, dampers and damping.** Underdamped, critically damped and overdamped motion, and
   the undamped case `b = 0` on its own.
6. **Scope and next steps.** The characteristic polynomial needs constant coefficients; a
   Cauchy-Euler example `t²y''+3ty'+y=0 → (C1 + C2 ln t)/t`; a variation-of-parameters reference.

Every quiz choice has an explanation. A wrong answer can be retried, and the score counts first
tries only. Further reading points to two MIT OpenCourseWare 18.03 resources.

**Explorer scope.** The live explorer covers only the constant-coefficient homogeneous
mass-spring model `a y'' + b y' + c y = 0` with `a > 0`, `c > 0`, `b ≥ 0`: sliders for
a ∈ [0.5, 3], b ∈ [0, 8], c ∈ [0.5, 9], y0 ∈ [-3, 3] and v0 ∈ [-3, 3], plotted over 0 ≤ t ≤ 8,
with roots and classification. Presets Undamped (1, 0, 4), Underdamped (1, 2, 4), Critical
(1, 4, 4) and Overdamped (1, 5, 4) change a, b, c only and keep y0, v0; Reset restores all five
defaults (1, 2, 4, 1, 0).

## Browser guide

### Run it locally

Viewing needs only Python 3.7+ (standard library) to serve the files; no ManimGL install is
required.

```powershell
.\launch_browser.ps1              # serves on http://127.0.0.1:8765/ and opens your browser
.\launch_browser.ps1 -Port 9000   # pick another starting port
.\launch_browser.ps1 -NoBrowser   # just serve and print the URL
```

- The server ([`courses/ode/browser/serve_local.py`](browser/serve_local.py)) binds **127.0.0.1 only**. If
  the port is busy it moves to the next free one and prints the URL it used. Before opening the
  page, the launcher confirms through `/__guide_health` and a per-launch nonce that the server
  answering is the one it started.
- Stop it with Ctrl+C or by closing the window.
- The launcher uses `.venv\Scripts\python.exe` if present, then `..\ManimGL\.venv`, then
  `python` from PATH.
- Without PowerShell, run the server directly: `python courses/ode/browser/serve_local.py --port 8765`.
  It adds explicit MIME types and byte-range support for the MP4 clips; a generic static server
  also works if it serves those correctly.
- Opening `index.html` straight from disk won't work: browsers block the `course.json` request
  from `file://` pages.

`courses/ode/browser/dist` is a self-contained static site and can be hosted as-is.

### How it works

The start page, **Animated derivations** (`#watch`), opens with the characteristic-equation
derivation on a large dark stage. Each lesson page (`#lesson-1` … `#lesson-6`) opens with its
derivation on the same stage, followed by the **lesson notes** from `course.json`; every worked
example appears as a written solution with an **Animate this example** button. The sidebar (a
**Chapters** button on phones) also leads to the live explorer, the quiz and further reading.

- **Authored, pre-rendered transitions.** Each derivation was written as a ManimGL scene and
  rendered to one master video, then cut at exact frame boundaries into one short H.264 clip per
  step (1.5–4.8 s) plus a still of every stable state. Clip *k* starts on the previous state's
  final frame, so playback never jumps.
- **Next step** plays exactly one equation transformation and stops on the result. **Back** and
  **Restart** jump to earlier states without animating; **Replay** plays the current step again.
  The panel beside the stage shows the step title, how the new line relates to the previous one
  (substitution, identity, equivalent equation, consequence, ...), the equation typeset with
  KaTeX and a short explanation. "All steps so far" gives the whole derivation as text.
- On the last step the stage shows **Derivation complete** and Next becomes **Next derivation**
  (the last one leads to the quiz).
- Keys: **→** or **N** next step, **←** or **B** back, **R** replay (ignored while typing or
  with Alt/Ctrl/Cmd held). In the explorer the arrow keys move the focused slider; in the quiz
  **A–D** answer.
- The nine derivations: normalized form and superposition (Lesson 1), the characteristic
  equation (2), the three worked IVPs (3), exponential forcing and resonance (4), damping regimes
  (5) and the Cauchy-Euler example (6). Addresses such as `#lesson-3/ivp-complex` or
  `#watch/resonance` open a specific one.
- **Light and dark themes.** The **Dark theme** switch in the top bar toggles the whole UI (the
  animation canvas stays near-black in both, like a video). With no saved choice the guide
  follows the system setting; the choice is saved in `localStorage` and applied before first
  paint, and still works for the visit if storage is blocked.
- With **reduced motion** set in the OS, Next shows each step's result immediately and Replay
  still plays the animation on request. If a clip cannot load, the step's still and text are
  shown; if a still cannot load, the equation is typeset on the stage. A full-screen button
  enlarges the stage.
- Three original continuous ManimGL overview clips (characteristic equation, three root cases,
  resonance) remain in the lesson notes, collapsed.

## Native ManimGL guide

```powershell
.\launch_native.ps1               # opens a 1280x720 ManimGL window
.\launch_native.ps1 -CheckOnly    # verify venv, files, LaTeX and window config; open nothing
```

The launcher uses this checkout's `.venv` (or, if absent, a sibling `..\ManimGL\.venv`),
re-reads the Machine and User PATH for this process only so MiKTeX is found, and runs from the
repository root:

```powershell
.\.venv\Scripts\manimgl.exe courses\ode\native\study_guide.py SecondOrderStudyGuide --config_file courses\ode\native\guide_config.yml
```

The first visit to each lesson page compiles its LaTeX (a few seconds); later visits use
ManimGL's cache.

| Control | Action |
|---|---|
| Tabs **Lessons / Explorer / Quiz / Help**, or keys **1 / 2 / 3 / H** | Switch view or show help |
| A lesson in the sidebar, **Prev / Next**, or **Left / Right** | Move between pages (Up/Down: previous/next lesson) |
| **Next step** button, Space or Enter | Reveal the next worked-example step (**R** or **Hide steps** hides them) |
| Drag a slider knob or click its track | Change a, b, c, y0 or v0 |
| Explorer: Up/Down, then Left/Right (Shift for x10) | Select a slider, then nudge it |
| Explorer: preset buttons, **P**, **Reset (R)**, **Play marker (Space)** | Presets, reset, time marker |
| Quiz: click an answer or **A–D**; **Try again (R)**, **Next/Prev**, **Reset quiz** | Answer, retry, move |
| **Q** or **Esc** | Close the window |

### Browser vs native

| | Browser guide | Native guide |
|---|---|---|
| Lessons, worked examples, explorer, quiz | Yes (from `course.json`) | Yes (from `course.json`) |
| Animated step-by-step derivation stage | Yes: nine pre-rendered derivations | No; worked-example steps are revealed one at a time |
| Overview clips | Yes, in the lesson notes | No (they are rendered from `courses/ode/native/explanation_scenes.py`) |
| Themes | Light and dark | One paper-coloured theme |
| Math rendering | KaTeX in the page | LaTeX via ManimGL, compiled on first visit |
| Requirements | A local static server | Python 3.12 venv with ManimGL, MiKTeX, OpenGL window |

## Setup (for the native guide, rendering and QA)

Tested on Windows 11 with Python 3.12, ManimGL 1.7.2, MiKTeX and FFmpeg. The render and
launcher scripts are Windows-specific (PowerShell, `.venv\Scripts\*.exe`, PATH from the Windows
registry); the browser guide itself runs anywhere.

Prerequisites, installed separately: **Python 3.12**, **FFmpeg** (`ffmpeg`/`ffprobe` on PATH),
**MiKTeX** (or another LaTeX with `latex` and `dvisvgm` on PATH) and, for the browser QA,
**Node.js 20+** and Google Chrome.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r courses/ode/requirements.txt
.\.venv\Scripts\python.exe courses\ode\fix_manim_miktex.py
```

`setuptools<81` is pinned because ManimGL 1.7.2 imports `pkg_resources`.
[`fix_manim_miktex.py`](fix_manim_miktex.py) makes ManimGL 1.7.2 work with MiKTeX's `latex`
(it passes the xelatex-only `-no-pdf` option to every compiler). It edits only
`.venv\Lib\site-packages\manimlib\utils\tex_file_writing.py` in this repository's `.venv`, keeps
the original in `backup\`, is idempotent, and refuses to touch files outside that `.venv`.
Re-run it after reinstalling ManimGL.

## Re-render the animated derivations

Source is in [`courses/ode/animation/`](animation): `sequence_specs.py` holds each step's title, relation,
equation and explanation; `sequence_scenes.py` holds one ManimGL scene per derivation;
`render_config.yml` sets 1280x720, 60 fps and the dark canvas.

```powershell
.\.venv\Scripts\python.exe courses\ode\animation\build_sequences.py               # render changed scenes, cut clips, write manifest
.\.venv\Scripts\python.exe courses\ode\animation\build_sequences.py --force       # re-render all nine masters
.\.venv\Scripts\python.exe courses\ode\animation\build_sequences.py --only resonance damping
.\.venv\Scripts\python.exe courses\ode\animation\build_sequences.py --no-render   # re-cut existing masters only
```

The script renders each scene offscreen into `courses/ode/animation/masters` (not versioned; a fresh
checkout therefore renders everything on the first run), records the frame where every step
ends, cuts one clip per step, extracts the stable-state stills from the clips and writes
`courses/ode/browser/dist/animations/manifest.json`. A stamp file skips scenes whose visual source is
unchanged, so after a text-only edit to `sequence_specs.py` run `--no-render` (once masters
exist).

## Re-render the overview clips

From the repository root with MiKTeX on PATH (renders offscreen, opens no window):

```powershell
foreach ($s in 'CharacteristicEquation','ThreeRootCases','Resonance') {
  .\.venv\Scripts\manimgl.exe courses\ode\native\explanation_scenes.py $s -w -m --video_dir media
}
Copy-Item media\*.mp4 courses\ode\browser\dist\media\
```

Refresh a poster frame with `ffmpeg -sseof -0.6 -i X.mp4 -frames:v 1 -q:v 4 X.jpg` and copy it
into `courses\ode\browser\dist\media`. The `media\` folder is a local scratch output and is not versioned.

## Run the checks

From the repository root. The browser checks use `playwright-core` with the installed Chrome
(no browser download); set `CHROME_PATH` if Chrome is not in the default location.

```powershell
cd qa\tooling; npm ci; cd ..\..                            # once: installs playwright-core

.\.venv\Scripts\python.exe qa\test_math.py                 # Python and JS solvers vs numeric ODE solutions
.\.venv\Scripts\python.exe qa\media_qa.py                  # clips: codec, frames, boundaries, motion, stills
node qa\stage_qa.js                                        # stage playback, fallbacks, themes, mobile (~1.5 min)
node qa\browser_qa.js                                      # notes, explorer, quiz, mobile layout
.\qa\launcher_qa.ps1                                       # browser launcher: busy port, loopback, stop
.\.venv\Scripts\python.exe qa\native_qa.py                 # native guide offscreen (MiKTeX on PATH)
```

Targeted checks for Lessons 2, 5 and 6: `node qa\review_affected_browser.js` and
`.\.venv\Scripts\python.exe qa\review_affected_native.py`.

Results, screenshots and contact sheets go to `qa\results`, `qa\screenshots` and `qa\scratch`,
which are not versioned. After editing `courses/ode/course.json`, copy it to `courses\ode\browser\dist\course.json`;
the browser QA checks that the two are identical.

**Solver note.** When |b² − 4ac| is within a relative 1e-9 of max(b², |4ac|), both solvers treat
the roots as repeated and use e^(αt)(y0 + kt) for the curve as well as the label. This is a
deliberate, tiny approximation: across the explorer ranges the worst case is about 3e-9 absolute.

## Layout

| Path | Contents |
|---|---|
| `courses/ode/course.json` | Shared lessons, examples, quiz and explorer settings |
| `courses/ode/browser/dist/` | The static site: `index.html`, `styles.css`, `app.js`, `ode_math.js`, a copy of `course.json`, `vendor/katex/` (KaTeX 0.19.0 with fonts and its MIT license), `animations/` (`manifest.json`, one folder per derivation with `step-NN.mp4` clips and `state-NN.jpg` stills) and `media/` (the three overview clips and posters) |
| `courses/ode/browser/serve_local.py` | Loopback-only static server used by the launcher (not part of the site) |
| `courses/ode/animation/` | Derivation scenes, step text, render config and `build_sequences.py` |
| `courses/ode/native/` | `study_guide.py` (`SecondOrderStudyGuide`), `ode_math.py` (standard-library solver), `explanation_scenes.py` (overview clips), `guide_config.yml` |
| `launch_browser.ps1`, `launch_native.ps1` | Launchers |
| `site/`, `launch_study.ps1`, `netlify.toml` | Unified study site: registry, build, local server and Netlify settings (output `site/dist` is generated and ignored) |
| `qa/` | Check scripts; `tooling/` holds the `package.json`/lockfile for `playwright-core` |
| `courses/ode/requirements.txt`, `courses/ode/fix_manim_miktex.py` | ManimGL environment setup |

## Licenses

No license has been chosen for this project's own code and content. Bundled third-party files
keep their own licenses: KaTeX (MIT, `courses/ode/browser/dist/vendor/katex/LICENSE`).
