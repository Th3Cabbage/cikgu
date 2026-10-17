---
name: build-study-package
description: Build or extend a Cikgu browser study package from a lecture and optional book, reusing the source scripts, ManimGL step animations, explorer, quiz and validation workflow. Use for lecture-package authoring or substantial revisions.
---

# Build a Cikgu study package

Read `CLAUDE.md` and `docs/HANDOVER.md` for the project map. For installation or missing local
sources, read `docs/SETUP.md`. For script arguments and the course/explorer contract, read
`tools/README.md`. Paths below are relative to the repository root.

## Establish the lesson

Identify the lecture URL, a unique package slug, and the intended scope. For a timestamped
video link, normally cover the whole lecture and make the linked moment easy to reach unless
the user requests only an excerpt. Inspect actual lecture content before promising topics.

Use `download_study.ps1` to cache metadata, captions/transcription, selected PDF text and sparse
frames under `sources/<slug>/`. PDF page arguments are physical PDF pages, not printed numbers.
Downloads are optional when suitable sources already exist. Local Whisper ASR is not an official
transcript: verify equations and terminology against video frames and the book. If access fails,
state the missing evidence and do independent work rather than repeating failing downloads.

Write a compact package brief with source locations, scope, notation, worked examples, explorer
behavior and checks. Read compact transcripts once and only the relevant book pages/frames.

## Reuse the framework

For a new package, use `tools/scaffold_study.py --slug <slug> --title <title> --port <free-port>`.
It refuses to overwrite an existing package or launcher. For a revision, inspect the existing
package rather than scaffolding over it. Read the helper's `--help` before changing arguments.

The scaffold is a shell, not a finished lesson. Author `dist/course.json` (a small Python source
generator is useful for LaTeX escaping), `animation/control_specs.py`,
`animation/sequence_scenes.py`, `dist/study_math.js` and `dist/explorer.js`. The Linear Systems
package is an example of this contract. Avoid copying its lecture-specific content or equations.
Use unique server identities, progress keys, launcher names and ports, and clear old labels.

Keep notes/examples and animations mathematically consistent. Every quiz option needs an
explanation; allow retries while counting first-try scores. Include meaningful source times/pages.
Use the existing step-aware tutor contract; no key is required for the rest of the guide.

## Animate and explore

Use **ManimGL**, with existing `Mx`, `Mat`, `ControlScene`, token morphs and frame boundaries.
The overview and Linear Systems helpers use mathtext SVGs without requiring LaTeX. Read helper
signatures and a relevant scene excerpt rather than the full previous implementation.

Each step should visibly perform one teachable operation and stop at a readable stable state.
Preserve Next, Back, Replay and Restart. Keep equations, source tags and relation chips inside
the stage and clear of player controls. Render using the package's build script. For observed
defects, rebuild only affected sequence IDs; `--no-render` requires existing master renders.

Give the explorer a small, accurate mathematical model with explicit assumptions, validated
saved settings, immediate slider updates and understandable plots. Keep core math testable
outside the browser. Playback should accumulate elapsed time independently of frame rate and
stop on navigation. Do not claim the explorer covers cases outside its mathematical family.

## Review and deliver

- Compare solver outputs with an independent reference (for example SciPy), including relevant
  edge cases and initial conditions. Check assumptions, signs and matrix order.
- Run `tools/check_study.py --package <slug> --decode` in the render environment. Add focused
  package checks for new mathematics and behavior; reuse reviewed infrastructure.
- Inspect stable-state contact sheets and important transitions. In a real browser, check all
  sequences, notes/examples, quiz scoring/retries, saved progress, source links, desktop/mobile,
  themes/reduced motion and the tutor's missing-key state. Do not call a paid API just for QA.
- Keep rendered `dist` assets in Git so another machine can view without rendering. Keep source
  downloads, environments, master renders, logs and credentials outside the commit. Preserve
  third-party asset licenses. Do not bundle the source textbook or lecture into the web assets.
- Update package README/review and the handover with commands, actual checks and limitations.
  Give the user the launcher command. Commit or push only when requested.

Claude can perform this workflow directly. `tools/run_claude.py` is an optional external handoff
runner for a planner/reviewer; it is not a requirement to start another Claude process. Its
safe-mode session does not automatically load repository customization: the supplied brief must
explicitly tell it to read `CLAUDE.md` and this skill if those instructions are wanted.
