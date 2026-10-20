// Stability explorer regressions (no browser, no API): verdict boundary cases, 240 Hz elapsed-time playback,
// pause/navigation cancellation, saved-settings validation, finite clipped plot coordinates.
//   node qa\stability_explorer_regression.js
"use strict";
const assert = require("assert/strict");
const fs = require("fs");
const vm = require("vm");
const path = require("path");
const M = require("../courses/controls/stability-eigenvalues/dist/study_math.js");
const course = JSON.parse(fs.readFileSync(path.join(__dirname, "../courses/controls/stability-eigenvalues/dist/course.json"), "utf8"));
const cfg = course.explorer;
const base = { s: 0.5, x1: 1, x2: 1 };
const cases = [
  [{ kind: "real", l1: -1, l2: -2 }, "asymptotic"], [{ kind: "real", l1: 0, l2: -1 }, "lyapunov"], [{ kind: "real", l1: 0, l2: 0 }, "lyapunov"],
  [{ kind: "real", l1: 0, l2: 0.5 }, "unstable"], [{ kind: "real", l1: 0.4, l2: -1 }, "unstable"], [{ kind: "real", l1: -1, l2: -1 }, "asymptotic"],
  [{ kind: "complex", a: 0, b: 1.5 }, "lyapunov"], [{ kind: "complex", a: -0.05, b: 4 }, "asymptotic"], [{ kind: "complex", a: 0.05, b: 0.2 }, "unstable"],
  [{ kind: "jordan", lj: 0 }, "unstable"], [{ kind: "jordan", lj: -0.05 }, "asymptotic"], [{ kind: "jordan", lj: 0.05 }, "unstable"],
];
for (const [p, want] of cases) {
  const q = Object.assign({}, base, p);
  assert.equal(M.classifyContinuous(q), want, JSON.stringify(p));
  for (const dt of [0.05, 0.5, 1.5]) assert.equal(M.classifyDiscrete(q, dt), want, "discrete " + JSON.stringify(p) + " dt=" + dt);
}
// per-start behaviour: special starts in unstable systems
assert.equal(M.startBehaviour({ kind: "real", l1: 0.4, l2: -1, s: 1, x1: 1, x2: 1 }), "decays");
assert.equal(M.startBehaviour({ kind: "jordan", lj: 0, s: 1.5, x1: 1, x2: 0 }), "bounded");
assert.equal(M.startBehaviour({ kind: "jordan", lj: 0, s: 0, x1: 0, x2: 1 }), "grows");
assert.equal(M.startBehaviour({ kind: "complex", a: -1, b: 1, s: 0, x1: 0, x2: 0 }), "rest");

// ---- run the real explorer with a tiny DOM adapter and a manually driven RAF clock
const nodes = new Map();
function element(tag, attrs, children) {
  attrs = attrs || {};
  const n = { tag, children: [], attrs: {}, value: attrs.value, textContent: attrs.text || "", hidden: false, parentNode: null,
    appendChild(c) { if (typeof c !== "object") c = element("#text", { text: String(c) }); this.children.push(c); c.parentNode = this; return c; },
    removeChild(c) { this.children.splice(this.children.indexOf(c), 1); },
    get firstChild() { return this.children[0]; },
    setAttribute(k, v) { this.attrs[k] = String(v); }, getAttribute(k) { return k in this.attrs ? this.attrs[k] : (attrs[k] === undefined ? null : String(attrs[k])); },
    addEventListener(k, fn) { this["on_" + k] = fn; } };
  Object.keys(attrs).forEach(k => { if (k !== "text" && k !== "onclick") n.attrs[k] = String(attrs[k]); });
  if (attrs.id) nodes.set(attrs.id, n);
  if (attrs.onclick) n.click = attrs.onclick;
  (children || []).forEach(c => n.appendChild(c));
  return n;
}
let pending = null;
const win = { StudyMath: M };
const sandbox = { window: win, requestAnimationFrame(fn) { pending = fn; return 1; }, cancelAnimationFrame() { pending = null; }, console, Math };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../courses/controls/stability-eigenvalues/dist/explorer.js"), "utf8"), sandbox);
const state = { explorer: null };
const math = (n, text) => { n.textContent = text; return n; };
const root = element("root");
let saves = 0;
win.StudyExplorer.render({ root, course, state, save() { saves++; }, html: element, svg: element, mathText: math, flowMath: math, displayMath: math, announce() {} });
const play = nodes.get("ex-play");
const t0 = state.explorer.t;
play.on_click();
for (let i = 0; i <= 240; i++) { const fn = pending; pending = null; assert.ok(fn, "frame " + i); fn(i * 1000 / 240); }
assert.ok(Math.abs(state.explorer.t - t0 - cfg.playRate) < 1e-9, "time advances by elapsed seconds, independent of frame rate");
play.on_click();
assert.equal(pending, null, "pause cancels playback");
play.on_click();
for (let i = 0; i <= 48; i++) { const fn = pending; pending = null; fn(10000 + i * 1000 / 48); }   // another 1 s of playback
const tLive = state.explorer.t, s0 = saves;
win.StudyExplorer.stop();
assert.equal(pending, null, "navigation stop cancels playback");
assert.ok(saves === s0 + 1 && state.explorer.t === tLive && tLive > t0 + cfg.playRate + 0.9, "navigation stop saves the latest playback time");
win.StudyExplorer.stop(); assert.equal(saves, s0 + 1, "stop without active playback does not save again");

