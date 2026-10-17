"""ManimGL scenes for the Linear Systems study companion (one scene per sequence in control_specs).

Rendered by build_sequences.py. Every step starts by swapping the relation chip, animates the
actual operation (token morphs, column scaling, grid shear, cancellation) and ends with
`step_done(...)`, which settles the scene to exactly the listed mobjects.

Colour code: x and its derivative teal, z (eigen coordinates) green, T blue, T^{-1} pink,
D / eigenvalues / e^{Dt} yellow, eigenvectors orange.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)   # this guide labels the relation "Picture"

COL = {"x": TEAL_C, "xd": TEAL_C, "x0": TEAL_C, "xt": TEAL_C, "z": GREEN_C, "zd": GREEN_C, "z0": GREEN_C,
       "zt": GREEN_C, "T": BLUE_C, "Ti": PINK_C, "D": YELLOW_C, "D2": YELLOW_C, "Dk": YELLOW_C, "eD": YELLOW_C,
       "lam": YELLOW_C, "c": ORANGE_C}


def M(*toks, size=1.0, color=FG):
    return Mx(*toks, size=size, color=color, colors=COL)


def zero(size=0.9):
    return Mx("0", size=size, color=DIM)


def col(*entries, size=0.9, color=FG):
    return Mat([[e] for e in entries], size=size, color=FG, colors=COL)


def brackets(m, color=FG, pad=0.14, arm=0.14):
    """Tall square brackets drawn around a mobject (mathtext has no stretchy \\left[)."""
    top, bot = m.get_top()[1] + pad, m.get_bottom()[1] - pad
    lx, rx = m.get_left()[0] - pad, m.get_right()[0] + pad
    lb = VMobject().set_points_as_corners([[lx + arm, top, 0], [lx, top, 0], [lx, bot, 0], [lx + arm, bot, 0]])
    rb = VMobject().set_points_as_corners([[rx - arm, top, 0], [rx, top, 0], [rx, bot, 0], [rx - arm, bot, 0]])
    return VGroup(lb, rb).set_stroke(color, 3.2).set_fill(opacity=0)


class Grid:
    """A small fixed coordinate plane: p(x, y) gives scene points."""
    def __init__(self, origin, unit, xr, yr, step=1):
        self.o, self.u, self.xr, self.yr = np.array(origin, dtype=float), unit, xr, yr
        lines = VGroup()
        for i in range(int(np.ceil(xr[0])), int(np.floor(xr[1])) + 1, step):
            if i != 0:
                lines.add(Line(self.p(i, yr[0]), self.p(i, yr[1])))
        for j in range(int(np.ceil(yr[0])), int(np.floor(yr[1])) + 1, step):
            if j != 0:
                lines.add(Line(self.p(xr[0], j), self.p(xr[1], j)))
        lines.set_stroke(FAINT, 1.5)
        axes = VGroup(Line(self.p(xr[0], 0), self.p(xr[1], 0)), Line(self.p(0, yr[0]), self.p(0, yr[1]))).set_stroke(DIM, 2.4)
        self.lines, self.axes = lines, axes
        self.mob = VGroup(lines, axes)

    def p(self, x, y):
        return self.o + self.u * np.array([x, y, 0.0])

    def vec(self, x, y, color=FG, width=4):
        return poly_arrow([self.p(0, 0), self.p(x, y)], color=color, width=width)


# ======================================================================== Section 1

class MatrixExponentialSequence(ControlScene):
    SEQ_ID = "matrix-exponential"

    def construct(self):
        e0 = M(("xd", r"\dot{x}"), "=", "A", "x", size=1.6).move_to([0, 1.2, 0])
        self.start(e0)

        # 1. sizes
        top = M(("xd", r"\dot{x}"), "=", "A", "x", size=1.2).move_to([0, 2.6, 0])
        xv = col("x_1", "x_2", r"\vdots", "x_n", size=0.85)
        xv_l = M("x", "=", size=1.0)
        xg = place_row(xv_l, xv, buff=0.25).move_to([-3.3, -0.2, 0])
        sq = Square(side_length=1.9).set_stroke(FG, 3).set_fill(FAINT, 0.35).move_to([2.6, -0.2, 0])
        a_in = M("A", size=1.2).move_to(sq)
        nl = label("n", 24, DIM).next_to(sq, LEFT, buff=0.15)
        nt = label("n", 24, DIM).next_to(sq, UP, buff=0.12)
        sz = M("x", r"\in", ("Rn", r"\mathbb{R}^n"), ("sp", r",\qquad"), "A", r"\in", ("Rnn", r"\mathbb{R}^{n\times n}"),
               size=1.0).move_to([0, -2.2, 0])
        self.play(self.chip("state vector, square matrix"), ReplacementTransform(e0, top), run_time=0.9)
        self.play(TransformFromCopy(top.k("x"), xv_l.k("x")), FadeIn(xv_l.k("=")),
                  FadeIn(xv, lag_ratio=0.15), TransformFromCopy(top.k("A"), a_in), ShowCreation(sq), run_time=1.4)
        self.play(FadeIn(nl), FadeIn(nt), Write(sz), run_time=1.0)
        self.step_done(top, xg, sq, a_in, nl, nt, sz)

        # 2. solution
        sol = M("x", ("t", "(t)"), "=", ("eAt", "e^{At}"), ("x0", "x(0)"), size=1.45).move_to([0, 0.4, 0])
        note = label("a matrix acting on the initial state, from the left", 24, DIM).next_to(sol, DOWN, buff=0.45)
        self.play(self.chip("x(t) from x(0)"), FadeOut(VGroup(xg, sq, a_in, nl, nt)), sz.animate.scale(0.75).to_corner(UR, buff=0.4),
                  run_time=0.8)
        self.play(TransformFromCopy(top.k("x"), sol.k("x")), FadeIn(sol.ks("t", "=")),
                  TransformFromCopy(top.k("A"), sol.k("eAt")), FadeIn(sol.k("x0"), shift=0.2 * LEFT), run_time=1.4)
        self.play(FadeIn(note, shift=0.1 * UP), Indicate(sol.k("eAt"), color=YELLOW_C), run_time=0.9)
        self.step_done(top, sz, sol, note)

        # 3. scalar Taylor series
        sol2 = sol.copy().scale(0.7).move_to([-3.6, 2.6, 0])
        ser = M(("ea", "e^{at}"), "=", ("1", "1"), "+", ("at", "at"), "+", ("a2", r"\frac{a^2t^2}{2!}"), "+",
                ("a3", r"\frac{a^3t^3}{3!}"), "+", r"\cdots", size=1.2).move_to([0, 0.2, 0])
        sl = label("for a number a", 24, DIM).next_to(ser, UP, buff=0.4)
        self.play(self.chip("scalar exponential"), FadeOut(VGroup(top, note)), ReplacementTransform(sol, sol2), run_time=0.8)
        self.play(FadeIn(sl), Write(ser), run_time=1.6)
        self.step_done(sol2, sz, sl, ser)

        # 4. matrix series: token-by-token substitution a -> A, 1 -> I
        mser = M(("ea", "e^{At}"), "=", ("1", "I"), "+", ("at", "At"), "+", ("a2", r"\frac{A^2t^2}{2!}"), "+",
                 ("a3", r"\frac{A^3t^3}{3!}"), "+", r"\cdots", size=1.2).move_to([0, 0.2, 0])
        ml = label("every term is an n × n matrix", 24, DIM).next_to(mser, UP, buff=0.4)
        self.play(self.chip("a → A, 1 → I"), run_time=0.5)
        self.play(self.tmorph(ser, mser, path_arc=0.0), ReplacementTransform(sl, ml), run_time=1.6)
        brs = VGroup(*[under_bracket(mser.k(k), YELLOW_C) for k in ("1", "at", "a2", "a3")])
        chk = M(("e0", r"e^{A\cdot 0}"), "=", "I", size=0.9).next_to(brs, DOWN, buff=0.45)
        self.play(ShowCreation(brs, lag_ratio=0.2), run_time=0.8)
        self.play(FadeIn(chk, shift=0.1 * UP), Indicate(mser.k("1"), color=GREEN_C), run_time=0.9)
        self.step_done(sol2, sz, ml, mser, brs, chk)

        # 5. caution: not entrywise
        wrong_l = M(("eAt", "e^{At}"), r"\neq", size=1.1)
        wrong_m = Mat([[r"e^{a_{11}t}", r"e^{a_{12}t}"], [r"e^{a_{21}t}", r"e^{a_{22}t}"]], size=0.95)
        wrong = place_row(wrong_l, wrong_m, buff=0.3).move_to([0, -1.25, 0])
        st = strike(wrong_m)
        why = label("A², A³, … mix the entries: no entry-by-entry shortcut", 24, ORANGE_C).next_to(wrong, DOWN, buff=0.35)
        self.play(self.chip("not entrywise"), FadeOut(VGroup(brs, chk)), ml.animate.set_opacity(0.0),
                  VGroup(mser).animate.shift(1.2 * UP), run_time=0.8)
        self.play(TransformFromCopy(mser.k("ea"), wrong_l.k("eAt")), FadeIn(wrong_l.k(r"\neq")), FadeIn(wrong_m), run_time=1.1)
        self.play(ShowCreation(st), FadeIn(why, shift=0.1 * UP), run_time=0.8)
        self.step_done(sol2, sz, mser, wrong, st, why)


# ======================================================================== Section 2

class EigenSequence(ControlScene):
    SEQ_ID = "eigen-at-td"

    def construct(self):
        e0 = M("A", "c", "=", ("lam", r"\lambda"), "c", size=1.6).move_to([0, 0.6, 0])
        nz = M("c", r"\neq", "0", size=1.0).next_to(e0, DOWN, buff=0.6)
        self.start(e0, nz)

        # 1. plane: a generic vector turns, eigenvectors stay on their lines
        g = Grid([-3.3, -0.45, 0], 0.86, (-2.6, 2.6), (-2.6, 2.4))
        e0s = VGroup(e0, nz)
        Am = Mat([["-1", "-1"], ["0", "-2"]], size=0.85)
        Al = M("A", "=", size=0.95)
        arow = place_row(Al, Am, buff=0.25).move_to([3.6, 1.2, 0])
        self.play(self.chip("A = [[−1, −1], [0, −2]]"), e0s.animate.scale(0.6).move_to([3.6, 2.7, 0]), FadeIn(g.mob), run_time=1.0)
        self.play(FadeIn(arow), run_time=0.6)
        v = g.vec(1, -1, FG)
        Av = g.vec(0, 2, RED_C)
        vl = label("v", 24, FG).next_to(g.p(1, -1), DR, buff=0.05)
        Avl = label("Av: turned", 22, RED_C).next_to(g.p(0, 2), LEFT, buff=0.15)
        self.play(GrowFromPoint(v, g.p(0, 0)), FadeIn(vl), run_time=0.6)
        self.play(TransformFromCopy(v, Av, path_arc=0.6), FadeIn(Avl), run_time=1.1)
        self.play(VGroup(v, Av, vl, Avl).animate.set_opacity(0.35), run_time=0.4)
        s1 = DashedLine(g.p(-2.6, 0), g.p(2.6, 0)).set_stroke(ORANGE_C, 2)
        s2 = DashedLine(g.p(-2.4, -2.4), g.p(2.4, 2.4)).set_stroke(ORANGE_C, 2)
        c1, c2 = g.vec(1, 0, ORANGE_C, 5), g.vec(1, 1, ORANGE_C, 5)
        Ac1, Ac2 = g.vec(-1, 0, YELLOW_C, 5), g.vec(-2, -2, YELLOW_C, 5)
        c1l = M(("c", "c_1"), size=0.8).next_to(g.p(0.75, 0), UP, buff=0.12)
        c2l = M(("c", "c_2"), size=0.8).next_to(g.p(1, 1), RIGHT, buff=0.18).shift(0.15 * DOWN)
        r1 = M("A", ("c", "c_1"), "=", ("lam", "-1"), ("c", "c_1"), size=0.9).move_to([3.6, -0.3, 0])
        r2 = M("A", ("c", "c_2"), "=", ("lam", "-2"), ("c", "c_2"), size=0.9).move_to([3.6, -1.3, 0])
        self.play(ShowCreation(s1), ShowCreation(s2), GrowFromPoint(c1, g.p(0, 0)), GrowFromPoint(c2, g.p(0, 0)),
                  FadeIn(c1l), FadeIn(c2l), run_time=1.0)
        self.play(TransformFromCopy(c1, Ac1), FadeIn(r1), run_time=1.1)
        self.play(TransformFromCopy(c2, Ac2), FadeIn(r2), run_time=1.1)
        fl = label("negative λ: flipped and rescaled, same line", 22, YELLOW_C).move_to([3.6, -2.2, 0])
        self.play(FadeIn(fl), run_time=0.5)
        plane = VGroup(g.mob, v, Av, vl, Avl, s1, s2, c1, c2, Ac1, Ac2, c1l, c2l)
        self.step_done(e0s, arow, plane, r1, r2, fl)

        # 2. T and D
        Tm = Mat([[("c", "c_1"), ("c", "c_2"), r"\cdots", ("c", "c_n")]], size=0.95)
        Tl = M("T", "=", size=1.1)
        Trow = place_row(Tl, Tm, buff=0.25).move_to([-3.2, 0.2, 0])
        Dm = Mat([[(("lam", r"\lambda_1")), "0", "0"], ["0", r"\ddots", "0"], ["0", "0", ("lam", r"\lambda_n")]], size=0.9,
                 colors=COL)
        for (i, j) in [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]:
            Dm.e[i][j].set_fill(DIM)
        Dl = M("D", "=", size=1.1)
        Drow = place_row(Dl, Dm, buff=0.25).move_to([3.0, 0.2, 0])
        tl = label("eigenvectors as columns", 22, ORANGE_C).next_to(Trow, DOWN, buff=0.5)
        dl = label("eigenvalues on the diagonal, same order", 22, YELLOW_C).next_to(Drow, DOWN, buff=0.4)
        self.play(self.chip("collect them"), FadeOut(VGroup(plane, arow, r1, r2, fl)), run_time=0.8)
        self.play(FadeIn(Tl), FadeIn(Tm.lb), FadeIn(Tm.rb), FadeIn(Tm.e[0][2]),
                  *[TransformFromCopy(e0.k("c", 0), Tm.e[0][j]) for j in (0, 1, 3)], run_time=1.3)
        self.play(FadeIn(Dl), FadeIn(Dm.lb), FadeIn(Dm.rb), TransformFromCopy(e0.k("lam"), Dm.e[0][0]),
                  TransformFromCopy(e0.k("lam"), Dm.e[2][2]), FadeIn(Dm.e[1][1]),
                  *[FadeIn(Dm.e[i][j]) for (i, j) in [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]], run_time=1.3)
        self.play(FadeIn(tl), FadeIn(dl), run_time=0.5)
        self.step_done(e0s, Trow, Drow, tl, dl)

        # 3. AT column by column
        Tsm = VGroup(Trow, Drow)
        AT_l = M("A", "T", "=", size=1.0)
        m1 = Mat([[M("A", ("c", "c_1"), size=0.9), M("A", ("c", "c_2"), size=0.9), r"\cdots", M("A", ("c", "c_n"), size=0.9)]], size=0.9)
        eqs = M("=", size=1.0)
        m2 = Mat([[M(("lam", r"\lambda_1"), ("c", "c_1"), size=0.9), M(("lam", r"\lambda_2"), ("c", "c_2"), size=0.9), r"\cdots",
                   M(("lam", r"\lambda_n"), ("c", "c_n"), size=0.9)]], size=0.9)
        atrow = place_row(AT_l, m1, eqs, m2, buff=0.25).move_to([0, 0.75, 0])
        self.play(self.chip("A times each column"), FadeOut(VGroup(tl, dl, e0s)),
                  Tsm.animate.scale(0.72).arrange(RIGHT, buff=1.2).move_to([-1.2, 2.55, 0]), run_time=0.9)
        self.play(FadeIn(AT_l), FadeIn(m1.lb), FadeIn(m1.rb), FadeIn(m1.e[0][2]),
                  *[TransformFromCopy(Tm.e[0][j], m1.e[0][j].k("c")) for j in (0, 1, 3)],
                  *[FadeIn(m1.e[0][j].k("A"), shift=0.2 * RIGHT) for j in (0, 1, 3)], run_time=1.3)
        self.play(FadeIn(eqs), FadeIn(m2.lb), FadeIn(m2.rb), FadeIn(m2.e[0][2]),
                  *[self.tmorph(m1.e[0][j], m2.e[0][j], keep_src=True) for j in (0, 1, 3)], run_time=1.5)
        self.step_done(Tsm, atrow)

        # 4. TD scales the columns
        TD_l = M("T", "D", "=", size=1.0)
        m3 = Mat([[M(("lam", r"\lambda_1"), ("c", "c_1"), size=0.9), M(("lam", r"\lambda_2"), ("c", "c_2"), size=0.9), r"\cdots",
                   M(("lam", r"\lambda_n"), ("c", "c_n"), size=0.9)]], size=0.9)
        tdrow = place_row(TD_l, m3, buff=0.25)
        tdrow.shift((m2.get_x() - m3.get_x()) * RIGHT).set_y(-0.75)
        res = M("A", "T", "=", "T", "D", size=1.4).move_to([0, -2.1, 0])
        rbox = hbox(res, GREEN_C, 0.16)
        rl = label("D on the right scales columns (DT would scale rows)", 22, DIM).next_to(rbox, RIGHT, buff=0.3)
        self.play(self.chip("T times diagonal D"), run_time=0.5)
        self.play(FadeIn(TD_l), FadeIn(m3.lb), FadeIn(m3.rb), FadeIn(m3.e[0][2]),
                  *[TransformFromCopy(Tm.e[0][j], m3.e[0][j].k("c")) for j in (0, 1, 3)],
                  TransformFromCopy(Dm.e[0][0], m3.e[0][0].k("lam")), TransformFromCopy(Dm.e[2][2], m3.e[0][3].k("lam")),
                  FadeIn(m3.e[0][1].k("lam")), run_time=1.5)
        same = VGroup(hbox(m2, GREEN_C, 0.06), hbox(m3, GREEN_C, 0.06))
        self.play(ShowCreation(same), run_time=0.6)
        self.play(TransformFromCopy(AT_l.ks("A", "T"), VGroup(res.k("A"), res.k("T", 0))), FadeIn(res.k("=")),
                  TransformFromCopy(TD_l.ks("T", "D"), VGroup(res.k("T", 1), res.k("D"))), FadeOut(same), run_time=1.3)
        rl.next_to(rbox, DOWN, buff=0.15).set_x(0)
        res.add(rbox)
        self.play(ShowCreation(rbox), FadeIn(rl), run_time=0.7)
        self.step_done(Tsm, atrow, tdrow, res, rl)

        # 5. caveat
        res2 = M("A", "T", "=", "T", "D", size=1.2).move_to([0, 2.5, 0])
        need = M(r"\det", "T", r"\neq", "0", size=1.1).move_to([0, 1.3, 0])
        nl = label("need n linearly independent eigenvectors", 24, FG).next_to(need, DOWN, buff=0.3)
        def card(title, body, colr, x):
            t = label(title, 24, colr, weight=BOLD)
            b = body if isinstance(body, Mobject) else label(body, 22, FG)
            content = VGroup(t, b).arrange(DOWN, buff=0.25)
            fr = RoundedRectangle(width=3.9, height=2.0, corner_radius=0.14).set_stroke(colr, 2.5).move_to(content)
            return VGroup(fr, content).move_to([x, -1.45, 0])
        k1 = card("distinct λ", label("always enough", 22, FG), GREEN_C, -4.4)
        k2 = card("repeated λ", M("A", "=", "2I", size=0.9), YELLOW_C, 0)
        k2s = label("can still be diagonal", 20, DIM).next_to(k2, DOWN, buff=0.1)
        dm = Mat([["1", "1"], ["0", "1"]], size=0.8)
        k3 = card("defective", dm, ORANGE_C, 4.4)
        k3s = label("one direction only → Jordan form", 20, DIM).next_to(k3, DOWN, buff=0.1)
        self.play(self.chip("n independent eigenvectors"), FadeOut(VGroup(Tsm, atrow, tdrow, rl)),
                  ReplacementTransform(res, res2), run_time=1.0)
        self.play(Write(need), FadeIn(nl), run_time=0.9)
        self.play(LaggedStart(FadeIn(k1, shift=0.1 * UP), FadeIn(VGroup(k2, k2s), shift=0.1 * UP),
                              FadeIn(VGroup(k3, k3s), shift=0.1 * UP), lag_ratio=0.35), run_time=1.6)
        self.step_done(res2, need, nl, k1, k2, k2s, k3, k3s)


# ======================================================================== Section 3

class CoordinatesSequence(ControlScene):
    SEQ_ID = "change-coordinates"

    def construct(self):
        e0 = M("x", "=", "T", "z", size=1.6).move_to([0, 0.5, 0])
        self.start(e0)

        # 1. sheared grid and x = z1 c1 + z2 c2
        g = Grid([-4.8, -1.7, 0], 1.0, (-1, 3.5), (-1, 2.2))
        top = M("x", "=", "T", "z", size=1.2).move_to([-3.3, 2.75, 0])
        sheared = VGroup()
        for i in range(-1, 4):
            y0, y1 = max(-1, -1 - i), min(2.2, 3.5 - i)
            sheared.add(Line(g.p(i + y0, y0), g.p(i + y1, y1)))
        sheared.set_stroke(GREEN_C, 2, opacity=0.7)
        straight = VGroup(*[Line(g.p(i, -1), g.p(i, 2.2)) for i in range(-1, 4)]).set_stroke(GREEN_C, 2, opacity=0.7)
        horiz = VGroup(*[Line(g.p(-1, j), g.p(3.5, j)) for j in range(-1, 3)]).set_stroke(GREEN_C, 2, opacity=0.7)
        self.play(self.chip("axes along the eigenvectors"), ReplacementTransform(e0, top), FadeIn(g.mob), run_time=0.9)
        self.play(ShowCreation(straight), ShowCreation(horiz), run_time=0.7)
        self.play(Transform(straight, sheared), run_time=1.5)
        c1 = g.vec(1, 0, ORANGE_C, 5)
        c2 = poly_arrow([g.p(1, 0), g.p(2, 1)], color=ORANGE_C, width=5)
        xa = g.vec(2, 1, TEAL_C, 5)
        c1l = M(("c", "1\\,c_1"), size=0.75).next_to(g.p(0.5, 0), DOWN, buff=0.12)
        c2l = M(("c", "1\\,c_2"), size=0.75).next_to(g.p(1.5, 0.5), RIGHT, buff=0.15)
        xl = M("x", size=0.9).next_to(g.p(2, 1), UR, buff=0.06)
        f1 = M("x", "=", ("z1", "z_1"), ("c1", "c_1"), "+", ("z2", "z_2"), ("c2", "c_2"), size=1.05,).move_to([3.6, 1.4, 0])
        for k in ("z1", "z2"):
            f1.k(k).set_fill(GREEN_C)
        for k in ("c1", "c2"):
            f1.k(k).set_fill(ORANGE_C)
        n_x = col("2", "1", size=0.8)
        n_c1 = col("1", "0", size=0.8)
        n_c2 = col("1", "1", size=0.8)
        f2 = place_row(n_x, M("=", "1", size=0.9), n_c1, M("+", "1", size=0.9), n_c2, buff=0.2).move_to([3.6, -0.1, 0])
        zl = label("z = (1, 1): one of each eigenvector", 22, GREEN_C).move_to([3.6, -1.3, 0])
        self.play(GrowFromPoint(c1, g.p(0, 0)), FadeIn(c1l), run_time=0.7)
        self.play(GrowFromPoint(c2, g.p(1, 0)), FadeIn(c2l), run_time=0.7)
        self.play(GrowFromPoint(xa, g.p(0, 0)), FadeIn(xl), Write(f1), run_time=1.0)
        self.play(FadeIn(f2), FadeIn(zl), run_time=0.8)
        plane = VGroup(g.mob, straight, horiz, c1, c2, xa, c1l, c2l, xl)
        self.step_done(top, plane, f1, f2, zl)

        # 2. z = T^{-1} x, inverse not transpose
        zi = M("z", "=", ("Ti", "T^{-1}"), "x", size=1.1).move_to([3.4, 2.75, 0])
        Ti = Mat([["1", "-1"], ["0", "1"]], size=0.8)
        Tt = Mat([["1", "0"], ["1", "1"]], size=0.8)
        r_i = place_row(M(("Ti", "T^{-1}"), "=", size=0.9), Ti, M("x", "=", size=0.85), col("1", "1", size=0.75), buff=0.2)
        r_t = place_row(M(("Tt", r"T^{\top}"), "=", size=0.9), Tt, M("x", "=", size=0.85), col("2", "3", size=0.75), buff=0.2)
        r_i.move_to([3.4, 1.3, 0])
        r_t.move_to([3.4, -0.5, 0])
        ok = label("✓ matches z = (1, 1)", 22, GREEN_C).next_to(r_i, DOWN, buff=0.15)
        bad = label("✗ transpose: wrong here", 22, RED_C).next_to(r_t, DOWN, buff=0.15)
        st = strike(r_t)
        ex = label("T⁻¹ = Tᵀ only for orthonormal eigenvectors", 20, DIM).move_to([3.4, -2.1, 0])
        self.play(self.chip("invert T"), FadeOut(VGroup(f1, f2, zl)), run_time=0.6)
        self.play(TransformFromCopy(top.k("x"), zi.k("x")), TransformFromCopy(top.k("z"), zi.k("z")),
                  TransformFromCopy(top.k("T"), zi.k("Ti")), FadeIn(zi.k("=")), run_time=1.2)
        self.play(FadeIn(r_i), run_time=0.8)
        self.play(FadeIn(ok), run_time=0.4)
        self.play(FadeIn(r_t), run_time=0.8)
        self.play(ShowCreation(st), FadeIn(bad), FadeIn(ex), run_time=0.8)
        self.step_done(top, plane, zi, r_i, ok, r_t, st, bad, ex)

        # 3. derivative
        S = 1.1
        L0 = M("x", "=", "T", "z", size=S).move_to([0, 2.6, 0])
        L1 = M(("xd", r"\dot{x}"), "=", "T", ("zd", r"\dot{z}"), size=S).move_to([0, 1.45, 0])
        side = M(("Ti", "T^{-1}"), "=", size=0.8)
        side_m = Mat([["1", "-1"], ["0", "1"]], size=0.65)
        sideg = place_row(side, side_m, buff=0.15).to_corner(UR, buff=0.4)
        cl = label("T is constant in time", 22, DIM).next_to(L1, RIGHT, buff=0.6)
        self.play(self.chip("d/dt of x = Tz"), FadeOut(VGroup(plane, zi, r_t, st, bad, ex, ok)),
                  ReplacementTransform(top, L0), ReplacementTransform(r_i, sideg), run_time=1.0)
        self.play(self.tmorph(L0, L1, keep_src=True, pairs=[("x", "xd"), ("z", "zd")]), run_time=1.4)
        self.play(FadeIn(cl), run_time=0.5)
        self.step_done(sideg, L0, L1, cl)

        # 4. substitute: T zdot = A x = A T z
        L2 = M("T", ("zd", r"\dot{z}"), "=", "A", "x", "=", ("A2", "A"), ("T2", "T"), ("z", "z"), size=S).move_to([0, 0.3, 0])
        self.play(self.chip("ẋ = Ax, x = Tz"), FadeOut(cl), run_time=0.5)
        self.play(TransformFromCopy(L1.k("T"), L2.k("T")), TransformFromCopy(L1.k("zd"), L2.k("zd")),
                  FadeIn(VGroup(L2.k("=", 0), L2.k("A"), L2.k("x"))), run_time=1.2)
        self.play(FadeIn(L2.k("=", 1)), TransformFromCopy(L2.k("A"), L2.k("A2")),
                  TransformFromCopy(L0.k("T"), L2.k("T2"), path_arc=-0.5), TransformFromCopy(L0.k("z"), L2.k("z"), path_arc=-0.5),
                  run_time=1.3)
        ol = label("T stays to the right of A", 22, DIM).next_to(L2, RIGHT, buff=0.5)
        self.play(FadeIn(ol), run_time=0.4)
        self.step_done(sideg, L0, L1, L2, ol)

        # 5. multiply on the left by T^{-1}
        L3a = M(("Ti", "T^{-1}"), "T", ("zd", r"\dot{z}"), "=", ("Ti", "T^{-1}"), "A", ("T2", "T"), "z", size=S).move_to([0, -0.85, 0])
        L3 = M(("zd", r"\dot{z}"), "=", ("Ti", "T^{-1}"), "A", ("T2", "T"), "z", size=S).move_to([0, -0.85, 0])
        self.play(self.chip("× T⁻¹ on the left, both sides"), FadeOut(ol), run_time=0.5)
        self.play(TransformFromCopy(L2.ks("T", "zd"), L3a.ks("T", "zd")), TransformFromCopy(L2.k("=", 0), L3a.k("=")),
                  TransformFromCopy(VGroup(L2.k("A2"), L2.k("T2"), L2.k("z")), VGroup(L3a.k("A"), L3a.k("T2"), L3a.k("z"))),
                  run_time=1.1)
        self.play(TransformFromCopy(side, L3a.k("Ti", 0)), TransformFromCopy(side, L3a.k("Ti", 1)), run_time=0.9)
        pair = VGroup(L3a.k("Ti", 0), L3a.k("T"))
        pb = hbox(pair, YELLOW_C, 0.06)
        il = M("=", "I", size=0.8).next_to(pb, DOWN, buff=0.12)
        self.play(ShowCreation(pb), FadeIn(il), run_time=0.7)
        self.play(self.tmorph(L3a, L3, pairs=[(("Ti", 1), "Ti")], skip_src=[pair]), FadeOut(pair), FadeOut(pb), FadeOut(il),
                  run_time=1.3)
        self.step_done(sideg, L0, L1, L2, L3)

        # 6. T^{-1} A T = D
        br = under_bracket(L3.ks("Ti", "A", "T2"), YELLOW_C)
        bl = M("=", "D", size=0.8).next_to(br, DOWN, buff=0.1)
        frm = label("from AT = TD", 20, DIM).next_to(bl, RIGHT, buff=0.25)
        L4 = M(("zd", r"\dot{z}"), "=", "D", "z", size=1.45).move_to([0, -2.55, 0])
        bx = hbox(L4, GREEN_C, 0.18)
        stars = VGroup(label("★", 30, YELLOW_C).next_to(bx, LEFT, buff=0.2), label("★", 30, YELLOW_C).next_to(bx, RIGHT, buff=0.2))
        self.play(self.chip("T⁻¹AT = D"), ShowCreation(br), FadeIn(bl), FadeIn(frm), run_time=0.9)
        L3c = M(("zd", r"\dot{z}"), "=", ("Ti", "T^{-1}"), "A", ("T2", "T"), "z", size=S).move_to(L3)
        self.play(self.tmorph(L3c, L4, pairs=[(L3c.ks("Ti", "A", "T2"), "D")]), run_time=1.4)
        self.play(ShowCreation(bx), FadeIn(stars), run_time=0.7)
        self.step_done(sideg, L0, L1, L2, L3, br, bl, frm, L4, bx, stars)


# ======================================================================== Section 4

class DecoupledSequence(ControlScene):
    SEQ_ID = "decoupled"

    def construct(self):
        e0 = M(("zd", r"\dot{z}"), "=", "D", "z", size=1.6).move_to([0, 0.6, 0])
        self.start(e0)

        # 1. write it out
        top = M(("zd", r"\dot{z}"), "=", "D", "z", size=1.1).move_to([0, 2.7, 0])
        ddt = M(("ddt", r"\frac{d}{dt}"), size=0.95)
        zc1 = col("z_1", "z_2", r"\vdots", "z_n", size=0.8)
        eqm = M("=", size=0.95)
        diag = Mat([[r"\lambda_1", "0", "0", "0"], ["0", r"\lambda_2", "0", "0"], ["0", "0", r"\ddots", "0"],
                    ["0", "0", "0", r"\lambda_n"]], size=0.8)
        for i in range(4):
            for j in range(4):
                diag.e[i][j].set_fill(YELLOW_C if i == j and i != 2 else (FG if i == j else DIM))
        zc2 = col("z_1", "z_2", r"\vdots", "z_n", size=0.8)
        for c in (zc1, zc2):
            for r in c.e:
                if r[0].tex != r"\vdots":
                    r[0].set_fill(GREEN_C)
        row = place_row(ddt, zc1, eqm, diag, zc2, buff=0.3).move_to([0, 0.15, 0])
        self.play(self.chip("write out the matrices"), ReplacementTransform(e0, top), run_time=0.8)
        self.play(TransformFromCopy(top.k("zd"), VGroup(ddt, zc1)), TransformFromCopy(top.k("="), eqm),
                  TransformFromCopy(top.k("D"), diag), TransformFromCopy(top.k("z"), zc2), run_time=1.6)
        offd = VGroup(*[diag.e[i][j] for i in range(4) for j in range(4) if i != j])
        ol = label("zeros off the diagonal", 22, DIM).next_to(row, DOWN, buff=0.35)
        self.play(Indicate(offd, color=DIM, scale_factor=1.15), FadeIn(ol), run_time=0.9)
        self.step_done(top, row, ol)

        # 2. rows decouple
        names = [("1", 0), ("2", 1), ("n", 3)]
        scal = []
        for n, _ in names:
            scal.append(M(("zd", rf"\dot{{z}}_{n}"), "=", ("lam", rf"\lambda_{n}"), ("z", rf"z_{n}"), size=0.95))
        sep1, sep2 = M(",", size=0.95), M(",", r"\ldots", ",", size=0.95)
        srow = place_row(scal[0], sep1, scal[1], sep2, scal[2], buff=0.25).move_to([0, -2.0, 0])
        self.play(self.chip("row by row"), FadeOut(ol), run_time=0.5)
        for (n, i), sc in zip(names, scal):
            hb = VGroup(hbox(zc1.e[i][0], GREEN_C, 0.05), hbox(diag.row(i), YELLOW_C, 0.05), hbox(zc2.e[i][0], GREEN_C, 0.05))
            self.play(ShowCreation(hb), run_time=0.4)
            self.play(TransformFromCopy(zc1.e[i][0], sc.k("zd")), FadeIn(sc.k("=")), TransformFromCopy(diag.e[i][i], sc.k("lam")),
                      TransformFromCopy(zc2.e[i][0], sc.k("z")), FadeOut(hb), run_time=0.9)
        self.play(FadeIn(VGroup(sep1, sep2)), run_time=0.3)
        dl = label("ż₁ depends only on z₁, ż₂ only on z₂, …", 22, GREEN_C).next_to(srow, DOWN, buff=0.3)
        self.play(FadeIn(dl), run_time=0.5)
        self.step_done(top, row, srow, dl)

        # 3. solve each
        self.play(self.chip("solve ẏ = λy in every row"), FadeOut(VGroup(row, dl, sep1, sep2)), run_time=0.6)
        ys = [1.2, 0.0, -1.5]
        sols, arrows = [], []
        anims = []
        for (n, _), sc, y in zip(names, scal, ys):
            anims.append(sc.animate.move_to([-3.3, y, 0]))
        dots = M(r"\vdots", size=0.9).move_to([-3.3, -0.75, 0])
        self.play(*anims, FadeIn(dots), run_time=1.0)
        for (n, _), sc, y in zip(names, scal, ys):
            so = M(("zt", rf"z_{n}(t)"), "=", ("eD", rf"e^{{\lambda_{n} t}}"), ("z0", rf"z_{n}(0)"), size=0.95).move_to([2.6, y, 0])
            ar = arrow([-1.6, y + 0.08, 0], [0.6, y + 0.08, 0], color=DIM)
            self.play(GrowFromPoint(ar, ar[0].get_points()[0]), TransformFromCopy(sc.k("z"), so.k("zt")), FadeIn(so.k("=")),
                      TransformFromCopy(sc.k("lam"), so.k("eD")), FadeIn(so.k("z0")), run_time=0.9)
            sols.append(so)
            arrows.append(ar)
        dots2 = M(r"\vdots", size=0.9).move_to([2.6, -0.75, 0])
        self.play(FadeIn(dots2), run_time=0.3)
        self.step_done(top, *scal, dots, *sols, *arrows, dots2)

        # 4. e^{Dt}
        zt = M(("zt", "z(t)"), "=", ("eD", "e^{Dt}"), ("z0", "z(0)"), size=1.1)
        Em = Mat([[r"e^{\lambda_1 t}", "0", "0"], ["0", r"\ddots", "0"], ["0", "0", r"e^{\lambda_n t}"]], size=0.85)
        for i in range(3):
            for j in range(3):
                Em.e[i][j].set_fill(YELLOW_C if (i == j and i != 1) else (FG if i == j else DIM))
        el = M((",", r",\quad"), ("eD", "e^{Dt}"), "=", size=1.1)
        erow = place_row(zt, el, Em, buff=0.3).move_to([0, 0.2, 0])
        for k in ("zt", "z0"):
            zt.k(k).set_fill(GREEN_C)
        zl = label("off-diagonal entries are 0 (not e⁰ = 1)", 22, ORANGE_C).next_to(erow, DOWN, buff=0.4)
        lam = label("the book writes Λ for this D", 20, DIM).next_to(zl, DOWN, buff=0.2)
        self.play(self.chip("stack the modes"), FadeOut(VGroup(*scal, dots, *arrows, dots2)), run_time=0.6)
        self.play(FadeIn(zt), FadeIn(el), FadeIn(Em.lb), FadeIn(Em.rb),
                  TransformFromCopy(sols[0].k("eD"), Em.e[0][0]), TransformFromCopy(sols[2].k("eD"), Em.e[2][2]),
                  FadeIn(Em.e[1][1]), *[FadeOut(s) for s in sols], run_time=1.5)
        offd = VGroup(*[Em.e[i][j] for i in range(3) for j in range(3) if i != j])
        self.play(FadeIn(offd, lag_ratio=0.1), FadeIn(zl), run_time=0.9)
        self.play(FadeIn(lam), run_time=0.4)
        self.step_done(top, erow, zl, lam)

        # 5. two modes, two clocks
        small = erow.copy().scale(0.62).move_to([0, 2.0, 0])
        pl = Plot(t_max=4, y_min=0, y_max=1.1, width=7.0, height=3.0, t_label="t", y_label="z_i(t)").move_to([-1.3, -0.9, 0])
        f1 = pl.curve(lambda t: np.exp(-t), color=GREEN_C, width=5)
        f2 = pl.curve(lambda t: np.exp(-2 * t), color=YELLOW_C, width=5)
        l1 = M(("z", "z_1"), "=", "e^{-t}", size=0.85).next_to(pl, RIGHT, buff=0.4).shift(0.5 * UP)
        l2 = M(("z", "z_2"), "=", "e^{-2t}", size=0.85).next_to(l1, DOWN, buff=0.45).align_to(l1, LEFT)
        l2.set_fill(YELLOW_C)
        ex = label("guide's example: λ₁ = −1, λ₂ = −2, z(0) = (1, 1)", 22, DIM).move_to([0, 2.95, 0])
        d1 = Dot(pl.c2p(0, 1), radius=0.08).set_fill(GREEN_C, 1)
        d2 = Dot(pl.c2p(0, 1), radius=0.08).set_fill(YELLOW_C, 1)
        self.play(self.chip("each mode on its own clock"), FadeOut(VGroup(zl, lam, top)), ReplacementTransform(erow, small),
                  run_time=0.9)
        self.play(FadeIn(pl), FadeIn(ex), run_time=0.6)
        self.play(ShowCreation(f1), ShowCreation(f2), MoveAlongPath(d1, f1), MoveAlongPath(d2, f2), run_time=2.2)
        self.play(FadeIn(l1), FadeIn(l2), run_time=0.5)
        self.step_done(small, pl, f1, f2, d1, d2, l1, l2, ex)


# ======================================================================== Section 5

def _series(size, terms):
    toks = [("eAt", "e^{At}"), "="]
    for i, t in enumerate(terms):
        if i:
            toks.append("+")
        toks.append(t)
    toks += ["+", r"\cdots"]
    return M(*toks, size=size)


class SimilaritySequence(ControlScene):
    SEQ_ID = "similarity-proof"

    def construct(self):
        ser = _series(1.15, [("I", "I"), ("A1", "At"), ("A2", r"\frac{A^2t^2}{2!}"), ("A3", r"\frac{A^3t^3}{3!}")]).move_to([0, 0.4, 0])
        self.start(ser)

        # 1. A = T D T^{-1}
        self.play(self.chip("× T⁻¹ on the right"), ser.animate.move_to([0, 2.6, 0]), run_time=0.8)
        r0 = M("A", "T", "=", ("T", "T"), "D", size=1.25).move_to([0, 1.0, 0])
        r1 = M("A", ("Tx", "T"), ("Tix", "T^{-1}"), "=", "T", "D", ("Ti", "T^{-1}"), size=1.25).move_to([0, 1.0, 0])
        r2 = M("A", "=", "T", "D", ("Ti", "T^{-1}"), size=1.25).move_to([0, 1.0, 0])
        self.play(Write(r0), run_time=0.8)
        self.play(self.tmorph(r0, r1, pairs=[(("T", 0), "Tx"), (("T", 1), "T")]), run_time=1.1)
        pb = hbox(r1.ks("Tx", "Tix"), YELLOW_C, 0.06)
        il = M("=", "I", size=0.8).next_to(pb, DOWN, buff=0.12)
        self.play(ShowCreation(pb), FadeIn(il), run_time=0.6)
        self.play(self.tmorph(r1, r2), FadeOut(pb), FadeOut(il), run_time=1.1)
        self.step_done(ser, r2)

        # 2. A^2 = (TDT^-1)(TDT^-1) = TD(T^-1 T)DT^-1 = T D^2 T^-1
        S = 1.0
        a = M(("A2", "A^2"), "=", "(", "T", "D", ("Ti", "T^{-1}"), ")", "(", "T", "D", ("Ti", "T^{-1}"), ")", size=S).move_to([-2.0, -0.1, 0])
        b = M("=", "T", "D", "(", ("Ti", "T^{-1}"), "T", ")", "D", ("Ti", "T^{-1}"), size=S)
        c = M("=", "T", ("D2", "D^2"), ("Ti", "T^{-1}"), size=S)
        b.next_to(a, DOWN, buff=0.55).align_to(a.k("="), LEFT)
        c.next_to(b, DOWN, buff=0.55).align_to(a.k("="), LEFT)
        self.play(self.chip("A² = A·A"), r2.animate.scale(0.75).to_corner(UR, buff=0.45).shift(0.0 * DOWN), run_time=0.7)
        self.play(FadeIn(a.ks("A2", "=")), FadeIn(VGroup(*a.all("("), *a.all(")"))),
                  TransformFromCopy(r2.ks("T", "D", "Ti"), VGroup(a.k("T", 0), a.k("D", 0), a.k("Ti", 0))),
                  TransformFromCopy(r2.ks("T", "D", "Ti"), VGroup(a.k("T", 1), a.k("D", 1), a.k("Ti", 1))), run_time=1.3)
        self.play(self.tmorph(a, b, keep_src=True, skip_src=[a.k("A2")]), run_time=1.4)
        pair = VGroup(b.k("("), b.k("Ti", 0), b.k("T", 1), b.k(")"))
        pb = hbox(pair, YELLOW_C, 0.06)
        il = label("adjacent pair = I", 20, YELLOW_C).next_to(b, RIGHT, buff=0.5)
        self.play(ShowCreation(pb), FadeIn(il), run_time=0.6)
        self.play(self.tmorph(b, c, keep_src=True, pairs=[(("T", 0), "T"), (("D", 0), "D2"), (("Ti", 1), "Ti")]),
                  TransformFromCopy(b.k("D", 1), c.k("D2")), run_time=1.3)
        self.step_done(ser, r2, a, b, pb, il, c)

        # 3. A^k
        cc = M(("A2", "A^2"), "=", "T", ("D2", "D^2"), ("Ti", "T^{-1}"), size=S).move_to([-3.0, 1.15, 0])
        ak = M(("Ak", "A^k"), "=", "(", "T", "D", ("Ti", "T^{-1}"), ")", "(", "T", "D", ("Ti", "T^{-1}"), ")", r"\cdots",
               "(", "T", "D", ("Ti", "T^{-1}"), ")", size=S).move_to([0, -0.2, 0])
        akr = M(("Ak", "A^k"), "=", "T", ("Dk", "D^k"), ("Ti", "T^{-1}"), size=1.3).move_to([0, -1.75, 0])
        self.play(self.chip("k factors"), FadeOut(VGroup(a, b, pb, il)), ReplacementTransform(c, cc.span("=", "Ti")),
                  FadeIn(cc.k("A2")), run_time=0.9)
        self.play(FadeIn(ak, lag_ratio=0.03), run_time=1.2)
        pairs = VGroup(hbox(VGroup(ak.k("Ti", 0), ak.k("T", 1)), YELLOW_C, 0.05),
                       hbox(VGroup(ak.k("Ti", 1), ak.k(r"\cdots"), ak.k("T", 2)), YELLOW_C, 0.05))
        kl = label("every inner T⁻¹T = I;  k copies of D remain", 22, YELLOW_C).next_to(ak, DOWN, buff=0.25)
        self.play(ShowCreation(pairs), FadeIn(kl), run_time=0.8)
        self.play(TransformFromCopy(ak.k("Ak"), akr.k("Ak")), FadeIn(akr.k("=")), TransformFromCopy(ak.k("T", 0), akr.k("T")),
                  TransformFromCopy(VGroup(*ak.all("D")), akr.k("Dk")), TransformFromCopy(ak.k("Ti", 2), akr.k("Ti")),
                  run_time=1.3)
        abox = hbox(akr, GREEN_C, 0.15)
        self.play(ShowCreation(abox), FadeOut(kl), run_time=0.5)
        self.step_done(ser, r2, cc, ak, pairs, akr, abox)

        # 4. substitute into the series, I = T T^{-1}
        sub = M(("eAt", "e^{At}"), "=", ("I1", "T"), ("I2", "T^{-1}"), "+", ("T", "T"), ("D", "D"), ("Ti", "T^{-1}"), ("t", "t"), "+",
                ("A2", r"\frac{TD^2T^{-1}t^2}{2!}"), "+", ("A3", r"\frac{TD^3T^{-1}t^3}{3!}"), "+", r"\cdots", size=1.0)
        sub.move_to([0, 0.6, 0])
        akm = akr.copy().scale(0.6).next_to(r2, DOWN, buff=0.3).align_to(r2, RIGHT)
        self.play(self.chip("A^k → T D^k T⁻¹,  I → T T⁻¹"), FadeOut(VGroup(cc, ak, pairs, abox)),
                  ReplacementTransform(akr, akm), ser.animate.to_edge(LEFT, buff=0.5), run_time=0.9)
        self.play(self.tmorph(ser, sub, keep_src=True, pairs=[("I", VGroup(sub.k("I1"), sub.k("I2"))),
                                                               ("A1", sub.ks("T", "D", "Ti", "t"))]), run_time=1.8)
        tl = label("write I = T T⁻¹ so every term has the same shape", 22, DIM).next_to(sub, DOWN, buff=0.45)
        self.play(FadeIn(tl), Indicate(sub.ks("I1", "I2"), color=YELLOW_C), run_time=0.9)
        self.step_done(ser, r2, akm, sub, tl)

        # 5. factor T left, T^{-1} right
        inner = M(("I", "I"), "+", ("Dt", "Dt"), "+", ("A2", r"\frac{D^2t^2}{2!}"), "+", ("A3", r"\frac{D^3t^3}{3!}"), "+", r"\cdots",
                  size=1.0)
        lhs = M(("eAt", "e^{At}"), "=", "T", size=1.0)
        rhs = M(("Ti", "T^{-1}"), size=1.0)
        fac = place_row(lhs, inner, rhs, buff=0.45).move_to([0, -1.0, 0])
        bk = brackets(inner)
        sub_t = VGroup(sub.k("I1"), sub.k("T"))
        sub_ti = VGroup(sub.k("I2"), sub.k("Ti"))
        tb = VGroup(hbox(sub.k("I1"), BLUE_C, 0.04), hbox(sub.k("T"), BLUE_C, 0.04))
        tib = VGroup(hbox(sub.k("I2"), PINK_C, 0.04), hbox(sub.k("Ti"), PINK_C, 0.04))
        self.play(self.chip("T on the left, T⁻¹ on the right"), FadeOut(tl), ShowCreation(tb), ShowCreation(tib), run_time=0.8)
        self.play(TransformFromCopy(sub.k("eAt"), lhs.k("eAt")), TransformFromCopy(sub.k("="), lhs.k("=")),
                  TransformFromCopy(sub_t, VGroup(lhs.k("T"))), TransformFromCopy(sub_ti, VGroup(rhs.k("Ti"))),
                  ShowCreation(bk), run_time=1.3)
        self.play(FadeIn(inner.k("I"), shift=0.2 * DOWN),
                  TransformFromCopy(sub.ks("D", "t"), inner.k("Dt")), TransformFromCopy(sub.k("A2"), inner.k("A2")),
                  TransformFromCopy(sub.k("A3"), inner.k("A3")), FadeIn(VGroup(*inner.all("+"), inner.k(r"\cdots"))),
                  FadeOut(tb), FadeOut(tib), run_time=1.5)
        sl = label("t, t², 2!, … are scalars; the order of T and T⁻¹ is kept", 20, DIM).next_to(fac, DOWN, buff=0.35)
        self.play(FadeIn(sl), run_time=0.5)
        self.step_done(ser, r2, akm, sub, fac, bk, sl)

        # 6. recognize e^{Dt}
        br = under_bracket(inner, YELLOW_C)
        bl = M("=", ("eD", "e^{Dt}"), size=0.85).next_to(br, DOWN, buff=0.1)
        fin = M(("eAt", "e^{At}"), "=", "T", ("eD", "e^{Dt}"), ("Ti", "T^{-1}"), size=1.4)
        self.play(self.chip("the bracket is e^{Dt}"), FadeOut(sl), ShowCreation(br), FadeIn(bl), run_time=0.9)
        fac_all = VGroup(fac, bk, br, bl)
        self.play(FadeOut(VGroup(sub, ser)), fac_all.animate.move_to([0, 1.5, 0]), run_time=0.8)
        fin.move_to([0, -1.2, 0])
        self.play(TransformFromCopy(lhs, fin.span("eAt", "T")), TransformFromCopy(bl.k("eD"), fin.k("eD")),
                  TransformFromCopy(rhs, fin.k("Ti")), run_time=1.4)
        fb = hbox(fin, GREEN_C, 0.2)
        fl = label("one diagonal exponential and two matrix products", 22, GREEN_C).next_to(fb, DOWN, buff=0.25)
        self.play(ShowCreation(fb), FadeIn(fl), run_time=0.7)
        self.step_done(r2, akm, fac_all, fin, fb, fl)


# ======================================================================== Section 6

def node(mx, color):
    r = RoundedRectangle(width=max(mx.get_width() + 0.5, 1.6), height=mx.get_height() + 0.45, corner_radius=0.14)
    r.set_stroke(color, 3).set_fill(BG, 1).move_to(mx)
    g = VGroup(r, mx)
    g.box = r
    return g


class PipelineSequence(ControlScene):
    SEQ_ID = "map-evolve-map"

    def construct(self):
        e0 = M(("xt", "x(t)"), "=", ("eAt", "e^{At}"), ("x0", "x(0)"), "=", "T", ("eD", "e^{Dt}"), ("Ti", "T^{-1}"),
               ("x0", "x(0)"), size=1.3).move_to([0, 0.6, 0])
        rl = label("read right to left", 22, DIM).next_to(e0, DOWN, buff=0.4)
        self.start(e0, rl)

        # 1. the three stages
        top = M(("xt", "x(t)"), "=", ("eAt", "e^{At}"), ("x0", "x(0)"), "=", "T", ("eD", "e^{Dt}"), ("Ti", "T^{-1}"),
                ("x0", "x(0)"), size=1.04).move_to([0, 2.7, 0])
        xs = [-5.0, -1.7, 1.7, 5.0]
        n_x0 = node(M(("x0", "x(0)"), size=1.0), TEAL_C).move_to([xs[0], 0.4, 0])
        n_z0 = node(M(("z0", "z(0)"), size=1.0), GREEN_C).move_to([xs[1], 0.4, 0])
        n_zt = node(M(("zt", "z(t)"), size=1.0), GREEN_C).move_to([xs[2], 0.4, 0])
        n_xt = node(M(("xt", "x(t)"), size=1.0), TEAL_C).move_to([xs[3], 0.4, 0])
        nodes = [n_x0, n_z0, n_zt, n_xt]
        arrs, labs = [], []
        for (a, b), key in zip(zip(nodes, nodes[1:]), ("Ti", "eD", "T")):
            ar = arrow(a.get_right() + 0.08 * RIGHT, b.get_left() + 0.08 * LEFT, color=FG)
            lb = M((key, {"Ti": "T^{-1}", "eD": "e^{Dt}", "T": "T"}[key]), size=0.95).next_to(ar, UP, buff=0.12)
            arrs.append(ar)
            labs.append(lb)
        caps = VGroup(label("physical", 20, TEAL_C).next_to(n_x0, DOWN, buff=0.2),
                      label("eigen coords", 20, GREEN_C).next_to(n_z0, DOWN, buff=0.2),
                      label("eigen coords", 20, GREEN_C).next_to(n_zt, DOWN, buff=0.2),
                      label("physical", 20, TEAL_C).next_to(n_xt, DOWN, buff=0.2))
        stage = VGroup(label("1  map", 22, PINK_C).next_to(arrs[0], DOWN, buff=0.75),
                       label("2  evolve (decoupled)", 22, YELLOW_C).next_to(arrs[1], DOWN, buff=0.75),
                       label("3  map back", 22, BLUE_C).next_to(arrs[2], DOWN, buff=0.75))
        tag = label("lecture 22:22", 22, YELLOW_C).to_corner(UR, buff=0.35)
        self.play(self.chip("x(0) → z(0) → z(t) → x(t)"), FadeOut(rl), ReplacementTransform(e0, top), run_time=0.9)
        self.play(TransformFromCopy(top.k("x0", 1), n_x0[1]), ShowCreation(n_x0.box), run_time=0.8)
        for i, key in enumerate(("Ti", "eD", "T")):
            self.play(GrowFromPoint(arrs[i], arrs[i][0].get_points()[0]), TransformFromCopy(top.k(key), labs[i]),
                      FadeIn(nodes[i + 1], shift=0.2 * RIGHT), run_time=0.9)
        self.play(FadeIn(caps), FadeIn(stage, lag_ratio=0.3), FadeIn(tag), run_time=1.0)
        diagram = VGroup(*nodes, *arrs, *labs, caps, stage)
        self.step_done(top, diagram, tag)

        # 2. map: z(0) = T^{-1} x(0)
        sm = VGroup(*nodes, *arrs, *labs, caps)
        self.play(self.chip("guide's example: x(0) = (2, 1)"), FadeOut(VGroup(stage, top)),
                  sm.animate.scale(0.62).move_to([0, 2.6, 0]), run_time=0.9)
        given = label("T = [[1, 1], [0, 1]],  D = diag(−1, −2),  A = [[−1, −1], [0, −2]]   (authored example)", 20, DIM)
        given.move_to([0, 1.55, 0])
        hl = hbox(VGroup(n_x0, arrs[0], n_z0), PINK_C, 0.08)
        Ti = Mat([["1", "-1"], ["0", "1"]], size=0.95)
        x0v = col("2", "1", size=0.95)
        z0v = col("1", "1", size=0.95)
        for e in z0v.e:
            e[0].set_fill(GREEN_C)
        for e in x0v.e:
            e[0].set_fill(TEAL_C)
        row = place_row(M(("z0", "z(0)"), "=", size=1.05), Ti, x0v, M("=", size=1.05), z0v, buff=0.25).move_to([0, 0.0, 0])
        arith = label("row 1: 1·2 + (−1)·1 = 1     row 2: 0·2 + 1·1 = 1", 22, FG).next_to(row, DOWN, buff=0.45)
        wrongT = label("(the transpose Tᵀ would give (2, 3): wrong)", 20, RED_C).next_to(arith, DOWN, buff=0.25)
        self.play(FadeIn(given), ShowCreation(hl), run_time=0.7)
        self.play(FadeIn(row[0]), FadeIn(Ti), TransformFromCopy(n_x0[1], x0v), run_time=1.1)
        self.play(FadeIn(arith), run_time=0.6)
        self.play(FadeIn(row[3]), TransformFromCopy(VGroup(Ti, x0v), z0v), run_time=1.1)
        self.play(FadeIn(wrongT), run_time=0.4)
        self.step_done(sm, tag, given, hl, row, arith, wrongT)

        # 3. evolve
        hl2 = hbox(VGroup(n_z0, arrs[1], n_zt), YELLOW_C, 0.08)
        Ed = Mat([["e^{-t}", "0"], ["0", "e^{-2t}"]], size=0.9)
        for (i, j) in [(0, 1), (1, 0)]:
            Ed.e[i][j].set_fill(DIM)
        for i in range(2):
            Ed.e[i][i].set_fill(YELLOW_C)
        z0b = col("1", "1", size=0.9)
        ztv = col("e^{-t}", "e^{-2t}", size=0.9)
        for c in (z0b, ztv):
            for e in c.e:
                e[0].set_fill(GREEN_C)
        row2 = place_row(M(("zt", "z(t)"), "=", size=1.0), Ed, z0b, M("=", size=1.0), ztv, buff=0.25).move_to([0, -0.1, 0])
        half = col("1/2", "1/4", size=0.85)
        for e in half.e:
            e[0].set_fill(GREEN_C)
        at = place_row(M("t", "=", r"\ln 2", ":", size=0.95), M(("zt", "z"), "=", size=0.95), half, buff=0.25).move_to([0, -1.75, 0])
        self.play(self.chip("each mode decays on its own"), FadeOut(VGroup(hl, row[0], Ti, x0v, row[3], arith, wrongT)),
                  z0v.animate.move_to(z0b), run_time=0.9)
        self.play(ShowCreation(hl2), FadeIn(row2[0]), FadeIn(Ed), run_time=0.9)
        self.remove(z0v)
        self.add(z0b)
        self.play(FadeIn(row2[3]), TransformFromCopy(VGroup(Ed.e[0][0], Ed.e[1][1]), VGroup(ztv.e[0][0], ztv.e[1][0])),
                  FadeIn(VGroup(ztv.lb, ztv.rb)), run_time=1.2)
        self.play(FadeIn(at), run_time=0.7)
        self.step_done(sm, tag, given, hl2, row2, at)

        # 4. map back
        hl3 = hbox(VGroup(n_zt, arrs[2], n_xt), BLUE_C, 0.08)
        Tm = Mat([["1", "1"], ["0", "1"]], size=0.9)
        ztb = col("e^{-t}", "e^{-2t}", size=0.9)
        for e in ztb.e:
            e[0].set_fill(GREEN_C)
        xtv = col("e^{-t} + e^{-2t}", "e^{-2t}", size=0.9)
        for e in xtv.e:
            e[0].set_fill(TEAL_C)
        row3 = place_row(M(("xt", "x(t)"), "=", size=1.0), Tm, ztb, M("=", size=1.0), xtv, buff=0.25).move_to([0, -0.1, 0])
        q = col("3/4", "1/4", size=0.85)
        for e in q.e:
            e[0].set_fill(TEAL_C)
        at2 = place_row(M("t", "=", r"\ln 2", ":", size=0.95), M("x", "=", size=0.95), q, buff=0.25).move_to([0, -1.75, 0])
        mix = label("x₁ = z₁ + z₂ mixes the modes; x₂ = z₂", 20, DIM).next_to(at2, DOWN, buff=0.3)
        self.play(self.chip("x = T z"), FadeOut(VGroup(hl2, row2[0], Ed, z0b, row2[3], at)), ztv.animate.move_to(ztb), run_time=0.9)
        self.remove(ztv)
        self.add(ztb)
        self.play(ShowCreation(hl3), FadeIn(row3[0]), FadeIn(Tm), run_time=0.8)
        self.play(FadeIn(row3[3]), TransformFromCopy(VGroup(Tm, ztb), xtv), run_time=1.3)
        self.play(FadeIn(at2), FadeIn(mix), run_time=0.7)
        self.step_done(sm, tag, given, hl3, row3, at2, mix)

        # 5. check xdot(0) = A x(0)
        d = col("-1 - 2", "-2", size=0.9)
        dr = col("-3", "-2", size=0.9)
        Am = Mat([["-1", "-1"], ["0", "-2"]], size=0.9)
        x0c = col("2", "1", size=0.9)
        r4 = place_row(M(("xd", r"\dot{x}(0)"), "=", size=1.0), d, M("=", size=1.0), Am, x0c, M("=", size=1.0), dr,
                       buff=0.22).move_to([0, -0.1, 0])
        dl = label("d/dt of the formula at t = 0", 20, TEAL_C).next_to(d, DOWN, buff=0.3)
        al = label("A x(0)", 20, FG).next_to(VGroup(Am, x0c), DOWN, buff=0.3)
        tick = label("✓ same vector;  and x(0) = (1 + 1, 1) = (2, 1)", 22, GREEN_C).move_to([0, -2.2, 0])
        self.play(self.chip("check the answer"), FadeOut(VGroup(hl3, row3, at2, mix)), run_time=0.7)
        self.play(FadeIn(r4[0]), FadeIn(d), FadeIn(dl), run_time=0.9)
        self.play(FadeIn(r4[2]), FadeIn(Am), FadeIn(x0c), FadeIn(al), run_time=0.9)
        self.play(FadeIn(r4[5]), TransformFromCopy(VGroup(Am, x0c), dr), run_time=1.0)
        self.play(FadeIn(tick), run_time=0.5)
        self.step_done(sm, tag, given, r4, dl, al, tick)

        # 6. recap
        f = M(("xt", "x(t)"), "=", "T", ("eD", "e^{Dt}"), ("Ti", "T^{-1}"), ("x0", "x(0)"), size=1.25)
        z = M(("zd", r"\dot{z}"), "=", "D", "z", size=1.25)
        rec = VGroup(f, z).arrange(RIGHT, buff=1.4).move_to([0, 0.5, 0])
        bx = hbox(rec, GREEN_C, 0.2)
        think = label("think in eigenvector coordinates; map back for physical values", 22, FG).next_to(bx, DOWN, buff=0.35)
        nxt = label("next videos: stability from eigenvalues · discrete time · adding control +Bu", 20, DIM).move_to([0, -2.1, 0])
        self.play(self.chip("recap"), FadeOut(VGroup(given, r4, dl, al, tick)), run_time=0.6)
        self.play(FadeIn(f, shift=0.1 * UP), FadeIn(z, shift=0.1 * UP), run_time=1.0)
        self.play(ShowCreation(bx), FadeIn(think), run_time=0.7)
        self.play(FadeIn(nxt), run_time=0.5)
        self.step_done(sm, tag, rec, bx, think, nxt)
