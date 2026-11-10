# Unit 8: Eigenvalues and Linear Systems y' = Ay

Study companion to videos 40-47 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Chapter 6 (printed pp.
325-384; local PDF page = printed + 12). Sources: ignored `sources/mit-de-40` ... `-47`.

- `course_source.py` -> `dist/course.json`: 6 sections (eigenvalues and eigenvectors;
  diagonalization, powers and Markov matrices; solving y' = Ay; the matrix exponential and similar
  matrices; symmetric and complex matrices; second order systems).
- `animation/`: 6 ManimGL sequences, 18 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\eigenvalues-systems\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: 2x2 eigenvalues/eigenvectors with complex arithmetic and a centred
  discriminant, defective detection, diagonalization, powers, and a stable closed-form e^(At)
  (series near repeated roots, overflow-safe exponentials, scaling by t first).
- `dist/explorer.js` (Sonnet package-builder, reviewed): Ax against x with the image ellipse,
  powers u_(k+1) = A u_k, and flows y' = Ay with e^(At).

Checks (10 November 2026): `qa/mit_de_eigenvalues_systems_math_qa.py` 8293/8293 (eigenpairs,
diagonalization and powers vs numpy over 643 matrices, e^(At) vs scipy.linalg.expm incl. defective,
long-time near-double and extreme-magnitude cases, SymPy examples); `tools/check_study.py --decode
--typeset` no errors (574 formulas); `qa/study_browser_qa.js` 44/44.
Codex review 1: 3 numerical findings (nearby eigenvalues collapsed to a double root; long-time
error near repeated roots; overflow in e^(At)), all fixed with regression checks.

Launch alone with `.\launch_eigenvalues_systems.ps1` (port 8838), or with `.\launch_study.ps1`.
