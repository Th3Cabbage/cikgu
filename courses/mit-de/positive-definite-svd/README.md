# Unit 9: Positive Definite Matrices and the SVD

Study companion to videos 48-49 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Section 7.2 (printed pp.
396-404; local PDF page = printed + 12). Sources: ignored `sources/mit-de-48`, `sources/mit-de-49`.

- `course_source.py` -> `dist/course.json`: 3 sections (positive definite matrices and A^T A; five
  tests and the energy; the SVD).
- `animation/`: 5 ManimGL sequences, 15 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\positive-definite-svd\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: symmetric 2x2 eigen-decomposition (Jacobi angle), the five tests with
  classification and Cholesky factor, energy, and a 2x2 SVD that keeps U orthogonal for nearly
  singular A (U and V may be reflections).
- `dist/explorer.js` (Sonnet package-builder, reviewed): five tests and an energy map; the SVD as
  four panes (circle, V^T, Sigma, U) and the rank-one pieces.

Source correction (frame 0510 of video 49): the board's matrix is corrected to the singular
A = [2 2; 1 1] (sigma = sqrt10, 0), but the lower-left entry of U keeps a -1 from the earlier
version; for this A, u1 = (2, 1)/sqrt5.

Checks (10 November 2026): `qa/mit_de_positive_definite_svd_math_qa.py` 3042/3042 (eigen-pairs,
tests, classification and Cholesky vs numpy over 223 symmetric matrices; SVD orthogonality,
reconstruction and singular values vs numpy over 266 matrices incl. near-singular and reflection
cases; SymPy examples); `tools/check_study.py --decode --typeset` no errors; `qa/study_browser_qa.js` 37/37.
Codex review 1: 2 findings (orthogonality of U for nearly singular A; orthogonal factors may be
reflections), both fixed.

Launch alone with `.\launch_positive_definite_svd.ps1` (port 8839), or with `.\launch_study.ps1`.
