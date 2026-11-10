/*
 * Mathematics for Unit 3, Second Order Equations (dependency-free; no DOM).
 *
 * Equation: y'' + B y' + C y = f(t)  (A = 1),  y(0) = y0, y'(0) = v0, with C > 0, B >= 0.
 * Inputs f: "none", "cos" (cos w t), "exp" (e^(s t)), "step" (H(t)), "impulse" (delta(t)).
 *
 * roots(B, C)      -> {kind, disc, s1, s2 ({re, im}), wn, zeta, wd}
 *                     kind: "undamped" | "underdamped" | "critical" | "overdamped"
 * nullSolution(B, C, u0, u1) -> function t -> value, the null solution with y(0)=u0, y'(0)=u1
 * particular(p)    -> {f(t), y0, v0, tex, ...}: a particular solution and its start values;
 *                     cos: M, N, G, alpha (or resonance t sin(wt)/(2w) when B = 0, w = wn);
 *                     exp: Y = 1/P(s), or t e^(st)/P'(s) at a simple root, t^2 e^(st)/2 at a double root.
 * response(p)      -> {total(t), particular(t), nul(t), roots, ...}: complete solution.
 *                     impulse: y'(0) jumps by 1 (values for t > 0); step: particular 1/C.
 * impulseResponse(B, C)(t), stepResponse(B, C)(t): g and r from rest.
 * gain(B, C, w)    -> 1/sqrt((C - w^2)^2 + (B w)^2)
 * TOL = 1e-9 decides double roots (|B^2 - 4C| < TOL) and resonance (|P(s)| < TOL, |w - wn| < TOL).
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var TOL = 1e-9;
  var INPUTS = ["none", "cos", "exp", "step", "impulse"];

  function num(x, name) {
    if (typeof x !== "number" || !isFinite(x)) throw new Error("bad parameter " + name);
    return x;
  }

  function roots(B, C) {
    num(B, "B"); num(C, "C");
    if (C <= 0) throw new Error("C must be positive");
    var disc = B * B - 4 * C, wn = Math.sqrt(C), zeta = B / (2 * wn);
    var r = { disc: disc, wn: wn, zeta: zeta, wd: null };
    if (Math.abs(disc) < TOL) {
      r.kind = "critical"; r.s1 = r.s2 = { re: -B / 2, im: 0 };
    } else if (disc > 0) {
      var q = Math.sqrt(disc);
      r.kind = "overdamped"; r.s1 = { re: (-B + q) / 2, im: 0 }; r.s2 = { re: (-B - q) / 2, im: 0 };
    } else {
      var wd = Math.sqrt(-disc) / 2;
      r.kind = B === 0 ? "undamped" : "underdamped"; r.wd = wd;
      r.s1 = { re: -B / 2, im: wd }; r.s2 = { re: -B / 2, im: -wd };
    }
    return r;
  }

  // Null solution with y(0) = u0, y'(0) = u1
  function nullSolution(B, C, u0, u1) {
    var r = roots(B, C);
    if (r.kind === "critical") {
      var s = r.s1.re;
      return function (t) { return Math.exp(s * t) * (u0 + (u1 - s * u0) * t); };
    }
    if (r.kind === "overdamped") {
      var a = r.s1.re, b = r.s2.re, c1 = (u1 - b * u0) / (a - b), c2 = (a * u0 - u1) / (a - b);
      return function (t) { return c1 * Math.exp(a * t) + c2 * Math.exp(b * t); };
    }
    var al = r.s1.re, w = r.wd, k = (u1 - al * u0) / w;
    return function (t) { return Math.exp(al * t) * (u0 * Math.cos(w * t) + k * Math.sin(w * t)); };
  }

  function impulseResponse(B, C) { return nullSolution(B, C, 0, 1); }

  function stepResponse(B, C) {
    var n = nullSolution(B, C, -1 / C, 0);
    return function (t) { return 1 / C + n(t); };
  }

  function gain(B, C, w) { var u = C - w * w, v = B * w; return 1 / Math.sqrt(u * u + v * v); }

  function particular(p) {
    var B = p.B, C = p.C, kind = p.input, out = { input: kind, resonance: false };
    if (kind === "none" || kind === "impulse") {
      out.f = function () { return 0; }; out.y0 = 0; out.v0 = 0; out.tex = "y_p = 0";
    } else if (kind === "step") {
      out.f = function () { return 1 / C; }; out.y0 = 1 / C; out.v0 = 0; out.tex = "y_p = 1/C";
    } else if (kind === "cos") {
      var w = num(p.omega, "omega");
      if (w <= 0) throw new Error("omega must be positive");
      var u = C - w * w, v = B * w, D = u * u + v * v;
      if (D < TOL * TOL || (B === 0 && Math.abs(w - Math.sqrt(C)) < TOL)) {
        out.resonance = true;
        out.f = function (t) { return t * Math.sin(w * t) / (2 * w); };
        out.y0 = 0; out.v0 = 0; out.tex = "y_p = \\dfrac{t\\sin\\omega t}{2\\omega}\\ \\ (\\omega = \\omega_n)";
      } else {
        var M = u / D, N = v / D;
        out.M = M; out.N = N; out.D = D; out.G = 1 / Math.sqrt(D); out.alpha = Math.atan2(N, M);
        out.f = function (t) { return M * Math.cos(w * t) + N * Math.sin(w * t); };
        out.y0 = M; out.v0 = N * w;
        out.tex = "y_p = M\\cos\\omega t + N\\sin\\omega t = G\\cos(\\omega t - \\alpha)";
      }
    } else if (kind === "exp") {
      var s = num(p.s, "s"), P = s * s + B * s + C, dP = 2 * s + B;
      out.P = P; out.dP = dP;
      if (Math.abs(P) < TOL) {
        out.resonance = true;
        if (Math.abs(dP) < TOL) {
          out.f = function (t) { return t * t * Math.exp(s * t) / 2; };
          out.y0 = 0; out.v0 = 0; out.tex = "y_p = \\tfrac12 t^2 e^{st}\\ \\ (\\text{double root})";
        } else {
          out.f = function (t) { return t * Math.exp(s * t) / dP; };
          out.y0 = 0; out.v0 = 1 / dP; out.tex = "y_p = \\dfrac{t\\,e^{st}}{P'(s)}\\ \\ (\\text{resonance})";
        }
      } else {
        out.Y = 1 / P;
        out.f = function (t) { return Math.exp(s * t) / P; };
        out.y0 = 1 / P; out.v0 = s / P; out.tex = "y_p = \\dfrac{e^{st}}{P(s)}";
      }
    } else throw new Error("unknown input");
    return out;
  }

  function response(p) {
    if (!p || INPUTS.indexOf(p.input) < 0) throw new Error("unknown input");
    var B = num(p.B, "B"), C = num(p.C, "C"), y0 = num(p.y0, "y0"), v0 = num(p.v0, "v0");
    if (B < 0) throw new Error("B must be non-negative");
    var r = roots(B, C), part = particular(p);
    var kick = p.input === "impulse" ? 1 : 0;
    var nul = nullSolution(B, C, y0 - part.y0, v0 + kick - part.v0);
    return {
      roots: r, particularInfo: part, resonance: part.resonance,
      particular: part.f, nul: nul,
      total: function (t) { return part.f(t) + nul(t); }
    };
  }

  function sample(f, t0, t1, n) {
    var pts = [];
    for (var i = 0; i <= n; i++) { var t = t0 + (t1 - t0) * i / n; pts.push([t, f(t)]); }
    return pts;
  }

  return { TOL: TOL, INPUTS: INPUTS, roots: roots, nullSolution: nullSolution, impulseResponse: impulseResponse,
           stepResponse: stepResponse, gain: gain, particular: particular, response: response, sample: sample };
}));
