// Browser QA for the animation stage, media and themes, using installed Chrome + playwright-core.
// Usage (from the repository root): node qa/stage_qa.js
// Real playback of the pre-rendered ManimGL clips: Next/Back/Replay/Restart, end-of-clip boundary
// (no black gap, no jump back), rapid clicks, navigation and theme switches during playback,
// keyboard, completion, every clip decoding in Chrome, media failure fallbacks, reduced motion,
// theme default/persistence/storage failure, contrast, no CSS filters, overflow, screenshots.
// Screenshots: qa/screenshots/browser-redo, results: qa/results/browser-redo/stage_results.json.
"use strict";
const path = require("path");
const fs = require("fs");
const { DIST, recorder, startServer, launch, contrast } = require("./qa_common");

const SHOTS = path.join(__dirname, "screenshots", "browser-redo");
const RESULTS = path.join(__dirname, "results", "browser-redo");
fs.mkdirSync(SHOTS, { recursive: true });
fs.mkdirSync(RESULTS, { recursive: true });
const manifest = JSON.parse(fs.readFileSync(path.join(DIST, "animations", "manifest.json"), "utf8"));
const course = JSON.parse(fs.readFileSync(path.join(DIST, "course.json"), "utf8"));
const SEQ = Object.fromEntries(manifest.sequences.map(s => [s.id, s]));
const CH = SEQ.characteristic;
const { results, check } = recorder();
const shot = (page, name, full) => page.screenshot({ path: path.join(SHOTS, name + ".png"), fullPage: !!full });

