// End-to-end browser checks for the Control Bootcamp companion (headless installed Chrome).
//   node qa/control_browser_qa.js
// Covers: every animation sequence stepped through with real clip playback (sped up 4x for the
// check only), Back/Replay/Restart, keyboard, persistence and corrupt storage, worked examples,
// quiz first-try scoring/retry/reset, themes and contrast, explorer cases, reduced motion, media
// failures, desktop + mobile navigation, overflow, and the tutor: missing key (real server, no key)
// and a MOCKED Responses API (a local fake; no live OpenAI call is made).
"use strict";
const http = require("http");
const path = require("path");
const fs = require("fs");
const { PROJECT, DIST, recorder, startServer, launch, contrast } = require("./control_qa_common.js");

const { results, check } = recorder();
const manifest = JSON.parse(fs.readFileSync(path.join(DIST, "animations", "manifest.json"), "utf8"));
const course = JSON.parse(fs.readFileSync(path.join(DIST, "course.json"), "utf8"));
const SHOTS = path.join(PROJECT, "qa", "screenshots", "control");
fs.mkdirSync(SHOTS, { recursive: true });

async function newPage(browser, opts) {
  const ctx = await browser.newContext(Object.assign({ viewport: { width: 1440, height: 900 } }, opts || {}));
  await ctx.addInitScript(() => {
    const play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () { this.playbackRate = 4; return play.call(this); };
  });
  const page = await ctx.newPage();
  page.errors = [];
  page.on("console", m => { if (m.type() === "error") page.errors.push(m.text()); });
  page.on("pageerror", e => page.errors.push("pageerror: " + e.message));
  return { ctx, page };
}

const wrapSel = ".stage-wrap";
async function stepState(page) {
  return page.evaluate(() => {
    const w = document.querySelector(".stage-wrap");
    const still = document.querySelector(".stage-still");
    return w ? { seq: w.dataset.seq, step: +w.dataset.step, playing: w.dataset.playing === "true",
                 still: still.getAttribute("src"), fallback: !document.querySelector(".stage-fallback").hidden,
                 notice: document.querySelector(".stage-notice").hidden ? "" : document.querySelector(".stage-notice").textContent } : null;
  });
}
async function waitStep(page, k, timeout) {
  await page.waitForFunction(k => {
    const w = document.querySelector(".stage-wrap");
    const img = document.querySelector(".stage-still");
    return w && w.dataset.playing === "false" && w.dataset.step === String(k) && img.complete && img.naturalWidth > 0 &&
      !document.querySelector(".stage").classList.contains("video-on");
  }, k, { timeout: timeout || 20000 });
}
function frameOf(sq, k) { return k === 0 ? sq.initial.frame : sq.steps[k - 1].finalFrame; }

async function sawVideo(page) {
  return page.evaluate(() => new Promise(res => {
    const stage = document.querySelector(".stage");
    if (stage.classList.contains("video-on")) return res(true);
    const mo = new MutationObserver(() => { if (stage.classList.contains("video-on")) { mo.disconnect(); res(true); } });
    mo.observe(stage, { attributes: true });
    setTimeout(() => { mo.disconnect(); res(false); }, 8000);
  }));
}

async function noOverflow(page) {
  return page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
}

// ---------------------------------------------------------------------------- mock Responses API
function startMock() {
  const seen = [];
  const srv = http.createServer((req, res) => {
    let body = "";
    req.on("data", d => { body += d; });
    req.on("end", () => {
      seen.push(JSON.parse(body));
      const text = "Because both terms end in $x$: $$Ax - BKx = (A - BK)x$$\n\n- order: $B$ then $K$\n- <img src=x onerror=\"window.__pwned=1\">";
      const out = JSON.stringify({ status: "completed", output: [{ type: "message", role: "assistant", content: [{ type: "output_text", text }] }] });
      res.writeHead(200, { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(out) });
      res.end(out);
    });
  });
  return new Promise(r => srv.listen(0, "127.0.0.1", () => r({ srv, port: srv.address().port, seen })));
}

