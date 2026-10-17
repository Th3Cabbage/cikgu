# Reusable study-package workflow

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

This copies the player, theme, local KaTeX assets, quiz and notes UI, optional GPT backend,
ManimGL helpers and renderer. It does **not** copy the overview's course content or animation
media. It refuses to overwrite an existing package or launcher. Each package receives a distinct
server identity and progress-storage key. Rendering uses the existing root `.venv` environment;
viewing needs only standard-library Python.

The author supplies these files:

- `dist/course.json`: the same schema as `control/dist/course.json`, with new sections, original
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
.\.venv\Scripts\python.exe another-lecture\animation\build_sequences.py --jobs 2
```

Use `--only sequence-id` for a targeted revision, or `--no-render` to update text metadata from
existing masters. Run package-specific math, media and browser checks before handing it over.
The generated launcher is `launch_another_lecture.ps1`.

The reusable audit checks section routes, quiz explanations, referenced media and decoded frame
counts, with compact output:

```powershell
.\.venv\Scripts\python.exe tools\check_study.py --package another-lecture --decode
```

Hand a focused implementation brief to Claude:

```powershell
.\.venv\Scripts\python.exe tools\run_claude.py another-lecture\BRIEF.md --name another-lecture
.\.venv\Scripts\python.exe tools\run_claude.py --status another-lecture
```

The runner finds Claude Code in PATH or the VS Code extension, uses the selected Opus 5.5 model
with medium effort, and retains resumable session IDs and raw logs in ignored `qa/scratch/`.
It prints brief progress instead of large tool results. It uses your existing Claude sign-in;
it does not read or print credentials. For a focused revision use a new task name and
`--resume <session_id>`. Model and effort can be overridden explicitly. Claude still needs
source review and independent checks; the scaffold is automation for repeated implementation work.

Savings come from cached sources, removing duplicate rolling captions, selecting only relevant
book pages/frames, reusing tested application code, and giving Claude a fresh, bounded brief
instead of replaying the entire previous implementation conversation. No fixed token saving is
guaranteed; model usage is recorded in each task's local summary JSON.
