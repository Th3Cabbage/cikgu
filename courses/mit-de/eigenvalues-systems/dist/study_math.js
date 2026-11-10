/*
 * Mathematics for Unit 8, Eigenvalues and Linear Systems (dependency-free; no DOM).
 * 2 by 2 matrices are [[a, b], [c, d]]; complex numbers are [re, im].
 *
 * eig(A)      -> {T, D, disc, lambdas: [l1, l2] (complex), vectors: [x1, x2] (complex 2-vectors,
 *                 unit length) or null for a defective double eigenvalue, defective, kind}
 *                Tolerances are relative to s = max |entry| (REL = 1e-12).
 * diagonalize(A) -> {V, Lambda, Vinv} (complex) or null when defective.
 * matMul, matVec, matPow(A, k) (repeated squaring, real).
 * expm(A, t)  -> real 2x2 e^(At) in closed form, evaluated stably (see the function):
 *                e^(B) = e^s [ C I + S (B - sI) ] for B = At, s = trace(B)/2, z = q^2 centred;
 *                series in z for |z| < 1 (covers repeated roots and long times near them),
 *                separate e^(s +- q) for z >= 1 (no inf * 0), cos/sin for z <= -1.
 * expand(A, u) -> coefficients c with u = c1 x1 + c2 x2 (complex), or null when defective.
 * powersSequence(A, u0, n), flow(A, y0, ts): reference sequences for the explorer.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  var REL = 1e-12, EPS = 2.220446049250313e-16;
  function C(re, im) { return [re, im || 0]; }
  function add(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function mul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
  function div(a, b) { var d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; }
  function cabs(a) { return Math.hypot(a[0], a[1]); }
  function scale(A) { return Math.max(Math.abs(A[0][0]), Math.abs(A[0][1]), Math.abs(A[1][0]), Math.abs(A[1][1])) || 1; }

  function normalize(v) {
    var n = Math.sqrt(cabs(v[0]) * cabs(v[0]) + cabs(v[1]) * cabs(v[1]));
    // make the largest component real positive for a tidy display
    var k = cabs(v[0]) >= cabs(v[1]) ? 0 : 1, ph = v[k], m = cabs(ph);
    var rot = [ph[0] / m, -ph[1] / m];
    return [mul(v[0], rot).map(function (x) { return x / n; }), mul(v[1], rot).map(function (x) { return x / n; })];
  }

  function eigvec(A, l, s) {
    // rows of A - l I; pick the larger row r and use v = (-r1, r0)
    var r1 = [sub(C(A[0][0]), l), C(A[0][1])], r2 = [C(A[1][0]), sub(C(A[1][1]), l)];
    var n1 = cabs(r1[0]) + cabs(r1[1]), n2 = cabs(r2[0]) + cabs(r2[1]);
    var r = n1 >= n2 ? r1 : r2;
    if (Math.max(n1, n2) < 1e-9 * s) return null;
    return normalize([[-r[1][0], -r[1][1]], r[0]]);
  }

  function eig(A) {
    // centred discriminant (a - d)^2 + 4bc = T^2 - 4D without cancelling large T^2 against 4D;
    // only roundoff-level values (|disc| <= 16 eps s^2) are treated as a double root
    var s = scale(A), T = A[0][0] + A[1][1], D = A[0][0] * A[1][1] - A[0][1] * A[1][0];
    var h = A[0][0] - A[1][1], disc = h * h + 4 * A[0][1] * A[1][0];
    var l1, l2;
    if (Math.abs(disc) <= 16 * EPS * s * s) { l1 = l2 = C(T / 2); disc = 0; }
    else if (disc > 0) { var q = Math.sqrt(disc); l1 = C((T + q) / 2); l2 = C((T - q) / 2); }
    else { var w = Math.sqrt(-disc) / 2; l1 = C(T / 2, w); l2 = C(T / 2, -w); }
    var out = { T: T, D: D, disc: disc, lambdas: [l1, l2], defective: false };
    if (disc === 0) {
      var off = Math.abs(A[0][1]) + Math.abs(A[1][0]) + Math.abs(A[0][0] - A[1][1]);
      if (off <= 1e-9 * s) out.vectors = [[C(1), C(0)], [C(0), C(1)]]; // A = lambda I: every vector
      else { out.defective = true; out.vectors = [eigvec(A, l1, s), null]; }
    } else out.vectors = [eigvec(A, l1, s), eigvec(A, l2, s)];
    out.kind = disc > 0 ? "real distinct" : (disc < 0 ? "complex pair" : (out.defective ? "defective double" : "double, diagonal"));
    return out;
  }

  function diagonalize(A) {
    var e = eig(A);
    if (e.defective) return null;
    var V = [[e.vectors[0][0], e.vectors[1][0]], [e.vectors[0][1], e.vectors[1][1]]];
    var det = sub(mul(V[0][0], V[1][1]), mul(V[0][1], V[1][0]));
    var Vinv = [[div(V[1][1], det), div([-V[0][1][0], -V[0][1][1]], det)],
                [div([-V[1][0][0], -V[1][0][1]], det), div(V[0][0], det)]];
    return { V: V, Lambda: [[e.lambdas[0], C(0)], [C(0), e.lambdas[1]]], Vinv: Vinv, eig: e };
  }

  function expand(A, u) {
    var d = diagonalize(A);
    if (!d) return null;
    var uc = [C(u[0]), C(u[1])];
    return [add(mul(d.Vinv[0][0], uc[0]), mul(d.Vinv[0][1], uc[1])), add(mul(d.Vinv[1][0], uc[0]), mul(d.Vinv[1][1], uc[1]))];
  }

  function matMul(A, B) {
    return [[A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]];
  }
  function matVec(A, v) { return [A[0][0] * v[0] + A[0][1] * v[1], A[1][0] * v[0] + A[1][1] * v[1]]; }
  function matPow(A, k) {
    var R = [[1, 0], [0, 1]], P = A;
    while (k > 0) { if (k & 1) R = matMul(R, P); P = matMul(P, P); k >>= 1; }
    return R;
  }

  // e^(B) for B = A t (scaling by t first avoids overflow in products of large entries).
  // With s = trace(B)/2 and z = q^2 = ((b11 - b22)/2)^2 + b12 b21 (centred):
  //   e^B = EC I + ES (B - sI),  EC = e^s C(z), ES = e^s S(z),
  //   C(z) = sum z^k/(2k)!, S(z) = sum z^k/(2k+1)!  (cosh/sinh(q)/q for z > 0, cos/sin(w)/w for z < 0).
  // |z| < 1: the series (no cancellation, any small q, defective q = 0 included).
  // z >= 1: EC, ES from e^(s+q) and e^(s-q) separately, so e^s cosh q never forms inf * 0.
  // z <= -1: e^s (cos w, sin w / w).
  function expm(A, t) {
    var b00 = A[0][0] * t, b01 = A[0][1] * t, b10 = A[1][0] * t, b11 = A[1][1] * t;
    var s = (b00 + b11) / 2, h = (b00 - b11) / 2, z = h * h + b01 * b10, EC, ES;
    if (Math.abs(z) < 1) {
      var c = 0, sn = 0, term = 1;
      for (var k = 0; k < 40; k++) {
        c += term / fact(2 * k); sn += term / fact(2 * k + 1);
        term *= z;
        if (Math.abs(term) < 1e-18) break;
      }
      var e = Math.exp(s); EC = e * c; ES = e * sn;
    } else if (z > 0) {
      var q = Math.sqrt(z), E1 = Math.exp(s + q), E2 = Math.exp(s - q);
      EC = (E1 + E2) / 2; ES = (E1 - E2) / (2 * q);
    } else {
      var w = Math.sqrt(-z), e2 = Math.exp(s);
      EC = e2 * Math.cos(w); ES = e2 * Math.sin(w) / w;
    }
    return [[EC + ES * (b00 - s), ES * b01], [ES * b10, EC + ES * (b11 - s)]];
  }
  var FACT = [1];
  function fact(n) { while (FACT.length <= n) FACT.push(FACT[FACT.length - 1] * FACT.length); return FACT[n]; }

  function powersSequence(A, u0, n) {
    var out = [u0.slice()], u = u0.slice();
    for (var k = 0; k < n; k++) { u = matVec(A, u); out.push(u); }
    return out;
  }

  function flow(A, y0, ts) { return ts.map(function (t) { return matVec(expm(A, t), y0); }); }

  return { REL: REL, eig: eig, diagonalize: diagonalize, expand: expand, matMul: matMul, matVec: matVec, matPow: matPow,
           expm: expm, powersSequence: powersSequence, flow: flow, complex: { add: add, sub: sub, mul: mul, div: div, abs: cabs } };
}));
