/*
 * Linearizing Around a Fixed Point explorer: the original nonlinear pendulum beside its local linear model.
 *   pendulums   both drawn at their absolute angles theta = theta_bar + eta (same start, same input)
 *   time plot   eta(t) for both models on 0 <= t <= T_MAX, with the current time as a cursor
 *   phase plot  (eta, nu) trajectories for both models
 * The equilibrium buttons choose theta_bar (0 down, pi up); every slider is a PERTURBATION from that point,
 * so switching the point never reinterprets a value as an absolute angle (the labels and readout say so).
 * Damping d is taught in the lecture (MATLAB d = 0.1, the default); the book's example is d = 0. The constant
 * input delta_u and the angle output y = theta are the book-supported input/output extension. Verdicts are
 * about the ZERO-INPUT reference (theta_bar, 0, u_bar = 0) and come from the Jacobian plus, for the undamped
 * hanging center, the pendulum's conserved energy - never from the plotted window or a forced trajectory.
 * Saved state: state.explorer = {eq, eta0, nu0, q, du, d, t}. Math: StudyMath (study_math.js).
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = SM.KEYS, PARAMS = SM.PARAMS, T_MAX = SM.T_MAX, N_PTS = 480;
  var timer = 0, onStop = null;

  function snap(v, c) {
    var k = Math.round((v - c.min) / c.step);
    return +(Math.min(c.max, Math.max(c.min, c.min + k * c.step))).toFixed(6);
  }
  function defaults() {
    var out = { eq: "down" };
    KEYS.forEach(function (k) { out[k] = PARAMS[k].default; });
    return out;
  }

  // Accept saved settings only if the equilibrium is known and every value is finite and inside its range.
  function restore(saved) {
    if (!saved || typeof saved !== "object" || !Object.prototype.hasOwnProperty.call(SM.EQUILIBRIA, saved.eq)) return null;
    var out = { eq: saved.eq };
    for (var i = 0; i < KEYS.length; i++) {
      var k = KEYS[i], v = saved[k], c = PARAMS[k];
      if (typeof v !== "number" || !isFinite(v) || v < c.min - 1e-9 || v > c.max + 1e-9) return null;
      out[k] = snap(v, c);
    }
    return out;
  }

  function stop() { if (timer) { cancelAnimationFrame(timer); timer = 0; if (onStop) onStop(); } }
  if (typeof window.addEventListener === "function") window.addEventListener("pagehide", stop);

  function fmt(v, digits) {
    if (!isFinite(v)) return "∞";
    var a = Math.abs(v);
    if (a < 5e-5) return "0";
    if (a >= 1e4 || a < 1e-3) return v.toExponential(1).replace("e+", "e");
    var d = digits !== undefined ? digits : a >= 100 ? 1 : a >= 10 ? 2 : 3;
    return (v < 0 ? "−" : "") + (+a.toFixed(d)).toString();
  }
  function tex(v, digits) {
    var s = fmt(v, digits).replace("−", "-");
    var m = /^(-?[\d.]+)e(-?\d+)$/.exec(s);
    return m ? m[1] + "\\times 10^{" + m[2] + "}" : s;
  }
  function texMat(M) { return "\\begin{bmatrix}" + M.map(function (r) { return r.map(function (v) { return tex(v); }).join(" & "); }).join("\\\\ ") + "\\end{bmatrix}"; }
  function texEig(ev) {
    var p = ev[0], q = ev[1];
    if (Math.abs(p.im) > 1e-12) return (Math.abs(p.re) < 5e-5 ? "" : tex(p.re) + " ") + "\\pm " + tex(Math.abs(p.im)) + "i";
    if (Math.abs(p.re - q.re) < 1e-9) return tex(p.re) + "\\ (\\text{twice})";
    return tex(p.re) + ",\\ " + tex(q.re);
  }
  var BAR = { down: "0", up: "\\pi" };

  var LINEAR_TEXT = {
    center: "Jacobian at the zero-input reference: a linear center. With d = 0 both eigenvalues are purely imaginary, ±i√q, so the local linear model oscillates forever without growing or decaying.",
    saddle: "Jacobian at the zero-input reference: a saddle. The eigenvalues (−d ± √(d² + 4q))/2 are real with opposite signs for every d ≥ 0, so the local linear model has one growing and one decaying direction.",
    focus: "Jacobian at the zero-input reference: an underdamped stable focus (0 < d < 2√q). The eigenvalues are complex with negative real part −d/2: decaying oscillation.",
    critical: "Jacobian at the zero-input reference: critically damped, d = 2√q. There is a repeated negative real eigenvalue −d/2.",
    node: "Jacobian at the zero-input reference: an overdamped stable node (d > 2√q). Both eigenvalues are real and negative, so there is no oscillation."
  };
  var NONLINEAR_TEXT = {
    lyapunov: "Conclusion for the zero-input reference of the original pendulum: stable (Lyapunov) but not asymptotically stable. Imaginary eigenvalues alone are inconclusive for a general nonlinear system. This pendulum needs its own argument: with d = 0 its energy E = ω²/2 + q(1 − cos θ) is conserved and has a strict minimum at the hanging position, so nearby solutions stay on closed energy curves and keep oscillating; they do not settle.",
    asymptotic: "Conclusion for the zero-input reference of the original pendulum: locally asymptotically stable. Every Jacobian eigenvalue has a negative real part (hyperbolic), so small offsets decay to rest. The linearization alone justifies this local statement.",
    unstable: "Conclusion for the zero-input reference of the original pendulum: unstable. A Jacobian eigenvalue with a positive real part implies the nonlinear fixed point is unstable: almost every small offset grows until the local model stops applying."
  };
  var DATA_KIND = { lyapunov: "marginal", asymptotic: "stable", unstable: "unstable" };
  var NICE = [0.1, 0.25, 0.5, 1, 2, 4, 8];
  function niceUp(v) { for (var i = 0; i < NICE.length; i++) if (v <= NICE[i] * 1.0001) return NICE[i]; return NICE[NICE.length - 1]; }

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, root = ctx.root, config = (ctx.course && ctx.course.explorer) || {};
    var st = ctx.state.explorer || defaults();
    ctx.state.explorer = st;
    onStop = function () { ctx.save(); };

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "The pendulum and its local linear model" }),
      ctx.mathText(h("p", { className: "lede" }), "Pick a fixed point $\\bar\\theta$ and start nearby. The original damped pendulum $\\dot\\theta = \\omega,\\ \\dot\\omega = -q\\sin\\theta - d\\,\\omega$ runs beside its linearization $\\dot\\eta = \\nu,\\ \\dot\\nu = -q\\cos\\bar\\theta\\,\\eta - d\\,\\nu$ from the same start. The defaults $q = 1$, $d = 0.1$ are the lecture's MATLAB example. The linear model is a local approximation, so watch where the two agree and where they part.")
    ]));

    // ---- controls
    var inputs = {}, outputs = {};
    function slider(key, labelText, unit) {
      var c = PARAMS[key], id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      var out = h("output", { "for": id });
      inp.addEventListener("input", function () {
        if (key === "t") stopPlay();
        st[key] = snap(parseFloat(inp.value), c); update(); ctx.save();
      });
      inputs[key] = inp; outputs[key] = { node: out, unit: unit || "" };
      return h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), labelText), out, inp]);
    }
    var eqBtns = [["down", "Hanging down, θ̄ = 0"], ["up", "Inverted up, θ̄ = π"]].map(function (e) {
      return h("button", { type: "button", className: "btn", "data-eq": e[0], text: e[1], onclick: function () {
        if (st.eq === e[0]) return;
        st.eq = e[0]; update(); ctx.save();
        ctx.announce("Fixed point " + e[1] + ". Offsets are measured from it: θ(0) = θ̄ + η(0) = " + fmt(SM.EQUILIBRIA[st.eq] + st.eta0) + " rad.");
      } });
    });
    var presetBtns = SM.PRESETS.map(function (p) {
      return h("button", { type: "button", className: "btn", "data-preset": p.id, text: p.label, onclick: function () {
        stopPlay();
        st.eq = p.eq;
        KEYS.forEach(function (k) { if (k !== "t") st[k] = snap(p[k], PARAMS[k]); });
        st.t = 0;
        update(); ctx.save();
        ctx.announce("Preset: " + p.label + ".");
      } });
    });
    var playBtn = h("button", { type: "button", className: "btn", id: "ex-play", "aria-pressed": "false", text: "▶ Play t" });
    playBtn.addEventListener("click", function () { if (timer) { stopPlay(); ctx.save(); } else startPlay(); });

    var controls = h("div", null, [
      h("h2", { className: "small-note", text: "Fixed point" }),
      h("div", { className: "presets", role: "group", "aria-label": "Fixed point" }, eqBtns),
      h("h2", { className: "small-note", text: "Presets" }),
      h("div", { className: "presets" }, presetBtns),
      slider("eta0", "offset $\\eta(0) = \\theta(0) - \\bar\\theta$", " rad"),
      slider("nu0", "angular velocity $\\nu(0) = \\omega(0)$", " rad/s"),
      slider("q", "$q = g/L$ (lecture: $1$)", " s⁻²"),
      slider("d", "damping $d$ (lecture: $0.1$; book: $0$)", " s⁻¹"),
      slider("t", "time $t$", " s"),
      h("div", { className: "card-actions" }, [playBtn]),
      h("fieldset", { className: "lz-ext" }, [
        h("legend", { text: "Book-supported extension: input and output" }),
        slider("du", "constant input $\\delta u$ in $\\dot\\omega = \\dots + u$", " rad/s²"),
        ctx.mathText(h("p", { className: "small-note" }), "The lecture linearizes the unforced pendulum. Book Eqs. 8.8–8.10 add $B = \\partial f/\\partial u = (0, 1)$ and, for the angle output $y = \\theta$, $C = [1\\ 0]$, $D = 0$. Keep $\\delta u = 0$ for the lecture model.")
      ])
    ]);

    // ---- readouts
    var modelBox = h("div", { className: "readout", id: "ex-model" });
    var matBox = h("div", { className: "readout", id: "ex-mats" });
    var nowBox = h("div", { className: "readout", id: "ex-now" });
    var vLin = h("p", { className: "plot-note", id: "ex-linear" });
    var vSys = h("p", { className: "plot-note verdict", id: "ex-verdict" });
    var inputNote = h("p", { className: "plot-note", id: "ex-input-note" });
    var presetNote = h("p", { className: "plot-note", id: "ex-preset-note" });

    // ---- SVG helpers
    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function plotSvg(id, W, H, label) {
      var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", id: id, "class": "lz-plot", "aria-label": label });
      var back = s("g"), layer = s("g"), front = s("g");
      svg.appendChild(back); svg.appendChild(layer); svg.appendChild(front);
      return { svg: svg, back: back, layer: layer, front: front, W: W, H: H };
    }
    // Clip segment (x0,y0)-(x1,y1) to the box (Liang-Barsky) so off-scale values never become huge SVG coordinates.
    function clipSeg(x0, y0, x1, y1, bx0, bx1, by0, by1) {
      var t0 = 0, t1 = 1, dx = x1 - x0, dy = y1 - y0, P = [-dx, dx, -dy, dy], Q = [x0 - bx0, bx1 - x0, y0 - by0, by1 - y0];
      for (var i = 0; i < 4; i++) {
        if (P[i] === 0) { if (Q[i] < 0) return null; continue; }
        var r = Q[i] / P[i];
        if (P[i] < 0) { if (r > t1) return null; if (r > t0) t0 = r; } else { if (r < t0) return null; if (r < t1) t1 = r; }
      }
      return [x0 + t0 * dx, y0 + t0 * dy, x0 + t1 * dx, y0 + t1 * dy, t0 > 0, t1 < 1];
    }
    // pts: [[x, y], ...] in data units; box in data units; map: data -> pixels.
    function clippedLine(g, pts, box, map, cls) {
      var cur = [];
      function flush() { if (cur.length > 1) g.appendChild(s("polyline", { points: cur.join(" "), "class": cls })); cur = []; }
      function add(x, y) { var p = map(x, y); cur.push(p[0].toFixed(1) + "," + p[1].toFixed(1)); }
      for (var i = 1; i < pts.length; i++) {
        var c = clipSeg(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], box[0], box[1], box[2], box[3]);
        if (!c) { flush(); continue; }
        if (c[4] || !cur.length) { flush(); add(c[0], c[1]); }
        add(c[2], c[3]);
        if (c[5]) flush();
      }
      flush();
    }

    // pendulums
    var pend = plotSvg("ex-pend", 480, 230, "");
    var pendBox = h("div", { className: "plot-box" }, [h("h3", { text: "Pendulums at the same time t (absolute angle θ = θ̄ + η)" }), pend.svg]);
    // time plot
    var TW = 480, TH = 250, TL = 46, TR = 12, TT = 12, TB = 30;
    var tp = plotSvg("ex-tplot", TW, TH, "");
    var tNote = h("p", { className: "plot-note", id: "ex-tnote" });
    var tBox = h("div", { className: "plot-box" }, [h("h3", { text: "Angle perturbation η(t) = θ(t) − θ̄" }), tp.svg, tNote]);
    // phase plot
    var PW = 480, PH = 300, PL = 46, PR = 12, PT = 12, PB = 30;
    var pp = plotSvg("ex-phase", PW, PH, "");
    var pNote = h("p", { className: "plot-note", id: "ex-pnote" });
    var pBox = h("div", { className: "plot-box" }, [h("h3", { text: "Phase plane (η, ν) about the fixed point" }), pp.svg, pNote]);
    var legend = h("div", { className: "legend" }, [
      h("span", null, [h("span", { className: "sw lz-nl" }), "original nonlinear"]),
      h("span", null, [h("span", { className: "sw lz-lin" }), "local linear model"])
    ]);

    var limits = config.limits || "Scope: the planar damped pendulum θ̇ = ω, ω̇ = −q sin θ − dω + u about the zero-input references θ̄ = 0 or π, with ω̄ = ū = 0; u is the book's normalized input. The linear model's accuracy depends on the start, q and the time horizon; no single offset is a universal cutoff. Curves are numerical solutions (RK4 with step ≤ " + SM.H_MAX + " for the nonlinear model, closed form for the linear model). A finite window cannot prove stability.";
    var right = h("div", null, [
      modelBox, matBox, nowBox, vLin, vSys, inputNote,
      pendBox, legend, h("div", { className: "plots lz-plots" }, [tBox, pBox]), presetNote,
      h("p", { className: "caveat", id: "ex-limits", text: limits })
    ]);
    root.appendChild(h("section", { className: "explorer lz-explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls, right])])
    ]));

    // ---- cached trajectories (recomputed only when parameters other than t change)
    var cache = { key: "", nl: null, lin: null };
    function trajectories() {
      var key = [st.eq, st.eta0, st.nu0, st.q, st.du, st.d].join("|");
      if (cache.key !== key) {
        var p = { eq: st.eq, eta0: st.eta0, nu0: st.nu0, q: st.q, du: st.du, d: st.d };
        cache = { key: key, nl: SM.nonlinearTrajectory(p, T_MAX, N_PTS), lin: SM.linearTrajectory(p, T_MAX, N_PTS) };
      }
      return cache;
    }

    function drawPendulums(nl, lin, tb) {
      clear(pend.back); clear(pend.layer); clear(pend.front);
      var R = 78;
      [[120, nl, "Original nonlinear", "lz-nl"], [360, lin, "Local linear", "lz-lin"]].forEach(function (c) {
        var cx = c[0], cy = 112, th = c[1].theta;
        pend.back.appendChild(s("circle", { cx: cx, cy: cy, r: R, "class": "lz-orbit" }));
        // reference ray at the fixed point theta_bar
        pend.back.appendChild(s("line", { x1: cx, y1: cy, x2: cx + R * Math.sin(tb), y2: cy + R * Math.cos(tb), "class": "lz-ref" }));
        var bx = cx + R * Math.sin(th), by = cy + R * Math.cos(th);
        pend.layer.appendChild(s("line", { x1: cx, y1: cy, x2: bx, y2: by, "class": "lz-rod " + c[3] }));
        pend.layer.appendChild(s("circle", { cx: bx, cy: by, r: 10, "class": "lz-bob " + c[3] }));
        pend.front.appendChild(s("circle", { cx: cx, cy: cy, r: 3.5, "class": "lz-pivot" }));
        pend.front.appendChild(s("text", { x: cx, y: 16, "text-anchor": "middle", "class": "ax-label", text: c[2] }));
        pend.front.appendChild(s("text", { x: cx, y: 222, "text-anchor": "middle", text: "θ = " + fmt(th) + " rad" }));
      });
      pend.svg.setAttribute("aria-label", "At t = " + fmt(st.t) + " s the nonlinear pendulum is at θ = " + fmt(nl.theta) +
        " rad and the linear model at θ = " + fmt(lin.theta) + " rad. Dashed ray: the fixed point θ̄. Drawings show the angle within one turn; the readout values are not wrapped.");
    }

    function axes(P, x0, x1, y0, y1, L, R, T, B, xTicks, yTicks, xLab, yLab) {
      var W = P.W, H = P.H;
      function map(x, y) { return [L + (x - x0) / (x1 - x0) * (W - L - R), T + (y1 - y) / (y1 - y0) * (H - T - B)]; }
      xTicks.forEach(function (x) {
        var p = map(x, y0);
        P.back.appendChild(s("line", { x1: p[0], y1: T, x2: p[0], y2: H - B, "class": x === 0 ? "p-axis" : "p-grid" }));
        P.back.appendChild(s("text", { x: p[0], y: H - B + 16, "text-anchor": "middle", text: fmt(x).replace("-", "−") }));
      });
      yTicks.forEach(function (y) {
        var p = map(x0, y);
        P.back.appendChild(s("line", { x1: L, y1: p[1], x2: W - R, y2: p[1], "class": y === 0 ? "p-axis" : "p-grid" }));
        P.back.appendChild(s("text", { x: L - 5, y: p[1] + 4, "text-anchor": "end", text: fmt(y) }));
      });
      P.back.appendChild(s("text", { x: W - R - 2, y: H - B - 5, "text-anchor": "end", "class": "ax-label", text: xLab }));
      P.back.appendChild(s("text", { x: L + 4, y: T + 13, "class": "ax-label", text: yLab }));
      return map;
    }
    function peak(tr, key) { var m = 0; tr.forEach(function (p) { m = Math.max(m, Math.abs(p[key])); }); return m; }
    // Scale to the nonlinear curve (bounded) and the linear curve where it stays modest; say when one leaves.
    function scaleFor(tr, key, minScale) {
      return niceUp(Math.max(minScale, peak(tr.nl, key), Math.min(peak(tr.lin, key), NICE[NICE.length - 1])));
    }
    function leaveTime(tr, key, Y) {
      for (var i = 0; i < tr.length; i++) if (Math.abs(tr[i][key]) > Y * 1.0001) return tr[i].t;
      return null;
    }

    function drawTime(tr, nowNl, nowLin) {
      clear(tp.back); clear(tp.layer); clear(tp.front);
      var Y = scaleFor(tr, "eta", 0.1);
      var map = axes(tp, 0, T_MAX, -Y, Y, TL, TR, TT, TB, [0, 2, 4, 6, 8, 10, 12], [-Y, -Y / 2, 0, Y / 2, Y], "t (s)", "η (rad)");
      var box = [0, T_MAX, -Y * 1.02, Y * 1.02];
      clippedLine(tp.layer, tr.nl.map(function (p) { return [p.t, p.eta]; }), box, map, "lz-nl-line");
      clippedLine(tp.layer, tr.lin.map(function (p) { return [p.t, p.eta]; }), box, map, "lz-lin-line");
      var c0 = map(st.t, Y), c1 = map(st.t, -Y);
      tp.front.appendChild(s("line", { x1: c0[0], y1: c0[1], x2: c1[0], y2: c1[1], "class": "p-cursor" }));
      [[nowNl, "lz-nl"], [nowLin, "lz-lin"]].forEach(function (c) {
        if (Math.abs(c[0].eta) <= Y) { var p = map(st.t, c[0].eta); tp.front.appendChild(s("circle", { cx: p[0], cy: p[1], r: 4, "class": "lz-dot " + c[1] })); }
      });
      var msgs = [], out = leaveTime(tr.lin, "eta", Y);
      if (out !== null) msgs.push("The linear curve leaves the plotted range ±" + fmt(Y) + " rad at t ≈ " + fmt(out, 1) + " s and reaches |η| ≈ " + fmt(Math.abs(tr.lin[tr.lin.length - 1].eta)) + " rad by t = " + T_MAX + " s.");
      var errMax = 0, amp = Math.max(peak(tr.nl, "eta"), 1e-300);
      for (var i = 0; i < tr.nl.length; i++) errMax = Math.max(errMax, Math.abs(tr.nl[i].theta - tr.lin[i].theta));
      if (amp > 1e-12 || errMax > 0) {
        var ratio = amp > 1e-12 ? errMax / amp : Infinity;
        msgs.push("Over this window the largest angle error is " + fmt(errMax) + " rad" +
          (ratio <= 1 ? " (" + fmt(100 * ratio, 1) + "% of the largest nonlinear |η|)." : ", larger than the largest nonlinear |η| itself."));
      }
      msgs.push("A finite window illustrates the behaviour; it does not by itself prove stability.");
      tNote.textContent = msgs.join(" ");
      tNote.className = "plot-note" + (out !== null ? " warn" : "");
      tp.svg.setAttribute("aria-label", "η(t) for 0 ≤ t ≤ " + T_MAX + " s, vertical scale ±" + fmt(Y) + " rad. At t = " + fmt(st.t) + " s: nonlinear η = " + fmt(nowNl.eta) + ", linear η = " + fmt(nowLin.eta) + ".");
    }

    function drawPhase(tr, nowNl, nowLin) {
      clear(pp.back); clear(pp.layer); clear(pp.front);
      var X = scaleFor(tr, "eta", 0.1), V = scaleFor(tr, "nu", 0.1);
      var map = axes(pp, -X, X, -V, V, PL, PR, PT, PB, [-X, -X / 2, 0, X / 2, X], [-V, -V / 2, 0, V / 2, V], "η (rad)", "ν (rad/s)");
      var box = [-X * 1.02, X * 1.02, -V * 1.02, V * 1.02];
      function pts(a, upTo) { var o = []; for (var i = 0; i < a.length && a[i].t <= upTo + 1e-9; i++) o.push([a[i].eta, a[i].nu]); return o; }
      clippedLine(pp.layer, pts(tr.nl, T_MAX), box, map, "lz-nl-line lz-faint");
      clippedLine(pp.layer, pts(tr.lin, T_MAX), box, map, "lz-lin-line lz-faint");
      var hidden = [];
      [[nowNl, "lz-nl", "nonlinear"], [nowLin, "lz-lin", "linear"]].forEach(function (c) {
        if (Math.abs(c[0].eta) <= X && Math.abs(c[0].nu) <= V) { var p = map(c[0].eta, c[0].nu); pp.front.appendChild(s("circle", { cx: p[0], cy: p[1], r: 5, "class": "lz-dot " + c[1] })); }
        else hidden.push(c[2]);
      });
      var o = map(0, 0);
      pp.front.appendChild(s("path", { d: "M" + (o[0] - 5) + " " + (o[1] - 5) + "L" + (o[0] + 5) + " " + (o[1] + 5) + "M" + (o[0] + 5) + " " + (o[1] - 5) + "L" + (o[0] - 5) + " " + (o[1] + 5), "class": "pole" }));
      pNote.textContent = "× marks the fixed point (η, ν) = (0, 0)." + (hidden.length ? " The current " + hidden.join(" and ") + " state is outside the plotted range." : "");
      pNote.className = "plot-note" + (hidden.length ? " warn" : "");
      pp.svg.setAttribute("aria-label", "Phase plane, η within ±" + fmt(X) + " rad and ν within ±" + fmt(V) + " rad/s, both trajectories for 0 ≤ t ≤ " + T_MAX + " s.");
    }

    function update() {
      KEYS.forEach(function (k) { inputs[k].value = st[k]; outputs[k].node.textContent = fmt(st[k]) + outputs[k].unit; });
      eqBtns.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-eq") === st.eq ? "true" : "false"); });

      var L = SM.linearization(st.eq, st.q, st.d), cls = SM.classify(st.eq, st.q, st.d), tb = L.thetaBar;
      var p = { eq: st.eq, eta0: st.eta0, nu0: st.nu0, q: st.q, du: st.du, d: st.d };
      var cmp = SM.compare(p, st.t), tr = trajectories();
      var damp = st.d > 0 ? " - " + tex(st.d) + "\\,\\omega" : "", dampL = st.d > 0 ? " - " + tex(st.d) + "\\,\\nu" : "";
      var c = st.eq === "down" ? "1" : "-1", forced = st.du !== 0;

      modelBox.textContent = "";
      modelBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "\\text{original: }\\dot\\theta = \\omega,\\ \\dot\\omega = -" + tex(st.q) + "\\sin\\theta" + damp + (forced ? " + u" : "")));
      modelBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "\\text{local at }\\bar\\theta = " + BAR[st.eq] + "\\ (\\cos\\bar\\theta = " + c + "):\\ \\dot\\eta = \\nu,\\ \\dot\\nu \\approx " +
        tex(-L.k) + "\\,\\eta" + dampL + (forced ? " + \\delta u\\quad(\\text{input extension})" : "")));
      matBox.textContent = "";
      matBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "A = \\left.\\tfrac{\\partial f}{\\partial x}\\right|_{\\bar x,\\bar u} = " + texMat(L.A) +
        ",\\quad \\lambda(A) = " + texEig(cls.eig) + ",\\quad f(\\bar x, \\bar u) = 0 \\text{ at } (\\bar\\theta, \\bar\\omega, \\bar u) = (" + BAR[st.eq] + ", 0, 0)"));
      matBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq lz-ext-eq" }),
        "\\text{book extension: } B = " + texMat(L.B) + ",\\ C = " + texMat(L.C) + ",\\ D = 0\\quad(\\delta y = \\eta)"));
      nowBox.textContent = "";
      var tbTex = BAR[st.eq];
      nowBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "t = " + tex(st.t, 2) + ":\\ \\theta_{\\text{NL}} = " + tbTex + " + " + "(" + tex(cmp.nonlinear.eta) + ") = " + tex(cmp.nonlinear.theta) +
        ",\\ \\theta_{\\text{lin}} = " + tbTex + " + (" + tex(cmp.linear.eta) + ") = " + tex(cmp.linear.theta)));
      nowBox.appendChild(ctx.flowMath(h("div", { className: "ro-eq" }),
        "\\text{angle error } \\theta_{\\text{NL}} - \\theta_{\\text{lin}} = " + tex(cmp.angleError) + "\\ \\text{rad}\\quad(\\text{not wrapped mod } 2\\pi)"));

      vLin.textContent = LINEAR_TEXT[cls.linear];
      vSys.textContent = NONLINEAR_TEXT[cls.nonlinear];
      vSys.setAttribute("data-kind", DATA_KIND[cls.nonlinear]);
      inputNote.textContent = st.du !== 0
        ? "Input extension active (δu ≠ 0): the zero-input reference is no longer a fixed point of the driven pendulum (ω̇ = δu there). The curves are an input-response comparison of the two models, not a proof of stability of that reference under drive; the verdict above is about the zero-input reference. In the book's normalized equation u acts as an angular acceleration (its figure calls it a torque)."
        : "";

      drawPendulums(cmp.nonlinear, cmp.linear, tb);
      drawTime(tr, cmp.nonlinear, cmp.linear);
      drawPhase(tr, cmp.nonlinear, cmp.linear);

      var match = SM.PRESETS.filter(function (pr) {
        return pr.eq === st.eq && KEYS.every(function (k) { return k === "t" || Math.abs(pr[k] - st[k]) < 1e-6; });
      })[0];
      presetBtns.forEach(function (b) { b.setAttribute("aria-pressed", match && b.getAttribute("data-preset") === match.id ? "true" : "false"); });
      presetNote.textContent = "";
      if (match) ctx.mathText(presetNote, match.note);
    }

    function stopPlay() { stop(); playBtn.textContent = "▶ Play t"; playBtn.setAttribute("aria-pressed", "false"); }
    // Model time advances by elapsed wall-clock seconds times the rate, independent of the frame rate.
    function startPlay() {
      var speed = (window.__studyExplorerSpeed || 1) * (config.playRate || 1), last = null;
      if (st.t >= T_MAX - 1e-9) st.t = 0;
      playBtn.textContent = "❚❚ Pause"; playBtn.setAttribute("aria-pressed", "true");
      function frame(ts) {
        if (last !== null) st.t = Math.min(T_MAX, st.t + Math.max(0, ts - last) / 1000 * speed);
        last = ts;
        update();
        if (st.t >= T_MAX) { stopPlay(); ctx.save(); return; }
        timer = requestAnimationFrame(frame);
      }
      timer = requestAnimationFrame(frame);
    }

    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
