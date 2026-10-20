"""Media and content checks for courses/controls/overview/dist.

    .venv\\Scripts\\python.exe qa\\control_media_qa.py

 1. manifest.json agrees with courses/controls/overview/animation/control_specs.py (ids, sections, step titles,
    relations, formulas) and has 25-35 steps; every referenced clip and still exists.
 2. Every clip decodes with FFmpeg (bundled imageio-ffmpeg) to exactly the manifest's frame count,
    is H.264 1280x720 at 30 fps, and its frames are contiguous in the master (clip k ends on frame
    b[k]-1, clip k+1 starts on the same frame).
 3. Boundary agreement: still k matches the last frame of clip k and the first frame of clip k+1
    (mean absolute difference after JPEG round trip), so Next / Back never jump.
 4. Each step actually animates (first and last frame of a clip differ).
 5. Distribution audit: only expected file types; no PDF, captions, transcript, chapter text or
    video download in dist; no 10-word run of the book chapter or lecture transcript copied into
    course.json, manifest.json or the specs.
Writes qa/results/control_media_qa.json.
"""
import io
import json
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(PROJECT, "courses/controls/overview", "dist")
SRC = os.path.join(PROJECT, "sources", "control-bootcamp-overview")
sys.path.insert(0, os.path.join(PROJECT, "courses/controls/overview", "animation"))
from control_specs import SEQUENCES  # noqa: E402

import imageio_ffmpeg  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"check": name, "ok": bool(ok), "detail": str(detail)[:400]})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{str(detail)[:200]}]" if detail != "" else ""))
    return ok


def decode_info(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path, "-map", "0:v:0", "-f", "null", "-"], capture_output=True, text=True)
    frames = [int(x) for x in re.findall(r"frame=\s*(\d+)", r.stderr)]
    stream = re.search(r"Stream #0:0[^\n]*Video: ([^\n]*)", r.stderr)
    return r.returncode, (frames[-1] if frames else 0), (stream.group(1) if stream else "")


def frame_rgb(path, index):
    r = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-vf",
                        f"select=eq(n\\,{index}),scale=in_color_matrix=bt601:in_range=tv:out_range=pc,format=rgb24",
                        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    return np.asarray(Image.open(io.BytesIO(r.stdout)).convert("RGB"), dtype=np.float32)


def still_rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def words(text):
    return re.findall(r"[a-z]+", text.lower())


