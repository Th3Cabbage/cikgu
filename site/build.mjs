// Build the unified Cikgu study website into site/dist (Node.js built-ins only, no dependencies).
//
//   node build.mjs            (run from site/, as Netlify does; or `node site/build.mjs` from the root)
//
// site/catalog.json lists the courses. Each lecture's existing package dist/ is copied byte-for-byte,
// except its index.html, which gets the shared course bar. The home page, the Control Bootcamp course
// page, a static "no chat server" api/status per lecture and the shared assets are generated here.
// Counts shown to students come from each package's course.json and animation manifest.
// Only site/dist is ever deleted, after its resolved path has been checked.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SITE = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.dirname(SITE);
export const DEFAULT_OUT = path.join(SITE, "dist");
const SRC = path.join(SITE, "src");
const ASSET_DIR = "site-assets";

// Public web files a package may contain. Anything else fails the build (keeps logs, PDFs,
// Python, credentials and stray files out of the published site).
const PUBLIC_EXT = new Set([".html", ".css", ".js", ".json", ".mp4", ".jpg", ".png", ".svg",
                            ".ttf", ".woff", ".woff2", ".txt"]);
const PUBLIC_NAMES = new Set(["LICENSE"]);
const OS_JUNK = new Set(["Thumbs.db", "desktop.ini", ".DS_Store"]);
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const MEDIA_REF = /^(?:animations|media)\/[A-Za-z0-9_./-]+\.(?:mp4|jpg|png|svg)$/;

// ------------------------------------------------------------------ catalog

export function loadCatalog(file = path.join(SITE, "catalog.json"), repo = REPO) {
  const cat = JSON.parse(fs.readFileSync(file, "utf8"));
  const fail = (msg) => { throw new Error("catalog.json: " + msg); };
  if (cat.version !== 1 || !Array.isArray(cat.courses) || cat.courses.length === 0) fail("expected version 1 and a courses list");
  const paths = new Set(), keys = new Set(), sources = new Set();
  const checkSource = (where, src) => {
    if (typeof src !== "string" || path.isAbsolute(src) || src.split(/[\\/]/).includes("..")) fail(where + ": source must be a repository-relative path");
    const abs = path.resolve(repo, src);
    if (!abs.startsWith(repo + path.sep)) fail(where + ": source is outside the repository");
    if (sources.has(abs)) fail(where + ": source used twice");
    sources.add(abs);
    for (const f of ["index.html", "course.json", path.join("animations", "manifest.json")])
      if (!fs.existsSync(path.join(abs, f))) fail(where + ": " + src + " has no " + f.replace(/\\/g, "/"));
    return abs;
  };
  const checkKey = (where, key) => {
    if (typeof key !== "string" || !key) fail(where + ": storeKey required");
    if (keys.has(key)) fail(where + ": storeKey " + key + " is used twice");
    keys.add(key);
  };
  for (const c of cat.courses) {
    const where = "course " + c.id;
    if (!SLUG.test(c.id || "") || !SLUG.test(c.path || "")) fail(where + ": id and path must be lowercase slugs");
    if (c.path === ASSET_DIR || paths.has(c.path)) fail(where + ": path " + c.path + " is reserved or used twice");
    paths.add(c.path);
    for (const k of ["title", "short", "description"]) if (typeof c[k] !== "string" || !c[k]) fail(where + ": " + k + " required");
    if (c.kind === "single") {
      c.sourceAbs = checkSource(where, c.source);
      checkKey(where, c.storeKey);
    } else if (c.kind === "series") {
      if (!Array.isArray(c.lectures) || c.lectures.length === 0) fail(where + ": lectures required");
      const slugs = new Set();
      for (const l of c.lectures) {
        const lw = where + " lecture " + l.slug;
        if (!SLUG.test(l.slug || "") || slugs.has(l.slug)) fail(lw + ": slug must be a unique lowercase slug");
        slugs.add(l.slug);
        for (const k of ["title", "description"]) if (typeof l[k] !== "string" || !l[k]) fail(lw + ": " + k + " required");
        l.sourceAbs = checkSource(lw, l.source);
        checkKey(lw, l.storeKey);
        if (l.statusApp !== null && (typeof l.statusApp !== "string" || !l.statusApp)) fail(lw + ": statusApp must be a string or null");
      }
    } else fail(where + ": kind must be single or series");
  }
  return cat;
}

