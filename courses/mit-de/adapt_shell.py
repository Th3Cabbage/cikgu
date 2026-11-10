"""Adapt a freshly scaffolded unit's player and server for the MIT Learn Differential Equations course.

    .venv\\Scripts\\python.exe courses\\mit-de\\adapt_shell.py <unit-slug>

Run once, after tools/scaffold_study.py --subject mit-de. Existing packages are not touched.
Changes (only inside courses/mit-de/<unit-slug>/):
- A unit spans several videos: course.json lists them in "videos" ({n, id, title, duration, url}),
  and every lecture source has "v" (the playlist video number) as well as "t" (seconds).
  Each section has "v" (its main video) and "time" (seconds within that video).
- Strang's book has no free online copy: the online-copy link appears only if book.onlineUrl is set.
- The local reference book is docs/DIFFER~1.pdf (ignored by Git), served only by the local server.
The script refuses to run twice (it checks for its marker).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MARK = "/* mit-de multi-video shell */"


def patch(path, pairs):
    s = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            raise SystemExit(f"{path.name}: expected one match for: {old[:70]!r}")
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    pkg = ROOT / "courses" / "mit-de" / sys.argv[1]
    app = pkg / "dist" / "app.js"
    if not app.is_file():
        raise SystemExit("Scaffold the unit first.")
    if MARK in app.read_text(encoding="utf-8"):
        raise SystemExit("Already adapted.")
    patch(app, [
        ('  function videoUrl(sec) { return course.video.url + "&t=" + Math.max(0, Math.floor(sec)) + "s"; }',
         '  ' + MARK + '\n'
         '  function videoOf(n) { for (var i = 0; i < course.videos.length; i++) if (course.videos[i].n === n) return course.videos[i]; return course.videos[0]; }\n'
         '  function videoUrl(sec, n) { return videoOf(n).url + "&t=" + Math.max(0, Math.floor(sec)) + "s"; }\n'
         '  function videoTag(v) { return "Video " + v.v + " · " + mmss(v.t); }'),
        ('''    parts.push(ext(course.book.onlineUrl + "#page=" + b.pdf, "online copy ↗", "Open the online copy of the book at PDF page " + b.pdf + " (new tab)"));
    return parts;''',
         '''    if (course.book.onlineUrl) parts.push(ext(course.book.onlineUrl + "#page=" + b.pdf, "online copy ↗", "Open the online copy of the book at PDF page " + b.pdf + " (new tab)"));
    else if (parts.length > 1) parts.pop();
    return parts;'''),
        ('''      return h("li", null, [ext(videoUrl(v.t), mmss(v.t), "Lecture at " + mmss(v.t) + ": " + v.label + " (YouTube, new tab)"), " ", v.label]);''',
         '''      return h("li", null, [ext(videoUrl(v.t, v.v), videoTag(v), videoOf(v.v).title + " at " + mmss(v.t) + ": " + v.label + " (YouTube, new tab)"), " ", v.label]);'''),
        ('''h("h3", { className: "small-note", text: "Book (Brunton & Kutz, Ch. 8)" })''',
         '''h("h3", { className: "small-note", text: "Book (" + course.book.short + ")" })'''),
        ('''      h("p", null, [ext(course.video.url, course.video.title + " ↗"), " · " + course.video.duration]),
      h("table", { className: "src-table" }, [h("thead", null, [h("tr", null, [h("th", { text: "Section" }), h("th", { text: "Time" }), h("th", { text: "Moment" })])]),''',
         '''      h("ul", { className: "sources-list" }, course.videos.map(function (v) {
        return h("li", null, [ext(v.url, "Video " + v.n + ": " + v.title + " ↗"), " · " + v.duration]);
      })),
      h("table", { className: "src-table" }, [h("thead", null, [h("tr", null, [h("th", { text: "Section" }), h("th", { text: "Video · time" }), h("th", { text: "Moment" })])]),'''),
        ('''                                   h("td", null, [ext(videoUrl(v.t), mmss(v.t), "Lecture at " + mmss(v.t) + " (YouTube, new tab)")]), h("td", { text: v.label })]);''',
         '''                                   h("td", null, [ext(videoUrl(v.t, v.v), videoTag(v), videoOf(v.v).title + " at " + mmss(v.t) + " (YouTube, new tab)")]), h("td", { text: v.label })]);'''),
        ('''h("span", { className: "sr-only", text: ", lecture " + mmss(sec.time[0]) + " to " + mmss(sec.time[1]) })''',
         '''h("span", { className: "sr-only", text: ", video " + sec.v + ", " + mmss(sec.time[0]) + " to " + mmss(sec.time[1]) })'''),
        ('''h("span", { className: "sec-time", "aria-hidden": "true", text: mmss(sec.time[0]) })''',
         '''h("span", { className: "sec-time", "aria-hidden": "true", text: "V" + sec.v })'''),
        ('''      h("p", { className: "eyebrow", text: "Section " + n + " of " + course.sections.length + " · lecture " +
               mmss(sec.time[0]) + "–" + mmss(sec.time[1]) }),''',
         '''      h("p", { className: "eyebrow", text: "Section " + n + " of " + course.sections.length + " · video " + sec.v + ", " +
               mmss(sec.time[0]) + "–" + mmss(sec.time[1]) }),'''),
        ('''      h("p", { className: "watch-link" }, [ext(videoUrl(sec.time[0]), "Watch this part of the lecture (" + mmss(sec.time[0]) + ") ↗",
                                               "Watch this part of the lecture on YouTube, from " + mmss(sec.time[0]) + " (opens a new tab)")])''',
         '''      h("p", { className: "watch-link" }, [ext(videoUrl(sec.time[0], sec.v), "Watch video " + sec.v + ": " + videoOf(sec.v).title + " ↗",
                                               "Watch video " + sec.v + " on YouTube, from " + mmss(sec.time[0]) + " (opens a new tab)")])'''),
        ('''(serverStatus && serverStatus.book && serverStatus.book.available ? " Local PDF links open your copy (databook.pdf) through the local server."
                                                                           : " No local copy is being served, so only the online links are shown.")''',
         '''(serverStatus && serverStatus.book && serverStatus.book.available ? " Local PDF links open your own copy through the local server."
                                                                           : " No local copy is being served, so only page numbers are shown.")'''),
    ])
    patch(pkg / "server.py", [
        ('BOOK = os.path.join(PROJECT, "databook.pdf")', 'BOOK = os.path.join(PROJECT, "docs", "DIFFER~1.pdf")  # local copy, never committed'),
        ('''               f"Lecture: {c['video']['title']} ({c['video']['duration']}). Book: {c['book']['authors']}, {c['book']['title']}, "''',
         '''               f"Lectures: " + "; ".join(f"video {v['n']} {v['title']} ({v['duration']})" for v in c['videos']) +
               f". Book: {c['book']['authors']}, {c['book']['title']}, "'''),
        ('''            out.append(f"\\nCurrent section {sec_n}: {s['title']} (lecture {_mmss(s['time'][0])}-{_mmss(s['time'][1])}).")''',
         '''            out.append(f"\\nCurrent section {sec_n}: {s['title']}.")'''),
        ('''"Sources: lecture moments " + "; ".join(f"{_mmss(v['t'])} {v['label']}" for v in s["sources"]["video"])''',
         '''"Sources: lecture moments " + "; ".join(f"video {v['v']} at {_mmss(v['t'])} {v['label']}" for v in s["sources"]["video"])'''),
        ('"No databook.pdf next to the control folder."', '"No local copy of the book (docs/DIFFER~1.pdf)."'),
        ("""'inline; filename="databook.pdf"'""", """'inline; filename="strang-de-la.pdf"'"""),
    ])
    print("adapted", pkg)


if __name__ == "__main__":
    main()
