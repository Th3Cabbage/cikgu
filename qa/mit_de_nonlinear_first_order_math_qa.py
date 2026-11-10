"""Independent numerical check of courses/mit-de/nonlinear-first-order/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_nonlinear_first_order_math_qa.py

Compares the JavaScript RK4 solutions with SciPy solve_ivp (rtol 1e-11), the logistic closed
form with the ODE, the steady states/classification with numpy roots and finite-difference
slopes, and the worked examples of the guide with SymPy. Exits 1 on any failure.
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
MATH = ROOT / "courses/mit-de/nonlinear-first-order/dist/study_math.js"

NODE = r"""
const SM = require(process.argv[1]);
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = cases.map(c => {
  const m = SM.model(c.p);
  const s = SM.solve(c.p, c.y0, c.tMax, 0.01);
  const exact = c.p.model === 'logistic' ? c.ts.map(t => SM.logisticExact(c.p.a, c.p.b, c.y0, t)) : null;
  return {steady: m.steady, f: c.ys.map(m.f), points: s.points, blowup: s.blowup, exact};
});
process.stdout.write(JSON.stringify(out));
"""

fails = []
checks = 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def f_of(p):
    m = p["model"]
    if m == "logistic":
        return lambda y: p["a"] * y - p["b"] * y * y
    if m == "cubic":
        return lambda y: y - y ** 3
    if m == "harvest":
        return lambda y: p["a"] * y - p["b"] * y * y - p["h"]
    return lambda y: y * y - 1


def poly(p):
    m = p["model"]
    if m == "logistic":
        return [-p["b"], p["a"], 0]
    if m == "cubic":
        return [-1, 0, 1, 0]
    if m == "harvest":
        return [-p["b"], p["a"], -p["h"]]
    return [1, 0, -1]


cases = []
for a, b in itertools.product([0.5, 1, 2.3], [0.4, 1, 1.7]):
    for y0 in [0.05, 0.25, a / b * 1.4, -0.02]:
        cases.append({"p": {"model": "logistic", "a": a, "b": b}, "y0": y0, "tMax": 8})
for y0 in [-1.8, -0.5, 0.1, 0.9, 1.6]:
    cases.append({"p": {"model": "cubic"}, "y0": y0, "tMax": 8})
for h in [0, 0.1, 0.15, 0.25, 0.4]:
    for y0 in [0.2, 0.6, 1.2]:
        cases.append({"p": {"model": "harvest", "a": 1, "b": 1, "h": h}, "y0": y0, "tMax": 8})
for y0 in [-1.5, 0, 0.99, 1.2]:
    cases.append({"p": {"model": "square"}, "y0": y0, "tMax": 8})
ys = list(np.linspace(-2, 3, 11))
for c in cases:
    c["ts"] = [0, 0.5, 1, 2, 4, 8]
    c["ys"] = ys

out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps(cases), capture_output=True,
                                text=True, check=True).stdout)

for c, r in zip(cases, out):
    p, f = c["p"], f_of(c["p"])
    tag = f"{p} y0={c['y0']}"
    # f values
    ok(np.allclose(r["f"], [f(y) for y in ys], atol=1e-12), f"f values {tag}")
    # steady states = real roots, classified by numerical slope
    roots = sorted(x.real for x in np.roots(poly(p)) if abs(x.imag) < 1e-7)
    roots = sorted(set(round(x, 9) for x in roots))
    got = [s["Y"] for s in r["steady"]]
    ok(len(got) == len(roots) and np.allclose(got, roots, atol=1e-7), f"steady states {tag}: {got} vs {roots}")
    for s in r["steady"]:
        Y = s["Y"]
        slope = (f(Y + 1e-6) - f(Y - 1e-6)) / 2e-6
        want = "undecided" if abs(slope) < 1e-6 else ("stable" if slope < 0 else "unstable")
        ok(s["kind"] == want, f"classification {tag} Y={Y}: {s['kind']} vs {want}")
    # trajectory vs solve_ivp
    pts = np.array(r["points"])
    tEnd = pts[-1, 0]
    ref = solve_ivp(lambda t, y: [f(y[0])], (0, tEnd), [c["y0"]], t_eval=pts[:, 0], rtol=1e-11, atol=1e-12)
    if ref.success and len(ref.y[0]) == len(pts):
        keep = np.abs(ref.y[0]) <= 5  # plotted range; near a blowup the step error dominates
        err = 0.0 if not keep.any() else np.max(np.abs(ref.y[0][keep] - pts[keep, 1]) / np.maximum(1, np.abs(ref.y[0][keep])))
        ok(err < 1e-5, f"rk4 vs solve_ivp {tag}: rel err {err:.2e}")
    else:
        ok(False, f"reference failed {tag}")
    if r["exact"] is not None:
        a, b, y0 = p["a"], p["b"], c["y0"]
        idx = [int(round(t / 0.01)) for t in c["ts"] if t <= tEnd]
        for t, i in zip(c["ts"], idx):
            ok(abs(pts[i, 1]) > 5 or abs(r["exact"][c["ts"].index(t)] - pts[i, 1]) < 1e-6 * max(1, abs(pts[i, 1])),
               f"logistic exact vs rk4 {tag} t={t}")

# square from 1.2 blows up: exact y = (1 + C e^{2t})/(1 - C e^{2t}) with C = (1.2-1)/(1.2+1) -> t* = ln(11)/2
sq = [r for c, r in zip(cases, out) if c["p"]["model"] == "square" and c["y0"] == 1.2][0]
ok(sq["blowup"] and abs(sq["points"][-1][0] - np.log(11) / 2) < 0.05, "y^2 - 1 blowup time ln(11)/2")
# harvest h = 0.4 > a^2/4b = 0.25: no steady states, collapse
hv = [r for c, r in zip(cases, out) if c["p"]["model"] == "harvest" and c["p"]["h"] == 0.4]
ok(all(len(r["steady"]) == 0 for r in hv), "harvest beyond critical has no steady state")
hc = [r for c, r in zip(cases, out) if c["p"]["model"] == "harvest" and c["p"]["h"] == 0.25][0]
ok(len(hc["steady"]) == 1 and hc["steady"][0]["kind"] == "undecided", "harvest critical double root")

# exact logistic formula must not cross a blowup: y0 = -1, a = b = 1 blows up at t = ln 2
blow_js = subprocess.run(["node", "-e", "const S=require(process.argv[1]);"
                          "console.log(JSON.stringify([S.logisticExact(1,1,-1,8), S.logisticExact(1,1,-1,0.5),"
                          "S.logisticExact(1,1,2,8), S.logisticExact(2,1,-0.02,1)]))", str(MATH)],
                         capture_output=True, text=True, check=True).stdout
after, before, above, small = json.loads(blow_js.replace("null", "NaN")) if "null" in blow_js else json.loads(blow_js)
ok(after is None or (isinstance(after, float) and np.isnan(after)), "logisticExact returns NaN after the blowup time")
ok(abs(before - 1 / (1 - 2 * np.exp(-0.5))) < 1e-12, "logisticExact before the blowup")
ok(abs(above - 1 / (1 - 0.5 * np.exp(-8))) < 1e-12, "logisticExact from above capacity")
t_star = np.log((2 / 0.02 + 1) / 1) / 2  # a=2,b=1,y0=-0.02: d = -101, pole at e^{-2t} = 1/101
ok(np.isfinite(small) == (1 < t_star), "logisticExact small negative start")

# worked examples and identities (SymPy)
t, y, a, b, d, y0 = sp.symbols("t y a b d y0", real=True)
logi = a / (b + d * sp.exp(-a * t))
ok(sp.simplify(sp.diff(logi, t) - (a * logi - b * logi ** 2)) == 0, "logistic formula solves y' = ay - by^2")
ok(sp.simplify(logi.subs({t: 0, d: a / y0 - b}) - y0) == 0, "d = a/y(0) - b")
z = sp.Function("z")
ok(sp.simplify(sp.diff(1 / y, y) * (a * y - b * y ** 2) - (-a / y + b)) == 0, "z = 1/y gives z' = -az + b")
ex1 = 1 / (1 + 3 * sp.exp(-t))
ok(sp.simplify(sp.diff(ex1, t) - (ex1 - ex1 ** 2)) == 0 and ex1.subs(t, 0) == sp.Rational(1, 4), "example 1/(1+3e^-t)")
ok(sp.simplify(ex1.subs(t, sp.log(3)) - sp.Rational(1, 2)) == 0, "half capacity at ln 3")
ok(sp.solve(sp.diff(ex1, t, 2), t) == [sp.log(3)], "inflection at ln 3")
ok(sp.diff(y - y ** 2, y).subs(y, 0) == 1 and sp.diff(y - y ** 2, y).subs(y, 1) == -1, "logistic slopes")
ok(sp.diff(y - y ** 3, y).subs(y, 1) == -2 and sp.diff(y - y ** 3, y).subs(y, 0) == 1, "cubic slopes")
sqrt_sol = sp.sqrt(9 + t ** 2)
ok(sp.simplify(sp.diff(sqrt_sol, t) - t / sqrt_sol) == 0, "y = sqrt(9 + t^2) solves y' = t/y")
for cand in (t, -t):
    ok(sp.simplify(sp.diff(cand, t) - t / cand) == 0, f"{cand} solves y' = t/y")
blow = 2 / (4 - t ** 2)
ok(sp.simplify(sp.diff(blow, t) - t * blow ** 2) == 0 and blow.subs(t, 0) == sp.Rational(1, 2), "y = 2/(4-t^2)")
ok(sp.simplify(1 / (y - y ** 2) - (1 / y + 1 / (1 - y))) == 0, "partial fractions 1/(y-y^2)")
sep = sp.exp(-y)  # quiz: y' = t e^y separable
ok(sp.simplify(sp.diff(-sp.log(sp.Rational(1) - t ** 2 / 2), t) - t * sp.exp(-sp.log(1 - t ** 2 / 2))) == 0,
   "y' = t e^y separates (y = -ln(1 - t^2/2))")

print(f"nonlinear-first-order math QA: {checks - len(fails)}/{checks} passed")
for m in fails[:20]:
    print("FAIL", m)
sys.exit(1 if fails else 0)
