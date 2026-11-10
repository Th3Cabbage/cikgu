# Unit 4: Electrical Networks and Solution Methods

Study companion to videos 20-23 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Sections 2.5-2.6
(printed pp. 118-135; local PDF page = printed + 12). Sources: ignored `sources/mit-de-20` ... `-23`.

- `course_source.py` -> `dist/course.json`: 4 sections (RLC loop and impedance, undetermined
  coefficients, the worked example y'' - 3y' + 2y = 4t with resonance, variation of parameters).
- `animation/`: 5 ManimGL sequences, 15 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\networks-and-methods\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: impedance; a general undetermined-coefficients solver for t^k e^(st)
  (s real, 0 or i w) with root multiplicity 0, 1, 2; exact residual; convolution with g.
- `dist/explorer.js` (Sonnet package-builder, reviewed): RLC phasor and current curve; trial
  form, solved coefficients, and y_p against the convolution solution from rest.

Checks (10 November 2026): `qa/mit_de_networks_and_methods_math_qa.py` 967/967 (SymPy residual
of every solved y_p, multiplicity, convolution vs SciPy, impedance, examples, VP kernel = g);
`tools/check_study.py --decode --typeset` no errors (412 formulas); `qa/study_browser_qa.js` 38/38.
Codex review 1: 2 findings (repeated-root case of the VP/impulse formula; finite-difference
residual inaccurate), both fixed with QA checks.

Launch alone with `.\launch_networks_and_methods.ps1` (port 8834), or with `.\launch_study.ps1`.
