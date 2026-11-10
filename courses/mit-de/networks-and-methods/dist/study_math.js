/*
 * Mathematics for Unit 4, Electrical Networks and Solution Methods (dependency-free; no DOM).
 *
 * impedance(R, L, C, w) -> {re, im, abs, phase, w0}: Z = R + i(wL - 1/(wC)), w0 = 1/sqrt(LC).
 *
 * Undetermined coefficients for y'' + B y' + C y = amp * t^k e^(s t), s complex (s = i w for the
 * cosine family, s = 0 for polynomials). For y = q(t) e^(st):
 *     P(D)(q e^(st)) = e^(st) [P(s) q + P'(s) q' + q''],   P(s) = s^2 + Bs + C, P'(s) = 2s + B.
 * ucSolve(p) finds the polynomial q (complex coefficients a_0..a_d) with P q + P' q' + q'' = t^k:
 *     P(s) != 0            : degree k, solved from the top coefficient down;
 *     P(s) = 0, P'(s) != 0 : multiplicity 1, q = t (b_0 + ... + b_k t^k);
 *     P(s) = P'(s) = 0     : multiplicity 2, q = t^(k+2) / ((k+1)(k+2)).
 * For the cosine family the real particular solution is Re[q(t) e^(iwt)] (P has real coefficients),
 * that is (sum Re a_j t^j) cos wt - (sum Im a_j t^j) sin wt.
 * convolution(B, C, f, t, n): integral_0^t g(t - T) f(T) dT by Simpson's rule (g = impulse response),
 * the solution with zero initial conditions. It differs from y_p by a null solution.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var TOL = 1e-9;

  // complex helpers [re, im]
  function cadd(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
  function csub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function cmul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
  function cscale(a, x) { return [a[0] * x, a[1] * x]; }
  function cdiv(a, b) { var d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; }
  function cabs(a) { return Math.hypot(a[0], a[1]); }

  function impedance(R, L, C, w) {
    var X = w * L - 1 / (w * C);
    return { re: R, im: X, abs: Math.hypot(R, X), phase: Math.atan2(X, R), w0: 1 / Math.sqrt(L * C) };
  }

  function charPoly(B, C, s) {
    var P = cadd(cadd(cmul(s, s), cscale(s, B)), [C, 0]);
    var dP = cadd(cscale(s, 2), [B, 0]);
    return { P: P, dP: dP };
  }

  function ucSolve(p) {
    var B = p.B, C = p.C, k = p.k | 0;
    var s = p.form === "cos" ? [0, p.w] : (p.form === "exp" ? [p.s, 0] : [0, 0]);
    var cp = charPoly(B, C, s), P = cp.P, dP = cp.dP;
    var m, a = [], j;
    for (j = 0; j <= k + 2; j++) a.push([0, 0]);
    if (cabs(P) > TOL) {
      m = 0;
      for (j = k; j >= 0; j--) {
        var rhs = j === k ? [1, 0] : [0, 0];
        rhs = csub(rhs, cscale(cmul(dP, a[j + 1]), j + 1));
        rhs = csub(rhs, cscale(a[j + 2], (j + 2) * (j + 1)));
        a[j] = cdiv(rhs, P);
      }
    } else if (cabs(dP) > TOL) {
      m = 1;
      // coefficient of t^j: P' (j+1) a_{j+1} + (j+2)(j+1) a_{j+2} = delta_{jk};  a_0 = 0
      for (j = k; j >= 0; j--) {
        var r2 = j === k ? [1, 0] : [0, 0];
        r2 = csub(r2, cscale(a[j + 2], (j + 2) * (j + 1)));
        a[j + 1] = cdiv(r2, cscale(dP, j + 1));
      }
    } else {
      m = 2;
      a[k + 2] = [1 / ((k + 1) * (k + 2)), 0];
    }
    var amp = p.amp === undefined ? 1 : p.amp;
    a = a.map(function (c) { return cscale(c, amp); });
    while (a.length > 1 && cabs(a[a.length - 1]) === 0) a.pop();
    function qv(t) {
      var re = 0, im = 0, tp = 1;
      for (var i = 0; i < a.length; i++) { re += a[i][0] * tp; im += a[i][1] * tp; tp *= t; }
      return [re, im];
    }
    var yp = function (t) {
      var q = qv(t), e = [Math.exp(s[0] * t) * Math.cos(s[1] * t), Math.exp(s[0] * t) * Math.sin(s[1] * t)];
      return cmul(q, e)[0];
    };
    var f = function (t) { return amp * Math.pow(t, k) * Math.exp(s[0] * t) * Math.cos(s[1] * t); };
    return { s: s, P: P, dP: dP, multiplicity: m, coeffs: a, yp: yp, f: f, k: k, form: p.form };
  }

  // residual P(D) y_p - f, exact up to rounding: P(D)(q e^(st)) = e^(st) [P(s) q + P'(s) q' + q'']
  function residual(sol, B, C, t) {
    var a = sol.coeffs, n = a.length, q = [0, 0], q1 = [0, 0], q2 = [0, 0];
    for (var j = 0; j < n; j++) {
      q = cadd(q, cscale(a[j], Math.pow(t, j)));
      if (j >= 1) q1 = cadd(q1, cscale(a[j], j * Math.pow(t, j - 1)));
      if (j >= 2) q2 = cadd(q2, cscale(a[j], j * (j - 1) * Math.pow(t, j - 2)));
    }
    var cp = charPoly(B, C, sol.s);
    var inner = cadd(cadd(cmul(cp.P, q), cmul(cp.dP, q1)), q2);
    var s = sol.s, e = [Math.exp(s[0] * t) * Math.cos(s[1] * t), Math.exp(s[0] * t) * Math.sin(s[1] * t)];
    return cmul(inner, e)[0] - sol.f(t);
  }

  function impulseResponse(B, C) {
    var disc = B * B - 4 * C;
    if (Math.abs(disc) < TOL) { var r = -B / 2; return function (t) { return t * Math.exp(r * t); }; }
    if (disc > 0) {
      var q = Math.sqrt(disc), s1 = (-B + q) / 2, s2 = (-B - q) / 2;
      return function (t) { return (Math.exp(s1 * t) - Math.exp(s2 * t)) / (s1 - s2); };
    }
    var al = -B / 2, wd = Math.sqrt(-disc) / 2;
    return function (t) { return Math.exp(al * t) * Math.sin(wd * t) / wd; };
  }

  function convolution(B, C, f, t, n) {
    n = n || 200; if (n % 2) n++;
    if (t <= 0) return 0;
    var g = impulseResponse(B, C), h = t / n, sum = 0;
    for (var i = 0; i <= n; i++) {
      var T = i * h, w = (i === 0 || i === n) ? 1 : (i % 2 ? 4 : 2);
      sum += w * g(t - T) * f(T);
    }
    return sum * h / 3;
  }

  // Human-readable trial form (LaTeX)
  function trialTex(sol) {
    var k = sol.k, m = sol.multiplicity, poly = [];
    var letters = "abcd";
    for (var j = 0; j <= k; j++) poly.push(letters[j] + (j === 0 ? "" : (j === 1 ? "t" : "t^{" + j + "}")));
    var P = "(" + poly.join(" + ") + ")";
    var pre = m === 0 ? "" : (m === 1 ? "t\\," : "t^2\\,");
    if (sol.form === "cos") {
      var poly2 = [];
      for (j = 0; j <= k; j++) poly2.push("c_{" + j + "}" + (j === 0 ? "" : (j === 1 ? "t" : "t^{" + j + "}")));
      return "y_p = " + pre + "\\left[" + P + "\\cos\\omega t + (" + poly2.join(" + ") + ")\\sin\\omega t\\right]";
    }
    if (sol.form === "exp") return "y_p = " + pre + P + "\\,e^{st}";
    return "y_p = " + pre + P;
  }

  return { TOL: TOL, impedance: impedance, charPoly: charPoly, ucSolve: ucSolve, residual: residual,
           impulseResponse: impulseResponse, convolution: convolution, trialTex: trialTex,
           complex: { add: cadd, sub: csub, mul: cmul, div: cdiv, abs: cabs } };
}));
