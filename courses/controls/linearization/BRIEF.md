# Linearization companion: complete the lesson

Thanks for phase 1! Please finish the actual study package, using your phase-1 math/explorer.
Read `SOURCE_REVIEW.md` in this package, then the compact `sources/linearization/transcript.txt`
once and `book.txt`. Read `CLAUDE.md` and `.claude/skills/build-study-package/SKILL.md` if not in
session context. Inspect 2–3 key source frames (especially 1560/1800). Source review corrects the
phase-1 damping assumption: damping IS taught; default q=1,d=0.1 should reproduce lecture numbers.
Input/output controls remain clearly labelled book-supported companion extensions.
With nonzero constant `delta_u`, the chosen zero-input reference is no longer a fixed point of
the driven system. Label eigenvalue classifications as the **zero-input reference**; a forced
trajectory is an input-response comparison, not a proof of stability of that reference under drive.

You own this package and new `qa/linearization_*` scripts only. Codex handles shared catalog,
shared test counts, root docs and integration, so don't edit shared files/other packages or
commit/push. No paid GPT calls or new credentials. Browser is the deliverable. Existing player,
progress, quiz, trusted tutor backend and root launcher `launch_linearization.ps1` are ready.
The corrected renderer is already copied from Stability into `animation/build_sequences.py`,
with default jobs1; use it. No need to change `ctl_common.py` without an observed issue.

Author `course_source.py` generating `dist/course.json`, `animation/control_specs.py` and
`animation/sequence_scenes.py`. Proposed **7** sections below; shell supports arbitrary section
counts, but check for leftover hardcoded 1–6 assumptions. Target ~35–42 meaningful animation
steps across ~7–8 sequences; keep concepts readable rather than cramming the video into one scene.
Every section has goals, original notes, key ideas, worked example with solution steps, verified
video/book references, tutor notes; 10 explanatory quiz questions with feedback on every option.
Use the course schema in `courses/controls/linear-systems/course_source.py` narrowly. Keep title
"Linearizing Around a Fixed Point", video1846s, `Study_linearization`, `linearization-v1`, port8810.

1. **Fixed points (0–180s)**: f(xbar)=0, not xbar=0. Physical up/down diagram, solve simple fixed
   point conditions. Distinguish fixed from stable. One local model per chosen equilibrium.
2. **Jacobian (180–405s)**: rows fi, columns xj; f=[x1*x2,x1²+x2²]; animate taking each derivative
   into the right matrix cell; numerical evaluation at zero. A=0 is inconclusive (defer to section4).
3. **Shift, expand, truncate (405–780s)**: explicitly move x to eta=x-xbar; doteta=dotx because
   xbar constant. Animate Taylor constant/linear/remainder terms; vanish f(xbar), shrink remainder,
   keep Aeta. Don't write an exact equality between nonlinear and truncated dynamics. Include
   non-equilibrium caution (affine residual remains); book-supported A/B/C/D in a short extension.
4. **Validity and hyperbolicity (780–960s)**: all eigenvalues Re!=0, local qualitative theorem,
   strict stable/unstable criteria; neutral/zero not decided. Companion ±x³ example makes identical
   zero Jacobian/opposite dynamics visible (arrows toward/away origin). Do not teach the false
   claim that the theorem requires all eigenvalues negative or that a neutral linearization proves
   nonlinear stability. State differentiability/smoothness conditions without overloading the UI.
5. **Pendulum state and equilibria (960–1350s)**: draw real pendulum, normalize q=g/L=1, viscous
   d; theta second-order -> statefirst-order; solve omega=0 and sin(theta)=0; down/up modulo2pi.
   Keep radians and theta from downward vertical explicit. Show small positive offset at pi.
6. **Two Jacobians, two behaviors (1350–1650s)**: derive general J with -qcos(theta), evaluate
   at0 andpi; show cospi=-1 changes the sign. Local coordinates eta=theta-theta_bar,nu=omega.
   Animate eigenvalues and phase arrows for up vs down. d=0 center vs saddle; d>0 down asymptotic,
   up unstable. Companion general damping formula lambda=(-d+-sqrt(d²-4q))/2 down, and
   (-d+-sqrt(d²+4q))/2 up; label overdamped option accurately. No global linear approximation.
7. **MATLAB check (1650–1846s)**: rebuild actual Ad/Au with d0.1; animate eigenvalues moving
   to -0.05+-0.998749i and -1.051249,0.951249; show equivalent short NumPy snippet as a companion,
   not claim it appears in video. Interactive browser lets learner reproduce with no MATLAB.
   Future feedback/controllability preview only, not a taught control design.

Animations must show operations: tokens move/cancel/substitute, individual partials populate
matrix cells, coordinate origin shifts, local arrows compare, pendulum/eigenvalues change.
Whole equation slides fading into the next aren't adequate. Use real ManimGL scenes with `Mx`,
`Mat`, `ControlScene.start/step_done`, token morphs. Read helper signatures and a narrow example
scene instead of whole prior scene modules. All mathtext SVG sizes/LaTeX conventions should match
existing helpers, with no MiKTeX requirement. Keep all content in stage bounds clear of header
and relation chip. Record coherent stable-state boundaries per authored step.

Render `.venv/Scripts/python.exe courses/controls/linearization/animation/build_sequences.py --jobs 1`.
Fix observed scene errors and rerender only affected ids. Stable states and captions must agree.
Run `tools/check_study.py --package linearization --decode` after rendering.

Expand or add compact QA for course/media/context and real browser. Check all section/sequence
routes, every sequence reaching final state (speed videos in tests only), Next/Back/Replay/
Restart/reduced-motion/fallback, explanatory quiz retry/first-try scoring, restore/save, missing-key
panel and section7/animation/explorer trusted context. Test explorer immediate updates, invalid
saved values, play elapsed time and navigation cancellation; desktop/mobile/themes/no overflow.
Use installed Chrome + qa/tooling/node_modules/playwright-core. Reuse test helpers appropriately;
don't repeat76 already-tested mock API cases. In tests don't require a clean Git tree because
the user's ongoing folder refactor is intentionally uncommitted. Verify derivative/model/metadata
assumptions; report actual checks, not inferred success.

Write package README (root commands, scope, accurate references, explorer assumptions/numerics,
math/moduleAPI), REVIEW (what sourceframes and actual checks, limitations). Keep intermediate
briefs/source review for future maintainers. Save QA artifacts in ignored qa/results/screenshots/
scratch and master renders in ignored animation/masters. No source media in dist.

Please complete code, rendered assets and relevant tests before returning. Codex will independently
inspect math/media/browser and integrate it into the combined site. Thank you!
