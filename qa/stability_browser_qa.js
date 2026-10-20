// Browser checks for the Stability and Eigenvalues study companion (installed Chrome via playwright-core).
//
//   node qa\stability_browser_qa.js
//
// Starts courses/controls/stability-eigenvalues/server.py on a free loopback port (identity confirmed by nonce, no OPENAI_*
// variables), then checks: every section renders with typeset math and no overflow; every sequence (both in
// Section 3) plays through to its final step with the correct stills; back/replay/restart and saved step;
// source and book links; the explorer (kinds, presets and their verdicts, slider redraw, off-scale clipping notes,
// play to the end, navigation cancels playback, save/restore, invalid saved state rejected); the quiz (retry,
// first-try score); the tutor's missing-key state and step-aware context; mobile, light/dark and reduced motion.
// Screenshots go to qa/screenshots/stability-eigenvalues, results to qa/results/stability_browser.json.
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");

const PROJECT = path.dirname(__dirname);
const PKG = path.join(PROJECT, "courses/controls/stability-eigenvalues");
const DIST = path.join(PKG, "dist");
const CHROME = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PY = [path.join(PROJECT, ".venv", "Scripts", "python.exe")].find(p => fs.existsSync(p)) || "python";
const { chromium } = require(path.join(__dirname, "tooling", "node_modules", "playwright-core"));
const manifest = JSON.parse(fs.readFileSync(path.join(DIST, "animations", "manifest.json"), "utf8"));
const course = JSON.parse(fs.readFileSync(path.join(DIST, "course.json"), "utf8"));
const SHOTS = path.join(PROJECT, "qa", "screenshots", "stability-eigenvalues");
fs.mkdirSync(SHOTS, { recursive: true });
const STORE = "stability-eigenvalues-v1";
const VERDICT_KIND = { asymptotic: "stable", lyapunov: "marginal", unstable: "unstable" };
const seqById = Object.fromEntries(manifest.sequences.map(s => [s.id, s]));

const results = [];
function check(name, ok, detail) {
  results.push({ check: name, ok: !!ok, detail: detail === undefined ? "" : String(detail) });
  console.log((ok ? "PASS " : "FAIL ") + name + (detail !== undefined && detail !== "" ? "  [" + detail + "]" : ""));
  return !!ok;
}

function startServer() {
  const portFile = path.join(os.tmpdir(), "se-qa-port-" + process.pid + "-" + Date.now() + ".txt");
  const nonce = "qa-" + process.pid + "-" + Date.now();
  const env = Object.assign({}, process.env);
  Object.keys(env).forEach(k => { if (/^OPENAI_/.test(k)) delete env[k]; });
  const proc = spawn(PY, ["-I", path.join(PKG, "server.py"), "--port", "8792", "--port-file", portFile, "--nonce", nonce],
                     { stdio: ["ignore", "pipe", "pipe"], env });
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    (function poll() {
      if (fs.existsSync(portFile)) {
        const port = fs.readFileSync(portFile, "utf8").trim();
        fetch(`http://127.0.0.1:${port}/__control_health`).then(r => r.json()).then(j => {
          if (j.app !== "Study_stability_eigenvalues" || j.nonce !== nonce) return reject(new Error("health mismatch " + JSON.stringify(j)));
          resolve({ base: `http://127.0.0.1:${port}/`, stop: () => { try { process.kill(j.pid); } catch (e) { /* gone */ }
                                                                       try { proc.kill(); } catch (e) { /* gone */ }
                                                                       try { fs.unlinkSync(portFile); } catch (e) { /* gone */ } } });
        }).catch(() => setTimeout(poll, 150));
      } else if (Date.now() - t0 > 15000) reject(new Error("server did not start"));
      else setTimeout(poll, 150);
    })();
  });
}

async function newPage(browser, opts) {
  const ctx = await browser.newContext(Object.assign({ viewport: { width: 1440, height: 900 } }, opts || {}));
  await ctx.addInitScript(() => {
    const play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () { this.playbackRate = 4; return play.call(this); };
    window.__studyExplorerSpeed = 6;
  });
  const page = await ctx.newPage();
  page.errors = [];
  page.on("console", m => { if (m.type() === "error") page.errors.push(m.text()); });
  page.on("pageerror", e => page.errors.push("pageerror: " + e.message));
  return { ctx, page };
}

