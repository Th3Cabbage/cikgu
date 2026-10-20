// Browser check of the Linearizing Around a Fixed Point explorer, mounted directly through the
// StudyExplorer contract (restore/stop/render) with the package styles and bundled KaTeX.
// Mounts independently of course.json and the full shell; useful during explorer authoring.
// Run from the repository root: node qa/linearization_explorer_qa.js
"use strict";
const path = require("path");
const fs = require("fs");
const CHROME = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const { chromium } = require(path.join(__dirname, "tooling", "node_modules", "playwright-core"));

const DIST = path.join(__dirname, "..", "courses", "controls", "linearization", "dist");
const SHOTS = path.join(__dirname, "screenshots", "linearization");
const fails = [];
let count = 0;
function check(cond, msg) { count++; if (!cond) fails.push(msg); }

const HARNESS = `
window.__saves = 0;
window.mount = function (saved) {
  var SVG_NS = "http://www.w3.org/2000/svg";
  function h(tag, attrs, children) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { var v = attrs[k]; if (v === null || v === undefined || v === false) return;
      if (k === "text") n.textContent = v; else if (k === "className") n.className = v; else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), v); else n.setAttribute(k, v === true ? "" : v); });
    (children || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function s(tag, attrs, children) {
    var n = document.createElementNS(SVG_NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { if (k === "text") n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]); });
    (children || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  var D = [{ left: "$", right: "$", display: false }];
  function mathText(n, t) { n.textContent = t || ""; renderMathInElement(n, { delimiters: D, throwOnError: false }); return n; }
  function flowMath(n, t) { katex.render("\\\\displaystyle " + t, n, { throwOnError: false }); return n; }
  var root = document.getElementById("view"); root.textContent = "";
  window.appState = { explorer: StudyExplorer.restore(saved, {}) };
  StudyExplorer.render({ root: root, course: { explorer: {} }, state: window.appState, save: function () { window.__saves++; },
    html: h, svg: s, mathText: mathText, displayMath: flowMath, flowMath: flowMath, announce: function () {}, panel: null });
};`;

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch({ executablePath: CHROME, headless: true });
  const errors = [];
  async function open(width, height) {
    const page = await browser.newPage({ viewport: { width, height } });
    page.on("pageerror", (e) => errors.push(String(e)));
    page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
    await page.setContent('<!doctype html><html data-theme="light"><body><main class="main"><div id="view"></div></main></body></html>');
    await page.addStyleTag({ path: path.join(DIST, "vendor", "katex", "katex.min.css") });
    await page.addStyleTag({ path: path.join(DIST, "styles.css") });
    for (const f of ["vendor/katex/katex.min.js", "vendor/katex/contrib/auto-render.min.js", "study_math.js", "explorer.js"])
      await page.addScriptTag({ path: path.join(DIST, f) });
    await page.addScriptTag({ content: HARNESS });
    return page;
  }

  const page = await open(1280, 1000);
  // restore validation
  const r = await page.evaluate(() => [
    StudyExplorer.restore({ eq: "up", eta0: 0.05, nu0: 0, q: 1, du: 0, d: 0, t: 3 }),
    StudyExplorer.restore({ eq: "sideways", eta0: 0, nu0: 0, q: 1, du: 0, d: 0, t: 0 }),
    StudyExplorer.restore({ eq: "down", eta0: 3.1, nu0: 0, q: 1, du: 0, d: 0, t: 0 }),
    StudyExplorer.restore({ eq: "down", eta0: 0, nu0: 0, q: 0, du: 0, d: 0, t: 0 }),
    StudyExplorer.restore({ eq: "down", eta0: 0, nu0: 0, q: 1, du: 0, d: -1, t: 0 }),
    StudyExplorer.restore({ eq: "down", eta0: "0", nu0: 0, q: 1, du: 0, d: 0, t: 0 }),
    StudyExplorer.restore(null)]);
  check(r[0] && r[0].eq === "up" && r[0].t === 3, "valid saved state restored");
  check(r.slice(1).every((x) => x === null), "invalid saved states rejected: " + JSON.stringify(r.slice(1)));

  await page.evaluate(() => mount(null));
  const txt = async (sel) => (await page.locator(sel).innerText()).replace(/\s+/g, " ");
  check(await page.locator("#ex-d").inputValue() === "0.1", "damping defaults to the lecture value d = 0.1");
  check((await txt("#ex-verdict")).includes("locally asymptotically stable") && (await txt("#ex-verdict")).includes("zero-input reference"), "lecture default down verdict: asymptotically stable zero-input reference");
  check((await txt("#ex-linear")).includes("focus"), "lecture default down: underdamped focus");
  check((await txt(".lz-ext legend")).includes("Book-supported extension"), "input/output labelled as the book extension");

  // presets
  for (const [id, expect] of [["undamped-down", "not asymptotically"], ["lecture-down", "locally asymptotically"], ["overdamped-down", "locally asymptotically"], ["large-down", "locally asymptotically"], ["lecture-up", "unstable"], ["exact-up", "unstable"]]) {
    await page.click(`[data-preset="${id}"]`);
    check(await page.getAttribute(`[data-preset="${id}"]`, "aria-pressed") === "true", `preset ${id} highlighted`);
    check((await txt("#ex-verdict")).includes(expect), `preset ${id} verdict`);
    const st = await page.evaluate(() => appState.explorer);
    const pr = await page.evaluate((i) => StudyMath.PRESETS.find((p) => p.id === i), id);
    check(st.eq === pr.eq && st.eta0 === pr.eta0 && st.q === pr.q && st.t === 0, `preset ${id} state`);
    if (id === "lecture-up") check((await txt("#ex-tnote")).includes("leaves the plotted range"), "small-up warns that the linear curve leaves the range");
    await page.screenshot({ path: path.join(SHOTS, `desktop-${id}.png`), fullPage: true });
  }
  // exact equilibrium shows zero error
  check(/angle error[^=]*= 0/.test(await txt("#ex-now")), "exact equilibrium zero error: " + await txt("#ex-now"));

  // switching the fixed point keeps eta0 as a perturbation and shows theta = theta_bar + eta
  await page.click('[data-preset="undamped-down"]');
  await page.click('[data-eq="up"]');
  const st2 = await page.evaluate(() => appState.explorer);
  check(st2.eq === "up" && st2.eta0 === 0.1, "switching point keeps the perturbation value");
  check((await txt("#ex-now")).includes("=π+(0.1)=3.242"), "theta = pi + eta at t = 0: " + await txt("#ex-now"));

  // slider updates immediately
  const before = await page.locator("#ex-tplot").innerHTML();
  await page.locator("#ex-q").fill("2");
  check(await page.evaluate(() => appState.explorer.q) === 2, "q slider updates state");
  check(await page.locator("#ex-tplot").innerHTML() !== before, "plot redrawn after slider change");
  check((await txt("#ex-mats")).includes("2"), "A shows new q");
  await page.locator("#ex-d").fill("1");
    check((await txt("#ex-verdict")).includes("unstable"), "damped up is still unstable");
  await page.click('[data-eq="down"]');
  check((await txt("#ex-linear")).includes("underdamped") && !(await txt("#ex-linear")).includes("companion"), "d > 0 down is a taught underdamped case, not an extension");
  await page.locator("#ex-q").fill("1"); await page.locator("#ex-d").fill("2");
  check((await txt("#ex-linear")).includes("critically damped"), "critical damping classified");
  await page.locator("#ex-d").fill("0");
  await page.locator("#ex-du").fill("0.3");
  check((await txt("#ex-input-note")).includes("no longer a fixed point") && (await txt("#ex-model")).includes("input extension"), "du != 0 note and input-extension label");
  await page.locator("#ex-du").fill("0");

  // playback: elapsed wall-clock time at 4x; stop cancels and saves
  await page.locator("#ex-t").fill("0");
  await page.evaluate(() => { window.__studyExplorerSpeed = 4; });
  await page.click("#ex-play");
  const t0 = Date.now();
  await page.waitForTimeout(700);
  const tPlay = await page.evaluate(() => appState.explorer.t);
  const wall = (Date.now() - t0) / 1000;
  check(tPlay > 1.2 && tPlay <= 4 * wall + 0.3, `playback follows wall-clock time (t=${tPlay.toFixed(2)} after ${wall.toFixed(2)} s at 4x)`);
  const saves = await page.evaluate(() => window.__saves);
  await page.evaluate(() => StudyExplorer.stop());
  const tStop = await page.evaluate(() => appState.explorer.t);
  await page.waitForTimeout(300);
  check(await page.evaluate(() => appState.explorer.t) === tStop, "stop cancels playback");
  check(await page.evaluate(() => window.__saves) > saves, "stop saves the latest time");
  await page.evaluate(() => { window.__studyExplorerSpeed = 1000; });
  await page.click("#ex-play");
  await page.waitForTimeout(400);
  check(await page.evaluate(() => appState.explorer.t) === 12, "playback ends at T_MAX");
  check((await page.locator("#ex-play").innerText()).includes("Play"), "play button resets at end");

  // dark theme + mobile layout
  await page.evaluate(() => document.documentElement.setAttribute("data-theme", "dark"));
  await page.click('[data-preset="large-down"]');
  await page.screenshot({ path: path.join(SHOTS, "desktop-dark-large-down.png"), fullPage: true });
  const mobile = await open(390, 844);
  await mobile.evaluate(() => mount({ eq: "up", eta0: 0.05, nu0: 0, q: 1, du: 0, d: 0, t: 6 }));
  const overflow = await mobile.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  check(overflow <= 1, `no horizontal page overflow on mobile (${overflow}px)`);
  const minFont = await mobile.evaluate(() => {
    let m = 99;
    document.querySelectorAll(".lz-plot").forEach((svg) => {
      const k = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
      svg.querySelectorAll("text").forEach((t) => { m = Math.min(m, parseFloat(getComputedStyle(t).fontSize) * k); });
    });
    return m;
  });
  check(minFont >= 8.5, `mobile chart labels render at >= 8.5 px (min ${minFont.toFixed(1)} px)`);
  await mobile.screenshot({ path: path.join(SHOTS, "mobile-small-up.png"), fullPage: true });

  check(errors.length === 0, "console/page errors: " + errors.join(" | "));
  await browser.close();
  console.log(`${count - fails.length}/${count} explorer checks passed; screenshots in ${path.relative(process.cwd(), SHOTS)}`);
  fails.forEach((f) => console.log("FAIL: " + f));
  process.exit(fails.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
