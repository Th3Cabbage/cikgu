"""Render the animated derivations with ManimGL and package them for the browser guide.

    ..\\.venv\\Scripts\\python.exe build_sequences.py [--only ID ...] [--force] [--no-render]

ManimGL is taken from the repo-local .venv, or from a sibling ..\\ManimGL\\.venv if the
repository has none (Windows only: Scripts\\manimgl.exe and the registry PATH below).

For every sequence in sequence_specs.SEQUENCES:
 1. Render the master video of its scene (sequence_scenes.py) offscreen at 1280x720, 60 fps,
    into courses/ode/animation/masters, unless the stored source stamp shows it is already current
    (--force always re-renders; --no-render never does). ManimGL also writes
    <Scene>.boundaries.json: the frame index where the opening still ends and where each
    step ends (after a short hold).
 2. Cut one clip per step at exact frame boundaries. Clip k covers master frames
    [b[k-1] - 1, b[k]): it starts on the last frame of the previous stable state and ends on
    the first fully settled frame of the new one, so playback never jumps.
 3. Extract the stable state stills: state 0 is the first frame of clip 1 and state k is the
    last frame of clip k (decoded from the clips themselves, with the same BT.601 matrix
    the clips are tagged with, so the still and the paused video match).
 4. Probe every clip with ffprobe and write courses/ode/browser/dist/animations/manifest.json with the
    ordered steps, their equations, explanations, frames and clip durations.

MiKTeX is found by re-reading the Machine and User PATH from the registry (this process only).
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import winreg

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PROJECT))
VENVS = [os.path.join(REPO, ".venv"), os.path.join(os.path.dirname(REPO), "ManimGL", ".venv")]
MANIMGL = next((exe for exe in (os.path.join(v, "Scripts", "manimgl.exe") for v in VENVS) if os.path.exists(exe)),
               os.path.join(VENVS[0], "Scripts", "manimgl.exe"))
SCENES_PY = os.path.join(HERE, "sequence_scenes.py")
SPECS_PY = os.path.join(HERE, "sequence_specs.py")
CONFIG = os.path.join(HERE, "render_config.yml")
MASTERS = os.path.join(HERE, "masters")
DIST = os.path.join(PROJECT, "browser", "dist")
OUT = os.path.join(DIST, "animations")
FPS = 60

sys.path.insert(0, HERE)
from sequence_specs import LESSON_SEQUENCES, RELATIONS, SEQUENCES  # noqa: E402

COLOR_TAGS = ["-colorspace", "smpte170m", "-color_primaries", "smpte170m", "-color_trc", "smpte170m",
              "-color_range", "tv"]


def registry_path():
    parts = []
    for root, key in ((winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                      (winreg.HKEY_CURRENT_USER, "Environment")):
        try:
            with winreg.OpenKey(root, key) as k:
                parts.append(os.path.expandvars(winreg.QueryValueEx(k, "Path")[0]))
        except OSError:
            pass
    return ";".join(parts)


def run(cmd, **kw):
    res = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if res.returncode != 0:
        raise RuntimeError(f"command failed ({res.returncode}): {' '.join(cmd)}\n{res.stderr[-3000:]}")
    return res


def stamp_for(scene):
    """Hash of everything that changes the pixels: the scene code, the render config and, from
    the specs, only what the scene reads (ids, step count, relation chips). Editing explanation
    text does not force a re-render."""
    h = hashlib.sha256()
    for p in (SCENES_PY, CONFIG):
        with open(p, "rb") as f:
            h.update(f.read())
    visual = [[q["id"], q["scene"], [st["relation"] for st in q["steps"]]] for q in SEQUENCES]
    h.update(json.dumps(visual).encode())
    h.update(scene.encode())
    return h.hexdigest()


def probe(path):
    res = run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
               "stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,avg_frame_rate,nb_read_frames,"
               "duration,color_space", "-of", "json", path])
    st = json.loads(res.stdout)["streams"][0]
    st["nb_read_frames"] = int(st["nb_read_frames"])
    st["duration"] = float(st.get("duration", 0))
    return st


def render_master(seq, env, force, no_render, log):
    scene = seq["scene"]
    master = os.path.join(MASTERS, scene + ".mp4")
    bfile = os.path.join(MASTERS, scene + ".boundaries.json")
    sfile = os.path.join(MASTERS, scene + ".stamp")
    stamp = stamp_for(scene)
    current = (os.path.exists(master) and os.path.exists(bfile) and os.path.exists(sfile)
               and open(sfile, encoding="ascii").read().strip() == stamp)
    if no_render or (current and not force):
        if not current:
            log(f"  WARNING {scene}: master is not current for this source (--no-render)")
        log(f"  {scene}: using existing master")
        return master, bfile, 0.0
    t0 = time.time()
    cmd = [MANIMGL, SCENES_PY, scene, "-w", "--config_file", CONFIG, "--video_dir", MASTERS]
    log(f"  {scene}: rendering ...")
    res = subprocess.run(cmd, cwd=HERE, env=env, capture_output=True, text=True)
    with open(os.path.join(MASTERS, scene + ".render.log"), "w", encoding="utf-8") as f:
        f.write(res.stdout + "\n--- stderr ---\n" + res.stderr)
    if res.returncode != 0 or not os.path.exists(bfile):
        raise RuntimeError(f"{scene} failed to render; see masters/{scene}.render.log\n{res.stderr[-2500:]}")
    with open(sfile, "w", encoding="ascii") as f:
        f.write(stamp)
    dt = time.time() - t0
    log(f"  {scene}: rendered in {dt:.1f}s")
    return master, bfile, dt


def cut(master, a, b, out):
    run(["ffmpeg", "-y", "-v", "error", "-i", master,
         "-vf", f"trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,"
                "setparams=colorspace=smpte170m:color_primaries=smpte170m:color_trc=smpte170m:range=tv",
         "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-g", "9999", *COLOR_TAGS, "-movflags", "+faststart", out])


def still(clip, index, out):
    run(["ffmpeg", "-y", "-v", "error", "-i", clip,
         "-vf", f"select=eq(n\\,{index}),scale=in_color_matrix=bt601:in_range=tv:out_range=pc,format=yuvj444p",
         "-frames:v", "1", "-q:v", "2", out])


def build_sequence(seq, env, args, log):
    sid = seq["id"]
    master, bfile, render_s = render_master(seq, env, args.force, args.no_render, log)
    with open(bfile, encoding="utf-8") as f:
        info = json.load(f)
    b = info["boundaries"]
    n = len(seq["steps"])
    if len(b) != n + 1:
        raise RuntimeError(f"{sid}: {len(b) - 1} recorded steps, spec has {n}")
    mp = probe(master)
    if mp["nb_read_frames"] != info["frames"]:
        raise RuntimeError(f"{sid}: master has {mp['nb_read_frames']} frames, scene emitted {info['frames']}")
    if b[-1] != info["frames"]:
        raise RuntimeError(f"{sid}: last boundary {b[-1]} is not the final frame count {info['frames']}")

    out_dir = os.path.join(OUT, sid)
    # Clear old outputs file by file (OneDrive can hold a lock on the folder itself).
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, name))
    rel = lambda name: f"animations/{sid}/{name}"  # noqa: E731

    steps = []
    for k in range(1, n + 1):
        a, e = b[k - 1] - 1, b[k]
        clip = os.path.join(out_dir, f"step-{k:02d}.mp4")
        cut(master, a, e, clip)
        p = probe(clip)
        if p["nb_read_frames"] != e - a:
            raise RuntimeError(f"{sid} step {k}: clip has {p['nb_read_frames']} frames, expected {e - a}")
        if k == 1:
            still(clip, 0, os.path.join(out_dir, "state-00.jpg"))
        still(clip, p["nb_read_frames"] - 1, os.path.join(out_dir, f"state-{k:02d}.jpg"))
        st = seq["steps"][k - 1]
        steps.append({
            "index": k,
            "title": st["title"],
            "relation": st["relation"],
            "relationLabel": RELATIONS[st["relation"]],
            "tex": st["tex"],
            "explanation": st["explanation"],
            "initialFrame": rel(f"state-{k - 1:02d}.jpg"),
            "finalFrame": rel(f"state-{k:02d}.jpg"),
            "transition": {
                "src": rel(f"step-{k:02d}.mp4"),
                "duration": round(p["nb_read_frames"] / FPS, 4),
                "frames": p["nb_read_frames"],
                "masterFrames": [a, e],
                "bytes": os.path.getsize(clip),
                "codec": p["codec_name"],
            },
            "layout": info.get("layout", [None] * (n + 1))[k],
        })
    entry = {
        "id": sid,
        "scene": seq["scene"],
        "lesson": seq["lesson"],
        "example": seq.get("example"),
        "title": seq["title"],
        "summary": seq["summary"],
        "initial": {**seq["initial"], "frame": rel("state-00.jpg")},
        "steps": steps,
        "totalDuration": round(sum(s["transition"]["duration"] for s in steps), 3),
        "masterFrames": info["frames"],
        "renderSeconds": round(render_s, 1),
    }
    log(f"  {sid}: {n} clips, {entry['totalDuration']:.2f}s of transitions")
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", help="sequence ids to rebuild (others are kept from the manifest)")
    ap.add_argument("--force", action="store_true", help="re-render masters even if current")
    ap.add_argument("--no-render", action="store_true", help="never render; only cut existing masters")
    args = ap.parse_args()

    os.makedirs(MASTERS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    env = dict(os.environ)
    env["PATH"] = registry_path() + ";" + env.get("PATH", "")
    if not shutil.which("latex", path=env["PATH"]):
        print("WARNING: latex not found on the registry PATH; Tex rendering will fail.")
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    manifest_path = os.path.join(OUT, "manifest.json")
    old = {}
    if args.only and os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            old = {s["id"]: s for s in json.load(f)["sequences"]}
    t0 = time.time()
    entries = []
    for seq in SEQUENCES:
        if args.only and seq["id"] not in args.only:
            if seq["id"] not in old:
                raise SystemExit(f"{seq['id']} is not in the existing manifest; build it too")
            entries.append(old[seq["id"]])
            continue
        log(f"[{seq['id']}]")
        entries.append(build_sequence(seq, env, args, log))

    manifest = {
        "version": 1,
        "width": 1280,
        "height": 720,
        "fps": FPS,
        "relations": RELATIONS,
        "lessons": {str(k): v for k, v in sorted(LESSON_SEQUENCES.items())},
        "sequences": entries,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    total = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fns in os.walk(OUT) for fn in fns)
    log(f"manifest: {len(entries)} sequences, {sum(len(e['steps']) for e in entries)} steps, "
        f"{total / 1e6:.2f} MB in dist/animations, built in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
