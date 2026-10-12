/*
 * Browser study guide for second-order linear ODEs.
 * Course text comes from course.json (shared with the native ManimGL guide); the animated
 * derivations come from animations/manifest.json (pre-rendered ManimGL clips, one per step);
 * the solver is ode_math.js (twin of native/ode_math.py). Math is typeset with bundled KaTeX.
 */
(function () {
  "use strict";

  var M = window.ODEMath;
  var SVG_NS = "http://www.w3.org/2000/svg";
  var DELIMS = [{ left: "$", right: "$", display: false }];
  var THEME_KEY = "sode-theme";
  var DEFAULT_SEQ = "characteristic";

  var course = null;
  var anim = null;                       // animations manifest
  var seqById = {};
  var viewEl = null;
  var firstRoute = true;
  var currentRoute = "";
  var state = {
    examples: {},                        // kept for compatibility (written solutions are always complete)
    explorer: null,                      // slider values, kept across route and theme changes
    marker: { t: 0, playing: false, raf: 0, last: 0 },
    quiz: { index: 0, answers: {} },     // question id -> {choice, attempts, firstCorrect}
    steps: {},                           // sequence id -> current step (0 = opening state)
    lessonSeq: {},                       // lesson number -> last chosen sequence id
    watchSeq: null                       // sequence last shown on the Animated derivations page
  };
  var ex = null;                         // live explorer DOM handles
  var reduceMotion = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };

  // ------------------------------------------------------------------ helpers

  function h(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "text") node.textContent = attrs[k];
        else if (k === "className") node.className = attrs[k];
        else if (k.slice(0, 2) === "on") node.addEventListener(k.slice(2), attrs[k]);
        else node.setAttribute(k, attrs[k]);
      });
    }
    (children || []).forEach(function (c) { if (c) node.appendChild(c); });
    return node;
  }

  function s(tag, attrs) {
    var node = document.createElementNS(SVG_NS, tag);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    return node;
  }

  // Text with $...$ inline math: set as plain text, then let KaTeX auto-render find the math.
  function mathText(node, text) {
    node.textContent = text;
    if (window.renderMathInElement) {
      window.renderMathInElement(node, { delimiters: DELIMS, throwOnError: false });
    }
    return node;
  }

  function displayMath(node, tex) {
    if (window.katex) window.katex.render(tex, node, { displayMode: true, throwOnError: false });
    else node.textContent = tex;
    return node;
  }

  // Display-style formula typeset inline, so a long one wraps after a relation or operator
  // instead of running off the side of a narrow panel.
  function flowMath(node, tex) {
    if (window.katex) window.katex.render("\\displaystyle " + tex, node, { displayMode: false, throwOnError: false });
    else node.textContent = tex;
    return node;
  }

  // Shrink a display formula until it fits its box (never below 62%); past that it scrolls inside the box.
  function fitMath(node) {
    node.style.fontSize = "";
    var size = 100;
    while (node.scrollWidth > node.clientWidth + 1 && size > 62) {
      size -= 6;
      node.style.fontSize = size + "%";
    }
  }

  function announce(msg) {
    var el = document.getElementById("app-status");
    if (!el) return;
    el.textContent = "";
    setTimeout(function () { el.textContent = msg; }, 30);
  }

  function focusHeading() {
    var h1 = viewEl.querySelector("h1");
    if (h1) { h1.setAttribute("tabindex", "-1"); h1.focus({ preventScroll: true }); }
  }

  function plainTitle(t) { return t.replace(/\$([^$]*)\$/g, "$1"); }

  // ------------------------------------------------------------------ theme

  var themeStorageOk = true;

  function storedTheme() {
    try {
      var t = window.localStorage.getItem(THEME_KEY);
      return t === "light" || t === "dark" ? t : null;
    } catch (e) { themeStorageOk = false; return null; }
  }

  function systemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }

  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    var btn = document.getElementById("theme-toggle");
    if (btn) btn.setAttribute("aria-pressed", t === "dark" ? "true" : "false");
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", t === "dark" ? "#0e131c" : "#1f2a44");
  }

  function setupTheme() {
    applyTheme(document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark");
    var btn = document.getElementById("theme-toggle");
    btn.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      var saved = true;
      try { window.localStorage.setItem(THEME_KEY, next); } catch (e) { saved = false; themeStorageOk = false; }
      announce((next === "dark" ? "Dark" : "Light") + " theme on." +
               (saved ? "" : " This browser does not allow saving the choice, so it lasts for this visit only."));
    });
    if (window.matchMedia) {
      var mq = window.matchMedia("(prefers-color-scheme: light)");
      var follow = function () { if (!storedTheme()) applyTheme(systemTheme()); };
      if (mq.addEventListener) mq.addEventListener("change", follow);
      else if (mq.addListener) mq.addListener(follow);
    }
  }

  // ------------------------------------------------------------------ boot + routing

  function boot() {
    viewEl = document.getElementById("view");
    setupTheme();
    var toggle = document.querySelector(".nav-toggle");
    var chapters = document.getElementById("chapters");
    toggle.addEventListener("click", function () {
      var open = chapters.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", quizKeys);
    document.addEventListener("keydown", stageKeys);

    var getJSON = function (url) {
      return fetch(url, { cache: "no-cache" }).then(function (r) {
        if (!r.ok) throw new Error(url + ": HTTP " + r.status);
        return r.json();
      });
    };
    Promise.all([getJSON("course.json"), getJSON("animations/manifest.json").catch(function () { return null; })])
      .then(function (res) {
        course = res[0];
        anim = res[1];
        if (anim) anim.sequences.forEach(function (sq) { seqById[sq.id] = sq; });
        buildNav();
        buildStage();
        window.addEventListener("hashchange", route);
        route();
      })
      .catch(function (err) {
        viewEl.innerHTML = "";
        viewEl.appendChild(h("p", { className: "error", text:
          "Could not load the course (" + err.message + "). If you opened index.html directly from disk, " +
          "start the guide with launch_browser.ps1 instead: browsers block data requests from pages opened from disk." }));
      });
  }

  function buildNav() {
    var list = document.getElementById("lesson-links");
    course.lessons.forEach(function (lesson) {
      list.appendChild(h("li", null, [
        h("a", { href: "#lesson-" + lesson.number, "data-route": "lesson-" + lesson.number }, [
          h("span", { className: "num", "aria-hidden": "true", text: String(lesson.number) }),
          document.createTextNode(lesson.nav || lesson.title)
        ])
      ]));
    });
  }

  function parseHash() {
    var hash = (location.hash || "").replace(/^#/, "");
    var parts = hash.split("/");
    return { base: parts[0] || "watch", seq: parts[1] || null };
  }

  function route() {
    var r = parseHash();
    stopMarker();
    settlePlayback();
    player.onSelect = null;
    player.context = null;
    ex = null;
    qx = null;
    if (player.wrap && player.wrap.parentNode) player.wrap.parentNode.removeChild(player.wrap);
    exitFullscreen();
    viewEl.innerHTML = "";
    var m = /^lesson-(\d+)$/.exec(r.base);
    var title, active = r.base;
    if (m && +m[1] >= 1 && +m[1] <= course.lessons.length) {
      title = renderLesson(+m[1], r.seq);
    } else if (r.base === "explorer") {
      title = renderExplorer();
    } else if (r.base === "quiz") {
      title = renderQuiz();
    } else if (r.base === "reading") {
      title = renderReading();
    } else {
      active = "watch";
      title = renderWatch(r.seq);
    }
    currentRoute = active;
    document.title = title + " · Second-Order Linear ODEs";
    document.querySelectorAll(".chapters a").forEach(function (a) {
      if (a.getAttribute("data-route") === active) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
    var chapters = document.getElementById("chapters");
    chapters.classList.remove("open");
    document.querySelector(".nav-toggle").setAttribute("aria-expanded", "false");
    if (!firstRoute) { window.scrollTo(0, 0); focusHeading(); }
    firstRoute = false;
  }

  // Update the address bar for a sequence choice without re-rendering the page.
  function replaceHash(hash) {
    if (location.hash === hash) return;
    if (window.history && history.replaceState) history.replaceState(null, "", hash);
    else location.hash = hash;
  }

  // ------------------------------------------------------------------ the animation stage

  var player = {
    wrap: null, seq: null, k: 0, playing: false, target: 0, token: 0, mode: "idle",
    started: false, watchdog: 0, loadingTimer: 0, notice: "", context: null
  };

  function seqList() { return anim ? anim.sequences : []; }
  function frameFor(sq, k) { return k === 0 ? sq.initial.frame : sq.steps[k - 1].finalFrame; }

  function buildStage() {
    var P = player;
    P.eyebrow = h("p", { className: "eyebrow stage-eyebrow" });
    P.title = h("h2", { className: "stage-title", id: "stage-title" });
    P.summary = h("p", { className: "stage-summary" });
    P.still = h("img", { className: "stage-still", alt: "", "aria-hidden": "true", decoding: "async" });
    P.video = h("video", { className: "stage-video", muted: "", playsinline: "", preload: "auto",
                           "aria-hidden": "true", tabindex: "-1", disablepictureinpicture: "" });
    P.video.muted = true;
    P.fallback = h("div", { className: "stage-fallback", hidden: "" });
    P.loading = h("div", { className: "stage-loading", hidden: "", "aria-hidden": "true" },
                  [h("span", { className: "spinner" }), h("span", { text: "Loading animation…" })]);
    P.fsBtn = h("button", { type: "button", className: "stage-fs", "aria-label": "Full screen", title: "Full screen" },
                [h("span", { "aria-hidden": "true", text: "⛶" })]);
    P.stage = h("div", { className: "stage", "data-state": "idle" }, [P.still, P.video, P.fallback, P.loading, P.fsBtn]);
    P.progress = h("ol", { className: "stage-progress", "aria-hidden": "true" });
    P.backBtn = h("button", { type: "button", className: "btn", "data-action": "back", "aria-label": "Back one step" },
                  [h("span", { "aria-hidden": "true", text: "◀ " }), document.createTextNode("Back")]);
    P.replayBtn = h("button", { type: "button", className: "btn", "data-action": "replay", "aria-label": "Replay this step's animation" },
                    [h("span", { "aria-hidden": "true", text: "↻ " }), document.createTextNode("Replay")]);
    P.nextBtn = h("button", { type: "button", className: "btn primary next-btn", "data-action": "next" });
    P.restartBtn = h("button", { type: "button", className: "btn", "data-action": "restart", "aria-label": "Restart this derivation" },
                     [h("span", { "aria-hidden": "true", text: "⏮ " }), document.createTextNode("Restart")]);
    P.controls = h("div", { className: "stage-controls", role: "group", "aria-label": "Animation controls" },
                   [P.backBtn, P.replayBtn, P.nextBtn, P.restartBtn]);
    P.keyHint = h("p", { className: "key-hint", text: "Keys: → or N next step, ← or B back, R replay." });
    P.col = h("div", { className: "stage-col" }, [P.stage, P.progress, P.controls, P.keyHint]);

    P.count = h("p", { className: "step-count" });
    P.badge = h("span", { className: "relation-badge" });
    P.stepTitle = h("h3", { className: "step-title", id: "step-title" });
    P.eq = h("div", { className: "step-eq" });
    P.expl = h("p", { className: "step-expl" });
    P.noticeEl = h("p", { className: "stage-notice", role: "note", hidden: "" });
    P.completeNext = h("button", { type: "button", className: "btn primary", "data-action": "next-seq" });
    P.completeRestart = h("button", { type: "button", className: "btn", "data-action": "restart-complete", text: "Watch again from the start" });
    P.complete = h("div", { className: "complete-box", hidden: "" }, [
      h("p", { className: "complete-title" }, [h("span", { "aria-hidden": "true", text: "✓ " }),
                                               document.createTextNode("Derivation complete")]),
      h("div", { className: "complete-actions" }, [P.completeNext, P.completeRestart])
    ]);
    P.transcriptList = h("ol", { className: "transcript-list" });
    P.transcript = h("details", { className: "transcript" }, [
      h("summary", { text: "All steps so far (text version)" }), P.transcriptList]);
    P.panel = h("section", { className: "step-panel", "aria-labelledby": "step-title" },
                [P.count, P.badge, P.stepTitle, P.eq, P.expl, P.noticeEl, P.complete, P.transcript]);
    P.status = h("p", { className: "sr-only", role: "status", "aria-live": "polite" });
    P.wrap = h("section", { className: "stage-wrap", "aria-labelledby": "stage-title" }, [
      h("header", { className: "stage-head" }, [P.eyebrow, P.title, P.summary]),
      h("div", { className: "stage-grid" }, [P.col, P.panel]),
      P.status
    ]);

    P.nextBtn.addEventListener("click", onNext);
    P.backBtn.addEventListener("click", onBack);
    P.replayBtn.addEventListener("click", onReplay);
    P.restartBtn.addEventListener("click", function () { goTo(0, "Back to the start."); });
    P.completeRestart.addEventListener("click", function () { goTo(0, "Back to the start."); P.nextBtn.focus(); });
    P.completeNext.addEventListener("click", goNextSequence);
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

  // Attach the shared stage to a page, showing sequence `id`.
  function mountStage(container, id, context) {
    var P = player;
    container.appendChild(P.wrap);
    P.context = context;
    if (!anim || !seqById[id]) {
      P.wrap.classList.add("unavailable");
      P.title.textContent = "Animations unavailable";
      P.summary.textContent = "The animated derivations could not be loaded. The lesson notes below cover the same material.";
      return;
    }
    selectSequence(id, true);
  }

  function selectSequence(id, quiet) {
    var P = player;
    var sq = seqById[id];
    if (!sq) return;
    if (P.seq !== sq) {
      cancelPlayback();
      P.seq = sq;
      P.notice = "";
      P.k = Math.min(state.steps[id] || 0, sq.steps.length);
      P.transcript.open = false;
    }
    var lesson = course.lessons[sq.lesson - 1];
    P.eyebrow.textContent = "Lesson " + sq.lesson + " · " + (lesson ? lesson.nav : "") + " · animated derivation";
    mathText(P.title, sq.title);
    mathText(P.summary, sq.summary);
    P.progress.innerHTML = "";
    sq.steps.forEach(function () { P.progress.appendChild(h("li")); });
    showState(P.k);
    preload();
    if (!quiet) announce("Showing " + plainTitle(sq.title) + ", step " + P.k + " of " + sq.steps.length + ".");
  }

  // Swap the visible still only after the new picture has decoded off-screen, so the stage
  // never shows a half-loaded or empty frame. Only the most recent request is applied.
  function setStill(src) {
    var P = player;
    P.stillWanted = src;
    if (P.still.getAttribute("src") === src && P.still.complete && P.still.naturalWidth) return Promise.resolve();
    var img = new Image();
    img.src = src;
    var ready = img.decode ? img.decode() : new Promise(function (res, rej) { img.onload = res; img.onerror = rej; });
    return ready.then(function () {
      if (P.stillWanted === src) P.still.setAttribute("src", src);
    }, function () {
      if (P.stillWanted === src) P.still.setAttribute("src", src);   // the error handler shows the fallback
    });
  }

  function showFallback(on) {
    var P = player;
    if (!on) { P.fallback.hidden = true; P.stage.classList.remove("fallback-on"); return; }
    if (!P.seq) return;
    var k = P.playing ? P.target : P.k;
    var tex = k === 0 ? P.seq.initial.tex : P.seq.steps[k - 1].tex;
    P.fallback.innerHTML = "";
    var box = displayMath(h("div", { className: "fallback-eq" }), tex);
    P.fallback.appendChild(box);
    P.fallback.appendChild(h("p", { text: "The picture for this step could not be loaded; the equation is shown instead." }));
    P.fallback.hidden = false;
    P.stage.classList.add("fallback-on");
    fitMath(box);
  }

  // Show stable state k. Resolves once the still is on screen and the video layer is hidden.
  function showState(k) {
    var P = player;
    P.k = k;
    state.steps[P.seq.id] = k;
    var tok = P.token;
    P.stage.setAttribute("data-state", k === P.seq.steps.length ? "complete" : "idle");
    renderPanel();
    return setStill(frameFor(P.seq, k)).then(function () {
      if (!P.playing && P.token === tok) P.stage.classList.remove("video-on");
    });
  }

  function hideVideoNow() {
    var P = player;
    P.stage.classList.remove("video-on");
    if (!P.video.paused) P.video.pause();
  }

  // Preload the next transition into the single video element while the user reads.
  function preload() {
    var P = player;
    // Never swap the source while the video is the visible layer (that would blank it).
    if (!P.seq || P.playing || P.stage.classList.contains("video-on")) return;
    if (P.k < P.seq.steps.length) {
      var st = P.seq.steps[P.k];
      if (P.video.getAttribute("src") !== st.transition.src) {
        P.video.setAttribute("src", st.transition.src);
        P.video.load();
      }
      var img = new Image();
      img.src = st.finalFrame;
    }
  }

  function showLoading() {
    var P = player;
    if (P.playing && !P.started) {
      P.loading.hidden = false;
      P.stage.setAttribute("data-state", "loading");
    }
  }

  function armWatchdog() {
    var P = player;
    clearTimeout(P.watchdog);
    var tok = P.token;
    var dur = P.seq.steps[P.target - 1].transition.duration;
    P.watchdog = setTimeout(function () { if (P.playing && P.token === tok) finishTransition(tok); }, dur * 1000 + 4000);
  }

  // Play the transition into state `k` (from state k-1).
  function playTransition(k) {
    var P = player;
    var st = P.seq.steps[k - 1];
    var tok = ++P.token;
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
    if (P.video.getAttribute("src") !== st.transition.src) {
      P.video.setAttribute("src", st.transition.src);
      P.video.load();
    } else {
      try { P.video.currentTime = 0; } catch (e) { /* not seekable yet */ }
    }
    P.loadingTimer = setTimeout(showLoading, 250);
    // A stalled first frame should not leave the learner stuck.
    P.watchdog = setTimeout(function () { if (P.playing && P.token === tok && !P.started) failTransition(tok); }, 12000);
    var pr = P.video.play();
    if (pr && pr.catch) pr.catch(function () { if (P.playing && P.token === tok) failTransition(tok); });
    P.status.textContent = "Playing step " + k + " of " + P.seq.steps.length + ": " + plainTitle(st.title) + ".";
  }

  function finishTransition(tok) {
    var P = player;
    if (!P.playing || tok !== P.token) return;
    clearTimeout(P.watchdog);
    clearTimeout(P.loadingTimer);
    P.playing = false;
    P.loading.hidden = true;
    var k = P.target;
    // The paused last frame stays on screen until the matching still has decoded; only then
    // is the video hidden and the next clip loaded into it. No flash, no jump back.
    showState(k).then(function () { if (!P.playing && P.k === k) preload(); });
    P.status.textContent = "Step " + k + " of " + P.seq.steps.length + ": " + plainTitle(P.seq.steps[k - 1].title) + "." +
      (k === P.seq.steps.length ? " Derivation complete." : "");
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
    P.notice = "The animation for this step could not be played, so the result is shown instead. The equation and explanation are complete without it.";
    showState(k);
    P.status.textContent = "Animation unavailable. Showing step " + k + " of " + P.seq.steps.length + ": " + plainTitle(P.seq.steps[k - 1].title) + ".";
    // Drop the broken source so a later Replay retries from scratch.
    P.video.removeAttribute("src");
    P.video.load();
  }

  // Stop any playback and forget it (used by Back/Restart and sequence switches).
  function cancelPlayback() {
    var P = player;
    P.token++;
    clearTimeout(P.watchdog);
    clearTimeout(P.loadingTimer);
    P.playing = false;
    P.loading.hidden = true;
    if (P.video) hideVideoNow();
  }

  // Leaving the page mid-transition: commit to the step that was requested.
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
    showState(Math.max(0, Math.min(k, P.seq.steps.length)));
    preload();
    P.status.textContent = (msg ? msg + " " : "") + "Step " + P.k + " of " + P.seq.steps.length + ".";
  }

  function onNext() {
    var P = player;
    if (!P.seq || P.playing) return;                         // guard double clicks
    if (P.k >= P.seq.steps.length) { goNextSequence(); return; }
    if (reduceMotion.matches) {
      showState(P.k + 1);
      preload();
      P.status.textContent = "Step " + P.k + " of " + P.seq.steps.length + ": " + plainTitle(P.seq.steps[P.k - 1].title) +
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
    var list = seqList();
    var i = list.indexOf(sq);
    return i >= 0 && i < list.length - 1 ? list[i + 1] : null;
  }

  function goNextSequence() {
    var P = player;
    var nx = nextSequenceOf(P.seq);
    if (!nx) { location.hash = "#quiz"; return; }
    if (P.context && P.context.type === "lesson" && nx.lesson !== P.context.lesson) {
      location.hash = "#lesson-" + nx.lesson + "/" + nx.id;
      return;
    }
    state.steps[nx.id] = 0;
    selectSequence(nx.id, false);
    replaceHash(P.context && P.context.type === "lesson" ? "#lesson-" + nx.lesson + "/" + nx.id : "#watch/" + nx.id);
    P.nextBtn.focus();
    P.wrap.scrollIntoView({ block: "start", behavior: reduceMotion.matches ? "auto" : "smooth" });
  }

  function renderPanel() {
    var P = player;
    var sq = P.seq;
    if (!sq) return;
    var n = sq.steps.length;
    var k = P.playing ? P.target : P.k;
    var item = k === 0 ? null : sq.steps[k - 1];
    P.count.textContent = k === 0 ? "Start · " + n + " steps" : "Step " + k + " of " + n;
    P.badge.hidden = !item;
    if (item) {
      P.badge.textContent = item.relationLabel;
      P.badge.setAttribute("data-relation", item.relation);
    }
    mathText(P.stepTitle, item ? item.title : sq.initial.title);
    flowMath(P.eq, item ? item.tex : sq.initial.tex);
    mathText(P.expl, item ? item.explanation : sq.initial.explanation +
             (reduceMotion.matches ? "" : " Press Next step to see the first transformation."));
    var notice = P.notice;
    if (!notice && reduceMotion.matches && k > 0 && !P.playing) {
      notice = "Reduced motion is on, so steps jump straight to their result. Press Replay to watch a transition.";
    }
    P.noticeEl.textContent = notice;
    P.noticeEl.hidden = !notice;
    P.noticeEl.className = "stage-notice" + (P.notice ? " warn" : "");
    var done = !P.playing && P.k === n;
    P.complete.hidden = !done;
    var nx = nextSequenceOf(sq);
    var nextLabel = nx ? "Next derivation: " + plainTitle(nx.title) : "Check yourself: the quiz";
    P.completeNext.textContent = nextLabel + " →";
    // Controls
    P.nextBtn.textContent = "";
    if (done) {
      P.nextBtn.appendChild(document.createTextNode(nx ? "Next derivation " : "Go to the quiz "));
      P.nextBtn.setAttribute("aria-label", nextLabel);
    } else {
      P.nextBtn.appendChild(document.createTextNode("Next step "));
      P.nextBtn.setAttribute("aria-label", P.playing ? "Next step (playing)" : "Next step");
    }
    P.nextBtn.appendChild(h("span", { "aria-hidden": "true", text: "▶" }));
    P.nextBtn.setAttribute("aria-disabled", P.playing ? "true" : "false");
    P.backBtn.disabled = !P.playing && P.k === 0;
    P.replayBtn.disabled = k === 0;
    P.restartBtn.disabled = !P.playing && P.k === 0;
    Array.prototype.forEach.call(P.progress.children, function (li, i) {
      li.className = i < P.k ? "done" : (P.playing && i === P.target - 1 ? "active" : "");
    });
    P.wrap.setAttribute("data-step", String(P.k));
    P.wrap.setAttribute("data-playing", P.playing ? "true" : "false");
    // Transcript of the steps reached so far
    P.transcriptList.innerHTML = "";
    P.transcriptList.appendChild(transcriptItem("Start: " + sq.initial.title, sq.initial.tex, sq.initial.explanation));
    for (var i = 0; i < P.k; i++) {
      var st = sq.steps[i];
      P.transcriptList.appendChild(transcriptItem(st.title + " (" + st.relationLabel + ")", st.tex, st.explanation));
    }
    requestAnimationFrame(function () { fitMath(P.eq); });
    if (P.onSelect) P.onSelect(sq);
  }

  function transcriptItem(title, tex, expl) {
    return h("li", null, [h("p", { className: "t-title", text: title }),
                          flowMath(h("div", { className: "t-eq" }), tex), mathText(h("p"), expl)]);
  }

  function stageAttached() { return player.wrap && document.body.contains(player.wrap) && player.seq; }

  function stageKeys(e) {
    if (!stageAttached()) return;
    if (e.altKey || e.ctrlKey || e.metaKey || e.defaultPrevented) return;
    var t = e.target || {};
    var tag = (t.tagName || "").toUpperCase();
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || t.isContentEditable) return;
    var key = e.key;
    if (key === "ArrowRight" || key === "n" || key === "N") { e.preventDefault(); onNext(); }
    else if (key === "ArrowLeft" || key === "b" || key === "B") { e.preventDefault(); onBack(); }
    else if (key === "r" || key === "R") { e.preventDefault(); onReplay(); }
  }

  function toggleFullscreen() {
    var P = player;
    if (document.fullscreenElement) { exitFullscreen(); return; }
    if (P.col.requestFullscreen) P.col.requestFullscreen().catch(function () { /* not allowed */ });
  }
  function exitFullscreen() {
    if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(function () {});
  }
  function syncFullscreen() {
    var on = document.fullscreenElement === player.col;
    player.fsBtn.setAttribute("aria-label", on ? "Exit full screen" : "Full screen");
    player.fsBtn.title = on ? "Exit full screen" : "Full screen";
  }

  // ------------------------------------------------------------------ watch hub

  function renderWatch(seqId) {
    var id = seqById[seqId] ? seqId : (seqById[state.watchSeq] ? state.watchSeq : DEFAULT_SEQ);
    viewEl.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Start here" }),
      h("h1", { text: "Watch the derivations, one step at a time" }),
      h("p", { className: "summary", text: "Each Next step plays one transformation and stops, so you can read the explanation beside it. " +
        "Back, Replay and Restart move through the steps; the lesson notes, explorer and quiz are in the sidebar." })
    ]));
    var stageHost = h("div");
    viewEl.appendChild(stageHost);
    var listHost = h("section", { className: "playlist", "aria-labelledby": "playlist-title" },
                     [h("h2", { id: "playlist-title", text: "All animated derivations" })]);
    var buttons = {};
    var ol = h("ol", { className: "playlist-list" });
    seqList().forEach(function (sq) {
      var lesson = course.lessons[sq.lesson - 1];
      var b = h("button", { type: "button", className: "playlist-item", "data-seq": sq.id, "aria-pressed": "false" }, [
        h("span", { className: "pl-lesson", text: "Lesson " + sq.lesson + " · " + lesson.nav }),
        mathText(h("span", { className: "pl-title" }), sq.title),
        h("span", { className: "pl-meta" })
      ]);
      b.addEventListener("click", function () {
        selectSequence(sq.id, false);
        replaceHash("#watch/" + sq.id);
        player.wrap.scrollIntoView({ block: "start", behavior: reduceMotion.matches ? "auto" : "smooth" });
        player.nextBtn.focus({ preventScroll: true });
      });
      buttons[sq.id] = b;
      ol.appendChild(h("li", null, [b, h("a", { className: "pl-notes", href: "#lesson-" + sq.lesson, text: "Lesson notes" })]));
    });
    listHost.appendChild(ol);
    player.onSelect = function (cur) {
      state.watchSeq = cur.id;
      Object.keys(buttons).forEach(function (k) {
        var on = k === cur.id;
        buttons[k].setAttribute("aria-pressed", on ? "true" : "false");
        var sq = seqById[k];
        var at = state.steps[k] || 0;
        buttons[k].querySelector(".pl-meta").textContent = sq.steps.length + " steps" +
          (at >= sq.steps.length ? " · completed" : at > 0 ? " · at step " + at : "");
      });
    };
    viewEl.appendChild(listHost);
    mountStage(stageHost, id, { type: "watch" });
    return "Animated derivations";
  }

  // ------------------------------------------------------------------ lessons

  function lessonSequences(n) {
    return seqList().filter(function (sq) { return sq.lesson === n; });
  }

  function renderLesson(n, seqId) {
    var lesson = course.lessons[n - 1];
    viewEl.appendChild(h("header", { className: "page-head lesson-head" }, [
      h("p", { className: "eyebrow", text: "Lesson " + n + " of " + course.lessons.length }),
      h("h1", { text: lesson.title }),
      mathText(h("p", { className: "summary" }), lesson.summary)
    ]));
    var seqs = lessonSequences(n);
    if (seqs.length) {
      var chosen = seqs.filter(function (sq) { return sq.id === seqId; })[0] ||
                   seqs.filter(function (sq) { return sq.id === state.lessonSeq[n]; })[0] || seqs[0];
      var tabs = null, tabBtns = {};
      if (seqs.length > 1) {
        tabs = h("div", { className: "seq-tabs", role: "group", "aria-label": "Derivations in this lesson" });
        seqs.forEach(function (sq) {
          var b = h("button", { type: "button", className: "seq-tab", "data-seq": sq.id, "aria-pressed": "false" });
          mathText(b, sq.title);
          b.addEventListener("click", function () {
            selectSequence(sq.id, false);
            replaceHash("#lesson-" + n + "/" + sq.id);
          });
          tabBtns[sq.id] = b;
          tabs.appendChild(b);
        });
        viewEl.appendChild(tabs);
      }
      player.onSelect = function (cur) {
        state.lessonSeq[n] = cur.id;
        Object.keys(tabBtns).forEach(function (k) { tabBtns[k].setAttribute("aria-pressed", k === cur.id ? "true" : "false"); });
      };
      var host = h("div");
      viewEl.appendChild(host);
      mountStage(host, chosen.id, { type: "lesson", lesson: n });
    }

    var notes = h("section", { className: "notes", "aria-labelledby": "notes-title" }, [
      h("h2", { className: "notes-title", id: "notes-title", text: "Lesson notes" })
    ]);
    lesson.pages.forEach(function (page, pi) {
      var sec = h("section", { className: "lesson-section", id: "l" + n + "-p" + (pi + 1),
                               "aria-labelledby": "l" + n + "-h" + (pi + 1) });
      var h3 = h("h3", { id: "l" + n + "-h" + (pi + 1) }, [h("span", { className: "sec-num", text: n + "." + (pi + 1) })]);
      h3.appendChild(document.createTextNode(page.heading));
      sec.appendChild(h3);
      page.blocks.forEach(function (block) { sec.appendChild(renderBlock(block, n)); });
      notes.appendChild(sec);
    });
    viewEl.appendChild(notes);

    var pager = h("nav", { className: "pager", "aria-label": "Lesson navigation" });
    if (n > 1) {
      pager.appendChild(h("a", { className: "prev", href: "#lesson-" + (n - 1) }, [
        h("small", { text: "← Previous lesson" }), document.createTextNode(course.lessons[n - 2].title)]));
    }
    if (n < course.lessons.length) {
      pager.appendChild(h("a", { className: "next", href: "#lesson-" + (n + 1) }, [
        h("small", { text: "Next lesson →" }), document.createTextNode(course.lessons[n].title)]));
    } else {
      pager.appendChild(h("a", { className: "next", href: "#quiz" }, [
        h("small", { text: "Check yourself →" }), document.createTextNode("Quiz")]));
    }
    viewEl.appendChild(pager);
    return lesson.title;
  }

  function renderBlock(block, lessonNumber) {
    switch (block.type) {
      case "p": return mathText(h("p"), block.text);
      case "math": return displayMath(h("div", { className: "display-math" }), block.tex);
      case "note": return mathText(h("aside", { className: "note" }), block.text);
      case "list": {
        var ul = h("ul");
        block.items.forEach(function (it) { ul.appendChild(mathText(h("li"), it)); });
        return ul;
      }
      case "video": return renderClip(block);
      case "example": return renderExample(course.examples.filter(function (e) { return e.id === block.id; })[0], lessonNumber);
      default: return h("p", { className: "error", text: "Unknown block type: " + block.type });
    }
  }

  // The original continuous overview clips stay in the notes, created only when opened.
  function renderClip(block) {
    var d = h("details", { className: "clip" });
    var sum = h("summary");
    mathText(sum, "Overview animation: " + block.caption.replace(/^ManimGL animation:\s*/, ""));
    d.appendChild(sum);
    d.addEventListener("toggle", function () {
      if (d.open && !d.querySelector("video")) {
        var v = h("video", { controls: "", preload: "metadata", playsinline: "", src: block.src,
                             poster: block.src.replace(/\.mp4$/, ".jpg") });
        v.appendChild(document.createTextNode("Your browser cannot play this MP4 animation."));
        d.appendChild(v);
      }
      if (!d.open) { var v2 = d.querySelector("video"); if (v2) v2.pause(); }
    });
    return d;
  }

  function renderExample(exm, lessonNumber) {
    var id = "ex-" + exm.id;
    var article = h("article", { className: "example", id: id, "aria-labelledby": id + "-title" });
    article.appendChild(h("p", { className: "example-title", id: id + "-title", text: "Worked example · " + exm.title }));
    article.appendChild(mathText(h("p", { className: "example-problem" }), exm.problem));
    var sq = seqList().filter(function (q) { return q.example === exm.id; })[0];
    if (sq) {
      var watch = h("button", { type: "button", className: "btn primary", "data-action": "watch-example", "data-seq": sq.id },
                    [h("span", { "aria-hidden": "true", text: "▶ " }), document.createTextNode("Animate this example")]);
      watch.addEventListener("click", function () {
        selectSequence(sq.id, false);
        replaceHash("#lesson-" + lessonNumber + "/" + sq.id);
        player.wrap.scrollIntoView({ block: "start", behavior: reduceMotion.matches ? "auto" : "smooth" });
        player.nextBtn.focus({ preventScroll: true });
      });
      article.appendChild(h("div", { className: "example-controls" }, [watch]));
    }
    var det = h("details", { className: "written" }, [h("summary", { text: "Written solution (" + exm.steps.length + " steps)" })]);
    var list = h("ol", { className: "steps" });
    exm.steps.forEach(function (step, i) {
      var li = h("li", { "data-step": String(i + 1) });
      li.appendChild(mathText(h("p", { className: "step-text" }), step.text));
      if (step.tex) li.appendChild(flowMath(h("div", { className: "step-math" }), step.tex));
      list.appendChild(li);
    });
    det.appendChild(list);
    det.appendChild(h("p", { className: "answer" }, [h("strong", { text: "Answer: " }), flowMath(h("span", { className: "answer-math" }), exm.answer)]));
    article.appendChild(det);
    return article;
  }

  // ------------------------------------------------------------------ explorer

  var PLOT = { w: 640, h: 340, l: 52, r: 26, t: 24, b: 34 };

  function renderExplorer() {
    var cfg = course.explorer;
    if (!state.explorer) state.explorer = defaults();
    viewEl.appendChild(h("header", { className: "page-head explorer-head" }, [
      h("p", { className: "eyebrow", text: "Practice" }),
      h("h1", { text: cfg.title })
    ]));
    var scope = h("p", { className: "scope" }, [h("strong", { text: "Scope. " })]);
    var scopeText = h("span");
    mathText(scopeText, cfg.scope);
    scope.appendChild(scopeText);
    viewEl.appendChild(scope);

    var svg = s("svg", { id: "plot", viewBox: "0 0 " + PLOT.w + " " + PLOT.h, role: "img",
                         "aria-labelledby": "plot-title plot-desc" });
    var title = s("title", { id: "plot-title" });
    var desc = s("desc", { id: "plot-desc" });
    var grid = s("g", { "class": "grid" });
    var labels = s("g");
    var curve = s("path", { "class": "curve", d: "" });
    var mLine = s("line", { "class": "marker-line" });
    var mDot = s("circle", { "class": "marker-dot", r: "5.5" });
    var zero = s("text", { "class": "zero-note", x: String(PLOT.l + 14), y: String(PLOT.t + 26) });
    zero.textContent = cfg.zero_note;
    [title, desc, grid, labels, curve, mLine, mDot, zero].forEach(function (n) { svg.appendChild(n); });

    var badge = h("span", { className: "class-badge", id: "class-badge" });
    var hint = h("span", { className: "policy", text: "y(t) for 0 ≤ t ≤ " + cfg.t_max });
    var dl = h("dl", { className: "readouts" });
    function readout(label, cls) {
      var dd = h("dd", { className: cls || "" });
      dl.appendChild(h("div", null, [h("dt", { text: label }), dd]));
      return dd;
    }
    var eq = readout("Equation");
    eq.parentNode.className = "wide";
    var roots = readout("Characteristic roots");
    var disc = readout("Discriminant");
    var mark = readout("Time marker", "marker-readout");
    var plotCard = h("section", { className: "plot-card", "aria-label": "Solution graph" },
                     [h("div", { className: "plot-top" }, [badge, hint]), svg, dl]);

    var controls = h("section", { className: "controls", "aria-labelledby": "controls-title" });
    controls.appendChild(h("h2", { id: "controls-title", text: "Parameters" }));
    var inputs = {};
    var outputs = {};
    cfg.sliders.forEach(function (sp) {
      var id = "s-" + sp.key;
      var input = h("input", { type: "range", id: id, min: String(sp.min), max: String(sp.max), step: String(sp.step),
                               value: String(state.explorer[sp.key]), "data-key": sp.key });
      var out = h("output", { "for": id, id: id + "-out" });
      input.addEventListener("input", function () {
        state.explorer[sp.key] = parseFloat(input.value);
        update();
      });
      inputs[sp.key] = input;
      outputs[sp.key] = out;
      controls.appendChild(h("div", { className: "slider-row" }, [h("label", { "for": id, text: sp.label }), out, input]));
    });
    var presetGrid = h("div", { className: "button-grid", role: "group", "aria-label": "Presets" });
    var presetBtns = cfg.presets.map(function (p) {
      var b = h("button", { type: "button", className: "btn", "data-preset": p.id, "aria-pressed": "false", text: p.label });
      b.addEventListener("click", function () {
        state.explorer.a = p.a; state.explorer.b = p.b; state.explorer.c = p.c;
        syncInputs();
        update();
      });
      presetGrid.appendChild(b);
      return { btn: b, p: p };
    });
    controls.appendChild(presetGrid);
    var resetBtn = h("button", { type: "button", className: "btn", id: "reset-btn", text: "Reset" });
    var playBtn = h("button", { type: "button", className: "btn primary", id: "play-btn", "aria-pressed": "false", text: "Play marker" });
    resetBtn.addEventListener("click", function () {
      state.explorer = defaults();
      stopMarker();
      state.marker.t = 0;
      syncInputs();
      update();
    });
    playBtn.addEventListener("click", function () { if (state.marker.playing) stopMarker(); else startMarker(); });
    controls.appendChild(h("div", { className: "button-grid" }, [resetBtn, playBtn]));
    controls.appendChild(h("p", { className: "policy", text: cfg.preset_policy }));
    var live = h("p", { className: "sr-only", "aria-live": "polite", id: "explorer-live" });
    controls.appendChild(live);

    viewEl.appendChild(h("div", { className: "explorer-grid" }, [plotCard, controls]));
    viewEl.appendChild(h("p", { className: "related" }, [
      document.createTextNode("See how the root cases are derived: "),
      h("a", { href: "#lesson-5/damping", text: "the damping derivation (Lesson 5)" }),
      document.createTextNode(".")
    ]));

    ex = { svg: svg, title: title, desc: desc, grid: grid, labels: labels, curve: curve, mLine: mLine, mDot: mDot,
           zero: zero, badge: badge, eq: eq, roots: roots, disc: disc, mark: mark, inputs: inputs, outputs: outputs,
           presetBtns: presetBtns, playBtn: playBtn, live: live, bound: null, lastKind: null, liveTimer: 0 };

    function syncInputs() {
      Object.keys(inputs).forEach(function (k) { inputs[k].value = String(state.explorer[k]); });
    }
    update();
    return cfg.title;
  }

  function defaults() {
    var d = {};
    course.explorer.sliders.forEach(function (sp) { d[sp.key] = sp.default; });
    return d;
  }

  function X(t) { return PLOT.l + (t / course.explorer.t_max) * (PLOT.w - PLOT.l - PLOT.r); }
  function Y(y, B) { return PLOT.t + (1 - (y / B + 1) / 2) * (PLOT.h - PLOT.t - PLOT.b); }

  function trimNum(x) { return M.fmt(x).replace(/\.?0+$/, ""); }

  function drawAxes(B) {
    ex.grid.innerHTML = "";
    ex.labels.innerHTML = "";
    var tMax = course.explorer.t_max;
    [-1, -0.5, 0.5, 1].forEach(function (f) {
      ex.grid.appendChild(s("line", { x1: PLOT.l, x2: PLOT.w - PLOT.r, y1: Y(f * B, B), y2: Y(f * B, B) }));
    });
    [-1, -0.5, 0, 0.5, 1].forEach(function (f) {
      var t = s("text", { "class": "tick-label", x: PLOT.l - 8, y: Y(f * B, B) + 4, "text-anchor": "end" });
      t.textContent = f === 0 ? "0" : trimNum(f * B);
      ex.labels.appendChild(t);
    });
    for (var t = 0; t <= tMax; t++) {
      ex.labels.appendChild(s("line", { "class": "axis", x1: X(t), x2: X(t), y1: Y(0, B) - 4, y2: Y(0, B) + 4 }));
      if (t > 0) {
        var lab = s("text", { "class": "tick-label", x: X(t), y: PLOT.h - PLOT.b + 18, "text-anchor": "middle" });
        lab.textContent = String(t);
        ex.labels.appendChild(lab);
      }
    }
    ex.labels.appendChild(s("line", { "class": "axis", x1: PLOT.l, x2: PLOT.w - PLOT.r + 6, y1: Y(0, B), y2: Y(0, B) }));
    ex.labels.appendChild(s("line", { "class": "axis", x1: PLOT.l, x2: PLOT.l, y1: PLOT.t, y2: PLOT.h - PLOT.b }));
    var tl = s("text", { "class": "axis-label", x: PLOT.w - PLOT.r + 10, y: Y(0, B) + 4 });
    tl.textContent = "t";
    var yl = s("text", { "class": "axis-label", x: PLOT.l + 6, y: PLOT.t - 8 });
    yl.textContent = "y(t)";
    ex.labels.appendChild(tl);
    ex.labels.appendChild(yl);
  }

  function update() {
    if (!ex) return;
    var v = state.explorer;
    var a = v.a, b = v.b, c = v.c, y0 = v.y0, v0 = v.v0;
    var tMax = course.explorer.t_max;
    var pts = M.sample(a, b, c, y0, v0, tMax, 400);
    var maxAbs = 0;
    pts.forEach(function (p) { maxAbs = Math.max(maxAbs, Math.abs(p[1])); });
    var B = M.niceBound(maxAbs);
    if (B !== ex.bound) { ex.bound = B; drawAxes(B); }
    var d = "";
    pts.forEach(function (p, i) { d += (i ? "L" : "M") + X(p[0]).toFixed(2) + " " + Y(p[1], B).toFixed(2); });
    ex.curve.setAttribute("d", d);
    ex.svg.setAttribute("data-bound", String(B));

    var info = M.analyze(a, b, c);
    var label = M.dampingText(a, b, c);
    ex.badge.textContent = label;
    ex.badge.setAttribute("data-kind", info.damping);
    ex.eq.textContent = M.fmt(a) + " y'' + " + M.fmt(b) + " y' + " + M.fmt(c) + " y = 0";
    ex.roots.textContent = M.rootsText(a, b, c);
    ex.disc.textContent = "b² − 4ac = " + M.fmt(b * b - 4 * a * c);
    Object.keys(ex.outputs).forEach(function (k) { ex.outputs[k].textContent = M.fmt(v[k]); });
    ex.presetBtns.forEach(function (pb) {
      var on = pb.p.a === a && pb.p.b === b && pb.p.c === c;
      pb.btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    var isZero = y0 === 0 && v0 === 0;
    ex.zero.style.display = isZero ? "" : "none";
    ex.svg.setAttribute("data-zero", isZero ? "true" : "false");

    ex.title.textContent = "Solution of " + ex.eq.textContent + " with y(0) = " + M.fmt(y0) + ", y'(0) = " + M.fmt(v0);
    ex.desc.textContent = label + ". " + (isZero ? "The curve is the zero solution along the t-axis. " :
      "Largest |y| on the window is " + M.fmt(maxAbs) + ". ") +
      "Horizontal axis t from 0 to " + tMax + "; vertical axis from " + trimNum(-B) + " to " + trimNum(B) + ".";
    if (info.damping !== ex.lastKind) {
      ex.lastKind = info.damping;
      clearTimeout(ex.liveTimer);
      ex.liveTimer = setTimeout(function () { if (ex) ex.live.textContent = label; }, 350);
    }
    drawMarker();
  }

  function drawMarker() {
    if (!ex) return;
    var v = state.explorer;
    var t = state.marker.t;
    var y = M.solution(t, v.a, v.b, v.c, v.y0, v.v0);
    var x = X(t);
    ex.mLine.setAttribute("x1", x); ex.mLine.setAttribute("x2", x);
    ex.mLine.setAttribute("y1", PLOT.t); ex.mLine.setAttribute("y2", PLOT.h - PLOT.b);
    ex.mDot.setAttribute("cx", x.toFixed(2)); ex.mDot.setAttribute("cy", Y(y, ex.bound).toFixed(2));
    ex.mark.textContent = "t = " + M.fmt(t) + "   y(t) = " + M.fmt(y);
  }

  function startMarker() {
    if (!ex) return;
    state.marker.playing = true;
    state.marker.last = 0;
    ex.playBtn.textContent = "Pause marker";
    ex.playBtn.setAttribute("aria-pressed", "true");
    function frame(now) {
      if (!state.marker.playing) return;
      if (state.marker.last) {
        var dt = Math.min(0.1, (now - state.marker.last) / 1000);
        state.marker.t = (state.marker.t + dt) % course.explorer.t_max;
        drawMarker();
      }
      state.marker.last = now;
      state.marker.raf = requestAnimationFrame(frame);
    }
    state.marker.raf = requestAnimationFrame(frame);
  }

  function stopMarker() {
    state.marker.playing = false;
    cancelAnimationFrame(state.marker.raf);
    if (ex) {
      ex.playBtn.textContent = "Play marker";
      ex.playBtn.setAttribute("aria-pressed", "false");
    }
  }

  // ------------------------------------------------------------------ quiz

  var qx = null;

  function renderQuiz() {
    var n = course.quiz.length;
    viewEl.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Practice" }),
      h("h1", { text: "Quiz" }),
      h("p", { className: "summary", text: n + " questions across all six lessons. Pick an answer for instant feedback. " +
        "A wrong answer can be retried; the score counts first tries. Keys A–D also answer." })
    ]));
    var wrap = h("div", { className: "quiz-wrap" });
    var dots = h("ol", { className: "q-dots", "aria-label": "Questions" });
    var dotBtns = course.quiz.map(function (q, i) {
      var b = h("button", { type: "button", text: String(i + 1) });
      b.addEventListener("click", function () { state.quiz.index = i; renderQuestion(); });
      dots.appendChild(h("li", null, [b]));
      return b;
    });
    var score = h("p", { className: "score", role: "status", "aria-live": "polite" });
    wrap.appendChild(h("div", { className: "quiz-meta" }, [dots, score]));

    var card = h("section", { className: "question", "aria-labelledby": "q-prompt" });
    var topic = h("p", { className: "topic" });
    var prompt = h("p", { className: "prompt", id: "q-prompt" });
    var choices = h("ul", { className: "choices" });
    var feedback = h("div", { className: "feedback", role: "status", "aria-live": "polite", hidden: "" });
    var prevBtn = h("button", { type: "button", className: "btn", text: "← Previous" });
    var retryBtn = h("button", { type: "button", className: "btn", text: "Try again" });
    var nextBtn = h("button", { type: "button", className: "btn primary", text: "Next →" });
    var resetBtn = h("button", { type: "button", className: "btn", text: "Reset quiz" });
    prevBtn.addEventListener("click", function () { if (state.quiz.index > 0) { state.quiz.index--; renderQuestion(); } });
    nextBtn.addEventListener("click", function () { if (state.quiz.index < n - 1) { state.quiz.index++; renderQuestion(); } });
    retryBtn.addEventListener("click", retry);
    resetBtn.addEventListener("click", function () {
      state.quiz = { index: 0, answers: {} };
      renderQuestion();
      prompt.focus();
    });
    card.appendChild(topic);
    card.appendChild(prompt);
    card.appendChild(choices);
    card.appendChild(feedback);
    card.appendChild(h("div", { className: "quiz-controls" },
      [prevBtn, retryBtn, h("span", { className: "spacer" }), resetBtn, nextBtn]));
    wrap.appendChild(card);
    viewEl.appendChild(wrap);
    prompt.setAttribute("tabindex", "-1");
    qx = { dots: dotBtns, score: score, topic: topic, prompt: prompt, choices: choices, feedback: feedback,
           prevBtn: prevBtn, retryBtn: retryBtn, nextBtn: nextBtn };
    renderQuestion();
    return "Quiz";
  }

  function renderQuestion() {
    var n = course.quiz.length;
    var q = course.quiz[state.quiz.index];
    var ans = state.quiz.answers[q.id];
    var locked = !!(ans && ans.choice !== null);
    qx.topic.textContent = "Question " + (state.quiz.index + 1) + " of " + n + " · " + q.topic;
    mathText(qx.prompt, q.prompt);
    qx.choices.innerHTML = "";
    q.choices.forEach(function (choice, i) {
      var btn = h("button", { type: "button", className: "choice", "data-index": String(i) }, [
        h("span", { className: "letter", text: "ABCD"[i] + "." })
      ]);
      var body = h("span");
      mathText(body, choice);
      btn.appendChild(body);
      if (locked) {
        btn.setAttribute("aria-disabled", "true");
        btn.setAttribute("data-state", i === ans.choice ? (i === q.answer ? "correct" : "wrong") : "locked");
      }
      btn.addEventListener("click", function () { answer(i); });
      qx.choices.appendChild(h("li", null, [btn]));
    });
    if (locked) {
      var ok = ans.choice === q.answer;
      qx.feedback.className = "feedback " + (ok ? "correct" : "wrong");
      qx.feedback.innerHTML = "";
      qx.feedback.appendChild(h("strong", { text: ok ? "Correct" : "Not quite" }));
      qx.feedback.appendChild(mathText(h("span"), q.feedback[ans.choice]));
      qx.feedback.hidden = false;
    } else {
      qx.feedback.hidden = true;
      qx.feedback.innerHTML = "";
    }
    qx.prevBtn.disabled = state.quiz.index === 0;
    qx.nextBtn.disabled = state.quiz.index === n - 1;
    qx.retryBtn.disabled = !(locked && ans.choice !== q.answer);
    course.quiz.forEach(function (qq, i) {
      var a = state.quiz.answers[qq.id];
      var st = !a ? "none" : (a.choice === null ? "retrying" : (a.choice === qq.answer ? "correct" : "wrong"));
      qx.dots[i].setAttribute("data-status", st);
      qx.dots[i].setAttribute("aria-label", "Question " + (i + 1) + (st === "none" ? "" : ", " + st));
      if (i === state.quiz.index) qx.dots[i].setAttribute("aria-current", "step");
      else qx.dots[i].removeAttribute("aria-current");
    });
    var answered = Object.keys(state.quiz.answers).length;
    var first = Object.keys(state.quiz.answers).filter(function (k) { return state.quiz.answers[k].firstCorrect; }).length;
    qx.score.textContent = "First-try correct: " + first + " / " + answered + " answered" +
      (answered === n ? " · finished (" + first + "/" + n + ")" : "");
  }

  function answer(i) {
    var q = course.quiz[state.quiz.index];
    var ans = state.quiz.answers[q.id];
    if (ans && ans.choice !== null) return;           // locked until "Try again"
    if (!ans) ans = state.quiz.answers[q.id] = { choice: null, attempts: 0, firstCorrect: i === q.answer };
    ans.choice = i;
    ans.attempts++;
    renderQuestion();
    var btn = qx.choices.querySelector('[data-index="' + i + '"]');
    if (btn) btn.focus();
  }

  function retry() {
    var q = course.quiz[state.quiz.index];
    var ans = state.quiz.answers[q.id];
    if (ans && ans.choice !== null && ans.choice !== q.answer) {
      ans.choice = null;
      renderQuestion();
      var first = qx.choices.querySelector("button");
      if (first) first.focus();
    }
  }

  function quizKeys(e) {
    if (!qx || !document.body.contains(qx.prompt)) return;
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var tag = (e.target && e.target.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    var idx = "abcd".indexOf((e.key || "").toLowerCase());
    if (idx >= 0 && idx < course.quiz[state.quiz.index].choices.length) {
      e.preventDefault();
      answer(idx);
    }
  }

  // ------------------------------------------------------------------ further reading

  function renderReading() {
    viewEl.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Further reading" }),
      h("h1", { text: "Where to read more" }),
      h("p", { className: "summary", text: "The lessons here are original summaries. These MIT OpenCourseWare materials develop the same ideas in more depth." })
    ]));
    var list = h("ul", { className: "reading-list" });
    course.references.forEach(function (r) {
      list.appendChild(h("li", null, [h("a", { href: r.url, rel: "noopener", target: "_blank", text: r.title })]));
    });
    viewEl.appendChild(list);
    var sec = h("section", { className: "lesson-section" }, [
      h("h2", { text: "Also in this guide" }),
      h("p", { text: "A native ManimGL version of this guide uses the same lessons, explorer and quiz. See the project README for how to launch it." })
    ]);
    viewEl.appendChild(sec);
    return "Further reading";
  }

  // Read-only hook for automated QA.
  window.SecondOrderGuide = {
    snapshot: function () {
      var P = player;
      return JSON.parse(JSON.stringify({
        examples: state.examples, explorer: state.explorer,
        marker: { t: state.marker.t, playing: state.marker.playing }, quiz: state.quiz,
        steps: state.steps, theme: document.documentElement.getAttribute("data-theme"),
        themeStorageOk: themeStorageOk,
        player: { seq: P.seq ? P.seq.id : null, k: P.k, playing: P.playing, target: P.target,
                  still: P.still ? P.still.getAttribute("src") : null,
                  video: P.video ? P.video.getAttribute("src") : null,
                  videoVisible: P.stage ? P.stage.classList.contains("video-on") : false,
                  notice: P.notice, reduceMotion: !!reduceMotion.matches }
      }));
    }
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
