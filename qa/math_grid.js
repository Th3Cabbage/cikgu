// Prints ODEMath values for a parameter grid as JSON, for qa/test_math.py to compare with Python.
// Usage: node qa/math_grid.js <path-to-ode_math.js>
"use strict";
const path = require("path");
const M = require(path.resolve(process.argv[2]));

const as = [0.5, 1, 1.7, 3], bs = [0, 0.4, 2, 4, 4.000001, 5, 8], cs = [0.5, 1, 4, 9];
const ics = [[1, 0], [0, 1], [-3, 3], [0, 0], [2.5, -1.25]];
const ts = [0, 0.37, 1, 2.5, 5, 8];
const rows = [];
for (const a of as) for (const b of bs) for (const c of cs) {
  const info = M.analyze(a, b, c);
  for (const [y0, v0] of ics) {
    rows.push({
      a, b, c, y0, v0,
      y: ts.map(t => M.solution(t, a, b, c, y0, v0)),
      dy: ts.map(t => M.derivative(t, a, b, c, y0, v0)),
      case: info.case, damping: info.damping,
      roots: M.rootsText(a, b, c), label: M.dampingText(a, b, c),
    });
  }
}
const bounds = [0, 1e-12, 0.5, 0.9, 0.95, 1, 2.7, 3.64, 7.9, 12, 123].map(m => M.niceBound(m));
const fmts = [-0.004, 0.004, -0.005, 1.005, -2.345, 3.14159, -0, 12.5].map(M.fmt);
let errors = [];
for (const bad of [[0, 1, 1], [NaN, 1, 1], [1, Infinity, 1]]) {
  try { M.solution(0.5, bad[0], bad[1], bad[2], 1, 0); errors.push("no-throw"); }
  catch (e) { errors.push(e.name); }
}
process.stdout.write(JSON.stringify({ ts, rows, bounds, fmts, errors }));
