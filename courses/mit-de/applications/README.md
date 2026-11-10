# Unit 12: Tumbling Box, Predator-Prey and Chaos

Study companion to videos 66-68 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Cleve Moler) and Strang, *Differential Equations and Linear Algebra*, Section 3.3 and its problems
(printed pp. 172-181; local PDF page = printed + 12). Sources: ignored `sources/mit-de-66` ... `-68`.
MATLAB is not needed.

- `course_source.py` -> `dist/course.json`: 3 sections (the tumbling box computed on the sphere;
  Lotka-Volterra with the conserved H and the period; the Lorenz attractor and chaos).
- `animation/`: 3 ManimGL sequences, 9 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\applications\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: RK4, box start vectors, predator-prey H and period (return to the starting
  angle), Lorenz right side and critical points.
- `dist/explorer.js` (written by the lead session; the Sonnet agents were at their usage limit):
  Lorenz butterfly with a second start 10^k away and their distance, box orbit on the sphere with
  time series, predator-prey phase plane with H and period; progressive drawing with Play.

Caption corrections: video 67 "100 and 300" at 5:30 is the start (400, 100); video 68 "beta times
the square root of rho minus one" is sqrt(beta(rho - 1)).

Checks (11 November 2026): `qa/mit_de_applications_math_qa.py` 34/34 (RK4 vs SciPy for all three
systems, conserved radius and H, period vs an event-based reference (6.536 for Moler's run, 2 pi for
small orbits), Lorenz critical points, sensitive dependence, rho = 160 periodic and rho = 28 not,
SymPy examples incl. Moler's matrix form); `tools/check_study.py --decode --typeset` no errors;
`qa/study_browser_qa.js` 29/29. Codex review 1: 1 finding (a singular A(u) does not by itself give
Lorenz equilibria), fixed with symbolic checks.

Launch alone with `.\launch_applications.ps1` (port 8842), or with `.\launch_study.ps1`.
