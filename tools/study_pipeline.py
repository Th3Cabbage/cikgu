"""Route a known playlist to a reusable recipe, with explicit resumable stages.

python tools/study_pipeline.py plan --url URL --slug SLUG --title TITLE --port 8820
python tools/study_pipeline.py prepare --slug SLUG
python tools/study_pipeline.py scaffold --slug SLUG
python tools/study_pipeline.py brief --slug SLUG
python tools/study_pipeline.py author --slug SLUG --name TASK --budget-usd 4
python tools/study_pipeline.py render --slug SLUG --only SEQUENCE
python tools/study_pipeline.py check --slug SLUG
python tools/study_pipeline.py status --slug SLUG

No model is called by planning, preparing, scaffolding, rendering or checking.
Book-page defaults are candidates that a reviewer must verify against this PDF.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]
PROFILES=json.loads((ROOT/'tools/study_profiles.json').read_text(encoding='utf-8'))


def route(url,title,subject=None,strategy=None):
    parts=urlsplit(url)
    if parts.scheme!='https' or parts.hostname not in ('youtube.com','www.youtube.com','m.youtube.com','youtu.be'):
        raise ValueError('Use an HTTPS YouTube video URL.')
    query=parse_qs(parts.query)
    vid=parts.path.strip('/') if parts.hostname=='youtu.be' else query.get('v',[''])[0]
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',vid):
        raise ValueError('A video ID is required.')
    playlist=query.get('list',[''])[0]
    inferred=next((k for k,v in PROFILES.items() if v['playlist']==playlist),None)
    if subject and inferred and subject!=inferred:
        raise ValueError('Subject conflicts with the registered playlist.')
    subject=subject or inferred
    if subject not in PROFILES:
        raise ValueError('Unknown playlist: choose a configured --subject; no keyword-only subject guessing.')
    recipes=PROFILES[subject]['strategies']
    if strategy is None:
        strategy=next((k for k,v in recipes.items() if any(w in title.lower() for w in v['keywords'])),'general')
    if strategy not in recipes:
        raise ValueError('Unknown strategy for this subject.')
    return dict(subject=subject,strategy=strategy,video_id=vid,playlist=playlist,
                url=f'https://www.youtube.com/watch?v={vid}',**recipes[strategy])


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def record_stage(checkpoint,stage,record):
    """Merge under a short lock so author/render/check processes cannot lose each other's state."""
    lock=checkpoint.with_suffix('.lock')
    for _ in range(100):
        try: lock.mkdir(); break
        except FileExistsError: time.sleep(0.05)
    else: raise RuntimeError('Checkpoint locked; inspect the process owning '+str(lock))
    try:
        latest=json.loads(checkpoint.read_text(encoding='utf-8'))
        latest.setdefault('stages',{})[stage]=record
        temp=checkpoint.with_suffix('.tmp');save(temp,latest);temp.replace(checkpoint)
    finally: lock.rmdir()


def execute(cmd,state,stage,checkpoint,extra=None):
    start=time.monotonic()
    print('Stage: '+stage,flush=True)
    record_stage(checkpoint,stage,dict(ok=False,running=True,**(extra or {})))
    proc=subprocess.run(cmd,cwd=ROOT)
    record_stage(checkpoint,stage,dict(ok=proc.returncode==0,seconds=round(time.monotonic()-start,1),**(extra or {})))
    if proc.returncode:
        raise SystemExit(proc.returncode)


