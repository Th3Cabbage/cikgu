"""Independent mathematics checks for the Linearizing Around a Fixed Point explorer.

Calls courses/controls/linearization/dist/study_math.js through Node and compares it with
NumPy/SciPy references written from the pendulum equations (book Eqs. 8.7-8.10, 8.23-8.25):
  theta' = omega,  omega' = -q sin(theta) - d omega + u   (d >= 0 is the companion extension)
References: central finite differences, numpy eigvals, solve_ivp (DOP853) in ABSOLUTE angle
coordinates, expm of the augmented matrix [[A, B], [0, 0]] for constant input, and closed-form
damped-oscillator formulas.

Run from the repository root:  .\\.venv\\Scripts\\python.exe qa\\linearization_math_qa.py
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
MATH_JS = ROOT / "courses" / "controls" / "linearization" / "dist" / "study_math.js"

RUNNER = r"""
const SM = require(process.argv[1]);
let buf = "";
process.stdin.on("data", d => buf += d);
process.stdin.on("end", () => {
  const out = JSON.parse(buf).map(([fn, args]) => {
    try {
      if (fn === "__get") return { ok: JSON.parse(JSON.stringify(SM[args[0]])) };
      if (fn === "__frozen") {
        const tr = SM.nonlinearTrajectory(...args), lt = SM.linearTrajectory(...args);
        return { ok: [Object.isFrozen(tr), Object.isFrozen(tr[0]), Object.isFrozen(lt), Object.isFrozen(SM.PRESETS),
                      Object.isFrozen(SM.PRESETS[0]), Object.isFrozen(SM.PARAMS.q), Object.isFrozen(SM)] };
      }
      return { ok: SM[fn](...args) };
    } catch (e) { return { err: e.name + ": " + e.message }; }
  });
  process.stdout.write(JSON.stringify(out));
});
"""

FAILS: list[str] = []
COUNT = 0


def js(calls):
    proc = subprocess.run(["node", "-e", RUNNER, str(MATH_JS)], input=json.dumps(calls),
                          capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def check(cond, msg):
    global COUNT
    COUNT += 1
    if not cond:
        FAILS.append(msg)


# ---- independent reference model
def f_ref(x, u, q, d=0.0):
    return np.array([x[1], -q * math.sin(x[0]) - d * x[1] + u])


def fd_jac(x, u, q, d, h=1e-6):
    fx = np.zeros((2, 2))
    for j in range(2):
        e = np.zeros(2); e[j] = h
        fx[:, j] = (f_ref(x + e, u, q, d) - f_ref(x - e, u, q, d)) / (2 * h)
    fu = (f_ref(x, u + h, q, d) - f_ref(x, u - h, q, d)) / (2 * h)
    return fx, fu


THETA_BAR = {"down": 0.0, "up": math.pi}


def nl_ref(p, ts):
    tb = THETA_BAR[p["eq"]]
    sol = solve_ivp(lambda t, x: f_ref(x, p.get("du", 0.0), p["q"], p.get("d", 0.0)), (0, ts[-1]),
                    [tb + p["eta0"], p["nu0"]], method="DOP853", t_eval=ts, rtol=1e-12, atol=1e-13)
    assert sol.success
    return sol.y  # absolute theta, omega


def A_ref(eq, q, d=0.0):
    # Evaluate the Jacobian at the fixed point by finite differences of the original f.
    return fd_jac(np.array([THETA_BAR[eq], 0.0]), 0.0, q, d)


def A_exact(eq, q, d=0.0):
    # Hand derivative of f_ref: d(-q sin theta)/dtheta = -q cos theta, d/domega = -d, d/du = 1.
    return np.array([[0.0, 1.0], [-q * math.cos(THETA_BAR[eq]), -d]]), np.array([0.0, 1.0])


def lin_ref(p, t):
    A, B = A_exact(p["eq"], p["q"], p.get("d", 0.0))
    M = np.zeros((3, 3)); M[:2, :2] = A; M[:2, 2] = B
    z = expm(M * t) @ np.array([p["eta0"], p["nu0"], p.get("du", 0.0)])
    return z[:2]


def main():
    rng = np.random.default_rng(20261020)

    # 1. Vector field and Jacobians against central finite differences at random states
    pts = [(rng.uniform(-7, 7), rng.uniform(-3, 3), rng.uniform(-0.5, 0.5), rng.uniform(0.25, 4), d)
           for d in (0.0, 0.7) for _ in range(12)]
    res = js([["f", [[th, om], u, q, d]] for th, om, u, q, d in pts] +
             [["jacobianAt", [th, q, d]] for th, om, u, q, d in pts])
    n = len(pts)
    for i, (th, om, u, q, d) in enumerate(pts):
        x = np.array([th, om])
        check(np.allclose(res[i]["ok"], f_ref(x, u, q, d), rtol=0, atol=1e-13), f"f mismatch at {pts[i]}")
        fx, fu = fd_jac(x, u, q, d)
        J = res[n + i]["ok"]
        check(np.allclose(J["A"], fx, atol=1e-8), f"f_x vs finite differences at {pts[i]}")
        check(np.allclose(np.ravel(J["B"]), fu, atol=1e-8), f"f_u vs finite differences at {pts[i]}")

    # 2. Equilibrium residuals and A, B, C, D at both fixed points
    qs = [0.25, 1.0, 2.5, 4.0]
    calls = []
    for eq in ("down", "up"):
        for q in qs:
            for d in (0.0, 1.3):
                calls.append(["linearization", [eq, q, d]])
                calls.append(["f", [[THETA_BAR[eq], 0], 0, q, d]])
    res = js(calls)
    k = 0
    for eq in ("down", "up"):
        for q in qs:
            for d in (0.0, 1.3):
                L, fr = res[k]["ok"], res[k + 1]["ok"]; k += 2
                check(np.max(np.abs(f_ref(np.array([THETA_BAR[eq], 0.0]), 0.0, q, d))) < 1e-14 and
                      max(abs(v) for v in fr) < 1e-14, f"equilibrium residual {eq} q={q}")
                fx, fu = A_ref(eq, q, d)
                check(np.allclose(L["A"], fx, atol=1e-8), f"A at {eq} q={q} d={d}")
                expected = [[0, 1], [-q if eq == "down" else q, -d]]
                check(np.allclose(L["A"], expected, atol=0), f"A closed form at {eq} q={q} d={d}")
                check(np.allclose(np.ravel(L["B"]), [0, 1]) and np.allclose(np.ravel(L["B"]), fu, atol=1e-8), f"B at {eq}")
                check(L["C"] == [[1, 0]] and L["D"] == [[0]], "C = [1 0], D = 0 for angle output")
                check(abs(L["thetaBar"] - THETA_BAR[eq]) == 0, f"thetaBar {eq}")

    # 3. Eigenvalues and classification
    cases = [(eq, q, d) for eq in ("down", "up") for q in (0.25, 1, 2.25, 4) for d in (0, 0.5, 2 * math.sqrt(q), 3.9)]
    res = js([["eigen2", [[[0, 1], [-(q if eq == "down" else -q), -d]]]] for eq, q, d in cases] +
             [["classify", [eq, q, d]] for eq, q, d in cases])
    for i, (eq, q, d) in enumerate(cases):
        ev = sorted((complex(v["re"], v["im"]) for v in res[i]["ok"]), key=lambda z: (z.real, z.imag))
        ref = sorted(np.linalg.eigvals(A_exact(eq, q, d)[0]), key=lambda z: (z.real, z.imag))
        check(np.allclose(ev, ref, atol=1e-7), f"eigenvalues {eq} q={q} d={d}: {ev} vs {ref}")
        c = res[len(cases) + i]["ok"]
        if eq == "up":
            check(c["linear"] == "saddle" and c["nonlinear"] == "unstable" and c["byLinearization"],
                  f"up must be a saddle, unstable by linearization (q={q}, d={d})")
            check(min(e.real for e in ref) < 0 < max(e.real for e in ref), "up eigenvalues have opposite signs")
        elif d == 0:
            check(c["linear"] == "center" and c["nonlinear"] == "lyapunov" and not c["byLinearization"],
                  f"undamped down must be a linear center, inconclusive by Jacobian alone (q={q})")
            check(all(abs(e.real) < 1e-12 for e in ref), "undamped down eigenvalues purely imaginary")
        else:
            want = "critical" if abs(d * d - 4 * q) < 1e-9 else ("focus" if d * d < 4 * q else "node")
            check(c["linear"] == want and c["nonlinear"] == "asymptotic" and c["byLinearization"],
                  f"damped down q={q} d={d}: got {c['linear']} want {want}")

    # 4. Nonlinear trajectories vs solve_ivp (absolute angle, never reduced mod 2 pi)
    T, N = 12.0, 60
    ts = np.linspace(0, T, N + 1)
    nl_cases = []
    for eq in ("down", "up"):
        for _ in range(10):
            nl_cases.append(dict(eq=eq, eta0=float(rng.uniform(-1.5, 1.5)), nu0=float(rng.uniform(-1.5, 1.5)),
                                 q=float(rng.uniform(0.25, 4)), du=float(rng.choice([0, rng.uniform(-0.5, 0.5)])),
                                 d=float(rng.choice([0, rng.uniform(0, 4)]))))
    nl_cases.append(dict(eq="up", eta0=0.1, nu0=1.5, q=0.25, du=0, d=0))      # goes over the top repeatedly
    res = js([["nonlinearTrajectory", [p, T, N]] for p in nl_cases])
    worst = 0.0
    for p, r in zip(nl_cases, res):
        tr = r["ok"]
        th = np.array([s["theta"] for s in tr]); om = np.array([s["omega"] for s in tr])
        eta = np.array([s["eta"] for s in tr])
        ref = nl_ref(p, ts)
        err = max(np.max(np.abs(th - ref[0])), np.max(np.abs(om - ref[1])))
        worst = max(worst, err)
        check(err < 1e-6, f"nonlinear vs solve_ivp err={err:.2e} for {p}")
        check(np.allclose(th, THETA_BAR[p["eq"]] + eta, atol=1e-15), "theta = theta_bar + eta")
        check(np.allclose([s["t"] for s in tr], ts, atol=1e-12), "trajectory time grid")
    over = res[-1]["ok"][-1]["theta"]
    check(over > 2 * math.pi, f"whirling pendulum angle must not be wrapped (theta(12) = {over:.3f})")
    print(f"nonlinear vs solve_ivp: {len(nl_cases)} cases, max abs error {worst:.2e}")

    # 5. Linear closed form vs augmented-matrix expm reference (constant input, damping, both points)
    lin_cases = [dict(p, t=float(t)) for p in nl_cases for t in (0.0, 0.37, 3.0, 7.5, 12.0)]
    q = 2.25
    lin_cases += [dict(eq="down", eta0=0.8, nu0=-0.4, q=q, du=0.3, d=2 * math.sqrt(q), t=t) for t in (1e-7, 0.01, 2.0, 12.0)]
    res = js([["linearState", [p, p["t"]]] for p in lin_cases])
    worst = 0.0
    for p, r in zip(lin_cases, res):
        s = r["ok"]; ref = lin_ref(p, p["t"])
        scale = max(1.0, float(np.max(np.abs(ref))))
        err = max(abs(s["eta"] - ref[0]), abs(s["nu"] - ref[1])) / scale
        worst = max(worst, err)
        check(err < 1e-10, f"linear vs expm rel err={err:.2e} for {p}")
        check(abs(s["theta"] - (THETA_BAR[p["eq"]] + s["eta"])) < 1e-15, "linear theta = theta_bar + eta")
    print(f"linear vs augmented expm: {len(lin_cases)} cases, max scaled error {worst:.2e}")

    # 6. Damping companion: independent closed forms (critical and underdamped), nu0 = 0, du = 0
    q, e0 = 1.0, 0.3
    dd = [("critical", 2.0, lambda t: e0 * (1 + t) * math.exp(-t)),
          ("underdamped", 0.6, lambda t: e0 * math.exp(-0.3 * t) * (math.cos(math.sqrt(0.91) * t) + 0.3 / math.sqrt(0.91) * math.sin(math.sqrt(0.91) * t))),
          ("overdamped", 2.5, lambda t: e0 * (2 * math.exp(-0.5 * t) - 0.5 * math.exp(-2 * t)) / 1.5)]
    for name, d, fn in dd:
        p = dict(eq="down", eta0=e0, nu0=0, q=q, du=0, d=d)
        res = js([["linearState", [p, t]] for t in (0.5, 2, 6)])
        for t, r in zip((0.5, 2, 6), res):
            check(abs(r["ok"]["eta"] - fn(t)) < 1e-12, f"{name} damping closed form at t={t}")

    # 7. t = 0 and exact equilibrium
    calls = []
    for eq in ("down", "up"):
        calls += [["compare", [dict(eq=eq, eta0=0.7, nu0=-0.3, q=2, du=0.4, d=0.5), 0]],
                  ["nonlinearTrajectory", [dict(eq=eq, eta0=0, nu0=0, q=4, du=0, d=0), 12, 24]],
                  ["linearTrajectory", [dict(eq=eq, eta0=0, nu0=0, q=4, du=0, d=0), 12, 24]]]
    res = js(calls)
    for i, eq in enumerate(("down", "up")):
        c, nt, lt = (res[3 * i + j]["ok"] for j in range(3))
        check(c["nonlinear"]["eta"] == 0.7 and c["linear"]["eta"] == 0.7 and c["nonlinear"]["nu"] == -0.3
              and c["linear"]["nu"] == -0.3 and c["angleError"] == 0, f"t = 0 initial state {eq}")
        check(all(s["eta"] == 0 and s["nu"] == 0 and s["theta"] == THETA_BAR[eq] for s in nt + lt),
              f"exact equilibrium stays exactly at rest ({eq})")

    # 8. Small offsets: error -> 0 faster than the offset (cubic nonlinearity); large offset: clear mismatch
    for eq, T in (("down", 8.0), ("up", 3.0)):
        scales = [0.16, 0.08, 0.04, 0.02]
        res = js([["compare", [dict(eq=eq, eta0=s, nu0=0, q=1, du=0, d=0), t]] for s in scales for t in np.linspace(0, T, 41).tolist()])
        errs = [max(abs(res[41 * i + j]["ok"]["angleError"]) for j in range(41)) for i in range(len(scales))]
        rel = [e / s for e, s in zip(errs, scales)]
        orders = [math.log2(errs[i] / errs[i + 1]) for i in range(len(errs) - 1)]
        check(all(rel[i + 1] < rel[i] for i in range(len(rel) - 1)) and rel[-1] < rel[0] / 40,
              f"{eq}: relative error must shrink with offset: {rel}")
        check(all(2.8 < o < 3.2 for o in orders), f"{eq}: angle error should scale like offset^3, orders {orders}")
        print(f"{eq} small-offset max |angle error| {['%.1e' % e for e in errs]}, orders {['%.2f' % o for o in orders]}")
    res = js([["compare", [dict(eq="down", eta0=1.4, nu0=0, q=1, du=0, d=0), float(t)]] for t in np.linspace(0, 12, 121)])
    big = max(abs(r["ok"]["angleError"]) for r in res)
    check(big > 0.5, f"large-offset down must visibly mismatch (max error {big:.3f})")
    res = js([["compare", [dict(eq="up", eta0=0.05, nu0=0, q=1, du=0, d=0), float(t)]] for t in (1.0, 6.0, 12.0)])
    e1, e6, e12 = (abs(r["ok"]["angleError"]) for r in res)
    check(e1 < 1e-4 and e6 > 1.0 and e12 > 1e3, f"small-up local validity lost after growth: {e1:.1e}, {e6:.2f}, {e12:.1e}")
    print(f"large-down max angle error {big:.3f} rad; small-up error at t=1,6,12: {e1:.1e}, {e6:.2f}, {e12:.1e}")

    # 9. Perturbation at pi: eta measured from pi, initial accelerations point away from upright
    res = js([["f", [[math.pi + 0.1, 0], 0, 2, 0]], ["linearState", [dict(eq="up", eta0=0.1, nu0=0, q=2, du=0, d=0), 0.5]],
              ["nonlinearState", [dict(eq="up", eta0=0.1, nu0=0, q=2, du=0, d=0), 0.5]]])
    acc = res[0]["ok"][1]
    check(abs(acc - 2 * math.sin(0.1)) < 1e-14 and acc > 0, "omega' = +q sin(eta) > 0 near upright")
    a = math.sqrt(2)
    check(abs(res[1]["ok"]["eta"] - 0.1 * math.cosh(a * 0.5)) < 1e-13, "linear up: eta = eta0 cosh(sqrt(q) t)")
    check(res[1]["ok"]["theta"] > math.pi and abs(res[2]["ok"]["theta"] - nl_ref(dict(eq="up", eta0=0.1, nu0=0, q=2), [0, 0.5])[0][-1]) < 1e-9,
          "absolute theta near pi = pi + eta, not eta")

    # 10. Energy conservation (d = 0, du = 0) for the original model
    p = dict(eq="down", eta0=1.5, nu0=1.2, q=3, du=0, d=0)
    res = js([["nonlinearTrajectory", [p, 12, 48]]])
    E = [0.5 * s["omega"] ** 2 + 3 * (1 - math.cos(s["theta"])) for s in res[0]["ok"]]
    check(max(E) - min(E) < 1e-9, f"energy drift {max(E) - min(E):.2e}")

    # 11. Input validation and immutability
    good = dict(eq="down", eta0=0.1, nu0=0, q=1, du=0, d=0)
    bad = [dict(good, q=0), dict(good, q=-1), dict(good, eta0=None), dict(good, eq="side"), dict(good, d=-0.1),
           dict(good, nu0="1"), {k: v for k, v in good.items() if k != "eta0"}]
    res = js([["nonlinearState", [b, 1]] for b in bad] + [["linearState", [b, 1]] for b in bad] +
             [["nonlinearState", [good, -1]], ["linearState", [good, -1]], ["nonlinearTrajectory", [good, 5, 0]],
              ["f", [[0, 0], 0, 0, 0]], ["linearization", ["up", -2, 0]], ["classify", ["down", 1, -1]], ["params", [None]]])
    for i, r in enumerate(res):
        check("err" in r and r["err"].startswith("RangeError"), f"invalid input #{i} must raise RangeError, got {r}")
    # NaN / Infinity cannot pass through JSON; check them inside Node
    proc = subprocess.run(["node", "-e", "const S=require(process.argv[1]);let n=0;for(const v of [NaN,Infinity,-Infinity])"
                           "for(const k of ['eta0','nu0','q','du','d']){try{S.params({eq:'up',eta0:0,nu0:0,q:1,du:0,d:0,[k]:v})}catch(e){if(e instanceof RangeError)n++}}"
                           "try{S.linearState({eq:'up',eta0:0,nu0:0,q:1},NaN)}catch(e){n++}console.log(n)", str(MATH_JS)],
                          capture_output=True, text=True, check=True)
    check(proc.stdout.strip() == "16", f"non-finite inputs rejected: {proc.stdout.strip()}/16")
    fr = js([["__frozen", [good, 2, 4]]])[0]["ok"]
    check(all(fr), f"frozen outputs/constants: {fr}")

    # 12. Presets: within slider ranges, on the slider grid, and meaning what their labels say
    P, R = js([["__get", ["PRESETS"]], ["__get", ["PARAMS"]]])
    P, R = P["ok"], R["ok"]
    for pr in P:
        for key in ("eta0", "nu0", "q", "du", "d"):
            c = R[key]; v = pr[key]
            on_grid = abs((v - c["min"]) / c["step"] - round((v - c["min"]) / c["step"])) < 1e-9
            check(c["min"] <= v <= c["max"] and on_grid, f"preset {pr['id']} {key}={v} outside slider grid")
        check(pr["du"] == 0, f"preset {pr['id']} must be an unforced (lecture) case")
    ids = {pr["id"]: pr for pr in P}
    check(ids["exact-up"]["eta0"] == 0 and ids["exact-up"]["nu0"] == 0 and ids["exact-up"]["du"] == 0, "exact preset at rest")
    check(R["d"]["default"] == 0.1 and R["q"]["default"] == 1 and R["du"]["default"] == 0 and R["q"]["min"] > 0,
          "defaults reproduce the lecture (q = 1, d = 0.1, no input); q range positive")
    # The lecture's MATLAB output (frame 30:00): eig(Ad) = -0.05 +- 0.9987i, eig(Au) = -1.0512, 0.9512
    res = js([["classify", [ids[k]["eq"], ids[k]["q"], ids[k]["d"]]] for k in ("lecture-down", "lecture-up", "undamped-down", "overdamped-down")])
    ev = [sorted((complex(v["re"], v["im"]) for v in r["ok"]["eig"]), key=lambda z: (z.real, z.imag)) for r in res]
    check(np.allclose(ev[0], [-0.05 - 0.9987492178j, -0.05 + 0.9987492178j], atol=1e-9) and res[0]["ok"]["linear"] == "focus",
          f"lecture-down eigenvalues {ev[0]}")
    check(np.allclose(ev[1], [-1.0512492197, 0.9512492197], atol=1e-9) and res[1]["ok"]["linear"] == "saddle", f"lecture-up eigenvalues {ev[1]}")
    check(np.allclose(ev[2], [-1j, 1j], atol=1e-12) and res[2]["ok"]["linear"] == "center", "undamped-down center")
    check(res[3]["ok"]["linear"] == "node" and all(z.imag == 0 and z.real < 0 for z in ev[3]), "overdamped-down node")
    check(np.allclose(ev[0], np.linalg.eigvals(np.array([[0, 1], [-1, -0.1]]))[np.argsort(np.linalg.eigvals(np.array([[0, 1], [-1, -0.1]])).imag)]),
          "lecture-down matches numpy eig of the board matrix")

    print(f"{COUNT - len(FAILS)}/{COUNT} checks passed")
    for m in FAILS[:30]:
        print("FAIL:", m)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
