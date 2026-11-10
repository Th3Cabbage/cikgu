"""Prepare cached sources for every video of a multi-video unit (or all units).

python tools/prepare_unit.py --units courses/mit-de/units.json            # all units
python tools/prepare_unit.py --units courses/mit-de/units.json --unit 3   # one unit

Each video goes to sources/<source_slug>/ through prepare_study.py with 720p downloads,
a frame every 60 s, and deletion of the video after its frames are saved. The unit's book pages
are extracted once, into the first video's folder. Existing caches are reused. Run with the
.venv-download Python (yt-dlp, imageio-ffmpeg, pymupdf).
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--units', required=True, help='Repository-relative units.json')
    ap.add_argument('--unit', type=int, help='Prepare only this unit number.')
    ap.add_argument('--max-height', type=int, default=720)
    ap.add_argument('--frame-every', type=int, default=60)
    ap.add_argument('--pause', type=float, default=45, help='Seconds to wait after each new download (avoids YouTube HTTP 429).')
    ap.add_argument('--cookies-from-browser', metavar='BROWSER', help='Pass a browser sign-in to yt-dlp (see prepare_study.py).')
    a = ap.parse_args()
    spec = json.loads((ROOT/a.units).read_text(encoding='utf-8'))
    units = [u for u in spec['units'] if a.unit in (None, u['n'])]
    if not units:
        ap.error('No such unit.')
    failed = []
    for unit in units:
        for k, video in enumerate(unit['videos']):
            cmd = [sys.executable, str(ROOT/'tools/prepare_study.py'), '--url', f"https://www.youtube.com/watch?v={video['id']}",
                   '--slug', video['source_slug'], '--max-height', str(a.max_height),
                   '--frame-every', str(a.frame_every), '--drop-video', '--book', spec['book']]
            if a.cookies_from_browser:
                cmd += ['--cookies-from-browser', a.cookies_from_browser]
            if k == 0 and unit.get('book_pages'):
                cmd += ['--book-pages', unit['book_pages']]
            done = (ROOT/'sources'/video['source_slug']/'transcript.txt').is_file()
            print(f"Unit {unit['n']} video {video['n']}: {video['title']}" + (' (cached)' if done else ''), flush=True)
            if subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL).returncode:
                failed.append(video['n'])
            if not done:
                time.sleep(a.pause)
    print(json.dumps({'units': [u['n'] for u in units], 'failed_videos': failed}))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
