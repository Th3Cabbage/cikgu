"""Targeted review check: the native lesson screens whose shared text changed in the review.

Run from the repository root with MiKTeX on PATH:
    .\\.venv\\Scripts\\python.exe qa\\review_affected_native.py
Builds only the affected pages with the real scene layout (offscreen, no window), checks
TeX compiles, everything stays in the content area at full scale, and saves previews.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.argv = ["manimgl", "-w", "-r", "1280x720", "--video_dir", os.path.join(HERE, "scratch", "native_out")]
sys.path.insert(0, os.path.join(PROJECT, "courses/ode/native"))
for d in ("screenshots", "results"):
    os.makedirs(os.path.join(HERE, d), exist_ok=True)
from manimlib import *  # noqa: E402,F403
import study_guide as SG  # noqa: E402

AFFECTED = [(1, 3), (1, 4), (4, 1), (4, 3), (5, 3)]  # (lesson index, page index), 0-based
PREVIEW = {(1, 3): "review_native_lesson2_complex", (4, 1): "review_native_lesson5_damping"}

scene = SG.SecondOrderStudyGuide()
scene.setup()
scene.construct()
results = []
for target in AFFECTED:
    pos = scene.flat_pages.index(target)
    screens = scene.build_screens(pos)
    for si, screen in enumerate(screens):
        parts = VGroup(screen.static, *(screen.example.rows if screen.example else []))
        l, r = parts.get_left()[0], parts.get_right()[0]
        b, t = parts.get_bottom()[1], parts.get_top()[1]
        ok = (l >= SG.CONTENT_LEFT - 0.02 and r <= SG.CONTENT_RIGHT + 0.02 and b >= SG.CONTENT_BOTTOM - 0.02
              and t <= 3.3 and screen.scale >= 0.999)
        results.append({"page": f"L{target[0] + 1}.{target[1] + 1}", "screen": f"{si + 1}/{len(screens)}",
                        "ok": bool(ok), "scale": round(screen.scale, 3),
                        "bbox": [round(l, 2), round(r, 2), round(b, 2), round(t, 2)]})
    if target in PREVIEW:
        scene.page_pos, scene.screen_idx = pos, 0
        scene.show_screen()
        scene.update_frame(dt=0, force_draw=True)
        scene.get_image().convert("RGB").save(os.path.join(HERE, "screenshots", PREVIEW[target] + ".png"))
for r in results:
    print(("PASS " if r["ok"] else "FAIL ") + f"{r['page']} screen {r['screen']} scale {r['scale']} bbox {r['bbox']}")
tex_ok = not scene.tex_errors
print(("PASS " if tex_ok else "FAIL ") + "no TeX compile errors", scene.tex_errors[:2])
with open(os.path.join(HERE, "results", "review_affected_native.json"), "w", encoding="utf-8") as f:
    json.dump({"screens": results, "tex_errors": scene.tex_errors}, f, indent=2)
failed = sum(not r["ok"] for r in results) + (0 if tex_ok else 1)
print(f"\n{len(results) + 1 - failed}/{len(results) + 1} affected-page native checks passed")
sys.exit(1 if failed else 0)
