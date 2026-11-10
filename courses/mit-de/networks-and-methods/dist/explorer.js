/*
 * Networks and methods explorer. Two modes:
 *   rlc: impedance Z = R + i(wL - 1/(wC)) and the current amplitude 1/|Z| against omega.
 *   uc : undetermined coefficients for y'' + B y' + C y = amp * f(t).
 * Maths comes from window.StudyMath (impedance, ucSolve, residual, convolution, trialTex).
 * Saved state: state.explorer = {mode, R, L, Cexp, omega, B, Cc, form, k, s, w, amp}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["R", "L", "Cexp", "omega", "B", "Cc", "k", "s", "w", "amp"];
  var RLC_KEYS = ["R", "L", "Cexp", "omega"];
  var CLIP = 200;

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function idsOf(list) { return (list || []).map(function (m) { return m.id; }); }
  function defaults(config) {
    var out = { mode: config.defaultMode || "uc", form: (config.forms[0] || {}).id || "poly" };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config || !Array.isArray(config.modes)) return out;
    if (typeof saved.mode === "string" && idsOf(config.modes).indexOf(saved.mode) >= 0) out.mode = saved.mode;
    if (typeof saved.form === "string" && idsOf(config.forms).indexOf(saved.form) >= 0) out.form = saved.form;
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
  function sig4(v) { return +v.toPrecision(4); }
  var uid = 0;

  // real polynomial coefficients -> LaTeX "3 + 2t - t^2"; returns {tex, terms}
  function polyTex(co) {
    var maxAbs = 0, j;
    co.forEach(function (c) { maxAbs = Math.max(maxAbs, Math.abs(c)); });
    var out = "", terms = 0;
    for (j = 0; j < co.length; j++) {
      var c = co[j];
      if (Math.abs(c) < 1e-9 * Math.max(maxAbs, 1e-300) || Math.abs(c) < 1e-9) continue;
      var r = sig4(c), a = Math.abs(r);
      var pw = j === 0 ? "" : j === 1 ? "t" : "t^{" + j + "}";
      var body = (a === 1 && j > 0) ? pw : String(a) + pw;
      out += terms === 0 ? (r < 0 ? "-" : "") + body : (r < 0 ? " - " : " + ") + body;
      terms++;
    }
    return { tex: terms ? out : "0", terms: terms };
  }

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var tMax = config.tMax || 3;
    var clipIds = [++uid, ++uid, ++uid].map(function (n) { return "ex-clip-" + n; });

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Impedance and undetermined coefficients" }),
      ctx.mathText(h("p", { className: "lede" }), "Switch between the RLC loop, where $Z = R + i(\\omega L - 1/\\omega C)$ sets the current, and the guess-and-solve method for $y'' + By' + Cy = $ input.")
    ]));

    var inputs = {}, outputs = {}, rows = {};
    var labels = {
      R: ["Resistance $R$", "Resistance R"], L: ["Inductance $L$", "Inductance L"],
      Cexp: ["Capacitance: $\\log_{10} C$", "Log base 10 of capacitance C"], omega: ["Frequency $\\omega$", "Frequency omega"],
      B: ["Coefficient $B$", "Coefficient B"], Cc: ["Coefficient $C$", "Coefficient C"],
      k: ["Power $k$", "Power k"], s: ["Exponent $s$", "Exponent s"], w: ["Frequency $\\omega$", "Input frequency omega"],
      amp: ["Amplitude", "Amplitude of the input"]
    };
    function readout(key) {
      return key === "Cexp" ? num(Math.pow(10, st.Cexp)) + " (C)" : num(st[key]);
    }
    function slider(key) {
      var c = config[key], id = "ex-" + key, label = labels[key][1];
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      inp.setAttribute("aria-label", label);
      var out = h("output", { "for": id, text: readout(key) });
      inp.addEventListener("input", function () {
        st[key] = snap(parseFloat(inp.value), c); update(); ctx.save();
        ctx.announce(label + " " + readout(key));
      });
      inputs[key] = inp; outputs[key] = out;
      var row = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), labels[key][0]), out, inp]);
      rows[key] = row;
      return row;
    }

    function radioGroup(name, legend, list, current, onPick) {
      var map = {};
      var box = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
        h("legend", { text: legend, style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
      ]);
      list.forEach(function (m) {
        var id = "ex-" + name + "-" + m.id;
        var r = h("input", { type: "radio", name: "ex-" + name, id: id, value: m.id });
        r.checked = current() === m.id;
        r.addEventListener("change", function () {
          if (r.checked) { onPick(m.id); update(); ctx.save(); ctx.announce(legend + ": " + m.label); }
        });
        map[m.id] = r;
        box.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
      });
      return { box: box, map: map };
    }
    var modeG = radioGroup("mode", "Mode", config.modes, function () { return st.mode; }, function (v) { st.mode = v; });
    var formG = radioGroup("form", "Input form", config.forms, function () { return st.form; }, function (v) { st.form = v; });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (p.mode && modeG.map[p.mode]) { st.mode = p.mode; modeG.map[p.mode].checked = true; }
        if (p.form && formG.map[p.form]) { st.form = p.form; formG.map[p.form].checked = true; }
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note);
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var rlcControls = h("div", null, RLC_KEYS.map(slider));
    var ucControls = h("div", null, [formG.box].concat(["B", "Cc", "k", "s", "w", "amp"].map(slider)));
    var controls = h("div", null, [h("h2", { text: "Controls" }), presets, modeG.box, ucControls, rlcControls]);

    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }
    var W = 360, L = 36, Rr = 10, Tp = 12;
    function makePanel(H, Bm, aria) {
      var idx = clipIds.shift();
      var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": aria });
      var defs = s("defs"), clip = s("clipPath", { id: idx });
      clip.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H - Tp - Bm }));
      defs.appendChild(clip); svg.appendChild(defs);
      var grid = s("g"), top = s("g", { "clip-path": "url(#" + idx + ")" });
      svg.appendChild(grid); svg.appendChild(top);
      return { svg: svg, grid: grid, top: top, H: H, B: Bm };
    }

    // rlc panels
    var P1 = makePanel(230, 24, "Complex plane showing the impedance Z as a vector");
    var cap1 = h("p", { className: "plot-note" });
    var box1 = h("div", { className: "plot-box" }, [h("h3", { text: "Impedance Z in the complex plane" }), P1.svg, cap1]);
    var P2 = makePanel(240, 28, "Plot of current amplitude 1 over absolute Z against omega on a log axis");
    var cap2 = h("p", { className: "plot-note" });
    var box2 = h("div", { className: "plot-box" }, [h("h3", { text: "Current amplitude 1/|Z| against ω" }), P2.svg,
      h("div", { className: "legend" }, [h("span", null, [sw("var(--teal)"), "1/|Z|"]), h("span", null, [sw("var(--orange)"), "current ω"]), h("span", null, [sw("var(--blue)"), "ω₀ (dashed)"])]), cap2]);
    // uc panel
    var P3 = makePanel(260, 26, "Plot of the particular solution, the convolution solution and their difference");
    var cap3 = h("p", { className: "plot-note" });
    var box3 = h("div", { className: "plot-box" }, [h("h3", { text: "Particular solution and convolution solution" }), P3.svg,
      h("div", { className: "legend" }, [h("span", null, [sw("var(--green)"), "y_p"]), h("span", null, [sw("var(--teal)"), "convolution (from rest)"]),
        h("span", null, [sw("var(--pink)"), "difference = null solution"])]), cap3]);

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
    function pathOf(arr, X, Y, lim) {
      var d = "";
      arr.forEach(function (q, j) {
        var yy = Math.max(-lim, Math.min(lim, Y(q[1])));
        d += (j ? "L" : "M") + X(q[0]).toFixed(2) + " " + yy.toFixed(2) + " ";
      });
      return d;
    }
    function show(el, on) { el.hidden = !on; el.style.display = on ? "" : "none"; }

    function fTex(form, k, sv, w) {
      var pw = k === 0 ? "" : k === 1 ? "t" : "t^{" + k + "}";
      if (form === "poly") return k === 0 ? "1" : pw;
      if (form === "exp") return pw + (sv === 0 ? "" : "e^{" + (sv === 1 ? "" : sv === -1 ? "-" : tnum(sv)) + "t}") || "1";
      return pw + "\\cos " + (w === 1 ? "" : tnum(w)) + "t";
    }
    function eqTex() {
      var o = "y''", B = st.B, C = st.Cc;
      if (B !== 0) o += (B < 0 ? " - " : " + ") + (Math.abs(B) === 1 ? "" : tnum(Math.abs(B))) + "y'";
      if (C !== 0) o += (C < 0 ? " - " : " + ") + (Math.abs(C) === 1 ? "" : tnum(Math.abs(C))) + "y";
      var rhs;
      if (st.amp === 0) rhs = "0";
      else {
        var f = fTex(st.form, st.k, st.s, st.w);
        var a = Math.abs(st.amp);
        rhs = (st.amp < 0 ? "-" : "") + (a === 1 && f !== "" ? "" : tnum(a)) + f;
      }
      return o + " = " + rhs;
    }

    function updateRLC() {
      var Cv = Math.pow(10, st.Cexp);
      var Z = SM.impedance(st.R, st.L, Cv, st.omega);
      var i, v;
      // panel 1
      var g = P1.grid, tp = P1.top, H1 = P1.H, ph = H1 - Tp - P1.B, pw = W - L - Rr;
      clear(g); clear(tp);
      var m = niceStep(2 * Math.max(Z.re, Math.abs(Z.im), 1) * 1.1) * 4 / 2;
      m = Math.max(m, 1);
      var xl = -0.25 * m, xh = 1.25 * m;
      var X1 = function (x) { return L + pw * (x - xl) / (xh - xl); };
      var Y1 = function (y) { return Tp + ph * (m - y) / (2 * m); };
      var sx = niceStep(xh - xl), sy = niceStep(2 * m);
      for (v = Math.ceil(xl / sx) * sx; v <= xh + 1e-9; v += sx) {
        g.appendChild(s("line", { x1: X1(v), y1: Tp, x2: X1(v), y2: Tp + ph, "class": Math.abs(v) < sx / 2 ? "p-axis" : "p-grid" }));
        g.appendChild(s("text", { x: X1(v), y: Tp + ph + 14, "text-anchor": "middle", text: num(Math.abs(v) < sx / 2 ? 0 : v) }));
      }
      for (v = Math.ceil(-m / sy) * sy; v <= m + 1e-9; v += sy) {
        g.appendChild(s("line", { x1: L, y1: Y1(v), x2: W - Rr, y2: Y1(v), "class": Math.abs(v) < sy / 2 ? "p-axis" : "p-grid" }));
        g.appendChild(s("text", { x: L - 4, y: Y1(v) + 4, "text-anchor": "end", text: num(Math.abs(v) < sy / 2 ? 0 : v) }));
      }
      g.appendChild(s("text", { x: W - Rr, y: Tp + ph + 22, "text-anchor": "end", text: "Re Z" }));
      g.appendChild(s("text", { x: L + 4, y: Tp + 9, text: "Im Z" }));
      var ox = X1(0), oy = Y1(0), zx = X1(Z.re), zy = Y1(Z.im);
      tp.appendChild(s("line", { x1: ox, y1: oy, x2: zx, y2: oy, style: "stroke:var(--orange);stroke-width:2.4" }));
      tp.appendChild(s("line", { x1: zx, y1: oy, x2: zx, y2: zy, style: "stroke:var(--blue);stroke-width:2.4" }));
      tp.appendChild(s("line", { x1: ox, y1: oy, x2: zx, y2: zy, style: "stroke:var(--teal);stroke-width:3.4;stroke-linecap:round" }));
      tp.appendChild(s("circle", { cx: zx, cy: zy, r: 4.5, style: "fill:var(--teal)" }));
      var ang = Z.phase, ar = Math.min(26, Math.hypot(zx - ox, zy - oy) * 0.6);
      if (ar > 6 && Math.abs(ang) > 0.01) {
        tp.appendChild(s("path", { d: "M" + (ox + ar) + " " + oy + " A" + ar + " " + ar + " 0 0 " + (ang > 0 ? 0 : 1) + " " +
          (ox + ar * Math.cos(ang)).toFixed(2) + " " + (oy - ar * Math.sin(ang)).toFixed(2), fill: "none", style: "stroke:var(--pink);stroke-width:2" }));
      }
      var lx = (ox + zx) / 2 - 4, ly = (oy + zy) / 2 + (Z.im >= 0 ? -8 : 16);
      tp.appendChild(s("text", { x: lx, y: ly, "text-anchor": "middle", style: "fill:var(--teal);font-weight:600", text: "|Z| = " + num(Z.abs) }));
      tp.appendChild(s("text", { x: ox + ar + 6, y: oy + (ang >= 0 ? -4 : 13), style: "fill:var(--pink)", text: "φ = " + num(ang * 180 / Math.PI) + "°" }));
      cap1.textContent = "Orange: R along the real axis; blue: reactance ωL − 1/(ωC) up (inductive) or down (capacitive); teal: Z.";

      // panel 2
      var g2 = P2.grid, c2 = P2.top, H2 = P2.H, h2 = H2 - Tp - P2.B;
      clear(g2); clear(c2);
      var wl = 10, wh = 1000, pts = [], gmax = 0;
      for (i = 0; i <= 300; i++) {
        var w = wl * Math.pow(wh / wl, i / 300), q = 1 / SM.impedance(st.R, st.L, Cv, w).abs;
        pts.push([Math.log10(w), q]); gmax = Math.max(gmax, q);
      }
      var ytop = gmax * 1.1 || 1;
      var X2 = function (lw) { return L + pw * (lw - 1) / 2; };
      var Y2 = function (q) { return Tp + h2 * (1 - q / ytop); };
      [10, 100, 1000].forEach(function (wv) {
        g2.appendChild(s("line", { x1: X2(Math.log10(wv)), y1: Tp, x2: X2(Math.log10(wv)), y2: H2 - P2.B, "class": "p-grid" }));
        g2.appendChild(s("text", { x: X2(Math.log10(wv)), y: H2 - P2.B + 14, "text-anchor": "middle", text: String(wv) }));
      });
      var sg = niceStep(ytop);
      for (v = 0; v <= ytop + 1e-9; v += sg) {
        g2.appendChild(s("line", { x1: L, y1: Y2(v), x2: W - Rr, y2: Y2(v), "class": v === 0 ? "p-axis" : "p-grid" }));
        g2.appendChild(s("text", { x: L - 4, y: Y2(v) + 4, "text-anchor": "end", text: num(v) }));
      }
      g2.appendChild(s("text", { x: W - Rr, y: H2 - 2, "text-anchor": "end", text: "ω (log scale)" }));
      if (Z.w0 >= wl && Z.w0 <= wh) {
        c2.appendChild(s("line", { x1: X2(Math.log10(Z.w0)), y1: Tp, x2: X2(Math.log10(Z.w0)), y2: H2 - P2.B, style: "stroke:var(--blue);stroke-width:1.6;stroke-dasharray:5 4" }));
      }
      c2.appendChild(s("path", { d: pathOf(pts, X2, Y2, 1e3), fill: "none", style: "stroke:var(--teal);stroke-width:3;stroke-linejoin:round" }));
      var cur = 1 / Z.abs;
      c2.appendChild(s("circle", { cx: X2(Math.log10(st.omega)), cy: Y2(cur), r: 5.5, style: "fill:var(--orange)" }));
      cap2.textContent = "Peak current 1/R = " + num(1 / st.R) + " at ω₀ = 1/√(LC) = " + num(Z.w0) + (Z.w0 >= wl && Z.w0 <= wh ? "." : " (outside 10 to 1000).");

      // readouts
      texBox.textContent = "";
      factsBox.textContent = "";
      function fact(t, cls) {
        var el = ctx.mathText(h("p", { style: "margin:2px 0" }), t);
        if (cls) el.className = cls;
        factsBox.appendChild(el);
      }
      fact("$Z = " + tnum(Z.re) + (Z.im < 0 ? " - " : " + ") + tnum(Math.abs(Z.im)) + "i$, $|Z| = " + tnum(Z.abs) + "$, phase $= " + tnum(Z.phase * 180 / Math.PI) + "^\\circ$.");
      fact("$\\omega_0 = 1/\\sqrt{LC} = " + tnum(Z.w0) + "$; $|I| = 1/|Z| = " + tnum(cur) + "$ for $V = 1$.");
      var rel = Math.abs(Z.im) / Math.max(Z.abs, 1e-12);
      var word = rel < 0.01 ? "at resonance" : Z.im > 0 ? "inductor dominates" : "capacitor dominates";
      fact("Regime: " + word + ".", "plot-note");
    }

    function updateUC() {
      var sol = SM.ucSolve({ B: st.B, C: st.Cc, form: st.form, k: st.k, s: st.s, w: st.w, amp: st.amp });
      var i, v;
      texBox.textContent = "";
      factsBox.textContent = "";
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), eqTex()));
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), SM.trialTex(sol)));
      function fact(t, cls) {
        var el = ctx.mathText(h("p", { style: "margin:2px 0" }), t);
        if (cls) el.className = cls;
        factsBox.appendChild(el);
      }
      var m = sol.multiplicity;
      var inRoot = (st.form === "poly" ? "$s = 0$" : st.form === "exp" ? "$s = " + tnum(st.s) + "$" : "$s = i\\omega$");
      fact("Multiplicity of " + inRoot + " as a root of $P(s) = s^2 + Bs + C$: $m = " + m + "$.");
      if (m > 0) {
        fact("Resonance: the input exponent is a root of P(s): multiply the guess by " + (m === 2 ? "t²" : "t") + ".", "plot-note warn");
      }
      // solved y_p
      var re = sol.coeffs.map(function (c) { return c[0]; }), im = sol.coeffs.map(function (c) { return c[1]; });
      var ypTex;
      if (st.form === "cos") {
        var pr = polyTex(re), pi = polyTex(im), wt = (st.w === 1 ? "" : tnum(st.w)) + "t";
        var parts = [];
        if (pr.terms) parts.push((pr.terms > 1 ? "(" + pr.tex + ")" : pr.tex) + "\\cos " + wt);
        if (pi.terms) {
          var body = pi.terms > 1 ? "(" + pi.tex + ")" : pi.tex.replace(/^-/, "");
          var neg = pi.terms > 1 ? false : pi.tex.charAt(0) === "-";
          // y_p has -Im: sign flips
          if (pi.terms > 1) parts.push({ minus: true, t: body + "\\sin " + wt });
          else parts.push({ minus: !neg, t: body + "\\sin " + wt });
        }
        ypTex = "";
        parts.forEach(function (p, j) {
          if (typeof p === "string") ypTex += (j ? " + " : "") + p;
          else ypTex += (j ? (p.minus ? " - " : " + ") : (p.minus ? "-" : "")) + p.t;
        });
        if (!ypTex) ypTex = "0";
      } else {
        var pp = polyTex(re);
        ypTex = st.form === "exp" && st.s !== 0 && pp.tex !== "0"
          ? (pp.terms > 1 ? "(" + pp.tex + ")" : pp.tex) + "e^{" + (st.s === 1 ? "" : st.s === -1 ? "-" : tnum(st.s)) + "t}"
          : pp.tex;
      }
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), "y_p = " + ypTex));
      var res = 0;
      [0.5, 1, 1.5, 2].forEach(function (t) { res = Math.max(res, Math.abs(SM.residual(sol, st.B, st.Cc, t))); });
      fact("Check: max |y_p'' + By_p' + Cy_p − input| over t = 0.5, 1, 1.5, 2 is " + (res < 1e-4 ? "about 0" : res.toPrecision(2)) + " (finite-difference estimate).");

      // plot
      var g = P3.grid, c = P3.top, H = P3.H, hp = H - Tp - P3.B, pw = W - L - Rr;
      clear(g); clear(c);
      var n = 80, A = [], Bv = [], D = [], lo = Infinity, hi = -Infinity, clipped = false;
      function track(q) {
        if (!isFinite(q)) return;
        if (Math.abs(q) > CLIP) clipped = true;
        q = Math.max(-CLIP, Math.min(CLIP, q)); lo = Math.min(lo, q); hi = Math.max(hi, q);
      }
      for (i = 0; i <= n; i++) {
        var t = tMax * i / n, a = sol.yp(t), b = SM.convolution(st.B, st.Cc, sol.f, t, 200);
        A.push([t, a]); Bv.push([t, b]); D.push([t, a - b]);
        track(a); track(b); track(a - b);
      }
      if (!isFinite(lo)) { lo = -1; hi = 1; }
      lo = Math.min(lo, 0); hi = Math.max(hi, 0);
      var pad = 0.1 * Math.max(hi - lo, 0.5); lo -= pad; hi += pad;
      var X = function (tt) { return L + pw * tt / tMax; };
      var Y = function (yy) { return Tp + hp * (hi - yy) / (hi - lo); };
      for (i = 0; i <= 3; i++) {
        var tt = tMax * i / 3;
        g.appendChild(s("line", { x1: X(tt), y1: Tp, x2: X(tt), y2: H - P3.B, "class": "p-grid" }));
        g.appendChild(s("text", { x: X(tt), y: H - P3.B + 14, "text-anchor": "middle", text: num(tt) }));
      }
      var sy = niceStep(hi - lo);
      for (v = Math.ceil(lo / sy - 1e-9) * sy; v <= hi + 1e-9; v += sy) {
        var z0 = Math.abs(v) < sy / 2;
        g.appendChild(s("line", { x1: L, y1: Y(v), x2: W - Rr, y2: Y(v), "class": z0 ? "p-axis" : "p-grid" }));
        g.appendChild(s("text", { x: L - 4, y: Y(v) + 4, "text-anchor": "end", text: num(z0 ? 0 : v) }));
      }
      g.appendChild(s("text", { x: W - Rr, y: H - 2, "text-anchor": "end", text: "t" }));
      c.appendChild(s("path", { d: pathOf(D, X, Y, 1e3), fill: "none", style: "stroke:var(--pink);stroke-width:2;stroke-dasharray:6 4" }));
      c.appendChild(s("path", { d: pathOf(Bv, X, Y, 1e3), fill: "none", style: "stroke:var(--teal);stroke-width:2.6;stroke-linejoin:round" }));
      c.appendChild(s("path", { d: pathOf(A, X, Y, 1e3), fill: "none", style: "stroke:var(--green);stroke-width:3.2;stroke-linejoin:round;stroke-linecap:round" }));
      cap3.className = "plot-note" + (clipped ? " warn" : "");
      cap3.textContent = clipped
        ? "Values beyond ±" + CLIP + " are clipped; the curves grow very large."
        : "Green: y_p. Teal: solution from rest. Dashed pink: their difference, a null solution.";
    }

    function update() {
      var rlc = st.mode === "rlc";
      KEYS.forEach(function (k) { outputs[k].textContent = readout(k); });
      show(rlcControls, rlc); show(ucControls, !rlc);
      show(rows.s, !rlc && st.form === "exp"); show(rows.w, !rlc && st.form === "cos");
      show(box1, rlc); show(box2, rlc); show(box3, !rlc);
      if (rlc) updateRLC(); else updateUC();
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
