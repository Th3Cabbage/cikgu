"""Run Claude with a focused file brief, retain raw logs, print only compact progress.

python tools/run_claude.py path/to/brief.md --name linear-systems
python tools/run_claude.py --status linear-systems
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
LOGS=ROOT/'qa/scratch'


def events(path):
    if not path.exists():
        return []
    out=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def summary(rows):
    changes=[]
    messages=[]
    result=next((r for r in reversed(rows) if r.get('type')=='result'),None)
    for r in rows:
        msg=r.get('message')
        if not isinstance(msg,dict):
            continue
        for c in msg.get('content',[]):
            if not isinstance(c,dict):
                continue
            if c.get('type')=='tool_use' and c.get('name') in ('Write','Edit'):
                p=c.get('input',{}).get('file_path','')
                if p and p not in changes:
                    changes.append(p)
            if c.get('type')=='text':
                messages.append(c.get('text',''))
    return {'session_id':next((r.get('session_id') for r in rows if r.get('session_id')),None),
            'state':result.get('terminal_reason','finished') if result else 'running',
            'changed_files':changes,'latest_messages':messages[-2:],
            'result':result.get('result') if result else None,
            'model_usage':result.get('modelUsage') if result else None}


def main():
    # Windows shells may default to cp1252, which cannot print mathematical symbols.
    # Reconfigure the runner itself, not only the child's environment.
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    sys.stderr.reconfigure(encoding='utf-8',errors='replace')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('prompt',nargs='?')
    ap.add_argument('--name')
    ap.add_argument('--status')
    ap.add_argument('--resume')
    ap.add_argument('--model',default='claude-opus-5-5')
    ap.add_argument('--effort',default='medium',choices=['low','medium','high'])
    a=ap.parse_args()
    name=a.status or a.name
    if not name or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*',name):
        ap.error('Use a simple task name containing letters, digits, hyphens or underscores.')
    logfile=LOGS/f'claude-{name}.jsonl'
    if a.status:
        print(json.dumps(summary(events(logfile)),ensure_ascii=True,indent=1))
        return
    if not a.prompt:
        ap.error('Provide a prompt file.')
    found=shutil.which('claude')
    if not found:
        choices=list((Path.home()/'.vscode/extensions').glob('anthropic.claude-code-*/resources/native-binary/claude.exe'))
        choices.sort(key=lambda p:tuple(map(int,re.search(r'claude-code-(\d+)\.(\d+)\.(\d+)',str(p)).groups())),reverse=True)
        found=str(choices[0]) if choices else None
    if not found:
        raise SystemExit('Claude Code not found; install/sign in before running the handoff.')
    prompt=Path(a.prompt).read_text(encoding='utf-8')
    LOGS.mkdir(parents=True,exist_ok=True)
    if logfile.exists():
        raise SystemExit('Task log already exists. Use a new --name and --resume SESSION_ID to continue safely.')
    env=dict(os.environ,PYTHONIOENCODING='utf-8',CLAUDE_CODE_GIT_BASH_PATH=r'C:\Program Files\Git\bin\bash.exe')
    env['PATH']=r'C:\Program Files\Git\cmd;'+str(ROOT/'.venv/Scripts')+';'+env['PATH']
    cmd=[found,'-p','--model',a.model,'--effort',a.effort,'--safe-mode','--strict-mcp-config',
         '--output-format','stream-json','--verbose','--permission-mode','acceptEdits',
         '--allowedTools','Read,Write,Edit,Glob,Grep,Bash,PowerShell']
    if a.resume:
        cmd.extend(['--resume',a.resume])
    with logfile.open('w',encoding='utf-8') as raw, (LOGS/f'claude-{name}.stderr.log').open('w',encoding='utf-8') as err:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf-8')
        proc.stdin.write(prompt)
        proc.stdin.close()
        for line in proc.stdout:
            raw.write(line)
            raw.flush()
            try:
                e=json.loads(line)
            except ValueError:
                continue
            msg=e.get('message')
            if e.get('type')=='assistant' and isinstance(msg,dict):
                for c in msg.get('content',[]):
                    if c.get('type')=='text':
                        print('Claude: '+c.get('text','')[:300].replace('\n',' '),flush=True)
                    elif c.get('type')=='tool_use' and c.get('name') in ('Write','Edit'):
                        print(c['name']+': '+c.get('input',{}).get('file_path',''),flush=True)
        code=proc.wait()
    (LOGS/f'claude-{name}.summary.json').write_text(json.dumps(summary(events(logfile)),ensure_ascii=False,indent=1),encoding='utf-8')
    print('Claude finished; exit '+str(code)+'. Summary: qa/scratch/claude-'+name+'.summary.json',flush=True)
    sys.exit(code)


if __name__=='__main__':
    main()