// ------------------------------------------------------------------ package inspection

export function listFiles(dir) {
  const out = [];
  (function walk(rel) {
    const abs = path.join(dir, rel);
    for (const ent of fs.readdirSync(abs, { withFileTypes: true }).sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0))) {
      const r = rel ? rel + "/" + ent.name : ent.name;
      if (OS_JUNK.has(ent.name)) continue;
      if (ent.name.startsWith(".")) throw new Error(`Hidden file in a published package: ${path.join(dir, r)}`);
      if (ent.isSymbolicLink()) throw new Error(`Symbolic link in a published package: ${path.join(dir, r)}`);
      if (ent.isDirectory()) walk(r);
      else if (ent.isFile()) {
        if (!PUBLIC_EXT.has(path.extname(ent.name).toLowerCase()) && !PUBLIC_NAMES.has(ent.name))
          throw new Error(`Not a public web asset: ${path.join(dir, r)} (move it out of dist/ or extend PUBLIC_EXT deliberately)`);
        out.push(r);
      }
    }
  })("");
  return out;
}

function readJSON(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }

function mediaRefs(value, acc = new Set()) {
  if (typeof value === "string") { if (MEDIA_REF.test(value)) acc.add(value); }
  else if (Array.isArray(value)) value.forEach((v) => mediaRefs(v, acc));
  else if (value && typeof value === "object") Object.values(value).forEach((v) => mediaRefs(v, acc));
  return acc;
}

// Read the counts students see, and check that the registry matches the package's own code.
export function inspectPackage(src, { storeKey, statusApp, sectionsKey = "sections" }) {
  const course = readJSON(path.join(src, "course.json"));
  const manifest = readJSON(path.join(src, "animations", "manifest.json"));
  const files = new Set(listFiles(src));
  const code = ["app.js", "index.html"].filter((f) => files.has(f)).map((f) => fs.readFileSync(path.join(src, f), "utf8")).join("\n");
  if (!code.includes(JSON.stringify(storeKey))) throw new Error(`${src}: storage key ${storeKey} not found in app.js/index.html`);
  if (statusApp && !code.includes(".app === " + JSON.stringify(statusApp)))
    throw new Error(`${src}: app identity ${statusApp} not found in app.js`);
  const missing = [...mediaRefs(manifest), ...mediaRefs(course)].filter((r) => !files.has(r));
  if (missing.length) throw new Error(`${src}: ${missing.length} media files missing, e.g. ${missing[0]}`);
  const seqs = (manifest.sequences || []).map((s) => ({ id: s.id, section: s.section ?? s.lesson ?? null, steps: s.steps.length }));
  if (!seqs.length || seqs.some((s) => !s.id || !(s.steps > 0))) throw new Error(`${src}: manifest has no usable sequences`);
  const sections = course[sectionsKey];
  if (!Array.isArray(sections) || !sections.length) throw new Error(`${src}: course.json has no ${sectionsKey}`);
  const quiz = Array.isArray(course.quiz) ? course.quiz : [];
  return {
    course, files: [...files],
    sections: sections.length,
    sequences: seqs.length,
    steps: seqs.reduce((n, s) => n + s.steps, 0),
    seqs,
    quiz: quiz.map((q) => ({ id: q.id, choices: q.choices.length })),
    hasExplorer: !!course.explorer,
    video: course.video ? { title: course.video.title, url: course.video.url, duration: course.video.duration } : null,
    book: course.book ? { authors: course.book.authors, title: course.book.title } : null,
  };
}