// ---- saved settings validation
const ok = win.StudyExplorer.restore(state.explorer, cfg);
assert.ok(ok && Math.abs(ok.t - state.explorer.t) <= cfg.t.step / 2 + 1e-9, "valid state restores (snapped)");
const bad = [null, "x", {}, Object.assign({}, ok, { kind: "magic" }), Object.assign({}, ok, { a: NaN }), Object.assign({}, ok, { b: Infinity }),
  Object.assign({}, ok, { dt: 0 }), Object.assign({}, ok, { s: "1" }), Object.assign({}, ok, { t: 10.5 }), (() => { const o = Object.assign({}, ok); delete o.lj; return o; })()];
bad.forEach((b, i) => assert.equal(win.StudyExplorer.restore(b, cfg), null, "invalid saved state #" + i + " rejected"));

// ---- per-eigenvalue colours: a saddle shows its decaying mode green and its growing mode red in both planes
function poles(id) { return all(nodes.get(id), "path").map(p => p.attrs.class).filter(c => /^pole /.test(c)); }
function all(n, tag, out) { out = out || []; if (n.tag === tag) out.push(n); n.children.forEach(c => all(c, tag, out)); return out; }
function setState(p) { Object.assign(state.explorer, p); nodes.get("ex-s").on_input(); }
setState({ kind: "real", l1: 0.4, l2: -1, s: 1, dt: 0.5, t: 5 });
assert.deepEqual(poles("ex-lplane").sort(), ["pole stable", "pole unstable"], "saddle: continuous-time colours per eigenvalue");
assert.deepEqual(poles("ex-zplane").sort(), ["pole stable", "pole unstable"], "saddle: discrete-time colours per eigenvalue");
assert.equal(nodes.get("ex-verdict").attrs["data-kind"], "unstable", "whole-system verdict stays unstable");
setState({ kind: "real", l1: 0, l2: -1 });
assert.deepEqual(poles("ex-lplane").sort(), ["pole marginal", "pole stable"], "zero mode amber, decaying mode green");
setState({ kind: "jordan", lj: 0 });
assert.deepEqual(poles("ex-lplane"), ["pole unstable"], "defective boundary eigenvalue red");
setState({ kind: "complex", a: 0, b: 1.5 });
assert.deepEqual(poles("ex-zplane"), ["pole marginal", "pole marginal"], "semisimple unit-circle pair amber");

// ---- extreme growth: plotted coordinates stay finite and bounded (clipped), with a warning
Object.assign(state.explorer, { kind: "complex", a: 1, b: 4, dt: 1.5, t: 10 });
nodes.get("ex-a").value = "1"; nodes.get("ex-a").on_input();
const pts = all(root, "polyline").flatMap(p => p.attrs.points.split(/[ ,]/).filter(Boolean).map(Number));
assert.ok(pts.length > 0 && pts.every(Number.isFinite) && Math.max(...pts.map(Math.abs)) < 3000, "clipped finite coordinates");
assert.match(nodes.get("ex-tnote").className || "", /warn/, "time plot warns when curves leave the range");
assert.equal(nodes.get("ex-verdict").attrs["data-kind"], "unstable");
console.log(`PASS ${cases.length} verdict cases x 3 sampling steps; 4 start cases; 240 Hz elapsed-time playback; pause; stop saves live time; per-eigenvalue colours; ${bad.length} invalid saved states; clipped extreme plot`);
