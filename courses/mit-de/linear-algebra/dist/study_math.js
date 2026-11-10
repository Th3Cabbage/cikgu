/*
 * Mathematics for Unit 7, Column Space, Basis and Graphs (dependency-free; no DOM).
 *
 * Exact rational arithmetic: a fraction is [p, q] with integers, q > 0, gcd 1 (entries are small
 * integers, so plain JS numbers stay exact well below 2^53).
 * rref(A)        -> {R, pivots, rank}
 * subspaces(A)   -> {rank, pivots, col (basis of C(A): pivot columns of A), row (nonzero rows of R),
 *                    null (special solutions), leftNull (special solutions of A^T), dims {col,row,null,leftNull}}
 * solve(A, b)    -> {solvable, particular (free variables 0), nullBasis}
 * incidence(n, edges) -> m x n matrix, row k: -1 at edges[k][0], +1 at edges[k][1] (1-based nodes)
 * graphInfo(n, edges) -> {A, rank, components, loops (basis of N(A^T)), laplacian}
 * Results are returned as fraction matrices; toNumber/toTex help the UI.
 *
 * UMD: window.StudyMath in the browser, module.exports in Node.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.StudyMath = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  function gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { var t = a % b; a = b; b = t; } return a || 1; }
  function F(p, q) { q = q === undefined ? 1 : q; if (q < 0) { p = -p; q = -q; } var g = gcd(p, q); return [p / g, q / g]; }
  function add(a, b) { return F(a[0] * b[1] + b[0] * a[1], a[1] * b[1]); }
  function sub(a, b) { return F(a[0] * b[1] - b[0] * a[1], a[1] * b[1]); }
  function mul(a, b) { return F(a[0] * b[0], a[1] * b[1]); }
  function div(a, b) { if (b[0] === 0) throw new Error("division by zero"); return F(a[0] * b[1], a[1] * b[0]); }
  function isZero(a) { return a[0] === 0; }
  function neg(a) { return [-a[0], a[1]]; }
  function toNumber(a) { return a[0] / a[1]; }
  function toTex(a) { return a[1] === 1 ? String(a[0]) : (a[0] < 0 ? "-" : "") + "\\tfrac{" + Math.abs(a[0]) + "}{" + a[1] + "}"; }

  function fracMatrix(A) { return A.map(function (r) { return r.map(function (x) { return Array.isArray(x) ? x : F(x); }); }); }
  function transpose(A) { return A[0].map(function (_, j) { return A.map(function (r) { return r[j]; }); }); }

  function rref(A0) {
    var R = fracMatrix(A0).map(function (r) { return r.slice(); });
    var m = R.length, n = R[0].length, pivots = [], row = 0;
    for (var col = 0; col < n && row < m; col++) {
      var p = -1;
      for (var i = row; i < m; i++) if (!isZero(R[i][col])) { p = i; break; }
      if (p < 0) continue;
      var tmp = R[row]; R[row] = R[p]; R[p] = tmp;
      var piv = R[row][col];
      R[row] = R[row].map(function (x) { return div(x, piv); });
      for (i = 0; i < m; i++) {
        if (i === row || isZero(R[i][col])) continue;
        var f = R[i][col];
        R[i] = R[i].map(function (x, j) { return sub(x, mul(f, R[row][j])); });
      }
      pivots.push(col); row++;
    }
    return { R: R, pivots: pivots, rank: pivots.length };
  }

  function nullBasis(A0) {
    var r = rref(A0), n = A0[0].length, free = [], basis = [];
    for (var j = 0; j < n; j++) if (r.pivots.indexOf(j) < 0) free.push(j);
    free.forEach(function (fj) {
      var v = []; for (var k = 0; k < n; k++) v.push(F(0));
      v[fj] = F(1);
      r.pivots.forEach(function (pc, i) { v[pc] = neg(r.R[i][fj]); });
      basis.push(v);
    });
    return basis;
  }

  function subspaces(A0) {
    var A = fracMatrix(A0), r = rref(A), m = A.length, n = A[0].length;
    var col = r.pivots.map(function (j) { return A.map(function (row) { return row[j]; }); });
    var rowsp = r.R.slice(0, r.rank);
    var nul = nullBasis(A), left = nullBasis(transpose(A));
    return { m: m, n: n, rank: r.rank, pivots: r.pivots, R: r.R, col: col, row: rowsp, null: nul, leftNull: left,
             dims: { row: r.rank, null: n - r.rank, col: r.rank, leftNull: m - r.rank } };
  }

  function solve(A0, b0) {
    var A = fracMatrix(A0), b = b0.map(function (x) { return Array.isArray(x) ? x : F(x); });
    var aug = A.map(function (row, i) { return row.concat([b[i]]); });
    var r = rref(aug), n = A[0].length;
    var solvable = r.pivots.indexOf(n) < 0;
    var part = null;
    if (solvable) {
      part = []; for (var k = 0; k < n; k++) part.push(F(0));
      r.pivots.forEach(function (pc, i) { part[pc] = r.R[i][n]; });
    }
    return { solvable: solvable, particular: part, nullBasis: nullBasis(A) };
  }

  function matVec(A0, v) {
    var A = fracMatrix(A0);
    return A.map(function (row) { return row.reduce(function (s, x, j) { return add(s, mul(x, v[j])); }, F(0)); });
  }

  function incidence(n, edges) {
    return edges.map(function (e) {
      var row = []; for (var j = 0; j < n; j++) row.push(0);
      row[e[0] - 1] = -1; row[e[1] - 1] = 1; return row;
    });
  }

  function components(n, edges) {
    var parent = []; for (var i = 0; i < n; i++) parent.push(i);
    function find(x) { while (parent[x] !== x) x = parent[x] = parent[parent[x]]; return x; }
    edges.forEach(function (e) { parent[find(e[0] - 1)] = find(e[1] - 1); });
    var roots = {}; for (i = 0; i < n; i++) roots[find(i)] = true;
    return Object.keys(roots).length;
  }

  function graphInfo(n, edges) {
    var A = incidence(n, edges), m = edges.length;
    var info = { A: A, m: m, n: n, components: components(n, edges) };
    if (m === 0) {
      // no edges: N(A) is all of R^n (standard basis) and A^T A is the n x n zero matrix
      info.rank = 0; info.loops = [];
      info.nullA = []; info.laplacian = [];
      for (var a = 0; a < n; a++) {
        var e = [], z = [];
        for (var c = 0; c < n; c++) { e.push(F(a === c ? 1 : 0)); z.push(0); }
        info.nullA.push(e); info.laplacian.push(z);
      }
      return info;
    }
    var s = subspaces(A);
    info.rank = s.rank; info.nullA = s.null; info.loops = s.leftNull;
    var L = [];
    for (var i = 0; i < n; i++) { L.push([]); for (var j = 0; j < n; j++) { var t = 0; for (var k = 0; k < m; k++) t += A[k][i] * A[k][j]; L[i].push(t); } }
    info.laplacian = L;
    return info;
  }

  return { F: F, add: add, sub: sub, mul: mul, div: div, toNumber: toNumber, toTex: toTex, rref: rref, nullBasis: nullBasis,
           subspaces: subspaces, solve: solve, matVec: matVec, transpose: transpose, incidence: incidence,
           components: components, graphInfo: graphInfo };
}));
