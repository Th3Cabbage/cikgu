/*
 * Mathematics for Unit 6, Phase Plane, Linearization and Stability (dependency-free; no DOM).
 *
 * eig2(a, b, c, d) -> {T, D, disc, l1, l2 ({re, im}), v1, v2 (real eigenvectors or null), kind}
 *   kind: "saddle" (D < 0), "source" / "sink" (real, same sign), "spiral source" / "spiral sink",
 *   "center" (T = 0, D > 0), and degenerate boundary cases "degenerate source" / "degenerate sink"
 *   (T^2 = 4D, D > 0) and "zero eigenvalue" (D = 0). TOL decides the boundaries.
 * stable(T, D): T < 0 and D > 0 (both eigenvalues have negative real part).
 * models: linear (A), predprey (y' = y - yz, z' = yz - z), pendulum (theta' = w, w' = -sin theta - k w),
 *   each with rhs(u), jacobian(u) and a list of critical points.
 * rk4(rhs, u0, h, n, limit) -> trajectory [[x, y], ...] (stops when |u| > limit).
 * tumbling: rhs(x, y, z) = (yz, -2xz, xy), jacobian, conserved quantities.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var TOL = 1e-9;

  function eigvec(a, b, c, d, l) {
    // (A - l I) v = 0 for real l; choose the larger row for stability
    var r1 = [a - l, b], r2 = [c, d - l];
    var r = Math.hypot(r1[0], r1[1]) >= Math.hypot(r2[0], r2[1]) ? r1 : r2;
    var sc = Math.max(Math.abs(a), Math.abs(b), Math.abs(c), Math.abs(d)) || 1;
    if (Math.hypot(r[0], r[1]) < 1e-9 * sc) return null; // A = l I: every vector
    var v = [-r[1], r[0]], n = Math.hypot(v[0], v[1]);
    return [v[0] / n, v[1] / n];
  }

  // Tolerances scale with the matrix: s = max |entry|; T is compared with REL*s, D and the
  // discriminant with REL*s^2, so a uniformly rescaled matrix gets the same classification.
  var REL = 1e-12;
  function eig2(a, b, c, d) {
    var s = Math.max(Math.abs(a), Math.abs(b), Math.abs(c), Math.abs(d)) || 1;
    var T = a + d, D = a * d - b * c, disc = T * T - 4 * D, out = { T: T, D: D, disc: disc, scale: s };
    if (disc >= -REL * s * s) {
      var q = Math.sqrt(Math.max(0, disc));
      out.l1 = { re: (T + q) / 2, im: 0 }; out.l2 = { re: (T - q) / 2, im: 0 };
      out.v1 = eigvec(a, b, c, d, out.l1.re); out.v2 = eigvec(a, b, c, d, out.l2.re);
    } else {
      var w = Math.sqrt(-disc) / 2;
      out.l1 = { re: T / 2, im: w }; out.l2 = { re: T / 2, im: -w }; out.v1 = out.v2 = null;
    }
    out.kind = classify(T, D, s);
    out.stable = stable(T, D, s);
    return out;
  }

  function classify(T, D, s) {
    s = s || 1;
    var tT = REL * s, tD = REL * s * s;
    if (Math.abs(D) < tD) return "zero eigenvalue";
    if (D < 0) return "saddle";
    var disc = T * T - 4 * D;
    if (Math.abs(T) < tT) return "center";
    if (Math.abs(disc) < tD) return T > 0 ? "degenerate source" : "degenerate sink";
    if (disc > 0) return T > 0 ? "source" : "sink";
    return T > 0 ? "spiral source" : "spiral sink";
  }

  // asymptotic stability: both eigenvalues have negative real part
  function stable(T, D, s) { s = s || 1; return T < -REL * s && D > REL * s * s; }

  var models = {
    linear: function (p) {
      return { rhs: function (u) { return [p.a * u[0] + p.b * u[1], p.c * u[0] + p.d * u[1]]; },
               jacobian: function () { return [[p.a, p.b], [p.c, p.d]]; },
               critical: [[0, 0]] };
    },
    predprey: function () {
      return { rhs: function (u) { return [u[0] - u[0] * u[1], u[0] * u[1] - u[1]]; },
               jacobian: function (u) { return [[1 - u[1], -u[0]], [u[1], u[0] - 1]]; },
               critical: [[0, 0], [1, 1]] };
    },
    pendulum: function (p) {
      var k = p.k;
      return { rhs: function (u) { return [u[1], -Math.sin(u[0]) - k * u[1]]; },
               jacobian: function (u) { return [[0, 1], [-Math.cos(u[0]), -k]]; },
               critical: [[-Math.PI, 0], [0, 0], [Math.PI, 0]] };
    }
  };

  function criticalInfo(model) {
    return model.critical.map(function (u) {
      var J = model.jacobian(u), e = eig2(J[0][0], J[0][1], J[1][0], J[1][1]);
      return { point: u, J: J, eig: e };
    });
  }

  function rk4(rhs, u0, h, n, limit) {
    var u = u0.slice(), pts = [u.slice()];
    limit = limit || 1e6;
    for (var i = 0; i < n; i++) {
      var k1 = rhs(u), k2 = rhs(u.map(function (x, j) { return x + h * k1[j] / 2; }));
      var k3 = rhs(u.map(function (x, j) { return x + h * k2[j] / 2; }));
      var k4 = rhs(u.map(function (x, j) { return x + h * k3[j]; }));
      u = u.map(function (x, j) { return x + h * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) / 6; });
      if (!u.every(isFinite) || Math.max.apply(null, u.map(Math.abs)) > limit) break;
      pts.push(u.slice());
    }
    return pts;
  }

  var tumbling = {
    rhs: function (u) { return [u[1] * u[2], -2 * u[0] * u[2], u[0] * u[1]]; },
    jacobian: function (u) { return [[0, u[2], u[1]], [-2 * u[2], 0, -2 * u[0]], [u[1], u[0], 0]]; },
    conserved: function (u) {
      return { sphere: u[0] * u[0] + u[1] * u[1] + u[2] * u[2], xy: 2 * u[0] * u[0] + u[1] * u[1],
               yz: u[1] * u[1] + 2 * u[2] * u[2], xz: u[0] * u[0] - u[2] * u[2] };
    }
  };

  // Predator-prey conserved quantity H = y - ln y + z - ln z (constant on orbits, y, z > 0)
  function predpreyH(u) { return u[0] - Math.log(u[0]) + u[1] - Math.log(u[1]); }

  return { TOL: TOL, eig2: eig2, classify: classify, stable: stable, models: models, criticalInfo: criticalInfo,
           rk4: rk4, tumbling: tumbling, predpreyH: predpreyH };
}));
