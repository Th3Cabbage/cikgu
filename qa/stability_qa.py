"""Non-browser checks for the Stability and Eigenvalues study companion.

    .venv\\Scripts\\python.exe qa\\stability_qa.py

1. math: dist/study_math.js (run in node) against independent references: scipy.linalg.expm,
   scipy.integrate.solve_ivp, numpy eigenvalues/ranks, numpy matrix powers of expm(A dt), and long-horizon
   700-digit mpmath solutions at t = 1500 for the stability verdicts, including real, complex, repeated,
   zero/imaginary-axis, unit-circle and defective (Jordan) boundary cases.
2. animations: specs <-> manifest agreement, every clip decodes with the recorded frame count,
   contiguous master boundaries, stills present, formulas typeset in KaTeX (node).
3. course.json: sections cover the 19:30 lecture, timestamps inside sections, book pages, quiz, explorer.
4. server: trusted tutor context, missing-key tutor state, health identity, /book byte ranges.
5. launcher and isolation: the launcher targets this package; dist holds no source media.
Writes qa/results/stability_qa.json. Exit code 1 if any check fails.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import mpmath
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "courses/controls/stability-eigenvalues")
DIST = os.path.join(PKG, "dist")
ANIM = os.path.join(DIST, "animations")
PY = sys.executable
NODE = shutil.which("node") or os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "nodejs", "node.exe")
sys.path.insert(0, os.path.join(PKG, "animation"))
sys.path.insert(0, PKG)
SM = "./courses/controls/stability-eigenvalues/dist/study_math.js"

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""), flush=True)
    return ok


def node(script):
    res = subprocess.run([NODE, "-e", script], capture_output=True, text=True, cwd=ROOT)
    if res.returncode:
        raise RuntimeError(res.stderr)
    return json.loads(res.stdout)


# ---------------------------------------------------------------------------- 1. math

def build_A(p):
    """The explorer family, written independently: A = T J T^-1 with T = [[1, s], [0, 1]]."""
    T = np.array([[1.0, p["s"]], [0.0, 1.0]])
    if p["kind"] == "complex":
        J = np.array([[p["a"], -p["b"]], [p["b"], p["a"]]])
    elif p["kind"] == "jordan":
        J = np.array([[p["lj"], 1.0], [0.0, p["lj"]]])
    else:
        J = np.diag([p["l1"], p["l2"]])
    return T @ J @ np.linalg.inv(T)


def ref_verdict(M, margin):
    """Independent stability verdict from numerical eigenvalues and the rank test for a defective
    repeated eigenvalue. margin(lam) is Re(lam) (continuous) or |lam| - 1 (discrete)."""
    ev = np.linalg.eigvals(M)
    worst = max(margin(v) for v in ev)
    if worst < -1e-7:
        return "asymptotic"
    if worst > 1e-7:
        return "unstable"
    on = [v for v in ev if abs(margin(v)) <= 1e-7]
    if len(on) == 2 and abs(on[0] - on[1]) < 1e-6:            # repeated boundary eigenvalue
        lam = (on[0] + on[1]) / 2
        if np.linalg.matrix_rank(M - lam * np.eye(2), tol=1e-7) == 1:
            return "unstable"                                      # one eigenvector only: Jordan block
    return "lyapunov"


def mp_A(p):
    """build_A in 700-digit arithmetic from the decimal slider values. A float-built A would put a
    start like (1, 1) one rounding error off the stable eigenvector of a saddle, and e^{0.4 * 1500}
    would amplify that error: the true solution decays, a double-precision simulation does not."""
    f = lambda k: mpmath.mpf(str(p[k]))  # noqa: E731
    s = f("s")
    if p["kind"] == "complex":
        J = mpmath.matrix([[f("a"), -f("b")], [f("b"), f("a")]])
    elif p["kind"] == "jordan":
        J = mpmath.matrix([[f("lj"), 1], [0, f("lj")]])
    else:
        J = mpmath.matrix([[f("l1"), 0], [0, f("l2")]])
    return mpmath.matrix([[1, s], [0, 1]]) * J * mpmath.matrix([[1, -s], [0, 1]])


def mp_behaviour(p, t_end=1500):
    """Behaviour at t = 1500 of ||e^{At}|| (the worst case over ALL initial states) and of the one
    solution from x0, using 700-digit mpmath expm so exact cancellations (a start on the stable
    eigenvector of a saddle) survive rounding. Slider steps keep every case far from the thresholds:
    slowest rate 0.05 gives e^{+-75}; a defective zero eigenvalue grows like t = 1500; bounded cases
    stay below cond(T) ~ 11."""
    mpmath.mp.dps = 700
    E = mpmath.expm(mp_A(p) * t_end)
    norm = mpmath.mnorm(E, 1)
    start = math.hypot(p["x1"], p["x2"])
    xn = mpmath.norm(E * mpmath.matrix([mpmath.mpf(str(p["x1"])), mpmath.mpf(str(p["x2"]))]))

    def kind(n, ref):
        if ref == 0:
            return "rest"
        if n < 1e-6 * ref:
            return "decays"
        return "grows" if n > 1e3 * ref else "bounded"
    return {"decays": "asymptotic", "bounded": "lyapunov", "grows": "unstable"}[kind(norm, 1.0)], kind(xn, start)


def math_cases():
    cases = [
        # real, distinct / repeated (diagonalizable), zero boundary
        {"kind": "real", "l1": -1, "l2": -2, "s": 1, "x1": 1, "x2": 0.5},
        {"kind": "real", "l1": 0.4, "l2": -1, "s": 1, "x1": 1, "x2": 0.5},      # saddle, generic start
        {"kind": "real", "l1": 0.4, "l2": -1, "s": 1, "x1": 1, "x2": 1},        # saddle, start on stable eigenvector
        {"kind": "real", "l1": 0, "l2": -1, "s": 0.5, "x1": 1, "x2": 1},        # zero eigenvalue, semisimple
        {"kind": "real", "l1": 0, "l2": 0, "s": 2, "x1": -1, "x2": 1},          # A = 0
        {"kind": "real", "l1": 0, "l2": 0.5, "s": -1, "x1": 1, "x2": 0},        # zero and positive; start on the zero mode
        {"kind": "real", "l1": -1, "l2": -1, "s": 3, "x1": 1, "x2": -2},        # repeated, A = -I
        {"kind": "real", "l1": 0.3, "l2": 0.3, "s": 0, "x1": 1, "x2": 1},
        {"kind": "real", "l1": -0.2, "l2": -2, "s": 3, "x1": 0, "x2": 1},       # stable with transient growth
        # complex pairs, including the imaginary axis
        {"kind": "complex", "a": -0.3, "b": 2, "s": 0, "x1": 1.5, "x2": 0},
        {"kind": "complex", "a": 0.15, "b": 2, "s": 0.5, "x1": 1, "x2": 0},
        {"kind": "complex", "a": 0, "b": 1.5, "s": 1, "x1": 1, "x2": 0.5},       # center
        {"kind": "complex", "a": -0.05, "b": 4, "s": -3, "x1": -2, "x2": 2},
        # defective (Jordan), including the zero boundary
        {"kind": "jordan", "lj": 0, "s": 0, "x1": 0, "x2": 1},                  # linear growth
        {"kind": "jordan", "lj": 0, "s": 1.5, "x1": 1, "x2": 0},                 # start on the eigenvector: constant
        {"kind": "jordan", "lj": -0.05, "s": 0, "x1": 0, "x2": 1},
        {"kind": "jordan", "lj": 0.05, "s": -1, "x1": 1, "x2": 1},
        {"kind": "real", "l1": 0, "l2": 0, "s": 0, "x1": 0, "x2": 0},           # rest
    ]
    rng = np.random.default_rng(11)
    grid = lambda lo, hi, st: float(np.round(rng.uniform(lo, hi) / st) * st)  # noqa: E731
    for i in range(150):
        kind = ("real", "complex", "jordan")[i % 3]
        p = {"kind": kind, "s": round(grid(-3, 3, 0.1), 6), "x1": round(grid(-2, 2, 0.1), 6), "x2": round(grid(-2, 2, 0.1), 6)}
        if kind == "real":
            p.update(l1=round(grid(-2, 1, 0.05), 6), l2=round(grid(-2, 1, 0.05), 6))
        elif kind == "complex":
            p.update(a=round(grid(-2, 1, 0.05), 6), b=round(max(0.2, grid(0.2, 4, 0.05)), 6))
        else:
            p.update(lj=round(grid(-2, 1, 0.05), 6))
        cases.append(p)
    for c in cases:
        c["dt"] = 0.25
    for c, dt in zip(cases[18:], np.round(rng.uniform(0.05, 1.5, len(cases) - 18) / 0.05) * 0.05):
        c["dt"] = round(float(max(0.05, dt)), 6)
    return cases


def math_checks():
    cases = math_cases()
    ts = [0, 0.37, 1.0, 2.5, 6.0]
    js = ("const M=require('" + SM + "');const C=" + json.dumps(cases) + ";const TS=" + json.dumps(ts) + ";"
          "console.log(JSON.stringify(C.map(p=>({sys:M.system(p),E:TS.map(t=>M.expA(p,t)),X:TS.map(t=>M.state(p,t)),"
          "ev:M.eigen(p),evd:M.eigenDiscrete(p,p.dt),cc:M.classifyContinuous(p),cd:M.classifyDiscrete(p,p.dt),"
          "sb:M.startBehaviour(p),S:M.samples(p,p.dt,10),P:M.powers(M.eigenDiscrete(p,p.dt).values[0],12)}))))")
    out = node(js)
    worst = {"A": 0, "expm": 0, "x": 0, "ivp": 0, "eig": 0, "eigd": 0, "samp": 0, "pow": 0}
    bad_c, bad_d, bad_long, bad_start, n_ivp = [], [], [], [], 0
    counts = {}
    for i, (p, o) in enumerate(zip(cases, out)):
        A = build_A(p)
        x0 = np.array([p["x1"], p["x2"]], dtype=float)
        worst["A"] = max(worst["A"], np.abs(np.array(o["sys"]["A"]) - A).max())
        for t, E, X in zip(ts, o["E"], o["X"]):
            R = expm(A * t)
            worst["expm"] = max(worst["expm"], np.abs(np.array(E) - R).max() / max(1, np.abs(R).max()))
            xr = R @ x0
            worst["x"] = max(worst["x"], np.abs(np.array(X) - xr).max() / max(1, np.abs(xr).max()))
        if i % 4 == 0:   # an ODE integrator as a second, method-independent reference
            sol = solve_ivp(lambda t, x: A @ x, (0, 6.0), x0, t_eval=ts, rtol=1e-11, atol=1e-12, method="DOP853")
            for X, xr in zip(o["X"], sol.y.T):
                worst["ivp"] = max(worst["ivp"], np.abs(np.array(X) - xr).max() / max(1, np.abs(xr).max()))
            n_ivp += 1
        # eigenvalues: continuous and discrete (eigenvalues of expm(A dt) computed numerically)
        ev = np.sort_complex(np.array([v["re"] + 1j * v["im"] for v in o["ev"]["values"]]))
        worst["eig"] = max(worst["eig"], np.abs(ev - np.sort_complex(np.linalg.eigvals(A))).max())
        Ad = expm(A * p["dt"])
        evd = np.sort_complex(np.array([v["re"] + 1j * v["im"] for v in o["evd"]["values"]]))
        ref = np.sort_complex(np.linalg.eigvals(Ad))
        # repeated (defective) eigenvalues are ill-conditioned for numerical eigensolvers: compare loosely there
        worst["eigd"] = max(worst["eigd"], np.abs(evd - ref).max() / max(1, np.abs(ref).max()) * (1e-4 if p["kind"] == "jordan" else 1))
        # discrete samples: iterated A_d against numpy powers of scipy expm(A dt)
        for smp in o["S"][:: max(1, len(o["S"]) // 10)]:
            xr = np.linalg.matrix_power(Ad, smp["k"]) @ x0
            worst["samp"] = max(worst["samp"], np.abs(np.array(smp["x"]) - xr).max() / max(1, np.abs(xr).max()))
        mu = complex(o["evd"]["values"][0]["re"], o["evd"]["values"][0]["im"])
        worst["pow"] = max(worst["pow"], max(abs(complex(*pk) - mu ** k) / max(1, abs(mu) ** k) for k, pk in enumerate(o["P"])))
        # verdicts: independent eigenvalue/rank reference, continuous and discrete
        rc = ref_verdict(A, lambda v: v.real)
        rd = ref_verdict(Ad, lambda v: abs(v) - 1)
        if o["cc"] != rc:
            bad_c.append((p, o["cc"], rc))
        if o["cd"] != rd or o["cd"] != o["cc"]:
            bad_d.append((p, o["cd"], rd))
        counts[o["cc"]] = counts.get(o["cc"], 0) + 1
        # and against the long-horizon behaviour itself (all initial states via the matrix norm; the start)
        if i < 18 or i % 5 == 0:
            sys_kind, start_kind = mp_behaviour(p)
            if sys_kind != o["cc"]:
                bad_long.append((p, o["cc"], sys_kind))
            if start_kind != o["sb"]:
                bad_start.append((p, o["sb"], start_kind))
    n = len(cases)
    check("math: A = T J T^-1 matches an independent construction", worst["A"] < 1e-12, f"{n} systems, max err {worst['A']:.1e}")
    check("math: e^{At} = T e^{Jt} T^-1 equals scipy expm(At) (real, complex, Jordan)", worst["expm"] < 1e-11,
          f"{n * len(ts)} samples, max rel err {worst['expm']:.1e}")
    check("math: x(t) equals expm(At) x0", worst["x"] < 1e-11, f"max rel err {worst['x']:.1e}")
    check("math: x(t) agrees with solve_ivp (DOP853)", worst["ivp"] < 1e-8, f"{n_ivp} systems, max rel err {worst['ivp']:.1e}")
    check("math: eigenvalues match numpy eigvals(A)", worst["eig"] < 1e-6, f"max err {worst['eig']:.1e}")
    check("math: discrete eigenvalues e^{lambda dt} match eigvals(expm(A dt))", worst["eigd"] < 1e-7, f"max err {worst['eigd']:.1e}")
    check("math: iterated x_{k+1} = A_d x_k equals matrix_power(expm(A dt), k) x0", worst["samp"] < 1e-9, f"max rel err {worst['samp']:.1e}")
    check("math: powers r^k e^{ik theta} equal complex powers", worst["pow"] < 1e-12, f"max err {worst['pow']:.1e}")
    check("verdict: continuous classification matches eigenvalue + rank reference", not bad_c, f"{counts}" if not bad_c else bad_c[:2])
    check("verdict: discrete classification matches reference and the continuous verdict", not bad_d, "" if not bad_d else bad_d[:2])
    check("verdict: long-horizon 700-digit solutions confirm every system verdict", not bad_long, "" if not bad_long else bad_long[:2])
    check("verdict: per-start behaviour (decays/bounded/grows/rest) confirmed at t = 1500", not bad_start, "" if not bad_start else bad_start[:2])
    need = {"asymptotic", "lyapunov", "unstable"}
    check("verdict: cases cover asymptotic, Lyapunov-only and unstable", need <= set(counts), counts)

    # worked examples (authored for the guide)
    close = lambda a, b, tol=1e-12: np.allclose(a, b, atol=tol)  # noqa: E731
    A1 = np.array([[1.0, 2], [2, 1]])
    t = 0.8
    x_gen = 0.5 * np.exp(3 * t) * np.array([1, 1]) + 0.5 * np.exp(-t) * np.array([1, -1])
    check("worked s1: A=[[1,2],[2,1]] has eigenvalues 3, -1; x0=(1,-1) decays, x0=(1,0) grows",
          close(np.sort(np.linalg.eigvals(A1)), [-1, 3]) and close(expm(A1 * t) @ [1, -1], np.exp(-t) * np.array([1, -1]))
          and close(expm(A1 * t) @ [1, 0], x_gen))
    A2 = np.array([[-1.0, 2], [-2, -1]])
    R2 = lambda t: np.exp(-t) * np.array([[np.cos(2 * t), np.sin(2 * t)], [-np.sin(2 * t), np.cos(2 * t)]])  # noqa: E731
    check("worked s2: A=[[-1,2],[-2,-1]] gives e^{-t} times a rotation; |x(t)| = e^{-t}|x0|",
          close(np.linalg.eigvals(A2), [-1 + 2j, -1 - 2j]) and all(close(expm(A2 * t), R2(t)) for t in (0.3, 1.7, 4))
          and close(np.linalg.norm(expm(A2 * 1.3) @ [3, 4]), 5 * np.exp(-1.3)))
    P = {"stable": np.array([[0.0, 1], [-2, -3]]), "unstable": np.array([[0.0, 1], [2, -1]]), "center": np.array([[0.0, 1], [-4, 0]])}
    check("worked s3: [[0,1],[-2,-3]] -> -1,-2; [[0,1],[2,-1]] -> 1,-2; [[0,1],[-4,0]] -> +-2i",
          close(np.sort(np.linalg.eigvals(P["stable"])), [-2, -1]) and close(np.sort(np.linalg.eigvals(P["unstable"])), [-2, 1])
          and close(np.sort_complex(np.linalg.eigvals(P["center"])), [-2j, 2j])
          and ref_verdict(P["center"], lambda v: v.real) == "lyapunov")
    Ad = expm(P["stable"] * math.log(2))
    check("worked s4: A_d = e^{A ln2} = [[3/4,1/4],[-1/2,0]]; x1=(3/4,-1/2), x2=(7/16,-3/8)",
          close(Ad, [[0.75, 0.25], [-0.5, 0]]) and close(Ad @ [1, 0], [0.75, -0.5]) and close(Ad @ Ad @ [1, 0], [7 / 16, -3 / 8])
          and close(np.sort(np.linalg.eigvals(Ad)), [0.25, 0.5]))
    Ad5 = np.array([[0.5, -0.9], [0.9, 0.5]])
    x24 = np.linalg.matrix_power(Ad5, 24) @ [1, 0]
    check("worked s5: [[0.5,-0.9],[0.9,0.5]]: Re = 0.5 < 1 but |lambda| = sqrt(1.06) > 1; |x_24| = 1.06^12 ~ 2.012",
          close(np.abs(np.linalg.eigvals(Ad5)), [math.sqrt(1.06)] * 2) and abs(np.linalg.norm(x24) - 1.06 ** 12) < 1e-12
          and abs(1.06 ** 12 - 2.0122) < 1e-4 and ref_verdict(Ad5, lambda v: abs(v) - 1) == "unstable")
    lam = np.array([-1, 0.2 + 3j, 0.2 - 3j])
    mu = np.exp(lam * 0.5)
    check("worked s6: dt = 0.5 maps -1 -> 0.607 (inside), 0.2 +- 3i -> |mu| = 1.105 (outside); +-3i aliasing check",
          close(np.abs(mu), [math.exp(-0.5), math.exp(0.1), math.exp(0.1)], 1e-12) and abs(math.exp(-0.5) - 0.6065) < 1e-4
          and abs(math.exp(0.1) - 1.1052) < 1e-4 and close(np.exp((0.2 + (3 + 2 * math.pi / 0.5) * 1j) * 0.5), mu[1]))
    # supplemental boundary facts used in notes/animations
    J0 = np.array([[0.0, 1], [0, 0]])
    check("boundary: e^{J0 t} = [[1, t], [0, 1]] (defective zero eigenvalue grows linearly)", close(expm(J0 * 3.5), [[1, 3.5], [0, 1]]))
    check("boundary: semisimple +-i: e^{At} is a rotation, norm 1 for all t",
          all(abs(np.linalg.norm(expm(np.array([[0.0, -1], [1, 0]]) * t), 2) - 1) < 1e-12 for t in (1, 10, 100)))
    Jd = expm(J0 * 0.25)
    check("boundary: discrete Jordan [[1, dt],[0, 1]]^k grows like k on the unit circle",
          close(np.linalg.matrix_power(Jd, 40), [[1, 10], [0, 1]]) and ref_verdict(Jd, lambda v: abs(v) - 1) == "unstable")


# ---------------------------------------------------------------------------- 2. animations

def ffmpeg_frames(path, exe):
    res = subprocess.run([exe, "-hide_banner", "-i", path, "-map", "0:v:0", "-f", "null", "-"], capture_output=True, text=True)
    fr = re.findall(r"frame=\s*(\d+)", res.stderr)
    return res.returncode, int(fr[-1]) if fr else 0, res.stderr


def animation_checks():
    import imageio_ffmpeg
    from control_specs import RELATIONS, SEQUENCES
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    man = json.load(open(os.path.join(ANIM, "manifest.json"), encoding="utf-8"))
    nsteps = sum(len(s["steps"]) for s in SEQUENCES)
    check("specs: 7 sequences across the 6 sections", len(SEQUENCES) == 7 and sorted({s["section"] for s in SEQUENCES}) == [1, 2, 3, 4, 5, 6])
    check("specs: 34-42 animated steps", 34 <= nsteps <= 42, nsteps)
    check("manifest: sequences and steps match specs",
          [s["id"] for s in man["sequences"]] == [s["id"] for s in SEQUENCES]
          and all(len(m["steps"]) == len(s["steps"]) and all(a["title"] == b["title"] and a["tex"] == b["tex"] and a["explanation"] == b["explanation"]
                                                              for a, b in zip(m["steps"], s["steps"]))
                  for m, s in zip(man["sequences"], SEQUENCES)))
    check("manifest: relations known", all(st["relation"] in RELATIONS for s in SEQUENCES for st in s["steps"]))
    bad, contiguous, n, sizes = [], True, 0, set()
    for seq in man["sequences"]:
        prev = None
        for st in seq["steps"]:
            tr = st["transition"]
            p = os.path.join(DIST, tr["src"])
            rc, fr, err = ffmpeg_frames(p, exe)
            m = re.search(r"Video: (\w+)[^\n]*?\b(\d{3,5})x(\d{3,5})\b", err)
            sizes.add((m.group(1), m.group(2) + "x" + m.group(3)) if m else ("?", "?"))
            n += 1
            if rc or fr != tr["frames"] or fr != tr["masterFrames"][1] - tr["masterFrames"][0] or tr["codec"] != "h264":
                bad.append(f"{seq['id']}#{st['index']} rc={rc} frames={fr}/{tr['frames']} codec={tr['codec']}")
            if prev is not None and tr["masterFrames"][0] != prev - 1:
                contiguous = False
            prev = tr["masterFrames"][1]
            for f in (st["initialFrame"], st["finalFrame"]):
                if not os.path.isfile(os.path.join(DIST, f)):
                    bad.append("missing " + f)
        if prev != seq["masterFrames"]:
            contiguous = False
    check("media: every clip decodes with its recorded frame count", not bad, f"{n} clips" if not bad else "; ".join(bad[:5]))
    check("media: decoded streams are h264 1280x720 (probed from the clip itself)", sizes == {("h264", "1280x720")}, sizes)
    check("media: clip boundaries are contiguous (clip k starts on the last frame of clip k-1)", contiguous)
    stills = sum(1 for s in man["sequences"] for _ in range(len(s["steps"]) + 1))
    files = sum(1 for s in man["sequences"] for f in os.listdir(os.path.join(ANIM, s["id"])) if f.startswith("state-"))
    check("media: exactly steps+1 stills per sequence", stills == files, f"{files} stills")
    texs = [s["initial"]["tex"] for s in SEQUENCES] + [st["tex"] for s in SEQUENCES for st in s["steps"]]
    course = json.load(open(os.path.join(DIST, "course.json"), encoding="utf-8"))
    for sec in course["sections"]:
        texs += [st["tex"] for st in sec["example"]["steps"]]
    errs = node("const k=require('./courses/controls/stability-eigenvalues/dist/vendor/katex/katex.min.js');const T=" + json.dumps(texs) + ";"
                "const e=[];T.forEach(t=>{try{k.renderToString(t,{throwOnError:true,displayMode:true})}catch(x){e.push(t.slice(0,40)+': '+x.message.slice(0,80))}});"
                "console.log(JSON.stringify(e))")
    check("math: every step/example display formula typesets in KaTeX", not errs, f"{len(texs)} formulas" if not errs else errs[:3])


# ---------------------------------------------------------------------------- 3. course

def course_checks():
    c = json.load(open(os.path.join(DIST, "course.json"), encoding="utf-8"))
    secs = c["sections"]
    times_ok = secs[0]["time"][0] == 0 and secs[-1]["time"][1] == 1170 and all(a["time"][1] == b["time"][0] for a, b in zip(secs, secs[1:]))
    check("course: 6 sections cover the whole 19:30 lecture contiguously", len(secs) == 6 and times_ok)
    inside = all(s["time"][0] <= v["t"] < s["time"][1] for s in secs for v in s["sources"]["video"])
    check("course: every lecture timestamp lies inside its section", inside)
    check("course: video identity h7nJ6ZL4Lf0, 19:30", c["video"]["id"] == "h7nJ6ZL4Lf0" and c["video"]["duration"] == "19:30")
    check("course: every section has notes, a worked example, book pages and tutor notes",
          all(s["notes"] and s["example"]["steps"] and s["sources"]["book"] and s["tutorNotes"] for s in secs))
    check("course: book pages are printed 332/334/335 with PDF = printed + 20",
          all(b["printed"] in (332, 334, 335) and b["pdf"] == b["printed"] + 20 for s in secs for b in s["sources"]["book"]))
    q = c["quiz"]
    check("quiz: 10 questions, one correct choice each", len(q) == 10 and all(sum(1 for ch in x["choices"] if ch.get("correct")) == 1 for x in q), len(q))
    check("quiz: every option has an explanation", all(ch.get("why", "").strip() for x in q for ch in x["choices"]))
    check("quiz: correct answers are not always in the same position", len({[i for i, ch in enumerate(x["choices"]) if ch.get("correct")][0] for x in q}) >= 3)
    ex = c["explorer"]
    keys = ("l1", "l2", "a", "b", "lj", "s", "x1", "x2", "dt", "t")
    check("explorer: presets inside slider ranges and of a known kind",
          all(p["kind"] in ("real", "complex", "jordan") and all(ex[k]["min"] <= p[k] <= ex[k]["max"] for k in keys if k in p) for p in ex["presets"]))
    out = node("const M=require('" + SM + "');const P=" + json.dumps(ex["presets"]) + ";const D=" + json.dumps({k: ex[k]["default"] for k in keys}) + ";"
               "console.log(JSON.stringify(P.map(p=>{const q=Object.assign({},D,p);return [p.id,M.classifyContinuous(q),M.startBehaviour(q)]})))")
    got = {i: (v, sb) for i, v, sb in out}
    want = {p["id"]: (p["expect"], p["expectStart"]) for p in ex["presets"]}
    check("explorer: each preset's stated verdict matches the math", got == want, got if got != want else len(got))
    txt = json.dumps(c)
    check("course: no leftover pendulum/cruise explorer config or Linear Systems sliders", "\"cruise\"" not in txt and "defectiveNote" not in txt)
    check("course: authored examples and supplemental material labelled", "authored" in txt.lower() and "supplement" in txt.lower())
    check("course: lecture slips are flagged (T^-1 D T order, 'real part' meaning magnitude)",
          "12:57" in txt and "16:10" in txt and "16:44" in txt and "magnitude" in txt)


# ---------------------------------------------------------------------------- 4. server

def http(url, method="GET", body=None, headers=None):
    req = urllib.request.Request(url, method=method, data=body, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def server_checks():
    import server
    course = server.Course()
    label, ctx = course.context({"page": "s5", "section": 5, "sequence": "powers-unit-circle", "step": 2})
    check("tutor context: section 5 step 2 of the new lecture", label.startswith("section 5, animation powers-unit-circle, step 2/")
          and "Stability and Eigenvalues" in ctx and "unit circle" in ctx.lower(), label)
    label2, ctx2 = course.context({"page": "explorer"})
    check("tutor context: explorer uses course.explorer.tutorContext", label2 == "explorer" and "T = [[1, s], [0, 1]]" in ctx2 and "Jordan" in ctx2)
    _, ctx3 = course.context({"section": 2, "sequence": "powers-unit-circle", "step": 1})
    check("tutor context: mismatched sequence/section is dropped", "Animation on screen" not in ctx3)
    check("tutor instructions: generic, mention asymptotic vs Lyapunov", "Lyapunov" in server.INSTRUCTIONS and "pendulum" not in server.INSTRUCTIONS.lower())

    env = {k: v for k, v in os.environ.items() if not k.startswith("OPENAI_")}
    pf = os.path.join(tempfile.gettempdir(), f"se-qa-port-{os.getpid()}.txt")
    nonce = f"qa-{os.getpid()}"
    proc = subprocess.Popen([PY, "-I", os.path.join(PKG, "server.py"), "--port", "8791", "--port-file", pf, "--nonce", nonce],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        t0 = time.time()
        while not os.path.exists(pf) and time.time() - t0 < 15:
            time.sleep(0.1)
        time.sleep(0.2)
        base = f"http://127.0.0.1:{open(pf).read().strip()}"
        st, _, b = http(base + "/__control_health")
        h = json.loads(b)
        check("server: health identity Study_stability_eigenvalues + nonce", st == 200 and h["app"] == "Study_stability_eigenvalues" and h["nonce"] == nonce)
        st, _, b = http(base + "/api/status")
        s = json.loads(b)
        check("server: tutor reports not configured without a key", st == 200 and s["tutor"]["configured"] is False)
        st, _, b = http(base + "/api/tutor", "POST", json.dumps({"question": "Why the unit circle?", "context": {"page": "s5", "section": 5}}).encode(),
                        {"Content-Type": "application/json", "Origin": base})
        check("server: /api/tutor without a key returns a clear error, no network call", st >= 400 and b"key" in b.lower(), f"HTTP {st}")
        st, hd, b = http(base + "/course.json")
        check("server: serves dist/course.json", st == 200 and json.loads(b)["video"]["id"] == "h7nJ6ZL4Lf0")
        if os.path.isfile(os.path.join(ROOT, "databook.pdf")):
            st, hd, b = http(base + "/book", headers={"Range": "bytes=0-99"})
            check("server: /book honours byte ranges", st == 206 and len(b) == 100 and b.startswith(b"%PDF"), f"HTTP {st}")
        st, _, _ = http(base + "/../server.py")
        st2, _, _ = http(base + "/animations/")
        check("server: no path escape, no directory listing", st in (400, 403, 404) and st2 in (403, 404), f"{st}/{st2}")
    finally:
        proc.terminate()
        proc.wait(10)
        try:
            os.remove(pf)
        except OSError:
            pass


def book_checks():
    pdf = os.path.join(ROOT, "databook.pdf")
    if not os.path.isfile(pdf):
        check("book: local PDF absent; page check skipped", True)
        return
    import importlib.util
    if importlib.util.find_spec("pymupdf") is None and importlib.util.find_spec("fitz") is None:
        dl = os.path.join(ROOT, ".venv-download", "Scripts", "python.exe")
        code = ("import sys,pymupdf;d=pymupdf.open(sys.argv[1]);import json;"
                "print(json.dumps({p:d[p-1].get_text() for p in (352,354,355)}))")
        res = subprocess.run([dl, "-I", "-c", code, pdf], capture_output=True, text=True, encoding="utf-8")
        pages = {int(k): v for k, v in json.loads(res.stdout).items()}
    else:
        import pymupdf
        d = pymupdf.open(pdf)
        pages = {p: d[p - 1].get_text() for p in (352, 354, 355)}
    check("book: PDF p.352 is printed 332 with the stability paragraph", pages[352].lstrip().startswith("332") and "negative" in pages[352] and "unstable" in pages[352])
    check("book: PDF p.354 is printed 334 with discrete-time Eqs. 8.21-8.22 and the unit circle",
          pages[354].lstrip().startswith("334") and "(8.22a)" in pages[354] and "unit circle" in pages[354])
    check("book: PDF p.355 is printed 335 with the inverted pendulum eigenvalues", "335" in pages[355][:80] and "Pendulum up" in pages[355])


# ---------------------------------------------------------------------------- 5. launcher, isolation

def isolation_checks():
    ps = open(os.path.join(ROOT, "launch_stability_eigenvalues.ps1"), encoding="utf-8").read()
    check("launcher: targets courses/controls/stability-eigenvalues/server.py, port 8790, app identity", "courses\\controls\\stability-eigenvalues\\server.py" in ps and "8790" in ps
          and "Study_stability_eigenvalues" in ps)
    banned = [os.path.relpath(os.path.join(dp, f), DIST) for dp, _, fs in os.walk(DIST) for f in fs
              if (f.lower().endswith((".pdf", ".vtt", ".srt", ".txt", ".py")) and "vendor" not in dp) or f == "video.mp4"]
    check("dist: no book, captions, transcript or lecture video bundled", not banned, banned[:3])
    app = open(os.path.join(DIST, "app.js"), encoding="utf-8").read() + open(os.path.join(DIST, "index.html"), encoding="utf-8").read()
    check("shell: no leftover pendulum/cruise/Linear Systems labels",
          not re.search(r"pendulum|cruise|control_math|linear_systems|Linear Systems", app, re.I))
    siblings = [os.path.join(ROOT, "courses", "controls", name, "dist")
                for name in ("overview", "linear-systems", "stability-eigenvalues")]
    keys = [re.search(r"var STORE_KEY\s*=\s*['\"]([^'\"]+)",
                      open(os.path.join(path, "app.js"), encoding="utf-8").read())
            for path in siblings]
    check("isolation: control lectures have independent assets and progress keys",
          len(set(map(os.path.realpath, siblings))) == 3 and all(keys)
          and len({key.group(1) for key in keys if key}) == 3)


def main():
    groups = [math_checks, animation_checks, course_checks, server_checks, book_checks, isolation_checks]
    only = set(sys.argv[1:])
    for f in groups:
        if only and f.__name__ not in only:
            continue
        try:
            f()
        except Exception as e:  # report and continue with the other groups
            check(f.__name__ + " ran", False, repr(e)[:300])
    os.makedirs(os.path.join(ROOT, "qa", "results"), exist_ok=True)
    with open(os.path.join(ROOT, "qa", "results", "stability_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    failed = [r for r in results if not r["ok"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