// ------------------------------------------------------------------ HTML helpers

export function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const plural = (n, one, many = one + "s") => `${n} ${n === 1 ? one : many}`;

function replaceOnce(html, re, fn, what, file) {
  const m = html.match(new RegExp(re.source, re.flags.replace("g", "") + "g"));
  if (!m || m.length !== 1) throw new Error(`${file}: expected exactly one ${what} to inject the course bar (found ${m ? m.length : 0})`);
  return html.replace(re, fn);
}

// Add the course bar, its stylesheet/script and the trailing-slash guard to a package's index.html.
export function injectIndex(html, { bar, assets, file = "index.html" }) {
  // Relative URLs (course.json, animations/...) need the directory URL; /controls/overview -> /controls/overview/.
  const guard = '<script>(function(l){if(!/\\/$/.test(l.pathname)&&!/\\.html$/.test(l.pathname))' +
                'l.replace(l.pathname+"/"+l.search+l.hash);})(location);</script>';
  html = replaceOnce(html, /<head>/, (m) => m + "\n" + guard, "<head>", file);
  html = replaceOnce(html, /<html\b([^>]*)>/, (m, attrs) => {
    if (/\sclass="/.test(attrs)) return m.replace(/\sclass="/, ' class="cikgu-site ');
    return `<html${attrs} class="cikgu-site">`;
  }, "<html>", file);
  html = replaceOnce(html, /<\/head>/, (m) => `<link rel="stylesheet" href="${assets}coursebar.css">\n` + m, "</head>", file);
  html = replaceOnce(html, /<a class="skip-link"[^>]*>[^<]*<\/a>/, (m) => m + "\n" + bar, "skip link", file);
  html = replaceOnce(html, /<\/body>/, (m) => `<script src="${assets}coursebar.js"></script>\n` + m, "</body>", file);
  return html;
}

function seriesBar(course, lectures, i, home, courseHref) {
  const cur = lectures[i];
  const items = lectures.map((l, j) => {
    const current = j === i ? ' aria-current="page"' : "";
    return `<li><a href="../${l.slug}/"${current}><span class="cikgu-cb-num" aria-hidden="true">${j + 1}</span>` +
           `<span class="cikgu-cb-name"><span class="cikgu-cb-sr">Lecture ${j + 1}: </span>${esc(l.title)}</span></a></li>`;
  }).join("");
  const prev = lectures[i - 1], next = lectures[i + 1];
  const pager = [
    prev ? `<a href="../${prev.slug}/" rel="prev" aria-label="Previous lecture: ${esc(prev.title)}">‹&nbsp;Previous<span class="cikgu-cb-target">: ${esc(prev.title)}</span></a>` : "",
    next ? `<a href="../${next.slug}/" rel="next" aria-label="Next lecture: ${esc(next.title)}">Next<span class="cikgu-cb-target">: ${esc(next.title)}</span>&nbsp;›</a>` : "",
  ].join("");
  return `<nav class="cikgu-cb" aria-label="${esc(course.title)} lectures"><div class="cikgu-cb-inner">` +
    `<p class="cikgu-cb-crumbs"><a class="cikgu-cb-home" href="${home}">Cikgu</a><span class="sep" aria-hidden="true">/</span>` +
    `<a href="${courseHref}">${esc(course.title)}</a><span class="sep" aria-hidden="true">/</span>` +
    `<strong class="cikgu-cb-where">Lecture ${i + 1} of ${lectures.length}</strong></p>` +
    `<ol class="cikgu-cb-lectures">${items}</ol>` +
    (pager ? `<p class="cikgu-cb-pager">${pager}</p>` : "") +
    `</div></nav>`;
}

