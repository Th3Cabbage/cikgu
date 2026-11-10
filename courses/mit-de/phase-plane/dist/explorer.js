/*
 * Phase-plane explorer: linear z' = A z, predator-prey, damped pendulum.
 * Maths comes from window.StudyMath (eig2, models, criticalInfo, rk4).
 * Saved state: state.explorer = {mode, a, b, c, d, k} (trajectories are not saved).
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["a", "b", "c", "d", "k"];
  var PI = Math.PI;
  var MAX_TRAJ = 8, STEP = 0.01, LIMIT = 50;
  var WINDOWS = {
    linear: { x: [-3, 3], y: [-3, 3], names: ["x", "y"] },
    predprey: { x: [0, 3], y: [0, 3], names: ["y (prey)", "z (predator)"] },
    pendulum: { x: [-2 * PI - 0.5, 2 * PI + 0.5], y: [-3, 3], names: ["θ", "ω"] }
  };
  var STARTS = {
    linear: [[2, 1], [-2, 1.5], [1, -2.5], [-1.5, -1]],
    predprey: [[0.5, 0.5], [1.5, 1.5], [2.2, 0.8], [0.4, 1.9]],
    pendulum: [[0, 2], [-3, 1.5], [4, 0], [1, -2]]
  };

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
  function stop() { /* no timers */ }

  function num(v) {
    if (!isFinite(v)) return v > 0 ? "∞" : v < 0 ? "−∞" : "NaN";
    if (Math.abs(v) < 5e-10) return "0";
    var r = Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 0.1 ? +v.toFixed(3) + "" : +v.toPrecision(3) + "";
    return String(r).replace("-", "−");
  }
  function tnum(v) { return num(v).replace("−", "-"); }
  function bmat(J) {
    return "\\begin{bmatrix} " + tnum(J[0][0]) + " & " + tnum(J[0][1]) + " \\\\ " + tnum(J[1][0]) + " & " + tnum(J[1][1]) + " \\end{bmatrix}";
  }
  function coordTex(v) {
    if (Math.abs(v) < 1e-9) return "0";
    if (Math.abs(Math.abs(v) - PI) < 1e-9) return v < 0 ? "-\\pi" : "\\pi";
    return tnum(v);
  }
  function eigText(e, tex) {
    var f = tex ? tnum : num, pm = tex ? "\\pm" : "±", i = tex ? "i" : "i";
    if (Math.abs(e.l1.im) > 1e-12) return f(e.l1.re) + " " + pm + " " + f(Math.abs(e.l1.im)) + i;
    return f(e.l1.re) + ", " + f(e.l2.re);
  }
  function stabWord(e) {
    return e.stable ? "stable" : e.kind === "center" ? "neutrally stable (center)" : "unstable";
  }
  function colourOf(e) {
    return e.stable ? "var(--green)" : e.kind === "center" ? "var(--yellow)" : "var(--red)";
  }
  var uid = 0;

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var tMax = config.tMax || 12;
    var clipIds = [++uid, ++uid].map(function (n) { return "pp-clip-" + n; });
    var trajs = {};   // per mode: list of start points
    Object.keys(STARTS).forEach(function (m) { trajs[m] = STARTS[m].map(function (p) { return p.slice(); }); });

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Where do solutions go in the plane?" }),
      ctx.mathText(h("p", { className: "lede" }), "Change the matrix $A$ and watch the trajectories of $z' = Az$. The trace $T$ and determinant $D$ decide the picture. Click the plane to start a new trajectory, or switch to a nonlinear system and read its critical points through the Jacobian.")
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
    var modeBox = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "System", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    config.modes.forEach(function (m) {
      var id = "ex-mode-" + m.id;
      var r = h("input", { type: "radio", name: "ex-mode", id: id, value: m.id });
      r.checked = st.mode === m.id;
      r.addEventListener("change", function () {
        if (r.checked) { st.mode = m.id; update(); ctx.save(); ctx.announce("System: " + m.label); }
      });
      radios[m.id] = r;
      modeBox.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
    });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (p.mode && radios[p.mode]) { st.mode = p.mode; radios[p.mode].checked = true; }
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note);
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var matBox = h("div", { className: "readout" });
    var controls = h("div", null, [
      h("h2", { text: "System" }),
      slider("a", "Entry $a$", "Matrix entry a"), slider("b", "Entry $b$", "Matrix entry b"),
      slider("c", "Entry $c$", "Matrix entry c"), slider("d", "Entry $d$", "Matrix entry d"),
      slider("k", "Damping $k$", "Pendulum damping k"),
      matBox, modeBox, presets
    ]);

    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }

    // ---- panel 1: phase plane ----
    var L = 34, Rr = 10, Tp = 10, Bt = 26, PS = 330, W1 = L + PS + Rr, H1 = Tp + PS + Bt;
    var svg1 = s("svg", { viewBox: "0 0 " + W1 + " " + H1, role: "img",
      "aria-label": "Phase plane with direction field, critical points and trajectories. Click to add a trajectory.",
      style: "touch-action:manipulation;cursor:crosshair;width:100%;height:auto" });
    var defs1 = s("defs"), clip1 = s("clipPath", { id: clipIds[0] });
    clip1.appendChild(s("rect", { x: L, y: Tp, width: PS, height: PS }));
    defs1.appendChild(clip1); svg1.appendChild(defs1);
    var grid1 = s("g"), field1 = s("g", { "clip-path": "url(#" + clipIds[0] + ")" });
    var eig1 = s("g", { "clip-path": "url(#" + clipIds[0] + ")" }), tr1 = s("g", { "clip-path": "url(#" + clipIds[0] + ")" });
    var pts1 = s("g");
    [grid1, field1, eig1, tr1, pts1].forEach(function (g) { svg1.appendChild(g); });
    var cap1 = h("p", { className: "plot-note" });
    var eigLegend = h("span", null, [sw("var(--blue)"), "eigenvector lines"]);
    var btnClear = h("button", { type: "button", className: "btn small", text: "Clear trajectories", onclick: function () {
      trajs[st.mode] = []; update(); ctx.announce("Trajectories cleared");
    } });
    var btnRand = h("button", { type: "button", className: "btn small", text: "Add trajectory at a random point", onclick: function () {
      var w = WINDOWS[st.mode];
      var p = [w.x[0] + (w.x[1] - w.x[0]) * (0.05 + 0.9 * Math.random()), w.y[0] + (w.y[1] - w.y[0]) * (0.05 + 0.9 * Math.random())];
      addTraj(p);
    } });
    var box1 = h("div", { className: "plot-box" }, [h("h3", { text: "Phase plane" }), svg1,
      h("div", { className: "legend" }, [h("span", null, [sw("var(--teal)"), "forward in time"]),
        h("span", null, [sw("rgba(20,184,166,0.4)"), "backward in time"]), eigLegend]),
      h("div", { className: "presets" }, [btnRand, btnClear]), cap1]);

    // ---- panel 2: trace-determinant ----
    var L2 = 36, W2 = 374, T2 = 12, B2 = 26, H2 = 270, pw2 = W2 - L2 - 10, ph2 = H2 - T2 - B2;
    var svg2 = s("svg", { viewBox: "0 0 " + W2 + " " + H2, role: "img", "aria-label": "Trace-determinant plane with the parabola D equals T squared over 4 and the current matrix marked", style: "width:100%;height:auto" });
    var defs2 = s("defs"), clip2 = s("clipPath", { id: clipIds[1] });
    clip2.appendChild(s("rect", { x: L2, y: T2, width: pw2, height: ph2 }));
    defs2.appendChild(clip2); svg2.appendChild(defs2);
    var grid2 = s("g"), top2 = s("g", { "clip-path": "url(#" + clipIds[1] + ")" });
    svg2.appendChild(grid2); svg2.appendChild(top2);
    var cap2 = h("p", { className: "plot-note" });
    var box2 = h("div", { className: "plot-box" }, [h("h3", { text: "Trace-determinant plane" }), svg2, cap2]);

    var infoBox = h("div", { className: "readout" }), factsBox = h("div", { className: "readout" });
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [box1, box2, presetNote, infoBox, factsBox])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function curModel() {
      if (st.mode === "predprey") return SM.models.predprey();
      if (st.mode === "pendulum") return SM.models.pendulum({ k: st.k });
      return SM.models.linear({ a: st.a, b: st.b, c: st.c, d: st.d });
    }
    function mapper() {
      var w = WINDOWS[st.mode];
      return {
        X: function (x) { return L + PS * (x - w.x[0]) / (w.x[1] - w.x[0]); },
        Y: function (y) { return Tp + PS * (w.y[1] - y) / (w.y[1] - w.y[0]); },
        w: w
      };
    }
    function addTraj(p) {
      var list = trajs[st.mode];
      list.push(p);
      while (list.length > MAX_TRAJ) list.shift();
      update();
      ctx.announce("Trajectory added at " + num(p[0]) + ", " + num(p[1]));
    }
    svg1.addEventListener("click", function (ev) {
      var r = svg1.getBoundingClientRect();
      if (!r.width || !r.height) return;
      var px = (ev.clientX - r.left) * W1 / r.width, py = (ev.clientY - r.top) * H1 / r.height;
      var w = WINDOWS[st.mode];
      if (px < L || px > L + PS || py < Tp || py > Tp + PS) return;
      addTraj([w.x[0] + (px - L) / PS * (w.x[1] - w.x[0]), w.y[1] - (py - Tp) / PS * (w.y[1] - w.y[0])]);
    });

    function pathOf(pts, M) {
      var d = "";
      pts.forEach(function (q, j) { d += (j ? "L" : "M") + M.X(q[0]).toFixed(1) + " " + M.Y(q[1]).toFixed(1) + " "; });
      return d;
    }

    function drawPlane(model) {
      var M = mapper(), w = M.w, i, v;
      clear(grid1); clear(field1); clear(eig1); clear(tr1); clear(pts1);
      // ticks and axes
      var xt = [], yt = [];
      if (st.mode === "pendulum") { xt = [-2 * PI, -PI, 0, PI, 2 * PI]; for (v = -3; v <= 3; v++) yt.push(v); }
      else { for (v = w.x[0]; v <= w.x[1] + 1e-9; v++) xt.push(v); yt = xt.slice(); }
      function xlab(v) {
        if (st.mode !== "pendulum") return num(v);
        var m = Math.round(v / PI);
        return m === 0 ? "0" : (m === 1 ? "π" : m === -1 ? "−π" : (m < 0 ? "−" : "") + Math.abs(m) + "π");
      }
      xt.forEach(function (x) {
        grid1.appendChild(s("line", { x1: M.X(x), y1: Tp, x2: M.X(x), y2: Tp + PS, "class": Math.abs(x) < 1e-9 ? "p-axis" : "p-grid" }));
        grid1.appendChild(s("text", { x: M.X(x), y: Tp + PS + 14, "text-anchor": "middle", text: xlab(x) }));
      });
      yt.forEach(function (y) {
        grid1.appendChild(s("line", { x1: L, y1: M.Y(y), x2: L + PS, y2: M.Y(y), "class": Math.abs(y) < 1e-9 ? "p-axis" : "p-grid" }));
        grid1.appendChild(s("text", { x: L - 4, y: M.Y(y) + 4, "text-anchor": "end", text: num(y) }));
      });
      grid1.appendChild(s("text", { x: L + PS, y: Tp + PS + 24, "text-anchor": "end", text: w.names[0] }));
      grid1.appendChild(s("text", { x: L + 4, y: Tp + 10, text: w.names[1] }));

      // direction field (17 x 17, arrows normalised in screen space)
      var N = 17, len = 12, d = "";
      for (i = 0; i < N; i++) for (var j = 0; j < N; j++) {
        var x = w.x[0] + (w.x[1] - w.x[0]) * (i + 0.5) / N, y = w.y[0] + (w.y[1] - w.y[0]) * (j + 0.5) / N;
        var f = model.rhs([x, y]);
        var dx = f[0] * PS / (w.x[1] - w.x[0]), dy = -f[1] * PS / (w.y[1] - w.y[0]), m = Math.hypot(dx, dy);
        if (!isFinite(m) || m < 1e-9) continue;
        dx /= m; dy /= m;
        var cx = M.X(x), cy = M.Y(y), x0 = cx - dx * len / 2, y0 = cy - dy * len / 2, x1 = cx + dx * len / 2, y1 = cy + dy * len / 2;
        d += "M" + x0.toFixed(1) + " " + y0.toFixed(1) + "L" + x1.toFixed(1) + " " + y1.toFixed(1) +
          "M" + (x1 - 3.5 * dx + 2.2 * dy).toFixed(1) + " " + (y1 - 3.5 * dy - 2.2 * dx).toFixed(1) +
          "L" + x1.toFixed(1) + " " + y1.toFixed(1) +
          "L" + (x1 - 3.5 * dx - 2.2 * dy).toFixed(1) + " " + (y1 - 3.5 * dy + 2.2 * dx).toFixed(1);
      }
      field1.appendChild(s("path", { d: d, fill: "none", style: "stroke:var(--muted);stroke-width:1;opacity:0.55;stroke-linecap:round;stroke-linejoin:round" }));

      // eigenvector lines (linear)
      var e = null;
      if (st.mode === "linear") {
        e = SM.eig2(st.a, st.b, st.c, st.d);
        [e.v1, e.v2].forEach(function (v1, idx) {
          if (!v1) return;
          if (idx === 1 && e.v1 && Math.abs(e.l1.re - e.l2.re) < 1e-9) return;
          eig1.appendChild(s("line", { x1: M.X(-20 * v1[0]), y1: M.Y(-20 * v1[1]), x2: M.X(20 * v1[0]), y2: M.Y(20 * v1[1]),
            style: "stroke:var(--blue);stroke-width:1.8;stroke-dasharray:6 4" }));
        });
      }

      // trajectories
      trajs[st.mode].forEach(function (p) {
        var n = Math.round(tMax / STEP);
        var fwd = SM.rk4(model.rhs, p, STEP, n, LIMIT);
        var neg = function (u) { var r = model.rhs(u); return [-r[0], -r[1]]; };
        var bwd = SM.rk4(neg, p, STEP, n, LIMIT);
        tr1.appendChild(s("path", { d: pathOf(bwd, M), fill: "none", style: "stroke:var(--teal);stroke-width:2;opacity:0.4;stroke-linejoin:round" }));
        tr1.appendChild(s("path", { d: pathOf(fwd, M), fill: "none", style: "stroke:var(--teal);stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round" }));
        if (fwd.length >= 3) {
          var mi = Math.floor(fwd.length / 2), a0 = fwd[mi - 1], a1 = fwd[mi + 1] || fwd[mi];
          var ax = M.X(a1[0]) - M.X(a0[0]), ay = M.Y(a1[1]) - M.Y(a0[1]), am = Math.hypot(ax, ay);
          if (am > 1e-9) {
            ax /= am; ay /= am;
            var px = M.X(fwd[mi][0]), py = M.Y(fwd[mi][1]), z = 6;
            tr1.appendChild(s("polygon", { points: [
              (px + ax * z).toFixed(1) + "," + (py + ay * z).toFixed(1),
              (px - ax * z + ay * z * 0.6).toFixed(1) + "," + (py - ay * z - ax * z * 0.6).toFixed(1),
              (px - ax * z - ay * z * 0.6).toFixed(1) + "," + (py - ay * z + ax * z * 0.6).toFixed(1)].join(" "),
              style: "fill:var(--teal)" }));
          }
        }
        tr1.appendChild(s("circle", { cx: M.X(p[0]), cy: M.Y(p[1]), r: 3, style: "fill:#fff;stroke:var(--teal);stroke-width:1.6" }));
      });

      // critical points
      SM.criticalInfo(model).forEach(function (ci) {
        pts1.appendChild(s("circle", { cx: M.X(ci.point[0]), cy: M.Y(ci.point[1]), r: 6,
          style: "fill:" + colourOf(ci.eig) + ";stroke:#fff;stroke-width:1.5" }));
      });
      eigLegend.style.display = e ? "" : "none";
    }

    function drawTD(e) {
      clear(grid2); clear(top2);
      var tl = -6, th = 6, dl = -6, dh = 9, v;
      var X = function (t) { return L2 + pw2 * (t - tl) / (th - tl); };
      var Y = function (dd) { return T2 + ph2 * (dh - dd) / (dh - dl); };
      grid2.appendChild(s("rect", { x: L2, y: Y(0), width: pw2, height: Y(dl) - Y(0), style: "fill:var(--red);opacity:0.07" }));
      for (v = -6; v <= 6; v += 2) {
        grid2.appendChild(s("line", { x1: X(v), y1: T2, x2: X(v), y2: T2 + ph2, "class": v === 0 ? "p-axis" : "p-grid" }));
        grid2.appendChild(s("text", { x: X(v), y: T2 + ph2 + 14, "text-anchor": "middle", text: num(v) }));
      }
      for (v = -6; v <= 9; v += 3) {
        grid2.appendChild(s("line", { x1: L2, y1: Y(v), x2: L2 + pw2, y2: Y(v), "class": v === 0 ? "p-axis" : "p-grid" }));
        grid2.appendChild(s("text", { x: L2 - 4, y: Y(v) + 4, "text-anchor": "end", text: num(v) }));
      }
      grid2.appendChild(s("text", { x: L2 + pw2, y: H2 - 2, "text-anchor": "end", text: "T (trace)" }));
      grid2.appendChild(s("text", { x: L2 + 4, y: T2 + 10, text: "D (determinant)" }));
      var d = "";
      for (var t = tl; t <= th + 1e-9; t += 0.25) d += (t === tl ? "M" : "L") + X(t).toFixed(1) + " " + Y(t * t / 4).toFixed(1) + " ";
      top2.appendChild(s("path", { d: d, fill: "none", style: "stroke:var(--muted);stroke-width:1.8;stroke-dasharray:6 4" }));
      top2.appendChild(s("line", { x1: X(0), y1: Y(0), x2: X(0), y2: Y(dh), style: "stroke:var(--yellow);stroke-width:2.4" }));
      function lab(t, dd, text, anchor) {
        grid2.appendChild(s("text", { x: X(t), y: Y(dd), "text-anchor": anchor || "middle", style: "font-size:11px;fill:var(--muted)", text: text }));
      }
      lab(0, -3, "saddle (D < 0)");
      lab(-3.2, 6.6, "spiral sink"); lab(3.2, 6.6, "spiral source");
      lab(-4.6, 1.8, "sink"); lab(4.6, 1.8, "source");
      lab(0.2, 8.5, "center", "start");
      var ct = Math.max(tl, Math.min(th, e.T)), cd = Math.max(dl, Math.min(dh, e.D));
      top2.appendChild(s("circle", { cx: X(ct), cy: Y(cd), r: 6, style: "fill:" + colourOf(e) + ";stroke:#fff;stroke-width:1.6" }));
      cap2.textContent = "Current (T, D) = (" + num(e.T) + ", " + num(e.D) + "); dashed parabola D = T²/4 separates nodes from spirals. Points off the window are shown at its edge.";
    }

    function update() {
      var lin = st.mode === "linear", pend = st.mode === "pendulum";
      KEYS.forEach(function (k) {
        outputs[k].textContent = num(st[k]);
        var show = k === "k" ? pend : lin;
        rows[k].hidden = !show; rows[k].style.display = show ? "" : "none";
      });
      radios[st.mode].checked = true;
      matBox.hidden = !lin; matBox.style.display = lin ? "" : "none";
      box2.hidden = !lin; box2.style.display = lin ? "" : "none";
      btnClear.disabled = !trajs[st.mode].length;
      var model = curModel();
      drawPlane(model);

      matBox.textContent = "";
      if (lin) matBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
        "A = \\begin{bmatrix} " + tnum(st.a) + " & " + tnum(st.b) + " \\\\ " + tnum(st.c) + " & " + tnum(st.d) + " \\end{bmatrix}"));

      infoBox.textContent = ""; factsBox.textContent = "";
      function fact(t, cls) {
        var el = ctx.mathText(h("p", { style: "margin:2px 0" }), t);
        if (cls) el.className = cls;
        factsBox.appendChild(el);
      }
      if (lin) {
        var e = SM.eig2(st.a, st.b, st.c, st.d);
        drawTD(e);
        var cx = Math.abs(e.l1.im) > 1e-12;
        cap1.textContent = "Direction field (grey), trajectories (teal; lighter is backward in time) and the origin, coloured by stability. Click the plane to add a trajectory.";
        fact("$T = " + tnum(e.T) + "$, $D = " + tnum(e.D) + "$, $T^2 - 4D = " + tnum(e.disc) + "$.");
        fact(cx ? "Eigenvalues $\\lambda = " + eigText(e, true) + "$." :
          "Eigenvalues $\\lambda_1 = " + tnum(e.l1.re) + "$, $\\lambda_2 = " + tnum(e.l2.re) + "$.");
        if (!cx) {
          if (e.v1 && e.v2 && Math.abs(e.l1.re - e.l2.re) > 1e-9)
            fact("Eigenvectors $v_1 = (" + tnum(e.v1[0]) + ", " + tnum(e.v1[1]) + ")$, $v_2 = (" + tnum(e.v2[0]) + ", " + tnum(e.v2[1]) + ")$.");
          else if (e.v1) fact("Eigenvector $v = (" + tnum(e.v1[0]) + ", " + tnum(e.v1[1]) + ")$ (repeated eigenvalue).");
          else fact("$A = \\lambda I$: every vector is an eigenvector.");
        } else fact("Complex eigenvalues: no real eigenvector lines.");
        fact("Classification: <b></b>".replace("<b></b>", "") + e.kind + "; " + stabWord(e) + ".", "plot-note");
      } else {
        cap1.textContent = "Critical points are coloured by the eigenvalues of the Jacobian there (green stable, red unstable, amber centre). Click the plane to add a trajectory.";
        infoBox.appendChild(h("h3", { text: "Critical points" }));
        SM.criticalInfo(model).forEach(function (ci) {
          var row = h("div", { className: "ro-eq" });
          infoBox.appendChild(ctx.displayMath(row,
            "(" + coordTex(ci.point[0]) + ",\\ " + coordTex(ci.point[1]) + "):\\quad J = " + bmat(ci.J)));
          var p = ctx.mathText(h("p", { style: "margin:2px 0 8px" }),
            "Eigenvalues $" + eigText(ci.eig, true) + "$: " + ci.eig.kind + ", " + stabWord(ci.eig) + ".");
          infoBox.appendChild(p);
        });
      }
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