def make_brief(plan):
    pkg=plan['package']; slug=plan['slug']
    return f'''# {plan['title']}: focused implementation

Read CLAUDE.md and .claude/skills/build-study-package/SKILL.md once. You are the implementer;
Codex reviews sources, mathematics, rendered output and shared browser integration.
Use a fresh session; do not launch other agents or Claude processes.

Package: {pkg}; video {plan['url']}; subject {plan['subject']}; strategy {plan['strategy']}.
Approach: {plan['approach']}

Read sources/{slug}/transcript.txt, sources/{slug}/book.txt if present, and
sources/{slug}/REVIEW.md (reviewed timestamps, source distinctions and corrections).
Do not read raw video.info.json, old BRIEF/HANDOVER logs or entire previous lesson implementations.
Read tools/README.md for contracts, ctl_common.py signatures and one relevant scene excerpt only.
The player/server/vendor/theme/render helper are already scaffolded: reuse them.

Author only course_source.py -> dist/course.json, animation/control_specs.py,
animation/sequence_scenes.py, dist/study_math.js, dist/explorer.js and a short package README.
Create source-backed sections covering the whole lecture, worked examples and 8-10 explanatory quiz
questions. Use the existing course schema and original paraphrases. Keep each animation operation
visible; use explicit safe stage bounds and split long formulas across rows. Aim for 5-6 sequences
of 3-5 clear operations when that covers the material; do not omit essential lecture topics.
The explorer needs validated saved state, immediate updates and correct edge cases.
Keep the mathematical core dependency-free and callable from Node for independent numerical QA.
Add a compact qa_cases.json with reference examples and the math export contract for review.

Do NOT render, run full browser suites, create duplicate QA harnesses, edit shared catalog/tools,
or commit/push. Codex handles these once. Run the content generator and basic syntax/math smoke
checks, then stop and report output paths, exports, assumptions and remaining concerns in <250 words.
Keep terminal output compact; avoid reading unchanged files repeatedly.
'''


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('stage',choices=['plan','prepare','scaffold','brief','author','preview','render','check','status'])
    ap.add_argument('--slug',required=True)
    ap.add_argument('--url'); ap.add_argument('--title'); ap.add_argument('--subject'); ap.add_argument('--strategy')
    ap.add_argument('--port',type=int,default=8820); ap.add_argument('--book-pages')
    ap.add_argument('--name'); ap.add_argument('--budget-usd',type=float,default=4)
    ap.add_argument('--effort',choices=['low','medium','high'],default='low',help='Authoring effort; independent math review remains required.')
    ap.add_argument('--only',nargs='+')
    a=ap.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a.slug):
        ap.error('Use a lowercase hyphenated slug.')
    if not math.isfinite(a.budget_usd) or a.budget_usd<=0:
        ap.error('Budget must be a positive finite number.')
    checkpoint=ROOT/'sources'/a.slug/'pipeline.json'
    if a.stage=='plan':
        if not a.url or not a.title: ap.error('plan requires --url and --title.')
        if not 1024<=a.port<=65000: ap.error('Invalid port.')
        try: plan=route(a.url,a.title,a.subject,a.strategy)
        except ValueError as e: ap.error(str(e))
        plan.update(slug=a.slug,title=a.title,port=a.port,package=f"courses/{plan['subject']}/{a.slug}")
        if a.book_pages is not None: plan['book_pages']=a.book_pages
        if checkpoint.exists():
            old=json.loads(checkpoint.read_text(encoding='utf-8'))
            if old['plan']!=plan: ap.error('Existing plan differs; use a new slug or review the checkpoint explicitly.')
            print(json.dumps(old,indent=2)); return
        existing=checkpoint.parent/'video.info.json'
        if existing.exists() and json.loads(existing.read_text(encoding='utf-8'))['id']!=plan['video_id']:
            ap.error('Source directory belongs to another video.')
        checkpoint.parent.mkdir(parents=True,exist_ok=True)
        save(checkpoint,dict(plan=plan,stages={}))
        print(json.dumps(plan,indent=2)); return
    if not checkpoint.exists(): ap.error('Run plan first.')
    state=json.loads(checkpoint.read_text(encoding='utf-8')); p=state['plan']; pkg=ROOT/p['package']
    py=sys.executable
    if a.stage=='status': print(json.dumps(state,indent=2)); return
    if a.stage=='prepare':
        cmd=['powershell','-NoProfile','-File',str(ROOT/'download_study.ps1'),'-Url',p['url'],'-Slug',a.slug,'-Transcribe']
        if p['book_pages']: cmd+=['-BookPages',p['book_pages']]
    elif a.stage=='scaffold':
        if pkg.exists():
            if state['stages'].get('scaffold',{}).get('ok'):
                print('Reusing scaffold; preserving authored files.'); return
            ap.error('Package already exists outside this checkpoint; refusing to overwrite it.')
        cmd=[py,'tools/scaffold_study.py','--slug',a.slug,'--subject',p['subject'],'--title',p['title'],'--port',str(p['port'])]
    elif a.stage=='brief':
        if not pkg.exists(): ap.error('Scaffold first.')
        brief=pkg/'BRIEF.md'
        if brief.exists(): ap.error('Brief already exists; preserving reviewed instructions.')
        brief.write_text(make_brief(p),encoding='utf-8')
        state['stages']['brief']={'ok':True}; save(checkpoint,state); print(brief); return
    elif a.stage=='author':
        if not a.name: ap.error('author requires a unique --name.')
        if state['stages'].get('author',{}).get('ok'):
            ap.error('Authoring is already complete. Review existing output; use the runner explicitly for a bounded revision.')
        if not (checkpoint.parent/'REVIEW.md').exists(): ap.error('Write the reviewed source capsule sources/<slug>/REVIEW.md first.')
        cmd=[py,'tools/run_claude.py',str(pkg/'BRIEF.md'),'--name',a.name,'--effort',a.effort,'--max-budget-usd',str(a.budget_usd)]
    elif a.stage=='preview':
        if not a.only or len(a.only)!=1: ap.error('preview requires --only ONE_SEQUENCE_ID.')
        cmd=[py,'tools/preview_study.py','--package',p['package'],'--sequence',a.only[0]]
    elif a.stage=='render':
        cmd=[py,str(pkg/'animation/build_sequences.py'),'--jobs','1']
        if a.only: cmd+=['--only',*a.only]
    else:
        cmd=[py,'tools/check_study.py','--package',p['package'],'--decode','--typeset']
    extra={'brief_sha256':hashlib.sha256((pkg/'BRIEF.md').read_bytes()).hexdigest(),'budget_usd':a.budget_usd,'effort':a.effort,'task':a.name} if a.stage=='author' else None
    execute(cmd,state,a.stage,checkpoint,extra)


if __name__=='__main__': main()
