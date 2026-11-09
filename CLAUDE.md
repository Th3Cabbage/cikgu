# Cikgu: start here

This repository contains six mathematics study packages. Read
[docs/HANDOVER.md](docs/HANDOVER.md) for their architecture, completed work and limitations;
read [docs/SETUP.md](docs/SETUP.md) when using a new computer.

For a new lecture or substantial study-package work, use the repository skill
`.claude/skills/build-study-package/SKILL.md` (`/build-study-package` in Claude Code).
The deterministic source/scaffold/render/check commands are in [tools/README.md](tools/README.md).
For new Controls lectures, `tools/study_pipeline.py` routes the playlist to a recipe and runs the
deterministic prepare/scaffold/preview/render/check stages with checkpoints. See the routed
workflow at the start of tools/README.md. Load detailed references only when needed.

## Team roles (from November 2026)

- **Claude Opus (the lead session) is the architect.** It plans, reviews sources, writes the
  mathematical core, animation design, notes, examples and quiz, integrates all changes and
  commits when asked.
- **Sonnet subagents** in `.claude/agents/` do bounded work the architect assigns with an exact
  file list: `package-builder` (coding), `render-qa` (renders and QA, simple layout fixes) and
  `source-reader` (read-only source maps). They report; the architect reads every change.
- **Codex is the only reviewer**, through the Claude Code Codex plugin (`gpt-6.1-sol`, medium
  effort, set in `.codex/config.toml`). It reviews code and mathematics but does not write the
  packages. Required checkpoints are in the skill. If Codex is unavailable, finish the work, mark
  the package "Codex review pending" in its `REVIEW.md`, and run the review later.
- Tests and QA scripts are checks, not reviews; anyone may run them. Do not launch Claude
  recursively from inside a Claude session. Packages built before November 2026 used the old
  arrangement (Codex planned, Claude implemented); their BRIEF/REVIEW files are historical.

Course sources are grouped by subject: `courses/controls/{overview,linear-systems,stability-eigenvalues,linearization,controllability}`
and `courses/ode/` (browser, native, animation and course.json). Shared tools, tests, environments
and root launcher commands stay at the repository root. See `courses/README.md` for the map.

## Project conventions

- The preferred experience is the browser guide with step-controlled, pre-rendered **ManimGL**
  derivations, original notes/examples, source references, an interactive explorer and an
  explanatory quiz. Preserve existing packages when adding another lecture.
- Show the mathematical operation in each animation: substitutions, matched terms, matrix
  multiplication or diagram changes. Whole-slide fades alone do not teach a derivation.
- Review actual lecture coverage and book pages before authoring. Cross-check ASR mathematics
  against frames/book; label companion examples as authored. Do not invent source timestamps.
- Reuse the player, optional tutor backend and render helpers. Validate mathematics independently
  and inspect rendered/browser output, in addition to automated checks.
- The optional GPT tutor must work gracefully without a key. Configure secrets locally; do not
  put keys, account credentials or machine-specific environments in Git.
- Windows/PowerShell is the tested development environment. Use repository-relative paths;
  recreate `.venv` and `.venv-download` on each machine. Viewing needs no ManimGL installation.

## Launch commands (repository root)

| Package | Command | Default port |
|---|---|---|
| Original ODE browser guide | `.\launch_browser.ps1` | 8765 |
| Control Bootcamp overview | `.\launch_control.ps1` | 8770 |
| Linear Systems | `.\launch_linear_systems.ps1` | 8780 |
| Stability and Eigenvalues | `.\launch_stability_eigenvalues.ps1` | 8790 |
| Linearizing Around a Fixed Point | `.\launch_linearization.ps1` | 8810 |
| Controllability | `.\launch_controllability.ps1` | 8820 |
| Unified study site (all courses; Netlify build) | `.\launch_study.ps1` | 8800 |

Model availability depends on the accounts on this computer; see setup docs.

The unified site (`site/`, see [site/README.md](site/README.md)) copies each package `dist/` and adds
shared navigation at build time; do not edit package apps for site integration. A finished lecture is
added to the site through `site/catalog.json`. `site/dist` is generated and ignored.

Update the handover and package documentation when architecture, commands or limitations change.
Report checks actually run; historical results do not prove a new environment works.
