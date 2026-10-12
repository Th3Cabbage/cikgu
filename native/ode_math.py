"""Exact solutions of the constant-coefficient homogeneous IVP

    a y'' + b y' + c y = 0,   y(0) = y0,   y'(0) = v0.

Pure Python (standard library only). The JavaScript twin is
browser/dist/ode_math.js; both expose solution(t, a, b, c, y0, v0) with the
same argument order and the same formulas.

With alpha = -b/(2a), k = v0 - alpha*y0 and Delta = b^2 - 4ac:
    Delta > 0:  y = e^(alpha t) [y0 cosh(q t) + k sinh(q t)/q],   q = sqrt(Delta)/(2|a|)
    Delta = 0:  y = e^(alpha t) (y0 + k t)
    Delta < 0:  y = e^(alpha t) [y0 cos(w t) + k sin(w t)/w],     w = sqrt(-Delta)/(2|a|)
(cosh, sinh(x)/x, cos and sin(x)/x are even, so |a| also covers a < 0.)
"""

import math

T_MAX = 8.0
# |Delta| below this fraction of max(b^2, |4ac|) counts as a repeated root. That changes
# the labels AND the formula: in that band solution()/derivative() use the repeated-root
# form e^(alpha t)(y0 + k t) instead of the exact near-critical cosh/sinh or cos/sin form.
# That is a small approximation, O(q^2 t^2) relative with q, w ~ sqrt(|Delta|)/(2|a|),
# because the formulas are continuous across Delta = 0. Over the lab ranges at the band
# edge, the worst case against a 40-digit mpmath evaluation of the exact formula is 3.0e-9
# absolute (4.6e-7 relative where |y| > 1e-6; qa/scratch/band_error.py). Codex's
# independent SciPy DOP853 check found a max abs error of about 2.1e-9.
CRITICAL_REL_TOL = 1e-9
NICE_BOUNDS = (1, 1.5, 2, 3, 4, 5, 6, 8, 10)


def _validate(values, names):
    for value, name in zip(values, names):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a real number")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")


def _check_coefficients(a, b, c):
    _validate((a, b, c), ("a", "b", "c"))
    if a == 0:
        raise ValueError("a must be nonzero (otherwise the equation is not second order)")


def discriminant(a, b, c):
    _check_coefficients(a, b, c)
    return b * b - 4 * a * c


def is_repeated(a, b, c):
    delta = discriminant(a, b, c)
    scale = max(b * b, abs(4 * a * c))
    return abs(delta) <= CRITICAL_REL_TOL * scale


def _parts(t, a, b, c, y0, v0):
    """Return (case, alpha, rate, y, dy) at time t."""
    _check_coefficients(a, b, c)
    _validate((t, y0, v0), ("t", "y0", "v0"))
    alpha = -b / (2 * a)
    k = v0 - alpha * y0
    delta = b * b - 4 * a * c
    if is_repeated(a, b, c):
        e = math.exp(alpha * t)
        y = e * (y0 + k * t)
        dy = e * (alpha * (y0 + k * t) + k)
        return "repeated", alpha, 0.0, y, dy
    if delta > 0:
        q = math.sqrt(delta) / (2 * abs(a))
        e_plus = math.exp((alpha + q) * t)
        e_minus = math.exp((alpha - q) * t)
        ch = 0.5 * (e_plus + e_minus)          # e^(alpha t) cosh(q t)
        if abs(q * t) < 0.5:
            sh_q = math.exp(alpha * t) * math.sinh(q * t) / q   # no cancellation for small q t
        else:
            sh_q = 0.5 * (e_plus - e_minus) / q                 # e^(alpha t) sinh(q t) / q
        y = y0 * ch + k * sh_q
        dy = alpha * y + y0 * q * q * sh_q + k * ch
        return "distinct", alpha, q, y, dy
    w = math.sqrt(-delta) / (2 * abs(a))
    e = math.exp(alpha * t)
    cs, sn = math.cos(w * t), math.sin(w * t)
    y = e * (y0 * cs + k * sn / w)
    dy = alpha * y + e * (-y0 * w * sn + k * cs)
    return "complex", alpha, w, y, dy


