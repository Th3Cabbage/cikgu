// Browser checks for the Linearizing Around a Fixed Point companion (installed Chrome via playwright-core).
//
//   node qa\linearization_browser_qa.js
//
// Starts courses/controls/linearization/server.py on a free loopback port (identity confirmed by nonce, no OPENAI_*
// variables) and checks: every section page renders with typeset math and no overflow; every sequence plays to its
// final stable still; back/replay/restart, saved step, reduced motion and the media fallbacks (missing still, failed
// clip); source/book links; the tutor's missing-key state and step/explorer context labels; the explorer (presets
// and verdicts, immediate slider redraws, input-extension note, elapsed-time playback, navigation cancels playback,
// save/restore, invalid saved state rejected, mobile chart text size); the quiz (retry, first-try score, restore);
// mobile, light/dark. Clips are sped up in the test only. Screenshots: qa/screenshots/linearization; results:
// qa/results/linearization_browser.json. Does not require a clean Git tree.
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");

const PROJECT = path.dirname(__dirname);
const PKG = path.join(PROJECT, "courses/controls/linearization");
const DIST = path.join(PKG, "dist");
const CHROME = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PY = [path.join(PROJECT, ".venv", "Scripts", "python.exe")].find(p => fs.existsSync(p)) || "python";
const { chromium } = require(path.join(__dirname, "tooling", "node_modules", "playwright-core"));
const manifest = JSON.parse(fs.readFileSync(path.join(DIST, "animations", "manifest.json"), "utf8"));
const course = JSON.parse(fs.readFileSync(path.join(DIST, "course.json"), "utf8"));
const SM = require(path.join(DIST, "study_math.js"));
const SHOTS = path.join(PROJECT, "qa", "screenshots", "linearization");
fs.mkdirSync(SHOTS, { recursive: true });
const STORE = "linearization-v1";
const SPEED = 6;
const seqById = Object.fromEntries(manifest.sequences.map(s => [s.id, s]));
const TOTAL_STEPS = manifest.sequences.reduce((n, s) => n + s.steps.length, 0);

const results = [];
function check(name, ok, detail) {
  results.push({ check: name, ok: !!ok, detail: detail === undefined ? "" : String(detail) });
  console.log((ok ? "PASS " : "FAIL ") + name + (detail !== undefined && detail !== "" ? "  [" + detail + "]" : ""));
  return !!ok;
}

