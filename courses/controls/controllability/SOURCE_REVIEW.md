# Reviewed sources: Controllability

Playlist item 5, u5Sv7YKAkt4, Steve Brunton, 1949 seconds (32:29 cached metadata;
flat playlist rounds to 32:30). Official YouTube automatic English captions, not local ASR.
Video downloaded; board/MATLAB frames at 15:30, 24:30 and 30:30 inspected by Codex.
databook.pdf is the 2017 preprint: PDF 356-357 = printed 336-337, Section 8.3,
Eqs. 8.26-8.31. Book's fourth B=[1,1]^T example is not worked in this lecture.

Actual coverage and section candidates:
- 0-360: add Bu, dimensions x in R^n, u in R^q, B n-by-q; assume full-state
  measurements y=x; substitute u=-Kx to obtain xdot=(A-BK)x. K is q-by-n.
- 360-660: controllability means arbitrary pole placement and finite-time steering
  in the ideal continuous-time LTI model. Pair (A,B), not A alone. A plant may be fixed;
  actuator placement B matters. No specific pole-placement algorithm derived here.
- 660-1050: three physical examples: A=diag(1,2), B=[0,1]^T cannot affect x1;
  B=I2 controls both; coupling A=[[1,1],[0,2]] makes the SAME B=[0,1]^T controllable.
- 1050-1290: curly C=[B AB ... A^(n-1)B], n-by-(nq); rank(C)=n iff controllable.
- 1290-1470: construct matrices: uncoupled C=[[0,0],[1,2]], rank1;
  coupled C=[[0,1],[1,2]], determinant -1, rank2. Compute AB in correct order.
  Higher powers cannot fix rank deficiency (Cayley-Hamilton theorem; proof deferred).
- 1470-1949: MATLAB ctrb and rank, limitations and outlook: nonlinear system may be
  controllable despite an uncontrollable linearization; SVD preview; MATLAB demo 1800+.
  rank(ctrb(A,B)) returns 1 then 2, matching board. Present 6 sections if convenient.

Corrections/precision:
- Lecturer says 'full column rank' around 19:00, but the correct general test is rank n,
  i.e. full ROW rank of n-by-nq C. Only SISO square C is also full column rank.
- Feedback is not universally optimal: optimality needs a specified cost/assumptions.
- For real A,B,K arbitrary assigned poles must respect complex-conjugate pairing.
- No actuator/saturation bounds are included in classical controllability.
- Rank is numerical with tolerance; tiny nonzero coupling may be mathematically full
  rank but poorly conditioned. Display singular values/condition estimate separately.
- SVD(C) describes amplification of coefficient vectors through C. Do not claim its
  singular values are continuous-time finite-horizon energy/reachability measures:
  those require a controllability Gramian and a horizon (later lecture).
- Reachable set from x0=0 is col(C). For nonzero x0, add the freely evolved state;
  do not claim an uncontrollable component is always zero for arbitrary initial states.
- An uncontrollable system can still be stabilizable if its uncontrollable modes are
  stable. The particular lecture counterexample has an uncontrollable +1 mode.

Explorer recommendation (authored): A=[[1,c],[0,2]], B=[b1,b2]^T, bounded sliders.
Presets: uncoupled c=0,B=[0,1]; coupled c=1,same B; two independent actuators B=I2;
book-extra c=0,B=[1,1]. Compute C explicitly, singular values robustly (avoid cancellation),
numerical rank with clearly stated relative tolerance. Include zero input vector case.
Plot B and AB and the reachable line/plane. Two coefficient sliders alpha,beta produce
x=C*[alpha,beta]^T. Label this as a bounded coefficient illustration, NOT continuous-time
unit-energy reachability. Optional precise authored discrete-time interpretation:
x_(k+1)=Ax_k+Bu_k, x0=0 -> x2=AB*u0+B*u1; alpha=u1,beta=u0.
The continuous-time A is not automatically its sampled discrete-time transition matrix;
label this as a separate discrete-time companion with numerically chosen A,B.
For B=I, C has four columns, so either use four coefficients or use a clearly labelled
two-column slice with other coefficients zero, while testing rank on all four columns.

Use six short original step animations: feedback substitution, blocked direction,
coupling multiplication, general controllability matrix, compare rank determinants,
MATLAB/limits. Avoid deriving a feedback controller or Gramian not covered here.
Include worked examples, quiz feedback and lecture/book timestamps. Keep tutor context
accurate and optional (no API key configured). Generated source downloads stay ignored.