(async () => {
  const srv = await startServer(8900);
  const browser = await launch();
  try {
    // ======================================================================== desktop
    const { ctx, page } = await newPage(browser);
    await page.goto(srv.base + "#s1");
    await page.waitForSelector(wrapSel);
    check("desktop: s1 loads with stage and step card", await page.isVisible(".step-card") && await page.isVisible(".stage"));
    check("nav lists 6 sections and 3 practice links", (await page.$$eval(".section-links a", a => a.length)) === 6 &&
      (await page.$$eval(".tool-links a", a => a.length)) === 3);
    check("current section marked aria-current", (await page.getAttribute('.section-links a[data-route="s1"]', "aria-current")) === "page");
    check("default theme is light", (await page.getAttribute("html", "data-theme")) === "light");
    check("no marketing splash: the first screen is a lesson with Next step", await page.isVisible('[data-action="next"]'));

    // every sequence, every step, real playback
    let played = 0, missing = [];
    for (const sq of manifest.sequences) {
      await page.goto(srv.base + "#s" + sq.section + "/" + sq.id);
      await page.waitForFunction(id => { const w = document.querySelector(".stage-wrap"); return w && w.dataset.seq === id; }, sq.id);
      await page.click('[data-action="restart"]').catch(() => {});
      await waitStep(page, 0);
      let ok = (await stepState(page)).still === frameOf(sq, 0);
      for (let k = 1; k <= sq.steps.length; k++) {
        const seen = sawVideo(page);
        await page.click('[data-action="next"]');
        const vid = await seen;
        await waitStep(page, k, 30000);
        const st = await stepState(page);
        if (!vid) missing.push(sq.id + ":" + k);
        else played++;
        if (st.still !== frameOf(sq, k) || st.fallback || st.notice) ok = false;
        const title = await page.textContent("#step-title");
        if (!title.trim()) ok = false;
      }
      check(`sequence ${sq.id}: ${sq.steps.length} steps play and settle on the matching still`, ok);
      if (sq.id === "close-loop") await page.screenshot({ path: path.join(SHOTS, "qa-desk-close-loop-end.png") });
    }
    check("every step's clip was actually shown (video layer on)", missing.length === 0, played + " played; missing " + missing.join(","));
    check("completion box offers the next animation/section", await page.isVisible(".complete-box"));

    // back / replay / restart / keyboard on close-loop
    const cl = manifest.sequences.find(s => s.id === "close-loop");
    await page.goto(srv.base + "#s5");
    await waitStep(page, cl.steps.length);
    check("persisted step restored after navigation", (await stepState(page)).step === cl.steps.length);
    await page.click('[data-action="back"]');
    await waitStep(page, cl.steps.length - 1);
    check("Back jumps to the previous stable state", (await stepState(page)).still === frameOf(cl, cl.steps.length - 1));
    const rp = sawVideo(page);
    await page.click('[data-action="replay"]');
    check("Replay plays the current step's clip again", await rp);
    await waitStep(page, cl.steps.length - 1);
    await page.click('[data-action="restart"]');
    await waitStep(page, 0);
    check("Restart returns to state 0", (await stepState(page)).step === 0);
    await page.focus("body");
    await page.keyboard.press("ArrowRight");
    await waitStep(page, 1);
    await page.keyboard.press("n");
    await waitStep(page, 2);
    await page.keyboard.press("b");
    await waitStep(page, 1);
    check("keyboard: → / N next, B back", (await stepState(page)).step === 1);
    const kr = sawVideo(page);
    await page.keyboard.press("r");
    check("keyboard: R replays", await kr);
    await waitStep(page, 1);
    // back during playback stops at previous state
    await page.click('[data-action="next"]');
    await page.waitForFunction(() => document.querySelector(".stage-wrap").dataset.playing === "true");
    await page.click('[data-action="back"]');
    await waitStep(page, 1);
    check("Back while playing stops and shows the previous state", (await stepState(page)).step === 1);
    // tutor context follows the step
    await page.click("#tutor-toggle");
    await page.waitForSelector("#tutor:not([hidden])");
    const ctxText = await page.textContent("#tutor-context");
    check("tutor context names section 5 and the current step", /Section 5/.test(ctxText) && /step 1 of 5/.test(ctxText), ctxText);
    check("missing key: tutor shows 'not set up' and setup guidance", /not set up/.test(await page.textContent("#tutor-status")) &&
      /OPENAI_API_KEY/.test(await page.textContent(".tutor-setup")));
    check("GPT tutor is labelled as GPT (toggle, heading, step button)",
      /Ask GPT/.test(await page.textContent("#tutor-toggle")) && (await page.textContent(".tutor-head h2")) === "GPT tutor" &&
      /Ask GPT about this step/.test(await page.textContent('[data-action="ask"]')) &&
      (await page.getAttribute("#tutor", "aria-label")) === "GPT tutor");
    check("missing key: setup text is honest that GPT chat is off", /no OpenAI API key is configured, so it is off/.test(await page.textContent(".tutor-setup")));
    check("missing key: input and send disabled (no fake replies possible)", await page.isDisabled("#tutor-input") &&
      await page.isDisabled(".tutor-form button[type=submit]"));
    await page.screenshot({ path: path.join(SHOTS, "qa-desk-s5-tutor.png") });
    check("desktop with tutor open: no horizontal overflow", await noOverflow(page));
    await page.click(".tutor-close");

    // sequence switcher in section 3
    await page.goto(srv.base + "#s3");
    await page.waitForSelector(".seq-btn");
    await page.click('.seq-btn[data-seq="why-feedback"]');
    await page.waitForFunction(() => document.querySelector(".stage-wrap").dataset.seq === "why-feedback");
    await page.click('.seq-btn[data-seq="cruise-model"]');
    await page.waitForFunction(() => document.querySelector(".stage-wrap").dataset.seq === "cruise-model");
    check("section 3 switcher shows the cruise animation and updates the URL", /#s3\/cruise-model$/.test(page.url()));

    // worked example reveal
    await page.goto(srv.base + "#s6");
    await page.waitForSelector(".example");
    const nSteps = course.sections[5].example.steps.length;
    for (let i = 0; i < nSteps; i++) await page.click(".example .reveal-btn:not([hidden])");
    check("worked example reveals step by step, then the answer", (await page.$$eval(".example ol li", l => l.length)) === nSteps &&
      await page.isVisible(".ex-answer"));
    const srcLinks = await page.$$eval(".sources-list a", as => as.map(a => a.href));
    check("section sources link the lecture with &t= and the book with #page=", srcLinks.some(h => /youtube\.com\/watch\?v=Pi7l8mMjYVE&t=1110s/.test(h)) &&
      srcLinks.some(h => /#page=348$/.test(h)), srcLinks.slice(0, 4).join(" "));
    check("local /book link offered when databook.pdf is present", srcLinks.some(h => /\/book#page=348$/.test(h)));

    // theme toggle + contrast
    await page.click("#theme-toggle");
    check("dark theme toggles on", (await page.getAttribute("html", "data-theme")) === "dark");
    const cDark = await page.evaluate(() => {
      const bg = getComputedStyle(document.body).backgroundColor, cs = e => getComputedStyle(document.querySelector(e));
      return { text: [cs(".notes p").color, bg], muted: [cs(".lede").color, bg], link: [cs(".sources-list a").color, cs(".panel").backgroundColor],
               btn: [cs(".btn.primary") ? cs(".reveal-btn").color : "", cs(".reveal-btn").backgroundColor] };
    });
    await page.reload();
    await page.waitForSelector(".example");
    check("theme choice persists across reload", (await page.getAttribute("html", "data-theme")) === "dark");
    await page.click("#theme-toggle");
    const cLight = await page.evaluate(() => {
      const bg = getComputedStyle(document.body).backgroundColor, cs = e => getComputedStyle(document.querySelector(e));
      return { text: [cs(".notes p").color, bg], muted: [cs(".lede").color, bg], link: [cs(".sources-list a").color, cs(".panel").backgroundColor],
               btn: [cs(".reveal-btn").color, cs(".reveal-btn").backgroundColor] };
    });
    const low = [];
    for (const [nm, c] of Object.entries({ dark: cDark, light: cLight })) {
      for (const [k, [fg, bg]] of Object.entries(c)) { const r = contrast(fg, bg); if (r < 4.5) low.push(`${nm}.${k}=${r.toFixed(2)}`); }
    }
    check("text, muted text, links and buttons meet 4.5:1 in both themes", !low.length, low.join(", ") || "all ≥ 4.5");

    // explorer
    await page.goto(srv.base + "#explorer");
    await page.waitForSelector("#pend-verdict");
    const verdict = async () => [await page.getAttribute("#pend-verdict", "data-kind"), await page.textContent("#resp-note")];
    let v = await verdict();
    check("explorer default K=[4 4] is asymptotically stable", v[0] === "stable", v[0]);
    await page.click('[data-preset="open"]');
    v = await verdict();
    check("explorer: no feedback is unstable and says it leaves the plotted window", v[0] === "unstable" && /Leaves the plotted window/.test(v[1]), v);
    await page.click('[data-preset="drift"]');
    check("explorer: [1 0] is the Jordan boundary case", (await verdict())[0] === "drift" && /Jordan/.test(await page.textContent("#pend-detail")));
    await page.click('[data-preset="nodamp"]');
    check("explorer: [4 0] is a marginal undamped oscillation", (await verdict())[0] === "marginal" && /imaginary axis/.test(await page.textContent("#pend-detail")));
    await page.click('[data-preset="negdamp"]');
    check("explorer: negative velocity gain is unstable", (await verdict())[0] === "unstable");
    await page.click('[data-preset="book"]');
    const eigText = await page.textContent(".readout");
    check("explorer: book gain shows A - BK with -3, -4 and eigenvalues -1, -3", /−3/.test(eigText) && /−4/.test(eigText) && /−1/.test(eigText), eigText.slice(0, 120));
    await page.focus("#k1");
    for (let i = 0; i < 31; i++) await page.keyboard.press("ArrowLeft");
    check("explorer slider works from the keyboard (k1 4.0 → 0.9: unstable)", (await page.inputValue("#k1")) === "0.9" && (await verdict())[0] === "unstable");
    await page.click('[data-action="reset-explorer"]');
    await page.check("#pulse");
    const note = await page.textContent("#resp-note");
    check("explorer: push disturbance option draws and stays in range for K=[4 4]", /Peak/.test(note) && await page.$("#response .p-pulse") !== null, note);
    check("explorer: cruise readout shows 57.69 and 0.0385 for the defaults", /57\.69/.test(await page.textContent("#cruise-readout")) &&
      /0\.0385/.test(await page.textContent("#cruise-readout")));
    await page.screenshot({ path: path.join(SHOTS, "qa-desk-explorer.png"), fullPage: true });
    check("explorer: no horizontal overflow", await noOverflow(page));

    // quiz
    await page.goto(srv.base + "#quiz");
    await page.waitForSelector(".q-card");
    await page.click('[data-action="reset-quiz"]');
    const q0 = course.quiz[0], wrong0 = q0.choices.findIndex(c => !c.correct), right0 = q0.choices.findIndex(c => c.correct);
    await page.click(`.choice[data-choice="${wrong0}"]`);
    check("quiz: wrong answer explains and allows retry", /Not quite/.test(await page.textContent(".feedback")) &&
      await page.isDisabled(`.choice[data-choice="${wrong0}"]`) && !(await page.isDisabled(`.choice[data-choice="${right0}"]`)));
    await page.click(`.choice[data-choice="${right0}"]`);
    check("quiz: correct on second try still scores 0 (first try counts)", /First-try score: 0 of 10/.test(await page.textContent("#quiz-score")));
    await page.click('[data-action="next-question"]');
    const q1 = course.quiz[1], right1 = q1.choices.findIndex(c => c.correct);
    await page.keyboard.press(String(right1 + 1));
    check("quiz: keyboard number picks a choice; first-try correct scores 1", /First-try score: 1 of 10 · answered 2/.test(await page.textContent("#quiz-score")));
    await page.reload();
    await page.waitForSelector(".q-card");
    check("quiz answers persist across reload", /First-try score: 1 of 10 · answered 2/.test(await page.textContent("#quiz-score")));
    await page.click('[data-action="reset-quiz"]');
    check("quiz reset clears the score", /First-try score: 0 of 10 · answered 0/.test(await page.textContent("#quiz-score")));
    let allWhy = true;
    for (const q of course.quiz) for (const c of q.choices) if (!c.why || c.why.length < 20) allWhy = false;
    check("every quiz choice has an explanation; exactly one correct each", allWhy && course.quiz.every(q => q.choices.filter(c => c.correct).length === 1));
    const qu = course.quiz.find(q => q.id === "q-uncertainty");
    check("q-uncertainty: the only model-uncertainty option is the longer rod; the push option is an external force",
      qu.choices.filter(c => c.correct).map(c => c.text).join() === "The real rod is 1 cm longer than the model assumes." &&
      !qu.choices.some(c => /drag|window/i.test(c.text)) && qu.choices.some(c => /pushes the pendulum sideways/.test(c.text)));
    check("quiz has 8-10 questions", course.quiz.length >= 8 && course.quiz.length <= 10, course.quiz.length);

    // sources
    await page.goto(srv.base + "#sources");
    await page.waitForSelector(".src-table");
    const nTs = await page.$$eval(".src-table a[href*='&t=']", a => a.length);
    check("sources page lists every lecture timestamp", nTs === course.sections.reduce((n, s) => n + s.sources.video.length, 0), nTs);

    // corrupt storage
    await page.waitForTimeout(300);
    await page.evaluate(() => localStorage.setItem("ctl-overview-v1", '{"v":1,"theme":"neon","steps":{"close-loop":99,"x":2},"quiz":{"q-state":{"first":7,"tried":[7]}},"pend":{"k1":"evil"}}'));
    await page.reload();                      // load with the corrupt data first ...
    await page.waitForSelector(".src-table");
    await page.goto(srv.base + "#s5");        // ... then look at a section it tried to corrupt
    await page.waitForSelector(wrapSel);
    check("corrupt / out-of-range storage is ignored safely", (await stepState(page)).step === 0 && (await page.getAttribute("html", "data-theme")) === "light");
    await page.evaluate(() => localStorage.setItem("ctl-overview-v1", "{{{not json"));
    await page.reload();
    await page.waitForSelector(wrapSel);
    check("unparseable storage does not break the page", await page.isVisible(".stage"));
    check("desktop: no console errors", page.errors.length === 0, page.errors.slice(0, 3).join(" | "));
    await ctx.close();

    // ======================================================================== media failures
    {
      const { ctx, page } = await newPage(browser);
      await page.route("**/*.mp4", r => r.abort());
      await page.goto(srv.base + "#s4");
      await waitStep(page, 0);
      await page.click('[data-action="next"]');
      await waitStep(page, 1, 20000);
      const st = await stepState(page);
      check("clip failure: advances to the step and explains", st.step === 1 && /could not be played/.test(st.notice), st.notice);
      await ctx.close();
    }
    {
      const { ctx, page } = await newPage(browser);
      await page.route("**/state-*.jpg", r => r.abort());
      await page.goto(srv.base + "#s5");
      await page.waitForSelector(".stage-fallback:not([hidden]) .katex", { timeout: 10000 }).catch(() => {});
      check("still failure: KaTeX formula fallback shown in the stage", await page.isVisible(".stage-fallback .katex"));
      await ctx.close();
    }
    {
      const { ctx, page } = await newPage(browser);
      await page.route("**/animations/manifest.json", r => r.fulfill({ status: 404, body: "" }));
      await page.goto(srv.base + "#s2");
      await page.waitForSelector(".notes");
      check("no manifest: lesson notes still render with a notice", /could not be loaded/.test(await page.textContent("#view")));
      await ctx.close();
    }

    // ======================================================================== reduced motion
    {
      const { ctx, page } = await newPage(browser, { reducedMotion: "reduce" });
      await page.goto(srv.base + "#s6");
      await waitStep(page, 0);
      await page.click('[data-action="next"]');
      await waitStep(page, 1, 5000);
      const st = await stepState(page);
      check("reduced motion: Next jumps to the result with a Replay hint", st.step === 1 && /Reduced motion/.test(st.notice), st.notice);
      const rv = sawVideo(page);
      await page.click('[data-action="replay"]');
      check("reduced motion: Replay still plays the transition on request", await rv);
      await ctx.close();
    }

    // ======================================================================== mobile
    {
      const { ctx, page } = await newPage(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
      await page.goto(srv.base + "#s2");
      await page.waitForSelector(wrapSel);
      check("mobile: sidebar hidden behind the Sections button", !(await page.isVisible(".sidenav.open")) && await page.isVisible(".nav-toggle"));
      await page.click(".nav-toggle");
      await page.waitForSelector(".sidenav.open");
      check("mobile: Sections opens the drawer", (await page.getAttribute(".nav-toggle", "aria-expanded")) === "true");
      await page.keyboard.press("Escape");
      check("mobile: Escape closes the drawer", (await page.getAttribute(".nav-toggle", "aria-expanded")) === "false");
      await page.click(".nav-toggle");
      await page.click('.section-links a[data-route="s4"]');
      await page.waitForFunction(() => location.hash === "#s4");
      check("mobile: drawer link navigates and closes", !(await page.$(".sidenav.open")));
      const box = await page.locator(".stage").boundingBox();
      check("mobile: stage fills the width", box && box.width > 340, box && box.width);
      await page.tap('[data-action="next"]');
      await waitStep(page, 1, 30000);
      check("mobile: Next works by touch", (await stepState(page)).step === 1);
      let over = [];
      for (const r of ["s1", "s3", "s5", "s6", "explorer", "quiz", "sources"]) {
        await page.goto(srv.base + "#" + r);
        await page.waitForTimeout(250);
        if (!(await noOverflow(page))) over.push(r);
      }
      check("mobile: no horizontal overflow on any page", !over.length, over.join(","));
      await page.goto(srv.base + "#s5");
      await page.click("#tutor-toggle");
      await page.waitForSelector("#tutor:not([hidden])");
      const tb = await page.locator("#tutor").boundingBox();
      const vp = await page.evaluate(() => ({ w: window.innerWidth, h: window.innerHeight }));
      check("mobile: tutor opens as a full-width, full-height overlay", tb && Math.abs(tb.x) < 1 && tb.width >= vp.w - 1 &&
        Math.abs(tb.y + tb.height - vp.h) < 2, JSON.stringify({ tb, vp }));
      await page.screenshot({ path: path.join(SHOTS, "qa-mobile-tutor.png") });
      await page.keyboard.press("Escape");
      check("mobile: Escape closes the tutor", await page.isHidden("#tutor"));
      check("mobile: no console errors", page.errors.length === 0, page.errors.slice(0, 3).join(" | "));
      await ctx.close();
    }
  } finally {
    srv.stop();
  }

  // ======================================================================== MOCKED tutor (no live API)
  const mock = await startMock();
  const srv2 = await startServer(8930, { OPENAI_API_KEY: "sk-test-browser-mock", OPENAI_BASE_URL: `http://127.0.0.1:${mock.port}/v1` });
  try {
    const { ctx, page } = await newPage(browser);
    await page.goto(srv2.base + "#s5");
    await waitStep(page, 0);
    await page.click('[data-action="next"]');
    await waitStep(page, 1, 30000);
    await page.click('[data-action="ask"]');
    await page.waitForSelector("#tutor:not([hidden])");
    check("MOCK: tutor shows ready with the default model", /ready · gpt-5-mini/.test(await page.textContent("#tutor-status")));
    await page.fill("#tutor-input", "Why can we factor x?");
    await page.click(".tutor-form button[type=submit]");
    await page.waitForSelector(".msg.assistant", { timeout: 15000 });
    const sent = mock.seen[mock.seen.length - 1];
    check("MOCK: request carried server-built context for step 1 of close-loop", /Current step 1 of 5/.test(sent.instructions) &&
      sent.input[sent.input.length - 1].content === "Why can we factor x?", sent.instructions.slice(-200));
    check("MOCK: reply is attributed to GPT", (await page.textContent(".msg.assistant .who")).trim() === "GPT");
    check("MOCK: assistant math typeset with KaTeX", (await page.$$(".msg.assistant .katex")).length >= 2);
    const injected = await page.evaluate(() => ({ img: document.querySelectorAll(".msg.assistant img").length, pwned: !!window.__pwned,
                                                   text: document.querySelector(".msg.assistant").textContent }));
    check("MOCK: model-supplied HTML shown as text, never rendered", injected.img === 0 && !injected.pwned && /<img/.test(injected.text));
    check("MOCK: bullet lines rendered as a list", (await page.$$(".msg.assistant li")).length === 2);
    await page.fill("#tutor-input", "And the sizes?");
    await page.click(".tutor-form button[type=submit]");
    await page.waitForFunction(() => document.querySelectorAll(".msg.assistant").length === 2, null, { timeout: 15000 });
    const sent2 = mock.seen[mock.seen.length - 1];
    check("MOCK: follow-up sends bounded history (user, assistant, user)", sent2.input.map(m => m.role).join(",") === "user,assistant,user");
    await page.screenshot({ path: path.join(SHOTS, "qa-desk-tutor-mock.png") });
    check("MOCK: no console errors", page.errors.length === 0, page.errors.slice(0, 3).join(" | "));
    await ctx.close();
  } finally {
    srv2.stop();
    mock.srv.close();
    await browser.close();
  }

  fs.mkdirSync(path.join(PROJECT, "qa", "results"), { recursive: true });
  fs.writeFileSync(path.join(PROJECT, "qa", "results", "control_browser_qa.json"), JSON.stringify(results, null, 1));
  const bad = results.filter(r => !r.ok).length;
  console.log(`\n${results.length - bad} passed, ${bad} failed  (tutor replies were MOCKED; no live OpenAI call)`);
  process.exit(bad ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
