"""Media QA for the animated derivations in courses/ode/browser/dist/animations.

    .\\.venv\\Scripts\\python.exe qa\\media_qa.py        (from the repository root)

For every sequence and step in manifest.json:
- ffprobe: H.264 (High), yuv420p, 1280x720, 60 fps, BT.601 tags, frame count and duration as
  in the manifest, moov atom before mdat (fast start), duration 0.5-5 s.
- Boundaries: the last frame of clip k and the first frame of clip k+1 are the same master
  frame, so their decoded pixels must agree; still k must match the last frame of clip k.
- Motion: every clip really animates (frames change across the clip, not a single fade
  between two stills) and ends on a static hold (the stable final state).
- Stills are 1280x720 JPEGs.
Representative mid-transition frames and per-sequence contact sheets go to
qa/screenshots/browser-redo/frames; results to qa/results/browser-redo/media_results.json.
"""
import json
import os
import struct
import subprocess
import sys

import numpy as np
from PIL import Image

QA = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(QA)
DIST = os.path.join(PROJECT, "courses/ode/browser", "dist")
FRAMES = os.path.join(QA, "screenshots", "browser-redo", "frames")
RESULTS = os.path.join(QA, "results", "browser-redo")
os.makedirs(FRAMES, exist_ok=True)
os.makedirs(RESULTS, exist_ok=True)

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""))
    return ok


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_read_frames,duration,"
                          "color_space,color_primaries,color_transfer,color_range", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["streams"][0]


def top_level_atoms(path):
    names = []
    with open(path, "rb") as f:
        while True:
            head = f.read(8)
            if len(head) < 8:
                break
            size, name = struct.unpack(">I4s", head)
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
                f.seek(size - 16, 1)
            else:
                f.seek(size - 8, 1)
            names.append(name.decode("latin-1"))
            if size == 0:
                break
    return names


def frames(path, indices, w=1280, h=720):
    """Decode the given frame indices as RGB arrays (BT.601, limited range, like the stills)."""
    expr = "+".join(f"eq(n\\,{i})" for i in indices)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf",
                          f"select='{expr}',scale={w}:{h}:in_color_matrix=bt601:in_range=tv:out_range=pc,format=rgb24",
                          "-vsync", "0", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw, np.uint8)[: n * w * h * 3].reshape(n, h, w, 3).astype(np.int16)


def all_small(path, w=160, h=90):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.int16)


def mad(a, b):
    return float(np.abs(a - b).mean())


