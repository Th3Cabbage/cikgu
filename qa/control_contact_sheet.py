"""Tile every stable state still of each Control Bootcamp sequence into one image per sequence.

    .venv\\Scripts\\python.exe qa\\control_contact_sheet.py [--scale 0.5]

Writes qa/screenshots/control/sheet-<id>.jpg (ignored by Git) for visual review.
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(PROJECT, "control", "dist")
OUT = os.path.join(PROJECT, "qa", "screenshots", "control")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--cols", type=int, default=2)
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(DIST, "animations", "manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    for sq in man["sequences"]:
        if args.only and sq["id"] not in args.only:
            continue
        frames = [sq["initial"]["frame"]] + [s["finalFrame"] for s in sq["steps"]]
        w, h = int(1280 * args.scale), int(720 * args.scale)
        rows = (len(frames) + args.cols - 1) // args.cols
        sheet = Image.new("RGB", (w * args.cols, (h + 22) * rows), "white")
        d = ImageDraw.Draw(sheet)
        for i, fr in enumerate(frames):
            im = Image.open(os.path.join(DIST, fr)).convert("RGB").resize((w, h))
            x, y = (i % args.cols) * w, (i // args.cols) * (h + 22)
            sheet.paste(im, (x, y + 22))
            d.text((x + 6, y + 4), f"{sq['id']} state {i}", fill="black")
        path = os.path.join(OUT, f"sheet-{sq['id']}.jpg")
        sheet.save(path, quality=88)
        print(path)


if __name__ == "__main__":
    main()
