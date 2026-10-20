/*
 * Exact math for the Stability and Eigenvalues explorer (closed forms, no eigensolver, no ODE integration).
 *
 * Every real 2x2 matrix is similar to one of three real canonical forms J; the explorer chooses J and
 * a change of basis T = [[1, s], [0, 1]] (det T = 1, always invertible) and builds A = T J T^-1:
 *   "real"    J = diag(l1, l2)            e^{Jt} = diag(e^{l1 t}, e^{l2 t})        (l1 = l2 is A = l1 I)
 *   "complex" J = [[a, -b], [b, a]], b > 0 e^{Jt} = e^{at} [[cos bt, -sin bt], [sin bt, cos bt]]   (a +- ib)
 *   "jordan"  J = [[l, 1], [0, l]]         e^{Jt} = e^{lt} [[1, t], [0, 1]]          (defective)
 * so x(t) = T e^{Jt} T^-1 x0 is exact. Sampling with step dt gives the discrete-time system
 * x_{k+1} = Ad x_k, Ad = e^{A dt}, whose eigenvalues are e^{lambda dt}.
 * The classification covers all initial states and the boundary cases: a semisimple eigenvalue on the
 * imaginary axis (or unit circle) is Lyapunov stable but not asymptotically stable; a defective one is unstable.
 * UMD: window.StudyMath in the browser, module.exports for the QA scripts (node).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var TOL = 1e-9;
  var KINDS = ["real", "complex", "jordan"];

  function matmul(P, Q) {
    return [[P[0][0] * Q[0][0] + P[0][1] * Q[1][0], P[0][0] * Q[0][1] + P[0][1] * Q[1][1]],
            [P[1][0] * Q[0][0] + P[1][1] * Q[1][0], P[1][0] * Q[0][1] + P[1][1] * Q[1][1]]];
  }
  function matvec(P, v) { return [P[0][0] * v[0] + P[0][1] * v[1], P[1][0] * v[0] + P[1][1] * v[1]]; }

  function basis(s) { return { T: [[1, s], [0, 1]], Tinv: [[1, -s], [0, 1]] }; }

  // The real canonical form chosen in the explorer.
  function canon(p) {
    if (p.kind === "complex") return [[p.a, -p.b], [p.b, p.a]];
    if (p.kind === "jordan") return [[p.lj, 1], [0, p.lj]];
    return [[p.l1, 0], [0, p.l2]];
  }

  function expCanon(p, t) {
    if (p.kind === "complex") {
      var e = Math.exp(p.a * t), c = Math.cos(p.b * t), s = Math.sin(p.b * t);
      return [[e * c, -e * s], [e * s, e * c]];
    }
    if (p.kind === "jordan") { var ej = Math.exp(p.lj * t); return [[ej, t * ej], [0, ej]]; }
    return [[Math.exp(p.l1 * t), 0], [0, Math.exp(p.l2 * t)]];
  }

  function system(p) {
    var b = basis(p.s), J = canon(p);
    return { T: b.T, Tinv: b.Tinv, J: J, A: matmul(matmul(b.T, J), b.Tinv) };
  }

  // e^{At} = T e^{Jt} T^-1.
  function expA(p, t) { var b = basis(p.s); return matmul(matmul(b.T, expCanon(p, t)), b.Tinv); }

  // Continuous-time eigenvalues {re, im}, and whether A is defective (non-semisimple).
  function eigen(p) {
    if (p.kind === "complex") return { values: [{ re: p.a, im: p.b }, { re: p.a, im: -p.b }], defective: false };
    if (p.kind === "jordan") return { values: [{ re: p.lj, im: 0 }, { re: p.lj, im: 0 }], defective: true };
    return { values: [{ re: p.l1, im: 0 }, { re: p.l2, im: 0 }], defective: false };
  }

  // Discrete-time eigenvalues of Ad = e^{A dt}: e^{lambda dt} = e^{a dt}(cos b dt + i sin b dt).
  function eigenDiscrete(p, dt) {
    var ev = eigen(p);
    return { values: ev.values.map(function (l) {
      var r = Math.exp(l.re * dt);
      return { re: r * Math.cos(l.im * dt), im: r * Math.sin(l.im * dt), r: r, theta: l.im * dt };
    }), defective: ev.defective };
  }

  // Stability of the zero state for ALL initial states:
  //   "asymptotic" every solution tends to 0;  "lyapunov" every solution stays bounded but some do not
  //   tend to 0 (semisimple eigenvalue on the boundary);  "unstable" some solution is unbounded.
  // `margin(v)` is Re(lambda) (continuous) or |lambda| - 1 (discrete). In 2x2 a defective matrix has a
  // single repeated eigenvalue, so "defective on the boundary" means that eigenvalue is on the boundary.
  function verdict(values, defective, margin) {
    var worst = Math.max.apply(null, values.map(margin));
    if (worst < -TOL) return "asymptotic";
    if (worst > TOL) return "unstable";
    return defective ? "unstable" : "lyapunov";
  }
  function classifyContinuous(p) {
    var ev = eigen(p);
    return verdict(ev.values, ev.defective, function (v) { return v.re; });
  }
  function classifyDiscrete(p, dt) {
    var ev = eigenDiscrete(p, dt);
    return verdict(ev.values, ev.defective, function (v) { return Math.hypot(v.re, v.im) - 1; });
  }

  // Behaviour of the ONE solution starting at x0 (as t -> infinity), from its modal coordinates z0 = T^-1 x0:
  // "rest" (x0 = 0), "decays", "bounded" (stays bounded, does not tend to 0), or "grows".
  function startBehaviour(p) {
    var z = matvec(basis(p.s).Tinv, [p.x1, p.x2]);
    var on = [Math.abs(z[0]) > TOL, Math.abs(z[1]) > TOL];
    if (!on[0] && !on[1]) return "rest";
    function bySign(l, polynomial) {
      if (l < -TOL) return "decays";
      if (l > TOL) return "grows";
      return polynomial ? "grows" : "bounded";
    }
    if (p.kind === "complex") return bySign(p.a, false);
    if (p.kind === "jordan") return bySign(p.lj, on[1]);   // z1(t) = e^{lt}(z1 + t z2): linear drift if l = 0, z2 != 0
    var rates = [];
    if (on[0]) rates.push(p.l1);
    if (on[1]) rates.push(p.l2);
    return bySign(Math.max.apply(null, rates), false);
  }

  function state(p, t) { return matvec(expA(p, t), [p.x1, p.x2]); }

  function trajectory(p, tMax, n) {
    var out = [];
    for (var i = 0; i <= n; i++) { var t = tMax * i / n; out.push({ t: t, x: state(p, t) }); }
    return out;
  }

  // Discrete-time samples by iterating x_{k+1} = Ad x_k (not by evaluating x(k dt)).
  function samples(p, dt, tMax) {
    var Ad = expA(p, dt), x = [p.x1, p.x2], out = [{ k: 0, t: 0, x: x }];
    var n = Math.floor(tMax / dt + 1e-9);
    for (var k = 1; k <= n; k++) { x = matvec(Ad, x); out.push({ k: k, t: k * dt, x: x }); }
    return out;
  }

  // Powers lambda~^k = r^k e^{i k theta} of one discrete eigenvalue, k = 0..n.
  function powers(mu, n) {
    var out = [];
    for (var k = 0; k <= n; k++) {
      var rk = Math.pow(mu.r, k);
      out.push([rk * Math.cos(k * mu.theta), rk * Math.sin(k * mu.theta)]);
    }
    return out;
  }

  return { TOL: TOL, KINDS: KINDS, matmul: matmul, matvec: matvec, basis: basis, canon: canon, expCanon: expCanon,
           system: system, expA: expA, eigen: eigen, eigenDiscrete: eigenDiscrete, classifyContinuous: classifyContinuous,
           classifyDiscrete: classifyDiscrete, startBehaviour: startBehaviour, state: state, trajectory: trajectory,
           samples: samples, powers: powers };
}));
