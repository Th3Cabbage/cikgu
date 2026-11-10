# Unit 10: Boundary Problems, Fourier Series and PDEs

Study companion to videos 50-56 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Sections 7.3-7.4, 8.1,
8.3-8.4 (printed pp. 406-470; local PDF page = printed + 12). Sources: ignored `sources/mit-de-50` ... `-56`.

- `course_source.py` -> `dist/course.json`: 7 sections (boundary value problems and the point
  load; Laplace's equation; Fourier coefficients by orthogonality; square wave and ramp; Laplace on
  a disc and the Poisson kernel; the heat equation; the wave equation).
- `animation/`: 7 ManimGL sequences, 21 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\fourier-pde\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: closed-form Fourier coefficients (square, ramp, sawtooth, delta), partial
  sums, a cancellation-free Poisson kernel, heat and wave sine series, d'Alembert's solution.
- `dist/explorer.js` (Sonnet package-builder, reviewed): partial sums with coefficient bars and the
  Gibbs overshoot, a cooling bar, and a plucked string compared with d'Alembert.

Checks (10 November 2026): `qa/mit_de_fourier_pde_math_qa.py` 103/103 (coefficients vs quadrature,
partial-sum convergence and Gibbs overshoot, Poisson kernel vs its series and near the edge, delta
series in the weak sense, heat and pluck coefficients, series vs d'Alembert, SymPy examples);
`tools/check_study.py --decode --typeset` no errors (532 formulas); `qa/study_browser_qa.js` 49/49.
Codex review 1: 2 findings (the delta series converges only as a distribution; cancellation in the
Poisson kernel near the boundary), both fixed with QA checks.

Launch alone with `.\launch_fourier_pde.ps1` (port 8840), or with `.\launch_study.ps1`.
