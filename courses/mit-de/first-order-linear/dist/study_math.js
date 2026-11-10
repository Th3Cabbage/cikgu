/*
 * Mathematics for Unit 1, First Order Linear Equations (dependency-free; no DOM).
 *
 * Equation: y' = a y + q(t), y(0) = y0, with one input family q of amplitude A:
 *   "constant"  q = A
 *   "exp"       q = A e^(s t)
 *   "cos"       q = A cos(w t)
 *   "step"      q = A H(t - T)
 *   "delta"     q = A delta(t - T)   (y jumps by A at t = T; values at t = T are after the jump)
 *
 * response(p) returns closed-form functions
 *   nullPart(t)    = y0 e^(a t)                 (solves y' = a y with the right y(0))
 *   drivenPart(t)  = very particular solution    (solves the full equation, starts at 0)
 *   total(t)       = nullPart + drivenPart
 * plus metadata: the formula used (LaTeX), resonance flag, gain G and lag alpha for "cos",
 * and the steady state for decaying constant/step inputs.
 *
 * Numerics: (e^(x) - 1)/x is evaluated as expm1(x)/x (phi), so (e^(st) - e^(at))/(s - a) =
 * t e^(at) phi((s - a) t) is accurate near resonance and equals t e^(at) at s = a exactly.
 * The resonance flag uses |s - a| < RES_TOL = 1e-9.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var RES_TOL = 1e-9;
  var KINDS = ["constant", "exp", "cos", "step", "delta"];

  function expm1(x) { return Math.expm1 ? Math.expm1(x) : (Math.abs(x) < 1e-5 ? x + x * x / 2 + x * x * x / 6 : Math.exp(x) - 1); }
  // phi(x) = (e^x - 1)/x, phi(0) = 1
  function phi(x) { return Math.abs(x) < 1e-12 ? 1 + x / 2 : expm1(x) / x; }

  // Polar data of the cosine response: M cos + N sin = G cos(w t - alpha)
  function cosineResponse(a, w) {
    var d = w * w + a * a;
    var M = -a / d, N = w / d;
    return { M: M, N: N, G: 1 / Math.sqrt(d), alpha: Math.atan2(w, -a) };
  }

  function check(p) {
    if (!p || KINDS.indexOf(p.kind) < 0) throw new Error("unknown input kind");
    ["a", "y0", "amp"].forEach(function (k) {
      if (typeof p[k] !== "number" || !isFinite(p[k])) throw new Error("bad parameter " + k);
    });
  }

  function response(p) {
    check(p);
    var a = p.a, y0 = p.y0, A = p.amp, kind = p.kind;
    var out = { kind: kind, a: a, y0: y0, amp: A, resonance: false, steady: null, cos: null };
    out.nullPart = function (t) { return y0 * Math.exp(a * t); };
    var driven, tex;
    if (kind === "constant") {
      driven = function (t) { return A * t * phi(a * t); };
      tex = Math.abs(a) < RES_TOL ? "y_{vp} = A\\,t" : "y_{vp} = \\dfrac{A\\,(e^{at} - 1)}{a}";
      if (a < 0) out.steady = -A / a;
    } else if (kind === "exp") {
      var s = p.s;
      if (typeof s !== "number" || !isFinite(s)) throw new Error("bad parameter s");
      out.s = s;
      out.resonance = Math.abs(s - a) < RES_TOL;
      driven = function (t) { return A * t * Math.exp(a * t) * phi((s - a) * t); };
      tex = out.resonance ? "y_{vp} = A\\,t\\,e^{at}\\quad(s = a:\\ \\text{resonance})"
                          : "y_{vp} = \\dfrac{A\\,(e^{st} - e^{at})}{s - a}";
    } else if (kind === "cos") {
      var w = p.omega;
      if (typeof w !== "number" || !isFinite(w) || w <= 0) throw new Error("bad parameter omega");
      var c = cosineResponse(a, w);
      out.omega = w;
      out.cos = c;
      // steady oscillation minus its own null-type start value, so the part starts at 0
      driven = function (t) { return A * (c.M * Math.cos(w * t) + c.N * Math.sin(w * t) - c.M * Math.exp(a * t)); };
      out.steadyPart = function (t) { return A * c.G * Math.cos(w * t - c.alpha); };
      tex = "y_{vp} = A\\left[G\\cos(\\omega t - \\alpha) - M e^{at}\\right],\\ G = \\tfrac{1}{\\sqrt{a^2+\\omega^2}}";
    } else {
      var T = p.T;
      if (typeof T !== "number" || !isFinite(T) || T < 0) throw new Error("bad parameter T");
      out.T = T;
      if (kind === "step") {
        driven = function (t) { var u = t - T; return u < 0 ? 0 : A * u * phi(a * u); };
        tex = Math.abs(a) < RES_TOL ? "y_{vp} = A\\,(t - T)\\ \\ (t \\ge T)"
                                    : "y_{vp} = \\dfrac{A\\,(e^{a(t-T)} - 1)}{a}\\ \\ (t \\ge T)";
        if (a < 0) out.steady = -A / a;
      } else {
        driven = function (t) { var u = t - T; return u < 0 ? 0 : A * Math.exp(a * u); };
        tex = "y_{vp} = A\\,H(t - T)\\,e^{a(t-T)}";
      }
    }
    out.drivenPart = driven;
    out.total = function (t) { return out.nullPart(t) + driven(t); };
    out.tex = tex;
    return out;
  }

  // Input q(t) itself (delta returns 0 away from T; the impulse is drawn separately)
  function input(p, t) {
    var A = p.amp;
    switch (p.kind) {
      case "constant": return A;
      case "exp": return A * Math.exp(p.s * t);
      case "cos": return A * Math.cos(p.omega * t);
      case "step": return t >= p.T ? A : 0;
      default: return 0;
    }
  }

  function sample(f, t0, t1, n) {
    var pts = [];
    for (var i = 0; i <= n; i++) { var t = t0 + (t1 - t0) * i / n; pts.push([t, f(t)]); }
    return pts;
  }

  // Integrating factor family of Section 8: a(t) = 2t, y(t) = e^(t^2) y0 + integral_0^t e^(t^2 - s^2) q(s) ds
  function growthFactor2t(s, t) { return Math.exp(t * t - s * s); }

  return { RES_TOL: RES_TOL, KINDS: KINDS, phi: phi, cosineResponse: cosineResponse, response: response,
           input: input, sample: sample, growthFactor2t: growthFactor2t };
}));
