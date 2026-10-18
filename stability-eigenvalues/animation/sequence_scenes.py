"""ManimGL scenes for the Stability and Eigenvalues study companion (one scene per sequence in control_specs).

Rendered by build_sequences.py. Every step starts by swapping the relation chip, animates the actual
operation (token morphs, exponent splitting, eigenvalues moving across the axis, powers spiralling,
lines mapped point by point by the exponential) and ends with `step_done(...)`, which settles the scene
to exactly the listed mobjects.

Colour code: x and its samples teal, T / T~ blue, T^{-1} pink, e^{Dt} / eigenvalue modes yellow, the
real part a yellow and the imaginary part b pink, eigenvectors orange, z green, stable green, unstable red.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"x": TEAL_C, "x0": TEAL_C, "xk": TEAL_C, "xk1": TEAL_C, "xN": TEAL_C, "x1": TEAL_C, "x2": TEAL_C, "x3": TEAL_C,
       "T": BLUE_C, "Tx": BLUE_C, "Ti": PINK_C, "Tix": PINK_C, "eD": YELLOW_C, "m1": YELLOW_C, "mn": YELLOW_C, "m2": YELLOW_C,
       "lam": YELLOW_C, "c1": ORANGE_C, "cn": ORANGE_C, "c2": ORANGE_C, "z1": GREEN_C, "zn": GREEN_C, "z2": GREEN_C,
       "a": YELLOW_C, "ib": PINK_C, "eat": YELLOW_C, "eibt": PINK_C, "At": BLUE_C, "AN": BLUE_C, "A3": BLUE_C,
       "D": YELLOW_C, "D3": YELLOW_C, "DN": YELLOW_C, "lt": YELLOW_C, "ltN": YELLOW_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def cross(p, color=FG, s=0.12):
    return pole_cross(color, s=s, width=5).move_to(p)


def note(text, color=DIM, size=22):
    return label(text, size, color)


def mixed(tex, color=DIM, size=0.75):
    """A caption mixing words (\\mathrm{...}) and math, typeset as one mathtext line so baselines agree."""
    return M(("all", tex), size=size, color=color)


class ZPlane:
    """A complex plane for discrete-time eigenvalues: axes, ticks at +-1, optional unit circle."""
    def __init__(self, center, unit, r=1.5, circle=True, circle_color=DIM):
        self.o, self.u = np.array([center[0], center[1], 0.0]), unit
        ax = VGroup(Line(self.p(-r, 0), self.p(r, 0)), Line(self.p(0, -r), self.p(0, r))).set_stroke(DIM, 2)
        ticks = VGroup()
        for v in (-1, 1):
            ticks.add(Line(self.p(v, 0) + 0.07 * DOWN, self.p(v, 0) + 0.07 * UP).set_stroke(DIM, 2))
            ticks.add(label(str(v).replace("-", "−"), 18, DIM).next_to(self.p(v, 0), DOWN + (LEFT if v < 0 else RIGHT) * 0.4, buff=0.08))
        names = VGroup(label("Re", 20, DIM).next_to(self.p(r, 0), UP, buff=0.1).shift(0.15 * LEFT),
                       label("Im", 20, DIM).next_to(self.p(0, r), RIGHT, buff=0.1).shift(0.15 * DOWN))
        self.circle = Circle(radius=unit).move_to(self.o).set_stroke(circle_color, 2.5)
        self.axes = VGroup(ax, ticks, names)
        self.mob = VGroup(self.axes, self.circle) if circle else VGroup(self.axes)

    def p(self, x, y=0.0):
        return self.o + self.u * np.array([x, y, 0.0])

    def pc(self, z):
        return self.p(z.real, z.imag)


def polyline(points, color, width=4):
    return VMobject().set_points_as_corners([np.array(p, dtype=float) for p in points]).set_stroke(color, width).set_fill(opacity=0)


# ======================================================================== Section 1

class ModesSequence(ControlScene):
    SEQ_ID = "modes-mix"

    def construct(self):
        e0 = M("x", ("t", "(t)"), "=", "T", ("eD", "e^{Dt}"), ("Ti", "T^{-1}"), ("x0", "x(0)"), size=1.5).move_to([0, 0.7, 0])
        self.start(e0)

        # 1. only e^{Dt} depends on t
        self.play(self.chip("which factor depends on t?"), e0.animate.move_to([0, 1.3, 0]), run_time=0.8)
        b1 = under_bracket(e0.k("T"), BLUE_C)
        b2 = under_bracket(e0.k("eD"), YELLOW_C)
        b3 = under_bracket(e0.ks("Ti", "x0"), PINK_C)
        l1 = note("constant", BLUE_C).next_to(b1, DOWN, buff=0.65)
        l2 = note("changes with t", YELLOW_C).next_to(b2, DOWN, buff=0.2)
        l3 = note("constant", PINK_C).next_to(b3, DOWN, buff=0.2)
        self.play(ShowCreation(b1), ShowCreation(b3), FadeIn(l1), FadeIn(l3), run_time=0.9)
        self.play(ShowCreation(b2), FadeIn(l2, shift=0.1 * UP), Indicate(e0.k("eD"), color=YELLOW_C, scale_factor=1.15), run_time=1.1)
        q = mixed(r"\mathrm{as}\ t \to \infty\mathrm{,\ every\ change\ comes\ from}\ e^{Dt}", FG, 0.8).move_to([0, -1.8, 0])
        self.play(FadeIn(q), run_time=0.6)
        grp1 = VGroup(b1, b2, b3, l1, l2, l3)
        self.step_done(e0, grp1, q)

        # 2. e^{Dt} is diagonal
        top = e0.copy().scale(0.75).move_to([0, 2.9, 0])
        Dm = Mat([[r"e^{\lambda_1 t}", "0", "0"], ["0", r"\ddots", "0"], ["0", "0", r"e^{\lambda_n t}"]], size=0.95)
        for (i, j) in [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]:
            Dm.e[i][j].set_fill(DIM)
        Dm.e[0][0].set_fill(YELLOW_C)
        Dm.e[2][2].set_fill(YELLOW_C)
        dl = M(("eD", "e^{Dt}"), "=", size=1.2)
        drow = place_row(dl, Dm, buff=0.3).move_to([0, 0.1, 0])
        dn = note("one exponential (a mode) per eigenvalue, zeros elsewhere", YELLOW_C).next_to(drow, DOWN, buff=0.45)
        self.play(self.chip("D is diagonal"), FadeOut(VGroup(grp1, q)), ReplacementTransform(e0, top), run_time=0.8)
        self.play(TransformFromCopy(top.k("eD"), dl.k("eD")), FadeIn(dl.k("=")), FadeIn(Dm.lb), FadeIn(Dm.rb), run_time=0.9)
        self.play(TransformFromCopy(dl.k("eD"), Dm.e[0][0]), TransformFromCopy(dl.k("eD"), Dm.e[2][2]), FadeIn(Dm.e[1][1]), run_time=1.1)
        offd = VGroup(*[Dm.e[i][j] for (i, j) in [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]])
        self.play(FadeIn(offd, lag_ratio=0.1), FadeIn(dn), run_time=0.8)
        self.step_done(top, drow, dn)

        # 3. a blend of modes
        blend = M("x", ("t", "(t)"), "=", ("z1", "z_1(0)"), ("m1", r"e^{\lambda_1 t}"), ("c1", "c_1"), "+", r"\cdots", "+",
                  ("zn", "z_n(0)"), ("mn", r"e^{\lambda_n t}"), ("cn", "c_n"), size=1.25).move_to([0, 0.3, 0])
        Tm = Mat([[("c1", "c_1"), r"\cdots", ("cn", "c_n")]], size=0.9, colors=COL)
        trow = place_row(M("T", "=", size=0.95), Tm, buff=0.25).move_to([-3.4, -1.7, 0])
        zrow = M(("z", "z(0)"), "=", ("Ti", "T^{-1}"), ("x0", "x(0)"), size=0.95, colors={"z": GREEN_C}).move_to([3.0, -1.7, 0])
        self.play(self.chip("columns of T, weights z(0)"), FadeOut(dn), drow.animate.scale(0.6).move_to([4.6, 1.75, 0]), run_time=0.8)
        self.play(TransformFromCopy(top.k("T"), trow), TransformFromCopy(top.ks("Ti", "x0"), zrow), run_time=1.0)
        self.play(FadeIn(blend.ks("x", "t", "=")), TransformFromCopy(Tm.e[0][0], blend.k("c1")), TransformFromCopy(Tm.e[0][2], blend.k("cn")),
                  TransformFromCopy(Dm.e[0][0], blend.k("m1")), TransformFromCopy(Dm.e[2][2], blend.k("mn")),
                  TransformFromCopy(zrow.k("z"), blend.k("z1")), TransformFromCopy(zrow.k("z"), blend.k("zn")),
                  FadeIn(blend.ks("+", r"\cdots")), FadeIn(blend.k("+", 1)), run_time=1.6)
        mix = note("each mode rides on its eigenvector with a fixed weight", DIM).next_to(blend, DOWN, buff=0.35)
        self.play(FadeIn(mix), run_time=0.5)
        self.step_done(top, drow, blend, trow, zrow, mix)

        # 4. example: one growing mode takes over
        ex = M("x", ("t", "(t)"), "=", ("z1", "z_1"), ("m1", "e^{-t}"), ("c1", "c_1"), "+", ("z2", "z_2"), ("m2", "e^{0.6t}"), ("c2", "c_2"),
               size=1.1).move_to([0, 2.0, 0])
        exl = note("example: λ₁ = −1, λ₂ = 0.6, weights z₁ = 1, z₂ = 0.08", DIM).next_to(ex, UP, buff=0.25)
        pl = Plot(t_max=6, y_min=-0.2, y_max=3.2, width=7.4, height=3.3, t_label="t").move_to([-1.2, -1.15, 0])
        f1 = pl.curve(lambda t: np.exp(-t), color=GREEN_C, width=4)
        f2 = pl.curve(lambda t: 0.08 * np.exp(0.6 * t), color=RED_C, width=4)
        fs = pl.curve(lambda t: np.exp(-t) + 0.08 * np.exp(0.6 * t), color=TEAL_C, width=6)
        k1 = M(("k1", "e^{-t}"), size=0.8, color=GREEN_C).next_to(pl, RIGHT, buff=0.35).shift(0.9 * DOWN)
        k2 = M(("k2", "0.08\\,e^{0.6t}"), size=0.8, color=RED_C).next_to(pl, RIGHT, buff=0.35).shift(0.15 * DOWN)
        k3 = note("blend", TEAL_C, 22).next_to(pl, RIGHT, buff=0.35).shift(0.75 * UP)
        self.play(self.chip("λ₂ > 0 takes over"), FadeOut(VGroup(top, drow, trow, zrow, mix)), run_time=0.6)
        self.play(self.tmorph(blend, ex, pairs=[("zn", "z2"), ("mn", "m2"), ("cn", "c2")]), FadeIn(exl), run_time=1.3)
        self.play(FadeIn(pl), run_time=0.5)
        self.play(ShowCreation(f1), ShowCreation(f2), FadeIn(k1), FadeIn(k2), run_time=1.8)
        self.play(ShowCreation(fs), FadeIn(k3), run_time=1.6)
        up = note("grows without bound", RED_C, 22).next_to(pl.c2p(6, 3.0), LEFT, buff=0.2)
        self.play(FadeIn(up), Indicate(ex.k("m2"), color=RED_C), run_time=0.8)
        self.step_done(ex, exl, pl, f1, f2, fs, k1, k2, k3, up)

        # 5. a start with z_2(0) = 0
        zero = M(("z2", "0"), size=1.1, color=YELLOW_C).move_to(ex.k("z2"))
        st = strike(ex.span("z2", "c2"), RED_C)
        f2z = pl.curve(lambda t: 0.0, color=RED_C, width=4)
        fsz = pl.curve(lambda t: np.exp(-t), color=TEAL_C, width=6)
        w = note("this start decays, but other starts still grow: the system is unstable", ORANGE_C, 22).move_to([0, 0.85, 0])
        exl0 = note("same rates, new start: weights z₁ = 1, z₂ = 0", DIM).move_to(exl)
        k2z = M(("k2", r"0\cdot e^{0.6t} = 0"), size=0.8, color=RED_C).move_to(k2, aligned_edge=LEFT)
        self.play(self.chip("start with z₂(0) = 0"), FadeOut(up), run_time=0.5)
        self.play(Transform(ex.k("z2"), zero), Transform(exl, exl0), Transform(k2, k2z), run_time=0.8)
        self.play(ShowCreation(st), Transform(f2, f2z), Transform(fs, fsz), run_time=1.5)
        self.play(FadeIn(w, shift=0.1 * UP), run_time=0.6)
        self.step_done(ex, exl, st, pl, f1, f2, fs, k1, k2, k3, w)


# ======================================================================== Section 2

def wave_group(pl, a, b=3.0):
    env_u = DashedVMobject(pl.curve(lambda t: np.exp(a * t), color=YELLOW_C, width=3), num_dashes=40)
    env_d = DashedVMobject(pl.curve(lambda t: -np.exp(a * t), color=YELLOW_C, width=3), num_dashes=40)
    w = pl.curve(lambda t: np.exp(a * t) * np.cos(b * t), color=TEAL_C, width=5, n=400)
    return VGroup(env_u, env_d, w)


class EulerSequence(ControlScene):
    SEQ_ID = "euler-envelope"

    def construct(self):
        lam = M(("lam", r"\lambda"), "=", "a", "+", "ib", size=1.6).move_to([0, 0.6, 0])
        self.start(lam)

        # 1. substitute
        lam2 = lam.copy().scale(0.6).to_corner(UL, buff=0.5)
        f1 = M(("e", r"e^{\lambda t}"), "=", ("eab", "e^{(a+ib)t}"), size=1.4).move_to([-3.0, 2.0, 0])
        self.play(self.chip("substitute λ = a + ib"), ReplacementTransform(lam, lam2), run_time=0.8)
        self.play(FadeIn(f1.ks("e", "=")), run_time=0.5)
        self.play(TransformFromCopy(lam2.ks("a", "+", "ib"), f1.k("eab"), path_arc=-0.5), run_time=1.2)
        self.step_done(lam2, f1)

        # 2. split the exponent
        f2 = M("=", ("eat", "e^{at}"), ("eibt", "e^{ibt}"), size=1.4)
        f2.next_to(f1, DOWN, buff=0.5).align_to(f1.k("="), LEFT)
        l2 = M(r"e^{u+v} = e^u\,e^v", size=0.8, color=DIM).next_to(f2, RIGHT, buff=0.6)
        self.play(self.chip("split the exponent"), FadeIn(f2.k("=")), run_time=0.5)
        self.play(TransformFromCopy(f1.k("eab"), f2.k("eat")), TransformFromCopy(f1.k("eab"), f2.k("eibt")), run_time=1.3)
        self.play(FadeIn(l2), run_time=0.4)
        self.step_done(lam2, f1, f2, l2)

        # 3. Euler's formula with the unit circle
        f3 = M("=", ("eat", "e^{at}"), "[", ("cos", r"\cos bt"), "+", ("isin", r"i\sin bt"), "]", size=1.4)
        f3.next_to(f2, DOWN, buff=0.5).align_to(f2.k("="), LEFT)
        C = np.array([4.9, -1.4, 0])
        R = 1.2
        circ = Circle(radius=R).move_to(C).set_stroke(DIM, 2.5)
        axs = VGroup(Line(C + 1.6 * LEFT, C + 1.6 * RIGHT), Line(C + 1.6 * DOWN, C + 1.6 * UP)).set_stroke(FAINT, 2)
        rad = Line(C, C + R * RIGHT).set_stroke(PINK_C, 4)
        dot = Dot(C + R * RIGHT, radius=0.1).set_fill(PINK_C, 1)
        arm = VGroup(rad, dot)
        cl = M(("eibt", "e^{ibt}"), size=0.9).next_to(circ, UP, buff=0.2)
        self.play(self.chip("Euler's formula"), FadeOut(l2), FadeIn(axs), ShowCreation(circ), FadeIn(arm), TransformFromCopy(f2.k("eibt"), cl), run_time=1.0)
        ang = TAU + 0.9
        self.play(Rotate(arm, ang, about_point=C), run_time=2.0)
        P = C + R * np.array([np.cos(0.9), np.sin(0.9), 0])
        pc = DashedLine(P, np.array([P[0], C[1], 0])).set_stroke(TEAL_C, 2)
        cosl = Line(C, np.array([P[0], C[1], 0])).set_stroke(TEAL_C, 5)
        sinl = Line(np.array([P[0], C[1], 0]), P).set_stroke(GREEN_C, 5)
        cl2 = M(r"\cos bt", size=0.65, color=TEAL_C).next_to(cosl, DOWN, buff=0.12)
        sl2 = M(r"\sin bt", size=0.65, color=GREEN_C).next_to(sinl, RIGHT, buff=0.1)
        self.play(FadeIn(f3.ks("=", "[", "]")), TransformFromCopy(f2.k("eat"), f3.k("eat")),
                  TransformFromCopy(f2.k("eibt"), f3.ks("cos", "+", "isin")), ShowCreation(cosl), ShowCreation(sinl), FadeIn(pc),
                  FadeIn(cl2), FadeIn(sl2), run_time=1.4)
        circle_grp = VGroup(axs, circ, arm, cl, pc, cosl, sinl, cl2, sl2)
        self.step_done(lam2, f1, f2, f3, circle_grp)

        # 4. size is e^{at}
        bx = SurroundingRectangle(f3.span("[", "]"), buff=0.08).set_stroke(GREEN_C, 3)
        one = note("size 1 for every t", GREEN_C).next_to(bx, DOWN, buff=0.15)
        rl = note("radius 1", GREEN_C, 20).next_to(circ, DOWN, buff=0.15)
        f4 = M("|", ("e", r"e^{\lambda t}"), ("bar", "|"), "=", ("eat", "e^{at}"), size=1.4).move_to([-2.0, -2.2, 0])
        b4 = SurroundingRectangle(f4, buff=0.15).set_stroke(YELLOW_C, 3)
        self.play(self.chip("|cos bt + i sin bt| = 1"), ShowCreation(bx), FadeIn(one), Indicate(circ, color=GREEN_C), FadeIn(rl), run_time=1.1)
        self.play(TransformFromCopy(f1.k("e"), f4.k("e")), FadeIn(f4.ks("|", "bar", "=")), TransformFromCopy(f3.k("eat"), f4.k("eat")), run_time=1.2)
        self.play(ShowCreation(b4), run_time=0.5)
        self.step_done(lam2, f1, f2, f3, circle_grp, bx, one, rl, f4, b4)

        # 5. a > 0: growing envelope
        f4s = VGroup(f4, b4)
        pl = Plot(t_max=8, y_min=-4, y_max=4, width=9.6, height=4.4, t_label="t").move_to([-0.6, -0.7, 0])
        waves = wave_group(pl, 0.3)
        al = M("a", "=", ("v", "0.3"), size=1.0).move_to([5.1, 1.9, 0])
        gl = mixed(r"\mathrm{growing\ envelope}\ \pm e^{at}", RED_C, 0.8).move_to([0.3, 2.1, 0])
        self.play(self.chip("a = 0.3 > 0"), FadeOut(VGroup(f1, f2, f3, circle_grp, bx, one, rl)),
                  f4s.animate.scale(0.7).to_corner(UR, buff=0.4), run_time=0.9)
        self.play(FadeIn(pl), FadeIn(al), run_time=0.6)
        self.play(ShowCreation(waves[0]), ShowCreation(waves[1]), run_time=1.0)
        self.play(ShowCreation(waves[2]), run_time=2.0)
        self.play(FadeIn(gl), run_time=0.5)
        self.step_done(lam2, f4s, pl, waves, al, gl)

        # 6. slide a through 0 to -0.5
        al2 = M("a", "=", ("v", "-0.5"), size=1.0).move_to(al)
        dl = note("decaying envelope: the oscillation dies out", GREEN_C).move_to(gl)

        def upd(m, alpha):
            m.become(wave_group(pl, 0.3 + (-0.5 - 0.3) * alpha))
        self.play(self.chip("slide a from 0.3 to −0.5"), FadeOut(gl), run_time=0.5)
        self.play(UpdateFromAlphaFunc(waves, upd), Transform(al, al2), run_time=3.0)
        self.play(FadeIn(dl), run_time=0.5)
        self.step_done(lam2, f4s, pl, waves, al, dl)

        # 7. conjugate pair
        L1 = M(("ep", "e^{(a+ib)t}"), "=", ("eat", "e^{at}"), "(", ("cos", r"\cos bt"), ("pm", "+"), ("isin", r"i\sin bt"), ")", size=1.2)
        L2 = M(("em", "e^{(a-ib)t}"), "=", ("eat", "e^{at}"), "(", ("cos", r"\cos bt"), ("pm", "-"), ("isin", r"i\sin bt"), ")", size=1.2)
        L1.move_to([-0.5, 1.4, 0])
        L2.next_to(L1, DOWN, buff=0.45)
        L2.shift((L1.k("=").get_x() - L2.k("=").get_x()) * RIGHT)
        S = M(("ep", "e^{(a+ib)t}"), "+", ("em", "e^{(a-ib)t}"), "=", ("two", "2"), ("eat", "e^{at}"), ("cos", r"\cos bt"), size=1.25).move_to([-0.3, -1.4, 0])
        pr = note("real A: eigenvalues come in pairs a ± ib", DIM).next_to(L1, UP, buff=0.4)
        self.play(self.chip("add the pair a ± ib"), FadeOut(VGroup(pl, waves, al, dl)), run_time=0.7)
        self.play(FadeIn(pr), Write(L1), run_time=1.0)
        self.play(Write(L2), run_time=1.0)
        s1 = strike(L1.ks("pm", "isin"), RED_C)
        s2 = strike(L2.ks("pm", "isin"), RED_C)
        cn = note("cancel", RED_C, 22).next_to(VGroup(s1, s2), RIGHT, buff=0.3)
        self.play(ShowCreation(s1), ShowCreation(s2), FadeIn(cn), run_time=0.9)
        self.play(TransformFromCopy(L1.k("ep"), S.k("ep")), TransformFromCopy(L2.k("em"), S.k("em")), FadeIn(S.ks("+", "=")),
                  TransformFromCopy(L1.k("cos"), S.k("cos")), TransformFromCopy(L2.k("cos"), S.k("cos")), FadeIn(S.k("two")),
                  TransformFromCopy(L1.k("eat"), S.k("eat")), run_time=1.5)
        rb = SurroundingRectangle(S, buff=0.15).set_stroke(TEAL_C, 3)
        rn = note("real: an oscillation inside the envelope", TEAL_C).next_to(rb, DOWN, buff=0.2)
        self.play(ShowCreation(rb), FadeIn(rn), run_time=0.6)
        self.step_done(lam2, f4s, pr, L1, L2, s1, s2, cn, S, rb, rn)


# ======================================================================== Section 3

class HalfPlaneSequence(ControlScene):
    SEQ_ID = "left-half-plane"

    def construct(self):
        pl = splane(xr=(-3, 2), yr=(-2, 2), unit=1.0, shade=False).move_to([-2.6, -0.3, 0])
        hdr = M(("lam", r"\lambda"), r"\in", r"\mathbb{C}", size=1.3).move_to([3.6, 2.6, 0])
        self.start(pl, hdr)
        O = pl.p(0, 0)

        # 1. eigenvalues as points
        pts = {"l1": (-1, 0), "l2": (-0.5, 1.5), "l3": (-0.5, -1.5)}
        xs = {k: cross(pl.p(*v), FG) for k, v in pts.items()}
        r1 = M(("lam", r"\lambda_1"), "=", "-1", size=1.0).move_to([3.6, 1.2, 0])
        r2 = M(("lam", r"\lambda_{2,3}"), "=", r"-0.5 \pm 1.5i", size=1.0).next_to(r1, DOWN, buff=0.4)
        lb = VGroup(M(r"\lambda_1", size=0.7).next_to(xs["l1"], DOWN, buff=0.15),
                    M(r"\lambda_2", size=0.7).next_to(xs["l2"], LEFT, buff=0.15),
                    M(r"\lambda_3", size=0.7).next_to(xs["l3"], LEFT, buff=0.15))
        mir = DashedLine(pl.p(-0.5, 1.5), pl.p(-0.5, -1.5)).set_stroke(DIM, 1.5)
        self.play(self.chip("each eigenvalue is a point"), run_time=0.5)
        self.play(LaggedStart(*[GrowFromCenter(x) for x in xs.values()], lag_ratio=0.3), Write(r1), Write(r2), run_time=1.4)
        self.play(FadeIn(lb), ShowCreation(mir), run_time=0.6)
        xg = VGroup(*xs.values())
        self.step_done(pl, hdr, xg, r1, r2, lb, mir)

        # 2. left half-plane
        h = 4.0
        left = Rectangle(width=3.0, height=h).set_stroke(width=0).set_fill(GREEN_C, 0.16).move_to(pl.p(-1.5, 0))
        right = Rectangle(width=2.0, height=h).set_stroke(width=0).set_fill(RED_C, 0.16).move_to(pl.p(1.0, 0))
        st = note("stable", GREEN_C, 26).move_to(pl.p(-2.3, 0.6))
        crit = VGroup(M(r"\mathrm{Re}\,\lambda_i < 0", r"\ \mathrm{for\ all}\ i", size=0.95),
                      M(r"\Leftrightarrow", size=0.95),
                      note("asymptotically stable", GREEN_C, 26)).arrange(DOWN, buff=0.25).move_to([3.6, -1.4, 0])
        self.play(self.chip("all real parts negative"), FadeOut(mir), run_time=0.5)
        self.play(GrowFromEdge(left, RIGHT), *[x.animate.set_stroke(GREEN_C) for x in xg], FadeIn(st), run_time=1.2)
        self.play(FadeIn(crit, lag_ratio=0.2), run_time=1.0)
        self.step_done(left, pl, hdr, xg, r1, r2, lb, st, crit)

        # 3. move the pair across
        r2b = M(("lam", r"\lambda_{2,3}"), "=", r"0.4 \pm 1.5i", size=1.0).move_to(r2)
        un = note("unstable", RED_C, 26).move_to(pl.p(1.1, 0.6))
        crit2 = VGroup(M(r"\mathrm{Re}\,\lambda_{2,3} = 0.4 > 0", size=0.95), M(r"\Rightarrow", size=0.95),
                       note("unstable: growing envelope", RED_C, 26)).arrange(DOWN, buff=0.25).move_to(crit)
        self.play(self.chip("move the pair to Re = 0.4"), FadeIn(right), FadeIn(un), run_time=0.7)
        self.play(xs["l2"].animate.move_to(pl.p(0.4, 1.5)).set_stroke(RED_C), xs["l3"].animate.move_to(pl.p(0.4, -1.5)).set_stroke(RED_C),
                  lb[1].animate.next_to(pl.p(0.4, 1.5), RIGHT, buff=0.2), lb[2].animate.next_to(pl.p(0.4, -1.5), RIGHT, buff=0.2),
                  Transform(r2, r2b), run_time=1.6)
        self.play(FadeTransform(crit, crit2), run_time=0.9)
        self.step_done(left, right, pl, hdr, xg, r1, r2, lb, st, un, crit2)

        # 4. preview: control drags them back
        tgt = {"l2": pl.p(-1.3, 1.5), "l3": pl.p(-1.3, -1.5)}
        ghosts = VGroup(cross(pl.p(0.4, 1.5), DIM), cross(pl.p(0.4, -1.5), DIM)).set_opacity(0.5)
        a1 = arc_arrow(pl.p(0.4, 1.75), tgt["l2"] + 0.25 * UP, angle=TAU / 7, color=BLUE_C)
        a2 = arc_arrow(pl.p(0.4, -1.75), tgt["l3"] + 0.25 * DOWN, angle=-TAU / 7, color=BLUE_C)
        pv = VGroup(M(r"\dot x = Ax + Bu", size=0.95, colors={"u": BLUE_C}),
                    note("preview: choose u to move", BLUE_C, 24), note("eigenvalues left (later lectures)", BLUE_C, 24)).arrange(DOWN, buff=0.2).move_to(crit2)
        r2c = M(("lam", r"\lambda_{2,3}"), r"\to", r"{-1.3} \pm 1.5i", size=1.0).move_to(r2)
        self.play(self.chip("preview: feedback moves eigenvalues"), FadeTransform(crit2, pv), FadeIn(ghosts), run_time=0.8)
        self.play(ShowCreation(a1), ShowCreation(a2), run_time=0.9)
        self.play(xs["l2"].animate.move_to(tgt["l2"]).set_stroke(GREEN_C), xs["l3"].animate.move_to(tgt["l3"]).set_stroke(GREEN_C),
                  lb[1].animate.next_to(tgt["l2"], LEFT, buff=0.15), lb[2].animate.next_to(tgt["l3"], LEFT, buff=0.15),
                  Transform(r2, r2c), run_time=1.3)
        self.step_done(left, right, pl, hdr, xg, r1, r2, lb, st, un, ghosts, a1, a2, pv)

        # 5. inverted pendulum
        pend = pendulum(theta=0.0, length=1.5).move_to([3.1, -1.6, 0])
        pivot = pend.hinge.get_center()
        pu = cross(pl.p(1.5, 0), RED_C)
        pd = cross(pl.p(-1.5, 0), GREEN_C)
        pf = M(r"\lambda = \pm\sqrt{g/L}", size=1.0).move_to([3.6, 1.3, 0])
        pn = VGroup(note("pendulum up (book p. 335)", DIM, 22), note("drawn with g/L = 2.25", DIM, 20)).arrange(DOWN, buff=0.12).next_to(pf, DOWN, buff=0.3)
        lab = VGroup(M(r"+\sqrt{g/L}", size=0.6, color=RED_C).next_to(pu, DOWN, buff=0.45).shift(0.35 * LEFT),
                     M(r"-\sqrt{g/L}", size=0.6, color=GREEN_C).next_to(pd, DOWN, buff=0.45))
        self.play(self.chip("inverted pendulum"), FadeOut(VGroup(xg, lb, r1, r2, ghosts, a1, a2, pv)), run_time=0.7)
        self.play(FadeIn(pend), Write(pf), FadeIn(pn), run_time=0.9)
        self.play(GrowFromCenter(pu), GrowFromCenter(pd), FadeIn(lab), run_time=0.8)
        self.play(Rotate(VGroup(pend.rod, pend.ball), -0.45, about_point=pivot), Indicate(pu, color=RED_C, scale_factor=1.4), run_time=1.2)
        fl = note("one eigenvalue in the right half-plane: it falls", RED_C, 22).move_to([3.4, -3.25, 0])
        self.play(FadeIn(fl), run_time=0.5)
        self.step_done(left, right, pl, hdr, st, un, pend, pf, pn, pu, pd, lab, fl)


class BoundarySequence(ControlScene):
    SEQ_ID = "boundary-cases"

    def construct(self):
        pl = splane(xr=(-3, 2), yr=(-2, 2), unit=1.0, shade=True).move_to([-3.0, -0.3, 0])
        axis = Line(pl.p(0, -2), pl.p(0, 2)).set_stroke(ORANGE_C, 6)
        sup = note("Supplement: not covered in the lecture", ORANGE_C, 24).move_to([3.4, 3.2, 0])
        q = M(r"\max_i \mathrm{Re}\,\lambda_i = 0\ ?", size=1.1).move_to([3.4, 2.2, 0])
        self.start(pl, axis, sup, q)

        # 1. pendulum down: rotate the eigenvalues onto the imaginary axis
        pend = pendulum(theta=0.0, length=1.4).move_to([3.0, -1.0, 0])
        pivot = pend.hinge.get_center()
        pts = VGroup(cross(pl.p(1.5, 0), RED_C), cross(pl.p(-1.5, 0), GREEN_C))
        fu = M(r"\lambda = \pm\sqrt{g/L}", size=0.95).move_to([3.4, 1.15, 0])
        fd = M(r"\lambda = \pm i\sqrt{g/L}", size=0.95).move_to(fu)
        ceil = VGroup(Line(pivot + 0.7 * LEFT + 0.12 * UP, pivot + 0.7 * RIGHT + 0.12 * UP).set_stroke(DIM, 3),
                      *[Line(pivot + (x - 0.1) * RIGHT + 0.12 * UP, pivot + x * RIGHT + 0.3 * UP).set_stroke(DIM, 2) for x in np.linspace(-0.55, 0.65, 6)])
        self.play(self.chip("pendulum up → down"), FadeIn(pend), FadeIn(pts), Write(fu), run_time=1.0)
        self.play(Rotate(pts, PI / 2, about_point=pl.p(0, 0)), Rotate(VGroup(pend.rod, pend.ball), PI, about_point=pivot),
                  FadeOut(VGroup(pend[0], pend.base)), FadeIn(ceil), Transform(fu, fd), run_time=2.0)
        pend = VGroup(ceil, pend.rod, pend.ball, pend.hinge)
        self.play(pts.animate.set_stroke(ORANGE_C), run_time=0.4)
        dn = note("hanging down: both on the axis (book p. 335)", DIM, 22).next_to(fu, DOWN, buff=0.25)
        self.play(FadeIn(dn), run_time=0.4)
        self.step_done(pl, axis, sup, q, pend, pts, fu, dn)

        # 2. semisimple: a rotation, bounded forever
        Rm = Mat([[r"\cos\omega t", r"-\sin\omega t"], [r"\sin\omega t", r"\cos\omega t"]], size=0.75)
        rrow = place_row(M(("eJ", "e^{Jt}"), "=", size=0.85), Rm, buff=0.2).move_to([3.4, 1.15, 0])
        Jm = Mat([["0", r"-\omega"], [r"\omega", "0"]], size=0.7)
        jrow = place_row(M("J", "=", size=0.8), Jm, buff=0.2).move_to([3.4, 2.2, 0])
        C = np.array([3.4, -1.3, 0])
        orbit = Circle(radius=0.95).move_to(C).set_stroke(TEAL_C, 3)
        oax = VGroup(Line(C + 1.3 * LEFT, C + 1.3 * RIGHT), Line(C + 1.3 * DOWN, C + 1.3 * UP)).set_stroke(FAINT, 2)
        dot = Dot(C + 0.95 * RIGHT, radius=0.1).set_fill(TEAL_C, 1)
        vec = Line(C, C + 0.95 * RIGHT).set_stroke(TEAL_C, 3)
        ol = note("x(t) circles forever", TEAL_C, 20).next_to(orbit, DOWN, buff=0.15)
        ly = note("bounded, never decays: Lyapunov stable, not asymptotically", ORANGE_C, 20).move_to([3.4, -3.3, 0])
        self.play(self.chip("semisimple: a rotation"), FadeOut(VGroup(pend, dn, q)), FadeTransform(fu, jrow), run_time=0.9)
        self.play(TransformFromCopy(jrow, rrow), FadeIn(oax), ShowCreation(orbit), FadeIn(vec), FadeIn(dot), run_time=1.2)
        self.play(Rotate(VGroup(vec, dot), TAU * 1.15, about_point=C), run_time=2.0)
        self.play(FadeIn(ol), FadeIn(ly), run_time=0.6)
        self.step_done(pl, axis, sup, pts, jrow, rrow, oax, orbit, vec, dot, ol, ly)

        # 3. defective: a Jordan block at 0
        Jd = Mat([["0", "1"], ["0", "0"]], size=0.7)
        jd = place_row(M("J", "=", size=0.8), Jd, buff=0.2).move_to(jrow)
        ser = M(("eJ", "e^{Jt}"), "=", "I", "+", ("Jt", "Jt"), ("p2", "+"), ("J2", r"\frac{J^2t^2}{2}"), ("p3", "+"), (r"\cdots", r"\cdots"),
                size=0.85).move_to([3.4, 1.15, 0])
        Em = Mat([["1", "t"], ["0", "1"]], size=0.8)
        Em.e[0][1].set_fill(RED_C)
        res = place_row(M(("eJ", "e^{Jt}"), "=", "I", "+", ("Jt", "Jt"), "=", size=0.85), Em, buff=0.2).move_to([3.4, 1.15, 0])
        dbl = VGroup(cross(pl.p(0, 0), RED_C), cross(pl.p(0, 0), RED_C).shift(0.0 * UP))
        d2 = note("0 twice, one eigenvector", RED_C, 20).next_to(pl.p(0, 0), DL, buff=0.3).shift(0.4 * DOWN)
        pt = Plot(t_max=4, y_min=-0.3, y_max=4.4, width=3.2, height=2.2, t_label="t").move_to([3.4, -1.45, 0])
        ln = pt.curve(lambda t: 1 + t, color=RED_C, width=5)
        lnl = M(r"x_1 = x_1(0) + t\,x_2(0)", size=0.6, color=RED_C).next_to(pt, DOWN, buff=0.15)
        un = note("grows like t: unstable, with no positive real part", RED_C, 20).move_to([3.4, -3.35, 0])
        self.play(self.chip("defective: J² = 0"), FadeOut(VGroup(oax, orbit, vec, dot, ol, ly, rrow)), FadeTransform(jrow, jd), run_time=0.9)
        self.play(Transform(pts[0], dbl[0]), Transform(pts[1], dbl[1]), FadeIn(d2), Write(ser), run_time=1.3)
        s2 = strike(ser.span("p2", r"\cdots"), RED_C)
        z2 = M(r"J^2 = 0", size=0.7, color=RED_C).next_to(s2, UP, buff=0.12)
        self.play(ShowCreation(s2), FadeIn(z2), run_time=0.8)
        self.play(FadeOut(VGroup(s2, z2, ser.span("p2", r"\cdots"))), self.tmorph(ser, res.submobjects[0], skip_src=[ser.span("p2", r"\cdots")]),
                  FadeIn(Em), run_time=1.3)
        self.play(FadeIn(pt), ShowCreation(ln), FadeIn(lnl), FadeIn(un), run_time=1.3)
        self.step_done(pl, axis, sup, pts, d2, jd, res, pt, ln, lnl, un)

        # 4. discrete twin: imaginary axis -> unit circle; summary
        zp = ZPlane([-3.0, -0.3], 1.25, r=1.6, circle=False)
        ucirc = Circle(radius=1.25).move_to(zp.o).set_stroke(ORANGE_C, 6)
        onec = VGroup(cross(zp.p(1, 0), RED_C), cross(zp.p(1, 0), RED_C))
        ss = VGroup(cross(zp.p(np.cos(1.1), np.sin(1.1)), ORANGE_C), cross(zp.p(np.cos(1.1), -np.sin(1.1)), ORANGE_C))
        P1 = Mat([["1", "1"], ["0", "1"]], size=0.75)
        P2 = Mat([["1", "N"], ["0", "1"]], size=0.75)
        P2.e[0][1].set_fill(RED_C)
        sup_n = M(("N", "N"), size=0.6).next_to(P1, UR, buff=0.02).shift(0.15 * DOWN)
        prow = VGroup(P1, sup_n)
        eq = M("=", size=0.85)
        row = VGroup(prow, eq, P2).arrange(RIGHT, buff=0.25).move_to([3.4, 1.9, 0])
        tbl = VGroup(
            note("asymptotically stable: all strictly inside", GREEN_C, 21),
            note("(Re λ < 0, or |λ| < 1 in discrete time)", GREEN_C, 19),
            note("Lyapunov only: boundary eigenvalues semisimple", ORANGE_C, 21),
            note("unstable: one outside, or defective on the boundary", RED_C, 21),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        tbl[1].shift(0.12 * UP)
        tbl.set_width(min(tbl.get_width(), 6.4)).move_to([3.4, -0.9, 0])
        e01 = M(r"e^{0\cdot\Delta t} = 1", size=0.55, color=DIM).next_to(zp.p(1, 0), DR, buff=0.12).shift(0.35 * RIGHT + 0.3 * DOWN)
        self.play(self.chip("discrete twin: the unit circle"), FadeOut(VGroup(jd, res, pt, ln, lnl, un, d2)), run_time=0.7)
        self.play(FadeOut(pl), FadeIn(zp.mob), Transform(axis, ucirc), Transform(pts[0], onec[0]), Transform(pts[1], onec[1]),
                  FadeIn(ss), FadeIn(e01), run_time=1.8)
        self.play(FadeIn(row), run_time=0.8)
        self.play(FadeIn(tbl, lag_ratio=0.25), run_time=1.2)
        self.step_done(zp.mob, axis, pts, ss, e01, sup, row, tbl)


# ======================================================================== Section 4

def xfun(t):
    return np.exp(-0.25 * t) * np.cos(1.6 * t)


class SamplingSequence(ControlScene):
    SEQ_ID = "sampling"

    def construct(self):
        top = M("x", ("t", "(t)"), "=", ("eAt", "e^{At}"), ("x0", "x(0)"), size=1.1).move_to([0, 3.2, 0])
        pl = Plot(t_max=6.3, y_min=-1.1, y_max=1.3, width=10.0, height=3.0, t_label="t").move_to([-0.3, 0.75, 0])
        cv = pl.curve(xfun, color=TEAL_C, width=4, n=300)
        cl = note("x(t), continuous", TEAL_C, 20).next_to(pl.c2p(3.6, 1.15), RIGHT, buff=0.1)
        self.start(top, pl, cv, cl)
        DT = 0.5
        ks = range(13)

        # 1. sample
        ticks = VGroup(*[DashedLine(pl.c2p(k * DT, -1.1), pl.c2p(k * DT, xfun(k * DT))).set_stroke(DIM, 1.5) for k in ks])
        dots = VGroup(*[Dot(pl.c2p(k * DT, xfun(k * DT)), radius=0.09).set_fill(TEAL_C, 1) for k in ks])
        names = VGroup(*[M(f"x_{k}", size=0.6, color=TEAL_C).next_to(dots[k], UP if xfun(k * DT) >= 0 else DOWN, buff=0.12) for k in range(4)])
        brace = VGroup(Line(pl.c2p(0, -1.0), pl.c2p(DT, -1.0)).set_stroke(YELLOW_C, 3))
        bl = M(r"\Delta t", size=0.6, color=YELLOW_C).next_to(brace, DOWN, buff=0.08)
        f1 = M(("xk", "x_k"), "=", ("xkt", r"x(k\,\Delta t)"), ",", r"\quad k = 0, 1, 2, \ldots", size=1.0).move_to([0, -1.55, 0])
        self.play(self.chip("measure every Δt"), cv.animate.set_stroke(opacity=0.45), run_time=0.5)
        self.play(ShowCreation(ticks, lag_ratio=0.08), run_time=1.0)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.12), FadeIn(names), FadeIn(brace), FadeIn(bl), run_time=1.6)
        self.play(Write(f1), run_time=0.9)
        samp = VGroup(ticks, dots, names, brace, bl)
        self.step_done(top, pl, cv, cl, samp, f1)

        # 2. one step is a matrix exponential
        g1 = M(("xk1", "x_{k+1}"), "=", ("eA1", r"e^{A(k+1)\Delta t}"), ("x0", "x(0)"), size=1.0)
        g2 = M("=", ("eAd", r"e^{A\Delta t}"), ("eAk", r"e^{Ak\Delta t}"), ("x0", "x(0)"), size=1.0)
        g3 = M("=", ("eAd", r"e^{A\Delta t}"), ("xk", "x_k"), size=1.0)
        chain = VGroup(g1, g2, g3).arrange(RIGHT, buff=0.25).move_to([0.2, -2.5, 0])
        for g in (g2, g3):
            g.set_baseline(g1.baseline())
        self.play(self.chip("split the exponential"), f1.animate.scale(0.75).move_to([-3.6, -1.45, 0]), run_time=0.7)
        self.play(Write(g1), run_time=0.9)
        self.play(FadeIn(g2.k("=")), TransformFromCopy(g1.k("eA1"), g2.k("eAd")), TransformFromCopy(g1.k("eA1"), g2.k("eAk")),
                  TransformFromCopy(g1.k("x0"), g2.k("x0")), run_time=1.3)
        ub = under_bracket(g2.ks("eAk", "x0"), TEAL_C, buff=0.1)
        ubl = M(("xk", "x_k"), size=0.7).next_to(ub, DOWN, buff=0.1)
        self.play(ShowCreation(ub), FadeIn(ubl), run_time=0.6)
        self.play(FadeIn(g3.k("=")), TransformFromCopy(g2.k("eAd"), g3.k("eAd")), TransformFromCopy(ubl.k("xk"), g3.k("xk")), run_time=1.1)
        self.step_done(top, pl, cv, cl, samp, f1, chain, ub, ubl)

        # 3. name it A~
        h1 = M(("xk1", "x_{k+1}"), "=", ("At", r"\tilde{A}"), ("xk", "x_k"), size=1.2).move_to([-2.0, -2.4, 0])
        h2 = M(("At", r"\tilde{A}"), "=", ("eAd", r"e^{A\Delta t}"), size=1.2).move_to([2.6, -2.4, 0])
        bk = note("book: A_d (Eq. 8.22a)", DIM, 20).next_to(h2, DOWN, buff=0.15)
        hops = VGroup(*[arc_arrow(dots[k].get_center() + 0.12 * UP, dots[k + 1].get_center() + 0.12 * UP, angle=-TAU / 4, color=BLUE_C, width=3)
                        for k in range(3)])
        hl = M(("At", r"\times\tilde{A}"), size=0.6, color=BLUE_C).next_to(hops[1], UR, buff=0.02)
        self.play(self.chip("call it Ã"), FadeOut(VGroup(ub, ubl)), run_time=0.4)
        self.play(TransformFromCopy(g3.k("eAd"), h2.k("eAd")), FadeIn(h2.ks("At", "=")), run_time=1.0)
        self.play(ReplacementTransform(g1.k("xk1"), h1.k("xk1")), ReplacementTransform(g3.k("xk"), h1.k("xk")),
                  ReplacementTransform(g3.k("eAd"), h1.k("At")), FadeIn(h1.k("=")),
                  FadeOut(VGroup(g1.k("="), g1.k("eA1"), g1.k("x0"), g2, g3.k("="))), FadeIn(bk), run_time=1.3)
        self.play(LaggedStart(*[ShowCreation(hp) for hp in hops], lag_ratio=0.4), FadeIn(hl), run_time=1.3)
        self.step_done(top, pl, cv, cl, samp, f1, h1, h2, bk, hops, hl)

        # 4. iterate by substitution
        r1 = M(("x1", "x_1"), "=", ("At", r"\tilde{A}"), ("x0", "x_0"), size=1.05)
        r2 = M(("x2", "x_2"), "=", ("At", r"\tilde{A}"), ("x1", "x_1"), size=1.05)
        r2b = M(("x2", "x_2"), "=", ("At", r"\tilde{A}"), ("ax", r"\tilde{A}x_0"), size=1.05)
        r2c = M(("x2", "x_2"), "=", ("A2", r"\tilde{A}^2"), ("x0", "x_0"), size=1.05, colors={"A2": BLUE_C})
        r3 = M(("x3", "x_3"), "=", ("A3", r"\tilde{A}^3"), ("x0", "x_0"), size=1.05)
        VGroup(r1, r2, r3).arrange(RIGHT, buff=1.0).move_to([0.6, -2.4, 0])
        r2b.move_to(r2).align_to(r2, LEFT)
        r2c.move_to(r2).align_to(r2, LEFT)
        self.play(self.chip("substitute x₁ = Ãx₀"), FadeOut(VGroup(h1, h2, bk, f1)), run_time=0.6)
        self.play(Write(r1), Write(r2), run_time=1.1)
        hb = hbox(r2.k("x1"), YELLOW_C)
        self.play(ShowCreation(hb), Indicate(r1.span("At", "x0"), color=YELLOW_C), run_time=0.7)
        self.play(FadeOut(hb), FadeOut(r2.k("x1")), TransformFromCopy(r1.span("At", "x0"), r2b.k("ax")), run_time=1.1)
        self.play(ReplacementTransform(r2.k("x2"), r2c.k("x2")), ReplacementTransform(r2.k("="), r2c.k("=")),
                  ReplacementTransform(VGroup(r2.k("At"), r2b.k("ax")), VGroup(r2c.k("A2"), r2c.k("x0"))), run_time=1.0)
        self.play(Write(r3), run_time=0.8)
        self.step_done(top, pl, cv, cl, samp, r1, r2c, r3)

        # 5. powers replace the exponential
        big = M(("xN", "x_N"), "=", ("AN", r"\tilde{A}^N"), ("x0", "x_0"), size=1.4).move_to([-2.3, -2.3, 0])
        vs = note("vs.", DIM, 26).move_to([0.6, -2.3, 0])
        ct = top.copy()
        q = mixed(r"\mathrm{stability:\ what\ does}\ \tilde{A}^N\ \mathrm{do\ as}\ N \to \infty\,?", YELLOW_C, 0.65).move_to([2.1, -3.35, 0])
        self.play(self.chip("N steps: Ã to the power N"), run_time=0.4)
        self.play(TransformFromCopy(r3.k("x3"), big.k("xN")), TransformFromCopy(r3.k("A3"), big.k("AN")), TransformFromCopy(r3.k("x0"), big.k("x0")),
                  FadeIn(big.k("=")), FadeOut(VGroup(r1, r2c, r3)), run_time=1.2)
        self.play(FadeIn(vs), ct.animate.move_to([3.6, -2.3, 0]), run_time=0.9)
        self.play(FadeIn(q), run_time=0.5)
        self.step_done(top, pl, cv, cl, samp, big, vs, ct, q)


# ======================================================================== Section 5

class PowersSequence(ControlScene):
    SEQ_ID = "powers-unit-circle"

    def construct(self):
        T, D, Ti, At = r"\tilde{T}", r"\tilde{D}", r"\tilde{T}^{-1}", r"\tilde{A}"
        h0 = M(("xN", "x_N"), "=", ("AN", r"\tilde{A}^N"), ("x0", "x_0"), size=1.2).move_to([0, 1.6, 0])
        e1 = M(("At", At), ("T", T), "=", ("T", T), ("D", D), size=1.4).move_to([0, 0.0, 0])
        self.start(h0, e1)

        # 1. A~ = T~ D~ T~^{-1}
        r1 = M(("At", At), ("Tx", T), ("Tix", Ti), "=", ("T", T), ("D", D), ("Ti", Ti), size=1.4).move_to([0, 0.0, 0])
        r2 = M(("At", At), "=", ("T", T), ("D", D), ("Ti", Ti), size=1.4).move_to([0, 0.0, 0])
        self.play(self.chip("× T⁻¹ on the right (with tildes)"), run_time=0.5)
        self.play(self.tmorph(e1, r1, pairs=[(("T", 0), "Tx"), (("T", 1), "T")]), run_time=1.2)
        pb = hbox(r1.ks("Tx", "Tix"), YELLOW_C, 0.06)
        il = M("=", "I", size=0.8).next_to(pb, DOWN, buff=0.12)
        self.play(ShowCreation(pb), FadeIn(il), run_time=0.6)
        self.play(self.tmorph(r1, r2), FadeOut(pb), FadeOut(il), run_time=1.1)
        on = VGroup(note("board order, 16:44", GREEN_C, 22), note("(aloud at 12:57: T⁻¹DT, unsure)", DIM, 20)).arrange(DOWN, buff=0.1).next_to(r2, DOWN, buff=0.5)
        self.play(FadeIn(on), run_time=0.5)
        self.step_done(h0, r2, on)

        # 2. A~^3: adjacent pairs cancel
        S = 1.0
        a3 = M(("A3", r"\tilde{A}^3"), "=", ("T", T), ("D", D), ("Ti", Ti), ("T", T), ("D", D), ("Ti", Ti), ("T", T), ("D", D), ("Ti", Ti),
               size=S).move_to([0, 0.5, 0])
        res = M("=", ("T", T), ("D3", r"\tilde{D}^3"), ("Ti", Ti), size=S)
        res.next_to(a3, DOWN, buff=0.5).align_to(a3.k("="), LEFT)
        gen = M(("AN", r"\tilde{A}^N"), "=", ("T", T), ("DN", r"\tilde{D}^N"), ("Ti", Ti), size=1.25).move_to([0, -2.0, 0])
        gb = SurroundingRectangle(gen, buff=0.15).set_stroke(YELLOW_C, 3)
        self.play(self.chip("adjacent pairs cancel"), FadeOut(on), h0.animate.scale(0.75).to_corner(UL, buff=0.45),
                  r2.animate.scale(0.7).to_corner(UR, buff=0.45), run_time=0.8)
        self.play(FadeIn(a3.ks("A3", "=")), *[TransformFromCopy(r2.span("T", "Ti"), VGroup(a3.k("T", i), a3.k("D", i), a3.k("Ti", i))) for i in range(3)],
                  run_time=1.3)
        boxes = VGroup(hbox(VGroup(a3.k("Ti", 0), a3.k("T", 1)), YELLOW_C, 0.05), hbox(VGroup(a3.k("Ti", 1), a3.k("T", 2)), YELLOW_C, 0.05))
        ils = VGroup(*[M("I", size=0.75, color=YELLOW_C).next_to(b, DOWN, buff=0.12) for b in boxes])
        self.play(ShowCreation(boxes), FadeIn(ils), run_time=0.8)
        self.play(FadeIn(res.k("=")), TransformFromCopy(a3.k("T", 0), res.k("T")), TransformFromCopy(a3.k("Ti", 2), res.k("Ti")),
                  *[TransformFromCopy(a3.k("D", i), res.k("D3")) for i in range(3)], run_time=1.3)
        self.play(TransformFromCopy(res, gen), run_time=1.0)
        dn = M(("DN", r"\tilde{D}^N"), "=", r"\mathrm{diag}(\tilde{\lambda}_1^N, \ldots, \tilde{\lambda}_n^N)", size=0.85).next_to(gb, DOWN, buff=0.3)
        self.play(ShowCreation(gb), FadeIn(dn), run_time=0.7)
        self.step_done(h0, r2, a3, boxes, ils, res, gen, gb, dn)

        # 3. radius and angle
        zp = ZPlane([-2.6, -0.45], 1.6, r=1.5, circle=False)
        th = 0.5
        P = zp.p(0.95 * np.cos(th), 0.95 * np.sin(th))
        rad = Line(zp.p(0, 0), P).set_stroke(YELLOW_C, 4)
        pt = cross(P, YELLOW_C)
        arc = Arc(start_angle=0, angle=th, radius=0.55, arc_center=zp.p(0, 0)).set_stroke(PINK_C, 3)
        thl = M(r"\theta", size=0.7, color=PINK_C).move_to(zp.p(0, 0) + 0.8 * np.array([np.cos(th / 2), np.sin(th / 2), 0]))
        rl = M("r", size=0.75, color=YELLOW_C).move_to((zp.p(0, 0) + P) / 2 + 0.25 * np.array([-np.sin(th), np.cos(th), 0]))
        prj = VGroup(DashedLine(P, zp.p(0.95 * np.cos(th), 0)), DashedLine(P, zp.p(0, 0.95 * np.sin(th)))).set_stroke(DIM, 1.5)
        pol = M(("lt", r"\tilde{\lambda}"), "=", ("r", "r"), ("eith", r"e^{i\theta}"), size=1.3).move_to([3.4, 0.9, 0])
        pol.k("r").set_fill(YELLOW_C)
        pol.k("eith").set_fill(PINK_C)
        rp = M(r"\mathrm{Re} = r\cos\theta,\ \ \mathrm{Im} = r\sin\theta", size=0.75).next_to(pol, DOWN, buff=0.4)
        self.play(self.chip("radius and angle"), FadeOut(VGroup(a3, boxes, ils, res, gb, dn, r2)), gen.animate.scale(0.7).to_corner(UR, buff=0.45), run_time=0.9)
        self.play(FadeIn(zp.mob), run_time=0.6)
        self.play(GrowFromCenter(pt), ShowCreation(rad), run_time=0.8)
        self.play(ShowCreation(arc), FadeIn(thl), FadeIn(rl), ShowCreation(prj), Write(pol), run_time=1.2)
        self.play(FadeIn(rp), run_time=0.5)
        geo = VGroup(rad, pt, arc, thl, rl, prj)
        self.step_done(h0, gen, zp.mob, geo, pol, rp)

        # 4. powers turn and scale
        polN = M(("lt", r"\tilde{\lambda}^N"), "=", ("r", "r^N"), ("eith", r"e^{iN\theta}"), size=1.3).move_to(pol)
        polN.k("r").set_fill(YELLOW_C)
        polN.k("eith").set_fill(PINK_C)

        def spiral(r, n, color):
            pts = []
            for k in range(1, n + 1):
                z = (r ** k) * np.exp(1j * th * k)
                if abs(z.real) > 1.5 or abs(z.imag) > 1.5:
                    break
                pts.append(zp.pc(z))
            path = polyline(pts, color, 3)
            ds = VGroup(*[Dot(p, radius=0.07).set_fill(color, 1) for p in pts])
            return path, ds
        p_in, d_in = spiral(0.88, 16, GREEN_C)
        p_out, d_out = spiral(1.1, 14, RED_C)
        lin = M("r = 0.88", size=0.7, color=GREEN_C).move_to([3.4, -1.1, 0])
        lout = M("r = 1.1", size=0.7, color=RED_C).next_to(lin, DOWN, buff=0.3)
        self.play(self.chip("multiply again and again"), FadeOut(VGroup(rp, prj, rl)), self.tmorph(pol, polN), run_time=1.1)
        self.play(FadeIn(lin), ShowCreation(p_in), LaggedStart(*[GrowFromCenter(d) for d in d_in], lag_ratio=0.15), run_time=2.0)
        self.play(FadeIn(lout), ShowCreation(p_out), LaggedStart(*[GrowFromCenter(d) for d in d_out], lag_ratio=0.15), run_time=1.8)
        il_ = note("spirals in", GREEN_C, 20).next_to(lin, RIGHT, buff=0.25)
        ol_ = note("spirals out", RED_C, 20).next_to(lout, RIGHT, buff=0.25)
        self.play(FadeIn(il_), FadeIn(ol_), run_time=0.4)
        geo2 = VGroup(rad, pt, arc, thl)
        sp = VGroup(p_in, d_in, p_out, d_out)
        self.step_done(h0, gen, zp.mob, geo2, polN, sp, lin, lout, il_, ol_)

        # 5. the unit circle
        disc = Circle(radius=1.6).move_to(zp.o).set_stroke(width=0).set_fill(GREEN_C, 0.16)
        uc = Circle(radius=1.6).move_to(zp.o).set_stroke(FG, 3)
        ins = note("stable", GREEN_C, 24).move_to(zp.p(-0.45, -0.45))
        outs = note("unstable", RED_C, 24).move_to(zp.p(1.05, -1.25))
        crit = VGroup(M(r"|\tilde{\lambda}_i| < 1\ \ \mathrm{for\ all}\ i", size=0.95), M(r"\Leftrightarrow", size=0.95),
                      note("asymptotically stable", GREEN_C, 26)).arrange(DOWN, buff=0.22).move_to([3.4, -1.2, 0])
        self.play(self.chip("draw the unit circle"), FadeOut(VGroup(lin, lout, il_, ol_)), run_time=0.5)
        self.play(ShowCreation(uc), run_time=1.0)
        self.play(FadeIn(disc), FadeIn(ins), FadeIn(outs), FadeIn(crit, lag_ratio=0.2), run_time=1.1)
        self.step_done(h0, gen, disc, zp.mob, uc, geo2, polN, sp, ins, outs, crit)

        # 6. magnitude, not real part
        z = 0.5 + 0.9j
        Pz = zp.pc(z)
        xz = cross(Pz, ORANGE_C, s=0.14)
        vline = DashedLine(zp.p(0.5, -1.4), zp.p(0.5, 1.4)).set_stroke(ORANGE_C, 2)
        rez = M(r"\mathrm{Re} = 0.5", size=0.6, color=ORANGE_C).next_to(zp.p(0.5, -1.4), DOWN, buff=0.08)
        rz = Line(zp.p(0, 0), Pz).set_stroke(RED_C, 4)
        mag = M(r"|\tilde{\lambda}| \approx 1.03", size=0.65, color=RED_C).next_to(Pz, RIGHT, buff=0.3).shift(0.1 * UP)
        cap = VGroup(M(r"\tilde{\lambda} = 0.5 + 0.9i", size=0.95),
                     note("real part 0.5 < 1, yet outside the circle", ORANGE_C, 24),
                     note("16:10 says 'real part': read magnitude", DIM, 22)).arrange(DOWN, buff=0.22).move_to(crit)
        self.play(self.chip("magnitude, not real part"), FadeOut(VGroup(sp, geo2)), FadeTransform(crit, cap), run_time=0.9)
        self.play(ShowCreation(vline), FadeIn(rez), GrowFromCenter(xz), run_time=0.9)
        self.play(ShowCreation(rz), FadeIn(mag), Indicate(xz, color=RED_C, scale_factor=1.5), run_time=1.1)
        self.step_done(h0, gen, disc, zp.mob, uc, polN, ins, outs, cap, vline, rez, xz, rz, mag)


# ======================================================================== Section 6

def vline_pts(pl, a, b0, b1, n=121):
    return [pl.p(a, b) for b in np.linspace(b0, b1, n)]


class ConformalSequence(ControlScene):
    SEQ_ID = "conformal-map"

    def construct(self):
        DT = 1.0
        U = 0.62
        L = splane(xr=(-3, 1), yr=(-4, 4), unit=U, shade=False, labels=False).move_to([-4.4, -0.5, 0])
        Ll = M(r"\lambda", size=0.8, color=DIM).next_to(L.p(1, 4), RIGHT, buff=0.15).shift(0.3 * DOWN)
        Z = ZPlane([2.7, -0.55], 1.75, r=1.45, circle=True, circle_color=FG)
        Zl = M(r"\tilde{\lambda}", size=0.8, color=DIM).next_to(Z.p(1.45, 1.45), UP, buff=0.05)
        top = M(("At", r"\tilde{A}"), "=", ("eAd", r"e^{A\Delta t}"), size=1.15).move_to([0, 3.45, 0])
        self.start(L, Ll, Z.mob, Zl, top)
        FY = 2.65   # formula row

        # 1. eigenvalues of e^{A dt}
        f1 = M(("eAd", r"e^{A\Delta t}"), "=", "T", ("eDd", r"e^{D\Delta t}"), ("Ti", "T^{-1}"), size=0.95, colors={"eDd": YELLOW_C})
        f2 = M(r"\Rightarrow", ("lt", r"\tilde{\lambda}_i"), "=", ("el", r"e^{\lambda_i\Delta t}"), size=0.95, colors={"el": YELLOW_C})
        VGroup(f1, f2).arrange(RIGHT, buff=0.45).move_to([0, FY, 0])
        f2.set_baseline(f1.baseline())
        arr = arc_arrow([-3.0, 1.55, 0], [-0.2, 1.55, 0], angle=-TAU / 8, color=YELLOW_C)
        arl = M(r"\lambda \mapsto e^{\lambda\Delta t}", size=0.7, color=YELLOW_C).next_to(arr, DOWN, buff=0.1)
        self.play(self.chip("same eigenvectors"), run_time=0.4)
        self.play(TransformFromCopy(top.k("eAd"), f1.k("eAd")), FadeIn(f1.ks("=", "T", "Ti")), TransformFromCopy(top.k("eAd"), f1.k("eDd")), run_time=1.2)
        self.play(FadeIn(f2.ks(r"\Rightarrow", "lt", "=")), TransformFromCopy(f1.k("eDd"), f2.k("el")), run_time=1.0)
        self.play(ShowCreation(arr), FadeIn(arl), run_time=0.7)
        self.step_done(L, Ll, Z.mob, Zl, top, f1, f2, arr, arl)

        # 2. one eigenvalue: radius from Re, angle from Im
        lam = -0.5 + 1.2j
        xl = VGroup(cross(L.p(lam.real, lam.imag), YELLOW_C), cross(L.p(lam.real, -lam.imag), YELLOW_C))
        mu = np.exp(lam * DT)
        xr = VGroup(cross(Z.pc(mu), YELLOW_C), cross(Z.pc(mu.conjugate()), YELLOW_C))
        g = M(("e", r"e^{(a+ib)\Delta t}"), "=", ("ea", r"e^{a\Delta t}"), ("eb", r"e^{ib\Delta t}"), size=0.95,
              colors={"ea": YELLOW_C, "eb": PINK_C}).move_to([0, FY, 0])
        lv = M(r"\lambda = -0.5 \pm 1.2i,\ \ \Delta t = 1", size=0.65, color=YELLOW_C).next_to(arl, DOWN, buff=0.25)
        rad = Line(Z.p(0, 0), Z.pc(mu)).set_stroke(YELLOW_C, 3)
        arc = Arc(start_angle=0, angle=lam.imag * DT, radius=0.45, arc_center=Z.p(0, 0)).set_stroke(PINK_C, 3)
        rl = M(r"e^{-0.5} \approx 0.61", size=0.6, color=YELLOW_C).next_to(Z.pc(mu), LEFT, buff=0.3).shift(0.3 * UP)
        al = M(r"1.2\ \mathrm{rad}", size=0.6, color=PINK_C).move_to(Z.p(0, 0) + 0.75 * np.array([np.cos(0.6), np.sin(0.6), 0]) + 0.35 * RIGHT)
        self.play(self.chip("one eigenvalue across"), FadeOut(VGroup(f1, f2)), run_time=0.5)
        self.play(Write(g), GrowFromCenter(xl[0]), GrowFromCenter(xl[1]), FadeIn(lv), run_time=1.0)
        self.play(TransformFromCopy(xl[0], xr[0], path_arc=-0.6), TransformFromCopy(xl[1], xr[1], path_arc=0.6), run_time=1.4)
        self.play(ShowCreation(rad), ShowCreation(arc), FadeIn(rl), FadeIn(al), run_time=0.8)
        self.step_done(L, Ll, Z.mob, Zl, top, arr, arl, g, xl, xr, lv, rad, arc, rl, al)

        # 3. a vertical line becomes a circle (point by point)
        bmax = np.pi / DT
        bs = np.linspace(-bmax, bmax, 121)
        lineL = polyline([L.p(-0.5, b) for b in bs], YELLOW_C, 4)
        circR = polyline([Z.pc(np.exp((-0.5 + 1j * b) * DT)) for b in bs], YELLOW_C, 4)
        g3 = M(r"\mathrm{Re}\,\lambda = a", r"\ \mapsto\ ", r"|\tilde{\lambda}| = e^{a\Delta t}", size=0.95).move_to([0, FY, 0])
        bl = note("−π ≤ Im λ ≤ π", DIM, 18).next_to(L.p(-0.5, -bmax), DOWN, buff=0.08)
        self.play(self.chip("map the line Re λ = −0.5"), FadeOut(VGroup(rad, arc, rl, al, lv)), FadeTransform(g, g3), run_time=0.8)
        self.play(ShowCreation(lineL), FadeIn(bl), run_time=0.9)
        self.play(Transform(lineL.copy(), circR, path_arc=-0.4), run_time=2.0)
        self.step_done(L, Ll, Z.mob, Zl, top, arr, arl, g3, xl, xr, lineL, bl, circR)

        # 4. more lines; imaginary axis -> unit circle; half-plane -> disc
        aa = [-2.0, -1.0, 0.0]
        cols = {-2.0: GREEN_C, -1.0: GREEN_C, 0.0: ORANGE_C}
        linesL = VGroup(*[polyline([L.p(a, b) for b in bs], cols[a], 6 if a == 0 else 3) for a in aa])
        circs = VGroup(*[polyline([Z.pc(np.exp((a + 1j * b) * DT)) for b in bs], cols[a], 6 if a == 0 else 3) for a in aa])
        lhp = Rectangle(width=3 * U, height=2 * bmax * U).set_stroke(width=0).set_fill(GREEN_C, 0.16).move_to(L.p(-1.5, 0))
        disc = Circle(radius=1.75).move_to(Z.o).set_stroke(width=0).set_fill(GREEN_C, 0.16)
        g4 = M(r"\mathrm{Re}\,\lambda = 0 \mapsto |\tilde{\lambda}| = 1,", r"\quad \mathrm{Re}\,\lambda < 0 \mapsto |\tilde{\lambda}| < 1",
               size=0.85).move_to([0, FY, 0])
        self.play(self.chip("imaginary axis → unit circle"), FadeTransform(g3, g4), FadeOut(bl), run_time=0.7)
        self.play(ShowCreation(linesL, lag_ratio=0.2), run_time=1.0)
        self.play(*[Transform(linesL[i].copy(), circs[i], path_arc=-0.4) for i in range(3)], run_time=2.0)
        self.play(FadeIn(lhp), FadeIn(disc), run_time=0.8)
        self.step_done(lhp, disc, L, Ll, Z.mob, Zl, top, arr, arl, g4, xl, xr, lineL, circR, linesL, circs)

        # 5. horizontal lines become rays; right angles survive
        bb = [-2.4, -1.2, 1.2, 2.4]
        As = np.linspace(-3, 0, 61)
        hl = VGroup(*[polyline([L.p(a, b) for a in As], PINK_C, 3) for b in bb])
        rays = VGroup(*[polyline([Z.pc(np.exp((a + 1j * b) * DT)) for a in As], PINK_C, 3) for b in bb])
        g5 = M(r"\mathrm{Im}\,\lambda = b", r"\ \mapsto\ ", r"\arg\tilde{\lambda} = b\Delta t\ (\mathrm{mod}\ 2\pi)", size=0.95).move_to([0, FY, 0])

        def corner(P, u, v, s=0.16):
            return polyline([P + s * u, P + s * (u + v), P + s * v], FG, 2.5)
        cL = corner(L.p(-0.5, 1.2), UP, RIGHT)
        mu2 = np.exp((-0.5 + 1.2j) * DT)
        ur = np.array([np.cos(1.2), np.sin(1.2), 0])
        ut = np.array([-np.sin(1.2), np.cos(1.2), 0])
        cR = corner(Z.pc(mu2), -ut, ur)
        cn = note("right angles survive: the map is conformal", FG, 22).move_to([2.7, -3.3, 0])
        self.play(self.chip("horizontal lines → rays"), FadeTransform(g4, g5), run_time=0.6)
        self.play(ShowCreation(hl, lag_ratio=0.15), run_time=0.9)
        self.play(*[Transform(hl[i].copy(), rays[i], path_arc=-0.4) for i in range(4)], run_time=2.0)
        self.play(ShowCreation(cL), ShowCreation(cR), FadeIn(cn), run_time=0.8)
        self.step_done(lhp, disc, L, Ll, Z.mob, Zl, top, arr, arl, g5, xl, xr, lineL, circR, linesL, circs, hl, rays, cL, cR, cn)

        # 6. the upshot
        dimmed = VGroup(lineL, circR, linesL, circs, hl, rays, cL, cR)
        up = M(r"\mathrm{Re}\,\lambda < 0", r"\ \Leftrightarrow\ ", r"|e^{\lambda\Delta t}| < 1", size=1.0).move_to([0, FY - 0.05, 0])
        ub = SurroundingRectangle(up, buff=0.12).set_stroke(YELLOW_C, 3)
        s3 = note("asymptotic stability depends only on the eigenvalues", YELLOW_C, 22).move_to([0.1, 1.9, 0])
        s12 = VGroup(note("continuous: all real parts negative", GREEN_C, 21),
                     note("discrete: all inside the unit circle", GREEN_C, 21)).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([-1.0, 1.2, 0])
        self.play(self.chip("the upshot"), FadeOut(VGroup(cn, arr, arl)), dimmed.animate.set_stroke(opacity=0.35), FadeTransform(g5, up), run_time=1.0)
        self.play(ShowCreation(ub), FadeIn(s3), run_time=0.7)
        self.play(FadeIn(s12), run_time=0.7)
        self.step_done(lhp, disc, L, Ll, Z.mob, Zl, top, dimmed, xl, xr, up, ub, s3, s12)