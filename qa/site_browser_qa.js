// Browser and HTTP checks for the unified Cikgu site (site/dist served by site/server.py).
//   node site/build.mjs && node qa/site_browser_qa.js
// Uses installed Chrome through qa/tooling's playwright-core. Covers: home and course pages, every
// package's lesson/explorer/quiz routes under the new paths, all media paths, one real animated
// step per package, lecture prev/next, saved progress across lectures and reloads, themes and
// contrast, desktop/mobile layout of the course bar against the lectures' sticky/fixed panels,
// fullscreen, the static-site tutor state, source links, blocked storage and no-JS links.
// Screenshots go to qa/screenshots/site/ (ignored).
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");
const { PROJECT, CHROME, PY, recorder, contrast } = require("./qa_common");
const { chromium } = require(path.join(__dirname, "tooling", "node_modules", "playwright-core"));

const DIST = path.join(PROJECT, "site", "dist");
const SHOTS = path.join(__dirname, "screenshots", "site");
const catalog = JSON.parse(fs.readFileSync(path.join(PROJECT, "site", "catalog.json"), "utf8"));
const series = catalog.courses.find(c => c.kind === "series");
const ode = catalog.courses.find(c => c.kind === "single");
const LECTURES = series.lectures.map(l => ({ ...l, url: `${series.path}/${l.slug}/`,
  manifest: JSON.parse(fs.readFileSync(path.join(PROJECT, l.source, "animations", "manifest.json"), "utf8")) }));
const odeManifest = JSON.parse(fs.readFileSync(path.join(PROJECT, ode.source, "animations", "manifest.json"), "utf8"));
const { results, check } = recorder();

function startSite() {
  if (!fs.existsSync(path.join(DIST, "index.html"))) throw new Error("Build first: node site/build.mjs");
  const portFile = path.join(os.tmpdir(), "cikgu-site-qa-" + process.pid + "-" + Date.now() + ".txt");
  const nonce = "qa-" + process.pid + "-" + Date.now();
  const proc = spawn(PY, ["-I", path.join(PROJECT, "site", "server.py"), "--port", "8840", "--port-file", portFile, "--nonce", nonce],
                     { stdio: ["ignore", "pipe", "pipe"], windowsHide: true });
  proc.stdout.on("data", () => {}); proc.stderr.on("data", () => {});
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    (function poll() {
      if (fs.existsSync(portFile)) {
        const port = fs.readFileSync(portFile, "utf8").trim();
        fetch(`http://127.0.0.1:${port}/__site_health`).then(r => r.json()).then(j => {
          if (j.app !== "CikguSite" || j.nonce !== nonce) return reject(new Error("health mismatch"));
          resolve({ base: `http://127.0.0.1:${port}/`, stop() {
            try { process.kill(j.pid); } catch (e) { /* gone */ }
            try { proc.kill(); } catch (e) { /* gone */ }
            try { fs.unlinkSync(portFile); } catch (e) { /* gone */ }
          } });
        }).catch(() => setTimeout(poll, 150));
      } else if (Date.now() - t0 > 15000) reject(new Error("server did not start"));
      else setTimeout(poll, 150);
    })();
  });
}

async function newPage(browser, opts, init) {
  const ctx = await browser.newContext(Object.assign({ viewport: { width: 1440, height: 900 } }, opts || {}));
  await ctx.addInitScript(() => {
    const play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () { this.playbackRate = 4; return play.call(this); };
  });
  if (init) await ctx.addInitScript(init);
  const page = await ctx.newPage();
  page.errors = []; page.bad = []; page.tutorPosts = 0;
  page.on("console", m => { if (m.type() === "error") page.errors.push(m.text()); });
  page.on("pageerror", e => page.errors.push("pageerror: " + e.message));
  page.on("response", r => { if (r.status() >= 400) page.bad.push(r.status() + " " + r.url()); });
  page.on("requestfailed", r => { if (!/\.mp4/.test(r.url())) page.bad.push("failed " + r.url()); });
  page.on("request", r => { if (/api\/tutor/.test(r.url())) page.tutorPosts++; });
  return { ctx, page };
}

