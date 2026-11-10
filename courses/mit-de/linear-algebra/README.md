# Unit 7: Column Space, Basis and Graphs

Study companion to videos 35-39 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Sections 5.1 and 5.4-5.6
(printed pp. 251-324; local PDF page = printed + 12). Sources: ignored `sources/mit-de-35` ... `-39`.

- `course_source.py` -> `dist/course.json`: 5 sections (column space and null space, independence
  and basis, the four subspaces, graphs and incidence matrices, null spaces of a graph and loops).
- `animation/`: 5 ManimGL sequences, 15 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\linear-algebra\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: exact fraction RREF, the four subspaces, complete solution of Av = b,
  incidence matrices, graph rank/components/loops/Laplacian (edgeless graph handled).
- `dist/explorer.js` (Sonnet package-builder, reviewed): editable matrix with the four subspaces
  and the solve panel; graph mode with toggled edges, loops and the Laplacian.

Board values checked on frames: b = (3, 4, 4) and v_p = (2, 1, 0) (video 35); a1 = (2, 1, 5),
a2 = (4, 2, 0) (video 36).

Checks (10 November 2026): `qa/mit_de_linear_algebra_math_qa.py` 1126/1126 (RREF, rank and all
four subspaces vs SymPy for ~150 random integer matrices, solvability and particular solutions,
graph incidence/rank/loops/Laplacian incl. the edgeless graph, examples); `tools/check_study.py
--decode --typeset` no errors (446 formulas); `qa/study_browser_qa.js` 38/38.
Codex review 1: 2 findings (edgeless graph results; loop combination needs orientation), both fixed.

Launch alone with `.\launch_linear_algebra.ps1` (port 8837), or with `.\launch_study.ps1`.
