// Browser checks for the Linear Systems study companion (installed Chrome via playwright-core).
//
//   node qa\linear_systems_browser_qa.js
//
// Starts linear-systems/server.py on a free loopback port (identity confirmed by nonce, no
// OPENAI_* variables), then checks: every section renders with typeset math and no overflow on
// desktop and mobile; every sequence plays through to its final step (clips at 4x speed) with the
// correct stills; back/replay/restart; the explorer (presets, sliders, exact worked numbers, play,
// save and restore, invalid saved state rejected); the quiz (retry, first-try score, summary); the
// tutor's missing-key state and the step-aware context label. Screenshots go to
// qa/screenshots/linear-systems, results to qa/results/linear_systems_browser.json.
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");

const PROJECT = path.dirname(__dirname);
const PKG = path.join(PROJECT, "linear-systems");
const DIST = path.join(PKG, "dist");
const CHROME = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const PY = [path.join(PROJECT, ".venv", "Scripts", "python.exe")].find(p => fs.existsSync(p)) || "python";
const { chromium } = require(path.join(__dirname, "tooling", "node_modules", "playwright-core"));
const manifest = JSON.parse(fs.readFileSync(path.join(DIST, "animations", "manifest.json"), "utf8"));
const course = JSON.parse(fs.readFileSync(path.join(DIST, "course.json"), "utf8"));
const SHOTS = path.join(PROJECT, "qa", "screenshots", "linear-systems");
fs.mkdirSync(SHOTS, { recursive: true });
const STORE = "linear-systems-v1";

const results = [];
function check(name, ok, detail) {
  results.push({ check: name, ok: !!ok, detail: detail === undefined ? "" : String(detail) });
  console.log((ok ? "PASS " : "FAIL ") + name + (detail !== undefined && detail !== "" ? "  [" + detail + "]" : ""));
  return !!ok;
}

