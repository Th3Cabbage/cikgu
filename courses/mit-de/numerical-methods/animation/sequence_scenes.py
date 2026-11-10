"""ManimGL scenes for Unit 11, Numerical Methods for ODEs (one scene per sequence).

Colour code: exact solutions dim, Euler red/teal steps, stage slopes blue/orange/pink/yellow,
weighted steps green. Formulas use matplotlib mathtext. Stage bounds: |x| <= 6.3, -2.8 <= y <= 3.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"res": GREEN_C}
SC = [BLUE_C, ORANGE_C, PINK_C, YELLOW_C]


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


class Box(VGroup):
    def __init__(self, x0, x1, y0, y1, center, w, h, xl="t", yl="y"):
        self.x0, self.x1, self.y0, self.y1, self.c, self.w, self.h = x0, x1, y0, y1, np.array(center, float), w, h
        parts = [Line(self.p(x0, y0), self.p(x1, y0)).set_stroke(DIM, 2), Line(self.p(x0, y0), self.p(x0, y1)).set_stroke(DIM, 2),
                 label(xl, 18, DIM).next_to(self.p(x1, y0), DOWN, buff=0.06), label(yl, 18, DIM).next_to(self.p(x0, y1), LEFT, buff=0.06)]
        super().__init__(*parts)

    def p(self, x, y):
        return self.c + np.array([(x - self.x0) / (self.x1 - self.x0) * self.w - self.w / 2,
                                  (y - self.y0) / (self.y1 - self.y0) * self.h - self.h / 2, 0])

    def graph(self, f, color, width=3, n=300, dashed=False):
        pts = []
        for x in np.linspace(self.x0, self.x1, n):
            y = float(f(x))
            if y > self.y1:
                break
            pts.append(self.p(x, y))
        m = VMobject().set_points_as_corners(pts).set_stroke(color, width).set_fill(opacity=0)
        return DashedVMobject(m, num_dashes=40) if dashed else m

    def slope(self, t, y, s, length=0.5, color=BLUE_C):
        # a short segment of slope s through (t, y) in scene coordinates
        d = self.p(t + 0.1, y + 0.1 * s) - self.p(t, y)
        d = d / np.linalg.norm(d) * length
        c = self.p(t, y)
        return Line(c - d, c + d).set_stroke(color, 5)


# ======================================================================== Section 1

class EulerStepsSequence(ControlScene):
    SEQ_ID = "euler-steps"

    def construct(self):
        B = Box(0, 3, 0, 450, [-2.5, -0.2, 0], 6.6, 4.6)
        ex = B.graph(lambda t: 10 * np.exp(2 * t), DIM, 3)
        e0 = M(("e", "y' = 2y,\\ \\ y(0) = 10,\\ \\ h = 1"), size=0.85).move_to([3.6, 2.7, 0])
        self.start(B, ex, e0)

        pts = [(0, 10), (1, 30), (2, 90), (3, 270)]
        d0 = Dot(B.p(*pts[0]), radius=0.07).set_fill(TEAL_C)
        seg1 = Line(B.p(*pts[0]), B.p(*pts[1])).set_stroke(RED_C, 4)
        d1 = Dot(B.p(*pts[1]), radius=0.07).set_fill(TEAL_C)
        e1 = M(("a", "s_1 = 20,\\ \\ y_1 = 30"), size=0.85, colors={"a": RED_C}).move_to([3.6, 1.9, 0])
        self.play(self.chip("follow the tangent"), FadeIn(d0), run_time=0.4)
        self.play(ShowCreation(seg1), Write(e1), run_time=1.2)
        self.play(FadeIn(d1), run_time=0.3)
        self.step_done(B, ex, e0, d0, seg1, d1, e1)

        seg2 = Line(B.p(*pts[1]), B.p(*pts[2])).set_stroke(RED_C, 4)
        seg3 = Line(B.p(*pts[2]), B.p(*pts[3])).set_stroke(RED_C, 4)
        d2, d3 = Dot(B.p(*pts[2]), radius=0.07).set_fill(TEAL_C), Dot(B.p(*pts[3]), radius=0.07).set_fill(TEAL_C)
        e2 = M(("a", "y_2 = 90,\\ \\ y_3 = 270"), size=0.85, colors={"a": RED_C}).move_to([3.6, 1.2, 0])
        self.play(self.chip("multiply by 1 + 2h = 3"), ShowCreation(seg2), FadeIn(d2), run_time=1.0)
        self.play(ShowCreation(seg3), FadeIn(d3), Write(e2), run_time=1.1)
        self.step_done(B, ex, e0, d0, seg1, d1, e1, seg2, seg3, d2, d3, e2)

        e3 = M(("x", r"y(3) = 10e^6 \approx 4034"), size=0.85, colors={"x": DIM}).move_to([3.6, 0.3, 0])
        n = label("exact curve leaves the box at t ≈ 1.9", 18, DIM).move_to([3.6, -0.35, 0])
        gap = DashedLine(B.p(1, 30), B.p(1, 10 * np.e ** 2)).set_stroke(YELLOW_C, 3)
        gl = label("error at t = 1: 44", 18, YELLOW_C).next_to(gap, LEFT, buff=0.1)
        self.play(self.chip("compare with the exact solution"), ShowCreation(gap), FadeIn(gl), Write(e3), FadeIn(n), run_time=1.3)
        self.step_done(B, ex, e0, d0, seg1, d1, e1, seg2, seg3, d2, d3, e2, e3, n, gap, gl)


# ======================================================================== Section 2

class RK4StagesSequence(ControlScene):
    SEQ_ID = "rk4-stages"

    def construct(self):
        B = Box(0, 1, 0, 160, [-2.6, -0.3, 0], 6.0, 4.6)
        ex = B.graph(lambda t: 10 * np.exp(2 * t), DIM, 3)
        d0 = Dot(B.p(0, 10), radius=0.07).set_fill(TEAL_C)
        e0 = M(("e", r"y_0 = 10,\ h = 1,\ y(1) \approx 73.9"), size=0.8).move_to([3.6, 2.8, 0])
        self.start(B, ex, d0, e0)

        # 1. midpoint
        s1 = B.slope(0, 10, 20, color=SC[0])
        probe = DashedLine(B.p(0, 10), B.p(0.5, 20)).set_stroke(SC[0], 2)
        mid = Dot(B.p(0.5, 20), radius=0.07).set_fill(SC[1])
        s2 = B.slope(0.5, 20, 40, color=SC[1])
        step = Line(B.p(0, 10), B.p(1, 50)).set_stroke(GREEN_C, 4)
        e1 = M(("m", "s_2 = 40,\\ \\ y_1 = 50"), size=0.8, colors={"m": SC[1]}).move_to([3.6, 2.0, 0])
        self.play(self.chip("Euler half step, then the midpoint slope"), ShowCreation(s1), ShowCreation(probe), FadeIn(mid), run_time=1.1)
        self.play(ShowCreation(s2), run_time=0.6)
        self.play(ShowCreation(step), Write(e1), run_time=1.0)
        self.step_done(B, ex, d0, e0, s1, probe, mid, s2, step, e1)

        # 2. four RK4 slopes
        p3 = Dot(B.p(0.5, 30), radius=0.07).set_fill(SC[2])
        s3 = B.slope(0.5, 30, 60, color=SC[2])
        p4 = Dot(B.p(1, 70), radius=0.07).set_fill(SC[3])
        s4 = B.slope(1, 70, 140, color=SC[3])
        pr3 = DashedLine(B.p(0, 10), B.p(0.5, 30)).set_stroke(SC[1], 2)
        pr4 = DashedLine(B.p(0, 10), B.p(1, 70)).set_stroke(SC[2], 2)
        e2 = M(("a", "s_1 = 20"), ",", ("b", "s_2 = 40"), ",", ("c", "s_3 = 60"), ",", ("d", "s_4 = 140"), size=0.75,
               colors={"a": SC[0], "b": SC[1], "c": SC[2], "d": SC[3]}).move_to([3.6, 1.2, 0])
        self.play(self.chip("start, midpoint, midpoint, end"), FadeOut(step), ShowCreation(pr3), FadeIn(p3), ShowCreation(s3), run_time=1.1)
        self.play(ShowCreation(pr4), FadeIn(p4), ShowCreation(s4), Write(e2), run_time=1.2)
        self.step_done(B, ex, d0, e0, s1, probe, mid, s2, e1, p3, s3, p4, s4, pr3, pr4, e2)

        # 3. weighted step
        rk = Line(B.p(0, 10), B.p(1, 70)).set_stroke(GREEN_C, 6)
        e3 = M(("r", r"y_1 = 10 + \frac{1}{6}(20 + 80 + 120 + 140) = 70"), size=0.75, colors={"r": GREEN_C}).move_to([3.4, 0.3, 0])
        cmp = label("Euler 30 · midpoint 50 · RK4 70 · exact 73.9", 20, GREEN_C).move_to([3.4, -0.5, 0])
        self.play(self.chip("weights 1, 2, 2, 1"), ShowCreation(rk), Write(e3), run_time=1.3)
        self.play(FadeIn(cmp), run_time=0.6)
        self.step_done(B, ex, d0, e0, s1, mid, s2, e1, p3, s3, p4, s4, e2, rk, e3, cmp)


# ======================================================================== Section 3

class OrderPlotSequence(ControlScene):
    SEQ_ID = "order-plot"

    def construct(self):
        B = Box(np.log2(0.04), np.log2(0.12), -26, -2, [-2.4, -0.3, 0], 6.0, 4.6, xl="log₂ h", yl="log₂ error")
        e0 = M(("e", r"\int_0^1 \frac{dt}{(1+t)^2} = \frac{1}{2}"), size=0.85).move_to([3.6, 2.7, 0])
        self.start(B, e0)

        data = [("ODE1", 0.5389551274648263, 0.5191143818782419, RED_C),
                ("ODE2", 0.4992736362916574, 0.49981788457208504, YELLOW_C),
                ("ODE4", None, None, GREEN_C)]
        # RK4 on y' = f(t) is Simpson's rule: compute its errors
        f = lambda t: 1 / (1 + t) ** 2
        def simpson(h):
            n = int(round(1 / h)); return sum(h / 6 * (f(i * h) + 4 * f(i * h + h / 2) + f(i * h + h)) for i in range(n))
        data[2] = ("ODE4", simpson(0.1), simpson(0.05), GREEN_C)
        texts = [r"0.5390,\ 0.5191:\ \mathrm{ratio} \approx 2,\ p = 1", r"0.49927,\ 0.49982:\ \mathrm{ratio} \approx 4,\ p = 2",
                 r"\mathrm{ratio} \approx 16,\ p = 4"]
        groups = []
        for k, ((name, v1, v2, c), tx) in enumerate(zip(data, texts)):
            a = B.p(np.log2(0.1), np.log2(abs(v1 - 0.5)))
            b = B.p(np.log2(0.05), np.log2(abs(v2 - 0.5)))
            ln = Line(a, b).set_stroke(c, 5)
            dots = VGroup(Dot(a, radius=0.08).set_fill(c), Dot(b, radius=0.08).set_fill(c))
            lab = label(name, 20, c).next_to(a, RIGHT, buff=0.15)
            e = M(("t", tx), size=0.75, colors={"t": c}).move_to([3.6, 1.8 - 0.8 * k, 0])
            self.play(self.chip(f"{name}: errors at h = 0.1 and 0.05"), FadeIn(dots), ShowCreation(ln), FadeIn(lab), Write(e), run_time=1.4)
            groups += [ln, dots, lab, e]
            self.step_done(B, e0, *groups)


# ======================================================================== Section 4

class BS23ControlSequence(ControlScene):
    SEQ_ID = "bs23-control"

    def construct(self):
        # one BS23 step for y' = y from y = 1 with h = 0.1, drawn with a magnified vertical scale
        B = Box(0, 0.1, 1.0, 1.11, [-2.8, -0.2, 0], 5.6, 4.4)
        ex = B.graph(lambda t: np.exp(t), DIM, 3)
        h = 0.1
        s1 = 1.0
        y2 = 1 + h / 2 * s1
        s2 = y2
        y3 = 1 + 3 * h / 4 * s2
        s3 = y3
        yn = 1 + h / 9 * (2 * s1 + 3 * s2 + 4 * s3)
        s4 = yn
        d0 = Dot(B.p(0, 1), radius=0.07).set_fill(TEAL_C)
        e0 = M(("e", r"y' = y,\ \ y_0 = 1,\ \ h = 0.1"), size=0.8).move_to([3.5, 2.8, 0])
        st = VGroup(B.slope(0, 1, s1, color=SC[0]), Dot(B.p(h / 2, y2), radius=0.07).set_fill(SC[1]), B.slope(h / 2, y2, s2, color=SC[1]),
                    Dot(B.p(3 * h / 4, y3), radius=0.07).set_fill(SC[2]), B.slope(3 * h / 4, y3, s3, color=SC[2]))
        self.start(B, ex, d0, e0, st)

        # 1. step and s4
        stp = Line(B.p(0, 1), B.p(h, yn)).set_stroke(GREEN_C, 5)
        dn = Dot(B.p(h, yn), radius=0.08).set_fill(GREEN_C)
        s4m = B.slope(h, yn, s4, color=SC[3])
        e1 = M(("y", r"y_1 = 1.1051667"), ",", ("s", "s_4 = f(t_1, y_1)"), size=0.75, colors={"y": GREEN_C, "s": SC[3]}).move_to([3.5, 2.0, 0])
        self.play(self.chip("third-order step, then one more slope"), ShowCreation(stp), FadeIn(dn), run_time=1.1)
        self.play(ShowCreation(s4m), Write(e1), run_time=1.0)
        self.step_done(B, ex, d0, e0, st, stp, dn, s4m, e1)

        # 2. error estimate
        e = h / 72 * (-5 * s1 + 6 * s2 + 8 * s3 - 9 * s4)
        e2 = M(("e", r"e = \frac{h}{72}(-5s_1 + 6s_2 + 8s_3 - 9s_4) \approx -2.3\times10^{-5}"), size=0.58).move_to([3.2, 1.2, 0])
        self.play(self.chip("difference of two orders"), Write(e2), run_time=1.3)
        self.step_done(B, ex, d0, e0, st, stp, dn, s4m, e1, e2)

        # 3. gauge on a log scale from 1e-7 to 1e-1
        gx0, gx1, gy = 1.1, 6.1, -0.3

        def gp(v):
            return np.array([gx0 + (np.log10(v) + 7) / 6 * (gx1 - gx0), gy, 0])
        xe = gp(abs(e) / yn)[0]
        bar = Rectangle(width=xe - gx0, height=0.3).set_fill(GREEN_C, 0.8).set_stroke(width=0)
        bar.move_to([(gx0 + xe) / 2, gy, 0])
        axis = Line([gx0, gy - 0.2, 0], [gx1, gy - 0.2, 0]).set_stroke(DIM, 2)
        tol = Line(gp(1e-3) + 0.35 * UP, gp(1e-3) + 0.35 * DOWN).set_stroke(RED_C, 4)
        tl = label("tol = 10^-3", 18, RED_C).next_to(tol, UP, buff=0.05)
        el = label("error / |y| ≈ 2×10^-5", 18, GREEN_C).next_to(bar, DOWN, buff=0.3)
        acc = label("accepted; next h = h·min(5, 0.8(tol/err)^(1/3)), capped at hmax", 18, GREEN_C).move_to([2.8, -1.5, 0])
        self.play(self.chip("compare with the tolerance"), FadeIn(axis), FadeIn(bar), ShowCreation(tol), FadeIn(tl), FadeIn(el), run_time=1.3)
        self.play(FadeIn(acc), run_time=0.7)
        self.step_done(B, ex, d0, e0, st, stp, dn, s4m, e1, e2, axis, bar, tol, tl, el, acc)


# ======================================================================== Section 5

class StiffEulerSequence(ControlScene):
    SEQ_ID = "stiff-euler"

    def construct(self):
        B = Box(0, 0.2, -70, 70, [-2.6, -0.2, 0], 6.0, 4.6)
        zero = Line(B.p(0, 0), B.p(0.2, 0)).set_stroke(DIM, 2)
        ex = B.graph(lambda t: np.exp(-100 * t), DIM, 3)
        e0 = M(("e", r"y' = -100y,\ \ h = 0.05"), size=0.85).move_to([3.5, 2.8, 0])
        self.start(B, zero, ex, e0)

        ts = [0, 0.05, 0.1, 0.15]
        ye = [1, -4, 16, -64]
        pts = [B.p(t, y) for t, y in zip(ts, ye)]
        eu = VMobject().set_points_as_corners(pts).set_stroke(RED_C, 4)
        dots = VGroup(*[Dot(p, radius=0.07).set_fill(RED_C) for p in pts])
        e1 = M(("a", r"(1 - 100h) = -4:\ 1, -4, 16, -64"), size=0.75, colors={"a": RED_C}).move_to([3.5, 1.9, 0])
        self.play(self.chip("explicit Euler"), ShowCreation(eu), FadeIn(dots), Write(e1), run_time=1.8)
        self.step_done(B, zero, ex, e0, eu, dots, e1)

        yb = [1, 1 / 6, 1 / 36, 1 / 216]
        bp = [B.p(t, y) for t, y in zip(ts, yb)]
        be = VMobject().set_points_as_corners(bp).set_stroke(GREEN_C, 5)
        bd = VGroup(*[Dot(p, radius=0.07).set_fill(GREEN_C) for p in bp])
        e2 = M(("b", r"y_{n+1} = \frac{y_n}{1 + 100h} = \frac{y_n}{6}"), size=0.8, colors={"b": GREEN_C}).move_to([3.5, 1.0, 0])
        self.play(self.chip("backward Euler: slope at the end"), ShowCreation(be), FadeIn(bd), Write(e2), run_time=1.5)
        self.step_done(B, zero, ex, e0, eu, dots, e1, be, bd, e2)

        e3 = M(("c", r"|1 + h\lambda| \leq 1 \Leftrightarrow h \leq \frac{2}{100} = 0.02"), size=0.8, colors={"c": YELLOW_C}).move_to([3.5, 0.0, 0])
        n = label("stability, not accuracy, limits the explicit step", 20, YELLOW_C).move_to([3.5, -0.7, 0])
        self.play(self.chip("the stability limit"), Write(e3), FadeIn(n), run_time=1.2)
        self.step_done(B, zero, ex, e0, eu, dots, e1, be, bd, e2, e3, n)


# ======================================================================== Section 6

class OscillatorDriftSequence(ControlScene):
    SEQ_ID = "oscillator-drift"

    def construct(self):
        c = np.array([-2.6, -0.2, 0])
        u = 1.3
        ax = VGroup(Line(c + 2.4 * LEFT, c + 2.4 * RIGHT).set_stroke(DIM, 2), Line(c + 2.4 * DOWN, c + 2.4 * UP).set_stroke(DIM, 2))
        e0 = M(("e", r"y_1' = y_2,\ \ y_2' = -y_1"), size=0.85).move_to([3.5, 2.8, 0])
        self.start(ax, e0)

        def P(y1, y2):
            return c + u * np.array([y1, y2, 0])
        circ = VMobject().set_points_as_corners([P(np.sin(t), np.cos(t)) for t in np.linspace(0, 2 * np.pi, 200)]).set_stroke(DIM, 3)
        e1 = M(("a", r"y = (\sin t, \cos t)"), size=0.8).move_to([3.5, 2.0, 0])
        self.play(self.chip("exact solution: the unit circle"), ShowCreation(circ), Write(e1), run_time=1.4)
        self.step_done(ax, e0, circ, e1)

        h = 2 * np.pi / 36
        y = np.array([0.0, 1.0])
        pts = [P(*y)]
        for _ in range(36):
            y = y + h * np.array([y[1], -y[0]])
            pts.append(P(*y))
        eu = VMobject().set_points_as_corners(pts).set_stroke(RED_C, 3)
        e2 = M(("b", r"r_{n+1}^2 = (1 + h^2)\,r_n^2"), size=0.8, colors={"b": RED_C}).move_to([3.5, 1.2, 0])
        n2 = label("after one turn: r = %.2f" % np.hypot(*y), 20, RED_C).move_to([3.5, 0.55, 0])
        self.play(self.chip("Euler spirals outward"), ShowCreation(eu), Write(e2), run_time=2.0)
        self.play(FadeIn(n2), run_time=0.5)
        self.step_done(ax, e0, circ, e1, eu, e2, n2)

        y = np.array([0.0, 1.0])
        pts = [P(*y)]

        def f(v):
            return np.array([v[1], -v[0]])
        for _ in range(36):
            k1 = f(y)
            k2 = f(y + h / 2 * k1)
            k3 = f(y + h / 2 * k2)
            k4 = f(y + h * k3)
            y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            pts.append(P(*y))
        rk = VMobject().set_points_as_corners(pts).set_stroke(GREEN_C, 4)
        e3 = M(("c", r"\mathrm{RK4}:\ |r - 1| < 10^{-5}"), size=0.8, colors={"c": GREEN_C}).move_to([3.5, -0.3, 0])
        self.play(self.chip("RK4 with the same h"), ShowCreation(rk), Write(e3), run_time=1.8)
        self.step_done(ax, e0, circ, e1, eu, e2, n2, rk, e3)
