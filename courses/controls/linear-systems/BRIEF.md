# Linear Systems — focused implementation brief

The user wants the same browser study package as courses/controls/overview/, for Steve Brunton's second lecture, https://www.youtube.com/watch?v=nyqJJdhReiA&t=1342s. Cover the FULL 24:47 lecture, with the linked 22:22 coordinate interpretation easy to find. Codex plans and independently reviews; Claude Opus 5.5 implements. Keep the collaboration friendly and focused. User requests a faster, lower-token workflow: reuse the scaffold and helpers; don't reread the old 1-hour session or reinvent the player/server.

## Sources and scope (reviewed by Codex)

- sources/linear-systems/transcript.txt: full 30-second timestamped transcript, about 4k words. YouTube has no captions; generated locally with Whisper base.en, so it contains ASR errors (especially formulas and a repeated filler at 02:00). Read it once; cross-check math against the book and video frames.
- sources/linear-systems/book.txt: extracted Chapter 8 pages. The actual mathematical basis is printed pp.331–332, PDF pp.351–352, Eqs 8.11–8.19. Printed p.330 covers linearization announced in the introduction; later pages are next topics, not this lecture's worked material.
- Frames sources/linear-systems/frames/0210.jpg (exponential introduction), 0570.jpg (x=Tz), 0930.jpg (decoupled solution), 1290.jpg and 1342.jpg (proof and three-stage interpretation). Inspect 2-3 frames; no need to open the entire video or all sources repeatedly.
- Important: the INTRO announces nonlinear linearization, stability, discrete time and controllability, but the END explicitly defers them to later videos. Don't pretend they are taught in this 24:47 lecture. Include only a brief next-steps note. Main subject: homogeneous xdot=Ax, eigenpairs, eigenbasis, decoupling, matrix exponential similarity proof, coordinate interpretation.

## Reused scaffold already created

courses/controls/linear-systems/dist/app.js, styles.css, index.html, theme-boot.js, favicon.svg and vendor/ are copied/adapted from the tested overview. Player, navigation, explanatory quiz, notes/examples, themes, progress, accessibility, mobile, reduced motion, fallbacks and step-aware GPT panel are ready. Do not rewrite the 65kB app.js. Read narrow ranges only if necessary. The explorer is delegated to explorer.js:

    window.StudyExplorer = {
      restore(saved, config): validated state or null,
      stop(): stop any timers on navigation,
      render({root,course,state,save,html,svg,mathText,displayMath,flowMath,announce,panel}): pageTitle
    }

Use state.explorer for saved explorer values. The shell calls restore on load and serializes it automatically. Supply dist/explorer.js and dist/study_math.js (UMD/module.exports for math QA). Any residual old pend/cruise/reset labels or guide name from the copied shell must be removed where necessary; check using targeted searches, not a full rewrite.

server.py: copied tested standard-library loopback server. APP='Study_linear_systems'; health endpoint remains /__control_health (launcher agrees); default port 8780. Generic tutor instructions and trusted course.explorer.tutorContext replace old overview assumptions. It uses the SAME reviewed Responses API implementation, no new integration required. API key is absent; user wants ready-to-enable later. No live GPT calls. Source metadata/course notes only; never bundle original book or downloaded lecture in dist.

launch_linear_systems.ps1 at root: already generated, reuses the tested nonce/port-fallback/shutdown launcher. root README entry and links to existing overview/ODE should be added after implementation.

animation/ctl_common.py: copied tested ManimGL mathtext helpers (Mx token equations, Mat matrices, ControlScene with start/step_done boundaries and tmorph). Keep as-is unless a proven defect appears. Read the relevant class signatures/examples, not the whole old scenes module. Imports control_specs from this package's animation directory. Note Mat accepts 2-D lists; Mx supports token specs (key, tex, color). No LaTeX installed. All dependencies and FFmpeg exist in .venv. Main code is real ManimGL rendering.

animation/build_sequences.py: copied tested 1280x720,30fps renderer/cutter; expects new animation/control_specs.py and animation/sequence_scenes.py. Write these two files. For quick comparison, the previous scenes' CloseLoopSequence (courses/controls/overview/animation/control_scenes.py around lines650-740) shows actual matched token substitution. Do not read the whole prior file. It uses exact boundaries, stable stills and source stamps. Render .venv/Scripts/python.exe courses/controls/linear-systems/animation/build_sequences.py --jobs 2. Use only real ManimGL authored transitions; no whole-slide-fade teaching.

## Deliverable

Six short sections, roughly 26–34 meaningful animated steps, worked examples and 8–10 quiz questions with explanation on EVERY option. Proposed sections match actual lecture:

