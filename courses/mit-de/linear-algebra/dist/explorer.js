/*
 * Linear-algebra explorer: four subspaces of an integer matrix, and the incidence matrix of a graph.
 * Maths comes from window.StudyMath (rref, subspaces, solve, graphInfo, toTex, toNumber).
 * Saved state: state.explorer = {mode, A, b, edges}.
 * Contract with app.js: window.StudyExplorer = { restore, stop, render }.
 */
(function () {
  "use strict";
  var SM = window.StudyMath;
  var uid = 0;

  function ex(config) { return config || {}; }
  function range(config) {
    var r = ex(config).entryRange;
    return Array.isArray(r) && r.length === 2 ? r : [-9, 9];
  }
  function maxRows(config) { return ex(config).maxRows || 4; }
  function maxCols(config) { return ex(config).maxCols || 4; }
  function modeIds(config) { return (ex(config).modes || []).map(function (m) { return m.id; }); }
  function cloneM(A) { return A.map(function (r) { return r.slice(); }); }
  function findMatrix(config, id) {
    var list = ex(config).matrices || [];
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return list[0] || { A: [[1, 0], [0, 1]], b: [0, 0] };
  }
  function validMatrix(A, config) {
    var rg = range(config);
    if (!Array.isArray(A) || A.length < 1 || A.length > maxRows(config)) return false;
    if (!Array.isArray(A[0]) || A[0].length < 1 || A[0].length > maxCols(config)) return false;
    return A.every(function (r) {
      return Array.isArray(r) && r.length === A[0].length && r.every(function (x) {
        return typeof x === "number" && isFinite(x) && Math.round(x) === x && x >= rg[0] && x <= rg[1];
      });
    });
  }
  function validVec(b, len, config) {
    var rg = range(config);
    return Array.isArray(b) && b.length === len && b.every(function (x) {
      return typeof x === "number" && isFinite(x) && Math.round(x) === x && x >= rg[0] && x <= rg[1];
    });
  }
  function edgeIndex(config, e) {
    var c = ex(config).candidateEdges || [];
    if (!Array.isArray(e) || e.length !== 2) return -1;
    for (var i = 0; i < c.length; i++) if (c[i][0] === e[0] && c[i][1] === e[1]) return i;
    return -1;
  }
  // Edges are kept in candidate order, without duplicates.
  function cleanEdges(list, config) {
    var on = {};
    (list || []).forEach(function (e) { var i = edgeIndex(config, e); if (i >= 0) on[i] = true; });
    var c = ex(config).candidateEdges || [];
    return c.filter(function (_, i) { return on[i]; }).map(function (e) { return e.slice(); });
  }
  function defaults(config) {
    var mat = findMatrix(config, null);
    return {
      mode: ex(config).defaultMode || (modeIds(config)[0] || "matrix"),
      A: cloneM(mat.A), b: mat.b.slice(),
      edges: cleanEdges(ex(config).defaultEdges, config)
    };
  }
  function restore(saved, config) {
    var out = defaults(config);
    if (!saved || typeof saved !== "object" || !config) return out;
    if (typeof saved.mode === "string" && modeIds(config).indexOf(saved.mode) >= 0) out.mode = saved.mode;
    if (validMatrix(saved.A, config)) {
      out.A = cloneM(saved.A);
      out.b = validVec(saved.b, saved.A.length, config) ? saved.b.slice() : saved.A.map(function () { return 0; });
    }
    if (Array.isArray(saved.edges) && saved.edges.every(function (e) { return edgeIndex(config, e) >= 0; })) {
      out.edges = cleanEdges(saved.edges, config);
    }
    return out;
  }
  function stop() { /* no timers */ }

  // ---- LaTeX helpers ----
  function fTex(x) { return SM.toTex(x); }
  function matTex(M) {
    return "\\begin{bmatrix} " + M.map(function (r) { return r.map(fTex).join(" & "); }).join(" \\\\ ") + " \\end{bmatrix}";
  }
  function intMatTex(M) {
    return "\\begin{bmatrix} " + M.map(function (r) { return r.join(" & "); }).join(" \\\\ ") + " \\end{bmatrix}";
  }
  function vecTex(v) {
    return "\\begin{bmatrix} " + v.map(fTex).join(" \\\\ ") + " \\end{bmatrix}";
  }
  function basisTex(list, len) {
    if (!list.length) return "\\{\\mathbf{0}\\}";
    return list.map(function (v) { return vecTex(len ? v : v); }).join(",\\ ");
  }
  function rowAsCol(v) { return v; } // row space vectors are shown as columns (transposed)
  function ordinal(i) { return String(i + 1); }

  function render(ctx) {
    stop();
    var h = ctx.html, s = ctx.svg, config = ctx.course.explorer, root = ctx.root;
    var st = ctx.state.explorer = restore(ctx.state.explorer, config);
    var rg = range(config), MR = maxRows(config), MC = maxCols(config);
    var NODES = config.graphNodes || [[0.15, 0.2], [0.85, 0.2], [0.5, 0.85], [0.5, 0.45]];
    var CAND = config.candidateEdges || [];
    var id = ++uid, loopSel = -1;

    root.appendChild(h("header", { className: "page-head" }, [
      h("p", { className: "eyebrow", text: "Explorer" }),
      h("h1", { text: "The four subspaces, and graphs" }),
      ctx.mathText(h("p", { className: "lede" }), "Edit an integer matrix $A$ and right side $b$ to see its row reduction, the four fundamental subspaces and the complete solution of $Av=b$. Or switch to a graph: toggle edges and read the incidence matrix, its null spaces and the loops.")
    ]));

    // ---------- shared controls ----------
    var radios = {};
    var modeBox = h("fieldset", { className: "kind-set", style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "Mode", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    (config.modes || []).forEach(function (m) {
      var rid = "la-mode-" + id + "-" + m.id;
      var r = h("input", { type: "radio", name: "la-mode-" + id, id: rid, value: m.id });
      r.checked = st.mode === m.id;
      r.addEventListener("change", function () {
        if (r.checked) { st.mode = m.id; update(); ctx.save(); ctx.announce("Mode: " + m.label); }
      });
      radios[m.id] = r;
      modeBox.appendChild(h("label", { className: "check-row", "for": rid, style: "margin:2px 0" }, [r, h("span", { text: m.label })]));
    });

    // matrix controls
    var rowSel = h("select", { id: "la-rows-" + id }), colSel = h("select", { id: "la-cols-" + id });
    var k;
    for (k = 1; k <= MR; k++) rowSel.appendChild(h("option", { value: k, text: String(k) }));
    for (k = 1; k <= MC; k++) colSel.appendChild(h("option", { value: k, text: String(k) }));
    rowSel.setAttribute("aria-label", "Number of rows m");
    colSel.setAttribute("aria-label", "Number of columns n");
    rowSel.addEventListener("change", function () { resize(parseInt(rowSel.value, 10), st.A[0].length); });
    colSel.addEventListener("change", function () { resize(st.A.length, parseInt(colSel.value, 10)); });
    var sizeRow = h("div", { style: "display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:6px 0" }, [
      h("label", { "for": rowSel.id, text: "Rows m " }), rowSel,
      h("label", { "for": colSel.id, text: "Columns n " }), colSel
    ]);
    var gridBox = h("div", { style: "overflow-x:auto;padding:4px 0" });
    var inputStyle = "width:3.6em;font-size:16px;padding:4px;text-align:center;box-sizing:border-box";

    function resize(m, n) {
      var A = [], b = [], i, j;
      for (i = 0; i < m; i++) {
        A.push([]);
        for (j = 0; j < n; j++) A[i].push(i < st.A.length && j < st.A[0].length ? st.A[i][j] : 0);
        b.push(i < st.b.length ? st.b[i] : 0);
      }
      st.A = A; st.b = b;
      buildGrid(); update(); ctx.save();
      ctx.announce("Matrix size " + m + " by " + n);
    }
    function entryInput(label, value, onset) {
      var inp = h("input", { type: "number", min: rg[0], max: rg[1], step: 1, value: value, style: inputStyle });
      inp.setAttribute("aria-label", label);
      inp.setAttribute("inputmode", "numeric");
      inp.addEventListener("input", function () {
        var v = parseInt(inp.value, 10);
        if (!isFinite(v)) v = 0;
        v = Math.max(rg[0], Math.min(rg[1], v));
        onset(v); update(); ctx.save();
      });
      inp.addEventListener("change", function () {
        var v = parseInt(inp.value, 10);
        if (!isFinite(v)) v = 0;
        v = Math.max(rg[0], Math.min(rg[1], v));
        inp.value = v;
      });
      return inp;
    }
    function buildGrid() {
      gridBox.textContent = "";
      var m = st.A.length, n = st.A[0].length;
      rowSel.value = String(m); colSel.value = String(n);
      var g = h("div", { role: "group", "aria-label": "Matrix A and right side b",
        style: "display:grid;gap:4px;align-items:center;width:max-content;grid-template-columns:repeat(" + n + ",3.6em) 1.2em 3.6em" });
      for (var i = 0; i < m; i++) {
        for (var j = 0; j < n; j++) {
          (function (i, j) {
            g.appendChild(entryInput("A row " + (i + 1) + " column " + (j + 1), st.A[i][j], function (v) { st.A[i][j] = v; }));
          }(i, j));
        }
        g.appendChild(h("span", { text: "|", style: "text-align:center", "aria-hidden": "true" }));
        (function (i) {
          g.appendChild(entryInput("b entry " + (i + 1), st.b[i], function (v) { st.b[i] = v; }));
        }(i));
      }
      gridBox.appendChild(g);
    }
    var matButtons = h("div", { className: "presets" }, (config.matrices || []).map(function (mx) {
      return h("button", { type: "button", className: "btn small", text: mx.label, onclick: function () { loadMatrix(mx); ctx.announce("Loaded " + mx.label); } });
    }));
    function loadMatrix(mx) {
      st.A = cloneM(mx.A); st.b = mx.b.slice();
      buildGrid(); update(); ctx.save();
    }
    var matControls = h("div", null, [
      h("p", { className: "plot-note", text: "Entries are integers from " + rg[0] + " to " + rg[1] + ". The last column is the right side b." }),
      sizeRow, gridBox,
      h("p", { className: "plot-note", text: "Load an example:" }), matButtons
    ]);

    // graph controls
    var edgeChecks = [];
    var edgeBox = h("fieldset", { style: "border:0;padding:0;margin:0 0 10px" }, [
      h("legend", { text: "Edges (direction start to end)", style: "font-weight:600;font-size:0.92rem;padding:0;margin-bottom:4px" })
    ]);
    CAND.forEach(function (e, i) {
      var cid = "la-edge-" + id + "-" + i;
      var cb = h("input", { type: "checkbox", id: cid });
      cb.setAttribute("aria-label", "Edge " + (i + 1) + " from node " + e[0] + " to node " + e[1]);
      cb.addEventListener("change", function () { setEdge(i, cb.checked); });
      edgeChecks.push(cb);
      edgeBox.appendChild(h("label", { className: "check-row", "for": cid, style: "margin:2px 0" }, [
        cb, h("span", { text: "Edge " + (i + 1) + ":  " + e[0] + " → " + e[1] })]));
    });
    var graphControls = h("div", null, [edgeBox]);
    function isOn(i) { return edgeIndex(config, CAND[i]) >= 0 && st.edges.some(function (e) { return e[0] === CAND[i][0] && e[1] === CAND[i][1]; }); }
    function setEdge(i, on) {
      var cur = {};
      st.edges.forEach(function (e) { cur[edgeIndex(config, e)] = true; });
      if (on) cur[i] = true; else delete cur[i];
      st.edges = CAND.filter(function (_, j) { return cur[j]; }).map(function (e) { return e.slice(); });
      loopSel = -1;
      update(); ctx.save();
      ctx.announce("Edge " + (i + 1) + (on ? " on" : " off") + ", " + st.edges.length + " edges active");
    }

    // presets
    var presetNote = h("p", { className: "plot-note" });
    var presets = h("div", { className: "presets" }, (config.presets || []).map(function (p) {
      return h("button", { type: "button", className: "btn small", text: p.label, onclick: function () {
        if (p.mode && radios[p.mode]) { st.mode = p.mode; radios[p.mode].checked = true; }
        if (p.matrix) { var mx = findMatrix(config, p.matrix); st.A = cloneM(mx.A); st.b = mx.b.slice(); buildGrid(); }
        else if (validMatrix(p.A, config)) {
          st.A = cloneM(p.A); st.b = validVec(p.b, p.A.length, config) ? p.b.slice() : p.A.map(function () { return 0; }); buildGrid();
        }
        if (Array.isArray(p.edges)) { st.edges = cleanEdges(p.edges, config); loopSel = -1; }
        if (p.note) ctx.mathText(presetNote, p.note); else presetNote.textContent = "";
        update(); ctx.save(); ctx.announce("Preset: " + p.label);
      } });
    }));

    var controls = h("div", null, [
      h("h2", { text: "Controls" }), modeBox,
      matControls, graphControls, presets
    ]);

    // ---------- matrix results ----------
    var mRef = h("div", { className: "readout" });
    var mCards = h("div", { style: "display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:8px 0" });
    var BW = 340, BH = 190;
    var bigSvg = s("svg", { viewBox: "0 0 " + BW + " " + BH, role: "img", style: "width:100%;height:auto;max-width:420px" });
    var bigCap = h("p", { className: "plot-note" });
    var mSolve = h("div", { className: "readout" });
    var matPanel = h("div", null, [
      h("div", { className: "plot-box" }, [h("h3", { text: "Row reduction" }), mRef]),
      h("div", { className: "plot-box" }, [h("h3", { text: "Four subspaces" }), mCards,
        h("h3", { text: "Big picture" }), bigSvg, bigCap]),
      h("div", { className: "plot-box" }, [h("h3", { text: "Solving Av = b" }), mSolve])
    ]);

    // ---------- graph results ----------
    var GW = 360, GH = 300, GP = 36, NR = 15;
    var gSvg = s("svg", { viewBox: "0 0 " + GW + " " + GH, role: "img",
      "aria-label": "Graph with four nodes and directed edges. Click an edge to switch it on or off.",
      style: "width:100%;height:auto;max-width:460px;touch-action:manipulation" });
    var gCap = h("p", { className: "plot-note" });
    var loopBtns = h("div", { className: "presets" });
    var gInfo = h("div", { className: "readout" });
    var gMat = h("div", { className: "readout" });
    var graphPanel = h("div", null, [
      h("div", { className: "plot-box" }, [h("h3", { text: "Graph" }), gSvg,
        h("div", { className: "legend" }, [
          h("span", null, [h("span", { className: "sw", style: "background:var(--teal)" }), "loop flow +1"]),
          h("span", null, [h("span", { className: "sw", style: "background:var(--orange)" }), "loop flow −1 (against the arrow)"])]),
        gCap]),
      h("div", { className: "plot-box" }, [h("h3", { text: "Incidence matrix and Laplacian" }), gMat]),
      h("div", { className: "plot-box" }, [h("h3", { text: "Null spaces and loops" }), gInfo, loopBtns])
    ]);

    root.appendChild(h("section", { className: "explorer" }, [
      h("div", { className: "ex-panel" }, [h("div", { className: "ex-layout" }, [controls,
        h("div", null, [matPanel, graphPanel, presetNote])])])
    ]));

    function clear(g) { while (g.firstChild) g.removeChild(g.firstChild); }
    function show(el, on) { el.hidden = !on; el.style.display = on ? "" : "none"; }
    function para(parent, t, cls) {
      var el = ctx.mathText(h("p", { style: "margin:3px 0" }), t);
      if (cls) el.className = cls;
      parent.appendChild(el);
      return el;
    }
    function eq(parent, tex) { parent.appendChild(ctx.displayMath(h("div", { className: "ro-eq" }), tex)); }
    function sub(list, len) {
      return list.length ? basisTex(list, len) : "\\{\\mathbf{0}\\}";
    }

    // ---------- matrix mode ----------
    function updateMatrix() {
      var A = st.A, b = st.b, m = A.length, n = A[0].length;
      var sp = SM.subspaces(A), r = sp.rank;
      var colour = function (j) { return sp.pivots.indexOf(j) >= 0; };

      mRef.textContent = "";
      var pivTex = sp.pivots.map(function (j) { return "\\mathbf{" + (j + 1) + "}"; }).join(", ") || "\\text{none}";
      // mark pivot columns with a coloured header row above R
      var head = "\\begin{bmatrix} " + sp.R.map(function (row) {
        return row.map(function (x, j) { return colour(j) ? "\\color{#0f766e}{" + fTex(x) + "}" : fTex(x); }).join(" & ");
      }).join(" \\\\ ") + " \\end{bmatrix}";
      eq(mRef, "A = " + intMatTex(A) + " \\;\\longrightarrow\\; R = \\operatorname{rref}(A) = " + head);
      para(mRef, "Rank $r = " + r + "$. Pivot columns (teal in $R$): " + (sp.pivots.length ? "columns $" + pivTex + "$" : "none") +
        ". Free columns: " + (n - r) + ".");

      mCards.textContent = "";
      var cards = [
        { key: "row", title: "Row space $C(A^T)$ in $\\mathbb{R}^{" + n + "}$", dim: "r = " + r, list: sp.row, len: n },
        { key: "null", title: "Null space $N(A)$ in $\\mathbb{R}^{" + n + "}$", dim: "n - r = " + (n - r), list: sp.null, len: n },
        { key: "col", title: "Column space $C(A)$ in $\\mathbb{R}^{" + m + "}$", dim: "r = " + r, list: sp.col, len: m },
        { key: "leftNull", title: "Left null space $N(A^T)$ in $\\mathbb{R}^{" + m + "}$", dim: "m - r = " + (m - r), list: sp.leftNull, len: m }
      ];
      cards.forEach(function (c) {
        var card = h("div", { className: "readout", style: "overflow-x:auto" });
        card.appendChild(ctx.mathText(h("h4", { style: "margin:0 0 4px" }), c.title));
        para(card, "Dimension $" + c.dim + "$ (dim " + sp.dims[c.key] + ")");
        eq(card, "\\text{basis: } " + sub(c.list, c.len));
        mCards.appendChild(card);
      });

      // big picture
      clear(bigSvg);
      var unit = 20, bw = 100, xl = 30, xr = BW - 30 - bw, top = 30;
      function box(x, y0, dim, fill, label) {
        var hgt = Math.max(dim, 0) * unit;
        if (dim === 0) bigSvg.appendChild(s("line", { x1: x, y1: y0, x2: x + bw, y2: y0, style: "stroke:" + fill + ";stroke-width:3" }));
        else bigSvg.appendChild(s("rect", { x: x, y: y0, width: bw, height: hgt, rx: 4, style: "fill:" + fill + ";fill-opacity:0.25;stroke:" + fill + ";stroke-width:1.8" }));
        bigSvg.appendChild(s("text", { x: x + bw / 2, y: y0 + hgt / 2 + (dim === 0 ? -6 : 4), "text-anchor": "middle", style: "font-size:12px;fill:currentColor", text: label + " (" + dim + ")" }));
        return hgt;
      }
      bigSvg.appendChild(s("text", { x: xl + bw / 2, y: 16, "text-anchor": "middle", style: "font-size:12px;font-weight:600;fill:currentColor", text: "R^" + n }));
      bigSvg.appendChild(s("text", { x: xr + bw / 2, y: 16, "text-anchor": "middle", style: "font-size:12px;font-weight:600;fill:currentColor", text: "R^" + m }));
      var y = top;
      y += box(xl, y, r, "var(--teal)", "row space") + 10;
      box(xl, y, n - r, "var(--orange)", "null space");
      y = top;
      y += box(xr, y, r, "var(--blue)", "column space") + 10;
      box(xr, y, m - r, "var(--pink)", "left null");
      bigSvg.appendChild(s("path", { d: "M" + (xl + bw + 6) + " " + (top + 10) + " L" + (xr - 6) + " " + (top + 10),
        style: "stroke:var(--muted);stroke-width:1.6;stroke-dasharray:5 4;fill:none" }));
      bigSvg.appendChild(s("text", { x: BW / 2, y: top + 6, "text-anchor": "middle", style: "font-size:11px;fill:var(--muted)", text: "A" }));
      bigSvg.setAttribute("aria-label", "Big picture: in R^" + n + ", row space dimension " + r + " and null space dimension " + (n - r) +
        "; in R^" + m + ", column space dimension " + r + " and left null space dimension " + (m - r));
      bigCap.textContent = "Box heights are proportional to dimension. Dimensions: " + r + " + " + (n - r) + " = " + n + " and " + r + " + " + (m - r) + " = " + m + ".";

      // solve
      mSolve.textContent = "";
      var sol = SM.solve(A, b);
      var bTex = vecTex(b.map(function (x) { return [x, 1]; }));
      eq(mSolve, "Av = b,\\quad b = " + bTex);
      if (sol.solvable) {
        para(mSolve, "$b$ is in $C(A)$, so there are solutions.");
        var tex = "v = " + vecTex(sol.particular);
        sol.nullBasis.forEach(function (v, i) { tex += " + c_{" + (i + 1) + "}" + vecTex(v); });
        eq(mSolve, "v_p = " + vecTex(sol.particular));
        eq(mSolve, tex);
        para(mSolve, sol.nullBasis.length
          ? "Free variables are set to $0$ for $v_p$; add any combination of the " + sol.nullBasis.length + " special solution" + (sol.nullBasis.length > 1 ? "s" : "") + " of $N(A)$."
          : "$N(A) = \\{\\mathbf{0}\\}$, so the solution is unique.");
      } else {
        var aug = A.map(function (row, i) { return row.concat([b[i]]); });
        var ra = SM.rref(aug), bad = ra.pivots.indexOf(n);
        para(mSolve, "$b$ is not in $C(A)$: no solution.", "");
        eq(mSolve, "\\operatorname{rref}([A\\ b]) = " + matTex(ra.R));
        if (bad >= 0) para(mSolve, "Row " + (bad + 1) + " of $\\operatorname{rref}([A\\ b])$ says $0 = " + fTex(ra.R[bad][n]) + "$, which is impossible.");
      }
    }

    // ---------- graph mode ----------
    function nodeXY(i) {
      var p = NODES[i] || [0.5, 0.5];
      return [GP + p[0] * (GW - 2 * GP), GP + p[1] * (GH - 2 * GP)];
    }
    function drawGraph(info, loop) {
      clear(gSvg);
      var defs = s("defs");
      gSvg.appendChild(defs);
      var layerE = s("g"), layerN = s("g");
      gSvg.appendChild(layerE); gSvg.appendChild(layerN);
      var rowOf = {};
      st.edges.forEach(function (e, r) { rowOf[edgeIndex(config, e)] = r; });
      CAND.forEach(function (e, i) {
        var a = nodeXY(e[0] - 1), b = nodeXY(e[1] - 1);
        var dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1, ux = dx / len, uy = dy / len;
        var on = rowOf[i] !== undefined;
        var w = 0;
        if (on && loop) w = Math.sign(SM.toNumber(loop[rowOf[i]]));
        var col = !on ? "var(--muted)" : w > 0 ? "var(--teal)" : w < 0 ? "var(--orange)" : loop ? "var(--muted)" : "var(--blue)";
        var op = !on ? 0.4 : (loop && w === 0 ? 0.35 : 1);
        var x1 = a[0] + ux * NR, y1 = a[1] + uy * NR, x2 = b[0] - ux * NR, y2 = b[1] - uy * NR;
        var g = s("g", { style: "cursor:pointer" });
        g.appendChild(s("line", { x1: x1, y1: y1, x2: x2, y2: y2, style: "stroke:transparent;stroke-width:16" }));
        g.appendChild(s("line", { x1: x1, y1: y1, x2: x2, y2: y2,
          style: "stroke:" + col + ";opacity:" + op + ";stroke-width:" + (on ? 2.6 : 1.6) + (on ? "" : ";stroke-dasharray:5 5") }));
        // arrowhead: at the end for forward flow, at the start when the loop runs against the arrow
        var rev = w < 0, tipx = rev ? x1 : x2, tipy = rev ? y1 : y2, dirx = rev ? -ux : ux, diry = rev ? -uy : uy, z = 10;
        g.appendChild(s("polygon", { points: [
          tipx.toFixed(1) + "," + tipy.toFixed(1),
          (tipx - dirx * z + diry * z * 0.5).toFixed(1) + "," + (tipy - diry * z - dirx * z * 0.5).toFixed(1),
          (tipx - dirx * z - diry * z * 0.5).toFixed(1) + "," + (tipy - diry * z + dirx * z * 0.5).toFixed(1)].join(" "),
          style: "fill:" + col + ";opacity:" + op }));
        // edge number, offset perpendicular to the edge
        var mx = (x1 + x2) / 2 - uy * 11, my = (y1 + y2) / 2 + ux * 11;
        g.appendChild(s("text", { x: mx, y: my + 4, "text-anchor": "middle",
          style: "font-size:12px;font-weight:600;fill:" + (on ? "currentColor" : "var(--muted)") + ";opacity:" + (on ? 1 : 0.7), text: String(i + 1) }));
        g.addEventListener("click", function () { edgeChecks[i].checked = !isOn(i); setEdge(i, edgeChecks[i].checked); });
        layerE.appendChild(g);
      });
      for (var i = 0; i < NODES.length; i++) {
        var p = nodeXY(i);
        layerN.appendChild(s("circle", { cx: p[0], cy: p[1], r: NR, style: "fill:#fff;stroke:var(--blue);stroke-width:2" }));
        layerN.appendChild(s("text", { x: p[0], y: p[1] + 5, "text-anchor": "middle", style: "font-size:14px;font-weight:700;fill:#1f2937", text: String(i + 1) }));
      }
    }
    function updateGraph() {
      var n = NODES.length, m = st.edges.length;
      CAND.forEach(function (_, i) { edgeChecks[i].checked = isOn(i); });
      var info = SM.graphInfo(n, st.edges);
      var loops = info.loops || [];
      if (loopSel >= loops.length) loopSel = -1;
      drawGraph(info, loopSel >= 0 ? loops[loopSel] : null);

      var edgeNums = st.edges.map(function (e) { return edgeIndex(config, e) + 1; });
      gMat.textContent = "";
      gInfo.textContent = "";
      loopBtns.textContent = "";
      var cc = info.components, r = info.rank;
      if (m === 0) {
        para(gMat, "No edges are active: $A$ has no rows. Switch some edges on.");
        gCap.textContent = "All edges are off. Click an edge in the picture or tick it in the list.";
      } else {
        eq(gMat, "A = " + intMatTex(info.A) + "\\quad \\text{(rows are edges } " + edgeNums.join(", ") + "\\text{)}");
        eq(gMat, "A^{\\mathsf T}A = " + intMatTex(info.laplacian) + "\\quad \\text{(the graph Laplacian)}");
        gCap.textContent = "Active edges are solid; inactive edges are faint and dashed. Arrows point from start to end. Click an edge to toggle it.";
      }
      para(gMat, "$m = " + m + "$ edges, $n = " + n + "$ nodes, rank $r = " + r + " = n - " + cc + "$ (" + cc + " connected component" + (cc === 1 ? "" : "s") + ").");

      // N(A): constant on components
      var nulls = m ? info.nullA : [];
      if (!m) { nulls = []; for (var j = 0; j < n; j++) { var e0 = []; for (var q = 0; q < n; q++) e0.push([q === j ? 1 : 0, 1]); nulls.push(e0); } }
      para(gInfo, "$\\dim N(A) = n - r = " + (n - r) + "$ = number of components: $A v = 0$ means $v$ is constant on each connected component.");
      eq(gInfo, "N(A)\\text{ basis: } " + basisTex(nulls, n));
      var nloop = m - r;
      para(gInfo, "$\\dim N(A^{\\mathsf T}) = m - r = m - n + " + cc + " = " + nloop + "$ independent loop" + (nloop === 1 ? "" : "s") + ".");
      if (nloop > 0) {
        eq(gInfo, "N(A^{\\mathsf T})\\text{ basis (loop flows } w\\text{): } " + basisTex(loops, m));
        para(gInfo, "Each loop $w$ satisfies $A^{\\mathsf T}w = 0$: the flow into every node balances. Press a button to see a loop on the graph (teal $+1$, orange $-1$).", "plot-note");
        loops.forEach(function (w, li) {
          var btn = h("button", { type: "button", className: "btn small", text: "Loop " + (li + 1), onclick: function () {
            loopSel = loopSel === li ? -1 : li;
            update();
            ctx.announce(loopSel >= 0 ? "Loop " + (li + 1) + " highlighted" : "Loop highlight off");
          } });
          btn.setAttribute("aria-pressed", loopSel === li ? "true" : "false");
          if (loopSel === li) btn.style.outline = "2px solid var(--teal)";
          btn.setAttribute("aria-label", "Highlight loop " + (li + 1) + " with flows " + w.map(function (x, ri) { return "edge " + edgeNums[ri] + ": " + fTex(x).replace("-", "minus "); }).join(", "));
          loopBtns.appendChild(btn);
        });
      } else if (m > 0) {
        para(gInfo, "$N(A^{\\mathsf T}) = \\{\\mathbf{0}\\}$: this graph has no loops (it is a forest).");
      }
    }

    function update() {
      var isMat = st.mode === "matrix";
      if (radios[st.mode]) radios[st.mode].checked = true;
      show(matControls, isMat); show(matPanel, isMat);
      show(graphControls, !isMat); show(graphPanel, !isMat);
      if (isMat) updateMatrix(); else updateGraph();
    }

    buildGrid();
    update();
    return "Explorer";
  }

  window.StudyExplorer = { restore: restore, stop: stop, render: render };
}());
