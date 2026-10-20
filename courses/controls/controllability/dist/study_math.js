/*
 * Mathematics for the Controllability guide (dependency-free; no DOM).
 *
 * General part (any n-by-n A, n-by-q B, matrices as arrays of rows):
 *   ctrb(A, B)      controllability matrix C = [B, AB, ..., A^(n-1) B], n-by-(n q)
 *   svd(M)          singular values (descending) and left singular vectors of M (one-sided Jacobi
 *                   rotations on M^T: no M M^T product, so no cancellation from squaring)
 *   rankInfo(M)     numerical rank with an explicit relative tolerance: sigma_i > relTol * sigma_max
 *                   (relTol defaults to 1e-9); a matrix whose sigma_max <= 1e-12 has rank 0
 *   controllability(A, B)  {C, sigma, rank, n, controllable, cond, U}
 *
 * Explorer family (authored, 2-by-2):  A = [[1, c], [0, 2]],  b = (b1, b2),
 *   single input: B = b;  dual: B = [e1, b] (a second actuator on x1; c = 0, b = (0, 1) gives B = I).
 *   explorerModel(st) returns A, B, AB, C, rank data, det(C) for one input, the uncontrollable
 *   direction w (w^T C = 0) when rank < 2, and the coefficient point x = alpha*b + beta*A b.
 *   Discrete-time companion (separate model, same numbers): x_(k+1) = A x_k + B u_k, x_0 = 0
 *   gives x_2 = A B u_0 + B u_1, so alpha = u_1 and beta = u_0. This is NOT the sampled version
 *   of the continuous-time system and NOT a continuous-time energy/reachability measure.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var REL_TOL = 1e-9, ABS_ZERO = 1e-12;

  function shape(M) { return [M.length, M.length ? M[0].length : 0]; }
  function zeros(r, c) { var out = []; for (var i = 0; i < r; i++) { out.push([]); for (var j = 0; j < c; j++) out[i].push(0); } return out; }
  function identity(n) { var I = zeros(n, n); for (var i = 0; i < n; i++) I[i][i] = 1; return I; }
  function transpose(M) {
    var s = shape(M), T = zeros(s[1], s[0]);
    for (var i = 0; i < s[0]; i++) for (var j = 0; j < s[1]; j++) T[j][i] = M[i][j];
    return T;
  }
  function matmul(P, Q) {
    var a = shape(P), b = shape(Q);
    if (a[1] !== b[0]) throw new Error("matmul: inner sizes " + a[1] + " and " + b[0] + " differ");
    var out = zeros(a[0], b[1]);
    for (var i = 0; i < a[0]; i++) for (var j = 0; j < b[1]; j++) {
      var acc = 0;
      for (var k = 0; k < a[1]; k++) acc += P[i][k] * Q[k][j];
      out[i][j] = acc;
    }
    return out;
  }
  function matvec(P, v) { return matmul(P, v.map(function (x) { return [x]; })).map(function (r) { return r[0]; }); }
  function hcat(blocks) {
    return blocks[0].map(function (_, i) { return [].concat.apply([], blocks.map(function (Bk) { return Bk[i]; })); });
  }
  function asColumns(B) { return Array.isArray(B[0]) ? B : B.map(function (x) { return [x]; }); }

  // C = [B, AB, A^2 B, ..., A^(n-1) B]: each block is A times the previous block (A on the left).
  function ctrbBlocks(A, B) {
    var n = A.length, Bm = asColumns(B);
    if (shape(A)[1] !== n) throw new Error("ctrb: A must be square");
    if (Bm.length !== n) throw new Error("ctrb: B must have n rows");
    var blocks = [Bm];
    for (var k = 1; k < n; k++) blocks.push(matmul(A, blocks[k - 1]));
    return blocks;
  }
  function ctrb(A, B) { return hcat(ctrbBlocks(A, B)); }

  // One-sided Jacobi on G = M^T (columns of G live in R^(rows of M)... indexed by M's rows).
  // G V has orthogonal columns; their norms are the singular values of M and V holds the left
  // singular vectors of M. Works for any shape, including zero matrices.
  function svd(M) {
    var n = M.length, G = transpose(M), m = G.length, V = identity(n);
    for (var sweep = 0; sweep < 80; sweep++) {
      var rotated = false;
      for (var p = 0; p < n - 1; p++) for (var q = p + 1; q < n; q++) {
        var al = 0, be = 0, ga = 0, i;
        for (i = 0; i < m; i++) { al += G[i][p] * G[i][p]; be += G[i][q] * G[i][q]; ga += G[i][p] * G[i][q]; }
        if (ga === 0 || Math.abs(ga) <= 1e-15 * Math.sqrt(al * be)) continue;
        rotated = true;
        var zeta = (be - al) / (2 * ga);
        var t = (zeta >= 0 ? 1 : -1) / (Math.abs(zeta) + Math.sqrt(1 + zeta * zeta));
        var cs = 1 / Math.sqrt(1 + t * t), sn = cs * t;
        for (i = 0; i < m; i++) { var gp = G[i][p], gq = G[i][q]; G[i][p] = cs * gp - sn * gq; G[i][q] = sn * gp + cs * gq; }
        for (i = 0; i < n; i++) { var vp = V[i][p], vq = V[i][q]; V[i][p] = cs * vp - sn * vq; V[i][q] = sn * vp + cs * vq; }
      }
      if (!rotated) break;
    }
    var items = [];
    for (var j = 0; j < n; j++) {
      var s2 = 0;
      for (var r = 0; r < m; r++) s2 += G[r][j] * G[r][j];
      items.push({ s: Math.sqrt(s2), u: V.map(function (row) { return row[j]; }) });
    }
    items.sort(function (a, b) { return b.s - a.s; });
    return { sigma: items.map(function (it) { return it.s; }), U: items.map(function (it) { return it.u; }) };
  }

  function rankInfo(M, relTol) {
    relTol = relTol === undefined ? REL_TOL : relTol;
    var d = svd(M), smax = d.sigma[0] || 0, rank = 0;
    if (smax > ABS_ZERO) d.sigma.forEach(function (s) { if (s > relTol * smax) rank++; });
    var smin = d.sigma[d.sigma.length - 1] || 0;
    return { sigma: d.sigma, U: d.U, rank: rank, relTol: relTol,
             cond: smax > ABS_ZERO && smin > relTol * smax ? smax / smin : Infinity };
  }

  function controllability(A, B, relTol) {
    var C = ctrb(A, B), ri = rankInfo(C, relTol);
    return { C: C, sigma: ri.sigma, U: ri.U, rank: ri.rank, n: A.length, controllable: ri.rank === A.length,
             cond: ri.cond, relTol: ri.relTol };
  }

  function det2(M) { return M[0][0] * M[1][1] - M[0][1] * M[1][0]; }

  // ---- explorer family
  function explorerSystem(c, b1, b2, dual) {
    var A = [[1, c], [0, 2]];
    var B = dual ? [[1, b1], [0, b2]] : [[b1], [b2]];
    return { A: A, B: B };
  }

  function explorerModel(st) {
    var sys = explorerSystem(st.c, st.b1, st.b2, !!st.dual);
    var A = sys.A, b = [st.b1, st.b2];
    var Ab = matvec(A, b);                            // (b1 + c b2, 2 b2)
    var info = controllability(A, sys.B);
    var out = {
      A: A, B: sys.B, b: b, Ab: Ab, AB: matmul(A, sys.B), C: info.C,
      sigma: info.sigma, rank: info.rank, controllable: info.controllable, cond: info.cond, relTol: info.relTol,
      // det of the square single-input C = [b, Ab]: b2 (b1 - c b2), written factored (no cancellation)
      det: st.dual ? null : st.b2 * (st.b1 - st.c * st.b2),
      eig: [1, 2],
      point: [st.alpha * b[0] + st.beta * Ab[0], st.alpha * b[1] + st.beta * Ab[1]],
      w: null, line: null
    };
    if (info.rank === 1) {
      out.line = info.U[0];                           // reachable set from x0 = 0: the line col(C)
      out.w = info.U[1];                              // unreachable direction, w^T C = 0
    } else if (info.rank === 0) {
      out.w = null;
    }
    return out;
  }

  // Discrete-time companion: x_(k+1) = A x_k + B u_k from x_0 = 0 with scalar inputs u_0, u_1.
  function discreteTwoSteps(A, b, u0, u1) {
    var x1 = b.map(function (v) { return v * u0; });
    var Ax1 = matvec(A, x1);
    return { x1: x1, x2: [Ax1[0] + b[0] * u1, Ax1[1] + b[1] * u1] };
  }

  return { REL_TOL: REL_TOL, shape: shape, identity: identity, transpose: transpose, matmul: matmul, matvec: matvec,
           ctrbBlocks: ctrbBlocks, ctrb: ctrb, svd: svd, rankInfo: rankInfo, controllability: controllability, det2: det2,
           explorerSystem: explorerSystem, explorerModel: explorerModel, discreteTwoSteps: discreteTwoSteps };
}));