async function waitStep(page, k) {
  await page.waitForFunction(k => {
    const w = document.querySelector(".stage-wrap"), img = document.querySelector(".stage-still");
    return w && w.dataset.playing === "false" && w.dataset.step === String(k) && img && img.complete && img.naturalWidth > 0 &&
      !document.querySelector(".stage").classList.contains("video-on");
  }, k, { timeout: 30000 });
}
async function loaded(page) {
  await page.waitForFunction(() => !document.querySelector(".loading-note, .loading"), null, { timeout: 15000 });
  await page.waitForTimeout(150);
}
const noOverflow = page => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
const rect = (page, sel) => page.evaluate(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, h: r.height }; }, sel);
const shot = (page, name, full) => page.screenshot({ path: path.join(SHOTS, name + ".png"), fullPage: !!full });

// Play the first step of the current sequence: the clip must actually play, then settle on step 1.
async function animateOneStep(page, label) {
  await waitStep(page, 0);
  const sawVideo = page.waitForFunction(() => {
    const v = document.querySelector(".stage-video");
    return document.querySelector(".stage").classList.contains("video-on") && v && v.currentTime > 0;
  }, null, { timeout: 15000 }).then(() => true, () => false);
  await page.click('[data-action="next"]');
  const played = await sawVideo;
  await waitStep(page, 1);
  const still = await page.evaluate(() => document.querySelector(".stage-still").getAttribute("src"));
  check(`${label}: Next plays a real clip and stops on the step-1 still`, played && /state-01\.jpg$/.test(still), still);
}

async function httpChecks(base) {
  const get = (p, init) => fetch(base + p, Object.assign({ redirect: "manual" }, init || {}));
  check("http: home and course pages served", (await get("")).status === 200 && (await get(series.path + "/")).status === 200);
  const r = await get(LECTURES[0].url.replace(/\/$/, ""));
  check("http: lecture directory without slash redirects to the slash URL", r.status === 301 && r.headers.get("location") === "/" + LECTURES[0].url,
        r.status + " " + r.headers.get("location"));
  for (const l of LECTURES) {
    const s = await get(l.url + "api/status");
    const j = await s.json();
    check(`http: ${l.slug} static status names the lecture and has no tutor or book`,
          s.headers.get("content-type").startsWith("application/json") && j.app === l.statusApp && j.tutor.configured === false && j.book.available === false);
  }
  check("http: POST to the tutor path is refused (no chat backend)", (await get(LECTURES[0].url + "api/tutor", { method: "POST", body: "{}" })).status === 405);
  const blocked = await Promise.all(["databook.pdf", "../README.md", ".git/config", "controls/overview/book", "site-assets/"].map(p => get(p).then(x => x.status)));
  check("http: no book, repository files, dot-paths or listings", blocked.every(s => s === 404), blocked.join(","));
  const vid = LECTURES[0].manifest.sequences[0].steps[0].transition.src;
  const rg = await get(LECTURES[0].url + vid, { headers: { Range: "bytes=0-99" } });
  check("http: MP4 byte ranges (seeking)", rg.status === 206 && rg.headers.get("content-type") === "video/mp4" && (await rg.arrayBuffer()).byteLength === 100);

  // Every clip/still referenced by every manifest is served under its new path.
  const refs = [];
  const walk = (v, prefix) => { if (typeof v === "string") { if (/^(animations|media)\/.+\.(mp4|jpg|png)$/.test(v)) refs.push(prefix + v); }
    else if (v && typeof v === "object") Object.values(v).forEach(x => walk(x, prefix)); };
  walk(odeManifest, ode.path + "/");
  LECTURES.forEach(l => walk(l.manifest, l.url));
  const uniq = [...new Set(refs)];
  const statuses = [];
  for (let i = 0; i < uniq.length; i += 24)
    statuses.push(...await Promise.all(uniq.slice(i, i + 24).map(u => get(u, { method: "HEAD" }).then(x => [u, x.status]))));
  const missing = statuses.filter(s => s[1] !== 200);
  check(`http: all ${uniq.length} media files referenced by the manifests are served`, missing.length === 0, missing.slice(0, 3).join(" "));
}

