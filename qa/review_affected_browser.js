// Targeted review check: typesetting and fit of the lessons touched by the review corrections.
// Usage (from the repository root): node qa/review_affected_browser.js
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");
const { chromium } = require(path.join(__dirname, "tooling", "node_modules", "playwright-core"));

const PROJECT = path.dirname(__dirname);
const PY = [path.join(PROJECT, ".venv", "Scripts", "python.exe"),
            path.join(path.dirname(PROJECT), "ManimGL", ".venv", "Scripts", "python.exe")].find(p => fs.existsSync(p))
           || "python";
const CHROME = process.env.CHROME_PATH || "C:/Program Files/Google/Chrome/Application/chrome.exe";
const results = [];
const check = (n, ok, d = "") => { results.push({ check: n, ok: !!ok, detail: String(d) });
  console.log((ok ? "PASS " : "FAIL ") + n + (d ? "  [" + d + "]" : "")); };

const PHRASES = {
  2: ["2|a|", "all solutions decay to zero exactly when every root has negative real part"],
  5: ["released from rest", "never more than once", "Started from rest"],
  6: ["give more differential-equations background"],
};

for (const d of ["screenshots", "results"]) fs.mkdirSync(path.join(__dirname, d), { recursive: true });

(async () => {
  const nonce = "review-" + Date.now();
  const portFile = path.join(os.tmpdir(), nonce + ".txt");
  const proc = spawn(PY, ["-I", path.join(PROJECT, "browser", "serve_local.py"), "--port", "8797", "--port-file", portFile, "--nonce", nonce]);
  let base = null, serverPid = null;
  for (let i = 0; i < 60 && !base; i++) {
    await new Promise(r => setTimeout(r, 200));
    if (!fs.existsSync(portFile)) continue;
    const port = fs.readFileSync(portFile, "utf8").trim();
    try {
      const h = await (await fetch(`http://127.0.0.1:${port}/__guide_health`)).json();
      if (h.nonce === nonce) { base = `http://127.0.0.1:${port}/`; serverPid = h.pid; }
    } catch (e) { /* not up yet */ }
  }
  const browser = await chromium.launch({ executablePath: CHROME, headless: true });
  try {
    for (const [label, opts] of [["desktop", { viewport: { width: 1366, height: 900 } }],
                                 ["mobile", { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true }]]) {
      const page = await (await browser.newContext(opts)).newPage();
      const errors = [];
      page.on("pageerror", e => errors.push(e.message));
      page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
      for (const n of [2, 5, 6]) {
        await page.goto(base + "#lesson-" + n, { waitUntil: "networkidle" });
        await page.waitForSelector(".lesson-section");
        const st = await page.evaluate(() => {
          const main = document.querySelector("#view");
          const plain = Array.from(main.querySelectorAll("p, li, aside")).map(el => {
            const c = el.cloneNode(true); c.querySelectorAll(".katex").forEach(k => k.remove()); return c.textContent; }).join(" ");
          const tex = Array.from(main.querySelectorAll("annotation")).map(a => a.textContent).join(" ");
          return { errors: main.querySelectorAll(".katex-error").length, raw: (plain.match(/\$/g) || []).length,
                   overflow: Array.from(main.querySelectorAll(".display-math, .step-math")).filter(d => d.scrollWidth > d.clientWidth + 1).length,
                   pageOverflow: document.documentElement.scrollWidth - innerWidth, text: plain + " " + tex };
        });
        const missing = PHRASES[n].filter(p => !st.text.includes(p));
        check(`${label} lesson ${n}: corrected text present, KaTeX clean, nothing overflows`,
              missing.length === 0 && st.errors === 0 && st.raw === 0 && st.overflow === 0 && st.pageOverflow <= 1,
              `missing=${JSON.stringify(missing)} errors=${st.errors} raw$=${st.raw} formulaOverflow=${st.overflow} pageOverflow=${st.pageOverflow}`);
      }
      if (label === "desktop") {
        await page.goto(base + "#lesson-5");
        await page.locator("#l5-p2").scrollIntoViewIfNeeded();
        await page.screenshot({ path: path.join(__dirname, "screenshots", "review_browser_lesson5_damping.png") });
        await page.goto(base + "#lesson-2");
        await page.locator("#l2-p4").scrollIntoViewIfNeeded();
        await page.screenshot({ path: path.join(__dirname, "screenshots", "review_browser_lesson2_complex.png") });
      }
      check(`${label}: no console/page errors`, errors.length === 0, errors.slice(0, 2).join(" | "));
    }
  } finally {
    await browser.close();
    try { process.kill(serverPid); } catch (e) { /* gone */ }
    proc.kill();
    try { fs.unlinkSync(portFile); } catch (e) { /* gone */ }
  }
  fs.writeFileSync(path.join(__dirname, "results", "review_affected_browser.json"), JSON.stringify(results, null, 2));
  const failed = results.filter(r => !r.ok).length;
  console.log(`\n${results.length - failed}/${results.length} affected-page browser checks passed`);
  process.exit(failed ? 1 : 0);
})();
