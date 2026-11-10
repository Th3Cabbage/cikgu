"""Independent check of courses/mit-de/networks-and-methods/dist/study_math.js.

    .venv\\Scripts\\python.exe qa\\mit_de_networks_and_methods_math_qa.py

Builds each undetermined-coefficients answer from the JavaScript coefficients as a SymPy expression
and checks P(D) y_p = f exactly at sample points, checks the multiplicity, compares the convolution
with SciPy solve_ivp from rest, checks the impedance, and verifies the worked examples with SymPy.
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
MATH = ROOT / "courses/mit-de/networks-and-methods/dist/study_math.js"

NODE = r"""
const SM = require(process.argv[1]);
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = cases.map(p => {
  if (p.kind === 'z') return SM.impedance(p.R, p.L, p.C, p.w);
  const s = SM.ucSolve(p);
  const conv = p.ts.map(t => SM.convolution(p.B, p.C, s.f, t, 400));
  const res = p.ts.map(t => SM.residual(s, p.B, p.C, t) / Math.max(1, Math.abs(s.f(t))));
  return {m: s.multiplicity, coeffs: s.coeffs, s: s.s, yp: p.ts.map(s.yp), conv, trial: SM.trialTex(s), res};
});
process.stdout.write(JSON.stringify(out));
"""

fails, checks = [], 0


def ok(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


t = sp.symbols("t", real=True)
TS = [0.0, 0.4, 1.1, 2.0, 3.0]
cases = [{"B": -3, "C": 1, "form": "exp", "k": 2, "s": 2.5, "w": 1, "amp": 4, "ts": TS}]  # Codex residual case
for B, C in [(-3, 2), (1, 1), (0, 1), (2, 1), (0, 0), (1, 0), (-2, 1), (0, 4), (3, 2)]:
    for form, k in itertools.product(["poly", "exp", "cos"], [0, 1, 2]):
        for s in ([None] if form != "exp" else [1, 2, -1, 0.5]):
            for w in ([None] if form != "cos" else [1, 2]):
                cases.append({"B": B, "C": C, "form": form, "k": k, "s": s or 0, "w": w or 1, "amp": 1.5, "ts": TS})
zc = [{"kind": "z", "R": R, "L": L, "C": Cc, "w": w} for R, L, Cc, w in
      [(10, 0.1, 1e-4, 100), (10, 0.1, 1e-4, 1 / np.sqrt(1e-5)), (5, 0.5, 1e-3, 30)]]
out = json.loads(subprocess.run(["node", "-e", NODE, str(MATH)], input=json.dumps(cases + zc), capture_output=True,
                                text=True, check=True).stdout)

for p, r in zip(cases, out):
    tag = {k: p[k] for k in ("B", "C", "form", "k", "s", "w")}
    sre, sim = r["s"]
    s_sym = sp.nsimplify(sre) + sp.I * sp.nsimplify(sim)
    q = sum((sp.Float(a[0]) + sp.I * sp.Float(a[1])) * t ** j for j, a in enumerate(r["coeffs"]))
    y = sp.re(sp.expand_complex(q * sp.exp(s_sym * t)))
    f = p["amp"] * t ** p["k"] * sp.exp(sre * t) * sp.cos(sim * t)
    res = sp.lambdify(t, y.diff(t, 2) + p["B"] * y.diff(t) + p["C"] * y - f, "numpy")
    vals = np.array([res(x) for x in TS], dtype=float)
    scale = max(1.0, max(abs(float(f.subs(t, x))) for x in TS))
    ok(np.max(np.abs(vals)) < 1e-8 * scale, f"residual {tag}: {np.max(np.abs(vals)):.2e}")
    ylam = sp.lambdify(t, y, "numpy")
    ok(max(abs(v) for v in r["res"]) < 1e-9 * max(1.0, max(abs(c) for a in r["coeffs"] for c in a)), f"displayed residual {tag}")
    ok(np.allclose([ylam(x) for x in TS], r["yp"], rtol=1e-10, atol=1e-10), f"yp values {tag}")
    # multiplicity
    P = lambda z: z * z + p["B"] * z + p["C"]
    dP = lambda z: 2 * z + p["B"]
    z = complex(sre, sim)
    want_m = 0 if abs(P(z)) > 1e-9 else (1 if abs(dP(z)) > 1e-9 else 2)
    ok(r["m"] == want_m, f"multiplicity {tag}: {r['m']} vs {want_m}")
    # convolution = solution from rest
    fn = sp.lambdify(t, f, "numpy")
    sol = solve_ivp(lambda tt, u: [u[1], fn(tt) - p["B"] * u[1] - p["C"] * u[0]], (0, TS[-1]), [0, 0],
                    t_eval=TS, rtol=1e-11, atol=1e-12, method="DOP853")
    ok(np.allclose(r["conv"], sol.y[0], rtol=1e-6, atol=1e-7), f"convolution vs solve_ivp {tag}")

for p, r in zip(zc, out[len(cases):]):
    X = p["w"] * p["L"] - 1 / (p["w"] * p["C"])
    ok(abs(r["re"] - p["R"]) < 1e-12 and abs(r["im"] - X) < 1e-9 and abs(r["abs"] - np.hypot(p["R"], X)) < 1e-9
       and abs(r["w0"] - 1 / np.sqrt(p["L"] * p["C"])) < 1e-9, f"impedance {p}")
ok(abs(out[len(cases)]["im"] + 90) < 1e-9 and abs(out[len(cases)]["abs"] - np.sqrt(8200)) < 1e-9, "book circuit Z = 10 - 90i")
ok(abs(out[len(cases) + 1]["im"]) < 1e-9, "reactance zero at w0")

# SymPy worked examples
ex = [
    (t - 1, (1, 1), t, "y'' + y' + y = t"),
    (t ** 2 - 2 * t, (1, 1), t ** 2, "y'' + y' + y = t^2"),
    (3 + 2 * t, (-3, 2), 4 * t, "y'' - 3y' + 2y = 4t"),
    (t * sp.exp(2 * t), (-3, 2), sp.exp(2 * t), "resonance e^{2t}"),
    (t * sp.exp(t) / 2, (0, -1), sp.exp(t), "y'' - y = e^t"),
    (t, (0, 1), t, "y'' + y = t"),
]
for y, (B, C), f, name in ex:
    ok(sp.simplify(y.diff(t, 2) + B * y.diff(t) + C * y - f) == 0, name)
y = sp.cos(t) * sp.log(sp.cos(t)) + t * sp.sin(t)
ok(sp.simplify(y.diff(t, 2) + y - 1 / sp.cos(t)) == 0, "VP sec t example")
s1, s2, T = sp.symbols("s1 s2 T")
y1, y2 = sp.exp(s1 * t), sp.exp(s2 * t)
W = sp.simplify(y1 * y2.diff(t) - y2 * y1.diff(t))
ok(sp.simplify(W - (s2 - s1) * sp.exp((s1 + s2) * t)) == 0, "Wronskian of exponentials")
# VP kernel equals g(t - T)
kern = sp.simplify((-y1 * y2.subs(t, T) + y2 * y1.subs(t, T)) / W.subs(t, T))
g = (sp.exp(s2 * (t - T)) - sp.exp(s1 * (t - T))) / (s2 - s1)
ok(sp.simplify(kern - g) == 0, "VP kernel = g(t - T)")
r_ = sp.symbols("r")
y1, y2 = sp.exp(r_ * t), t * sp.exp(r_ * t)
W2 = sp.simplify(y1 * y2.diff(t) - y2 * y1.diff(t))
kern2 = sp.simplify((-y1 * y2.subs(t, T) + y2 * y1.subs(t, T)) / W2.subs(t, T))
ok(sp.simplify(W2 - sp.exp(2 * r_ * t)) == 0 and sp.simplify(kern2 - (t - T) * sp.exp(r_ * (t - T))) == 0,
   "double root: W = e^{2rt}, g = t e^{rt}")
ok(sp.simplify(sp.limit((sp.exp(s2 * t) - sp.exp(s1 * t)) / (s2 - s1), s2, s1) - t * sp.exp(s1 * t)) == 0, "limit of quotient")
w, L, Cc, R = sp.symbols("omega L C R", positive=True)
Z = sp.I * w * L + R + 1 / (sp.I * w * Cc)
ok(sp.simplify(Z - (R + sp.I * (w * L - 1 / (w * Cc)))) == 0, "impedance formula")

print(f"networks-and-methods math QA: {checks - len(fails)}/{checks} passed")
for m_ in fails[:20]:
    print("FAIL", m_)
sys.exit(1 if fails else 0)
