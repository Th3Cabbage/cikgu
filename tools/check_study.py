"""Compact, reusable content/media audit. Run with the render environment.

python tools/check_study.py --package linear-systems [--decode]
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def audit(package,decode=False):
    dist=package/'dist'
    errors=[]
    def check(ok,msg):
        if not ok:
            errors.append(msg)
    course=json.loads((dist/'course.json').read_text(encoding='utf-8'))
    man=json.loads((dist/'animations/manifest.json').read_text(encoding='utf-8'))
    ids=[s['id'] for s in man['sequences']]
    check(len(ids)==len(set(ids)),'Duplicate animation IDs')
    n=len(course['sections'])
    check([s['number'] for s in course['sections']]==list(range(1,n+1)),'Section numbers must be consecutive')
    for sec in course['sections']:
        check(sec['id']==f"s{sec['number']}",f"Section route {sec['id']} does not match its number")
        check(sec['time'][0]<sec['time'][1],f"Invalid section time {sec['id']}")
        for v in sec['sources']['video']:
            check(v['t']>=0,f"Negative lecture timestamp in {sec['id']}")
        check(bool(sec['notes']) and bool(sec['example']['steps']),f"Missing teaching content {sec['id']}")
    for q in course['quiz']:
        check(sum(bool(c.get('correct')) for c in q['choices'])==1,f"Quiz {q['id']} must have one correct answer")
        check(all(c.get('why','').strip() for c in q['choices']),f"Quiz {q['id']} needs an explanation on every choice")
    clips=[]
    for seq in man['sequences']:
        check(1<=seq['section']<=n,f"Invalid section on {seq['id']}")
        paths=[seq['initial']['frame']]
        for i,step in enumerate(seq['steps'],1):
            check(step['index']==i,f"Wrong step index in {seq['id']}")
            paths.extend([step['initialFrame'],step['finalFrame'],step['transition']['src']])
            clips.append((seq['id'],i,step['transition']))
        for rel in paths:
            p=(dist/rel).resolve()
            check(p.is_relative_to(dist.resolve()) and p.is_file(),f'Missing/unsafe media path {rel}')
    ffmpeg=None
    if decode:
        import imageio_ffmpeg
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
        for sid,i,clip in clips:
            r=subprocess.run([ffmpeg,'-hide_banner','-i',str(dist/clip['src']),'-map','0:v:0','-f','null','-'],capture_output=True,text=True)
            frames=re.findall(r'frame=\s*(\d+)',r.stderr)
            check(r.returncode==0 and bool(frames) and int(frames[-1])==clip['frames'],f'Decode/frame-count failure {sid}/{i}')
    blocked=[str(p.relative_to(dist)) for p in dist.rglob('*') if p.suffix.lower() in ('.pdf','.vtt','.srt','.env','.py')]
    check(not blocked,'Non-web source files in dist: '+','.join(blocked))
    return {'package':package.name,'sections':n,'sequences':len(ids),'steps':len(clips),
            'quiz_questions':len(course['quiz']),'decoded':decode,'errors':errors}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',required=True)
    ap.add_argument('--decode',action='store_true')
    a=ap.parse_args()
    p=(ROOT/a.package).resolve()
    if not p.is_relative_to(ROOT) or p==ROOT:
        ap.error('Choose a package directory inside this repository.')
    try:
        result=audit(p,a.decode)
    except (OSError,KeyError,TypeError,ValueError) as e:
        result={'package':a.package,'errors':[str(e)]}
    print(json.dumps(result,ensure_ascii=True,indent=1))
    sys.exit(bool(result['errors']))


if __name__=='__main__':
    main()
