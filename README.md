# Cikgu

An animation-first mathematics study library. Open **all courses in one browser**:

```powershell
.\launch_study.ps1
```

The homepage offers ODE and Control Bootcamp. Node.js builds the site; standard-library Python
serves it locally. Netlify builds the same website from `netlify.toml`.
See [website and publishing instructions](site/README.md).

## Course folders

```text
courses/
  controls/
    overview/
    linear-systems/
    stability-eigenvalues/
    linearization/
    controllability/
  ode/
    animation/
    browser/
    native/
    course.json
```

- [Control Bootcamp](courses/controls/README.md): five ordered lecture packages with their own
  course data, animations, explorer, quiz, server and maintenance notes.
- [Second-Order ODEs](courses/ode/README.md): browser/native guides and their shared course source.

Shared infrastructure stays at the root: `site/` (website), `tools/` (authoring), `qa/` (checks),
`docs/` and root launchers. Environments, source downloads and the optional `databook.pdf` stay
outside Git. Future subjects belong under `courses/<subject>/`.

## Launchers

| Guide | Command | Default port |
|---|---|---|
| ODE browser | `.\launch_browser.ps1` | 8765 |
| ODE native ManimGL | `.\launch_native.ps1` | Native window |
| Control overview | `.\launch_control.ps1` | 8770 |
| Linear Systems | `.\launch_linear_systems.ps1` | 8780 |
| Stability and Eigenvalues | `.\launch_stability_eigenvalues.ps1` | 8790 |
| Linearizing Around a Fixed Point | `.\launch_linearization.ps1` | 8810 |
| Controllability | `.\launch_controllability.ps1` | 8820 |
| All courses | `.\launch_study.ps1` | 8800 |

The optional GPT tutor/local PDF routes use the standalone control servers. The combined static
website provides lessons, videos, explorers and quizzes without an API key. Existing website URLs
and browser storage keys are preserved; progress is separate for each website origin.

## Continue development

Read [CLAUDE.md](CLAUDE.md), [the handover](docs/HANDOVER.md) and
[setup instructions](docs/SETUP.md). The repository's `/build-study-package` skill describes
the authoring workflow, with reusable commands in [tools/README.md](tools/README.md).

```powershell
node site/build.mjs
node --test site/test/build.test.mjs
node qa/site_browser_qa.js
.\.venv\Scripts\python.exe -m unittest qa.test_study_tools
.\.venv\Scripts\python.exe qa/repo_layout_qa.py
```

Package-specific checks are documented with each course. Rendered viewing assets are versioned
with their course; master renders and QA output are regenerated locally.
