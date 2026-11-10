"""ManimGL scenes for Unit 10, Boundary Problems, Fourier Series and PDEs (one scene per sequence).

Colour code: solutions teal, targets white/dim, partial sums yellow, decaying modes pink, results
green. Formulas use matplotlib mathtext (no \\tfrac, \\text, \\Big, standalone \\quad).
Stage bounds: |x| <= 6.3, -2.8 <= y <= 3.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"res": GREEN_C}
PI = np.pi


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


class Axes2(VGroup):
    """Simple axes for x in [x0, x1], y in [y0, y1] mapped into a box (centre, width, height)."""
    def __init__(self, x0, x1, y0, y1, center, w, h, xl="x"):
        self.x0, self.x1, self.y0, self.y1, self.c, self.w, self.h = x0, x1, y0, y1, np.array(center, float), w, h
        parts = [Line(self.p(x0, max(y0, min(0, y1))), self.p(x1, max(y0, min(0, y1)))).set_stroke(DIM, 2)]
        if x0 <= 0 <= x1:
            parts.append(Line(self.p(0, y0), self.p(0, y1)).set_stroke(DIM, 2))
        parts.append(label(xl, 18, DIM).next_to(self.p(x1, max(y0, min(0, y1))), DOWN, buff=0.06))
        super().__init__(*parts)

    def p(self, x, y):
        return self.c + np.array([(x - self.x0) / (self.x1 - self.x0) * self.w - self.w / 2,
                                  (y - self.y0) / (self.y1 - self.y0) * self.h - self.h / 2, 0])

    def graph(self, f, color=TEAL_C, width=4, n=400, x0=None, x1=None):
        x0 = self.x0 if x0 is None else x0
        x1 = self.x1 if x1 is None else x1
        pts = []
        for x in np.linspace(x0, x1, n):
            y = float(f(x))
            y = min(max(y, self.y0), self.y1)
            pts.append(self.p(x, y))
        return VMobject().set_points_as_corners(pts).set_stroke(color, width).set_fill(opacity=0)


# ======================================================================== Section 1

class PointLoadSequence(ControlScene):
    SEQ_ID = "point-load"

    def construct(self):
        A = Axes2(0, 1, -0.05, 0.3, [-2.6, -0.4, 0], 6.4, 4.0)
        a = 0.35
        load = arrow(A.p(a, 0.29), A.p(a, 0.245), color=YELLOW_C)
        ll = label("unit load at a", 20, YELLOW_C).next_to(load, UP, buff=0.05)
        sup = VGroup(Triangle().scale(0.12).move_to(A.p(0, 0) + 0.12 * DOWN).set_fill(DIM, 1).set_stroke(DIM),
                     Triangle().scale(0.12).move_to(A.p(1, 0) + 0.12 * DOWN).set_fill(DIM, 1).set_stroke(DIM))
        eq = M(("e", r"-y'' = \delta(x - a)"), size=0.95).move_to([3.6, 2.6, 0])
        self.start(A, sup, load, ll, eq)

        # 1. lines
        l1 = Line(A.p(0, 0), A.p(a, (1 - a) * a)).set_stroke(TEAL_C, 5)
        l2 = Line(A.p(a, (1 - a) * a), A.p(1, 0)).set_stroke(PINK_C, 5)
        e1 = M(("a", "y = Cx"), ",", ("b", "y = E(1 - x)"), size=0.85, colors={"a": TEAL_C, "b": PINK_C}).move_to([3.6, 1.6, 0])
        self.play(self.chip("no load away from a: straight lines"), ShowCreation(l1), ShowCreation(l2), Write(e1), run_time=1.6)
        self.step_done(A, sup, load, ll, eq, l1, l2, e1)

        # 2. match
        e2 = M(("c", "Ca = E(1 - a)"), size=0.85).move_to([3.6, 0.8, 0])
        e3 = M(("d", "-E - C = -1"), size=0.85, colors={"d": YELLOW_C}).move_to([3.6, 0.15, 0])
        s1 = label("slope 1 − a", 18, TEAL_C).next_to(l1.get_center(), UP, buff=0.15)
        s2 = label("slope −a", 18, PINK_C).next_to(l2.get_center(), UP, buff=0.15)
        self.play(self.chip("continuous; slope drops by 1"), Write(e2), run_time=0.9)
        self.play(Write(e3), FadeIn(s1), FadeIn(s2), run_time=1.0)
        self.step_done(A, sup, load, ll, eq, l1, l2, e1, e2, e3, s1, s2)

        # 3. answer
        e4 = M(("y", "y = (1 - a)x,\\ \\ a(1 - x)"), size=0.9, colors={"y": GREEN_C}).move_to([3.6, -0.8, 0])
        g = label("Green's function: response at x to a load at a", 20, GREEN_C).move_to([3.4, -1.5, 0])
        self.play(self.chip("solve: C = 1 - a, E = a"), Write(e4), FadeIn(g), run_time=1.2)
        self.step_done(A, sup, load, ll, eq, l1, l2, e1, e2, e3, s1, s2, e4, g)


# ======================================================================== Section 2

class HarmonicPatternSequence(ControlScene):
    SEQ_ID = "harmonic-pattern"

    def construct(self):
        e0 = M(("e", "u_{xx} + u_{yy} = 0"), size=1.2).move_to([0, 2.6, 0])
        self.start(e0)

        e1 = M(("p", "(x + iy)^2"), "=", ("r", "(x^2 - y^2)"), "+", ("i", "i(2xy)"), size=1.0, colors={"r": TEAL_C, "i": PINK_C}).move_to([0, 1.5, 0])
        c1 = label("2 − 2 = 0   and   0 + 0 = 0", 20, DIM).move_to([0, 0.95, 0])
        self.play(self.chip("square x + iy"), Write(e1), run_time=1.2)
        self.play(FadeIn(c1), run_time=0.6)
        self.step_done(e0, e1, c1)

        e2 = M(("p", "(x + iy)^3"), "=", ("r", "(x^3 - 3xy^2)"), "+", ("i", "i(3x^2y - y^3)"), size=1.0, colors={"r": TEAL_C, "i": PINK_C}).move_to([0, 0.15, 0])
        c2 = label("real part: 6x − 6x = 0", 20, DIM).move_to([0, -0.4, 0])
        self.play(self.chip("cube"), Write(e2), run_time=1.3)
        self.play(FadeIn(c2), run_time=0.6)
        self.step_done(e0, e1, c1, e2, c2)

        e3 = M(("p", r"(re^{i\theta})^n"), "=", ("r", r"r^n\cos n\theta"), "+", ("i", r"i\,r^n\sin n\theta"), size=1.05,
               colors={"r": TEAL_C, "i": PINK_C}).move_to([0, -1.3, 0])
        c3 = label("two harmonic functions for every n", 22, GREEN_C).move_to([0, -2.1, 0])
        self.play(self.chip("polar form"), Write(e3), run_time=1.2)
        self.play(FadeIn(c3), run_time=0.6)
        self.step_done(e0, e1, c1, e2, c2, e3, c3)


# ======================================================================== Section 3

class OrthogonalitySequence(ControlScene):
    SEQ_ID = "orthogonality"

    def construct(self):
        e0 = M(("f", "f(x)"), "=", ("a0", "a_0"), "+", ("a1", r"a_1\cos x"), "+", ("ak", r"a_k\cos kx"), "+", r"\cdots", "+",
               ("b1", r"b_1\sin x"), "+", r"\cdots", size=0.95, colors={"ak": YELLOW_C}).move_to([0, 2.6, 0])
        self.start(e0)

        # 1. multiply and integrate
        e1 = M(("i", r"\int_{-\pi}^{\pi} f\cos kx\,dx"), "=", ("t0", r"\int a_0\cos kx"), "+", ("t1", r"\int a_1\cos x\cos kx"), "+",
               ("tk", r"\int a_k\cos^2 kx"), "+", r"\cdots", size=0.78, colors={"tk": YELLOW_C}).move_to([0, 1.2, 0])
        self.play(self.chip("multiply by cos kx, integrate"), TransformFromCopy(e0, e1), run_time=1.5)
        self.step_done(e0, e1)

        # 2. orthogonality: plot cos x cos 3x and cos^2 3x
        A1 = Axes2(-PI, PI, -1.1, 1.1, [-3.2, -0.75, 0], 5.0, 1.4)
        A2 = Axes2(-PI, PI, -1.1, 1.1, [3.2, -0.75, 0], 5.0, 1.4)
        g1 = A1.graph(lambda x: np.cos(x) * np.cos(3 * x), PINK_C, 3)
        g2 = A2.graph(lambda x: np.cos(3 * x) ** 2, YELLOW_C, 3)
        t1 = label("cos x · cos 3x: area 0", 20, PINK_C).move_to([-3.2, 0.15, 0])
        t2 = label("cos² 3x: area π", 20, YELLOW_C).move_to([3.2, 0.15, 0])
        x1, x2 = strike(e1.k("t0"), RED_C), strike(e1.k("t1"), RED_C)
        self.play(self.chip("different frequencies average to zero"), FadeIn(A1), FadeIn(A2), ShowCreation(g1), ShowCreation(g2), run_time=1.5)
        self.play(FadeIn(t1), FadeIn(t2), ShowCreation(x1), ShowCreation(x2), run_time=0.9)
        self.step_done(e0, e1, A1, A2, g1, g2, t1, t2, x1, x2)

        # 3. formula
        e3 = M(("a", "a_k"), "=", ("f", r"\frac{1}{\pi}\int_{-\pi}^{\pi} f(x)\cos kx\,dx"), size=1.05, colors={"a": YELLOW_C}).move_to([0, -2.5, 0])
        self.play(self.chip("only pi a_k survives"), Write(e3), run_time=1.2)
        self.play(ShowCreation(hbox(e3, GREEN_C)), run_time=0.5)
        self.step_done(e0, e1, A1, A2, g1, g2, t1, t2, x1, x2, e3, hbox(e3, GREEN_C))


# ======================================================================== Section 4

def sq_partial(x, N):
    return 4 / PI * sum(np.sin(k * x) / k for k in range(1, N + 1, 2))


class SquareWaveSequence(ControlScene):
    SEQ_ID = "square-wave"

    def construct(self):
        A = Axes2(-PI, PI, -1.4, 1.4, [-2.7, -0.2, 0], 6.2, 4.4)
        sw = VGroup(Line(A.p(-PI, -1), A.p(0, -1)), Line(A.p(0, 1), A.p(PI, 1))).set_stroke(DIM, 3)
        self.start(A, sw)

        # 1. one term
        s1 = A.graph(lambda x: sq_partial(x, 1), YELLOW_C, 4)
        e1 = M(("s", r"S_1 = \frac{4}{\pi}\sin x"), size=0.85, colors={"s": YELLOW_C}).move_to([4.4, 2.5, 0])
        self.play(self.chip("b_1 = 4/pi"), ShowCreation(s1), Write(e1), run_time=1.4)
        self.step_done(A, sw, s1, e1)

        # 2. more terms
        s3, s5, s7 = [A.graph(lambda x, N=N: sq_partial(x, N), YELLOW_C, 4) for N in (3, 5, 7)]
        e2 = M(("s", r"S_7 = \frac{4}{\pi}\left(\sin x + \frac{\sin 3x}{3} + \frac{\sin 5x}{5} + \frac{\sin 7x}{7}\right)"), size=0.55, colors={"s": YELLOW_C}).move_to([3.6, 1.7, 0])
        self.play(self.chip("add odd harmonics"), Transform(s1, s3), run_time=0.9)
        self.play(Transform(s1, s5), run_time=0.9)
        self.play(Transform(s1, s7), Write(e2), run_time=1.0)
        self.step_done(A, sw, s1, e1, e2)

        # 3. many terms: Gibbs
        s41 = A.graph(lambda x: sq_partial(x, 41), GREEN_C, 3, n=1600)
        peak = Dot(A.p(PI / 42, sq_partial(PI / 42, 41)), radius=0.07).set_fill(RED_C)
        e3 = label("overshoot ≈ 1.179: about 9% of the jump of 2", 20, RED_C).move_to([3.4, 0.9, 0])
        self.play(self.chip("Gibbs phenomenon"), Transform(s1, s41), run_time=1.3)
        self.play(GrowFromCenter(peak), FadeIn(e3), run_time=0.8)
        self.step_done(A, sw, s1, e1, e2, peak, e3)


# ======================================================================== Section 5

class PoissonDiscSequence(ControlScene):
    SEQ_ID = "poisson-disc"

    def construct(self):
        e0 = M(("d", r"u(1, \theta) = \delta(\theta) = \frac{1}{2\pi} + \frac{1}{\pi}\sum\cos n\theta"), size=0.85).move_to([0, 2.7, 0])
        self.start(e0)

        e1 = M(("u", r"u(r, \theta) = \frac{1}{2\pi} + \frac{1}{\pi}\sum r^n\cos n\theta"), size=0.85, colors={"u": TEAL_C}).move_to([-2.4, 1.6, 0])
        A = Axes2(-PI, PI, -0.2, 2.2, [3.4, 0.6, 0], 5.0, 2.6, xl="θ")
        curves = VGroup(*[A.graph(lambda th, r=r: (1 - r * r) / (2 * PI * (1 + r * r - 2 * r * np.cos(th))), c, 3)
                          for r, c in [(0.2, BLUE_C), (0.5, TEAL_C), (0.75, YELLOW_C)]])
        lab = label("r = 0.2, 0.5, 0.75", 18, DIM).next_to(A, DOWN, buff=0.05)
        self.play(self.chip("damp each cosine by r^n"), Write(e1), FadeIn(A), run_time=1.2)
        self.play(LaggedStart(*[ShowCreation(c) for c in curves], lag_ratio=0.3), FadeIn(lab), run_time=1.5)
        self.step_done(e0, e1, A, curves, lab)

        e2 = M(("g", r"1 + 2\sum (re^{i\theta})^n = \frac{1 + re^{i\theta}}{1 - re^{i\theta}}"), size=0.8).move_to([-2.4, 0.3, 0])
        self.play(self.chip("geometric series"), Write(e2), run_time=1.3)
        self.step_done(e0, e1, A, curves, lab, e2)

        e3 = M(("k", r"u = \frac{1}{2\pi}\frac{1 - r^2}{1 + r^2 - 2r\cos\theta}"), size=1.0, colors={"k": GREEN_C}).move_to([-2.2, -1.2, 0])
        c = label("centre r = 0: 1/(2π), the average of the boundary data", 20, GREEN_C).move_to([0, -2.3, 0])
        self.play(self.chip("take the real part"), Write(e3), run_time=1.2)
        self.play(FadeIn(c), run_time=0.6)
        self.step_done(e0, e1, A, curves, lab, e2, e3, c)


# ======================================================================== Section 6

def heat_one(t, x, K=199):
    return 4 / PI * sum(np.exp(-k * k * PI * PI * t) * np.sin(k * PI * x) / k for k in range(1, K + 1, 2))


class HeatModesSequence(ControlScene):
    SEQ_ID = "heat-modes"

    def construct(self):
        A = Axes2(0, 1, -0.1, 1.35, [-2.6, -0.3, 0], 6.0, 4.2)
        init = Line(A.p(0.002, 1), A.p(0.998, 1)).set_stroke(DIM, 3)
        e0 = M(("e", "u_t = u_{xx},\\ \\ u(0, x) = 1"), size=0.85).move_to([3.4, 2.7, 0])
        self.start(A, init, e0)

        modes = VGroup(*[A.graph(lambda x, k=k: 4 / (PI * k) * np.sin(k * PI * x), c, 3) for k, c in [(1, TEAL_C), (3, PINK_C), (5, YELLOW_C)]])
        e1 = M(("s", r"1 = \frac{4}{\pi}\left(\sin\pi x + \frac{1}{3}\sin 3\pi x + \cdots\right)"), size=0.7).move_to([3.4, 1.8, 0])
        self.play(self.chip("sine series of the start"), LaggedStart(*[ShowCreation(m) for m in modes], lag_ratio=0.3), Write(e1), run_time=1.8)
        self.step_done(A, init, e0, modes, e1)

        curves = VGroup(*[A.graph(lambda x, t=t: heat_one(t, x), c, 3) for t, c in [(0.002, FG), (0.01, YELLOW_C), (0.03, TEAL_C), (0.08, GREEN_C)]])
        e2 = M(("u", r"u = \frac{4}{\pi}\sum_{k\ \mathrm{odd}} \frac{e^{-k^2\pi^2 t}}{k}\sin k\pi x"), size=0.7, colors={"u": TEAL_C}).move_to([3.4, 0.9, 0])
        tl = label("t = 0.002, 0.01, 0.03, 0.08", 18, DIM).move_to([3.4, 0.3, 0])
        self.play(self.chip("each mode decays at k^2 pi^2"), FadeOut(modes), Write(e2), run_time=0.9)
        self.play(LaggedStart(*[ShowCreation(c) for c in curves], lag_ratio=0.3), FadeIn(tl), run_time=2.0)
        self.step_done(A, init, e0, e1, e2, curves, tl)

        e3 = M(("u", r"u \approx \frac{4}{\pi}e^{-\pi^2 t}\sin\pi x"), size=0.85, colors={"u": GREEN_C}).move_to([3.4, -0.6, 0])
        n = label("high modes vanish first: one arch remains", 20, GREEN_C).move_to([3.4, -1.3, 0])
        self.play(self.chip("long times"), Write(e3), FadeIn(n), run_time=1.1)
        self.step_done(A, init, e0, e1, e2, curves, tl, e3, n)


# ======================================================================== Section 7

def tent(x):
    return np.where(x <= PI / 2, x / (PI / 2), (PI - x) / (PI / 2))


def tent_odd(x):
    y = (x + PI) % (2 * PI) - PI
    return np.sign(y) * tent(np.abs(y))


class WaveSplitSequence(ControlScene):
    SEQ_ID = "wave-split"

    def construct(self):
        A = Axes2(0, PI, -1.15, 1.15, [-3.0, -0.2, 0], 5.8, 3.8)
        u0 = A.graph(lambda x: float(tent(x)), DIM, 3)
        e0 = M(("e", "u_{tt} = u_{xx},\\ \\ u_t(0, x) = 0"), size=0.8).move_to([3.9, 2.7, 0])
        self.start(A, u0, e0)

        e1 = M(("d", r"u = \frac{1}{2}u_0(x - t) + \frac{1}{2}u_0(x + t)"), size=0.8, colors={"d": TEAL_C}).move_to([3.9, 1.8, 0])
        halves = VGroup(A.graph(lambda x: 0.5 * float(tent(x)), PINK_C, 3), A.graph(lambda x: 0.5 * float(tent(x)), BLUE_C, 3))
        self.play(self.chip("d'Alembert"), Write(e1), TransformFromCopy(u0, halves[0]), TransformFromCopy(u0, halves[1]), run_time=1.5)
        self.step_done(A, u0, e0, e1, halves)

        def at(t, c, w=4):
            return A.graph(lambda x: 0.5 * float(tent_odd(x - t)) + 0.5 * float(tent_odd(x + t)), c, w)
        right = A.graph(lambda x: 0.5 * float(tent_odd(x - PI / 4)), PINK_C, 3)
        left = A.graph(lambda x: 0.5 * float(tent_odd(x + PI / 4)), BLUE_C, 3)
        s1 = at(PI / 4, TEAL_C)
        s2 = at(PI / 2, YELLOW_C)
        tl = label("t = π/4 (teal), π/2 (yellow)", 18, DIM).move_to([3.9, 1.1, 0])
        self.play(self.chip("halves move apart at speed 1"), Transform(halves[0], right), Transform(halves[1], left), run_time=1.3)
        self.play(ShowCreation(s1), FadeIn(tl), run_time=0.9)
        self.play(ShowCreation(s2), run_time=0.9)
        self.step_done(A, u0, e0, e1, halves, s1, s2, tl)

        e2 = M(("s", r"u = \sum d_n\cos nt\,\sin nx,\ \ d_n = \frac{8}{\pi^2 n^2}\sin\frac{n\pi}{2}"), size=0.66, colors={"s": GREEN_C}).move_to([3.5, 0.2, 0])
        s3 = at(PI, GREEN_C)
        n = label("t = π: the inverted tent", 20, GREEN_C).move_to([3.9, -0.5, 0])
        self.play(self.chip("the sine series agrees"), Write(e2), run_time=1.2)
        self.play(ShowCreation(s3), FadeIn(n), run_time=1.0)
        self.step_done(A, u0, e0, e1, halves, s1, s2, tl, e2, s3, n)
