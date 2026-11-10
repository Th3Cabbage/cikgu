"""Independent check of courses/mit-de/applications/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_applications_math_qa.py

Compares the RK4 trajectories with SciPy solve_ivp (DOP853, rtol 1e-12) for the three systems,
checks conserved quantities (box radius, predator-prey H), the predator-prey period against an
independent event-based measurement, the Lorenz critical points and sensitive dependence, the
behaviour claimed in the notes, and the worked examples with SymPy.
"""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/applications/dist/study_math.js"

NODE = r"""
const S = require(process.argv[1]);
const out = {};
out.box = ['x', 'y', 'z'].map(a => { const y0 = S.boxStart(a, 0.1); return {y0, tr: S.rk4(S.box, y0, 0.002, 15000).filter((_, i) => i % 500 === 0)}; });
out.pp = (() => { const f = S.predprey(300, 200); const tr = S.rk4(f, [400, 100], 0.001, 25000); return {tr: tr.filter((_, i) => i % 1000 === 0), H: tr.filter((_, i) => i % 1000 === 0).map(y => S.H(300, 200, y))}; })();
out.periods = [[300, 200, 400, 100], [300, 200, 310, 200], [300, 200, 600, 50]].map(a => S.period(...a, 40));
out.lorenz = (() => { const c = S.lorenzCritical(28, 8 / 3)[0], f = S.lorenz(10, 28, 8 / 3);
  const y0 = [c[0] + 3, c[1] + 2, c[2] - 4], y1 = [y0[0] + 1e-6, y0[1], y0[2]];
  const A = S.rk4(f, y0, 0.002, 15000), B = S.rk4(f, y1, 0.002, 15000);
  return {crit: S.lorenzCritical(28, 8 / 3), fcrit: S.lorenzCritical(28, 8 / 3).map(f), y0, A: A.filter((_, i) => i % 250 === 0), dist: A.map((a, i) => Math.hypot(a[0] - B[i][0], a[1] - B[i][1], a[2] - B[i][2])).filter((_, i) => i % 250 === 0)}; })();
out.l160 = (() => { const c = S.lorenzCritical(160, 8 / 3)[0]; return S.rk4(S.lorenz(10, 160, 8 / 3), [c[0] + 3, c[1] + 2, c[2] - 4], 0.001, 60000).filter((_, i) => i % 10 === 0).map(y => y[0]); })();
process.stdout.write(JSON.stringify(out));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], capture_output=True, text=True, check=True).stdout)
box = lambda t, y: [y[1] * y[2], -2 * y[0] * y[2], y[0] * y[1]]
for name, r in zip("xyz", out["box"]):
    tr = np.array(r["tr"])
    ts = np.arange(len(tr)) * 1.0
    sol = solve_ivp(box, (0, ts[-1]), r["y0"], t_eval=ts, rtol=1e-12, atol=1e-13, method="DOP853")
    ok(np.max(np.abs(sol.y.T - tr)) < 1e-6, f"box rk4 vs solve_ivp near {name}")
    ok(np.max(np.abs(np.linalg.norm(tr, axis=1) - 1)) < 1e-9, f"box radius conserved near {name}")
    ok(abs(np.linalg.norm(r["y0"]) - 1) < 1e-15, f"box start normalised {name}")
bx, by, bz = [np.array(r["tr"]) for r in out["box"]]
ok(np.min(bx[:, 0]) > 0.9, f"short axis stays near x = 1 (min {np.min(bx[:, 0]):.3f})")
ok(np.min(bz[:, 2]) > 0.9, f"long axis stays near z = 1 (min {np.min(bz[:, 2]):.3f})")
ok(np.min(by[:, 1]) < -0.9 and np.max(by[:, 1]) > 0.9, "middle axis: y swings from +1 to -1")

pp = lambda t, y: [y[0] * (1 - y[1] / 200), -y[1] * (1 - y[0] / 300)]
tr = np.array(out["pp"]["tr"])
ts = np.arange(len(tr)) * 1.0
sol = solve_ivp(pp, (0, ts[-1]), [400, 100], t_eval=ts, rtol=1e-12, atol=1e-10, method="DOP853")
ok(np.max(np.abs(sol.y.T - tr) / np.maximum(1, np.abs(tr))) < 1e-7, "predator-prey rk4 vs solve_ivp")
ok(np.ptp(out["pp"]["H"]) < 1e-9, "predator-prey H conserved")


def period_ref(mu1, mu2, e1, e2):
    a0 = np.arctan2(e2 - mu2, e1 - mu1)
    f = lambda t, y: [y[0] * (1 - y[1] / mu2), -y[1] * (1 - y[0] / mu1)]

    def ev(t, y):
        return np.sin(np.arctan2(y[1] - mu2, y[0] - mu1) - a0) if t > 0.5 else 1.0
    ev.direction = 1
    s = solve_ivp(f, (0, 40), [e1, e2], events=ev, rtol=1e-12, atol=1e-10, method="DOP853")
    for t, y in zip(s.t_events[0], s.y_events[0]):
        if np.cos(np.arctan2(y[1] - mu2, y[0] - mu1) - a0) > 0:
            return t


for args, got in zip([[300, 200, 400, 100], [300, 200, 310, 200], [300, 200, 600, 50]], out["periods"]):
    want = period_ref(*args)
    ok(got is not None and abs(got - want) < 2e-3, f"period {args}: {got} vs {want}")
ok(6.4 < out["periods"][0] < 6.6, f"Moler's period about 6.5: {out['periods'][0]}")
ok(abs(out["periods"][1] - 2 * np.pi) < 0.02, f"small orbit period near 2 pi: {out['periods'][1]}")
ok(out["periods"][2] > out["periods"][0], "larger orbits take longer")

L = out["lorenz"]
eta = np.sqrt(8 / 3 * 27)
ok(np.allclose(L["crit"], [[eta, eta, 27], [-eta, -eta, 27]]) and np.allclose(L["fcrit"], 0, atol=1e-12), "Lorenz critical points")
lor = lambda t, y: [10 * (y[1] - y[0]), 28 * y[0] - y[1] - y[0] * y[2], y[0] * y[1] - 8 / 3 * y[2]]
A = np.array(L["A"])
ts = np.arange(len(A)) * 0.5
sol = solve_ivp(lor, (0, 5), L["y0"], t_eval=ts[ts <= 5], rtol=1e-12, atol=1e-12, method="DOP853")
ok(np.max(np.abs(sol.y.T - A[: len(sol.t)])) < 1e-4, "Lorenz rk4 vs solve_ivp for t <= 5")
d = np.array(L["dist"])
ok(d[0] < 2e-6 and np.max(d) > 5, f"sensitive dependence: distance grows from 1e-6 to {np.max(d):.1f}")
ok(np.max(np.abs(A)) < 60, "Lorenz solution bounded")
x = np.array(out["l160"])[3000:]  # t from 30 to 60, step 0.01
def ncorr(x, k):
    a, b = x[:-k] - x[:-k].mean(), x[k:] - x[k:].mean()
    return float(np.dot(a, b) / np.sqrt(np.dot(a, a) * np.dot(b, b)))
best = max(ncorr(x, k) for k in range(50, 1500))
ok(best > 0.999, f"rho = 160 periodic after a transient (normalised lag correlation {best:.5f})")
x28 = A[20:, 0]  # rho = 28, t from 10 to 30 (sampled every 0.5): not periodic
best28 = max(ncorr(x28, k) for k in range(2, 20))
ok(best28 < 0.9, f"rho = 28 not periodic (best lag correlation {best28:.3f})")

# SymPy: examples
y, z, m1, m2 = sp.symbols("y z mu1 mu2", positive=True)
Hs = sp.log(y) - y / m1 + sp.log(z) - z / m2
f1, f2 = y * (1 - z / m2), -z * (1 - y / m1)
ok(sp.simplify(sp.diff(Hs, y) * f1 + sp.diff(Hs, z) * f2) == 0, "H conserved (symbolic)")
J = sp.Matrix([f1, f2]).jacobian([y, z]).subs({y: m1, z: m2})
ok(sp.simplify(J - sp.Matrix([[0, -m1 / m2], [m2 / m1, 0]])) == sp.zeros(2, 2) and set(J.eigenvals()) == {sp.I, -sp.I}, "Jacobian at (mu1, mu2)")
X, Y, Z = sp.symbols("X Y Z")
crit = sp.solve([10 * (Y - X), 28 * X - Y - X * Z, X * Y - sp.Rational(8, 3) * Z], [X, Y, Z], dict=True)
ok({(c[X], c[Z]) for c in crit} == {(0, 0), (6 * sp.sqrt(2), 27), (-6 * sp.sqrt(2), 27)}, "Lorenz critical points (symbolic)")
Jb = sp.Matrix([Y * Z, -2 * X * Z, X * Y]).jacobian([X, Y, Z]).subs({X: 1, Y: 0, Z: 0})
ok(set(Jb.eigenvals()) == {0, sp.sqrt(2) * sp.I, -sp.sqrt(2) * sp.I}, "box short axis eigenvalues: period 2 pi/sqrt2")
# Moler's matrix form A(y) y with state (z, x, y)
sig, rho, beta = sp.symbols("sigma rho beta")
Am = sp.Matrix([[-beta, 0, X], [0, -sig, sig], [-X, rho, -1]])
rhs = Am * sp.Matrix([Z, X, Y])
ok(sp.simplify(rhs - sp.Matrix([X * Y - beta * Z, sig * (Y - X), rho * X - Y - X * Z])) == sp.zeros(3, 1), "Moler's matrix form")
ok(sp.factor(Am.det()) == sp.factor(sig * (beta * (rho - 1) - X ** 2)) or sp.simplify(Am.det() - sig * (beta * (rho - 1) - X ** 2)) == 0, "det A = sigma(beta(rho - 1) - x^2)")
vals = {sig: 10, rho: 28, beta: sp.Rational(8, 3)}
etaq = sp.sqrt(sp.Rational(8, 3) * 27)
ok((Am.subs(vals).subs(X, etaq) * sp.Matrix([0, etaq, 0])) != sp.zeros(3, 1), "(eta, 0, 0): A singular but not an equilibrium")
ok(Am.subs(vals).subs(X, 0).det() == 720, "origin: A nonsingular yet an equilibrium (A(0) * 0 = 0)")

print(f"applications math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
