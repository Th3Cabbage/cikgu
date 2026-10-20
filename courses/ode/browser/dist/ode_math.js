/*
 * Exact solutions of the constant-coefficient homogeneous IVP
 *     a y'' + b y' + c y = 0,   y(0) = y0,   y'(0) = v0.
 *
 * Twin of courses/ode/native/ode_math.py: same argument order, same formulas.
 * Browser: window.ODEMath.  Node (QA): module.exports.
 *
 * With alpha = -b/(2a), k = v0 - alpha*y0 and Delta = b^2 - 4ac:
 *   Delta > 0:  y = e^(alpha t) [y0 cosh(q t) + k sinh(q t)/q],  q = sqrt(Delta)/(2|a|)
 *   Delta = 0:  y = e^(alpha t) (y0 + k t)
 *   Delta < 0:  y = e^(alpha t) [y0 cos(w t) + k sin(w t)/w],    w = sqrt(-Delta)/(2|a|)
 */
(function (root) {
  "use strict";

  var T_MAX = 8;
  // |Delta| below this fraction of max(b^2, |4ac|) counts as a repeated root, for both the
  // label and the formula: inside that band the repeated-root form e^(alpha t)(y0 + k t)
  // replaces the exact near-critical form. That is a small O(q^2 t^2) relative approximation,
  // q ~ sqrt(|Delta|)/(2|a|), because the formulas are continuous across Delta = 0
  // (see courses/ode/native/ode_math.py).
  var CRITICAL_REL_TOL = 1e-9;
  var NICE_BOUNDS = [1, 1.5, 2, 3, 4, 5, 6, 8, 10];

  function validate(values, names) {
    for (var i = 0; i < values.length; i++) {
      if (typeof values[i] !== "number") throw new TypeError(names[i] + " must be a real number");
      if (!isFinite(values[i])) throw new RangeError(names[i] + " must be finite");
    }
  }

  function checkCoefficients(a, b, c) {
    validate([a, b, c], ["a", "b", "c"]);
    if (a === 0) throw new RangeError("a must be nonzero (otherwise the equation is not second order)");
  }

  function discriminant(a, b, c) {
    checkCoefficients(a, b, c);
    return b * b - 4 * a * c;
  }

  function isRepeated(a, b, c) {
    var delta = discriminant(a, b, c);
    var scale = Math.max(b * b, Math.abs(4 * a * c));
    return Math.abs(delta) <= CRITICAL_REL_TOL * scale;
  }

  function parts(t, a, b, c, y0, v0) {
    checkCoefficients(a, b, c);
    validate([t, y0, v0], ["t", "y0", "v0"]);
    var alpha = -b / (2 * a);
    var k = v0 - alpha * y0;
    var delta = b * b - 4 * a * c;
    var e, y, dy;
    if (isRepeated(a, b, c)) {
      e = Math.exp(alpha * t);
      y = e * (y0 + k * t);
      dy = e * (alpha * (y0 + k * t) + k);
      return { y: y, dy: dy };
    }
    if (delta > 0) {
      var q = Math.sqrt(delta) / (2 * Math.abs(a));
      var ePlus = Math.exp((alpha + q) * t);
      var eMinus = Math.exp((alpha - q) * t);
      var ch = 0.5 * (ePlus + eMinus);                    // e^(alpha t) cosh(q t)
      var shQ = Math.abs(q * t) < 0.5
        ? Math.exp(alpha * t) * Math.sinh(q * t) / q      // no cancellation for small q t
        : 0.5 * (ePlus - eMinus) / q;                     // e^(alpha t) sinh(q t) / q
      y = y0 * ch + k * shQ;
      dy = alpha * y + y0 * q * q * shQ + k * ch;
      return { y: y, dy: dy };
    }
    var w = Math.sqrt(-delta) / (2 * Math.abs(a));
    e = Math.exp(alpha * t);
    var cs = Math.cos(w * t), sn = Math.sin(w * t);
    y = e * (y0 * cs + k * sn / w);
    dy = alpha * y + e * (-y0 * w * sn + k * cs);
    return { y: y, dy: dy };
  }

  function solution(t, a, b, c, y0, v0) { return parts(t, a, b, c, y0, v0).y; }
  function derivative(t, a, b, c, y0, v0) { return parts(t, a, b, c, y0, v0).dy; }

  function analyze(a, b, c) {
    checkCoefficients(a, b, c);
    var delta = b * b - 4 * a * c;
    var alpha = -b / (2 * a);
    var kase, rate, roots;
    if (isRepeated(a, b, c)) {
      kase = "repeated"; rate = 0; roots = [[alpha, 0], [alpha, 0]];
    } else if (delta > 0) {
      rate = Math.sqrt(delta) / (2 * Math.abs(a));
      kase = "distinct"; roots = [[alpha + rate, 0], [alpha - rate, 0]];
    } else {
      rate = Math.sqrt(-delta) / (2 * Math.abs(a));
      kase = "complex"; roots = [[alpha, rate], [alpha, -rate]];
    }
    var damping;
    if (!(a > 0 && c > 0 && b >= 0)) damping = "outside lab";
    else if (b === 0) damping = "undamped";
    else damping = { complex: "underdamped", repeated: "critical", distinct: "overdamped" }[kase];
    return { delta: delta, "case": kase, alpha: alpha, rate: rate, roots: roots, damping: damping };
  }

  // Two-decimal label text, identical to ode_math.fmt in Python (no "-0.00").
  function fmt(x) {
    var n = Math.floor(Math.abs(x) * 100 + 0.5);
    return (n !== 0 && x < 0 ? "-" : "") + (n / 100).toFixed(2);
  }

  function rootsText(a, b, c) {
    var info = analyze(a, b, c);
    var r1 = info.roots[0], r2 = info.roots[1];
    if (info["case"] === "complex") {
      if (fmt(r1[0]) === "0.00") return "r = ±" + fmt(r1[1]) + "i";
      return "r = " + fmt(r1[0]) + " ± " + fmt(r1[1]) + "i";
    }
    if (info["case"] === "repeated") return "r = " + fmt(r1[0]) + " (double)";
    return "r₁ = " + fmt(r1[0]) + ",  r₂ = " + fmt(r2[0]);
  }

  var DAMPING_LABELS = {
    "undamped": "Undamped (b = 0): purely imaginary roots, steady oscillation",
    "underdamped": "Underdamped: complex roots, decaying oscillation",
    "critical": "Critically damped: repeated real root",
    "overdamped": "Overdamped: two distinct negative real roots",
    "outside lab": "Outside the lab region (needs a > 0, c > 0, b >= 0)"
  };

  function dampingText(a, b, c) { return DAMPING_LABELS[analyze(a, b, c).damping]; }

  // Symmetric plot half-height: a "nice" value >= 1.1 * maxAbs, never below 1.
  function niceBound(maxAbs) {
    var target = 1.1 * maxAbs;
    if (!isFinite(target) || target <= 1) return 1;
    var scale = Math.pow(10, Math.floor(Math.log10(target)));
    for (var i = 0; i < NICE_BOUNDS.length; i++) {
      if (NICE_BOUNDS[i] * scale >= target - 1e-12) return NICE_BOUNDS[i] * scale;
    }
    return 10 * scale;
  }

  function sample(a, b, c, y0, v0, tMax, n) {
    if (tMax === undefined) tMax = T_MAX;
    if (n === undefined) n = 400;
    var pts = [];
    for (var i = 0; i <= n; i++) {
      var t = tMax * i / n;
      pts.push([t, solution(t, a, b, c, y0, v0)]);
    }
    return pts;
  }

  var api = {
    T_MAX: T_MAX,
    CRITICAL_REL_TOL: CRITICAL_REL_TOL,
    discriminant: discriminant,
    isRepeated: isRepeated,
    solution: solution,
    derivative: derivative,
    analyze: analyze,
    fmt: fmt,
    rootsText: rootsText,
    dampingText: dampingText,
    DAMPING_LABELS: DAMPING_LABELS,
    niceBound: niceBound,
    sample: sample
  };

  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.ODEMath = api;
})(typeof window !== "undefined" ? window : (typeof globalThis !== "undefined" ? globalThis : null));
