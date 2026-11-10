/*
 * Mathematics for Unit 11, Numerical Methods for ODEs (dependency-free; no DOM).
 * Every state y is an array (scalar problems have length 1).
 *
 * problem(id, params) -> {id, f(t, y), t0, tf, y0, exact(t) | null, dim, hDefault}
 *   exp2, circle, order, flame (params.delta), nearsing, stiffcos, oscillator, vdp (params.mu).
 *
 * step(method, P, t, y, h, s1?) -> one fixed-size step with full stage data for drawing:
 *   {t, y, h, tNew, yNew, stages: [{label, t, y, s}], weights (string), evals, err?, s4?}
 *   methods: euler, midpoint, heun, rk4, bs23, dp45 (one attempt, with error vector), beuler.
 *   For bs23/dp45, err is the error vector (embedded difference); s1 may be passed in (FSAL).
 *
 * integrate(method, P, opts) -> {steps: [...], accepted: [...], rejected, evals, t: [], y: [], failed}
 *   fixed methods: opts.h; adaptive: opts.rtol (default 1e-3), opts.threshold (1e-3),
 *   opts.hmax ((tf - t0)/10), error norm max_i |e_i| / max(|y_i|, |yNew_i|, threshold),
 *   accept iff norm <= rtol, h <- h * min(5, max(0.1, 0.8 (rtol/norm)^(1/(q+1)))) with q = 2 (bs23)
 *   or 4 (dp45); first h = min(hmax, 0.8 rtol^(1/(q+1)) / max(|f0|/max(|y0|, threshold), 1e-4/hmax)).
 *   opts.maxSteps (default 20000) stops runaway integrations (failed: "too many steps").
 * orderExperiment(method, h) -> {v1, v2, ratio, p}: y' = 1/(1+t)^2 on [0, 1], exact 1/2.
 * hermite(t0, y0, f0, t1, y1, f1, t): cubic Hermite interpolant (continuous output).
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  function axpy(y, a, x) { return y.map(function (v, i) { return v + a * x[i]; }); }
  function lin(y, terms) { // y + sum c_j * k_j
    var out = y.slice();
    terms.forEach(function (tk) { if (tk[0] !== 0) for (var i = 0; i < out.length; i++) out[i] += tk[0] * tk[1][i]; });
    return out;
  }

  var PROBLEMS = {
    exp2: function () { return { f: function (t, y) { return [2 * y[0]]; }, t0: 0, tf: 3, y0: [10],
      exact: function (t) { return [10 * Math.exp(2 * t)]; }, hDefault: 1, label: "y' = 2y" }; },
    circle: function () { return { f: function (t, y) { return [Math.sqrt(Math.max(0, 1 - y[0] * y[0]))]; }, t0: 0, tf: Math.PI / 2, y0: [0],
      exact: function (t) { return [Math.sin(t)]; }, hDefault: Math.PI / 32, label: "y' = sqrt(1 - y^2)" }; },
    order: function () { return { f: function (t) { return [1 / ((1 + t) * (1 + t))]; }, t0: 0, tf: 1, y0: [0],
      exact: function (t) { return [t / (1 + t)]; }, hDefault: 0.1, label: "y' = 1/(1+t)^2" }; },
    flame: function (p) { var d = p && p.delta || 0.01; return { f: function (t, y) { return [y[0] * y[0] - y[0] * y[0] * y[0]]; },
      t0: 0, tf: 2 / d, y0: [d], exact: null, hDefault: 1 / (5 * d) / 10, label: "y' = y^2 - y^3" }; },
    nearsing: function () { var a = 0.25, y0 = 15.9; return { f: function (t, y) { return [2 * (a - t) * y[0] * y[0]]; }, t0: 0, tf: 1, y0: [y0],
      exact: function (t) { return [1 / (1 / y0 - 2 * a * t + t * t)]; }, hDefault: 0.01, label: "y' = 2(a - t)y^2" }; },
    stiffcos: function () { return { f: function (t, y) { return [-100 * (y[0] - Math.cos(t)) - Math.sin(t)]; }, t0: 0, tf: 2, y0: [1],
      exact: function (t) { return [Math.cos(t)]; }, hDefault: 0.03, label: "y' = -100(y - cos t) - sin t" }; },
    oscillator: function () { return { f: function (t, y) { return [y[1], -y[0]]; }, t0: 0, tf: 2 * Math.PI, y0: [0, 1],
      exact: function (t) { return [Math.sin(t), Math.cos(t)]; }, hDefault: 2 * Math.PI / 36, label: "x'' + x = 0" }; },
    vdp: function (p) { var mu = p && p.mu || 5; return { f: function (t, y) { return [y[1], mu * (1 - y[0] * y[0]) * y[1] - y[0]]; },
      t0: 0, tf: Math.max(20, 3 * mu), y0: [2, 0], exact: null, hDefault: 0.05, label: "Van der Pol" }; }
  };

  function problem(id, params) {
    if (!PROBLEMS[id]) throw new Error("unknown problem");
    var P = PROBLEMS[id](params || {});
    P.id = id; P.dim = P.y0.length;
    return P;
  }

  // Dormand-Prince tableau
  var DP = {
    c: [0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1],
    a: [[], [1 / 5], [3 / 40, 9 / 40], [44 / 45, -56 / 15, 32 / 9],
        [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
        [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656],
        [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]],
    b: [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0],
    e: [71 / 57600, 0, -71 / 16695, 71 / 1920, -17253 / 339200, 22 / 525, -1 / 40]
  };

  function newtonBE(P, t1, y, h) {
    // solve Y - h f(t1, Y) - y = 0 by Newton with a finite-difference Jacobian
    var Y = axpy(y, h, P.f(t1, y)), n = y.length, evals = 1, converged = false;
    function small(G, Y) { return Math.max.apply(null, G.map(Math.abs)) <= 1e-10 * (1 + Math.max.apply(null, Y.map(Math.abs))); }
    for (var it = 0; it < 25; it++) {
      var F = P.f(t1, Y); evals++;
      var G = Y.map(function (v, i) { return v - h * F[i] - y[i]; });
      if (!G.every(isFinite)) break;
      if (small(G, Y)) { converged = true; break; }
      var J = [];
      for (var j = 0; j < n; j++) {
        var d = 1e-7 * Math.max(1, Math.abs(Y[j])), Yd = Y.slice(); Yd[j] += d;
        var Fd = P.f(t1, Yd); evals++;
        J.push(Fd.map(function (v, i) { return (i === j ? 1 : 0) - h * (v - F[i]) / d; })); // column j of I - hJ
      }
      var dY;
      if (n === 1) dY = [-G[0] / J[0][0]];
      else { // 2x2 solve, J[j][i] = M[i][j]
        var a = J[0][0], b = J[1][0], c = J[0][1], dd = J[1][1], det = a * dd - b * c;
        dY = [-(dd * G[0] - b * G[1]) / det, -(-c * G[0] + a * G[1]) / det];
      }
      Y = Y.map(function (v, i) { return v + dY[i]; });
    }
    if (!converged && Y.every(isFinite)) {
      var Fe = P.f(t1, Y); evals++;
      converged = small(Y.map(function (v, i) { return v - h * Fe[i] - y[i]; }), Y);
    }
    return { Y: Y, evals: evals, converged: converged };
  }

  function step(method, P, t, y, h, s1in) {
    var f = P.f, st = [], out = { t: t, y: y, h: h, tNew: t + h };
    var s1 = s1in || f(t, y);
    var evals = s1in ? 0 : 1;
    if (method === "euler") {
      st.push({ label: "s1", t: t, y: y, s: s1 });
      out.yNew = axpy(y, h, s1); out.weights = "s1";
    } else if (method === "midpoint") {
      var ym = axpy(y, h / 2, s1), s2 = f(t + h / 2, ym); evals++;
      st.push({ label: "s1", t: t, y: y, s: s1 }, { label: "s2", t: t + h / 2, y: ym, s: s2 });
      out.yNew = axpy(y, h, s2); out.weights = "s2";
    } else if (method === "heun") {
      var ye = axpy(y, h, s1), s2h = f(t + h, ye); evals++;
      st.push({ label: "s1", t: t, y: y, s: s1 }, { label: "s2", t: t + h, y: ye, s: s2h });
      out.yNew = lin(y, [[h / 2, s1], [h / 2, s2h]]); out.weights = "(s1 + s2)/2";
    } else if (method === "rk4") {
      var y2 = axpy(y, h / 2, s1), k2 = f(t + h / 2, y2);
      var y3 = axpy(y, h / 2, k2), k3 = f(t + h / 2, y3);
      var y4 = axpy(y, h, k3), k4 = f(t + h, y4); evals += 3;
      st.push({ label: "s1", t: t, y: y, s: s1 }, { label: "s2", t: t + h / 2, y: y2, s: k2 },
              { label: "s3", t: t + h / 2, y: y3, s: k3 }, { label: "s4", t: t + h, y: y4, s: k4 });
      out.yNew = lin(y, [[h / 6, s1], [h / 3, k2], [h / 3, k3], [h / 6, k4]]); out.weights = "(s1 + 2s2 + 2s3 + s4)/6";
    } else if (method === "bs23") {
      var b2y = axpy(y, h / 2, s1), b2 = f(t + h / 2, b2y);
      var b3y = axpy(y, 3 * h / 4, b2), b3 = f(t + 3 * h / 4, b3y);
      var yn = lin(y, [[2 * h / 9, s1], [3 * h / 9, b2], [4 * h / 9, b3]]), b4 = f(t + h, yn); evals += 3;
      st.push({ label: "s1", t: t, y: y, s: s1 }, { label: "s2", t: t + h / 2, y: b2y, s: b2 },
              { label: "s3", t: t + 3 * h / 4, y: b3y, s: b3 }, { label: "s4", t: t + h, y: yn, s: b4 });
      out.yNew = yn; out.s4 = b4; out.weights = "(2s1 + 3s2 + 4s3)/9";
      out.err = y.map(function (_, i) { return h / 72 * (-5 * s1[i] + 6 * b2[i] + 8 * b3[i] - 9 * b4[i]); });
    } else if (method === "dp45") {
      var K = [s1], Ys = [y];
      for (var j = 1; j < 7; j++) {
        var terms = DP.a[j].map(function (aij, m) { return [h * aij, K[m]]; });
        var yj = lin(y, terms); Ys.push(yj); K.push(f(t + DP.c[j] * h, yj)); evals++;
      }
      for (j = 0; j < 7; j++) st.push({ label: "s" + (j + 1), t: t + DP.c[j] * h, y: Ys[j], s: K[j] });
      out.yNew = Ys[6]; out.s4 = K[6]; out.weights = "Dormand-Prince 5th order";
      out.err = y.map(function (_, i) { var s = 0; for (var m = 0; m < 7; m++) s += DP.e[m] * K[m][i]; return h * s; });
    } else if (method === "beuler") {
      var nb = newtonBE(P, t + h, y, h); evals += nb.evals - 1;
      var sEnd = f(t + h, nb.Y); evals++;
      st.push({ label: "s(end)", t: t + h, y: nb.Y, s: sEnd });
      out.yNew = nb.Y; out.weights = "slope at the end (implicit)";
      if (!nb.converged) out.failed = "Newton's method did not converge: no backward Euler step of this size";
    } else throw new Error("unknown method");
    out.stages = st; out.evals = evals;
    return out;
  }

  var LOWER = { bs23: 2, dp45: 4 };

  function integrate(method, P, opts) {
    opts = opts || {};
    var t = P.t0, y = P.y0.slice(), tf = P.tf, maxSteps = opts.maxSteps || 20000;
    var res = { steps: [], accepted: 0, rejected: 0, evals: 0, t: [t], y: [y.slice()], failed: null };
    if (!LOWER[method]) {
      var h = opts.h || P.hDefault, n = Math.max(1, Math.round((tf - t) / h));
      if (n > maxSteps) { res.failed = "too many steps"; n = maxSteps; }
      h = (tf - t) / Math.round((tf - t) / h || 1);
      for (var i = 0; i < n; i++) {
        var s = step(method, P, t, y, h);
        res.evals += s.evals;
        if (s.failed) { s.accepted = false; res.steps.push(s); res.failed = s.failed; break; }
        res.accepted++; s.accepted = true; res.steps.push(s);
        t = s.tNew; y = s.yNew; res.t.push(t); res.y.push(y.slice());
        if (!y.every(isFinite) || Math.max.apply(null, y.map(Math.abs)) > 1e12) { res.failed = "solution blew up"; break; }
      }
      return res;
    }
    var rtol = opts.rtol || 1e-3, thr = opts.threshold || 1e-3, hmax = opts.hmax || (tf - t) / 10, q = LOWER[method];
    var f0 = P.f(t, y); res.evals++;
    var r0 = Math.max.apply(null, f0.map(function (v, i) { return Math.abs(v) / Math.max(Math.abs(y[i]), thr); }));
    var hh = Math.min(hmax, 0.8 * Math.pow(rtol, 1 / (q + 1)) / Math.max(r0, 1e-4 / hmax));
    var s1 = f0;
    while (t < tf) {
      if (res.accepted + res.rejected >= maxSteps) { res.failed = "too many steps"; break; }
      var hmin = 16 * 2.22e-16 * Math.abs(t);
      hh = Math.min(hmax, Math.max(hmin, hh));
      var last = t + 1.1 * hh >= tf;
      if (last) hh = tf - t;
      var sp = step(method, P, t, y, hh, s1);
      if (last) sp.tNew = tf;
      res.evals += sp.evals;
      var yN = sp.yNew;
      var err = Math.max.apply(null, sp.err.map(function (e, i) {
        return Math.abs(e) / Math.max(Math.abs(y[i]), Math.abs(yN[i]), thr);
      }));
      sp.errNorm = err; sp.tol = rtol;
      sp.accepted = err <= rtol;
      res.steps.push(sp);
      if (sp.accepted) {
        res.accepted++; t = sp.tNew; y = yN; s1 = sp.s4;
        res.t.push(t); res.y.push(y.slice());
      } else {
        res.rejected++;
        if (hh <= hmin) { res.failed = "step size too small"; break; }
      }
      var fac = err === 0 ? 5 : Math.min(5, Math.max(0.1, 0.8 * Math.pow(rtol / err, 1 / (q + 1))));
      hh = hh * fac;
    }
    return res;
  }

  // Nested meshes: N and 2N steps on [0, 1], so the step sizes differ by exactly 2.
  function orderExperiment(method, h) {
    var P = problem("order"), N = Math.max(1, Math.round(1 / h)), h1 = 1 / N, h2 = 1 / (2 * N);
    var v1 = integrate(method, P, { h: h1 }).y.slice(-1)[0][0], v2 = integrate(method, P, { h: h2 }).y.slice(-1)[0][0];
    var ratio = (v1 - 0.5) / (v2 - 0.5);
    return { v1: v1, v2: v2, h1: h1, h2: h2, ratio: ratio, p: Math.round(Math.log2(Math.abs(ratio))) };
  }

  function hermite(t0, y0, f0, t1, y1, f1, t) {
    var h = t1 - t0, s = (t - t0) / h, h00 = 2 * s * s * s - 3 * s * s + 1, h10 = s * s * s - 2 * s * s + s,
        h01 = -2 * s * s * s + 3 * s * s, h11 = s * s * s - s * s;
    return y0.map(function (_, i) { return h00 * y0[i] + h10 * h * f0[i] + h01 * y1[i] + h11 * h * f1[i]; });
  }

  return { problem: problem, PROBLEMS: Object.keys(PROBLEMS), step: step, integrate: integrate, orderExperiment: orderExperiment,
           hermite: hermite, DP: DP };
}));
