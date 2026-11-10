"""ManimGL scenes for Unit 9, Positive Definite Matrices and the SVD (one scene per sequence).

Colour code: first direction/singular vector teal, second pink, pivots and squares yellow,
results green, negative energy red. Matrices use Mat. Stage bounds: |x| <= 6.3, -2.8 <= y <= 3.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"p": YELLOW_C, "res": GREEN_C, "v1": TEAL_C, "v2": PINK_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def row(*mobs, buff=0.18):
    return VGroup(*mobs).arrange(RIGHT, buff=buff)


def curve_pts(pts, color, width=3):
    return VMobject().set_points_as_corners(pts).set_stroke(color, width).set_fill(opacity=0)


# ======================================================================== Section 1

class AtANonnegativeSequence(ControlScene):
    SEQ_ID = "ata-nonnegative"

    def construct(self):
        e0 = M(("A", "A^TA"), ("x", "x"), "=", ("l", r"\lambda"), ("x2", "x"), size=1.3, colors={"l": YELLOW_C}).move_to([0, 2.5, 0])
        self.start(e0)

        # 1. multiply by x^T
        e1 = M(("xt", "x^T"), ("A", "A^TA"), ("x", "x"), "=", ("l", r"\lambda"), ("xt2", "x^T"), ("x2", "x"), size=1.2,
               colors={"xt": BLUE_C, "xt2": BLUE_C, "l": YELLOW_C}).move_to([0, 1.3, 0])
        self.play(self.chip("multiply both sides by x^T"), self.tmorph(e0, e1, keep_src=True), run_time=1.4)
        self.step_done(e0, e1)

        # 2. squared length
        e2 = M(("a", "(Ax)^T"), ("b", "(Ax)"), "=", ("n", r"\|Ax\|^2"), size=1.2, colors={"n": GREEN_C}).move_to([-2.4, 0.0, 0])
        e3 = M(("xx", r"x^Tx = \|x\|^2"), size=1.0, colors={"xx": BLUE_C}).move_to([3.0, 0.0, 0])
        br = under_bracket(e1.ks("xt", "A", "x"), GREEN_C)
        self.play(self.chip("group in pairs"), ShowCreation(br), run_time=0.6)
        self.play(TransformFromCopy(e1.ks("xt", "A", "x"), e2), run_time=1.3)
        self.play(TransformFromCopy(e1.ks("xt2", "x2"), e3), run_time=1.0)
        self.step_done(e0, e1, br, e2, e3)

        # 3. sign
        e4 = M(("l", r"\lambda"), "=", ("f", r"\frac{\|Ax\|^2}{\|x\|^2}"), r"\geq", "0", size=1.3, colors={"l": YELLOW_C, "f": GREEN_C}).move_to([0, -1.6, 0])
        n = label("> 0 when the columns of A are independent", 22, GREEN_C).move_to([0, -2.5, 0])
        self.play(self.chip("divide"), TransformFromCopy(VGroup(e2.k("n"), e3), e4.k("f")), FadeIn(e4.ks("l", "=", r"\geq", "0")), run_time=1.4)
        self.play(FadeIn(n), run_time=0.6)
        self.step_done(e0, e1, br, e2, e3, e4, n)


# ======================================================================== Section 2

class FiveTestsSequence(ControlScene):
    SEQ_ID = "five-tests"

    def construct(self):
        S = Mat([["4", "6"], ["6", "10"]], size=0.95)
        top = row(M(("S", "S ="), size=0.95), S).move_to([-3.8, 2.4, 0])
        self.start(top)

        # 1. elimination
        U = Mat([["4", "6"], ["0", "1"]], size=0.95)
        U.e[0][0].set_color(YELLOW_C); U.e[1][1].set_color(YELLOW_C)
        op = label("row 2 − (6/4)·row 1:  10 − 9 = 1", 22, DIM).move_to([2.3, 2.9, 0])
        el = row(M(("a", r"\rightarrow"), size=0.95), U, label("pivots 4, 1", 24, YELLOW_C)).move_to([1.9, 2.1, 0])
        self.play(self.chip("eliminate below the first pivot"), FadeIn(op), run_time=0.7)
        self.play(TransformFromCopy(S, el[1]), FadeIn(el[0]), run_time=1.2)
        self.play(FadeIn(el[2]), run_time=0.6)
        self.step_done(top, op, el)

        # 2. determinants
        d1 = M(("a", r"\det[4] = 4"), size=0.9).move_to([-3.6, 0.8, 0])
        d2 = M(("b", r"\det S = 40 - 36 = 4 = 4\cdot1"), size=0.9, colors={"b": YELLOW_C}).move_to([1.6, 0.8, 0])
        box = SurroundingRectangle(S.e[0][0], buff=0.08).set_stroke(BLUE_C, 3)
        self.play(self.chip("upper-left determinants"), ShowCreation(box), Write(d1), run_time=1.0)
        self.play(Write(d2), run_time=1.0)
        self.step_done(top, op, el, d1, d2, box)

        # 3. energy and completing the square
        e1 = M(("E", r"x^TSx"), "=", ("q", r"4x_1^2 + 12x_1x_2 + 10x_2^2"), size=1.0).move_to([0, -0.6, 0])
        e2 = M("=", ("p1", "4"), ("s1", r"\left(x_1 + \frac{3}{2}x_2\right)^2"), "+", ("p2", "1"), (r"s2", r"\cdot x_2^2"), size=1.05,
               colors={"p1": YELLOW_C, "p2": YELLOW_C}).move_to([0.7, -1.7, 0])
        pos = label("pivots in front of squares: positive for every x ≠ 0", 22, GREEN_C).move_to([0, -2.55, 0])
        self.play(self.chip("energy"), Write(e1), run_time=1.0)
        self.play(TransformFromCopy(e1.k("q"), e2), run_time=1.3)
        self.play(Indicate(e2.k("p1"), color=YELLOW_C), Indicate(e2.k("p2"), color=YELLOW_C), FadeIn(pos), run_time=0.9)
        self.step_done(top, op, el, d1, d2, box, e1, e2, pos)


class EnergyBowlSequence(ControlScene):
    SEQ_ID = "energy-bowl"

    def construct(self):
        u = 1.0
        o1, o2 = np.array([-3.2, -0.1, 0]), np.array([3.2, -0.1, 0])

        def axes(o):
            return VGroup(Line(o + 2.4 * LEFT, o + 2.4 * RIGHT).set_stroke(DIM, 2), Line(o + 2.4 * DOWN, o + 2.4 * UP).set_stroke(DIM, 2))
        a1, a2 = axes(o1), axes(o2)
        h1 = label("S = [4 6; 6 10]", 22, TEAL_C).move_to(o1 + 2.75 * UP)
        h2 = label("S = [3 4; 4 5]", 22, PINK_C).move_to(o2 + 2.75 * UP)
        self.start(a1, a2, h1, h2)

        def levels(S, o, c, color):
            w, Q = np.linalg.eigh(np.array(S, float))
            g = VGroup()
            if np.all(w > 0):
                for lev in c:
                    pts = [o + np.array([*(Q @ np.array([np.sqrt(lev / w[0]) * np.cos(t), np.sqrt(lev / w[1]) * np.sin(t)])) * u, 0]) for t in np.linspace(0, 2 * np.pi, 160)]
                    g.add(curve_pts(pts, color))
            else:
                # hyperbola branches w0 a^2 + w1 b^2 = lev (w0 < 0 < w1) for lev > 0 and lev < 0
                for lev in c:
                    for sgn in (1, -1):
                        pts = []
                        for s in np.linspace(-2.2, 2.2, 120):
                            if lev > 0:
                                b = sgn * np.sqrt(lev / w[1]) * np.cosh(s); a = np.sqrt(lev / -w[0]) * np.sinh(s)
                            else:
                                a = sgn * np.sqrt(-lev / -w[0]) * np.cosh(s); b = np.sqrt(-lev / w[1]) * np.sinh(s)
                            p = Q @ np.array([a, b]) * u
                            if abs(p[0]) <= 2.3 and abs(p[1]) <= 2.3:
                                pts.append(o + np.array([p[0], p[1], 0]))
                        if len(pts) > 1:
                            g.add(curve_pts(pts, color if lev > 0 else RED_C))
            return g

        # 1. bowl
        e1 = levels([[4, 6], [6, 10]], o1, [0.1, 0.3, 0.6, 1.0], TEAL_C)
        t1 = label("ellipses: a bowl", 22, TEAL_C).move_to(o1 + 2.55 * DOWN + 1.0 * RIGHT)
        self.play(self.chip("positive definite"), LaggedStart(*[ShowCreation(c) for c in e1], lag_ratio=0.25), run_time=1.6)
        self.play(FadeIn(t1), run_time=0.5)
        self.step_done(a1, a2, h1, h2, e1, t1)

        # 2. saddle
        e2 = levels([[3, 4], [4, 5]], o2, [0.5, 2, -0.5, -2], PINK_C)
        t2 = label("hyperbolas: a saddle (red: negative energy)", 20, PINK_C).move_to(o2 + 2.55 * DOWN)
        self.play(self.chip("determinant -1"), LaggedStart(*[ShowCreation(c) for c in e2], lag_ratio=0.15), run_time=1.6)
        self.play(FadeIn(t2), run_time=0.5)
        self.step_done(a1, a2, h1, h2, e1, t1, e2, t2)

        # 3. the test
        tt = M(("t", r"\mathrm{bowl} \Leftrightarrow \lambda_1, \lambda_2 > 0 \Leftrightarrow \mathrm{pivots} > 0"), size=0.9, colors={"t": GREEN_C}).move_to([0, 3.2, 0])
        self.play(self.chip("eigenvalue signs decide"), FadeOut(VGroup(h1, h2)), Write(tt), run_time=1.1)
        self.step_done(a1, a2, e1, t1, e2, t2, tt)


# ======================================================================== Section 3

class SVDGeometrySequence(ControlScene):
    SEQ_ID = "svd-geometry"

    def construct(self):
        A = np.array([[3.0, 0.0], [4.0, 5.0]])
        U, s, Vt = np.linalg.svd(A)
        if U[0, 0] < 0:
            U[:, 0] *= -1; Vt[0, :] *= -1
        if U[0, 1] < 0:
            U[:, 1] *= -1; Vt[1, :] *= -1
        sc = 0.17
        o = np.array([-2.2, 0.0, 0])
        ts = np.linspace(0, 2 * np.pi, 160)
        circle = np.array([[np.cos(t), np.sin(t)] for t in ts])

        def shape(pts, color):
            return curve_pts([o + np.array([p[0] * sc * 1.0, p[1] * sc * 1.0, 0]) * 1 for p in pts], color, 4)

        def vec(p, color):
            return arrow(o, o + np.array([p[0] * sc, p[1] * sc, 0]), color=color, width=4)

        big = 2.2  # draw the circle magnified so the final ellipse fits
        circ = shape(circle * big, FG)
        v1, v2 = Vt[0] * big, Vt[1] * big
        a1, a2 = vec(v1, TEAL_C), vec(v2, PINK_C)
        ax = VGroup(Line(o + 3.6 * LEFT, o + 3.6 * RIGHT).set_stroke(FAINT, 1), Line(o + 2.9 * DOWN, o + 3.5 * UP).set_stroke(FAINT, 1))
        info = label("unit circle (drawn ×2.2), v₁ teal, v₂ pink", 20, DIM).move_to([4.0, 2.9, 0])
        self.start(ax, circ, a1, a2, info)

        # 1. V^T
        r1 = (Vt @ circle.T).T * big
        c1 = shape(r1, FG)
        b1, b2 = vec(Vt @ v1, TEAL_C), vec(Vt @ v2, PINK_C)
        t1 = M(("t", "V^T:\\ v_i \\to e_i"), size=0.85).move_to([4.0, 2.2, 0])
        self.play(self.chip("orthogonal V^T: v_i to the axes"), Transform(circ, c1), Transform(a1, b1), Transform(a2, b2), Write(t1), run_time=1.6)
        self.step_done(ax, circ, a1, a2, info, t1)

        # 2. Sigma
        r2 = (np.diag(s) @ (Vt @ circle.T)).T * big
        c2 = shape(r2, YELLOW_C)
        d1, d2 = vec(np.diag(s) @ Vt @ v1, TEAL_C), vec(np.diag(s) @ Vt @ v2, PINK_C)
        t2 = M(("t", r"\Sigma:\ \sigma_1 = 3\sqrt{5},\ \sigma_2 = \sqrt{5}"), size=0.85, colors={"t": YELLOW_C}).move_to([4.0, 1.4, 0])
        self.play(self.chip("stretch along the axes"), Transform(circ, c2), Transform(a1, d1), Transform(a2, d2), Write(t2), run_time=1.6)
        self.step_done(ax, circ, a1, a2, info, t1, t2)

        # 3. U
        r3 = (A @ circle.T).T * big
        c3 = shape(r3, GREEN_C)
        f1, f2 = vec(A @ v1, TEAL_C), vec(A @ v2, PINK_C)
        t3 = M(("t", r"U:\ Av_i = \sigma_iu_i"), size=0.85, colors={"t": GREEN_C}).move_to([4.0, 0.6, 0])
        t4 = label("final ellipse = A(circle)", 20, GREEN_C).move_to([4.0, -0.1, 0])
        self.play(self.chip("orthogonal U: turn into place"), Transform(circ, c3), Transform(a1, f1), Transform(a2, f2), Write(t3), run_time=1.6)
        self.play(FadeIn(t4), run_time=0.5)
        self.step_done(ax, circ, a1, a2, info, t1, t2, t3, t4)


class SVDExampleSequence(ControlScene):
    SEQ_ID = "svd-example"

    def construct(self):
        A = Mat([["2", "2"], ["1", "1"]], size=0.9)
        top = row(M(("A", "A ="), size=0.9), A, label("rank 1", 22, DIM)).move_to([-3.6, 2.5, 0])
        self.start(top)

        # 1. A^T A
        AtA = Mat([["5", "5"], ["5", "5"]], size=0.85)
        g1 = row(M(("a", "A^TA ="), size=0.85), AtA, M(("s", r"\sigma_1^2 = 10,\ \sigma_2^2 = 0"), size=0.85, colors={"s": YELLOW_C})).move_to([1.6, 2.5, 0])
        g1b = M(("v", r"v_1 = \frac{(1, 1)}{\sqrt{2}},\ \ v_2 = \frac{(1, -1)}{\sqrt{2}}"), size=0.85, colors={"v": TEAL_C}).move_to([1.6, 1.5, 0])
        self.play(self.chip("eigenvalues of A^T A"), FadeIn(g1), run_time=1.2)
        self.play(Write(g1b), run_time=1.0)
        self.step_done(top, g1, g1b)

        # 2. u1
        u = M(("u", "u_1"), "=", ("a", r"\frac{Av_1}{\sigma_1}"), "=", ("b", r"\frac{(4, 2)/\sqrt{2}}{\sqrt{10}}"), "=", ("c", r"\frac{(2, 1)}{\sqrt{5}}"),
              size=0.95, colors={"c": GREEN_C}).move_to([0, 0.2, 0])
        note = label("(the board keeps a −1 from an earlier version of A; here u₁ = (2, 1)/√5)", 18, DIM).move_to([0, -0.65, 0])
        self.play(self.chip("u = A v / sigma"), Write(u), run_time=1.5)
        self.play(FadeIn(note), run_time=0.6)
        self.step_done(top, g1, g1b, u, note)

        # 3. one piece
        pc = M(("A", "A"), "=", ("s", r"\sqrt{10}"), ("u", r"\frac{(2, 1)}{\sqrt{5}}"), ("v", r"\frac{(1, 1)^T}{\sqrt{2}}"), "=",
               ("r", r"\sqrt{10}\cdot\frac{1}{\sqrt{10}}\,(2, 1)(1, 1)^T"), size=0.9, colors={"s": YELLOW_C, "u": GREEN_C, "v": TEAL_C}).move_to([0, -1.6, 0])
        fin = row(M(("x", "="), size=0.9), Mat([["2", "2"], ["1", "1"]], size=0.75)).move_to([4.9, -2.45, 0])
        self.play(self.chip("sigma_2 = 0: one rank-one piece"), Write(pc), run_time=1.5)
        self.play(FadeIn(fin), run_time=0.7)
        self.step_done(top, g1, g1b, u, note, pc, fin)
