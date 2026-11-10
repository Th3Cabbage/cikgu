# Unit 3: Second Order Equations and Oscillation

Study companion to videos 14-19 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang) and Strang, *Differential Equations and Linear Algebra*, Sections 2.1-2.4
(printed pp. 73-109; local PDF page = printed + 12). Sources: ignored `sources/mit-de-14` ... `-19`.

- `course_source.py` -> `dist/course.json`: 6 sections (free harmonic motion, forced motion and
  impulse, damping cases, impulse and step response, exponential response and resonance, damped
  cosine forcing with gain and phase), authored worked examples, 10-question quiz, explorer config.
- `animation/`: 6 ManimGL sequences, 19 steps. Render with
  `.\.venv\Scripts\python.exe courses\mit-de\second-order\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: closed-form solutions of y'' + By' + Cy = f for no input, cos, e^(st),
  step and impulse, including resonance (t sin wt/2w, t e^(st)/P'(s), t^2 e^(st)/2), g, r and gain.
- `dist/explorer.js` (Sonnet package-builder, reviewed): roots in the complex plane, response,
  gain curve.

Source notes: the step response board in video 17 is written for C = 1; the guide gives the
general r = 1/C + (s2 e^(s1 t) - s1 e^(s2 t))/(C(s1 - s2)).

Checks (10 November 2026): `qa/mit_de_second_order_math_qa.py` 405/405 (closed forms vs SciPy
DOP853 for every input and damping case, g, r, gain peak, SymPy examples); `tools/check_study.py
--decode --typeset` no errors (616 formulas); `qa/study_browser_qa.js` 45/45.
Codex review 1: 2 findings (gain peak exists only when B^2 < 2AC; envelope of the underdamped
example is sqrt5/2 e^(-t)), both fixed with QA checks.

Launch alone with `.\launch_second_order.ps1` (port 8833), or the whole library with `.\launch_study.ps1`.
