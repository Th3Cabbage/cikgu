/*
 * The Phase Plane and Stability study companion (browser only, no framework).
 * Course text: course.json. Animations: animations/manifest.json (pre-rendered ManimGL clips, one
 * per step, with stable stills). Explorer math: control_math.js. Math typesetting: bundled KaTeX.
 * Optional tutor: POST /api/tutor on the local server (server.py), which holds the API key.
 * Everything the page renders from data is inserted as text (KaTeX typesets $...$ math); no raw HTML.
 */
(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var STORE_KEY = "phase-plane-v1";
  var DELIMS = [{ left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false },
                { left: "\\(", right: "\\)", display: false }, { left: "\\[", right: "\\]", display: true }];
  var COURSE_DELIMS = [{ left: "$", right: "$", display: false }];
  var reduceMotion = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };

  var course = null, anim = null, seqById = {}, serverStatus = null;
  var viewEl = null, firstRoute = true, currentRoute = "";
  var storageOk = true, saveTimer = 0;
  var state = {
    theme: "light", steps: {}, reached: {}, quiz: {}, quizIndex: 0, explorer: null,
    sectionSeq: {}, examples: {}, tutorOpen: false
  };

  // ------------------------------------------------------------------ helpers

  function h(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === "text") node.textContent = v;
        else if (k === "className") node.className = v;
        else if (k.slice(0, 2) === "on") node.addEventListener(k.slice(2), v);
        else node.setAttribute(k, v === true ? "" : v);
      });
    }
    (children || []).forEach(function (c) {
      if (c === null || c === undefined) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function s(tag, attrs, children) {
    var node = document.createElementNS(SVG_NS, tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  // Text with $...$ inline math: set as plain text, then KaTeX auto-render typesets the math.
  function mathText(node, text, delims) {
    node.textContent = text || "";
    if (window.renderMathInElement) {
      window.renderMathInElement(node, { delimiters: delims || COURSE_DELIMS, throwOnError: false, trust: false });
    }
    return node;
  }
  function M(tag, text, attrs) { return mathText(h(tag, attrs), text); }

  function displayMath(node, tex) {
    if (window.katex) window.katex.render(tex, node, { displayMode: true, throwOnError: false, trust: false });
    else node.textContent = tex;
    return node;
  }
  function flowMath(node, tex) {
    if (window.katex) window.katex.render("\\displaystyle " + tex, node, { displayMode: false, throwOnError: false, trust: false });
    else node.textContent = tex;
    return node;
  }
  function fitMath(node) {
    node.style.fontSize = "";
    var size = 100;
    while (node.scrollWidth > node.clientWidth + 1 && size > 64) { size -= 6; node.style.fontSize = size + "%"; }
  }
  function announce(msg) {
    var el = document.getElementById("app-status");
    if (!el) return;
    el.textContent = "";
    setTimeout(function () { el.textContent = msg; }, 30);
  }
  function plain(t) { return String(t || "").replace(/\$([^$]*)\$/g, "$1").replace(/\\[a-zA-Z]+/g, "").replace(/[{}]/g, ""); }
  function mmss(sec) { var m = Math.floor(sec / 60), r = sec % 60; return m + ":" + (r < 10 ? "0" : "") + r; }
  /* mit-de multi-video shell */
  function videoOf(n) { for (var i = 0; i < course.videos.length; i++) if (course.videos[i].n === n) return course.videos[i]; return course.videos[0]; }
  function videoUrl(sec, n) { return videoOf(n).url + "&t=" + Math.max(0, Math.floor(sec)) + "s"; }
  function videoTag(v) { return "Video " + v.v + " · " + mmss(v.t); }
  function ext(href, text, label) {
    return h("a", { href: href, target: "_blank", rel: "noopener noreferrer", "aria-label": label || null }, [text]);
  }
  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
  function isNum(v) { return typeof v === "number" && isFinite(v); }

  // ------------------------------------------------------------------ storage (validated)

  function loadStored() {
    var raw = null;
    try { raw = window.localStorage.getItem(STORE_KEY); } catch (e) { storageOk = false; return; }
    if (!raw) return;
    var d;
    try { d = JSON.parse(raw); } catch (e) { return; }
    if (!d || typeof d !== "object" || d.v !== 1) return;
    if (d.theme === "dark" || d.theme === "light") state.theme = d.theme;
    state.tutorOpen = d.tutorOpen === true;
    var obj = function (o) { return o && typeof o === "object" && !Array.isArray(o) ? o : {}; };
    Object.keys(obj(d.steps)).forEach(function (id) {
      var sq = seqById[id], k = d.steps[id];
      if (sq && Number.isInteger(k) && k >= 0 && k <= sq.steps.length) state.steps[id] = k;
    });
    Object.keys(obj(d.reached)).forEach(function (id) {
      var sq = seqById[id], k = d.reached[id];
      if (sq && Number.isInteger(k) && k >= 0 && k <= sq.steps.length) state.reached[id] = k;
    });
    Object.keys(obj(d.sectionSeq)).forEach(function (n) {
      var id = d.sectionSeq[n];
      if (seqById[id] && String(seqById[id].section) === n) state.sectionSeq[n] = id;
    });
    Object.keys(obj(d.examples)).forEach(function (sid) {
      var sec = course.sections.find(function (x) { return x.id === sid; }), k = d.examples[sid];
      if (sec && Number.isInteger(k) && k >= 0 && k <= sec.example.steps.length) state.examples[sid] = k;
    });
    course.quiz.forEach(function (q) {
      var e = obj(d.quiz)[q.id];
      if (!e || typeof e !== "object") return;
      var n = q.choices.length;
      var ok = function (i) { return Number.isInteger(i) && i >= 0 && i < n; };
      var tried = Array.isArray(e.tried) ? e.tried.filter(ok).filter(function (v, i, a) { return a.indexOf(v) === i; }) : [];
      if (!ok(e.first) || tried.indexOf(e.first) !== 0) return;
      var solved = tried.some(function (i) { return q.choices[i].correct; });
      state.quiz[q.id] = { first: e.first, tried: tried, solved: solved };
    });
    if (Number.isInteger(d.quizIndex)) state.quizIndex = clamp(d.quizIndex, 0, course.quiz.length);
    state.explorer = window.StudyExplorer && window.StudyExplorer.restore ? window.StudyExplorer.restore(d.explorer, course.explorer) : null;
  }

  function validRanges(src, cfg, numKeys, boolKeys) {
    if (!src || typeof src !== "object") return null;
    var out = {};
    for (var i = 0; i < numKeys.length; i++) {
      var k = numKeys[i], v = src[k], r = cfg[k];
      if (!isNum(v)) return null;
      out[k] = clamp(v, r.min, r.max);
    }
    boolKeys.forEach(function (k) { out[k] = src[k] === true; });
    return out;
  }

  var savePending = false;
  function saveNow() {
    clearTimeout(saveTimer);
    savePending = false;
    var d = { v: 1, theme: state.theme, tutorOpen: state.tutorOpen, steps: state.steps, reached: state.reached,
              sectionSeq: state.sectionSeq, examples: state.examples, quiz: state.quiz, quizIndex: state.quizIndex,
              explorer: state.explorer };
    try { window.localStorage.setItem(STORE_KEY, JSON.stringify(d)); storageOk = true; }
    catch (e) { storageOk = false; }
    updateProgress();
  }
  // Debounced (sliders fire often); flushed when the page is hidden or unloaded.
  function save() {
    clearTimeout(saveTimer);
    savePending = true;
    saveTimer = setTimeout(saveNow, 120);
  }
  window.addEventListener("pagehide", function () { if (savePending) saveNow(); });
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden" && savePending) saveNow(); });

  // ------------------------------------------------------------------ theme

  function applyTheme(t) {
    state.theme = t;
    document.documentElement.setAttribute("data-theme", t);
    var btn = document.getElementById("theme-toggle");
    btn.setAttribute("aria-pressed", t === "dark" ? "true" : "false");
    btn.querySelector(".theme-label").textContent = t === "dark" ? "Light theme" : "Dark theme";
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", t === "dark" ? "#161c26" : "#f5f6f8");
  }

  // ------------------------------------------------------------------ boot

  function getJSON(url) {
    return fetch(url, { cache: "no-cache", credentials: "same-origin" }).then(function (r) {
      if (!r.ok) throw new Error(url + ": HTTP " + r.status);
      return r.json();
    });
  }

  function boot() {
    viewEl = document.getElementById("view");
    Promise.all([getJSON("course.json"),
                 getJSON("animations/manifest.json").catch(function () { return null; }),
                 getJSON("api/status").catch(function () { return null; })])
      .then(function (res) {
        course = res[0];
        anim = res[1];
        serverStatus = res[2] && res[2].app === "Study_phase_plane" ? res[2] : null;
        if (anim && Array.isArray(anim.sequences)) anim.sequences.forEach(function (sq) { seqById[sq.id] = sq; });
        loadStored();
        applyTheme(state.theme);
        setupChrome();
        buildNav();
        buildStage();
        buildTutor();
        if (state.tutorOpen) setTutorOpen(true, true);
        updateProgress();
        window.addEventListener("hashchange", route);
        route();
        if (!storageOk) announce("This browser blocks local storage, so progress lasts for this visit only.");
      })
      .catch(function (err) {
        viewEl.textContent = "";
        viewEl.appendChild(h("p", { className: "error", text:
          "Could not load the course (" + err.message + "). Start the guide with launch_phase_plane.ps1: browsers block " +
          "data requests from pages opened directly from disk." }));
      });
  }

  function setupChrome() {
    document.getElementById("theme-toggle").addEventListener("click", function () {
      applyTheme(state.theme === "dark" ? "light" : "dark");
      saveNow();
      announce((state.theme === "dark" ? "Dark" : "Light") + " theme on." + (storageOk ? "" : " (Not saved: storage is blocked.)"));
    });
    var toggle = document.querySelector(".nav-toggle");
    var nav = document.getElementById("sidenav");
    var scrim = document.getElementById("scrim");
    toggle.addEventListener("click", function () { setNavOpen(!nav.classList.contains("open")); });
    scrim.addEventListener("click", function () { setNavOpen(false); if (isNarrowTutor()) setTutorOpen(false); });
    document.getElementById("tutor-toggle").addEventListener("click", function () { setTutorOpen(!state.tutorOpen); });
    document.getElementById("reset-progress").addEventListener("click", function () {
      if (!window.confirm("Reset all saved progress (steps, quiz answers, explorer settings)? The theme is kept.")) return;
      var theme = state.theme;
      state.steps = {}; state.reached = {}; state.quiz = {}; state.quizIndex = 0; state.explorer = null; 
      state.sectionSeq = {}; state.examples = {};
      state.theme = theme;
      if (player.seq) { cancelPlayback(); player.seq = null; }
      saveNow();
      route();
      announce("Saved progress reset.");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        if (document.getElementById("sidenav").classList.contains("open")) { setNavOpen(false); toggle.focus(); }
        else if (state.tutorOpen && isNarrowTutor()) { setTutorOpen(false); document.getElementById("tutor-toggle").focus(); }
      }
    });
    document.addEventListener("keydown", stageKeys);
    document.addEventListener("keydown", quizKeys);
  }

  function setNavOpen(open) {
    var nav = document.getElementById("sidenav");
    nav.classList.toggle("open", open);
    document.querySelector(".nav-toggle").setAttribute("aria-expanded", open ? "true" : "false");
    document.getElementById("scrim").hidden = !open;
    if (open) { var a = nav.querySelector("a"); if (a) a.focus(); }
  }

  function buildNav() {
    var list = document.getElementById("section-links");
    course.sections.forEach(function (sec) {
      list.appendChild(h("li", null, [
        h("a", { href: "#" + sec.id, "data-route": sec.id }, [
          h("span", { className: "sec-num", "aria-hidden": "true", text: String(sec.number) }),
          h("span", { className: "sec-name" }, [sec.nav, h("span", { className: "sr-only", text: ", video " + sec.v + ", " + mmss(sec.time[0]) + " to " + mmss(sec.time[1]) })]),
          h("span", { className: "sec-meta" }, [h("span", { className: "sec-check", "data-check": sec.id, "aria-hidden": "true" }),
                                                 h("span", { className: "sec-time", "aria-hidden": "true", text: "V" + sec.v })])
        ])
      ]));
    });
  }

  function sectionSeqs(n) {
    var ids = anim && anim.sections ? (anim.sections[String(n)] || []) : [];
    return ids.filter(function (id) { return seqById[id]; }).map(function (id) { return seqById[id]; });
  }

  function updateProgress() {
    if (!course) return;
    var total = 0, reached = 0;
    Object.keys(seqById).forEach(function (id) { total += seqById[id].steps.length; reached += state.reached[id] || 0; });
    var answered = 0, firstOk = 0;
    course.quiz.forEach(function (q) {
      var e = state.quiz[q.id];
      if (e) { answered++; if (q.choices[e.first].correct) firstOk++; }
    });
    var el = document.getElementById("progress-summary");
    if (el) el.textContent = reached + " of " + total + " animation steps seen · quiz " + firstOk + "/" + course.quiz.length +
      " first try" + (storageOk ? "" : " · not saved (storage blocked)");
    course.sections.forEach(function (sec) {
      var seqs = sectionSeqs(sec.number);
      var done = seqs.length > 0 && seqs.every(function (sq) { return (state.reached[sq.id] || 0) >= sq.steps.length; });
      var c = document.querySelector('[data-check="' + sec.id + '"]');
      if (c) c.textContent = done ? "✓" : "";
      var a = c && c.closest("a");
      if (a) {
        var sr = a.querySelector(".sr-done");
        if (done && !sr) a.appendChild(h("span", { className: "sr-only sr-done", text: " (animations completed)" }));
        if (!done && sr) sr.remove();
      }
    });
  }

  // ------------------------------------------------------------------ routing

  function parseHash() {
    var parts = (location.hash || "").replace(/^#/, "").split("/");
    return { base: parts[0] || "s1", sub: parts[1] || null };
  }

  function route() {
    var r = parseHash();
    settlePlayback();
    stopTimers();
    player.onSelect = null;
    if (player.wrap && player.wrap.parentNode) player.wrap.parentNode.removeChild(player.wrap);
    exitFullscreen();
    viewEl.textContent = "";
    var title, active = r.base, m = /^s(\d+)$/.exec(r.base);
    if (m && course.sections[+m[1] - 1]) title = renderSection(+m[1], r.sub);
    else if (r.base === "explorer") title = renderExplorer();
    else if (r.base === "quiz") title = renderQuiz();
    else if (r.base === "sources") title = renderSources();
    else { active = "s1"; title = renderSection(1, null); }
    currentRoute = active;
    document.title = plain(title) + " · The Phase Plane and Stability companion";
    document.querySelectorAll(".sidenav a").forEach(function (a) {
      if (a.getAttribute("data-route") === active) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    setNavOpen(false);
    updateTutorContext();
    if (!firstRoute) {
      window.scrollTo(0, 0);
      var h1 = viewEl.querySelector("h1");
      if (h1) { h1.setAttribute("tabindex", "-1"); h1.focus({ preventScroll: true }); }
    }
    firstRoute = false;
  }

  function replaceHash(hash) {
    if (location.hash === hash) return;
    if (window.history && history.replaceState) history.replaceState(null, "", hash);
    else location.hash = hash;
  }

  // ------------------------------------------------------------------ the animation stage

  var player = {
    wrap: null, seq: null, k: 0, playing: false, target: 0, token: 0, started: false,
    watchdog: 0, loadingTimer: 0, notice: "", stillWanted: null, activeSrc: null, onSelect: null
  };

  function frameFor(sq, k) { return k === 0 ? sq.initial.frame : sq.steps[k - 1].finalFrame; }

  function buildStage() {
    var P = player;
    P.still = h("img", { className: "stage-still", alt: "", decoding: "async" });
    P.video = h("video", { className: "stage-video", muted: true, playsinline: true, preload: "auto",
                           "aria-hidden": "true", tabindex: "-1", disablepictureinpicture: true });
    P.video.muted = true;
    P.fallback = h("div", { className: "stage-fallback", hidden: true });
    P.loading = h("div", { className: "stage-loading", hidden: true, "aria-hidden": "true" },
                  [h("span", { className: "spinner" }), "Loading animation…"]);
    P.fsBtn = h("button", { type: "button", className: "stage-fs", "aria-label": "Full screen", title: "Full screen" },
                [h("span", { "aria-hidden": "true", text: "⛶" })]);
    P.stage = h("div", { className: "stage", "data-state": "idle", role: "img" }, [P.still, P.video, P.fallback, P.loading, P.fsBtn]);
    P.progress = h("ol", { className: "stage-progress", "aria-hidden": "true" });
    P.backBtn = h("button", { type: "button", className: "btn", "data-action": "back", "aria-label": "Back one step" },
                  [h("span", { "aria-hidden": "true", text: "◀" }), "Back"]);
    P.replayBtn = h("button", { type: "button", className: "btn", "data-action": "replay", "aria-label": "Replay this step's animation" },
                    [h("span", { "aria-hidden": "true", text: "↻" }), "Replay"]);
    P.nextBtn = h("button", { type: "button", className: "btn primary", "data-action": "next" });
    P.restartBtn = h("button", { type: "button", className: "btn", "data-action": "restart", "aria-label": "Restart this animation" },
                     [h("span", { "aria-hidden": "true", text: "⏮" }), "Restart"]);
    P.controls = h("div", { className: "stage-controls", role: "group", "aria-label": "Animation controls" },
                   [P.backBtn, P.replayBtn, P.nextBtn, P.restartBtn]);
    P.keyHint = h("p", { className: "key-hint", text: "Keys: → or N next step · ← or B back · R replay · F full screen." });
    P.col = h("div", { className: "stage-col" }, [P.stage, P.progress, P.controls, P.keyHint]);

    P.count = h("p", { className: "step-count" });
    P.badge = h("span", { className: "relation-badge" });
    P.stepTitle = h("h2", { className: "step-title", id: "step-title" });
    P.eq = h("div", { className: "step-eq" });
    P.expl = h("p", { className: "step-expl" });
    P.noticeEl = h("p", { className: "stage-notice", role: "note", hidden: true });
    P.askBtn = h("button", { type: "button", className: "btn small", "data-action": "ask" },
                 [h("span", { "aria-hidden": "true", text: "✦" }), "Ask GPT about this step"]);
    P.completeNext = h("button", { type: "button", className: "btn primary", "data-action": "next-seq" });
    P.completeRestart = h("button", { type: "button", className: "btn", "data-action": "restart-complete", text: "Watch again" });
    P.complete = h("div", { className: "complete-box", hidden: true }, [
      h("p", { className: "complete-title" }, [h("span", { "aria-hidden": "true", text: "✓ " }), "Animation complete"]),
      h("div", { className: "complete-actions" }, [P.completeNext, P.completeRestart])
    ]);
    P.transcriptList = h("ol", { className: "transcript-list" });
    P.transcript = h("details", { className: "transcript" }, [h("summary", { text: "All steps so far (text version)" }), P.transcriptList]);
    P.card = h("section", { className: "step-card", "aria-labelledby": "step-title" },
               [P.count, P.badge, P.stepTitle, P.eq, P.expl, P.noticeEl, h("div", { className: "card-actions" }, [P.askBtn]),
                P.complete, P.transcript]);
    P.status = h("p", { className: "sr-only", role: "status", "aria-live": "polite" });
    P.wrap = h("section", { className: "stage-wrap", "aria-label": "Animated steps" },
               [h("div", { className: "stage-grid" }, [P.col, P.card]), P.status]);

    P.nextBtn.addEventListener("click", onNext);
    P.backBtn.addEventListener("click", onBack);
    P.replayBtn.addEventListener("click", onReplay);
    P.restartBtn.addEventListener("click", function () { goTo(0, "Back to the start."); });
    P.completeRestart.addEventListener("click", function () { goTo(0, "Back to the start."); P.nextBtn.focus(); });
    P.completeNext.addEventListener("click", goNextSequence);
    P.askBtn.addEventListener("click", function () { setTutorOpen(true); focusTutorInput(); });
    P.fsBtn.addEventListener("click", toggleFullscreen);
    document.addEventListener("fullscreenchange", syncFullscreen);

    P.video.addEventListener("playing", function () {
      if (!P.playing) return;
      P.started = true;
      clearTimeout(P.loadingTimer);
      P.loading.hidden = true;
      P.stage.classList.add("video-on");
      P.stage.setAttribute("data-state", "playing");
      armWatchdog();
    });
    P.video.addEventListener("waiting", function () {
      if (P.playing) { clearTimeout(P.loadingTimer); P.loadingTimer = setTimeout(showLoading, 250); }
    });
    P.video.addEventListener("ended", function () {
      if (P.playing && P.video.getAttribute("src") === P.activeSrc) finishTransition(P.token);
    });
    P.video.addEventListener("error", function () {
      if (P.playing && P.video.getAttribute("src") === P.activeSrc) failTransition(P.token);
    });
    P.still.addEventListener("error", function () { showFallback(true); });
    P.still.addEventListener("load", function () { showFallback(false); });
    if (reduceMotion.addEventListener) reduceMotion.addEventListener("change", function () { renderPanel(); });
  }

  function mountStage(container, id) {
    var P = player;
    container.appendChild(P.wrap);
    if (!anim || !seqById[id]) {
      P.wrap.classList.add("unavailable");
      container.appendChild(h("p", { className: "stage-notice warn", text:
        "The animations could not be loaded. The notes and worked example below cover the same material." }));
      return;
    }
    P.wrap.classList.remove("unavailable");
    selectSequence(id, true);
  }

  function selectSequence(id, quiet) {
    var P = player, sq = seqById[id];
    if (!sq) return;
    if (P.seq !== sq) {
      cancelPlayback();
      P.seq = sq;
      P.notice = "";
      P.k = Math.min(state.steps[id] || 0, sq.steps.length);
      P.transcript.open = false;
    }
    P.progress.textContent = "";
    sq.steps.forEach(function () { P.progress.appendChild(h("li")); });
    P.stage.setAttribute("aria-label", "Animation: " + plain(sq.title));
    showState(P.k);
    preload();
    if (!quiet) announce("Showing " + plain(sq.title) + ", step " + P.k + " of " + sq.steps.length + ".");
  }

  function setStill(src) {
    var P = player;
    P.stillWanted = src;
    if (P.still.getAttribute("src") === src && P.still.complete && P.still.naturalWidth) return Promise.resolve();
    var img = new Image();
    img.src = src;
    var ready = img.decode ? img.decode() : new Promise(function (res, rej) { img.onload = res; img.onerror = rej; });
    return ready.then(function () { if (P.stillWanted === src) P.still.setAttribute("src", src); },
                      function () { if (P.stillWanted === src) P.still.setAttribute("src", src); });
  }

  function showFallback(on) {
    var P = player;
    if (!on) { P.fallback.hidden = true; return; }
    if (!P.seq) return;
    var k = P.playing ? P.target : P.k;
    var tex = k === 0 ? P.seq.initial.tex : P.seq.steps[k - 1].tex;
    P.fallback.textContent = "";
    var box = displayMath(h("div", { className: "fallback-eq" }), tex);
    P.fallback.appendChild(box);
    P.fallback.appendChild(h("p", { text: "The picture for this step could not be loaded; its formula is shown instead." }));
    P.fallback.hidden = false;
  }

  function showState(k) {
    var P = player;
    P.k = k;
    state.steps[P.seq.id] = k;
    if (k > (state.reached[P.seq.id] || 0)) state.reached[P.seq.id] = k;
    save();
    var tok = P.token;
    P.stage.setAttribute("data-state", k === P.seq.steps.length ? "complete" : "idle");
    renderPanel();
    return setStill(frameFor(P.seq, k)).then(function () {
      if (!P.playing && P.token === tok) P.stage.classList.remove("video-on");
    });
  }

  function hideVideoNow() {
    player.stage.classList.remove("video-on");
    if (!player.video.paused) player.video.pause();
  }

  function preload() {
    var P = player;
    if (!P.seq || P.playing || P.stage.classList.contains("video-on")) return;
    if (P.k < P.seq.steps.length) {
      var st = P.seq.steps[P.k];
      if (P.video.getAttribute("src") !== st.transition.src) { P.video.setAttribute("src", st.transition.src); P.video.load(); }
      var img = new Image();
      img.src = st.finalFrame;
    }
  }

  function showLoading() {
    var P = player;
    if (P.playing && !P.started) { P.loading.hidden = false; P.stage.setAttribute("data-state", "loading"); }
  }

  function armWatchdog() {
    var P = player;
    clearTimeout(P.watchdog);
    var tok = P.token, dur = P.seq.steps[P.target - 1].transition.duration;
    P.watchdog = setTimeout(function () { if (P.playing && P.token === tok) finishTransition(tok); }, dur * 1000 + 4000);
  }

  function playTransition(k) {
    var P = player, st = P.seq.steps[k - 1], tok = ++P.token;
    clearTimeout(P.watchdog);
    clearTimeout(P.loadingTimer);
    P.playing = true;
    P.started = false;
    P.target = k;
    P.notice = "";
    P.activeSrc = st.transition.src;
    P.stage.classList.remove("video-on");
    setStill(frameFor(P.seq, k - 1));
    P.k = k - 1;
    renderPanel();
    if (P.video.getAttribute("src") !== st.transition.src) { P.video.setAttribute("src", st.transition.src); P.video.load(); }
    else { try { P.video.currentTime = 0; } catch (e) { /* not seekable yet */ } }
    P.loadingTimer = setTimeout(showLoading, 250);
    P.watchdog = setTimeout(function () { if (P.playing && P.token === tok && !P.started) failTransition(tok); }, 12000);
    var pr = P.video.play();
    if (pr && pr.catch) pr.catch(function () { if (P.playing && P.token === tok) failTransition(tok); });
    P.status.textContent = "Playing step " + k + " of " + P.seq.steps.length + ": " + plain(st.title) + ".";
  }

  function finishTransition(tok) {
    var P = player;
    if (!P.playing || tok !== P.token) return;
    clearTimeout(P.watchdog);
    clearTimeout(P.loadingTimer);
    P.playing = false;
    P.loading.hidden = true;
    var k = P.target;
    showState(k).then(function () { if (!P.playing && P.k === k) preload(); });
    P.status.textContent = "Step " + k + " of " + P.seq.steps.length + ": " + plain(P.seq.steps[k - 1].title) + "." +
      (k === P.seq.steps.length ? " Animation complete." : "");
  }

  function failTransition(tok) {
    var P = player;
    if (!P.playing || tok !== P.token) return;
    clearTimeout(P.watchdog);
    clearTimeout(P.loadingTimer);
    P.playing = false;
    P.loading.hidden = true;
    hideVideoNow();
    var k = P.target;
    P.notice = "The animation for this step could not be played, so its result is shown instead. The formula and explanation are complete without it.";
    showState(k);
    P.status.textContent = "Animation unavailable. Showing step " + k + " of " + P.seq.steps.length + ".";
    P.video.removeAttribute("src");
    P.video.load();
  }

  function cancelPlayback() {
    var P = player;
    P.token++;
    clearTimeout(P.watchdog);
    clearTimeout(P.loadingTimer);
    P.playing = false;
    if (P.loading) P.loading.hidden = true;
    if (P.video) hideVideoNow();
  }

  function settlePlayback() {
    var P = player;
    if (!P.seq || !P.playing) return;
    var k = P.target;
    cancelPlayback();
    showState(k);
  }

  function goTo(k, msg) {
    var P = player;
    if (!P.seq) return;
    cancelPlayback();
    P.notice = "";
    showState(clamp(k, 0, P.seq.steps.length));
    preload();
    P.status.textContent = (msg ? msg + " " : "") + "Step " + P.k + " of " + P.seq.steps.length + ".";
  }

  function onNext() {
    var P = player;
    if (!P.seq || P.playing) return;
    if (P.k >= P.seq.steps.length) { goNextSequence(); return; }
    if (reduceMotion.matches) {
      showState(P.k + 1);
      preload();
      P.status.textContent = "Step " + P.k + " of " + P.seq.steps.length + ": " + plain(P.seq.steps[P.k - 1].title) +
        ". Showing the result; press Replay to watch the transition.";
      return;
    }
    playTransition(P.k + 1);
  }

  function onBack() {
    var P = player;
    if (!P.seq) return;
    if (P.playing) { goTo(P.target - 1, "Stopped."); return; }
    if (P.k > 0) goTo(P.k - 1, "Back one step.");
  }

  function onReplay() {
    var P = player;
    if (!P.seq) return;
    var k = P.playing ? P.target : P.k;
    if (k < 1) return;
    cancelPlayback();
    playTransition(k);
  }

  function nextSequenceOf(sq) {
    var list = anim ? anim.sequences : [];
    var i = list.indexOf(sq);
    return i >= 0 && i < list.length - 1 ? list[i + 1] : null;
  }

  function goNextSequence() {
    var P = player, nx = nextSequenceOf(P.seq);
    if (!nx) { location.hash = "#explorer"; return; }
    if (nx.section !== P.seq.section) { location.hash = "#s" + nx.section; return; }
    state.sectionSeq[nx.section] = nx.id;
    state.steps[nx.id] = 0;
    location.hash = "#s" + nx.section + "/" + nx.id;
  }

  function renderPanel() {
    var P = player, sq = P.seq;
    if (!sq) return;
    var n = sq.steps.length, k = P.playing ? P.target : P.k, item = k === 0 ? null : sq.steps[k - 1];
    P.count.textContent = k === 0 ? "Start · " + n + " steps" : "Step " + k + " of " + n;
    P.badge.hidden = !item;
    if (item) { P.badge.textContent = item.relationLabel; P.badge.setAttribute("data-relation", item.relation); }
    mathText(P.stepTitle, item ? item.title : sq.initial.title);
    flowMath(P.eq, item ? item.tex : sq.initial.tex);
    mathText(P.expl, item ? item.explanation : sq.initial.explanation + (reduceMotion.matches ? "" : " Press Next step to begin."));
    var notice = P.notice;
    if (!notice && reduceMotion.matches && k > 0 && !P.playing) {
      notice = "Reduced motion is on, so steps jump straight to their result. Press Replay to watch a transition.";
    }
    P.noticeEl.textContent = notice;
    P.noticeEl.hidden = !notice;
    P.noticeEl.className = "stage-notice" + (P.notice ? " warn" : "");
    var done = !P.playing && P.k === n, nx = nextSequenceOf(sq);
    P.complete.hidden = !done;
    var nextLabel = nx ? (nx.section === sq.section ? "Next animation: " + plain(nx.title)
                                                    : "Next section: " + plain(course.sections[nx.section - 1].title))
                       : "Try the explorer";
    P.completeNext.textContent = nextLabel + " →";
    P.nextBtn.textContent = "";
    if (done) { P.nextBtn.appendChild(document.createTextNode(nx ? "Continue " : "Explorer ")); P.nextBtn.setAttribute("aria-label", nextLabel); }
    else { P.nextBtn.appendChild(document.createTextNode("Next step ")); P.nextBtn.setAttribute("aria-label", P.playing ? "Next step (playing)" : "Next step"); }
    P.nextBtn.appendChild(h("span", { "aria-hidden": "true", text: "▶" }));
    P.nextBtn.setAttribute("aria-disabled", P.playing ? "true" : "false");
    P.backBtn.disabled = !P.playing && P.k === 0;
    P.replayBtn.disabled = k === 0;
    P.restartBtn.disabled = !P.playing && P.k === 0;
    Array.prototype.forEach.call(P.progress.children, function (li, i) {
      li.className = i < P.k ? "done" : (P.playing && i === P.target - 1 ? "active" : "");
    });
    P.wrap.setAttribute("data-seq", sq.id);
    P.wrap.setAttribute("data-step", String(P.k));
    P.wrap.setAttribute("data-playing", P.playing ? "true" : "false");
    P.transcriptList.textContent = "";
    P.transcriptList.appendChild(transcriptItem("Start: " + sq.initial.title, sq.initial.tex, sq.initial.explanation));
    for (var i = 0; i < P.k; i++) {
      var st = sq.steps[i];
      P.transcriptList.appendChild(transcriptItem(st.title + " (" + st.relationLabel + ")", st.tex, st.explanation));
    }
    requestAnimationFrame(function () { fitMath(P.eq); });
    updateTutorContext();
  }

  function transcriptItem(title, tex, expl) {
    return h("li", null, [M("p", title, { className: "t-title" }), flowMath(h("div", { className: "t-eq" }), tex), M("p", expl)]);
  }

  function stageAttached() { return player.wrap && document.body.contains(player.wrap) && player.seq; }

  function typingTarget(e) {
    var t = e.target || {}, tag = (t.tagName || "").toUpperCase();
    return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || t.isContentEditable;
  }

  function stageKeys(e) {
    if (!stageAttached() || e.altKey || e.ctrlKey || e.metaKey || e.defaultPrevented || typingTarget(e)) return;
    var key = e.key;
    if (key === "ArrowRight" || key === "n" || key === "N") { e.preventDefault(); onNext(); }
    else if (key === "ArrowLeft" || key === "b" || key === "B") { e.preventDefault(); onBack(); }
    else if (key === "r" || key === "R") { e.preventDefault(); onReplay(); }
    else if (key === "f" || key === "F") { e.preventDefault(); toggleFullscreen(); }
  }

  function toggleFullscreen() {
    if (document.fullscreenElement) { exitFullscreen(); return; }
    if (player.col && player.col.requestFullscreen) player.col.requestFullscreen().catch(function () { /* not allowed */ });
  }
  function exitFullscreen() { if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {}); }
  function syncFullscreen() {
    var on = document.fullscreenElement === player.col;
    player.fsBtn.setAttribute("aria-label", on ? "Exit full screen" : "Full screen");
    player.fsBtn.title = on ? "Exit full screen" : "Full screen";
  }

  // ------------------------------------------------------------------ section pages

  function renderSection(n, seqId) {
    var sec = course.sections[n - 1];
    var seqs = sectionSeqs(n);
    var id = seqById[seqId] && seqById[seqId].section === n ? seqId
           : (state.sectionSeq[n] && seqById[state.sectionSeq[n]] ? state.sectionSeq[n] : (seqs[0] ? seqs[0].id : null));
    if (id) state.sectionSeq[n] = id;

    viewEl.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Section " + n + " of " + course.sections.length + " · video " + sec.v + ", " +
               mmss(sec.time[0]) + "–" + mmss(sec.time[1]) }),
      M("h1", sec.title),
      M("p", sec.summary, { className: "lede" }),
      h("p", { className: "watch-link" }, [ext(videoUrl(sec.time[0], sec.v), "Watch video " + sec.v + ": " + videoOf(sec.v).title + " ↗",
                                               "Watch video " + sec.v + " on YouTube, from " + mmss(sec.time[0]) + " (opens a new tab)")])
    ]));

    if (seqs.length > 1) {
      var sw = h("div", { className: "seq-switch", role: "group", "aria-label": "Animations in this section" });
      seqs.forEach(function (sq) {
        var b = h("button", { type: "button", className: "seq-btn", "aria-pressed": sq.id === id ? "true" : "false", "data-seq": sq.id });
        mathText(b, sq.title);
        b.addEventListener("click", function () {
          if (player.seq && player.seq.id === sq.id) return;
          state.sectionSeq[n] = sq.id;
          save();
          selectSequence(sq.id, false);
          sw.querySelectorAll(".seq-btn").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
          replaceHash("#s" + n + "/" + sq.id);
        });
        sw.appendChild(b);
      });
      viewEl.appendChild(sw);
    }
    var holder = h("div");
    viewEl.appendChild(holder);
    mountStage(holder, id);

    // Notes and side panels
    var notes = h("article", { className: "notes", "aria-labelledby": "notes-h" }, [h("h2", { id: "notes-h", text: "Lesson notes" })]);
    sec.notes.forEach(function (blk) {
      notes.appendChild(M("h3", blk.heading));
      blk.paragraphs.forEach(function (p) { notes.appendChild(M("p", p)); });
    });
    notes.appendChild(renderExample(sec));
    var side = h("div", { className: "side" }, [
      panel("What you should be able to do", h("ul", null, sec.goals.map(function (g) { return M("li", g); }))),
      panel("Key ideas", h("ul", null, sec.keyIdeas.map(function (g) { return M("li", g); }))),
      panel("Sources for this section", renderSectionSources(sec))
    ]);
    viewEl.appendChild(h("div", { className: "lesson-grid" }, [notes, side]));

    var prev = n > 1 ? course.sections[n - 2] : null, next = n < course.sections.length ? course.sections[n] : null;
    viewEl.appendChild(h("nav", { className: "pager", "aria-label": "Section navigation" }, [
      prev ? h("a", { href: "#" + prev.id }, ["← " + prev.number + ". " + prev.nav]) : h("span"),
      next ? h("a", { href: "#" + next.id }, [next.number + ". " + next.nav + " →"]) : h("a", { href: "#explorer" }, ["Explorer →"])
    ]));
    save();
    return sec.title;
  }

  function panel(title, body) { return h("section", { className: "panel" }, [h("h2", { text: title }), body]); }

  function renderExample(sec) {
    var ex = sec.example, shown = state.examples[sec.id] || 0;
    var box = h("section", { className: "example", "aria-labelledby": "ex-h" });
    box.appendChild(h("h2", { id: "ex-h", text: "Worked example: " + ex.title }));
    box.appendChild(M("p", ex.problem));
    var list = h("ol");
    var answer = h("div", { className: "ex-answer", hidden: true }, [M("p", "Answer: " + ex.answer)]);
    var nextBtn = h("button", { type: "button", className: "btn small reveal-btn" });
    var allBtn = h("button", { type: "button", className: "btn small reveal-btn", text: "Show the whole solution" });
    var resetBtn = h("button", { type: "button", className: "link-btn", text: "Hide the solution" });
    function draw() {
      list.textContent = "";
      for (var i = 0; i < shown; i++) {
        var st = ex.steps[i];
        var li = h("li", null, [M("p", st.text)]);
        if (st.tex) li.appendChild(flowMath(h("div", { className: "ex-eq" }), st.tex));
        list.appendChild(li);
      }
      var all = shown >= ex.steps.length;
      answer.hidden = !all;
      nextBtn.hidden = all;
      allBtn.hidden = all;
      resetBtn.hidden = shown === 0;
      nextBtn.textContent = shown === 0 ? "Show the first step" : "Show step " + (shown + 1) + " of " + ex.steps.length;
    }
    nextBtn.addEventListener("click", function () {
      shown = Math.min(ex.steps.length, shown + 1); state.examples[sec.id] = shown; save(); draw();
      var last = list.lastElementChild;
      if (last) { last.setAttribute("tabindex", "-1"); last.focus(); }
    });
    allBtn.addEventListener("click", function () { shown = ex.steps.length; state.examples[sec.id] = shown; save(); draw(); });
    resetBtn.addEventListener("click", function () { shown = 0; state.examples[sec.id] = 0; save(); draw(); nextBtn.focus(); });
    box.appendChild(list);
    box.appendChild(answer);
    box.appendChild(h("div", { className: "card-actions" }, [nextBtn, allBtn, resetBtn]));
    draw();
    return box;
  }

  function bookLinks(b) {
    var parts = [h("span", { className: "page-ref", text: "printed p. " + b.printed + " · PDF p. " + b.pdf + " " })];
    if (serverStatus && serverStatus.book && serverStatus.book.available) {
      parts.push(ext("book#page=" + b.pdf, "local PDF ↗", "Open printed page " + b.printed + " in the local PDF (new tab)"));
      parts.push(" · ");
    }
    if (course.book.onlineUrl) parts.push(ext(course.book.onlineUrl + "#page=" + b.pdf, "online copy ↗", "Open the online copy of the book at PDF page " + b.pdf + " (new tab)"));
    else if (parts.length > 1) parts.pop();
    return parts;
  }

  function renderSectionSources(sec) {
    var wrap = h("div");
    wrap.appendChild(h("h3", { className: "small-note", text: "Lecture" }));
    wrap.appendChild(h("ul", { className: "sources-list" }, sec.sources.video.map(function (v) {
      return h("li", null, [ext(videoUrl(v.t, v.v), videoTag(v), videoOf(v.v).title + " at " + mmss(v.t) + ": " + v.label + " (YouTube, new tab)"), " ", v.label]);
    })));
    wrap.appendChild(h("h3", { className: "small-note", text: "Book (" + course.book.short + ")" }));
    wrap.appendChild(h("ul", { className: "sources-list" }, sec.sources.book.map(function (b) {
      return h("li", null, [h("span", { text: b.label }), h("br"), h("span", null, bookLinks(b))]);
    })));
    return wrap;
  }

  // Explorer-specific teaching logic lives in explorer.js; the player and tutor are reused.
  function stopTimers() { if (window.StudyExplorer && window.StudyExplorer.stop) window.StudyExplorer.stop(); }
  function renderExplorer() {
    return window.StudyExplorer.render({root:viewEl,course:course,state:state,save:save,html:h,svg:s,
      mathText:mathText,displayMath:displayMath,flowMath:flowMath,announce:announce,panel:panel});
  }

  // ------------------------------------------------------------------ quiz

  var quizUI = null;

  function quizScore() {
    var answered = 0, ok = 0, solved = 0;
    course.quiz.forEach(function (q) {
      var e = state.quiz[q.id];
      if (!e) return;
      answered++;
      if (q.choices[e.first].correct) ok++;
      if (e.solved) solved++;
    });
    return { answered: answered, ok: ok, solved: solved, total: course.quiz.length };
  }

  function renderQuiz() {
    viewEl.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Practice" }), h("h1", { text: "Quiz" }),
      h("p", { className: "lede", text: "Ten questions. Every choice explains itself. Your score counts first tries only; after a wrong answer you can try again." })
    ]));
    var score = h("p", { className: "quiz-score", id: "quiz-score", "aria-live": "polite" });
    var resetBtn = h("button", { type: "button", className: "btn small", "data-action": "reset-quiz", text: "Reset quiz" });
    var dots = h("ol", { className: "quiz-dots", "aria-label": "Questions" });
    var body = h("div", { id: "quiz-body" });
    var wrap = h("div", { className: "quiz" }, [h("div", { className: "quiz-top" }, [score, resetBtn]), dots, body]);
    viewEl.appendChild(wrap);
    quizUI = { score: score, dots: dots, body: body };
    resetBtn.addEventListener("click", function () {
      state.quiz = {}; state.quizIndex = 0; save(); drawQuiz(); announce("Quiz reset."); focusQuestion();
    });
    drawQuiz();
    return "Quiz";
  }

  function drawQuiz() {
    var U = quizUI, sc = quizScore();
    U.score.textContent = "First-try score: " + sc.ok + " of " + sc.total + " · answered " + sc.answered + " of " + sc.total;
    U.dots.textContent = "";
    course.quiz.forEach(function (q, i) {
      var e = state.quiz[q.id];
      var cls = e ? (q.choices[e.first].correct ? "first-ok" : "first-bad") : "";
      var label = "Question " + (i + 1) + (e ? (q.choices[e.first].correct ? ", right first time" : ", wrong first time" + (e.solved ? ", then solved" : "")) : ", not answered");
      U.dots.appendChild(h("li", null, [h("button", { type: "button", className: cls, "aria-label": label,
        "aria-current": i === state.quizIndex ? "step" : null, text: String(i + 1),
        onclick: function () { state.quizIndex = i; save(); drawQuiz(); focusQuestion(); } })]));
    });
    U.dots.appendChild(h("li", null, [h("button", { type: "button", "aria-label": "Summary", "aria-current": state.quizIndex === course.quiz.length ? "step" : null,
      text: "Σ", onclick: function () { state.quizIndex = course.quiz.length; save(); drawQuiz(); focusQuestion(); } })]));
    U.body.textContent = "";
    if (state.quizIndex >= course.quiz.length) { U.body.appendChild(quizSummary(sc)); return; }
    var i = state.quizIndex, q = course.quiz[i], e = state.quiz[q.id];
    var card = h("section", { className: "q-card", "aria-labelledby": "q-text", "data-qid": q.id });
    card.appendChild(h("p", { className: "small-note", text: "Question " + (i + 1) + " of " + course.quiz.length }));
    card.appendChild(M("p", q.question, { className: "q-text", id: "q-text" }));
    var list = h("ul", { className: "choices" });
    q.choices.forEach(function (c, j) {
      var tried = e && e.tried.indexOf(j) >= 0;
      var cls = "choice" + (tried ? (c.correct ? " correct" : " wrong") : "");
      var mark = tried ? (c.correct ? " (correct)" : " (incorrect)") : "";
      var b = h("button", { type: "button", className: cls, "data-choice": String(j), disabled: (e && e.solved) || tried ? true : null },
                [h("span", { className: "key", "aria-hidden": "true", text: String(j + 1) }), M("span", c.text), h("span", { className: "sr-only", text: mark })]);
      b.addEventListener("click", function () { answer(q, j); });
      list.appendChild(h("li", null, [b]));
    });
    card.appendChild(list);
    if (e) {
      var last = e.tried[e.tried.length - 1], c = q.choices[last];
      var fb = h("div", { className: "feedback " + (c.correct ? "ok" : "bad"), role: "status" },
                 [h("strong", { text: c.correct ? (e.first === last ? "Correct. " : "Correct now. ") : "Not quite. " }), M("span", c.why)]);
      card.appendChild(fb);
      if (!e.solved) card.appendChild(h("p", { className: "small-note", text: "Try another choice." }));
    }
    var nav = h("div", { className: "q-nav" }, [
      h("button", { type: "button", className: "btn", disabled: i === 0 ? true : null, text: "◀ Previous",
                    onclick: function () { state.quizIndex = i - 1; save(); drawQuiz(); focusQuestion(); } }),
      h("button", { type: "button", className: "btn primary", "data-action": "next-question",
                    text: i === course.quiz.length - 1 ? "See summary ▶" : "Next question ▶",
                    onclick: function () { state.quizIndex = i + 1; save(); drawQuiz(); focusQuestion(); } })
    ]);
    card.appendChild(nav);
    card.appendChild(h("p", { className: "key-hint", text: "Keys: 1–4 choose an answer." }));
    U.body.appendChild(card);
  }

  function focusQuestion() {
    var el = document.getElementById("q-text") || document.querySelector(".quiz-summary h2");
    if (el) { el.setAttribute("tabindex", "-1"); el.focus(); }
  }

  function answer(q, j) {
    var e = state.quiz[q.id];
    if (e && (e.solved || e.tried.indexOf(j) >= 0)) return;
    if (!e) e = state.quiz[q.id] = { first: j, tried: [], solved: false };
    e.tried.push(j);
    if (q.choices[j].correct) e.solved = true;
    saveNow();
    drawQuiz();
    var fb = quizUI.body.querySelector(".feedback");
    if (fb) announce(fb.textContent);
    var next = quizUI.body.querySelector(e.solved ? '[data-action="next-question"]' : ".choice:not([disabled])");
    if (next) next.focus();
  }

  function quizSummary(sc) {
    var box = h("section", { className: "quiz-summary", "aria-labelledby": "qs-h" }, [
      h("h2", { id: "qs-h", text: "Summary" }),
      h("p", { text: "First-try score: " + sc.ok + " of " + sc.total + ". Answered " + sc.answered + ", solved " + sc.solved + "." })
    ]);
    var missed = course.quiz.filter(function (q) { var e = state.quiz[q.id]; return !e || !q.choices[e.first].correct; });
    if (missed.length) {
      box.appendChild(h("p", { text: "Worth another look:" }));
      box.appendChild(h("ul", null, missed.map(function (q) {
        var i = course.quiz.indexOf(q);
        return h("li", null, [h("button", { type: "button", className: "link-btn", onclick: function () { state.quizIndex = i; save(); drawQuiz(); focusQuestion(); } },
                                 ["Question " + (i + 1) + (state.quiz[q.id] ? "" : " (not answered)")])]);
      })));
    } else box.appendChild(h("p", { text: "Every question right on the first try." }));
    return box;
  }

  function quizKeys(e) {
    if (currentRoute !== "quiz" || !quizUI || e.altKey || e.ctrlKey || e.metaKey || typingTarget(e)) return;
    var n = parseInt(e.key, 10);
    if (n >= 1 && n <= 9) {
      var b = quizUI.body.querySelector('.choice[data-choice="' + (n - 1) + '"]');
      if (b && !b.disabled) { e.preventDefault(); b.click(); }
    }
  }

  // ------------------------------------------------------------------ sources page

  function renderSources() {
    viewEl.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Reference" }), h("h1", { text: "Sources & credits" }),
      h("p", { className: "lede", text: course.attribution })
    ]));
    viewEl.appendChild(panel("Lecture", h("div", null, [
      h("ul", { className: "sources-list" }, course.videos.map(function (v) {
        return h("li", null, [ext(v.url, "Video " + v.n + ": " + v.title + " ↗"), " · " + v.duration]);
      })),
      h("table", { className: "src-table" }, [h("thead", null, [h("tr", null, [h("th", { text: "Section" }), h("th", { text: "Video · time" }), h("th", { text: "Moment" })])]),
        h("tbody", null, [].concat.apply([], course.sections.map(function (sec) {
          return sec.sources.video.map(function (v, i) {
            return h("tr", null, [h("td", { text: i === 0 ? sec.number + ". " + sec.nav : "" }),
                                   h("td", null, [ext(videoUrl(v.t, v.v), videoTag(v), videoOf(v.v).title + " at " + mmss(v.t) + " (YouTube, new tab)")]), h("td", { text: v.label })]);
          });
        })))])
    ])));
    var rows = [];
    course.sections.forEach(function (sec) {
      sec.sources.book.forEach(function (b) {
        rows.push(h("tr", null, [h("td", { text: sec.number + ". " + sec.nav }), h("td", { text: b.label }), h("td", null, bookLinks(b))]));
      });
    });
    viewEl.appendChild(panel("Book", h("div", null, [
      h("p", { text: course.book.authors + ", " + course.book.title + ", " + course.book.edition + "." }),
      h("p", { className: "small-note", text: course.book.pageNote +
        (serverStatus && serverStatus.book && serverStatus.book.available ? " Local PDF links open your own copy through the local server."
                                                                           : " No local copy is being served, so only page numbers are shown.") }),
      h("table", { className: "src-table" }, [h("thead", null, [h("tr", null, [h("th", { text: "Section" }), h("th", { text: "Topic" }), h("th", { text: "Page" })])]),
                                              h("tbody", null, rows)])
    ])));
    viewEl.appendChild(panel("How this guide was made", h("ul", null, [
      M("li", "Animations: original ManimGL scenes rendered offscreen, one clip per step, cut at exact frame boundaries with stable stills. Formulas in the animations are typeset by matplotlib mathtext (no LaTeX)."),
      M("li", "Math on the page: KaTeX 0.19, bundled locally (MIT licence, vendor/katex/LICENSE)."),
      M("li", "Not included: the lecture video, its captions and the book's text. Section notes and worked examples are authored for this companion."),
      M("li", "The optional tutor sends your question, a short recent chat and this guide's own notes for the current step to the OpenAI API, only when you ask and only if the person running the server has configured a key.")
    ])));
    return "Sources & credits";
  }

  // ------------------------------------------------------------------ tutor

  var tutor = { history: [], busy: false, el: {}, controller: null };
  var MAX_Q = 1500, MAX_HISTORY = 8;

  function isNarrowTutor() { return window.matchMedia && window.matchMedia("(max-width: 1320px)").matches; }

  function buildTutor() {
    var T = tutor.el, aside = document.getElementById("tutor");
    T.status = h("span", { className: "tutor-status", id: "tutor-status" });
    T.close = h("button", { type: "button", className: "icon-btn tutor-close", "aria-label": "Close the GPT tutor" }, [h("span", { "aria-hidden": "true", text: "✕" })]);
    T.context = h("div", { className: "tutor-context", id: "tutor-context" });
    T.setup = h("div", { className: "tutor-setup", hidden: true });
    T.log = h("div", { className: "tutor-log", id: "tutor-log", role: "log", "aria-live": "polite", "aria-label": "Conversation" });
    T.prompts = h("div", { className: "tutor-prompts", role: "group", "aria-label": "Suggested questions" },
      ["Explain this step another way", "Why is this step valid?", "Give me a quick check question"].map(function (p) {
        return h("button", { type: "button", className: "btn small", text: p, onclick: function () { T.input.value = p; sendTutor(); } });
      }));
    T.input = h("textarea", { id: "tutor-input", maxlength: String(MAX_Q), rows: "3", "aria-describedby": "tutor-count",
                              placeholder: "Ask GPT about the current step…" });
    T.count = h("span", { className: "count", id: "tutor-count" });
    T.send = h("button", { type: "submit", className: "btn primary small", text: "Send" });
    T.clear = h("button", { type: "button", className: "link-btn", text: "Clear chat" });
    T.form = h("form", { className: "tutor-form" }, [h("label", { for: "tutor-input", className: "sr-only", text: "Question for the tutor" }), T.input,
      h("div", { className: "row" }, [T.count, h("span", null, [T.clear, " ", T.send])])]);
    aside.appendChild(h("div", { className: "tutor-head" }, [h("h2", { text: "GPT tutor" }), T.status, T.close]));
    aside.appendChild(T.context);
    aside.appendChild(T.setup);
    aside.appendChild(T.log);
    aside.appendChild(T.prompts);
    aside.appendChild(T.form);
    T.close.addEventListener("click", function () { setTutorOpen(false); document.getElementById("tutor-toggle").focus(); });
    T.input.addEventListener("input", syncCount);
    T.input.addEventListener("keydown", function (e) { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); sendTutor(); } });
    T.form.addEventListener("submit", function (e) { e.preventDefault(); sendTutor(); });
    T.clear.addEventListener("click", function () { tutor.history = []; T.log.textContent = ""; addNote("Chat cleared."); });
    syncCount();
    applyTutorStatus();
  }

  function syncCount() { tutor.el.count.textContent = tutor.el.input.value.length + " / " + MAX_Q; }

  function applyTutorStatus() {
    var T = tutor.el, st = serverStatus && serverStatus.tutor;
    T.setup.textContent = "";
    if (!serverStatus) {
      T.status.textContent = "offline"; T.status.setAttribute("data-state", "off");
      T.setup.appendChild(document.createTextNode("The GPT tutor needs the local server. Start the guide with launch_phase_plane.ps1; lessons, explorer and quiz work without it."));
      T.setup.hidden = false;
    } else if (!st || !st.configured) {
      T.status.textContent = "not set up"; T.status.setAttribute("data-state", "off");
      T.setup.appendChild(document.createTextNode("GPT chat is ready to enable, but no OpenAI API key is configured, so it is off. To turn it on, set the "));
      T.setup.appendChild(h("code", { text: "OPENAI_API_KEY" }));
      T.setup.appendChild(document.createTextNode(" environment variable (and optionally "));
      T.setup.appendChild(h("code", { text: "OPENAI_MODEL" }));
      T.setup.appendChild(document.createTextNode(") before running launch_phase_plane.ps1. See courses/mit-de/phase-plane/README.md. Everything else works without it."));
      T.setup.hidden = false;
    } else {
      T.status.textContent = "ready · " + st.model; T.status.setAttribute("data-state", "ready");
      T.setup.hidden = true;
    }
    var usable = !!(st && st.configured);
    T.send.disabled = !usable || tutor.busy;
    T.input.disabled = !usable;
    T.prompts.querySelectorAll("button").forEach(function (b) { b.disabled = !usable || tutor.busy; });
  }

  function setTutorOpen(open, quiet) {
    state.tutorOpen = open;
    var aside = document.getElementById("tutor"), shell = document.getElementById("shell");
    aside.hidden = !open;
    shell.classList.toggle("tutor-open", open);
    document.getElementById("tutor-toggle").setAttribute("aria-expanded", open ? "true" : "false");
    if (isNarrowTutor() && window.matchMedia("(max-width: 900px)").matches) document.getElementById("scrim").hidden = !open;
    updateTutorContext();
    if (!quiet) save();
    if (open && !quiet) focusTutorInput();
  }

  function focusTutorInput() {
    var T = tutor.el;
    setTimeout(function () { (T.input.disabled ? T.close : T.input).focus(); }, 0);
  }

  function tutorContext() {
    var r = currentRoute, ctx = { page: r };
    var m = /^s(\d+)$/.exec(r);
    if (m) {
      ctx.section = +m[1];
      if (stageAttached()) { ctx.sequence = player.seq.id; ctx.step = player.playing ? player.target : player.k; }
    }
    return ctx;
  }

  function contextLabel(ctx) {
    if (ctx.section) {
      var sec = course.sections[ctx.section - 1];
      var s1 = "Section " + ctx.section + ": " + plain(sec.title);
      if (ctx.sequence) {
        var sq = seqById[ctx.sequence];
        s1 += " · " + (ctx.step === 0 ? "start of “" + plain(sq.title) + "”" : "step " + ctx.step + " of " + sq.steps.length + ": " + plain(sq.steps[ctx.step - 1].title));
      }
      return s1;
    }
    return { explorer: "Explorer page", quiz: "Quiz page (the tutor will not reveal answers outright)", sources: "Sources page" }[ctx.page] || "Course";
  }

  function updateTutorContext() {
    if (!course || !tutor.el.context) return;
    var T = tutor.el;
    T.context.textContent = "";
    T.context.appendChild(h("strong", { text: "Context sent with your question" }));
    T.context.appendChild(document.createTextNode(contextLabel(tutorContext())));
  }

  function addMsg(role, text, extra) {
    var T = tutor.el;
    var who = { user: "You", assistant: "GPT", error: "Problem", note: "Note" }[role] || role;
    var m = h("div", { className: "msg " + role }, [h("span", { className: "who", text: who })]);
    if (role === "assistant") renderRich(m, text);
    else m.appendChild(h("p", { text: text }));
    if (extra) m.appendChild(h("p", { className: "small-note", text: extra }));
    T.log.appendChild(m);
    T.log.scrollTop = T.log.scrollHeight;
    return m;
  }
  function addNote(text) { return addMsg("note", text); }

  // Untrusted model text: paragraphs and simple "- " bullet lists as text nodes, then KaTeX for math.
  function renderRich(container, text) {
    var blocks = String(text).replace(/\r/g, "").split(/\n{2,}/);
    blocks.forEach(function (b) {
      var lines = b.split("\n");
      if (lines.every(function (l) { return /^\s*([-*•]|\d+[.)])\s+/.test(l); })) {
        var ul = h("ul");
        lines.forEach(function (l) { ul.appendChild(h("li", { text: l.replace(/^\s*([-*•]|\d+[.)])\s+/, "") })); });
        container.appendChild(ul);
      } else container.appendChild(h("p", { text: b }));
    });
    if (window.renderMathInElement) window.renderMathInElement(container, { delimiters: DELIMS, throwOnError: false, trust: false });
  }

  function sendTutor() {
    var T = tutor.el, q = T.input.value.trim();
    if (!q || tutor.busy || T.send.disabled) return;
    if (q.length > MAX_Q) { addMsg("error", "Please keep questions under " + MAX_Q + " characters."); return; }
    var ctx = tutorContext();
    addMsg("user", q, "Context: " + contextLabel(ctx));
    T.input.value = "";
    syncCount();
    tutor.busy = true;
    applyTutorStatus();
    var pending = addNote("Waiting for GPT…");
    var body = { question: q, history: tutor.history.slice(-MAX_HISTORY), context: ctx };
    var ctl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 75000);
    fetch("api/tutor", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" },
                         body: JSON.stringify(body), signal: ctl ? ctl.signal : undefined })
      .then(function (r) { return r.json().catch(function () { return { ok: false, error: "The server sent an unreadable reply (HTTP " + r.status + ")." }; }); })
      .then(function (res) {
        pending.remove();
        if (res && res.ok && typeof res.text === "string") {
          var extra = res.incomplete ? "This answer was cut short (" + res.incomplete + ")." : (res.refusal ? "The model declined to answer this." : "");
          addMsg("assistant", res.text, extra || null);
          tutor.history.push({ role: "user", text: q });
          tutor.history.push({ role: "assistant", text: res.text.slice(0, 4000) });
          tutor.history = tutor.history.slice(-MAX_HISTORY);
        } else {
          addMsg("error", (res && res.error) || "GPT could not answer.");
          if (res && res.code === "not_configured" && serverStatus) { serverStatus.tutor = { configured: false }; }
        }
      })
      .catch(function (err) {
        pending.remove();
        addMsg("error", err && err.name === "AbortError" ? "No reply within 75 seconds; please try again." : "Could not reach the local server.");
      })
      .then(function () { clearTimeout(timer); tutor.busy = false; applyTutorStatus(); if (!T.input.disabled) T.input.focus(); });
  }

  // expose a tiny hook for QA (read-only state)
  window.__controlGuide = { player: function () { return player.seq ? { seq: player.seq.id, k: player.k, playing: player.playing } : null; } };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
