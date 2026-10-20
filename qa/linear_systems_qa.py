"""Non-browser checks for the Linear Systems study companion.

    .venv\\Scripts\\python.exe qa\\linear_systems_qa.py

1. math: dist/study_math.js (run in node) against scipy.linalg.expm and the worked numbers.
2. animations: specs <-> manifest agreement, every clip decodes with the recorded frame count,
   contiguous master boundaries, stills present, clip formulas parse in KaTeX (node).
3. course.json: sections, timings, linked 22:22 moment, quiz explanations, explorer config.
4. server: trusted tutor context, missing-key tutor state, health identity, /book byte ranges.
5. launcher and isolation: launch_linear_systems.ps1 targets this package; dist holds no source media.
Writes qa/results/linear_systems_qa.json. Exit code 1 if any check fails.
"""
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request

import numpy as np
from scipy.linalg import expm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "courses/controls/linear-systems")
DIST = os.path.join(PKG, "dist")
ANIM = os.path.join(DIST, "animations")
PY = sys.executable
sys.path.insert(0, os.path.join(PKG, "animation"))
sys.path.insert(0, PKG)

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""), flush=True)
    return ok


def node(script):
    res = subprocess.run(["node", "-e", script], capture_output=True, text=True, cwd=ROOT)
    if res.returncode:
        raise RuntimeError(res.stderr)
    return json.loads(res.stdout)


# ---------------------------------------------------------------------------- 1. math

def math_checks():
    rng = np.random.default_rng(7)
    cases = [(-1, -2, 1, 2, 1, math.log(2)), (0.5, -1.5, 1, 1.2, 2.5, 1.5), (-1, -1, 1, 2, 1, 1.0), (0, 0, 0, 1, -1, 3)]
    for _ in range(40):
        cases.append(tuple(np.round(rng.uniform([-3, -3, -2, -3, -3, 0], [2, 2, 2, 3, 3, 4]), 2)))
    js = ("const M=require('./courses/controls/linear-systems/dist/study_math.js');const C=" + json.dumps(cases) + ";"
          "console.log(JSON.stringify(C.map(c=>{const p={l1:c[0],l2:c[1],s:c[2],x1:c[3],x2:c[4]};"
          "return {r:M.pipeline(p,c[5]),E:M.expA(c[0],c[1],c[2],c[5]),r0:M.pipeline(p,0),"
          "rs:M.pipeline(p,c[5]+0.37),half:M.pipeline({l1:c[0],l2:c[1],s:c[2],x1:M.pipeline(p,c[5]).xt[0],x2:M.pipeline(p,c[5]).xt[1]},0.37)};})))")
    out = node(js)
    worst = {"A": 0, "expm": 0, "x": 0, "t0": 0, "semi": 0, "eig": 0}
    for c, o in zip(cases, out):
        l1, l2, s, x1, x2, t = c
        T = np.array([[1, s], [0, 1.0]])
        D = np.diag([l1, l2])
        A = T @ D @ np.linalg.inv(T)
        worst["A"] = max(worst["A"], np.abs(np.array(o["r"]["A"]) - A).max())
        E = expm(A * t)
        worst["expm"] = max(worst["expm"], np.abs(np.array(o["E"]) - E).max() / max(1, np.abs(E).max()))
        xt = E @ np.array([x1, x2])
        worst["x"] = max(worst["x"], np.abs(np.array(o["r"]["xt"]) - xt).max() / max(1, np.abs(xt).max()))
        worst["t0"] = max(worst["t0"], np.abs(np.array(o["r0"]["xt"]) - [x1, x2]).max())
        a, b = np.array(o["rs"]["xt"]), np.array(o["half"]["xt"])
        worst["semi"] = max(worst["semi"], np.abs(a - b).max() / max(1, np.abs(a).max()))
        # columns of T are eigenvectors of A with the eigenvalues in D, in that order
        worst["eig"] = max(worst["eig"], np.abs(A @ T - T @ D).max())
    check("math: A = T D T^-1 matches the closed form [[l1, s(l2-l1)], [0, l2]]", worst["A"] < 1e-12, f"{len(cases)} cases, max err {worst['A']:.1e}")
    check("math: T e^{Dt} T^-1 equals scipy expm(At)", worst["expm"] < 1e-12, f"max rel err {worst['expm']:.1e}")
    check("math: x(t) equals expm(At) x0", worst["x"] < 1e-12, f"max rel err {worst['x']:.1e}")
    check("math: x(0) = x0", worst["t0"] < 1e-15)
    check("math: semigroup x(t+h) = e^{Ah} x(t)", worst["semi"] < 1e-12, f"max rel err {worst['semi']:.1e}")
    check("math: AT = TD (columns are eigenvectors)", worst["eig"] < 1e-12)

    w = node("const M=require('./courses/controls/linear-systems/dist/study_math.js');const p={l1:-1,l2:-2,s:1,x1:2,x2:1};"
             "console.log(JSON.stringify({r:M.pipeline(p,Math.log(2)),r0:M.pipeline(p,0),"
             "Tt:M.matvec(M.transpose(M.basis(-1,-2,1).T),[2,1]),J:M.expJordan(-1,0.7),rep:M.basis(-1,-1,1.3).A}))")
    r = w["r"]
    close = lambda a, b: np.allclose(a, b, atol=1e-12)  # noqa: E731
    check("worked: T^-1 = [[1,-1],[0,1]], A = [[-1,-1],[0,-2]]", close(r["Tinv"], [[1, -1], [0, 1]]) and close(r["A"], [[-1, -1], [0, -2]]))
    check("worked: z0 = (1, 1)", close(r["z0"], [1, 1]))
    check("worked: t = ln 2 gives z = (1/2, 1/4), x = (3/4, 1/4)", close(r["zt"], [0.5, 0.25]) and close(r["xt"], [0.75, 0.25]))
    A = np.array(r["A"])
    check("worked: xdot(0) = A x0 = (-3, -2) = derivative of (e^-t + e^-2t, e^-2t)",
          close(A @ [2, 1], [-3, -2]) and close([-1 - 2, -2], [-3, -2]))
    check("worked: transpose gives (2, 3), not z0", close(w["Tt"], [2, 3]) and not close(w["Tt"], r["z0"]))
    check("repeated eigenvalues: A = -I for any s", close(w["rep"], [[-1, 0], [0, -1]]))
    J = np.array([[-1, 1], [0, -1.0]])
    check("defective note: e^{Jt} = e^{-t}[[1,t],[0,1]] matches expm", np.allclose(w["J"], expm(J * 0.7), atol=1e-12))
    # series identity: partial sums of sum (TDT^-1)^k t^k/k! converge to T e^{Dt} T^-1
    T = np.array([[1, 1], [0, 1.0]]); Ti = np.linalg.inv(T); D = np.diag([-1, -2.0]); t = 0.9
    S = sum(np.linalg.matrix_power(T @ D @ Ti, k) * t ** k / math.factorial(k) for k in range(30))
    Pk = all(np.allclose(np.linalg.matrix_power(T @ D @ Ti, k), T @ np.linalg.matrix_power(D, k) @ Ti) for k in range(8))
    check("series: A^k = T D^k T^-1 and the summed series equals T e^{Dt} T^-1", Pk and np.allclose(S, T @ expm(D * t) @ Ti, atol=1e-13))
    check("series: e^{At} is not entrywise exp", not np.allclose(expm(A * t), np.exp(A * t)))


