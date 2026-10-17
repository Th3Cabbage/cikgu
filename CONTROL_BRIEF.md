# Control Bootcamp overview — implementation and review brief

## Agreed experience

Browser-only companion to Steve Brunton's 19:31 overview (Pi7l8mMjYVE), supported by the user's local databook.pdf. Preserve the existing ODE package. Codex plans/reviews; Claude implements. No publication is needed for this local project. Build in control/ with launch_control.ps1 at the root.

Match the ODE guide's teaching mechanism: real ManimGL animations, authored per meaningful step, rendered to masters, then cut into clips and stable stills. Next plays one transition; Back jumps to previous state; Replay repeats; Restart resets. Rich equation/diagram transformations, not whole-slide fades. Include readable explanations and relationship labels, lesson notes, worked examples, source timestamps/page references, a live explorer, explanatory quiz, themes, keyboard support, responsive layout, reduced motion, and media fallback.

## Sources reviewed by Codex

- Local sources/control-bootcamp-overview/transcript.txt: English automatic captions, entire overview read. Correct recognition errors (Brunton, Kalman, state-space, u=-Kx).
- Video frames reviewed at 04:30, 08:40, and 17:20 to check diagram and derivation.
- Local databook.pdf: 572 PDF pages, Chapter 8 on PDF pages 343–395 / printed pages 323–375. Relevant portion is printed pp. 323–331, Sections 8.1 and opening 8.2. PDF page = printed page + 20 for these pages.
- sources/control-bootcamp-overview/chapter8.txt is local extracted text. Printed p.328 also visually checked.
- Use original paraphrased lesson text and freshly drawn diagrams. Do not copy the book chapter into the static distribution.

## Scope and suggested learning arc

1. From prediction to action (00:00–03:00): state, system, input, output, goal. Example: pendulum angle and angular velocity form a state. Prerequisite refresher: derivative, vector, matrix multiplication.
2. Types of control (03:00–08:10): passive truck fairing, active control; preplanned open-loop versus measured closed-loop. Animate taxonomy and progressively assemble a feedback block diagram; output sensing and controller signal return must be unambiguous.
3. Why feedback (08:10–12:58): model uncertainty, instability, external disturbance, efficient corrections. Distinguish internal model mismatch and external forcing. Benefit is possible with good design, not guaranteed. A controller can destabilize or amplify noise; high gain is not universally better. Optional book-supported static cruise example, clearly labeled a teaching model, not a physical vehicle simulator.
4. State-space language (12:58–15:44): xdot=Ax, x(t)=exp(At)x(0); add Bu; measure y=Cx. Dimensions x∈R^n, u∈R^m, y∈R^p, A n×n, B n×m, C p×n. The overview assumes no direct feedthrough, D=0. Don't teach the matrix exponential in depth.
5. Close the loop (15:44–18:30): explicitly assume full state available y=x; choose u=-Kx, K m×n; animate substitution xdot=Ax+B(-Kx), simplify Ax-BKx, factor ON THE RIGHT into (A-BK)x; A_cl=A-BK. Preserve matrix order. Eigenvalues of A_cl govern homogeneous stability, not A. Negative real parts all => asymptotically stable; any positive => unstable; zero-real-part boundary needs further analysis.
6. Make it concrete and recap (18:30–19:31 + book p.328): A=[[0,1],[1,0]], B=[[0],[1]], K=[4,4]. BK=[[0,0],[4,4]], A-BK=[[0,1],[-3,-4]], characteristic polynomial λ²+4λ+3=(λ+1)(λ+3), poles -1,-3 versus +1,-1. Full state feedback, normalized linearized small-angle example. Reachability/stabilizability, LQR, estimation, Kalman are next steps only.

## Mathematical caveats to teach naturally

- The lecture's broad claim about open-loop not changing dynamics needs qualification: additive preplanned input to a fixed LTI plant leaves its homogeneous matrix A unchanged. High-frequency parametric excitation (Kapitza pendulum) is a different model and can change effective stability. Don't contradict the lecture's own example by making a universal claim.
- Feedback can reduce disturbance effects; proportional control need not eliminate steady-state error. Efficient corrections depend on design and operating conditions.
- The book p.328 contains inconsistent wording of the cruise-control error for y=2u; derive examples independently. For y=a*u+d, u_open=r/a_model, y_open=a*r/a_model+d; with u=K(r-y), y_closed=(a*K*r+d)/(1+a*K). Label this static model explicitly.
- For interactive normalized pendulum: xdot=[[0,1],[1-k1,-k2]]x plus a pulse input if offered. Characteristic polynomial λ²+k2λ+(k1-1). Asymptotic stability iff k1>1 and k2>0. Distinguish neutral boundaries and Jordan drift at k1=1,k2=0. Display finite plot range / linear-model validity honestly, never silently clamp data into stable curves.

## Architecture and ownership

Environment verified: Python 3.13 repo .venv with ManimGL 1.7.2, matplotlib, scipy, pymupdf, imageio-ffmpeg, and audioop-lts installed. Offscreen render qa/scratch/control_render_probe.py succeeded with a real animated math SVG. Match its mathtext/SVGMobject technique to avoid needing MiKTeX. FFmpeg path can be set in generated render config file_writer.ffmpeg_bin. Existing qa/tooling/node_modules/playwright-core and system Chrome installed. See qa/scratch/control_probe.yml. User approved Claude Opus 5.5 after Fable credit rejection; tutor should be delivered ready to enable later, no live API key requested.

- control/dist: standalone original course content, UI, copied local KaTeX vendor, manifest, rendered clips/stills. No framework build needed.
- control/animation: ManimGL scenes/specs/build pipeline. Use repo .venv and bundled imageio_ffmpeg FFmpeg. MiKTeX is not found on this machine; can use individual mathematical glyphs rendered via matplotlib mathtext SVG into ManimGL SVGMobject for deterministic LaTeX-free typesetting, and real ManimGL transforms. Document this clearly. Avoid turning all animations into flat text slides.
- control/server.py: loopback-only standard-library server with range support and GPT tutor endpoint using OpenAI Responses API. Environment OPENAI_API_KEY only; no key in HTML, JS, URLs, logs, or source files. Configurable OPENAI_MODEL; sensible documented default. Missing key yields clear setup status while lessons still work.
- launch_control.ps1: robust launcher, busy-port fallback, ownership nonce/health check, clean termination. Existing ODE launchers/content untouched.
- Tutor: collapsible right panel; pinned context indicates lesson/step sent. Server constructs trusted context from local course/manifest IDs, bounded recent chat and selected book paraphrases; never trust arbitrary client system prompts. JSON input limits; same-origin protection; timeouts; useful error states; no fabricated offline GPT replies. Render output as text / safe math, never raw untrusted HTML. No need to send entire textbook.
- QA: independently check mathematical cases (SciPy reference), all media exists/decodes and boundaries agree, desktop/mobile navigation, every sequence, keyboard, quiz first-attempt scoring/retry/reset, themes, reduced motion/failures, tutor missing key and mocked successful response/context. Clearly distinguish mocked API tests from live API test.

## Review collaboration

Please implement with care and let me know concrete uncertainties or tradeoffs. I will review your work against source material and run independent checks, then send focused revisions. Keep changes within the new control package and its launcher/docs/tests. Do not commit, publish, read credentials, or modify the ODE guide. Thank you!
