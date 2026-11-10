# Unit 5: The Laplace Transform

Study companion to videos 24-26 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Sections 2.7 and 8.5-8.6
(printed pp. 139-152, 470-489; local PDF page = printed + 12). Sources: ignored `sources/mit-de-24` ... `-26`.

- `course_source.py` -> `dist/course.json`: 3 sections (first order by Laplace with partial
  fractions, second order with the transfer function and cosine inputs, convolution).
- `animation/`: 5 ManimGL sequences, 16 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\laplace-transform\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: Y(s) for first and second order equations with six inputs; poles with
  multiplicity (merged within 1e-5 for a stable inverse; cancelled poles removed); residues by
  power-series division; inverse transform; RK4 comparison. Impulse values y0, v0 mean t = 0-.
- `dist/explorer.js` (Sonnet package-builder, reviewed): s-plane poles, partial fractions, y(t).

Checks (10 November 2026): `qa/mit_de_laplace_transform_math_qa.py` 571/571 (inverse vs SciPy for
every input and order, Y(s) values, reduced poles vs SymPy, near-coincident and cancelled poles,
transforms and examples); `tools/check_study.py --decode --typeset` no errors; `qa/study_browser_qa.js` 38/38.
Codex review 1: 4 findings (near-coincident poles, cancelled poles, repeated-pole shape for cosine
inputs, impulse initial-value convention), all fixed with regression checks.

Launch alone with `.\launch_laplace_transform.ps1` (port 8835), or with `.\launch_study.ps1`.
