/*
 * Mathematics for Unit 2, Nonlinear First Order Equations (dependency-free; no DOM).
 *
 * Autonomous equations y' = f(y):
 *   "logistic"  f = a y - b y^2        steady states 0, a/b
 *   "cubic"     f = y - y^3            steady states -1, 0, 1
 *   "harvest"   f = a y - b y^2 - h    steady states (a +- sqrt(a^2 - 4bh)) / (2b) when a^2 >= 4bh
 *   "square"    f = y^2 - 1            steady states -1, 1
 *
 * model(p) returns {f, df, steady: [{Y, slope, kind}], tex}; kind is "stable" (f'(Y) < 0),
 * "unstable" (f'(Y) > 0) or "undecided" (|f'(Y)| <= TOL, a double root).
 * solve(p, y0, tMax, h) integrates with classical RK4 and stops early (blowup: true) when |y|
 * exceeds LIMIT. logisticExact(a, b, y0, t) is the closed form a / (b + d e^(-a t)).
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var TOL = 1e-9, LIMIT = 50;
  var MODELS = ["logistic", "cubic", "harvest", "square"];

  function num(x, name) {
    if (typeof x !== "number" || !isFinite(x)) throw new Error("bad parameter " + name);
    return x;
  }

  function classify(slope) {
    return Math.abs(slope) <= TOL ? "undecided" : (slope < 0 ? "stable" : "unstable");
  }

  function model(p) {
    if (!p || MODELS.indexOf(p.model) < 0) throw new Error("unknown model");
    var f, df, roots, tex;
    if (p.model === "logistic") {
      var a = num(p.a, "a"), b = num(p.b, "b");
      if (b <= 0) throw new Error("b must be positive");
      f = function (y) { return a * y - b * y * y; };
      df = function (y) { return a - 2 * b * y; };
      roots = a === 0 ? [0] : [0, a / b];
      tex = "y' = " + a + "\\,y - " + b + "\\,y^2";
    } else if (p.model === "cubic") {
      f = function (y) { return y - y * y * y; };
      df = function (y) { return 1 - 3 * y * y; };
      roots = [-1, 0, 1];
      tex = "y' = y - y^3";
    } else if (p.model === "harvest") {
      var A = num(p.a, "a"), B = num(p.b, "b"), h = num(p.h, "h");
      if (B <= 0) throw new Error("b must be positive");
      f = function (y) { return A * y - B * y * y - h; };
      df = function (y) { return A - 2 * B * y; };
      var disc = A * A - 4 * B * h;
      if (Math.abs(disc) <= TOL) roots = [A / (2 * B)];
      else if (disc < 0) roots = [];
      else { var r = Math.sqrt(disc); roots = [(A - r) / (2 * B), (A + r) / (2 * B)]; }
      tex = "y' = " + A + "\\,y - " + B + "\\,y^2 - " + h;
    } else {
      f = function (y) { return y * y - 1; };
      df = function (y) { return 2 * y; };
      roots = [-1, 1];
      tex = "y' = y^2 - 1";
    }
    roots.sort(function (u, v) { return u - v; });
    var steady = roots.map(function (Y) { var s = df(Y); return { Y: Y, slope: s, kind: classify(s) }; });
    // a double root has f'(Y) = 0 analytically; report it as undecided even with rounding
    if (p.model === "harvest" && roots.length === 1) steady[0].slope = 0, steady[0].kind = "undecided";
    return { model: p.model, f: f, df: df, steady: steady, tex: tex };
  }

  function rk4(f, y0, tMax, h) {
    num(y0, "y0"); num(tMax, "tMax");
    h = h || 0.01;
    var n = Math.max(1, Math.round(tMax / h)); h = tMax / n;
    var pts = [[0, y0]], y = y0, blowup = false;
    for (var i = 1; i <= n; i++) {
      var k1 = f(y), k2 = f(y + h * k1 / 2), k3 = f(y + h * k2 / 2), k4 = f(y + h * k3);
      y = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6;
      if (!isFinite(y) || Math.abs(y) > LIMIT) { blowup = true; break; }
      pts.push([i * h, y]);
    }
    return { points: pts, blowup: blowup };
  }

  function solve(p, y0, tMax, h) { return rk4(model(p).f, y0, tMax, h); }

  // Closed form a / (b + d e^(-at)). The denominator is monotone in t; if it changes sign
  // between 0 and t the solution has blown up before t, and NaN is returned (no value exists
  // on the solution's interval of existence).
  function logisticExact(a, b, y0, t) {
    if (y0 === 0) return 0;
    var d = a / y0 - b;
    var den0 = b + d, den = b + d * Math.exp(-a * t);
    if (den === 0 || (den0 > 0) !== (den > 0)) return NaN;
    return a / den;
  }

  return { TOL: TOL, LIMIT: LIMIT, MODELS: MODELS, model: model, classify: classify, rk4: rk4, solve: solve,
           logisticExact: logisticExact };
}));
