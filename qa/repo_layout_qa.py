r"""Check relocated course entrypoints and a fresh scaffold without rendering or opening windows.

Run from the repository root: .venv\Scripts\python.exe qa/repo_layout_qa.py
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
GIT=shutil.which('git') or str(Path(os.environ.get('ProgramFiles',r'C:\Program Files'))/'Git/cmd/git.exe')


def probe(path,code):
    script="import runpy;from pathlib import Path;d=runpy.run_path("+repr(str(ROOT/path))+",run_name='layout_probe');"+code
    r=subprocess.run([sys.executable,'-I','-c',script],cwd=ROOT,capture_output=True,text=True)
    assert r.returncode==0,(str(path),r.stderr[-1600:])


def main():
    catalog=json.loads((ROOT/'site/catalog.json').read_text(encoding='utf-8'))
    sources=[]
    for course in catalog['courses']:
        entries=course['lectures'] if course['kind']=='series' else [course]
        for entry in entries:
            sources.append(entry['source'])
            assert (ROOT/entry['source']/'course.json').is_file()
    assert 'courses/ode/browser/dist' in sources
    assert all(source.startswith(('courses/controls/','courses/ode/')) for source in sources)
    print(f'PASS catalog resolves the subject folders and all {len(sources)} guides')

    root_expr=repr(str(ROOT))
    for source in (source for source in sources if source.startswith('courses/controls/')):
        package=Path(source).parent
        name=package.name
        probe(package/'server.py',"assert Path(d['PROJECT'])==Path("+root_expr+");assert Path(d['BOOK'])==Path("+root_expr+")/'databook.pdf';d['Course']()")
        render='build_control.py' if name=='overview' else 'build_sequences.py'
        probe(package/'animation'/render,"assert Path(d['PROJECT'])==Path("+root_expr+");assert Path(d['VENV'])==Path("+root_expr+")/'.venv';assert Path(d['OUT']).is_dir()")
    probe(Path('courses/ode/animation/build_sequences.py'),"assert Path(d['REPO'])==Path("+root_expr+");assert Path(d['MANIMGL']).is_file();assert Path(d['DIST']).is_dir()")
    print('PASS all renderers find shared environments; control servers find root book and their own content')

    packages=[Path(source).parent for source in sources if source.startswith('courses/controls/')]
    packages.append(Path('courses/ode'))
    for package in packages:
        master=ROOT/package/'animation/masters/layout-probe.mp4'
        public=ROOT/package/('browser/dist' if package.name=='ode' else 'dist')/'animations/manifest.json'
        assert subprocess.run([GIT,'check-ignore','--no-index','-q',str(master)],cwd=ROOT).returncode==0,master
        assert subprocess.run([GIT,'check-ignore','--no-index','-q',str(public)],cwd=ROOT).returncode==1,public
    print('PASS all course master renders are ignored and public manifests remain versionable')

    launchers=['launch_browser.ps1']+[
        'launch_control.ps1' if package.name=='overview' else 'launch_'+package.name.replace('-','_')+'.ps1'
        for package in packages if package.name!='ode']
    for launcher in launchers:
        import re
        text=(ROOT/launcher).read_text(encoding='utf-8')
        target=re.search(r"\$server = Join-Path \$root '([^']+)'",text)[1]
        assert (ROOT/Path(target.replace('\\','/'))).is_file(),launcher
    assert (ROOT/'courses/ode/native/study_guide.py').is_file()
    assert (ROOT/'courses/ode/course.json').read_bytes()==(ROOT/'courses/ode/browser/dist/course.json').read_bytes()
    print('PASS existing launchers target moved servers; ODE course source matches viewing copy')

    # Build a fresh isolated scaffold using the actual generator. Never create a fake lecture in courses/.
    spec=importlib.util.spec_from_file_location('scaffold_layout',ROOT/'tools/scaffold_study.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    temp_base=Path(tempfile.gettempdir()).resolve()
    with tempfile.TemporaryDirectory(prefix='cikgu-layout-',dir=temp_base) as temp:
        work=Path(temp).resolve()
        assert work.parent==temp_base and work.name.startswith('cikgu-layout-')
        template=work/'courses/controls/overview'
        template.mkdir(parents=True)
        actual=ROOT/'courses/controls/overview'
        for name in ('.gitignore','requirements-render.txt','server.py'):
            shutil.copy2(actual/name,template/name)
        for directory in ('dist','animation'):
            shutil.copytree(actual/directory,template/directory,ignore=shutil.ignore_patterns('animations','masters','__pycache__'))
        shutil.copy2(ROOT/'launch_control.ps1',work/'launch_control.ps1')
        mature=work/'courses/controls/linearization/animation'
        mature.mkdir(parents=True)
        shutil.copy2(ROOT/'courses/controls/linearization/animation/build_sequences.py',mature/'build_sequences.py')
        mod.ROOT=work
        with patch.object(sys,'argv',['scaffold','--slug','fresh-lecture','--title','Fresh Lecture','--port','8810']):
            mod.main()
        generated=work/'courses/controls/fresh-lecture'
        assert (generated/'animation/ctl_common.py').is_file()
        assert (generated/'animation/build_sequences.py').is_file()
        build=(generated/'animation/build_sequences.py').read_text(encoding='utf-8')
        assert 'default=1' in build and '# first match: the input stream' in build
        text=(work/'launch_fresh_lecture.ps1').read_text(encoding='utf-8')
        assert 'courses\\controls\\fresh-lecture\\server.py' in text
        assert not (generated/'dist/animations').exists()
        assert '/animation/masters/' in (generated/'.gitignore').read_text(encoding='utf-8')
        assert (work/'courses/controls/overview/server.py').read_bytes()==(actual/'server.py').read_bytes()
    print('PASS scaffolder creates new control lectures under courses/controls with a working launcher path')


if __name__=='__main__':
    main()
