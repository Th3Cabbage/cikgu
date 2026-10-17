/*
 * Mathematics for the Control Bootcamp explorers (no dependencies; also loadable in Node for QA).
 *
 * Normalized, linearized inverted pendulum with full-state feedback u = -k1*theta - k2*thetadot:
 *     thetaddot = theta + u + d(t)   =>   xdot = [[0, 1], [1 - k1, -k2]] x + [0, 1]^T d(t)
 * Characteristic polynomial: lambda^2 + k2*lambda + (k1 - 1).
 * Asymptotically stable iff k1 > 1 and k2 > 0. Boundaries: k1 = 1 (an eigenvalue at 0; with
 * k2 = 0 a double zero eigenvalue with a Jordan block, so velocity makes theta drift linearly)
 * and k2 = 0 with k1 > 1 (undamped oscillation).
 *
 * Static cruise teaching model: y = a*u + d. Open loop u = r/aModel; closed loop u = K(r - y):
 *     yOpen = a*r/aModel + d,   yClosed = (a*K*r + d) / (1 + a*K).
 */
(function (root) {
  "use strict";

  var EPS = 1e-9;

  // Snap slider values so that 1.0000000002 counts as the boundary value 1.
  function snap(v) { return Math.round(v * 1e6) / 1e6; }

  function eigenvalues(k1, k2) {
    k1 = snap(k1); k2 = snap(k2);
    var c = k1 - 1;
    var disc = snap(k2 * k2 - 4 * c);
    if (disc >= 0) {
      var s = Math.sqrt(disc);
      return [{ re: (-k2 + s) / 2, im: 0 }, { re: (-k2 - s) / 2, im: 0 }];
    }
    var w = Math.sqrt(-disc) / 2;
    return [{ re: -k2 / 2, im: w }, { re: -k2 / 2, im: -w }];
  }

  function closedLoopMatrix(k1, k2) { return [[0, 1], [1 - k1, -k2]]; }

  // kind: "stable" | "unstable" | "marginal" | "drift"
  function classify(k1, k2) {
    k1 = snap(k1); k2 = snap(k2);
    var ev = eigenvalues(k1, k2);
    var maxRe = Math.max(ev[0].re, ev[1].re);
    var c = k1 - 1;
    var disc = snap(k2 * k2 - 4 * c);
    var complex = ev[0].im !== 0;
    if (maxRe > EPS) {
      var detail;
      if (complex) detail = "Complex eigenvalues with positive real part: an oscillation that grows.";
      else if (Math.min(ev[0].re, ev[1].re) < -EPS) detail = "One positive and one negative eigenvalue (a saddle): almost every small tilt grows.";
      else if (Math.abs(Math.min(ev[0].re, ev[1].re)) <= EPS) detail = "One eigenvalue at 0 and one positive: the tilt grows.";
      else detail = "Both eigenvalues positive: every small tilt grows.";
      return { kind: "unstable", label: "Unstable", detail: detail };
    }
    if (maxRe < -EPS) {
      var damping = disc < -EPS ? "underdamped: it oscillates while it decays"
        : disc > EPS ? "overdamped: it returns without oscillating" : "critically damped: a double eigenvalue";
      return { kind: "stable", label: "Asymptotically stable",
               detail: "Both eigenvalues have negative real part, so a small tilt decays to zero; " + damping + "." };
    }
    // Largest real part is zero: boundary cases.
    if (Math.abs(c) <= EPS && Math.abs(k2) <= EPS) {
      return { kind: "drift", label: "Boundary: not stable",
               detail: "A double eigenvalue at 0 with a Jordan block. Gravity is exactly cancelled and nothing damps the motion: any velocity (from the initial state or a push) makes the tilt drift linearly." };
    }
    if (Math.abs(c) <= EPS) {
      return { kind: "marginal", label: "Boundary: not asymptotically stable",
               detail: "An eigenvalue at 0 (the other is " + fmt(-k2) + "). The tilt settles to a constant offset instead of returning to 0." };
    }
    return { kind: "marginal", label: "Boundary: not asymptotically stable",
             detail: "Eigenvalues on the imaginary axis, ±" + fmt(Math.sqrt(c)) + "i: an undamped oscillation that neither grows nor decays." };
  }

  function pulseValue(t, pulse) {
    if (!pulse) return 0;
    return t >= pulse.start - 1e-12 && t < pulse.start + pulse.duration - 1e-12 ? pulse.amplitude : 0;
  }

  // Classic RK4 with the disturbance held constant within each step. The step divides the pulse
  // start and duration, so this is the exact piecewise-constant forcing.
  function simulate(k1, k2, theta0, omega0, pulse, tMax, dt) {
    dt = dt || 0.005;
    var n = Math.round(tMax / dt);
    var a = 1 - k1, b = -k2;
    var t = new Array(n + 1), th = new Array(n + 1), om = new Array(n + 1), u = new Array(n + 1);
    var x1 = theta0, x2 = omega0;
    function f1(p, q) { return q; }
    function f2(p, q, d) { return a * p + b * q + d; }
    for (var i = 0; i <= n; i++) {
      var ti = i * dt;
      t[i] = ti; th[i] = x1; om[i] = x2; u[i] = -k1 * x1 - k2 * x2;
      if (i === n) break;
      var d = pulseValue(ti + dt / 2, pulse);
      var p1 = f1(x1, x2), q1 = f2(x1, x2, d);
      var p2 = f1(x1 + dt / 2 * p1, x2 + dt / 2 * q1), q2 = f2(x1 + dt / 2 * p1, x2 + dt / 2 * q1, d);
      var p3 = f1(x1 + dt / 2 * p2, x2 + dt / 2 * q2), q3 = f2(x1 + dt / 2 * p2, x2 + dt / 2 * q2, d);
      var p4 = f1(x1 + dt * p3, x2 + dt * q3), q4 = f2(x1 + dt * p3, x2 + dt * q3, d);
      x1 += dt / 6 * (p1 + 2 * p2 + 2 * p3 + p4);
      x2 += dt / 6 * (q1 + 2 * q2 + 2 * q3 + q4);
      if (!isFinite(x1) || !isFinite(x2) || Math.abs(x1) > 1e12) {
        // Keep the arrays honest: stop where the numbers stop being meaningful.
        t.length = th.length = om.length = u.length = i + 1;
        break;
      }
    }
    return { t: t, theta: th, omega: om, u: u };
  }

  // First time |theta| exceeds `limit`, or null.
  function exitTime(sim, limit) {
    for (var i = 0; i < sim.t.length; i++) if (Math.abs(sim.theta[i]) > limit) return sim.t[i];
    return null;
  }

  function cruise(aTrue, aModel, K, r, d) {
    var open = aTrue * r / aModel + d;
    var closed = (aTrue * K * r + d) / (1 + aTrue * K);
    return { open: open, closed: closed, openError: r - open, closedError: r - closed,
             attenuation: 1 / (1 + aTrue * K) };
  }

  function hill(t, amplitude) { return amplitude * Math.sin(Math.PI * t); }   // 0.5 Hz, as in the book's example

  function fmt(x, digits) {
    if (!isFinite(x)) return x > 0 ? "∞" : "−∞";
    var d = digits === undefined ? 2 : digits;
    var s = Math.abs(x) < 0.5 * Math.pow(10, -d) ? (0).toFixed(d) : x.toFixed(d);
    return s.replace(/^-/, "−");
  }

  var api = { eigenvalues: eigenvalues, closedLoopMatrix: closedLoopMatrix, classify: classify,
              simulate: simulate, exitTime: exitTime, cruise: cruise, hill: hill, fmt: fmt, pulseValue: pulseValue };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ControlMath = api;
})(this);
