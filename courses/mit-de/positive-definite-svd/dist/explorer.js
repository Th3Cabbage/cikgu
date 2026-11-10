/*
 * Positive definite matrices and the SVD explorer.
 * Mode "pd": the five tests for S = [s11 s12; s12 s22] and a filled contour plot of x^T S x on [-2, 2]^2.
 * Mode "svd": A = U Sigma V^T as rotate, stretch, rotate on the unit circle, plus rank-one pieces.
 * Maths comes from window.StudyMath (symEig, tests, energy, svd, rankOne).
 * Saved state: state.explorer = {mode, s11, s12, s22, a, b, c, d}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["s11", "s12", "s22", "a", "b", "c", "d"];
  var PI = Math.PI;
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

  function clean(v, dp) {
    var r = +v.toFixed(dp);
    return Math.abs(r) < Math.pow(10, -dp) / 2 ? 0 : r;
  }
  function num(v) { return String(clean(v, 3)).replace("-", "−"); }
  function tnum(v) { return String(clean(v, 3)); }
  function f2(v) { return clean(v, 2).toFixed(2).replace("-", "−"); }
  function f3(v) { return String(clean(v, 3)); }
  function bmat(M, f) {
    f = f || tnum;
    return "\\begin{bmatrix} " + f(M[0][0]) + " & " + f(M[0][1]) + " \\\\ " + f(M[1][0]) + " & " + f(M[1][1]) + " \\end{bmatrix}";
  }
  function par(v) { return v < 0 ? "(" + tnum(v) + ")" : tnum(v); }
  function lerp(a, b, t) { return Math.round(a + (b - a) * t); }
  var uid = 0;

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var clipId = "pd-clip-" + (++uid);

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Positive definite tests and the SVD" }),
      ctx.mathText(h("p", { className: "lede" }), "Choose a symmetric $S$ to run the five tests and see the energy $x^T S x$ as a surface seen from above, or choose any $A$ and watch $A = U \\Sigma V^T$ turn the unit circle into an ellipse.")
    ]));

    var inputs = {}, outputs = {}, rows = {};
    function slider(key, text, label) {
      var c = config[key], id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      inp.setAttribute("aria-label", label);
      var out = h("output", { "for": id, text: num(st[key]) });
      inp.addEventListener("input", function () {
        st[key] = snap(parseFloat(inp.value), c); ctx.save(); update();
        ctx.announce(label + " " + num(st[key]));
      });
      inputs[key] = inp; outputs[key] = out;
      var row = h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
      rows[key] = row;
      return row;
    }

    var radios = {};
    var modeBox = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "Mode", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    config.modes.forEach(function (m) {
      var id = "ex-mode-" + m.id;
      var r = h("input", { type: "radio", name: "ex-mode", id: id, value: m.id });
      r.checked = st.mode === m.id;
      r.addEventListener("change", function () {
        if (r.checked) { st.mode = m.id; update(); ctx.save(); ctx.announce("Mode: " + m.label); }
      });
      radios[m.id] = r;
      modeBox.appendChild(h("label", { className: "check-row", "for": id, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
    });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (p.mode && radios[p.mode]) { st.mode = p.mode; radios[p.mode].checked = true; }
        KEYS.forEach(function (k) { if (typeof p[k] === "number") { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; } });
        ctx.mathText(presetNote, p.note || "");
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var matBox = h("div", { className: "readout" });
    var controls = h("div", null, [
      h("h2", { text: "Matrix" }),
      slider("s11", "Entry $s_{11}$", "Symmetric matrix entry s11"),
      slider("s12", "Entry $s_{12} = s_{21}$", "Symmetric matrix entry s12"),
      slider("s22", "Entry $s_{22}$", "Symmetric matrix entry s22"),
      slider("a", "Entry $a$", "Matrix entry a"), slider("b", "Entry $b$", "Matrix entry b"),
      slider("c", "Entry $c$", "Matrix entry c"), slider("d", "Entry $d$", "Matrix entry d"),
      matBox, modeBox, presets
    ]);

    function sw(color) { return h("span", { className: "sw", style: "background:" + color }); }
    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function setShown(el, on) { el.hidden = !on; el.style.display = on ? "" : "none"; }

    // ================= PD mode: plot =================
    var L = 30, Rr = 10, Tp = 10, Bt = 26, PS = 320, W1 = L + PS + Rr, H1 = Tp + PS + Bt, RNG = 2, N = 36;
    var svg = s("svg", { viewBox: "0 0 " + W1 + " " + H1, role: "img",
      "aria-label": "Filled contour plot of the energy x transpose S x over the square from minus 2 to 2, with eigenvector axes.",
      style: "width:100%;height:auto" });
    var defs = s("defs"), clip = s("clipPath", { id: clipId });
    clip.appendChild(s("rect", { x: L, y: Tp, width: PS, height: PS }));
    defs.appendChild(clip); svg.appendChild(defs);
    function X(x) { return L + PS * (x + RNG) / (2 * RNG); }
    function Y(y) { return Tp + PS * (RNG - y) / (2 * RNG); }
    var cells = s("g"), overlay = s("g", { "clip-path": "url(#" + clipId + ")" }), frame = s("g");
    svg.appendChild(cells); svg.appendChild(overlay); svg.appendChild(frame);
    var cellEls = [], i, j, cw = PS / N;
    for (j = 0; j < N; j++) for (i = 0; i < N; i++) {
      var rc = s("rect", { x: (L + i * cw).toFixed(2), y: (Tp + j * cw).toFixed(2), width: (cw + 0.4).toFixed(2), height: (cw + 0.4).toFixed(2), fill: "#fff" });
      cells.appendChild(rc); cellEls.push(rc);
    }
    frame.appendChild(s("rect", { x: L, y: Tp, width: PS, height: PS, fill: "none", style: "stroke:var(--muted);stroke-width:1" }));
    [-2, -1, 0, 1, 2].forEach(function (v) {
      frame.appendChild(s("text", { x: X(v), y: Tp + PS + 14, "text-anchor": "middle", text: String(v) }));
      frame.appendChild(s("text", { x: L - 4, y: Y(v) + 4, "text-anchor": "end", text: String(v) }));
    });
    frame.appendChild(s("text", { x: L + PS, y: Tp + PS + 24, "text-anchor": "end", text: "x₁" }));
    frame.appendChild(s("text", { x: L + 4, y: Tp + 12, text: "x₂" }));

    var legend = h("div", { className: "legend" });
    var cap = h("p", { className: "plot-note" });
    var badge = h("span", { style: "display:inline-block;padding:3px 12px;border-radius:999px;font-weight:700;color:#fff" });
    var badgeRow = h("p", { style: "margin:6px 0" }, [h("span", { text: "Overall: ", style: "font-weight:600" }), badge]);
    var plotBox = h("div", { className: "plot-box" }, [h("h3", { text: "Energy xᵀ S x" }), svg, legend, cap]);
    var testsBox = h("div", { className: "readout" });
    var pdPane = h("div", null, [badgeRow, plotBox, testsBox]);

    // ================= SVD mode: panes =================
    var NP = 120, PW = 160, PH = 186;
    var paneBox = h("div", { style: "display:flex;flex-wrap:wrap;gap:8px" });
    var panes = [], titles = ["Unit circle", "After Vᵀ (rotate)", "After Σ (stretch)", "After U (rotate)"];
    var k;
    for (k = 0; k < 4; k++) {
      var sv = s("svg", { viewBox: "0 0 " + PW + " " + PH, role: "img", "aria-label": titles[k] + ": the unit circle, the vectors v1 and v2, and dots, at this stage.",
        style: "width:100%;height:auto" });
      var g = s("g");
      sv.appendChild(g);
      sv.appendChild(s("text", { x: PW / 2, y: PH - 8, "text-anchor": "middle", text: titles[k], style: "font-weight:600" }));
      paneBox.appendChild(h("div", { style: "flex:1 1 140px;min-width:130px;max-width:230px" }, [sv]));
      panes.push(g);
    }
    var svdLegend = h("div", { className: "legend" });
    var svdCap = h("p", { className: "plot-note" });
    var svdPlot = h("div", { className: "plot-box" }, [h("h3", { text: "Rotate, stretch, rotate" }), paneBox, svdLegend, svdCap]);
    var svdRead = h("div", { className: "readout" });
    var rankBox = h("div", { className: "readout" });
    var svdPane = h("div", null, [svdPlot, svdRead, rankBox]);

    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [pdPane, svdPane, presetNote])])])
    ]));

    // ---- PD drawing ----
    function color(v, m) {
      var t = m > 0 ? Math.max(-1, Math.min(1, v / m)) : 0, a = Math.pow(Math.abs(t), 0.65);
      return t >= 0 ? "rgb(" + lerp(255, 234, a) + "," + lerp(255, 110, a) + "," + lerp(255, 40, a) + ")"
        : "rgb(" + lerp(255, 37, a) + "," + lerp(255, 99, a) + "," + lerp(255, 235, a) + ")";
    }
    function zeroDirs(S, T, tol) {
      // directions (angles in [0, pi)) along which x^T S x = 0
      var out = [], n = 720, prev = null, t, e;
      if (T.kind === "positive semidefinite" || T.kind === "negative semidefinite") {
        e = Math.abs(T.eig.l2) <= tol ? T.eig.v2 : T.eig.v1;
        return [Math.atan2(e[1], e[0])];
      }
      if (T.kind !== "indefinite") return out;
      function f(a) { return SM.energy(S, [Math.cos(a), Math.sin(a)]); }
      for (t = 0; t <= n; t++) {
        var a1 = PI * t / n, v = f(a1);
        if (prev && prev.v * v < 0) {
          var lo = prev.a, hi = a1, flo = prev.v, it;
          for (it = 0; it < 40; it++) {
            var mid = (lo + hi) / 2, fm = f(mid);
            if (fm * flo <= 0) hi = mid; else { lo = mid; flo = fm; }
          }
          out.push((lo + hi) / 2);
        }
        prev = { a: a1, v: v };
      }
      return out;
    }
    function dirLine(ang, style) {
      var R = 6, c = Math.cos(ang), sn = Math.sin(ang);
      return s("line", { x1: X(-R * c), y1: Y(-R * sn), x2: X(R * c), y2: Y(R * sn), style: style });
    }
    function drawPD() {
      var S = [[st.s11, st.s12], [st.s12, st.s22]], T = SM.tests(st.s11, st.s12, st.s22), e = T.eig;
      var sc = Math.max(Math.abs(st.s11), Math.abs(st.s12), Math.abs(st.s22), 1), tol = 1e-9 * sc;
      var vals = [], mx = 0, ii, jj;
      for (jj = 0; jj < N; jj++) for (ii = 0; ii < N; ii++) {
        var v = SM.energy(S, [-RNG + (ii + 0.5) * 2 * RNG / N, RNG - (jj + 0.5) * 2 * RNG / N]);
        vals.push(v); mx = Math.max(mx, Math.abs(v));
      }
      vals.forEach(function (v, n) { cellEls[n].setAttribute("fill", color(v, mx)); });
      clear(overlay);
      var zs = zeroDirs(S, T, tol), hasZero = zs.length > 0;
      zs.forEach(function (a) { overlay.appendChild(dirLine(a, "stroke:#111;stroke-width:3.2;stroke-linecap:round")); });
      [["v1", e.v1, e.l1], ["v2", e.v2, e.l2]].forEach(function (q, n) {
        overlay.appendChild(dirLine(Math.atan2(q[1][1], q[1][0]), "stroke:var(--teal);stroke-width:1.8;stroke-dasharray:6 4"));
        var r = 1.8;
        overlay.appendChild(s("text", { x: X(r * q[1][0]) + (q[1][0] < 0 ? -4 : 4), y: Y(r * q[1][1]) + 4, "text-anchor": q[1][0] < 0 ? "end" : "start",
          style: "fill:var(--teal);font-weight:700;paint-order:stroke;stroke:#fff;stroke-width:3px",
          text: "λ" + (n === 0 ? "₁" : "₂") + " = " + f2(q[2]) }));
      });
      clear(legend);
      legend.appendChild(h("span", null, [sw("rgb(234,110,40)"), "positive energy"]));
      legend.appendChild(h("span", null, [sw("rgb(37,99,235)"), "negative energy"]));
      legend.appendChild(h("span", null, [sw("var(--teal)"), "eigenvector axes"]));
      if (hasZero) legend.appendChild(h("span", null, [sw("#111"), "zero level"]));
      var shape = { "positive definite": "bowl", "positive semidefinite": "trough", "indefinite": "saddle",
        "negative definite": "upside-down bowl", "negative semidefinite": "upside-down trough" }[T.kind] || "flat (S = 0)";
      cap.textContent = "Shape of the energy: " + shape + ". Region [−2, 2]²; colours scale with the largest energy shown (" + f2(mx) + ").";

      var pd = T.kind === "positive definite", semi = T.kind === "positive semidefinite";
      badge.textContent = T.kind;
      badge.style.background = pd ? "#15803d" : semi ? "#b45309" : "#b91c1c";

      // tests table
      clear(testsBox);
      testsBox.appendChild(h("h3", { text: "Five tests for positive definiteness" }));
      var table = h("table", { className: "ro-table", style: "border-collapse:collapse;font-size:0.92rem;width:100%" });
      function mark(ok) {
        return h("span", { text: ok ? "✓" : "✗", "aria-label": ok ? "passes" : "fails",
          style: "font-weight:700;font-size:1.1rem;color:" + (ok ? "var(--green)" : "var(--red)") });
      }
      function row(name, detail, ok) {
        var td = h("td", { style: "padding:4px 8px 4px 0;vertical-align:top" });
        ctx.mathText(td, detail);
        table.appendChild(h("tr", { style: "border-top:1px solid rgba(128,128,128,0.25)" }, [
          h("td", { text: name, style: "padding:4px 8px 4px 0;vertical-align:top;font-weight:600" }), td,
          h("td", { style: "padding:4px 0;vertical-align:top;text-align:center" }, [mark(ok)])]));
      }
      var pos = function (x) { return x > tol; };
      row("1. Eigenvalues", "$\\lambda_1 = " + f2(e.l1) + ",\\ \\lambda_2 = " + f2(e.l2) + "$ (all must be $> 0$)", pos(e.l2));
      row("2. Pivots", T.pivots ? "$" + f2(T.pivots[0]) + ",\\ " + f2(T.pivots[1]) + "$ (all must be $> 0$)" :
        "$s_{11} = 0$: no first pivot", !!T.pivots && pos(T.pivots[0]) && pos(T.pivots[1]));
      row("3. Upper-left determinants", "$" + f2(T.dets[0]) + ",\\ " + f2(T.dets[1]) + "$ (all must be $> 0$)", pos(T.dets[0]) && pos(T.dets[1]));
      row("4. S = RᵀR", T.cholesky ? "$R = " + bmat(T.cholesky, f2) + "$ (independent columns)" :
        "no real factor with independent columns", !!T.cholesky);
      var en = "$x^T S x = " + tnum(st.s11) + "x_1^2 + 2(" + tnum(st.s12) + ")x_1x_2 + " + par(st.s22) + "x_2^2$";
      var enMore = pd ? "; positive for every $x \\ne 0$" :
        "; for $x = v_2$ it equals $\\lambda_2 = " + f2(e.l2) + "$, not positive";
      row("5. Energy", en + enMore, pd);
      testsBox.appendChild(table);
    }

    // ---- SVD drawing ----
    function matVec(M, p) { return [M[0][0] * p[0] + M[0][1] * p[1], M[1][0] * p[0] + M[1][1] * p[1]]; }
    function T2(M) { return [[M[0][0], M[1][0]], [M[0][1], M[1][1]]]; }
    function drawSVD() {
      var A = [[st.a, st.b], [st.c, st.d]], F = SM.svd(A), Vt = T2(F.V);
      var Sg = [[F.sigma[0], 0], [0, F.sigma[1]]];
      var stages = [[[1, 0], [0, 1]], Vt, null, null];
      stages[2] = [[Sg[0][0] * Vt[0][0], Sg[0][0] * Vt[0][1]], [Sg[1][1] * Vt[1][0], Sg[1][1] * Vt[1][1]]];
      stages[3] = [[0, 0], [0, 0]];
      var a2, b2;
      for (a2 = 0; a2 < 2; a2++) for (b2 = 0; b2 < 2; b2++)
        stages[3][a2][b2] = F.U[a2][0] * stages[2][0][b2] + F.U[a2][1] * stages[2][1][b2];
      var R = Math.max(1.2, F.sigma[0] * 1.15), Sz = PW - 20;
      var px = function (p) { return 10 + Sz * (p[0] + R) / (2 * R); }, py = function (p) { return 10 + Sz * (R - p[1]) / (2 * R); };
      var v1 = [F.V[0][0], F.V[1][0]], v2 = [F.V[0][1], F.V[1][1]];
      panes.forEach(function (g, n) {
        clear(g);
        var M = stages[n];
        g.appendChild(s("rect", { x: 10, y: 10, width: Sz, height: Sz, fill: "none", style: "stroke:var(--muted);stroke-width:0.8;opacity:0.6" }));
        g.appendChild(s("line", { x1: 10, y1: py([0, 0]), x2: 10 + Sz, y2: py([0, 0]), style: "stroke:var(--muted);stroke-width:0.6;opacity:0.5" }));
        g.appendChild(s("line", { x1: px([0, 0]), y1: 10, x2: px([0, 0]), y2: 10 + Sz, style: "stroke:var(--muted);stroke-width:0.6;opacity:0.5" }));
        var d = "", q, m;
        for (q = 0; q <= NP; q++) {
          var an = 2 * PI * q / NP, p = matVec(M, [Math.cos(an), Math.sin(an)]);
          d += (q ? "L" : "M") + px(p).toFixed(1) + " " + py(p).toFixed(1) + " ";
        }
        g.appendChild(s("path", { d: d + "Z", fill: "rgba(37,99,235,0.07)", style: "stroke:var(--blue);stroke-width:1.8" }));
        for (m = 0; m < 12; m++) {
          var am = 2 * PI * m / 12, pm = matVec(M, [Math.cos(am), Math.sin(am)]);
          g.appendChild(s("circle", { cx: px(pm), cy: py(pm), r: m === 0 ? 3.4 : 2, style: m === 0 ? "fill:var(--yellow);stroke:#333;stroke-width:0.8" : "fill:var(--muted);opacity:0.8" }));
        }
        [[v1, "var(--teal)", "v₁"], [v2, "var(--pink)", "v₂"]].forEach(function (vv) {
          var p = matVec(M, vv[0]);
          g.appendChild(s("line", { x1: px([0, 0]), y1: py([0, 0]), x2: px(p), y2: py(p), style: "stroke:" + vv[1] + ";stroke-width:2.6;stroke-linecap:round" }));
          g.appendChild(s("circle", { cx: px(p), cy: py(p), r: 3.6, style: "fill:" + vv[1] }));
        });
      });
      clear(svdLegend);
      svdLegend.appendChild(h("span", null, [sw("var(--teal)"), "v₁ and its image"]));
      svdLegend.appendChild(h("span", null, [sw("var(--pink)"), "v₂ and its image"]));
      svdLegend.appendChild(h("span", null, [sw("var(--yellow)"), "reference dot (angle 0)"]));
      svdCap.textContent = "Each pane maps 120 points of the circle through the partial products. Vᵀ turns v₁, v₂ onto the axes, Σ stretches by σ₁ = " +
        f3(F.sigma[0]) + " and σ₂ = " + f3(F.sigma[1]) + ", U turns the result into A(circle). Same scale in all panes (±" + f2(R) + ").";

      var rank = (F.sigma[0] > 1e-9 ? 1 : 0) + (F.sigma[1] > 1e-9 ? 1 : 0);
      clear(svdRead);
      svdRead.appendChild(h("p", { style: "margin:2px 0", text: "σ₁ = " + f3(F.sigma[0]) + ",  σ₂ = " + f3(F.sigma[1]) + ",  rank = " + rank }));
      svdRead.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
        "U = " + bmat(F.U, f3) + ",\\quad V = " + bmat(F.V, f3)));

      clear(rankBox);
      rankBox.appendChild(h("h3", { text: "Rank-one pieces" }));
      var P1 = SM.rankOne(F, 0), P2 = SM.rankOne(F, 1);
      rankBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
        "\\sigma_1 u_1 v_1^T = " + bmat(P1, f3) + ",\\quad \\sigma_2 u_2 v_2^T = " + bmat(P2, f3)));
      rankBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
        bmat(P1, f3) + " + " + bmat(P2, f3) + " = " + bmat([[P1[0][0] + P2[0][0], P1[0][1] + P2[0][1]], [P1[1][0] + P2[1][0], P1[1][1] + P2[1][1]]], f3) + " = A"));
    }

    function update() {
      var m = st.mode, isPD = m === "pd";
      KEYS.forEach(function (key) { outputs[key].textContent = num(st[key]); inputs[key].value = st[key]; });
      ["s11", "s12", "s22"].forEach(function (key) { setShown(rows[key], isPD); });
      ["a", "b", "c", "d"].forEach(function (key) { setShown(rows[key], !isPD); });
      setShown(pdPane, isPD); setShown(svdPane, !isPD);
      radios[m].checked = true;
      clear(matBox);
      if (isPD) {
        matBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }),
          "S = \\begin{bmatrix} " + tnum(st.s11) + " & " + tnum(st.s12) + " \\\\ " + tnum(st.s12) + " & " + tnum(st.s22) + " \\end{bmatrix}"));
        drawPD();
      } else {
        matBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), "A = " + bmat([[st.a, st.b], [st.c, st.d]])));
        drawSVD();
      }
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