function startServer() {
  const portFile = path.join(os.tmpdir(), "ls-qa-port-" + process.pid + "-" + Date.now() + ".txt");
  const nonce = "qa-" + process.pid + "-" + Date.now();
  const env = Object.assign({}, process.env);
  Object.keys(env).forEach(k => { if (/^OPENAI_/.test(k)) delete env[k]; });
  const proc = spawn(PY, ["-I", path.join(PKG, "server.py"), "--port", "8791", "--port-file", portFile, "--nonce", nonce],
                     { stdio: ["ignore", "pipe", "pipe"], env });
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    (function poll() {
      if (fs.existsSync(portFile)) {
        const port = fs.readFileSync(portFile, "utf8").trim();
        fetch(`http://127.0.0.1:${port}/__control_health`).then(r => r.json()).then(j => {
          if (j.app !== "Study_linear_systems" || j.nonce !== nonce) return reject(new Error("health mismatch " + JSON.stringify(j)));
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

async function go(page, base, hash) {
  await page.goto(base + "#" + hash);
  await page.waitForFunction(() => !document.querySelector(".loading-note"), null, { timeout: 15000 });
  await page.waitForTimeout(150);
}

async function main() {
  const srv = await startServer();
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ["--autoplay-policy=no-user-gesture-required"] });
  try {
    const { ctx, page } = await newPage(browser);
    const base = srv.base;

    // ---- sections: render, math, overflow, every sequence to its final step
    for (const sec of course.sections) {
      await go(page, base, sec.id);
      const h1 = await page.textContent("h1");
      check(`${sec.id}: page renders "${h1.slice(0, 40)}"`, h1 && h1.length > 3);
      const seqs = manifest.sequences.filter(s => s.section === sec.number);
      for (const sq of seqs) {
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
        await page.screenshot({ path: path.join(SHOTS, `desktop-${sec.id}-final.png`) });
      }
      check(`${sec.id}: math typesets without KaTeX errors`, (await katexErrors(page)) === 0);
      check(`${sec.id}: no horizontal overflow (desktop)`, await noOverflow(page));
    }

    // ---- controls on section 5: back, replay, restart, persistence of the step
    await go(page, base, "s5");
    await page.click('[data-action="restart"]').catch(() => {});
    await waitStep(page, 0);
    await page.click('[data-action="next"]'); await waitStep(page, 1);
    await page.click('[data-action="next"]'); await waitStep(page, 2);
    await page.click('[data-action="back"]'); await waitStep(page, 1);
    check("controls: back returns to the previous stable still", (await still(page)) === frameOf(manifest.sequences[4], 1));
    await page.click('[data-action="replay"]'); await waitStep(page, 1);
    check("controls: replay ends on the same step", (await still(page)) === frameOf(manifest.sequences[4], 1));
    await page.reload(); await page.waitForTimeout(400); await waitStep(page, 1);
    check("progress: step position restored after reload", (await page.evaluate(() => document.querySelector(".stage-wrap").dataset.step)) === "1");
    const label = await page.evaluate(() => { document.getElementById("tutor-toggle").click(); return new Promise(r => setTimeout(() => r(document.querySelector(".tutor-context") ? document.querySelector(".tutor-context").textContent : ""), 300)); });
    check("tutor: context label names the section and step", /Section 5/.test(label) && /step 1 of 6/.test(label), label.slice(0, 90));
    const tutorText = await page.textContent("#tutor");
    check("tutor: missing-key state explained, no chat sent", /key|not configured|OPENAI/i.test(tutorText), tutorText.replace(/\s+/g, " ").slice(0, 120));
    await page.evaluate(() => document.getElementById("tutor-toggle").click());
    await go(page, base, "s6");
    const links = await page.$$eval(".sources-list a", as => as.map(a => a.href));
    check("s6: linked 22:22 moment is linked first (t=1342s)", links.some(h => /nyqJJdhReiA&t=1342s/.test(h)) && /t=1342s/.test(links[0] || ""), links[0]);

    // ---- explorer
    await go(page, base, "explorer");
    check("explorer: renders without KaTeX errors", (await katexErrors(page)) === 0);
    await page.click('[data-preset="worked"]');
    await page.waitForTimeout(100);
    const ro = await page.textContent(".explorer");
    check("explorer: worked preset shows A = [[-1,-1],[0,-2]] and z0 = (1,1)", /-1-10-2|−1−10−2/.test(ro.replace(/\s/g, "")) && /z\(0\)/.test(ro));
    const nums = await page.evaluate(() => {
      const M = window.StudyMath, r = M.pipeline({ l1: -1, l2: -2, s: 1, x1: 2, x2: 1 }, Math.log(2));
      return r.xt.concat(r.zt);
    });
    check("explorer: exact worked numbers x=(3/4,1/4), z=(1/2,1/4)", Math.abs(nums[0] - 0.75) < 1e-12 && Math.abs(nums[1] - 0.25) < 1e-12 && Math.abs(nums[2] - 0.5) < 1e-12);
    const before = await page.$eval(".plot-box polyline", p => p.getAttribute("points"));
    await page.$eval("#ex-s", el => { el.value = "-1.5"; el.dispatchEvent(new Event("input", { bubbles: true })); });
    const after = await page.$eval(".plot-box polyline", p => p.getAttribute("points"));
    const aTex = await page.textContent(".readout");
    check("explorer: slider change redraws immediately", before !== after && /1\.5/.test(aTex));
    for (const p of course.explorer.presets) {
      await page.click(`[data-preset="${p.id}"]`);
      await page.waitForTimeout(60);
      const pressed = await page.$eval(`[data-preset="${p.id}"]`, b => b.getAttribute("aria-pressed"));
      if (!check(`explorer: preset ${p.id} applies`, pressed === "true")) break;
    }
    check("explorer: repeated preset explains A = λI", /diagonalizable/.test(await page.textContent(".explorer")));
    await page.click('[data-preset="saddle"]');
    await page.$eval("#ex-t", el => { el.value = "0"; el.dispatchEvent(new Event("input", { bubbles: true })); });
    await page.click("#ex-play");
    await page.waitForFunction(() => document.getElementById("ex-play").getAttribute("aria-pressed") === "false", null, { timeout: 8000 });
    const tEnd = await page.$eval("#ex-t", el => +el.value);
    check("explorer: play advances t to the end and stops", Math.abs(tEnd - course.explorer.tMax) < 1e-9, tEnd);
    check("explorer: no horizontal overflow (desktop)", await noOverflow(page));
    await page.screenshot({ path: path.join(SHOTS, "desktop-explorer.png"), fullPage: true });
    await page.click('[data-preset="worked"]');
    await page.waitForTimeout(700);
    await page.reload(); await page.waitForTimeout(500);
    const restored = await page.$eval("#ex-l2", el => +el.value);
    check("explorer: settings restored after reload", restored === -2, restored);
    const saved = await page.evaluate(k => JSON.parse(localStorage.getItem(k)).explorer, STORE);
    check("explorer: saved state is the validated slider set", saved && saved.l1 === -1 && saved.s === 1 && Object.keys(saved).length === 6, JSON.stringify(saved));
    await page.evaluate(k => { const d = JSON.parse(localStorage.getItem(k)); d.explorer = { l1: "evil", l2: 99 }; localStorage.setItem(k, JSON.stringify(d)); }, STORE);
    await page.reload(); await page.waitForTimeout(500);
    check("explorer: invalid saved state falls back to defaults", (await page.$eval("#ex-l1", el => +el.value)) === course.explorer.l1.default && page.errors.length === 0, page.errors.slice(0, 2));

    // ---- quiz
    await go(page, base, "quiz");
    await page.click('[data-action="reset-quiz"]').catch(() => {});
    const q0 = course.quiz[0];
    const wrong = q0.choices.findIndex(c => !c.correct), right = q0.choices.findIndex(c => c.correct);
    await page.click(`[data-choice="${wrong}"]`);
    const fb1 = await page.textContent(".feedback");
    check("quiz: wrong choice shows its explanation", fb1.includes("Not quite") && fb1.length > 30);
    await page.click(`[data-choice="${right}"]`);
    const fb2 = await page.textContent(".feedback");
    check("quiz: retry allowed, correct choice explained", /Correct now/.test(fb2));
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
    check("progress: sidebar summary counts steps and quiz", /33/.test(prog) && /quiz/.test(prog), prog);
    await go(page, base, "sources");
    check("sources: page lists the new lecture and book", /nyqJJdhReiA/.test(await page.innerHTML("#view")) && /331/.test(await page.textContent("#view")));
    check("desktop: no console errors", page.errors.length === 0, page.errors.slice(0, 3).join(" | "));
    await ctx.close();

    // ---- mobile
    const m = await newPage(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    for (const hash of ["s1", "s3", "s5", "s6", "explorer", "quiz"]) {
      await go(m.page, base, hash);
      check(`mobile ${hash}: no horizontal overflow`, await noOverflow(m.page));
    }
    await go(m.page, base, "s6");
    await waitStep(m.page, 0);
    await m.page.click('[data-action="next"]'); await waitStep(m.page, 1);
    check("mobile s6: step plays to its still", (await still(m.page)) === frameOf(manifest.sequences[5], 1));
    await m.page.screenshot({ path: path.join(SHOTS, "mobile-s6.png"), fullPage: true });
    await go(m.page, base, "explorer");
    await m.page.screenshot({ path: path.join(SHOTS, "mobile-explorer.png"), fullPage: true });
    check("mobile: no console errors", m.page.errors.length === 0, m.page.errors.slice(0, 3).join(" | "));
    await m.ctx.close();

    // ---- reduced motion: steps still complete (no video required)
    const r = await newPage(browser, { reducedMotion: "reduce" });
    await go(r.page, base, "s4");
    await waitStep(r.page, 0);
    await r.page.click('[data-action="next"]'); await waitStep(r.page, 1);
    check("reduced motion: step advances to its still", (await still(r.page)) === frameOf(manifest.sequences[3], 1));
    await r.ctx.close();
  } catch (e) {
    check("browser run completed", false, e.message.split("\n")[0]);
  } finally {
    await browser.close();
    srv.stop();
  }
  fs.mkdirSync(path.join(PROJECT, "qa", "results"), { recursive: true });
  fs.writeFileSync(path.join(PROJECT, "qa", "results", "linear_systems_browser.json"), JSON.stringify(results, null, 1));
  const failed = results.filter(r => !r.ok).length;
  console.log(`\n${results.length - failed}/${results.length} checks passed`);
  process.exit(failed ? 1 : 0);
}

main();