async function waitStep(page, k, timeout) {
  await page.waitForFunction(k => {
    const w = document.querySelector(".stage-wrap"), img = document.querySelector(".stage-still");
    return w && w.dataset.playing === "false" && w.dataset.step === String(k) && img.complete && img.naturalWidth > 0 &&
      !document.querySelector(".stage").classList.contains("video-on");
  }, k, { timeout: timeout || 30000 });
}
const still = page => page.evaluate(() => document.querySelector(".stage-still").getAttribute("src"));
const frameOf = (sq, k) => k === 0 ? sq.initial.frame : sq.steps[k - 1].finalFrame;
const noOverflow = page => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
const katexErrors = page => page.evaluate(() => document.querySelectorAll(".katex-error").length);
async function clickIfReady(page, sel) {   // optional controls: no 30 s timeout when absent or disabled
  const el = await page.$(sel);
  if (el && await el.isVisible() && await el.isEnabled()) { await el.click(); return true; }
  return false;
}
const setRange = (page, id, v) => page.$eval(id, (el, v) => { el.value = String(v); el.dispatchEvent(new Event("input", { bubbles: true })); }, v);

async function go(page, base, hash) {
  await page.goto(base + "#" + hash);
  await page.waitForFunction(() => !document.querySelector(".loading-note"), null, { timeout: 15000 });
  await page.waitForTimeout(150);
}

async function playThrough(page, sq) {
  await waitStep(page, 0);
  check(`${sq.id}: opening still`, (await still(page)) === frameOf(sq, 0));
  let ok = true, bad = "";
  for (let k = 1; k <= sq.steps.length; k++) {
    await page.click('[data-action="next"]');
    await waitStep(page, k);
    const s = await still(page);
    if (s !== frameOf(sq, k)) { ok = false; bad = `step ${k}: ${s}`; break; }
  }
  check(`${sq.id}: plays through all ${sq.steps.length} steps with the right stills`, ok, bad);
  const state = await page.evaluate(() => document.querySelector(".stage").dataset.state);
  check(`${sq.id}: reaches the complete state`, state === "complete", state);
}

