"""Contact sheet of the final state of every sequence of a package (review aid).

    python courses/mit-de/sheet.py <slug> <out.jpg>
"""
import glob
import sys
from PIL import Image

slug, out = sys.argv[1], sys.argv[2]
ims = []
for d in sorted(glob.glob(f"courses/mit-de/{slug}/dist/animations/*/")):
    f = sorted(glob.glob(d + "state-*.jpg"))[-1]
    ims.append(Image.open(f).resize((640, 360)))
W = Image.new("RGB", (1280, 360 * ((len(ims) + 1) // 2)))
for i, im in enumerate(ims):
    W.paste(im, ((i % 2) * 640, (i // 2) * 360))
W.save(out)