function singleBar(course, others, home) {
  const links = others.map((o) => `<a href="${home}${o.path}/"><span class="cikgu-cb-sr">Other course: </span>${esc(o.short)}&nbsp;›</a>`).join("");
  return `<nav class="cikgu-cb" aria-label="Cikgu library"><div class="cikgu-cb-inner">` +
    `<p class="cikgu-cb-crumbs"><a class="cikgu-cb-home" href="${home}">Cikgu</a><span class="sep" aria-hidden="true">/</span>` +
    `<strong aria-current="page">${esc(course.short)}</strong></p>` +
    (links ? `<p class="cikgu-cb-pager">${links}</p>` : "") +
    `</div></nav>`;
}

// ------------------------------------------------------------------ library pages

const THEME_BOOT = '<script>(function(){var t=null;try{t=localStorage.getItem("cikgu-site-theme");}catch(e){}' +
  'if(t!=="light"&&t!=="dark")t=window.matchMedia&&matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";' +
  'document.documentElement.setAttribute("data-theme",t);})();</script>';

function page({ title, description, assets, crumbs, body, data }) {
  return `<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="${assets}favicon.svg" type="image/svg+xml">
${THEME_BOOT}
<link rel="stylesheet" href="${assets}site.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="lib-top">
  <a class="lib-brand" href="${crumbs ? crumbs[0].href : "./"}"><span class="lib-mark" aria-hidden="true">C</span><span>Cikgu<small>Animated mathematics study guides</small></span></a>
  <button type="button" class="lib-theme" id="theme-toggle" aria-pressed="false" hidden>Dark theme</button>
</header>
${crumbs ? `<nav class="lib-crumbs" aria-label="Breadcrumb"><ol>${crumbs.map((c) => c.href ? `<li><a href="${c.href}">${esc(c.label)}</a></li>` : `<li aria-current="page">${esc(c.label)}</li>`).join("")}</ol></nav>\n` : ""}<main id="main" class="lib-main" tabindex="-1">
${body}
</main>
<footer class="lib-foot"><p>Original study companions: notes, worked examples and ManimGL animations written for these guides, with links to the lectures and books they follow. Progress is saved only in this browser. No accounts, no tracking.</p></footer>
${data ? `<script type="application/json" id="cikgu-data">${JSON.stringify(data).replace(/</g, "\\u003c")}</script>\n` : ""}<script src="${assets}library.js"></script>
</body>
</html>
`;
}

function homePage(cat, info) {
  const cards = cat.courses.map((c) => {
    let facts, extra = "";
    if (c.kind === "single") {
      const p = info[c.id];
      facts = [plural(p.sections, c.sectionLabel || "section"),
               `${plural(p.sequences, "animation")}, ${p.steps} steps`, p.hasExplorer ? "live explorer" : "", plural(p.quiz.length, "quiz question")];
    } else {
      const ps = c.lectures.map((l) => info[c.id + "/" + l.slug]);
      facts = [plural(c.lectures.length, "lecture"), `${plural(ps.reduce((n, p) => n + p.sequences, 0), "animation")}, ${ps.reduce((n, p) => n + p.steps, 0)} steps`,
               "explorer and quiz per lecture"];
      extra = `<ol class="lib-mini">${c.lectures.map((l) => `<li><a href="${c.path}/${l.slug}/">${esc(l.title)}</a></li>`).join("")}</ol>`;
    }
    return `<li class="lib-card">
  <p class="lib-eyebrow">${c.kind === "series" ? "Course · lecture series" : "Course"}</p>
  <h2><a href="${c.path}/">${esc(c.title)}</a></h2>
  <p>${esc(c.description)}</p>
  <p class="lib-facts">${facts.filter(Boolean).map(esc).join(" · ")}</p>
  ${extra}
  <p class="lib-cta"><a class="lib-btn" href="${c.path}/">${c.kind === "series" ? "Open course" : "Start studying"}<span class="lib-sr">: ${esc(c.short)}</span> →</a></p>
</li>`;
  }).join("\n");
  return page({
    title: "Cikgu · study library", description: "Animated mathematics study guides: step-by-step derivations, worked examples, explorers and quizzes.",
    assets: ASSET_DIR + "/", crumbs: null,
    body: `<section class="lib-hero"><h1>Study library</h1>
<p>Step-by-step animated derivations, worked examples, interactive explorers and quizzes with explanations. Choose a course to begin.</p></section>
<ul class="lib-cards">
${cards}
</ul>`,
  });
}

