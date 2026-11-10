/*
 * Nonlinear first-order explorer: autonomous y' = f(y), y(0) = y0.
 * Maths comes from window.StudyMath (model, solve, logisticExact).
 * Saved state: state.explorer = {model, a, b, h, y0}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["a", "b", "h", "y0"];
  var KIND_COLOR = { stable: "var(--green, #2e9d5b)", unstable: "var(--red, #d64550)", undecided: "var(--orange, #e0a020)" };
  var KIND_WORD = { stable: "stable", unstable: "unstable", undecided: "undecided (semi-stable)" };

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function modelIds(config) { return config.models.map(function (m) { return m.id; }); }
  function defaults(config) {
    var out = { model: config.defaultModel };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config || !Array.isArray(config.models)) return out;
    if (typeof saved.model === "string" && modelIds(config).indexOf(saved.model) >= 0) out.model = saved.model;
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
    var tMax = config.tMax || 8, yr = config.yRange || [-2, 3];
    var yLo = yr[0], yHi = yr[1];
    var clipId = "ex-clip-" + (++uid), clipId2 = "ex-clip-" + (++uid);

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Where does y' = f(y) send a solution?" }),
      ctx.mathText(h("p", { className: "lede" }), "Pick a model, move the sliders and the start value $y_0$. The sign of $f(y)$ decides whether $y$ rises or falls; steady states are the zeros of $f$.")
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
      h("legend", { text: "Model", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    config.models.forEach(function (m) {
      var id = "ex-model-" + m.id;
      var r = h("input", { type: "radio", name: "ex-model", id: id, value: m.id });
      r.checked = st.model === m.id;
      r.addEventListener("change", function () {
        if (r.checked) { st.model = m.id; update(); ctx.save(); ctx.announce("Model: " + m.label.replace(/\s+/g, " ")); }
      });
      radios[m.id] = r;
      kindBox.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
    });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (radios[p.model]) { st.model = p.model; radios[p.model].checked = true; }
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note);
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var controls = h("div", null, [
      h("h2", { text: "Equation" }), presets, kindBox,
      slider("a", "Growth rate $a$", "Growth rate a"), slider("b", "Crowding $b$", "Crowding b"),
      slider("h", "Harvest $h$", "Harvest h"), slider("y0", "Start value $y_0$", "Start value y zero")
    ]);

    // panel 1: f(y) and the stability line
    var W = 360, H1 = 250, L = 34, Rr = 10, Tp = 12;
    var plotBottom = H1 - 62;
    var svg1 = s("svg", { viewBox: "0 0 " + W + " " + H1, role: "img", "aria-label": "Plot of f of y with steady states, and the stability line beneath it" });
    var defs1 = s("defs"), clip1 = s("clipPath", { id: clipId });
    clip1.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: plotBottom - Tp }));
    defs1.appendChild(clip1); svg1.appendChild(defs1);
    var grid1 = s("g"), curve1 = s("g", { "clip-path": "url(#" + clipId + ")" }), top1 = s("g");
    svg1.appendChild(grid1); svg1.appendChild(curve1); svg1.appendChild(top1);
    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }
    var legend1 = h("div", { className: "legend" }, [
      h("span", null, [sw(KIND_COLOR.stable), "stable"]),
      h("span", null, [sw(KIND_COLOR.unstable), "unstable"]),
      h("span", null, [sw(KIND_COLOR.undecided), "undecided"]),
      h("span", null, [sw("var(--blue)"), "start y₀"])
    ]);
    var box1 = h("div", { className: "plot-box" }, [h("h3", { text: "f(y) and the stability line" }), svg1, legend1]);

    // panel 2: y(t)
    var H2 = 230, B = 26;
    var svg2 = s("svg", { viewBox: "0 0 " + W + " " + H2, role: "img", "aria-label": "Plot of the solution y of t with steady states as dashed lines" });
    var defs2 = s("defs"), clip2 = s("clipPath", { id: clipId2 });
    clip2.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H2 - Tp - B }));
    defs2.appendChild(clip2); svg2.appendChild(defs2);
    var grid2 = s("g"), curve2 = s("g", { "clip-path": "url(#" + clipId2 + ")" });
    svg2.appendChild(grid2); svg2.appendChild(curve2);
    var note2 = h("p", { className: "plot-note" });
    var box2 = h("div", { className: "plot-box" }, [h("h3", { text: "Solution y(t)" }), svg2, note2]);

    var texBox = h("div", { className: "readout" }), factsBox = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [box1, box2, presetNote, texBox, factsBox])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function niceStep(span) {
      var step = Math.pow(10, Math.floor(Math.log10(span / 4))), m = span / 4 / step;
      return step * (m > 5 ? 10 : m > 2 ? 5 : m > 1 ? 2 : 1);
    }
    function pts(arr) { return arr.map(function (q) { return q.join(","); }).join(" "); }

    function update() {
      var mdef = config.models[modelIds(config).indexOf(st.model)];
      KEYS.forEach(function (k) {
        outputs[k].textContent = num(st[k]);
        var show = k === "y0" || mdef.params.indexOf(k) >= 0;
        rows[k].hidden = !show;
        rows[k].style.display = show ? "" : "none";
      });
      var p = { model: st.model, a: st.a, b: st.b, h: st.h };
      var M = SM.model(p);
      var sol = SM.solve(p, st.y0, tMax, 0.01);
      var i, yv;

      // ---- panel 1 ----
      clear(grid1); clear(curve1); clear(top1);
      var N = 200, fs = [], fLo = 0, fHi = 0;
      for (i = 0; i <= N; i++) {
        var y = yLo + (yHi - yLo) * i / N, fv = M.f(y);
        fs.push([y, fv]); fLo = Math.min(fLo, fv); fHi = Math.max(fHi, fv);
      }
      var padF = 0.1 * Math.max(fHi - fLo, 1e-6); fLo -= padF; fHi += padF;
      var X1 = function (yy) { return L + (W - L - Rr) * (yy - yLo) / (yHi - yLo); };
      var F1 = function (f) { return Tp + (plotBottom - Tp) * (fHi - f) / (fHi - fLo); };
      var sx = niceStep(yHi - yLo);
      for (yv = Math.ceil(yLo / sx - 1e-9) * sx; yv <= yHi + 1e-9; yv += sx) {
        grid1.appendChild(s("line", { x1: X1(yv), y1: Tp, x2: X1(yv), y2: plotBottom, "class": "p-grid" }));
        grid1.appendChild(s("text", { x: X1(yv), y: plotBottom + 12, "text-anchor": "middle", text: num(Math.abs(yv) < sx / 2 ? 0 : yv) }));
      }
      var sf = niceStep(fHi - fLo);
      for (var fy = Math.ceil(fLo / sf) * sf; fy <= fHi + 1e-9; fy += sf) {
        if (Math.abs(fy) < sf / 2) continue;
        grid1.appendChild(s("line", { x1: L, y1: F1(fy), x2: W - Rr, y2: F1(fy), "class": "p-grid" }));
        grid1.appendChild(s("text", { x: L - 4, y: F1(fy) + 4, "text-anchor": "end", text: num(fy) }));
      }
      grid1.appendChild(s("line", { x1: L, y1: F1(0), x2: W - Rr, y2: F1(0), "class": "p-axis" }));
      grid1.appendChild(s("text", { x: L - 4, y: F1(0) + 4, "text-anchor": "end", text: "0" }));
      grid1.appendChild(s("text", { x: L + 4, y: Tp + 9, text: "f(y)" }));
      var d1 = "";
      fs.forEach(function (q, j) { d1 += (j ? "L" : "M") + X1(q[0]).toFixed(2) + " " + F1(q[1]).toFixed(2) + " "; });
      curve1.appendChild(s("path", { d: d1, fill: "none", style: "stroke:var(--teal);stroke-width:3;stroke-linejoin:round" }));
      var inRange = M.steady.filter(function (e) { return e.Y >= yLo - 1e-9 && e.Y <= yHi + 1e-9; });
      inRange.forEach(function (e) {
        top1.appendChild(s("circle", { cx: X1(e.Y), cy: F1(0), r: 5, style: "fill:" + KIND_COLOR[e.kind] + ";stroke:var(--bg, #fff);stroke-width:1.5" }));
      });

      // stability line
      var ly = plotBottom + 36;
      top1.appendChild(s("line", { x1: L, y1: ly, x2: W - Rr, y2: ly, "class": "p-axis" }));
      top1.appendChild(s("text", { x: L - 4, y: ly + 4, "text-anchor": "end", text: "y" }));
      var cuts = [yLo];
      inRange.forEach(function (e) { if (e.Y > yLo + 1e-9 && e.Y < yHi - 1e-9) cuts.push(e.Y); });
      cuts.push(yHi);
      for (i = 0; i + 1 < cuts.length; i++) {
        var fm = M.f((cuts[i] + cuts[i + 1]) / 2), xa = X1(cuts[i]), xb = X1(cuts[i + 1]);
        if (xb - xa < 14 || Math.abs(fm) < 1e-12) continue;
        var cx = (xa + xb) / 2, dir = fm > 0 ? 1 : -1, hw = Math.min(16, (xb - xa) / 2 - 4);
        var col = "var(--text, currentColor)";
        top1.appendChild(s("line", { x1: cx - dir * hw, y1: ly - 9, x2: cx + dir * (hw - 4), y2: ly - 9, style: "stroke:" + col + ";stroke-width:2" }));
        top1.appendChild(s("polygon", { points: pts([[cx + dir * (hw + 2), ly - 9], [cx + dir * (hw - 6), ly - 13], [cx + dir * (hw - 6), ly - 5]]), style: "fill:" + col }));
      }
      inRange.forEach(function (e) {
        top1.appendChild(s("circle", { cx: X1(e.Y), cy: ly, r: 5, style: "fill:" + KIND_COLOR[e.kind] + ";stroke:var(--bg, #fff);stroke-width:1.5" }));
        top1.appendChild(s("text", { x: X1(e.Y), y: ly + 17, "text-anchor": "middle", text: num(e.Y) }));
      });
      var x0 = X1(st.y0);
      top1.appendChild(s("line", { x1: x0, y1: Tp, x2: x0, y2: ly - 12, style: "stroke:var(--blue);stroke-width:1.4;stroke-dasharray:3 3" }));
      top1.appendChild(s("polygon", { points: pts([[x0, ly - 1], [x0 - 5, ly - 11], [x0 + 5, ly - 11]]), style: "fill:var(--blue)" }));

      // ---- panel 2 ----
      clear(grid2); clear(curve2);
      var X2 = function (t) { return L + (W - L - Rr) * t / tMax; };
      var Y2 = function (yy) { return Tp + (H2 - Tp - B) * (yHi - yy) / (yHi - yLo); };
      for (i = 0; i <= 4; i++) {
        var tt = tMax * i / 4;
        grid2.appendChild(s("line", { x1: X2(tt), y1: Tp, x2: X2(tt), y2: H2 - B, "class": "p-grid" }));
        grid2.appendChild(s("text", { x: X2(tt), y: H2 - B + 14, "text-anchor": "middle", text: num(tt) }));
      }
      for (yv = Math.ceil(yLo / sx - 1e-9) * sx; yv <= yHi + 1e-9; yv += sx) {
        var z = Math.abs(yv) < sx / 2;
        grid2.appendChild(s("line", { x1: L, y1: Y2(yv), x2: W - Rr, y2: Y2(yv), "class": z ? "p-axis" : "p-grid" }));
        grid2.appendChild(s("text", { x: L - 4, y: Y2(yv) + 4, "text-anchor": "end", text: num(z ? 0 : yv) }));
      }
      grid2.appendChild(s("text", { x: W - Rr, y: H2 - 2, "text-anchor": "end", text: "t" }));
      inRange.forEach(function (e) {
        curve2.appendChild(s("line", { x1: L, y1: Y2(e.Y), x2: W - Rr, y2: Y2(e.Y), style: "stroke:" + KIND_COLOR[e.kind] + ";stroke-width:1.6;stroke-dasharray:6 4" }));
      });
      var d2 = "", leave = null;
      sol.points.forEach(function (q, j) {
        if (leave === null && (q[1] < yLo - 1e-9 || q[1] > yHi + 1e-9)) leave = q[0];
        var yy = Math.max(-1e3, Math.min(1e3, Y2(q[1])));
        d2 += (j ? "L" : "M") + X2(q[0]).toFixed(2) + " " + yy.toFixed(2) + " ";
      });
      curve2.appendChild(s("path", { d: d2, fill: "none", style: "stroke:var(--teal);stroke-width:3.2;stroke-linejoin:round;stroke-linecap:round" }));
      curve2.appendChild(s("circle", { cx: X2(0), cy: Y2(st.y0), r: 4, style: "fill:var(--blue)" }));
      var last = sol.points[sol.points.length - 1];
      if (sol.blowup && leave === null) leave = last[0];
      note2.className = "plot-note" + (leave !== null ? " warn" : "");
      note2.textContent = leave !== null
        ? "leaves the plotted range at t ≈ " + num(leave) + (sol.blowup ? " (blow-up in finite time)" : "") + "; the curve is clipped."
        : "Dashed lines are steady states (green stable, red unstable, amber undecided). The solution is computed by RK4.";

      // ---- readouts ----
      texBox.textContent = "";
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), M.tex + ",\\ \\ y(0) = " + tnum(st.y0)));

      factsBox.textContent = "";
      function fact(t) { factsBox.appendChild(ctx.mathText(h("p", { style: "margin:2px 0" }), t)); }
      if (M.steady.length === 0) {
        fact("No steady states: $h > a^2/4b = " + tnum(st.a * st.a / (4 * st.b)) + "$, so the population collapses (y decreases from every start value).");
      }
      M.steady.forEach(function (e) {
        fact("Steady state $Y = " + tnum(e.Y) + "$: $f'(Y) = " + tnum(e.slope) + "$, " + KIND_WORD[e.kind] + ".");
      });
      if (sol.blowup) {
        fact("RK4 stops at $t \\approx " + tnum(last[0]) + "$ because $|y|$ exceeds " + SM.LIMIT + ".");
      } else {
        fact("RK4: $y(" + tMax + ") = " + tnum(last[1]) + "$");
      }
      if (st.model === "logistic") {
        var ex = SM.logisticExact(st.a, st.b, st.y0, tMax);
        if (isFinite(ex)) fact("Exact $a/(b + d e^{-at})$ at $t = " + tMax + "$: $" + tnum(ex) + "$.");
        else fact("Exact solution: the denominator $b + d e^{-at}$ reaches $0$ before $t = " + tMax + "$, so the solution blows up and has no value there.");
      }
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
