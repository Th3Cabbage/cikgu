"""ManimGL scenes for the Controllability study companion (one scene per sequence in control_specs).

Rendered by build_sequences.py. Every step swaps the relation chip, animates the operation itself
(substitution, row-by-column products, assembling the columns of the controllability matrix,
column geometry) and ends with `step_done(...)`, which settles the scene to the listed mobjects.

Colour code: x teal, u and B blue, K yellow, AB / products yellow, curly C green, failures red.
Stage bounds: content stays within |x| <= 6.3 and -2.8 <= y <= 3.3 (chip sits bottom-left).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"xd": TEAL_C, "x2": TEAL_C, "l1": TEAL_C, "l2": TEAL_C, "AB": YELLOW_C, "A2B": YELLOW_C, "An": YELLOW_C,
       "cC": GREEN_C, "u2": BLUE_C}
MONO = "Consolas"


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def mat(rows, size=0.9, color=FG):
    return Mat(rows, size=size, color=color, colors=COL)


XD = ("xd", r"\dot{x}")


def node(tex, color, pos, r=0.42):
    c = Circle(radius=r).set_stroke(color, 3).set_fill(BG, 1).move_to(pos)
    return VGroup(c, M(("n", tex), size=0.9, color=color).move_to(pos))


def edge(a, b, color=FG):
    d = b.get_center() - a.get_center()
    d = d / np.linalg.norm(d)
    return arrow(a.get_center() + 0.46 * d, b.get_center() - 0.46 * d, color=color)


def console(lines, color=FG, size=20):
    t = VGroup(*[Text(s, font=MONO, font_size=size).set_color(YELLOW_C if s.startswith("ans") else color) for s in lines])
    t.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    box = RoundedRectangle(width=t.get_width() + 0.5, height=t.get_height() + 0.4, corner_radius=0.12)
    box.set_stroke(FAINT, 2).set_fill("#121826", 1).move_to(t)
    return VGroup(box, t)


def mlabel(tex, text, color=FG, size=26):
    """Math (mathtext) followed by UI text, e.g. rank C = 1 then ': uncontrollable'."""
    return VGroup(M(("m", tex), size=0.9, color=color), label(text, size, color)).arrange(RIGHT, buff=0.15)


class Grid:
    """A small fixed coordinate plane for column vectors: p(x, y) gives scene points."""
    def __init__(self, origin, unit, xr, yr):
        self.o, self.u = np.array([*origin,0] if len(origin)==2 else origin, dtype=float), unit
        lines = VGroup()
        for i in range(int(np.ceil(xr[0])), int(np.floor(xr[1])) + 1):
            if i:
                lines.add(Line(self.p(i, yr[0]), self.p(i, yr[1])))
        for j in range(int(np.ceil(yr[0])), int(np.floor(yr[1])) + 1):
            if j:
                lines.add(Line(self.p(xr[0], j), self.p(xr[1], j)))
        lines.set_stroke(FAINT, 1.5)
        axes = VGroup(Line(self.p(xr[0], 0), self.p(xr[1], 0)), Line(self.p(0, yr[0]), self.p(0, yr[1]))).set_stroke(DIM, 2.4)
        lx = M(("a", "x_1"), size=0.7, color=DIM).next_to(self.p(xr[1], 0), RIGHT, buff=0.08)
        ly = M(("a", "x_2"), size=0.7, color=DIM).next_to(self.p(0, yr[1]), UP, buff=0.06)
        self.xr, self.yr = xr, yr
        self.mob = VGroup(lines, axes, lx, ly)

    def p(self, x, y):
        return self.o + self.u * np.array([x, y, 0.0])

    def vec(self, x, y, color=FG, width=5):
        return poly_arrow([self.p(0, 0), self.p(x, y)], color=color, width=width)

    def plane(self, color=GREEN_C):
        (x0, x1), (y0, y1) = self.xr, self.yr
        return Polygon(self.p(x0, y0), self.p(x1, y0), self.p(x1, y1), self.p(x0, y1)).set_stroke(width=0).set_fill(color, 0.12)


# ======================================================================== Section 1

class InputSizesSequence(ControlScene):
    SEQ_ID = "input-sizes"

    def construct(self):
        e0 = M(XD, "=", "A", "x", size=1.5).move_to([0, 1.0, 0])
        self.start(e0)

        # 1. add Bu
        e1 = M(XD, "=", "A", "x", "+", "B", "u", size=1.5).move_to([0, 1.0, 0])
        self.play(self.chip("add an input"), run_time=0.5)
        self.play(self.tmorph(e0, e1), run_time=1.3)
        self.play(Indicate(e1.ks("B", "u"), color=BLUE_C), run_time=0.8)
        self.step_done(e1)

        # 2. shapes under each factor
        sizes = {"A": r"n\times n", "x": r"n\times 1", "B": r"n\times q", "u": r"q\times 1"}
        brs, labs = VGroup(), VGroup()
        for k, s in sizes.items():
            br = under_bracket(e1.k(k), YELLOW_C, buff=0.12, depth=0.14)
            brs.add(br)
            lab=M(("s", s), size=0.62, color=YELLOW_C).next_to(br, DOWN, buff=0.12)
            if k in ("x","u"):
                lab.shift(0.65*DOWN)
            labs.add(lab)
        dims = M("x", r"\in", ("Rn", r"\mathbb{R}^n"), ("sp", r",\quad"), "u", r"\in", ("Rq", r"\mathbb{R}^q"),
                 size=0.95).move_to([0, 2.7, 0])
        res = M(("B", "B"), ("u", "u"), ":", ("a", r"(n\times q)(q\times 1)"), "=", ("b", r"n\times 1"), size=0.95).move_to([0, -1.5, 0])
        note = label("same shape as Ax: one column of B per actuator", 24, DIM).move_to([0, -2.35, 0])
        self.play(self.chip("sizes must match"), FadeIn(dims, shift=0.1 * DOWN), run_time=0.8)
        self.play(LaggedStart(*[AnimationGroup(ShowCreation(b), FadeIn(l, shift=0.1 * DOWN)) for b, l in zip(brs, labs)],
                              lag_ratio=0.3), run_time=1.8)
        self.play(TransformFromCopy(e1.k("B"), res.k("B")), TransformFromCopy(e1.k("u"), res.k("u")),
                  FadeIn(res.ks(":", "a", "=", "b")), run_time=1.2)
        self.play(FadeIn(note), run_time=0.6)
        self.step_done(e1, brs, labs, dims, res, note)

        # 3. full-state measurement
        top = e1.copy().scale(0.75).move_to([0, 2.5, 0])
        y1 = M("y", "=", "C", "x", size=1.25).move_to([0, 0.6, 0])
        y2 = M(("C", "C"), "=", ("I", "I"), (r"\R", r"\;\Rightarrow\;"), ("y", "y"), ("e2", "="), ("x", "x"), size=1.25).move_to([0, -0.7, 0])
        note2 = label("this lecture: every state is measured (full-state feedback)", 24, DIM).move_to([0, -1.9, 0])
        self.play(self.chip("measurements"), FadeOut(VGroup(brs, labs, dims, res, note)), ReplacementTransform(e1, top), run_time=0.9)
        self.play(Write(y1), run_time=0.9)
        self.play(TransformFromCopy(y1.k("C"), y2.k("C")), FadeIn(y2.ks("=", "I")), run_time=0.9)
        self.play(FadeIn(y2.k(r"\R")), TransformFromCopy(y1.k("y"), y2.k("y")), FadeIn(y2.k("e2")),
                  TransformFromCopy(y1.k("x"), y2.k("x")), FadeIn(note2), run_time=1.1)
        self.step_done(top, y1, y2, note2)


# ======================================================================== Section 2

class FeedbackSequence(ControlScene):
    SEQ_ID = "feedback-substitution"

    def construct(self):
        e0 = M(XD, "=", "A", "x", "+", "B", "u", size=1.4).move_to([0, 1.3, 0])
        law = M("u", "=", "-", "K", "x", size=1.2).move_to([0, -0.5, 0])
        self.start(e0, law)

        # 1. substitute
        e1 = M(XD, "=", "A", "x", "+", "B", ("lp", "("), ("m", "-"), "K", ("x2", "x"), ("rp", ")"), size=1.4).move_to([0, 1.3, 0])
        self.play(self.chip("u → −Kx"), Indicate(law.ks("-", "K", "x"), color=YELLOW_C), Indicate(e0.k("u"), color=YELLOW_C), run_time=0.9)
        self.play(self.tmorph(e0, e1, skip=[e1.k("m"), e1.k("K"), e1.k("x2")]),
                  TransformFromCopy(law.k("-"), e1.k("m"), path_arc=0.4), TransformFromCopy(law.k("K"), e1.k("K"), path_arc=0.4),
                  TransformFromCopy(law.k("x"), e1.k("x2"), path_arc=0.4), run_time=1.5)
        self.step_done(e1, law)

        # 2. pull out the sign
        e2 = M(XD, "=", "A", "x", ("m", "-"), "B", "K", ("x2", "x"), size=1.4).move_to([0, 1.3, 0])
        shp = M(("B", "B"), ("K", "K"), ":", ("a", r"(n\times q)(q\times n)"), "=", ("b", r"n\times n"), size=0.95).move_to([0, -0.5, 0])
        self.play(self.chip("B(−Kx) = −BKx"), FadeOut(law), run_time=0.6)
        self.play(self.tmorph(e1, e2, path_arc=0.3), run_time=1.4)
        self.play(TransformFromCopy(e2.k("B"), shp.k("B")), TransformFromCopy(e2.k("K"), shp.k("K")),
                  FadeIn(shp.ks(":", "a", "=", "b")), run_time=1.1)
        self.step_done(e2, shp)

        # 3. factor x on the right
        e3 = M(XD, "=", ("lp", "("), "A", ("m", "-"), "B", "K", ("rp", ")"), ("x2", "x"), size=1.4).move_to([0, 1.3, 0])
        self.play(self.chip("factor x"), Indicate(e2.k("x"), color=TEAL_C), Indicate(e2.k("x2"), color=TEAL_C), run_time=0.8)
        self.play(self.tmorph(e2, e3, pairs=[("x", "x2")]), run_time=1.4)
        box = hbox(e3.span("lp", "rp"), GREEN_C)
        cl = label("closed-loop matrix: its eigenvalues decide stability", 24, GREEN_C).next_to(box, DOWN, buff=0.35)
        self.play(ShowCreation(box), FadeIn(cl, shift=0.1 * UP), run_time=0.9)
        self.step_done(e3, shp, box, cl)

        # 4. what controllability promises
        top = VGroup(e3, box).copy().scale(0.7).move_to([0, 2.6, 0])
        l1 = label("(A, B) controllable  (a property of A and B only)", 28, TEAL_C)
        a2, a3 = M(r"\Leftrightarrow", size=1.1), M(r"\Leftrightarrow", size=1.1)
        l2 = VGroup(a2, label("a suitable K puts the eigenvalues of A − BK anywhere*", 26)).arrange(RIGHT, buff=0.3)
        l3 = VGroup(a3, label("some input steers x to any state in finite time", 26)).arrange(RIGHT, buff=0.3)
        rows = VGroup(l1, l2, l3).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([0, 0.2, 0])
        foot = label("* real A, B, K: complex eigenvalues come in conjugate pairs; actuator limits are ignored", 20, DIM).move_to([0, -2.2, 0])
        self.play(self.chip("controllability"), FadeOut(VGroup(shp, cl)), ReplacementTransform(VGroup(e3, box), top), run_time=0.9)
        self.play(FadeIn(l1, shift=0.1 * DOWN), run_time=0.7)
        self.play(FadeIn(l2, shift=0.1 * DOWN), run_time=0.7)
        self.play(FadeIn(l3, shift=0.1 * DOWN), FadeIn(foot), run_time=0.8)
        self.step_done(top, rows, foot)


# ======================================================================== Section 3

def matrix_eq(A_rows, B_rows, u_rows, y, size=0.85):
    lhs = M(XD, "=", size=1.0)
    Am = mat(A_rows, size=size)
    xm = M("x", size=1.0)
    pl = M("+", size=1.0)
    Bm = mat(B_rows, size=size, color=BLUE_C)
    um = mat([[r] for r in u_rows], size=size, color=BLUE_C) if len(u_rows) > 1 else M("u", size=1.0)
    g = place_row(lhs, Am, xm, pl, Bm, um, buff=0.2).move_to([0, y, 0])
    g.Am, g.Bm = Am, Bm
    return g


class ThreeExamplesSequence(ControlScene):
    SEQ_ID = "three-examples"

    def construct(self):
        eq = matrix_eq([["1", "0"], ["0", "2"]], [["0"], ["1"]], ["u"], 0.6, size=1.0)
        self.start(eq)

        # 1. expand row by row
        eqt = matrix_eq([["1", "0"], ["0", "2"]], [["0"], ["1"]], ["u"], 2.4)
        r1 = M(("l1", r"\dot{x}_1"), "=", ("a", r"1\cdot x_1"), ("p", "+"), ("b", r"0\cdot x_2"), ("p2", "+"), ("c", r"0\cdot u"))
        r2 = M(("l2", r"\dot{x}_2"), "=", ("a", r"0\cdot x_1"), ("p", "+"), ("b", r"2x_2"), ("p2", "+"), ("c", r"1\cdot u"))
        r1.move_to([0, 0.7, 0])
        r2.next_to(r1, DOWN, buff=0.45, aligned_edge=LEFT)
        self.play(self.chip("row by row"), ReplacementTransform(eq, eqt), run_time=0.8)
        for r, i in ((r1, 0), (r2, 1)):
            hi = VGroup(hbox(eqt.Am.row(i), YELLOW_C), hbox(eqt.Bm.row(i), YELLOW_C))
            self.play(ShowCreation(hi), run_time=0.5)
            self.play(TransformFromCopy(eqt.Am.row(i), r.ks("a", "b")), TransformFromCopy(eqt.Bm.row(i), r.k("c")),
                      FadeIn(r.ks("l1" if i == 0 else "l2", "=", "p", "p2")), run_time=1.1)
            self.play(FadeOut(hi), run_time=0.3)
        s1 = M(("l1", r"\dot{x}_1"), "=", ("a", "x_1")).move_to(r1, aligned_edge=LEFT)
        s2 = M(("l2", r"\dot{x}_2"), "=", ("b", "2x_2"), ("p2", "+"), ("c", "u")).move_to(r2, aligned_edge=LEFT)
        self.play(self.tmorph(r1, s1), self.tmorph(r2, s2), run_time=1.2)
        self.step_done(eqt, s1, s2)

        # 2. x1 is out of reach
        rows = VGroup(s1, s2)
        nx1, nx2 = node("x_1", TEAL_C, [4.3, 0.9, 0]), node("x_2", TEAL_C, [4.3, -0.9, 0])
        nu = node("u", BLUE_C, [2.2, -0.9, 0])
        e_u = edge(nu, nx2, BLUE_C)
        why = label("x₁(t) = x₁(0)e^t: no input can change this free motion", 24, RED_C).move_to([0, -2.2, 0])
        tag = label("unreachable", 22, RED_C).next_to(nx1, RIGHT, buff=0.15)
        self.play(self.chip("uncontrollable"), rows.animate.shift(2.0 * LEFT), run_time=0.7)
        self.play(FadeIn(VGroup(nx1, nx2, nu)), grow_arrow(e_u), run_time=1.0)
        bad = hbox(s1, RED_C)
        self.play(ShowCreation(bad), FadeIn(tag), FadeIn(why, shift=0.1 * UP), run_time=1.0)
        self.step_done(eqt, rows, nx1, nx2, nu, e_u, bad, tag, why)

        # 3. two actuators, B = I
        eq2 = matrix_eq([["1", "0"], ["0", "2"]], [["1", "0"], ["0", "1"]], ["u_1", "u_2"], 2.4)
        t1 = M(("l1", r"\dot{x}_1"), "=", ("a", "x_1"), ("p1", "+"), ("d", "u_1")).move_to(s1, aligned_edge=LEFT)
        t2 = M(("l2", r"\dot{x}_2"), "=", ("b", "2x_2"), ("p2", "+"), ("c", "u_2")).move_to(s2, aligned_edge=LEFT)
        nu1 = node("u_1", BLUE_C, [2.2, 0.9, 0])
        nu2 = node("u_2", BLUE_C, [2.2, -0.9, 0])
        e1, e2 = edge(nu1, nx1, BLUE_C), edge(nu2, nx2, BLUE_C)
        ok = label("each state has its own knob: controllable", 24, GREEN_C).move_to([0, -2.2, 0])
        self.play(self.chip("more actuators"), FadeOut(VGroup(bad, tag, why)), FadeTransform(eqt, eq2), run_time=0.9)
        self.play(self.tmorph(s1, t1), self.tmorph(s2, t2), ReplacementTransform(nu, nu2), ReplacementTransform(e_u, e2), run_time=1.2)
        self.play(FadeIn(nu1), grow_arrow(e1), Indicate(eq2.Bm, color=BLUE_C), run_time=1.0)
        self.play(FadeIn(ok, shift=0.1 * UP), run_time=0.6)
        self.step_done(eq2, t1, t2, nx1, nx2, nu1, nu2, e1, e2, ok)

        # 4. coupling, one actuator
        eq3 = matrix_eq([["1", "1"], ["0", "2"]], [["0"], ["1"]], ["u"], 2.4)
        eq3.Am.e[0][1].set_color(YELLOW_C)
        c1 = M(("l1", r"\dot{x}_1"), "=", ("a", "x_1"), ("p1", "+"), ("d", "x_2", YELLOW_C)).move_to(t1, aligned_edge=LEFT)
        c2 = M(("l2", r"\dot{x}_2"), "=", ("b", "2x_2"), ("p2", "+"), ("c", "u")).move_to(t2, aligned_edge=LEFT)
        nu = node("u", BLUE_C, [2.2, -0.9, 0])
        e21 = edge(nx2, nx1, YELLOW_C)
        e_u = edge(nu, nx2, BLUE_C)
        msg = label("u drives x₂, and x₂ now drives x₁: controllable (rank test, Section 5)", 24, GREEN_C).move_to([0, -2.2, 0])
        self.play(self.chip("coupling"), FadeOut(VGroup(ok, nu1, e1)), FadeTransform(eq2, eq3), run_time=0.9)
        self.play(self.tmorph(t1, c1), self.tmorph(t2, c2), ReplacementTransform(nu2, nu), ReplacementTransform(e2, e_u), run_time=1.2)
        self.play(TransformFromCopy(eq3.Am.e[0][1], c1.k("d")), grow_arrow(e21), run_time=1.0)
        self.play(FadeIn(msg, shift=0.1 * UP), run_time=0.6)
        self.step_done(eq3, c1, c2, nx1, nx2, nu, e21, e_u, msg)


# ======================================================================== Section 4

class ControllabilityMatrixSequence(ControlScene):
    SEQ_ID = "controllability-matrix"

    def construct(self):
        row = M(("cC", r"\mathcal{C}"), "=", ("lb", "["), ("B", r"B\quad"), ("AB", r"AB\quad"), ("A2B", r"A^2B\quad"),
                ("cd", r"\cdots\quad"), ("An", r"A^{n-1}B"), ("rb", "]"), size=1.25).move_to([0, 0.9, 0])
        b0 = M("B", size=1.25)
        b0.move_to(row.k("B"), aligned_edge=LEFT)
        self.start(b0)

        # 1. multiply by A, again and again
        self.play(self.chip("× A on the left"), ReplacementTransform(b0, row.k("B")), run_time=0.4)
        arcs = VGroup()
        chain = ["B", "AB", "A2B", "cd", "An"]
        for a, b in zip(chain, chain[1:]):
            arc = arc_arrow(row.k(a).get_top() + 0.15 * UP, row.k(b).get_top() + 0.15 * UP, angle=-TAU / 5, color=YELLOW_C, width=3)
            tag = M(("A", "A"), size=0.6, color=YELLOW_C).next_to(arc, UP, buff=0.05)
            arcs.add(VGroup(arc, tag))
            self.play(ShowCreation(arc[0]), FadeIn(arc[1]), FadeIn(tag), TransformFromCopy(row.k(a), row.k(b)), run_time=0.75)
        self.play(FadeIn(row.ks("cC", "=", "lb", "rb")), run_time=0.7)
        self.step_done(row, arcs)

        # 2. size
        brs, labs = VGroup(), VGroup()
        for k in chain:
            if k == "cd":
                continue
            br = under_bracket(row.k(k), BLUE_C, buff=0.12, depth=0.12)
            brs.add(br)
            labs.add(M(("s", r"n\times q"), size=0.55, color=BLUE_C).next_to(br, DOWN, buff=0.1))
        sz = M(("cC", r"\mathcal{C}"), r"\in", ("R", r"\mathbb{R}^{n\times nq}"), size=1.1).move_to([0, -1.2, 0])
        note = label("n blocks of size n × q side by side (square only when q = 1)", 24, DIM).move_to([0, -2.2, 0])
        self.play(self.chip("n × nq"), ShowCreation(brs, lag_ratio=0.2), FadeIn(labs, lag_ratio=0.2), run_time=1.2)
        self.play(TransformFromCopy(row.k("cC"), sz.k("cC")), FadeIn(sz.ks(r"\in", "R")), FadeIn(note), run_time=1.0)
        self.step_done(row, arcs, brs, labs, sz, note)

        # 3. rank test
        lhs = label("controllable", 34, TEAL_C)
        rhs = M(r"\Leftrightarrow", ("rk", r"\mathrm{rank}\,"), ("cC", r"\mathcal{C}"), "=", "n", size=1.2)
        test = place_row(lhs, rhs, buff=0.35).move_to([0, -1.0, 0])
        warn = label("n independent columns span the whole state space: full ROW rank", 24, ORANGE_C).move_to([0, -2.2, 0])
        self.play(self.chip("rank n"), FadeOut(VGroup(brs, labs, note)), ReplacementTransform(sz, test), run_time=1.1)
        self.play(Indicate(rhs.k("n"), color=YELLOW_C), FadeIn(warn, shift=0.1 * UP), run_time=0.9)
        self.step_done(row, arcs, test, warn)

        # 4. discrete-time picture
        top = VGroup(row, arcs).copy().scale(0.7).move_to([0, 2.75, 0])
        hdr = M(r"x_{k+1}", "=", "A", r"x_k", "+", "B", r"u_k", (",", r",\quad"), r"x_0", ("e0", "="), "0", size=0.8).move_to([0, 1.65, 0])
        d1 = M(("x", "x_1"), "=", ("B0", "Bu_0"), size=1.0)
        d2 = M(("x", "x_2"), "=", ("AB0", "ABu_0"), "+", ("B1", "Bu_1"), size=1.0)
        d3 = M(("x", "x_3"), "=", ("A2B0", "A^2Bu_0"), ("p", "+"), ("AB1", "ABu_1"), ("p2", "+"), ("B2", "Bu_2"), size=1.0)
        d1.move_to([-2.6, 0.75, 0], aligned_edge=LEFT)
        d2.move_to([-2.6, -0.15, 0], aligned_edge=LEFT)
        d3.move_to([-2.6, -1.05, 0], aligned_edge=LEFT)
        note2 = label("authored discrete-time illustration: reachable states combine the columns of the matrix above", 22, DIM).move_to([0, -2.2, 0])
        self.play(self.chip("kick and let it ring"), FadeOut(VGroup(test, warn)), ReplacementTransform(VGroup(row, arcs), top), run_time=0.9)
        self.play(FadeIn(hdr), Write(d1), run_time=0.9)
        self.play(FadeIn(d2.ks("x", "=", "+")), TransformFromCopy(d1.k("B0"), d2.k("AB0"), path_arc=-0.6), FadeIn(d2.k("B1")), run_time=1.0)
        self.play(FadeIn(d3.ks("x", "=", "p", "p2")), TransformFromCopy(d2.k("AB0"), d3.k("A2B0"), path_arc=-0.6),
                  TransformFromCopy(d2.k("B1"), d3.k("AB1"), path_arc=-0.6), FadeIn(d3.k("B2")), run_time=1.1)
        self.play(FadeIn(note2), run_time=0.6)
        self.step_done(top, hdr, d1, d2, d3, note2)


# ======================================================================== Section 5

def given_row(A_rows, y=2.75):
    a = place_row(M("A", "="), mat(A_rows, 0.8), buff=0.15)
    b = place_row(M("B", "="), mat([["0"], ["1"]], 0.8, BLUE_C), buff=0.15)
    g = VGroup(a, b).arrange(RIGHT, buff=0.8).move_to([-2.2, y, 0])
    g.Am, g.Bm = a[1], b[1]
    return g


def product_row(A_rows, mids, res, y=1.25):
    Am = mat(A_rows, 0.8)
    Bm = mat([["0"], ["1"]], 0.8, BLUE_C)
    e1, e2 = M("=", size=0.9), M("=", size=0.9)
    mid = mat([[mids[0]], [mids[1]]], 0.8)
    rm = mat([[res[0]], [res[1]]], 0.8, YELLOW_C)
    g = place_row(Am, Bm, e1, mid, e2, rm, buff=0.2).move_to([-2.0, y, 0])
    g.Am, g.Bm, g.mid, g.res, g.eqs = Am, Bm, mid, rm, VGroup(e1, e2)
    return g


class CompareRanksSequence(ControlScene):
    SEQ_ID = "compare-ranks"

    def multiply(self, given, prod, detail):
        self.play(self.chip(detail), TransformFromCopy(given.Am, prod.Am), TransformFromCopy(given.Bm, prod.Bm),
                  FadeIn(prod.eqs[0]), FadeIn(VGroup(prod.mid.lb, prod.mid.rb)), run_time=1.0)
        for i in (0, 1):
            hi = VGroup(hbox(prod.Am.row(i), YELLOW_C), hbox(prod.Bm, YELLOW_C))
            self.play(ShowCreation(hi), run_time=0.4)
            self.play(TransformFromCopy(VGroup(prod.Am.row(i), prod.Bm.cells), prod.mid.e[i][0]), run_time=0.9)
            self.play(FadeOut(hi), run_time=0.25)
        self.play(FadeIn(prod.eqs[1]), TransformFromCopy(prod.mid, prod.res), run_time=0.9)

    def construct(self):
        grid = Grid([4.4, -2.2, 0], 0.5, (-1.5, 3.0), (-0.5, 4.5))
        given = given_row([["1", "0"], ["0", "2"]])
        self.start(given)

        # 1. AB for the uncoupled pair
        prod = product_row([["1", "0"], ["0", "2"]], [r"1\cdot0+0\cdot1", r"0\cdot0+2\cdot1"], ["0", "2"])
        self.multiply(given, prod, "A times B, row by column")
        self.step_done(given, prod)

        # 2. assemble C and draw its columns
        cm = mat([["0", "0"], ["1", "2"]], 0.85)
        cm.e[0][0].set_color(BLUE_C); cm.e[1][0].set_color(BLUE_C)
        cm.e[0][1].set_color(YELLOW_C); cm.e[1][1].set_color(YELLOW_C)
        crow = place_row(M(("cC", r"\mathcal{C}"), "="), cm, buff=0.2).move_to([-2.0, -0.25, 0])
        vb, vab = grid.vec(0, 1, BLUE_C), grid.vec(0, 2, YELLOW_C, width=3)
        lb = M(("B", "B"), size=0.7).next_to(grid.p(0, 1), LEFT, buff=0.12)
        lab = M(("AB", "AB"), size=0.7).next_to(grid.p(0, 2), LEFT, buff=0.12)
        self.play(self.chip("assemble [B  AB]"), FadeIn(crow[0]), FadeIn(VGroup(cm.lb, cm.rb)),
                  TransformFromCopy(given.Bm.cells, cm.col(0)), TransformFromCopy(prod.res.cells, cm.col(1)), run_time=1.2)
        self.play(FadeIn(grid.mob), run_time=0.6)
        self.play(grow_arrow(vab), grow_arrow(vb), FadeIn(lb), FadeIn(lab), run_time=1.0)
        self.step_done(given, prod, crow, grid.mob, vab, vb, lb, lab)

        # 3. determinant 0, rank 1, higher powers do not help
        det = M(("d", r"\mathrm{det}\,\mathcal{C}"), "=", ("a", r"0\cdot2"), ("m", "-"), ("b", r"0\cdot1"), ("e2", "="), ("z", "0"),
                size=0.95).move_to([-2.0, -1.4, 0])
        verdict = mlabel(r"\mathrm{rank}\,\mathcal{C} = 1 < 2", ": uncontrollable", RED_C).move_to([-2.0, -2.25, 0])
        v2 = grid.vec(0, 4, DIM, width=3)
        l2 = M(("A2B", r"A^2B"), size=0.6, color=DIM).next_to(grid.p(0, 4), RIGHT, buff=0.12)
        self.play(self.chip("det = 0 → rank 1"), Write(det), run_time=1.1)
        self.play(FadeIn(verdict, shift=0.1 * UP), grow_arrow(v2), FadeIn(l2), run_time=1.0)
        self.step_done(given, prod, crow, det, verdict, grid.mob, v2, l2, vab, vb, lb, lab)

        # 4. coupled A, same B
        given2 = given_row([["1", "1"], ["0", "2"]])
        given2.Am.e[0][1].set_color(YELLOW_C)
        prod2 = product_row([["1", "1"], ["0", "2"]], [r"1\cdot0+1\cdot1", r"0\cdot0+2\cdot1"], ["1", "2"])
        prod2.Am.e[0][1].set_color(YELLOW_C)
        self.play(FadeOut(VGroup(prod, crow, det, verdict, v2, l2, vab, vb, lb, lab)), FadeTransform(given, given2), run_time=0.9)
        self.multiply(given2, prod2, "coupled A, same B")
        self.step_done(given2, prod2, grid.mob)

        # 5. determinant -1, rank 2, the columns span the plane
        cm2 = mat([["0", "1"], ["1", "2"]], 0.85)
        cm2.e[0][0].set_color(BLUE_C); cm2.e[1][0].set_color(BLUE_C)
        cm2.e[0][1].set_color(YELLOW_C); cm2.e[1][1].set_color(YELLOW_C)
        crow2 = place_row(M(("cC", r"\mathcal{C}"), "="), cm2, buff=0.2).move_to([-2.0, -0.25, 0])
        det2 = M(("d", r"\mathrm{det}\,\mathcal{C}"), "=", ("a", r"0\cdot2"), ("m", "-"), ("b", r"1\cdot1"), ("e2", "="), ("z", "-1"),
                 (r"\neq", r"\neq"), ("zz", "0"), size=0.95).move_to([-2.0, -1.4, 0])
        good = mlabel(r"\mathrm{rank}\,\mathcal{C} = 2", ": controllable", GREEN_C).move_to([-2.0, -2.25, 0])
        vb, vab = grid.vec(0, 1, BLUE_C), grid.vec(1, 2, YELLOW_C)
        lb = M(("B", "B"), size=0.7).next_to(grid.p(0, 1), LEFT, buff=0.12)
        lab = M(("AB", "AB"), size=0.7).next_to(grid.p(1, 2), RIGHT, buff=0.12)
        plane = grid.plane(GREEN_C)
        self.play(self.chip("det = −1 → rank 2"), FadeIn(crow2[0]), FadeIn(VGroup(cm2.lb, cm2.rb)),
                  TransformFromCopy(given2.Bm.cells, cm2.col(0)), TransformFromCopy(prod2.res.cells, cm2.col(1)), run_time=1.1)
        self.play(grow_arrow(vb), grow_arrow(vab), FadeIn(lb), FadeIn(lab), Write(det2), run_time=1.2)
        self.play(FadeIn(plane), FadeIn(good, shift=0.1 * UP), run_time=0.9)
        self.step_done(given2, prod2, crow2, det2, good, plane, grid.mob, vb, vab, lb, lab)


# ======================================================================== Section 6

class CtrbLimitsSequence(ControlScene):
    SEQ_ID = "ctrb-limits"

    def construct(self):
        cmd = console([">> rank(ctrb(A,B))"], size=30).move_to([0, 0.8, 0])
        self.start(cmd)

        # 1. the two examples on the computer
        left = console([">> A = [1 0; 0 2]; B = [0; 1];", ">> ctrb(A,B)", "ans = [0 0; 1 2]", ">> rank(ctrb(A,B))", "ans = 1"]).move_to([-3.25, 0.7, 0])
        right = console([">> A = [1 1; 0 2]; B = [0; 1];", ">> ctrb(A,B)", "ans = [0 1; 1 2]", ">> rank(ctrb(A,B))", "ans = 2"]).move_to([3.25, 0.7, 0])
        vl = label("rank 1: not controllable", 24, RED_C).next_to(left, DOWN, buff=0.35)
        vr = label("rank 2: controllable", 24, GREEN_C).next_to(right, DOWN, buff=0.35)
        self.play(self.chip("MATLAB"), FadeTransform(cmd, left), run_time=1.0)
        self.play(FadeIn(right, shift=0.2 * LEFT), run_time=0.9)
        self.play(FadeIn(vl), FadeIn(vr), run_time=0.7)
        self.step_done(left, right, vl, vr)

        # 2. linearizations only
        nl = block("nonlinear system", 3.0, 1.0, TEAL_C, 26).move_to([-3.8, 1.2, 0])
        lin = block("linearization at a fixed point", 3.6, 1.0, BLUE_C, 24).move_to([2.6, 1.2, 0])
        ar = arrow(nl.get_right() + 0.1 * RIGHT, lin.get_left() + 0.1 * LEFT, FG)
        st1 = label("uncontrollable", 24, RED_C).next_to(lin, DOWN, buff=0.25)
        st2 = label("may still be controllable, or not", 24, ORANGE_C).next_to(nl, DOWN, buff=0.25)
        msg = label("the rank test speaks about the linear model only", 26, FG).move_to([0, -1.4, 0])
        self.play(self.chip("linear only"), FadeOut(VGroup(left, right, vl, vr)), run_time=0.6)
        self.play(FadeIn(nl), grow_arrow(ar), FadeIn(lin), run_time=1.0)
        self.play(FadeIn(st1), run_time=0.5)
        self.play(FadeIn(st2), FadeIn(msg), run_time=0.8)
        self.step_done(nl, lin, ar, st1, st2, msg)

        # 3. yes/no hides the degree: singular values of C
        base_y, unit = -1.7, 1.25
        groups = VGroup()
        for cx, title, svals, col in ((-3.0, "c = 1", (2.414, 0.414), GREEN_C), (3.0, "c = 0.1", (2.238, 0.0447), ORANGE_C)):
            bars = VGroup()
            for j, s in enumerate(svals):
                h = max(s * unit, 0.03)
                r = Rectangle(width=0.8, height=h).set_stroke(width=0).set_fill(col, 0.85)
                r.move_to([cx - 0.65 + 1.3 * j, base_y + h / 2, 0])
                v = M(("v", f"{s:.3g}"), size=0.6).next_to(r, UP, buff=0.08)
                nm = M(("s", rf"\sigma_{j + 1}"), size=0.7, color=DIM).next_to([cx - 0.65 + 1.3 * j, base_y, 0], DOWN, buff=0.12)
                bars.add(VGroup(r, v, nm))
            axis = Line([cx - 1.4, base_y, 0], [cx + 1.4, base_y, 0]).set_stroke(DIM, 2)
            ttl = label(title + ":  rank 2", 24, col).move_to([cx, 2.0, 0])
            groups.add(VGroup(axis, bars, ttl))
        hdr = label("singular values of the controllability matrix (A = [1 c; 0 2], B = [0; 1])", 24, DIM).move_to([0, 2.8, 0])
        foot = label("same yes/no answer, very different margins (SVD preview; energy needs the Gramian, later)", 20, DIM).move_to([0, -2.75, 0])
        self.play(self.chip("how controllable?"), FadeOut(VGroup(nl, lin, ar, st1, st2, msg)), FadeIn(hdr), run_time=0.7)
        for g in groups:
            self.play(FadeIn(g[0]), FadeIn(g[2]), LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in g[1]], lag_ratio=0.3),
                      FadeIn(VGroup(*[VGroup(b[1], b[2]) for b in g[1]])), run_time=1.1)
        self.play(Indicate(groups[1][1][1], color=RED_C), FadeIn(foot), run_time=0.9)
        self.step_done(hdr, groups, foot)

        # 4. what comes next
        b1 = block("why this matrix works", 3.6, 1.1, TEAL_C, 24).move_to([-4.3, 0.4, 0])
        b2 = block("degree of controllability", 3.4, 1.1, YELLOW_C, 24).move_to([0, 0.4, 0])
        b3 = block("design u = −Kx", 3.0, 1.1, GREEN_C, 24).move_to([4.3, 0.4, 0])
        a1 = arrow(b1.get_right() + 0.05 * RIGHT, b2.get_left() + 0.05 * LEFT)
        a2 = arrow(b2.get_right() + 0.05 * RIGHT, b3.get_left() + 0.05 * LEFT)
        tag = label("next lectures", 26, DIM).move_to([0, 1.8, 0])
        self.play(self.chip("next"), FadeOut(VGroup(hdr, groups, foot)), FadeIn(tag), run_time=0.6)
        self.play(FadeIn(b1), run_time=0.5)
        self.play(grow_arrow(a1), FadeIn(b2), run_time=0.7)
        self.play(grow_arrow(a2), FadeIn(b3), run_time=0.7)
        self.step_done(tag, b1, b2, b3, a1, a2)
