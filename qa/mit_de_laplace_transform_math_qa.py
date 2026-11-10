"""Independent check of courses/mit-de/laplace-transform/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_laplace_transform_math_qa.py

Compares the partial-fraction inverse y(t) with SciPy solve_ivp for first and second order equations
and every input (including double poles and undamped resonance), checks Y(s) against SymPy's
Laplace transform of the reference solution at sample s values, and verifies the worked examples.
"""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
MATH = ROOT / "courses/mit-de/laplace-transform/dist/study_math.js"
TS = list(np.linspace(0, 8, 33))

NODE = r"""
const SM = require(process.argv[1]);
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = cases.map(p => {
  const b = SM.build(p);
  return {y: p.ts.map(b.y), poles: b.poles.map(g => ({p: g.p, m: g.m, c: g.tcoef})), Y: [b.Yat([3.7, 0.4]), b.Yat([5, -1])]};
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
    return {"step": lambda t: 1.0, "exp": lambda t: np.exp(p["c"] * t), "cos": lambda t: np.cos(p["omega"] * t),
            "sin": lambda t: np.sin(p["omega"] * t)}.get(k, lambda t: 0.0)


def ref(p):
    f, kick = forcing(p), (1 if p["input"] == "delta" else 0)
    if p["order"] == "first":
        sol = solve_ivp(lambda t, y: [p["a"] * y[0] + f(t)], (0, TS[-1]), [p["y0"] + kick], t_eval=TS, rtol=1e-11, atol=1e-12, method="DOP853")
    else:
        sol = solve_ivp(lambda t, u: [u[1], f(t) - p["B"] * u[1] - p["C"] * u[0]], (0, TS[-1]), [p["y0"], p["v0"] + kick],
                        t_eval=TS, rtol=1e-11, atol=1e-12, method="DOP853")
    return sol.y[0]


cases = []
for inp in ["none", "delta", "step", "exp", "cos", "sin"]:
    for a, c in [(2, -1), (-1, -1), (0.5, 0), (-2, 1)]:
        cases.append({"order": "first", "a": a, "c": c, "omega": 1.5, "input": inp, "y0": 0.7, "v0": 0, "ts": TS})
    for B, C in [(3, 2), (1, 2), (0, 1), (4, 4), (0, 4), (2, 1)]:
        for c, w, y0, v0 in [(-1, 1, 0, 0), (-2, 2, 0.5, -1), (1, 1.5, -0.3, 0.8)]:
            cases.append({"order": "second", "B": B, "C": C, "c": c, "omega": w, "input": inp, "y0": y0, "v0": v0, "ts": TS})
# cancellation cases (Codex) and near-coincident poles (stability of the inverse)
cases += [
    {"order": "second", "B": 2, "C": 1, "c": 0, "omega": 1, "input": "none", "y0": 1, "v0": -1, "ts": TS},
    {"order": "first", "a": -1, "c": -2, "omega": 1, "input": "exp", "y0": -1, "v0": 0, "ts": TS},
]
for dc in [2e-7, 3e-6, 1e-4, 1e-3]:
    cases.append({"order": "second", "B": 2, "C": 1, "c": -1 + dc, "omega": 1, "input": "exp", "y0": 0.5, "v0": -1, "ts": TS, "near": True})
    cases.append({"order": "first", "a": 0.5, "c": 0.5 + dc, "omega": 1, "input": "exp", "y0": 0.2, "v0": 0, "ts": TS, "near": True})
out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps(cases), capture_output=True,
                                text=True, check=True).stdout)

t, s = sp.symbols("t s", positive=True)
for p, r in zip(cases, out):
    tag = {k: p.get(k) for k in ("order", "a", "B", "C", "input", "c", "omega", "y0", "v0")}
    want = ref(p)
    err = np.max(np.abs(np.array(r["y"]) - want) / np.maximum(1, np.abs(want)))
    ok(err < 1e-7, f"inverse vs solve_ivp {tag}: {err:.2e}")
    # Y(s) at two complex points against the formula [F + init]/P
    for z, Yv in zip([3.7 + 0.4j, 5 - 1j], r["Y"]):
        F = {"none": 0, "delta": 1, "step": 1 / z, "exp": 1 / (z - p["c"]), "cos": z / (z * z + p["omega"] ** 2),
             "sin": p["omega"] / (z * z + p["omega"] ** 2)}[p["input"]]
        if p["order"] == "first":
            Yw = (F + p["y0"]) / (z - p["a"])
        else:
            Yw = (F + (z + p["B"]) * p["y0"] + p["v0"]) / (z * z + p["B"] * z + p["C"])
        ok(abs(complex(*Yv) - Yw) < 1e-12 * max(1, abs(Yw)), f"Y(s) {tag}")
    # reported poles = poles of the reduced rational function (SymPy cancel), with multiplicity
    if not p.get("near"):
        S = sp.symbols("S")
        R = lambda v: sp.nsimplify(v)
        Fs = {"none": 0, "delta": 1, "step": 1 / S, "exp": 1 / (S - R(p["c"])), "cos": S / (S ** 2 + R(p["omega"]) ** 2),
              "sin": R(p["omega"]) / (S ** 2 + R(p["omega"]) ** 2)}[p["input"]]
        if p["order"] == "first":
            Ys = (Fs + R(p["y0"])) / (S - R(p["a"]))
        else:
            Ys = (Fs + (S + R(p["B"])) * R(p["y0"]) + R(p["v0"])) / (S ** 2 + R(p["B"]) * S + R(p["C"]))
        den = sp.denom(sp.cancel(sp.together(Ys)))
        want_poles = [(complex(k), m) for k, m in sp.roots(sp.Poly(den, S)).items()] if sp.degree(den, S) > 0 else []
        got = [(complex(*g["p"]), g["m"]) for g in r["poles"]]
        okp = len(got) == len(want_poles) and all(abs(a[0] - b[0]) < 1e-7 and a[1] == b[1] for a, b in
                                                  zip(sorted(got, key=lambda x: (x[0].real, x[0].imag)),
                                                      sorted(want_poles, key=lambda x: (x[0].real, x[0].imag))))
        ok(okp, f"reduced poles {tag}: {got} vs {want_poles}")

# SymPy: transforms used in the notes
a_, c_, w_ = sp.symbols("a c omega", positive=True)
ok(sp.simplify(sp.laplace_transform(sp.exp(-2 * t), t, s, noconds=True) - 1 / (s + 2)) == 0, "L[e^{at}]")
ok(sp.simplify(sp.laplace_transform(sp.cos(w_ * t), t, s, noconds=True) - s / (s ** 2 + w_ ** 2)) == 0, "L[cos]")
ok(sp.simplify(sp.laplace_transform(sp.sin(w_ * t), t, s, noconds=True) - w_ / (s ** 2 + w_ ** 2)) == 0, "L[sin]")
ok(sp.simplify(sp.laplace_transform(t * sp.exp(-t), t, s, noconds=True) - 1 / (s + 1) ** 2) == 0, "double pole")
a, c = sp.symbols("a c")
ok(sp.simplify(1 / ((s - a) * (s - c)) - (1 / (c - a)) * (1 / (s - c) - 1 / (s - a))) == 0, "partial fractions")
y = sp.Rational(4, 3) * sp.exp(2 * t) - sp.exp(-t) / 3
ok(sp.simplify(y.diff(t) - 2 * y - sp.exp(-t)) == 0 and y.subs(t, 0) == 1, "s1 example")
ok(sp.simplify(sp.apart(1 / (s * (s + 1) * (s + 2)), s) - (sp.Rational(1, 2) / s - 1 / (s + 1) + sp.Rational(1, 2) / (s + 2))) == 0, "s2 example PF")
T = sp.symbols("T", positive=True)
ok(sp.simplify(sp.integrate(sp.sin(T), (T, 0, t)) - (1 - sp.cos(t))) == 0, "1 * sin t")
ok(sp.simplify(1 / (s * (s ** 2 + 1)) - (1 / s - s / (s ** 2 + 1))) == 0, "s3 PF")
conv = sp.integrate(sp.exp(a * (t - T)) * sp.exp(c * T), (T, 0, t), conds="none")
ok(sp.simplify(conv - (sp.exp(c * t) - sp.exp(a * t)) / (c - a)) == 0, "e^{at} * e^{ct}")
# undamped resonance y'' + y = cos t from rest is t sin t / 2
res = [r for p, r in zip(cases, out) if p["order"] == "second" and p["B"] == 0 and p["C"] == 1 and p["input"] == "cos" and p["omega"] == 1 and p["y0"] == 0]
ok(len(res) == 1 and np.allclose(res[0]["y"], [x * np.sin(x) / 2 for x in TS], atol=1e-10), "resonance t sin t / 2")

print(f"laplace-transform math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
