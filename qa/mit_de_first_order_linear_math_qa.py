"""Independent numerical check of courses/mit-de/first-order-linear/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_first_order_linear_math_qa.py

Evaluates the JavaScript closed forms through Node and compares them with SciPy's solve_ivp
(RK45, rtol 1e-11) on y' = a y + q(t). Step and delta inputs are integrated piecewise: the
delta adds its amplitude to y at t = T. Also checks the worked examples of the guide and
the identities the notes rely on. Prints a compact summary and exits 1 on any failure.
"""
import itertools
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/first-order-linear/dist/study_math.js"
TS = np.linspace(0, 10, 41)

NODE = r"""
const SM = require(process.argv[1]);
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = cases.map(p => {
  const r = SM.response(p);
  return {total: p.ts.map(r.total), driven: p.ts.map(r.drivenPart), nul: p.ts.map(r.nullPart),
          resonance: r.resonance, cos: r.cos, steady: r.steady};
});
process.stdout.write(JSON.stringify(out));
"""


def js(cases):
    proc = subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps(cases), capture_output=True,
                          text=True, check=True)
    return json.loads(proc.stdout)


def q_of(p):
    A, k = p["amp"], p["kind"]
    if k == "constant":
        return lambda t: A
    if k == "exp":
        return lambda t: A * np.exp(p["s"] * t)
    if k == "cos":
        return lambda t: A * np.cos(p["omega"] * t)
    if k == "step":
        return lambda t: A if t >= p["T"] else 0.0
    return lambda t: 0.0


def reference(p):
    a, q = p["a"], q_of(p)
    f = lambda t, y: a * y + q(t)
    kw = dict(rtol=1e-11, atol=1e-12, method="RK45")
    if p["kind"] in ("step", "delta") and 0 < p["T"] < TS[-1]:
        T = p["T"]
        left = TS[TS < T]
        y = np.empty_like(TS)
        s1 = solve_ivp(f, (0, T), [p["y0"]], t_eval=np.append(left, T), **kw)
        y[: len(left)] = s1.y[0][: len(left)]
        yT = s1.y[0][-1] + (p["amp"] if p["kind"] == "delta" else 0.0)
        right = TS[TS >= T]
        s2 = solve_ivp(f, (T, TS[-1]), [yT], t_eval=right, **kw)
        y[len(left):] = s2.y[0]
        return y
    if p["kind"] == "delta" and p["T"] == 0:
        return solve_ivp(f, (0, TS[-1]), [p["y0"] + p["amp"]], t_eval=TS, **kw).y[0]
    return solve_ivp(f, (0, TS[-1]), [p["y0"]], t_eval=TS, **kw).y[0]


def main():
    fails, n = [], 0
    cases = []
    for kind, a, y0, amp in itertools.product(["constant", "exp", "cos", "step", "delta"], [-2, -0.5, 0, 0.3],
                                              [-1, 0, 1.5], [0, 1, 2]):
        p = dict(kind=kind, a=a, y0=y0, amp=amp)
        if kind == "exp":
            for s in [-1, a, a + 1e-7, 0.2]:
                cases.append(dict(p, s=s))
            continue
        if kind == "cos":
            for w in [0.5, 2, 4]:
                cases.append(dict(p, omega=w))
            continue
        if kind in ("step", "delta"):
            for T in [0, 2.05, 6]:
                cases.append(dict(p, T=T))
            continue
        cases.append(p)
    for c in cases:
        c["ts"] = TS.tolist()
    res = js(cases)
    for p, r in zip(cases, res):
        ref = reference(p)
        got = np.array(r["total"])
        scale = max(1.0, np.max(np.abs(ref)))
        err = np.max(np.abs(got - ref)) / scale
        n += 1
        if err > 1e-7:
            fails.append((p["kind"], {k: v for k, v in p.items() if k != "ts"}, err))
        if abs(r["driven"][0]) > 1e-12 and not (p["kind"] == "delta" and p["T"] == 0):
            fails.append(("driven part must start at 0", p["kind"], r["driven"][0]))
    # identities used in the notes
    for a, w in [(-1, 1), (-0.5, 2), (0.3, 1.7), (0, 3)]:
        r = js([dict(kind="cos", a=a, y0=0, amp=1, omega=w, ts=[0])])[0]["cos"]
        n += 1
        d = w * w + a * a
        ok = (abs(-a * r["M"] + w * r["N"] - 1) < 1e-12 and abs(-w * r["M"] - a * r["N"]) < 1e-12
              and abs(r["G"] - 1 / np.sqrt(d)) < 1e-12
              and abs(r["G"] * np.cos(r["alpha"]) - r["M"]) < 1e-12 and abs(r["G"] * np.sin(r["alpha"]) - r["N"]) < 1e-12)
        if not ok:
            fails.append(("cos identities", a, w, r))
    # worked examples (closed forms in the notes)
    t = np.linspace(0, 3, 13)
    ex = {
        "s2 y = e^t - 1": (dict(kind="constant", a=1, y0=0, amp=1), np.exp(t) - 1),
        "s3 y' = -2y + e^t": (dict(kind="exp", a=-2, s=1, y0=1, amp=1), np.exp(-2 * t) + (np.exp(t) - np.exp(-2 * t)) / 3),
        "s3 resonance t e^{2t}": (dict(kind="exp", a=2, s=2, y0=0, amp=1), t * np.exp(2 * t)),
        "s4 steady (cos t + sin t)/2": (dict(kind="cos", a=-1, omega=1, y0=0.5, amp=1), (np.cos(t) + np.sin(t)) / 2),
        "s5 impulse 3 e^{-(t-2)}": (dict(kind="delta", a=-1, T=2, y0=0, amp=3), np.where(t >= 2, 3 * np.exp(-(t - 2)), 0)),
        "s5 step 1 - e^{-(t-2)}": (dict(kind="step", a=-1, T=2, y0=0, amp=1), np.where(t >= 2, 1 - np.exp(-(t - 2)), 0)),
    }
    for name, (p, want) in ex.items():
        got = np.array(js([dict(p, ts=t.tolist())])[0]["total"])
        n += 1
        if np.max(np.abs(got - want)) > 1e-10 * max(1, np.max(np.abs(want))):
            fails.append(("example", name))
    # a = 2t integrating-factor example: y' = 2ty + 2t, y(0) = 0 -> e^{t^2} - 1
    sol = solve_ivp(lambda tt, y: 2 * tt * y + 2 * tt, (0, 2), [0], t_eval=[2], rtol=1e-12, atol=1e-12)
    n += 1
    if abs(sol.y[0][-1] - (np.exp(4) - 1)) > 1e-7 * np.exp(4):
        fails.append(("example s7 a=2t", sol.y[0][-1]))
    print(json.dumps({"checks": n, "failures": len(fails)}))
    for f in fails[:10]:
        print("FAIL", f)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
