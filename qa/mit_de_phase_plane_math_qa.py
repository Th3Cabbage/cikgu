"""Independent check of courses/mit-de/phase-plane/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_phase_plane_math_qa.py

Compares eigenvalues/eigenvectors with numpy, the classification with an independent rule,
RK4 trajectories with SciPy, Jacobians with SymPy, conserved quantities of the tumbling box and
predator-prey, and the worked examples of the guide.
"""
import itertools
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/phase-plane/dist/study_math.js"

NODE = r"""
const SM = require(process.argv[1]);
const inp = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const eig = inp.mats.map(m => SM.eig2(m[0], m[1], m[2], m[3]));
const traj = inp.traj.map(c => {
  const M = SM.models[c.model](c.p);
  return SM.rk4(M.rhs, c.u0, 0.01, 600);
});
const crit = ['predprey', 'pendulum'].map(n => SM.criticalInfo(SM.models[n]({k: 0.5})));
const tumb = inp.tumb.map(u => ({J: SM.tumbling.jacobian(u), c: SM.tumbling.conserved(u), f: SM.tumbling.rhs(u)}));
const H = inp.traj.filter(c => c.model === 'predprey').map(c => {
  const M = SM.models.predprey(); const pts = SM.rk4(M.rhs, c.u0, 0.01, 600); return pts.map(SM.predpreyH);
});
process.stdout.write(JSON.stringify({eig, traj, crit, tumb, H}));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


vals = [-3, -1.5, 0, 0.5, 2]
mats = [list(m) for m in itertools.product(vals, repeat=4)]
mats += [[0, -1e-5, 1e-5, 0], [-1e-5, 0, 0, -2e-5], [1e-4, 2e-4, -3e-4, -4e-4], [0, 1e3, -2e3, -2e3]]  # small/large scales
mats += [[0, 1, -2, 3], [0, 1, 3, 0], [0, 1, -2, -2], [0, 1, -2, 0], [1, 2, -3, -4], [2, 4, 4, 2], [-2, 1, -3, -1], [-1, 1, 0, -1]]
traj = []
for p in [{"a": 1, "b": 2, "c": -3, "d": -4}, {"a": 0, "b": 1, "c": -2, "d": -2}, {"a": 0.5, "b": -2, "c": 1, "d": 0.25}]:
    for u0 in [[1, 0], [-0.5, 1.5]]:
        traj.append({"model": "linear", "p": p, "u0": u0})
for u0 in [[0.5, 0.5], [2, 1.2], [1.2, 0.8]]:
    traj.append({"model": "predprey", "p": {}, "u0": u0})
for u0 in [[1, 0], [3, 0.5], [-2, 2]]:
    traj.append({"model": "pendulum", "p": {"k": 0.5}, "u0": u0})
tumb = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0.3, -0.6, 0.74]]
out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps({"mats": mats, "traj": traj, "tumb": tumb}),
                                capture_output=True, text=True, check=True).stdout)


def kind(T, D, s=1.0):
    # independent rule, invariant under positive rescaling of A (compare with s = max |entry|)
    if abs(D) < 1e-10 * s * s:
        return "zero eigenvalue"
    if D < 0:
        return "saddle"
    if abs(T) < 1e-10 * s:
        return "center"
    disc = T * T - 4 * D
    if abs(disc) < 1e-10 * s * s:
        return "degenerate source" if T > 0 else "degenerate sink"
    if disc > 0:
        return "source" if T > 0 else "sink"
    return "spiral source" if T > 0 else "spiral sink"


for m, e in zip(mats, out["eig"]):
    A = np.array(m, float).reshape(2, 2)
    w = np.linalg.eigvals(A)
    got = sorted([complex(e["l1"]["re"], e["l1"]["im"]), complex(e["l2"]["re"], e["l2"]["im"])], key=lambda z: (z.real, z.imag))
    want = sorted(w, key=lambda z: (z.real, z.imag))
    sc = float(np.max(np.abs(A))) or 1.0
    ok(np.allclose(got, want, atol=1e-6 * max(sc, 1e-300), rtol=1e-6), f"eigenvalues {m}: {got} vs {want}")
    T, D = np.trace(A), A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
    ok(e["kind"] == kind(T, D, sc), f"kind {m}: {e['kind']} vs {kind(T, D, sc)}")
    ok(e["stable"] == bool(np.all(w.real < -1e-10 * sc)), f"stable {m}")
    if any(abs(z.imag) > 1e-10 * sc for z in w):
        ok(e["v1"] is None and e["v2"] is None, f"no real eigenvectors for complex eigenvalues {m}")
    for lk, vk in (("l1", "v1"), ("l2", "v2")):
        if e[vk] is not None:
            v = np.array(e[vk])
            ok(abs(np.linalg.norm(v) - 1) < 1e-12 and np.linalg.norm(A @ v - e[lk]["re"] * v) < 1e-6 * sc, f"eigenvector {m}")
# rescaling invariance of the classification
for m in [[1, 2, -3, -4], [0, 1, -2, 0], [0, 1, 3, 0], [0, 1, -2, -2], [-1, 0, 0, -2]]:
    kinds = set()
    for f_ in [1e-6, 1e-3, 1, 1e3]:
        r = json.loads(subprocess.run(["node", "-e", "const S=require(process.argv[1]);const m=JSON.parse(process.argv[2]);"
                                       "console.log(JSON.stringify(S.eig2(m[0],m[1],m[2],m[3]).kind))", str(MATH), json.dumps([x * f_ for x in m])],
                                      capture_output=True, text=True, check=True).stdout)
        kinds.add(r)
    ok(len(kinds) == 1, f"classification invariant under rescaling {m}: {kinds}")

rhs = {"linear": lambda p: (lambda t, u: [p["a"] * u[0] + p["b"] * u[1], p["c"] * u[0] + p["d"] * u[1]]),
       "predprey": lambda p: (lambda t, u: [u[0] - u[0] * u[1], u[0] * u[1] - u[1]]),
       "pendulum": lambda p: (lambda t, u: [u[1], -np.sin(u[0]) - p["k"] * u[1]])}
for c, pts in zip(traj, out["traj"]):
    pts = np.array(pts)
    tt = np.arange(len(pts)) * 0.01
    sol = solve_ivp(rhs[c["model"]](c["p"]), (0, tt[-1]), c["u0"], t_eval=tt, rtol=1e-11, atol=1e-12, method="DOP853")
    ok(np.max(np.abs(sol.y.T - pts)) < 1e-6 * max(1, np.max(np.abs(pts))), f"rk4 {c}")
for Hs in out["H"]:
    ok(np.ptp(Hs) < 1e-7, f"predator-prey H conserved (spread {np.ptp(Hs):.1e})")

# Jacobians and critical points
y, z, th, w_, k = sp.symbols("y z theta omega k")
Jpp = sp.Matrix([y - y * z, y * z - z]).jacobian([y, z])
for info in out["crit"][0]:
    pt = dict(zip((y, z), info["point"]))
    ok(np.allclose(np.array(Jpp.subs(pt), float), info["J"]), f"predprey J at {info['point']}")
pp = {tuple(i["point"]): i["eig"]["kind"] for i in out["crit"][0]}
ok(pp[(0, 0)] == "saddle" and pp[(1, 1)] == "center", f"predprey classes {pp}")
Jpend = sp.Matrix([w_, -sp.sin(th) - k * w_]).jacobian([th, w_])
for info in out["crit"][1]:
    ok(np.allclose(np.array(Jpend.subs({th: info["point"][0], w_: 0, k: 0.5}), float), info["J"]), f"pendulum J at {info['point']}")
pend = {round(i["point"][0], 3): i["eig"]["kind"] for i in out["crit"][1]}
ok(pend[0.0] == "spiral sink" and pend[3.142] == "saddle", f"pendulum classes {pend}")

# tumbling box
X, Y, Z = sp.symbols("x y z")
F = sp.Matrix([Y * Z, -2 * X * Z, X * Y])
JT = F.jacobian([X, Y, Z])
for u, r in zip(tumb, out["tumb"]):
    sub = dict(zip((X, Y, Z), u))
    ok(np.allclose(np.array(JT.subs(sub), float), r["J"]), f"tumbling J at {u}")
for q in [X ** 2 + Y ** 2 + Z ** 2, 2 * X ** 2 + Y ** 2, Y ** 2 + 2 * Z ** 2, X ** 2 - Z ** 2]:
    ok(sp.simplify(sp.Matrix([q]).jacobian([X, Y, Z]) * F)[0] == 0, f"conserved {q}")
for u, want in [((1, 0, 0), [0, sp.sqrt(2) * sp.I, -sp.sqrt(2) * sp.I]), ((0, 1, 0), [0, 1, -1]), ((0, 0, 1), [0, sp.sqrt(2) * sp.I, -sp.sqrt(2) * sp.I])]:
    ev = JT.subs(dict(zip((X, Y, Z), u))).eigenvals()
    ok(set(ev.keys()) == set(want), f"tumbling eigenvalues at {u}: {ev}")

# worked examples
t = sp.symbols("t")
yy = t - 1
ok(sp.simplify(yy.diff(t) - (t - yy)) == 0, "isocline solution y = t - 1")
yy = 2 * sp.exp(-t) - sp.exp(-2 * t)
ok(sp.simplify(yy.diff(t, 2) + 3 * yy.diff(t) + 2 * yy) == 0 and yy.subs(t, 0) == 1 and yy.diff(t).subs(t, 0) == 0, "sink example")
ok(set(sp.roots(sp.Poly(sp.Symbol("s") ** 2 + 2 * sp.Symbol("s") + 5)).keys()) == {-1 + 2 * sp.I, -1 - 2 * sp.I}, "spiral example roots")
A = sp.Matrix([[1, 2], [-3, -4]])
ok(A.eigenvals() == {-1: 1, -2: 1} and A * sp.Matrix([1, -1]) == -sp.Matrix([1, -1]) and A * sp.Matrix([2, -3]) == -2 * sp.Matrix([2, -3]), "2x2 example")
ok(sp.Matrix([[2, 4], [4, 2]]).eigenvals() == {6: 1, -2: 1}, "lecture [2 4; 4 2]")
Jp0 = sp.Matrix([[0, 1], [-1, -sp.Rational(1, 2)]])
ok(set(Jp0.eigenvals()) == {-sp.Rational(1, 4) + sp.sqrt(15) * sp.I / 4, -sp.Rational(1, 4) - sp.sqrt(15) * sp.I / 4}, "pendulum example eigenvalues")

print(f"phase-plane math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
