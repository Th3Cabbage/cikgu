/*
 * Mathematics for the Linearizing Around a Fixed Point explorer (dependency-free).
 *
 * Original nonlinear pendulum (Brunton & Kutz 2017 preprint, Eqs. 8.23-8.25), state x = (theta, omega):
 *   theta' = omega,   omega' = -q sin(theta) - d omega + u,     q = g/L > 0
 * u is the book's normalized angular-acceleration input (not a physical torque without units/scaling).
 * d >= 0 is viscous damping: the lecture adds it (board delta, MATLAB d = 0.1); the book example has d = 0.
 *
 * Fixed points used: theta_bar = 0 ("down") or pi ("up"), omega_bar = 0, u_bar = 0, so f(x_bar, u_bar) = 0.
 * Perturbations eta = theta - theta_bar, nu = omega, delta_u = u. Jacobians (Eqs. 8.7-8.10):
 *   A = df/dx = [[0, 1], [-q cos(theta_bar), -d]],  B = df/du = [0, 1]^T,  C = [1, 0], D = 0 (angle output).
 * Local linear model: eta' = nu, nu' = -k eta - d nu + delta_u with k = q cos(theta_bar) = +q (down) or -q (up).
 * The physical angle is always theta = theta_bar + eta and is never reduced modulo 2 pi.
 *
 * Numerics
 *   nonlinear: classical RK4 with step h <= H_MAX = 0.004, integrated in perturbation coordinates using the
 *     exact identity sin(theta_bar + eta) = cos(theta_bar) sin(eta) for theta_bar in {0, pi}, so the exact
 *     equilibrium stays exactly at rest (no sin(pi) round-off residual).
 *   linear: closed form, independent of RK4. For any real 2x2 A with a = tr(A)/2 and disc = a^2 - det(A),
 *     (A - aI)^2 = disc I, so e^{At} = e^{at} (C(t) I + S(t) (A - aI)) with C = cosh(sqrt(disc) t),
 *     S = sinh(sqrt(disc) t)/sqrt(disc) (cos/sin for disc < 0, series near disc t^2 = 0: no case split at
 *     critical damping). The constant-input response is (delta_u/k)(1 - e^{at}(C - aS)) in eta and
 *     (delta_u) e^{at} S in nu, using k = det A = +-q, which is never zero because q > 0.
 * UMD: window.StudyMath in the browser, module.exports in Node (QA scripts).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var H_MAX = 0.004;
  var T_MAX = 12;
  var EQUILIBRIA = Object.freeze({ down: 0, up: Math.PI });

  // Slider ranges (also used to validate saved settings and presets).
  var PARAMS = Object.freeze({
    eta0: Object.freeze({ min: -1.5, max: 1.5, step: 0.01, default: 0.2 }),
    nu0: Object.freeze({ min: -1.5, max: 1.5, step: 0.01, default: 0 }),
    q: Object.freeze({ min: 0.25, max: 4, step: 0.05, default: 1 }),
    du: Object.freeze({ min: -0.5, max: 0.5, step: 0.01, default: 0 }),
    d: Object.freeze({ min: 0, max: 4, step: 0.05, default: 0.1 }),
    t: Object.freeze({ min: 0, max: T_MAX, step: 0.01, default: 0 })
  });
  var KEYS = Object.freeze(["eta0", "nu0", "q", "du", "d", "t"]);

  function freezeAll(o) { Object.freeze(o); Object.keys(o).forEach(function (k) { if (o[k] && typeof o[k] === "object") Object.freeze(o[k]); }); return o; }
  var PRESETS = Object.freeze([
    freezeAll({ id: "lecture-down", label: "Lecture: down, d = 0.1", eq: "down", eta0: 0.2, nu0: 0, q: 1, du: 0, d: 0.1,
      note: "The lecture's MATLAB numbers: $q = 1$, $d = 0.1$ give $\\lambda = -0.05 \\pm 0.9987i$. A small kick oscillates inside a slowly decaying envelope, and the two models stay close." }),
    freezeAll({ id: "lecture-up", label: "Lecture: up, d = 0.1", eq: "up", eta0: 0.05, nu0: 0, q: 1, du: 0, d: 0.1,
      note: "The lecture's up matrix: $\\lambda = -1.0512$ and $0.9512$, a saddle. Both models first grow together; once the angle is no longer small the linear model keeps growing while the real pendulum swings through the bottom." }),
    freezeAll({ id: "undamped-down", label: "Undamped down (book)", eq: "down", eta0: 0.1, nu0: 0, q: 1, du: 0, d: 0,
      note: "The book's undamped pendulum ($d = 0$): $\\lambda = \\pm i$, a linear center. The verdict comes from the conserved energy, not from the eigenvalues alone." }),
    freezeAll({ id: "large-down", label: "Large swing, down", eq: "down", eta0: 1.4, nu0: 0, q: 1, du: 0, d: 0.1,
      note: "A large swing: $\\sin\\eta$ is noticeably smaller than $\\eta$, so the true period is longer and the linear model drifts out of phase." }),
    freezeAll({ id: "overdamped-down", label: "Overdamped down, d = 3", eq: "down", eta0: 0.5, nu0: 0, q: 1, du: 0, d: 3,
      note: "With $d = 3 > 2\\sqrt q$ both eigenvalues are real and negative: the pendulum creeps back without oscillating. Damping does not always give complex eigenvalues." }),
    freezeAll({ id: "exact-up", label: "Exactly at equilibrium", eq: "up", eta0: 0, nu0: 0, q: 1, du: 0, d: 0.1,
      note: "Starting exactly at the fixed point with no input: $f(\\bar x, \\bar u) = 0$, so both models stay at rest. Any tiny offset from the inverted position would grow." })
  ]);

  function isNum(v) { return typeof v === "number" && isFinite(v); }
  function req(v, name) { if (!isNum(v)) throw new RangeError(name + " must be a finite number"); return v; }
  function reqQ(q) { req(q, "q"); if (!(q > 0)) throw new RangeError("q = g/L must be positive"); return q; }
  function reqD(d) { d = d === undefined ? 0 : req(d, "d"); if (d < 0) throw new RangeError("damping d must be >= 0"); return d; }
  function thetaBarOf(eq) {
    if (!Object.prototype.hasOwnProperty.call(EQUILIBRIA, eq)) throw new RangeError("equilibrium must be 'down' or 'up'");
    return EQUILIBRIA[eq];
  }

  // Validated, frozen parameter set {eq, thetaBar, eta0, nu0, q, du, d}; throws RangeError otherwise.
  // Ranges are physical validity (q > 0, d >= 0, finite); slider ranges are enforced by the explorer.
  function params(p) {
    if (!p || typeof p !== "object") throw new RangeError("parameters must be an object");
    return Object.freeze({
      eq: p.eq, thetaBar: thetaBarOf(p.eq),
      eta0: req(p.eta0, "eta0"), nu0: req(p.nu0, "nu0"), q: reqQ(p.q),
      du: p.du === undefined ? 0 : req(p.du, "du"), d: reqD(p.d)
    });
  }

  // Original nonlinear vector field in absolute coordinates x = [theta, omega].
  function f(x, u, q, d) {
    reqQ(q); d = reqD(d); req(u, "u"); req(x[0], "theta"); req(x[1], "omega");
    return [x[1], -q * Math.sin(x[0]) - d * x[1] + u];
  }

  // Jacobians at an arbitrary (theta, omega): f_x and f_u (Eq. 8.8 applied to the pendulum).
  function jacobianAt(theta, q, d) {
    reqQ(q); d = reqD(d); req(theta, "theta");
    return { A: [[0, 1], [-q * Math.cos(theta), -d]], B: [[0], [1]] };
  }

  // Local linear model at the named fixed point. cos(theta_bar) is exactly +1 or -1.
  function linearization(eq, q, d) {
    var tb = thetaBarOf(eq); reqQ(q); d = reqD(d);
    var c = eq === "down" ? 1 : -1;
    return {
      thetaBar: tb, k: c * q,
      A: [[0, 1], [-c * q, -d]], B: [[0], [1]], C: [[1, 0]], D: [[0]]
    };
  }

  // Eigenvalues of a real 2x2 matrix, sorted by real part then imaginary part (descending).
  function eigen2(A) {
    var tr = A[0][0] + A[1][1], det = A[0][0] * A[1][1] - A[0][1] * A[1][0];
    var a = tr / 2, disc = a * a - det;
    var v;
    if (disc >= 0) {
      var r = Math.sqrt(disc);
      // stable root pair: avoid cancellation for the smaller-magnitude root
      var big = a >= 0 ? a + r : a - r, small = big !== 0 ? det / big : 0;
      v = [{ re: big, im: 0 }, { re: small, im: 0 }];
    } else {
      var w = Math.sqrt(-disc);
      v = [{ re: a, im: w }, { re: a, im: -w }];
    }
    return v.sort(function (p, s) { return s.re - p.re || s.im - p.im; });
  }

  // What the Jacobian says, and what can actually be concluded about the nonlinear fixed point.
  //   linear:    "center" | "saddle" | "focus" | "critical" | "node"
  //   nonlinear: "lyapunov" (stable, not asymptotically), "asymptotic", "unstable"
  //   byLinearization: false when eigenvalues lie on the imaginary axis (Jacobian test inconclusive in general).
  function classify(eq, q, d) {
    var L = linearization(eq, q, d);
    d = L.A[1][1] === 0 ? 0 : -L.A[1][1];
    var ev = eigen2(L.A);
    if (eq === "up") return { linear: "saddle", nonlinear: "unstable", byLinearization: true, eig: ev };
    if (d === 0) return { linear: "center", nonlinear: "lyapunov", byLinearization: false, eig: ev };
    var disc = d * d - 4 * q;
    var kind = Math.abs(disc) <= 1e-12 * Math.max(1, d * d) ? "critical" : disc < 0 ? "focus" : "node";
    return { linear: kind, nonlinear: "asymptotic", byLinearization: true, eig: ev };
  }

  // Conserved energy of the undamped, unforced pendulum (per unit m L^2): E = omega^2/2 + q (1 - cos theta).
  function energy(theta, omega, q) { reqQ(q); return 0.5 * omega * omega + q * (1 - Math.cos(theta)); }

  // ---- nonlinear (RK4 in perturbation coordinates)
  function rhsPert(c, q, d, du, eta, nu) { return [nu, -q * c * Math.sin(eta) - d * nu + du]; }
  function rk4Step(c, q, d, du, eta, nu, h) {
    var k1 = rhsPert(c, q, d, du, eta, nu);
    var k2 = rhsPert(c, q, d, du, eta + 0.5 * h * k1[0], nu + 0.5 * h * k1[1]);
    var k3 = rhsPert(c, q, d, du, eta + 0.5 * h * k2[0], nu + 0.5 * h * k2[1]);
    var k4 = rhsPert(c, q, d, du, eta + h * k3[0], nu + h * k3[1]);
    return [eta + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), nu + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])];
  }
  function advance(P, y, dt) {
    var n = Math.max(1, Math.ceil(dt / H_MAX - 1e-9)), h = dt / n, c = P.eq === "down" ? 1 : -1;
    for (var i = 0; i < n; i++) y = rk4Step(c, P.q, P.d, P.du, y[0], y[1], h);
    if (!isNum(y[0]) || !isNum(y[1])) throw new RangeError("nonlinear solution became non-finite");
    return y;
  }
  function pack(P, t, eta, nu) {
    return Object.freeze({ t: t, eta: eta, nu: nu, theta: P.thetaBar + eta, omega: nu });
  }
  function reqT(t) { req(t, "t"); if (t < 0) throw new RangeError("t must be >= 0"); return t; }

  function nonlinearState(p, t) {
    var P = params(p); reqT(t);
    var y = t > 0 ? advance(P, [P.eta0, P.nu0], t) : [P.eta0, P.nu0];
    return pack(P, t, y[0], y[1]);
  }
  function grid(tMax, n) {
    reqT(tMax);
    if (!(n >= 1 && n === Math.floor(n))) throw new RangeError("n must be a positive integer");
    var g = []; for (var i = 0; i <= n; i++) g.push(tMax * i / n); return g;
  }
  function nonlinearTrajectory(p, tMax, n) {
    var P = params(p), ts = grid(tMax, n), y = [P.eta0, P.nu0], out = [pack(P, 0, y[0], y[1])];
    for (var i = 1; i < ts.length; i++) { y = advance(P, y, ts[i] - ts[i - 1]); out.push(pack(P, ts[i], y[0], y[1])); }
    return Object.freeze(out);
  }

  // ---- linear (closed form)
  // C(t) = cosh(r t) / cos(w t), S(t) = sinh(r t)/r / sin(w t)/w, with a series when |disc| t^2 is small.
  function cs(disc, t) {
    var z = disc * t * t;
    if (Math.abs(z) < 1e-3) {
      // C = sum z^n/(2n)!, S = t sum z^n/(2n+1)!
      var C = 1 + z / 2 * (1 + z / 12 * (1 + z / 30 * (1 + z / 56)));
      var S = t * (1 + z / 6 * (1 + z / 20 * (1 + z / 42 * (1 + z / 72))));
      return [C, S];
    }
    if (disc > 0) { var r = Math.sqrt(disc); return [Math.cosh(r * t), Math.sinh(r * t) / r]; }
    var w = Math.sqrt(-disc); return [Math.cos(w * t), Math.sin(w * t) / w];
  }
  // e^{At} for any real 2x2 A.
  function expm2(A, t) {
    req(t, "t");
    var a = (A[0][0] + A[1][1]) / 2, det = A[0][0] * A[1][1] - A[0][1] * A[1][0], disc = a * a - det;
    var e = Math.exp(a * t), c = cs(disc, t), C = c[0], S = c[1];
    return [[e * (C + S * (A[0][0] - a)), e * S * A[0][1]], [e * S * A[1][0], e * (C + S * (A[1][1] - a))]];
  }

  function linearState(p, t) {
    var P = params(p); reqT(t);
    var L = linearization(P.eq, P.q, P.d), E = expm2(L.A, t);
    var eta = E[0][0] * P.eta0 + E[0][1] * P.nu0, nu = E[1][0] * P.eta0 + E[1][1] * P.nu0;
    if (P.du !== 0) {
      var a = -P.d / 2, disc = a * a - L.k, c = cs(disc, t), e = Math.exp(a * t);
      eta += P.du / L.k * (1 - e * (c[0] - a * c[1]));
      nu += P.du * e * c[1];
    }
    if (!isNum(eta) || !isNum(nu)) throw new RangeError("linear solution became non-finite");
    return pack(P, t, eta, nu);
  }
  function linearTrajectory(p, tMax, n) {
    params(p);
    return Object.freeze(grid(tMax, n).map(function (t) { return linearState(p, t); }));
  }

  // Nonlinear and linear at one time; the angle error uses absolute angles, never reduced mod 2 pi.
  function compare(p, t) {
    var nl = nonlinearState(p, t), lin = linearState(p, t);
    return Object.freeze({ t: t, nonlinear: nl, linear: lin, angleError: nl.theta - lin.theta, rateError: nl.omega - lin.omega });
  }

  return Object.freeze({
    H_MAX: H_MAX, T_MAX: T_MAX, EQUILIBRIA: EQUILIBRIA, PARAMS: PARAMS, KEYS: KEYS, PRESETS: PRESETS,
    params: params, f: f, jacobianAt: jacobianAt, linearization: linearization, eigen2: eigen2, classify: classify,
    energy: energy, expm2: expm2, nonlinearState: nonlinearState, nonlinearTrajectory: nonlinearTrajectory,
    linearState: linearState, linearTrajectory: linearTrajectory, compare: compare
  });
}));