function startServer() {
  const portFile = path.join(os.tmpdir(), "lz-qa-port-" + process.pid + "-" + Date.now() + ".txt");
  const nonce = "qa-" + process.pid + "-" + Date.now();
  const env = Object.assign({}, process.env);
  Object.keys(env).forEach(k => { if (/^OPENAI_/.test(k)) delete env[k]; });
  const proc = spawn(PY, ["-I", path.join(PKG, "server.py"), "--port", "8812", "--port-file", portFile, "--nonce", nonce],
                     { stdio: ["ignore", "pipe", "pipe"], env });
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    (function poll() {
      if (fs.existsSync(portFile)) {
        const port = fs.readFileSync(portFile, "utf8").trim();
        fetch(`http://127.0.0.1:${port}/__control_health`).then(r => r.json()).then(j => {
          if (j.app !== "Study_linearization" || j.nonce !== nonce) return reject(new Error("health mismatch " + JSON.stringify(j)));
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
  await ctx.addInitScript(s => {   // test-only speed-ups: faster clips and explorer playback
    const play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () { this.playbackRate = 4; return play.call(this); };
    window.__studyExplorerSpeed = s;
  }, SPEED);
  const page = await ctx.newPage();
  page.errors = [];
  page.on("console", m => { if (m.type() === "error" && !/Failed to load resource/.test(m.text())) page.errors.push(m.text()); });
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
async function clickIfReady(page, sel) {
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
async function selectSeq(page, id) {
  const btn = await page.$(`.seq-btn[data-seq="${id}"]`);
  if (btn) { await btn.click(); await page.waitForTimeout(200); }
  return page.evaluate(() => document.querySelector(".stage-wrap").dataset.seq);
}
async function playThrough(page, sq) {
  if (!(await clickIfReady(page, '[data-action="restart-complete"]'))) await clickIfReady(page, '[data-action="restart"]');
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
async function tutorLabel(page) {
  return page.evaluate(() => { document.getElementById("tutor-toggle").click();
    return new Promise(r => setTimeout(() => { const t = document.querySelector(".tutor-context"); r(t ? t.textContent : ""); }, 300)); });
}

async function main() {
  const srv = await startServer();
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
  try {
    const { ctx, page } = await newPage(browser);
    const base = srv.base;

    // ---- every section and every sequence
    for (const sec of course.sections) {
      await go(page, base, sec.id);
      const h1 = await page.textContent("h1");
      check(`${sec.id}: page renders "${h1.slice(0, 50)}"`, h1 && h1.length > 3);
      for (const sq of manifest.sequences.filter(s => s.section === sec.number)) {
        check(`${sq.id}: selected on its section page`, (await selectSeq(page, sq.id)) === sq.id);
        await playThrough(page, sq);
        await page.screenshot({ path: path.join(SHOTS, `desktop-${sec.id}-${sq.id}-final.png`) });
      }
      check(`${sec.id}: math typesets without KaTeX errors`, (await katexErrors(page)) === 0);
      check(`${sec.id}: no horizontal overflow (desktop)`, await noOverflow(page));
      const view = await page.textContent("#view");
      check(`${sec.id}: notes, worked example and answer present`, /Worked example|example/i.test(view) && view.includes(sec.example.title.slice(0, 20)));
    }
    check("navigation: Section 7 shows 'Section 7 of 7'", /Section 7 of 7/.test(await page.textContent("#view")));

    // ---- controls and tutor on section 7 (MATLAB)
    const mt = seqById["matlab-check"];
    await go(page, base, "s7");
    if (!(await clickIfReady(page, '[data-action="restart-complete"]'))) await clickIfReady(page, '[data-action="restart"]');
    await waitStep(page, 0);
    await page.click('[data-action="next"]'); await waitStep(page, 1);
    await page.click('[data-action="next"]'); await waitStep(page, 2);
    await page.click('[data-action="back"]'); await waitStep(page, 1);
    check("controls: back returns to the previous stable still", (await still(page)) === frameOf(mt, 1));
    await page.click('[data-action="replay"]'); await waitStep(page, 1);
    check("controls: replay ends on the same step", (await still(page)) === frameOf(mt, 1));
    await page.click('[data-action="next"]'); await waitStep(page, 2);
    await page.reload(); await page.waitForTimeout(400); await waitStep(page, 2);
    check("progress: step position restored after reload", (await page.evaluate(() => document.querySelector(".stage-wrap").dataset.step)) === "2");
    const label = await tutorLabel(page);
    check("tutor: context label names Section 7 and the MATLAB step 2 of 5", /Section 7/.test(label) && /step 2 of 5/.test(label) && /eig\(Ad\)/.test(label), label.slice(0, 110));
    const tutorText = await page.textContent("#tutor");
    check("tutor: missing-key state explained, input disabled, no chat sent",
          /OPENAI_API_KEY/.test(tutorText) && /not set up/i.test(tutorText) && await page.$eval("#tutor textarea, #tutor input[type=text]", el => el.disabled).catch(() => true),
          tutorText.replace(/\s+/g, " ").slice(0, 120));
    await page.evaluate(() => document.getElementById("tutor-toggle").click());
    if (!(await clickIfReady(page, '[data-action="restart-complete"]'))) await clickIfReady(page, '[data-action="restart"]');
    await waitStep(page, 0);
    check("controls: restart returns to the opening still", (await still(page)) === frameOf(mt, 0));
    const links = await page.$$eval(".sources-list a", as => as.map(a => a.href));
    check("s7: lecture links use 1YMTkELi3tE with the MATLAB moment 30:00", links.some(h => /1YMTkELi3tE&t=1800s/.test(h)), links.length);
    check("s7: book links target PDF page 355 (local and online)", links.some(h => /\/book#page=355$/.test(h)) && links.some(h => /databookuw\.com\/databook\.pdf#page=355$/.test(h)));
    await go(page, base, "s3");
    const l3 = await page.$$eval(".sources-list a", as => as.map(a => a.href));
    check("s3: book links include p.330 (PDF 350)", l3.some(h => /#page=350$/.test(h)));
    const bookRes = await page.evaluate(async () => { const r = await fetch("book", { headers: { Range: "bytes=0-4" } }); return [r.status, await r.text()]; });
    check("book: local PDF served by the package server", (bookRes[0] === 206 || bookRes[0] === 200) && bookRes[1].startsWith("%PDF"), bookRes[0]);

    // ---- media fallbacks
    const fb = await newPage(browser);
    const sq2 = seqById["jacobian-cells"];
    await fb.page.route("**/animations/jacobian-cells/state-02.jpg", r => r.abort());
    await fb.page.route("**/animations/jacobian-cells/step-01.mp4", r => r.abort());
    await go(fb.page, base, "s2");
    if (!(await clickIfReady(fb.page, '[data-action="restart-complete"]'))) await clickIfReady(fb.page, '[data-action="restart"]');
    await waitStep(fb.page, 0);
    await fb.page.click('[data-action="next"]');
    await waitStep(fb.page, 1, 20000);
    check("fallback: a failed clip still lands on the step's stable still", (await still(fb.page)) === frameOf(sq2, 1));
    await fb.page.click('[data-action="next"]');
    await fb.page.waitForFunction(() => { const f = document.querySelector(".stage-fallback"); return f && !f.hidden; }, null, { timeout: 15000 }).catch(() => {});
    const fbs = await fb.page.evaluate(() => { const f = document.querySelector(".stage-fallback"); return f ? [f.hidden, !!f.querySelector(".katex"), f.textContent.slice(0, 60)] : [true, false, ""]; });
    check("fallback: a missing still shows the step's formula instead", fbs[0] === false && fbs[1], JSON.stringify(fbs));
    await fb.ctx.close();

    // ---- explorer
    await go(page, base, "explorer");
    const tl = await tutorLabel(page);
    check("tutor: explorer context label", /Explorer page/.test(tl), tl.slice(0, 60));
    await page.evaluate(() => document.getElementById("tutor-toggle").click());
    check("explorer: renders without KaTeX errors", (await katexErrors(page)) === 0);
    const def = await page.evaluate(() => [document.getElementById("ex-q").value, document.getElementById("ex-d").value, document.getElementById("ex-du").value,
                                           document.querySelector('[data-preset="lecture-down"]').getAttribute("aria-pressed")]);
    check("explorer: defaults are the lecture's q = 1, d = 0.1, no input", +def[0] === 1 && +def[1] === 0.1 && +def[2] === 0, def);
    const mats = await page.textContent("#ex-mats");
    check("explorer: lecture default shows eig(Ad) = -0.05 ± 0.999i", /−?-?0\.05/.test(mats) && /0\.999/.test(mats), mats.replace(/\s+/g, " ").slice(0, 120));
    const KIND = { lyapunov: "marginal", asymptotic: "stable", unstable: "unstable" };
    for (const p of SM.PRESETS) {
      await page.click(`[data-preset="${p.id}"]`);
      await page.waitForTimeout(60);
      const r = await page.evaluate(id => ({ pressed: document.querySelector(`[data-preset="${id}"]`).getAttribute("aria-pressed"),
        kind: document.getElementById("ex-verdict").getAttribute("data-kind"), verdict: document.getElementById("ex-verdict").textContent,
        lin: document.getElementById("ex-linear").textContent, note: document.getElementById("ex-preset-note").textContent }), p.id);
      const c = SM.classify(p.eq, p.q, p.d);
      check(`explorer: preset ${p.id} applies with verdict ${c.nonlinear} (${c.linear})`,
            r.pressed === "true" && r.kind === KIND[c.nonlinear] && /zero-input reference/.test(r.verdict) && r.lin.includes(c.linear === "center" ? "center" : c.linear) && r.note.length > 20,
            JSON.stringify(r).slice(0, 140));
      if (p.id === "lecture-up") check("explorer: lecture-up shows the MATLAB eigenvalues -1.051 and 0.951", /1\.051/.test(await page.textContent("#ex-mats")) && /0\.951/.test(await page.textContent("#ex-mats")));
    }
    await page.click('[data-preset="undamped-down"]');
    check("explorer: undamped center explains the energy argument, not the eigenvalues", /energy/.test(await page.textContent("#ex-verdict")) && /inconclusive/.test(await page.textContent("#ex-verdict")));
    await page.click('[data-preset="lecture-up"]');
    check("explorer: up linear curve leaves the plotted range with a warning", /leaves the plotted range/.test(await page.textContent("#ex-tnote")));
    // immediate redraw on a slider change
    await page.click('[data-preset="lecture-down"]');
    const before = await page.$eval("#ex-tplot", s => s.innerHTML);
    await setRange(page, "#ex-eta0", 1.0);
    const after = await page.$eval("#ex-tplot", s => s.innerHTML);
    check("explorer: slider change redraws immediately and updates the readout", before !== after && /\(1\)/.test(await page.textContent("#ex-now")));
    await setRange(page, "#ex-du", 0.3);
    const inote = await page.textContent("#ex-input-note");
    check("explorer: nonzero input is labelled an extension and an input-response comparison", /extension/.test(inote) && /no longer a fixed point/.test(inote) && /input-response comparison/.test(inote));
    await setRange(page, "#ex-du", 0);
    check("explorer: input note clears when the input returns to 0", (await page.textContent("#ex-input-note")).trim() === "");
    // elapsed-time playback
    await setRange(page, "#ex-t", 0);
    const t0 = Date.now();
    await page.click("#ex-play");
    await page.waitForTimeout(900);
    const tNow = await page.evaluate(() => +document.getElementById("ex-t").value);
    const wall = (Date.now() - t0) / 1000;
    check("explorer: playback advances by elapsed wall time (test speed x6)", tNow > 2.5 && tNow <= SPEED * wall + 0.3, `t=${tNow.toFixed(2)} after ${wall.toFixed(2)} s`);
    await page.waitForFunction(() => document.getElementById("ex-play").getAttribute("aria-pressed") === "false", null, { timeout: 8000 });
    check("explorer: playback stops at the end of the window", +(await page.$eval("#ex-t", el => el.value)) === SM.T_MAX);
    // navigation cancels playback; the reached time is saved
    await setRange(page, "#ex-t", 0);
    await page.evaluate(() => { window.__raf = 0; const r = window.requestAnimationFrame; window.requestAnimationFrame = f => { window.__raf++; return r(f); }; });
    await page.click("#ex-play");
    await page.waitForTimeout(250);
    const tLive = await page.evaluate(() => { const v = +document.getElementById("ex-t").value; location.hash = "#s1"; return v; });
    await page.waitForTimeout(300);
    const r0 = await page.evaluate(() => window.__raf);
    await page.waitForTimeout(500);
    const r1 = await page.evaluate(() => window.__raf);
    check("explorer: leaving the page cancels playback", r1 === r0, `${r0} -> ${r1}`);
    const savedT = await page.evaluate(k => JSON.parse(localStorage.getItem(k)).explorer.t, STORE);
    check("explorer: time reached during playback was saved on navigation", savedT >= tLive - 0.02 && savedT < SM.T_MAX, `${tLive} -> ${savedT}`);
    // save / restore / invalid saved state
    await go(page, base, "explorer");
    await page.click('[data-preset="overdamped-down"]');
    await page.waitForTimeout(400);
    await page.reload(); await page.waitForTimeout(500);
    const restored = await page.evaluate(() => [document.getElementById("ex-d").value, document.querySelector('[data-preset="overdamped-down"]').getAttribute("aria-pressed")]);
    check("explorer: settings restored after reload", +restored[0] === 3 && restored[1] === "true", restored);
    const saved = await page.evaluate(k => JSON.parse(localStorage.getItem(k)).explorer, STORE);
    check("explorer: saved state is the validated set (eq + 6 numbers)", saved && saved.eq === "down" && saved.d === 3 && Object.keys(saved).length === 7, JSON.stringify(saved));
    for (const badState of [{ eq: "down", eta0: "evil" }, Object.assign({}, saved, { eq: "sideways" }), Object.assign({}, saved, { q: 0 }),
                            Object.assign({}, saved, { d: -1 }), Object.assign({}, saved, { eta0: 3.2 }), Object.assign({}, saved, { du: null })]) {
      await page.evaluate(([k, b]) => { const d = JSON.parse(localStorage.getItem(k)); d.explorer = b; localStorage.setItem(k, JSON.stringify(d)); }, [STORE, badState]);
      await page.reload(); await page.waitForTimeout(400);
      const v = await page.evaluate(() => [+document.getElementById("ex-d").value, document.querySelector('[data-preset="lecture-down"]').getAttribute("aria-pressed")]);
      if (!check(`explorer: invalid saved state ${JSON.stringify(badState).slice(0, 44)} falls back to defaults`, v[0] === 0.1 && v[1] === "true", v)) break;
    }
    check("explorer: no horizontal overflow (desktop)", await noOverflow(page));
    const theme0 = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    await page.click('[data-preset="lecture-up"]');
    await setRange(page, "#ex-t", 6);
    await page.screenshot({ path: path.join(SHOTS, `desktop-explorer-${theme0}.png`), fullPage: true });
    await page.click("#theme-toggle");
    await page.waitForTimeout(200);
    const theme = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    await page.click('[data-preset="large-down"]');
    await setRange(page, "#ex-t", 7);
    await page.screenshot({ path: path.join(SHOTS, `desktop-explorer-${theme}.png`), fullPage: true });
    await go(page, base, "s6");
    await page.screenshot({ path: path.join(SHOTS, `desktop-s6-${theme}.png`), fullPage: true });
    check("theme: toggles and persists across navigation", theme !== theme0 && (await page.evaluate(() => document.documentElement.getAttribute("data-theme"))) === theme, `${theme0} -> ${theme}`);
    await page.click("#theme-toggle");

    // ---- quiz
    await go(page, base, "quiz");
    await clickIfReady(page, '[data-action="reset-quiz"]');
    const q0 = course.quiz[0];
    const wrong = q0.choices.findIndex(c => !c.correct), right = q0.choices.findIndex(c => c.correct);
    await page.click(`[data-choice="${wrong}"]`);
    const fb1 = await page.textContent(".feedback");
    check("quiz: wrong choice shows its explanation", fb1.includes("Not quite") && fb1.includes(q0.choices[wrong].why.slice(0, 12).replace(/\$/g, "").trim().slice(0, 6)));
    await page.click(`[data-choice="${right}"]`);
    check("quiz: retry allowed, correct choice explained", /Correct now/.test(await page.textContent(".feedback")));
    let score = await page.textContent("#quiz-score");
    check("quiz: first-try score counts first tries only", /score: 0 of 10/.test(score), score);
    for (let i = 1; i < course.quiz.length; i++) {
      await page.click('[data-action="next-question"]');
      await page.click(`[data-choice="${course.quiz[i].choices.findIndex(c => c.correct)}"]`);
    }
    score = await page.textContent("#quiz-score");
    check("quiz: scoring after all answers", /score: 9 of 10 · answered 10 of 10/.test(score), score);
    check("quiz: math typesets", (await katexErrors(page)) === 0);
    await page.reload(); await page.waitForTimeout(400);
    check("progress: quiz answers restored after reload", /answered 10 of 10/.test(await page.textContent("#quiz-score")));
    const prog = await page.textContent("#progress-summary");
    check(`progress: sidebar summary counts ${TOTAL_STEPS} steps and the quiz`, new RegExp(String(TOTAL_STEPS)).test(prog) && /quiz/.test(prog), prog);
    await go(page, base, "sources");
    const srcText = await page.textContent("#view");
    check("sources: lists the lecture, the transcript note and printed pp. 330/335", /1YMTkELi3tE/.test(await page.innerHTML("#view")) && /330/.test(srcText)
          && /335/.test(srcText) && /speech-recognition transcript/.test(srcText));
    check("desktop: no console errors", page.errors.length === 0, page.errors.slice(0, 3).join(" | "));
    await ctx.close();

    // ---- mobile
    const m = await newPage(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    for (const hash of course.sections.map(s => s.id).concat(["explorer", "quiz", "sources"])) {
      await go(m.page, base, hash);
      check(`mobile ${hash}: no horizontal overflow`, await noOverflow(m.page));
    }
    await go(m.page, base, "s6");
    if (!(await clickIfReady(m.page, '[data-action="restart-complete"]'))) await clickIfReady(m.page, '[data-action="restart"]');
    await waitStep(m.page, 0);
    await m.page.click('[data-action="next"]'); await waitStep(m.page, 1);
    check("mobile s6: step plays to its still", (await still(m.page)) === frameOf(seqById["two-jacobians"], 1));
    await m.page.screenshot({ path: path.join(SHOTS, "mobile-s6.png"), fullPage: true });
    await go(m.page, base, "explorer");
    await m.page.click('[data-preset="lecture-up"]');
    const minFont = await m.page.evaluate(() => {
      let mn = 99;
      document.querySelectorAll(".lz-plot").forEach(svg => {
        const k = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
        svg.querySelectorAll("text").forEach(t => { mn = Math.min(mn, parseFloat(getComputedStyle(t).fontSize) * k); });
      });
      return mn;
    });
    check("mobile explorer: chart labels render at >= 8.5 CSS px", minFont >= 8.5, minFont.toFixed(1));
    await m.page.screenshot({ path: path.join(SHOTS, "mobile-explorer.png"), fullPage: true });
    check("mobile: no console errors", m.page.errors.length === 0, m.page.errors.slice(0, 3).join(" | "));
    await m.ctx.close();

    // ---- reduced motion
    const r = await newPage(browser, { reducedMotion: "reduce" });
    await go(r.page, base, "s4");
    if (!(await clickIfReady(r.page, '[data-action="restart-complete"]'))) await clickIfReady(r.page, '[data-action="restart"]');
    await waitStep(r.page, 0);
    await r.page.click('[data-action="next"]'); await waitStep(r.page, 1);
    check("reduced motion: step advances to its still", (await still(r.page)) === frameOf(seqById["hyperbolic"], 1));
    check("reduced motion: no console errors", r.page.errors.length === 0, r.page.errors.slice(0, 3).join(" | "));
    await r.ctx.close();
  } catch (e) {
    check("browser run completed", false, e.message.split("\n")[0]);
  } finally {
    await browser.close();
    srv.stop();
  }
  fs.mkdirSync(path.join(PROJECT, "qa", "results"), { recursive: true });
  fs.writeFileSync(path.join(PROJECT, "qa", "results", "linearization_browser.json"), JSON.stringify(results, null, 1));
  const failed = results.filter(r => !r.ok).length;
  console.log(`\n${results.length - failed}/${results.length} checks passed`);
  process.exit(failed ? 1 : 0);
}

main();
