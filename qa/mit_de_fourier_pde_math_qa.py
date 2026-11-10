"""Independent check of courses/mit-de/fourier-pde/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_fourier_pde_math_qa.py

Checks the closed-form Fourier coefficients against numerical quadrature (scipy.integrate.quad),
partial sums converging to the functions, the Poisson kernel against its series, heat and wave
coefficients against quadrature, the wave sine series against d'Alembert, the boundary value
solutions with SymPy, and the worked examples.
"""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/fourier-pde/dist/study_math.js"

NODE = r"""
const S = require(process.argv[1]);
const out = {};
out.coef = {}; for (const f of ['square', 'ramp', 'saw', 'delta']) out.coef[f] = S.coefficients(f, 12);
out.ps = {}; for (const f of ['square', 'ramp', 'saw']) { const c = S.coefficients(f, 4000);
  out.ps[f] = [-2.5, -1, 0.4, 1.3, 2.9].map(x => [S.partialSum(c, x), S.target(f, x)]); }
out.gibbs = (() => { const c = S.coefficients('square', 201); let m = 0; for (let i = 1; i < 2000; i++) { m = Math.max(m, S.partialSum(c, i * 0.0005)); } return m; })();
out.pois = [[0.3, 0.2], [0.7, 1.4], [0.9, 3.0]].map(([r, t]) => S.poisson(r, t));
out.poisEdge = [0.999999999, 0.99999, 0.9999999999].map(r => S.poisson(r, 0));
out.deltaPi = [10, 11].map(N => S.partialSum(S.coefficients('delta', N), Math.PI));
out.deltaWeak = (() => { const c = S.coefficients('delta', 200); let s = 0, n = 20000; for (let i = 0; i < n; i++) { const x = -Math.PI + (i + 0.5) * 2 * Math.PI / n; s += S.partialSum(c, x) * Math.exp(Math.cos(x)) * 2 * Math.PI / n; } return s; })();
out.heat = {}; for (const s of ['one', 'tent', 'two']) out.heat[s] = S.heatCoeffs(s, 9);
out.heatVals = (() => { const B = S.heatCoeffs('two', 9); return [0.0, 0.01, 0.05].map(t => S.heat(B, t, 0.3)); })();
out.pluck = S.pluckCoeffs(1.1, 9);
out.wave = (() => { const d = S.pluckCoeffs(1.1, 6000); return [[0.4, 0.5], [1.3, 2.0], [2.2, 3.5], [0.7, 5.9]].map(([t, x]) => [S.wave(d, t, x), S.waveDAlembert(1.1, t, x)]); })();
out.green = [[0.2, 0.3], [0.5, 0.3], [0.9, 0.6]].map(([x, a]) => S.green(x, a));
process.stdout.write(JSON.stringify(out));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], capture_output=True, text=True, check=True).stdout)
P = np.pi
funcs = {"square": lambda x: np.sign(x), "ramp": abs, "saw": lambda x: x}
for name, f in funcs.items():
    c = out["coef"][name]
    a0 = quad(f, -P, P, points=[0])[0] / (2 * P)
    ok(abs(c["a0"] - a0) < 1e-10, f"{name} a0")
    for k in range(1, 13):
        ak = quad(lambda x: f(x) * np.cos(k * x), -P, P, points=[0], limit=200)[0] / P
        bk = quad(lambda x: f(x) * np.sin(k * x), -P, P, points=[0], limit=200)[0] / P
        ok(abs(c["a"][k - 1] - ak) < 1e-9 and abs(c["b"][k - 1] - bk) < 1e-9, f"{name} k={k}")
d = out["coef"]["delta"]
ok(abs(d["a0"] - 1 / (2 * P)) < 1e-15 and all(abs(a - 1 / P) < 1e-15 for a in d["a"]) and not any(d["b"]), "delta coefficients")
for name, pts in out["ps"].items():
    tol = 2e-3 if name != "ramp" else 1e-4
    ok(all(abs(s - t) < tol for s, t in pts), f"{name} partial sums converge {pts}")
ok(1.17 < out["gibbs"] < 1.19, f"Gibbs overshoot {out['gibbs']}")  # about 1.179 = 1 + 0.0895 * 2
for (r, t), v in zip([[0.3, 0.2], [0.7, 1.4], [0.9, 3.0]], out["pois"]):
    series = 1 / (2 * P) + sum(r ** n * np.cos(n * t) for n in range(1, 400)) / P
    ok(abs(v - series) < 1e-10, f"Poisson kernel r={r}")
for r_, v in zip([0.999999999, 0.99999, 0.9999999999], out["poisEdge"]):
    want = (1 + r_) / ((1 - r_) * 2 * P)
    ok(np.isfinite(v) and abs(v / want - 1) < 1e-6, f"Poisson near the edge r={r_}: {v} vs {want}")
ok(abs(out["deltaPi"][0] - 1 / (2 * P)) < 1e-12 and abs(out["deltaPi"][1] + 1 / (2 * P)) < 1e-12, "delta partial sums alternate at pi")
ok(abs(out["deltaWeak"] - np.e) < 1e-6, f"delta series against exp(cos x) tends to g(0) = e: {out['deltaWeak']}")
starts = {"one": lambda x: 1.0, "tent": lambda x: 2 * x if x <= 0.5 else 2 * (1 - x), "two": lambda x: np.sin(P * x) + 0.5 * np.sin(3 * P * x)}
for s, f in starts.items():
    for k in range(1, 10):
        Bk = 2 * quad(lambda x: f(x) * np.sin(k * P * x), 0, 1, points=[0.5])[0]
        ok(abs(out["heat"][s][k - 1] - Bk) < 1e-10, f"heat B_{k} for {s}")
want = [np.exp(-P ** 2 * t) * np.sin(0.3 * P) + 0.5 * np.exp(-9 * P ** 2 * t) * np.sin(0.9 * P) for t in [0, 0.01, 0.05]]
ok(np.allclose(out["heatVals"], want, atol=1e-14), "heat two-mode example")
p = 1.1
tent = lambda x: x / p if x <= p else (P - x) / (P - p)
for n in range(1, 10):
    dn = 2 / P * quad(lambda x: tent(x) * np.sin(n * x), 0, P, points=[p])[0]
    ok(abs(out["pluck"][n - 1] - dn) < 1e-10, f"pluck d_{n}")
ok(all(abs(a - b) < 2e-3 for a, b in out["wave"]), f"wave series = d'Alembert {out['wave']}")
ok(np.allclose(out["green"], [(1 - 0.3) * 0.2, 0.3 * 0.5, 0.6 * 0.1]), "green values")

x, a, t, r, th = sp.symbols("x a t r theta", real=True)
y = (x - x ** 2) / 2
ok(sp.simplify(-y.diff(x, 2) - 1) == 0 and y.subs(x, 0) == 0 and y.subs(x, 1) == 0, "uniform load")
y = (x - x ** 3) / 6
ok(sp.simplify(-y.diff(x, 2) - x) == 0 and y.subs(x, 1) == 0, "s1 example")
gl, gr = (1 - a) * x, a * (1 - x)
ok(sp.simplify((gl - gr).subs(x, a)) == 0 and sp.simplify(gr.diff(x) - gl.diff(x)) == -1, "point load: continuous, slope drop 1")
X, Y = sp.symbols("X Y", real=True)
lap = lambda u: sp.simplify(u.diff(X, 2) + u.diff(Y, 2))
ok(all(lap(u) == 0 for u in [X ** 2 - Y ** 2, 2 * X * Y, X ** 3 - 3 * X * Y ** 2, 3 * X ** 2 * Y - Y ** 3, sp.exp(X) * sp.cos(Y), X ** 4 - 6 * X ** 2 * Y ** 2 + Y ** 4]), "harmonic examples")
ok(lap(X ** 2 + Y ** 2) == 4, "x^2 + y^2 not harmonic")
u = sp.Rational(1, 2) + sp.Rational(1, 2) * (X ** 2 - Y ** 2)
ok(lap(u) == 0 and sp.simplify(u.subs({X: sp.cos(th), Y: sp.sin(th)}) - sp.cos(th) ** 2) == 0, "s5 disc example")
ok(sp.simplify(sp.integrate(sp.Symbol("z") * sp.sin(3 * sp.Symbol("z")), (sp.Symbol("z"), -sp.pi, sp.pi)) / sp.pi - sp.Rational(2, 3)) == 0, "sawtooth b_3 = 2/3")
ok(abs(float(sp.Sum(sp.Integer(-1) ** sp.Symbol("k", integer=True) / (2 * sp.Symbol("k", integer=True) + 1), (sp.Symbol("k", integer=True), 0, sp.oo)).doit()) - P / 4) < 1e-12, "Leibniz pi/4")
ok(abs(sum(1 / (2 * k + 1) ** 2 for k in range(200000)) - P ** 2 / 8) < 1e-5, "odd squares pi^2/8")
uw = sp.cos(t) * sp.sin(x) + sp.Rational(1, 2) * sp.cos(3 * t) * sp.sin(3 * x)
ok(sp.simplify(uw.diff(t, 2) - uw.diff(x, 2)) == 0 and sp.simplify(uw.subs(t, sp.pi) + uw.subs(t, 0)) == 0, "s7 wave example")
uh = sp.exp(-sp.pi ** 2 * t) * sp.sin(sp.pi * x)
ok(sp.simplify(uh.diff(t) - uh.diff(x, 2)) == 0, "heat mode")
G = sp.exp(-x ** 2 / (4 * t)) / sp.sqrt(4 * sp.pi * t)
ok(sp.simplify(G.diff(t) - G.diff(x, 2)) == 0, "heat kernel solves u_t = u_xx")

print(f"fourier-pde math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
