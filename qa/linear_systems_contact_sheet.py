"""Contact sheets of every stable still of the Linear Systems animations (one sheet per sequence).

    .venv\Scripts\python.exe qa\linear_systems_contact_sheet.py
Writes qa/screenshots/linear-systems/sheet-<sequence>.jpg.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIM = os.path.join(ROOT, "courses/controls/linear-systems", "dist", "animations")
OUT = os.path.join(ROOT, "qa", "screenshots", "linear-systems")


def main():
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(os.path.join(ANIM, "manifest.json"), encoding="utf-8"))
    only = set(sys.argv[1:])
    for seq in man["sequences"]:
        if only and seq["id"] not in only:
            continue
        frames = [seq["initial"]["frame"]] + [s["finalFrame"] for s in seq["steps"]]
        w, h, cols = 640, 360, 2
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * (h + 22)), "white")
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(frames):
            im = Image.open(os.path.join(ANIM, "..", f)).resize((w, h))
            x, y = (i % cols) * w, (i // cols) * (h + 22)
            sheet.paste(im, (x, y + 22))
            d.text((x + 6, y + 5), f"state {i}", fill="black")
        p = os.path.join(OUT, f"sheet-{seq['id']}.jpg")
        sheet.save(p, quality=85)
        print(p)


if __name__ == "__main__":
    main()
