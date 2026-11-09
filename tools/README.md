# Reusable study-package workflow

## Routed workflow (start here for another lecture)

`study_pipeline.py` selects a subject by a registered playlist ID, then chooses a strategy
from the title. Unknown playlists require an explicit configured subject; generic recipes
still require source review. `tools/study_profiles.json` stores subject/strategy recipes.
The current supported subject profile is Controls; the older ODE package remains separate.

```powershell
.\.venv\Scripts\python.exe tools/study_pipeline.py plan --url 'https://www.youtube.com/watch?v=u5Sv7YKAkt4&list=PLMrJAkhIeNNR20Mz-VpzgfQs5zrYi085m' --slug controllability --title 'Controllability' --port 8820
.\.venv\Scripts\python.exe tools/study_pipeline.py prepare --slug controllability
.\.venv\Scripts\python.exe tools/study_pipeline.py scaffold --slug controllability
# Review transcript/book/frames (optionally via the source-reader agent), write
# sources/controllability/REVIEW.md, author the lesson, then run the Codex plan/maths review.
.\.venv\Scripts\python.exe tools/study_pipeline.py status --slug controllability
```

Each stage is explicit. Planning makes no network/model calls; preparation downloads sources.
Source files and stage checkpoints live under ignored `sources/<slug>/`. Repeated preparation
uses its existing cache; repeated scaffolding preserves authored files. A conflicting video/plan
is rejected. Book-page defaults are candidates and must be checked against the local edition.
No stage calls a model. The lead Claude session authors the lesson between `scaffold` and
`preview`, delegating bounded work to the Sonnet agents in `.claude/agents/`; Codex reviews it
at the checkpoints in `.claude/skills/build-study-package/SKILL.md`. The earlier `brief`/`author`
stages and `tools/run_claude.py` (Codex launching a restricted Claude implementer) were removed
in November 2026; historical package BRIEF files describe that older arrangement.

Preview one sequence, inspect its contact sheet, then render the remainder:

```powershell
.\.venv\Scripts\python.exe tools/study_pipeline.py preview --slug controllability --only compare-ranks
# Inspect qa/screenshots/controllability/preview-compare-ranks.jpg before continuing.
.\.venv\Scripts\python.exe tools/study_pipeline.py render --slug controllability
.\.venv\Scripts\python.exe tools/study_pipeline.py check --slug controllability
node qa/study_browser_qa.js courses/controls/controllability
```

Replace `compare-ranks` with an actual authored sequence ID from `control_specs.py`.
Preview leaves the full manifest alone and its master is reused by the full render.
Use `render --only <id>` for a targeted revision after the full manifest exists.
The shared browser suite checks every animation step, back/replay, quiz, save/restore,
mobile layout, reduced motion and the no-key tutor state. Add focused checks for new math
and explorer semantics instead of copying the entire previous QA suite. Integrate a finished
lesson through `site/catalog.json`, build once, then run the site build/browser checks.
An optional `qa/<slug_with_underscores>_explorer_checks.js` exports an async function receiving
`{page, context, course, check}` for lesson-specific UI assertions. `--explorer-only` runs that
part with the shared responsive checks. It reuses the same server/browser infrastructure.

## Individual tools

Prepare one video from the project root:

```powershell
.\download_study.ps1 -Url 'https://www.youtube.com/watch?v=nyqJJdhReiA&t=1342s' -Slug linear-systems -BookPages '351-352' -Transcribe
```

`BookPages` uses **PDF page numbers**, not the numbers printed on the pages. For the supplied
preprint, PDF pages 351–352 are printed pages 331–332. `-Transcribe` generates local English
captions when YouTube provides none; it downloads Whisper base.en once and runs locally on CPU,
without an API key. Local transcription is explicitly labelled in `source.json`.

Downloads, captions, compact 30-second transcript segments, selected PDF text and review frames
are cached in `sources/<slug>/` (ignored by Git). A repeated run reuses the existing files and
does not transcribe again. A slug cannot silently reuse another video's download. `-CaptionsOnly`
skips video downloads; `-Refresh` explicitly refreshes downloaded files. On a failed download the
script updates its isolated yt-dlp installation to the latest prerelease and retries once.
Python is required; Node.js supports YouTube's JavaScript challenges. Tools are installed into
`.venv-download`, separate from rendering dependencies. A site restriction can still prevent a
download; the script reports it rather than claiming success.

Create a **new** package from the existing, tested overview framework:

```powershell
python tools/scaffold_study.py --slug another-lecture --title 'Another Lecture' --port 8790
```

The default target is `courses/controls/another-lecture/`; `--subject` selects another subject
folder. This copies the player, theme, local KaTeX assets, quiz and notes UI, optional GPT backend,
ManimGL helpers and renderer. It does **not** copy the overview's course content or animation
media. It refuses to overwrite an existing package or launcher. Each package receives a distinct
server identity and progress-storage key. Rendering uses the existing root `.venv` environment;
viewing needs only standard-library Python.

The author supplies these files:

- `dist/course.json`: the same schema as `courses/controls/overview/dist/course.json`, with new sections, original
  notes/examples, source times/pages, quiz questions, and an `explorer` object. The navigation
  supports arbitrary section counts. Keep source IDs `s1`, `s2`, etc. and consecutive numbers.
- `animation/control_specs.py`: `RELATIONS`, `SEQUENCES`, `SECTION_SEQUENCES`, using the existing
  metadata schema. `ControlScene` loads these specs and records stable-state frame boundaries.
- `animation/sequence_scenes.py`: authored ManimGL diagram and token transformations. Reuse
  `ctl_common.py` (`Mx`, `Mat`, `ControlScene`, `start`, `step_done`, `tmorph`).
- `dist/study_math.js`: dependency-free mathematics, exportable in Node for numerical checks.
- `dist/explorer.js`: `window.StudyExplorer` with `restore(saved, config)`, `stop()`, and
  `render(api)` methods. `api` supplies `root`, `course`, `state`, `save`, `html`, `svg`,
  `mathText`, `displayMath`, `flowMath`, `announce`, and `panel`. Save validated values in
  `state.explorer`. Put an accurate tutor summary in `course.explorer.tutorContext`.

Render with:

```powershell
.\.venv\Scripts\python.exe courses\controls\another-lecture\animation\build_sequences.py --jobs 2
```

Use `--only sequence-id` for a targeted revision, or `--no-render` to update text metadata from
existing masters. Prefer `--jobs 1` if scenes share text labels: parallel ManimGL processes were seen
to race on the same temporary SVG file (Stability and Eigenvalues defaults to one job). To check that
a scene runs without rendering video, use `manimgl sequence_scenes.py <Scene> -w -s` from the
package's `animation` folder; `-s` without `-w` opens an interactive window that does not exit.
The scaffold uses the corrected Linearization renderer (input-stream codec/size probe, one render
process by default). Run package-specific math, media and browser checks before handing it over.
The generated launcher is `launch_another_lecture.ps1`.

The reusable audit checks section routes, quiz explanations, referenced media and decoded frame
counts, with compact output:

```powershell
.\.venv\Scripts\python.exe tools\check_study.py --package another-lecture --decode
```

A slug resolves within `courses/controls/`. For another subject, pass its full repository-relative
path, for example `--package courses/algebra/another-lecture`.

Savings come from cached sources, removing duplicate rolling captions, selecting only relevant
book pages/frames, reusing tested application code, and delegating long mechanical work (source
maps, renders, browser QA) to Sonnet agents instead of filling the lead session's context.
No fixed token saving is guaranteed.
