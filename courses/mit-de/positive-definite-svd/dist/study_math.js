/*
 * Mathematics for Unit 9, Positive Definite Matrices and the SVD (dependency-free; no DOM).
 *
 * symEig(s11, s12, s22) -> {l1 >= l2, v1, v2 (orthonormal)} via the stable Jacobi rotation angle.
 * tests(s11, s12, s22)  -> {eig, pivots ([s11, det/s11] or null when s11 = 0), dets [s11, det],
 *                           cholesky R (upper triangular, S = R^T R) or null, kind}
 *   kind: "positive definite" | "positive semidefinite" | "indefinite" | "negative semidefinite" |
 *         "negative definite" (zero tests are relative to the size of S).
 * energy(S, x) = x^T S x.
 * svd(A) for 2x2 A -> {U, sigma [s1 >= s2 >= 0], V} with A = U diag(sigma) V^T, U and V orthogonal
 *   (V from symEig of A^T A; u_1 = A v_1 / sigma_1; u_2 is perpendicular to u_1 with the sign that
 *    makes A = U Sigma V^T, sigma_2 = |det A| / sigma_1; when A = 0 both U and V are the identity).
 *   U and V may be rotations or reflections.
 * rankOne(svd, i) = sigma_i u_i v_i^T.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var EPS = 2.220446049250313e-16;

  function symEig(a, b, d) {
    // rotation angle theta with tan(2 theta) = 2b / (a - d); columns of the rotation are eigenvectors
    var th = 0.5 * Math.atan2(2 * b, a - d), c = Math.cos(th), s = Math.sin(th);
    var l1 = a * c * c + 2 * b * c * s + d * s * s;
    var l2 = a * s * s - 2 * b * c * s + d * c * c;
    var v1 = [c, s], v2 = [-s, c];
    if (l2 > l1) { var t = l1; l1 = l2; l2 = t; var tv = v1; v1 = v2; v2 = [-tv[0], -tv[1]]; }
    return { l1: l1, l2: l2, v1: v1, v2: v2 };
  }

  function tests(a, b, d) {
    var e = symEig(a, b, d), det = a * d - b * b, sc = Math.max(Math.abs(a), Math.abs(b), Math.abs(d)) || 1;
    var tol = 64 * EPS * sc;
    var out = { eig: e, det: det, dets: [a, det], pivots: Math.abs(a) > tol ? [a, det / a] : null, cholesky: null };
    var p = e.l2 > tol, n = e.l1 < -tol, z1 = Math.abs(e.l1) <= tol, z2 = Math.abs(e.l2) <= tol;
    if (p) out.kind = "positive definite";
    else if (n) out.kind = "negative definite";
    else if (e.l2 < -tol && e.l1 > tol) out.kind = "indefinite";
    else if (z2 && !z1 && e.l1 > 0) out.kind = "positive semidefinite";
    else if (z1 && !z2 && e.l2 < 0) out.kind = "negative semidefinite";
    else out.kind = "zero matrix";
    if (out.kind === "positive definite") {
      var r11 = Math.sqrt(a), r12 = b / r11, r22 = Math.sqrt(d - r12 * r12);
      out.cholesky = [[r11, r12], [0, r22]];
    }
    return out;
  }

  function energy(S, x) { return S[0][0] * x[0] * x[0] + 2 * S[0][1] * x[0] * x[1] + S[1][1] * x[1] * x[1]; }

  function svd(A) {
    var a = A[0][0], b = A[0][1], c = A[1][0], d = A[1][1];
    var e = symEig(a * a + c * c, a * b + c * d, b * b + d * d);
    var s1 = Math.sqrt(Math.max(0, e.l1)), s2 = Math.sqrt(Math.max(0, e.l2));
    var V = [[e.v1[0], e.v2[0]], [e.v1[1], e.v2[1]]];
    var sc = Math.max(Math.abs(a), Math.abs(b), Math.abs(c), Math.abs(d));
    if (sc === 0) return { U: [[1, 0], [0, 1]], sigma: [0, 0], V: [[1, 0], [0, 1]] };
    // sigma2 from |det A| / sigma1 is more accurate than the square root of a tiny eigenvalue
    s2 = Math.abs(a * d - b * c) / s1;
    var u1 = [(a * V[0][0] + b * V[1][0]) / s1, (c * V[0][0] + d * V[1][0]) / s1];
    var n1 = Math.hypot(u1[0], u1[1]); u1 = [u1[0] / n1, u1[1] / n1];
    // u2 is built perpendicular to u1 (no division by a small sigma2, so U stays orthogonal for
    // nearly singular A). Its sign follows det A = det(U) sigma1 sigma2 det(V): with
    // u2 = sgn * (-u1y, u1x), det U = sgn, so sgn = sign(det A) * det V (any sign when det A = 0).
    var detA = a * d - b * c, detV = V[0][0] * V[1][1] - V[0][1] * V[1][0];
    var sgn = detA === 0 ? 1 : (detA > 0 ? 1 : -1) * (detV > 0 ? 1 : -1);
    var u2 = [-sgn * u1[1], sgn * u1[0]];
    if (s2 <= 64 * EPS * s1) s2 = 0;
    return { U: [[u1[0], u2[0]], [u1[1], u2[1]]], sigma: [s1, s2], V: V };
  }

  function rankOne(S, i) {
    var u = [S.U[0][i], S.U[1][i]], v = [S.V[0][i], S.V[1][i]], s = S.sigma[i];
    return [[s * u[0] * v[0], s * u[0] * v[1]], [s * u[1] * v[0], s * u[1] * v[1]]];
  }

  return { symEig: symEig, tests: tests, energy: energy, svd: svd, rankOne: rankOne };
}));
