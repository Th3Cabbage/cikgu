"""Independent numerical check of courses/mit-de/second-order/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_second_order_math_qa.py

Compares the JavaScript closed forms of y'' + B y' + C y = f with SciPy solve_ivp (rtol 1e-11)
for every input kind and damping case (including resonance and double roots), the impulse and
step responses, the gain formula, and the worked examples of the guide with SymPy.
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
MATH = ROOT / "courses/mit-de/second-order/dist/study_math.js"
TS = list(np.linspace(0, 12, 49))

NODE = r"""
const SM = require(process.argv[1]);
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = cases.map(p => {
  const r = SM.response(p);
  const g = SM.impulseResponse(p.B, p.C), st = SM.stepResponse(p.B, p.C);
  return {total: p.ts.map(r.total), kind: r.roots.kind, resonance: r.resonance, info: r.particularInfo,
          g: p.ts.map(g), r: p.ts.map(st), gain: SM.gain(p.B, p.C, p.omega || 1)};
});
process.stdout.write(JSON.stringify(out));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def forcing(p):
    k = p["input"]
    if k == "cos":
        return lambda t: np.cos(p["omega"] * t)
    if k == "exp":
        return lambda t: np.exp(p["s"] * t)
    if k == "step":
        return lambda t: 1.0
    return lambda t: 0.0


def ref(p, ts):
    f = forcing(p)
    v0 = p["v0"] + (1 if p["input"] == "impulse" else 0)
    sol = solve_ivp(lambda t, u: [u[1], f(t) - p["B"] * u[1] - p["C"] * u[0]], (0, ts[-1]), [p["y0"], v0],
                    t_eval=ts, rtol=1e-11, atol=1e-12, method="DOP853")
    return sol.y[0]


cases = []
for B, C in [(0, 4), (0.5, 4), (2, 5), (4, 4), (3, 2), (5, 1), (0, 0.25)]:
    for inp in ["none", "cos", "exp", "step", "impulse"]:
        for y0, v0 in [(1, 0), (-0.5, 2)]:
            p = {"B": B, "C": C, "input": inp, "y0": y0, "v0": v0, "omega": 1.3, "s": -0.5, "ts": TS}
            cases.append(p)
# resonance and special cases
cases += [
    {"B": 0, "C": 4, "input": "cos", "omega": 2, "s": 0, "y0": 0, "v0": 0, "ts": TS},          # undamped resonance
    {"B": 3, "C": 2, "input": "exp", "s": -1, "omega": 1, "y0": 0, "v0": 0, "ts": TS},          # simple root
    {"B": 3, "C": 2, "input": "exp", "s": -2, "omega": 1, "y0": 1, "v0": 0, "ts": TS},          # other root
    {"B": 4, "C": 4, "input": "exp", "s": -2, "omega": 1, "y0": 0.3, "v0": -1, "ts": TS},       # double root
    {"B": 1, "C": 2, "input": "cos", "omega": 1, "s": 0, "y0": 0.5, "v0": 0.5, "ts": TS},       # lecture example
    {"B": 0, "C": 4, "input": "cos", "omega": 1, "s": 0, "y0": 0, "v0": 0, "ts": TS},          # beats example
]
out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps(cases), capture_output=True,
                                text=True, check=True).stdout)

for p, r in zip(cases, out):
    tag = {k: p[k] for k in ("B", "C", "input", "y0", "v0", "omega", "s")}
    want = ref(p, TS)
    err = np.max(np.abs(np.array(r["total"]) - want) / np.maximum(1, np.abs(want)))
    ok(err < 1e-7, f"total vs solve_ivp {tag}: {err:.2e}")
    # impulse and step responses
    gref = ref({**p, "input": "impulse", "y0": 0, "v0": 0}, TS)
    rref = ref({**p, "input": "step", "y0": 0, "v0": 0}, TS)
    ok(np.allclose(r["g"], gref, atol=1e-8), f"impulse response {tag}")
    ok(np.allclose(r["r"], rref, atol=1e-8), f"step response {tag}")
    disc = p["B"] ** 2 - 4 * p["C"]
    want_kind = "critical" if abs(disc) < 1e-9 else ("overdamped" if disc > 0 else ("undamped" if p["B"] == 0 else "underdamped"))
    ok(r["kind"] == want_kind, f"kind {tag}: {r['kind']}")
    w = p.get("omega") or 1
    ok(abs(r["gain"] - 1 / np.sqrt((p["C"] - w * w) ** 2 + (p["B"] * w) ** 2)) < 1e-12 if (p["C"] - w * w) ** 2 + (p["B"] * w) ** 2 > 0 else True,
       f"gain {tag}")

lec = out[-2]["info"]
ok(abs(lec["M"] - 0.5) < 1e-12 and abs(lec["N"] - 0.5) < 1e-12 and abs(lec["G"] - 1 / np.sqrt(2)) < 1e-12
   and abs(lec["alpha"] - np.pi / 4) < 1e-12, "lecture example M = N = 1/2, G = 1/sqrt2, alpha = pi/4")
ok(out[-6]["resonance"] and out[-5]["resonance"] and out[-3]["resonance"], "resonance flags")