async function main() {
  const srv = await startServer();
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
  try {
    const { ctx, page } = await newPage(browser);
    const base = srv.base;

    // ---- sections and every sequence
    for (const sec of course.sections) {
      await go(page, base, sec.id);
      const h1 = await page.textContent("h1");
      check(`${sec.id}: page renders "${h1.slice(0, 50)}"`, h1 && h1.length > 3);
      const seqs = manifest.sequences.filter(s => s.section === sec.number);
      for (const sq of seqs) {
        const btn = await page.$(`.seq-btn[data-seq="${sq.id}"]`);
        if (btn) { await btn.click(); await page.waitForTimeout(200); }
        check(`${sq.id}: selected on its section page`, (await page.evaluate(() => document.querySelector(".stage-wrap").dataset.seq)) === sq.id);
        await playThrough(page, sq);
        await page.screenshot({ path: path.join(SHOTS, `desktop-${sec.id}-${sq.id}-final.png`) });
      }
      check(`${sec.id}: math typesets without KaTeX errors`, (await katexErrors(page)) === 0);
      check(`${sec.id}: no horizontal overflow (desktop)`, await noOverflow(page));
      const ex = await page.$$('[data-action]');
      check(`${sec.id}: worked example and controls present`, ex.length > 4 && /authored/i.test(await page.textContent("#view")));
    }

    // ---- controls on section 5: back, replay, restart, persistence, tutor
    const pw = seqById["powers-unit-circle"];
    await go(page, base, "s5");
    if (!(await clickIfReady(page, '[data-action="restart-complete"]'))) await clickIfReady(page, '[data-action="restart"]');
    await waitStep(page, 0);
    await page.click('[data-action="next"]'); await waitStep(page, 1);
    await page.click('[data-action="next"]'); await waitStep(page, 2);
    await page.click('[data-action="back"]'); await waitStep(page, 1);
    check("controls: back returns to the previous stable still", (await still(page)) === frameOf(pw, 1));
    await page.click('[data-action="replay"]'); await waitStep(page, 1);
    check("controls: replay ends on the same step", (await still(page)) === frameOf(pw, 1));
    await page.reload(); await page.waitForTimeout(400); await waitStep(page, 1);
    check("progress: step position restored after reload", (await page.evaluate(() => document.querySelector(".stage-wrap").dataset.step)) === "1");
    const label = await page.evaluate(() => { document.getElementById("tutor-toggle").click(); return new Promise(r => setTimeout(() => r(document.querySelector(".tutor-context") ? document.querySelector(".tutor-context").textContent : ""), 300)); });
    check("tutor: context label names the section and step", /Section 5/.test(label) && /step 1 of 6/.test(label), label.slice(0, 90));
    const tutorText = await page.textContent("#tutor");
    check("tutor: missing-key state explained, no chat sent", /OPENAI_API_KEY/.test(tutorText) && /not set up/i.test(tutorText), tutorText.replace(/\s+/g, " ").slice(0, 120));
    await page.evaluate(() => document.getElementById("tutor-toggle").click());

    // ---- source links: lecture times and book pages
    const links = await page.$$eval(".sources-list a", as => as.map(a => a.href));
    check("s5: lecture links point at h7nJ6ZL4Lf0 with the slip times 12:57 and 16:10", links.some(h => /h7nJ6ZL4Lf0&t=777s/.test(h)) && links.some(h => /h7nJ6ZL4Lf0&t=970s/.test(h)), links.length);
    check("s5: book links target PDF page 354 (local and online)", links.some(h => /\/book#page=354$/.test(h)) && links.some(h => /databookuw\.com\/databook\.pdf#page=354$/.test(h)));
    const bookRes = await page.evaluate(async () => { const r = await fetch("book", { headers: { Range: "bytes=0-4" } }); return [r.status, await r.text()]; });
    check("book: local PDF served by the package server", (bookRes[0] === 206 || bookRes[0] === 200) && bookRes[1].startsWith("%PDF"), bookRes[0]);
    await go(page, base, "s3");
    const l3 = await page.$$eval(".sources-list a", as => as.map(a => a.href));
    check("s3: book links include p.335 pendulum example (PDF 355)", l3.some(h => /#page=355$/.test(h)));

    // ---- explorer
    await go(page, base, "explorer");
    check("explorer: renders without KaTeX errors", (await katexErrors(page)) === 0);
    for (const p of course.explorer.presets) {
      await page.click(`[data-preset="${p.id}"]`);
      await page.waitForTimeout(60);
      const r = await page.evaluate(id => ({ pressed: document.querySelector(`[data-preset="${id}"]`).getAttribute("aria-pressed"),
        kind: document.getElementById("ex-verdict").getAttribute("data-kind"), start: document.getElementById("ex-start").textContent,
        note: document.getElementById("ex-preset-note").textContent }), p.id);
      const startWord = { decays: "decays", bounded: "stays bounded", grows: "grows", rest: "rest" }[p.expectStart];
      check(`explorer: preset ${p.id} applies, verdict ${p.expect}, start ${p.expectStart}`,
            r.pressed === "true" && r.kind === VERDICT_KIND[p.expect] && r.start.includes(startWord) && r.note.length > 20, JSON.stringify(r).slice(0, 120));
    }
    // each eigenvalue is coloured by its own mode, not by the whole-system verdict
    await page.click('[data-preset="saddle"]');
    const poleCls = await page.evaluate(() => ["ex-lplane", "ex-zplane"].map(id => [...document.querySelectorAll("#" + id + " path.pole")].map(p => p.getAttribute("class")).sort().join(",")));
    check("explorer: saddle colours the decaying eigenvalue green and the growing one red in both planes",
          poleCls.every(c => c === "pole stable,pole unstable") && (await page.$eval("#ex-verdict", e => e.dataset.kind)) === "unstable", poleCls.join(" | "));
    // kinds switch the visible sliders
    await page.click('[data-kind="real"]');
    const vis = await page.evaluate(() => ["l1", "a", "lj"].map(k => !document.getElementById("ex-" + k).closest(".slider-row").hidden));
    check("explorer: kind 'real' shows λ sliders only", vis[0] && !vis[1] && !vis[2], vis);
    await page.click('[data-kind="jordan"]');
    const ro = await page.textContent(".explorer");
    check("explorer: Jordan kind reports a defective eigenvalue", /defective/.test(ro));
    // slider redraws immediately
    await page.click('[data-preset="spiral-in"]');
    const before = await page.$eval("#ex-tplot polyline", p => p.getAttribute("points"));
    await setRange(page, "#ex-a", -0.8);
    const after = await page.$eval("#ex-tplot polyline", p => p.getAttribute("points"));
    check("explorer: slider change redraws immediately", before !== after && /-0\.8/.test(await page.textContent(".readout")));
    // extreme growth: clipped, finite coordinates, notes
    await setRange(page, "#ex-a", 1); await setRange(page, "#ex-b", 4); await setRange(page, "#ex-dt", 1.5); await setRange(page, "#ex-t", 10);
    const ext = await page.evaluate(() => {
      const nums = [].concat(...[...document.querySelectorAll("#ex-tplot polyline, #ex-zplane polyline")].map(p => p.getAttribute("points").split(/[ ,]/).map(Number)));
      return { finite: nums.every(Number.isFinite), maxAbs: Math.max(...nums.map(Math.abs)), t: document.getElementById("ex-tnote").className,
               z: document.querySelector("#ex-zplane").parentNode.querySelector(".plot-note").className, verdict: document.getElementById("ex-verdict").dataset.kind };
    });
    check("explorer: off-scale growth is clipped with finite coordinates and warnings", ext.finite && ext.maxAbs < 3000 && /warn/.test(ext.t) && /warn/.test(ext.z) && ext.verdict === "unstable", JSON.stringify(ext));
    // play to the end, then navigation cancels playback
    await page.click('[data-preset="center"]');
    await setRange(page, "#ex-t", 0);
    await page.click("#ex-play");
    await page.waitForFunction(() => document.getElementById("ex-play").getAttribute("aria-pressed") === "false", null, { timeout: 8000 });
    const tEnd = await page.$eval("#ex-t", el => +el.value);
    check("explorer: play advances t to the end and stops", Math.abs(tEnd - course.explorer.tMax) < 1e-9, tEnd);
    await setRange(page, "#ex-t", 0);
    await page.evaluate(() => { window.__raf = 0; const r = window.requestAnimationFrame; window.requestAnimationFrame = f => { window.__raf++; return r(f); }; });
    await page.click("#ex-play");
    await page.waitForTimeout(150);
    await page.evaluate(() => { location.hash = "#s1"; });
    await page.waitForTimeout(300);
    const r0 = await page.evaluate(() => window.__raf);
    await page.waitForTimeout(500);
    const r1 = await page.evaluate(() => window.__raf);
    check("explorer: leaving the page cancels playback", r1 === r0, `${r0} -> ${r1}`);
    // the time reached during active playback survives navigation + reload (and playback does not resume)
    await go(page, base, "explorer");
    await page.click('[data-preset="center"]');
    await setRange(page, "#ex-t", 0);
    await page.click("#ex-play");
    await page.waitForTimeout(500);
    const tLive = await page.evaluate(() => { const v = +document.getElementById("ex-t").value; location.hash = "#sources"; return v; });
    await page.waitForTimeout(300);
    await page.reload(); await page.waitForTimeout(400);
    await go(page, base, "explorer");
    const back = await page.evaluate(() => [+document.getElementById("ex-t").value, document.getElementById("ex-play").getAttribute("aria-pressed")]);
    check("explorer: active playback time persisted through navigation and reload", tLive > 0.5 && back[0] >= tLive - 0.011 && back[0] <= tLive + 0.5 && back[1] === "false", `live ${tLive} -> restored ${back[0]}, playing=${back[1]}`);
    await go(page, base, "explorer");
    check("explorer: no horizontal overflow (desktop)", await noOverflow(page));
    await page.click('[data-preset="transient"]');
    await page.waitForTimeout(300);
    const theme0 = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    await page.screenshot({ path: path.join(SHOTS, `desktop-explorer-${theme0}.png`), fullPage: true });
    await page.reload(); await page.waitForTimeout(500);
    const restored = await page.evaluate(() => [document.getElementById("ex-s").value, document.querySelector('[data-preset="transient"]').getAttribute("aria-pressed")]);
    check("explorer: settings restored after reload", restored[0] === "3" && restored[1] === "true", restored);
    const saved = await page.evaluate(k => JSON.parse(localStorage.getItem(k)).explorer, STORE);
    check("explorer: saved state is the validated set (kind + 10 numbers)", saved && saved.kind === "real" && saved.s === 3 && Object.keys(saved).length === 11, JSON.stringify(saved));
    for (const badState of [{ kind: "real", l1: "evil" }, Object.assign({}, saved, { kind: "magic" }), Object.assign({}, saved, { a: 99 }), Object.assign({}, saved, { dt: null })]) {
      await page.evaluate(([k, b]) => { const d = JSON.parse(localStorage.getItem(k)); d.explorer = b; localStorage.setItem(k, JSON.stringify(d)); }, [STORE, badState]);
      await page.reload(); await page.waitForTimeout(400);
      const v = await page.evaluate(() => [document.getElementById("ex-a").value, document.querySelector('[data-kind="complex"]').getAttribute("aria-pressed")]);
      if (!check(`explorer: invalid saved state ${JSON.stringify(badState).slice(0, 40)} falls back to defaults`, +v[0] === course.explorer.a.default && v[1] === "true", v)) break;
    }
    // the other theme
    await page.click("#theme-toggle");
    await page.waitForTimeout(200);
    const theme = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    await page.click('[data-preset="spiral-out"]');
    await page.screenshot({ path: path.join(SHOTS, `desktop-explorer-${theme}.png`), fullPage: true });
    await go(page, base, "s3");
    await page.screenshot({ path: path.join(SHOTS, `desktop-s3-${theme}.png`), fullPage: true });
    check("theme: toggles and persists across navigation", theme !== theme0 && (await page.evaluate(() => document.documentElement.getAttribute("data-theme"))) === theme, `${theme0} -> ${theme}`);
    await page.click("#theme-toggle");
    await page.screenshot({ path: path.join(SHOTS, `desktop-s3-${theme0}.png`), fullPage: true });

    // ---- quiz
    await go(page, base, "quiz");
    await clickIfReady(page, '[data-action="reset-quiz"]');
    const q0 = course.quiz[0];
    const wrong = q0.choices.findIndex(c => !c.correct), right = q0.choices.findIndex(c => c.correct);
    await page.click(`[data-choice="${wrong}"]`);
    const fb1 = await page.textContent(".feedback");
    check("quiz: wrong choice shows its explanation", fb1.includes("Not quite") && fb1.length > 30);
    await page.click(`[data-choice="${right}"]`);
    check("quiz: retry allowed, correct choice explained", /Correct now/.test(await page.textContent(".feedback")));
    let score = await page.textContent("#quiz-score");
    check("quiz: first-try score counts first tries only", /score: 0 of 10/.test(score), score);
    for (let i = 1; i < course.quiz.length; i++) {
      await page.click('[data-action="next-question"]');
      const r = course.quiz[i].choices.findIndex(c => c.correct);
      await page.click(`[data-choice="${r}"]`);
    }
    score = await page.textContent("#quiz-score");
    check("quiz: scoring after all answers", /score: 9 of 10 · answered 10 of 10/.test(score), score);
    check("quiz: math typesets", (await katexErrors(page)) === 0);
    await page.reload(); await page.waitForTimeout(400);
    check("progress: quiz answers restored after reload", /answered 10 of 10/.test(await page.textContent("#quiz-score")));
    const prog = await page.textContent("#progress-summary");
    check("progress: sidebar summary counts 38 steps and the quiz", /38/.test(prog) && /quiz/.test(prog), prog);
    await go(page, base, "sources");
    const srcText = await page.textContent("#view");
    check("sources: lists the lecture, automatic-caption note and printed pp. 332/334/335", /h7nJ6ZL4Lf0/.test(await page.innerHTML("#view")) && /332/.test(srcText) && /334/.test(srcText) && /335/.test(srcText) && /automatic captions/.test(srcText));
    check("desktop: no console errors", page.errors.length === 0, page.errors.slice(0, 3).join(" | "));
    await ctx.close();

    // ---- mobile
    const m = await newPage(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    for (const hash of ["s1", "s2", "s3", "s4", "s5", "s6", "explorer", "quiz", "sources"]) {
      await go(m.page, base, hash);
      check(`mobile ${hash}: no horizontal overflow`, await noOverflow(m.page));
    }
    await go(m.page, base, "s6");
    await waitStep(m.page, 0);
    await m.page.click('[data-action="next"]'); await waitStep(m.page, 1);
    check("mobile s6: step plays to its still", (await still(m.page)) === frameOf(seqById["conformal-map"], 1));
    await m.page.screenshot({ path: path.join(SHOTS, "mobile-s6.png"), fullPage: true });
    await go(m.page, base, "explorer");
    await m.page.click('[data-preset="saddle"]');
    await m.page.screenshot({ path: path.join(SHOTS, "mobile-explorer.png"), fullPage: true });
    check("mobile: no console errors", m.page.errors.length === 0, m.page.errors.slice(0, 3).join(" | "));
    await m.ctx.close();

    // ---- reduced motion: steps still complete
    const r = await newPage(browser, { reducedMotion: "reduce" });
    await go(r.page, base, "s4");
    await waitStep(r.page, 0);
    await r.page.click('[data-action="next"]'); await waitStep(r.page, 1);
    check("reduced motion: step advances to its still", (await still(r.page)) === frameOf(seqById["sampling"], 1));
    check("reduced motion: no console errors", r.page.errors.length === 0, r.page.errors.slice(0, 3).join(" | "));
    await r.ctx.close();
  } catch (e) {
    check("browser run completed", false, e.message.split("\n")[0]);
  } finally {
    await browser.close();
    srv.stop();
  }
  fs.mkdirSync(path.join(PROJECT, "qa", "results"), { recursive: true });
  fs.writeFileSync(path.join(PROJECT, "qa", "results", "stability_browser.json"), JSON.stringify(results, null, 1));
  const failed = results.filter(r => !r.ok).length;
  console.log(`\n${results.length - failed}/${results.length} checks passed`);
  process.exit(failed ? 1 : 0);
}

main();
