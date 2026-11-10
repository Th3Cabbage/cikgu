# Unit 1: First Order Linear Equations

Study companion to videos 1-10 of MIT OpenCourseWare's
[Learn Differential Equations](https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG)
(Gilbert Strang and Cleve Moler) and Strang, *Differential Equations and Linear Algebra*,
Sections 1.1-1.6 (printed pp. 1-52; local PDF page = printed + 12). Part of the
[MIT Learn Differential Equations course](../PROGRESS.md); sources are cached in ignored
`sources/mit-de-01` ... `sources/mit-de-10`.

- `course_source.py` -> `dist/course.json`: 8 sections (overview, calculus, exponential input and
  resonance, cosine input, any input, step and delta, complex exponential, integrating factors),
  authored worked examples, 10-question quiz, explorer config. Each lecture source has a video
  number `v` and time `t`.
- `animation/control_specs.py`, `animation/sequence_scenes.py`: 10 ManimGL sequences, 33 steps.
  Render: `.\.venv\Scripts\python.exe courses\mit-de\first-order-linear\animation\build_sequences.py --jobs 1`.
- `dist/study_math.js`: closed-form responses of y' = ay + q(t) for constant, e^(st), cos(wt),
  step and delta inputs (expm1-based near resonance), usable from Node.
- `dist/explorer.js`: input-kind selector, sliders and presets; plots the null part, the driven
  (very particular) part, their sum and the input, with gain/phase and resonance readouts.

Corrections from the sources: in video 7 the board first omits the rate a in the impulse
response e^(a(t-T)) and then corrects it; captions in video 10 read "0 to 2T" for the limits
0 to t. Both videos 9 and 10 use a(t) = 2t despite the playlist titles.

Checks (10 November 2026): `qa/mit_de_first_order_linear_math_qa.py` 515/515 (closed forms vs
SciPy solve_ivp, identities, worked examples); `tools/check_study.py --decode --typeset` no errors
(816 formulas); `qa/study_browser_qa.js` 65/65; site build tests 7/7 and site browser checks 104/104.
Codex review 1 (plan and mathematics) found no mathematical errors.

Launch alone with `.\launch_first_order_linear.ps1` (port 8831), or the whole library with
`.\launch_study.ps1` (MIT Learn Differential Equations -> Unit 1). The optional GPT tutor works
only with a locally configured key; the guide works without it.
