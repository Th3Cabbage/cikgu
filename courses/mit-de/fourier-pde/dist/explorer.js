/*
 * Fourier series, heat and wave explorer.
 * Maths comes from window.StudyMath (coefficients, target, partialSum, heatCoeffs, heatStart, heat,
 * pluckCoeffs, pluckShape, wave, waveDAlembert).
 * Saved state: state.explorer = {mode, fn, N, start, t, pluck, tw}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var PI = Math.PI;
  var NUM_KEYS = ["N", "t", "pluck", "tw"];
  var raf = 0;

  function ids(list) { return (list || []).map(function (m) { return m.id; }); }
  function defaults(config) {
    var out = { mode: config.defaultMode || config.modes[0].id, fn: config.functions[0].id, start: config.heatStarts[0].id };
    NUM_KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config || !Array.isArray(config.modes)) return out;
    if (typeof saved.mode === "string" && ids(config.modes).indexOf(saved.mode) >= 0) out.mode = saved.mode;
    if (typeof saved.fn === "string" && ids(config.functions).indexOf(saved.fn) >= 0) out.fn = saved.fn;
    if (typeof saved.start === "string" && ids(config.heatStarts).indexOf(saved.start) >= 0) out.start = saved.start;
    NUM_KEYS.forEach(function (k) {
      var v = saved[k], c = config[k];
      if (typeof v === "number" && isFinite(v) && v >= c.min - 1e-9 && v <= c.max + 1e-9) out[k] = k === "N" ? Math.round(v) : v;
    });
    return out;
  }
  function stop() {
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
  }

  function num(v) {
    if (!isFinite(v)) return v > 0 ? "∞" : v < 0 ? "−∞" : "NaN";
    if (Math.abs(v) < 5e-10) return "0";
    var r = Math.abs(v) >= 1000 ? v.toExponential(2) : Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 0.1 ? +v.toFixed(3) + "" : +v.toPrecision(3) + "";
    return String(r).replace("-", "−");
  }
  function sci(v) { return v === 0 ? "0" : v.toExponential(2).replace("e-", "e−").replace("e+", "e"); }
  var uid = 0;
  var MUTED = "var(--muted)";

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var clipBase = "fp-clip-" + (++uid);
    var playing = null, lastTs = 0;
    var reduced = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Fourier series, heat and waves" }),
      ctx.mathText(h("p", { className: "lede" }), "Build a function from sines and cosines, watch the modes of $u_t = u_{xx}$ die at the rate $e^{-k^2\\pi^2 t}$, and compare a plucked string's sine series with d'Alembert's travelling pieces.")
    ]));

    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text, label, c, fmt) {
      var id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      inp.setAttribute("aria-label", label);
      var out = h("output", { "for": id, text: fmt ? fmt(st[key]) : num(st[key]) });
      inp.addEventListener("input", function () {
        var v = parseFloat(inp.value);
        if (!isFinite(v)) return;
        st[key] = key === "N" ? Math.round(v) : v;
        if (playing && (key === "t" || key === "tw")) pause();
        update(); ctx.save();
        ctx.announce(label + " " + (fmt ? fmt(st[key]) : num(st[key])));
      });
      inputs[key] = inp; outputs[key] = { el: out, fmt: fmt || num };
      var row = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
      rows[key] = row;
      return row;
    }

    function radioSet(name, legendText, list, key, groupKey) {
      var box = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
        h("legend", { text: legendText, style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
      ]);
      var map = {};
      list.forEach(function (m) {
        var id = "ex-" + name + "-" + m.id;
        var r = h("input", { type: "radio", name: "ex-" + name, id: id, value: m.id });
        r.checked = st[key] === m.id;
        r.addEventListener("change", function () {
          if (!r.checked) return;
          st[key] = m.id; pause(); update(); ctx.save();
          ctx.announce(legendText + ": " + m.label);
        });
        map[m.id] = r;
        box.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
      });
      return { box: box, map: map };
    }

    // N slider must come first in the DOM (shared QA moves the first range input).
    var rN = slider("N", "Terms $N$", "Number of terms N", config.N);
    var rT = slider("t", "Time $t$", "Heat time t", config.t, function (v) { return num(v); });
    var rP = slider("pluck", "Pluck position $p$", "Pluck position p", config.pluck);
    var rW = slider("tw", "Time $t$", "Wave time t", config.tw);

    var fnSet = radioSet("fn", "Function", config.functions, "fn");
    var stSet = radioSet("start", "Initial temperature", config.heatStarts, "start");
    var modeSet = radioSet("mode", "Mode", config.modes, "mode");

    var btnPlay = h("button", { type: "button", className: "btn small", text: "Play", onclick: function () {
      if (playing) pause(); else play();
    } });
    var playRow = h("div", { className: "presets" }, [btnPlay]);
    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        pause();
        if (p.mode && modeSet.map[p.mode]) st.mode = p.mode;
        if (p.fn && fnSet.map[p.fn]) st.fn = p.fn;
        if (p.start && stSet.map[p.start]) st.start = p.start;
        NUM_KEYS.forEach(function (k) { if (typeof p[k] === "number" && isFinite(p[k])) st[k] = p[k]; });
        ctx.mathText(presetNote, p.note || "");
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var controls = h("div", null, [
      h("h2", { text: "Controls" }),
      rN, fnSet.box, rT, stSet.box, rP, rW, playRow, modeSet.box, presets
    ]);

    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }

    // ---- plot scaffolding ----
    var W = 480, H = 280, L = 42, Rr = 12, Tp = 10, Bt = 26;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", style: "width:100%;height:auto",
      "aria-label": "Plot of the current mode." });
    var legend = h("div", { className: "legend" });
    var cap = h("p", { className: "plot-note" });
    var plotTitle = h("h3", { text: "Plot" });
    var plotBox = h("div", { className: "plot-box" }, [plotTitle, svg, legend, cap]);

    var bsvg = s("svg", { viewBox: "0 0 " + W + " 200", role: "img", style: "width:100%;height:auto",
      "aria-label": "Bar chart of the absolute values of the Fourier coefficients on a logarithmic axis." });
    var barBox = h("div", { className: "plot-box" }, [h("h3", { text: "Coefficient sizes |a_k| and |b_k|" }), bsvg,
      h("div", { className: "legend" }, [h("span", null, [sw("var(--blue)"), "|a_k| (cosines)"]), h("span", null, [sw("var(--orange)"), "|b_k| (sines)"])]),
      h("p", { className: "plot-note", text: "Log scale from 1e−4 to 2. Zero coefficients have no bar." })]);

    var formulaBox = h("div", { className: "readout" });
    var gibbsBox = h("p", { className: "plot-note", style: "font-weight:600" });
    var readBox = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [plotBox, gibbsBox, presetNote, formulaBox, readBox, barBox])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function setShown(el, on) { el.hidden = !on; el.style.display = on ? "" : "none"; }
    function legendSet(items) {
      clear(legend);
      items.forEach(function (it) { legend.appendChild(h("span", null, [sw(it[0]), it[1]])); });
    }

    // frame(): axes, grid, clip; returns coordinate mappers
    function frame(g, x0, x1, y0, y1, xt, yt, tag) {
      clear(g);
      var cid = clipBase + tag;
      var defs = s("defs"), cp = s("clipPath", { id: cid });
      cp.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H - Tp - Bt }));
      defs.appendChild(cp); g.appendChild(defs);
      var X = function (x) { return L + (W - L - Rr) * (x - x0) / (x1 - x0); };
      var Y = function (y) { return Tp + (H - Tp - Bt) * (y1 - y) / (y1 - y0); };
      xt.forEach(function (t) {
        g.appendChild(s("line", { x1: X(t[0]), y1: Tp, x2: X(t[0]), y2: H - Bt, "class": Math.abs(t[0]) < 1e-9 ? "p-axis" : "p-grid" }));
        g.appendChild(s("text", { x: X(t[0]), y: H - Bt + 14, "text-anchor": "middle", text: t[1] }));
      });
      yt.forEach(function (t) {
        g.appendChild(s("line", { x1: L, y1: Y(t[0]), x2: W - Rr, y2: Y(t[0]), "class": Math.abs(t[0]) < 1e-9 ? "p-axis" : "p-grid" }));
        g.appendChild(s("text", { x: L - 4, y: Y(t[0]) + 4, "text-anchor": "end", text: t[1] }));
      });
      var layer = s("g", { "clip-path": "url(#" + cid + ")" });
      g.appendChild(layer);
      return { X: X, Y: Y, layer: layer };
    }
    function curve(M, n, xa, xb, f, style) {
      var d = "", i;
      for (i = 0; i <= n; i++) {
        var x = xa + (xb - xa) * i / n, y = f(x);
        d += (i ? "L" : "M") + M.X(x).toFixed(1) + " " + M.Y(y).toFixed(1) + " ";
      }
      M.layer.appendChild(s("path", { d: d, fill: "none", style: style + ";stroke-linejoin:round" }));
    }
    function ticks(list, labels) { return list.map(function (v, i) { return [v, labels ? labels[i] : num(v)]; }); }
    var PI_T = ticks([-PI, -PI / 2, 0, PI / 2, PI], ["−π", "−π/2", "0", "π/2", "π"]);

    // ---- series ----
    function formulaTex(fn) {
      if (fn === "square") return "f = \\begin{cases} 1 & 0<x<\\pi \\\\ -1 & -\\pi<x<0 \\end{cases}:\\quad b_k = \\frac{4}{\\pi k}\\ (k \\text{ odd}),\\quad a_k = 0,\\quad b_k = 0\\ (k \\text{ even})";
      if (fn === "ramp") return "f = |x|:\\quad a_0 = \\frac{\\pi}{2},\\quad a_k = -\\frac{4}{\\pi k^2}\\ (k \\text{ odd}),\\quad a_k = 0\\ (k \\text{ even}),\\quad b_k = 0";
      if (fn === "saw") return "f = x:\\quad b_k = \\frac{2(-1)^{k+1}}{k},\\quad a_k = 0";
      return "f = \\delta(x):\\quad a_0 = \\frac{1}{2\\pi},\\quad a_k = \\frac{1}{\\pi},\\quad b_k = 0";
    }

    function drawSeries() {
      var fn = st.fn, N = st.N, c = SM.coefficients(fn, N), notice = "";
      var y0, y1, yt;
      if (fn === "square") { y0 = -1.4; y1 = 1.4; yt = ticks([-1, 0, 1]); }
      else if (fn === "saw") { y0 = -3.5; y1 = 3.5; yt = ticks([-3, -2, -1, 0, 1, 2, 3]); }
      else if (fn === "ramp") { y0 = -0.2; y1 = 3.4; yt = ticks([0, 1, 2, 3]); }
      else {
        var peak = SM.partialSum(c, 0);
        var top = Math.max(1, peak * 1.1);
        if (top > 25) { top = 25; notice = " Notice: the peak S_N(0) = " + num(peak) + " is above the window and is clipped at 25."; }
        y0 = -top * 0.15; y1 = top;
        var st2 = niceStep(top);
        yt = []; for (var v = 0; v <= top + 1e-9; v += st2) yt.push([v, num(v)]);
      }
      var M = frame(svg, -PI, PI, y0, y1, PI_T, yt, "a");
      if (fn === "delta") {
        var xa = M.X(0), yb = M.Y(0), yt0 = M.Y(y1 * 0.92);
        M.layer.appendChild(s("line", { x1: xa, y1: yb, x2: xa, y2: yt0, style: "stroke:" + MUTED + ";stroke-width:2" }));
        M.layer.appendChild(s("polygon", { points: (xa - 5) + "," + (yt0 + 9) + " " + xa + "," + yt0 + " " + (xa + 5) + "," + (yt0 + 9), style: "fill:" + MUTED }));
      } else {
        curve(M, 600, -PI, PI, function (x) { return SM.target(fn, x); }, "stroke:" + MUTED + ";stroke-width:1.8;opacity:0.8");
      }
      curve(M, 600, -PI, PI, function (x) { return SM.partialSum(c, x); }, "stroke:var(--teal);stroke-width:2.2");
      legendSet([[MUTED, fn === "delta" ? "δ(x) (arrow at 0)" : "f(x)"], ["var(--teal)", "S_" + N + "(x)"]]);
      plotTitle.textContent = "Partial sum S_" + N + " on [−π, π]";
      svg.setAttribute("aria-label", "Plot of the " + fn + " function and its partial sum with " + N + " terms.");
      cap.textContent = "The partial sum uses terms up to k = " + N + "." + notice;

      clear(formulaBox);
      formulaBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), formulaTex(fn)));

      if (fn === "square") {
        var mx = -Infinity, i;
        for (i = 1; i < 3000; i++) mx = Math.max(mx, SM.partialSum(c, PI * i / 3000));
        gibbsBox.textContent = "Overshoot: max S_" + N + " on (0, π) = " + num(mx) + " (jump height 2 from −1 to 1; Gibbs limit ≈ 1.179).";
        setShown(gibbsBox, true);
      } else setShown(gibbsBox, false);
      drawBars(c, N);
    }
    function niceStep(top) {
      var mag = Math.pow(10, Math.floor(Math.log(top / 4) / Math.LN10)), m = [1, 2, 5, 10], i;
      for (i = 0; i < m.length; i++) if (m[i] * mag >= top / 4) return m[i] * mag;
      return 10 * mag;
    }

    function drawBars(c, N) {
      clear(bsvg);
      var BH = 200, lo = -4, hi = Math.log(2) / Math.LN10;
      var pw = W - L - Rr, ph = BH - Tp - Bt;
      var Y = function (v) { return Tp + ph * (hi - Math.log(v) / Math.LN10) / (hi - lo); };
      var X = function (k) { return L + pw * (k - 0.5) / N; };
      [1e-4, 1e-3, 1e-2, 1e-1, 1].forEach(function (v) {
        bsvg.appendChild(s("line", { x1: L, y1: Y(v), x2: W - Rr, y2: Y(v), "class": "p-grid" }));
        bsvg.appendChild(s("text", { x: L - 4, y: Y(v) + 4, "text-anchor": "end", text: v === 1 ? "1" : "1e" + Math.round(Math.log(v) / Math.LN10).toString().replace("-", "−") }));
      });
      var step = N <= 12 ? 1 : N <= 30 ? 5 : 10, k;
      for (k = 1; k <= N; k++) {
        if (k === 1 || k % step === 0) bsvg.appendChild(s("text", { x: X(k), y: BH - Bt + 14, "text-anchor": "middle", text: String(k) }));
      }
      bsvg.appendChild(s("text", { x: W - Rr, y: BH - 2, "text-anchor": "end", text: "k" }));
      var bw = pw / N * 0.4, base = Y(1e-4);
      for (k = 1; k <= N; k++) {
        [["a", "var(--blue)", -bw], ["b", "var(--orange)", 0]].forEach(function (q) {
          var v = Math.abs(c[q[0]][k - 1]);
          if (!(v >= 1e-4) || v > 2) return;
          var yy = Y(v);
          bsvg.appendChild(s("rect", { x: X(k) + q[2], y: yy, width: bw, height: Math.max(0.5, base - yy), style: "fill:" + q[1] }));
        });
      }
      bsvg.appendChild(s("line", { x1: L, y1: base, x2: W - Rr, y2: base, "class": "p-axis" }));
    }

    // ---- heat ----
    function drawHeat() {
      var B = SM.heatCoeffs(st.start, 60), t = st.t;
      var y0 = st.start === "two" ? -0.2 : 0, y1 = st.start === "two" ? 1.6 : 1.3;
      var yt = st.start === "two" ? ticks([0, 0.5, 1, 1.5]) : ticks([0, 0.5, 1]);
      var M = frame(svg, 0, 1, y0, y1, ticks([0, 0.25, 0.5, 0.75, 1]), yt, "h");
      curve(M, 300, 0, 1, function (x) { return SM.heatStart(st.start, x); }, "stroke:" + MUTED + ";stroke-width:1.8;opacity:0.8");
      curve(M, 300, 0, 1, function (x) { return SM.heat(B, t, x); }, "stroke:var(--teal);stroke-width:2.2");
      legendSet([[MUTED, "u(0, x)"], ["var(--teal)", "u(t, x), t = " + num(t)]]);
      plotTitle.textContent = "Heat equation, t = " + num(t);
      svg.setAttribute("aria-label", "Temperature profile at time " + num(t) + " compared with the initial profile.");
      cap.textContent = "60 sine modes. The zero ends stay at temperature 0; higher modes decay faster.";
      clear(readBox);
      readBox.appendChild(h("h3", { text: "First modes" }));
      var k;
      for (k = 1; k <= 3; k++) {
        readBox.appendChild(h("p", { style: "margin:2px 0", text: "B_" + k + " = " + num(B[k - 1]) + ",  decay e^(−" + k * k + "π²t) = " + num(Math.exp(-k * k * PI * PI * t)) }));
      }
    }

    // ---- wave ----
    function drawWave() {
      var p = st.pluck, t = st.tw, d = SM.pluckCoeffs(p, 80);
      var M = frame(svg, 0, PI, -1.2, 1.2, ticks([0, PI / 2, PI], ["0", "π/2", "π"]), ticks([-1, -0.5, 0, 0.5, 1]), "w");
      curve(M, 300, 0, PI, function (x) { return SM.pluckShape(p, x); }, "stroke:" + MUTED + ";stroke-width:1.6;opacity:0.8");
      curve(M, 300, 0, PI, function (x) { return SM.wave(d, t, x); }, "stroke:var(--teal);stroke-width:2.4");
      curve(M, 300, 0, PI, function (x) { return SM.waveDAlembert(p, t, x); }, "stroke:var(--orange);stroke-width:2;stroke-dasharray:6 4");
      legendSet([[MUTED, "initial pluck"], ["var(--teal)", "sine series (80 modes)"], ["var(--orange)", "d'Alembert"]]);
      plotTitle.textContent = "Plucked string, t = " + num(t);
      svg.setAttribute("aria-label", "String shape at time " + num(t) + ": sine series and d'Alembert solution.");
      cap.textContent = "Pluck of height 1 at x = " + num(p) + ", released from rest, c = 1.";
      var mx = 0, i;
      for (i = 0; i < 200; i++) {
        var x = PI * (i + 0.5) / 200;
        mx = Math.max(mx, Math.abs(SM.wave(d, t, x) - SM.waveDAlembert(p, t, x)));
      }
      clear(readBox);
      readBox.appendChild(h("h3", { text: "Coefficients and comparison" }));
      readBox.appendChild(h("p", { style: "margin:2px 0", text: "d_1 = " + num(d[0]) + ", d_2 = " + num(d[1]) + ", d_3 = " + num(d[2]) + ", d_4 = " + num(d[3]) }));
      readBox.appendChild(h("p", { style: "margin:2px 0", text: "max difference series − d'Alembert over 200 points = " + sci(mx) }));
    }

    // ---- animation ----
    function play() {
      if (st.mode !== "heat" && st.mode !== "wave") return;
      var key = st.mode === "heat" ? "t" : "tw", c = config[key];
      if (st[key] >= c.max - 1e-9) { st[key] = c.min; }
      playing = key; lastTs = 0; btnPlay.textContent = "Pause";
      ctx.announce("Animation started");
      raf = requestAnimationFrame(tick);
    }
    function pause() {
      var was = playing;
      playing = null; stop();
      btnPlay.textContent = "Play";
      if (was) ctx.announce("Animation paused");
    }
    function tick(ts) {
      if (!playing) return;
      var key = playing, c = config[key];
      if (lastTs) {
        var dt = Math.min(0.1, (ts - lastTs) / 1000);
        st[key] = Math.min(c.max, st[key] + (c.max - c.min) * dt / 6);
        inputs[key].value = st[key];
        update();
        if (st[key] >= c.max - 1e-9) { pause(); ctx.save(); return; }
      }
      lastTs = ts;
      raf = requestAnimationFrame(tick);
    }

    function update() {
      var m = st.mode;
      NUM_KEYS.forEach(function (k) { outputs[k].el.textContent = outputs[k].fmt(st[k]); inputs[k].value = st[k]; });
      modeSet.map[m].checked = true;
      fnSet.map[st.fn].checked = true;
      stSet.map[st.start].checked = true;
      setShown(rows.N, m === "series"); setShown(fnSet.box, m === "series");
      setShown(rows.t, m === "heat"); setShown(stSet.box, m === "heat");
      setShown(rows.pluck, m === "wave"); setShown(rows.tw, m === "wave");
      setShown(playRow, m !== "series");
      setShown(barBox, m === "series");
      if (m === "series") { drawSeries(); }
      else {
        setShown(gibbsBox, false); clear(formulaBox);
        if (m === "heat") drawHeat(); else drawWave();
      }
      if (m !== "series") formulaBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
        m === "heat" ? "u(t,x) = \\sum_k B_k\\, e^{-k^2\\pi^2 t}\\sin k\\pi x" : "u(t,x) = \\sum_n d_n \\cos nt\\,\\sin nx = \\tfrac12\\big(u_0(x-t) + u_0(x+t)\\big)"));
      setShown(readBox, m !== "series");
    }
    // reduced motion: never autoplay (Play only starts on a click); keep the flag for clarity
    if (reduced) btnPlay.title = "Animation plays only when you press Play";
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