def main():
    man = json.load(open(os.path.join(DIST, "animations", "manifest.json"), encoding="utf-8"))
    seqs = man["sequences"]
    check("manifest: 9 sequences covering lessons 1-6", len(seqs) == 9 and sorted({s["lesson"] for s in seqs}) == [1, 2, 3, 4, 5, 6],
          ", ".join(s["id"] for s in seqs))
    course = json.load(open(os.path.join(DIST, "course.json"), encoding="utf-8"))
    ex_ids = sorted(e["id"] for e in course["examples"])
    check("manifest: every course worked example has an animated sequence",
          sorted(s["example"] for s in seqs if s.get("example")) == ex_ids, ex_ids)
    check("manifest: format 1280x720 at 60 fps", (man["width"], man["height"], man["fps"]) == (1280, 720, 60))

    stats = []
    total_bytes = 0
    for sq in seqs:
        sid = sq["id"]
        n = len(sq["steps"])
        problems = []
        last_frames = []
        motion = []
        mids = []
        for st in sq["steps"]:
            tr = st["transition"]
            path = os.path.join(DIST, tr["src"])
            if not os.path.exists(path):
                problems.append(f"missing {tr['src']}")
                continue
            total_bytes += os.path.getsize(path)
            p = probe(path)
            nf = int(p["nb_read_frames"])
            if (p["codec_name"], p["profile"], p["pix_fmt"], p["width"], p["height"], p["r_frame_rate"]) != \
               ("h264", "High", "yuv420p", 1280, 720, "60/1"):
                problems.append(f"step {st['index']} format {p}")
            if (p.get("color_space"), p.get("color_primaries"), p.get("color_transfer"), p.get("color_range")) != \
               ("smpte170m", "smpte170m", "smpte170m", "tv"):
                problems.append(f"step {st['index']} colour tags {p.get('color_space')}")
            if nf != tr["frames"] or abs(nf / 60 - tr["duration"]) > 1e-3:
                problems.append(f"step {st['index']} frames {nf} vs manifest {tr['frames']}/{tr['duration']}")
            if not 0.5 <= tr["duration"] <= 5.0:
                problems.append(f"step {st['index']} duration {tr['duration']}")
            atoms = top_level_atoms(path)
            if "moov" not in atoms or "mdat" not in atoms or atoms.index("moov") > atoms.index("mdat"):
                problems.append(f"step {st['index']} not fast-start {atoms}")
            for key in ("initialFrame", "finalFrame"):
                fp = os.path.join(DIST, st[key])
                if not os.path.exists(fp):
                    problems.append(f"missing {st[key]}")
                else:
                    with Image.open(fp) as im:
                        if im.size != (1280, 720) or im.format != "JPEG":
                            problems.append(f"{st[key]} is {im.format} {im.size}")
            ends = frames(path, [0, nf - 1])
            first, last = ends[0], ends[-1]
            # still k-1 vs first frame, still k vs last frame
            s0 = np.asarray(Image.open(os.path.join(DIST, st["initialFrame"])).convert("RGB"), np.int16)
            s1 = np.asarray(Image.open(os.path.join(DIST, st["finalFrame"])).convert("RGB"), np.int16)
            d_init, d_final = mad(s0, first), mad(s1, last)
            if d_init > 1.5 or d_final > 1.5:
                problems.append(f"step {st['index']} still/video mismatch {d_init:.2f}/{d_final:.2f}")
            if last_frames:
                d_join = mad(last_frames[-1], first)
                if d_join > 1.0:
                    problems.append(f"step {st['index']} boundary jump {d_join:.2f}")
            last_frames.append(last)
            small = all_small(path)
            diffs = np.abs(np.diff(small, axis=0)).mean(axis=(1, 2))
            moving = int((diffs > 0.02).sum())
            changed = float(np.abs(small[-1] - small[0]).mean())
            peak = float(np.abs(small - small[0]).mean(axis=(1, 2)).max())
            # Hold: the final 0.35 s (21 frames) plus the step into it, at full resolution. A visible
            # change is a pixel whose summed RGB difference exceeds 90 (about 30 per channel). Up to 300
            # such pixels are tolerated: sub-pixel re-rasterisation of a line when the final objects
            # are settled; a real pop (a box or term appearing/vanishing) is thousands.
            tail = frames(path, list(range(max(0, nf - 22), nf)))
            hold = int(max((np.abs(tail[i + 1] - tail[i]).sum(axis=2) > 90).sum() for i in range(len(tail) - 1)))
            motion.append({"step": st["index"], "frames": nf, "movingFrames": moving, "endChange": round(changed, 3),
                           "peakChange": round(peak, 3), "holdMaxChangedPixels": hold})
            if moving < 0.35 * 60:
                problems.append(f"step {st['index']} only {moving} moving frames")
            if peak < 0.5:
                problems.append(f"step {st['index']} barely changes (peak {peak:.2f})")
            if hold > 300:
                problems.append(f"step {st['index']} does not end on a static hold ({hold} pixels change)")
            mid = frames(path, [nf // 2])[0].astype(np.uint8)
            mp = os.path.join(FRAMES, f"{sid}-step{st['index']:02d}-mid.jpg")
            Image.fromarray(mid).save(mp, quality=88)
            mids.append(mp)
        # contact sheet of mid-transition frames
        thumbs = [Image.open(m).resize((480, 270)) for m in mids]
        cols = 3
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 486, rows * 276), (60, 60, 60))
        for i, t in enumerate(thumbs):
            sheet.paste(t, ((i % cols) * 486, (i // cols) * 276))
        sheet.save(os.path.join(FRAMES, f"{sid}-mid-transitions.jpg"), quality=85)
        check(f"{sid}: {n} clips are H.264 1280x720 60 fps, tagged, fast-start, frame-exact; boundaries and stills "
              "match; every clip animates and ends on a static hold", not problems, "; ".join(problems[:4]))
        stats.append({"sequence": sid, "steps": n, "motion": motion})

    stills = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(os.path.join(DIST, "animations"))
                 for f in fs if f.endswith(".jpg"))
    largest = max(st["transition"]["bytes"] for s in seqs for st in s["steps"])
    durs = [st["transition"]["duration"] for s in seqs for st in s["steps"]]
    check("media budget: clips + stills under 25 MB, no single clip over 600 kB",
          total_bytes + stills < 25e6 and largest < 600e3,
          f"clips {total_bytes / 1e6:.2f} MB, stills {stills / 1e6:.2f} MB, largest clip {largest / 1e3:.0f} kB, "
          f"durations {min(durs):.2f}-{max(durs):.2f} s (mean {sum(durs) / len(durs):.2f} s)")

    with open(os.path.join(RESULTS, "media_results.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results, "sequences": stats}, f, indent=1)
    failed = [r for r in results if not r["ok"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} media checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
