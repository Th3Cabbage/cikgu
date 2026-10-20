"""Reusable stable-state sheets: python tools/contact_sheets.py --package controllability [--only ID]."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',required=True); ap.add_argument('--only',nargs='+')
    a=ap.parse_args()
    pkg=(ROOT/a.package).resolve()
    if not pkg.exists(): pkg=(ROOT/'courses/controls'/a.package).resolve()
    if not pkg.is_relative_to(ROOT/'courses'): ap.error('Choose a package under courses/.')
    dist=pkg/'dist'
    out=ROOT/'qa/screenshots'/pkg.name; out.mkdir(parents=True,exist_ok=True)
    man=json.loads((dist/'animations/manifest.json').read_text(encoding='utf-8'))
    for seq in man['sequences']:
        if a.only and seq['id'] not in a.only: continue
        frames=[seq['initial']['frame']]+[s['finalFrame'] for s in seq['steps']]
        sheet=Image.new('RGB',(1280,((len(frames)+1)//2)*382),'white')
        draw=ImageDraw.Draw(sheet)
        for i,f in enumerate(frames):
            src=(dist/f).resolve()
            if not src.is_relative_to(dist.resolve()): raise ValueError('Unsafe frame path')
            with Image.open(src) as im: sheet.paste(im.resize((640,360)),((i%2)*640,(i//2)*382+22))
            draw.text(((i%2)*640+6,(i//2)*382+5),f"{seq['id']} state {i}",fill='black')
        path=out/f"sheet-{seq['id']}.jpg"; sheet.save(path,quality=85); print(path)


if __name__=='__main__': main()
