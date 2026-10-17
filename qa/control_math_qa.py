"""Independent mathematical checks for the Control Bootcamp companion (SciPy/NumPy reference).

    .venv\\Scripts\\python.exe qa\\control_math_qa.py

Checks
 1. The worked numbers the guide states (book example A, B, K; BK; A - BK; polynomial; eigenvalues;
    static cruise formulas and the worked-example values; open-loop eigenvalues +/-1).
 2. control/dist/control_math.js, run in Node, against NumPy eigenvalues, the analytic stability
    rule (k1 > 1 and k2 > 0) and its boundary cases, and SciPy solve_ivp responses (with and
    without the disturbance pulse) on a grid of gains and initial states.
 3. The static cruise formulas in JS against a direct linear solve.
Writes qa/results/control_math_qa.json. Exit code 1 if any check fails.
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(PROJECT, "control", "dist")
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    return ok


def run_js(cases):
    script = r"""
const CM = require(process.argv[1]);
let data = ""; process.stdin.on("data", d => data += d).on("end", () => {
  const cases = JSON.parse(data), out = [];
  for (const c of cases) {
    if (c.kind === "eig") out.push({ ev: CM.eigenvalues(c.k1, c.k2), cls: CM.classify(c.k1, c.k2) });
    else if (c.kind === "sim") {
      const s = CM.simulate(c.k1, c.k2, c.th0, c.w0, c.pulse, c.tMax, 0.005);
      const idx = c.times.map(t => Math.round(t / 0.005));
      out.push({ theta: idx.map(i => s.theta[i]), omega: idx.map(i => s.omega[i]), u: idx.map(i => s.u[i]), n: s.t.length });
    } else if (c.kind === "cruise") out.push(CM.cruise(c.a, c.am, c.K, c.r, c.d));
  }
  process.stdout.write(JSON.stringify(out));
});"""
    res = subprocess.run(["node", "-e", script, os.path.join(DIST, "control_math.js")], input=json.dumps(cases),
                         capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def main():
    # ---------------------------------------------------------------- 1. stated numbers
    A = np.array([[0.0, 1.0], [1.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    K = np.array([[4.0, 4.0]])
    check("open-loop eigenvalues of A are +1 and -1", np.allclose(sorted(np.linalg.eigvals(A).real), [-1, 1]))
    check("BK = [[0, 0], [4, 4]]", np.allclose(B @ K, [[0, 0], [4, 4]]))
    Acl = A - B @ K
    check("A - BK = [[0, 1], [-3, -4]]", np.allclose(Acl, [[0, 1], [-3, -4]]))
    check("char. polynomial of A - BK is l^2 + 4 l + 3", np.allclose(np.poly(Acl), [1, 4, 3]))
    check("closed-loop eigenvalues are -1 and -3", np.allclose(sorted(np.linalg.eigvals(Acl).real), [-3, -1]))
    check("lambda(lambda+4)+3 == (lambda+1)(lambda+3)", np.allclose(np.polymul([1, 1], [1, 3]), [1, 4, 3]))
    x0 = np.array([0.1, 0.0])
    ts = np.linspace(0, 5, 11)
    closed = [(expm(Acl * t) @ x0)[0] for t in ts]
    formula = [0.1 * (1.5 * np.exp(-t) - 0.5 * np.exp(-3 * t)) for t in ts]
    check("animation's closed-loop curve 0.1(1.5e^-t - 0.5e^-3t) matches expm", np.allclose(closed, formula, atol=1e-12))
    opened = [(expm(A * t) @ x0)[0] for t in ts]
    check("animation's open-loop curve 0.1 cosh t matches expm", np.allclose(opened, 0.1 * np.cosh(ts), atol=1e-12))
    K2 = np.array([[2.0, 2.0]])
    check("example K=[2 2]: A-BK = [[0,1],[-1,-2]], double eigenvalue -1",
          np.allclose(A - B @ K2, [[0, 1], [-1, -2]]) and np.allclose(np.poly(A - B @ K2), [1, 2, 1]))
    check("section-1 example: A [0.1, -0.2] = [-0.2, 0.1]", np.allclose(A @ [0.1, -0.2], [-0.2, 0.1]))
    # sizes example
    Aq, Bq, Cq = np.zeros((12, 12)), np.zeros((12, 4)), np.zeros((6, 12))
    check("quadrotor sizes: Ax, Bu are 12-vectors, Cx is a 6-vector",
          (Aq @ np.zeros(12)).shape == (12,) and (Bq @ np.zeros(4)).shape == (12,) and (Cq @ np.zeros(12)).shape == (6,))
    # scalar example: xdot = 2x + u, u = -kx
    check("scalar example: k = 5 gives eigenvalue -3; stable iff k > 2", 2 - 5 == -3 and all((2 - k < 0) == (k > 2) for k in [0, 1, 2, 2.1, 5]))

    # static cruise
    def cruise_solve(a, am, Kc, r, d):
        u_open = r / am
        y_open = a * u_open + d
        # y = a K (r - y) + d  ->  linear in y
        M = np.array([[1 + a * Kc]])
        y_closed = np.linalg.solve(M, [a * Kc * r + d])[0]
        return y_open, y_closed
    yo, yc = cruise_solve(0.5, 1.0, 50, 60, 0)
    check("cruise: open loop 30 mph, closed 57.69 mph (a=0.5, K=50, r=60, d=0)", abs(yo - 30) < 1e-12 and abs(yc - 1500 / 26) < 1e-12,
          f"{yo:.4f}, {yc:.4f}")
    _, yc2 = cruise_solve(0.5, 1.0, 50, 60, -10)
    check("cruise worked example: d=-10 gives 57.31", abs(yc2 - 57.3077) < 1e-3, f"{yc2:.4f}")
    _, yc3 = cruise_solve(0.5, 1.0, 5, 60, 0)
    _, yc4 = cruise_solve(0.5, 1.0, 5, 60, -10)
    check("cruise worked example: K=5 gives 42.86 and 40.00", abs(yc3 - 42.857) < 1e-3 and abs(yc4 - 40.0) < 1e-9,
          f"{yc3:.3f}, {yc4:.3f}")
    a, Kc, r, d = 0.5, 50, 60, 7.0
    _, ycd = cruise_solve(a, 1, Kc, r, d)
    check("cruise: error r - y = (r - d)/(1 + aK)", abs((r - ycd) - (r - d) / (1 + a * Kc)) < 1e-12)
    check("book p.328 case y = 2u with u = r: open-loop output 2r (100% error)", cruise_solve(2, 1, 0, 60, 0)[0] == 120)

    # ---------------------------------------------------------------- 2. control_math.js vs reference
    gains = [(k1, k2) for k1 in (0, 0.5, 1, 1.5, 2, 4, 10) for k2 in (-2, -0.5, 0, 0.5, 2, 4, 8)]
    eig_cases = [{"kind": "eig", "k1": k1, "k2": k2} for k1, k2 in gains]
    eig_cases.append({"kind": "eig", "k1": 1.0000000002, "k2": 0.0000000001})  # slider rounding
    js = run_js(eig_cases)
    bad_ev, bad_cls = [], []
    for (k1, k2), res in zip(gains, js):
        Acl = np.array([[0, 1], [1 - k1, -k2]])
        ref = np.linalg.eigvals(Acl)
        got = np.array([complex(e["re"], e["im"]) for e in res["ev"]])
        if not np.allclose(sorted(ref, key=lambda z: (z.real, z.imag)), sorted(got, key=lambda z: (z.real, z.imag)), atol=1e-6):
            bad_ev.append((k1, k2))
        kind = res["cls"]["kind"]
        if k1 > 1 and k2 > 0:
            want = "stable"
        elif k1 < 1 or k2 < 0:
            want = "unstable"
        elif k1 == 1 and k2 == 0:
            want = "drift"
        else:
            want = "marginal"
        if kind != want:
            bad_cls.append((k1, k2, kind, want))
    check("JS eigenvalues match NumPy on 49 gain pairs", not bad_ev, bad_ev[:5])
    check("JS classification matches the analytic rule (stable iff k1>1 and k2>0; boundaries)", not bad_cls, bad_cls[:5])
    check("near-boundary slider values snap to the Jordan case", js[-1]["cls"]["kind"] == "drift", js[-1]["cls"]["kind"])
    check("classification text distinguishes the Jordan drift case",
          "Jordan" in js[gains.index((1, 0))]["cls"]["detail"])
    check("classification text: k1 = 1, k2 > 0 settles to an offset",
          "offset" in js[gains.index((1, 2))]["cls"]["detail"])

    # simulations
    pulse = {"amplitude": 0.6, "start": 1.0, "duration": 0.2}
    times = [0.5, 1.0, 1.1, 1.2, 2.0, 3.0, 5.0, 8.0, 10.0]
    sim_specs = [(4, 4, 0.1, 0, None), (2, 2, 0.1, 0, None), (4, 0, 0.1, 0, None), (1, 0, 0.0, 0.1, None),
                 (1, 2, 0.1, 0.2, None), (0, 0, 0.05, 0, None), (4, 4, 0.0, 0.0, pulse), (1, 0, 0.0, 0.0, pulse),
                 (2.5, 0.7, -0.2, 0.3, pulse), (4, -0.5, 0.1, 0, None)]
    cases = [{"kind": "sim", "k1": k1, "k2": k2, "th0": t0, "w0": w0, "pulse": p, "tMax": 10, "times": times}
             for k1, k2, t0, w0, p in sim_specs]
    js = run_js(cases)
    worst = 0.0
    fails = []
    for (k1, k2, t0, w0, p), res in zip(sim_specs, js):
        def f(t, x, d):
            return [x[1], (1 - k1) * x[0] - k2 * x[1] + d]
        segs = [(0, 10, 0.0)] if p is None else [(0, p["start"], 0.0), (p["start"], p["start"] + p["duration"], p["amplitude"]),
                                                   (p["start"] + p["duration"], 10, 0.0)]
        x = [t0, w0]
        ref = {}
        for a0, a1, d in segs:
            tev = [t for t in times if a0 <= t <= a1]
            sol = solve_ivp(f, (a0, a1), x, args=(d,), t_eval=sorted(set(tev + [a1])), rtol=1e-11, atol=1e-13, method="DOP853")
            for t, th in zip(sol.t, sol.y[0]):
                ref.setdefault(round(t, 6), th)
            x = sol.y[:, -1]
        refv = np.array([ref[round(t, 6)] for t in times])
        got = np.array(res["theta"])
        scale = max(1.0, np.max(np.abs(refv)))
        err = np.max(np.abs(got - refv)) / scale
        worst = max(worst, err)
        if err > 1e-6:
            fails.append((k1, k2, t0, w0, bool(p), float(err)))
        # the reported feedback effort is u = -k1 theta - k2 thetadot
        if not np.allclose(res["u"], -k1 * np.array(res["theta"]) - k2 * np.array(res["omega"]), atol=1e-12):
            fails.append(("u", k1, k2))
    check("JS RK4 responses match SciPy DOP853 (10 cases, incl. pulse, boundaries, unstable)", not fails,
          f"worst relative error {worst:.2e}" + (f"; {fails[:3]}" if fails else ""))
    jd = js[3]["theta"]
    check("Jordan case k1=1, k2=0 with velocity drifts linearly: theta(10) = 0.1*10", abs(jd[-1] - 1.0) < 1e-9, jd[-1])
    off = js[4]["theta"][-1]
    check("k1=1, k2=2 settles to theta0 + omega0/k2 = 0.2", abs(off - 0.2) < 1e-6, off)

    cr_specs = [(0.5, 1, 50, 60, 0), (0.5, 1, 50, 60, -10), (2, 1, 0, 60, 5), (1.3, 0.7, 12, 60, 8)]
    js = run_js([{"kind": "cruise", "a": a, "am": am, "K": k, "r": r, "d": d} for a, am, k, r, d in cr_specs])
    ok = all(abs(res["open"] - cruise_solve(a, am, k, r, d)[0]) < 1e-12 and abs(res["closed"] - cruise_solve(a, am, k, r, d)[1]) < 1e-12
             and abs(res["attenuation"] - 1 / (1 + a * k)) < 1e-15 for (a, am, k, r, d), res in zip(cr_specs, js))
    check("JS static cruise formulas match a direct linear solve", ok)

    os.makedirs(os.path.join(PROJECT, "qa", "results"), exist_ok=True)
    with open(os.path.join(PROJECT, "qa", "results", "control_math_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(RESULTS, fh, indent=1)
    n_bad = sum(not r["ok"] for r in RESULTS)
    print(f"\n{len(RESULTS) - n_bad} passed, {n_bad} failed")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
