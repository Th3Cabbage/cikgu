/*
 * Linear Systems explorer: the three-stage pipeline x(0) -> z(0) -> z(t) -> x(t) live.
 * The eigenbasis T = [[1, s], [0, 1]] and D = diag(l1, l2) are chosen with sliders and A = T D T^-1
 * is built from them (StudyMath, exact formulas). Saved state: state.explorer = {l1, l2, s, x1, x2, t}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["l1", "l2", "s", "x1", "x2", "t"];
  var timer = 0;

  function cfgOf(config) { return config || {}; }

  function snap(v, c) {
    var k = Math.round((v - c.min) / c.step);
    return +(c.min + k * c.step).toFixed(6);
  }

  function defaults(config) {
    var out = {};
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }

  function restore(saved, config) {
    config = cfgOf(config);
    if (!saved || typeof saved !== "object" || !config.l1) return null;
    var out = {};
    for (var i = 0; i < KEYS.length; i++) {
      var k = KEYS[i], v = saved[k], c = config[k];
      if (typeof v !== "number" || !isFinite(v) || v < c.min - 1e-9 || v > c.max + 1e-9) return null;
      out[k] = snap(v, c);
    }
    return out;
  }

  function stop() { if (timer) { cancelAnimationFrame(timer); timer = 0; } }

  function fmt(v) {
    if (Math.abs(v) < 5e-4) return "0";
    var a = Math.abs(v), d = a >= 100 ? 1 : a >= 10 ? 2 : 3;
    return (v < 0 ? "-" : "") + (+a.toFixed(d)).toString();
  }
  function texNum(v) { return fmt(v); }
  function texMat(M) {
    return "\\begin{bmatrix}" + texNum(M[0][0]) + " & " + texNum(M[0][1]) + "\\\\ " + texNum(M[1][0]) + " & " + texNum(M[1][1]) + "\\end{bmatrix}";
  }
  function texVec(v) { return "\\begin{bmatrix}" + texNum(v[0]) + "\\\\ " + texNum(v[1]) + "\\end{bmatrix}"; }

  var KIND_TEXT = {
    stable: "Both eigenvalues negative: both modes decay and every trajectory goes to the origin.",
    unstable: "At least one eigenvalue is positive: that mode grows. Any zero-eigenvalue mode stays constant.",
    saddle: "Opposite signs (a saddle): one mode decays, the other grows, so almost every start eventually leaves along the growing eigenvector.",
    marginal: "An eigenvalue at 0: that mode neither grows nor decays."
  };

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, course = ctx.course, config = course.explorer, root = ctx.root;
    var st = ctx.state.explorer || defaults(config);
    ctx.state.explorer = st;
    var R = config.range, tMax = config.tMax;

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Map, evolve, map back" }),
      ctx.mathText(h("p", { className: "lede" }), "Choose the eigenvalues in $D$ and the eigenvector direction $c_2 = (s, 1)$ in $T$; the guide builds $A = TDT^{-1}$. Then follow $x(0) \\to z(0) = T^{-1}x(0) \\to z(t) = e^{Dt}z(0) \\to x(t) = Tz(t)$ in both coordinate systems.")
    ]));

    // ---- controls
    var inputs = {}, outputs = {};
    function slider(key, labelText) {
      var c = config[key], id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      var out = h("output", { "for": id, text: fmt(st[key]) });
      inp.addEventListener("input", function () {
        if (key === "t") stopPlay();
        st[key] = snap(parseFloat(inp.value), c); update(); ctx.save();
      });
      inputs[key] = inp; outputs[key] = out;
      return h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), labelText), out, inp]);
    }
    var presetBtns = config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn", "data-preset": p.id, text: p.label, onclick: function () {
        stopPlay();
        KEYS.forEach(function (k) { if (typeof p[k] === "number") st[k] = snap(p[k], config[k]); });
        update(); ctx.save();
        ctx.announce("Preset: " + p.label + ". " + p.note);
      } });
    });
    var playBtn = h("button", { type: "button", className: "btn", id: "ex-play", "aria-pressed": "false", text: "▶ Play t" });
    playBtn.addEventListener("click", function () { if (timer) stopPlay(); else startPlay(); });

    var controls = h("div", null, [
      h("h2", { className: "small-note", text: "Presets" }),
      h("div", { className: "presets" }, presetBtns),
      slider("l1", "$\\lambda_1$ (mode along $c_1$)"),
      slider("l2", "$\\lambda_2$ (mode along $c_2$)"),
      slider("s", "$s$: eigenvector $c_2 = (s, 1)$"),
      slider("x1", "$x_1(0)$"),
      slider("x2", "$x_2(0)$"),
      slider("t", "time $t$"),
      h("div", { className: "card-actions" }, [playBtn])
    ]);

    // ---- readouts
    var matsBox = h("div", { className: "readout" });
    var pipeBox = h("div", { className: "readout" });
    var verdict = h("p", { className: "plot-note" });
    var presetNote = h("p", { className: "plot-note" });

    // ---- planes
    var W = 300, H = 300, PAD = 26;
    function plane(title, cls) {
      var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img" });
      var clip = "clip-" + cls;
      svg.appendChild(s("defs", null, [s("clipPath", { id: clip }, [s("rect", { x: PAD, y: PAD / 2, width: W - PAD * 1.5, height: H - PAD * 1.5 })])]));
      for (var g = -R; g <= R; g++) {
        var pg = map(g, 0), qg = map(0, g);
        svg.appendChild(s("line", { x1: pg[0], y1: map(0, -R)[1], x2: pg[0], y2: map(0, R)[1], "class": g === 0 ? "p-axis" : "p-grid" }));
        svg.appendChild(s("line", { x1: map(-R, 0)[0], y1: qg[1], x2: map(R, 0)[0], y2: qg[1], "class": g === 0 ? "p-axis" : "p-grid" }));
        if (g !== 0 && g % 2 === 0) {
          svg.appendChild(s("text", { x: pg[0], y: map(0, -R)[1] + 14, "text-anchor": "middle", text: String(g).replace("-", "−") }));
          svg.appendChild(s("text", { x: map(-R, 0)[0] - 5, y: qg[1] + 4, "text-anchor": "end", text: String(g).replace("-", "−") }));
        }
      }
      var ax = cls === "x" ? ["x₁", "x₂"] : ["z₁", "z₂"];
      svg.appendChild(s("text", { x: map(R, 0)[0] - 2, y: map(0, 0)[1] - 6, "text-anchor": "end", "class": "ax-label", text: ax[0] }));
      svg.appendChild(s("text", { x: map(0, 0)[0] + 6, y: map(0, R)[1] + 12, "class": "ax-label", text: ax[1] }));
      var layer = s("g", { "clip-path": "url(#" + clip + ")" });
      svg.appendChild(layer);
      var note = h("p", { className: "plot-note" });
      var box = h("div", { className: "plot-box" }, [h("h3", { text: title }), svg, note]);
      return { svg: svg, layer: layer, note: note, box: box };
    }
    function map(x, y) {
      var u = (W - PAD * 1.5) / (2 * R);
      return [PAD + (x + R) * u, PAD / 2 + (R - y) * u];
    }
    function pts(list) { return list.map(function (p) { var q = map(p[0], p[1]); return q[0].toFixed(1) + "," + q[1].toFixed(1); }).join(" "); }

    var px = plane("Physical coordinates x", "x");
    var pz = plane("Eigenvector coordinates z", "z");
    var legend = h("div", { className: "legend" }, [
      h("span", null, [h("span", { className: "sw ev" }), "eigenvector lines (c₁, c₂)"]),
      h("span", null, [h("span", { className: "sw traj" }), "trajectory 0 ≤ t ≤ " + tMax]),
      h("span", null, [h("span", { className: "sw start" }), "start"]),
      h("span", null, [h("span", { className: "sw now" }), "now"])
    ]);

    var right = h("div", null, [
      matsBox, pipeBox, verdict,
      h("div", { className: "plots plots-even" }, [px.box, pz.box]), legend, presetNote,
      ctx.mathText(h("p", { className: "caveat" }), config.defectiveNote)
    ]);
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls, right])])
    ]));

    function draw(P, traj, now, start, ev) {
      while (P.layer.firstChild) P.layer.removeChild(P.layer.firstChild);
      ev.forEach(function (d) {
        var k = 3 * R, a = map(-k * d[0], -k * d[1]), b = map(k * d[0], k * d[1]);
        P.layer.appendChild(s("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1], "class": "p-ev" }));
      });
      P.layer.appendChild(s("polyline", { points: pts(traj), "class": "p-traj" }));
      var o = map(0, 0), q0 = map(start[0], start[1]), q = map(now[0], now[1]);
      P.layer.appendChild(s("line", { x1: o[0], y1: o[1], x2: q[0], y2: q[1], "class": "p-vec" }));
      P.layer.appendChild(s("circle", { cx: q0[0], cy: q0[1], r: 4.5, "class": "p-start" }));
      P.layer.appendChild(s("circle", { cx: q[0], cy: q[1], r: 5.5, "class": "p-now" }));
      var out = Math.abs(now[0]) > R || Math.abs(now[1]) > R;
      P.note.textContent = out ? "The current point is outside the plotted square (|value| > " + R + ")." : "";
      P.note.className = "plot-note" + (out ? " warn" : "");
    }

    function update() {
      KEYS.forEach(function (k) { inputs[k].value = st[k]; outputs[k].textContent = fmt(st[k]); });
      var r = SM.pipeline(st, st.t), tr = SM.trajectory(st, tMax, 240);
      matsBox.textContent = "";
      matsBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "T = " + texMat(r.T) + ",\\; D = " + texMat(r.D) + ",\\; T^{-1} = " + texMat(r.Tinv) + ",\\; A = TDT^{-1} = " + texMat(r.A)));
      pipeBox.textContent = "";
      pipeBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "z(0) = T^{-1}x(0) = " + texVec(r.z0) + ",\\quad z(" + fmt(st.t) + ") = e^{Dt}z(0) = " + texVec(r.zt) +
        ",\\quad x(" + fmt(st.t) + ") = Tz = " + texVec(r.xt)));
      var kind = SM.classify(st.l1, st.l2);
      verdict.textContent = KIND_TEXT[kind] + (Math.abs(st.l1 - st.l2) < 1e-9 ? " Equal eigenvalues here: A = λI is still diagonalizable (every direction is an eigenvector)." : "");
      verdict.setAttribute("data-kind", kind);
      draw(px, tr.x, r.xt, r.x0, [[1, 0], [st.s, 1]]);
      draw(pz, tr.z, r.zt, r.z0, [[1, 0], [0, 1]]);
      px.svg.setAttribute("aria-label", "Physical plane: trajectory from x(0) = (" + fmt(r.x0[0]) + ", " + fmt(r.x0[1]) + ") to x(t) = (" + fmt(r.xt[0]) + ", " + fmt(r.xt[1]) + ") at t = " + fmt(st.t));
      pz.svg.setAttribute("aria-label", "Eigenvector plane: z(0) = (" + fmt(r.z0[0]) + ", " + fmt(r.z0[1]) + "), z(t) = (" + fmt(r.zt[0]) + ", " + fmt(r.zt[1]) + ")");
      var match = config.presets.filter(function (p) { return KEYS.every(function (k) { return typeof p[k] !== "number" || Math.abs(p[k] - st[k]) < 1e-6 || k === "t"; }); })[0];
      presetBtns.forEach(function (b) { b.setAttribute("aria-pressed", match && b.getAttribute("data-preset") === match.id ? "true" : "false"); });
      presetNote.textContent = "";
      if (match) ctx.mathText(presetNote, match.note);
    }

    function stopPlay() { stop(); playBtn.textContent = "▶ Play t"; playBtn.setAttribute("aria-pressed", "false"); }
    function startPlay() {
      var speed = (window.__studyExplorerSpeed || 1) * config.playRate, last = null;
      if (st.t >= tMax - 1e-9) st.t = 0;
      playBtn.textContent = "❚❚ Pause"; playBtn.setAttribute("aria-pressed", "true");
      function frame(ts) {
        if (last !== null) st.t = Math.min(tMax, st.t + (ts - last) / 1000 * speed);
        last = ts;
        update();
        if (st.t >= tMax) { stopPlay(); ctx.save(); return; }
        timer = requestAnimationFrame(frame);
      }
      timer = requestAnimationFrame(frame);
    }

    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