function seriesPage(c, info) {
  const lectures = c.lectures.map((l, i) => {
    const p = info[c.id + "/" + l.slug];
    const facts = [plural(p.sections, "section"), `${plural(p.sequences, "animation")}, ${p.steps} steps`,
                   p.hasExplorer ? "explorer" : "", plural(p.quiz.length, "quiz question")].filter(Boolean);
    const source = p.video ? `<p class="lib-source">Lecture: <a href="${esc(p.video.url)}" target="_blank" rel="noopener noreferrer">${esc(p.video.title)}<span class="lib-sr"> (opens in a new tab)</span></a> · ${esc(p.video.duration)}</p>` : "";
    return `<li class="lib-lecture" data-lecture="${esc(l.slug)}">
  <span class="lib-num" aria-hidden="true">${i + 1}</span>
  <div class="lib-lecture-body">
    <h2><a href="${l.slug}/"><span class="lib-sr">Lecture ${i + 1}: </span>${esc(l.title)}</a></h2>
    <p>${esc(l.description)}</p>
    <p class="lib-facts">${facts.map(esc).join(" · ")}</p>
    ${source}
    <p class="lib-progress" data-progress hidden></p>
    <p class="lib-cta"><a class="lib-btn" href="${l.slug}/" data-continue><span data-label>Start lecture</span><span class="lib-sr"> (lecture ${i + 1}: ${esc(l.title)})</span> →</a></p>
  </div>
</li>`;
  }).join("\n");
  const book = info[c.id + "/" + c.lectures[0].slug].book;
  const data = { lectures: c.lectures.map((l) => {
    const p = info[c.id + "/" + l.slug];
    return { slug: l.slug, title: l.title, storeKey: l.storeKey, seqs: p.seqs, quiz: p.quiz };
  }) };
  return page({
    title: `${c.title} · Cikgu`, description: c.description, assets: "../" + ASSET_DIR + "/",
    crumbs: [{ href: "../", label: "Library" }, { label: c.title }],
    body: `<section class="lib-hero"><p class="lib-eyebrow">Course · ${plural(c.lectures.length, "lecture")}</p><h1>${esc(c.title)}</h1>
<p>${esc(c.description)}</p>
${book ? `<p class="lib-source">Reading: ${esc(book.authors)}, <cite>${esc(book.title)}</cite>. Each lecture links its book pages and lecture moments.</p>` : ""}</section>
<ol class="lib-lectures">
${lectures}
</ol>
<p class="lib-note" id="progress-note" hidden></p>`,
    data,
  });
}

// ------------------------------------------------------------------ output

function cleanOut(out) {
  const resolved = path.resolve(out);
  if (resolved === DEFAULT_OUT) {
    if (fs.existsSync(resolved)) {
      if (fs.lstatSync(resolved).isSymbolicLink() || !fs.lstatSync(resolved).isDirectory()) throw new Error(resolved + " is not a plain directory");
      fs.rmSync(resolved, { recursive: true, force: true });
    }
  } else if (fs.existsSync(resolved)) {
    throw new Error(`Refusing to write into existing ${resolved}: only site/dist is cleaned automatically`);
  }
  const rel = path.relative(REPO, resolved);
  if (!rel.startsWith("..") && !path.isAbsolute(rel) && resolved !== DEFAULT_OUT)
    throw new Error("Custom output directories must be outside the repository");
  fs.mkdirSync(resolved, { recursive: true });
  return resolved;
}

