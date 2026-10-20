"""Package checks for the Linearizing Around a Fixed Point companion (lesson math, media, course, server, book).

    .venv\\Scripts\\python.exe qa\\linearization_qa.py [math_checks animation_checks course_checks server_checks book_checks isolation_checks]

Independent of the explorer solver tests in qa/linearization_math_qa.py. The lesson's claims (Jacobian entries,
fixed points, eigenvalues, MATLAB numbers, worked examples, the remainder table) are recomputed with NumPy and
central finite differences; media is decoded with FFmpeg; every display and inline formula is typeset with the
bundled KaTeX; the server is started without OPENAI_* variables (no network call). Results go to
qa/results/linearization_qa.json. Does not require a clean Git tree.
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
import urllib.error
import urllib.request

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "courses", "controls", "linearization")
DIST = os.path.join(PKG, "dist")
ANIM = os.path.join(DIST, "animations")
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
GIT = shutil.which("git") or os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Git", "cmd", "git.exe")
sys.path.insert(0, os.path.join(PKG, "animation"))
sys.path.insert(0, PKG)

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    return bool(ok)


def node(script):
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True, cwd=ROOT, encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr[-600:])
    return json.loads(r.stdout)


def jac_fd(f, x, h=1e-6):
    x = np.asarray(x, float)
    n = len(x)
    J = np.zeros((n, n))
    for j in range(n):
        e = np.zeros(n); e[j] = h
        J[:, j] = (np.asarray(f(x + e)) - np.asarray(f(x - e))) / (2 * h)
    return J


def course():
    return json.load(open(os.path.join(DIST, "course.json"), encoding="utf-8"))


# ---------------------------------------------------------------------------- 1. lesson mathematics

def math_checks():
    rng = np.random.default_rng(7)
    # Section 2: the lecture's example
    f = lambda x: np.array([x[0] * x[1], x[0] ** 2 + x[1] ** 2])
    J = lambda x: np.array([[x[1], x[0]], [2 * x[0], 2 * x[1]]])
    pts = rng.uniform(-2, 2, (20, 2))
    check("s2: [[x2, x1], [2x1, 2x2]] matches finite differences at 20 random points",
          all(np.allclose(jac_fd(f, p), J(p), atol=1e-7) for p in pts))
    grid = [(a, b) for a in np.linspace(-2, 2, 41) for b in np.linspace(-2, 2, 41)]
    zeros = [p for p in grid if np.allclose(f(np.array(p)), 0, atol=1e-12)]
    check("s2: the only real fixed point on a grid is (0, 0), where A = 0", zeros == [(0.0, 0.0)] and np.allclose(jac_fd(f, [0, 0]), 0, atol=1e-9), zeros)
    ode = lambda t, x: f(x)
    from scipy.integrate import solve_ivp
    s = solve_ivp(ode, (0, 4), [0, 0.2], rtol=1e-10, atol=1e-12)
    check("s2: origin unstable despite A = 0 (x2 = 0.2 on the x2 axis grows past 1)", s.status == 1 or s.y[1, -1] > 1, f"x2 end {s.y[1, -1]:.3g}")
    # Section 1 animation and Section 3 non-fixed point
    g = lambda x: x * (1 - x)
    d = lambda x: (g(x + 1e-6) - g(x - 1e-6)) / 2e-6
    check("s1: x(1 - x) has fixed points 0 and 1 with slopes +1 (unstable) and -1 (stable)",
          g(0) == 0 and g(1) == 0 and abs(d(0) - 1) < 1e-8 and abs(d(1) + 1) < 1e-8)
    e = np.linspace(-0.5, 0.5, 11)
    check("s3: about x0 = 0.5, f(0.5 + eta) = 0.25 + 0*eta - eta^2 exactly", np.allclose(g(0.5 + e), 0.25 - e ** 2) and abs(d(0.5)) < 1e-8)
    # Section 3 remainder table (sin)
    r12, r06 = abs(math.sin(1.2) - 1.2), abs(math.sin(0.6) - 0.6)
    check("s3: sin remainders 0.268 and 0.035, ratio about 7.6", round(r12, 3) == 0.268 and round(r06, 3) == 0.035 and round(r12 / r06, 1) == 7.6,
          f"{r12:.4f}, {r06:.4f}, {r12 / r06:.2f}")
    # Section 4: -x^3 and +x^3
    fm, fp = (lambda x: -x ** 3), (lambda x: x ** 3)
    dz = [(h(1e-4) - h(-1e-4)) / 2e-4 for h in (fm, fp)]
    check("s4: -x^3 and +x^3 both have A = 0 at the origin; arrows point in for -x^3, out for +x^3",
          all(abs(v) < 1e-7 for v in dz) and fm(0.5) < 0 < fm(-0.5) and fp(0.5) > 0 > fp(-0.5))
    # Sections 5-6: pendulum
    def fpend(q, dd):
        return lambda x: np.array([x[1], -q * math.sin(x[0]) - dd * x[1]])
    ok = True
    for q in (0.25, 1, 4):
        for dd in (0, 0.1, 3):
            F = fpend(q, dd)
            for k in range(-2, 3):
                ok &= np.allclose(F(np.array([k * math.pi, 0])), 0, atol=1e-12)
            for p in rng.uniform(-4, 4, (5, 2)):
                ok &= np.allclose(jac_fd(F, p), [[0, 1], [-q * math.cos(p[0]), -dd]], atol=1e-6)
            ok &= np.allclose(jac_fd(F, [0, 0]), [[0, 1], [-q, -dd]], atol=1e-7) and np.allclose(jac_fd(F, [math.pi, 0]), [[0, 1], [q, -dd]], atol=1e-7)
    check("s5/s6: f(k pi, 0) = 0; J = [[0, 1], [-q cos x1, -d]]; A_d = [[0,1],[-q,-d]], A_u = [[0,1],[q,-d]]", ok)
    check("s5: theta = pi + 0.15 is about 3.29 rad", round(math.pi + 0.15, 2) == 3.29)
    ok_formula, ok_up, ok_down = True, True, True
    for q in np.linspace(0.25, 4, 16):
        for dd in np.linspace(0, 4, 17):
            ed = np.sort_complex(np.linalg.eigvals([[0, 1], [-q, -dd]]))
            eu = np.sort(np.linalg.eigvals([[0, 1], [q, -dd]]).real)
            fd = np.sort_complex(np.array([(-dd + np.sqrt(complex(dd * dd - 4 * q))) / 2, (-dd - np.sqrt(complex(dd * dd - 4 * q))) / 2]))
            fu = np.sort([(-dd + math.sqrt(dd * dd + 4 * q)) / 2, (-dd - math.sqrt(dd * dd + 4 * q)) / 2])
            ok_formula &= np.allclose(ed, fd, atol=1e-9) and np.allclose(eu, fu, atol=1e-9)
            ok_up &= eu[1] > 0 > eu[0]
            if dd > 0:
                ok_down &= max(ed.real) < 0
                ok_down &= (abs(ed.imag).max() > 0) == (dd * dd < 4 * q - 1e-12) or abs(dd * dd - 4 * q) < 1e-9
    check("s6: companion formulas (-d +- sqrt(d^2 -+ 4q))/2 equal numpy eigenvalues on a 16x17 grid", ok_formula)
    check("s6: up has one positive eigenvalue for every d >= 0; down has Re < 0 for d > 0, complex iff d < 2 sqrt q", ok_up and ok_down)
    check("s6: d = 3, q = 1 gives down -0.382, -2.618 and up +0.303", np.allclose(np.sort(np.linalg.eigvals([[0, 1], [-1, -3]]).real), [-2.618034, -0.381966], atol=1e-6)
          and abs(max(np.linalg.eigvals([[0, 1], [1, -3]]).real) - 0.302776) < 1e-6)
    # Section 7: the lecture's MATLAB numbers (frame 30:00) and the 6-decimal values used on screen
    ed = np.linalg.eigvals([[0, 1], [-1, -0.1]])
    eu = np.sort(np.linalg.eigvals([[0, 1], [1, -0.1]]).real)
    check("s7: eig(Ad) rounds to -0.0500 +- 0.9987i and eig(Au) to -1.0512, 0.9512",
          np.allclose(np.round(ed.real, 4), -0.05) and np.allclose(np.round(abs(ed.imag), 4), 0.9987) and np.allclose(np.round(eu, 4), [-1.0512, 0.9512]))
    from control_specs import SEQUENCES
    mt = json.dumps([s for s in SEQUENCES if s["id"] == "matlab-check"])
    check("s7: on-screen 6-decimal values agree with numpy (0.998749, 1.051249, 0.951249)",
          f"{abs(ed[0].imag):.6f}" == "0.998749" and f"{-eu[0]:.6f}" == "1.051249" and f"{eu[1]:.6f}" == "0.951249"
          and "0.998749" in mt and "1.051249" in mt and "0.951249" in mt)
    # The NumPy snippet quoted in the Section 7 notes, evaluated literally
    s7 = " ".join(p for blk in course()["sections"][6]["notes"] for p in blk["paragraphs"])
    calls = re.findall(r"np\.linalg\.eigvals\((\[\[[^\]]*\], \[[^\]]*\]\])\)", s7)
    vals = [np.linalg.eigvals(eval(c, {"d": 0.1})) for c in calls]
    check("s7: the NumPy snippet in the notes reproduces both MATLAB results", len(calls) == 2 and np.allclose(np.sort_complex(vals[0]), np.sort_complex(ed))
          and np.allclose(np.sort(vals[1].real), eu), calls)
    # Worked examples
    f1 = lambda x: np.array([x[1], x[0] - x[0] ** 3])
    check("example s1: (0,0), (1,0), (-1,0) are fixed points of (x2, x1 - x1^3)", all(np.allclose(f1(np.array(p, float)), 0) for p in [(0, 0), (1, 0), (-1, 0)]))
    f2 = lambda x: np.array([x[0] - x[0] * x[1], -x[1] + x[0] ** 2])
    A00, A11, Am11 = jac_fd(f2, [0, 0]), jac_fd(f2, [1, 1]), jac_fd(f2, [-1, 1])
    check("example s2: fixed points and A matrices of (x1 - x1 x2, -x2 + x1^2)",
          all(np.allclose(f2(np.array(p, float)), 0) for p in [(0, 0), (1, 1), (-1, 1)]) and np.allclose(A00, [[1, 0], [0, -1]], atol=1e-7)
          and np.allclose(A11, [[0, -1], [2, -1]], atol=1e-7) and np.allclose(Am11, [[0, 1], [-2, -1]], atol=1e-7))
    e11, em11 = np.linalg.eigvals(A11), np.linalg.eigvals(Am11)
    check("example s4: (±1, 1) have lambda = (-1 ± i sqrt 7)/2 (stable focus); origin saddle",
          np.allclose(np.sort_complex(e11), np.sort_complex([(-1 - 1j * math.sqrt(7)) / 2, (-1 + 1j * math.sqrt(7)) / 2]), atol=1e-6)
          and np.allclose(np.sort_complex(em11), np.sort_complex(e11), atol=1e-6) and sorted(np.linalg.eigvals(A00).real) == [-1, 1])
    eta = np.array([0.1, 0.5])
    check("example s3: (1 + eta)^2 - 1 = 2 eta + eta^2; shares 5% and 25%", np.allclose((1 + eta) ** 2 - 1, 2 * eta + eta ** 2)
          and np.allclose(eta ** 2 / (2 * eta), [0.05, 0.25]))
    check("example s5: 6.2 - 2 pi = -0.083", round(6.2 - 2 * math.pi, 3) == -0.083)
    e6d, e6u = np.linalg.eigvals([[0, 1], [-4, -1]]), np.sort(np.linalg.eigvals([[0, 1], [4, -1]]).real)
    check("example s6: q = 4, d = 1: -0.5 ± 1.936i and 1.562, -2.562; oscillation stops at d = 4",
          np.allclose(e6d.real, -0.5) and round(abs(e6d[0].imag), 3) == 1.936 and np.allclose(np.round(e6u, 3), [-2.562, 1.562]))
    e7d, e7u = np.linalg.eigvals([[0, 1], [-1, -0.4]]), np.sort(np.linalg.eigvals([[0, 1], [1, -0.4]]).real)
    check("example s7: d = 0.4: -0.2 ± 0.9798i and 0.8198, -1.2198", np.allclose(e7d.real, -0.2) and round(abs(e7d[0].imag), 4) == 0.9798
          and np.allclose(np.round(e7u, 4), [-1.2198, 0.8198]))


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
    check("specs: 8 sequences covering all 7 sections", len(SEQUENCES) == 8 and sorted({s["section"] for s in SEQUENCES}) == list(range(1, 8)))
    check("specs: 35-42 animated steps", 35 <= nsteps <= 42, nsteps)
    check("manifest: sequences and steps match specs (titles, tex, explanations)",
          [s["id"] for s in man["sequences"]] == [s["id"] for s in SEQUENCES]
          and all(len(m["steps"]) == len(s["steps"]) and m["initial"]["tex"] == s["initial"]["tex"]
                  and all(a["title"] == b["title"] and a["tex"] == b["tex"] and a["explanation"] == b["explanation"] for a, b in zip(m["steps"], s["steps"]))
                  for m, s in zip(man["sequences"], SEQUENCES)))
    check("manifest: relations known", all(st["relation"] in RELATIONS for s in SEQUENCES for st in s["steps"]))
    bad, contiguous, n, sizes = [], True, 0, set()
    for seq in man["sequences"]:
        prev = None
        for st in seq["steps"]:
            tr = st["transition"]
            rc, fr, err = ffmpeg_frames(os.path.join(DIST, tr["src"]), exe)
            m = re.search(r"Video: (\w+)[^\n]*?\b(\d{3,5})x(\d{3,5})\b", err)
            sizes.add((m.group(1), m.group(2) + "x" + m.group(3)) if m else ("?", "?"))
            n += 1
            if rc or fr != tr["frames"] or fr != tr["masterFrames"][1] - tr["masterFrames"][0]:
                bad.append(f"{seq['id']}#{st['index']} rc={rc} frames={fr}/{tr['frames']}")
            if prev is not None and tr["masterFrames"][0] != prev - 1:
                contiguous = False
            prev = tr["masterFrames"][1]
            for fpath in (st["initialFrame"], st["finalFrame"]):
                if not os.path.isfile(os.path.join(DIST, fpath)):
                    bad.append("missing " + fpath)
    check("media: every clip decodes with its recorded frame count", not bad, f"{n} clips" if not bad else "; ".join(bad[:5]))
    check("media: decoded streams are h264 1280x720", sizes == {("h264", "1280x720")}, sizes)
    check("media: clip boundaries are contiguous", contiguous)
    stills = sum(len(s["steps"]) + 1 for s in man["sequences"])
    files = sum(1 for s in man["sequences"] for f in os.listdir(os.path.join(ANIM, s["id"])) if f.startswith("state-"))
    check("media: exactly steps+1 stills per sequence", stills == files, f"{files} stills")
    c = course()
    from control_specs import SEQUENCES as SQ
    disp = [s["initial"]["tex"] for s in SQ] + [st["tex"] for s in SQ for st in s["steps"]]
    inline = [s["title"] for s in SQ] + [s["summary"] for s in SQ] + [s["initial"]["explanation"] for s in SQ]
    inline += [st["title"] for s in SQ for st in s["steps"]] + [st["explanation"] for s in SQ for st in s["steps"]]
    for sec in c["sections"]:
        disp += [st["tex"] for st in sec["example"]["steps"]]
        inline += [sec["title"], sec["summary"], sec["example"]["problem"], sec["example"]["answer"]] + sec["goals"] + sec["keyIdeas"]
        inline += [st["text"] for st in sec["example"]["steps"]] + [p for blk in sec["notes"] for p in blk["paragraphs"]]
    for qq in c["quiz"]:
        inline += [qq["question"]] + [ch["text"] for ch in qq["choices"]] + [ch["why"] for ch in qq["choices"]]
    pieces = [m for t in inline for m in re.findall(r"\$([^$]+)\$", t)]
    errs = node("const k=require('./courses/controls/linearization/dist/vendor/katex/katex.min.js');"
                "const D=" + json.dumps(disp) + ",I=" + json.dumps(pieces) + ";const e=[];"
                "D.forEach(t=>{try{k.renderToString(t,{throwOnError:true,displayMode:true})}catch(x){e.push(t.slice(0,40)+': '+x.message.slice(0,60))}});"
                "I.forEach(t=>{try{k.renderToString(t,{throwOnError:true})}catch(x){e.push(t.slice(0,40)+': '+x.message.slice(0,60))}});"
                "console.log(JSON.stringify(e))")
    check("math: every display formula and every inline $...$ fragment typesets in KaTeX", not errs,
          f"{len(disp)} display, {len(pieces)} inline" if not errs else errs[:3])
    odd = [t for t in inline if t.count("$") % 2]
    check("math: no unbalanced $ delimiters in course or step text", not odd, odd[:2])


# ---------------------------------------------------------------------------- 3. course

def course_checks():
    c = course()
    secs = c["sections"]
    check("course: 7 sections cover 0:00-30:46 contiguously", len(secs) == 7 and secs[0]["time"][0] == 0 and secs[-1]["time"][1] == 1846
          and all(a["time"][1] == b["time"][0] for a, b in zip(secs, secs[1:])))
    check("course: section boundaries 180/405/780/960/1350/1650 as briefed", [s["time"][0] for s in secs[1:]] == [180, 405, 780, 960, 1350, 1650])
    inside = all(s["time"][0] <= v["t"] < s["time"][1] for s in secs for v in s["sources"]["video"])
    check("course: every lecture timestamp lies inside its section", inside)
    check("course: timestamps sit on the 30-second transcript segments (no invented precision)",
          all(v["t"] % 30 == 0 for s in secs for v in s["sources"]["video"]))
    check("course: video 1YMTkELi3tE, 30:46, title kept", c["video"]["id"] == "1YMTkELi3tE" and c["video"]["duration"] == "30:46"
          and c["title"] == "Linearizing Around a Fixed Point")
    check("course: every section has goals, notes, key ideas, a worked example with steps, book pages and tutor notes",
          all(s["goals"] and s["notes"] and s["keyIdeas"] and s["example"]["steps"] and s["example"]["answer"] and s["sources"]["book"]
              and len(s["tutorNotes"]) > 200 for s in secs))
    check("course: book pages are printed 330/335 with PDF = printed + 20",
          all(b["printed"] in (330, 335) and b["pdf"] == b["printed"] + 20 for s in secs for b in s["sources"]["book"]))
    q = c["quiz"]
    check("quiz: 10 questions, one correct choice each, unique ids", len(q) == 10 and len({x["id"] for x in q}) == 10
          and all(sum(1 for ch in x["choices"] if ch.get("correct")) == 1 for x in q))
    check("quiz: every option has an explanation", all(len(ch.get("why", "").strip()) > 20 for x in q for ch in x["choices"]))
    check("quiz: correct answers spread over positions", len({[i for i, ch in enumerate(x["choices"]) if ch.get("correct")][0] for x in q}) >= 3)
    txt = json.dumps(c, ensure_ascii=False)
    check("course: authored/companion/extension material labelled", "authored" in txt.lower() and "companion" in txt.lower() and "extension" in txt.lower())
    check("course: damping is taught (d = 0.1 MATLAB) and the book example is undamped",
          "d = 0.1" in txt and "on the board" in txt and "no friction" in txt)
    check("course: no false hyperbolicity claims", "does not mean all eigenvalues are negative" in json.dumps(__import__("control_specs").SEQUENCES)
          and "signs do not matter" in txt)
    check("course: no leftover content from other lectures", not re.search(r"cruise|Stability and Eigenvalues|h7nJ6ZL4Lf0|Linear Systems lecture", txt))
    ex = c["explorer"]
    check("explorer config: limits/tutorContext describe the zero-input reference and the book extension",
          "zero-input reference" in ex["limits"] and "zero-input reference" in ex["tutorContext"] and "extension" in ex["limits"]
          and "d = 0.1" in ex["tutorContext"] and ex["playRate"] == 1)
    out = node("const S=require('./courses/controls/linearization/dist/study_math.js');"
               "console.log(JSON.stringify({p:S.PRESETS.map(p=>[p.id,p.eq,p.d,S.classify(p.eq,p.q,p.d).linear,S.classify(p.eq,p.q,p.d).nonlinear]),"
               "d:[S.PARAMS.q.default,S.PARAMS.d.default,S.PARAMS.du.default]}))")
    want = {"lecture-down": "focus", "lecture-up": "saddle", "undamped-down": "center", "large-down": "focus", "overdamped-down": "node", "exact-up": "saddle"}
    got = {p[0]: p[3] for p in out["p"]}
    check("explorer: presets classify as their labels say", got == want, got)
    check("explorer: defaults q = 1, d = 0.1, delta u = 0 (the lecture's MATLAB example)", out["d"] == [1, 0.1, 0])
    check("course: tutor notes cite printed pages and lecture times", all(re.search(r"p\.\s?33[05]", s["tutorNotes"]) for s in secs))


# ---------------------------------------------------------------------------- 4. server and trusted context

def http(url, method="GET", body=None, headers=None):
    req = urllib.request.Request(url, method=method, data=body, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def server_checks():
    import importlib
    server = importlib.import_module("server")
    cs = server.Course()
    label, ctx = cs.context({"page": "s7", "section": 7, "sequence": "matlab-check", "step": 2})
    check("tutor context: section 7, MATLAB animation step 2 with the eigenvalues", label == "section 7, animation matlab-check, step 2/5"
          and "Linearizing Around a Fixed Point" in ctx and "0.998749" in ctx and "eig(Ad)" in ctx and "30:00" in ctx, label)
    label0, ctx0 = cs.context({"page": "s7", "section": 7, "sequence": "matlab-check", "step": 0})
    check("tutor context: opening state of a sequence", label0 == "section 7, animation matlab-check" and "opening state" in ctx0)
    label2, ctx2 = cs.context({"page": "explorer"})
    check("tutor context: explorer uses course.explorer.tutorContext", label2 == "explorer" and "zero-input reference" in ctx2 and "delta u" in ctx2)
    _, ctx3 = cs.context({"page": "s6", "section": 6, "sequence": "matlab-check", "step": 1})
    check("tutor context: mismatched sequence/section is dropped", "Animation on screen" not in ctx3)
    _, ctx4 = cs.context({"page": "s9", "section": 9, "sequence": "x", "step": "7"})
    check("tutor context: out-of-range section ignored", "Current section" not in ctx4)
    check("tutor instructions: linearization caveat present and generic otherwise",
          "zero real part" in server.INSTRUCTIONS and "Linear Systems" not in server.INSTRUCTIONS)

    env = {k: v for k, v in os.environ.items() if not k.startswith("OPENAI_")}
    pf = os.path.join(tempfile.gettempdir(), f"lz-qa-port-{os.getpid()}.txt")
    nonce = f"qa-{os.getpid()}"
    proc = subprocess.Popen([PY, "-I", os.path.join(PKG, "server.py"), "--port", "8811", "--port-file", pf, "--nonce", nonce],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        t0 = time.time()
        while not os.path.exists(pf) and time.time() - t0 < 15:
            time.sleep(0.1)
        time.sleep(0.3)
        base = f"http://127.0.0.1:{open(pf).read().strip()}"
        st, _, b = http(base + "/__control_health")
        h = json.loads(b)
        check("server: health identity Study_linearization + nonce", st == 200 and h["app"] == "Study_linearization" and h["nonce"] == nonce)
        st, _, b = http(base + "/api/status")
        check("server: tutor reports not configured without a key", st == 200 and json.loads(b)["tutor"]["configured"] is False)
        st, _, b = http(base + "/api/tutor", "POST", json.dumps({"question": "Why is the top unstable?", "context": {"page": "s7", "section": 7}}).encode(),
                        {"Content-Type": "application/json", "Origin": base})
        check("server: /api/tutor without a key returns a clear error (no network call)", st >= 400 and b"key" in b.lower(), f"HTTP {st}")
        st, _, b = http(base + "/course.json")
        check("server: serves dist/course.json", st == 200 and json.loads(b)["video"]["id"] == "1YMTkELi3tE")
        if os.path.isfile(os.path.join(ROOT, "databook.pdf")):
            st, _, b = http(base + "/book", headers={"Range": "bytes=0-99"})
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


# ---------------------------------------------------------------------------- 5. book pages

def book_checks():
    pdf = os.path.join(ROOT, "databook.pdf")
    if not os.path.isfile(pdf):
        check("book: local PDF absent; page check skipped", True)
        return
    dl = os.path.join(ROOT, ".venv-download", "Scripts", "python.exe")
    code = "import sys,json,pymupdf;d=pymupdf.open(sys.argv[1]);print(json.dumps({p:d[p-1].get_text() for p in (350,355)}))"
    res = subprocess.run([dl, "-I", "-c", code, pdf], capture_output=True, text=True, encoding="utf-8")
    pages = {int(k): v for k, v in json.loads(res.stdout).items()}
    check("book: PDF p.350 is printed 330 with the Taylor linearization Eqs. 8.7-8.10",
          pages[350].lstrip().startswith("330") and all(e in pages[350] for e in ("(8.7a)", "(8.8)", "(8.9)", "(8.10a)")) and "ﬁxed point" in pages[350])
    check("book: PDF p.355 is printed 335 with the pendulum Eqs. 8.23-8.25 (undamped)",
          "335" in pages[355][:80] and all(e in pages[355] for e in ("(8.23)", "(8.24)", "(8.25)")) and "Pendulum up" in pages[355])


# ---------------------------------------------------------------------------- 6. launcher and isolation

def isolation_checks():
    ps = open(os.path.join(ROOT, "launch_linearization.ps1"), encoding="utf-8").read()
    check("launcher: targets courses/controls/linearization/server.py, port 8810, app identity",
          "courses\\controls\\linearization\\server.py" in ps and "8810" in ps and "Study_linearization" in ps)
    banned = [os.path.relpath(os.path.join(dp, f), DIST) for dp, _, fs in os.walk(DIST) for f in fs
              if (f.lower().endswith((".pdf", ".vtt", ".srt", ".txt", ".py", ".m4a", ".json")) and "vendor" not in dp
                  and f not in ("course.json", "manifest.json")) or f == "video.mp4"]
    check("dist: no book, captions, transcript, audio or lecture video bundled", not banned, banned[:3])
    app = open(os.path.join(DIST, "app.js"), encoding="utf-8").read()
    idx = open(os.path.join(DIST, "index.html"), encoding="utf-8").read()
    check("shell: identity, storage key and launcher names are this package's",
          'STORE_KEY = "linearization-v1"' in app and "Study_linearization" in app and "launch_linearization.ps1" in app
          and "Linearizing Around a Fixed Point" in idx)
    check("shell: no leftover labels from other packages", not re.search(r"cruise|control_math|Stability and Eigenvalues|Linear Systems|overview", app + idx, re.I))
    srv = open(os.path.join(PKG, "server.py"), encoding="utf-8").read()
    check("server: docstrings name this package (no overview paths)", "controls/overview" not in srv and 'APP = "Study_linearization"' in srv)
    siblings = [os.path.join(ROOT, "courses", "controls", n, "dist") for n in ("overview", "linear-systems", "stability-eigenvalues", "linearization")]
    keys = [re.search(r"var STORE_KEY\s*=\s*['\"]([^'\"]+)", open(os.path.join(p, "app.js"), encoding="utf-8").read()) for p in siblings]
    check("isolation: four control lectures with independent progress keys", all(keys) and len({k.group(1) for k in keys}) == 4,
          [k.group(1) for k in keys if k])
    probe = [os.path.join(PKG, "animation", "masters", "MatlabSequence.mp4"), os.path.join(PKG, "animation", "masters", "render_config.yml")]
    r = subprocess.run([GIT, "check-ignore", "--no-index", *probe], cwd=ROOT, capture_output=True, text=True)
    check("repo hygiene: master renders and generated config are git-ignored", len(r.stdout.strip().splitlines()) == 2, r.stdout.strip()[-80:])
    r2 = subprocess.run([GIT, "check-ignore", "--no-index", os.path.join(DIST, "animations", "manifest.json")], cwd=ROOT, capture_output=True, text=True)
    check("repo hygiene: rendered dist assets are not ignored (viewable without rendering)", r2.returncode == 1)


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
    with open(os.path.join(ROOT, "qa", "results", "linearization_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    failed = [r for r in results if not r["ok"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
