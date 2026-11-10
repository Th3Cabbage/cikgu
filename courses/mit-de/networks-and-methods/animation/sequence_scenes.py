"""ManimGL scenes for Unit 4, Electrical Networks and Solution Methods (one scene per sequence).

Colour code: unknown coefficients yellow, inputs blue, resistance teal, reactance pink, results
green, resonance red. Formulas use matplotlib mathtext (no \\tfrac, \\text, \\Big, \\quad tokens).
Stage bounds: content stays within |x| <= 6.3 and -2.8 <= y <= 3.3 (chip sits bottom-left).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"a": YELLOW_C, "b": YELLOW_C, "in": BLUE_C, "R": TEAL_C, "X": PINK_C, "res": GREEN_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


# ======================================================================== Section 1

class RLCImpedanceSequence(ControlScene):
    SEQ_ID = "rlc-impedance"

    def construct(self):
        e0 = M(("L", "L I'"), "+", ("R", "R I"), "+", ("C", r"\frac{1}{C}\int I\,dt"), "=", ("in", r"V e^{i\omega t}"),
               size=1.05, colors={"L": PINK_C, "C": PINK_C}).move_to([0, 2.7, 0])
        self.start(e0)

        # 1. substitute
        e1 = M("(", ("L", r"i\omega L"), "+", ("R", "R"), "+", ("C", r"\frac{1}{i\omega C}"), ")", ("W", "W"), "=", ("V", "V"),
               size=1.05, colors={"L": PINK_C, "C": PINK_C, "W": YELLOW_C}).move_to([0, 1.6, 0])
        self.play(self.chip("I = W e^(iwt)"), run_time=0.5)
        self.play(TransformFromCopy(e0.k("L"), e1.k("L")), TransformFromCopy(e0.k("R"), e1.k("R")),
                  TransformFromCopy(e0.k("C"), e1.k("C")), FadeIn(e1.ks("(", "+", ")", "W", "=", "V")), run_time=1.5)
        self.step_done(e0, e1)

        # 2. Z
        e2 = M(("Z", "Z"), "=", ("R", "R"), "+", ("i", "i"), ("X", r"\left(\omega L - \frac{1}{\omega C}\right)"), size=1.05).move_to([-2.6, 0.45, 0])
        side = M(("one", r"\frac{1}{i} = -i"), size=0.8, colors={"one": YELLOW_C}).move_to([3.4, 0.45, 0])
        self.play(self.chip("1/i = -i"), FadeIn(side), run_time=0.7)
        self.play(TransformFromCopy(e1.span("L", "C"), e2.ks("R", "+", "i", "X")), FadeIn(e2.ks("Z", "=")), run_time=1.5)
        self.step_done(e0, e1, e2, side)

        # 3. the picture of Z
        o = np.array([-4.6, -2.2, 0])
        ax = VGroup(Line(o + 0.2 * LEFT, o + 4.2 * RIGHT).set_stroke(DIM, 2), Line(o + 0.6 * DOWN, o + 2.4 * UP).set_stroke(DIM, 2))
        rv = Line(o, o + 3.0 * RIGHT).set_stroke(TEAL_C, 6)
        xv = Line(o + 3.0 * RIGHT, o + 3.0 * RIGHT + 1.8 * UP).set_stroke(PINK_C, 6)
        zv = arrow(o, o + 3.0 * RIGHT + 1.8 * UP, color=GREEN_C, width=5)
        rl = label("R", 22, TEAL_C).next_to(rv, DOWN, buff=0.1)
        xl = label("ωL − 1/(ωC)", 20, PINK_C).next_to(xv, RIGHT, buff=0.1)
        zl = label("|Z|", 22, GREEN_C).move_to(o + 1.2 * RIGHT + 1.15 * UP)
        mag = M(("m", "|Z|^2"), "=", ("R", "R^2"), "+", ("X", r"\left(\omega L - \frac{1}{\omega C}\right)^2"), size=0.85).move_to([2.6, -1.0, 0])
        tune = label("ω0 = 1/√(LC):  reactance 0,  |Z| = R", 20, GREEN_C).move_to([2.6, -1.9, 0])
        self.play(self.chip("real part R, imaginary part the reactance"), FadeOut(side), FadeIn(ax), run_time=0.6)
        self.play(TransformFromCopy(e2.k("R"), rv), FadeIn(rl), run_time=0.9)
        self.play(TransformFromCopy(e2.k("X"), xv), FadeIn(xl), run_time=0.9)
        self.play(grow_arrow(zv), FadeIn(zl), Write(mag), run_time=1.2)
        self.play(FadeIn(tune), run_time=0.6)
        self.step_done(e0, e1, e2, ax, rv, xv, zv, rl, xl, zl, mag, tune)


# ======================================================================== Section 2

class UCMatchSequence(ControlScene):
    SEQ_ID = "uc-match"

    def construct(self):
        e0 = M(("ypp", "y''"), "+", ("yp", "y'"), "+", ("y", "y"), "=", ("in", "t"), size=1.3).move_to([0, 2.7, 0])
        self.start(e0)

        # 1. guess
        g = M(("y", "y_p"), "=", ("a", "a"), "+", ("b", "b"), "t", size=1.0).move_to([-3.6, 1.5, 0])
        g1 = M(("y", "y_p'"), "=", ("b", "b"), size=1.0).move_to([0, 1.5, 0])
        g2 = M(("y", "y_p''"), "=", "0", size=1.0).move_to([3.3, 1.5, 0])
        self.play(self.chip("same form, unknown numbers"), Write(g), run_time=1.0)
        self.play(TransformFromCopy(g, g1), run_time=0.9)
        self.play(TransformFromCopy(g1, g2), run_time=0.9)
        self.step_done(e0, g, g1, g2)

        # 2. substitute
        s = M(("z", "0"), "+", ("b", "b"), "+", "(", ("a", "a"), "+", ("b2", "b"), "t", ")", "=", ("in", "t"),
              size=1.2, colors={"b2": YELLOW_C}).move_to([0, 0.2, 0])
        self.play(self.chip("put y_p into the equation"), run_time=0.5)
        self.play(TransformFromCopy(g2.k("0"), s.k("z")), TransformFromCopy(g1.k("b"), s.k("b")),
                  TransformFromCopy(g.span("a", "t"), s.span("a", "t")), FadeIn(s.ks("+", "(", ")", "=", "in")), run_time=1.5)
        self.step_done(e0, g, g1, g2, s)

        # 3. match
        m1 = M(("l", "t:"), ("b", "b = 1"), size=1.0).move_to([-3.0, -1.1, 0])
        m2 = M(("l", "1:"), ("a", "a + b = 0"), r"\Rightarrow", ("a2", "a = -1"), size=1.0).move_to([1.6, -1.1, 0])
        res = M(("y", "y_p"), "=", ("res", "t - 1"), size=1.3).move_to([0, -2.2, 0])
        self.play(self.chip("match t terms, then constants"), Indicate(s.k("b2"), color=YELLOW_C), Indicate(s.k("in"), color=BLUE_C), run_time=0.8)
        self.play(Write(m1), run_time=0.8)
        self.play(Write(m2), run_time=1.0)
        self.play(FadeIn(res, shift=0.2 * UP), ShowCreation(hbox(res, GREEN_C)), run_time=0.9)
        self.step_done(e0, g, g1, g2, s, m1, m2, res, hbox(res, GREEN_C))


# ======================================================================== Section 3

class UCExampleSequence(ControlScene):
    SEQ_ID = "uc-example"

    def construct(self):
        e0 = M(("e", "y'' - 3y' + 2y"), "=", ("in", "4t"), size=1.15).move_to([-2.8, 2.7, 0])
        n0 = M(("P", "s^2 - 3s + 2"), "=", ("f", "(s - 1)(s - 2)"), size=0.75, colors={"f": PINK_C}).move_to([3.4, 2.2, 0])
        self.start(e0, n0)

        # 1. substitute
        s = M(("z", "0"), "-", ("b", "3b"), "+", ("a", "2(a + bt)"), "=", ("in", "4t"), size=1.15).move_to([-2.8, 1.5, 0])
        self.play(self.chip("y = a + bt, y' = b, y'' = 0"), run_time=0.5)
        self.play(TransformFromCopy(e0, s), run_time=1.4)
        self.step_done(e0, n0, s)

        # 2. match
        m1 = M(("t", "2b = 4"), r"\Rightarrow", ("b", "b = 2"), size=0.95).move_to([-2.8, 0.45, 0])
        m2 = M(("c", "2a - 3b = 0"), r"\Rightarrow", ("a", "a = 3"), size=0.95).move_to([-2.8, -0.35, 0])
        res = M(("y", "y_p"), "=", ("res", "3 + 2t"), size=1.15).move_to([-2.8, -1.3, 0])
        self.play(self.chip("match"), Write(m1), run_time=1.0)
        self.play(Write(m2), run_time=1.0)
        self.play(FadeIn(res), ShowCreation(hbox(res, GREEN_C)), run_time=0.8)
        self.step_done(e0, n0, s, m1, m2, res, hbox(res, GREEN_C))

        # 3. resonance with e^{2t}
        r0 = M(("in", "e^{2t}"), ":", ("P", "P(2) = 0"), size=0.95, colors={"P": RED_C}).move_to([3.1, 1.5, 0])
        r1 = M(("x", r"Y e^{2t}\ \to\ 0"), size=0.85, colors={"x": RED_C}).move_to([3.1, 0.7, 0])
        r2 = M(("y", "y_p"), "=", ("t", r"\frac{t\,e^{2t}}{P'(2)}"), "=", ("res", r"t\,e^{2t}"), size=1.0).move_to([3.1, -0.3, 0])
        r3 = label("P'(s) = 2s - 3,  P'(2) = 1", 20, YELLOW_C).move_to([3.1, -1.2, 0])
        self.play(self.chip("the input is a null solution"), Indicate(n0.k("f"), color=PINK_C), Write(r0), run_time=1.1)
        self.play(FadeIn(r1), run_time=0.7)
        self.play(Write(r2), FadeIn(r3), run_time=1.2)
        self.step_done(e0, n0, s, m1, m2, res, hbox(res, GREEN_C), r0, r1, r2, r3)


# ======================================================================== Section 4

class VPWronskianSequence(ControlScene):
    SEQ_ID = "vp-wronskian"

    def construct(self):
        e0 = M(("y", "y"), "=", ("c1", "c_1(t)"), ("y1", "y_1"), "+", ("c2", "c_2(t)"), ("y2", "y_2"), size=1.2,
               colors={"c1": YELLOW_C, "c2": YELLOW_C}).move_to([0, 2.7, 0])
        self.start(e0)

        # 1. the system
        A = Mat([["y_1", "y_2"], ["y_1'", "y_2'"]], size=1.0)
        x = Mat([["c_1'"], ["c_2'"]], size=1.0, colors={})
        b = Mat([["0"], ["f"]], size=1.0)
        sysm = VGroup(A, x, M("="), b).arrange(RIGHT, buff=0.25).move_to([0, 1.1, 0])
        for row in x.e:
            row[0].set_color(YELLOW_C)
        b.e[1][0].set_color(BLUE_C)
        lab1 = label("keeps y' simple", 20, DIM).move_to([4.3, 1.45, 0])
        lab2 = label("makes y solve the equation", 20, DIM).move_to([4.6, 0.75, 0])
        self.play(self.chip("two conditions on c1', c2'"), FadeIn(sysm), run_time=1.2)
        self.play(FadeIn(lab1), FadeIn(lab2), run_time=0.7)
        self.step_done(e0, sysm, lab1, lab2)

        # 2. Wronskian
        w = M(("W", "W"), "=", ("d", "y_1 y_2' - y_2 y_1'"), size=1.0, colors={"W": GREEN_C}).move_to([0, -0.4, 0])
        cross1 = Line(A.e[0][0].get_center(), A.e[1][1].get_center()).set_stroke(GREEN_C, 3)
        cross2 = Line(A.e[0][1].get_center(), A.e[1][0].get_center()).set_stroke(RED_C, 3)
        self.play(self.chip("determinant of the matrix"), ShowCreation(cross1), ShowCreation(cross2), run_time=0.9)
        self.play(Write(w), run_time=1.0)
        self.step_done(e0, sysm, lab1, lab2, w, cross1, cross2)

        # 3. Cramer
        c1 = M(("c", "c_1'"), "=", ("v", r"-\frac{y_2 f}{W}"), size=1.05, colors={"c": YELLOW_C}).move_to([-2.4, -1.8, 0])
        c2 = M(("c", "c_2'"), "=", ("v", r"\frac{y_1 f}{W}"), size=1.05, colors={"c": YELLOW_C}).move_to([2.4, -1.8, 0])
        self.play(self.chip("Cramer's rule"), FadeOut(VGroup(cross1, cross2)), run_time=0.5)
        self.play(TransformFromCopy(VGroup(b, A.col(1)), c1), run_time=1.3)
        self.play(TransformFromCopy(VGroup(b, A.col(0)), c2), run_time=1.3)
        self.step_done(e0, sysm, lab1, lab2, w, c1, c2)


class VPConvolutionSequence(ControlScene):
    SEQ_ID = "vp-convolution"

    def construct(self):
        g = lambda t: np.where(t > 0, np.exp(-t) - np.exp(-2 * t), 0.0)
        p = Plot(t_max=6, y_min=-0.05, y_max=0.6, width=6.2, height=3.8, t_label="t").move_to([-3.0, -0.3, 0])
        e0 = M(("g", "g(t)"), "=", ("v", "e^{-t} - e^{-2t}"), size=0.8, colors={"g": TEAL_C}).move_to([3.4, 2.7, 0])
        c0 = p.curve(lambda t: float(g(t)), color=TEAL_C, width=5)
        self.start(p, e0, c0)

        # 1. shifted copies
        Ts = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        dT = 0.5
        copies = VGroup(*[p.curve(lambda t, T=T: float(g(t - T)) * dT, color=BLUE_C, width=2.5) for T in Ts])
        ticks = VGroup(*[Line(p.c2p(T, 0), p.c2p(T, 0.07)).set_stroke(BLUE_C, 4) for T in Ts])
        e1 = M(("f", r"f(T)\,dT"), r"\to", ("r", r"f(T)\,g(t - T)\,dT"), size=0.68, colors={"f": BLUE_C, "r": BLUE_C}).move_to([3.4, 1.8, 0])
        self.play(self.chip("slices of input at times T (f = 1)"), FadeIn(ticks), Write(e1), run_time=1.0)
        self.play(LaggedStart(*[ShowCreation(c) for c in copies], lag_ratio=0.25), run_time=2.2)
        self.step_done(p, e0, c0, ticks, e1, copies)

        # 2. add
        def total(t):
            return float(sum(g(t - T) * dT for T in [0.25 + 0.5 * i for i in range(int(t / 0.5) + 1)] if T < t))
        e2 = M(("y", "y(t)"), "=", ("i", r"\int_0^t g(t - T)\,f(T)\,dT"), size=0.75, colors={"y": GREEN_C}).move_to([3.4, 0.8, 0])
        r = lambda t: 0.5 - np.exp(-t) + 0.5 * np.exp(-2 * t)
        cr = p.curve(r, color=GREEN_C, width=5)
        self.play(self.chip("superposition: add them"), Write(e2), run_time=1.0)
        self.play(TransformFromCopy(copies, cr), run_time=1.6)
        self.step_done(p, e0, c0, ticks, e1, copies, e2, cr)

        # 3. step response
        e3 = M(("y", "y"), "=", ("v", r"\frac{1}{2} - e^{-t} + \frac{1}{2}e^{-2t}"), size=0.75, colors={"y": GREEN_C}).move_to([3.4, -0.2, 0])
        lim = DashedLine(p.c2p(0, 0.5), p.c2p(6, 0.5)).set_stroke(GREEN_C, 2)
        n = label("f = 1: the step response of Unit 3", 20, GREEN_C).move_to([3.4, -1.0, 0])
        self.play(self.chip("check with f = 1"), FadeOut(copies), Write(e3), run_time=1.1)
        self.play(ShowCreation(lim), FadeIn(n), run_time=0.8)
        self.step_done(p, e0, c0, ticks, e1, e2, cr, e3, lim, n)
