"""ManimGL scenes for Unit 12, Tumbling Box, Predator-Prey and Chaos (one scene per sequence).

Colour code: x green, y red (the unstable middle axis), z blue; prey teal, predators orange;
two Lorenz runs teal and orange. Stage bounds: |x| <= 6.3, -2.8 <= y <= 3.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403
from scipy.integrate import solve_ivp  # noqa: E402

CHIP["diagram"] = ("PICTURE", PINK_C)
COL = {"res": GREEN_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


class Box(VGroup):
    def __init__(self, x0, x1, y0, y1, center, w, h, xl="t", yl=""):
        self.x0, self.x1, self.y0, self.y1, self.c, self.w, self.h = x0, x1, y0, y1, np.array(center, float), w, h
        super().__init__(Rectangle(width=w, height=h).move_to(self.c).set_stroke(FAINT, 1.5),
                         label(xl, 18, DIM).next_to(self.c + np.array([w / 2, -h / 2, 0]), DOWN, buff=0.05),
                         label(yl, 18, DIM).next_to(self.c + np.array([-w / 2, h / 2, 0]), UP, buff=0.05))

    def p(self, x, y):
        return self.c + np.array([(x - self.x0) / (self.x1 - self.x0) * self.w - self.w / 2,
                                  (y - self.y0) / (self.y1 - self.y0) * self.h - self.h / 2, 0])

    def line(self, xs, ys, color, width=3):
        return VMobject().set_points_as_corners([self.p(x, y) for x, y in zip(xs, ys)]).set_stroke(color, width).set_fill(opacity=0)


def box_rhs(t, y):
    return [y[1] * y[2], -2 * y[0] * y[2], y[0] * y[1]]


def box_run(axis, size=0.1, T=20):
    e = {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}[axis]
    v = np.array(e, float) + size * np.array([0.6, -0.5, 0.62])
    v /= np.linalg.norm(v)
    ts = np.linspace(0, T, 800)
    return ts, solve_ivp(box_rhs, (0, T), v, t_eval=ts, rtol=1e-10, atol=1e-12).y


class BoxAxesSequence(ControlScene):
    SEQ_ID = "box-axes"

    def construct(self):
        eq = M(("e", "x' = yz,\\ \\ y' = -2xz,\\ \\ z' = xy"), size=0.9).move_to([0, 2.9, 0])
        self.start(eq)
        rows = []
        for k, (axis, title) in enumerate([("x", "start near the short axis (x)"), ("z", "start near the long axis (z)"), ("y", "start near the middle axis (y)")]):
            B = Box(0, 20, -1.1, 1.1, [-0.6, 1.55 - 1.55 * k, 0], 8.6, 1.15, xl="t")
            ts, Y = box_run(axis)
            lines = VGroup(B.line(ts, Y[0], GREEN_C), B.line(ts, Y[1], RED_C), B.line(ts, Y[2], BLUE_C))
            tl = label(title, 20, YELLOW_C if axis == "y" else FG).move_to([-0.6, 2.28 - 1.55 * k, 0])
            note = label(["steady: x ≈ 1", "steady: z ≈ 1", "flips: y from +1 to −1"][k], 20, RED_C if axis == "y" else GREEN_C).move_to([5.0, 1.55 - 1.55 * k, 0])
            self.play(self.chip(title), FadeIn(B), FadeIn(tl), run_time=0.6)
            self.play(ShowCreation(lines), run_time=1.6)
            self.play(FadeIn(note), run_time=0.4)
            rows += [B, lines, tl, note]
            self.step_done(eq, *rows)


class PredPreyCycleSequence(ControlScene):
    SEQ_ID = "predprey-cycle"

    def construct(self):
        eq = M(("e", r"y_1' = y_1\left(1 - \frac{y_2}{200}\right),\ \ y_2' = -y_2\left(1 - \frac{y_1}{300}\right)"), size=0.8).move_to([0, 2.9, 0])
        self.start(eq)
        f = lambda t, y: [y[0] * (1 - y[1] / 200), -y[1] * (1 - y[0] / 300)]
        ts = np.linspace(0, 13, 1200)
        Y = solve_ivp(f, (0, 13), [400, 100], t_eval=ts, rtol=1e-10, atol=1e-10).y

        B = Box(0, 13, 50, 650, [-3.0, -0.2, 0], 5.6, 3.8, xl="t", yl="populations")
        prey, pred = B.line(ts, Y[0], TEAL_C), B.line(ts, Y[1], ORANGE_C)
        lg = VGroup(label("prey y₁", 18, TEAL_C), label("predators y₂", 18, ORANGE_C)).arrange(RIGHT, buff=0.4).next_to(B, DOWN, buff=0.35)
        self.play(self.chip("prey peak first, predators follow"), FadeIn(B), FadeIn(lg), run_time=0.6)
        self.play(ShowCreation(prey), ShowCreation(pred), run_time=2.0)
        self.step_done(eq, B, prey, pred, lg)

        Q = Box(100, 620, 60, 400, [3.4, -0.2, 0], 4.2, 3.8, xl="y₁", yl="y₂")
        orb = Q.line(Y[0], Y[1], TEAL_C, 4)
        cp = Dot(Q.p(300, 200), radius=0.08).set_fill(GREEN_C)
        cl = label("(300, 200)", 18, GREEN_C).next_to(cp, UR, buff=0.05)
        self.play(self.chip("phase plane"), FadeIn(Q), GrowFromCenter(cp), FadeIn(cl), run_time=0.7)
        self.play(ShowCreation(orb), run_time=2.0)
        self.step_done(eq, B, prey, pred, lg, Q, orb, cp, cl)

        h = M(("h", r"H = \ln y_1 - \frac{y_1}{300} + \ln y_2 - \frac{y_2}{200}"), size=0.7, colors={"h": GREEN_C}).move_to([3.3, 2.15, 0])
        T = label("conserved: the orbit closes; period ≈ 6.5 (2π for small orbits)", 18, GREEN_C).move_to([3.3, -2.5, 0])
        self.play(self.chip("a conserved quantity"), Write(h), FadeIn(T), run_time=1.2)
        self.step_done(eq, B, prey, pred, lg, Q, orb, cp, cl, h, T)


class LorenzButterflySequence(ControlScene):
    SEQ_ID = "lorenz-butterfly"

    def construct(self):
        eq = M(("e", r"x' = 10(y - x),\ \ y' = 28x - y - xz,\ \ z' = xy - \frac{8}{3}z"), size=0.75).move_to([0, 2.95, 0])
        self.start(eq)
        f = lambda t, y: [10 * (y[1] - y[0]), 28 * y[0] - y[1] - y[0] * y[2], y[0] * y[1] - 8 / 3 * y[2]]
        e = np.sqrt(8 / 3 * 27)
        y0 = np.array([e + 3, e + 2, 27 - 4])
        ts = np.linspace(0, 30, 6000)
        A = solve_ivp(f, (0, 30), y0, t_eval=ts, rtol=1e-11, atol=1e-11).y
        Bv = solve_ivp(f, (0, 30), y0 + np.array([1e-6, 0, 0]), t_eval=ts, rtol=1e-11, atol=1e-11).y

        P = Box(-20, 20, 0, 50, [-2.6, -0.3, 0], 5.6, 4.9, xl="x", yl="z")
        a = P.line(A[0], A[2], TEAL_C, 1.6)
        cps = VGroup(Dot(P.p(e, 27), radius=0.07).set_fill(GREEN_C), Dot(P.p(-e, 27), radius=0.07).set_fill(GREEN_C))
        self.play(self.chip("x-z projection"), FadeIn(P), FadeIn(cps), run_time=0.6)
        self.play(ShowCreation(a), run_time=3.0)
        self.step_done(eq, P, a, cps)

        Q = Box(0, 30, -20, 20, [3.6, 0.7, 0], 4.8, 2.4, xl="t", yl="x")
        xa, xb = Q.line(ts, A[0], TEAL_C, 2), Q.line(ts, Bv[0], ORANGE_C, 2)
        n = label("orange: start moved by 10⁻⁶", 18, ORANGE_C).next_to(Q, DOWN, buff=0.3)
        self.play(self.chip("two starts 1e-6 apart"), FadeIn(Q), FadeIn(n), run_time=0.6)
        self.play(ShowCreation(xa), ShowCreation(xb), run_time=2.5)
        self.step_done(eq, P, a, cps, Q, xa, xb, n)

        d = np.linalg.norm(A - Bv, axis=0)
        sep = ts[np.argmax(d > 1)]
        mark = DashedLine(Q.p(sep, -20), Q.p(sep, 20)).set_stroke(RED_C, 3)
        ml = label("they part at t ≈ %.0f" % sep, 20, RED_C).move_to([3.6, -1.8, 0])
        self.play(self.chip("sensitive dependence"), ShowCreation(mark), FadeIn(ml), run_time=1.0)
        self.step_done(eq, P, a, cps, Q, xa, xb, n, mark, ml)
