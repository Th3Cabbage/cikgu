/*
 * Eigenvalues and linear systems explorer: Ax against x, powers A^k u0, and y' = Ay with e^(At).
 * Maths comes from window.StudyMath (eig, diagonalize, expand, powersSequence, expm, flow).
 * Saved state: state.explorer = {mode, a, b, c, d}. theta, u0 and t are not saved.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["a", "b", "c", "d"];
  var PI = Math.PI;
  var CLIP = 1e3;
  var raf = 0;

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function modeIds(config) { return config.modes.map(function (m) { return m.id; }); }
  function defaults(config) {
    var out = { mode: config.defaultMode || config.modes[0].id };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config || !Array.isArray(config.modes)) return out;
    if (typeof saved.mode === "string" && modeIds(config).indexOf(saved.mode) >= 0) out.mode = saved.mode;
    KEYS.forEach(function (k) {
      var v = saved[k], c = config[k];
      if (typeof v === "number" && isFinite(v) && v >= c.min - 1e-9 && v <= c.max + 1e-9) out[k] = snap(v, c);
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
  function tnum(v) { return num(v).replace("−", "-"); }
  function f3(v) { var r = +v.toFixed(3); return (Math.abs(r) < 5e-4 ? 0 : r) + ""; }
  function bmat(M, f) {
    f = f || tnum;
    return "\\begin{bmatrix} " + f(M[0][0]) + " & " + f(M[0][1]) + " \\\\ " + f(M[1][0]) + " & " + f(M[1][1]) + " \\end{bmatrix}";
  }
  function isReal(z) { return Math.abs(z[1]) < 1e-9; }
  function cnum(z) {
    if (isReal(z)) return num(z[0]);
    var re = Math.abs(z[0]) < 5e-10 ? "" : num(z[0]) + " ";
    return re + (z[1] < 0 ? "− " : (re ? "+ " : "")) + num(Math.abs(z[1])) + "i";
  }
  function niceCeil(v) {
    var mag = Math.pow(10, Math.floor(Math.log(v) / Math.LN10)), m = [1, 2, 5, 10], i;
    for (i = 0; i < m.length; i++) if (m[i] * mag >= v - 1e-12) return m[i] * mag;
    return 10 * mag;
  }
  var uid = 0;

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var tMax = config.tMax || 3, nSteps = config.steps || 12;
    var local = { theta: 30, u0x: 1, u0y: 0.5, t: Math.min(1, tMax) };
    var clipId = "ev-clip-" + (++uid);
    var playing = false, lastTs = 0;

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "What does a matrix do to vectors?" }),
      ctx.mathText(h("p", { className: "lede" }), "Choose a $2 \\times 2$ matrix $A$. Compare $Ax$ with $x$, repeat $u_{k+1} = Au_k$, or follow $y' = Ay$. The eigenvalues and eigenvectors decide the pattern in every mode.")
    ]));

    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text, label, c, getv, setv) {
      var id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: getv() });
      inp.setAttribute("aria-label", label);
      var out = h("output", { "for": id, text: num(getv()) });
      inp.addEventListener("input", function () {
        setv(snap(parseFloat(inp.value), c)); update();
        ctx.announce(label + " " + num(getv()));
      });
      inputs[key] = inp; outputs[key] = out;
      var row = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
      rows[key] = row;
      return row;
    }
    function mslider(key, text, label) {
      return slider(key, text, label, config[key], function () { return st[key]; }, function (v) { st[key] = v; ctx.save(); });
    }
    function lslider(key, text, label, c) {
      return slider(key, text, label, c, function () { return local[key]; }, function (v) { local[key] = v; });
    }
    var thetaC = { min: 0, max: 360, step: 1 }, uC = { min: -2, max: 2, step: 0.1 }, tC = { min: 0, max: tMax, step: 0.05 };

    var radios = {};
    var modeBox = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "Mode", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    config.modes.forEach(function (m) {
      var id = "ex-mode-" + m.id;
      var r = h("input", { type: "radio", name: "ex-mode", id: id, value: m.id });
      r.checked = st.mode === m.id;
      r.addEventListener("change", function () {
        if (r.checked) { st.mode = m.id; pause(); update(); ctx.save(); ctx.announce("Mode: " + m.label); }
      });
      radios[m.id] = r;
      modeBox.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
    });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        pause();
        if (p.mode && radios[p.mode]) { st.mode = p.mode; radios[p.mode].checked = true; }
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note || "");
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var matBox = h("div", { className: "readout" });
    var btnPlay = h("button", { type: "button", className: "btn small", text: "Play", onclick: function () {
      if (playing) pause(); else play();
    } });
    var playRow = h("div", { className: "presets" }, [btnPlay]);
    var controls = h("div", null, [
      h("h2", { text: "Matrix" }),
      mslider("a", "Entry $a$", "Matrix entry a"), mslider("b", "Entry $b$", "Matrix entry b"),
      mslider("c", "Entry $c$", "Matrix entry c"), mslider("d", "Entry $d$", "Matrix entry d"),
      lslider("theta", "Angle $\\theta$ (degrees)", "Angle theta of x in degrees", thetaC),
      lslider("u0x", "Start $u_{0,1}$", "Start vector first entry", uC),
      lslider("u0y", "Start $u_{0,2}$", "Start vector second entry", uC),
      lslider("t", "Time $t$", "Time t", tC),
      playRow, matBox, modeBox, presets
    ]);

    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }

    // ---- plot ----
    var L = 34, Rr = 10, Tp = 10, Bt = 26, PS = 340, W1 = L + PS + Rr, H1 = Tp + PS + Bt;
    var svg = s("svg", { viewBox: "0 0 " + W1 + " " + H1, role: "img",
      "aria-label": "Plane showing the current mode: vectors x and Ax, the sequence of powers, or flow trajectories.",
      style: "width:100%;height:auto" });
    var defs = s("defs"), clip = s("clipPath", { id: clipId });
    clip.appendChild(s("rect", { x: L, y: Tp, width: PS, height: PS }));
    defs.appendChild(clip); svg.appendChild(defs);
    var cp = { "clip-path": "url(#" + clipId + ")" };
    var grid = s("g"), lines = s("g", cp), curves = s("g", cp), marks = s("g", cp);
    [grid, lines, curves, marks].forEach(function (g) { svg.appendChild(g); });
    var legend = h("div", { className: "legend" });
    var cap = h("p", { className: "plot-note" });
    var plotTitle = h("h3", { text: "Plane" });
    var plotBox = h("div", { className: "plot-box" }, [plotTitle, svg, legend, cap]);

    var tableBox = h("div", { className: "readout" }), parBox = h("p", { className: "plot-note", style: "font-weight:600" });
    var factsBox = h("div", { className: "readout" }), expBox = h("div", { className: "readout" }), facBox = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [plotBox, parBox, presetNote, expBox, tableBox, factsBox, facBox])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function setShown(el, on) { el.hidden = !on; el.style.display = on ? "" : "none"; }
    function matrix() { return [[st.a, st.b], [st.c, st.d]]; }

    function play() {
      if (st.mode !== "eig") return;
      playing = true; lastTs = 0; btnPlay.textContent = "Pause";
      ctx.announce("Sweep started");
      raf = requestAnimationFrame(tick);
    }
    function pause() {
      var was = playing;
      playing = false; stop();
      btnPlay.textContent = "Play";
      if (was) ctx.announce("Sweep paused");
    }
    function tick(ts) {
      if (!playing) return;
      if (lastTs) {
        local.theta = (local.theta + 30 * Math.min(0.1, (ts - lastTs) / 1000)) % 360;
        inputs.theta.value = Math.round(local.theta);
        update();
      }
      lastTs = ts;
      raf = requestAnimationFrame(tick);
    }

    // ---- drawing helpers ----
    function drawAxes(R) {
      clear(grid);
      var step = niceCeil(R / 3), v;
      var X = function (x) { return L + PS * (x + R) / (2 * R); }, Y = function (y) { return Tp + PS * (R - y) / (2 * R); };
      for (v = -Math.floor(R / step) * step; v <= R + 1e-9; v += step) {
        var vv = +v.toFixed(6), ax = Math.abs(vv) < 1e-9;
        grid.appendChild(s("line", { x1: X(vv), y1: Tp, x2: X(vv), y2: Tp + PS, "class": ax ? "p-axis" : "p-grid" }));
        grid.appendChild(s("line", { x1: L, y1: Y(vv), x2: L + PS, y2: Y(vv), "class": ax ? "p-axis" : "p-grid" }));
        grid.appendChild(s("text", { x: X(vv), y: Tp + PS + 14, "text-anchor": "middle", text: num(vv) }));
        grid.appendChild(s("text", { x: L - 4, y: Y(vv) + 4, "text-anchor": "end", text: num(vv) }));
      }
      grid.appendChild(s("text", { x: L + PS, y: Tp + PS + 24, "text-anchor": "end", text: "x₁" }));
      grid.appendChild(s("text", { x: L + 4, y: Tp + 10, text: "x₂" }));
      return { X: X, Y: Y, R: R };
    }
    function pathOf(pts, M) {
      var d = "", pen = false;
      pts.forEach(function (q) {
        if (!q || !isFinite(q[0]) || !isFinite(q[1]) || Math.abs(q[0]) > CLIP || Math.abs(q[1]) > CLIP) { pen = false; return; }
        d += (pen ? "L" : "M") + M.X(q[0]).toFixed(1) + " " + M.Y(q[1]).toFixed(1) + " ";
        pen = true;
      });
      return d;
    }
    function arrow(M, x0, y0, x1, y1, color, w) {
      var px0 = M.X(x0), py0 = M.Y(y0), px1 = M.X(x1), py1 = M.Y(y1), dx = px1 - px0, dy = py1 - py0, m = Math.hypot(dx, dy);
      curves.appendChild(s("line", { x1: px0, y1: py0, x2: px1, y2: py1, style: "stroke:" + color + ";stroke-width:" + w + ";stroke-linecap:round" }));
      if (m < 6) return;
      dx /= m; dy /= m;
      var z = 8;
      curves.appendChild(s("polygon", { points: [
        px1.toFixed(1) + "," + py1.toFixed(1),
        (px1 - dx * z + dy * z * 0.4).toFixed(1) + "," + (py1 - dy * z - dx * z * 0.4).toFixed(1),
        (px1 - dx * z - dy * z * 0.4).toFixed(1) + "," + (py1 - dy * z + dx * z * 0.4).toFixed(1)].join(" "),
        style: "fill:" + color }));
    }
    function eigLines(M, e) {
      var any = false;
      [0, 1].forEach(function (i) {
        var v = e.vectors[i], l = e.lambdas[i];
        if (!v || !isReal(l) || !isReal(v[0]) || !isReal(v[1])) return;
        any = true;
        var R = M.R * 4;
        lines.appendChild(s("line", { x1: M.X(-R * v[0][0]), y1: M.Y(-R * v[1][0]), x2: M.X(R * v[0][0]), y2: M.Y(R * v[1][0]),
          style: "stroke:var(--blue);stroke-width:1.8;stroke-dasharray:6 4" }));
      });
      return any;
    }
    function legendSet(items) {
      clear(legend);
      items.forEach(function (it) { legend.appendChild(h("span", null, [sw(it[0]), it[1]])); });
    }

    // ---- modes ----
    function drawEig(A, e) {
      var M = drawAxes(7), th = local.theta * PI / 180, x = [Math.cos(th), Math.sin(th)], Ax = SM.matVec(A, x), i;
      clear(lines); clear(curves); clear(marks);
      var ell = [];
      for (i = 0; i <= 180; i++) { var a = 2 * PI * i / 180; ell.push(SM.matVec(A, [Math.cos(a), Math.sin(a)])); }
      var hasEig = eigLines(M, e);
      curves.appendChild(s("circle", { cx: M.X(0), cy: M.Y(0), r: PS / 14, fill: "none", style: "stroke:var(--teal);stroke-width:1;opacity:0.35" }));
      curves.appendChild(s("path", { d: pathOf(ell, M) + "Z", fill: "none", style: "stroke:var(--orange);stroke-width:2;opacity:0.35" }));
      arrow(M, 0, 0, Ax[0], Ax[1], "var(--orange)", 2.8);
      arrow(M, 0, 0, x[0], x[1], "var(--teal)", 2.8);
      legendSet([["var(--teal)", "x on the unit circle"], ["var(--orange)", "Ax"], ["rgba(249,115,22,0.35)", "all Ax (image ellipse)"]]);
      if (hasEig) legend.appendChild(h("span", null, [sw("var(--blue)"), "real eigenvector lines"]));
      cap.textContent = "Rotate x with the angle slider. When Ax lies on the line through x, x is an eigenvector and Ax = λx.";
      var nAx = Math.hypot(Ax[0], Ax[1]), cross = x[0] * Ax[1] - x[1] * Ax[0], dot = x[0] * Ax[0] + x[1] * Ax[1];
      var par = nAx > 1e-9 && Math.abs(cross) < 0.02 * nAx;
      parBox.textContent = "x = (" + num(x[0]) + ", " + num(x[1]) + "),  Ax = (" + num(Ax[0]) + ", " + num(Ax[1]) + ")" +
        (par ? ".  Ax is parallel to x: Ax = λx with λ = " + num(dot) : ".  Ax is not parallel to x.");
      parBox.style.color = par ? "var(--green)" : "";
      parBox.style.display = "";
    }

    function drawPowers(A, e) {
      var u0 = [local.u0x, local.u0y], seq = SM.powersSequence(A, u0, nSteps), i, shown = [], clipped = false, mx = 0.5;
      for (i = 0; i < seq.length; i++) {
        var p = seq[i];
        if (!isFinite(p[0]) || !isFinite(p[1]) || Math.abs(p[0]) > CLIP || Math.abs(p[1]) > CLIP) { clipped = true; break; }
        shown.push(p); mx = Math.max(mx, Math.abs(p[0]), Math.abs(p[1]));
      }
      var M = drawAxes(niceCeil(mx * 1.15));
      clear(lines); clear(curves); clear(marks);
      eigLines(M, e);
      for (i = 1; i < shown.length; i++) {
        var q0 = shown[i - 1], q1 = shown[i];
        var px0 = M.X(q0[0]), py0 = M.Y(q0[1]), px1 = M.X(q1[0]), py1 = M.Y(q1[1]), dx = px1 - px0, dy = py1 - py0, m = Math.hypot(dx, dy);
        if (m < 1e-6) continue;
        var ux = dx / m, uy = dy / m, ex = px1 - ux * 4, ey = py1 - uy * 4;
        curves.appendChild(s("line", { x1: px0, y1: py0, x2: ex, y2: ey, style: "stroke:var(--teal);stroke-width:1;opacity:0.7" }));
        if (m > 14) curves.appendChild(s("polygon", { points: [
          ex.toFixed(1) + "," + ey.toFixed(1),
          (ex - ux * 6 + uy * 2.5).toFixed(1) + "," + (ey - uy * 6 - ux * 2.5).toFixed(1),
          (ex - ux * 6 - uy * 2.5).toFixed(1) + "," + (ey - uy * 6 + ux * 2.5).toFixed(1)].join(" "), style: "fill:var(--teal);opacity:0.7" }));
      }
      shown.forEach(function (p, k) {
        marks.appendChild(s("circle", { cx: M.X(p[0]), cy: M.Y(p[1]), r: k === 0 ? 5 : 3.4,
          style: k === 0 ? "fill:#fff;stroke:var(--orange);stroke-width:2" : "fill:var(--teal)" }));
      });
      legendSet([["var(--teal)", "u_k"], ["var(--orange)", "start u_0"]]);
      if (shown.length) legend.appendChild(h("span", null, [sw("var(--blue)"), "real eigenvector lines"]));
      cap.textContent = "Dots are u_0, u_1, …, u_" + nSteps + "; arrows show each multiplication by A. Window ±" + num(M.R) +
        (clipped ? ". Notice: the sequence passes 1000 in size and the rest is not drawn." : ".");
      parBox.style.display = "none";

      clear(tableBox);
      tableBox.appendChild(h("h3", { text: "Powers" }));
      var table = h("table", { className: "ro-table", style: "border-collapse:collapse;font-size:0.9rem" }, [
        h("tr", null, [h("th", { text: "k", style: "text-align:left;padding:2px 10px 2px 0" }), h("th", { text: "u_k", style: "text-align:left" })])
      ]);
      seq.forEach(function (p, k) {
        table.appendChild(h("tr", null, [h("td", { text: String(k), style: "padding:1px 10px 1px 0" }),
          h("td", { text: "(" + num(p[0]) + ", " + num(p[1]) + ")" })]));
      });
      tableBox.appendChild(table);
      clear(expBox);
      var d = SM.diagonalize(A);
      if (d && isReal(e.lambdas[0]) && isReal(e.lambdas[1])) {
        var c = SM.expand(A, u0), l = [e.lambdas[0][0], e.lambdas[1][0]], v = [d.V[0][0][0], d.V[1][0][0], d.V[0][1][0], d.V[1][1][0]];
        var t1 = num(c[0][0]) + " (" + num(l[0]) + ")^k (" + num(v[0]) + ", " + num(v[1]) + ")";
        var t2 = num(c[1][0]) + " (" + num(l[1]) + ")^k (" + num(v[2]) + ", " + num(v[3]) + ")";
        expBox.appendChild(h("p", { style: "margin:2px 0", text: "u_k = c₁ λ₁^k x₁ + c₂ λ₂^k x₂ = " + t1 + " + " + t2 }));
      } else {
        expBox.appendChild(h("p", { className: "plot-note", text: d ? "Complex eigenvalues: u_k rotates and scales, so there is no real two-term decomposition." :
          "Defective matrix: only one eigenvector, so u_0 cannot be split into eigenvectors." }));
      }
      setShown(expBox, true); setShown(tableBox, true);
    }

    function drawFlow(A, e) {
      var M = drawAxes(4), k, j;
      clear(lines); clear(curves); clear(marks);
      eigLines(M, e);
      var ts = [];
      for (j = 0; j <= 60; j++) ts.push(tMax * j / 60);
      for (k = 0; k < 8; k++) {
        var an = k * PI / 4, y0 = [1.5 * Math.cos(an), 1.5 * Math.sin(an)];
        curves.appendChild(s("path", { d: pathOf(SM.flow(A, y0, ts), M), fill: "none", style: "stroke:var(--teal);stroke-width:2;stroke-linejoin:round;opacity:0.8" }));
        curves.appendChild(s("circle", { cx: M.X(y0[0]), cy: M.Y(y0[1]), r: 2.6, style: "fill:#fff;stroke:var(--teal);stroke-width:1.4" }));
        var p = SM.flow(A, y0, [local.t])[0];
        if (isFinite(p[0]) && isFinite(p[1]) && Math.abs(p[0]) < CLIP && Math.abs(p[1]) < CLIP)
          marks.appendChild(s("circle", { cx: M.X(p[0]), cy: M.Y(p[1]), r: 4.6, style: "fill:var(--orange);stroke:#fff;stroke-width:1.4" }));
      }
      legendSet([["var(--teal)", "y(s) for s from 0 to " + num(tMax)], ["var(--orange)", "y(t) now"]]);
      legend.appendChild(h("span", null, [sw("var(--blue)"), "real eigenvector lines"]));
      cap.textContent = "Eight solutions start on the circle of radius 1.5. Window ±4; parts outside are clipped.";
      parBox.style.display = "none";
      clear(expBox);
      expBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
        "e^{At} = " + bmat(SM.expm(A, local.t), f3) + ",\\quad t = " + tnum(local.t)));
      setShown(expBox, true); setShown(tableBox, false);
    }

    function update() {
      var A = matrix(), e = SM.eig(A), m = st.mode;
      KEYS.forEach(function (k) { outputs[k].textContent = num(st[k]); });
      outputs.theta.textContent = num(local.theta);
      outputs.u0x.textContent = num(local.u0x); outputs.u0y.textContent = num(local.u0y);
      outputs.t.textContent = num(local.t);
      setShown(rows.theta, m === "eig"); setShown(playRow, m === "eig");
      setShown(rows.u0x, m === "powers"); setShown(rows.u0y, m === "powers");
      setShown(rows.t, m === "flow");
      radios[m].checked = true;
      plotTitle.textContent = m === "eig" ? "Ax against x" : m === "powers" ? "Powers of A" : "Flow of y' = Ay";
      setShown(expBox, false); setShown(tableBox, false);
      if (m === "eig") drawEig(A, e); else if (m === "powers") drawPowers(A, e); else drawFlow(A, e);

      clear(matBox);
      matBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), "A = " + bmat(A)));

      clear(factsBox); clear(facBox);
      function fact(t, parent, cls) {
        var el = h("p", { style: "margin:2px 0", text: t });
        if (cls) el.className = cls;
        (parent || factsBox).appendChild(el);
      }
      fact("Trace T = " + num(e.T) + ", determinant D = " + num(e.D) + ".");
      var l1 = e.lambdas[0], l2 = e.lambdas[1];
      if (!isReal(l1)) fact("Eigenvalues λ = " + num(l1[0]) + " ± " + num(Math.abs(l1[1])) + "i.");
      else fact("Eigenvalues λ₁ = " + num(l1[0]) + ", λ₂ = " + num(l2[0]) + ".");
      if (e.defective) fact("Eigenvector: x = " + vecText(e.vectors[0]) + " (only one).");
      else fact("Eigenvectors: x₁ = " + vecText(e.vectors[0]) + ", x₂ = " + vecText(e.vectors[1]) + ".");
      fact("Kind: " + e.kind + ".");

      var dg = SM.diagonalize(A);
      if (dg && isReal(l1)) {
        var V = [[dg.V[0][0][0], dg.V[0][1][0]], [dg.V[1][0][0], dg.V[1][1][0]]];
        var Lm = [[dg.Lambda[0][0][0], 0], [0, dg.Lambda[1][1][0]]];
        facBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
          "A = V\\Lambda V^{-1},\\quad V = " + bmat(V) + ",\\quad \\Lambda = " + bmat(Lm)));
      } else if (e.defective) {
        fact("Defective: only one eigenvector, so A cannot be diagonalized.", facBox);
      } else {
        fact("Complex eigenvalues: rotation and scaling.", facBox);
      }
    }
    function vecText(v) {
      if (!v) return "none";
      return "(" + cnum(v[0]) + ", " + cnum(v[1]) + ")";
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
