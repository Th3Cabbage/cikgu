/*
 * First-order linear explorer: y' = a y + q(t), y(0) = y0, 0 <= t <= tMax.
 * All formulas come from window.StudyMath.response(). Saved state:
 * state.explorer = {kind, a, y0, amp, s, omega, T}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["a", "y0", "amp", "s", "omega", "T"];
  var KIND_LABEL = { constant: "Constant", exp: "Exponential e^(st)", cos: "Cosine cos(ωt)", step: "Step H(t − T)", delta: "Delta δ(t − T)" };
  var KIND_TEX = { constant: "q = A", exp: "q = A e^{st}", cos: "q = A\\cos(\\omega t)", step: "q = A\\,H(t - T)", delta: "q = A\\,\\delta(t - T)" };
  var SHOWS = {
    a: function () { return true; }, y0: function () { return true; }, amp: function () { return true; },
    s: function (k) { return k === "exp"; }, omega: function (k) { return k === "cos"; },
    T: function (k) { return k === "step" || k === "delta"; }
  };
  var YCLAMP = 20;

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function defaults(config) {
    var out = { kind: config.defaultInput };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    if (!saved || typeof saved !== "object" || !config || !config.a || !Array.isArray(config.inputs)) return null;
    if (typeof saved.kind !== "string" || config.inputs.indexOf(saved.kind) < 0) return null;
    var out = { kind: saved.kind };
    for (var i = 0; i < KEYS.length; i++) {
      var k = KEYS[i], v = saved[k], c = config[k];
      if (typeof v !== "number" || !isFinite(v) || v < c.min - 1e-9 || v > c.max + 1e-9) return null;
      out[k] = snap(v, c);
    }
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
    var st = ctx.state.explorer || defaults(config);
    ctx.state.explorer = st;
    var tMax = config.tMax || 10;
    var W = 360, H = 250, L = 34, Rr = 10, Tp = 12, B = 26;
    var clipId = "ex-clip-" + (++uid);

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "How does y respond to the input q(t)?" }),
      ctx.mathText(h("p", { className: "lede" }), "Solve $y' = ay + q(t)$ with $y(0) = y_0$: pick an input, move the sliders, and watch the null part $y_0e^{at}$ and the driven part add up to $y(t)$.")
    ]));

    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text) {
      var c = config[key], id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      var out = h("output", { "for": id, text: num(st[key]) });
      inp.addEventListener("input", function () { st[key] = snap(parseFloat(inp.value), c); update(); ctx.save(); });
      inputs[key] = inp; outputs[key] = out;
      var row = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
      rows[key] = row;
      return row;
    }

    // input-kind selector (radio group)
    var radios = {};
    function setKind(k) { st.kind = k; if (radios[k]) radios[k].checked = true; }
    var kindBox = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "Input q(t)", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    config.inputs.forEach(function (k) {
      var id = "ex-kind-" + k;
      var r = h("input", { type: "radio", name: "ex-kind", id: id, value: k });
      r.checked = st.kind === k;
      r.addEventListener("change", function () { if (r.checked) { st.kind = k; update(); ctx.save(); } });
      radios[k] = r;
      kindBox.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: KIND_LABEL[k] || k })]));
    });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (config.inputs.indexOf(p.input) >= 0) setKind(p.input);
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note);
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var controls = h("div", null, [
      h("h2", { text: "Equation" }), presets, kindBox,
      slider("a", "Growth rate $a$"), slider("y0", "Start value $y_0$"), slider("amp", "Input size $A$"),
      slider("s", "Exponent $s$"), slider("omega", "Frequency $\\omega$"), slider("T", "Switch time $T$")
    ]);

    // plot
    var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Plot of the input, null part, driven part and total solution against time" });
    var defs = s("defs"), clip = s("clipPath", { id: clipId });
    clip.appendChild(s("rect", { x: L, y: Tp, width: W - L - Rr, height: H - Tp - B }));
    defs.appendChild(clip); svg.appendChild(defs);
    var gridLayer = s("g"), curveLayer = s("g", { "clip-path": "url(#" + clipId + ")" }), topLayer = s("g");
    svg.appendChild(gridLayer); svg.appendChild(curveLayer); svg.appendChild(topLayer);
    var plotNote = h("p", { className: "plot-note" });
    function sw(color, extra) { return h("span", { className: "sw", style: "background:" + color + (extra || "") }); }
    var legend = h("div", { className: "legend" }, [
      h("span", null, [sw("var(--pink)", ";opacity:.8"), "null part y₀e^(at)"]),
      h("span", null, [sw("var(--blue)"), "driven part"]),
      h("span", null, [sw("var(--teal)", ";height:5px"), "total y(t)"]),
      h("span", null, [sw("var(--muted)", ";height:1.5px"), "input q(t)"])
    ]);
    var plotBox = h("div", { className: "plot-box" }, [h("h3", { text: "Solution on 0 ≤ t ≤ " + tMax }), svg, legend, plotNote]);

    var texBox = h("div", { className: "readout" }), factsBox = h("div", { className: "readout" }), badge = h("p", { className: "verdict" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [plotBox, presetNote, texBox, badge, factsBox])])])
    ]));

    function pathD(pts, X, Y, lo, hi) {
      var d = "", pen = false, big = 1e3;
      pts.forEach(function (p, i) {
        var y = p[1];
        if (!isFinite(y)) { pen = false; return; }
        var yy = Math.max(-big, Math.min(big, Y(y)));
        d += (pen ? "L" : "M") + X(p[0]).toFixed(2) + " " + yy.toFixed(2) + " ";
        pen = true;
      });
      return d;
    }
    function curve(d, color, w, dash, op) {
      var a = { d: d, fill: "none", style: "stroke:" + color + ";stroke-width:" + w + ";stroke-linejoin:round;stroke-linecap:round" + (op ? ";opacity:" + op : "") };
      if (dash) a["stroke-dasharray"] = dash;
      return s("path", a);
    }

    function update() {
      KEYS.forEach(function (k) {
        outputs[k].textContent = num(st[k]);
        var show = SHOWS[k](st.kind);
        rows[k].hidden = !show;
        rows[k].style.display = show ? "" : "none";
      });
      var p = { kind: st.kind, a: st.a, y0: st.y0, amp: st.amp, s: st.s, omega: st.omega, T: st.T };
      var R = SM.response(p);

      // sample times (duplicate T so jumps are vertical)
      var N = 400, ts = [], i;
      for (i = 0; i <= N; i++) ts.push(tMax * i / N);
      if ((st.kind === "step" || st.kind === "delta") && st.T > 0 && st.T < tMax) ts.push(st.T - 1e-9, st.T);
      ts.sort(function (x, y) { return x - y; });
      function pts(f) { return ts.map(function (t) { return [t, f(t)]; }); }
      var nullP = pts(R.nullPart), drvP = pts(R.drivenPart), totP = pts(R.total);
      var inP = pts(function (t) { return SM.input(p, t); });
      var steadyP = (st.kind === "cos" && st.a < 0) ? pts(R.steadyPart) : null;

      // y range from curves that carry the solution
      var lo = 0, hi = 0;
      [nullP, drvP, totP].concat(steadyP ? [steadyP] : []).forEach(function (arr) { arr.forEach(function (q) { if (isFinite(q[1])) { lo = Math.min(lo, q[1]); hi = Math.max(hi, q[1]); } }); });
      // the input only sets the range when it is modest (<= 2x the solution span, min 2); otherwise it is clipped
      var cap = Math.max(2, 2 * (hi - lo));
      inP.forEach(function (q) { if (Math.abs(q[1]) <= cap) { lo = Math.min(lo, q[1]); hi = Math.max(hi, q[1]); } });
      if (st.kind === "delta") { lo = Math.min(lo, st.amp); hi = Math.max(hi, st.amp); }
      var span0 = Math.max(hi - lo, 1e-6);
      var padd = 0.1 * span0;
      var yLo = Math.max(-YCLAMP, lo - padd), yHi = Math.min(YCLAMP, hi + padd);
      if (yHi - yLo < 1) { var mid = (yHi + yLo) / 2; yLo = mid - 0.5; yHi = mid + 0.5; }
      var off = lo < yLo - 1e-9 || hi > yHi + 1e-9;
      var X = function (t) { return L + (W - L - Rr) * t / tMax; };
      var Y = function (y) { return Tp + (H - Tp - B) * (yHi - y) / (yHi - yLo); };

      // axes and grid
      while (gridLayer.firstChild) gridLayer.removeChild(gridLayer.firstChild);
      while (curveLayer.firstChild) curveLayer.removeChild(curveLayer.firstChild);
      while (topLayer.firstChild) topLayer.removeChild(topLayer.firstChild);
      for (i = 0; i <= 5; i++) {
        var tt = tMax * i / 5;
        gridLayer.appendChild(s("line", { x1: X(tt), y1: Tp, x2: X(tt), y2: H - B, "class": "p-grid" }));
        gridLayer.appendChild(s("text", { x: X(tt), y: H - B + 14, "text-anchor": "middle", text: num(tt) }));
      }
      var step = Math.pow(10, Math.floor(Math.log10((yHi - yLo) / 4))), m = (yHi - yLo) / 4 / step;
      step *= m > 5 ? 10 : m > 2 ? 5 : m > 1 ? 2 : 1;
      for (var yv = Math.ceil(yLo / step) * step; yv <= yHi + 1e-9; yv += step) {
        var near0 = Math.abs(yv) < step / 2;
        gridLayer.appendChild(s("line", { x1: L, y1: Y(yv), x2: W - Rr, y2: Y(yv), "class": near0 ? "p-axis" : "p-grid" }));
        gridLayer.appendChild(s("text", { x: L - 4, y: Y(yv) + 4, "text-anchor": "end", text: num(near0 ? 0 : yv) }));
      }
      gridLayer.appendChild(s("text", { x: W - Rr, y: H - 2, "text-anchor": "end", text: "t" }));
      if (st.kind === "step" || st.kind === "delta") {
        gridLayer.appendChild(s("line", { x1: X(st.T), y1: Tp, x2: X(st.T), y2: H - B, "class": "p-axis", "stroke-dasharray": "2 3" }));
      }

      // curves
      curveLayer.appendChild(curve(pathD(inP, X, Y), "var(--muted)", 1.2, null, 0.8));
      if (steadyP) curveLayer.appendChild(curve(pathD(steadyP, X, Y), "var(--teal)", 1.4, "1 4", 0.7));
      curveLayer.appendChild(curve(pathD(nullP, X, Y), "var(--pink)", 2, "6 4"));
      curveLayer.appendChild(curve(pathD(drvP, X, Y), "var(--blue)", 2.2));
      curveLayer.appendChild(curve(pathD(totP, X, Y), "var(--teal)", 3.6));

      if (st.kind === "delta") {
        var tx = X(st.T), y0p = Y(0), y1p = Y(st.amp);
        if (Math.abs(st.amp) > 1e-9) {
          var dir = st.amp > 0 ? 1 : -1, ytip = Math.max(Tp + 2, Math.min(H - B - 2, y1p));
          topLayer.appendChild(s("line", { x1: tx, y1: y0p, x2: tx, y2: ytip, style: "stroke:var(--orange);stroke-width:2.4" }));
          topLayer.appendChild(s("polygon", { points: [[tx, ytip], [tx - 4, ytip + 7 * dir], [tx + 4, ytip + 7 * dir]].map(function (q) { return q.join(","); }).join(" "), style: "fill:var(--orange)" }));
          topLayer.appendChild(s("text", { x: Math.min(tx + 5, W - 40), y: Math.max(Tp + 10, Math.min(H - B - 4, (y0p + ytip) / 2)), style: "fill:var(--orange)", text: "δ" }));
        }
      }
      plotNote.className = "plot-note" + (off ? " warn" : "");
      plotNote.textContent = off
        ? "Off scale: some curves leave the plotted range ±" + YCLAMP + " and are clipped, not squashed."
        : "Vertical axis fits the curves. Dashed pink = null part; blue = driven part (starts at 0); thick teal = their sum.";

      // readouts
      texBox.textContent = "";
      var eq = "y' = " + tnum(st.a) + "\\,y + q(t),\\ \\ y(0) = " + tnum(st.y0) + ",\\ \\ " + KIND_TEX[st.kind];
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), eq));
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), R.tex));
      texBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), "y = y_0e^{at} + y_{vp}"));

      if (R.resonance) {
        badge.setAttribute("data-kind", "marginal");
        badge.textContent = "Resonance (s = a): factor t";
      } else if (st.kind === "cos" && st.a >= 0) {
        badge.setAttribute("data-kind", "unstable");
        badge.textContent = "a ≥ 0: the null part does not die away";
      } else if (R.steady !== null) {
        badge.setAttribute("data-kind", "stable");
        badge.textContent = "a < 0: settles to the steady state " + num(R.steady);
      } else {
        badge.setAttribute("data-kind", "drift");
        badge.textContent = st.kind === "delta" ? "Impulse: y jumps by A at t = T" : "";
      }
      badge.hidden = !badge.textContent;

      var facts = [];
      if (st.kind === "cos") {
        var c = R.cos, deg = c.alpha * 180 / Math.PI;
        facts.push("$M = " + tnum(c.M) + "$, $N = " + tnum(c.N) + "$, $G = " + tnum(c.G) + "$, $\\alpha = " + tnum(c.alpha) + "\\text{ rad} = " + tnum(deg) + "^\\circ$");
        if (st.a < 0) facts.push("Steady oscillation $AG\\cos(\\omega t-\\alpha)$ is the faint dotted curve; its amplitude is $" + tnum(st.amp * c.G) + "$.");
      }
      if ((st.kind === "constant" || st.kind === "step") && R.steady !== null) facts.push("Steady state $-A/a = " + tnum(R.steady) + "$.");
      if (st.kind === "delta") {
        var tj = st.T;
        facts.push("Jump at $t = " + tnum(tj) + "$: $y$ goes from $" + tnum(R.nullPart(tj)) + "$ to $" + tnum(R.total(tj)) + "$ (change $A = " + tnum(st.amp) + "$).");
      }
      facts.push("$y(" + tMax + ") = " + tnum(R.total(tMax)) + "$");
      factsBox.textContent = "";
      facts.forEach(function (f) { factsBox.appendChild(ctx.mathText(h("p", { style: "margin:2px 0" }), f)); });
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
