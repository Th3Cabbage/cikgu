/*
 * Numerical methods explorer (Unit 11): watch Euler, midpoint, Heun, RK4, ode23 (BS23), ode45
 * (Dormand-Prince) and backward Euler take their steps, stage by stage.
 * Maths comes from window.StudyMath (problem, step, integrate, orderExperiment).
 * Saved state: state.explorer = {method, problem, h, logTol, delta, mu, view}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var NUMKEYS = ["h", "logTol", "delta", "mu"];
  var STAGE_COLORS = ["var(--blue)", "var(--orange)", "var(--pink)", "var(--yellow)", "#8b5cf6", "#0ea5e9", "#a3a3a3"];
  var timer = 0, raf = 0;

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function ids(list) { return list.map(function (m) { return m.id; }); }
  function defaults(config) {
    var out = { method: "euler", problem: "exp2", view: "time" };
    NUMKEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config) return out;
    if (ids(config.methods).indexOf(saved.method) >= 0) out.method = saved.method;
    if (ids(config.problems).indexOf(saved.problem) >= 0) out.problem = saved.problem;
    if (saved.view === "time" || saved.view === "phase") out.view = saved.view;
    NUMKEYS.forEach(function (k) {
      var v = saved[k], c = config[k];
      if (typeof v === "number" && isFinite(v) && v >= c.min - 1e-9 && v <= c.max + 1e-9) out[k] = snap(v, c);
    });
    return out;
  }
  function stop() {
    if (timer) { clearInterval(timer); timer = 0; }
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
  }

  function num(v, p) {
    if (v === null || v === undefined) return "–";
    if (!isFinite(v)) return v > 0 ? "∞" : v < 0 ? "−∞" : "NaN";
    if (v === 0) return "0";
    var a = Math.abs(v), r;
    if (a >= 1e5 || a < 1e-3) r = v.toExponential(p ? p - 1 : 2);
    else r = String(+v.toPrecision(p || 4));
    return r.replace("-", "−");
  }
  function reducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  var METHOD_TEX = {
    euler: ["s_1 = f(t_n, y_n)", "y_{n+1} = y_n + h\\,s_1"],
    midpoint: ["s_1 = f(t_n, y_n),\\quad s_2 = f\\!\\left(t_n + \\tfrac h2,\\ y_n + \\tfrac h2 s_1\\right)", "y_{n+1} = y_n + h\\,s_2"],
    heun: ["s_1 = f(t_n, y_n),\\quad s_2 = f(t_n + h,\\ y_n + h s_1)", "y_{n+1} = y_n + \\tfrac h2(s_1 + s_2)"],
    rk4: ["s_1 = f(t_n, y_n),\\ s_2 = f(t_n + \\tfrac h2, y_n + \\tfrac h2 s_1),\\ s_3 = f(t_n + \\tfrac h2, y_n + \\tfrac h2 s_2),\\ s_4 = f(t_n + h, y_n + h s_3)",
          "y_{n+1} = y_n + \\tfrac h6\\,(s_1 + 2s_2 + 2s_3 + s_4)"],
    bs23: ["s_2 = f(t_n + \\tfrac h2, y_n + \\tfrac h2 s_1),\\quad s_3 = f(t_n + \\tfrac34h, y_n + \\tfrac34 h s_2)",
           "y_{n+1} = y_n + \\tfrac h9(2s_1 + 3s_2 + 4s_3),\\quad s_4 = f(t_{n+1}, y_{n+1})",
           "e = \\tfrac{h}{72}(-5s_1 + 6s_2 + 8s_3 - 9s_4),\\quad \\text{accept if } \\|e\\| \\le \\text{tol}"],
    dp45: ["\\text{slopes at } t_n,\\ t_n + \\tfrac h5,\\ t_n + \\tfrac{3h}{10},\\ t_n + \\tfrac{4h}{5},\\ t_n + \\tfrac{8h}{9},\\ t_n + h,\\ t_n + h",
           "y_{n+1}: \\text{fifth order};\\quad e = y^{(5)} - y^{(4)},\\quad \\text{FSAL: } s_7 \\to \\text{next } s_1"],
    beuler: ["y_{n+1} = y_n + h\\,f(t_{n+1}, y_{n+1})", "\\text{solve } Y - h f(t_{n+1}, Y) - y_n = 0 \\text{ by Newton's method}"]
  };

  var uid = 0;

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var methodOf = {}; config.methods.forEach(function (m) { methodOf[m.id] = m; });
    var clipId = "nm-clip-" + (++uid);
    var run = null, P = null, ref = null, cursor = { step: 0, sub: 0 }, playing = false;

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Watch a numerical method take its steps" }),
      ctx.mathText(h("p", { className: "lede" }), "Pick a method and a problem. Step through one stage at a time: each slope $s_k$ is drawn where it is evaluated, then the weighted step moves the solution. Adaptive methods show their error estimate against the tolerance and change $h$.")
    ]));

    // ---------------- controls
    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text, label, fmt) {
      var c = config[key], id = "nm-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      inp.setAttribute("aria-label", label);
      var out = h("output", { "for": id, text: fmt(st[key]) });
      inp.addEventListener("input", function () {
        st[key] = snap(parseFloat(inp.value), c); out.textContent = fmt(st[key]);
        recompute(); ctx.save(); ctx.announce(label + " " + fmt(st[key]));
      });
      inputs[key] = inp; outputs[key] = out;
      rows[key] = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
      return rows[key];
    }
    var hRow = slider("h", "Step size $h$", "Step size h", function (v) { return num(v, 3); });
    var tolRow = slider("logTol", "Tolerance $10^{k}$", "Tolerance exponent", function (v) { return "10^" + v; });
    var dRow = slider("delta", "Flame start $\\delta$", "Flame start delta", function (v) { return num(v, 3); });
    var muRow = slider("mu", "Van der Pol $\\mu$", "Van der Pol mu", function (v) { return num(v, 3); });

    var methodSel = h("select", { id: "nm-method" }, config.methods.map(function (m) {
      var o = h("option", { value: m.id, text: m.label }); if (m.id === st.method) o.selected = true; return o;
    }));
    methodSel.addEventListener("change", function () { st.method = methodSel.value; recompute(); ctx.save(); ctx.announce("Method " + methodOf[st.method].label); });
    var probSel = h("select", { id: "nm-problem" }, config.problems.map(function (p) {
      var o = h("option", { value: p.id, text: p.label }); if (p.id === st.problem) o.selected = true; return o;
    }));
    probSel.addEventListener("change", function () { st.problem = probSel.value; recompute(); ctx.save(); ctx.announce("Problem " + probSel.selectedOptions[0].textContent); });
    var viewSel = h("select", { id: "nm-view" }, [h("option", { value: "time", text: "time plot y₁(t)" }), h("option", { value: "phase", text: "phase plane (y₁, y₂)" })]);
    viewSel.value = st.view;
    viewSel.addEventListener("change", function () { st.view = viewSel.value; draw(); ctx.save(); });
    var viewRow = h("div", { className: "slider-row" }, [h("label", { "for": "nm-view", text: "View" }), h("span"), viewSel]);

    function btn(text, label, fn) { var b = h("button", { type: "button", className: "btn small", text: text, onclick: fn }); b.setAttribute("aria-label", label); return b; }
    var bBack = btn("◀ Stage", "Back one stage", function () { pause(); back(); });
    var bNext = btn("Stage ▶", "Next stage", function () { pause(); advance(); });
    var bStep = btn("Step ⏭", "Next whole step", function () { pause(); nextStep(); });
    var bPlay = btn("Play", "Play or pause", function () { if (playing) pause(); else play(); });
    var bEnd = btn("Run to end", "Run to the end", function () { pause(); cursor = { step: run.steps.length, sub: 0 }; draw(); });
    var bReset = btn("Reset", "Back to the start", function () { pause(); cursor = { step: 0, sub: 0 }; draw(); });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        pause();
        st.method = p.method; st.problem = p.problem; methodSel.value = p.method; probSel.value = p.problem;
        NUMKEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; outputs[k].textContent = inputs[k].value; } });
        ctx.mathText(presetNote, p.note || "");
        recompute(); ctx.save(); ctx.announce("Preset " + p.label);
      } });
    }));

    var controls = h("div", null, [
      h("h2", { text: "Method" }),
      hRow, tolRow, dRow, muRow,
      h("div", { className: "slider-row" }, [h("label", { "for": "nm-method", text: "Method" }), h("span"), methodSel]),
      h("div", { className: "slider-row" }, [h("label", { "for": "nm-problem", text: "Problem" }), h("span"), probSel]),
      viewRow,
      h("div", { className: "presets" }, [bBack, bNext, bStep, bPlay, bEnd, bReset]),
      h("h3", { text: "Presets" }), presets, presetNote
    ]);

    // ---------------- main plot
    var W = 640, H = 360, L = 52, R = 12, T = 12, B = 30;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", style: "width:100%;height:auto",
      "aria-label": "Live view of the numerical solution: completed steps, the stage slopes of the current step, and the exact or reference solution." });
    var defs = s("defs"), clip = s("clipPath", { id: clipId });
    clip.appendChild(s("rect", { x: L, y: T, width: W - L - R, height: H - T - B }));
    defs.appendChild(clip);
    var mk = s("marker", { id: clipId + "-arr", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 3.5, markerHeight: 3.5, orient: "auto-start-reverse" });
    mk.appendChild(s("path", { d: "M0,0 L10,5 L0,10 z", fill: "var(--green)" }));
    defs.appendChild(mk); svg.appendChild(defs);
    var gGrid = s("g"), gRef = s("g", { "clip-path": "url(#" + clipId + ")" }), gPath = s("g", { "clip-path": "url(#" + clipId + ")" }),
        gStage = s("g", { "clip-path": "url(#" + clipId + ")" });
    [gGrid, gRef, gPath, gStage].forEach(function (g) { svg.appendChild(g); });
    var legend = h("div", { className: "legend" }, [
      h("span", null, [h("span", { className: "sw", style: "background:var(--muted)" }), "exact / reference"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--teal)" }), "accepted steps"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--blue)" }), "stage slopes s₁, s₂, …"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--green)" }), "weighted step"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--red)" }), "rejected try"])
    ]);
    var notice = h("p", { className: "plot-note", style: "font-weight:600" });
    var mainBox = h("div", { className: "plot-box" }, [h("h3", { text: "Live step" }), svg, legend, notice]);

    // gauge
    var gW = 640, gH = 70;
    var gauge = s("svg", { viewBox: "0 0 " + gW + " " + gH, role: "img", style: "width:100%;height:auto", "aria-label": "Error estimate against the tolerance on a logarithmic scale" });
    var gaugeBox = h("div", { className: "plot-box" }, [h("h3", { text: "Error estimate against the tolerance" }), gauge]);
    // step-size strip
    var sW = 640, sH = 120;
    var strip = s("svg", { viewBox: "0 0 " + sW + " " + sH, role: "img", style: "width:100%;height:auto", "aria-label": "Accepted step sizes against time" });
    var stripBox = h("div", { className: "plot-box" }, [h("h3", { text: "Step sizes h along the way" }), strip]);
    // order chart
    var oW = 640, oH = 210;
    var order = s("svg", { viewBox: "0 0 " + oW + " " + oH, role: "img", style: "width:100%;height:auto", "aria-label": "Log-log plot of error against step size for four fixed-step methods" });
    var orderNote = h("p", { className: "plot-note" });
    var orderBox = h("div", { className: "plot-box" }, [h("h3", { text: "Order experiment: y' = 1/(1+t)², exact 1/2" }), order, orderNote]);

    var stepBox = h("div", { className: "readout" }), errBox = h("div", { className: "readout" }), cardBox = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [mainBox, stepBox, gaugeBox, stripBox, errBox, cardBox, orderBox])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function shown(el, on) { el.hidden = !on; el.style.display = on ? "" : "none"; }

    // ---------------- computation
    var refKey = "";
    function recompute() {
      pause();
      P = SM.problem(st.problem, { delta: st.delta, mu: st.mu });
      var m = methodOf[st.method];
      run = m.adaptive ? SM.integrate(st.method, P, { rtol: Math.pow(10, st.logTol), maxSteps: 6000 })
                       : SM.integrate(st.method, P, { h: st.h, maxSteps: 6000 });
      var key = st.problem + "|" + st.delta + "|" + st.mu;
      if (key !== refKey) {
        refKey = key;
        if (P.exact) {
          ref = []; for (var i = 0; i <= 400; i++) { var t = P.t0 + (P.tf - P.t0) * i / 400; ref.push([t, P.exact(t)]); }
        } else {
          var rr = SM.integrate("dp45", P, { rtol: 1e-9, threshold: 1e-9, maxSteps: 40000 });
          ref = rr.t.map(function (t, j) { return [t, rr.y[j]]; });
        }
      }
      cursor = { step: 0, sub: 0 };
      shown(hRow, !m.adaptive); shown(tolRow, !!m.adaptive);
      shown(dRow, st.problem === "flame"); shown(muRow, st.problem === "vdp");
      shown(viewRow, P.dim === 2);
      draw(); drawOrder();
    }

    function subCount(sp) { return sp.stages.length + 1 + (sp.err ? 1 : 0); }

    function advance() {
      if (cursor.step >= run.steps.length) return;
      var sp = run.steps[cursor.step];
      cursor.sub++;
      if (cursor.sub > subCount(sp)) { cursor.step++; cursor.sub = 0; }
      draw(); announceStage();
    }
    function back() {
      if (cursor.sub > 0) cursor.sub--;
      else if (cursor.step > 0) { cursor.step--; cursor.sub = subCount(run.steps[cursor.step]); }
      draw(); announceStage();
    }
    function nextStep() {
      if (cursor.step < run.steps.length) { cursor.step++; cursor.sub = 0; }
      draw(); announceStage();
    }
    function announceStage() {
      var sp = run.steps[cursor.step];
      if (!sp) { ctx.announce("End of the integration"); return; }
      if (cursor.sub === 0) ctx.announce("Step " + (cursor.step + 1) + " from t = " + num(sp.t, 3));
      else if (cursor.sub <= sp.stages.length) ctx.announce("Stage " + sp.stages[cursor.sub - 1].label + " at t = " + num(sp.stages[cursor.sub - 1].t, 3));
      else ctx.announce(sp.err ? (sp.accepted ? "Step accepted" : "Step rejected") : "Weighted step to t = " + num(sp.tNew, 3));
    }
    function play() {
      if (cursor.step >= run.steps.length) cursor = { step: 0, sub: 0 };
      playing = true; bPlay.textContent = "Pause";
      var dt = reducedMotion() ? 900 : 420;
      timer = setInterval(function () {
        if (cursor.step >= run.steps.length) { pause(); return; }
        advance();
      }, dt);
    }
    function pause() {
      playing = false; bPlay.textContent = "Play";
      if (timer) { clearInterval(timer); timer = 0; }
    }

    // ---------------- drawing helpers
    var phase = function () { return P.dim === 2 && st.view === "phase"; };
    function coords(t, y) { return phase() ? [y[0], y[1]] : [t, y[0]]; }
    var view = null;
    function setView() {
      var xs = [], ys = [], CL = 1e6;
      function add(t, y) { var c = coords(t, y); if (isFinite(c[1]) && Math.abs(c[1]) < CL && isFinite(c[0])) { xs.push(c[0]); ys.push(c[1]); } }
      run.t.forEach(function (t, j) { add(t, run.y[j]); });
      // the reference widens the window, but at most to 1.6 times the spread of the computed points,
      // so a lagging method (Euler on y' = 2y) stays visible while the exact curve leaves the box
      var ry0 = Math.min.apply(null, ys), ry1 = Math.max.apply(null, ys), spread = Math.max(ry1 - ry0, 1e-9);
      ref.forEach(function (p) {
        var c = coords(p[0], p[1]);
        if (isFinite(c[1]) && c[1] <= ry1 + 0.6 * spread && c[1] >= ry0 - 0.6 * spread) { xs.push(c[0]); ys.push(c[1]); }
      });
      var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
      if (!phase()) { x0 = P.t0; x1 = P.tf; }
      var py = (y1 - y0) * 0.08 || 1, px = phase() ? ((x1 - x0) * 0.08 || 1) : 0;
      view = { x0: x0 - px, x1: x1 + px, y0: y0 - py, y1: y1 + py };
    }
    function X(x) { return L + (x - view.x0) / (view.x1 - view.x0) * (W - L - R); }
    function Y(y) { return T + (view.y1 - y) / (view.y1 - view.y0) * (H - T - B); }
    function pt(t, y) { var c = coords(t, y); return [X(c[0]), Y(Math.max(-1e7, Math.min(1e7, c[1])))]; }
    function poly(points, attrs) {
      var d = points.map(function (q, i) { return (i ? "L" : "M") + q[0].toFixed(1) + " " + q[1].toFixed(1); }).join(" ");
      var a = { d: d, fill: "none" }; for (var k in attrs) a[k] = attrs[k];
      return s("path", a);
    }
    function slopeSeg(t, y, sv, color, len) {
      // direction of the slope in screen space
      var a = pt(t, y), b;
      if (phase()) b = pt(t, [y[0] + sv[0] * 1e-3, y[1] + sv[1] * 1e-3]);
      else b = pt(t + 1e-3, [y[0] + sv[0] * 1e-3]);
      var dx = b[0] - a[0], dy = b[1] - a[1], n = Math.hypot(dx, dy) || 1;
      dx = dx / n * len; dy = dy / n * len;
      return s("line", { x1: (a[0] - (phase() ? 0 : dx)).toFixed(1), y1: (a[1] - (phase() ? 0 : dy)).toFixed(1), x2: (a[0] + dx).toFixed(1), y2: (a[1] + dy).toFixed(1),
        stroke: color, "stroke-width": 4, "stroke-linecap": "round" });
    }
    function dot(t, y, r, fill) { var a = pt(t, y); return s("circle", { cx: a[0].toFixed(1), cy: a[1].toFixed(1), r: r, fill: fill }); }
    function text(x, y, str, color, anchor) { var e = s("text", { x: x, y: y, fill: color || "var(--muted)", "font-size": 12, "text-anchor": anchor || "start" }); e.textContent = str; return e; }

    function drawGrid() {
      clear(gGrid);
      gGrid.appendChild(s("rect", { x: L, y: T, width: W - L - R, height: H - T - B, fill: "none", stroke: "var(--border)" }));
      [0, 0.25, 0.5, 0.75, 1].forEach(function (f) {
        var yv = view.y0 + f * (view.y1 - view.y0), xv = view.x0 + f * (view.x1 - view.x0);
        gGrid.appendChild(s("line", { x1: L, x2: W - R, y1: Y(yv), y2: Y(yv), stroke: "var(--border)", "stroke-width": 0.6 }));
        gGrid.appendChild(text(L - 4, Y(yv) + 4, num(yv, 3), null, "end"));
        gGrid.appendChild(text(X(xv), H - 10, num(xv, 3), null, "middle"));
      });
      gGrid.appendChild(text(W - R, H - 22, phase() ? "y₁" : "t", null, "end"));
      gGrid.appendChild(text(L + 4, T + 14, phase() ? "y₂" : "y₁"));
    }

    // ---------------- main draw
    function draw() {
      setView(); drawGrid();
      clear(gRef); clear(gPath); clear(gStage);
      gRef.appendChild(poly(ref.map(function (p) { return pt(p[0], p[1]); }), { stroke: "var(--muted)", "stroke-width": 2, "stroke-dasharray": "6 4" }));

      // completed steps up to the cursor
      var pts = [pt(P.t0, P.y0)], acc = 0, rejects = [];
      for (var i = 0; i < Math.min(cursor.step, run.steps.length); i++) {
        var sp = run.steps[i];
        if (sp.accepted) { pts.push(pt(sp.tNew, sp.yNew)); acc++; }
        else rejects.push(sp);
      }
      rejects.forEach(function (sp) {
        gPath.appendChild(poly([pt(sp.t, sp.y), pt(sp.tNew, sp.yNew)], { stroke: "var(--red)", "stroke-width": 1.5, "stroke-dasharray": "3 3", opacity: 0.6 }));
      });
      gPath.appendChild(poly(pts, { stroke: "var(--teal)", "stroke-width": 2.5 }));
      if (pts.length < 300) pts.forEach(function (q) { gPath.appendChild(s("circle", { cx: q[0].toFixed(1), cy: q[1].toFixed(1), r: 3, fill: "var(--teal)" })); });

      var cur = run.steps[cursor.step];
      if (cur) drawStage(cur);
      drawReadouts(cur, acc);
      drawGauge(cur); drawStrip();
      var fail = run.failed;
      var blew = run.y.some(function (y) { return y.some(function (v) { return !isFinite(v) || Math.abs(v) > 1e6; }); });
      notice.textContent = fail ? "Stopped: " + fail + "." : (blew ? "The numerical solution blew up (values beyond 10⁶ are clipped)." : "");
    }

    function drawStage(sp) {
      var k = cursor.sub, n = sp.stages.length, m = methodOf[st.method];
      gStage.appendChild(dot(sp.t, sp.y, 5, "var(--teal)"));
      for (var j = 0; j < Math.min(k, n); j++) {
        var sg = sp.stages[j], col = STAGE_COLORS[j % STAGE_COLORS.length];
        if (!(sg.t === sp.t && sg.y === sp.y) && st.method !== "beuler") {
          gStage.appendChild(poly([pt(sp.t, sp.y), pt(sg.t, sg.y)], { stroke: col, "stroke-width": 1.2, "stroke-dasharray": "4 3", opacity: 0.8 }));
        }
        gStage.appendChild(dot(sg.t, sg.y, 4, col));
        gStage.appendChild(slopeSeg(sg.t, sg.y, sg.s, col, 22));
        var a = pt(sg.t, sg.y);
        gStage.appendChild(text(a[0] + 6, a[1] - 8, sg.label, col));
      }
      if (k > n) {
        var a0 = pt(sp.t, sp.y), a1 = pt(sp.tNew, sp.yNew), ok = sp.accepted !== false;
        gStage.appendChild(s("line", { x1: a0[0], y1: a0[1], x2: a1[0], y2: a1[1], stroke: ok ? "var(--green)" : "var(--red)", "stroke-width": 4,
          "marker-end": ok ? "url(#" + clipId + "-arr)" : null }));
        gStage.appendChild(text(Math.min(a1[0] + 8, W - 160), a1[1] + 16, sp.weights, ok ? "var(--green)" : "var(--red)"));
        if (st.method === "beuler") gStage.appendChild(text(L + 8, T + 30, "solve Y − h f(t+h, Y) = yₙ by Newton", "var(--pink)"));
      }
      if (m.adaptive && k > n + 0) {
        var msg = sp.accepted ? "✓ accepted" : "✗ rejected: retry with smaller h";
        gStage.appendChild(text(L + 40, T + 16, msg, sp.accepted ? "var(--green)" : "var(--red)"));
      }
    }

    function drawReadouts(sp, acc) {
      var m = methodOf[st.method], lines = [];
      if (sp) {
        lines.push("Step " + (cursor.step + 1) + " of " + run.steps.length + (m.adaptive ? " (attempts, incl. rejected)" : "") +
                   ": t = " + num(sp.t, 4) + ", h = " + num(sp.h, 3) + ", y = " + sp.y.map(function (v) { return num(v, 5); }).join(", "));
        sp.stages.forEach(function (sg, j) {
          if (j < cursor.sub) lines.push(sg.label + " at t = " + num(sg.t, 4) + ": slope " + sg.s.map(function (v) { return num(v, 3); }).join(", "));
        });
        if (cursor.sub > sp.stages.length) lines.push("y_new = " + sp.yNew.map(function (v) { return num(v, 6); }).join(", ") + " at t = " + num(sp.tNew, 4));
        if (sp.err && cursor.sub > sp.stages.length) {
          var q = st.method === "bs23" ? 2 : 4, tol = sp.tol, e = sp.errNorm;
          var fac = e === 0 ? 5 : Math.min(5, Math.max(0.1, 0.8 * Math.pow(tol / e, 1 / (q + 1))));
          lines.push("error estimate " + num(e, 3) + " vs tol " + num(tol, 2) + " → " + (sp.accepted ? "accept" : "reject") + "; next h = h × " + num(fac, 3));
        }
      } else lines.push("Integration finished at t = " + num(run.t[run.t.length - 1], 4) + ".");
      lines.push("Function evaluations (whole run): " + run.evals + "; accepted steps " + run.accepted + (m.adaptive ? ", rejected " + run.rejected : "") + ".");
      clear(stepBox); lines.forEach(function (l) { stepBox.appendChild(h("p", { text: l, style: "margin:2px 0" })); });

      clear(errBox);
      var tEnd = run.t[run.t.length - 1], yEnd = run.y[run.y.length - 1];
      var yRef = P.exact ? P.exact(tEnd) : nearestRef(tEnd);
      var err = yRef ? Math.max.apply(null, yEnd.map(function (v, i) { return Math.abs(v - yRef[i]); })) : null;
      errBox.appendChild(h("p", { text: "At the end, t = " + num(tEnd, 4) + ": numerical " + yEnd.map(function (v) { return num(v, 6); }).join(", ") +
        (yRef ? "; " + (P.exact ? "exact " : "reference ") + yRef.map(function (v) { return num(v, 6); }).join(", ") + "; error " + num(err, 3) : ""), style: "margin:2px 0" }));
      clear(cardBox);
      cardBox.appendChild(h("p", { text: m.label + " — order " + m.order + (m.adaptive ? ", adaptive" : "") + (m.implicit ? ", implicit" : ""), style: "margin:2px 0;font-weight:600" }));
      METHOD_TEX[st.method].forEach(function (tx) { var d = h("div"); ctx.displayMath(d, tx); cardBox.appendChild(d); });
    }
    function nearestRef(t) {
      var best = null, bd = Infinity;
      ref.forEach(function (p) { var d = Math.abs(p[0] - t); if (d < bd) { bd = d; best = p[1]; } });
      return bd < 1e-6 * (1 + Math.abs(t)) ? best : null;
    }

    function drawGauge(sp) {
      clear(gauge);
      var m = methodOf[st.method];
      shown(gaugeBox, !!m.adaptive);
      if (!m.adaptive) return;
      var x0 = 40, x1 = gW - 20, lo = -12, hi = 0;
      function GX(v) { var lv = Math.log10(Math.max(v, 1e-12)); return x0 + (Math.min(hi, Math.max(lo, lv)) - lo) / (hi - lo) * (x1 - x0); }
      gauge.appendChild(s("line", { x1: x0, x2: x1, y1: 44, y2: 44, stroke: "var(--border)" }));
      for (var e = lo; e <= hi; e += 2) { gauge.appendChild(text(GX(Math.pow(10, e)), 62, "1e" + e, null, "middle")); }
      var tol = Math.pow(10, st.logTol);
      gauge.appendChild(s("line", { x1: GX(tol), x2: GX(tol), y1: 6, y2: 50, stroke: "var(--red)", "stroke-width": 3 }));
      gauge.appendChild(text(GX(tol) + 4, 14, "tol", "var(--red)"));
      if (sp && sp.err && cursor.sub > sp.stages.length) {
        var ok = sp.accepted;
        gauge.appendChild(s("rect", { x: x0, y: 24, width: Math.max(1, GX(sp.errNorm) - x0), height: 14, fill: ok ? "var(--green)" : "var(--red)", opacity: 0.85 }));
        gauge.appendChild(text(x0, 18, "error estimate " + num(sp.errNorm, 3) + (ok ? "  ✓ accepted" : "  ✗ rejected"), ok ? "var(--green)" : "var(--red)"));
      } else gauge.appendChild(text(x0, 18, "step through the stages to see this step's error estimate"));
    }

    function drawStrip() {
      clear(strip);
      var acc = run.steps.filter(function (sp) { return sp.accepted; });
      var x0 = 40, x1 = sW - 10, y0 = sH - 20, y1 = 10;
      var hmax = Math.max.apply(null, acc.map(function (sp) { return sp.h; }).concat([1e-12]));
      strip.appendChild(s("line", { x1: x0, x2: x1, y1: y0, y2: y0, stroke: "var(--border)" }));
      strip.appendChild(text(x0 - 4, y1 + 8, num(hmax, 2), null, "end"));
      strip.appendChild(text(x0 - 4, y0, "0", null, "end"));
      var span = P.tf - P.t0;
      acc.forEach(function (sp, i) {
        var xa = x0 + (sp.t - P.t0) / span * (x1 - x0), xb = x0 + (sp.tNew - P.t0) / span * (x1 - x0);
        var hh = (sp.h / hmax) * (y0 - y1);
        var done = run.steps.indexOf(sp) < cursor.step;
        strip.appendChild(s("rect", { x: xa, y: y0 - hh, width: Math.max(0.6, xb - xa - 0.3), height: hh, fill: done ? "var(--teal)" : "var(--border)" }));
      });
      strip.appendChild(text(x1, sH - 4, "t → (" + acc.length + " accepted steps)", null, "end"));
    }

    var orderCache = null;
    function drawOrder() {
      clear(order);
      if (!orderCache) {
        // the lecture's experiment: h = 0.1 and h = 0.05 (nested meshes)
        orderCache = { rows: ["euler", "midpoint", "heun", "rk4"].map(function (m) { return { m: m, r: SM.orderExperiment(m, 0.1) }; }) };
      }
      var rows = orderCache.rows, x0 = 60, x1 = oW - 120, y0 = oH - 30, y1 = 12;
      var all = [];
      rows.forEach(function (q) { all.push(Math.log2(Math.abs(q.r.v1 - 0.5)), Math.log2(Math.abs(q.r.v2 - 0.5))); });
      all = all.filter(isFinite);
      var lo = Math.floor(Math.min.apply(null, all)) - 1, hi = Math.ceil(Math.max.apply(null, all)) + 1;
      function OY(v) { return y0 - (v - lo) / (hi - lo) * (y0 - y1); }
      var hx1 = Math.log2(rows[0].r.h1), hx2 = Math.log2(rows[0].r.h2);
      function OX(v) { return x0 + (v - (hx2 - 0.3)) / ((hx1 + 0.3) - (hx2 - 0.3)) * (x1 - x0); }
      order.appendChild(s("rect", { x: x0, y: y1, width: x1 - x0, height: y0 - y1, fill: "none", stroke: "var(--border)" }));
      order.appendChild(text(x0 - 6, OY(hi) + 10, "2^" + hi, null, "end"));
      order.appendChild(text(x0 - 6, OY(lo), "2^" + lo, null, "end"));
      order.appendChild(text(OX(hx1), oH - 12, "h = " + num(rows[0].r.h1, 3), null, "middle"));
      order.appendChild(text(OX(hx2), oH - 12, "h/2", null, "middle"));
      var cols = { euler: "var(--red)", midpoint: "var(--orange)", heun: "var(--yellow)", rk4: "var(--green)" };
      var names = { euler: "Euler", midpoint: "midpoint", heun: "Heun", rk4: "RK4" };
      rows.forEach(function (q) {
        var a = [OX(hx1), OY(Math.log2(Math.abs(q.r.v1 - 0.5)))], b = [OX(hx2), OY(Math.log2(Math.abs(q.r.v2 - 0.5)))];
        order.appendChild(poly([a, b], { stroke: cols[q.m], "stroke-width": 3 }));
        order.appendChild(s("circle", { cx: a[0], cy: a[1], r: 4, fill: cols[q.m] }));
        order.appendChild(s("circle", { cx: b[0], cy: b[1], r: 4, fill: cols[q.m] }));
        order.appendChild(text(x1 + 8, a[1] + 4, names[q.m] + ": order " + q.r.p, cols[q.m]));
      });
      var sel = rows.filter(function (q) { return q.m === st.method; })[0] || rows[3];
      orderNote.textContent = names[sel.m] + ": " + num(sel.r.v1, 6) + " (h = " + num(sel.r.h1, 3) + ") and " + num(sel.r.v2, 6) +
        " (h/2); error ratio " + num(sel.r.ratio, 3) + " ≈ 2^" + sel.r.p + ". Steeper lines mean higher order.";
    }

    recompute();
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
