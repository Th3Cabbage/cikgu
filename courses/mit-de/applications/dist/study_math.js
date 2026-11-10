/*
 * Mathematics for Unit 12, Tumbling Box, Predator-Prey and Chaos (dependency-free; no DOM).
 *
 * rk4(f, y0, h, n) -> array of states [y0, y1, ..., yn] (fixed step).
 * box: f(y) = (y2 y3, -2 y1 y3, y1 y2); boxStart(axis, size) = unit vector near the axis
 *      (axis + size * fixed direction, normalised; the direction is deterministic for repeatability).
 * predprey(mu1, mu2): f(y) = (y1(1 - y2/mu2), -y2(1 - y1/mu1)); H(y) = ln y1 - y1/mu1 + ln y2 - y2/mu2;
 *      period(mu, eta): time between returns to the starting angle around (mu1, mu2) (linear
 *      interpolation of the crossing), from an RK4 run with h = 0.001.
 * lorenz(sigma, rho, beta): f(y) = (sigma(y - x), rho x - y - x z, x y - beta z);
 *      lorenzCritical(rho, beta) = [(eta, eta, rho - 1), (-eta, -eta, rho - 1)], eta = sqrt(beta(rho - 1)).
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  function rk4(f, y0, h, n) {
    var y = y0.slice(), out = [y.slice()], d = y.length, i, j;
    var a = new Array(d), b = new Array(d), c = new Array(d);
    for (i = 0; i < n; i++) {
      var k1 = f(y);
      for (j = 0; j < d; j++) a[j] = y[j] + h / 2 * k1[j];
      var k2 = f(a);
      for (j = 0; j < d; j++) b[j] = y[j] + h / 2 * k2[j];
      var k3 = f(b);
      for (j = 0; j < d; j++) c[j] = y[j] + h * k3[j];
      var k4 = f(c);
      for (j = 0; j < d; j++) y[j] += h / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]);
      out.push(y.slice());
    }
    return out;
  }

  function box(y) { return [y[1] * y[2], -2 * y[0] * y[2], y[0] * y[1]]; }
  function boxStart(axis, size) {
    var e = { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1] }[axis];
    var d = [0.6, -0.5, 0.62]; // fixed small direction (not along any axis)
    var v = e.map(function (x, i) { return x + size * d[i]; });
    var n = Math.hypot(v[0], v[1], v[2]);
    return v.map(function (x) { return x / n; });
  }

  function predprey(mu1, mu2) { return function (y) { return [y[0] * (1 - y[1] / mu2), -y[1] * (1 - y[0] / mu1)]; }; }
  function H(mu1, mu2, y) { return Math.log(y[0]) - y[0] / mu1 + Math.log(y[1]) - y[1] / mu2; }

  function period(mu1, mu2, eta1, eta2, tMax) {
    var h = 0.001, n = Math.round((tMax || 40) / h), f = predprey(mu1, mu2);
    var ang = function (y) { return Math.atan2(y[1] - mu2, y[0] - mu1); };
    var a0 = ang([eta1, eta2]), y = [eta1, eta2], prev = 0, t = 0, turned = 0;
    var unwrap = function (a) { var d = a - a0; while (d <= -Math.PI) d += 2 * Math.PI; while (d > Math.PI) d -= 2 * Math.PI; return d; };
    for (var i = 0; i < n; i++) {
      var s = rk4(f, y, h, 1)[1], d0 = unwrap(ang(y)), d1 = unwrap(ang(s));
      t += h;
      // the orbit runs counterclockwise around (mu1, mu2) in the (y1, y2) plane; count a crossing of
      // the starting ray from below (d0 < 0 <= d1) after moving away from it
      if (Math.abs(d1) > 1) turned = 1;
      if (turned && d0 < 0 && d1 >= 0) return t - h + h * (-d0) / (d1 - d0);
      y = s;
    }
    return null;
  }

  function lorenz(sigma, rho, beta) {
    return function (y) { return [sigma * (y[1] - y[0]), rho * y[0] - y[1] - y[0] * y[2], y[0] * y[1] - beta * y[2]]; };
  }
  function lorenzCritical(rho, beta) {
    var e = Math.sqrt(beta * (rho - 1));
    return [[e, e, rho - 1], [-e, -e, rho - 1]];
  }

  return { rk4: rk4, box: box, boxStart: boxStart, predprey: predprey, H: H, period: period, lorenz: lorenz, lorenzCritical: lorenzCritical };
}));
