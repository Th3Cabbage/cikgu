"""Independent check of courses/mit-de/eigenvalues-systems/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_eigenvalues_systems_math_qa.py

Compares eigenvalues/eigenvectors and diagonalization with numpy, e^(At) with scipy.linalg.expm
(including defective and complex cases), powers with numpy.linalg.matrix_power, the expansion of
u0 in eigenvectors, and the worked examples of the guide with SymPy.
"""
import itertools
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/eigenvalues-systems/dist/study_math.js"

NODE = r"""
const SM = require(process.argv[1]);
const mats = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = mats.map(A => {
  const e = SM.eig(A), d = SM.diagonalize(A);
  return {e, d: d ? {V: d.V, Vinv: d.Vinv} : null, ex: [0.3, 1, 2.2].map(t => SM.expm(A, t)), p: [0, 1, 5, 8].map(k => SM.matPow(A, k)),
          c: SM.expand(A, [1, -0.5])};
});
process.stdout.write(JSON.stringify(out));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


vals = [-2, -0.5, 0, 1, 3]
mats = [[[a, b], [c, d]] for a, b, c, d in itertools.product(vals, repeat=4)]
mats += [[[1, 0], [0, 1.0000001]], [[1, 1e-7], [-1e-7, 1]], [[0, 1], [-1e-14, 0]], [[-2000, 0], [0, -1]]]  # Codex regressions
mats += [[[5, 1], [3, 3]], [[0.8, 0.3], [0.2, 0.7]], [[-1, 2], [1, -2]], [[0, 1], [0, 0]], [[2, 1], [0, 2]], [[3, 1], [1, 3]],
         [[0, -1], [1, 0]], [[3, -1], [1, 3]], [[4, 1], [2, 3]], [[0, 1], [-1, 0]], [[2, 3], [0, 4]], [[0, 2], [-4, 6]],
         [[1e-6, 0], [0, 2e-6]], [[1e3, 1e3], [0, 1e3]]]
out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps(mats), capture_output=True, text=True, check=True).stdout)


def cz(v):
    return complex(v[0], v[1])


for A, r in zip(mats, out):
    An = np.array(A, float)
    sc = np.max(np.abs(An)) or 1.0
    w = np.linalg.eigvals(An)
    got = [cz(l) for l in r["e"]["lambdas"]]
    key = lambda z: (round(z.real, 6), round(z.imag, 6))
    ok(np.allclose(sorted(got, key=key), sorted(w, key=key), atol=1e-6 * sc), f"eigenvalues {A}: {got} vs {w}")
    for l, v in zip(r["e"]["lambdas"], r["e"]["vectors"]):
        if v is None:
            continue
        x = np.array([cz(v[0]), cz(v[1])])
        ok(abs(np.linalg.norm(x) - 1) < 1e-9 and np.linalg.norm(An @ x - cz(l) * x) < 1e-6 * sc, f"eigenvector {A}")
    # defective iff a double eigenvalue with a one-dimensional eigenspace
    T = np.trace(An)
    hh = An[0, 0] - An[1, 1]
    double = abs(hh * hh + 4 * An[0, 1] * An[1, 0]) <= 16 * 2.22e-16 * sc * sc
    defective = double and np.linalg.matrix_rank(An - T / 2 * np.eye(2), tol=1e-9 * sc) == 1
    ok(r["e"]["defective"] == defective, f"defective flag {A}")
    if r["d"]:
        V = np.array([[cz(x) for x in row] for row in r["d"]["V"]])
        Vi = np.array([[cz(x) for x in row] for row in r["d"]["Vinv"]])
        L = np.diag(got)
        ok(np.allclose(V @ L @ Vi, An, atol=1e-8 * sc) and np.allclose(V @ Vi, np.eye(2), atol=1e-9), f"A = V L V^-1 {A}")
        c = np.array([cz(x) for x in r["c"]])
        ok(np.allclose(V @ c, [1, -0.5], atol=1e-9), f"expansion {A}")
    else:
        ok(defective, f"diagonalize returned null for non-defective {A}")
    for t, E in zip([0.3, 1, 2.2], r["ex"]):
        Ew = expm(An * t)
        if not np.all(np.isfinite(Ew)) or np.max(np.abs(Ew)) > 1e300:
            continue
        ok(np.allclose(E, Ew, rtol=1e-9, atol=1e-9 * max(1, np.max(np.abs(Ew)))), f"expm {A} t={t}")
    for k, P in zip([0, 1, 5, 8], r["p"]):
        Pw = np.linalg.matrix_power(An, k)
        ok(np.allclose(P, Pw, rtol=1e-12, atol=1e-12 * max(1, np.max(np.abs(Pw)))), f"power {A} k={k}")

# extreme expm cases with finite answers (Codex)
X = json.loads(subprocess.run(["node", "-e", "const S=require(process.argv[1]);console.log(JSON.stringify(["
    "S.expm([[0,1],[-1e-14,0]],1e7), S.expm([[-2000,0],[0,-1]],1), S.expm([[1e200,0],[0,2e200]],1e-200), S.eig([[1,0],[0,1.0000001]]).defective]))", str(MATH)],
    capture_output=True, text=True, check=True).stdout)
ok(np.allclose(X[0], expm(np.array([[0, 1], [-1e-14, 0]]) * 1e7), rtol=1e-8), f"long-time near-double expm {X[0]}")
ok(np.allclose(X[1], [[0, 0], [0, np.exp(-1)]], atol=1e-15), f"underflow-safe expm {X[1]}")
ok(np.allclose(X[2], [[np.e, 0], [0, np.e ** 2]], rtol=1e-12), f"scaled expm {X[2]}")
ok(X[3] is False, "nearby distinct eigenvalues are not defective")

# SymPy: lecture and authored examples
M = sp.Matrix
A = M([[5, 1], [3, 3]])
ok(A * M([1, 1]) == 6 * M([1, 1]) and A * M([1, -3]) == 2 * M([1, -3]) and (A ** 2).eigenvals() == {36: 1, 4: 1}, "lecture 40")
A = M([[4, 1], [2, 3]])
ok(A.eigenvals() == {5: 1, 2: 1} and A * M([1, -2]) == 2 * M([1, -2]), "s1 example")
t = sp.symbols("t")
y = sp.exp(5 * t) * M([1, 1]) + sp.exp(2 * t) * M([1, -2])
ok(sp.simplify(y.diff(t) - A * y) == sp.zeros(2, 1) and y.subs(t, 0) == M([2, -1]), "s3 example")
Mk = M([[sp.Rational(8, 10), sp.Rational(3, 10)], [sp.Rational(2, 10), sp.Rational(7, 10)]])
k = sp.symbols("k", integer=True, nonnegative=True)
uk = M([sp.Rational(6, 10), sp.Rational(4, 10)]) + sp.Rational(4, 10) * sp.Rational(1, 2) ** k * M([1, -1])
ok(all(sp.simplify(Mk ** int(n) * M([1, 0]) - uk.subs(k, n)) == sp.zeros(2, 1) for n in range(6)), "s2 Markov example")
ok(Mk * M([sp.Rational(6, 10), sp.Rational(4, 10)]) == M([sp.Rational(6, 10), sp.Rational(4, 10)]), "Markov steady state")
A = M([[-1, 2], [1, -2]])
ok(A * M([2, 1]) == M([0, 0]) and A * M([1, -1]) == -3 * M([1, -1]), "lecture 43")
ok(sp.simplify((M([[0, 1], [0, 0]]) * t).exp() - M([[1, t], [0, 1]])) == sp.zeros(2, 2), "e^{At} shear")
Rt = M([[sp.cos(t), sp.sin(t)], [-sp.sin(t), sp.cos(t)]])
ok(sp.simplify(Rt.diff(t) - M([[0, 1], [-1, 0]]) * Rt) == sp.zeros(2, 2) and Rt.subs(t, 0) == sp.eye(2), "s4 rotation solves Y' = AY, Y(0) = I")
for B in [M([[2, 3], [0, 4]]), M([[2, 0], [0, 4]]), M([[4, 0], [0, 2]]), M([[0, 2], [-4, 6]]), M([[2, 0], [3, 4]])]:
    ok(B.eigenvals() == {2: 1, 4: 1}, f"similar family {B.tolist()}")
S = M([[2, 1], [1, 2]])
Q = M([[1, 1], [1, -1]]) / sp.sqrt(2)
ok(sp.simplify(Q * sp.diag(3, 1) * Q.T - S) == sp.zeros(2, 2) and sp.simplify(Q.T * Q) == sp.eye(2), "s5 spectral form")
ok(M([[0, -1], [1, 0]]).eigenvals() == {sp.I: 1, -sp.I: 1} and M([[3, -1], [1, 3]]).eigenvals() == {3 + sp.I: 1, 3 - sp.I: 1}, "lecture 46")
Qr = M([[1, -1], [1, 1]]) / sp.sqrt(2)
ok(all(sp.simplify(sp.Abs(l) - 1) == 0 for l in Qr.eigenvals()), "orthogonal |lambda| = 1")
K = M([[2, -1], [-1, 2]])
ok(K.eigenvals() == {1: 1, 3: 1} and K * M([1, 1]) == M([1, 1]) and K * M([1, -1]) == 3 * M([1, -1]), "lecture 47 modes")
y = sp.Rational(1, 2) * sp.cos(t) * M([1, 1]) + sp.Rational(1, 2) * sp.cos(sp.sqrt(3) * t) * M([1, -1])
ok(sp.simplify(y.diff(t, 2) + K * y) == sp.zeros(2, 1) and y.subs(t, 0) == M([1, 0]) and y.diff(t).subs(t, 0) == M([0, 0]), "s6 example")

print(f"eigenvalues-systems math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
