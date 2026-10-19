// Cikgu library pages: theme toggle, and (on a course page) a read-only summary of the progress each
// lecture has saved in this browser. Lecture data is read with the same validation the lectures use;
// nothing here writes or resets lecture progress. The pages work without this script.
(function () {
  "use strict";
  var THEME_KEY = "cikgu-site-theme";
  var root = document.documentElement;

  var btn = document.getElementById("theme-toggle");
  function showTheme(t) {
    root.setAttribute("data-theme", t);
    btn.setAttribute("aria-pressed", t === "dark" ? "true" : "false");
    btn.textContent = t === "dark" ? "Light theme" : "Dark theme";
  }
  if (btn) {
    btn.hidden = false;
    showTheme(root.getAttribute("data-theme") === "dark" ? "dark" : "light");
    btn.addEventListener("click", function () {
      var t = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      showTheme(t);
      try { window.localStorage.setItem(THEME_KEY, t); } catch (e) { /* storage blocked: theme lasts for this page */ }
    });
  }

  var dataEl = document.getElementById("cikgu-data");
  if (!dataEl) return;
  var data;
  try { data = JSON.parse(dataEl.textContent); } catch (e) { return; }

  function read(key) {
    var raw = window.localStorage.getItem(key);   // may throw if storage is blocked
    if (!raw) return null;
    try { var d = JSON.parse(raw); return d && typeof d === "object" && d.v === 1 ? d : null; } catch (e) { return null; }
  }
  function obj(o) { return o && typeof o === "object" && !Array.isArray(o) ? o : {}; }

  function summarize(lec, d) {
    var reachedMap = obj(d.reached), quizMap = obj(d.quiz);
    var total = 0, seen = 0, firstOpen = null;
    lec.seqs.forEach(function (s) {
      var k = reachedMap[s.id];
      k = Number.isInteger(k) && k >= 0 && k <= s.steps ? k : 0;
      total += s.steps; seen += k;
      if (k < s.steps && (firstOpen === null || s.section < firstOpen)) firstOpen = s.section;
    });
    var answered = 0;
    lec.quiz.forEach(function (q) {
      var e = quizMap[q.id];
      if (!e || typeof e !== "object" || !Array.isArray(e.tried)) return;
      var ok = Number.isInteger(e.first) && e.first >= 0 && e.first < q.choices && e.tried[0] === e.first;
      if (ok) answered++;
    });
    return { total: total, seen: seen, firstOpen: firstOpen, answered: answered, quiz: lec.quiz.length };
  }

  var blocked = false;
  data.lectures.forEach(function (lec) {
    var item = document.querySelector('[data-lecture="' + lec.slug + '"]');
    if (!item) return;
    var d;
    try { d = read(lec.storeKey); } catch (e) { blocked = true; return; }
    if (!d) return;
    var s = summarize(lec, d);
    if (s.seen === 0 && s.answered === 0) return;
    var p = item.querySelector("[data-progress]");
    p.textContent = "Saved in this browser: " + s.seen + " of " + s.total + " animation steps seen · " +
      s.answered + " of " + s.quiz + " quiz questions answered";
    p.hidden = false;
    var a = item.querySelector("[data-continue]");
    var label, hash;
    if (s.firstOpen !== null) { label = "Continue at section " + s.firstOpen; hash = "#s" + s.firstOpen; }
    else if (s.answered < s.quiz) { label = "Continue to the quiz"; hash = "#quiz"; }
    else { label = "Review lecture"; hash = ""; }
    a.setAttribute("href", lec.slug + "/" + hash);
    a.querySelector("[data-label]").textContent = label;
  });
  if (blocked) {
    var note = document.getElementById("progress-note");
    note.textContent = "This browser is blocking site storage, so saved lecture progress cannot be shown here or kept between visits.";
    note.hidden = false;
  }
})();
