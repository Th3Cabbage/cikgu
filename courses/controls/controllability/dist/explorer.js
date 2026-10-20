/*
 * Controllability explorer: A = [[1, c], [0, 2]], one input column b = (b1, b2) or B = [e1, b].
 * Shows AB, C = [B, AB], singular values, numerical rank, the reachable set from x0 = 0 and the
 * coefficient point alpha*b + beta*Ab. Saved state: state.explorer = {c, b1, b2, alpha, beta, dual}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var KEYS = ["c", "b1", "b2", "alpha", "beta"];

  function snap(v, c) { return +(c.min + Math.round((v - c.min) / c.step) * c.step).toFixed(6); }
  function defaults(config) {
    var out = { dual: !!(config.dual && config.dual.default) };
    KEYS.forEach(function (k) { out[k] = config[k].default; });
    return out;
  }
  function restore(saved, config) {
    if (!saved || typeof saved !== "object" || !config || !config.c) return null;
    var out = {};
    for (var i = 0; i < KEYS.length; i++) {
      var k = KEYS[i], v = saved[k], c = config[k];
      if (typeof v !== "number" || !isFinite(v) || v < c.min - 1e-9 || v > c.max + 1e-9) return null;
      out[k] = snap(v, c);
    }
    if (typeof saved.dual !== "boolean") return null;
    out.dual = saved.dual;
    return out;
  }
  function stop() { /* no timers: every update is immediate */ }

  function num(v) {
    if (Math.abs(v) < 5e-10) return "0";
    var r = Math.abs(v) >= 100 ? v.toFixed(0) : Math.abs(v) >= 0.1 ? +v.toFixed(3) + "" : +v.toPrecision(3) + "";
    return String(r).replace("-", "−");
  }
  function tnum(v) { return num(v).replace("−", "-"); }
  function texMat(M) {
    return "\\begin{bmatrix}" + M.map(function (r) { return r.map(tnum).join(" & "); }).join("\\\\ ") + "\\end{bmatrix}";
  }

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer || defaults(config);
    ctx.state.explorer = st;
    var R = config.range, W = 360, PAD = 12;

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "Which directions can the input reach?" }),
      ctx.mathText(h("p", { className: "lede" }), "Choose the coupling $c$ in $A = \\begin{bmatrix}1&c\\\\0&2\\end{bmatrix}$ and the actuator direction $b$. The guide multiplies $Ab$, assembles $\\mathcal{C} = [B\\ \\ AB]$, and tests $\\operatorname{rank}\\mathcal{C} = 2$.")
    ]));

    var inputs = {}, outputs = {};
    function slider(key, text) {
      var c = config[key], id = "ex-" + key;
      var inp = h("input", { type: "range", id: id, min: c.min, max: c.max, step: c.step, value: st[key] });
      var out = h("output", { "for": id, text: num(st[key]) });
      inp.addEventListener("input", function () { st[key] = snap(parseFloat(inp.value), c); update(); ctx.save(); });
      inputs[key] = inp; outputs[key] = out;
      return h("div", { className: "slider-row" }, [ctx.mathText(h("label", { "for": id }), text), out, inp]);
    }
    var dualBox = h("input", { type: "checkbox", id: "ex-dual" });
    dualBox.checked = st.dual;
    dualBox.addEventListener("change", function () { st.dual = dualBox.checked; update(); ctx.save(); });

    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, config.presets.map(function (p) {
      return h("button", { type: "button", className: "btn", text: p.label, onclick: function () {
        KEYS.forEach(function (k) { st[k] = snap(p[k], config[k]); inputs[k].value = st[k]; });
        st.dual = !!p.dual; dualBox.checked = st.dual;
        ctx.mathText(presetNote, p.note);
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var controls = h("div", null, [
      h("h2", { text: "System" }), presets,
      slider("c", "Coupling $c$ (entry $a_{12}$)"), slider("b1", "$b_1$"), slider("b2", "$b_2$"),
      h("label", { className: "check-row", "for": "ex-dual" }, [dualBox, ctx.mathText(h("span"), "Second actuator on $x_1$: $B = [e_1\\ \\ b]$")]),
      h("h2", { text: "Coefficients" }),
      slider("alpha", "$\\alpha$ multiplies $b$"), slider("beta", "$\\beta$ multiplies $Ab$")
    ]);

    var matsBox = h("div", { className: "readout" }), verdict = h("p", { className: "verdict" });
    var svBox = h("div", { className: "readout" });
    var svg = s("svg", { viewBox: "0 0 " + W + " " + W, role: "img", "aria-label": "Columns b and Ab, reachable set and coefficient point" });
    var layer = s("g");
    function map(x, y) { var k = (W - 2 * PAD) / (2 * R); return [W / 2 + k * x, W / 2 - k * y]; }
    for (var g = -R; g <= R; g++) {
      var a = map(g, -R), b = map(g, R), c2 = map(-R, g), d = map(R, g);
      svg.appendChild(s("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1], "class": g ? "p-grid" : "p-axis" }));
      svg.appendChild(s("line", { x1: c2[0], y1: c2[1], x2: d[0], y2: d[1], "class": g ? "p-grid" : "p-axis" }));
    }
    var lx = map(R, 0), ly = map(0, R);
    svg.appendChild(s("text", { x: lx[0] - 18, y: lx[1] - 6, text: "x₁" }));
    svg.appendChild(s("text", { x: ly[0] + 6, y: ly[1] + 12, text: "x₂" }));
    svg.appendChild(layer);
    var plotNote = h("p", { className: "plot-note" });
    var legend = h("div", { className: "legend" }, [
      h("span", null, [h("span", { className: "sw", style: "background:var(--blue)" }), "b"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--orange)" }), "Ab"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--green);opacity:.5;height:8px" }), "reachable from 0 (col 𝒞)"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--red)" }), "unreachable direction w"]),
      h("span", null, [h("span", { className: "sw", style: "background:var(--teal)" }), "αb + βAb"])
    ]);
    var plotBox = h("div", { className: "plot-box" }, [h("h3", { text: "State plane" }), svg, legend, plotNote]);

    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [matsBox, verdict, svBox, plotBox, presetNote,
          ctx.mathText(h("p", { className: "caveat" }), "The point $\\alpha b + \\beta Ab$ is a bounded coefficient illustration. Read as a separate discrete-time companion $x_{k+1} = Ax_k + Bu_k$ with $x_0 = 0$, it is $x_2$ for $u_1 = \\alpha$, $u_0 = \\beta$ (not the sampled continuous system). Singular values of $\\mathcal{C}$ are not continuous-time control energies; that needs the controllability Gramian (later lecture). With two actuators the sliders move only the $b$, $Ab$ coefficients, while the rank uses all four columns. Rank counts $\\sigma_i > 10^{-9}\\,\\sigma_{\\max}$.")
        ])])])
    ]));

    function line(x1, y1, x2, y2, style, w) {
      var p = map(x1, y1), q = map(x2, y2);
      return s("line", { x1: p[0], y1: p[1], x2: q[0], y2: q[1], style: "stroke:" + style + ";stroke-width:" + (w || 2.4) + ";stroke-linecap:round" });
    }
    function vec(v, color, label) {
      var gg = s("g");
      var n = Math.hypot(v[0], v[1]);
      if (n < 1e-12) { var o = map(0, 0); gg.appendChild(s("circle", { cx: o[0], cy: o[1], r: 4, style: "fill:" + color })); return gg; }
      var sc = Math.min(1, (R - 0.2) / Math.max(Math.abs(v[0]), Math.abs(v[1]))), e = [v[0] * sc, v[1] * sc];
      gg.appendChild(line(0, 0, e[0], e[1], color, 3));
      var p = map(e[0], e[1]), ang = Math.atan2(-(e[1]), e[0]), L = 9;
      var pts = [p, [p[0] - L * Math.cos(ang - 0.4), p[1] - L * Math.sin(ang - 0.4)], [p[0] - L * Math.cos(ang + 0.4), p[1] - L * Math.sin(ang + 0.4)]];
      gg.appendChild(s("polygon", { points: pts.map(function (q) { return q.join(","); }).join(" "), style: "fill:" + color }));
      gg.appendChild(s("text", { x: p[0] + 6, y: p[1] - 6, text: label + (sc < 1 ? " (clipped)" : ""), style: "fill:" + color }));
      return gg;
    }

    function update() {
      KEYS.forEach(function (k) { outputs[k].textContent = num(st[k]); });
      var m = SM.explorerModel(st);
      var ABtex = st.dual ? "AB = " + texMat(m.AB) : "Ab = " + texMat([[1, st.c], [0, 2]]) + texMat([[st.b1], [st.b2]]) + " = " + texMat(m.Ab.map(function (v) { return [v]; }));
      matsBox.textContent = "";
      [["", "A = " + texMat(m.A) + ",\\quad B = " + texMat(m.B)], ["", ABtex],
       ["", "\\mathcal{C} = [B\\ \\ AB] = " + texMat(m.C) + (m.det === null ? "\\quad(2\\times4)" : ",\\quad \\det\\mathcal{C} = b_2(b_1 - c\\,b_2) = " + tnum(m.det))]
      ].forEach(function (r) { matsBox.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), r[1])); });

      var kind = m.rank === 2 ? "stable" : m.rank === 1 ? "marginal" : "unstable";
      verdict.setAttribute("data-kind", kind);
      verdict.textContent = m.rank === 2 ? "rank 2 = n: controllable" :
        m.rank === 1 ? "rank 1 < 2: uncontrollable (the eigenvalue " + (Math.abs(st.b2) < 1e-12 ? "2" : "1") + " mode cannot be moved)" :
        "rank 0: B = 0, the input does nothing";
      if (m.rank === 1 && st.dual) verdict.textContent = "rank 1 < 2: uncontrollable";
      svBox.textContent = "";
      var cond = isFinite(m.cond) ? num(m.cond) : "∞";
      ctx.mathText(svBox, "Singular values of $\\mathcal{C}$: $\\sigma_1 = " + tnum(m.sigma[0]) + "$, $\\sigma_2 = " + tnum(m.sigma[1]) +
        "$; $\\sigma_1/\\sigma_2 = " + cond.replace("−", "-").replace("∞", "\\infty") + "$." +
        (m.rank === 2 && m.sigma[1] < 0.1 * m.sigma[0] ? " Controllable, but one direction is weakly actuated." : "") +
        (m.rank === 1 && !st.dual ? " Here $b$ lies along an eigenvector of $A$, so $Ab$ is a multiple of $b$." : ""));

      while (layer.firstChild) layer.removeChild(layer.firstChild);
      var note = "";
      if (m.rank === 2) {
        var c0 = map(-R, -R), c1 = map(R, R);
        layer.appendChild(s("rect", { x: c0[0], y: c1[1], width: c1[0] - c0[0], height: c0[1] - c1[1], style: "fill:var(--green);opacity:0.10" }));
        note = "Reachable set from 0: the whole plane.";
      } else if (m.rank === 1) {
        var u = m.line, ww = m.w;
        layer.appendChild(line(-2 * R * u[0], -2 * R * u[1], 2 * R * u[0], 2 * R * u[1], "var(--green)", 7));
        layer.appendChild(line(0, 0, 1.6 * ww[0], 1.6 * ww[1], "var(--red)", 2.2));
        note = "Reachable set from 0: one line. No combination of the columns has a component along w = (" + num(ww[0]) + ", " + num(ww[1]) + ").";
      } else {
        note = "Reachable set from 0: only the origin.";
      }
      layer.appendChild(vec(m.b, "var(--blue)", "b"));
      layer.appendChild(vec(m.Ab, "var(--orange)", "Ab"));
      var P = m.point, inside = Math.abs(P[0]) <= R && Math.abs(P[1]) <= R;
      if (inside) { var q = map(P[0], P[1]); layer.appendChild(s("circle", { cx: q[0], cy: q[1], r: 6, style: "fill:var(--teal)" })); }
      plotNote.textContent = note + " Point αb + βAb = (" + num(P[0]) + ", " + num(P[1]) + ")" + (inside ? "." : " is outside the plotted square.");
      plotNote.className = "plot-note" + (inside ? "" : " warn");
    }
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