1. xdot=Ax and the matrix exponential (00:00–04:30): x is n-vector, A n×n; x(t)=e^{At}x0, E(0)=I; scalar Taylor series becomes I+At+A²t²/2!+... . Matrix exponential is NOT entrywise exp. Avoid claiming diagonalization is how all practical numerical algorithms compute expm; it is the lecture's analytical route, while numerical libraries use robust methods.
2. Eigenpairs to AT=TD (04:30–08:15): Ac_i=lambda_i c_i, c_i nonzero; T columns independent eigenvectors, D diagonal. Animate columns being scaled, and why AT=TD. Distinct eigenvalues sufficient but not necessary; repeated can still be diagonalizable; defective needs generalized eigenvectors/Jordan form (brief caution only).
3. Change coordinates (08:15–11:30): x=Tz, z=T^{-1}x; constant T means xdot=T zdot; substitute T zdot=ATz; multiply on LEFT by T^{-1}; zdot=T^{-1}ATz=Dz. Keep matrix order, do not imply T^{-1}=T^T unless orthogonal. Show transformations geometrically (a shear/eigenbasis, not only equations).
4. Decoupled dynamics (11:30–14:45): diagonal D gives zdot_i=lambda_i z_i; z_i(t)=e^{lambda_i t}z_i(0). e^{Dt} has exponentials on diagonal and ZEROS off diagonal. Physically each mode evolves independently. Lambda notation: lecture uses D; book uses Lambda; explain once.
5. Why e^{At}=Te^{Dt}T^{-1} (14:45–20:45): derive A=TDT^{-1}; animate A²=(TDT^{-1})(TDT^{-1}), cancel adjacent T^{-1}T only; A^k=TD^kT^{-1}; rewrite I=TT^{-1}; substitute into series; factor T on LEFT and T^{-1} on RIGHT; recognize the middle series e^{Dt}. This is the mathematical centrepiece: show each operation, not a jump to the final identity.
6. Map -> evolve -> map back (20:45–24:47), explicitly highlight linked 22:22. z0=T^{-1}x0; z(t)=e^{Dt}z0; x(t)=Tz(t). Choose an original non-orthogonal example to make inverse-vs-transpose matter:
   T=[[1,1],[0,1]], D=diag(-1,-2), T^{-1}=[[1,-1],[0,1]], A=[[-1,-1],[0,-2]], x0=[2,1]. Then z0=[1,1]; x(t)=[e^{-t}+e^{-2t},e^{-2t}]. At t=ln2 -> z=[1/2,1/4], x=[3/4,1/4]. Verify xdot(0)=Ax0=[-3,-2]. Clearly label this numerical example as authored for the companion, not quoted from the video.

## Live explorer — small, focused, accurate

Visualize the 3-stage coordinate pipeline with changing time and the physical/modal trajectories. To avoid fragile numerical eigensolvers and excess code, construct an invertible basis T=[[1,s],[0,1]], D=diag(l1,l2), A=TDT^{-1}=[[l1,s(l2-l1)],[0,l2]]. Sliders l1,l2,s, x0 components, and time; presets 'worked example', 'both decay', 'saddle', 'repeated but diagonalizable'. Display T,D,T^{-1},A, z0,z(t),x(t). Show vectors/trajectory in physical and modal planes with legible axes. Play/pause optional. Parameter changes respond immediately. Use exact formulas (not RK4) and save/restore validated values. If adding a defective preset, don't invent an invertible eigenbasis: show limitation and compute correct Jordan response. Fine to leave defective as a note to keep scope focused.

## Verification and efficiency

Implement package source first, render, then test once; revise only observed failures. Reuse server and player infrastructure. Don't re-run unchanged overview/ODE suites. Make a compact qa/linear_systems_qa.py and qa/linear_systems_browser_qa.js, or a generic parameterized checker, that verify:
- math vs SciPy expm across varied l1,l2,s,t and initial states; t=0, semigroup property, worked numbers ln2, equal eigenvalue example; inverse-vs-transpose; eigenbasis and series identities.
- specs/manifest agree; every media file exists, all clips decode and boundaries/stills agree; math typesets without errors.
- desktop/mobile navigation and no overflow, all sequences reach final steps (speed up only in tests), step control behavior, quiz retry/scoring, progress restore, tutor missing-key state and server-built NEW lecture context, /book range route, API mock only if needed. Existing API behavior is already tested; don't duplicate 76 unchanged tests.
- local launcher points to correct package and unique port/identity. No accidental ODE/overview edits.

The existing qa/tooling/node_modules/playwright-core and system Chrome are installed. No need to install anything unless proven missing. Keep test result output concise, screenshots/contact sheets under qa/screenshots/linear-systems, logs/results ignored folders. Don't commit/publish or inspect credentials. Return what exists, actual check results, and concrete limitations. Please implement now, not just a plan. Thank you!
