# Cikgu: start here

This repository contains three working mathematics study packages. Read
[docs/HANDOVER.md](docs/HANDOVER.md) for their architecture, completed work and limitations;
read [docs/SETUP.md](docs/SETUP.md) when using a new computer.

For a new lecture or substantial study-package work, use the repository skill
`.claude/skills/build-study-package/SKILL.md` (`/build-study-package` in Claude Code).
The deterministic source/scaffold/render/check commands are in [tools/README.md](tools/README.md).
Load detailed references only when needed.

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

The new-package skill works with Claude alone. Codex can also plan/review when requested;
do not recursively launch Claude from inside a Claude session just to follow the skill.
Model choice is configurable and depends on the account on this computer; see setup docs.

Update the handover and package documentation when architecture, commands or limitations change.
Report checks actually run; historical results do not prove a new environment works.
