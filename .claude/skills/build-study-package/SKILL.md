---
name: build-study-package
description: Build or extend a Cikgu browser study package from a lecture and optional book, reusing the source scripts, ManimGL step animations, explorer, quiz and validation workflow. Use for lecture-package authoring or substantial revisions.
---

# Build a Cikgu study package

Read `CLAUDE.md` and `docs/HANDOVER.md` for the project map. For installation or missing local
sources, read `docs/SETUP.md`. For script arguments and the course/explorer contract, read
`tools/README.md`. Paths below are relative to the repository root.

## Team and review checkpoints

You (the lead Claude session) are the architect and own the whole workflow. Keep the plan, the
mathematical core, animation design, notes, worked examples, quiz content, integration and
commits yourself. Delegate only bounded, long or mechanical work to the Sonnet agents in
`.claude/agents/`, each with an exact file list:

- `source-reader`: a topic map of `sources/<slug>/` before you plan (read-only).
- `package-builder`: explorer UI wiring, scaffolding, QA scripts/fixtures, catalog entry, docs.
- `render-qa`: renders, `check_study`, contact sheets and browser suites; simple layout fixes.

Do not let two agents edit the same file; give parallel coding tasks separate worktrees. Read
every agent change before it stays in the branch. Agent reports are checks, not reviews.

Codex is the only reviewer (Claude Code Codex plugin; model and effort in `.codex/config.toml`).
Two reviews are required for a new package or substantial revision:

1. **Plan and mathematics**, before animations and the explorer are built: an adversarial
   review focused on source coverage, timestamps, derivations, worked examples, `study_math.js`
   and `qa_cases.json`.
2. **Before committing**: run the package math checks and `check_study`, then a standard review
   of the full diff (code, explorer edge cases, quiz answers, docs, site integration).

Start both reviews yourself; do not wait for the user to type a slash command. The plugin's
slash commands cannot be invoked by Claude, but they only run its companion script, which you
run with Bash (Git Bash) in the background and read when it finishes:

```bash
CX=$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/ | sort -V | tail -1)
node "$CX/scripts/codex-companion.mjs" adversarial-review --wait "<focus text>"   # checkpoint 1
node "$CX/scripts/codex-companion.mjs" review --wait                              # checkpoint 2
```

Every argument after the flags becomes focus text (even `--help`), and each run uses Codex
usage, so run only the reviews you intend. Reviews cover the working-tree diff by default; add
`--base <ref>` for committed branch work. Untracked files are included. Report the verdict and
findings to the user.

The user may ask for more reviews at any time. Fix or explicitly answer every finding, and record
the findings and resolutions in the package `REVIEW.md`. If Codex is unavailable (not installed,
not signed in or out of usage), continue, write "Codex review pending" with the missed
checkpoint in `REVIEW.md`, tell the user, and run the review when Codex is available.

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
It creates `courses/controls/<slug>/` by default; use `--subject <subject>` for another subject.
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
- Add the finished lecture to the unified site: append it to `site/catalog.json` (slug, source,
  title, short description, `storeKey`, `statusApp`), then run `node site/build.mjs`,
  `node --test site/test/build.test.mjs` and `node qa/site_browser_qa.js`. See `site/README.md`.
- Update package README/review and the handover with commands, actual checks and limitations.
  Give the user the launcher command. Commit or push only when requested, and only after the
  pre-commit Codex review or a recorded "Codex review pending".
