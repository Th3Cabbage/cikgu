# Controllability

Study companion to Steve Brunton's Control Bootcamp lecture
[Controllability](https://www.youtube.com/watch?v=u5Sv7YKAkt4) (32:29) and Brunton & Kutz,
Section 8.3 (printed pp. 336-337 / PDF 356-357, Eqs. 8.26-8.31).
Reviewed source evidence is recorded in [SOURCE_REVIEW.md](SOURCE_REVIEW.md); the local
download/cache lives in ignored `sources/controllability/`.

- `course_source.py` -> `dist/course.json`: 6 sections (0:00-32:29), worked examples, 10-question quiz,
  explorer config. Regenerate with `.\.venv\Scripts\python.exe courses\controls\controllability\course_source.py`.
- `animation/control_specs.py`, `animation/sequence_scenes.py`: 6 ManimGL sequences, 24 steps
  (input sizes, feedback substitution, three examples, the matrix and rank test, rank 1 vs rank 2,
  MATLAB and limits). Render: `.\.venv\Scripts\python.exe courses\controls\controllability\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: dependency-free math (ctrb, Jacobi SVD, numerical rank with relative tolerance 1e-9,
  explorer model), usable from Node. `qa_cases.json` lists reference cases and the export contract.
- `dist/explorer.js`: A = [[1, c], [0, 2]] with input b (optionally a second actuator e1); shows AB, C,
  determinant, singular values, rank, reachable set and unreachable direction.

Corrections applied from review: rank test stated as rank n (full row rank); "optimal" qualified;
conjugate-pair and actuator-limit caveats; singular values of C are not Gramian energies;
the discrete-time coefficient picture is labelled authored. Launcher: `.\launch_controllability.ps1`.

Open the complete library with `.\launch_study.ps1`, then Controls -> Controllability.
The public URL is `/controls/controllability/`. The optional GPT tutor remains ready for a
locally configured key in the standalone guide; the static site works without it.

Maintenance commands (repository root):

```powershell
.\.venv\Scripts\python.exe qa/controllability_math_qa.py
.\.venv\Scripts\python.exe tools/check_study.py --package controllability --decode --typeset
node qa/study_browser_qa.js courses/controls/controllability
.\.venv\Scripts\python.exe tools/contact_sheets.py --package controllability
```

The explorer depicts column-space reachability from zero and a bounded coefficient point.
For two actuators, the sliders vary only the b/Ab slice; rank uses all four columns.
The separate discrete-time illustration is not a sampled version of the continuous model.
SVD values depend on state/input scaling; they are not finite-time continuous control energies.
The numerical rank uses sigma_i > 1e-9 sigma_max, with sigma_max <= 1e-12 treated as zero.
See [REVIEW.md](REVIEW.md) for the trial's verification and usage records.