def main():
    man = json.load(open(os.path.join(DIST, "animations", "manifest.json"), encoding="utf-8"))
    seqs = man["sequences"]
    check("manifest: 1280x720 at 30 fps", (man["width"], man["height"], man["fps"]) == (1280, 720, 30))
    check("manifest sequences match specs (ids, order)", [s["id"] for s in seqs] == [s["id"] for s in SEQUENCES])
    total = sum(len(s["steps"]) for s in seqs)
    check("25-35 animated steps in total", 25 <= total <= 35, total)
    check("every section 1-6 has at least one animation", sorted(man["sections"]) == [str(i) for i in range(1, 7)], man["sections"])
    spec_by = {s["id"]: s for s in SEQUENCES}
    mism = []
    for s in seqs:
        sp = spec_by[s["id"]]
        if s["section"] != sp["section"] or len(s["steps"]) != len(sp["steps"]):
            mism.append(s["id"])
        for a, b in zip(s["steps"], sp["steps"]):
            if (a["title"], a["relation"], a["tex"], a["explanation"]) != (b["title"], b["relation"], b["tex"], b["explanation"]):
                mism.append(f"{s['id']}:{a['index']}")
    check("manifest step text is current with control_specs.py", not mism, mism[:5])

    bad_decode, bad_meta, bad_contig, bad_bound, static_steps = [], [], [], [], []
    worst = 0.0
    for s in seqs:
        prev_end = None
        for st in s["steps"]:
            clip = os.path.join(DIST, st["transition"]["src"])
            if not os.path.isfile(clip):
                bad_decode.append(st["transition"]["src"] + " missing")
                continue
            rc, n, stream = decode_info(clip)
            if rc != 0 or n != st["transition"]["frames"]:
                bad_decode.append(f"{st['transition']['src']} rc={rc} frames={n}/{st['transition']['frames']}")
            if not ("h264" in stream and "1280x720" in stream and "30 fps" in stream and "yuv420p" in stream):
                bad_meta.append(f"{st['transition']['src']}: {stream[:80]}")
            a, b = st["transition"]["masterFrames"]
            if b - a != n or (prev_end is not None and a != prev_end - 1):
                bad_contig.append(f"{s['id']}:{st['index']}")
            prev_end = b
            first, last = frame_rgb(clip, 0), frame_rgb(clip, n - 1)
            for still, frame, where in ((st["initialFrame"], first, "start"), (st["finalFrame"], last, "end")):
                p = os.path.join(DIST, still)
                if not os.path.isfile(p):
                    bad_bound.append(f"{still} missing")
                    continue
                im = still_rgb(p)
                if im.shape != (720, 1280, 3):
                    bad_bound.append(f"{still} shape {im.shape}")
                    continue
                d = float(np.mean(np.abs(im - frame)))
                worst = max(worst, d)
                if d > 2.0:
                    bad_bound.append(f"{s['id']}:{st['index']} {where} mad={d:.2f}")
            if float(np.mean(np.abs(first - last))) < 0.5:
                static_steps.append(f"{s['id']}:{st['index']}")
    check(f"all {total} clips decode to the manifest frame count", not bad_decode, bad_decode[:4])
    check("clips are H.264 yuv420p 1280x720 30 fps", not bad_meta, bad_meta[:3])
    check("clips are contiguous master ranges sharing their boundary frame", not bad_contig, bad_contig[:4])
    check("stills match clip first/last frames (no jump at Next/Back)", not bad_bound, f"worst MAD {worst:.2f}/255; {bad_bound[:3]}")
    check("every step changes the picture (no empty steps)", not static_steps, static_steps)
    mp4_bytes = sum(st["transition"]["bytes"] for s in seqs for st in s["steps"])
    check("animation clips total under 15 MB", mp4_bytes < 15e6, f"{mp4_bytes / 1e6:.2f} MB")

    # ---------------------------------------------------------------- distribution audit
    allowed = {".html", ".css", ".js", ".json", ".svg", ".jpg", ".mp4", ".woff2", ".woff", ".ttf", ".txt", ""}
    unexpected, forbidden = [], []
    for dp, _, fns in os.walk(DIST):
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), DIST).replace("\\", "/")
            ext = os.path.splitext(fn)[1].lower()
            if ext not in allowed:
                unexpected.append(rel)
            if ext in (".pdf", ".vtt", ".srt") or re.search(r"transcript|chapter8|overview\.(mp4|info)|databook", fn, re.I):
                forbidden.append(rel)
            if ext == ".txt" and not rel.startswith("vendor/katex/"):
                forbidden.append(rel)
            if ext == "" and not rel.startswith("vendor/katex/"):
                unexpected.append(rel)
    check("dist holds only web assets", not unexpected, unexpected[:5])
    check("no PDF, captions, transcript, chapter text or lecture video in dist", not forbidden, forbidden[:5])

    texts = {"course.json": open(os.path.join(DIST, "course.json"), encoding="utf-8").read(),
             "manifest.json": open(os.path.join(DIST, "animations", "manifest.json"), encoding="utf-8").read(),
             "app.js": open(os.path.join(DIST, "app.js"), encoding="utf-8").read(),
             "control_specs.py": open(os.path.join(PROJECT, "courses/controls/overview", "animation", "control_specs.py"), encoding="utf-8").read()}
    for src_name in ("chapter8.txt", "transcript.txt"):
        p = os.path.join(SRC, src_name)
        if not os.path.isfile(p):
            check(f"copy audit vs {src_name}", True, "source not present locally; skipped")
            continue
        raw = open(p, encoding="utf-8", errors="replace").read()
        if src_name == "transcript.txt":
            raw = re.sub(r"\[\d\d:\d\d:\d\d\.\d+\]", " ", raw)
        sw = words(raw)
        N = 10
        grams = {" ".join(sw[i:i + N]) for i in range(len(sw) - N + 1)}
        hits = []
        for name, t in texts.items():
            tw = words(t)
            for i in range(len(tw) - N + 1):
                g = " ".join(tw[i:i + N])
                # prose only: a run of math symbols (d dt x x g l ...) is not copied wording
                if g in grams and sum(len(w) >= 3 for w in tw[i:i + N]) >= 6:
                    hits.append(f"{name}: '{g}'")
                    break
        check(f"no 10-word run copied from {src_name}", not hits, hits[:3])

    os.makedirs(os.path.join(PROJECT, "qa", "results"), exist_ok=True)
    with open(os.path.join(PROJECT, "qa", "results", "control_media_qa.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=1)
    bad = sum(not r["ok"] for r in RESULTS)
    print(f"\n{len(RESULTS) - bad} passed, {bad} failed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
