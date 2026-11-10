"""Add (or update) one MIT DE unit in site/catalog.json from courses/mit-de/units.json.

    python courses/mit-de/add_to_site.py <slug> "<one-sentence description>"
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
slug, desc = sys.argv[1], sys.argv[2]
units = json.loads((ROOT / "courses/mit-de/units.json").read_text(encoding="utf-8"))["units"]
unit = next(u for u in units if u["slug"] == slug)
cat_path = ROOT / "site/catalog.json"
cat = json.loads(cat_path.read_text(encoding="utf-8"))
course = next(c for c in cat["courses"] if c["id"] == "mit-de")
entry = {"slug": slug, "source": f"courses/mit-de/{slug}/dist", "title": f"Unit {unit['n']}: {unit['title']}",
         "description": desc, "storeKey": f"{slug}-v1", "statusApp": "Study_" + slug.replace("-", "_")}
lect = [l for l in course["lectures"] if l["slug"] != slug] + [entry]
order = {u["slug"]: u["n"] for u in units}
course["lectures"] = sorted(lect, key=lambda l: order[l["slug"]])
cat_path.write_text(json.dumps(cat, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"catalog: {len(course['lectures'])} MIT DE units")