function write(out, rel, content) {
  const f = path.join(out, ...rel.split("/"));
  fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, content);
}

function copyPackage(src, out, dest, files, transformIndex) {
  for (const rel of files) {
    const target = path.join(out, ...dest.split("/"), ...rel.split("/"));
    fs.mkdirSync(path.dirname(target), { recursive: true });
    if (rel === "index.html") fs.writeFileSync(target, transformIndex(fs.readFileSync(path.join(src, rel), "utf8")));
    else fs.copyFileSync(path.join(src, ...rel.split("/")), target);
  }
}

export function build({ out = DEFAULT_OUT, catalogFile, repo = REPO, quiet = false } = {}) {
  const cat = loadCatalog(catalogFile, repo);
  const info = {};
  for (const c of cat.courses) {
    if (c.kind === "single") info[c.id] = inspectPackage(c.sourceAbs, c);
    else for (const l of c.lectures) info[c.id + "/" + l.slug] = inspectPackage(l.sourceAbs, l);
  }
  out = cleanOut(out);
  fs.mkdirSync(path.join(out, ASSET_DIR));
  for (const f of ["site.css", "library.js", "coursebar.css", "coursebar.js", "favicon.svg"])
    fs.copyFileSync(path.join(SRC, f), path.join(out, ASSET_DIR, f));

  write(out, "index.html", homePage(cat, info));
  for (const c of cat.courses) {
    if (c.kind === "single") {
      const others = cat.courses.filter((o) => o !== c);
      const bar = singleBar(c, others, "../");
      copyPackage(c.sourceAbs, out, c.path, info[c.id].files,
                  (html) => injectIndex(html, { bar, assets: "../" + ASSET_DIR + "/", file: c.source + "/index.html" }));
      continue;
    }
    write(out, c.path + "/index.html", seriesPage(c, info));
    c.lectures.forEach((l, i) => {
      const bar = seriesBar(c, c.lectures, i, "../../", "../");
      const dest = c.path + "/" + l.slug;
      copyPackage(l.sourceAbs, out, dest, info[c.id + "/" + l.slug].files,
                  (html) => injectIndex(html, { bar, assets: "../../" + ASSET_DIR + "/", file: l.source + "/index.html" }));
      if (l.statusApp) {
        // The lectures ask api/status whether their optional chat server is present. This static site has none.
        write(out, dest + "/api/status", JSON.stringify({ app: l.statusApp, hosted: true,
          tutor: { configured: false, model: "" }, book: { available: false } }) + "\n");
      }
    });
  }
  const files = listOutput(out);
  const bytes = files.reduce((n, f) => n + fs.statSync(path.join(out, f)).size, 0);
  if (!quiet) {
    console.log(`Built ${path.relative(process.cwd(), out) || "."}: ${files.length} files, ${(bytes / 1048576).toFixed(1)} MB`);
    for (const c of cat.courses) {
      if (c.kind === "single") console.log(`  /${c.path}/  ${c.title}: ${info[c.id].sequences} animations, ${info[c.id].steps} steps`);
      else c.lectures.forEach((l, i) => { const p = info[c.id + "/" + l.slug];
        console.log(`  /${c.path}/${l.slug}/  ${i + 1}. ${l.title}: ${p.sections} sections, ${p.sequences} animations, ${p.steps} steps, ${p.quiz.length} quiz`); });
    }
  }
  return { out, files, bytes, info, catalog: cat };
}

export function listOutput(out) {
  const res = [];
  (function walk(rel) {
    for (const ent of fs.readdirSync(path.join(out, rel), { withFileTypes: true }).sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0))) {
      const r = rel ? rel + "/" + ent.name : ent.name;
      if (ent.isDirectory()) walk(r); else res.push(r);
    }
  })("");
  return res;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    build();
  } catch (e) {
    console.error("Build failed: " + e.message);
    process.exit(1);
  }
}
