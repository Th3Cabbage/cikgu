/*
 * Second-order explorer: y'' + B y' + C y = f(t), y(0) = y0, y'(0) = v0.
 * Maths comes from window.StudyMath (response, gain).
 * Saved state: state.explorer = {input, B, C, y0, v0, omega, s}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["B", "C", "y0", "v0", "omega", "s"];
  var KIND_WORD = { undamped: "undamped", underdamped: "underdamped", critical: "critically damped", overdamped: "overdamped" };
  var CLIP = 50;

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function inputIds(config) { return config.inputs.map(function (m) { return m.id; }); }
  function defaults(config) {
    var out = { input: config.defaultInput };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config || !Array.isArray(config.inputs)) return out;
    if (typeof saved.input === "string" && inputIds(config).indexOf(saved.input) >= 0) out.input = saved.input;
    KEYS.forEach(function (k) {
      var v = saved[k], c = config[k];
      if (typeof v === "number" && isFinite(v) && v >= c.min - 1e-9 && v <= c.max + 1e-9) out[k] = snap(v, c);
    });
    return out;
  }
  function stop() { /* no timers: every update is immediate */ }

  function num(v) {
    if (!isFinite(v)) return v > 0 ? "∞" : v < 0 ? "−∞" : "NaN";
    if (Math.abs(v) < 5e-10) return "0";
    var r = Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 0.1 ? +v.toFixed(3) + "" : +v.toPrecision(3) + "";
    return String(r).replace("-", "−");
  }
  function tnum(v) { return num(v).replace("−", "-"); }
  var uid = 0;

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var tMax = config.tMax || 16;
    var clipIds = [++uid, ++uid, ++uid].map(function (n) { return "ex-clip-" + n; });

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "How do the roots shape the response?" }),
      ctx.mathText(h("p", { className: "lede" }), "Choose an input and move $B$, $C$ and the start values. The roots of $s^2 + Bs + C$ decide the null solution; the input decides the particular solution.")
    ]));

    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text, label) {
      var c = config[key], id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      inp.setAttribute("aria-label", label);
      var out = h("output", { "for": id, text: num(st[key]) });
      inp.addEventListener("input", function () {
        st[key] = snap(parseFloat(inp.value), c); update(); ctx.save();
        ctx.announce(label + " " + num(st[key]));
      });
      inputs[key] = inp; outputs[key] = out;
      var row = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
      rows[key] = row;
      return row;
    }

    var radios = {};
    var kindBox = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "Input f(t)", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    config.inputs.forEach(function (m) {
      var id = "ex-input-" + m.id;
      var r = h("input", { type: "radio", name: "ex-input", id: id, value: m.id });
      r.checked = st.input === m.id;
      r.addEventListener("change", function () {
        if (r.checked) { st.input = m.id; update(); ctx.save(); ctx.announce("Input: " + m.label.replace(/\s+/g, " ")); }
      });
      radios[m.id] = r;
      kindBox.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
    });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (radios[p.input]) { st.input = p.input; radios[p.input].checked = true; }
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note);
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var controls = h("div", null, [
      h("h2", { text: "Equation" }), presets, kindBox,
      slider("B", "Damping $B$", "Damping B"), slider("C", "Stiffness $C$", "Stiffness C"),
      slider("y0", "Start value $y_0$", "Start value y zero"), slider("v0", "Start velocity $v_0$", "Start velocity v zero"),
      slider("omega", "Frequency $\\omega$", "Input frequency omega"), slider("s", "Exponent $s$", "Input exponent s")
    ]);

    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }
    var W = 360, L = 36, Rr = 10, Tp = 12;

    // panel 1: complex plane
    var H1 = 230, B1 = 24;
    var svg1 = s("svg", { viewBox: "0 0 " + W + " " + H1, role: "img", "aria-label": "Complex plane showing the two roots of s squared plus B s plus C" });
    var defs1 = s("defs"), clip1 = s("clipPath", { id: clipIds[0] });
    clip1.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H1 - Tp - B1 }));
    defs1.appendChild(clip1); svg1.appendChild(defs1);
    var grid1 = s("g"), top1 = s("g", { "clip-path": "url(#" + clipIds[0] + ")" });
    svg1.appendChild(grid1); svg1.appendChild(top1);
    var cap1 = h("p", { className: "plot-note" });
    var box1 = h("div", { className: "plot-box" }, [h("h3", { text: "Roots of s² + Bs + C" }), svg1,
      h("div", { className: "legend" }, [h("span", null, [sw("var(--teal)"), "roots"]), h("span", null, [sw("var(--orange)"), "input exponent s"])]), cap1]);

    // panel 2: response
    var H2 = 240, B2 = 26;
    var svg2 = s("svg", { viewBox: "0 0 " + W + " " + H2, role: "img", "aria-label": "Plot of the response y of t with the particular part dashed" });
    var defs2 = s("defs"), clip2 = s("clipPath", { id: clipIds[1] });
    clip2.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H2 - Tp - B2 }));
    defs2.appendChild(clip2); svg2.appendChild(defs2);
    var grid2 = s("g"), curve2 = s("g", { "clip-path": "url(#" + clipIds[1] + ")" });
    svg2.appendChild(grid2); svg2.appendChild(curve2);
    var note2 = h("p", { className: "plot-note" });
    var parLegend = h("span", null, [sw("var(--blue)"), "particular y_p"]);
    var legend2 = h("div", { className: "legend" }, [h("span", null, [sw("var(--teal)"), "y(t)"]), parLegend]);
    var box2 = h("div", { className: "plot-box" }, [h("h3", { text: "Response y(t)" }), svg2, legend2, note2]);

    // panel 3: gain
    var H3 = 190, B3 = 26;
    var svg3 = s("svg", { viewBox: "0 0 " + W + " " + H3, role: "img", "aria-label": "Plot of the gain G of omega with a marker at the current omega" });
    var defs3 = s("defs"), clip3 = s("clipPath", { id: clipIds[2] });
    clip3.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H3 - Tp - B3 }));
    defs3.appendChild(clip3); svg3.appendChild(defs3);
    var grid3 = s("g"), curve3 = s("g", { "clip-path": "url(#" + clipIds[2] + ")" });
    svg3.appendChild(grid3); svg3.appendChild(curve3);
    var note3 = h("p", { className: "plot-note" });
    var box3 = h("div", { className: "plot-box" }, [h("h3", { text: "Gain G(ω)" }), svg3, note3]);

    var texBox = h("div", { className: "readout" }), factsBox = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [box1, box2, box3, presetNote, texBox, factsBox])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function niceStep(span) {
      var step = Math.pow(10, Math.floor(Math.log10(span / 4))), m = span / 4 / step;
      return step * (m > 5 ? 10 : m > 2 ? 5 : m > 1 ? 2 : 1);
    }
    function cross(g, x, y, color, r) {
      g.appendChild(s("line", { x1: x - r, y1: y - r, x2: x + r, y2: y + r, style: "stroke:" + color + ";stroke-width:2.6;stroke-linecap:round" }));
      g.appendChild(s("line", { x1: x - r, y1: y + r, x2: x + r, y2: y - r, style: "stroke:" + color + ";stroke-width:2.6;stroke-linecap:round" }));
    }
    function pathOf(arr, X, Y, lim) {
      var d = "";
      arr.forEach(function (q, j) {
        var yy = Math.max(-lim, Math.min(lim, Y(q[1])));
        d += (j ? "L" : "M") + X(q[0]).toFixed(2) + " " + yy.toFixed(2) + " ";
      });
      return d;
    }

    function update() {
      var hasOmega = st.input === "cos", hasS = st.input === "exp";
      KEYS.forEach(function (k) {
        outputs[k].textContent = num(st[k]);
        var show = k === "omega" ? hasOmega : k === "s" ? hasS : true;
        rows[k].hidden = !show;
        rows[k].style.display = show ? "" : "none";
      });
      var p = { input: st.input, B: st.B, C: st.C, y0: st.y0, v0: st.v0, omega: st.omega, s: st.s };
      var R = SM.response(p), rt = R.roots, info = R.particularInfo;
      var i, v;

      // ---- panel 1: roots ----
      clear(grid1); clear(top1);
      var rl = -5.5, rh = 1.5, il = 3.5;
      var pw = W - L - Rr, ph = H1 - Tp - B1;
      var X1 = function (re) { return L + pw * (re - rl) / (rh - rl); };
      var Y1 = function (im) { return Tp + ph * (il - im) / (2 * il); };
      grid1.appendChild(s("rect", { x: L, y: Tp, width: X1(0) - L, height: ph, style: "fill:var(--teal);opacity:0.08" }));
      for (v = -5; v <= 1; v++) {
        grid1.appendChild(s("line", { x1: X1(v), y1: Tp, x2: X1(v), y2: Tp + ph, "class": v === 0 ? "p-axis" : "p-grid" }));
        grid1.appendChild(s("text", { x: X1(v), y: Tp + ph + 14, "text-anchor": "middle", text: num(v) }));
      }
      for (v = -3; v <= 3; v++) {
        grid1.appendChild(s("line", { x1: L, y1: Y1(v), x2: W - Rr, y2: Y1(v), "class": v === 0 ? "p-axis" : "p-grid" }));
        grid1.appendChild(s("text", { x: L - 4, y: Y1(v) + 4, "text-anchor": "end", text: num(v) }));
      }
      grid1.appendChild(s("text", { x: W - Rr, y: Tp + ph + 22, "text-anchor": "end", text: "Re" }));
      grid1.appendChild(s("text", { x: L + 4, y: Tp + 9, text: "Im" }));
      if (hasS) {
        top1.appendChild(s("circle", { cx: X1(st.s), cy: Y1(0), r: 6, style: "fill:none;stroke:var(--orange);stroke-width:2.4" }));
      }
      [rt.s1, rt.s2].forEach(function (z, j) {
        if (j === 1 && rt.kind === "critical") return;
        cross(top1, X1(z.re), Y1(z.im), "var(--teal)", 6);
      });
      var cap = KIND_WORD[rt.kind] + ": ω_n = " + num(rt.wn) + ", ζ = " + num(rt.zeta) +
        (rt.wd !== null ? ", ω_d = " + num(rt.wd) : "") +
        ". Roots " + (rt.kind === "overdamped"
          ? num(rt.s1.re) + " and " + num(rt.s2.re)
          : rt.kind === "critical" ? num(rt.s1.re) + " (double)"
          : num(rt.s1.re) + " ± " + num(rt.s1.im) + "i") + ".";
      if (hasS) cap += info.resonance ? " Resonance: s lands on a root." : " s = " + num(st.s) + " is not a root.";
      cap1.textContent = cap;

      // ---- panel 2: response ----
      clear(grid2); clear(curve2);
      var n = 400, tot = [], par = [], lo = Infinity, hi = -Infinity, clipped = false;
      var showPar = st.input !== "none" && st.input !== "impulse";
      function track(q) {
        if (!isFinite(q)) return;
        if (Math.abs(q) > CLIP) clipped = true;
        q = Math.max(-CLIP, Math.min(CLIP, q)); lo = Math.min(lo, q); hi = Math.max(hi, q);
      }
      for (i = 0; i <= n; i++) {
        var t = tMax * i / n, yt = R.total(t), yp = showPar ? R.particular(t) : 0;
        tot.push([t, yt]); par.push([t, yp]);
        track(yt); if (showPar) track(yp);
      }
      if (!isFinite(lo)) { lo = -1; hi = 1; }
      lo = Math.min(lo, 0); hi = Math.max(hi, 0);
      var pad = 0.1 * Math.max(hi - lo, 0.5); lo -= pad; hi += pad;
      var h2 = H2 - Tp - B2;
      var X2 = function (tt) { return L + (W - L - Rr) * tt / tMax; };
      var Y2 = function (yy) { return Tp + h2 * (hi - yy) / (hi - lo); };
      for (i = 0; i <= 4; i++) {
        var tt = tMax * i / 4;
        grid2.appendChild(s("line", { x1: X2(tt), y1: Tp, x2: X2(tt), y2: H2 - B2, "class": "p-grid" }));
        grid2.appendChild(s("text", { x: X2(tt), y: H2 - B2 + 14, "text-anchor": "middle", text: num(tt) }));
      }
      var sy = niceStep(hi - lo);
      for (v = Math.ceil(lo / sy - 1e-9) * sy; v <= hi + 1e-9; v += sy) {
        var z0 = Math.abs(v) < sy / 2;
        grid2.appendChild(s("line", { x1: L, y1: Y2(v), x2: W - Rr, y2: Y2(v), "class": z0 ? "p-axis" : "p-grid" }));
        grid2.appendChild(s("text", { x: L - 4, y: Y2(v) + 4, "text-anchor": "end", text: num(z0 ? 0 : v) }));
      }
      grid2.appendChild(s("text", { x: W - Rr, y: H2 - 2, "text-anchor": "end", text: "t" }));
      if (showPar) {
        curve2.appendChild(s("path", { d: pathOf(par, X2, Y2, 1e3), fill: "none", style: "stroke:var(--blue);stroke-width:2;stroke-dasharray:6 4" }));
      }
      curve2.appendChild(s("path", { d: pathOf(tot, X2, Y2, 1e3), fill: "none", style: "stroke:var(--teal);stroke-width:3.2;stroke-linejoin:round;stroke-linecap:round" }));
      curve2.appendChild(s("circle", { cx: X2(0), cy: Y2(st.y0), r: 4, style: "fill:var(--teal)" }));
      parLegend.style.display = showPar ? "" : "none";
      note2.className = "plot-note" + (clipped ? " warn" : "");
      note2.textContent = clipped
        ? "Values beyond ±" + CLIP + " are clipped; the response grows very large."
        : st.input === "impulse" ? "The impulse adds 1 to y′(0); the curve shows t > 0."
        : "Teal: complete solution y = y_p + null solution; dashed blue: particular part.";

      // ---- panel 3: gain ----
      box3.hidden = !hasOmega; box3.style.display = hasOmega ? "" : "none";
      if (hasOmega) {
        clear(grid3); clear(curve3);
        var wl = 0.05, wh = 5, gs = [], gh = 0;
        for (i = 0; i <= 250; i++) {
          var w = wl + (wh - wl) * i / 250, g = SM.gain(st.B, st.C, w);
          gs.push([w, g]); if (isFinite(g)) gh = Math.max(gh, g);
        }
        var gtop = (Math.min(gh, 6 / st.C) || 1) * 1.1;
        var h3 = H3 - Tp - B3;
        var X3 = function (ww) { return L + (W - L - Rr) * (ww - wl) / (wh - wl); };
        var Y3 = function (g) { return Tp + h3 * (1 - g / gtop); };
        for (v = 0; v <= 5; v++) {
          var xv = X3(v === 0 ? wl : v);
          grid3.appendChild(s("line", { x1: xv, y1: Tp, x2: xv, y2: H3 - B3, "class": "p-grid" }));
          grid3.appendChild(s("text", { x: xv, y: H3 - B3 + 14, "text-anchor": "middle", text: String(v) }));
        }
        var sg = niceStep(gtop);
        for (v = 0; v <= gtop + 1e-9; v += sg) {
          grid3.appendChild(s("line", { x1: L, y1: Y3(v), x2: W - Rr, y2: Y3(v), "class": v === 0 ? "p-axis" : "p-grid" }));
          grid3.appendChild(s("text", { x: L - 4, y: Y3(v) + 4, "text-anchor": "end", text: num(v) }));
        }
        grid3.appendChild(s("text", { x: W - Rr, y: H3 - 2, "text-anchor": "end", text: "ω" }));
        curve3.appendChild(s("path", { d: pathOf(gs, X3, Y3, 1e3), fill: "none", style: "stroke:var(--teal);stroke-width:3;stroke-linejoin:round" }));
        var gw = SM.gain(st.B, st.C, st.omega);
        curve3.appendChild(s("line", { x1: X3(st.omega), y1: Tp, x2: X3(st.omega), y2: H3 - B3, style: "stroke:var(--orange);stroke-width:1.4;stroke-dasharray:3 3" }));
        if (isFinite(gw)) curve3.appendChild(s("circle", { cx: X3(st.omega), cy: Math.max(-1e3, Y3(gw)), r: 5, style: "fill:var(--orange)" }));
        note3.textContent = "Gain G(ω) = 1/√((C − ω²)² + (Bω)²); the orange marker is the current ω. Peaks above the plotted range are clipped.";
      }

      // ---- readouts ----
      texBox.textContent = "";
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), info.tex));
      factsBox.textContent = "";
      function fact(t, cls) {
        var el = ctx.mathText(h("p", { style: "margin:2px 0" }), t);
        if (cls) el.className = cls;
        factsBox.appendChild(el);
      }
      if (st.input === "step") fact("$Y = 1/C = " + tnum(1 / st.C) + "$.");
      if (st.input === "exp") {
        if (info.resonance) fact("$P(s) = " + tnum(info.P) + "$, so $s$ is a root: resonance, $P'(s) = " + tnum(info.dP) + "$.");
        else fact("$P(s) = " + tnum(info.P) + "$, so $Y = 1/P(s) = " + tnum(info.Y) + "$.");
      }
      if (st.input === "cos") {
        if (info.resonance) {
          fact("resonance: $y_p = t\\sin\\omega t/(2\\omega)$ grows without bound.", "plot-note warn");
        } else {
          fact("$M = " + tnum(info.M) + "$, $N = " + tnum(info.N) + "$, $G = " + tnum(info.G) + "$, $\\alpha = " +
            tnum(info.alpha) + "$ rad $= " + tnum(info.alpha * 180 / Math.PI) + "^\\circ$.");
        }
      }
      if (st.input === "impulse") fact("The impulse acts as a jump: $y'(0^+) = v_0 + 1 = " + tnum(st.v0 + 1) + "$.");
      if (st.input === "none") fact("No input: the response is the null solution alone.");
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
