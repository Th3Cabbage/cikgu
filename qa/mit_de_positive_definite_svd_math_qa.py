"""Independent check of courses/mit-de/positive-definite-svd/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_positive_definite_svd_math_qa.py

Compares the symmetric eigen-decomposition, the five tests and the classification with numpy,
the Cholesky factor (S = R^T R), the energy, and the 2x2 SVD (orthogonality, reconstruction,
singular values vs numpy.linalg.svd, rank-one pieces), plus the worked examples with SymPy.
"""
import itertools
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/positive-definite-svd/dist/study_math.js"

NODE = r"""
const SM = require(process.argv[1]);
const inp = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const sym = inp.sym.map(s => ({t: SM.tests(s[0], s[1], s[2]), e: SM.energy([[s[0], s[1]], [s[1], s[2]]], [0.7, -1.3])}));
const svd = inp.mats.map(A => { const S = SM.svd(A); return {S, r1: SM.rankOne(S, 0), r2: SM.rankOne(S, 1)}; });
process.stdout.write(JSON.stringify({sym, svd}));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


vals = [-3, -1, 0, 0.5, 2, 4]
sym = [list(s) for s in itertools.product(vals, repeat=3)] + [[4, 6, 10], [3, 4, 5], [1, 2, 4], [2, 1, 2], [2, 2, 5], [1e-8, 0, 1], [1e6, 1e6, 1e6 + 1]]
mats = [[[a, b], [c, d]] for a, b, c, d in itertools.product([-2, 0, 1, 3], repeat=4)]
mats += [[[1, 1], [0, 1e-13]], [[1, 1], [1, 1 + 1e-12]], [[1, -1], [0, -1e-10]], [[1, 0], [0, -1]], [[0, 1], [1, 0]]]  # Codex regressions
mats += [[[2, 2], [1, 1]], [[3, 0], [4, 5]], [[1, 1e-9], [0, 1]], [[1e5, 1], [1e5, 1]], [[0, 0], [0, 0]]]
out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps({"sym": sym, "mats": mats}),
                                capture_output=True, text=True, check=True).stdout)

for s, r in zip(sym, out["sym"]):
    S = np.array([[s[0], s[1]], [s[1], s[2]]], float)
    w, Q = np.linalg.eigh(S)
    t = r["t"]
    sc = np.max(np.abs(S)) or 1.0
    ok(abs(t["eig"]["l1"] - w[1]) < 1e-9 * sc and abs(t["eig"]["l2"] - w[0]) < 1e-9 * sc, f"eigenvalues {s}")
    for l, v in ((t["eig"]["l1"], t["eig"]["v1"]), (t["eig"]["l2"], t["eig"]["v2"])):
        v = np.array(v)
        ok(abs(np.linalg.norm(v) - 1) < 1e-12 and np.linalg.norm(S @ v - l * v) < 1e-9 * sc, f"eigenvector {s}")
    ok(abs(np.dot(t["eig"]["v1"], t["eig"]["v2"])) < 1e-12, f"orthogonal eigenvectors {s}")
    tol = 64 * 2.22e-16 * sc
    want = ("positive definite" if w[0] > tol else "negative definite" if w[1] < -tol else
            "indefinite" if (w[0] < -tol and w[1] > tol) else "positive semidefinite" if (abs(w[0]) <= tol and w[1] > tol) else
            "negative semidefinite" if (abs(w[1]) <= tol and w[0] < -tol) else "zero matrix")
    ok(t["kind"] == want, f"kind {s}: {t['kind']} vs {want}")
    # five tests agree for positive definite
    pd = want == "positive definite"
    ok(pd == (s[0] > 0 and np.linalg.det(S) > 0), f"leading determinants test {s}")
    if t["pivots"]:
        ok(abs(t["pivots"][0] - s[0]) < 1e-12 and abs(t["pivots"][1] - (s[2] - s[1] ** 2 / s[0])) < 1e-9 * sc, f"pivots {s}")
    if pd:
        R = np.array(t["cholesky"])
        ok(np.allclose(R.T @ R, S, rtol=1e-12, atol=1e-12 * sc) and R[1, 0] == 0 and R[0, 0] > 0 and R[1, 1] > 0, f"cholesky {s}")
    else:
        ok(t["cholesky"] is None, f"no cholesky {s}")
    x = np.array([0.7, -1.3])
    ok(abs(r["e"] - x @ S @ x) < 1e-12 * max(1, sc), f"energy {s}")

for A, r in zip(mats, out["svd"]):
    An = np.array(A, float)
    U, sig, V = np.array(r["S"]["U"]), np.array(r["S"]["sigma"]), np.array(r["S"]["V"])
    sc = max(1.0, np.max(np.abs(An)))
    ok(np.allclose(U.T @ U, np.eye(2), atol=1e-12) and np.allclose(V.T @ V, np.eye(2), atol=1e-12), f"orthogonal U, V {A}")
    ok(np.allclose(U @ np.diag(sig) @ V.T, An, atol=1e-9 * sc), f"A = U S V^T {A}")
    ok(np.allclose(sig, np.linalg.svd(An, compute_uv=False), atol=1e-9 * sc) and sig[0] >= sig[1] >= 0, f"singular values {A}")
    ok(np.allclose(np.array(r["r1"]) + np.array(r["r2"]), An, atol=1e-9 * sc), f"rank-one pieces sum {A}")

# examples
lec = out["svd"][len(mats) - 5]["S"]
ok(np.allclose(lec["sigma"], [np.sqrt(10), 0], atol=1e-12) and np.allclose(np.abs(np.array(lec["U"])[:, 0]), np.array([2, 1]) / np.sqrt(5)), "lecture SVD [2 2; 1 1]")
ok(np.allclose(out["svd"][len(mats) - 4]["S"]["sigma"], [3 * np.sqrt(5), np.sqrt(5)]), "s3 example sigma")
M = sp.Matrix
A = M([[1, 2], [0, 1], [1, 0]])
ok(A.T * A == M([[2, 2], [2, 5]]) and (A.T * A).eigenvals() == {1: 1, 6: 1}, "s1 example")
x1, x2 = sp.symbols("x1 x2")
E = (M([[x1, x2]]) * M([[4, 6], [6, 10]]) * M([x1, x2]))[0]
ok(sp.expand(E - (4 * (x1 + sp.Rational(3, 2) * x2) ** 2 + x2 ** 2)) == 0 and E.subs({x1: 1, x2: 1}) == 26 and E.subs({x1: 1, x2: -1}) == 2, "lecture energy")
E2 = (M([[x1, x2]]) * M([[3, 4], [4, 5]]) * M([x1, x2]))[0]
ok(E2.subs({x1: 4, x2: -3}) == -3, "s2 example negative energy")
a, b, c = sp.symbols("a b c")
C3 = M([[1, a, b], [a, 1, c], [b, c, 1]])
ok(sp.expand(C3.det() - (1 + 2 * a * b * c - a ** 2 - b ** 2 - c ** 2)) == 0, "correlation determinant")
u1 = M([1, 3]) / sp.sqrt(10)
ok(sp.simplify(M([[3, 0], [4, 5]]) * M([1, 1]) / sp.sqrt(2) - 3 * sp.sqrt(5) * u1) == M([0, 0]), "s3 u1")

print(f"positive-definite-svd math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
