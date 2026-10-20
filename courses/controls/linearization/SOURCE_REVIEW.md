# Source review: Linearizing Around a Fixed Point

Reviewed 20 October 2026. Playlist item 4, video `1YMTkELi3tE`, duration **1846 seconds / 30:46**.
Primary source: https://www.youtube.com/watch?v=1YMTkELi3tE
Local research cache (ignored): `sources/linearization/`.

`transcript.txt` contains a locally generated Whisper base.en transcript (5070 words, 30-second
segments), because YouTube provided no English captions. It is research, not a verified transcript.
ASR errors include “Hartman-Growman” (Hartman–Grobman), “sines”/“signs”, and spoken matrix rows
rendered as “0.1”. Verified the board and MATLAB values in actual 1080p frames.

## Actual lecture scope and useful source times

- 00:00–03:00: get local linear models from nonlinear autonomous dynamics; fixed points satisfy
  `f(xbar)=0`. Up and down pendulum equilibria are examples. A fixed point may be unstable.
- 03:00–06:45: Jacobian indexing, rows are output component `fi`, columns differentiated state
  `xj`. Explicit example `f1=x1*x2`, `f2=x1^2+x2^2`, with Jacobian
  `[[x2,x1],[2*x1,2*x2]]`. Verified frame 06:00. Evaluating at a fixed point makes a numerical
  constant matrix. Its only real fixed point is zero, where the Jacobian is zero (nonhyperbolic).
  Any evaluation at another point is an illustrative derivative computation, not a claimed fixed point.
- 06:45–13:00: zoom near equilibrium; shift origin; Taylor expansion; `eta=x-xbar`, so
  `eta_dot=f(xbar+eta)=f(xbar)+J(xbar)*eta+O(||eta||^2)` for sufficiently smooth dynamics.
  The constant term vanishes at an equilibrium; truncating gives **approximately**, not exactly,
  `eta_dot=A*eta`. Higher-order terms become small, not literally zero at a finite offset.
  Stabilizing feedback can keep trajectories where the local approximation is useful; it is only
  motivated, not designed here.
- 13:00–16:00: Hartman–Grobman caveat. Hyperbolic means **every** eigenvalue has nonzero real
  part; all negative is sufficient for local asymptotic stability, any positive real part implies
  instability. The theorem gives local qualitative/topological behavior, not exact trajectories,
  equal periods or a numerical accuracy radius. Imaginary or zero real parts require nonlinear
  analysis. Counterexamples `xdot=-x^3` and `xdot=+x^3` have the same zero Jacobian but opposite
  stability; these are companion examples, not the lecturer's examples.
- 16:00–22:30: derive state form for the pendulum. Initially `theta_ddot=-(g/L)*sin(theta)`, then
  add viscous friction `-d*theta_dot` at about **17:30**, normalize `g/L=1` at **19:30–20:00**.
  States `x1=theta`, `x2=theta_dot` give `f=[x2,-sin(x1)-d*x2]`. Fixed states satisfy
  `x2=0`, `sin(x1)=0`: `(k*pi,0)`, represented by down `(0,0)` and up `(pi,0)` modulo `2*pi`.
- 22:30–27:30: compute `J=[[0,1],[-cos(x1),-d]]`; evaluate down/up:
  `Ad=[[0,1],[-1,-d]]`, `Au=[[0,1],[1,-d]]`. With `d=0` eigenvalues are `+-i` down and `+-1`
  up. With small positive damping, down oscillations decay; large positive damping can remove
  oscillation, so do not claim all damping values give complex eigenvalues. Up retains one positive
  eigenvalue for all finite `d>=0`. At up, the linear state is **offset from pi**, not absolute angle.
- 27:30–30:46: MATLAB demonstration `d=0.1; Ad=[0 1; -1 -d]; eig(Ad)` gives
  `-0.05 +- 0.9987492178 i`; `Au=[0 1; 1 -d]; eig(Au)` gives
  `-1.0512492197`, `0.9512492197`. Concludes with `+Bu`/feedback motivation for future lessons;
  controllability/pole placement and an actual controller are deferred.

## Book correspondence

Root `databook.pdf` is the same 2017 preprint used by earlier packages.

- Printed **330**, PDF **350**, Section8.2 Eqs8.7–8.10: Taylor linearization of state/input/output,
  A/B/C/D evaluated at `(xbar,ubar)`, shifting coordinates. This is the primary general derivation.
- Printed **335**, PDF **355**, Eqs8.23–8.25: the **undamped** pendulum, Jacobian, down/up matrices.
  The video explicitly adds damping. Keep the distinction clear when citing book and video.
- Input and output extensions `eta_dot=A*eta+B*delta_u`, `delta_y=C*eta+D*delta_u` are book-supported
  companion material; the video mostly treats autonomous dynamics. For angle output C=[1,0],D=0.
  In the book's simplified equation u is normalized angular acceleration input.

Frames reviewed by Codex: `frames/0360.jpg` (polynomial Jacobian), `0600.jpg` and `0840.jpg`
(Taylor/offset coordinates), `1080.jpg` and `1320.jpg` (pendulum and fixed points), `1560.jpg`
(Jacobian/down/up), `1800.jpg` (MATLAB matrices/eigenvalues). The sparse auto-generated review
frames are also available. Do not bundle lecture, captions or textbook in public `dist/`.

**Correction to the phase-1 implementation brief:** damping is explicitly in this lecture; it
must not be labelled a new companion extension. Default `d=0.1`, `q=g/L=1` reproduces the MATLAB
example; retain an undamped preset. Constant input/output models are the optional book extension.
