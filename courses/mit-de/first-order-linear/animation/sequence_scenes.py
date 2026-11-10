"""ManimGL scenes for Unit 1, First Order Linear Equations (one scene per sequence in control_specs).

Rendered by build_sequences.py. Every step swaps the relation chip, animates the operation itself
(token substitutions, cancellations, matched coefficients, curves being built, the complex plane)
and ends with `step_done(...)`, which settles the scene to the listed mobjects.

Colour code: y and its pieces teal, the input q and its deposits blue, growth/rates yellow,
null solutions pink, results green, cancelled terms red.
Stage bounds: content stays within |x| <= 6.3 and -2.8 <= y <= 3.3 (chip sits bottom-left).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"y": TEAL_C, "yp": TEAL_C, "q": BLUE_C, "e": YELLOW_C, "et": YELLOW_C, "ems": YELLOW_C, "emt": YELLOW_C,
       "C": PINK_C, "null": PINK_C, "Y": GREEN_C, "M": YELLOW_C, "N": YELLOW_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def note(text, y, color=DIM, size=24):
    return label(text, size, color).move_to([0, y, 0])


# ======================================================================== Section 1

class CourseMapSequence(ControlScene):
    SEQ_ID = "course-map"

    def construct(self):
        eq = M(("dy", r"\frac{dy}{dt}"), "=", ("a", "a"), ("y", "y"), "+", ("q", "q(t)"), size=1.3).move_to([0, 2.2, 0])
        tag = note("first order, linear: the model equation of Unit 1", 1.2)
        self.start(eq, tag)

        # 1. nonlinear and second order
        b1 = block("y' = f(y)  nonlinear", w=4.4, h=0.8, color=TEAL_C, size=24).move_to([-3.2, 0.1, 0])
        b2 = block("m y'' + b y' + k y = f(t)", w=4.6, h=0.8, color=YELLOW_C, size=24).move_to([3.0, 0.1, 0])
        a1 = arrow(eq.get_bottom() + 0.2 * DOWN + 0.6 * LEFT, b1.get_top() + 0.05 * UP)
        a2 = arrow(eq.get_bottom() + 0.2 * DOWN + 0.6 * RIGHT, b2.get_top() + 0.05 * UP)
        self.play(self.chip("change the equation"), FadeOut(tag), run_time=0.6)
        self.play(grow_arrow(a1), FadeIn(b1, shift=0.2 * DOWN), run_time=0.9)
        self.play(grow_arrow(a2), FadeIn(b2, shift=0.2 * DOWN), run_time=0.9)
        self.step_done(eq, a1, a2, b1, b2)

        # 2. systems
        b3 = block("y' = A y  (vector y, matrix A)", w=6.2, h=0.8, color=BLUE_C, size=24).move_to([0, -1.25, 0])
        a3 = arrow(b2.get_bottom() + 0.05 * DOWN, b3.get_top() + 0.05 * UP + 1.2 * RIGHT)
        eig = note("eigenvectors uncouple n equations", -1.95, BLUE_C, 22)
        self.play(self.chip("many unknowns"), grow_arrow(a3), FadeIn(b3, shift=0.2 * DOWN), run_time=1.0)
        self.play(FadeIn(eig), run_time=0.6)
        self.step_done(eq, a1, a2, b1, b2, a3, b3, eig)

        # 3. numerics and PDEs
        b4 = block("Euler → ode45", w=3.2, h=0.75, color=GREEN_C, size=24).move_to([-3.3, -2.45, 0])
        b5 = block("u_t = u_xx ,  u_tt = u_xx", w=4.2, h=0.75, color=PINK_C, size=24).move_to([3.0, -2.45, 0])
        self.play(self.chip("where the series goes"), FadeOut(eig), run_time=0.5)
        self.play(FadeIn(b4, shift=0.2 * UP), FadeIn(b5, shift=0.2 * UP), run_time=1.0)
        self.play(Indicate(b4, color=GREEN_C), Indicate(b5, color=PINK_C), run_time=0.9)
        self.step_done(eq, a1, a2, b1, b2, a3, b3, b4, b5)


# ======================================================================== Section 2

class CalculusCheckSequence(ControlScene):
    SEQ_ID = "calculus-check"

    def construct(self):
        e0 = M(("y", "y"), "=", ("int", r"\int_0^t"), ("ets", "e^{t-s}"), ("q", "q(s)"), ("ds", "ds"), size=1.3).move_to([0, 1.6, 0])
        self.start(e0)

        # 1. split the exponential
        e1 = M(("y", "y"), "=", ("et", "e^{t}"), ("int", r"\int_0^t"), ("ems", "e^{-s}"), ("q", "q(s)"), ("ds", "ds"),
               size=1.3).move_to([0, 1.6, 0])
        side = M(("ets", "e^{t-s}"), "=", ("et", "e^{t}"), ("ems", "e^{-s}"), size=0.9).move_to([0, 0.2, 0])
        self.play(self.chip("e^(t-s) = e^t e^(-s)"), run_time=0.5)
        self.play(TransformFromCopy(e0.k("ets"), side.k("ets")), FadeIn(side.ks("=", "et", "ems")), run_time=1.0)
        self.play(self.tmorph(e0, e1, pairs=[("ets", "ems")]), run_time=1.3)
        self.play(TransformFromCopy(side.k("et"), e1.k("et").copy()), Indicate(e1.k("et"), color=YELLOW_C), run_time=0.8)
        self.step_done(e1, side)

        # 2. product rule
        top = e1.copy().scale(0.8).move_to([0, 2.6, 0])
        d1 = M(("yp", "y'"), "=", ("et", "e^{t}"), ("int", r"\int_0^t"), ("ems", "e^{-s}"), ("q", "q(s)"), ("ds", "ds"),
               "+", ("et2", "e^{t}"), ("dot", r"\cdot"), ("emt", "e^{-t}"), ("qt", "q(t)"), size=1.1,
               colors={"et2": YELLOW_C, "qt": BLUE_C}).move_to([0, 0.9, 0])
        b1 = under_bracket(d1.span("et", "ds"), YELLOW_C)
        b2 = under_bracket(d1.span("et2", "qt"), BLUE_C)
        l1 = label("(e^t)' times the integral", 20, YELLOW_C).next_to(b1, DOWN, buff=0.12)
        l2 = label("fundamental theorem", 20, BLUE_C).next_to(b2, DOWN, buff=0.12)
        self.play(self.chip("product rule"), FadeOut(side), ReplacementTransform(e1, top), run_time=0.8)
        self.play(FadeIn(d1.ks("yp", "=")), TransformFromCopy(top.span("et", "ds"), d1.span("et", "ds")), run_time=1.1)
        self.play(ShowCreation(b1), FadeIn(l1), run_time=0.7)
        self.play(FadeIn(d1.k("+")), TransformFromCopy(top.k("et"), d1.k("et2")), FadeIn(d1.k("dot")),
                  TransformFromCopy(top.ks("ems", "q"), d1.ks("emt", "qt")), run_time=1.2)
        self.play(ShowCreation(b2), FadeIn(l2), run_time=0.7)
        self.step_done(top, d1, b1, b2, l1, l2)

        # 3. recognise y and q
        r = M(("yp", "y'"), "=", ("y", "y"), "+", ("qt", "q(t)"), size=1.4, colors={"qt": BLUE_C}).move_to([0, -1.4, 0])
        one = M(("et2", "e^{t}"), ("emt", "e^{-t}"), "=", ("one", "1"), size=0.85).move_to([3.4, -0.2, 0])
        self.play(self.chip("first term is y; e^t e^(-t) = 1"), FadeOut(VGroup(l1, l2)), run_time=0.6)
        self.play(FadeIn(r.ks("yp", "=")), ReplacementTransform(d1.span("et", "ds").copy(), r.k("y")), run_time=1.1)
        self.play(FadeIn(one), run_time=0.6)
        self.play(FadeIn(r.k("+")), ReplacementTransform(d1.k("qt").copy(), r.k("qt")), run_time=1.0)
        box = hbox(r, GREEN_C)
        self.play(ShowCreation(box), run_time=0.6)
        self.step_done(top, d1, b1, b2, one, r, box)


class TangentTaylorSequence(ControlScene):
    SEQ_ID = "tangent-taylor"

    def construct(self):
        p = Plot(t_max=2.0, y_min=0.0, y_max=6.0, width=5.6, height=4.4, t_label="Δt", y_label="e^t").move_to([-2.7, 0.2, 0])
        curve = p.curve(lambda t: np.exp(t), color=TEAL_C, width=5)
        dot = Dot(p.c2p(0, 1), radius=0.07).set_fill(YELLOW_C)
        eq0 = M(("f", "f(t)"), "=", ("e", "e^{t}"), size=1.0).move_to([3.4, 2.4, 0])
        self.start(p, curve, dot, eq0)

        # 1. tangent line
        line = p.curve(lambda t: 1 + t, color=YELLOW_C, width=4)
        e1 = M(("f", r"f(\Delta t)"), r"\approx", ("one", "1"), "+", ("dt", r"\Delta t"), size=1.0).move_to([3.4, 1.4, 0])
        gap = DashedLine(p.c2p(1.8, 1 + 1.8), p.c2p(1.8, np.exp(1.8))).set_stroke(RED_C, 3)
        self.play(self.chip("height + step × slope"), run_time=0.5)
        self.play(ShowCreation(line), Write(e1), run_time=1.3)
        self.play(ShowCreation(gap), FadeIn(label("far from the curve", 20, RED_C).next_to(gap, RIGHT, buff=0.1)), run_time=0.8)
        self.step_done(p, curve, dot, eq0, line, e1, gap)

        # 2. tangent parabola
        para = p.curve(lambda t: 1 + t + t * t / 2, color=GREEN_C, width=4)
        e2 = M(("f", r"f(\Delta t)"), r"\approx", ("one", "1"), "+", ("dt", r"\Delta t"), "+", ("half", r"\frac{1}{2}"),
               ("dt2", r"(\Delta t)^2"), size=1.0, colors={"half": GREEN_C, "dt2": GREEN_C}).move_to([3.3, 0.2, 0])
        gap2 = DashedLine(p.c2p(1.8, 1 + 1.8 + 1.62), p.c2p(1.8, np.exp(1.8))).set_stroke(RED_C, 3)
        self.play(self.chip("add the bending"), FadeOut(gap), run_time=0.5)
        self.play(TransformFromCopy(e1, e2.span("f", "dt")), FadeIn(e2.ks("+", "half", "dt2"), shift=0.1 * UP), run_time=1.1)
        self.play(ShowCreation(para), run_time=1.0)
        self.play(ShowCreation(gap2), run_time=0.5)
        self.step_done(p, curve, dot, eq0, line, e1, para, e2, gap2)

        # 3. Taylor series
        e3 = M(("e", "e^{t}"), "=", ("one", "1"), "+", ("t1", "t"), "+", ("t2", r"\frac{t^2}{2!}"), "+",
               ("t3", r"\frac{t^3}{3!}"), "+", ("dots", r"\cdots"), size=1.0).move_to([3.1, -1.2, 0])
        cubic = p.curve(lambda t: 1 + t + t * t / 2 + t ** 3 / 6, color=BLUE_C, width=3)
        self.play(self.chip("all derivatives"), FadeOut(gap2), run_time=0.5)
        self.play(Write(e3), run_time=1.4)
        self.play(ShowCreation(cubic), run_time=0.9)
        self.play(Indicate(e3.k("dots"), color=GREEN_C), FadeIn(note("each term: (Δt)^n f^(n) / n!", -2.2, DIM, 22).shift(3.1 * RIGHT)),
                  run_time=0.8)
        self.step_done(p, curve, dot, eq0, line, para, cubic, e1, e2, e3,
                       note("each term: (Δt)^n f^(n) / n!", -2.2, DIM, 22).shift(3.1 * RIGHT))


# ======================================================================== Section 3

class ExponentialResponseSequence(ControlScene):
    SEQ_ID = "exponential-response"

    def construct(self):
        e0 = M(("yp", "y'"), "=", ("a", "a"), ("y", "y"), "+", ("in", "e^{st}"), size=1.4,
               colors={"in": BLUE_C}).move_to([0, 2.3, 0])
        self.start(e0)

        # 1. substitute
        guess = M(("y", "y"), "=", ("Y", "Y"), ("e", "e^{st}"), size=1.0).move_to([-3.6, 1.1, 0])
        e1 = M(("s", "s"), ("Y", "Y"), ("e", "e^{st}"), "=", ("a", "a"), ("Y2", "Y", GREEN_C), ("e2", "e^{st}", YELLOW_C), "+",
               ("in", "e^{st}"), size=1.3, colors={"in": BLUE_C, "s": YELLOW_C}).move_to([0, 0.6, 0])
        self.play(self.chip("try y = Y e^(st)"), FadeIn(guess, shift=0.1 * RIGHT), run_time=0.8)
        self.play(TransformFromCopy(e0.k("yp"), e1.ks("s", "Y", "e")), TransformFromCopy(e0.k("="), e1.k("=")),
                  TransformFromCopy(e0.k("a"), e1.k("a")), TransformFromCopy(e0.k("y"), e1.ks("Y2", "e2")),
                  TransformFromCopy(e0.k("+"), e1.k("+")), TransformFromCopy(e0.k("in"), e1.k("in")), run_time=1.4)
        self.play(Indicate(e1.k("s"), color=YELLOW_C), run_time=0.6)
        self.step_done(e0, guess, e1)

        # 2. divide by e^{st}
        strikes = VGroup(*[strike(e1.k(k)) for k in ("e", "e2", "in")])
        e2 = M(("sa", "(s-a)"), ("Y", "Y"), "=", ("one", "1"), size=1.3).move_to([-1.6, -0.8, 0])
        yv = M(("Y", "Y"), "=", size=1.3, colors={"Y": GREEN_C})
        fr = Frac(M(("one", "1"), size=1.3), M(("sa", "s-a"), size=1.3))
        res = VGroup(yv, fr).arrange(RIGHT, buff=0.2).move_to([2.6, -0.8, 0])
        self.play(self.chip("divide by e^(st) ≠ 0"), LaggedStart(*[ShowCreation(s) for s in strikes], lag_ratio=0.3), run_time=1.1)
        self.play(TransformFromCopy(e1.ks("s", "a"), e2.k("sa")), TransformFromCopy(e1.k("Y"), e2.k("Y")),
                  FadeIn(e2.ks("=", "one")), run_time=1.2)
        self.play(FadeIn(yv), TransformFromCopy(e2.k("one"), fr.num), FadeIn(fr.bar), TransformFromCopy(e2.k("sa"), fr.den), run_time=1.1)
        box = hbox(res, GREEN_C)
        self.play(ShowCreation(box), run_time=0.5)
        self.step_done(e0, e1, strikes, e2, res, box)

        # 3. add a null solution
        lhs = M(("y", "y"), "=", size=1.3)
        f2 = Frac(M(("in", "e^{st}"), size=1.2, colors={"in": BLUE_C}), M(("sa", "s-a"), size=1.2))
        rhs = M("+", ("C", "C"), ("eat", "e^{at}"), size=1.3, colors={"eat": PINK_C})
        full = VGroup(lhs, f2, rhs).arrange(RIGHT, buff=0.22).move_to([0, 0.4, 0])
        nl = note("Ce^(at) solves y' = ay: the null solution", -0.9, PINK_C, 24)
        self.play(self.chip("particular + null"), FadeOut(VGroup(e1, strikes, e2, box, guess)),
                  res.animate.scale(0.7).move_to([4.6, 2.3, 0]), run_time=0.9)
        self.play(FadeIn(lhs), FadeIn(f2), run_time=0.8)
        self.play(FadeIn(rhs, shift=0.2 * LEFT), FadeIn(nl), run_time=0.9)
        self.step_done(e0, res, lhs, f2, rhs, nl)

        # 4. match y(0) and regroup
        c = M(("C", "C"), "=", ("y0", "y(0)"), "-", size=1.0)
        cf = Frac(M(("one", "1"), size=0.9), M(("sa", "s-a"), size=0.9))
        cg = VGroup(c, cf).arrange(RIGHT, buff=0.15).move_to([0, -0.9, 0])
        l2 = M(("y", "y"), "=", ("y0", "y(0)"), ("eat", "e^{at}"), "+", size=1.25, colors={"eat": PINK_C, "y0": PINK_C})
        f3 = Frac(M(("in", "e^{st}"), "-", ("eat", "e^{at}"), size=1.15, colors={"in": BLUE_C}), M(("sa", "s-a"), size=1.15))
        fin = VGroup(l2, f3).arrange(RIGHT, buff=0.2).move_to([0, -2.1, 0])
        self.play(self.chip("t = 0 fixes C"), FadeOut(nl), FadeIn(cg, shift=0.1 * DOWN), run_time=1.0)
        self.play(FadeIn(l2), TransformFromCopy(f2, f3), run_time=1.3)
        tag = label("input part: 0 at t = 0", 20, BLUE_C).next_to(f3, RIGHT, buff=0.25)
        self.play(FadeIn(tag), ShowCreation(hbox(fin, GREEN_C)), run_time=0.8)
        self.step_done(e0, res, lhs, f2, rhs, cg, fin, tag, hbox(fin, GREEN_C))


class ResonanceSequence(ControlScene):
    SEQ_ID = "resonance"

    def construct(self):
        lhs = M(("v", r"y_{vp}"), "=", size=1.3)
        f0 = Frac(M(("est", "e^{st}"), "-", ("eat", "e^{at}"), size=1.3, colors={"est": BLUE_C, "eat": PINK_C}),
                  M(("s", "s"), "-", ("a", "a"), size=1.3))
        g0 = VGroup(lhs, f0).arrange(RIGHT, buff=0.2).move_to([0, 2.0, 0])
        self.start(g0)

        # 1. s -> a
        f1 = Frac(M(("est", "e^{at}"), "-", ("eat", "e^{at}"), size=1.2, colors={"est": RED_C, "eat": RED_C}),
                  M(("s", "a"), "-", ("a", "a"), size=1.2, colors={"s": RED_C}))
        z = M("=", ("zz", r"\frac{0}{0}"), size=1.2, colors={"zz": RED_C})
        g1 = VGroup(f1, z).arrange(RIGHT, buff=0.25).move_to([0, 0.2, 0])
        self.play(self.chip("s → a"), run_time=0.5)
        self.play(TransformFromCopy(f0, f1), run_time=1.2)
        self.play(FadeIn(z, shift=0.2 * LEFT), run_time=0.7)
        self.play(FadeIn(note("not infinite: undecided", -1.2, ORANGE_C)), run_time=0.6)
        self.step_done(g0, g1, note("not infinite: undecided", -1.2, ORANGE_C))

        # 2. l'Hopital in s
        num = M(("d", r"\partial_s"), ("p", r"(e^{st} - e^{at})"), "=", ("t", "t"), ("est", "e^{st}"), size=1.0,
                colors={"t": YELLOW_C, "est": BLUE_C}).move_to([-2.4, 0.2, 0])
        den = M(("d", r"\partial_s"), ("p", "(s - a)"), "=", ("one", "1"), size=1.0).move_to([3.0, 0.2, 0])
        self.play(self.chip("l'Hôpital: differentiate in s"), FadeOut(g1), FadeOut(note("not infinite: undecided", -1.2, ORANGE_C)),
                  run_time=0.7)
        self.play(FadeIn(num.ks("d", "p", "=")), run_time=0.6)
        self.play(FadeIn(num.ks("t", "est"), shift=0.1 * UP), Indicate(num.k("t"), color=YELLOW_C), run_time=1.1)
        self.play(FadeIn(den), run_time=0.8)
        self.step_done(g0, num, den)

        # 3. result and picture
        r = M(("v", r"y_{vp}"), "=", ("t", "t"), ("eat", "e^{at}"), size=1.3, colors={"t": YELLOW_C, "eat": PINK_C}).move_to([-3.4, -0.9, 0])
        p = Plot(t_max=3.0, y_min=0, y_max=6, width=4.6, height=2.6, y_label="a = 0.5").move_to([3.0, -1.3, 0])
        cr = p.curve(lambda t: t * np.exp(0.5 * t), color=YELLOW_C, width=5)
        cn = p.curve(lambda t: np.exp(0.5 * t), color=PINK_C, width=3)
        kl = label("t e^(at)", 20, YELLOW_C).next_to(p.c2p(3.0, 3 * np.exp(1.5) if 3 * np.exp(1.5) < 6 else 6), LEFT, buff=0.1)
        self.play(self.chip("set s = a"), FadeOut(VGroup(num, den)), run_time=0.6)
        self.play(TransformFromCopy(g0[0], r.ks("v", "=")), FadeIn(r.ks("t", "eat")), run_time=1.0)
        self.play(FadeIn(p), ShowCreation(cn), run_time=0.8)
        self.play(ShowCreation(cr), FadeIn(kl), run_time=1.1)
        self.step_done(g0, r, p, cn, cr, kl)


# ======================================================================== Section 4

class CosineResponseSequence(ControlScene):
    SEQ_ID = "cosine-response"

    def construct(self):
        e0 = M(("yp", "y'"), "=", ("a", "a"), ("y", "y"), "+", ("in", r"\cos\omega t"), size=1.3,
               colors={"in": BLUE_C}).move_to([0, 2.5, 0])
        self.start(e0)

        # 1. guess
        g = M(("y", "y_p"), "=", ("M", "M"), ("c", r"\cos\omega t"), "+", ("N", "N"), ("s", r"\sin\omega t"),
              size=1.2).move_to([0, 1.3, 0])
        self.play(self.chip("cosine AND sine"), run_time=0.5)
        self.play(Write(g), run_time=1.2)
        self.play(Indicate(g.ks("M", "N"), color=YELLOW_C), run_time=0.7)
        self.step_done(e0, g)

        # 2. substitute and match
        lhs = M(("l", "y_p'"), "=", ("m1", r"-\omega M"), ("s1", r"\sin\omega t"), "+", ("n1", r"\omega N"), ("c1", r"\cos\omega t"),
                size=0.95, colors={"s1": PINK_C, "c1": BLUE_C}).move_to([0, 0.35, 0])
        rhs = M("=", ("am", "aM"), ("c2", r"\cos\omega t"), "+", ("an", "aN"), ("s2", r"\sin\omega t"), "+", ("c3", r"\cos\omega t"),
                size=0.95, colors={"s2": PINK_C, "c2": BLUE_C, "c3": BLUE_C}).move_to([0.4, -0.45, 0])
        eqc = M(("lab", r"\cos:"), ("x", r"-aM + \omega N = 1"), size=1.0, colors={"lab": BLUE_C}).move_to([-3.1, -1.6, 0])
        eqs = M(("lab", r"\sin:"), ("x", r"-\omega M - aN = 0"), size=1.0, colors={"lab": PINK_C}).move_to([3.1, -1.6, 0])
        self.play(self.chip("substitute"), FadeIn(lhs, shift=0.1 * DOWN), run_time=1.1)
        self.play(FadeIn(rhs, shift=0.1 * DOWN), run_time=1.0)
        self.play(Indicate(VGroup(lhs.k("c1"), rhs.k("c2"), rhs.k("c3")), color=BLUE_C), run_time=0.8)
        self.play(FadeIn(eqc, shift=0.1 * UP), run_time=0.7)
        self.play(Indicate(VGroup(lhs.k("s1"), rhs.k("s2")), color=PINK_C), run_time=0.8)
        self.play(FadeIn(eqs, shift=0.1 * UP), run_time=0.7)
        self.step_done(e0, g, lhs, rhs, eqc, eqs)

        # 3. solve
        mres = VGroup(M(("M", "M"), "=", size=1.1), Frac(M(("x", "-a"), size=1.0), M(("d", r"\omega^2+a^2"), size=1.0))).arrange(RIGHT, buff=0.15)
        nres = VGroup(M(("N", "N"), "=", size=1.1), Frac(M(("x", r"\omega"), size=1.0), M(("d", r"\omega^2+a^2"), size=1.0))).arrange(RIGHT, buff=0.15)
        both = VGroup(mres, nres).arrange(RIGHT, buff=1.2).move_to([0, 0.0, 0])
        self.play(self.chip("two equations, two unknowns"), FadeOut(VGroup(lhs, rhs)),
                  eqc.animate.move_to([-3.1, 0.9, 0]), eqs.animate.move_to([3.1, 0.9, 0]), run_time=0.9)
        self.play(FadeIn(mres, shift=0.1 * UP), run_time=0.9)
        self.play(FadeIn(nres, shift=0.1 * UP), run_time=0.9)
        self.step_done(e0, g, eqc, eqs, both)

        # 4. polar form: point (M, N), length G, angle alpha  (picture for a = -1, w = 1)
        o = np.array([-4.2, -1.9, 0])
        sc = 3.0
        mn = np.array([0.5, 0.5, 0]) * sc
        ax_x = Arrow(o + 0.2 * LEFT, o + RIGHT * 2.4, buff=0).set_stroke(DIM, 2)
        ax_y = Arrow(o + 0.2 * DOWN, o + UP * 2.0, buff=0).set_stroke(DIM, 2)
        pt = Dot(o + mn, radius=0.08).set_fill(YELLOW_C)
        rad = Line(o, o + mn).set_stroke(GREEN_C, 5)
        ang = Arc(radius=0.55, start_angle=0, angle=PI / 4, arc_center=o).set_stroke(YELLOW_C, 3)
        lab = VGroup(label("(M, N)", 20, YELLOW_C).next_to(pt, UR, buff=0.05), label("G", 22, GREEN_C).next_to(rad.get_center(), UL, buff=0.08),
                     label("α", 22, YELLOW_C).move_to(o + 0.8 * np.array([np.cos(PI / 8), np.sin(PI / 8), 0])))
        pol = M(("y", "y_p"), "=", ("G", "G"), ("c", r"\cos(\omega t - \alpha)"), size=1.1, colors={"G": GREEN_C}).move_to([2.1, -1.0, 0])
        gs = VGroup(M(("G", "G"), "=", size=1.0, colors={"G": GREEN_C}),
                    Frac(M(("one", "1"), size=0.9), M(("r", r"\sqrt{\omega^2+a^2}"), size=0.9))).arrange(RIGHT, buff=0.12).move_to([2.1, -2.3, 0])
        self.play(self.chip("polar coordinates of (M, N)"), FadeOut(VGroup(eqc, eqs)), both.animate.scale(0.75).move_to([2.1, 0.25, 0]), run_time=0.8)
        self.play(FadeIn(VGroup(ax_x, ax_y)), FadeIn(pt), FadeIn(lab[0]), run_time=0.8)
        self.play(ShowCreation(rad), FadeIn(lab[1]), ShowCreation(ang), FadeIn(lab[2]), run_time=1.0)
        self.play(Write(pol), run_time=1.0)
        self.play(FadeIn(gs, shift=0.1 * UP), run_time=0.8)
        self.step_done(e0, g, both, ax_x, ax_y, pt, rad, ang, lab, pol, gs)


# ======================================================================== Section 5

class AnyInputSequence(ControlScene):
    SEQ_ID = "any-input"

    def construct(self):
        a = 0.35
        p = Plot(t_max=4.0, y_min=0, y_max=5, width=6.0, height=3.6, t_label="time", y_label="balance").move_to([-2.4, 0.3, 0])
        e0 = M(("yp", "y'"), "=", ("a", "a"), ("y", "y"), "+", ("q", "q(t)"), size=1.0).move_to([4.0, 2.4, 0])
        self.start(p, e0)

        # 1. starting deposit grows
        y0 = 1.0
        cn = p.curve(lambda t: y0 * np.exp(a * t), color=PINK_C, width=5)
        f1 = M(("y0", "y(0)"), ("e", "e^{at}"), size=1.0, colors={"y0": PINK_C}).move_to([4.0, 1.3, 0])
        self.play(self.chip("no deposits yet"), FadeIn(Dot(p.c2p(0, y0), radius=0.07).set_fill(PINK_C)), run_time=0.6)
        self.play(ShowCreation(cn), Write(f1), run_time=1.3)
        self.step_done(p, e0, cn, f1, Dot(p.c2p(0, y0), radius=0.07).set_fill(PINK_C))

        # 2. one deposit at time s grows over t - s
        s0, t1 = 1.2, 4.0
        bar = Line(p.c2p(s0, 0), p.c2p(s0, 0.5)).set_stroke(BLUE_C, 8)
        grow = p.curve(lambda t: 0.5 * np.exp(a * (t - s0)), t0=s0, t1=t1, color=BLUE_C, width=4)
        mid = (p.c2p(s0, -0.35) + p.c2p(t1, -0.35)) / 2
        brace = VGroup(Arrow(mid, p.c2p(s0, -0.35), buff=0), Arrow(mid, p.c2p(t1, -0.35), buff=0)).set_stroke(YELLOW_C, 3).set_fill(YELLOW_C)
        bl = label("t − s", 20, YELLOW_C).next_to(brace, DOWN, buff=0.05)
        f2 = M(("q", "q(s)"), ("ds", "ds"), r"\longrightarrow", ("e", "e^{a(t-s)}"), ("q2", "q(s)"), ("ds2", "ds"), size=0.95,
               colors={"q2": BLUE_C}).move_to([3.8, 0.1, 0])
        self.play(self.chip("deposit at time s"), ShowCreation(bar), run_time=0.7)
        self.play(ShowCreation(grow), GrowFromCenter(brace), FadeIn(bl), run_time=1.3)
        self.play(Write(f2), run_time=1.0)
        self.step_done(p, e0, cn, f1, bar, grow, brace, bl, f2)

        # 3. many deposits add up: the integral
        bars, curves = VGroup(), VGroup()
        for s in np.arange(0.2, 3.9, 0.4):
            bars.add(Line(p.c2p(s, 0), p.c2p(s, 0.25)).set_stroke(BLUE_C, 6))
            curves.add(p.curve(lambda t, s=s: 0.25 * np.exp(a * (t - s)), t0=s, t1=t1, color=BLUE_C, width=2).set_stroke(opacity=0.6))
        q_const = 0.625  # 0.25 per 0.4 time
        total = p.curve(lambda t: y0 * np.exp(a * t) + q_const * (np.exp(a * t) - 1) / a, color=GREEN_C, width=5)
        f3 = M(("y", "y(t)"), "=", ("y0", "y(0)"), ("e", "e^{at}"), "+", ("int", r"\int_0^t"), ("g", "e^{a(t-s)}"), ("q", "q(s)"),
               ("ds", "ds"), size=0.95, colors={"y0": PINK_C}).move_to([2.6, -2.25, 0])
        self.play(self.chip("linear: contributions add"), FadeOut(VGroup(bar, grow, brace, bl)), run_time=0.6)
        self.play(LaggedStart(*[ShowCreation(b) for b in bars], lag_ratio=0.1), run_time=1.0)
        self.play(LaggedStart(*[ShowCreation(c) for c in curves], lag_ratio=0.1), run_time=1.3)
        self.play(ShowCreation(total), Write(f3), run_time=1.4)
        self.step_done(p, e0, cn, f1, f2, bars, curves, total, f3)


# ======================================================================== Section 6

class StepDeltaSequence(ControlScene):
    SEQ_ID = "step-delta"

    def construct(self):
        T = 1.5
        p1 = Plot(t_max=4.0, y_min=-0.2, y_max=1.4, width=5.2, height=1.8, y_label="H(t − T)").move_to([-3.2, 1.9, 0])
        h0 = p1.curve(lambda t: 0.0, t1=T, color=BLUE_C, width=5)
        h1 = p1.curve(lambda t: 1.0, t0=T, color=BLUE_C, width=5)
        jump = DashedLine(p1.c2p(T, 0), p1.c2p(T, 1)).set_stroke(BLUE_C, 2)
        tl = label("T", 20, DIM).next_to(p1.c2p(T, 0), DOWN, buff=0.08)
        self.start(p1, h0, h1, jump, tl)

        # 1. derivative: delta
        p2 = Plot(t_max=4.0, y_min=-0.2, y_max=1.4, width=5.2, height=1.8, y_label="δ(t − T)").move_to([-3.2, -0.6, 0])
        d0 = p2.curve(lambda t: 0.0, color=YELLOW_C, width=4)
        spike = Arrow(p2.c2p(T, 0), p2.c2p(T, 1.35), buff=0).set_stroke(YELLOW_C, 6)
        e1 = M(("i", r"\int"), ("d", r"\delta(t-T)"), ("dt", "dt"), "=", ("one", "1"), size=1.0,
               colors={"d": YELLOW_C}).move_to([3.0, 1.2, 0])
        self.play(self.chip("slope of the step"), FadeIn(p2), run_time=0.6)
        self.play(ShowCreation(d0), run_time=0.7)
        self.play(TransformFromCopy(jump, spike), run_time=1.0)
        self.play(Write(e1), run_time=0.9)
        self.step_done(p1, h0, h1, jump, tl, p2, d0, spike, e1)

        # 2. sifting
        e2 = M(("i", r"\int"), ("d", r"\delta(t-T)"), ("f", "f(t)"), ("dt", "dt"), "=", ("fT", "f(T)"), size=1.0,
               colors={"d": YELLOW_C, "fT": GREEN_C}).move_to([3.0, 0.1, 0])
        self.play(self.chip("only t = T counts"), TransformFromCopy(e1.ks("i", "d"), e2.ks("i", "d")),
                  FadeIn(e2.ks("f", "dt", "=")), run_time=1.1)
        self.play(FadeIn(e2.k("fT"), shift=0.1 * LEFT), Indicate(spike, color=GREEN_C), run_time=0.9)
        self.step_done(p1, h0, h1, jump, tl, p2, d0, spike, e1, e2)

        # 3. impulse response y = H(t-T) e^{a(t-T)}, a = -0.7
        a = -0.7
        p3 = Plot(t_max=4.0, y_min=-0.2, y_max=1.4, width=5.2, height=1.8, y_label="y, a < 0").move_to([3.0, -1.6, 0])
        r0 = p3.curve(lambda t: 0.0, t1=T, color=TEAL_C, width=5)
        r1 = p3.curve(lambda t: np.exp(a * (t - T)), t0=T, color=TEAL_C, width=5)
        rj = DashedLine(p3.c2p(T, 0), p3.c2p(T, 1)).set_stroke(TEAL_C, 2)
        e3 = M(("y", "y"), "=", ("H", "H(t-T)"), ("g", "e^{a(t-T)}"), size=0.95, colors={"H": BLUE_C, "g": YELLOW_C}).move_to([3.0, -0.35, 0])
        self.play(self.chip("deposit one unit at T"), FadeOut(VGroup(e1, e2)), run_time=0.5)
        self.play(FadeIn(p3), ShowCreation(r0), run_time=0.8)
        self.play(TransformFromCopy(spike, rj), run_time=0.7)
        self.play(ShowCreation(r1), Write(e3), run_time=1.2)
        self.step_done(p1, h0, h1, jump, tl, p2, d0, spike, p3, r0, rj, r1, e3)


# ======================================================================== Section 7

class ComplexPolarSequence(ControlScene):
    SEQ_ID = "complex-polar"

    def construct(self):
        top = VGroup(M(("Y", "Y"), "=", size=1.2, colors={"Y": GREEN_C}),
                     Frac(M(("one", "1"), size=1.1), M(("iw", r"i\omega"), "-", ("a", "a"), size=1.1))).arrange(RIGHT, buff=0.15).move_to([3.2, 2.4, 0])
        self.start(top)

        # picture for a = -1, w = 1.5:  i w - a = 1 + 1.5 i
        o = np.array([-4.5, -1.6, 0])
        sc = 1.9
        z = np.array([1.0, 1.5, 0]) * sc
        # 1. place the number
        rx = Arrow(o + 0.3 * LEFT, o + 3.0 * RIGHT, buff=0).set_stroke(DIM, 2)
        iy = Arrow(o + 0.3 * DOWN, o + 3.6 * UP, buff=0).set_stroke(DIM, 2)
        axl = VGroup(label("real", 18, DIM).next_to(rx, RIGHT, buff=0.05), label("imaginary", 18, DIM).next_to(iy, UP, buff=0.05))
        dz = Dot(o + z, radius=0.08).set_fill(YELLOW_C)
        h = DashedLine(o, o + z * np.array([1, 0, 0])).set_stroke(TEAL_C, 3)
        v = DashedLine(o + z * np.array([1, 0, 0]), o + z).set_stroke(PINK_C, 3)
        hl = label("−a", 20, TEAL_C).next_to(h, DOWN, buff=0.06)
        vl = label("ω", 20, PINK_C).next_to(v, RIGHT, buff=0.06)
        rr = Line(o, o + z).set_stroke(GREEN_C, 5)
        rl = label("R", 22, GREEN_C).next_to(rr.get_center(), UL, buff=0.06)
        arc = Arc(radius=0.6, start_angle=0, angle=np.arctan2(1.5, 1.0), arc_center=o).set_stroke(YELLOW_C, 3)
        al = label("α", 22, YELLOW_C).move_to(o + 0.85 * np.array([np.cos(0.49), np.sin(0.49), 0]))
        e1 = M(("iw", r"i\omega - a"), "=", ("R", "R"), ("ea", r"e^{i\alpha}"), size=1.05, colors={"R": GREEN_C, "ea": YELLOW_C}).move_to([2.6, 1.0, 0])
        r1 = M(("R", "R"), "=", ("sq", r"\sqrt{a^2+\omega^2}"), size=1.0, colors={"R": GREEN_C}).move_to([2.6, 0.0, 0])
        self.play(self.chip("complex plane"), FadeIn(VGroup(rx, iy, axl)), run_time=0.7)
        self.play(ShowCreation(h), FadeIn(hl), run_time=0.7)
        self.play(ShowCreation(v), FadeIn(vl), FadeIn(dz), run_time=0.7)
        self.play(ShowCreation(rr), FadeIn(rl), ShowCreation(arc), FadeIn(al), run_time=1.0)
        self.play(Write(e1), FadeIn(r1, shift=0.1 * UP), run_time=1.2)
        pic = VGroup(rx, iy, axl, h, v, hl, vl, dz, rr, rl, arc, al)
        self.step_done(top, pic, e1, r1)

        # 2. divide in polar form
        e2 = M(("yc", "y_c"), "=", ("inv", r"\frac{1}{R}"), ("ema", r"e^{-i\alpha}"), ("ew", r"e^{i\omega t}"), "=",
               ("inv2", r"\frac{1}{R}"), ("all", r"e^{i(\omega t - \alpha)}"), size=1.0,
               colors={"inv": GREEN_C, "inv2": GREEN_C, "ema": YELLOW_C, "all": YELLOW_C}).move_to([2.2, -1.1, 0])
        self.play(self.chip("divide: 1/R, angle −α"), run_time=0.5)
        self.play(FadeIn(e2.span("yc", "ew")), run_time=1.1)
        self.play(TransformFromCopy(e2.ks("ema", "ew"), e2.k("all")), FadeIn(e2.ks("inv2")), FadeIn(e2.k("=", 1)), run_time=1.1)
        self.step_done(top, pic, e1, r1, e2)

        # 3. real part
        e3 = M(("re", r"\mathrm{Re}\,y_c"), "=", ("inv", r"\frac{1}{R}"), ("c", r"\cos(\omega t - \alpha)"), size=1.1,
               colors={"inv": GREEN_C, "c": TEAL_C}).move_to([2.2, -2.3, 0])
        self.play(self.chip("real part answers cos ωt"), run_time=0.5)
        self.play(TransformFromCopy(e2.ks("inv2", "all"), e3.ks("inv", "c")), FadeIn(e3.ks("re", "=")), run_time=1.2)
        self.play(ShowCreation(hbox(e3, GREEN_C)), run_time=0.6)
        self.step_done(top, pic, e1, r1, e2, e3, hbox(e3, GREEN_C))


# ======================================================================== Section 8

class IntegratingFactorSequence(ControlScene):
    SEQ_ID = "integrating-factor"

    def construct(self):
        e0 = M(("yp", "y'"), "=", ("a", "a(t)"), ("y", "y"), "+", ("q", "q(t)"), size=1.3,
               colors={"a": YELLOW_C}).move_to([0, 2.6, 0])
        self.start(e0)

        # 1. choose M
        m1 = M(("Mp", "M'"), "=", ("ma", "-a(t)"), ("M", "M"), size=1.1, colors={"ma": YELLOW_C}).move_to([-3.0, 1.5, 0])
        m2 = M(("M", "M(t)"), "=", ("e", r"e^{-\int_0^t a}"), size=1.1).move_to([3.0, 1.5, 0])
        self.play(self.chip("null equation, minus sign"), Write(m1), run_time=1.1)
        self.play(FadeIn(m2, shift=0.1 * LEFT), run_time=1.0)
        self.step_done(e0, m1, m2)

        # 2. product rule and cancellation
        d = M(("l", "(My)'"), "=", ("M1", "M"), ("yp", "y'"), "+", ("Mp", "M'"), ("y", "y"), "=", ("M2", "M"), ("ay", "a y"), "+",
              ("M3", "M"), ("q", "q"), "-", ("M4", "a M"), ("y2", "y"), size=1.0, colors={"ay": YELLOW_C, "M4": YELLOW_C}).move_to([0, 0.3, 0])
        self.play(self.chip("product rule"), FadeIn(d.span("l", "y"), shift=0.1 * DOWN), run_time=1.1)
        self.play(FadeIn(d.span("M2", "y2"), shift=0.1 * DOWN), run_time=1.1)
        s1 = strike(d.ks("M2", "ay"))
        s2 = strike(d.ks("M4", "y2"))
        self.play(ShowCreation(s1), ShowCreation(s2), run_time=0.8)
        res = M(("l", "(My)'"), "=", ("M", "M"), ("q", "q"), size=1.3, colors={"q": BLUE_C}).move_to([0, -0.9, 0])
        self.play(FadeIn(res.ks("l", "=")), TransformFromCopy(d.ks("M3", "q"), res.ks("M", "q")), run_time=1.0)
        self.play(ShowCreation(hbox(res, GREEN_C)), run_time=0.5)
        self.step_done(e0, m1, m2, d, s1, s2, res, hbox(res, GREEN_C))

        # 3. integrate and divide
        it = M(("Mt", "M(t)y(t)"), "-", ("y0", "y(0)"), "=", ("int", r"\int_0^t M(s)q(s)ds"), size=1.0).move_to([0, 0.3, 0])
        sol = M(("y", "y(t)"), "=", ("g0", r"e^{\int_0^t a}"), ("y0", "y(0)"), "+", ("int", r"\int_0^t"), ("g", r"e^{\int_s^t a}"),
                ("q", "q(s)ds"), size=1.05, colors={"g0": YELLOW_C, "g": YELLOW_C, "q": BLUE_C}).move_to([0, -1.1, 0])
        self.play(self.chip("integrate from 0 to t"), FadeOut(VGroup(d, s1, s2)), res.animate.scale(0.75).move_to([4.6, 1.5 - 0.0, 0]),
                  FadeOut(m1), m2.animate.move_to([-3.4, 1.5, 0]), run_time=0.9)
        self.play(Write(it), run_time=1.2)
        self.play(FadeIn(sol, shift=0.1 * DOWN), run_time=1.2)
        self.play(FadeIn(label("divide by M(t): M(s)/M(t) = growth from s to t", 20, DIM).move_to([0, -2.0, 0])), run_time=0.7)
        self.step_done(e0, m2, res, it, sol, label("divide by M(t): M(s)/M(t) = growth from s to t", 20, DIM).move_to([0, -2.0, 0]))

        # 4. example a = 2t
        ex1 = M(("a", "a = 2t"), r"\;\Rightarrow\;", ("M", "M = e^{-t^2}"), size=1.0, colors={"a": YELLOW_C}).move_to([0, 0.4, 0])
        ex2 = M(("y", "y(t)"), "=", ("g0", "e^{t^2}"), ("y0", "y(0)"), "+", ("int", r"\int_0^t"), ("g", "e^{t^2 - s^2}"),
                ("q", "q(s)ds"), size=1.1, colors={"g0": YELLOW_C, "g": YELLOW_C, "q": BLUE_C}).move_to([0, -0.9, 0])
        self.play(self.chip("a(t) = 2t"), FadeOut(it), sol.animate.scale(0.8).move_to([0, 1.5 - 0.1, 0]), FadeOut(m2), FadeOut(res),
                  FadeOut(label("divide by M(t): M(s)/M(t) = growth from s to t", 20, DIM).move_to([0, -2.0, 0])), run_time=0.9)
        self.play(Write(ex1), run_time=1.0)
        self.play(TransformFromCopy(sol, ex2), run_time=1.3)
        self.play(Indicate(ex2.k("g"), color=YELLOW_C), run_time=0.7)
        self.step_done(e0, sol, ex1, ex2)
