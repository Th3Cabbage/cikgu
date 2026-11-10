# Unit 11: Numerical Methods for ODEs

Study companion to videos 57-65 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Cleve Moler) and Strang, *Differential Equations and Linear Algebra*, Sections 3.4-3.5 (printed pp.
184-196; local PDF page = printed + 12). Sources: ignored `sources/mit-de-57` ... `-65`.
MATLAB is not needed: every method is implemented in JavaScript.

- `course_source.py` -> `dist/course.json`: 6 sections (Euler; midpoint and RK4; order; ode23 and
  ode45 error control; stiffness and backward Euler; systems and the ODE suite).
- `animation/`: 6 ManimGL sequences, 18 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\numerical-methods\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: Euler, midpoint, Heun, RK4, Bogacki-Shampine 3(2) with FSAL, Dormand-Prince
  5(4), backward Euler with Newton (failed solves are not accepted), adaptive step control,
  nested-mesh order experiment, Hermite interpolant, eight problems.
- `dist/explorer.js` (written by the lead session after the Sonnet agent hit a usage limit):
  live step view, stage by stage (stage points, slope arrows, probe lines, weighted step), error
  gauge with accept/reject, step-size strip, error readout, method card and order chart.

Source notes: the order experiment integrates 1/(1+t)^2 (screen; exact 1/2), not 1/(1+t^2) as
narrated. The near-singular problem y' = 2(a - t)y^2, a = 1/4, y(0) = 15.9 peaks at
1/(1/15.9 - 1/16) = 2544.

Checks (11 November 2026): `qa/mit_de_numerical_methods_math_qa.py` 274/274 (each method's step,
stages and error estimate vs an independent Python implementation, lecture numbers, observed orders
on nested meshes, adaptive accuracy vs SciPy DOP853, stiff behaviour, examples);
`tools/check_study.py --decode --typeset` no errors; `qa/study_browser_qa.js` 44/44.
Codex review 1: 2 findings (backward Euler accepted failed Newton solves; order experiment used
non-nested meshes), both fixed with regression checks.

Launch alone with `.\launch_numerical_methods.ps1` (port 8841), or with `.\launch_study.ps1`.