async function main() {
  fs.mkdirSync(SHOTS, { recursive: true });
  const srv = await startSite();
  const base = srv.base;
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
  try {
    await httpChecks(base);

    // ---------------------------------------------------------------- desktop
    const { ctx, page } = await newPage(browser);
    await page.goto(base);
    const cards = await page.$$eval(".lib-card h2 a", as => as.map(a => [a.textContent, a.getAttribute("href")]));
    check("home: one card per catalog course, in catalog order",
          JSON.stringify(cards.map(c => c[1])) === JSON.stringify(catalog.courses.map(c => c.path + "/")), JSON.stringify(cards));
    check("home: no horizontal overflow at 1440 px", await noOverflow(page));
    await shot(page, "home-desktop-light");
    await page.click("#theme-toggle");
    const dark = await page.evaluate(() => document.documentElement.dataset.theme);
    await shot(page, "home-desktop-dark");
    await page.reload();
    check("home: theme toggle switches and persists", dark === "dark" && (await page.evaluate(() => document.documentElement.dataset.theme)) === "dark");
    await page.click("#theme-toggle");

    await page.click('.lib-card h2 a[href="controls/"]');
    await page.waitForURL(base + "controls/");
    const order = await page.$$eval(".lib-lecture h2 a", as => as.map(a => a.getAttribute("href")));
    check("course: lectures in catalog order", JSON.stringify(order) === JSON.stringify(LECTURES.map(l => l.slug + "/")), order.join(" "));
    const facts = await page.$$eval(".lib-lecture .lib-facts", ps => ps.map(p => p.textContent));
    const expectSteps = LECTURES.map(l => l.manifest.sequences.reduce((n, s) => n + s.steps.length, 0));
    check("course: step counts read from the manifests", facts.every((f, i) => f.includes(`${LECTURES[i].manifest.sequences.length} animations, ${expectSteps[i]} steps`)), facts.join(" | "));
    const ctas = await page.$$eval("[data-continue]", as => as.map(a => a.textContent));
    check("course: fresh browser offers Start lecture", ctas.every(t => /^Start lecture \(lecture \d: .+\) →$/.test(t)), ctas.join(" | "));
    const srcLinks = await page.$$eval(".lib-source a", as => as.map(a => a.href));
    check("course: each lecture links its source video", srcLinks.length === LECTURES.length && srcLinks.every(h => /youtube\.com\/watch\?v=/.test(h)));
    await shot(page, "course-desktop", true);

    // Lecture 1 from the course page; bar shows position and next lecture.
    await page.click(`.lib-lecture h2 a[href="${LECTURES[0].slug}/"]`);
    await loaded(page);
    const bar1 = await page.evaluate(() => ({
      current: document.querySelector('.cikgu-cb-lectures a[aria-current="page"]').getAttribute("href"),
      prev: !!document.querySelector('.cikgu-cb a[rel="prev"]'), next: document.querySelector('.cikgu-cb a[rel="next"]').getAttribute("href") }));
    check("lecture 1: bar marks the active lecture, no previous, next is lecture 2", bar1.current === "../overview/" && !bar1.prev && bar1.next === "../linear-systems/", JSON.stringify(bar1));

    // Every lecture: lesson animation, explorer, quiz, sources, tutor, layout.
    for (const [i, l] of LECTURES.entries()) {
      const url = base + l.url;
      await page.goto(url + "#s1"); await loaded(page);
      await animateOneStep(page, l.slug);
      // Sticky layout at the top of the page and after scrolling past the course bar.
      const top = await page.evaluate(() => {
        const cb = document.querySelector(".cikgu-cb").getBoundingClientRect(), tb = document.querySelector(".topbar").getBoundingClientRect(),
              sn = document.querySelector(".sidenav").getBoundingClientRect();
        return { cb: cb.bottom, tb: tb.top, tbBottom: tb.bottom, snTop: sn.top, snBottom: sn.bottom, vh: innerHeight };
      });
      check(`${l.slug}: at the top, header sits under the bar and the side panel ends at the viewport`,
            Math.abs(top.tb - top.cb) < 1.5 && Math.abs(top.snTop - top.tbBottom) < 1.5 && Math.abs(top.snBottom - top.vh) < 2, JSON.stringify(top));
      await page.evaluate(() => window.scrollTo(0, 400)); await page.waitForTimeout(120);
      const sc = await page.evaluate(() => ({ tb: document.querySelector(".topbar").getBoundingClientRect().top,
        sn: document.querySelector(".sidenav").getBoundingClientRect().top, snB: document.querySelector(".sidenav").getBoundingClientRect().bottom, vh: innerHeight }));
      check(`${l.slug}: scrolled, sticky header and side panel fill the viewport`, Math.abs(sc.tb) < 1 && Math.abs(sc.sn - 52) < 1.5 && Math.abs(sc.snB - sc.vh) < 2, JSON.stringify(sc));
      await page.evaluate(() => window.scrollTo(0, 0));

      // Tutor: the static site explains chat is unavailable; nothing is sent.
      await page.click("#tutor-toggle"); await page.waitForTimeout(150);
      const tut = await page.evaluate(() => {
        const t = document.getElementById("tutor"), r = t.getBoundingClientRect();
        return { status: t.querySelector(".tutor-status").textContent, note: (t.querySelector(".cikgu-tutor-note") || {}).textContent || "",
                 setupShown: getComputedStyle(t.querySelector(".tutor-setup")).display !== "none", send: t.querySelector('button[type="submit"]').disabled,
                 input: t.querySelector("textarea").disabled, bottom: r.bottom, vh: innerHeight, keyField: !!t.querySelector('input[type="password"]') };
      });
      check(`${l.slug}: tutor panel says chat is not on this site, send/input disabled, no key field`,
            tut.status === "not on this site" && /not available on this study site/.test(tut.note) && !tut.setupShown && tut.send && tut.input && !tut.keyField, JSON.stringify(tut));
      check(`${l.slug}: tutor column fits the viewport under the bar`, Math.abs(tut.bottom - tut.vh) < 2, tut.bottom + "/" + tut.vh);
      if (i === 0) await shot(page, "lecture-desktop-tutor");
      await page.click("#tutor-toggle");

      await page.goto(url + "#explorer"); await loaded(page);
      check(`${l.slug}: explorer route renders`, await page.$eval(".explorer", e => e.getBoundingClientRect().height > 200).catch(() => false));
      await page.goto(url + "#quiz"); await loaded(page);
      const nChoices = await page.$$eval(".choices button", b => b.length);
      check(`${l.slug}: quiz route renders choices`, nChoices >= 2, nChoices);
      await page.goto(url + "#sources"); await loaded(page);
      const src = await page.evaluate(() => ({ online: [...document.querySelectorAll('a[href^="http://databookuw.com/databook.pdf#page="]')].length,
        local: document.querySelectorAll('a[href^="book#"]').length, video: document.querySelectorAll('a[href*="youtube.com/watch"]').length }));
      check(`${l.slug}: sources keep online book and lecture links, no local PDF links`, src.online > 0 && src.video > 0 && src.local === 0, JSON.stringify(src));
      check(`${l.slug}: no console errors or failed requests`, page.errors.length === 0 && page.bad.length === 0, page.errors.concat(page.bad).slice(0, 3).join(" | "));
      page.errors.length = 0; page.bad.length = 0;
    }
    check("lectures: no request was sent to api/tutor", page.tutorPosts === 0, page.tutorPosts);

    // Fullscreen keeps working (the bar is outside the stage) and keyboard order starts with skip link then bar.
    await page.goto(base + LECTURES[1].url + "#s2"); await loaded(page); await waitStep(page, 0);
    await page.click(".stage-fs");
    await page.waitForTimeout(300);
    const fs1 = await page.evaluate(() => !!document.fullscreenElement && document.fullscreenElement.classList.contains("stage-col") && !document.fullscreenElement.querySelector(".cikgu-cb"));
    await page.keyboard.press("ArrowRight"); await waitStep(page, 1);
    await page.evaluate(() => document.exitFullscreen && document.fullscreenElement && document.exitFullscreen());
    check("fullscreen: stage enters full screen without the bar; arrow key still steps", fs1);
    await page.goto(base + LECTURES[1].url + "#s1"); await loaded(page);
    await page.reload(); await loaded(page); // A hash-only move retains focus from the fullscreen test.
    // The lecture moves focus to its main area on load, so start from the skip link as a keyboard user would.
    await page.focus(".skip-link"); const t1 = await page.evaluate(() => document.activeElement.className);
    await page.keyboard.press("Tab"); const t2 = await page.evaluate(() => document.activeElement.textContent);
    check("keyboard: skip link first, then the course bar", t1 === "skip-link" && t2 === "Cikgu", t1 + " / " + t2);

    // Progress survives switching lectures with the bar and reloading; course page summarizes it.
    const ls = LECTURES[1];
    await page.goto(base + ls.url + "#s1"); await loaded(page); await waitStep(page, 1);   // restored step 1 from the earlier run
    await page.goto(base + ls.url + "#quiz"); await loaded(page);
    await page.click(".choices button >> nth=0"); await page.waitForTimeout(250);
    await page.click('.cikgu-cb a[rel="next"]'); await loaded(page);
    check("bar: Next lecture opens lecture 3 in the same tab", page.url() === base + LECTURES[2].url, page.url());
    await page.click('.cikgu-cb a[rel="prev"]'); await loaded(page);
    await page.reload(); await loaded(page);
    const saved = await page.evaluate(k => JSON.parse(localStorage.getItem(k)), ls.storeKey);
    const firstSeq = ls.manifest.sequences.find(s => s.section === 1).id;
    check("progress: lecture 2 keeps its step and quiz answer after switching lectures and reloading",
          saved && saved.reached[firstSeq] >= 1 && Object.keys(saved.quiz).length === 1, JSON.stringify(saved && saved.reached));
    const keys = await page.evaluate(() => Object.keys(localStorage).sort());
    check("progress: each lecture keeps its own original storage key", LECTURES.every(l => keys.includes(l.storeKey)), keys.join(","));
    const seenSteps = Object.values(saved.reached).reduce((n, k) => n + k, 0);
    await page.goto(base + series.path + "/");
    const prog = await page.$eval(`[data-lecture="${ls.slug}"] [data-progress]`, p => p.hidden ? "" : p.textContent);
    const cont = await page.$eval(`[data-lecture="${ls.slug}"] [data-continue]`, a => [a.getAttribute("href"), a.textContent]);
    // The fullscreen test also viewed a step in section 2; include both sequences.
    const expectedSeen = ls.manifest.sequences.reduce((n, s) => n + (saved.reached[s.id] || 0), 0);
    const expectedTotal = ls.manifest.sequences.reduce((n, s) => n + s.steps.length, 0);
    check("course: summary shows saved steps and quiz answers with a continue link",
          prog.includes(`${expectedSeen} of ${expectedTotal} animation steps seen · 1 of 10 quiz questions answered`) && cont[0] === ls.slug + "/#s1" && cont[1] === "Continue at section 1 (lecture 2: Linear Systems) →", prog + " | " + cont);

    // Appending a lecture must also connect it to the preceding lecture in the live course bar.
    const lastLecture = LECTURES[LECTURES.length - 1], previousLecture = LECTURES[LECTURES.length - 2];
    await page.goto(base + previousLecture.url + "#s1"); await loaded(page);
    await page.click('.cikgu-cb a[rel="next"]'); await loaded(page);
    check("bar: final lecture is reachable from its predecessor in the same tab", page.url() === base + lastLecture.url, page.url());
    check("bar: final lecture has a previous link and no next link",
          await page.locator('.cikgu-cb a[rel="next"]').count() === 0 &&
          await page.locator('.cikgu-cb a[rel="prev"]').getAttribute("href") === `../${previousLecture.slug}/`);
    await page.click('.cikgu-cb a[rel="prev"]'); await loaded(page);
    check("bar: final lecture links back to its predecessor", page.url() === base + previousLecture.url, page.url());

    // Theme: dark lecture, readable bar in both themes.
    await page.goto(base + LECTURES[2].url + "#s1"); await loaded(page);
    const contrastOf = () => page.evaluate(() => {
      const bar = document.querySelector(".cikgu-cb"), a = bar.querySelector(".cikgu-cb-home"), cur = bar.querySelector('[aria-current="page"]');
      return [getComputedStyle(a).color, getComputedStyle(bar).backgroundColor, getComputedStyle(cur).color, getComputedStyle(cur).backgroundColor];
    });
    const light = await contrastOf();
    await page.click("#theme-toggle"); await page.waitForTimeout(100);
    const darkC = await contrastOf();
    const ratios = [contrast(light[0], light[1]), contrast(light[2], light[3]), contrast(darkC[0], darkC[1]), contrast(darkC[2], darkC[3])].map(x => +x.toFixed(2));
    check("theme: bar follows the lecture theme with AA contrast in light and dark", light[1] !== darkC[1] && ratios.every(r => r >= 4.5), ratios.join(","));
    await shot(page, "lecture-desktop-dark");
    await page.click("#theme-toggle");

    // ODE guide under /ode/.
    await page.goto(base + "ode/"); await loaded(page);
    await page.goto(base + "ode/#watch"); await loaded(page);
    await animateOneStep(page, "ode");
    const odeBar = await page.$$eval(".cikgu-cb a", as => as.map(a => a.getAttribute("href")));
    check("ode: bar links back to the library and to Control Bootcamp", odeBar.includes("../") && odeBar.includes("../controls/"), odeBar.join(" "));
    await page.goto(base + "ode/#explorer"); await loaded(page);
    check("ode: explorer renders", await page.$eval(".explorer-grid", e => e.getBoundingClientRect().height > 200).catch(() => false));
    await page.goto(base + "ode/#quiz"); await loaded(page);
    check("ode: quiz renders", (await page.$$eval(".choices button, .choice", b => b.length)) >= 2);
    await page.goto(base + "ode/#reading"); await loaded(page);
    check("ode: further reading links render", (await page.$$eval(".reading-list a", a => a.length)) >= 2);
    const chap = await page.evaluate(() => { const c = document.querySelector(".chapters").getBoundingClientRect(); return [c.bottom, innerHeight]; });
    check("ode: chapter list fits the viewport under the bar", chap[0] <= chap[1] + 1, chap.join("/"));
    await shot(page, "ode-desktop");
    check("ode: no console errors or failed requests", page.errors.length === 0 && page.bad.length === 0, page.errors.concat(page.bad).slice(0, 3).join(" | "));

    // Narrow desktop (1200): the tutor becomes a fixed drawer under the header.
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.goto(base + LECTURES[0].url + "#s1"); await loaded(page);
    await page.click("#tutor-toggle"); await page.waitForTimeout(150);
    let d = await page.evaluate(() => [document.getElementById("tutor").getBoundingClientRect().top, document.querySelector(".topbar").getBoundingClientRect().bottom]);
    check("1200 px: tutor drawer starts under the header at the top of the page", Math.abs(d[0] - d[1]) < 1.5, d.join("/"));
    await page.evaluate(() => window.scrollTo(0, 300)); await page.waitForTimeout(120);
    d = await page.evaluate(() => [document.getElementById("tutor").getBoundingClientRect().top, document.querySelector(".topbar").getBoundingClientRect().bottom]);
    check("1200 px: tutor drawer follows the sticky header after scrolling", Math.abs(d[0] - d[1]) < 1.5, d.join("/"));
    await page.click("#tutor-toggle");
    await ctx.close();

    // ---------------------------------------------------------------- mobile 390 px
    const m = await newPage(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    for (const p of ["", series.path + "/", "ode/#watch"].concat(LECTURES.map(l => l.url + "#s1"))) {
      await m.page.goto(base + p); if (p) await loaded(m.page);
      check(`390 px: /${p} has no horizontal overflow`, await noOverflow(m.page));
    }
    await shot(m.page, "ode-mobile");
    await m.page.goto(base); await shot(m.page, "home-mobile", true);
    await m.page.goto(base + series.path + "/"); await shot(m.page, "course-mobile", true);
    await m.page.goto(base + LECTURES[2].url + "#s3"); await loaded(m.page);
    const mb = await m.page.evaluate(() => {
      const bar = document.querySelector(".cikgu-cb"), links = [...bar.querySelectorAll("a")];
      const vis = links.filter(a => { const r = a.getBoundingClientRect(); return r.width > 0 && r.right <= innerWidth + 1 && r.left >= -1; });
      return { h: bar.getBoundingClientRect().height, links: links.length, visible: vis.length,
               small: links.filter(a => a.getBoundingClientRect().height < 24).length };
    });
    check("390 px: every bar link is on screen and at least 24 px tall", mb.visible === mb.links && mb.small === 0, JSON.stringify(mb));
    await shot(m.page, "lecture-mobile");
    await m.page.click(".nav-toggle"); await m.page.waitForTimeout(350);
    const nav = await m.page.evaluate(() => {
      const t = document.querySelector(".nav-toggle").getBoundingClientRect(), sn = document.querySelector(".sidenav").getBoundingClientRect(),
            tb = document.querySelector(".topbar").getBoundingClientRect(), sc = document.querySelector(".scrim").getBoundingClientRect();
      const hit = document.elementFromPoint(t.left + t.width / 2, t.top + t.height / 2);
      return { snTop: sn.top, scTop: sc.top, tb: tb.bottom, toggleClickable: !!hit.closest(".nav-toggle"), snBottom: sn.bottom, vh: innerHeight };
    });
    check("390 px: opened section menu starts under the header and leaves the menu button usable",
          Math.abs(nav.snTop - nav.tb) < 1.5 && Math.abs(nav.scTop - nav.tb) < 1.5 && nav.toggleClickable && Math.abs(nav.snBottom - nav.vh) < 2, JSON.stringify(nav));
    await shot(m.page, "lecture-mobile-menu");
    await m.page.click(".nav-toggle"); await m.page.waitForTimeout(300);
    await m.page.evaluate(() => window.scrollTo(0, 500)); await m.page.waitForTimeout(120);
    await m.page.click(".nav-toggle"); await m.page.waitForTimeout(350);
    const nav2 = await m.page.evaluate(() => [document.querySelector(".sidenav").getBoundingClientRect().top, document.querySelector(".topbar").getBoundingClientRect().bottom]);
    check("390 px: after scrolling, the menu still starts under the sticky header", Math.abs(nav2[0] - nav2[1]) < 1.5, nav2.join("/"));
    await m.page.click(".nav-toggle"); await m.page.waitForTimeout(300);
    await m.page.click("#tutor-toggle"); await m.page.waitForTimeout(250);
    const mt = await m.page.evaluate(() => [document.getElementById("tutor").getBoundingClientRect().top, document.querySelector(".topbar").getBoundingClientRect().bottom,
                                            !!document.querySelector(".cikgu-tutor-note")]);
    check("390 px: tutor drawer sits under the header and shows the site note", Math.abs(mt[0] - mt[1]) < 1.5 && mt[2], mt.join("/"));
    await shot(m.page, "lecture-mobile-tutor");
    await m.page.click("#tutor-toggle");
    await m.page.goto(base + "ode/#watch"); await loaded(m.page);
    await m.page.click(".nav-toggle"); await m.page.waitForTimeout(200);
    check("390 px: ODE chapter menu opens without overflow", (await m.page.$eval(".chapters", e => e.classList.contains("open"))) && await noOverflow(m.page));
    check("390 px: no console errors or failed requests", m.page.errors.length === 0 && m.page.bad.length === 0, m.page.errors.concat(m.page.bad).slice(0, 3).join(" | "));
    await m.ctx.close();

    // ---------------------------------------------------------------- blocked storage
    const blocked = await newPage(browser, {}, () => {
      Object.defineProperty(window, "localStorage", { configurable: true, get() { throw new DOMException("blocked", "SecurityError"); } });
    });
    await blocked.page.goto(base + series.path + "/");
    const note = await blocked.page.$eval("#progress-note", n => n.hidden ? "" : n.textContent);
    check("storage blocked: course page explains progress cannot be shown", /blocking site storage/.test(note), note);
    await blocked.page.goto(base); await blocked.page.click("#theme-toggle");
    check("storage blocked: home theme toggle still works", (await blocked.page.evaluate(() => document.documentElement.dataset.theme)) === "dark");
    await blocked.page.goto(base + LECTURES[0].url + "#s1"); await loaded(blocked.page);
    await blocked.page.waitForTimeout(400);
    const bs = await blocked.page.evaluate(() => [document.getElementById("progress-summary").textContent, !!document.querySelector(".cikgu-cb")]);
    check("storage blocked: lecture loads with its own 'not saved' notice and the bar", /not saved/.test(bs[0]) && bs[1], bs[0]);
    await blocked.page.goto(base + "ode/#watch"); await loaded(blocked.page);
    check("storage blocked: no page errors", blocked.page.errors.filter(e => /pageerror/.test(e)).length === 0, blocked.page.errors.join(" | "));
    await blocked.ctx.close();

    // ---------------------------------------------------------------- reduced motion, no JavaScript
    const rm = await newPage(browser, { reducedMotion: "reduce" });
    await rm.page.goto(base + LECTURES[0].url + "#s1"); await loaded(rm.page); await waitStep(rm.page, 0);
    await rm.page.click('[data-action="next"]'); await waitStep(rm.page, 1);
    check("reduced motion: lecture still steps with the bar present", !!(await rm.page.$(".cikgu-cb")));
    await rm.ctx.close();
    const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 1024, height: 768 } });
    const np = await nojs.newPage();
    await np.goto(base);
    const hl = await np.$$eval("a", as => as.map(a => a.getAttribute("href")));
    await np.goto(base + series.path + "/");
    const cl = await np.$$eval(".lib-lecture h2 a", as => as.map(a => a.getAttribute("href")));
    await np.goto(base + LECTURES[1].url);
    const bl = await np.$$eval(".cikgu-cb a", as => as.map(a => a.getAttribute("href")));
    check("no JavaScript: library and course bar links are plain links",
          hl.includes("ode/") && hl.includes("controls/") && cl.length === LECTURES.length && bl.includes("../../") && bl.includes("../stability-eigenvalues/"), [hl.length, cl.length, bl.length].join(","));
    await nojs.close();
  } finally {
    await browser.close();
    srv.stop();
  }
  const failed = results.filter(r => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} site checks passed. Screenshots: ${path.relative(PROJECT, SHOTS)}`);
  fs.mkdirSync(path.join(__dirname, "results"), { recursive: true });
  fs.writeFileSync(path.join(__dirname, "results", "site_browser_qa.json"), JSON.stringify(results, null, 1));
  process.exit(failed.length ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(2); });
