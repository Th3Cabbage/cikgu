// Cikgu site course bar: injected into each lecture by site/build.mjs. The bar's links are static
// HTML and work without this script. This script only (1) reports how much of the non-sticky bar is
// still on screen as --cikgu-cb-vis, so the lecture's sticky side panels fit the viewport, and
// (2) explains in the optional tutor panel that chat is not available on this static site.
(function () {
  "use strict";
  var root = document.documentElement;
  var bar = document.querySelector(".cikgu-cb");
  if (!bar) return;

  var queued = false;
  function measure() {
    queued = false;
    var vis = Math.max(0, Math.round(bar.getBoundingClientRect().bottom));
    root.style.setProperty("--cikgu-cb-vis", vis + "px");
  }
  function queue() {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(measure);
  }
  measure();
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);

  // Tutor panel (Control Bootcamp lectures only). The app builds it after loading the course.
  var tutor = document.getElementById("tutor");
  if (!tutor || !window.MutationObserver) return;
  var OFF_LABEL = "not on this site";

  function note() {
    var box = document.createElement("div");
    box.className = "cikgu-tutor-note";
    box.setAttribute("role", "note");
    var p1 = document.createElement("p");
    p1.textContent = "Ask GPT chat is not available on this study site. The lessons, animations, explorer and quiz all work here without it.";
    var p2 = document.createElement("p");
    p2.textContent = "The chat is an optional extra for the single-lecture version of this guide, run on a computer that has its own OpenAI API key set up.";
    box.appendChild(p1);
    box.appendChild(p2);
    return box;
  }

  function adapt() {
    var setup = tutor.querySelector(".tutor-setup");
    if (setup && !tutor.querySelector(".cikgu-tutor-note")) setup.parentNode.insertBefore(note(), setup.nextSibling);
    var status = tutor.querySelector(".tutor-status");
    if (status && status.getAttribute("data-state") !== "ready" && status.textContent !== OFF_LABEL) status.textContent = OFF_LABEL;
  }
  new MutationObserver(adapt).observe(tutor, { childList: true, subtree: true, characterData: true });
  adapt();
})();
