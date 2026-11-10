/*
 * Mathematics for Unit 10, Boundary Problems, Fourier Series and PDEs (dependency-free; no DOM).
 *
 * bvpUniform(x)          y = (x - x^2)/2 solves -y'' = 1, y(0) = y(1) = 0.
 * green(x, a)            point-load solution of -y'' = delta(x - a): (1 - a)x for x <= a, a(1 - x) after.
 * coefficients(fn, N)    {a0, a: [a1..aN], b: [b1..bN]} on [-pi, pi] in closed form for
 *                        "square" (odd, +1 on (0, pi)), "ramp" (|x|), "saw" (x), "delta".
 * target(fn, x)          the function itself (delta returns 0 away from 0; jumps return the midpoint).
 * partialSum(c, x)       a0 + sum (a_k cos kx + b_k sin kx).
 * poisson(r, theta)      (1/2pi) (1 - r^2)/(1 + r^2 - 2 r cos theta), the disc solution for delta data.
 * heatCoeffs(start, K)   sine coefficients B_1..B_K on [0, 1] for "one", "tent", "two".
 * heat(B, t, x)          sum B_k e^(-k^2 pi^2 t) sin(k pi x).
 * pluckCoeffs(p, K)      d_n = 2 sin(n p) / (n^2 p (pi - p)) for a pluck of height 1 at x = p on [0, pi].
 * pluckShape(p, x)       the initial tent; pluckOdd(p, x) its odd 2 pi periodic extension.
 * wave(d, t, x)          sum d_n cos(n t) sin(n x)  (c = 1); waveDAlembert(p, t, x) = (u0(x - t) + u0(x + t))/2.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var PI = Math.PI;

  function bvpUniform(x) { return (x - x * x) / 2; }
  function green(x, a) { return x <= a ? (1 - a) * x : a * (1 - x); }

  function coefficients(fn, N) {
    var a = [], b = [], a0 = 0;
    for (var k = 1; k <= N; k++) {
      var odd = k % 2 === 1;
      if (fn === "square") { a.push(0); b.push(odd ? 4 / (PI * k) : 0); }
      else if (fn === "ramp") { a.push(odd ? -4 / (PI * k * k) : 0); b.push(0); }
      else if (fn === "saw") { a.push(0); b.push(2 * (odd ? 1 : -1) / k); }
      else if (fn === "delta") { a.push(1 / PI); b.push(0); }
      else throw new Error("unknown function");
    }
    if (fn === "ramp") a0 = PI / 2;
    if (fn === "delta") a0 = 1 / (2 * PI);
    return { a0: a0, a: a, b: b };
  }

  function wrap(x) { var y = ((x + PI) % (2 * PI) + 2 * PI) % (2 * PI) - PI; return y; }

  function target(fn, x) {
    var y = wrap(x);
    if (fn === "square") return y > 0 && y < PI ? 1 : (y < 0 && y > -PI ? -1 : 0);
    if (fn === "ramp") return Math.abs(y);
    if (fn === "saw") return Math.abs(Math.abs(y) - PI) < 1e-12 ? 0 : y;
    return 0;
  }

  function partialSum(c, x) {
    var s = c.a0;
    for (var k = 1; k <= c.a.length; k++) s += c.a[k - 1] * Math.cos(k * x) + c.b[k - 1] * Math.sin(k * x);
    return s;
  }

  // 1 + r^2 - 2r cos(theta) = (1 - r)^2 + 4r sin^2(theta/2): no cancellation near r = 1, theta = 0
  function poisson(r, th) {
    var s = Math.sin(th / 2);
    return (1 - r) * (1 + r) / (2 * PI * ((1 - r) * (1 - r) + 4 * r * s * s));
  }

  function heatCoeffs(start, K) {
    var B = [];
    for (var k = 1; k <= K; k++) {
      if (start === "one") B.push(k % 2 ? 4 / (k * PI) : 0);
      else if (start === "tent") B.push(8 * Math.sin(k * PI / 2) / (k * k * PI * PI));
      else if (start === "two") B.push(k === 1 ? 1 : (k === 3 ? 0.5 : 0));
      else throw new Error("unknown start");
    }
    return B;
  }

  function heatStart(start, x) {
    if (start === "one") return x > 0 && x < 1 ? 1 : 0;
    if (start === "tent") return x <= 0.5 ? 2 * x : 2 * (1 - x);
    return Math.sin(PI * x) + 0.5 * Math.sin(3 * PI * x);
  }

  function heat(B, t, x) {
    var s = 0;
    for (var k = 1; k <= B.length; k++) if (B[k - 1]) s += B[k - 1] * Math.exp(-k * k * PI * PI * t) * Math.sin(k * PI * x);
    return s;
  }

  function pluckCoeffs(p, K) {
    var d = [];
    for (var n = 1; n <= K; n++) d.push(2 * Math.sin(n * p) / (n * n * p * (PI - p)));
    return d;
  }

  function pluckShape(p, x) { return x <= p ? x / p : (PI - x) / (PI - p); }

  function pluckOdd(p, x) {
    var y = wrap(x);
    return y >= 0 ? pluckShape(p, y) : -pluckShape(p, -y);
  }

  function wave(d, t, x) {
    var s = 0;
    for (var n = 1; n <= d.length; n++) s += d[n - 1] * Math.cos(n * t) * Math.sin(n * x);
    return s;
  }

  function waveDAlembert(p, t, x) { return 0.5 * (pluckOdd(p, x - t) + pluckOdd(p, x + t)); }

  return { bvpUniform: bvpUniform, green: green, coefficients: coefficients, target: target, partialSum: partialSum,
           poisson: poisson, heatCoeffs: heatCoeffs, heatStart: heatStart, heat: heat, pluckCoeffs: pluckCoeffs,
           pluckShape: pluckShape, pluckOdd: pluckOdd, wave: wave, waveDAlembert: waveDAlembert };
}));
