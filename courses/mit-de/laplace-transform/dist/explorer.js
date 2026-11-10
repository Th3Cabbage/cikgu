/*
 * Laplace-transform explorer: solve y' - a y = f or y'' + B y' + C y = f by Y(s) = N(s)/D(s),
 * partial fractions, and inverse transform; checked against an RK4 solution.
 * Maths comes from window.StudyMath (build, simulate, systemPoles).
 * Saved state: state.explorer = {order, input, a, B, C, c, omega, y0, v0}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["a", "B", "C", "c", "omega", "y0", "v0"];
  var CLIP = 100;

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function ids(list) { return list.map(function (m) { return m.id; }); }
  function defaults(config) {
    var out = { order: config.defaultOrder, input: config.defaultInput };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config || !Array.isArray(config.inputs) || !Array.isArray(config.orders)) return out;
    if (typeof saved.order === "string" && ids(config.orders).indexOf(saved.order) >= 0) out.order = saved.order;
    if (typeof saved.input === "string" && ids(config.inputs).indexOf(saved.input) >= 0) out.input = saved.input;
    KEYS.forEach(function (k) {
      var v = saved[k], c = config[k];
      if (typeof v === "number" && isFinite(v) && v >= c.min - 1e-9 && v <= c.max + 1e-9) out[k] = snap(v, c);
    });
    return out;
  }
  function stop() { /* no timers */ }

  // ---- number and TeX helpers ----
  function r3(v) { var r = Math.round(v * 1000) / 1000; return r === 0 ? 0 : r; }
  function num(v) { return String(r3(v)).replace("-", "−"); }
  function tn(v) { return String(r3(v)); }
  // sum of {c, body} terms as TeX; body "" is a constant term
  function joinTerms(list) {
    var out = "";
    list.forEach(function (t) {
      var c = r3(t.c);
      if (c === 0) return;
      var a = Math.abs(c), body = t.body;
      var mag = (a === 1 && body) ? "" : String(a);
      var piece = mag + body;
      if (!out) out = (c < 0 ? "-" : "") + piece;
      else out += (c < 0 ? " - " : " + ") + piece;
    });
    return out || "0";
  }
  function polyTex(coefs, v) {
    var list = [];
    for (var d = coefs.length - 1; d >= 0; d--) {
      list.push({ c: coefs[d][0], body: d === 0 ? "" : d === 1 ? v : v + "^{" + d + "}" });
    }
    return joinTerms(list);
  }
  function inputTexNum(p) {
    switch (p.input) {
      case "none": return "0";
      case "delta": return "1";
      case "step": return "\\frac{1}{s}";
      case "exp": return "\\frac{1}{" + joinTerms([{ c: 1, body: "s" }, { c: -p.c, body: "" }]) + "}";
      case "cos": return "\\frac{s}{s^2 + " + tn(p.omega * p.omega) + "}";
      default: return "\\frac{" + tn(p.omega) + "}{s^2 + " + tn(p.omega * p.omega) + "}";
    }
  }
  function cTex(z) {
    var re = r3(z[0]), im = r3(z[1]);
    if (im === 0) return tn(re);
    if (re === 0) return tn(im) + "i";
    return tn(re) + (im < 0 ? " - " : " + ") + tn(Math.abs(im)) + "i";
  }
  function polesTex(z) { return cTex(z); }
  function expBody(r, a) {
    var s = r === 0 ? "" : r === 1 ? "t" : "t^{" + r + "}";
    var ra = r3(a);
    if (ra !== 0) s += "e^{" + (ra === 1 ? "" : tn(ra)) + "t}";
    return s;
  }
  var uid = 0;

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var tMax = config.tMax || 10;
    var clipIds = [++uid, ++uid].map(function (n) { return "lx-clip-" + n; });

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "From the equation to Y(s) and back" }),
      ctx.mathText(h("p", { className: "lede" }), "Choose an order and an input. The transform turns the equation into $Y(s) = N(s)/D(s)$; the poles of $Y$ give the partial fractions, and each pole gives one piece of $y(t)$.")
    ]));

    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text, label) {
      var c = config[key], id = "lx-" + key;
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

    function radioSet(legend, name, list, key) {
      var box = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
        h("legend", { text: legend, style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
      ]);
      var map = {};
      list.forEach(function (m) {
        var id = "lx-" + name + "-" + m.id;
        var r = h("input", { type: "radio", name: "lx-" + name, id: id, value: m.id });
        r.checked = st[key] === m.id;
        r.addEventListener("change", function () {
          if (r.checked) { st[key] = m.id; update(); ctx.save(); ctx.announce(legend + ": " + m.label.replace(/\s+/g, " ")); }
        });
        map[m.id] = r;
        box.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
      });
      return { box: box, map: map };
    }
    var orderSet = radioSet("Order", "order", config.orders, "order");
    var inputSet = radioSet("Input f(t)", "input", config.inputs, "input");

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (orderSet.map[p.order]) { st.order = p.order; orderSet.map[p.order].checked = true; }
        if (inputSet.map[p.input]) { st.input = p.input; inputSet.map[p.input].checked = true; }
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note);
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    // the default state (second order, cos) shows B first
    var controls = h("div", null, [
      h("h2", { text: "Equation" }),
      slider("B", "Damping $B$", "Damping B"), slider("C", "Stiffness $C$", "Stiffness C"),
      slider("a", "Rate $a$", "Rate a"),
      slider("y0", "Start value $y_0$", "Start value y zero"), slider("v0", "Start velocity $v_0$", "Start velocity v zero"),
      slider("omega", "Frequency $\\omega$", "Input frequency omega"), slider("c", "Exponent $c$", "Input exponent c"),
      presets, orderSet.box, inputSet.box
    ]);

    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }
    var W = 360, L = 36, Rr = 10, Tp = 12;

    // panel: s-plane
    var H1 = 250, B1 = 24;
    var svg1 = s("svg", { viewBox: "0 0 " + W + " " + H1, role: "img", "aria-label": "Complex s-plane showing the system poles and the input poles" });
    var defs1 = s("defs"), clip1 = s("clipPath", { id: clipIds[0] });
    clip1.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H1 - Tp - B1 }));
    defs1.appendChild(clip1); svg1.appendChild(defs1);
    var grid1 = s("g"), top1 = s("g", { "clip-path": "url(#" + clipIds[0] + ")" });
    svg1.appendChild(grid1); svg1.appendChild(top1);
    var cap1 = h("p", { className: "plot-note" });
    var box1 = h("div", { className: "plot-box" }, [h("h3", { text: "Poles in the s-plane" }), svg1,
      h("div", { className: "legend" }, [h("span", null, [sw("var(--teal)"), "system poles"]), h("span", null, [sw("var(--orange)"), "input poles"])]), cap1]);

    // panel: partial fractions
    var pfList = h("div", { className: "readout" });
    var box2 = h("div", { className: "plot-box" }, [h("h3", { text: "Partial fractions" }), pfList]);

    // panel: y(t)
    var H3 = 250, B3 = 26;
    var svg3 = s("svg", { viewBox: "0 0 " + W + " " + H3, role: "img", "aria-label": "Plot of y of t: partial-fraction solution and the numerical solution dashed on top" });
    var defs3 = s("defs"), clip3 = s("clipPath", { id: clipIds[1] });
    clip3.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H3 - Tp - B3 }));
    defs3.appendChild(clip3); svg3.appendChild(defs3);
    var grid3 = s("g"), curve3 = s("g", { "clip-path": "url(#" + clipIds[1] + ")" });
    svg3.appendChild(grid3); svg3.appendChild(curve3);
    var note3 = h("p", { className: "plot-note" }), agree = h("p", { className: "plot-note", style: "font-weight:600" });
    var box3 = h("div", { className: "plot-box" }, [h("h3", { text: "y(t)" }), svg3,
      h("div", { className: "legend" }, [h("span", null, [sw("var(--green)"), "partial-fraction y(t)"]), h("span", null, [sw("var(--teal)"), "numerical RK4 (dashed)"])]),
      agree, note3]);

    var texBox = h("div", { className: "readout" }), yBox = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [texBox, yBox, box1, box2, box3, presetNote])])])
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
    function pathOf(arr, X, Y) {
      var d = "";
      arr.forEach(function (q, j) {
        var yy = Math.max(-1e3, Math.min(1e3, Y(q[1])));
        d += (j ? "L" : "M") + X(q[0]).toFixed(2) + " " + yy.toFixed(2) + " ";
      });
      return d;
    }
    function isNear(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-7; }

    // time-function TeX contributed by one pole group (conjugate pairs combined)
    function timeTex(G) {
      var im = G.p[1], a = G.p[0], pieces = [], r;
      if (Math.abs(im) < 1e-9) {
        var list = [];
        for (r = 0; r < G.m; r++) list.push({ c: G.tcoef[r][0], body: expBody(r, a) });
        return joinTerms(list);
      }
      var b = Math.abs(im), bs = (r3(b) === 1 ? "" : tn(b));
      for (r = 0; r < G.m; r++) {
        var kr = G.tcoef[r][0], ki = G.tcoef[r][1];
        var trig = joinTerms([{ c: 2 * kr, body: "\\cos " + bs + "t" }, { c: -2 * ki, body: "\\sin " + bs + "t" }]);
        if (trig === "0") continue;
        pieces.push(expBody(r, a) + "\\left(" + trig + "\\right)");
      }
      return pieces.length ? pieces.join(" + ") : "0";
    }

    function update() {
      var first = st.order === "first";
      var hasC = st.input === "exp", hasW = st.input === "cos" || st.input === "sin";
      var vis = { a: first, B: !first, C: !first, v0: !first, omega: hasW, c: hasC, y0: true };
      KEYS.forEach(function (k) {
        outputs[k].textContent = num(st[k]);
        rows[k].hidden = !vis[k];
        rows[k].style.display = vis[k] ? "" : "none";
      });
      var p = { order: st.order, input: st.input, a: st.a, B: st.B, C: st.C, c: st.c, omega: st.omega, y0: st.y0, v0: st.v0 };
      var bd = SM.build(p), sys = SM.systemPoles(p);
      var i, v;

      // ---- transformed equation and Y(s) ----
      var P = first ? [[-st.a, 0], [1, 0]] : [[st.C, 0], [st.B, 0], [1, 0]];
      var eq;
      if (first) eq = "\\left(" + polyTex(P, "s") + "\\right)Y - \\left(" + tn(st.y0) + "\\right) = " + inputTexNum(p);
      else eq = "\\left(" + polyTex(P, "s") + "\\right)Y - \\left(" + polyTex([[st.B, 0], [1, 0]], "s") + "\\right)\\left(" + tn(st.y0) +
        "\\right) - \\left(" + tn(st.v0) + "\\right) = " + inputTexNum(p);
      var general = first ? "(s - a)Y - y_0 = F(s)" : "(s^2 + Bs + C)Y - (s + B)y_0 - v_0 = F(s)";
      texBox.textContent = "";
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), general));
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), eq));
      yBox.textContent = "";
      yBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
        "Y(s) = \\frac{" + polyTex(bd.N, "s") + "}{" + polyTex(bd.D, "s") + "}"));

      // ---- s-plane ----
      clear(grid1); clear(top1);
      var rl = -5, rh = 3, il = 4.5;
      var pw = W - L - Rr, ph = H1 - Tp - B1;
      var X1 = function (re) { return L + pw * (re - rl) / (rh - rl); };
      var Y1 = function (im) { return Tp + ph * (il - im) / (2 * il); };
      grid1.appendChild(s("rect", { x: L, y: Tp, width: X1(0) - L, height: ph, style: "fill:var(--teal);opacity:0.08" }));
      for (v = -5; v <= 3; v++) {
        grid1.appendChild(s("line", { x1: X1(v), y1: Tp, x2: X1(v), y2: Tp + ph, "class": v === 0 ? "p-axis" : "p-grid" }));
        grid1.appendChild(s("text", { x: X1(v), y: Tp + ph + 14, "text-anchor": "middle", text: num(v) }));
      }
      for (v = -4; v <= 4; v += 2) {
        grid1.appendChild(s("line", { x1: L, y1: Y1(v), x2: W - Rr, y2: Y1(v), "class": v === 0 ? "p-axis" : "p-grid" }));
        grid1.appendChild(s("text", { x: L - 4, y: Y1(v) + 4, "text-anchor": "end", text: num(v) }));
      }
      grid1.appendChild(s("text", { x: W - Rr, y: Tp + ph + 22, "text-anchor": "end", text: "Re s" }));
      grid1.appendChild(s("text", { x: X1(0) + 4, y: Tp + 10, text: "imaginary axis (Im s)" }));
      grid1.appendChild(s("text", { x: L + 4, y: Tp + ph - 6, style: "opacity:0.7", text: "left half-plane: decay" }));
      var capParts = [];
      bd.poles.forEach(function (G) {
        var sc = 0;
        sys.forEach(function (z) { if (isNear(z, G.p)) sc++; });
        var isSys = sc > 0, alsoIn = G.m > sc;
        var x = X1(G.p[0]), y = Y1(G.p[1]);
        cross(top1, x, y, isSys ? "var(--teal)" : "var(--orange)", 6);
        if (isSys && alsoIn) top1.appendChild(s("circle", { cx: x, cy: y, r: 9, style: "fill:none;stroke:var(--orange);stroke-width:2" }));
        if (G.m > 1) top1.appendChild(s("text", { x: x + 9, y: y - 7, style: "font-weight:700;font-size:13px;fill:currentColor", text: String(G.m) }));
        capParts.push((isSys ? "system" : "input") + " pole " + tn(G.p[0]) + (Math.abs(G.p[1]) > 1e-9 ? (G.p[1] < 0 ? " − " : " + ") + tn(Math.abs(G.p[1])) + "i" : "") + (G.m > 1 ? " (x" + G.m + ")" : ""));
      });
      cap1.textContent = capParts.join("; ") + ".";
      svg1.setAttribute("aria-label", "Complex s-plane. Poles: " + capParts.join("; "));

      // ---- partial fractions ----
      pfList.textContent = "";
      bd.poles.forEach(function (G) {
        var im = G.p[1];
        if (im < -1e-9) return; // conjugate handled with its partner
        var complex = Math.abs(im) >= 1e-9, j, parts = [];
        for (j = 0; j < G.m; j++) {
          var k = G.m - j, den = "(s " + (G.p[0] > 0 ? "- " : "+ ") + tn(Math.abs(G.p[0])) + (complex ? (" - " + tn(im) + "i") : "") + ")";
          if (r3(G.p[0]) === 0 && !complex) den = "s";
          parts.push("$c_{" + k + "} = " + cTex(G.c[j]) + "$ on $1/" + den + (k > 1 ? "^{" + k + "}" : "") + "$");
        }
        var head = complex
          ? "Pole $" + polesTex(G.p) + "$ with its conjugate pole" + (G.m > 1 ? " (multiplicity " + G.m + ")" : "") + ": "
          : "Pole $" + polesTex(G.p) + "$ (multiplicity " + G.m + "): ";
        var line = head + "coefficient" + (G.m > 1 ? "s " : " ") + parts.join(", ") + ". ";
        var tt = timeTex(G);
        line += complex ? "Pair contributes $" + tt + "$." : "Contributes $" + tt + "$.";
        var el = ctx.mathText(h("p", { style: "margin:4px 0" }), line);
        pfList.appendChild(el);
      });

      // ---- y(t) ----
      clear(grid3); clear(curve3);
      var n = 300, yp = [], lo = Infinity, hi = -Infinity, clipped = false;
      for (i = 0; i <= n; i++) {
        var t = tMax * i / n, yt = bd.y(t);
        yp.push([t, yt]);
        if (isFinite(yt)) {
          if (Math.abs(yt) > CLIP) clipped = true;
          var q = Math.max(-CLIP, Math.min(CLIP, yt)); lo = Math.min(lo, q); hi = Math.max(hi, q);
        }
      }
      var sim = SM.simulate(p, tMax, 2000), maxd = 0;
      for (i = 0; i < sim.length; i++) {
        var ex = bd.y(sim[i][0]);
        if (Math.abs(ex) <= CLIP && Math.abs(sim[i][1]) <= CLIP) maxd = Math.max(maxd, Math.abs(ex - sim[i][1]));
      }
      var simPts = [];
      for (i = 0; i < sim.length; i += 5) simPts.push([sim[i][0], Math.max(-CLIP, Math.min(CLIP, sim[i][1]))]);
      yp = yp.map(function (q) { return [q[0], Math.max(-CLIP, Math.min(CLIP, q[1]))]; });
      if (!isFinite(lo)) { lo = -1; hi = 1; }
      lo = Math.min(lo, 0); hi = Math.max(hi, 0);
      var pad = 0.1 * Math.max(hi - lo, 0.5); lo -= pad; hi += pad;
      var h3 = H3 - Tp - B3;
      var X3 = function (tt) { return L + (W - L - Rr) * tt / tMax; };
      var Y3 = function (yy) { return Tp + h3 * (hi - yy) / (hi - lo); };
      for (i = 0; i <= 5; i++) {
        var tt = tMax * i / 5;
        grid3.appendChild(s("line", { x1: X3(tt), y1: Tp, x2: X3(tt), y2: H3 - B3, "class": "p-grid" }));
        grid3.appendChild(s("text", { x: X3(tt), y: H3 - B3 + 14, "text-anchor": "middle", text: num(tt) }));
      }
      var sy = niceStep(hi - lo);
      for (v = Math.ceil(lo / sy - 1e-9) * sy; v <= hi + 1e-9; v += sy) {
        var z0 = Math.abs(v) < sy / 2;
        grid3.appendChild(s("line", { x1: L, y1: Y3(v), x2: W - Rr, y2: Y3(v), "class": z0 ? "p-axis" : "p-grid" }));
        grid3.appendChild(s("text", { x: L - 4, y: Y3(v) + 4, "text-anchor": "end", text: num(z0 ? 0 : v) }));
      }
      grid3.appendChild(s("text", { x: W - Rr, y: H3 - 2, "text-anchor": "end", text: "t" }));
      curve3.appendChild(s("path", { d: pathOf(yp, X3, Y3), fill: "none", style: "stroke:var(--green);stroke-width:4;stroke-linejoin:round;stroke-linecap:round" }));
      curve3.appendChild(s("path", { d: pathOf(simPts, X3, Y3), fill: "none", style: "stroke:var(--teal);stroke-width:1.8;stroke-dasharray:5 4" }));
      var y00 = first ? st.y0 + (st.input === "delta" ? 1 : 0) : st.y0;
      curve3.appendChild(s("circle", { cx: X3(0), cy: Y3(y00), r: 4, style: "fill:var(--green)" }));
      agree.textContent = maxd < 1e-12 ? "Maximum difference below 1e-12: the two curves agree to 1e-12 or better."
        : "Maximum difference " + maxd.toExponential(1) + ": the curves agree to 1e-" + Math.max(0, Math.floor(-Math.log10(maxd))) + ".";
      note3.className = "plot-note" + (clipped ? " warn" : "");
      note3.textContent = clipped
        ? "Values beyond ±" + CLIP + " are clipped (the response grows very large); the difference is measured where |y| ≤ " + CLIP + "."
        : st.input === "delta" ? "The impulse adds 1 to the top derivative at t = 0; the curve shows t > 0."
        : "Green: inverse transform from partial fractions; dashed teal: RK4 solution of the same equation.";
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