def solution(t, a, b, c, y0, v0):
    """y(t) for a y'' + b y' + c y = 0, y(0) = y0, y'(0) = v0."""
    return float(_parts(t, a, b, c, y0, v0)[3])


def derivative(t, a, b, c, y0, v0):
    """y'(t) for the same initial value problem."""
    return float(_parts(t, a, b, c, y0, v0)[4])


def analyze(a, b, c):
    """Roots and classification of a r^2 + b r + c = 0.

    Returns a dict with delta, case ('distinct' | 'repeated' | 'complex'),
    alpha, rate (q or omega), roots [(re, im), (re, im)] and damping
    ('undamped' | 'underdamped' | 'critical' | 'overdamped' for the lab
    region a > 0, c > 0, b >= 0, otherwise 'outside lab').
    """
    _check_coefficients(a, b, c)
    delta = b * b - 4 * a * c
    alpha = -b / (2 * a)
    if is_repeated(a, b, c):
        case, rate, roots = "repeated", 0.0, [(alpha, 0.0), (alpha, 0.0)]
    elif delta > 0:
        rate = math.sqrt(delta) / (2 * abs(a))
        case, roots = "distinct", [(alpha + rate, 0.0), (alpha - rate, 0.0)]
    else:
        rate = math.sqrt(-delta) / (2 * abs(a))
        case, roots = "complex", [(alpha, rate), (alpha, -rate)]
    if not (a > 0 and c > 0 and b >= 0):
        damping = "outside lab"
    elif b == 0:
        damping = "undamped"
    else:
        damping = {"complex": "underdamped", "repeated": "critical", "distinct": "overdamped"}[case]
    return {"delta": delta, "case": case, "alpha": alpha, "rate": rate,
            "roots": roots, "damping": damping}


def fmt(x):
    """Two-decimal label text, identical to ODEMath.fmt in JavaScript (no '-0.00')."""
    n = math.floor(abs(x) * 100 + 0.5)
    return ("-" if n != 0 and x < 0 else "") + f"{n / 100:.2f}"


def roots_text(a, b, c):
    info = analyze(a, b, c)
    (r1, i1), (r2, _) = info["roots"]
    if info["case"] == "complex":
        if fmt(r1) == "0.00":
            return f"r = ±{fmt(i1)}i"
        return f"r = {fmt(r1)} ± {fmt(i1)}i"
    if info["case"] == "repeated":
        return f"r = {fmt(r1)} (double)"
    return f"r₁ = {fmt(r1)},  r₂ = {fmt(r2)}"


DAMPING_LABELS = {
    "undamped": "Undamped (b = 0): purely imaginary roots, steady oscillation",
    "underdamped": "Underdamped: complex roots, decaying oscillation",
    "critical": "Critically damped: repeated real root",
    "overdamped": "Overdamped: two distinct negative real roots",
    "outside lab": "Outside the lab region (needs a > 0, c > 0, b >= 0)",
}


def damping_text(a, b, c):
    return DAMPING_LABELS[analyze(a, b, c)["damping"]]


def nice_bound(max_abs):
    """Symmetric plot half-height: a 'nice' value >= 1.1 * max_abs, never below 1."""
    target = 1.1 * max_abs
    if not math.isfinite(target) or target <= 1:
        return 1.0
    scale = 10 ** math.floor(math.log10(target))
    for m in NICE_BOUNDS:
        if m * scale >= target - 1e-12:
            return float(m * scale)
    return float(10 * scale)


def sample(a, b, c, y0, v0, t_max=T_MAX, n=400):
    """n + 1 evenly spaced (t, y) points on [0, t_max]."""
    return [(t_max * i / n, solution(t_max * i / n, a, b, c, y0, v0)) for i in range(n + 1)]