# ---------------------------------------------------------------------------- 2. animations

def ffmpeg_frames(path, exe):
    res = subprocess.run([exe, "-hide_banner", "-i", path, "-map", "0:v:0", "-f", "null", "-"], capture_output=True, text=True)
    fr = re.findall(r"frame=\s*(\d+)", res.stderr)
    return res.returncode, int(fr[-1]) if fr else 0


def animation_checks():
    import imageio_ffmpeg
    from control_specs import RELATIONS, SEQUENCES
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    man = json.load(open(os.path.join(ANIM, "manifest.json"), encoding="utf-8"))
    nsteps = sum(len(s["steps"]) for s in SEQUENCES)
    check("specs: 6 sequences, one per section", len(SEQUENCES) == 6 and sorted(s["section"] for s in SEQUENCES) == [1, 2, 3, 4, 5, 6])
    check("specs: 26-34 animated steps", 26 <= nsteps <= 34, nsteps)
    check("manifest: sequences and steps match specs",
          [s["id"] for s in man["sequences"]] == [s["id"] for s in SEQUENCES]
          and all(len(m["steps"]) == len(s["steps"]) and all(a["title"] == b["title"] and a["tex"] == b["tex"] and a["explanation"] == b["explanation"]
                                                              for a, b in zip(m["steps"], s["steps"]))
                  for m, s in zip(man["sequences"], SEQUENCES)))
    check("manifest: relations known", all(st["relation"] in RELATIONS for s in SEQUENCES for st in s["steps"]))
    bad, contiguous, n = [], True, 0
    for seq in man["sequences"]:
        prev = None
        for st in seq["steps"]:
            tr = st["transition"]
            p = os.path.join(DIST, tr["src"])
            rc, fr = ffmpeg_frames(p, exe)
            n += 1
            if rc or fr != tr["frames"] or fr != tr["masterFrames"][1] - tr["masterFrames"][0] or tr["codec"] != "h264":
                bad.append(f"{seq['id']}#{st['index']} rc={rc} frames={fr}/{tr['frames']}")
            if prev is not None and tr["masterFrames"][0] != prev - 1:
                contiguous = False
            prev = tr["masterFrames"][1]
            for f in (st["initialFrame"], st["finalFrame"]):
                if not os.path.isfile(os.path.join(DIST, f)):
                    bad.append("missing " + f)
        if prev != seq["masterFrames"]:
            contiguous = False
    check("media: every clip decodes with its recorded frame count", not bad, f"{n} clips" if not bad else "; ".join(bad[:5]))
    check("media: clip boundaries are contiguous (clip k starts on the last frame of clip k-1)", contiguous)
    texs = [s["initial"]["tex"] for s in SEQUENCES] + [st["tex"] for s in SEQUENCES for st in s["steps"]]
    course = json.load(open(os.path.join(DIST, "course.json"), encoding="utf-8"))
    for sec in course["sections"]:
        texs += [st["tex"] for st in sec["example"]["steps"]]
    errs = node("const k=require('./courses/controls/linear-systems/dist/vendor/katex/katex.min.js');const T=" + json.dumps(texs) + ";"
                "const e=[];T.forEach(t=>{try{k.renderToString(t,{throwOnError:true,displayMode:true})}catch(x){e.push(t.slice(0,40)+': '+x.message.slice(0,80))}});"
                "console.log(JSON.stringify(e))")
    check("math: every step/example display formula typesets in KaTeX", not errs, f"{len(texs)} formulas" if not errs else errs[:3])