let stopServer = () => {};
async function main() {
  const { base: BASE, stop } = await startServer(8791);
  stopServer = stop;
  const browser = await launch();
  const external = [];
  const errors = [];
  const allowedFailures = [];          // requests this script aborts on purpose
  async function newPage(opts, init) {
    const ctx = await browser.newContext(Object.assign({ viewport: { width: 1366, height: 900 } }, opts || {}));
    if (init) await ctx.addInitScript(init);
    const page = await ctx.newPage();
    page.on("console", m => {
      if (m.type() !== "error") return;
      const t = m.text();
      if (allowedFailures.some(a => t.includes(a) || /ERR_FAILED|ERR_ABORTED/.test(t))) return;
      errors.push(t);
    });
    page.on("pageerror", e => errors.push("pageerror: " + e.message));
    page.on("response", r => { if (r.status() >= 400) errors.push("HTTP " + r.status() + " " + r.url()); });
    page.on("request", r => { if (!r.url().startsWith(BASE) && !r.url().startsWith("data:")) external.push(r.url()); });
    return page;
  }
  const snap = p => p.evaluate(() => window.SecondOrderGuide.snapshot());
  const settled = (p, k, timeout) => p.waitForFunction(k => {
    const s = window.SecondOrderGuide.snapshot().player;
    const img = document.querySelector(".stage-still");
    return !s.playing && (k === undefined || s.k === k) && !s.videoVisible && img.complete && img.naturalWidth > 0;
  }, k, { timeout: timeout || 15000 });
  const stillName = s => (s.player.still || "").split("/").slice(-2).join("/");
  const startSampler = p => p.evaluate(() => {
    const st = document.querySelector(".stage"), v = st.querySelector(".stage-video"),
          im = st.querySelector(".stage-still"), fb = st.querySelector(".stage-fallback");
    window.__samples = []; window.__sampling = true;
    (function f() {
      if (!window.__sampling) return;
      const s = window.SecondOrderGuide.snapshot().player;
      window.__samples.push({ playing: s.playing, k: s.k, target: s.target, vOn: st.classList.contains("video-on"),
        vReady: v.readyState, vTime: v.currentTime, vSrc: v.getAttribute("src"), stillOk: im.complete && im.naturalWidth > 0,
        still: im.getAttribute("src"), fb: !fb.hidden });
      requestAnimationFrame(f);
    })();
  });
  const stopSampler = p => p.evaluate(() => { window.__sampling = false; return window.__samples; });
  // A frame is a gap when neither a decoded video frame nor a loaded still is visible.
  const gaps = samples => samples.filter(s => !(s.vOn && s.vReady >= 2) && !s.stillOk && !s.fb);

  // ------------------------------------------------------------------ manifest + assets over HTTP
  const seqs = manifest.sequences;
  check("manifest lists 9 sequences, every lesson 1-6 has one, every worked example has one",
        seqs.length === 9 && [1, 2, 3, 4, 5, 6].every(n => seqs.some(s => s.lesson === n)) &&
        course.examples.every(e => seqs.some(s => s.example === e.id)), seqs.map(s => s.id + "(" + s.steps.length + ")").join(" "));
  const metaProblems = [];
  for (const s of seqs) {
    if (!s.initial || !s.initial.tex || !s.initial.explanation || !s.initial.frame) metaProblems.push(s.id + " initial");
    s.steps.forEach((st, i) => {
      if (st.index !== i + 1 || !st.title || !st.tex || !st.explanation || !manifest.relations[st.relation] ||
          st.relationLabel !== manifest.relations[st.relation] || !st.initialFrame || !st.finalFrame)
        metaProblems.push(`${s.id}#${i + 1} fields`);
      const tr = st.transition;
      if (!tr || !tr.src || Math.abs(tr.duration - tr.frames / 60) > 1e-3 || tr.duration < 0.5 || tr.duration > 5)
        metaProblems.push(`${s.id}#${i + 1} transition ${tr && tr.duration}`);
      if (i > 0 && st.initialFrame !== s.steps[i - 1].finalFrame) metaProblems.push(`${s.id}#${i + 1} chain`);
    });
    if (s.steps[0].initialFrame !== s.initial.frame) metaProblems.push(s.id + " first frame");
  }
  check("every step has title, relation, equation, explanation, initial/final frame and a 0.5-5 s clip; frames chain",
        metaProblems.length === 0, metaProblems.slice(0, 5).join("; "));
  const httpBad = [];
  for (const s of seqs) {
    const urls = [s.initial.frame, ...s.steps.flatMap(st => [st.finalFrame, st.transition.src])];
    for (const u of urls) {
      const r = await fetch(BASE + u, { headers: { Range: "bytes=0-1" } });
      const ct = r.headers.get("content-type");
      if (!(r.status === 206 || r.status === 200) || !(u.endsWith(".mp4") ? ct === "video/mp4" : ct === "image/jpeg")) httpBad.push(u + " " + r.status + " " + ct);
    }
  }
  check("every clip and still is served with the right type (byte ranges for clips)", httpBad.length === 0, httpBad.slice(0, 3).join("; "));

  // ------------------------------------------------------------------ desktop, dark system theme
  const page = await newPage({ colorScheme: "dark" });
  await page.goto(BASE, { waitUntil: "networkidle" });
  await settled(page, 0);
  let s = await snap(page);
  const land = await page.evaluate(() => {
    const st = document.querySelector(".stage").getBoundingClientRect();
    const ctl = document.querySelector(".stage-controls").getBoundingClientRect();
    const panel = document.querySelector(".step-panel").getBoundingClientRect();
    return { top: st.top, bottom: st.bottom, width: st.width, ctlBottom: ctl.bottom, panelTop: panel.top, vh: innerHeight,
             bg: getComputedStyle(document.querySelector(".stage")).backgroundColor,
             h1: document.querySelector("h1").textContent };
  });
  check("default landing: characteristic derivation on a large stage fully above the fold, controls visible",
        s.player.seq === "characteristic" && s.player.k === 0 && land.top >= 0 && land.ctlBottom <= land.vh &&
        land.width >= 640 && /Watch the derivations/.test(land.h1), JSON.stringify(land));
  check("default theme follows a dark system preference; stage canvas is near-black",
        s.theme === "dark" && land.bg === "rgb(11, 15, 23)", s.theme + " " + land.bg);
  check("opening state: still state-00, Back/Replay/Restart disabled, Next labelled 'Next step'",
        stillName(s) === "characteristic/state-00.jpg" &&
        await page.$eval("[data-action=back]", b => b.disabled) && await page.$eval("[data-action=replay]", b => b.disabled) &&
        await page.$eval("[data-action=restart]", b => b.disabled) &&
        (await page.getAttribute("[data-action=next]", "aria-label")) === "Next step", stillName(s));
  check("next clip is preloaded into the single video element while idle; only one video element on the page",
        s.player.video === CH.steps[0].transition.src && (await page.$$("video")).length === 1, s.player.video);
  await shot(page, "stage_dark_initial");

  // real playback of step 1 with a per-frame gap sampler
  await startSampler(page);
  await page.click("[data-action=next]");
  s = await snap(page);
  check("Next starts the step-1 transition and marks Next busy (aria-disabled)",
        s.player.playing && s.player.target === 1 && (await page.getAttribute("[data-action=next]", "aria-disabled")) === "true");
  await page.waitForFunction(d => { const v = document.querySelector(".stage-video"); return v.currentTime > d * 0.45; },
                             CH.steps[0].transition.duration, { timeout: 15000 });
  await shot(page, "stage_dark_mid");
  await settled(page, 1);
  await page.waitForTimeout(300);
  let samples = await stopSampler(page);
  s = await snap(page);
  const vTimes = samples.filter(x => x.vOn).map(x => x.vTime);
  const afterEnd = samples.filter(x => !x.playing && samples.indexOf(x) > samples.findIndex(y => y.playing));
  check("the clip really plays (video visible, time advances through the clip)",
        vTimes.length > 20 && Math.max(...vTimes) > CH.steps[0].transition.duration - 0.2 && new Set(vTimes.map(t => t.toFixed(2))).size > 15,
        `${vTimes.length} visible frames, max t ${Math.max(...vTimes).toFixed(2)} / ${CH.steps[0].transition.duration}`);
  check("no frame without picture during start, playback and hand-over (video or loaded still always shown)",
        gaps(samples).length === 0, `${samples.length} frames sampled, ${gaps(samples).length} gaps`);
  check("hand-over keeps the final state: after the clip ends only the step-1 still is shown (no jump back)",
        afterEnd.length > 0 && afterEnd.every(x => x.vOn || x.still === CH.steps[0].finalFrame) &&
        afterEnd.filter(x => !x.vOn).every(x => x.still === CH.steps[0].finalFrame),
        afterEnd.length + " frames after end");
  check("completed step: k=1, still state-01, video hidden, next clip preloaded, panel shows step 1",
        s.player.k === 1 && stillName(s) === "characteristic/state-01.jpg" && !s.player.videoVisible &&
        s.player.video === CH.steps[1].transition.src &&
        (await page.textContent(".step-count")) === "Step 1 of " + CH.steps.length, JSON.stringify(s.player));
  check("panel explains the transition with its relation label and typeset equation",
        (await page.textContent(".relation-badge")) === CH.steps[0].relationLabel &&
        (await page.$$(".step-eq .katex")).length === 1 && (await page.$$(".step-panel .katex-error")).length === 0);
  await shot(page, "stage_dark_final");
  await page.waitForTimeout(700);
  check("state stays put after the clip ends (no stale ended/timeupdate effects)", (await snap(page)).player.k === 1);

  // Back / Replay / Restart
  await page.click("[data-action=back]");
  await settled(page, 0);
  s = await snap(page);
  check("Back returns to the previous stable state without animating", s.player.k === 0 && !s.player.videoVisible &&
        stillName(s) === "characteristic/state-00.jpg");
  await page.click("[data-action=next]");
  await settled(page, 1);
  await page.click("[data-action=replay]");
  s = await snap(page);
  const replayStarted = s.player.playing && s.player.target === 1;
  await page.waitForFunction(() => window.SecondOrderGuide.snapshot().player.videoVisible, null, { timeout: 15000 });
  await settled(page, 1);
  check("Replay plays the current step's transition again and ends on the same state", replayStarted &&
        (await snap(page)).player.k === 1);
  await page.click("[data-action=restart]");
  await settled(page, 0);
  check("Restart returns to the opening still", (await snap(page)).player.k === 0);

  // rapid clicks
  await page.dblclick("[data-action=next]");
  await settled(page);
  check("double-clicking Next plays one transition only", (await snap(page)).player.k === 1, "k = " + (await snap(page)).player.k);
  await page.evaluate(() => { const b = document.querySelector("[data-action=next]"); b.click(); b.click(); b.click(); });
  await settled(page);
  check("three clicks in one tick still advance one step", (await snap(page)).player.k === 2, "k = " + (await snap(page)).player.k);
  await page.click("[data-action=next]");
  await page.waitForTimeout(250);
  await page.click("[data-action=back]");
  s = await snap(page);
  check("Back during playback stops at the state before the transition", !s.player.playing && s.player.k === 2 && !s.player.videoVisible);
  await page.waitForTimeout(CH.steps[2].transition.duration * 1000 + 800);
  check("…and the interrupted clip's late events change nothing", (await snap(page)).player.k === 2);
  await page.click("[data-action=next]");
  await page.waitForTimeout(150);
  await page.click("[data-action=replay]");
  await page.waitForTimeout(100);
  await page.click("[data-action=replay]");
  await settled(page);
  s = await snap(page);
  check("repeated Replay during playback ends cleanly on the same step", s.player.k === 3 && !s.player.playing, "k = " + s.player.k);

  // theme switch during playback
  await page.click("[data-action=next]");
  await page.waitForTimeout(200);
  await page.click("#theme-toggle");
  const midTheme = await snap(page);
  await settled(page);
  s = await snap(page);
  check("switching theme during playback keeps playing and finishes the step",
        midTheme.player.playing && midTheme.theme === "light" && s.player.k === 4 && s.theme === "light");
  await page.click("#theme-toggle");

  // route change during playback commits the step
  await page.click("[data-action=next]");
  await page.waitForTimeout(200);
  await page.evaluate(() => { location.hash = "#explorer"; });
  await page.waitForSelector("#plot .curve");
  s = await snap(page);
  check("leaving the page during playback commits the requested step and stops playback",
        !s.player.playing && s.steps.characteristic === 5);
  await page.evaluate(() => { location.hash = "#watch"; });
  await settled(page, 5);
  s = await snap(page);
  check("returning shows the same derivation at the same step", s.player.seq === "characteristic" && s.player.k === 5 &&
        stillName(s) === "characteristic/state-05.jpg");

  // keyboard
  await page.click("h1");
  await page.keyboard.press("ArrowRight");
  await settled(page, 6);
  await page.keyboard.press("b");
  await settled(page, 5);
  await page.keyboard.press("n");
  await settled(page, 6);
  const kBeforeAlt = (await snap(page)).player.k;
  await page.evaluate(() => document.body.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowLeft", altKey: true, bubbles: true })));
  await page.waitForTimeout(200);
  s = await snap(page);
  check("keyboard: → / N next, B back; Alt+arrow (browser navigation) is ignored by the stage",
        kBeforeAlt === 6 && s.player.k === 6 && !s.player.playing, "k = " + s.player.k);
  await page.keyboard.press("r");
  const kr = (await snap(page)).player;
  await settled(page, 6);
  check("keyboard: R replays the current step", kr.playing && kr.target === 6);

  // completion
  check("final step shows the completion box and Next becomes 'Next derivation'",
        await page.isVisible(".complete-box") && /^Next derivation/.test(await page.getAttribute("[data-action=next]", "aria-label")),
        await page.getAttribute("[data-action=next]", "aria-label"));
  await shot(page, "stage_dark_complete");
  await page.click("[data-action=next-seq]");
  await settled(page, 0);
  s = await snap(page);
  check("'Next derivation' loads the next sequence at its start and updates the address",
        s.player.seq === "ivp-distinct" && page.url().endsWith("#watch/ivp-distinct"), page.url());

  // every clip decodes in Chrome with the manifest duration
  const decode = await page.evaluate(async seqs => {
    const bad = [];
    let n = 0;
    for (const sq of seqs) {
      for (const st of sq.steps) {
        const v = document.createElement("video");
        v.muted = true; v.preload = "auto"; v.src = st.transition.src;
        const ok = await new Promise(res => {
          const t = setTimeout(() => res("timeout"), 10000);
          v.addEventListener("loadeddata", () => { clearTimeout(t); res("ok"); }, { once: true });
          v.addEventListener("error", () => { clearTimeout(t); res("error"); }, { once: true });
        });
        n++;
        if (ok !== "ok" || Math.abs(v.duration - st.transition.duration) > 0.03 || v.videoWidth !== 1280 || v.videoHeight !== 720)
          bad.push(`${st.transition.src}: ${ok} ${v.duration} ${v.videoWidth}x${v.videoHeight}`);
        v.removeAttribute("src"); v.load();
      }
      for (const src of [sq.initial.frame, ...sq.steps.map(st => st.finalFrame)]) {
        const im = new Image(); im.src = src;
        try { await im.decode(); if (im.naturalWidth !== 1280 || im.naturalHeight !== 720) bad.push(src + " size"); }
        catch (e) { bad.push(src + " decode"); }
      }
    }
    return { n, bad };
  }, manifest.sequences);
  check(`all ${decode.n} clips decode in Chrome at 1280x720 with the manifest duration; all stills decode`,
        decode.bad.length === 0, decode.bad.slice(0, 3).join("; "));

  // lesson pages, deep links
  await page.goto(BASE + "#lesson-3");
  await settled(page);
  const tabs = await page.$$eval(".seq-tab", b => b.map(x => x.getAttribute("data-seq")));
  await page.click(".seq-tab[data-seq=ivp-complex]");
  await settled(page);
  s = await snap(page);
  check("lesson 3 offers its three IVP derivations as tabs; choosing one switches the stage and the address",
        tabs.join() === "ivp-distinct,ivp-repeated,ivp-complex" && s.player.seq === "ivp-complex" &&
        page.url().endsWith("#lesson-3/ivp-complex") &&
        (await page.getAttribute(".seq-tab[data-seq=ivp-complex]", "aria-pressed")) === "true");
  const links = {};
  for (const h of ["#lesson-1", "#lesson-2", "#lesson-4", "#lesson-5", "#lesson-6", "#lesson-4/resonance", "#watch/damping",
                   "#explorer", "#quiz", "#reading", "#nonsense", "#lesson-9", "#lesson-3/bogus"]) {
    await page.goto(BASE + h);
    await page.waitForSelector("h1");
    await page.waitForTimeout(120);
    const r = await page.evaluate(() => ({ h1: document.querySelector("h1").textContent,
      seq: document.querySelector(".stage-wrap") ? window.SecondOrderGuide.snapshot().player.seq : null }));
    links[h] = r;
  }
  check("deep links resolve: lessons show their own derivation, #lesson-4/resonance and #watch/damping select it, " +
        "practice routes work, unknown routes fall back to the start page",
        links["#lesson-1"].seq === "normal-form" && links["#lesson-2"].seq === "characteristic" &&
        links["#lesson-4"].seq === "forced-exp" && links["#lesson-5"].seq === "damping" && links["#lesson-6"].seq === "cauchy-euler" &&
        links["#lesson-4/resonance"].seq === "resonance" && links["#watch/damping"].seq === "damping" &&
        links["#explorer"].seq === null && links["#quiz"].h1 === "Quiz" && /Where to read/.test(links["#reading"].h1) &&
        /Watch the derivations/.test(links["#nonsense"].h1) && /Watch the derivations/.test(links["#lesson-9"].h1) &&
        links["#lesson-3/bogus"].h1 === course.lessons[2].title &&
        ["ivp-distinct", "ivp-repeated", "ivp-complex"].includes(links["#lesson-3/bogus"].seq),
        Object.entries(links).map(([k, v]) => k + "→" + (v.seq || v.h1.slice(0, 12))).join(" "));
  await page.goto(BASE + "#lesson-2");
  await settled(page);
  check("progress is remembered per derivation across routes", (await snap(page)).player.k === 6);

  // theme visibility (dark), explorer + quiz screenshots
  async function contrastReport(p) {
    return p.evaluate(() => {
      // Effective background: composite every (possibly translucent) background layer from the
      // element up to the first opaque one.
      const parse = c => { const n = (c.match(/[\d.]+/g) || []).map(Number); return [n[0] || 0, n[1] || 0, n[2] || 0, n.length > 3 ? n[3] : 1]; };
      const bgOf = el => {
        const layers = [];
        for (let e = el; e; e = e.parentElement) {
          const c = parse(getComputedStyle(e).backgroundColor);
          if (c[3] > 0) { layers.push(c); if (c[3] >= 1) break; }
        }
        if (!layers.length || layers[layers.length - 1][3] < 1) layers.push(parse(getComputedStyle(document.documentElement).backgroundColor || "rgb(255,255,255)").slice(0, 3).concat([1]));
        let [r, g, b] = layers.pop();
        while (layers.length) {
          const [r2, g2, b2, a] = layers.pop();
          r = r2 * a + r * (1 - a); g = g2 * a + g * (1 - a); b = b2 * a + b * (1 - a);
        }
        return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`;
      };
      const pick = sel => Array.from(document.querySelectorAll(sel)).filter(e => e.offsetParent !== null).slice(0, 3);
      const sels = ["h1", ".summary", ".chapter-list a", ".btn", ".btn.primary", ".step-expl", ".step-count", ".relation-badge",
                    ".key-hint", ".eyebrow", ".site-footer p", ".choice", ".feedback", ".tick-label", ".readouts dd", ".policy",
                    ".lesson-section p", ".note", ".seq-tab", ".pl-meta", ".theme-label"];
      const out = [];
      for (const sel of sels) for (const el of pick(sel)) {
        const cs = getComputedStyle(el);
        const fg = el instanceof SVGElement ? cs.fill : cs.color;
        out.push({ sel, fg, bg: bgOf(el instanceof SVGElement ? el.closest(".plot-card") : el) });
      }
      return out;
    });
  }
  const lowContrast = [];
  async function auditContrast(p, label) {
    for (const r of await contrastReport(p)) {
      const c = contrast(r.fg, r.bg);
      if (c < 4.5) lowContrast.push(`${label} ${r.sel} ${c.toFixed(2)}`);
    }
  }
  await auditContrast(page, "dark watch");
  await page.goto(BASE + "#lesson-2");
  await settled(page);
  await auditContrast(page, "dark lesson");
  await page.goto(BASE + "#explorer");
  await page.waitForSelector("#plot .curve");
  await page.focus("#s-b");
  await page.keyboard.press("Home");
  await auditContrast(page, "dark explorer");
  await shot(page, "explorer_dark");
  const exBefore = (await snap(page)).explorer;
  const curveBefore = await page.getAttribute("#plot .curve", "d");
  await page.click("#theme-toggle");
  await page.click("#theme-toggle");
  check("theme switches keep explorer coefficients and the plotted curve", JSON.stringify((await snap(page)).explorer) === JSON.stringify(exBefore) &&
        (await page.getAttribute("#plot .curve", "d")) === curveBefore, JSON.stringify(exBefore));
  await page.goto(BASE + "#quiz");
  await page.waitForSelector(".choice");
  await page.click(`.choice[data-index='${(course.quiz[0].answer + 1) % 4}']`);
  await auditContrast(page, "dark quiz");
  await shot(page, "quiz_dark");
  const quizBefore = JSON.stringify((await snap(page)).quiz);
  await page.click("#theme-toggle");
  check("theme switch keeps quiz answers", JSON.stringify((await snap(page)).quiz) === quizBefore);
  await page.click("#theme-toggle");

  // ------------------------------------------------------------------ light system theme + persistence
  const lp = await newPage({ colorScheme: "light" }, () => {
    document.addEventListener("readystatechange", () => {
      if (document.readyState === "interactive" && !window.__themeAtInteractive)
        window.__themeAtInteractive = document.documentElement.getAttribute("data-theme");
    });
  });
  await lp.goto(BASE, { waitUntil: "networkidle" });
  await settled(lp, 0);
  s = await snap(lp);
  check("default theme follows a light system preference when nothing is saved",
        s.theme === "light" && (await lp.getAttribute("#theme-toggle", "aria-pressed")) === "false");
  const stageBgLight = await lp.$eval(".stage", e => getComputedStyle(e).backgroundColor);
  const filters = await lp.evaluate(() => {
    const els = [document.querySelector(".stage"), document.querySelector(".stage-still"), document.querySelector(".stage-video"),
                 ...Array.from(document.querySelectorAll(".stage-col, .stage-grid, .stage-wrap, main, body, html"))];
    return els.map(e => getComputedStyle(e).filter + "|" + getComputedStyle(e).mixBlendMode).filter(f => f !== "none|normal");
  });
  check("light theme keeps the near-black stage and applies no CSS filter/blend to the video or stills",
        stageBgLight === "rgb(11, 15, 23)" && filters.length === 0, stageBgLight + " " + filters.join(","));
  await shot(lp, "stage_light_initial");
  await lp.click("[data-action=next]");
  await lp.waitForFunction(d => document.querySelector(".stage-video").currentTime > d * 0.45, CH.steps[0].transition.duration);
  await shot(lp, "stage_light_mid");
  await settled(lp, 1);
  await shot(lp, "stage_light_final");
  await auditContrast(lp, "light watch");
  await lp.click("#theme-toggle");
  check("toggle switches to dark and saves the choice", (await snap(lp)).theme === "dark" &&
        (await lp.evaluate(() => localStorage.getItem("sode-theme"))) === "dark" &&
        (await lp.getAttribute("#theme-toggle", "aria-pressed")) === "true");
  await lp.reload({ waitUntil: "networkidle" });
  await settled(lp);
  const atInteractive = await lp.evaluate(() => window.__themeAtInteractive);
  check("saved theme survives reload and is applied before the app script runs (no flash)",
        (await snap(lp)).theme === "dark" && atInteractive === "dark", "at interactive: " + atInteractive);
  await lp.goto(BASE + "#quiz");
  await lp.waitForSelector(".choice");
  check("saved theme persists across routes", (await snap(lp)).theme === "dark");
  await lp.click("#theme-toggle");
  await lp.goto(BASE + "#lesson-5");
  await settled(lp);
  await auditContrast(lp, "light lesson");
  await lp.goto(BASE + "#explorer");
  await lp.waitForSelector("#plot .curve");
  await auditContrast(lp, "light explorer");
  await shot(lp, "explorer_light");
  await lp.goto(BASE + "#quiz");
  await lp.waitForSelector(".choice");
  await lp.click(`.choice[data-index='${course.quiz[0].answer}']`);
  await auditContrast(lp, "light quiz");
  await shot(lp, "quiz_light");
  check("text contrast is at least 4.5:1 in both themes (headings, nav, buttons, panel, notes, quiz feedback, plot labels)",
        lowContrast.length === 0, lowContrast.slice(0, 6).join("; "));

  // ------------------------------------------------------------------ storage denied
  const sp = await newPage({ colorScheme: "dark" }, () => {
    Object.defineProperty(window, "localStorage", { configurable: true, get() { throw new DOMException("denied", "SecurityError"); } });
  });
  await sp.goto(BASE, { waitUntil: "networkidle" });
  await settled(sp, 0);
  await sp.click("#theme-toggle");
  await sp.waitForTimeout(150);
  s = await snap(sp);
  const status = await sp.textContent("#app-status");
  await sp.goto(BASE + "#quiz");
  await sp.waitForSelector(".choice");
  check("with storage denied the page loads from the system theme, the toggle still works for the visit and says so",
        s.theme === "light" && !s.themeStorageOk && /this visit only/.test(status) && (await snap(sp)).theme === "light", status);

  // ------------------------------------------------------------------ reduced motion
  const rm = await newPage({ colorScheme: "dark", reducedMotion: "reduce" });
  await rm.goto(BASE, { waitUntil: "networkidle" });
  await settled(rm, 0);
  await startSampler(rm);
  await rm.click("[data-action=next]");
  await settled(rm, 1, 3000);
  samples = await stopSampler(rm);
  check("reduced motion: Next shows the step's final state at once, without playing the clip, and says how to replay",
        samples.every(x => !x.vOn) && /Replay/.test(await rm.textContent(".stage-notice")) && (await snap(rm)).player.k === 1);
  await shot(rm, "stage_reduced_motion");
  await rm.click("[data-action=replay]");
  await rm.waitForFunction(() => window.SecondOrderGuide.snapshot().player.videoVisible, null, { timeout: 15000 });
  await settled(rm, 1);
  check("reduced motion: Replay still plays the real animation on request", true);
  await rm.goto(BASE + "#lesson-6");
  await settled(rm, 0);
  for (let i = 0; i < SEQ["cauchy-euler"].steps.length; i++) await rm.click("[data-action=next]");
  await settled(rm, SEQ["cauchy-euler"].steps.length);
  check("last derivation's completion offers the quiz", /quiz/i.test(await rm.getAttribute("[data-action=next]", "aria-label")));
  await rm.click("[data-action=next]");
  await rm.waitForSelector(".choice");
  check("…and goes there", rm.url().endsWith("#quiz"));

  // every step's panel equation fits (desktop) — walk all 63 steps with reduced motion
  const fitDesk = await walkAll(rm);
  check("desktop: every step's panel equation wraps to fit (no horizontal scroll in the panel)", fitDesk.length === 0, fitDesk.slice(0, 4).join("; "));

  // ------------------------------------------------------------------ media failures
  const vf = await newPage({ colorScheme: "dark" });
  allowedFailures.push("characteristic/step-01.mp4", "characteristic/state-00.jpg");
  await vf.route("**/characteristic/step-01.mp4", r => r.abort());
  await vf.goto(BASE + "#watch/characteristic");
  await settled(vf, 0);
  const t0 = Date.now();
  await vf.click("[data-action=next]");
  await settled(vf, 1, 20000);
  s = await snap(vf);
  check("clip failure: the step still completes with its still, a visible notice, and usable controls",
        s.player.k === 1 && stillName(s) === "characteristic/state-01.jpg" && /could not be played/.test(s.player.notice) &&
        (await vf.getAttribute("[data-action=next]", "aria-disabled")) === "false", `${Date.now() - t0} ms`);
  await shot(vf, "stage_video_failure");
  await vf.click("[data-action=next]");
  await settled(vf, 2);
  check("…and the next (working) clip plays normally afterwards", (await snap(vf)).player.k === 2);
  const sf = await newPage({ colorScheme: "light" });
  await sf.route("**/characteristic/state-00.jpg", r => r.abort());
  await sf.goto(BASE + "#watch/characteristic");
  await sf.waitForFunction(() => !document.querySelector(".stage-fallback").hidden, null, { timeout: 10000 });
  check("still failure: the stage shows the typeset equation instead", (await sf.$$(".stage-fallback .katex")).length === 1);
  await shot(sf, "stage_still_failure");

  // ------------------------------------------------------------------ mobile
  for (const scheme of ["dark", "light"]) {
    const mob = await newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2, colorScheme: scheme });
    await mob.goto(BASE, { waitUntil: "networkidle" });
    await settled(mob, 0);
    const lay = await mob.evaluate(() => {
      const st = document.querySelector(".stage").getBoundingClientRect();
      const nb = document.querySelector("[data-action=next]").getBoundingClientRect();
      return { overflow: document.documentElement.scrollWidth - innerWidth, stageW: st.width, stageBottom: st.bottom,
               nextBottom: nb.bottom, nextH: nb.height, vh: innerHeight };
    });
    check(`mobile ${scheme}: stage spans the width, Next is reachable above the fold, no sideways scroll`,
          lay.overflow <= 1 && lay.stageW >= 340 && lay.nextBottom <= lay.vh && lay.nextH >= 44, JSON.stringify(lay));
    await mob.locator("[data-action=next]").tap();
    await settled(mob, 1);
    check(`mobile ${scheme}: tapping Next plays and completes a step`, (await snap(mob)).player.k === 1);
    await shot(mob, `mobile_${scheme}_watch`);
    if (scheme === "light") {
      await mob.goto(BASE + "#lesson-4/resonance");
      await settled(mob);
      await shot(mob, "mobile_light_lesson4", true);
    }
    const ovr = [];
    for (const r of ["watch", "lesson-1", "lesson-2", "lesson-3", "lesson-4", "lesson-5", "lesson-6", "explorer", "quiz", "reading"]) {
      await mob.goto(BASE + "#" + r);
      await mob.waitForSelector("h1");
      await mob.waitForTimeout(150);
      const o = await mob.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      if (o > 1) ovr.push(r + ":" + o);
    }
    check(`mobile ${scheme}: no horizontal overflow on any route`, ovr.length === 0, ovr.join(" "));
  }
  const mrm = await newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  await mrm.goto(BASE, { waitUntil: "networkidle" });
  await settled(mrm, 0);
  const fitMob = await walkAll(mrm);
  check("mobile: every step's panel equation wraps to fit a 390px screen", fitMob.length === 0, fitMob.slice(0, 4).join("; "));
  const fsOk = await mrm.evaluate(() => typeof document.querySelector(".stage-col").requestFullscreen === "function" &&
                                        !!document.querySelector(".stage-fs[aria-label='Full screen']"));
  check("a full-screen button is offered for the stage", fsOk);

  check("no requests to any non-local host", external.length === 0, external.slice(0, 3).join(" "));
  check("no console or page errors (other than the deliberately aborted requests)", errors.length === 0, errors.slice(0, 3).join(" | "));

  await browser.close();
  stop();
  fs.writeFileSync(path.join(RESULTS, "stage_results.json"), JSON.stringify({ base: BASE, results, lowContrast }, null, 2));
  const failed = results.filter(r => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} stage, media and theme checks passed`);
  process.exit(failed.length ? 1 : 0);

  // Step through every sequence (reduced motion: instant) and report panel equations that overflow.
  async function walkAll(p) {
    const bad = [];
    for (const sq of manifest.sequences) {
      await p.goto(BASE + "#watch/" + sq.id);
      await settled(p);
      // Restart only when the derivation is not already at its opening state: clicking the
      // disabled button would make Playwright wait out its 30 s actionability timeout.
      if ((await snap(p)).player.k > 0) await p.click("[data-action=restart]");
      await settled(p, 0);
      for (let k = 0; k <= sq.steps.length; k++) {
        if (k > 0) { await p.click("[data-action=next]"); await settled(p, k, 3000); }
        await p.waitForTimeout(40);
        const o = await p.evaluate(() => {
          const e = document.querySelector(".step-eq");
          return { over: e.scrollWidth - e.clientWidth, page: document.documentElement.scrollWidth - innerWidth };
        });
        if (o.over > 1 || o.page > 1) bad.push(`${sq.id}#${k} panel+${o.over} page+${o.page}`);
      }
    }
    return bad;
  }
}

main().catch(e => { console.error(e); stopServer(); process.exit(2); });