# SymPy: worked examples and formulas in the notes
t, s1, s2, B, C, w = sp.symbols("t s1 s2 B C omega", real=True)
y = sp.cos(2 * t) + sp.sin(2 * t)
ok(sp.simplify(y.diff(t, 2) + 4 * y) == 0 and y.subs(t, 0) == 1 and y.diff(t).subs(t, 0) == 2, "s1 example")
ok(sp.simplify(y - sp.sqrt(2) * sp.cos(2 * t - sp.pi / 4)) == 0, "s1 polar form")
y = (sp.cos(t) - sp.cos(2 * t)) / 3
ok(sp.simplify(y.diff(t, 2) + 4 * y - sp.cos(t)) == 0 and y.subs(t, 0) == 0 and y.diff(t).subs(t, 0) == 0, "s2 example")
m, k = sp.symbols("m k", positive=True)
g = sp.sin(sp.sqrt(k / m) * t) / (m * sp.sqrt(k / m))
ok(sp.simplify(m * g.diff(t, 2) + k * g) == 0 and g.subs(t, 0) == 0 and sp.simplify(g.diff(t).subs(t, 0) - 1 / m) == 0, "impulse g = sin/(m wn)")
y = sp.exp(-t) * (sp.cos(2 * t) + sp.sin(2 * t) / 2)
ok(sp.simplify(y.diff(t, 2) + 2 * y.diff(t) + 5 * y) == 0 and y.subs(t, 0) == 1 and y.diff(t).subs(t, 0) == 0, "s3 example")
ts_ = np.linspace(0, 6, 2001)
yv = np.exp(-ts_) * (np.cos(2 * ts_) + np.sin(2 * ts_) / 2)
ok(np.all(np.abs(yv) <= np.sqrt(5) / 2 * np.exp(-ts_) + 1e-12) and np.any(np.abs(yv) > np.exp(-ts_)),
   "s3 envelope is sqrt5/2 e^{-t} (and e^{-t} alone is exceeded)")
# gain peak: interior maximum at sqrt(C - B^2/2) iff B^2 < 2C (A = 1), else maximum at omega = 0
ws = np.linspace(0, 6, 60001)
for Bq, Cq in [(0.5, 4), (1, 2), (2, 2), (5, 1), (2.5, 4)]:
    G = 1 / np.sqrt((Cq - ws ** 2) ** 2 + (Bq * ws) ** 2)
    wpk = ws[np.argmax(G)]
    want = np.sqrt(Cq - Bq ** 2 / 2) if Bq ** 2 < 2 * Cq else 0.0
    ok(abs(wpk - want) < 1e-3, f"gain peak B={Bq} C={Cq}: {wpk} vs {want}")
gg = sp.exp(-t) - sp.exp(-2 * t)
rr = sp.Rational(1, 2) - sp.exp(-t) + sp.exp(-2 * t) / 2
ok(sp.simplify(gg.diff(t, 2) + 3 * gg.diff(t) + 2 * gg) == 0 and gg.subs(t, 0) == 0 and gg.diff(t).subs(t, 0) == 1, "s4 g")
ok(sp.simplify(rr.diff(t, 2) + 3 * rr.diff(t) + 2 * rr - 1) == 0 and rr.subs(t, 0) == 0 and sp.simplify(rr.diff(t) - gg) == 0, "s4 r")
# general step response formula with s1 s2 = C, s1 + s2 = -B
rgen = 1 / (s1 * s2) + (s2 * sp.exp(s1 * t) - s1 * sp.exp(s2 * t)) / (s1 * s2 * (s1 - s2))
ode = rgen.diff(t, 2) - (s1 + s2) * rgen.diff(t) + s1 * s2 * rgen - 1
ok(sp.simplify(ode) == 0 and sp.simplify(rgen.subs(t, 0)) == 0 and sp.simplify(rgen.diff(t).subs(t, 0)) == 0, "general step response")
ok(sp.simplify(rgen.diff(t) - (sp.exp(s1 * t) - sp.exp(s2 * t)) / (s1 - s2)) == 0, "r' = g")
y = t * sp.exp(-t)
ok(sp.simplify(y.diff(t, 2) + 3 * y.diff(t) + 2 * y - sp.exp(-t)) == 0, "s5 resonance t e^{-t}")
y = sp.exp(t) / 6
ok(sp.simplify(y.diff(t, 2) + 3 * y.diff(t) + 2 * y - sp.exp(t)) == 0, "s5 e^t/6")
y = t * sp.exp(t) / 2
ok(sp.simplify(y.diff(t, 2) - y - sp.exp(t)) == 0, "quiz y'' - y = e^t")
A_, M_, N_ = sp.symbols("A M N")
yp = M_ * sp.cos(w * t) + N_ * sp.sin(w * t)
eqs = sp.expand(A_ * yp.diff(t, 2) + B * yp.diff(t) + C * yp - sp.cos(w * t))
sol = sp.solve([eqs.coeff(sp.cos(w * t)), eqs.coeff(sp.sin(w * t))], [M_, N_])
D = (C - A_ * w ** 2) ** 2 + (B * w) ** 2
ok(sp.simplify(sol[M_] - (C - A_ * w ** 2) / D) == 0 and sp.simplify(sol[N_] - B * w / D) == 0, "M, N formulas")
yp = (sp.cos(t) + 2 * sp.sin(t)) / 5
ok(sp.simplify(yp.diff(t, 2) + 2 * yp.diff(t) + 2 * yp - sp.cos(t)) == 0, "s6 example M = 1/5, N = 2/5")
for (Bq, Cq, kind) in [(4, 4, "critical"), (2, 5, "under"), (5, 4, "over")]:
    d = Bq * Bq - 4 * Cq
    ok((d == 0) == (kind == "critical") and (d < 0) == (kind == "under"), f"quiz case {Bq},{Cq}")

print(f"second-order math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
