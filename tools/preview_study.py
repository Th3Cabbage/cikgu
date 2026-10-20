"""Render and inspect one scene before the first full build, reusing its master later.

python tools/preview_study.py --package controllability --sequence coupled
Writes only that sequence's media and an ignored sheet; does not publish a partial manifest.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',required=True); ap.add_argument('--sequence',required=True)
    a=ap.parse_args();pkg=(ROOT/a.package).resolve()
    if not pkg.exists(): pkg=(ROOT/'courses/controls'/a.package).resolve()
    if not pkg.is_relative_to(ROOT/'courses'): ap.error('Choose a package under courses/.')
    sys.path.insert(0,str(pkg/'animation'))
    spec=importlib.util.spec_from_file_location('preview_renderer',pkg/'animation/build_sequences.py')
    d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
    seq=next((s for s in d.SEQUENCES if s['id']==a.sequence),None)
    if not seq: ap.error('Unknown sequence.')
    d.FFMPEG=d.ffmpeg_exe();d.write_config();os.makedirs(d.OUT,exist_ok=True)
    env=dict(os.environ,PATH=os.path.dirname(d.FFMPEG)+os.pathsep+os.environ.get('PATH',''),PYTHONWARNINGS='ignore')
    entry=d.package(seq,*d.render_master(seq,env,False,False,print),print)
    out=ROOT/'qa/screenshots'/pkg.name;out.mkdir(parents=True,exist_ok=True)
    frames=[entry['initial']['frame']]+[s['finalFrame'] for s in entry['steps']]
    sheet=Image.new('RGB',(1280,((len(frames)+1)//2)*382),'white');draw=ImageDraw.Draw(sheet)
    for i,rel in enumerate(frames):
        with Image.open(pkg/'dist'/rel) as im: sheet.paste(im.resize((640,360)),((i%2)*640,(i//2)*382+22))
        draw.text(((i%2)*640+6,(i//2)*382+5),f'{a.sequence} state {i}',fill='black')
    target=out/f'preview-{a.sequence}.jpg';sheet.save(target,quality=85)
    print(json.dumps({'preview':str(target),'master_reused_by_full_build':True}))


if __name__=='__main__': main()
