// Headless browser regression QA for courses/ode/browser/dist, using the installed Chrome (no browser download).
// Usage (from the repository root): node qa/browser_qa.js
// Covers routing, lesson notes (KaTeX, fit, worked examples), the explorer (exact solution,
// sliders, presets, zero solution, marker), the quiz, further reading, mobile layout and static
// checks of dist. The animation stage, media and themes are covered by qa/stage_qa.js.
// Screenshots: qa/screenshots/browser-redo/regression, results: qa/results/browser-redo.
"use strict";
const path = require("path");
const fs = require("fs");
const { PROJECT, DIST, recorder, startServer, launch } = require("./qa_common");

const SHOTS = path.join(__dirname, "screenshots", "browser-redo", "regression");
const RESULTS = path.join(__dirname, "results", "browser-redo");
fs.mkdirSync(SHOTS, { recursive: true });
fs.mkdirSync(RESULTS, { recursive: true });

const course = JSON.parse(fs.readFileSync(path.join(DIST, "course.json"), "utf8"));
const manifest = JSON.parse(fs.readFileSync(path.join(DIST, "animations", "manifest.json"), "utf8"));
const { results, check } = recorder();

let stopServer = () => {};
async function main() {
  const { base: BASE, stop } = await startServer(8790);
  stopServer = stop;
  check("local server started on loopback and passed identity health check", true, BASE);

  const clip = manifest.sequences[0].steps[0].transition.src;
  const mp4 = await fetch(BASE + clip, { headers: { Range: "bytes=0-99" } });
  check("server: MP4 byte ranges (206, video/mp4) for step clips", mp4.status === 206 && mp4.headers.get("content-type") === "video/mp4",
        mp4.status + " " + mp4.headers.get("content-type"));
  const js = await fetch(BASE + "app.js");
  check("server: JavaScript MIME type", (js.headers.get("content-type") || "").startsWith("text/javascript"));

  const browser = await launch();
  const external = [];
  const consoleErrors = [];
  async function newPage(opts) {
    const ctx = await browser.newContext(opts);
    const page = await ctx.newPage();
    page.on("console", m => { if (m.type() === "error") consoleErrors.push(m.text()); });
    page.on("pageerror", e => consoleErrors.push("pageerror: " + e.message));
    page.on("response", r => { if (r.status() >= 400) consoleErrors.push("HTTP " + r.status() + " " + r.url()); });
    page.on("request", r => { if (!r.url().startsWith(BASE) && !r.url().startsWith("data:")) external.push(r.url()); });
    return page;
  }
  const snap = p => p.evaluate(() => window.SecondOrderGuide.snapshot());

  // ------------------------------------------------------------------ desktop
  const page = await newPage({ viewport: { width: 1366, height: 900 } });
  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.waitForSelector(".stage-wrap h2.stage-title");
  check("home is the animated-derivations page with the characteristic derivation on stage",
        /Watch the derivations/.test(await page.textContent("h1")) && (await snap(page)).player.seq === "characteristic");
  check("sidebar lists start page, 6 lessons, explorer, quiz, reading", (await page.$$(".chapters a")).length === 10);

  const lessonStats = [];
  for (const lesson of course.lessons) {
    await page.goto(BASE + "#lesson-" + lesson.number);
    await page.waitForFunction(n => document.querySelector("h1") && document.title.includes(n), lesson.title);
    await page.evaluate(() => document.querySelectorAll("#view details").forEach(d => { d.open = true; }));
    const st = await page.evaluate(() => {
      const main = document.querySelector("#view");
      const notes = main.querySelector(".notes");
      const text = Array.from(main.querySelectorAll("p, li, aside, summary")).map(n => {
        const c = n.cloneNode(true);
        c.querySelectorAll(".katex").forEach(k => k.remove());
        return c.textContent;
      }).join(" ");
      const disp = Array.from(notes.querySelectorAll(".display-math, .step-math"));
      return {
        katex: main.querySelectorAll(".katex").length,
        errors: main.querySelectorAll(".katex-error").length,
        rawDollar: (text.match(/\$/g) || []).length,
        overflow: disp.filter(d => d.scrollWidth > d.clientWidth + 1).length,
        sections: notes.querySelectorAll(".lesson-section").length,
        examples: notes.querySelectorAll(".example").length,
        clips: notes.querySelectorAll("details.clip").length,
        stage: !!main.querySelector(".stage-wrap"),
        seq: window.SecondOrderGuide.snapshot().player.seq
      };
    });
    st.lesson = lesson.number;
    lessonStats.push(st);
  }
  check("all 6 lessons render every course page as a notes section",
        lessonStats.every((s, i) => s.sections === course.lessons[i].pages.length), lessonStats.map(s => s.sections).join(","));
  check("every lesson opens with the animation stage showing one of its own derivations",
        lessonStats.every(s => s.stage && manifest.sequences.some(q => q.id === s.seq && q.lesson === s.lesson)),
        lessonStats.map(s => s.lesson + ":" + s.seq).join(" "));
  check("KaTeX typesets lesson math (no katex-error, no raw $)",
        lessonStats.every(s => s.katex > 5 && s.errors === 0 && s.rawDollar === 0),
        lessonStats.map(s => `L${s.lesson}:${s.katex}/${s.errors}/${s.rawDollar}`).join(" "));
  check("note formulas and written solutions fit their column at 1366px",
        lessonStats.every(s => s.overflow === 0), lessonStats.map(s => s.overflow).join(","));
  check("all six worked examples are in the notes", lessonStats.reduce((a, s) => a + s.examples, 0) === course.examples.length);
  check("the three original overview clips remain in the notes (collapsed)",
        lessonStats.reduce((a, s) => a + s.clips, 0) === 3, lessonStats.map(s => s.clips).join(","));

  // sidebar navigation by click
  await page.goto(BASE + "#lesson-1");
  await page.waitForSelector(".notes");
  await page.click(".chapters a[data-route='lesson-2']");
  await page.waitForFunction(() => location.hash === "#lesson-2");
  check("clicking the sidebar navigates and marks the current chapter",
        (await page.textContent("h1")).trim() === course.lessons[1].title &&
        (await page.getAttribute(".chapters a[data-route='lesson-2']", "aria-current")) === "page");
  check("focus moves to the new heading after navigation", await page.evaluate(() => document.activeElement.tagName === "H1"));

  // overview clips load only when opened
  const before = await page.$$eval("details.clip video", v => v.length);
  await page.locator("details.clip summary").first().click();
  await page.waitForFunction(() => { const v = document.querySelector("details.clip video"); return v && v.readyState >= 1; }, null, { timeout: 15000 });
  const dur = await page.$eval("details.clip video", v => v.duration);
  check("overview clip is created only when its notes entry is opened, then loads", before === 0 && dur > 10, `before=${before} duration=${dur.toFixed(1)}s`);

  // worked example: written solution + animate button
  await page.goto(BASE + "#lesson-3");
  await page.waitForSelector("#ex-ex-distinct");
  const exSel = "#ex-ex-distinct";
  await page.click(exSel + " details.written summary");
  const steps = await page.$$eval(exSel + " .steps li", ls => ls.length);
  const ans = await page.$eval(exSel + " .answer annotation", a => a.textContent);
  check("written solution shows all 5 steps and the answer 2e^t - e^(2t)",
        steps === 5 && /2e\^\{t\}\s*-\s*e\^\{2t\}/.test(ans), ans);
  await page.click("#ex-ex-repeated [data-action='watch-example']");
  await page.waitForFunction(() => location.hash === "#lesson-3/ivp-repeated");
  const sp = await snap(page);
  check("'Animate this example' loads that example's derivation on the stage and updates the link",
        sp.player.seq === "ivp-repeated" && /ivp-repeated\/state-00\.jpg$/.test(sp.player.still), JSON.stringify(sp.player));
  await page.screenshot({ path: path.join(SHOTS, "lesson3_example_on_stage.png") });

  // ------------------------------------------------------------------ explorer
  await page.goto(BASE + "#explorer");
  await page.waitForSelector("#plot .curve");
  const badge = () => page.$eval("#class-badge", b => ({ text: b.textContent, kind: b.getAttribute("data-kind") }));
  check("explorer labels its scope as the constant-coefficient homogeneous spring subset",
        /Constant-coefficient homogeneous mass-spring model/.test(await page.textContent(".scope")) &&
        /subset/.test(await page.textContent(".scope")));
  let s0 = await snap(page);
  check("explorer defaults", JSON.stringify(s0.explorer) === JSON.stringify({ a: 1, b: 2, c: 4, y0: 1, v0: 0 }), JSON.stringify(s0.explorer));
  check("default classification underdamped", (await badge()).kind === "underdamped");

  async function curveError() {
    return page.evaluate(() => {
      const st = window.SecondOrderGuide.snapshot().explorer;
      const d = document.querySelector("#plot .curve").getAttribute("d");
      const pts = d.slice(1).split("L").map(p => p.split(" ").map(Number));
      const B = Number(document.querySelector("#plot").getAttribute("data-bound"));
      const P = { w: 640, h: 340, l: 52, r: 26, t: 24, b: 34 };
      let worst = 0;
      pts.forEach((p, i) => {
        const t = 8 * i / (pts.length - 1);
        const y = window.ODEMath.solution(t, st.a, st.b, st.c, st.y0, st.v0);
        const X = P.l + (t / 8) * (P.w - P.l - P.r);
        const Y = P.t + (1 - (y / B + 1) / 2) * (P.h - P.t - P.b);
        worst = Math.max(worst, Math.abs(p[0] - X), Math.abs(p[1] - Y));
      });
      return { worst, n: pts.length };
    });
  }
  let ce = await curveError();
  check("SVG curve matches the exact solution (401 points)", ce.n === 401 && ce.worst < 0.01, JSON.stringify(ce));

  await page.focus("#s-b");
  await page.keyboard.press("Home");
  check("keyboard Home on b -> b = 0, undamped", (await snap(page)).explorer.b === 0 && (await badge()).kind === "undamped");
  for (let i = 0; i < 80; i++) await page.keyboard.press("ArrowRight");
  s0 = await snap(page);
  check("80 x ArrowRight -> b = 4, critically damped, repeated root label",
        s0.explorer.b === 4 && (await badge()).kind === "critical" && /double/.test(await page.textContent(".readouts")),
        s0.explorer.b + " " + (await badge()).text);
  check("slider output shows the value", (await page.textContent("#s-b-out")) === "4.00");
  ce = await curveError();
  check("curve updated to the critical solution", ce.worst < 0.01);

  const dBefore = await page.getAttribute("#plot .curve", "d");
  const box = await page.locator("#s-c").boundingBox();
  await page.mouse.move(box.x + box.width * (4 - 0.5) / 8.5, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.85, box.y + box.height / 2, { steps: 8 });
  await page.mouse.up();
  s0 = await snap(page);
  check("mouse drag on c changes c and redraws immediately",
        s0.explorer.c > 6.5 && (await page.getAttribute("#plot .curve", "d")) !== dBefore, "c = " + s0.explorer.c);

  await page.focus("#s-y0");
  for (let i = 0; i < 50; i++) await page.keyboard.press("ArrowLeft");
  await page.focus("#s-v0");
  for (let i = 0; i < 40; i++) await page.keyboard.press("ArrowRight");
  for (const p of course.explorer.presets) {
    await page.click(`[data-preset='${p.id}']`);
    s0 = await snap(page);
    const b = await badge();
    const pressed = await page.getAttribute(`[data-preset='${p.id}']`, "aria-pressed");
    ce = await curveError();
    check(`preset ${p.label}: a,b,c set, y0/v0 kept, class ${p.id}, aria-pressed`,
          s0.explorer.a === p.a && s0.explorer.b === p.b && s0.explorer.c === p.c &&
          s0.explorer.y0 === -1.5 && s0.explorer.v0 === 2 && b.kind === p.id && pressed === "true" && ce.worst < 0.01,
          JSON.stringify(s0.explorer) + " " + b.kind);
  }
  check("slider inputs reflect the preset", (await page.inputValue("#s-b")) === "5" && (await page.inputValue("#s-c")) === "4");

  await page.focus("#s-y0");
  for (let i = 0; i < 30; i++) await page.keyboard.press("ArrowRight");
  await page.focus("#s-v0");
  for (let i = 0; i < 40; i++) await page.keyboard.press("ArrowLeft");
  s0 = await snap(page);
  const zero = await page.evaluate(() => {
    const svg = document.querySelector("#plot");
    const d = svg.querySelector(".curve").getAttribute("d");
    const ys = d.slice(1).split("L").map(p => Number(p.split(" ")[1]));
    return { zero: svg.getAttribute("data-zero"), bound: svg.getAttribute("data-bound"),
             spread: Math.max(...ys) - Math.min(...ys), note: getComputedStyle(svg.querySelector(".zero-note")).display,
             desc: svg.querySelector("desc").textContent };
  });
  check("y0 = v0 = 0 -> flat zero curve, axis bound 1, uniqueness note, honest description",
        s0.explorer.y0 === 0 && s0.explorer.v0 === 0 && zero.zero === "true" && zero.bound === "1" &&
        zero.spread === 0 && zero.note !== "none" && /zero solution/.test(zero.desc), JSON.stringify(zero));
  await page.screenshot({ path: path.join(SHOTS, "explorer_zero.png") });

  await page.click("#reset-btn");
  s0 = await snap(page);
  check("Reset restores all five defaults", JSON.stringify(s0.explorer) === JSON.stringify({ a: 1, b: 2, c: 4, y0: 1, v0: 0 }));
  await page.click("#play-btn");
  await page.waitForTimeout(900);
  s0 = await snap(page);
  check("Play moves the time marker", s0.marker.playing && s0.marker.t > 0.4 &&
        (await page.getAttribute("#play-btn", "aria-pressed")) === "true", "t = " + s0.marker.t.toFixed(2));
  const mark = await page.textContent(".marker-readout");
  check("marker readout shows t and y(t)", /^t = \d+\.\d\d {3}y\(t\) = -?\d+\.\d\d$/.test(mark), mark);
  await page.click("#play-btn");
  const tPaused = (await snap(page)).marker.t;
  await page.waitForTimeout(400);
  check("Pause stops the marker", !(await snap(page)).marker.playing && (await snap(page)).marker.t === tPaused);
  check("plot has an accessible name and description",
        (await page.getAttribute("#plot", "role")) === "img" &&
        (await page.textContent("#plot-desc")).includes("Underdamped"));
  await page.focus("#s-a");
  const kBefore = (await snap(page)).player;
  await page.keyboard.press("ArrowRight");
  const sAfter = await snap(page);
  check("arrow keys on a slider move the slider, not the animation stage",
        sAfter.explorer.a === 1.05 && sAfter.player.k === kBefore.k && !sAfter.player.playing, "a = " + sAfter.explorer.a);

  // ------------------------------------------------------------------ quiz
  await page.goto(BASE + "#quiz");
  await page.waitForSelector(".choice");
  const q0 = course.quiz[0], q1 = course.quiz[1];
  const wrong = (q0.answer + 1) % q0.choices.length;
  check("quiz shows question 1 of " + course.quiz.length, (await page.textContent(".topic")).startsWith("Question 1 of " + course.quiz.length));
  await page.click(`.choice[data-index='${wrong}']`);
  const fbWrong = await page.textContent(".feedback");
  check("wrong answer: marked wrong with its own explanation",
        (await page.getAttribute(`.choice[data-index='${wrong}']`, "data-state")) === "wrong" &&
        fbWrong.startsWith("Not quite") && (await page.isVisible(".feedback")), fbWrong.slice(0, 70));
  await page.screenshot({ path: path.join(SHOTS, "quiz_wrong.png") });
  await page.click(`.choice[data-index='${q0.answer}']`, { force: true });
  check("answers lock until Try again", (await page.getAttribute(`.choice[data-index='${wrong}']`, "data-state")) === "wrong");
  await page.click("text=Try again");
  check("Try again clears the answer", !(await page.isVisible(".feedback")) &&
        (await page.getAttribute(`.choice[data-index='${wrong}']`, "data-state")) === null);
  await page.click(`.choice[data-index='${q0.answer}']`);
  check("correct answer: marked correct + explanation",
        (await page.getAttribute(`.choice[data-index='${q0.answer}']`, "data-state")) === "correct" &&
        (await page.textContent(".feedback")).startsWith("Correct"));
  check("score counts first tries only", (await page.textContent(".score")) === "First-try correct: 0 / 1 answered");
  await page.click("text=Next →");
  await page.keyboard.press("abcd"[q1.answer]);
  check("letter key answers question 2 (stage keys do not interfere on the quiz)",
        (await page.getAttribute(`.choice[data-index='${q1.answer}']`, "data-state")) === "correct" &&
        (await page.textContent(".score")) === "First-try correct: 1 / 2 answered");
  check("question dots show status", (await page.getAttribute(".q-dots li:nth-child(1) button", "data-status")) === "correct");
  await page.screenshot({ path: path.join(SHOTS, "quiz_correct.png") });
  await page.click("text=Reset quiz");
  check("Reset quiz clears everything", (await page.textContent(".score")) === "First-try correct: 0 / 0 answered" &&
        (await page.textContent(".topic")).startsWith("Question 1 of"));
  for (let i = 0; i < course.quiz.length; i++) {
    await page.click(`.choice[data-index='${course.quiz[i].answer}']`);
    if (i < course.quiz.length - 1) await page.click("text=Next →");
  }
  check("all questions answerable; finished score shown",
        (await page.textContent(".score")).includes(`finished (${course.quiz.length}/${course.quiz.length})`), await page.textContent(".score"));
  check("no KaTeX errors in quiz", (await page.$$eval(".katex-error", e => e.length)) === 0);

  await page.goto(BASE + "#reading");
  await page.waitForSelector(".reading-list a");
  const links = await page.$$eval(".reading-list a", as => as.map(a => a.href));
  check("further reading links both MIT sources", links.length === 2 && links.every(u => u.startsWith("https://ocw.mit.edu/")));

  // ------------------------------------------------------------------ mobile
  const mob = await newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  await mob.goto(BASE + "#lesson-2", { waitUntil: "networkidle" });
  await mob.waitForSelector(".stage-wrap");
  check("mobile: chapter list collapsed behind a toggle", !(await mob.isVisible("#chapters")) && (await mob.isVisible(".nav-toggle")));
  const overflowAt = async () => mob.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  check("mobile: no page-level horizontal overflow (lesson 2)", (await overflowAt()) <= 1, await overflowAt());
  await mob.click(".nav-toggle");
  check("mobile: toggle opens the chapter list", (await mob.isVisible("#chapters")) &&
        (await mob.getAttribute(".nav-toggle", "aria-expanded")) === "true");
  await mob.screenshot({ path: path.join(SHOTS, "mobile_nav.png") });
  await mob.click(".chapters a[data-route='explorer']");
  await mob.waitForSelector("#plot .curve");
  check("mobile: choosing a chapter navigates and closes the list", !(await mob.isVisible("#chapters")));
  const stack = await mob.evaluate(() => {
    const p = document.querySelector(".plot-card").getBoundingClientRect();
    const c = document.querySelector(".controls").getBoundingClientRect();
    return { stacked: c.top >= p.bottom - 1, plotW: p.width, overflow: document.documentElement.scrollWidth - innerWidth };
  });
  check("mobile: explorer stacks plot above controls with no overflow", stack.stacked && stack.overflow <= 1, JSON.stringify(stack));
  await mob.locator("[data-preset='overdamped']").tap();
  check("mobile: tapping a preset works", (await mob.evaluate(() => window.SecondOrderGuide.snapshot().explorer.b)) === 5);
  const mobileOverflow = [];
  for (const r of ["watch", "lesson-1", "lesson-3", "lesson-4", "lesson-5", "lesson-6", "quiz", "reading"]) {
    await mob.goto(BASE + "#" + r);
    await mob.waitForSelector("h1");
    await mob.waitForTimeout(150);
    mobileOverflow.push(r + ":" + (await overflowAt()));
  }
  check("mobile: no page-level horizontal overflow on any route", mobileOverflow.every(x => +x.split(":")[1] <= 1), mobileOverflow.join(" "));
  await mob.goto(BASE + "#quiz");
  await mob.waitForSelector(".choice");
  await mob.locator(`.choice[data-index='${course.quiz[0].answer}']`).tap();
  await mob.screenshot({ path: path.join(SHOTS, "mobile_quiz.png"), fullPage: true });
  const wideMath = [];
  for (let n = 1; n <= 6; n++) {
    await mob.goto(BASE + "#lesson-" + n);
    await mob.waitForSelector(".notes");
    const out = await mob.evaluate(() => {
      document.querySelectorAll(".notes details.written").forEach(d => { d.open = true; });
      return Array.from(document.querySelectorAll(".notes .display-math, .notes .step-math"))
        .filter(d => d.scrollWidth > d.clientWidth + 1).length;
    });
    if (out) wideMath.push(`L${n}:${out}`);
  }
  check("mobile: every note formula and written-solution step fits a 390px screen without scrolling",
        wideMath.length === 0, wideMath.length ? "boxes that overflow: " + wideMath.join(" ") : "none");

  check("no requests to any non-local host (all assets bundled)", external.length === 0, external.slice(0, 3).join(" "));
  check("no console errors or page errors", consoleErrors.length === 0, consoleErrors.slice(0, 3).join(" | "));

  await browser.close();
  stop();

  // ------------------------------------------------------------------ static checks of dist
  const files = [];
  (function walk(d) {
    for (const f of fs.readdirSync(d)) {
      const p = path.join(d, f);
      if (fs.statSync(p).isDirectory()) walk(p); else files.push(p);
    }
  })(DIST);
  const textFiles = files.filter(f => /\.(html|css|js|json|txt)$/.test(f) && !f.includes(path.join("vendor", "katex")));
  const bad = [];
  for (const f of textFiles) {
    const t = fs.readFileSync(f, "utf8");
    // Drive-letter paths into real folders, user folders, file URLs. (Plain "x:\\" also occurs in
    // TeX such as "4mk:\\ \\text", so a bare drive-letter pattern would be a false positive.)
    if (/\b[A-Za-z]:(\\\\|\\|\/)(Users|Program Files|Windows|Documents)|\\Users\\|\/Users\/|file:\/\/|OneDrive/i.test(t))
      bad.push(path.relative(DIST, f) + ": local path");
    // Credential-shaped values (the player's numeric playback "token" counter is not one).
    if (/appgprj_|api[_-]?key|secret|password|bearer\s+[A-Za-z0-9]|token\s*[:=]\s*["'][A-Za-z0-9_\-.]{12,}/i.test(t))
      bad.push(path.relative(DIST, f) + ": credential-like text");
  }
  check("app files contain no local absolute paths or credentials", bad.length === 0, bad.join("; "));
  check("dist/course.json is an exact copy of the shared course.json",
        fs.readFileSync(path.join(PROJECT, "courses/ode/course.json"), "utf8") === fs.readFileSync(path.join(DIST, "course.json"), "utf8"));
  const mediaOk = course.lessons.flatMap(l => l.pages).flatMap(p => p.blocks).filter(b => b.type === "video")
    .every(b => fs.existsSync(path.join(DIST, b.src)) &&
                fs.readFileSync(path.join(DIST, b.src)).equals(fs.readFileSync(path.join(PROJECT, "media", path.basename(b.src)))));
  check("every original overview clip exists in dist/media and matches the Manim render", mediaOk);
  check("KaTeX vendored with fonts and license", fs.existsSync(path.join(DIST, "vendor/katex/LICENSE")) &&
        fs.readdirSync(path.join(DIST, "vendor/katex/fonts")).filter(f => f.endsWith(".woff2")).length >= 20);

  fs.writeFileSync(path.join(RESULTS, "browser_results.json"),
                   JSON.stringify({ base: BASE, results, lessonStats, mobileOverflow, wideMath }, null, 2));
  const failed = results.filter(r => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} browser regression checks passed`);
  process.exit(failed.length ? 1 : 0);
}

main().catch(e => { console.error(e); stopServer(); process.exit(2); });
