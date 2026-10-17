/*
 * Exact math for the Linear Systems explorer (no numerical eigensolver, no ODE integration).
 *
 * The explorer builds A from a chosen eigenbasis instead of the other way round:
 *   T = [[1, s], [0, 1]]   (columns c1 = (1, 0), c2 = (s, 1); det T = 1, always invertible)
 *   D = diag(l1, l2)
 *   A = T D T^-1 = [[l1, s (l2 - l1)], [0, l2]]
 * so x(t) = T e^{Dt} T^-1 x0 is exact for every slider setting, including l1 = l2.
 * UMD: window.StudyMath in the browser, module.exports for the QA scripts (node).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  function basis(l1, l2, s) {
    return {
      T: [[1, s], [0, 1]],
      Tinv: [[1, -s], [0, 1]],
      D: [[l1, 0], [0, l2]],
      A: [[l1, s * (l2 - l1)], [0, l2]]
    };
  }

  function matmul(P, Q) {
    return [[P[0][0] * Q[0][0] + P[0][1] * Q[1][0], P[0][0] * Q[0][1] + P[0][1] * Q[1][1]],
            [P[1][0] * Q[0][0] + P[1][1] * Q[1][0], P[1][0] * Q[0][1] + P[1][1] * Q[1][1]]];
  }
  function matvec(P, v) { return [P[0][0] * v[0] + P[0][1] * v[1], P[1][0] * v[0] + P[1][1] * v[1]]; }
  function transpose(P) { return [[P[0][0], P[1][0]], [P[0][1], P[1][1]]]; }

  // e^{Dt} for diagonal D: exponentials on the diagonal, zeros off it.
  function expDiag(l1, l2, t) { return [[Math.exp(l1 * t), 0], [0, Math.exp(l2 * t)]]; }

  // e^{At} = T e^{Dt} T^-1, written out.
  function expA(l1, l2, s, t) {
    var b = basis(l1, l2, s);
    return matmul(matmul(b.T, expDiag(l1, l2, t)), b.Tinv);
  }

  // The three stages of x(t) = T e^{Dt} T^-1 x0.
  function pipeline(p, t) {
    var b = basis(p.l1, p.l2, p.s), x0 = [p.x1, p.x2];
    var z0 = matvec(b.Tinv, x0);
    var zt = [Math.exp(p.l1 * t) * z0[0], Math.exp(p.l2 * t) * z0[1]];
    var xt = matvec(b.T, zt);
    return { T: b.T, Tinv: b.Tinv, D: b.D, A: b.A, eDt: expDiag(p.l1, p.l2, t), x0: x0, z0: z0, zt: zt, xt: xt };
  }

  // Sampled trajectories in both coordinate systems for t in [0, tMax].
  function trajectory(p, tMax, n) {
    var xs = [], zs = [];
    for (var i = 0; i <= n; i++) {
      var r = pipeline(p, tMax * i / n);
      xs.push(r.xt); zs.push(r.zt);
    }
    return { x: xs, z: zs };
  }

  // Sign pattern of the modes, for a short verbal description.
  function classify(l1, l2) {
    var tol = 1e-9;
    if (l1 < -tol && l2 < -tol) return "stable";
    if ((l1 > tol && l2 < -tol) || (l1 < -tol && l2 > tol)) return "saddle";
    if (l1 > tol || l2 > tol) return "unstable";
    return "marginal";
  }

  // Defective comparison (not used by the sliders): A = [[l, 1], [0, l]] has one eigenvector
  // direction; its exponential is e^{lt} [[1, t], [0, 1]] (Jordan form), not a diagonal one.
  function expJordan(l, t) { var e = Math.exp(l * t); return [[e, t * e], [0, e]]; }

  return { basis: basis, matmul: matmul, matvec: matvec, transpose: transpose, expDiag: expDiag, expA: expA,
           pipeline: pipeline, trajectory: trajectory, classify: classify, expJordan: expJordan };
}));
