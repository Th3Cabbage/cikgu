"""ManimGL scenes for Unit 5, The Laplace Transform (one scene per sequence in control_specs).

Colour code: time functions teal, transforms yellow, poles red, inputs blue, results green.
Formulas use matplotlib mathtext (no \\tfrac, \\text, \\Big, standalone \\quad tokens).
Stage bounds: content stays within |x| <= 6.3 and -2.8 <= y <= 3.3 (chip sits bottom-left).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"f": TEAL_C, "F": YELLOW_C, "Y": YELLOW_C, "in": BLUE_C, "res": GREEN_C, "pole": RED_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def s_axis(x0=-3.0, x1=3.0, y=-1.9, unit=0.9, cx=0.0):
    o = np.array([cx, y, 0])
    ax = VGroup(Line(o + x0 * unit * RIGHT, o + x1 * unit * RIGHT).set_stroke(DIM, 2),
                Line(o + 1.2 * DOWN, o + 1.2 * UP).set_stroke(DIM, 2))
    lab = VGroup(label("Re s", 18, DIM).next_to(o + x1 * unit * RIGHT, DOWN, buff=0.08),
                 label("Im s", 18, DIM).next_to(o + 1.2 * UP, RIGHT, buff=0.08))
    return VGroup(ax, lab), (lambda re, im=0.0: o + re * unit * RIGHT + im * unit * UP)


# ======================================================================== Section 1

class TransformExpSequence(ControlScene):
    SEQ_ID = "transform-exp"

    def construct(self):
        e0 = M(("F", "F(s)"), "=", ("i", r"\int_0^\infty"), ("f", "f(t)"), ("w", "e^{-st}"), ("dt", "dt"), size=1.15).move_to([0, 2.75, 0])
        self.start(e0)

        # 1. substitute
        e1 = M(("i", r"\int_0^\infty"), ("f", "e^{at}"), ("w", "e^{-st}"), ("dt", "dt"), "=", ("i2", r"\int_0^\infty"),
               ("c", "e^{(a - s)t}"), ("dt2", "dt"), size=1.05, colors={"c": TEAL_C}).move_to([0, 1.2, 0])
        self.play(self.chip("f = e^(at)"), run_time=0.5)
        self.play(TransformFromCopy(e0.ks("i", "f", "w", "dt"), e1.ks("i", "f", "w", "dt")), run_time=1.2)
        self.play(FadeIn(e1.ks("=", "i2", "dt2")), TransformFromCopy(e1.ks("f", "w"), e1.k("c")), run_time=1.2)
        self.step_done(e0, e1)

        # 2. integrate
        e2 = M(("b", r"\left[\frac{e^{(a-s)t}}{a - s}\right]_0^\infty"), "=", ("z", "0"), "-", ("o", r"\frac{1}{a - s}"), "=",
               ("F", r"\frac{1}{s - a}"), size=1.0).move_to([0, -0.25, 0])
        n = label("s > a: the upper limit gives 0", 20, DIM).move_to([0, -1.05, 0])
        self.play(self.chip("antiderivative, then the limits"), TransformFromCopy(e1.k("c"), e2.k("b")), run_time=1.3)
        self.play(FadeIn(e2.ks("=", "z", "-", "o")), FadeIn(n), run_time=1.0)
        self.play(FadeIn(e2.all("=")[1]), TransformFromCopy(e2.k("o"), e2.k("F")), run_time=1.0)
        self.step_done(e0, e1, e2, n)

        # 3. pole on the s-axis
        ax, P = s_axis(y=-2.15)
        pole = pole_cross(RED_C).move_to(P(1.5))
        pl = label("pole at s = a", 20, RED_C).next_to(pole, UP, buff=0.15)
        self.play(self.chip("exponent a  ->  pole at a"), FadeOut(n), FadeIn(ax), run_time=0.6)
        self.play(TransformFromCopy(e2.k("F"), pole), FadeIn(pl), run_time=1.2)
        self.step_done(e0, e1, e2, ax, pole, pl)


class DerivativeRuleSequence(ControlScene):
    SEQ_ID = "derivative-rule"

    def construct(self):
        e0 = M(("L", r"\mathcal{L}[y']"), "=", ("i", r"\int_0^\infty"), ("yp", "y'"), ("w", "e^{-st}"), ("dt", "dt"), size=1.15,
               colors={"yp": TEAL_C, "w": YELLOW_C}).move_to([0, 2.6, 0])
        self.start(e0)

        # 1. by parts
        e1 = M("=", ("bd", r"\left[\,y\,e^{-st}\right]_0^\infty"), "-", ("i", r"\int_0^\infty"), ("y", "y"), ("dw", "(-s)e^{-st}"), ("dt", "dt"),
               size=1.05, colors={"bd": PINK_C, "y": TEAL_C, "dw": YELLOW_C}).move_to([0.3, 1.2, 0])
        rule = label("∫ u dv = uv − ∫ v du,   u = e^(−st),  dv = y′ dt", 20, DIM).move_to([0, 0.25, 0])
        self.play(self.chip("move the derivative onto e^(-st)"), FadeIn(rule), run_time=0.7)
        self.play(TransformFromCopy(e0.ks("yp", "w"), e1.k("bd")), FadeIn(e1.ks("=", "-", "i", "dt")),
                  TransformFromCopy(e0.k("yp"), e1.k("y")), TransformFromCopy(e0.k("w"), e1.k("dw")), run_time=1.6)
        self.step_done(e0, e1, rule)

        # 2. boundary term
        e2 = M(("bd", r"\left[\,y\,e^{-st}\right]_0^\infty"), "=", ("z", "0"), "-", ("y0", "y(0)"), size=1.0,
               colors={"bd": PINK_C, "y0": PINK_C}).move_to([-2.6, -0.6, 0])
        self.play(self.chip("evaluate at infinity and at 0"), FadeOut(rule), TransformFromCopy(e1.k("bd"), e2.k("bd")), run_time=1.1)
        self.play(FadeIn(e2.ks("=", "z", "-", "y0")), run_time=0.9)
        self.step_done(e0, e1, e2)

        # 3. the rule
        e3 = M(("L", r"\mathcal{L}[y']"), "=", ("s", "s"), ("Y", "Y(s)"), "-", ("y0", "y(0)"), size=1.3,
               colors={"s": YELLOW_C, "y0": PINK_C}).move_to([0, -1.95, 0])
        n = label("the remaining integral is s Y(s)", 20, YELLOW_C).move_to([2.9, -0.6, 0])
        self.play(self.chip("collect"), FadeIn(n), run_time=0.6)
        self.play(TransformFromCopy(e1.ks("y", "dw"), e3.ks("s", "Y")), TransformFromCopy(e2.k("y0"), e3.k("y0")),
                  FadeIn(e3.ks("L", "=", "-")), run_time=1.5)
        self.play(ShowCreation(hbox(e3, GREEN_C)), run_time=0.6)
        self.step_done(e0, e1, e2, n, e3, hbox(e3, GREEN_C))


class SolveFirstSequence(ControlScene):
    SEQ_ID = "solve-first"

    def construct(self):
        e0 = M(("yp", "y'"), "-", ("a", "a"), ("y", "y"), "=", ("in", "e^{ct}"), size=1.2).move_to([-3.2, 2.7, 0])
        self.start(e0)

        # 1. transform
        e1 = M(("sY", "sY - y(0)"), "-", ("a", "a"), ("Y", "Y"), "=", ("in", r"\frac{1}{s - c}"), size=1.05).move_to([2.6, 2.7, 0])
        arr = arrow(e0.get_right() + 0.15 * RIGHT, e1.get_left() + 0.15 * LEFT, color=YELLOW_C)
        self.play(self.chip("transform every term"), grow_arrow(arr), run_time=0.6)
        self.play(TransformFromCopy(e0.k("yp"), e1.k("sY")), TransformFromCopy(e0.ks("-", "a", "y"), e1.ks("-", "a", "Y")),
                  FadeIn(e1.k("=")), TransformFromCopy(e0.k("in"), e1.k("in")), run_time=1.5)
        self.step_done(e0, arr, e1)

        # 2. solve
        e2 = M(("Y", "Y"), "=", ("n", r"\frac{y(0)}{s - a}"), "+", ("pp", r"\frac{1}{(s - a)(s - c)}"), size=1.05,
               colors={"pp": YELLOW_C}).move_to([0, 1.3, 0])
        self.play(self.chip("algebra: divide by s - a"), TransformFromCopy(e1, e2), run_time=1.4)
        self.step_done(e0, arr, e1, e2)

        # 3. partial fractions
        e3 = M(("pp", r"\frac{1}{(s - a)(s - c)}"), "=", ("k", r"\frac{1}{c - a}"), "(", ("c", r"\frac{1}{s - c}"), "-",
               ("a", r"\frac{1}{s - a}"), ")", size=1.0, colors={"pp": YELLOW_C, "c": BLUE_C, "a": PINK_C}).move_to([0, -0.1, 0])
        self.play(self.chip("split the product"), TransformFromCopy(e2.k("pp"), e3.k("pp")), run_time=1.0)
        self.play(FadeIn(e3.ks("=", "k", "(", "-", ")")), FadeIn(e3.ks("c", "a"), shift=0.1 * UP), run_time=1.2)
        self.step_done(e0, arr, e1, e2, e3)

        # 4. invert
        e4 = M(("y", "y"), "=", ("n", "y(0)e^{at}"), "+", ("r", r"\frac{e^{ct} - e^{at}}{c - a}"), size=1.15,
               colors={"n": PINK_C, "r": GREEN_C}).move_to([0, -1.6, 0])
        rule = label("1/(s − p)  ←→  e^(pt)", 22, YELLOW_C).move_to([0, -2.45, 0])
        self.play(self.chip("each 1/(s - p) is e^(pt)"), FadeIn(rule), run_time=0.6)
        self.play(TransformFromCopy(e2.k("n"), e4.k("n")), TransformFromCopy(e3.ks("k", "c", "a"), e4.k("r")),
                  FadeIn(e4.ks("y", "=", "+")), run_time=1.6)
        self.step_done(e0, arr, e1, e2, e3, e4, rule)


# ======================================================================== Section 2

class CosTransformSequence(ControlScene):
    SEQ_ID = "cos-transform"

    def construct(self):
        e0 = M(("L", r"\mathcal{L}[e^{i\omega t}]"), "=", ("F", r"\frac{1}{s - i\omega}"), size=1.2).move_to([-2.5, 2.6, 0])
        self.start(e0)

        # 1. conjugate
        e1 = M(("F", r"\frac{1}{s - i\omega}"), r"\cdot", ("cj", r"\frac{s + i\omega}{s + i\omega}"), "=",
               ("r", r"\frac{s + i\omega}{s^2 + \omega^2}"), size=1.1, colors={"cj": PINK_C}).move_to([-1.0, 1.3, 0])
        self.play(self.chip("multiply by the conjugate"), TransformFromCopy(e0.k("F"), e1.k("F")), run_time=0.9)
        self.play(FadeIn(e1.ks(r"\cdot", "cj")), run_time=0.8)
        self.play(FadeIn(e1.k("=")), Write(e1.k("r")), run_time=1.1)
        self.step_done(e0, e1)

        # 2. real and imaginary parts
        c = M(("L", r"\mathcal{L}[\cos\omega t]"), "=", ("r", r"\frac{s}{s^2 + \omega^2}"), size=1.0, colors={"r": TEAL_C}).move_to([-3.2, -0.1, 0])
        s = M(("L", r"\mathcal{L}[\sin\omega t]"), "=", ("r", r"\frac{\omega}{s^2 + \omega^2}"), size=1.0, colors={"r": PINK_C}).move_to([-3.2, -1.3, 0])
        self.play(self.chip("real part: cos, imaginary part: sin"), TransformFromCopy(e1.k("r"), c.k("r")), FadeIn(c.ks("L", "=")), run_time=1.3)
        self.play(TransformFromCopy(e1.k("r"), s.k("r")), FadeIn(s.ks("L", "=")), run_time=1.3)
        self.step_done(e0, e1, c, s)

        # 3. poles at +- i omega
        ax, P = s_axis(x0=-2.0, x1=2.0, y=-0.9, unit=0.8, cx=3.6)
        p1 = pole_cross(RED_C).move_to(P(0, 1.0))
        p2 = pole_cross(RED_C).move_to(P(0, -1.0))
        l1 = label("+iω", 20, RED_C).next_to(p1, RIGHT, buff=0.12)
        l2 = label("−iω", 20, RED_C).next_to(p2, RIGHT, buff=0.12)
        self.play(self.chip("s^2 + w^2 = 0"), FadeIn(ax), run_time=0.6)
        self.play(GrowFromCenter(p1), GrowFromCenter(p2), FadeIn(l1), FadeIn(l2), run_time=1.0)
        self.step_done(e0, e1, c, s, ax, p1, p2, l1, l2)


# ======================================================================== Section 3

class ConvolutionSequence(ControlScene):
    SEQ_ID = "convolution"

    def construct(self):
        e0 = M(("Y", "Y"), "=", ("G", r"\frac{1}{s - a}"), r"\cdot", ("F", r"\frac{1}{s - c}"), size=1.15,
               colors={"G": PINK_C, "F": BLUE_C}).move_to([0, 2.7, 0])
        self.start(e0)

        # 1. convolution integral
        e1 = M(("y", "y(t)"), "=", ("i", r"\int_0^t"), ("g", "e^{a(t - T)}"), ("f", "e^{cT}"), ("dT", "dT"), size=1.1,
               colors={"g": PINK_C, "f": BLUE_C}).move_to([0, 1.3, 0])
        self.play(self.chip("g = e^(at), f = e^(ct)"), FadeIn(e1.ks("y", "=", "i", "dT")), run_time=0.8)
        self.play(TransformFromCopy(e0.k("G"), e1.k("g")), TransformFromCopy(e0.k("F"), e1.k("f")), run_time=1.3)
        self.step_done(e0, e1)

        # 2. compute
        e2 = M("=", ("ea", "e^{at}"), ("i", r"\int_0^t"), ("c", "e^{(c - a)T}"), ("dT", "dT"), "=", ("ea2", "e^{at}"),
               ("q", r"\frac{e^{(c-a)t} - 1}{c - a}"), size=1.05, colors={"ea": PINK_C, "ea2": PINK_C}).move_to([0.3, -0.15, 0])
        self.play(self.chip("pull e^(at) out of the integral"), TransformFromCopy(e1.ks("i", "g", "f", "dT"), e2.ks("ea", "i", "c", "dT")),
                  FadeIn(e2.all("=")[0]), run_time=1.5)
        self.play(FadeIn(e2.all("=")[1]), TransformFromCopy(e2.ks("ea", "c"), e2.ks("ea2", "q")), run_time=1.2)
        self.step_done(e0, e1, e2)

        # 3. same answer
        e3 = M(("y", "y"), "=", ("r", r"\frac{e^{ct} - e^{at}}{c - a}"), size=1.3, colors={"r": GREEN_C}).move_to([-1.8, -1.75, 0])
        n = label("= inverse of the partial fractions", 22, GREEN_C).move_to([3.0, -1.75, 0])
        self.play(self.chip("multiply out"), TransformFromCopy(e2.ks("ea2", "q"), e3.k("r")), FadeIn(e3.ks("y", "=")), run_time=1.4)
        self.play(FadeIn(n), ShowCreation(hbox(e3, GREEN_C)), run_time=0.8)
        self.step_done(e0, e1, e2, e3, n, hbox(e3, GREEN_C))