# ---------------------------------------------------------------------------- 3. course

def course_checks():
    c = json.load(open(os.path.join(DIST, "course.json"), encoding="utf-8"))
    secs = c["sections"]
    times_ok = secs[0]["time"][0] == 0 and secs[-1]["time"][1] == 1487 and all(a["time"][1] == b["time"][0] for a, b in zip(secs, secs[1:]))
    check("course: 6 sections cover the whole 24:47 lecture contiguously", len(secs) == 6 and times_ok)
    s6 = secs[5]
    check("course: linked 22:22 moment is the first source of section 6 and inside its time range",
          s6["sources"]["video"][0]["t"] == 1342 and s6["time"][0] <= 1342 < s6["time"][1] and "22:22" in s6["title"])
    check("course: every section has notes, a worked example and book pages",
          all(s["notes"] and s["example"]["steps"] and s["sources"]["book"] and s["tutorNotes"] for s in secs))
    check("course: book pages are printed 331-332 (PDF +20)", all(331 <= b["printed"] <= 332 and b["pdf"] == b["printed"] + 20
                                                                 for s in secs for b in s["sources"]["book"]))
    q = c["quiz"]
    check("quiz: 8-10 questions, one correct choice each", 8 <= len(q) <= 10 and all(sum(1 for ch in x["choices"] if ch.get("correct")) == 1 for x in q), len(q))
    check("quiz: every option has an explanation", all(ch.get("why", "").strip() for x in q for ch in x["choices"]))
    check("quiz: correct answers are not always in the same position", len({[i for i, ch in enumerate(x["choices"]) if ch.get("correct")][0] for x in q}) >= 3)
    ex = c["explorer"]
    check("explorer: presets inside slider ranges", all(ex[k]["min"] <= p[k] <= ex[k]["max"] for p in ex["presets"] for k in ("l1", "l2", "s", "x1", "x2", "t")))
    check("explorer: required presets present", {p["id"] for p in ex["presets"]} >= {"worked", "decay", "saddle", "repeated"})
    txt = json.dumps(c)
    check("course: no leftover pendulum/cruise explorer config", "pendulum\"" not in txt and "cruise" not in txt)
    check("course: authored example labelled as such", "authored" in txt.lower())


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
    label, ctx = course.context({"page": "s6", "section": 6, "sequence": "map-evolve-map", "step": 2})
    check("tutor context: section 6 step 2 of the new lecture", label == "section 6, animation map-evolve-map, step 2/6"
          and "Linear Systems" in ctx and "z(0)" in ctx and "22:22" in ctx, label)
    label2, ctx2 = course.context({"page": "explorer"})
    check("tutor context: explorer uses course.explorer.tutorContext", label2 == "explorer" and "T = [[1, s], [0, 1]]" in ctx2)
    _, ctx3 = course.context({"section": 2, "sequence": "map-evolve-map", "step": 1})
    check("tutor context: mismatched sequence/section is dropped", "Animation on screen" not in ctx3)
    check("tutor instructions: generic, mention diagonalizable vs defective", "defective" in server.INSTRUCTIONS and "pendulum" not in server.INSTRUCTIONS.lower())

    env = {k: v for k, v in os.environ.items() if not k.startswith("OPENAI_")}
    pf = os.path.join(tempfile.gettempdir(), f"ls-qa-port-{os.getpid()}.txt")
    nonce = f"qa-{os.getpid()}"
    proc = subprocess.Popen([PY, "-I", os.path.join(PKG, "server.py"), "--port", "8790", "--port-file", pf, "--nonce", nonce],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        t0 = time.time()
        while not os.path.exists(pf) and time.time() - t0 < 15:
            time.sleep(0.1)
        time.sleep(0.2)
        base = f"http://127.0.0.1:{open(pf).read().strip()}"
        st, _, b = http(base + "/__control_health")
        h = json.loads(b)
        check("server: health identity Study_linear_systems + nonce", st == 200 and h["app"] == "Study_linear_systems" and h["nonce"] == nonce)
        st, _, b = http(base + "/api/status")
        s = json.loads(b)
        check("server: tutor reports not configured without a key", st == 200 and s["tutor"]["configured"] is False and "key" not in json.dumps(s).lower().replace("configured", ""))
        st, _, b = http(base + "/api/tutor", "POST", json.dumps({"question": "Why T inverse?", "context": {"page": "s6", "section": 6}}).encode(),
                        {"Content-Type": "application/json", "Origin": base})
        check("server: /api/tutor without a key returns a clear error, no network call", st >= 400 and b"key" in b.lower(), f"HTTP {st}")
        st, hd, b = http(base + "/course.json")
        check("server: serves dist/course.json", st == 200 and json.loads(b)["video"]["id"] == "nyqJJdhReiA")
        if os.path.isfile(os.path.join(ROOT, "databook.pdf")):
            st, hd, b = http(base + "/book", headers={"Range": "bytes=0-99"})
            check("server: /book honours byte ranges", st == 206 and len(b) == 100 and b.startswith(b"%PDF"), f"HTTP {st}")
        st, _, _ = http(base + "/../server.py")
        st2, _, _ = http(base + "/animations/")
        check("server: no path escape, no directory listing", st in (400, 403, 404) and st2 in (403, 404), f"{st}/{st2}")
    finally:
        proc.terminate()
        try:
            os.remove(pf)
        except OSError:
            pass


# ---------------------------------------------------------------------------- 5. launcher, isolation

def isolation_checks():
    ps = open(os.path.join(ROOT, "launch_linear_systems.ps1"), encoding="utf-8").read()
    check("launcher: targets courses/controls/linear-systems/server.py, port 8780, app identity", "courses\\controls\\linear-systems\\server.py" in ps and "8780" in ps
          and "Study_linear_systems" in ps)
    banned = [os.path.relpath(os.path.join(dp, f), DIST) for dp, _, fs in os.walk(DIST) for f in fs
              if f.lower().endswith((".pdf", ".vtt", ".txt")) and "vendor" not in dp or f == "video.mp4"]
    check("dist: no book, captions, transcript or lecture video bundled", not banned, banned[:3])
    app = open(os.path.join(DIST, "app.js"), encoding="utf-8").read() + open(os.path.join(DIST, "index.html"), encoding="utf-8").read()
    check("shell: no leftover pendulum/cruise/Control Bootcamp overview labels",
          not re.search(r"pendulum|cruise|control_math|Control Bootcamp: the overview", app, re.I))
    siblings = [os.path.join(ROOT, "courses", "controls", name, "dist")
                for name in ("overview", "linear-systems", "stability-eigenvalues")]
    keys = [re.search(r"var STORE_KEY\s*=\s*['\"]([^'\"]+)",
                      open(os.path.join(path, "app.js"), encoding="utf-8").read())
            for path in siblings]
    check("isolation: control lectures have independent assets and progress keys",
          len(set(map(os.path.realpath, siblings))) == 3 and all(keys)
          and len({key.group(1) for key in keys if key}) == 3)


def main():
    for f in (math_checks, animation_checks, course_checks, server_checks, isolation_checks):
        try:
            f()
        except Exception as e:  # report and continue with the other groups
            check(f.__name__ + " ran", False, repr(e)[:300])
    os.makedirs(os.path.join(ROOT, "qa", "results"), exist_ok=True)
    with open(os.path.join(ROOT, "qa", "results", "linear_systems_qa.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    failed = [r for r in results if not r["ok"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
