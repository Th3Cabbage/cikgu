# Control Bootcamp: overview companion

A local, browser-only study companion to Steve Brunton's **Control Bootcamp overview** lecture
([YouTube Pi7l8mMjYVE](https://www.youtube.com/watch?v=Pi7l8mMjYVE), 19:31) and Section 8.1 of
Brunton & Kutz, *Data-Driven Science and Engineering* (2017 preprint, Chapter 8, printed pp. 323–331).
It sits next to the existing second-order ODE guide in this repository and does not change it.

The workspace has section navigation on the left, a dark animation stage with a step card in the
middle, lesson notes, a worked example and sources below, and an optional GPT tutor ("Ask GPT") on the right. The
calm light theme is the default; a dark theme is one click away. There is no splash screen.

## Run it

```powershell
.\launch_control.ps1              # serves on http://127.0.0.1:8770/ (or the next free port) and opens the browser
.\launch_control.ps1 -Port 9100   # pick another starting port
.\launch_control.ps1 -NoBrowser   # serve only and print the URL
```

Viewing needs only Python 3 and its standard library. The launcher uses the repository's `.venv`
Python if it exists, and otherwise `python` on PATH. It binds 127.0.0.1 only, skips busy ports,
confirms through `/__control_health` and a random nonce that the server answering is the one it
started, and stops that server on Ctrl+C. The server is also given the launcher's process ID
(`--watch-pid`) and exits by itself if the launcher window is killed.

## What is in it

| Section | Lecture | Animated steps |
|---|---|---|
| 1. From prediction to action: state, input, output, goal; refresher on matrix products | 00:00–03:00 | `state-io` (5) |
| 2. Types of control: passive/active, open/closed loop, feedback diagram built piece by piece | 03:00–08:10 | `control-types` (5) |
| 3. Why feedback: uncertainty, instability, disturbances, efficiency, and the fine print; static cruise model | 08:10–12:58 | `why-feedback` (4), `cruise-model` (4) |
| 4. State-space language: ẋ = Ax, e^{At}, + Bu, y = Cx, sizes, pendulum in matrix form | 12:58–15:44 | `state-space` (5) |
| 5. Closing the loop: u = −Kx, substitute, factor on the right, A − BK and stability | 15:44–18:30 | `close-loop` (5) |
| 6. Make it concrete: BK, A − BK, λ² + 4λ + 3, eigenvalues ±1 → −1, −3; recap and next steps | 18:30–19:31 + book p. 328 | `pendulum-poles` (6) |

That makes **7 animations with 34 steps**. Each step is a real ManimGL transition (term-by-term
substitutions, factoring, matrix entries flying into place, poles moving, diagrams assembling)
with a stable still before and after. **Next** plays one transition, **Back** jumps to the
previous stable state, **Replay** repeats the step and **Restart** goes back to the start. Keys:
→/N, ←/B, R and F (full screen). With reduced motion, Next jumps straight to the result and
Replay still plays the transition on request. If a clip fails to play, the step's result is
shown with a notice; if a still fails to load, the step's formula is typeset in its place.

The section pages also have lesson notes, goals and key ideas, a worked example revealed step by
step, and sources: lecture timestamps that link to the exact second, and book pages given as both
printed and PDF page numbers.

**Explorer.** There are two explorers:

- **State feedback on the normalized pendulum.** Sliders set k₁ ∈ [0, 10] and k₂ ∈ [−2, 8],
  plus θ(0), θ̇(0) and an optional push. The explorer shows A − BK, the characteristic polynomial,
  the eigenvalues on a complex plane, θ(t), and the effort u(t). It classifies the result as
  asymptotically stable (k₁ > 1 and k₂ > 0), unstable, or one of the boundary cases: k₁ = 1
  (an eigenvalue at 0, which gives a constant offset), k₁ = 1 and k₂ = 0 (a Jordan block, which
  gives linear drift), or k₂ = 0 with k₁ > 1 (an undamped oscillation). The θ plot covers
  |θ| ≤ 0.5 rad, shades the region past 0.3 rad where the small-angle model degrades, and says
  when and where the response leaves the window. The curve is clipped there, never squeezed in.
- **Static cruise-control teaching model.** It plots y = au + d with rolling hills, comparing
  open loop (u = r/aₘ) with closed loop (u = K(r − y)). It is clearly labelled as a static model
  that cannot show instability.

**Quiz.** Ten questions. Every choice has an explanation, a wrong answer can be retried, and the
score counts first tries only. The quiz can be reset.

Progress is kept in `localStorage` under one versioned key: steps, quiz answers, explorer settings
and theme. Everything read back is validated, so corrupt or out-of-range data is ignored. If
storage is blocked, progress lasts for the visit and the sidebar says so.

## The optional GPT tutor (ready to enable; off by default)

The toolbar button is labelled **Ask GPT** and the panel **GPT tutor**. No API key is configured, so the panel says GPT chat is ready to enable but off. Everything else works
without it. To enable it, set the key in the PowerShell window before launching:

```powershell
$env:OPENAI_API_KEY = "sk-..."      # required; read once by the server at start-up
$env:OPENAI_MODEL   = "gpt-5-mini"  # optional; this is the default
.\launch_control.ps1
```

Optional settings (environment variables):

| Variable | Default | Meaning |
|---|---|---|
| `OPENAI_MODEL` | `gpt-5-mini` | any Responses API text model your key can use |
| `OPENAI_MAX_OUTPUT_TOKENS` | `1200` | clamped to 64–8000; reasoning models spend part of it on reasoning |
| `OPENAI_REASONING_EFFORT` | `low` for `gpt-5*`/`o*` models, omitted otherwise | `minimal`/`low`/`medium`/`high`, or `none` to omit |
| `OPENAI_TIMEOUT` | `60` | seconds |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | https only (an `http://127.0.0.1` URL is accepted for local tests) |

How it works: the page sends `POST /api/tutor` with the question, up to 8 recent messages, and the
IDs of the current page, section, animation and step. The server ignores any other fields. It
builds the trusted context itself from `course.json` and the manifest: the section summary, key
ideas, notes, a short book paraphrase, and the current and previous step's formula and
explanation. It then calls `POST {base}/responses` with
`model`, `instructions` (fixed tutor rules plus that context), `input` (bounded history plus the
question), `max_output_tokens`, `store: false`, and `reasoning.effort` where it applies, sending the key as a
Bearer token. The server reads `output[].content[]` items of type `output_text`. It reports
`refusal` items as a refusal, a partial answer with `status: incomplete` as cut short, and an
incomplete reply with no text, an HTTP error (401/403/404/429/5xx), a timeout or a non-JSON body
as a readable error. It never invents a reply. The page renders answers as text: paragraphs and
`- ` bullets as text nodes, with math typeset by KaTeX. Model output is never inserted as HTML.

Safety measures:

- The server binds to loopback only.
- The Host header is checked on every request, to block DNS rebinding.
- Requests to the tutor must come from the same origin: the Origin header must match,
  Sec-Fetch-Site must be `same-origin` if present, and the body must be `application/json`.
- The body is capped at 32 KB and the question at 1500 characters.
- Only one question runs at a time.
- The key is never sent to the page, logged, or echoed back in error messages.
- The page cannot supply instructions.

Questions and the guide's notes go to OpenAI only when the user asks something.

The default `gpt-5-mini` is a current Responses API model as far as I know. If your account
does not offer it, the tutor reports a 404 or 403 that tells you to set `OPENAI_MODEL`.

## Files

```
launch_control.ps1            launcher (repository root)
courses/controls/overview/
  server.py                   standard-library server: static root courses/controls/overview/dist, /book, /api/status, /api/tutor
  dist/                       the guide, self-contained, no build step
    index.html  styles.css  app.js  control_math.js  theme-boot.js  favicon.svg  course.json
    animations/manifest.json  animations/<sequence>/step-NN.mp4, state-NN.jpg
    vendor/katex/             KaTeX 0.19.0 (MIT), copied unmodified from courses/ode/browser/dist/vendor/katex
  animation/
    control_specs.py          step titles, relations, formulas, explanations (pure data)
    ctl_common.py             LaTeX-free math typesetting (matplotlib mathtext → SVG → ManimGL), helpers, base scene
    control_scenes.py         the seven ManimGL scenes
    build_control.py          render masters, cut clips at exact frames, extract stills, write the manifest
  requirements-render.txt     render and QA dependencies (pinned, tested)
```

`/book` serves the repository's own `databook.pdf`, if it is present, and nothing else. The PDF is
not copied into `dist`. Section pages link to `book#page=N` when the local copy is available, and
always to the online copy as well. The online copy may be a different revision, so its PDF page
numbers can differ.

## Rebuild the animations

```powershell
.venv\Scripts\python.exe -m pip install -r courses\controls\overview\requirements-render.txt   # once
.venv\Scripts\python.exe courses\controls\overview\animation\build_control.py                  # all; --only ID ..., --force, --no-render, --jobs N
```

The build renders each scene offscreen at 1280×720 and 30 fps into `courses/controls/overview/animation/masters`. It
writes a generated ManimGL config there with `file_writer.ffmpeg_bin` set to imageio-ffmpeg's
bundled FFmpeg. Each scene records the frame at which every step settles; the build cuts clip k from
master frames [b(k−1) − 1, b(k)), so every clip starts on the previous stable frame and ends on the
new one. It then extracts the stills from the clips with the same BT.601 conversion, checks every
clip's decoded frame count, and writes the manifest. Masters are re-rendered only when the scene
code changes, and editing explanation text does not force a re-render. A full build takes about
1 minute on this machine (4 scenes in parallel, about 15 s each).

**Math without LaTeX.** MiKTeX is not installed here, so each formula is written as named tokens,
for example `Mx(XD, "=", "(", "A", "-", "B", "K", ")", "x")`. The whole formula is typeset once by
matplotlib mathtext (Computer Modern), and its glyphs are then split back into one group per
token, with each token's glyph count measured separately. A mismatch raises an error instead of
mis-grouping. A marker added to every SVG records the baseline, so formulas, hand-built fractions
and matrices (individual entries plus drawn brackets) line up. Transforms then move the identity
of each term: `TransformFromCopy` for substitutions, `ReplacementTransform` for rewrites and
factoring.

## Checks

```powershell
.venv\Scripts\python.exe qa\control_math_qa.py      # SciPy/NumPy reference for the math and the explorer (26 checks)
.venv\Scripts\python.exe qa\control_media_qa.py     # clips, frame boundaries, stills, manifest vs specs, dist audit (15)
.venv\Scripts\python.exe qa\control_server_qa.py    # static root, /book, range parsing, guards, tutor: missing key + MOCKED API (76)
node qa\control_browser_qa.js                       # headless Chrome end to end, desktop + mobile (79)
powershell -NoProfile -ExecutionPolicy Bypass -File qa\control_launcher_qa.ps1   # launcher (12)
.venv\Scripts\python.exe qa\control_contact_sheet.py # optional: tile all stills for visual review
```

All of these checks passed when this guide was built (see `qa/results/control_*.json`). The tutor
checks use a **local mock** of the Responses API. **No live OpenAI call has been made**, because
no key is configured on this machine. The request and response shapes follow the Responses API as
documented at <https://developers.openai.com/api/docs/guides/text>, but they were written from
the implementer's knowledge of that API; the page itself could not be fetched while building, so
the first real call should be treated as the final check.

## Content notes and caveats

- The text is original paraphrase. The lecture captions, the chapter text and the downloaded
  video stay in `sources/`, which is ignored by Git, and are not in `dist`. The media check fails
  if any 10-word prose run of either source appears in the course data.
- The lecture's claim that open loop cannot change dynamics is qualified: a preplanned additive
  input to a fixed linear model leaves the eigenvalues of A unchanged, and the shaken-base
  (Kapitza) pendulum works through parametric excitation, which is a different model.
- The cruise example is derived independently. The book's p. 328 wording of the y = 2u case
  says 50% open-loop error, but with these definitions that case gives 100%, and the guide notes
  this. Proportional control leaves a steady-state error of (r − d)/(1 + aK).
- The K = [4 4] pendulum example comes from the book (printed p. 328). The lecture itself
  stops at (A − BK)x.
