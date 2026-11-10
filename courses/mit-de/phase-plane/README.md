# Unit 6: Phase Plane, Linearization and Stability

Study companion to videos 27-34 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Chapter 3 (printed pp.
154-180; local PDF page = printed + 12). Sources: ignored `sources/mit-de-27` ... `-34`.

- `course_source.py` -> `dist/course.json`: 6 sections (direction fields and isoclines; source,
  sink, saddle; spirals and centers; trace/determinant stability; linearization with the Jacobian,
  predator-prey; the tumbling box in 3-D).
- `animation/`: 6 ManimGL sequences, 18 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\phase-plane\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: 2x2 eigenvalues/eigenvectors with scale-aware classification, asymptotic
  stability test, linear/predator-prey/pendulum models with Jacobians, RK4, tumbling-box Jacobian
  and conserved quantities.
- `dist/explorer.js` (Sonnet package-builder, reviewed): phase plane with direction field and
  click-to-start trajectories, trace-determinant plane, critical points of nonlinear systems.

Checks (10 November 2026): `qa/mit_de_phase_plane_math_qa.py` 3070/3070 (eigenpairs vs numpy over
629 matrices incl. tiny and large scales, rescaling invariance, RK4 vs SciPy, conserved quantities,
Jacobians and tumbling eigenvalues with SymPy, examples); `tools/check_study.py --decode --typeset`
no errors (501 formulas); `qa/study_browser_qa.js` 44/44.
Codex review 1: 3 findings (stable vs asymptotically stable in the quiz and notes; absolute
tolerances for small matrices; separatrices cannot pass through the tumbling equilibria), all fixed.

Launch alone with `.\launch_phase_plane.ps1` (port 8836), or with `.\launch_study.ps1`.
