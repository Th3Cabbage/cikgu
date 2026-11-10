// Apply the saved theme before first paint (the calm light theme is the default).
(function () {
  try {
    var raw = window.localStorage.getItem("phase-plane-v1");
    var t = raw ? JSON.parse(raw).theme : null;
    if (t === "dark" || t === "light") document.documentElement.setAttribute("data-theme", t);
  } catch (e) { /* storage blocked or corrupt: keep the default */ }
})();
