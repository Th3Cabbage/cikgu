"""Independent check of courses/mit-de/numerical-methods/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_numerical_methods_math_qa.py

Re-implements every method in Python from the published formulas (Euler, midpoint, Heun, RK4,
Bogacki-Shampine 3(2), Dormand-Prince 5(4), backward Euler) and compares single steps, stage
values and error estimates; checks observed orders, the lecture's numbers, adaptive accuracy
against SciPy solve_ivp (DOP853, rtol 1e-12), stiff behaviour, and the worked examples.
"""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/numerical-methods/dist/study_math.js"

NODE = r"""
const S = require(process.argv[1]);
const inp = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {};
out.steps = inp.steps.map(c => { const P = S.problem(c.prob, c.par); const s = S.step(c.m, P, c.t, c.y, c.h);
  return {yNew: s.yNew, err: s.err || null, stages: s.stages.map(q => ({t: q.t, y: q.y, s: q.s})), evals: s.evals}; });
out.fixed = inp.fixed.map(c => { const r = S.integrate(c.m, S.problem(c.prob, c.par), {h: c.h}); return {t: r.t, y: r.y, failed: r.failed}; });
out.adapt = inp.adapt.map(c => { const r = S.integrate(c.m, S.problem(c.prob, c.par), {rtol: c.rtol});
  return {t: r.t, y: r.y, acc: r.accepted, rej: r.rejected, evals: r.evals, failed: r.failed,
          hs: r.steps.filter(s => s.accepted).map(s => s.h), errs: r.steps.map(s => [s.errNorm, s.accepted, s.tol])}; });
out.order = ['euler', 'midpoint', 'heun', 'rk4'].map(m => S.orderExperiment(m, 0.1));
out.order2 = [0.3, 0.4, 0.07].map(h => ['euler', 'midpoint', 'rk4'].map(m => S.orderExperiment(m, h)));
out.beFail = (() => { const r = S.integrate('beuler', S.problem('nearsing'), {h: 0.1}); return {failed: r.failed, n: r.t.length}; })();
process.stdout.write(JSON.stringify(out));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


def F(prob, par=None):
    par = par or {}
    return {
        "exp2": lambda t, y: np.array([2 * y[0]]),
        "circle": lambda t, y: np.array([np.sqrt(max(0.0, 1 - y[0] ** 2))]),
        "order": lambda t, y: np.array([1 / (1 + t) ** 2]),
        "flame": lambda t, y: np.array([y[0] ** 2 - y[0] ** 3]),
        "nearsing": lambda t, y: np.array([2 * (0.25 - t) * y[0] ** 2]),
        "stiffcos": lambda t, y: np.array([-100 * (y[0] - np.cos(t)) - np.sin(t)]),
        "oscillator": lambda t, y: np.array([y[1], -y[0]]),
        "vdp": lambda t, y: np.array([y[1], par.get("mu", 5) * (1 - y[0] ** 2) * y[1] - y[0]]),
    }[prob]


DPc = [0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1]
DPa = [[], [1 / 5], [3 / 40, 9 / 40], [44 / 45, -56 / 15, 32 / 9], [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
       [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656], [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]]
DPb4 = [5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40]


def ref_step(m, f, t, y, h):
    y = np.array(y, float)
    s1 = f(t, y)
    if m == "euler":
        return y + h * s1, None
    if m == "midpoint":
        return y + h * f(t + h / 2, y + h / 2 * s1), None
    if m == "heun":
        return y + h / 2 * (s1 + f(t + h, y + h * s1)), None
    if m == "rk4":
        k2 = f(t + h / 2, y + h / 2 * s1); k3 = f(t + h / 2, y + h / 2 * k2); k4 = f(t + h, y + h * k3)
        return y + h / 6 * (s1 + 2 * k2 + 2 * k3 + k4), None
    if m == "bs23":
        k2 = f(t + h / 2, y + h / 2 * s1); k3 = f(t + 3 * h / 4, y + 3 * h / 4 * k2)
        yn = y + h / 9 * (2 * s1 + 3 * k2 + 4 * k3); k4 = f(t + h, yn)
        y2 = y + h * (7 / 24 * s1 + 1 / 4 * k2 + 1 / 3 * k3 + 1 / 8 * k4)  # embedded second-order solution
        return yn, yn - y2
    if m == "dp45":
        K = [s1]
        for j in range(1, 7):
            K.append(f(t + DPc[j] * h, y + h * sum(DPa[j][i] * K[i] for i in range(j))))
        y5 = y + h * sum(DPa[6][i] * K[i] for i in range(6))
        y4 = y + h * sum(DPb4[i] * K[i] for i in range(7))
        return y5, y5 - y4
    if m == "beuler":
        Y = y.copy()
        for _ in range(60):
            G = Y - h * f(t + h, Y) - y
            J = np.zeros((len(y), len(y)))
            for j in range(len(y)):
                d = 1e-7 * max(1, abs(Y[j])); Yd = Y.copy(); Yd[j] += d
                J[:, j] = (Yd - h * f(t + h, Yd) - y - G) / d
            Y = Y - np.linalg.solve(J, G)
        return Y, None


steps = []
for m in ["euler", "midpoint", "heun", "rk4", "bs23", "dp45", "beuler"]:
    for prob, t, y, h, par in [("exp2", 0, [10], 1.0, {}), ("nearsing", 0.1, [20.0], 0.05, {}), ("oscillator", 0.3, [0.2, 0.9], 0.2, {}),
                               ("vdp", 0.0, [2.0, 0.0], 0.05, {"mu": 5}), ("stiffcos", 0.2, [0.9], 0.03, {}), ("flame", 10, [0.3], 2.0, {})]:
        steps.append({"m": m, "prob": prob, "t": t, "y": y, "h": h, "par": par})
fixed = [{"m": "euler", "prob": "exp2", "h": 1}, {"m": "midpoint", "prob": "exp2", "h": 1}, {"m": "rk4", "prob": "exp2", "h": 1},
         {"m": "midpoint", "prob": "circle", "h": np.pi / 32}, {"m": "euler", "prob": "stiffcos", "h": 0.03},
         {"m": "beuler", "prob": "stiffcos", "h": 0.1}, {"m": "euler", "prob": "oscillator", "h": 2 * np.pi / 36},
         {"m": "rk4", "prob": "oscillator", "h": 2 * np.pi / 36}]
adapt = []
for m in ["bs23", "dp45"]:
    for prob, par, rtol in [("exp2", {}, 1e-3), ("nearsing", {}, 1e-3), ("nearsing", {}, 1e-6), ("oscillator", {}, 1e-5),
                            ("flame", {"delta": 0.01}, 1e-4), ("vdp", {"mu": 5}, 1e-5)]:
        adapt.append({"m": m, "prob": prob, "par": par, "rtol": rtol})
out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps({"steps": steps, "fixed": fixed, "adapt": adapt}),
                                capture_output=True, text=True, check=True).stdout)

for c, r in zip(steps, out["steps"]):
    f = F(c["prob"], c["par"])
    yn, e = ref_step(c["m"], f, c["t"], c["y"], c["h"])
    sc = max(1.0, np.max(np.abs(yn)))
    ok(np.allclose(r["yNew"], yn, rtol=1e-10, atol=1e-10 * sc), f"step {c['m']} {c['prob']}: {r['yNew']} vs {yn}")
    if e is not None:
        ok(np.allclose(r["err"], e, rtol=1e-8, atol=1e-12 * sc), f"error estimate {c['m']} {c['prob']}: {r['err']} vs {e}")
    for st in r["stages"]:
        ok(np.allclose(st["s"], f(st["t"], np.array(st["y"])), rtol=1e-12, atol=1e-12 * sc), f"stage slope {c['m']} {c['prob']}")
    want_evals = {"euler": 1, "midpoint": 2, "heun": 2, "rk4": 4, "bs23": 4, "dp45": 7}.get(c["m"])
    if want_evals:
        ok(r["evals"] == want_evals, f"evaluations {c['m']}: {r['evals']}")

fx = out["fixed"]
ok(np.allclose([v[0] for v in fx[0]["y"]], [10, 30, 90, 270]), "Euler 10, 30, 90, 270")
ok(np.allclose([v[0] for v in fx[1]["y"]], [10, 50, 250, 1250]), "midpoint 10, 50, 250, 1250")
ok(abs(fx[2]["y"][1][0] - 70) < 1e-12, "RK4 first step 70")
ok(abs(fx[3]["y"][-1][0] - 0.997) < 0.002, f"midpoint circle final ~0.997: {fx[3]['y'][-1][0]}")
ok(abs(fx[4]["y"][-1][0]) > 10, f"Euler on stiff problem with h = 0.03 blows up: {fx[4]['y'][-1][0]}")
ok(max(abs(v[0] - np.cos(t)) for t, v in zip(fx[5]["t"], fx[5]["y"])) < 2e-3, "backward Euler stable and accurate with h = 0.1")
h = 2 * np.pi / 36
r_end = np.hypot(*fx[6]["y"][-1])
ok(abs(r_end - (1 + h * h) ** 18) < 1e-10, f"Euler oscillator radius (1 + h^2)^(n/2): {r_end}")
ok(abs(np.hypot(*fx[7]["y"][-1]) - 1) < 1e-5, "RK4 oscillator stays near the circle")

orders = out["order"]
ok(abs(orders[0]["v1"] - 0.538955) < 1e-6 and abs(orders[0]["v2"] - 0.519114) < 1e-6, f"lecture ODE1 values {orders[0]}")
ok([o["p"] for o in orders] == [1, 2, 2, 4], f"observed orders {[o['p'] for o in orders]}")
for row in out["order2"]:
    ok([o["p"] for o in row] == [1, 2, 4] and all(abs(o["h1"] - 2 * o["h2"]) < 1e-15 for o in row), f"nested meshes give orders 1, 2, 4: {[(o['h1'], o['p']) for o in row]}")
ok(out["beFail"]["failed"] is not None and out["beFail"]["n"] == 1, f"backward Euler without a real root is not accepted: {out['beFail']}")

for c, r in zip(adapt, out["adapt"]):
    tag = f"{c['m']} {c['prob']} rtol={c['rtol']}"
    ok(r["failed"] is None and abs(r["t"][-1] - (2 / c["par"]["delta"] if c["prob"] == "flame" else {"exp2": 3, "nearsing": 1, "oscillator": 2 * np.pi, "vdp": max(20, 3 * c["par"].get("mu", 5))}[c["prob"]])) < 1e-9,
       f"reaches tf {tag}")
    ok(all((e <= tol) == acc for e, acc, tol in r["errs"]), f"accept rule {tag}")
    f = F(c["prob"], c["par"])
    y0 = {"exp2": [10], "nearsing": [15.9], "oscillator": [0, 1], "flame": [0.01], "vdp": [2, 0]}[c["prob"]]
    sol = solve_ivp(f, (0, r["t"][-1]), y0, t_eval=r["t"], rtol=1e-12, atol=1e-14, method="DOP853")
    rel = np.max(np.abs(np.array(r["y"]).T - sol.y) / np.maximum(np.abs(sol.y), 1e-3))
    bound = {"exp2": 50, "nearsing": 500, "oscillator": 1000, "flame": 2000, "vdp": 10000}[c["prob"]] * c["rtol"]  # global error can exceed the local tolerance
    ok(rel < bound, f"global accuracy {tag}: {rel:.2e} (bound {bound:.1e})")
ns = [r for c, r in zip(adapt, out["adapt"]) if c["prob"] == "nearsing" and c["m"] == "bs23" and c["rtol"] == 1e-3][0]
peak = max(v[0] for v in ns["y"])
tt = np.linspace(0, 1, 200001); ex = 1 / (1 / 15.9 - 0.5 * tt + tt * tt)
ok(abs(np.max(ex) - 1 / (1 / 15.9 - 1 / 16)) < 1 and 2540 < np.max(ex) < 2550, "exact near-singular peak 2544")
ok(1000 < peak <= 2600, f"adaptive solution climbs towards the peak: {peak}")
hs, ts = np.array(ns["hs"]), np.array(ns["t"][1:])
ok(hs[np.argmin(np.abs(ts - 0.25))] < 0.2 * np.max(hs), "steps shrink near t = 1/4")
e2 = [r for c, r in zip(adapt, out["adapt"]) if c["prob"] == "exp2"]
ok(e2[1]["evals"] < e2[0]["evals"] * 3, "ode45 not much more expensive than ode23 on a smooth problem")

# worked examples
y = 1.0
for _ in range(2):
    y += 0.5 * (-y)
ok(abs(y - 0.25) < 1e-15, "s1 example Euler 0.25")
yb, eb = ref_step("bs23", lambda t, y: y, 0, [1.0], 0.1)
ebs = 0.1 / 72 * (-5 * 1 + 6 * 1.05 + 8 * 1.07875 - 9 * yb[0])
ok(abs(yb[0] - 1.1051666667) < 1e-9 and abs(ebs + 2.29e-5) < 2e-7, f"s4 example BS23 {yb[0]}, {ebs}")
ok(abs(100 * (1 + 0.06 / 12) ** 120 - 181.94) < 0.01, "interest example ~182")
ok(abs(((1 - 0.05 * 100) ** 3) + 64) < 1e-12 and abs((1 / 6) ** 2 - 0.0277778) < 1e-6, "s5 stiff example")

print(f"numerical-methods math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
