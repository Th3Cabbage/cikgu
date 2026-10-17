"""Download one lecture, de-duplicate rolling captions, extract selected PDF pages/keyframes.

All generated research stays under ignored sources/<slug>. Existing downloads and frames are
reused. Outputs: video.mp4, video.en.vtt, transcript.txt, transcript.json, source.json, book.txt,
frames/*.jpg. Book page arguments are 1-based PDF pages, not printed page numbers.
"""
import argparse
import html
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def seconds(stamp):
    parts = stamp.replace(',', '.').split(':')
    return sum(float(p) * 60**i for i, p in enumerate(reversed(parts)))


def mmss(t):
    return f'{int(t)//60:02}:{int(t)%60:02}'


def compact_captions(raw, rolling=True):
    cues = []
    for block in re.split(r'\n\s*\n', raw.replace('\r', '')):
        lines = block.splitlines()
        idx = next((i for i, line in enumerate(lines) if '-->' in line), None)
        if idx is None:
            continue
        left, right = lines[idx].split(' -->')
        start, end = seconds(left), seconds(right.strip().split()[0])
        words = html.unescape(re.sub(r'<[^>]*>', '', ' '.join(lines[idx+1:]))).split()
        if words:
            cues.append((start, end, words))
    buckets = {}
    previous = []
    previous_end = -1
    for start, end, words in cues:
        overlap = 0
        for n in range(min(len(previous), len(words)) if rolling and start <= previous_end + 0.15 else 0, 0, -1):
            if previous[-n:] == words[:n]:
                overlap = n
                break
        new = words[overlap:]
        if new:
            key = int(start // 30) * 30
            buckets.setdefault(key, []).extend(new)
        previous = words
        previous_end = end
    return [{'start': k, 'text': ' '.join(v)} for k, v in buckets.items()]


def page_numbers(spec):
    pages = set()
    for part in spec.split(','):
        if not part.strip():
            continue
        if not re.fullmatch(r'\d+(?:-\d+)?',part.strip()):
            raise ValueError('Use positive PDF page numbers, for example 351-352,354.')
        a, sep, b = part.strip().partition('-')
        if not a:
            continue
        start, end = int(a), int(b) if sep else int(a)
        if not 1 <= start <= end:
            raise ValueError('Book pages must be positive ascending PDF page ranges.')
        pages.update(range(start, end+1))
    return sorted(pages)


def transcribe(video, out):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        subprocess.run([sys.executable,'-m','pip','install','faster-whisper'],check=True)
        from faster_whisper import WhisperModel
    print('No YouTube captions: generating a local English transcript with Whisper base.en.', flush=True)
    import imageio_ffmpeg
    import numpy as np
    decoded=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(video),
                            '-vn','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True)
    audio=np.frombuffer(decoded.stdout,dtype=np.float32).copy()
    model = WhisperModel('base.en', device='cpu', compute_type='int8', cpu_threads=4)
    segments, _ = model.transcribe(audio,language='en',beam_size=3,vad_filter=True,
                                   initial_prompt='Linear systems, eigenvalues, eigenvectors, matrix exponential, state space, diagonalization, x dot equals A x.')
    rows=[]
    for segment in segments:
        rows.append({'start':segment.start,'end':segment.end,'text':segment.text.strip()})
        if len(rows)%50==0:
            print(f'Transcribed through {mmss(segment.end)}',flush=True)
    (out/'transcription.json').write_text(json.dumps(rows,ensure_ascii=False,indent=1),encoding='utf-8')
    def stamp(t):
        ms=round(t*1000)
        return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
    (out/'video.en-local.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(f"{stamp(r['start'])} --> {stamp(r['end'])}\n{r['text']}" for r in rows),encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--url', required=True)
    ap.add_argument('--slug', required=True)
    ap.add_argument('--book-pages', default='')
    ap.add_argument('--captions-only', action='store_true')
    ap.add_argument('--refresh', action='store_true')
    ap.add_argument('--transcribe', action='store_true', help='Generate local captions if YouTube has none (downloads Whisper once).')
    args = ap.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.slug):
        ap.error('Slug must contain lowercase words separated by hyphens.')
    url = urlsplit(args.url)
    if url.scheme != 'https' or url.hostname not in ('www.youtube.com','youtube.com','youtu.be','m.youtube.com'):
        ap.error('Use an https YouTube video URL.')
    query = parse_qs(url.query)
    vid = url.path.strip('/') if url.hostname == 'youtu.be' else query.get('v', [''])[0]
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid):
        ap.error('Could not identify a YouTube video ID.')
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = ROOT / 'sources' / args.slug
    out.mkdir(parents=True, exist_ok=True)
    existing_info = out/'video.info.json'
    if existing_info.is_file():
        existing = json.loads(existing_info.read_text(encoding='utf-8'))
        if existing.get('id') != vid:
            ap.error('This source slug belongs to a different video. Choose a new slug.')
    captions = sorted(out.glob('video.en*.vtt'))
    cached = (out/'video.info.json').is_file() and (captions or args.transcribe) and (args.captions_only or (out/'video.mp4').is_file())
    if args.refresh or not cached:
        cmd = [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--no-playlist', '--force-overwrites' if args.refresh else '--no-overwrites',
               '--js-runtimes', 'node', '--ffmpeg-location', ffmpeg, '--write-subs', '--write-auto-subs',
               '--sub-langs', 'en,en-orig', '--sub-format', 'vtt', '--write-info-json', '--write-description',
               '--socket-timeout', '30', '--retries', '3', '--no-progress',
               '-f', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/b[height<=1080]',
               '--merge-output-format', 'mp4', '-o', str(out/'video.%(ext)s')]
        if args.captions_only:
            cmd.append('--skip-download')
        result = subprocess.run(cmd + [f'https://www.youtube.com/watch?v={vid}'])
        if result.returncode:
            print('Retrying once after updating the isolated downloader to its latest prerelease.',flush=True)
            subprocess.run([sys.executable,'-m','pip','install','--pre','--upgrade','yt-dlp[default]'],check=True)
            subprocess.run(cmd + [f'https://www.youtube.com/watch?v={vid}'],check=True)
    else:
        print('Reusing cached source files.')
    info = json.loads((out/'video.info.json').read_text(encoding='utf-8'))
    captions = sorted(out.glob('video.en*.vtt'))
    if not captions and args.transcribe and (out/'video.mp4').is_file():
        transcribe(out/'video.mp4',out)
        captions=sorted(out.glob('video.en*.vtt'))
    if not captions:
        raise SystemExit('No English captions were available; download is saved but source review needs transcription.')
    cap = next((p for p in captions if p.name == 'video.en-orig.vtt'),
               next((p for p in captions if p.name == 'video.en.vtt'),captions[0]))
    transcript = compact_captions(cap.read_text(encoding='utf-8'),rolling='local' not in cap.name)
    (out/'transcript.json').write_text(json.dumps(transcript, ensure_ascii=False, indent=1), encoding='utf-8')
    (out/'transcript.txt').write_text('\n'.join(f"[{mmss(c['start'])}] {c['text']}" for c in transcript), encoding='utf-8')
    summary = {k: info.get(k) for k in ('id','title','channel','duration','width','height','description')}
    if (out/'video.mp4').is_file():
        probe=subprocess.run([ffmpeg,'-hide_banner','-i',str(out/'video.mp4')],capture_output=True,text=True)
        stream=next((line for line in probe.stderr.splitlines() if 'Video:' in line), '')
        resolution=re.search(r'\b(\d{2,5})x(\d{2,5})\b',stream)
        if resolution:
            summary.update(width=int(resolution[1]),height=int(resolution[2]))
    summary.update(url=f'https://www.youtube.com/watch?v={vid}', caption_file=cap.name,
                   caption_note=('Locally generated Whisper base.en captions, not YouTube captions. ' if 'local' in cap.name else '')+'Automatic captions may contain recognition errors; check equations against video/book.',
                   pdf_pages=page_numbers(args.book_pages))
    (out/'source.json').write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding='utf-8')
    if summary['pdf_pages']:
        import pymupdf
        with pymupdf.open(ROOT/'databook.pdf') as doc:
            if max(summary['pdf_pages']) > len(doc):
                ap.error('Book page exceeds PDF length.')
            text = '\n'.join(f'\n--- PDF PAGE {p}; PRINTED PAGE {doc[p-1].get_label()} ---\n'+doc[p-1].get_text()
                             for p in summary['pdf_pages'])
            (out/'book.txt').write_text(text, encoding='utf-8')
    frames = out/'frames'
    if (out/'video.mp4').is_file():
        frames.mkdir(exist_ok=True)
        times = set(range(30, int(info['duration']), 180))
        focus = query.get('t', [''])[0].rstrip('s')
        if focus.isdigit() and int(focus) < info['duration']:
            times.add(int(focus))
        for t in sorted(times):
            frame = frames/f'{t:04}.jpg'
            if not frame.exists() or args.refresh:
                subprocess.run([ffmpeg,'-v','error','-y','-ss',str(t),'-i',str(out/'video.mp4'),
                                '-frames:v','1','-update','1',str(frame)],check=True)
    print(json.dumps({'title':info['title'],'duration':info['duration'],'source_folder':str(out),
                      'transcript_words':sum(len(c['text'].split()) for c in transcript),
                      'transcript_segments':len(transcript),'keyframes':len(list(frames.glob('*.jpg'))),
                      'pdf_pages':summary['pdf_pages']},ensure_ascii=True))


if __name__ == '__main__':
    main()
