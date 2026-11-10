/*
 * Mathematics for Unit 5, The Laplace Transform (dependency-free; no DOM).
 *
 * build(p) forms Y(s) = N(s) / D(s) for
 *   first order  y' - a y = f:            Y = [F(s) + y0] / (s - a)
 *   second order y'' + B y' + C y = f:    Y = [F(s) + (s + B) y0 + v0] / (s^2 + B s + C)
 * with F = Fn/Fd:  none 0/1, delta 1/1, step 1/s, exp 1/(s - c), cos s/(s^2 + w^2), sin w/(s^2 + w^2).
 * The poles are known in closed form (system roots and input poles); poles closer than
 * MERGE * max(1, |p|) are merged into one repeated pole (stable evaluation near coincidence).
 * After the residues are found, a pole whose principal part is cancelled by the numerator is
 * reported with its reduced order (or removed); G.denomOrder keeps the unreduced count.
 * Impulse convention: y0, v0 are the values just before t = 0 (0-); delta adds 1 to y (first
 * order) or to y' (second order), as the Laplace transform with the 0- convention does.
 *
 * Partial fractions: near a pole p of multiplicity m, Y = g(s)/(s - p)^m with
 * g(s) = N(s) / prod_{q != p} (s - q)^{m_q}. With the Taylor coefficients g(p + h) = sum c_j h^j,
 *   Y = sum_{j=0}^{m-1} c_j / (s - p)^(m - j) + (terms regular at p),
 * and the inverse transform of 1/(s - p)^r is t^(r-1) e^(pt)/(r-1)!. So
 *   y(t) = Re sum_p sum_{j=0}^{m-1} c_j t^(m-1-j) e^(pt) / (m-1-j)!.
 * (deg N < deg D in every case, so there is no polynomial part.)
 * Taylor coefficients are computed exactly by power-series arithmetic of polynomials shifted to p.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var TOL = 1e-9, MERGE = 1e-5;
  function C(re, im) { return [re, im || 0]; }
  function add(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function mul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
  function div(a, b) { var d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; }
  function cabs(a) { return Math.hypot(a[0], a[1]); }
  function cexp(a) { var r = Math.exp(a[0]); return [r * Math.cos(a[1]), r * Math.sin(a[1])]; }

  // polynomials: arrays of complex coefficients, low degree first
  function padd(p, q) { var n = Math.max(p.length, q.length), r = []; for (var i = 0; i < n; i++) r.push(add(p[i] || C(0), q[i] || C(0))); return r; }
  function pmul(p, q) {
    var r = []; for (var i = 0; i < p.length + q.length - 1; i++) r.push(C(0));
    for (i = 0; i < p.length; i++) for (var j = 0; j < q.length; j++) r[i + j] = add(r[i + j], mul(p[i], q[j]));
    return r;
  }
  function peval(p, s) { var r = C(0); for (var i = p.length - 1; i >= 0; i--) r = add(mul(r, s), p[i]); return r; }
  // Taylor coefficients of p at s0: p(s0 + h) = sum b_k h^k
  function shift(p, s0) {
    var b = p.slice(), n = b.length;
    for (var i = 0; i < n; i++) for (var j = n - 2; j >= i; j--) b[j] = add(b[j], mul(s0, b[j + 1]));
    return b;
  }
  // power series a / b truncated to n terms (b[0] != 0)
  function sdiv(a, b, n) {
    var c = [];
    for (var k = 0; k < n; k++) {
      var v = a[k] || C(0);
      for (var j = 1; j <= k; j++) if (b[j]) v = sub(v, mul(b[j], c[k - j]));
      c.push(div(v, b[0]));
    }
    return c;
  }

  var INPUTS = ["none", "delta", "step", "exp", "cos", "sin"];

  function inputTransform(p) {
    var w = p.omega, c = p.c;
    switch (p.input) {
      case "none": return { Fn: [C(0)], Fd: [C(1)], poles: [], tex: "0" };
      case "delta": return { Fn: [C(1)], Fd: [C(1)], poles: [], tex: "1" };
      case "step": return { Fn: [C(1)], Fd: [C(0), C(1)], poles: [C(0)], tex: "\\frac{1}{s}" };
      case "exp": return { Fn: [C(1)], Fd: [C(-c), C(1)], poles: [C(c)], tex: "\\frac{1}{s - c}" };
      case "cos": return { Fn: [C(0), C(1)], Fd: [C(w * w), C(0), C(1)], poles: [C(0, w), C(0, -w)], tex: "\\frac{s}{s^2 + \\omega^2}" };
      case "sin": return { Fn: [C(w)], Fd: [C(w * w), C(0), C(1)], poles: [C(0, w), C(0, -w)], tex: "\\frac{\\omega}{s^2 + \\omega^2}" };
    }
    throw new Error("unknown input");
  }

  function systemPoles(p) {
    if (p.order === "first") return [C(p.a)];
    var B = p.B, Cc = p.C, d = B * B - 4 * Cc;
    if (Math.abs(d) < TOL) return [C(-B / 2), C(-B / 2)];
    if (d > 0) { var q = Math.sqrt(d); return [C((-B + q) / 2), C((-B - q) / 2)]; }
    var w = Math.sqrt(-d) / 2; return [C(-B / 2, w), C(-B / 2, -w)];
  }

  function build(p) {
    if (!p || INPUTS.indexOf(p.input) < 0) throw new Error("unknown input");
    var F = inputTransform(p);
    var y0 = p.y0 || 0, v0 = p.v0 || 0, P, init;
    if (p.order === "first") { P = [C(-p.a), C(1)]; init = [C(y0)]; }
    else { P = [C(p.C), C(p.B), C(1)]; init = [C(p.B * y0 + v0), C(y0)]; }
    var N = padd(F.Fn, pmul(init, F.Fd)), D = pmul(P, F.Fd);
    // Poles closer than MERGE are treated as one repeated pole at their mean: separate residues of
    // nearly equal poles are huge and cancel, which destroys accuracy; merging changes y by O(MERGE).
    var all = systemPoles(p).concat(F.poles), groups = [];
    all.forEach(function (z) {
      var g = groups.find(function (G) { return cabs(sub(G.p, z)) < MERGE * Math.max(1, cabs(z)); });
      if (g) { g.p = [(g.p[0] * g.m + z[0]) / (g.m + 1), (g.p[1] * g.m + z[1]) / (g.m + 1)]; g.m++; }
      else groups.push({ p: z, m: 1 });
    });
    groups.forEach(function (G) {
      // g(s) = N(s) / prod_{other}(s - q)^{m_q}, Taylor at p
      var num = shift(N, G.p), den = [C(1)];
      groups.forEach(function (H) {
        if (H === G) return;
        for (var k = 0; k < H.m; k++) den = pmul(den, [sub(G.p, H.p), C(1)]);
      });
      G.c = sdiv(num, den, G.m);
      // coefficient of t^r e^(pt): c_{m-1-r} / r!
      G.tcoef = [];
      for (var r = 0; r < G.m; r++) {
        var f = 1; for (var i = 2; i <= r; i++) f *= i;
        G.tcoef.push([G.c[G.m - 1 - r][0] / f, G.c[G.m - 1 - r][1] / f]);
      }
    });
    // numerator cancellation (after every residue is known): zero top coefficients lower the
    // effective order of a pole
    groups.forEach(function (G) {
      G.denomOrder = G.m;
      var scale = 1;
      G.tcoef.forEach(function (k) { scale = Math.max(scale, cabs(k)); });
      while (G.tcoef.length && cabs(G.tcoef[G.tcoef.length - 1]) < 1e-10 * scale) G.tcoef.pop();
      G.m = G.tcoef.length;
    });
    groups = groups.filter(function (G) { return G.m > 0; });
    function y(t) {
      var s = C(0);
      groups.forEach(function (G) {
        var e = cexp([G.p[0] * t, G.p[1] * t]), poly = C(0), tp = 1;
        for (var r = 0; r < G.m; r++) { poly = add(poly, [G.tcoef[r][0] * tp, G.tcoef[r][1] * tp]); tp *= t; }
        s = add(s, mul(poly, e));
      });
      return s[0];
    }
    return { N: N, D: D, poles: groups, y: y, inputTex: F.tex, Yat: function (s) { return div(peval(N, s), peval(D, s)); } };
  }

  // numerical check: RK4 on the ODE (impulse adds 1 to the top derivative at t = 0+)
  function simulate(p, tMax, n) {
    var h = tMax / n, w = p.omega, c = p.c;
    function f(t) {
      switch (p.input) {
        case "step": return 1; case "exp": return Math.exp(c * t);
        case "cos": return Math.cos(w * t); case "sin": return Math.sin(w * t); default: return 0;
      }
    }
    var kick = p.input === "delta" ? 1 : 0, pts = [];
    if (p.order === "first") {
      var y = (p.y0 || 0) + kick, rhs = function (t, y) { return p.a * y + f(t); };
      for (var i = 0; i <= n; i++) {
        pts.push([i * h, y]); var t = i * h;
        var k1 = rhs(t, y), k2 = rhs(t + h / 2, y + h * k1 / 2), k3 = rhs(t + h / 2, y + h * k2 / 2), k4 = rhs(t + h, y + h * k3);
        y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6;
      }
      return pts;
    }
    var u = [p.y0 || 0, (p.v0 || 0) + kick];
    function F2(t, u) { return [u[1], f(t) - p.B * u[1] - p.C * u[0]]; }
    for (var j = 0; j <= n; j++) {
      pts.push([j * h, u[0]]); var tt = j * h;
      var a1 = F2(tt, u), a2 = F2(tt + h / 2, [u[0] + h * a1[0] / 2, u[1] + h * a1[1] / 2]);
      var a3 = F2(tt + h / 2, [u[0] + h * a2[0] / 2, u[1] + h * a2[1] / 2]), a4 = F2(tt + h, [u[0] + h * a3[0], u[1] + h * a3[1]]);
      u = [u[0] + h * (a1[0] + 2 * a2[0] + 2 * a3[0] + a4[0]) / 6, u[1] + h * (a1[1] + 2 * a2[1] + 2 * a3[1] + a4[1]) / 6];
    }
    return pts;
  }

  return { TOL: TOL, INPUTS: INPUTS, build: build, simulate: simulate, inputTransform: inputTransform, systemPoles: systemPoles,
           complex: { add: add, sub: sub, mul: mul, div: div, abs: cabs, exp: cexp } };
}));
