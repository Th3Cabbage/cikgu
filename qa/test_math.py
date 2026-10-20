"""Checks for courses/ode/native/ode_math.py and courses/ode/browser/dist/ode_math.js.

Run from anywhere with the repo's .venv python (needs numpy/scipy, installed with manimgl):
    .\\.venv\\Scripts\\python.exe qa\\test_math.py
Writes qa/results/math_results.json and exits nonzero on any failure.
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, "courses/ode/native"))
import ode_math as M  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def max_err(f, g, ts):
    return max(abs(f(t) - g(t)) for t in ts)


TS = np.linspace(0, 8, 161)

# 1. Known IVPs from the course (one per root case) and the closed forms quoted in the lessons.
known = [
    ("distinct y''-3y'+2y=0", (1, -3, 2, 1, 0), lambda t: 2 * math.exp(t) - math.exp(2 * t)),
    ("repeated y''+2y'+y=0", (1, 2, 1, 1, 0), lambda t: (1 + t) * math.exp(-t)),
    ("complex y''+2y'+5y=0", (1, 2, 5, 1, 0),
     lambda t: math.exp(-t) * (math.cos(2 * t) + 0.5 * math.sin(2 * t))),
    ("undamped y''+4y=0, y0=1, v0=2", (1, 0, 4, 1, 2), lambda t: math.cos(2 * t) + math.sin(2 * t)),
    ("overdamped x''+5x'+4x=0, y0=1, v0=0", (1, 5, 4, 1, 0),
     lambda t: (4 * math.exp(-t) - math.exp(-4 * t)) / 3),
]
for name, (a, b, c, y0, v0), exact in known:
    rel = max(abs(M.solution(t, a, b, c, y0, v0) - exact(t)) / max(1, abs(exact(t))) for t in TS)
    check(f"closed form: {name}", rel < 1e-12, f"max rel err {rel:.2e}")

# 2. Initial value and derivative, residual and an independent RK45 reference over a grid.
grid_a, grid_b, grid_c = [0.5, 1.3, 3], [0, 0.7, 2, 4, 6.5, 8], [0.5, 2, 4, 9]
ics = [(1, 0), (0, 1), (-3, 3), (2.2, -1.7)]
worst_ic = worst_res = worst_ref = 0.0
for a in grid_a:
    for b in grid_b:
        for c in grid_c:
            for y0, v0 in ics:
                worst_ic = max(worst_ic, abs(M.solution(0, a, b, c, y0, v0) - y0),
                               abs(M.derivative(0, a, b, c, y0, v0) - v0))
                # residual a y'' + b y' + c y with y'' from a central difference of the exact y'
                h = 1e-5
                for t in (0.3, 1.7, 4.0, 7.5):
                    y = M.solution(t, a, b, c, y0, v0)
                    dy = M.derivative(t, a, b, c, y0, v0)
                    ddy = (M.derivative(t + h, a, b, c, y0, v0) - M.derivative(t - h, a, b, c, y0, v0)) / (2 * h)
                    scale = max(1.0, abs(a * ddy), abs(b * dy), abs(c * y))
                    worst_res = max(worst_res, abs(a * ddy + b * dy + c * y) / scale)
                sol = solve_ivp(lambda t, s: [s[1], -(b * s[1] + c * s[0]) / a], (0, 8), [y0, v0],
                                t_eval=TS, method="DOP853", rtol=1e-11, atol=1e-12)
                ours = np.array([M.solution(t, a, b, c, y0, v0) for t in TS])
                worst_ref = max(worst_ref, float(np.max(np.abs(ours - sol.y[0]))))
check("y(0)=y0 and y'(0)=v0 on 288 parameter sets", worst_ic < 1e-12, f"max err {worst_ic:.2e}")
check("relative ODE residual (central difference)", worst_res < 1e-6, f"max {worst_res:.2e}")
check("agrees with scipy DOP853 reference on [0, 8]", worst_ref < 1e-7, f"max abs diff {worst_ref:.2e}")

# 3. Near critical damping: continuity across Delta = 0 and no division by zero.
a, c = 1.0, 4.0
crit = lambda t: M.solution(t, a, 4.0, c, 1.3, -0.4)
cont = 0.0
for eps in (1e-3, 1e-6, 1e-9, 1e-12, 1e-15):
    for sign in (1, -1):
        b = 4.0 + sign * eps
        for t in TS:
            v = M.solution(t, a, b, c, 1.3, -0.4)
            if not math.isfinite(v):
                cont = float("inf")
            cont = max(cont, abs(v - crit(t)) / eps if eps >= 1e-9 else abs(v - crit(t)))
check("near-critical solutions finite and continuous (|dy| = O(eps))", cont < 50, f"max {cont:.3g}")
check("exact critical preset classified as repeated",
      M.analyze(1, 4, 4)["case"] == "repeated" and M.analyze(1, 4, 4)["damping"] == "critical")
check("b = 4 + 1e-12 (snapped slider noise) treated as repeated", M.analyze(1, 4 + 1e-12, 4)["case"] == "repeated")
check("preset classes", [M.analyze(1, b, 4)["damping"] for b in (0, 2, 4, 5)]
      == ["undamped", "underdamped", "critical", "overdamped"])

# 4. Zero solution, extreme slider corners, plot bounds.
zero = [M.solution(t, 1, 2, 4, 0, 0) for t in TS]
check("y0 = v0 = 0 gives the identically zero solution", max(map(abs, zero)) == 0.0)
check("nice_bound(0) keeps a usable axis", M.nice_bound(0) == 1.0)
corner_max = 0.0
for a in (0.5, 3):
    for b in (0, 8):
        for c in (0.5, 9):
            for y0 in (-3, 3):
                for v0 in (-3, 3):
                    vals = [M.solution(t, a, b, c, y0, v0) for t in TS]
                    corner_max = max(corner_max, max(map(abs, vals)))
                    if not all(map(math.isfinite, vals)):
                        corner_max = float("inf")
check("all 32 slider-range corners finite", math.isfinite(corner_max), f"max |y| = {corner_max:.3f}")
check("nice_bound covers the corner maximum", M.nice_bound(corner_max) >= corner_max * 1.1 - 1e-9,
      f"bound {M.nice_bound(corner_max)}")

# 5. Input validation.
for bad, label in (((0, 1, 1), "a = 0"), ((float('nan'), 1, 1), "a = NaN"), ((1, float('inf'), 1), "b = inf")):
    try:
        M.solution(0.5, *bad, 1, 0)
        ok = False
    except ValueError:
        ok = True
    check(f"rejects {label}", ok)

# 6. JavaScript twin: same values, labels, bounds, formatting and validation.
js = os.path.join(PROJECT, "courses/ode/browser", "dist", "ode_math.js")
out = subprocess.run(["node", os.path.join(HERE, "math_grid.js"), js], capture_output=True, text=True, encoding="utf-8", check=True)
data = json.loads(out.stdout)
worst = 0.0
label_mismatch = 0
for row in data["rows"]:
    args = (row["a"], row["b"], row["c"], row["y0"], row["v0"])
    for t, yj, dyj in zip(data["ts"], row["y"], row["dy"]):
        worst = max(worst, abs(M.solution(t, *args) - yj) / max(1, abs(yj)),
                    abs(M.derivative(t, *args) - dyj) / max(1, abs(dyj)))
    info = M.analyze(*args[:3])
    if (info["case"], info["damping"], M.roots_text(*args[:3]), M.damping_text(*args[:3])) != \
            (row["case"], row["damping"], row["roots"], row["label"]):
        label_mismatch += 1
check(f"JS solution/derivative match Python on {len(data['rows'])} parameter sets x {len(data['ts'])} times",
      worst < 1e-13, f"max rel diff {worst:.2e}")
check("JS case/damping/root/label text identical to Python", label_mismatch == 0, f"{label_mismatch} mismatches")
py_bounds = [M.nice_bound(m) for m in [0, 1e-12, 0.5, 0.9, 0.95, 1, 2.7, 3.64, 7.9, 12, 123]]
check("JS niceBound identical", py_bounds == data["bounds"], str(data["bounds"]))
py_fmts = [M.fmt(x) for x in [-0.004, 0.004, -0.005, 1.005, -2.345, 3.14159, -0.0, 12.5]]
check("JS fmt identical", py_fmts == data["fmts"], str(data["fmts"]))
check("JS rejects a = 0, NaN, Infinity", data["errors"] == ["RangeError"] * 3, str(data["errors"]))

os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
with open(os.path.join(HERE, "results", "math_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
failed = [r for r in results if not r["ok"]]
print(f"\n{len(results) - len(failed)}/{len(results)} math checks passed")
sys.exit(1 if failed else 0)
