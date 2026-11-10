"""ManimGL scenes for Unit 2, Nonlinear First Order Equations (one scene per sequence in control_specs).

Colour code: y teal, z yellow, the competition term and unstable states red, stable states and
results green, slopes/tangents yellow, t-side of a separated equation blue.
Stage bounds: content stays within |x| <= 6.3 and -2.8 <= y <= 3.3 (chip sits bottom-left).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"y": TEAL_C, "y2": RED_C, "z": YELLOW_C, "zp": YELLOW_C, "t": BLUE_C, "dt": BLUE_C, "res": GREEN_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def note(text, y, color=DIM, size=24, x=0.0):
    return label(text, size, color).move_to([x, y, 0])


class XPlot(Plot):
    """Plot whose horizontal variable runs over [x0, x1] (Plot itself starts at 0)."""
    def __init__(self, x0, x1, y_min, y_max, width, height, x_label="y", y_label=None):
        self.x0 = x0
        super().__init__(t_max=x1 - x0, y_min=y_min, y_max=y_max, width=width, height=height,
                         t_label=x_label, y_label=y_label)
        # dim the left frame axis; draw the true vertical axis x = 0 if it is inside
        self[3].set_stroke(FAINT, 1)
        if x0 < 0 < x1:
            self.add(Line(self.xp(0, y_min), self.xp(0, y_max)).set_stroke(DIM, 2))

    def xp(self, x, y):
        return self.c2p(x - self.x0, y)

    def xcurve(self, f, color=TEAL_C, width=4, n=240):
        """Draw only the pieces of the graph inside the y-range (clipped at the frame)."""
        x1 = self.x0 + self.t_max
        segs, cur = [], []
        for x in np.linspace(self.x0, x1, n):
            y = float(f(x))
            if np.isfinite(y) and self.y_min <= y <= self.y_max:
                cur.append(self.xp(x, y))
            elif cur:
                segs.append(cur)
                cur = []
        if cur:
            segs.append(cur)
        g = VGroup()
        for s in segs:
            if len(s) > 1:
                g.add(VMobject().set_points_as_corners(s).set_stroke(color, width).set_fill(opacity=0))
        return g


# ======================================================================== Section 1

class LogisticZSequence(ControlScene):
    SEQ_ID = "logistic-z"

    def construct(self):
        e0 = M(("yp", "y'"), "=", ("a", "a"), ("y", "y"), "-", ("b", "b"), ("y2", "y^2"), size=1.3,
               colors={"yp": TEAL_C}).move_to([0, 2.6, 0])
        tag = note("growth  minus  competition", 1.75)
        self.start(e0, tag)

        # 1. chain rule
        d = M(("z", "z"), "=", ("inv", r"\frac{1}{y}"), r"\quad\Rightarrow\quad", ("zp", "z'"), "=",
              ("minus", "-"), ("frac", r"\frac{y'}{y^2}"), size=1.15).move_to([0, 1.0, 0])
        self.play(self.chip("z = 1/y"), FadeOut(tag), run_time=0.5)
        self.play(FadeIn(d.ks("z", "=")), Write(d.k("inv")), run_time=0.9)
        self.play(FadeIn(d.k(r"\quad\Rightarrow\quad")), FadeIn(d.ks("zp")), FadeIn(d.all("=")[1]),
                  FadeIn(d.k("minus")), TransformFromCopy(d.k("inv"), d.k("frac")), run_time=1.2)
        self.play(Indicate(d.k("frac"), color=YELLOW_C), run_time=0.7)
        self.step_done(e0, d)

        # 2. substitute y' and divide each term by y^2
        s1 = M(("zp", "z'"), "=", "-", ("num", r"\frac{a y - b y^2}{y^2}"), size=1.1).move_to([-3.2, -0.5, 0])
        s2 = M("=", "-", ("ay", r"\frac{a}{y}"), "+", ("b", "b"), size=1.1).next_to(s1, RIGHT, buff=0.25)
        s3 = M("=", ("m", "-a"), ("z", "z"), "+", ("b", "b"), size=1.1, colors={"z": YELLOW_C}).next_to(s2, RIGHT, buff=0.25)
        self.play(self.chip("put in y' = ay - by^2"), run_time=0.5)
        self.play(FadeIn(s1.ks("zp", "=", "-")), TransformFromCopy(e0.span("a", "y2"), s1.k("num")), run_time=1.3)
        self.play(FadeIn(s2), run_time=1.0)
        self.play(Indicate(s2.k("ay"), color=YELLOW_C), run_time=0.6)
        self.play(TransformFromCopy(s2.k("ay"), s3.ks("m", "z")), FadeIn(s3.ks("=", "+", "b")), run_time=1.0)
        lin = label("linear in z", 22, GREEN_C).next_to(s3, DOWN, buff=0.2)
        self.play(ShowCreation(hbox(s3, GREEN_C)), FadeIn(lin), run_time=0.7)
        box = hbox(s3, GREEN_C)
        self.step_done(e0, d, s1, s2, s3, box, lin)

        # 3. solve for z, flip to y
        zs = M(("z", "z"), "=", ("ss", r"\frac{b}{a}"), "+", ("c", r"\left(z(0) - \frac{b}{a}\right)"), ("e", "e^{-at}"),
               size=1.0, colors={"ss": GREEN_C, "e": YELLOW_C}).move_to([0, -1.55, 0])
        ys = M(("y", "y"), "=", ("res", r"\frac{a}{b + d\,e^{-at}}"), size=1.2).move_to([-1.6, -2.45, 0])
        dd = M(("d", "d"), "=", ("dd", r"\frac{a}{y(0)} - b"), size=0.85).next_to(ys, RIGHT, buff=0.7)
        self.play(self.chip("steady value + decaying part"), FadeOut(lin), run_time=0.5)
        self.play(TransformFromCopy(s3, zs), run_time=1.3)
        self.play(TransformFromCopy(zs, ys), run_time=1.3)
        self.play(FadeIn(dd), ShowCreation(hbox(ys, GREEN_C)), run_time=0.8)
        self.step_done(e0, d, s1, s2, s3, box, zs, ys, dd, hbox(ys, GREEN_C))


class SCurveSequence(ControlScene):
    SEQ_ID = "s-curve"

    def construct(self):
        p = Plot(t_max=8, y_min=0, y_max=1.6, width=7.2, height=4.4, t_label="t", y_label="y").move_to([-2.2, 0.3, 0])
        cap = DashedLine(p.c2p(0, 1), p.c2p(8, 1)).set_stroke(GREEN_C, 2)
        caplab = label("a/b = 1", 20, GREEN_C).next_to(p.c2p(8, 1), RIGHT, buff=0.1)
        eq = M(("yp", "y'"), "=", ("y", "y"), "-", ("y2", "y^2"), size=1.0).move_to([4.3, 2.6, 0])
        self.start(p, cap, caplab, eq)

        def logi(y0):
            d = 1 / y0 - 1
            return lambda t: 1 / (1 + d * np.exp(-t))

        # 1. one S-curve
        c = p.curve(logi(0.25), color=TEAL_C, width=5)
        f = M(("y", "y"), "=", ("res", r"\frac{1}{1 + 3e^{-t}}"), size=0.95).move_to([4.3, 1.4, 0])
        self.play(self.chip("y(0) = 1/4"), FadeIn(Dot(p.c2p(0, 0.25), radius=0.07).set_fill(TEAL_C)), run_time=0.6)
        self.play(ShowCreation(c), Write(f), run_time=2.0)
        self.step_done(p, cap, caplab, eq, c, f)

        # 2. inflection
        t3 = np.log(3)
        half = DashedLine(p.c2p(0, 0.5), p.c2p(t3, 0.5)).set_stroke(YELLOW_C, 2)
        vline = DashedLine(p.c2p(t3, 0), p.c2p(t3, 0.5)).set_stroke(YELLOW_C, 2)
        dot = Dot(p.c2p(t3, 0.5), radius=0.08).set_fill(YELLOW_C)
        tang = Line(p.c2p(t3 - 1.2, 0.5 - 0.3), p.c2p(t3 + 1.2, 0.5 + 0.3)).set_stroke(YELLOW_C, 3)
        fl = M(("ypp", "y''"), "=", ("k", "(1 - 2y)"), ("yp", "y'"), "=", "0", size=0.85,
               colors={"k": YELLOW_C}).move_to([4.3, 0.4, 0])
        tl = label("t = ln 3,  y = 1/2: steepest", 20, YELLOW_C).move_to([4.3, -0.3, 0])
        self.play(self.chip("bend at half capacity"), run_time=0.5)
        self.play(Write(fl), run_time=1.0)
        self.play(ShowCreation(half), ShowCreation(vline), FadeIn(dot), run_time=0.9)
        self.play(ShowCreation(tang), FadeIn(tl), run_time=0.9)
        self.step_done(p, cap, caplab, eq, c, f, half, vline, dot, tang, fl, tl)

        # 3. a family
        fam = VGroup(*[p.curve(logi(y0), color=TEAL_C if y0 < 1 else PINK_C, width=3)
                       for y0 in (0.03, 0.08, 0.5, 0.8, 1.3, 1.55)])
        zero = Line(p.c2p(0, 0.005), p.c2p(8, 0.005)).set_stroke(RED_C, 4)
        zl = label("0: unstable", 20, RED_C).move_to([4.3, -1.3, 0])
        sl = label("1: stable", 20, GREEN_C).move_to([4.3, -1.8, 0])
        self.play(self.chip("all positive starts"), FadeOut(VGroup(half, vline, tang, tl)), run_time=0.5)
        self.play(LaggedStart(*[ShowCreation(m) for m in fam], lag_ratio=0.25), run_time=2.4)
        self.play(ShowCreation(zero), FadeIn(zl), FadeIn(sl), Indicate(cap, color=GREEN_C), run_time=1.0)
        self.step_done(p, cap, caplab, eq, c, f, dot, fl, fam, zero, zl, sl)


# ======================================================================== Section 2

class StabilityTestSequence(ControlScene):
    SEQ_ID = "stability-test"

    def construct(self):
        p = XPlot(-0.6, 1.6, -0.9, 0.5, width=6.4, height=4.2, x_label="y", y_label="f(y)").move_to([-2.6, 0.2, 0])
        f = lambda y: y - y * y
        c = p.xcurve(f, color=TEAL_C, width=5)
        eq = M(("yp", "y'"), "=", ("f", "f(y)"), "=", ("y", "y"), "-", ("y2", "y^2"), size=0.95).move_to([3.6, 2.7, 0])
        self.start(p, c, eq)

        # 1. roots
        d0 = Dot(p.xp(0, 0), radius=0.09).set_fill(RED_C)
        d1 = Dot(p.xp(1, 0), radius=0.09).set_fill(GREEN_C)
        r = M(("Y", "Y(1 - Y)"), "=", "0", r"\;\Rightarrow\;", ("r", "Y = 0,\\ 1"), size=0.85).move_to([3.6, 1.7, 0])
        self.play(self.chip("f(Y) = 0"), run_time=0.5)
        self.play(Write(r), run_time=1.0)
        self.play(GrowFromCenter(d0), GrowFromCenter(d1), run_time=0.8)
        self.step_done(p, c, eq, d0, d1, r)

        # 2. tangents
        t0 = Line(p.xp(-0.5, -0.5), p.xp(0.5, 0.5)).set_stroke(YELLOW_C, 3)
        t1 = Line(p.xp(0.5, 0.5), p.xp(1.5, -0.5)).set_stroke(YELLOW_C, 3)
        s = M(("fp", "f'(y)"), "=", "1 - 2y", size=0.85).move_to([3.6, 0.8, 0])
        s0 = label("f'(0) = +1", 22, RED_C).move_to([3.0, 0.1, 0])
        s1 = label("f'(1) = -1", 22, GREEN_C).move_to([4.6, 0.1, 0])
        self.play(self.chip("slope at each root"), Write(s), run_time=1.0)
        self.play(ShowCreation(t0), FadeIn(s0), run_time=0.9)
        self.play(ShowCreation(t1), FadeIn(s1), run_time=0.9)
        self.step_done(p, c, eq, d0, d1, r, t0, t1, s, s0, s1)

        # 3. gap equation
        g = M(("g", "(y - Y)'"), r"\approx", ("fp", "f'(Y)"), ("g2", "(y - Y)"), size=0.9,
              colors={"fp": YELLOW_C}).move_to([3.6, -0.8, 0])
        g2 = M(("g", "y - Y"), r"\approx", ("C", "C"), ("e", "e^{f'(Y)t}"), size=0.9,
               colors={"e": YELLOW_C}).move_to([3.6, -1.6, 0])
        verdict = label("negative slope: gap shrinks (stable)", 20, GREEN_C).move_to([3.4, -2.3, 0])
        self.play(self.chip("tangent line approximation"), run_time=0.5)
        self.play(TransformFromCopy(s, g), run_time=1.2)
        self.play(TransformFromCopy(g, g2), run_time=1.0)
        self.play(FadeIn(verdict), Indicate(d1, color=GREEN_C), run_time=0.8)
        self.step_done(p, c, eq, d0, d1, r, t0, t1, s, s0, s1, g, g2, verdict)


class StabilityLineSequence(ControlScene):
    SEQ_ID = "stability-line"

    def construct(self):
        p = XPlot(-1.6, 1.6, -1.2, 1.2, width=7.0, height=3.4, x_label="y", y_label="f(y)").move_to([-1.9, 1.2, 0])
        f = lambda y: y - y ** 3
        c = p.xcurve(f, color=TEAL_C, width=5)
        eq = M(("f", "f(y)"), "=", ("y", "y(1 - y)(1 + y)"), size=0.9).move_to([3.9, 2.8, 0])
        self.start(p, c, eq)

        # 1. signs
        pos = [p.xcurve(lambda y: f(y) if (y < -1 or 0 < y < 1) else np.nan, color=GREEN_C, width=6)]
        regions = VGroup()
        for a, b, sgn in [(-1.6, -1, "+"), (-1, 0, "−"), (0, 1, "+"), (1, 1.6, "−")]:
            col = GREEN_C if sgn == "+" else RED_C
            regions.add(label(sgn, 30, col, weight=BOLD).move_to(p.xp((a + b) / 2, 0.75 if sgn == "+" else -0.75)))
        self.play(self.chip("sign of f"), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in regions], lag_ratio=0.3), run_time=1.4)
        self.step_done(p, c, eq, regions)

        # 2. the line with arrows
        yl = -1.6
        line = Line(p.xp(-1.6, 0) + (yl - p.xp(0, 0)[1]) * UP, p.xp(1.6, 0) + (yl - p.xp(0, 0)[1]) * UP).set_stroke(FG, 3)
        def lp(y):
            return np.array([p.xp(y, 0)[0], yl, 0])
        arrows = VGroup()
        for a, b, right in [(-1.55, -1.1, True), (-0.4, -0.9, False), (0.1, 0.9, True), (1.55, 1.1, False)]:
            col = GREEN_C if right else RED_C
            arrows.add(arrow(lp(a) + 0.25 * UP, lp(b) + 0.25 * UP, color=col))
        ticks = VGroup(*[label(str(v), 22, FG).next_to(lp(v), DOWN, buff=0.15) for v in (-1, 0, 1)])
        dots = VGroup(*[Dot(lp(v), radius=0.09).set_fill(FG) for v in (-1, 0, 1)])
        self.play(self.chip("copy the signs onto the y line"), ShowCreation(line), FadeIn(ticks), FadeIn(dots), run_time=1.0)
        for a, r in zip(arrows, regions):
            self.play(TransformFromCopy(r, a), run_time=0.6)
        self.step_done(p, c, eq, regions, line, ticks, dots, arrows)

        # 3. classify
        newdots = VGroup(Dot(lp(-1), radius=0.11).set_fill(GREEN_C), Dot(lp(0), radius=0.11).set_fill(RED_C),
                         Dot(lp(1), radius=0.11).set_fill(GREEN_C))
        txt = VGroup(label("stable", 20, GREEN_C).next_to(lp(-1), DOWN, buff=0.55),
                     label("unstable", 20, RED_C).next_to(lp(0), DOWN, buff=0.55),
                     label("stable", 20, GREEN_C).next_to(lp(1), DOWN, buff=0.55))
        chk = M(("fp", "f'(\\pm1) = -2,"), ("f0", "f'(0) = 1"), size=0.8).move_to([4.2, 1.6, 0])
        self.play(self.chip("arrows in: stable; arrows out: unstable"), run_time=0.5)
        self.play(ReplacementTransform(dots, newdots), FadeIn(txt), run_time=1.0)
        self.play(Write(chk), run_time=1.0)
        self.step_done(p, c, eq, regions, line, ticks, newdots, arrows, txt, chk)


# ======================================================================== Section 3

class SeparateSequence(ControlScene):
    SEQ_ID = "separate"

    def construct(self):
        e0 = M(("dy", "dy"), "/", ("dt", "dt"), "=", ("t", "t"), "/", ("y", "y"), size=1.3).move_to([-3.3, 2.6, 0])
        self.start(e0)

        # 1. separate
        e1 = M(("y", "y"), ("dy", "dy"), "=", ("t", "t"), ("dt", "dt"), size=1.3).move_to([-3.3, 1.5, 0])
        self.play(self.chip("multiply by y dt"), run_time=0.5)
        self.play(self.tmorph(e0, e1, keep_src=True, path_arc=0.6), run_time=1.6)
        self.step_done(e0, e1)

        # 2. integrate
        e2 = M(("l", r"\frac{1}{2}y^2 - \frac{1}{2}y(0)^2"), "=", ("r", r"\frac{1}{2}t^2"), size=1.05,
               colors={"l": TEAL_C, "r": BLUE_C}).move_to([-3.1, 0.4, 0])
        self.play(self.chip("integrate both sides"), run_time=0.5)
        self.play(TransformFromCopy(e1.ks("y", "dy"), e2.k("l")), FadeIn(e2.k("=")),
                  TransformFromCopy(e1.ks("t", "dt"), e2.k("r")), run_time=1.4)
        self.step_done(e0, e1, e2)

        # 3. solve and draw
        e3 = M(("y", "y"), "=", ("res", r"\sqrt{y(0)^2 + t^2}"), size=1.1).move_to([-3.1, -0.7, 0])
        p = Plot(t_max=3, y_min=-3, y_max=3.2, width=5.0, height=4.6, t_label="t", y_label="y").move_to([3.4, 0.2, 0])
        curves = VGroup(*[p.curve(lambda t, c=c: np.sqrt(c * c + t * t), color=GREEN_C, width=3) for c in (0.5, 1, 1.5, 2)])
        self.play(self.chip("solve for y"), run_time=0.5)
        self.play(TransformFromCopy(e2, e3), run_time=1.2)
        self.play(FadeIn(p), LaggedStart(*[ShowCreation(m) for m in curves], lag_ratio=0.2), run_time=1.6)
        self.step_done(e0, e1, e2, e3, p, curves)

        # 4. y(0) = 0: two solutions
        up = p.curve(lambda t: t, color=YELLOW_C, width=5)
        dn = p.curve(lambda t: -t, color=RED_C, width=5)
        o = Dot(p.c2p(0, 0), radius=0.09).set_fill(YELLOW_C)
        e4 = M(("a", "y = t"), r"\ \mathrm{and}\ ", ("b", "y = -t"), r"\ (t \neq 0)", size=1.0, colors={"a": YELLOW_C, "b": RED_C}).move_to([-3.1, -1.8, 0])
        w = label("t/y = 0/0 at the start: no unique solution", 22, RED_C).move_to([-3.1, -2.5, 0])
        self.play(self.chip("start at y(0) = 0"), FadeIn(o), run_time=0.6)
        self.play(ShowCreation(up), ShowCreation(dn), Write(e4), run_time=1.5)
        self.play(FadeIn(w), run_time=0.6)
        self.step_done(e0, e1, e2, e3, p, curves, o, up, dn, e4, w)


class PartialFractionsSequence(ControlScene):
    SEQ_ID = "partial-fractions"

    def construct(self):
        e0 = M(("l", r"\frac{dy}{y - y^2}"), "=", ("dt", "dt"), size=1.3).move_to([0, 2.6, 0])
        self.start(e0)

        # 1. factor and split
        e1 = M(("f", r"\frac{1}{y(1 - y)}"), "=", ("A", r"\frac{A}{y}"), "+", ("B", r"\frac{B}{1 - y}"), size=1.2,
               colors={"A": TEAL_C, "B": YELLOW_C}).move_to([0, 1.3, 0])
        self.play(self.chip("y - y^2 = y(1 - y)"), run_time=0.5)
        self.play(TransformFromCopy(e0.k("l"), e1.k("f")), run_time=1.1)
        self.play(FadeIn(e1.ks("=", "A", "+", "B")), run_time=1.0)
        self.step_done(e0, e1)

        # 2. cover-up: put in y = 0 and y = 1
        e2 = M("1", "=", ("A", "A(1 - y)"), "+", ("B", "B\\,y"), size=1.05, colors={"A": TEAL_C, "B": YELLOW_C}).move_to([-2.6, 0.1, 0])
        a = M(("y0", "y = 0:"), ("A", "A = 1"), size=0.9, colors={"A": TEAL_C}).move_to([2.6, 0.4, 0])
        b = M(("y1", "y = 1:"), ("B", "B = 1"), size=0.9, colors={"B": YELLOW_C}).move_to([2.6, -0.3, 0])
        self.play(self.chip("multiply by y(1 - y)"), TransformFromCopy(e1, e2), run_time=1.3)
        self.play(FadeIn(a.k("y0")), TransformFromCopy(e2.k("A"), a.k("A")), run_time=1.0)
        self.play(FadeIn(b.k("y1")), TransformFromCopy(e2.k("B"), b.k("B")), run_time=1.0)
        self.step_done(e0, e1, e2, a, b)

        # 3. integrate
        e3 = M(("A", r"\ln|y|"), "-", ("B", r"\ln|1 - y|"), "=", ("t", "t + C"), size=1.15,
               colors={"A": TEAL_C, "B": YELLOW_C}).move_to([0, -1.2, 0])
        self.play(self.chip("each piece gives a logarithm"), run_time=0.5)
        self.play(TransformFromCopy(e1.k("A"), e3.k("A")), TransformFromCopy(e1.k("B"), e3.k("B")),
                  FadeIn(e3.ks("-", "=", "t")), run_time=1.4)
        self.step_done(e0, e1, e2, a, b, e3)

        # 4. exponentiate and solve
        e4 = M(("q", r"\frac{y}{1 - y}"), "=", ("K", "K e^{t}"), r"\;\Rightarrow\;", ("res", r"y = \frac{1}{1 + e^{-t}/K}"),
               size=1.05).move_to([0, -2.3, 0])
        self.play(self.chip("exponentiate"), TransformFromCopy(e3, e4.ks("q", "=", "K")), run_time=1.3)
        self.play(FadeIn(e4.k(r"\;\Rightarrow\;")), Write(e4.k("res")), run_time=1.1)
        self.play(ShowCreation(hbox(e4.k("res"), GREEN_C)), run_time=0.6)
        self.step_done(e0, e1, e2, a, b, e3, e4, hbox(e4.k("res"), GREEN_C))
