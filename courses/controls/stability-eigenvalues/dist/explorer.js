/*
 * Stability and Eigenvalues explorer: one 2x2 system seen three ways, live.
 *   left plane   eigenvalues lambda of A (stable left half-plane shaded)
 *   right plane  eigenvalues e^{lambda dt} of the sampled A~ = e^{A dt}, the unit circle and the powers lambda~^k
 *   time plot    x1(t), x2(t) from x(0) for 0 <= t <= tMax, with the samples x_k = A~^k x_0 as dots
 * The system is A = T J T^-1 with T = [[1, s], [0, 1]] and a real canonical form J (StudyMath, exact closed forms).
 * Verdicts come from the eigenvalues / Jordan structure (StudyMath.classify*), never from the plotted window.
 * Saved state: state.explorer = {kind, l1, l2, a, b, lj, s, x1, x2, dt, t}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["l1", "l2", "a", "b", "lj", "s", "x1", "x2", "dt", "t"];
  var timer = 0;

  function snap(v, c) {
    var k = Math.round((v - c.min) / c.step);
    return +(Math.min(c.max, Math.max(c.min, c.min + k * c.step))).toFixed(6);
  }

  function kindIds(config) { return (config.kinds || []).map(function (k) { return k.id; }); }

  function defaults(config) {
    var out = { kind: config.kindDefault };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }

  // Accept saved settings only if every value is a finite number inside its slider range and the kind is known.
  function restore(saved, config) {
    config = config || {};
    if (!saved || typeof saved !== "object" || !config.l1 || kindIds(config).indexOf(saved.kind) < 0) return null;
    var out = { kind: saved.kind };
    for (var i = 0; i < KEYS.length; i++) {
      var k = KEYS[i], v = saved[k], c = config[k];
      if (typeof v !== "number" || !isFinite(v) || v < c.min - 1e-9 || v > c.max + 1e-9) return null;
      out[k] = snap(v, c);
    }
    return out;
  }

  // Cancelling active playback (navigation, re-render, pagehide) also saves the latest time via onStop.
  var onStop = null;
  function stop() { if (timer) { cancelAnimationFrame(timer); timer = 0; if (onStop) onStop(); } }
  if (typeof window.addEventListener === "function") window.addEventListener("pagehide", stop);

  // Colour class of ONE eigenvalue from its own margin (Re lambda, or |lambda~| - 1): decaying modes are
  // "stable", growing "unstable", boundary "marginal" unless defective (then "unstable").
  function eigClass(margin, defective) {
    if (margin < -SM.TOL) return "stable";
    if (margin > SM.TOL) return "unstable";
    return defective ? "unstable" : "marginal";
  }

  function fmt(v) {
    if (!isFinite(v)) return "∞";
    var a = Math.abs(v);
    if (a < 5e-4) return "0";
    if (a >= 1e4) return v.toExponential(2).replace("e+", "e");
    var d = a >= 100 ? 1 : a >= 10 ? 2 : 3;
    return (v < 0 ? "-" : "") + (+a.toFixed(d)).toString();
  }
  function texNum(v) {
    var s = fmt(v);
    var m = /^(-?[\d.]+)e(-?\d+)$/.exec(s);
    return m ? m[1] + "\\times 10^{" + m[2] + "}" : s;
  }
  function texMat(M) {
    return "\\begin{bmatrix}" + texNum(M[0][0]) + " & " + texNum(M[0][1]) + "\\\\ " + texNum(M[1][0]) + " & " + texNum(M[1][1]) + "\\end{bmatrix}";
  }
  function texC(z) {
    if (Math.abs(z.im) < 5e-4) return texNum(z.re);
    return texNum(z.re) + (z.im < 0 ? " - " : " + ") + texNum(Math.abs(z.im)) + "i";
  }
  function texPair(vals) {
    // conjugate pair -> a \pm bi ; equal values -> "x (twice)"
    var p = vals[0], q = vals[1];
    if (Math.abs(p.im) > 5e-4 && Math.abs(p.re - q.re) < 1e-12 && Math.abs(p.im + q.im) < 1e-12)
      return texNum(p.re) + " \\pm " + texNum(Math.abs(p.im)) + "i";
    if (Math.abs(p.re - q.re) < 1e-12 && Math.abs(p.im - q.im) < 1e-12) return texC(p) + "\\ (\\text{twice})";
    return texC(p) + ",\\ " + texC(q);
  }

  var SYS_TEXT = {
    asymptotic: "Asymptotically stable: every eigenvalue has Re λ < 0, equivalently every sampled eigenvalue lies inside the unit circle, so every solution decays to 0.",
    lyapunov: "Lyapunov stable, not asymptotically stable (Supplement): the largest real part is exactly 0 and those eigenvalues are semisimple (sampled eigenvalues on the unit circle). Every solution stays bounded, but not every solution decays.",
    unstablePos: "Unstable: an eigenvalue has Re λ > 0 (its sampled eigenvalue lies outside the unit circle), so every start with a component along it grows without bound.",
    unstableJordan: "Unstable (Supplement): a defective eigenvalue sits on the boundary (Jordan block with Re λ = 0, on the unit circle after sampling), which gives growth like t even though no real part is positive."
  };
  var START_TEXT = {
    decays: "This start decays to 0.",
    bounded: "This start stays bounded but does not decay to 0.",
    grows: "This start grows without bound.",
    rest: "x(0) = 0 stays at rest."
  };
  var DATA_KIND = { asymptotic: "stable", lyapunov: "marginal", unstable: "unstable" };

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer || defaults(config);
    ctx.state.explorer = st;
    onStop = function () { ctx.save(); };   // keep the latest playback time if playback is cut off
    var tMax = config.tMax;

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Where are the eigenvalues?" }),
      ctx.mathText(h("p", { className: "lede" }), "Choose a 2×2 system by its eigenvalues. Watch them in the continuous-time plane, after sampling as $\\tilde\\lambda = e^{\\lambda\\Delta t}$ with the unit circle, and in the time response $x(t)$ with the samples $x_k = \\tilde A^k x_0$.")
    ]));

    // ---- controls
    var inputs = {}, outputs = {}, rows = {};
    function slider(key, labelText) {
      var c = config[key], id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      var out = h("output", { "for": id, text: fmt(st[key]) });
      inp.addEventListener("input", function () {
        if (key === "t") stopPlay();
        st[key] = snap(parseFloat(inp.value), c); update(); ctx.save();
      });
      inputs[key] = inp; outputs[key] = out;
      rows[key] = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), labelText), out, inp]);
      return rows[key];
    }
    var kindBtns = config.kinds.map(function (k) {
      return h("button", { type: "button", className: "btn", "data-kind": k.id, text: k.label, onclick: function () {
        stopPlay(); st.kind = k.id; update(); ctx.save(); ctx.announce("Eigenvalue type: " + k.label);
      } });
    });
    var presetBtns = config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn", "data-preset": p.id, text: p.label, onclick: function () {
        stopPlay();
        st.kind = p.kind;
        KEYS.forEach(function (k) { if (typeof p[k] === "number") st[k] = snap(p[k], config[k]); });
        update(); ctx.save();
        ctx.announce("Preset: " + p.label + ".");
      } });
    });
    var playBtn = h("button", { type: "button", className: "btn", id: "ex-play", "aria-pressed": "false", text: "▶ Play t" });
    playBtn.addEventListener("click", function () { if (timer) { stopPlay(); ctx.save(); } else startPlay(); });

    var controls = h("div", null, [
      h("h2", { className: "small-note", text: "Presets" }),
      h("div", { className: "presets" }, presetBtns),
      h("h2", { className: "small-note", text: "Eigenvalue type" }),
      h("div", { className: "presets", role: "group", "aria-label": "Eigenvalue type" }, kindBtns),
      slider("l1", "$\\lambda_1$ (along $c_1 = (1, 0)$)"),
      slider("l2", "$\\lambda_2$ (along $c_2 = (s, 1)$)"),
      slider("a", "real part $a$"),
      slider("b", "imaginary part $b$ ($\\lambda = a \\pm ib$)"),
      slider("lj", "repeated $\\lambda$ (Jordan block)"),
      slider("s", "basis shear $s$ in $T = \\begin{bmatrix}1&s\\\\0&1\\end{bmatrix}$"),
      slider("x1", "$x_1(0)$"),
      slider("x2", "$x_2(0)$"),
      slider("dt", "sampling step $\\Delta t$"),
      slider("t", "time $t$"),
      h("div", { className: "card-actions" }, [playBtn])
    ]);

    // ---- readouts
    var matsBox = h("div", { className: "readout" });
    var eigBox = h("div", { className: "readout" });
    var vSys = h("p", { className: "plot-note verdict", id: "ex-verdict" });
    var vStart = h("p", { className: "plot-note", id: "ex-start" });
    var presetNote = h("p", { className: "plot-note", id: "ex-preset-note" });

    // ---- planes
    var W = 300, H = 300, PAD = 26;
    function planeBox(title, id) {
      var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", id: id });
      var clip = "clip-" + id;
      svg.appendChild(s("defs", null, [s("clipPath", { id: clip }, [s("rect", { x: PAD, y: PAD / 2, width: W - PAD * 1.5, height: H - PAD * 1.5 })])]));
      var back = s("g"), layer = s("g", { "clip-path": "url(#" + clip + ")" }), front = s("g");
      svg.appendChild(back); svg.appendChild(layer); svg.appendChild(front);
      var note = h("p", { className: "plot-note" });
      var box = h("div", { className: "plot-box" }, [h("h3", { text: title }), svg, note]);
      return { svg: svg, back: back, layer: layer, front: front, note: note, box: box };
    }
    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function mapper(x0, x1, y0, y1) {
      var w = W - PAD * 1.5, hh = H - PAD * 1.5;
      return function (x, y) { return [PAD + (x - x0) / (x1 - x0) * w, PAD / 2 + (y1 - y) / (y1 - y0) * hh]; };
    }
    function crossAt(g, p, cls, label) {
      var r = 6;
      g.appendChild(s("path", { d: "M" + (p[0] - r) + " " + (p[1] - r) + "L" + (p[0] + r) + " " + (p[1] + r) + "M" + (p[0] + r) + " " + (p[1] - r) + "L" + (p[0] - r) + " " + (p[1] + r), "class": "pole " + cls }));
      if (label) g.appendChild(s("text", { x: p[0] + 8, y: p[1] - 8, "class": "ax-label", text: label }));
    }

    var lp = planeBox("Continuous time: eigenvalues λ of A", "ex-lplane");
    var zp = planeBox("Discrete time: sampled eigenvalues exp(λΔt) of Ã", "ex-zplane");

    // time plot
    var TW = 640, TH = 260, TL = 44, TR = 12, TT = 12, TB = 28;
    var tsvg = s("svg", { viewBox: "0 0 " + TW + " " + TH, role: "img", id: "ex-tplot" });
    tsvg.appendChild(s("defs", null, [s("clipPath", { id: "clip-t" }, [s("rect", { x: TL, y: TT, width: TW - TL - TR, height: TH - TT - TB })])]));
    var tBack = s("g"), tLayer = s("g", { "clip-path": "url(#clip-t)" }), tFront = s("g");
    tsvg.appendChild(tBack); tsvg.appendChild(tLayer); tsvg.appendChild(tFront);
    var tNote = h("p", { className: "plot-note", id: "ex-tnote" });
    var tBox = h("div", { className: "plot-box" }, [h("h3", { text: "Time response x(t) and samples xₖ" }), tsvg, tNote]);
    var legend = h("div", { className: "legend" }, [
      h("span", null, [h("span", { className: "sw x1" }), "x₁(t)"]),
      h("span", null, [h("span", { className: "sw x2" }), "x₂(t)"]),
      h("span", null, [h("span", { className: "sw samp" }), "samples xₖ = Ãᵏx₀"]),
      h("span", null, [h("span", { className: "sw trail" }), "powers of the largest sampled eigenvalue"])
    ]);

    var right = h("div", null, [
      matsBox, eigBox, vSys, vStart,
      h("div", { className: "plots plots-even" }, [lp.box, zp.box]), tBox, legend, presetNote,
      h("p", { className: "caveat", id: "ex-limits", text: config.limits })
    ]);
    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls, right])])
    ]));

    // ---- drawing
    function drawL(ev, verdict) {
      var X0 = -2.5, X1 = 1.5, Y0 = -4.5, Y1 = 4.5, m = mapper(X0, X1, Y0, Y1);
      clear(lp.back); clear(lp.layer); clear(lp.front);
      var o = m(0, 0), tl = m(X0, Y1), br = m(X1, Y0);
      lp.back.appendChild(s("rect", { x: tl[0], y: tl[1], width: o[0] - tl[0], height: br[1] - tl[1], "class": "p-stable" }));
      lp.back.appendChild(s("rect", { x: o[0], y: tl[1], width: br[0] - o[0], height: br[1] - tl[1], "class": "p-unstable" }));
      for (var gx = -2; gx <= 1; gx++) {
        var p = m(gx, 0);
        lp.back.appendChild(s("line", { x1: p[0], y1: tl[1], x2: p[0], y2: br[1], "class": gx === 0 ? "p-imag" : "p-grid" }));
        if (gx !== 0) lp.back.appendChild(s("text", { x: p[0], y: br[1] + 14, "text-anchor": "middle", text: String(gx).replace("-", "−") }));
      }
      for (var gy = -4; gy <= 4; gy += 2) {
        var q = m(0, gy);
        lp.back.appendChild(s("line", { x1: tl[0], y1: q[1], x2: br[0], y2: q[1], "class": gy === 0 ? "p-axis" : "p-grid" }));
        if (gy !== 0) lp.back.appendChild(s("text", { x: tl[0] - 4, y: q[1] + 4, "text-anchor": "end", text: (String(gy) + "i").replace("-", "−") }));
      }
      lp.back.appendChild(s("text", { x: br[0] - 2, y: o[1] - 5, "text-anchor": "end", "class": "ax-label", text: "Re λ" }));
      lp.back.appendChild(s("text", { x: o[0] + 5, y: tl[1] + 12, "class": "ax-label", text: "Im λ" }));
      var pts = ev.values.map(function (v) { return m(v.re, v.im); });
      var cl = ev.values.map(function (v) { return eigClass(v.re, ev.defective); });
      if (ev.defective || (Math.abs(ev.values[0].re - ev.values[1].re) < 1e-12 && Math.abs(ev.values[0].im - ev.values[1].im) < 1e-12)) {
        crossAt(lp.front, pts[0], cl[0], ev.defective ? "×2 (one eigenvector)" : "×2");
      } else {
        pts.forEach(function (p, i) { crossAt(lp.front, p, cl[i]); });
      }
      lp.svg.setAttribute("aria-label", "Continuous-time eigenvalues: " + ev.values.map(function (v) { return fmt(v.re) + (Math.abs(v.im) > 5e-4 ? (v.im < 0 ? " − " : " + ") + fmt(Math.abs(v.im)) + "i" : ""); }).join(", ") + (ev.defective ? " (defective)" : ""));
      lp.note.textContent = "";
    }

    function drawZ(evd, verdict, kNow) {
      var rMax = Math.max.apply(null, evd.values.map(function (v) { return v.r; }));
      var R = Math.min(4, Math.max(1.5, Math.ceil(rMax * 1.15 * 2) / 2));
      var m = mapper(-R, R, -R, R), o = m(0, 0), u = (W - PAD * 1.5) / (2 * R);
      clear(zp.back); clear(zp.layer); clear(zp.front);
      var tl = m(-R, R), br = m(R, -R);
      zp.back.appendChild(s("rect", { x: tl[0], y: tl[1], width: br[0] - tl[0], height: br[1] - tl[1], "class": "p-unstable" }));
      zp.back.appendChild(s("circle", { cx: o[0], cy: o[1], r: u, "class": "p-disc" }));
      zp.back.appendChild(s("line", { x1: tl[0], y1: o[1], x2: br[0], y2: o[1], "class": "p-axis" }));
      zp.back.appendChild(s("line", { x1: o[0], y1: tl[1], x2: o[0], y2: br[1], "class": "p-axis" }));
      zp.back.appendChild(s("circle", { cx: o[0], cy: o[1], r: u, "class": "p-unit" }));
      [-1, 1].forEach(function (v) {
        var p = m(v, 0);
        zp.back.appendChild(s("text", { x: p[0] + (v > 0 ? 4 : -4), y: o[1] + 14, "text-anchor": v > 0 ? "start" : "end", text: String(v).replace("-", "−") }));
      });
      zp.back.appendChild(s("text", { x: br[0] - 2, y: o[1] - 5, "text-anchor": "end", "class": "ax-label", text: "Re" }));
      zp.back.appendChild(s("text", { x: o[0] + 5, y: tl[1] + 12, "class": "ax-label", text: "Im" }));
      zp.back.appendChild(s("text", { x: tl[0] + 4, y: br[1] - 6, text: "radius ≤ " + fmt(R) + " shown" }));
      // powers of the eigenvalue with the largest radius (upper one of a pair)
      var lead = evd.values.slice().sort(function (p, q) { return q.r - p.r || q.im - p.im; })[0];
      var pw = SM.powers(lead, kNow), outside = false;
      var trail = pw.map(function (z) { if (Math.abs(z[0]) > R || Math.abs(z[1]) > R) outside = true; var p = m(Math.max(-3 * R, Math.min(3 * R, z[0])), Math.max(-3 * R, Math.min(3 * R, z[1]))); return p[0].toFixed(1) + "," + p[1].toFixed(1); });
      zp.layer.appendChild(s("polyline", { points: trail.join(" "), "class": "p-trail" }));
      pw.forEach(function (z) { var p = m(z[0], z[1]); zp.layer.appendChild(s("circle", { cx: p[0], cy: p[1], r: 2.4, "class": "p-trail-dot" })); });
      var off = [];
      evd.values.forEach(function (v) {
        if (Math.abs(v.re) > R || Math.abs(v.im) > R) off.push(v);
        else crossAt(zp.front, m(v.re, v.im), eigClass(v.r - 1, evd.defective));
      });
      var msgs = [];
      if (off.length) msgs.push("An eigenvalue (radius " + fmt(off[0].r) + ") lies outside the plotted square.");
      if (outside) msgs.push("Its powers leave the plotted square.");
      zp.note.textContent = msgs.join(" ");
      zp.note.className = "plot-note" + (msgs.length ? " warn" : "");
      zp.svg.setAttribute("aria-label", "Discrete-time eigenvalues: " + evd.values.map(function (v) { return "radius " + fmt(v.r) + ", angle " + fmt(v.theta) + " rad"; }).join("; ") + ". Unit circle drawn. Powers up to k = " + kNow + ".");
    }

    var NICE = [1, 2, 3, 5, 10, 20, 50];
    function drawT(traj, samp) {
      var peak = 0;
      traj.forEach(function (p) { peak = Math.max(peak, Math.abs(p.x[0]), Math.abs(p.x[1])); });
      var Y = NICE[NICE.length - 1];
      for (var i = 0; i < NICE.length; i++) if (peak <= NICE[i] * 1.0001) { Y = NICE[i]; break; }
      var clipped = peak > Y * 1.0001;
      function px(t) { return TL + t / tMax * (TW - TL - TR); }
      function py(y) { return TT + (Y - y) / (2 * Y) * (TH - TT - TB); }
      clear(tBack); clear(tLayer); clear(tFront);
      for (var t = 0; t <= tMax; t += 1) {
        tBack.appendChild(s("line", { x1: px(t), y1: TT, x2: px(t), y2: TH - TB, "class": "p-grid" }));
        if (t % 2 === 0) tBack.appendChild(s("text", { x: px(t), y: TH - TB + 15, "text-anchor": "middle", text: String(t) }));
      }
      [-Y, -Y / 2, 0, Y / 2, Y].forEach(function (y) {
        tBack.appendChild(s("line", { x1: TL, y1: py(y), x2: TW - TR, y2: py(y), "class": y === 0 ? "p-axis" : "p-grid" }));
        tBack.appendChild(s("text", { x: TL - 5, y: py(y) + 4, "text-anchor": "end", text: fmt(y).replace("-", "−") }));
      });
      tBack.appendChild(s("text", { x: TW - TR - 2, y: TH - TB - 5, "text-anchor": "end", "class": "ax-label", text: "t" }));
      // clip each segment to |y| <= 1.05 Y so off-scale values never become huge SVG coordinates
      function series(idx, cls) {
        var lim = Y * 1.05, segs = [], cur = [];
        function push(t, y) { cur.push(px(t).toFixed(1) + "," + py(y).toFixed(1)); }
        for (var k = 0; k < traj.length; k++) {
          var t1 = traj[k].t, y1 = traj[k].x[idx];
          if (k === 0) { if (Math.abs(y1) <= lim) push(t1, y1); continue; }
          var t0 = traj[k - 1].t, y0 = traj[k - 1].x[idx];
          var in0 = Math.abs(y0) <= lim, in1 = Math.abs(y1) <= lim;
          if (in0 && in1) { push(t1, y1); continue; }
          if (in0 && !in1) { var yb = y1 > 0 ? lim : -lim; push(t0 + (t1 - t0) * (yb - y0) / (y1 - y0), yb); segs.push(cur); cur = []; continue; }
          if (!in0 && in1) { var ya = y0 > 0 ? lim : -lim; push(t0 + (t1 - t0) * (ya - y0) / (y1 - y0), ya); push(t1, y1); continue; }
          if (y0 * y1 < 0) {   // jumped across the whole window in one step
            var ta = t0 + (t1 - t0) * ((y0 > 0 ? lim : -lim) - y0) / (y1 - y0), tb = t0 + (t1 - t0) * ((y1 > 0 ? lim : -lim) - y0) / (y1 - y0);
            push(ta, y0 > 0 ? lim : -lim); push(tb, y1 > 0 ? lim : -lim); segs.push(cur); cur = [];
          }
        }
        if (cur.length) segs.push(cur);
        segs.forEach(function (sg) { if (sg.length > 1) tLayer.appendChild(s("polyline", { points: sg.join(" "), "class": cls })); });
      }
      series(0, "p-x1"); series(1, "p-x2");
      samp.forEach(function (q) {
        [0, 1].forEach(function (i) {
          if (Math.abs(q.x[i]) <= Y) tLayer.appendChild(s("circle", { cx: px(q.t), cy: py(q.x[i]), r: 2.6, "class": i ? "p-samp2" : "p-samp1" }));
        });
      });
      tFront.appendChild(s("line", { x1: px(st.t), y1: TT, x2: px(st.t), y2: TH - TB, "class": "p-cursor" }));
      var end = traj[traj.length - 1].x, endN = Math.hypot(end[0], end[1]);
      var msg = "Window 0 ≤ t ≤ " + tMax + " only: the verdict above comes from the eigenvalues, not from this picture.";
      if (clipped) msg = "The curves leave the plotted range ±" + Y + " (at t = " + tMax + ", |x| ≈ " + fmt(endN) + "). " + msg;
      tNote.textContent = msg;
      tNote.className = "plot-note" + (clipped ? " warn" : "");
      var now = SM.state(st, st.t);
      tsvg.setAttribute("aria-label", "Time response from x(0) = (" + fmt(st.x1) + ", " + fmt(st.x2) + "); at t = " + fmt(st.t) + ", x = (" + fmt(now[0]) + ", " + fmt(now[1]) + "). Vertical scale ±" + Y + ".");
    }

    function update() {
      KEYS.forEach(function (k) { inputs[k].value = st[k]; outputs[k].textContent = fmt(st[k]); });
      kindBtns.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-kind") === st.kind ? "true" : "false"); });
      rows.l1.hidden = rows.l2.hidden = st.kind !== "real";
      rows.a.hidden = rows.b.hidden = st.kind !== "complex";
      rows.lj.hidden = st.kind !== "jordan";

      var sys = SM.system(st), ev = SM.eigen(st), evd = SM.eigenDiscrete(st, st.dt), Ad = SM.expA(st, st.dt);
      var vc = SM.classifyContinuous(st), vd = SM.classifyDiscrete(st, st.dt), sb = SM.startBehaviour(st);
      matsBox.textContent = "";
      matsBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "J = " + texMat(sys.J) + ",\\; A = TJT^{-1} = " + texMat(sys.A) + ",\\; \\tilde A = e^{A\\Delta t} = " + texMat(Ad)));
      eigBox.textContent = "";
      eigBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "\\lambda = " + texPair(ev.values) + (ev.defective ? "\\ (\\text{defective})" : "") +
        ",\\quad \\tilde\\lambda = e^{\\lambda\\Delta t} = " + texPair(evd.values) +
        ",\\quad |\\tilde\\lambda| = " + evd.values.map(function (v) { return texNum(v.r); }).filter(function (v, i, a) { return a.indexOf(v) === i; }).join(",\\ ")));
      var maxRe = Math.max(ev.values[0].re, ev.values[1].re);
      var sysText = vc === "unstable" ? (maxRe > SM.TOL ? SYS_TEXT.unstablePos : SYS_TEXT.unstableJordan) : SYS_TEXT[vc];
      if (vd !== vc) sysText += " (Discrete-time check disagrees: " + vd + ".)";
      vSys.textContent = sysText;
      vSys.setAttribute("data-kind", DATA_KIND[vc]);
      var startText = START_TEXT[sb];
      if (vc === "unstable" && (sb === "decays" || sb === "bounded")) startText += " It avoids the growing direction exactly; almost every other start grows, so the system is still unstable.";
      if (vc === "lyapunov" && sb === "decays") startText += " It has no component along the boundary mode; other starts do not decay.";
      vStart.textContent = startText;

      var kNow = Math.floor(st.t / st.dt + 1e-9);
      drawL(ev, vc);
      drawZ(evd, vc, kNow);
      drawT(SM.trajectory(st, tMax, 400), SM.samples(st, st.dt, tMax));

      var match = config.presets.filter(function (p) {
        return p.kind === st.kind && KEYS.every(function (k) { return k === "t" || typeof p[k] !== "number" || Math.abs(p[k] - st[k]) < 1e-6; });
      })[0];
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
