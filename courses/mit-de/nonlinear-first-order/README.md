# Unit 2: Nonlinear First Order Equations

Study companion to videos 11-13 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Sections 1.7-1.8
(printed pp. 53-66; local PDF page = printed + 12). Part of the
[MIT Learn Differential Equations course](../PROGRESS.md); sources are cached in ignored
`sources/mit-de-11` ... `sources/mit-de-13`.

- `course_source.py` -> `dist/course.json`: 3 sections (logistic equation, stability of steady
  states, separable equations), authored worked examples, 10-question quiz, explorer config.
- `animation/control_specs.py`, `animation/sequence_scenes.py`: 6 ManimGL sequences, 20 steps
  (z = 1/y substitution, S-curves, slope test, stability line, separation of y' = t/y, partial fractions).
  Render: `.\.venv\Scripts\python.exe courses\mit-de\nonlinear-first-order\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: models logistic, cubic, harvesting and y^2 - 1; steady states and their
  classification by f'(Y); RK4 with blow-up detection; exact logistic formula (NaN after a blow-up).
- `dist/explorer.js` (Sonnet package-builder, reviewed): f(y) with the stability line, and y(t).

Corrections from the sources: caption "12 t^2" is (1/2)t^2; for y' = t/y the start y(0) = 0 makes
the right side 0/0, so y = t and y = -t are candidates for t != 0, not classical solutions at t = 0.

Checks (10 November 2026): `qa/mit_de_nonlinear_first_order_math_qa.py` 519/519 (RK4 vs SciPy,
roots and classification, exact formula including the blow-up case, SymPy worked examples);
`tools/check_study.py --decode --typeset` no errors; `qa/study_browser_qa.js` 43/43.
Codex review 1 (adversarial, mathematics): 3 findings (quiz on y(0) = 0, exact formula past a
blow-up, absolute values and lost constant solutions in partial fractions), all fixed.

Launch alone with `.\launch_nonlinear_first_order.ps1` (port 8832), or the whole library with
`.\launch_study.ps1`.
