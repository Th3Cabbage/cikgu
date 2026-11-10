/*
 * Applications explorer (Unit 12): the tumbling box on a sphere, predator-prey cycles, and the
 * Lorenz attractor with two nearby starts. Trajectories are computed by RK4 (window.StudyMath)
 * and drawn progressively ("comet") with Play / Pause / Show all.
 * Saved state: state.explorer = {mode, rho, eps, tEnd, axis, perturb, mu1, mu2, eta1, eta2}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var NUM = ["eps", "tEnd", "perturb", "mu1", "mu2", "eta1", "eta2"];
  var raf = 0;

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function defaults(config) {
    var out = { mode: config.defaultMode || "lorenz", rho: config.rho.default, axis: config.axis.default };
    NUM.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config) return out;
    if (config.modes.some(function (m) { return m.id === saved.mode; })) out.mode = saved.mode;
    if (config.rho.options.indexOf(saved.rho) >= 0) out.rho = saved.rho;
    if (config.axis.options.indexOf(saved.axis) >= 0) out.axis = saved.axis;
    NUM.forEach(function (k) {
      var v = saved[k], c = config[k];
      if (typeof v === "number" && isFinite(v) && v >= c.min - 1e-9 && v <= c.max + 1e-9) out[k] = snap(v, c);
    });
    return out;
  }
  function stop() { if (raf) { cancelAnimationFrame(raf); raf = 0; } }

  function num(v, p) {
    if (!isFinite(v)) return "–";
    if (v === 0) return "0";
    var a = Math.abs(v);
    return (a >= 1e5 || a < 1e-3 ? v.toExponential((p || 3) - 1) : String(+v.toPrecision(p || 4))).replace("-", "−");
  }
  function reduced() { return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches; }

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var data = null, shown = 1, playing = false, lastTs = 0;

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Three famous nonlinear systems" }),
      ctx.mathText(h("p", { className: "lede" }), "Run the tumbling box, the predator-prey cycle or the Lorenz attractor. Press Play to watch the solution being drawn; change the parameters and compare. For Lorenz, a second start a distance $10^{k}$ away shows how fast nearby solutions separate.")
    ]));

    // ---------------- controls
    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text, label, fmt) {
      var c = config[key], id = "ap-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      inp.setAttribute("aria-label", label);
      var out = h("output", { "for": id, text: fmt(st[key]) });
      inp.addEventListener("input", function () {
        st[key] = snap(parseFloat(inp.value), c); out.textContent = fmt(st[key]);
        compute(); ctx.save(); ctx.announce(label + " " + fmt(st[key]));
      });
      inputs[key] = inp; outputs[key] = out;
      rows[key] = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
      return rows[key];
    }
    function selectRow(id, text, opts, value, onChange) {
      var sel = h("select", { id: id }, opts.map(function (o) { var e = h("option", { value: String(o[0]), text: o[1] }); return e; }));
      sel.value = String(value);
      sel.addEventListener("change", function () { onChange(sel.value); });
      var row = h("div", { className: "slider-row" }, [h("label", { "for": id, text: text }), h("span"), sel]);
      row.sel = sel;
      return row;
    }
    var epsRow = slider("eps", "Second start offset $10^{k}$", "Second start offset exponent", function (v) { return "10^" + v; });
    var tRow = slider("tEnd", "Final time $t$", "Final time", function (v) { return String(v); });
    var pertRow = slider("perturb", "Perturbation size", "Perturbation size", function (v) { return num(v, 2); });
    var mu1Row = slider("mu1", "$\\mu_1$ (prey level)", "mu 1", function (v) { return String(v); });
    var mu2Row = slider("mu2", "$\\mu_2$ (predator level)", "mu 2", function (v) { return String(v); });
    var e1Row = slider("eta1", "$\\eta_1$ (prey at start)", "eta 1", function (v) { return String(v); });
    var e2Row = slider("eta2", "$\\eta_2$ (predators at start)", "eta 2", function (v) { return String(v); });
    var rhoRow = selectRow("ap-rho", "ρ (Lorenz)", config.rho.options.map(function (r) { return [r, String(r)]; }), st.rho,
      function (v) { st.rho = parseFloat(v); compute(); ctx.save(); ctx.announce("rho " + v); });
    var axisRow = selectRow("ap-axis", "Start near axis", [["x", "x: short axis"], ["y", "y: middle axis"], ["z", "z: long axis"]], st.axis,
      function (v) { st.axis = v; compute(); ctx.save(); ctx.announce("Axis " + v); });

    var radios = {};
    var modeBox = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "System", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })]);
    config.modes.forEach(function (m) {
      var id = "ap-mode-" + m.id, r = h("input", { type: "radio", name: "ap-mode", id: id, value: m.id });
      r.checked = st.mode === m.id;
      r.addEventListener("change", function () { if (r.checked) { st.mode = m.id; compute(); ctx.save(); ctx.announce("System " + m.label); } });
      radios[m.id] = r;
      modeBox.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
    });
    var bPlay = h("button", { type: "button", className: "btn small", text: "Play", onclick: function () { if (playing) pause(); else play(); } });
    var bAll = h("button", { type: "button", className: "btn small", text: "Show all", onclick: function () { pause(); shown = data.n; draw(); } });
    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        pause();
        st.mode = p.mode; radios[p.mode].checked = true;
        if (typeof p.rho === "number") { st.rho = p.rho; rhoRow.sel.value = String(p.rho); }
        if (p.axis) { st.axis = p.axis; axisRow.sel.value = p.axis; }
        NUM.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; outputs[k].textContent = String(st[k]); } });
        ctx.mathText(presetNote, p.note || "");
        compute(); ctx.save(); ctx.announce("Preset " + p.label);
      } });
    }));
    var controls = h("div", null, [h("h2", { text: "System" }), epsRow, tRow, pertRow, mu1Row, mu2Row, e1Row, e2Row, rhoRow, axisRow,
      modeBox, h("div", { className: "presets" }, [bPlay, bAll]), h("h3", { text: "Presets" }), presets, presetNote]);

    // ---------------- panels
    function panel(title, w, hh, aria) {
      var svg = s("svg", { viewBox: "0 0 " + w + " " + hh, role: "img", "aria-label": aria, style: "width:100%;height:auto" });
      var cap = h("p", { className: "plot-note" });
      var box = h("div", { className: "plot-box" }, [h("h3", { text: title }), svg, cap]);
      return { svg: svg, cap: cap, box: box, w: w, h: hh, title: box.firstChild };
    }
    var P1 = panel("Picture", 520, 420, "Main view of the trajectory");
    var P2 = panel("Time series", 640, 220, "Components against time");
    var P3 = panel("Distance between the two Lorenz runs (log scale)", 640, 180, "Logarithm of the distance between two nearby Lorenz solutions against time");
    var facts = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls, h("div", null, [P1.box, facts, P2.box, P3.box])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function vis(el, on) { el.hidden = !on; el.style.display = on ? "" : "none"; }
    function path(pts, attrs) {
      var d = ""; for (var i = 0; i < pts.length; i++) d += (i ? "L" : "M") + pts[i][0].toFixed(1) + " " + pts[i][1].toFixed(1);
      var a = { d: d, fill: "none" }; for (var k in attrs) a[k] = attrs[k]; return s("path", a);
    }
    function txt(svg, x, y, str, color, anchor) { var e = s("text", { x: x, y: y, fill: color || "var(--muted)", "font-size": 12, "text-anchor": anchor || "start" }); e.textContent = str; svg.appendChild(e); }

    // ---------------- computation
    function compute() {
      pause();
      vis(epsRow, st.mode === "lorenz"); vis(rhoRow, st.mode === "lorenz");
      vis(pertRow, st.mode === "box"); vis(axisRow, st.mode === "box");
      [mu1Row, mu2Row, e1Row, e2Row].forEach(function (r) { vis(r, st.mode === "pp"); });
      vis(P3.box, st.mode === "lorenz");
      var T = st.tEnd;
      if (st.mode === "lorenz") {
        var hh = 0.002, n = Math.round(T / hh), c = SM.lorenzCritical(st.rho, 8 / 3)[0], f = SM.lorenz(10, st.rho, 8 / 3);
        var y0 = [c[0] + 3, c[1] + 2, c[2] - 4], y1 = [y0[0] + Math.pow(10, st.eps), y0[1], y0[2]];
        var A = SM.rk4(f, y0, hh, n), B = SM.rk4(f, y1, hh, n), stepK = 5;
        data = { kind: "lorenz", t: [], A: [], B: [], d: [], dt: hh * stepK, crit: SM.lorenzCritical(st.rho, 8 / 3) };
        for (var i = 0; i <= n; i += stepK) {
          data.t.push(i * hh); data.A.push(A[i]); data.B.push(B[i]);
          data.d.push(Math.hypot(A[i][0] - B[i][0], A[i][1] - B[i][1], A[i][2] - B[i][2]));
        }
      } else if (st.mode === "box") {
        var hb = 0.002, nb = Math.round(T / hb), y0b = SM.boxStart(st.axis, st.perturb), Y = SM.rk4(SM.box, y0b, hb, nb);
        data = { kind: "box", t: [], A: [], dt: hb * 5, y0: y0b };
        for (var j = 0; j <= nb; j += 5) { data.t.push(j * hb); data.A.push(Y[j]); }
      } else {
        var hp = 0.001, np_ = Math.round(T / hp), fp = SM.predprey(st.mu1, st.mu2), Yp = SM.rk4(fp, [st.eta1, st.eta2], hp, np_);
        data = { kind: "pp", t: [], A: [], dt: hp * 10, period: SM.period(st.mu1, st.mu2, st.eta1, st.eta2, Math.max(40, T)) };
        for (var k = 0; k <= np_; k += 10) { data.t.push(k * hp); data.A.push(Yp[k]); }
        data.H = data.A.map(function (y) { return SM.H(st.mu1, st.mu2, y); });
      }
      data.n = data.t.length;
      shown = data.n;
      draw();
    }

    // ---------------- animation
    function play() {
      if (shown >= data.n) shown = 1;
      if (reduced()) { shown = data.n; draw(); return; }
      playing = true; bPlay.textContent = "Pause"; lastTs = 0;
      raf = requestAnimationFrame(tick);
    }
    function pause() { playing = false; bPlay.textContent = "Play"; stop(); }
    function tick(ts) {
      if (!playing) return;
      var dt = lastTs ? (ts - lastTs) / 1000 : 0; lastTs = ts;
      var speed = st.mode === "lorenz" ? 3 : 2.5; // simulated time units per second
      shown = Math.min(data.n, shown + Math.max(1, Math.round(dt * speed / data.dt)));
      draw();
      if (shown >= data.n) { pause(); return; }
      raf = requestAnimationFrame(tick);
    }

    // ---------------- drawing
    function draw() {
      if (data.kind === "lorenz") drawLorenz();
      else if (data.kind === "box") drawBox();
      else drawPP();
      drawSeries();
    }

    function frame(P, x0, x1, y0, y1, xl, yl) {
      clear(P.svg);
      var L = 46, R = 10, T = 10, B = 28, W = P.w, H = P.h;
      var X = function (x) { return L + (x - x0) / (x1 - x0) * (W - L - R); };
      var Y = function (y) { return T + (y1 - y) / (y1 - y0) * (H - T - B); };
      P.svg.appendChild(s("rect", { x: L, y: T, width: W - L - R, height: H - T - B, fill: "none", stroke: "var(--border)" }));
      txt(P.svg, L - 4, T + 10, num(y1, 3), null, "end"); txt(P.svg, L - 4, H - B, num(y0, 3), null, "end");
      txt(P.svg, L, H - 8, num(x0, 3)); txt(P.svg, W - R, H - 8, num(x1, 3), null, "end");
      txt(P.svg, (L + W - R) / 2, H - 8, xl, null, "middle"); txt(P.svg, L + 4, T + 14, yl);
      return { X: X, Y: Y };
    }
    function range(arr, idx) {
      var lo = Infinity, hi = -Infinity;
      arr.forEach(function (y) { var v = y[idx]; if (isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); } });
      var pad = (hi - lo) * 0.06 || 1; return [lo - pad, hi + pad];
    }

    function drawLorenz() {
      P1.title.textContent = "Lorenz attractor, x–z projection (ρ = " + st.rho + ")";
      var xr = range(data.A, 0), zr = range(data.A, 2), F = frame(P1, xr[0], xr[1], zr[0], zr[1], "x", "z");
      var a = data.A.slice(0, shown).map(function (y) { return [F.X(y[0]), F.Y(y[2])]; });
      var b = data.B.slice(0, shown).map(function (y) { return [F.X(y[0]), F.Y(y[2])]; });
      P1.svg.appendChild(path(a, { stroke: "var(--teal)", "stroke-width": 1.1, opacity: 0.9 }));
      P1.svg.appendChild(path(b, { stroke: "var(--orange)", "stroke-width": 1.1, opacity: 0.75 }));
      data.crit.forEach(function (c) { P1.svg.appendChild(s("circle", { cx: F.X(c[0]), cy: F.Y(c[2]), r: 4, fill: "var(--green)" })); });
      var ha = a[a.length - 1], hb = b[b.length - 1];
      P1.svg.appendChild(s("circle", { cx: ha[0], cy: ha[1], r: 5, fill: "var(--teal)" }));
      P1.svg.appendChild(s("circle", { cx: hb[0], cy: hb[1], r: 5, fill: "var(--orange)" }));
      P1.cap.textContent = "Teal: start at the critical point + (3, 2, −4). Orange: the same start moved by 10^" + st.eps + " in x. Green dots: critical points (±η, ±η, ρ − 1).";
      var d = data.d[shown - 1], tNow = data.t[shown - 1], eta = Math.sqrt(8 / 3 * (st.rho - 1));
      var tSep = null; for (var i = 0; i < shown; i++) if (data.d[i] > 1) { tSep = data.t[i]; break; }
      setFacts(["t = " + num(tNow, 3) + ";  distance between the runs " + num(d, 3),
                "η = √(β(ρ − 1)) = " + num(eta, 4) + ";  critical points (±" + num(eta, 4) + ", ±" + num(eta, 4) + ", " + num(st.rho - 1, 4) + ")",
                tSep === null ? "The runs have not yet separated by more than 1." : "The runs first differ by more than 1 at t ≈ " + num(tSep, 3) + "."]);
      // distance panel
      var lo = -10, hi = 2.5, G = frame(P3, 0, st.tEnd, lo, hi, "t", "log10 distance");
      var pts = []; for (var j = 0; j < shown; j++) { var v = Math.log10(Math.max(1e-12, data.d[j])); pts.push([G.X(data.t[j]), G.Y(Math.max(lo, Math.min(hi, v)))]); }
      P3.svg.appendChild(path(pts, { stroke: "var(--red)", "stroke-width": 1.6 }));
      P3.cap.textContent = "On a log scale exponential growth is a rising straight trend; it stops when the distance reaches the size of the attractor.";
    }

    function drawBox() {
      P1.title.textContent = "Orbit on the unit sphere (start near the " + st.axis + " axis)";
      clear(P1.svg);
      var W = P1.w, H = P1.h, cx = W / 2, cy = H / 2, R = Math.min(W, H) * 0.42;
      var az = 0.6, el = 0.35, ca = Math.cos(az), sa = Math.sin(az), ce = Math.cos(el), se = Math.sin(el);
      function proj(p) { // orthographic view
        var x = ca * p[0] - sa * p[1], y = sa * p[0] + ca * p[1], z = p[2];
        var y2 = ce * z - se * y, depth = se * z + ce * y;
        return [cx + R * x, cy - R * y2, depth];
      }
      P1.svg.appendChild(s("circle", { cx: cx, cy: cy, r: R, fill: "none", stroke: "var(--border)" }));
      [["x", [1, 0, 0]], ["y", [0, 1, 0]], ["z", [0, 0, 1]]].forEach(function (ax) {
        var p = proj(ax[1]), m = proj(ax[1].map(function (v) { return -v; }));
        P1.svg.appendChild(s("line", { x1: m[0], y1: m[1], x2: p[0], y2: p[1], stroke: "var(--muted)", "stroke-width": 0.8, "stroke-dasharray": "4 3" }));
        txt(P1.svg, p[0] + 4, p[1] - 4, ax[0], ax[0] === "y" ? "var(--red)" : "var(--green)");
        P1.svg.appendChild(s("circle", { cx: p[0], cy: p[1], r: 4, fill: ax[0] === "y" ? "var(--red)" : "var(--green)" }));
        P1.svg.appendChild(s("circle", { cx: m[0], cy: m[1], r: 4, fill: ax[0] === "y" ? "var(--red)" : "var(--green)" }));
      });
      var front = [], back = [], prev = null;
      for (var i = 0; i < shown; i++) {
        var q = proj(data.A[i]);
        (q[2] >= 0 ? front : back).push(q);
      }
      P1.svg.appendChild(path(data.A.slice(0, shown).map(proj), { stroke: "var(--teal)", "stroke-width": 1.6, opacity: 0.85 }));
      var last = proj(data.A[shown - 1]);
      P1.svg.appendChild(s("circle", { cx: last[0], cy: last[1], r: 5, fill: "var(--orange)" }));
      P1.cap.textContent = "Green: stable spins about the short (x) and long (z) axes. Red: the unstable middle axis (y).";
      var y = data.A[shown - 1], r = Math.hypot(y[0], y[1], y[2]);
      var miny = Math.min.apply(null, data.A.slice(0, shown).map(function (v) { return v[1]; }));
      setFacts(["t = " + num(data.t[shown - 1], 3) + ";  (x, y, z) = (" + y.map(function (v) { return num(v, 3); }).join(", ") + ")",
                "x² + y² + z² = " + num(r * r, 10) + " (conserved)",
                st.axis === "y" ? "Smallest y so far: " + num(miny, 3) + " — the box flips when y reaches about −1." : "The spin stays near its axis: small oscillations."]);
    }

    function drawPP() {
      P1.title.textContent = "Phase plane: prey y₁ against predators y₂";
      var xr = range(data.A, 0), yr = range(data.A, 1);
      xr[0] = Math.min(xr[0], st.mu1 * 0.9); xr[1] = Math.max(xr[1], st.mu1 * 1.1);
      yr[0] = Math.min(yr[0], st.mu2 * 0.9); yr[1] = Math.max(yr[1], st.mu2 * 1.1);
      var F = frame(P1, Math.max(0, xr[0]), xr[1], Math.max(0, yr[0]), yr[1], "y₁ (prey)", "y₂ (predators)");
      P1.svg.appendChild(path(data.A.slice(0, shown).map(function (y) { return [F.X(y[0]), F.Y(y[1])]; }), { stroke: "var(--teal)", "stroke-width": 2 }));
      P1.svg.appendChild(s("circle", { cx: F.X(st.mu1), cy: F.Y(st.mu2), r: 5, fill: "var(--green)" }));
      txt(P1.svg, F.X(st.mu1) + 6, F.Y(st.mu2) - 6, "(μ₁, μ₂)", "var(--green)");
      var last = data.A[shown - 1];
      P1.svg.appendChild(s("circle", { cx: F.X(last[0]), cy: F.Y(last[1]), r: 5, fill: "var(--orange)" }));
      P1.cap.textContent = "The orbit runs counterclockwise around (μ₁, μ₂) and closes, because H = ln y₁ − y₁/μ₁ + ln y₂ − y₂/μ₂ is conserved.";
      var Hs = data.H.slice(0, shown), spread = Math.max.apply(null, Hs) - Math.min.apply(null, Hs);
      setFacts(["t = " + num(data.t[shown - 1], 3) + ";  prey " + num(last[0], 4) + ", predators " + num(last[1], 4),
                "Measured period: " + (data.period ? num(data.period, 4) : "–") + "  (2π = 6.2832 for small orbits)",
                "H = " + num(Hs[0], 8) + ", variation along the computed orbit " + num(spread, 2)]);
    }

    function drawSeries() {
      var comps = data.kind === "pp" ? [[0, "y₁ prey", "var(--teal)"], [1, "y₂ predators", "var(--orange)"]]
        : data.kind === "box" ? [[0, "x", "var(--green)"], [1, "y", "var(--red)"], [2, "z", "var(--blue)"]]
        : [[0, "x (teal run)", "var(--teal)"]];
      var lo = Infinity, hi = -Infinity;
      comps.forEach(function (c) { var r = range(data.A, c[0]); lo = Math.min(lo, r[0]); hi = Math.max(hi, r[1]); });
      var F = frame(P2, 0, data.t[data.n - 1], lo, hi, "t", "");
      comps.forEach(function (c) {
        P2.svg.appendChild(path(data.A.slice(0, shown).map(function (y, i) { return [F.X(data.t[i]), F.Y(y[c[0]])]; }), { stroke: c[2], "stroke-width": 1.5 }));
      });
      if (data.kind === "lorenz") {
        P2.svg.appendChild(path(data.B.slice(0, shown).map(function (y, i) { return [F.X(data.t[i]), F.Y(y[0])]; }), { stroke: "var(--orange)", "stroke-width": 1.2, opacity: 0.8 }));
      }
      P2.cap.textContent = comps.map(function (c) { return c[1]; }).join(", ") + (data.kind === "lorenz" ? ", x (orange run)" : "") + ".";
    }

    function setFacts(lines) { clear(facts); lines.forEach(function (l) { facts.appendChild(h("p", { text: l, style: "margin:2px 0" })); }); }

    compute();
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
