"""ManimGL scenes for Unit 8, Eigenvalues and Linear Systems (one scene per sequence).

Colour code: first eigenvector / eigenvalue teal, second pink, matrices white, results green,
decaying parts blue. Matrices use Mat (mathtext has no bmatrix). Stage bounds: |x| <= 6.3,
-2.8 <= y <= 3.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"l1": TEAL_C, "l2": PINK_C, "res": GREEN_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def V(entries, size=0.85, color=FG):
    m = Mat([[str(e)] for e in entries], size=size)
    m.set_color(color)
    return m


def row(*mobs, buff=0.18):
    return VGroup(*mobs).arrange(RIGHT, buff=buff)


class Plane2(VGroup):
    def __init__(self, center, half, unit, labels=("y₁", "y₂")):
        self.o, self.u, self.h = np.array(center, float), unit, half
        ax = VGroup(Line(self.p(-half, 0), self.p(half, 0)).set_stroke(DIM, 2), Line(self.p(0, -half), self.p(0, half)).set_stroke(DIM, 2))
        lab = VGroup(label(labels[0], 18, DIM).next_to(self.p(half, 0), DOWN, buff=0.06), label(labels[1], 18, DIM).next_to(self.p(0, half), RIGHT, buff=0.06))
        super().__init__(ax, lab)

    def p(self, x, y):
        return self.o + np.array([x * self.u, y * self.u, 0])

    def line(self, d, color, width=3):
        d = np.array(d, float) / np.linalg.norm(d)
        return DashedLine(self.p(*(-self.h * d)), self.p(*(self.h * d))).set_stroke(color, width)


# ======================================================================== Section 1

class EigCheckSequence(ControlScene):
    SEQ_ID = "eig-check"

    def construct(self):
        eq = M(("s", "y_1' = 5y_1 + y_2,\\ \\ y_2' = 3y_1 + 3y_2"), size=0.9).move_to([0, 2.8, 0])
        self.start(eq)

        A = Mat([["5", "1"], ["3", "3"]], size=0.85)
        # 1. A (1,1)
        x1 = V([1, 1], color=TEAL_C)
        r1 = V([6, 6], color=TEAL_C)
        l1 = row(A, x1, M("="), r1, M("="), M(("l", "6"), colors={"l": TEAL_C}), V([1, 1], color=TEAL_C)).move_to([0, 1.4, 0])
        work = label("5·1 + 1·1 = 6,   3·1 + 3·1 = 6", 20, DIM).next_to(l1, DOWN, buff=0.15)
        self.play(self.chip("row times column"), FadeIn(l1[:3]), run_time=0.8)
        self.play(Indicate(A.row(0), color=YELLOW_C), FadeIn(work), run_time=0.8)
        self.play(FadeIn(l1[3]), run_time=0.6)
        self.play(FadeIn(l1[4:]), run_time=0.7)
        self.step_done(eq, l1, work)

        # 2. A (1,-3)
        A2 = Mat([["5", "1"], ["3", "3"]], size=0.85)
        l2 = row(A2, V([1, -3], color=PINK_C), M("="), V([2, -6], color=PINK_C), M("="), M(("l", "2"), colors={"l": PINK_C}), V([1, -3], color=PINK_C)).move_to([0, -0.4, 0])
        work2 = label("5 − 3 = 2,   3 − 9 = −6", 20, DIM).next_to(l2, DOWN, buff=0.15)
        self.play(self.chip("second candidate"), FadeIn(l2[:3]), FadeIn(work2), run_time=0.9)
        self.play(FadeIn(l2[3:]), run_time=0.9)
        self.step_done(eq, l1, work, l2, work2)

        # 3. solution
        sol = M(("y", "y(t)"), "=", ("a", "c_1e^{6t}(1, 1)"), "+", ("b", "c_2e^{2t}(1, -3)"), size=1.0,
                colors={"a": TEAL_C, "b": PINK_C}).move_to([0, -2.2, 0])
        self.play(self.chip("each eigenvector grows at its rate"), Write(sol), run_time=1.3)
        self.play(ShowCreation(hbox(sol, GREEN_C)), run_time=0.5)
        self.step_done(eq, l1, work, l2, work2, sol, hbox(sol, GREEN_C))


# ======================================================================== Section 2

class DiagMarkovSequence(ControlScene):
    SEQ_ID = "diag-markov"

    def construct(self):
        A = Mat([["0.8", "0.3"], ["0.2", "0.7"]], size=0.8)
        top = row(M(("A", "A ="), size=0.85), A).move_to([-4.2, 2.6, 0])
        self.start(top)

        # 1. AV = V Lambda
        Vm = Mat([["0.6", "1"], ["0.4", "-1"]], size=0.8)
        for i in range(2):
            Vm.e[i][0].set_color(TEAL_C); Vm.e[i][1].set_color(PINK_C)
        Vm2 = Vm.copy()
        L = Mat([["1", "0"], ["0", "1/2"]], size=0.8)
        L.e[0][0].set_color(TEAL_C); L.e[1][1].set_color(PINK_C)
        eqn = row(A.copy(), Vm, M("="), Vm2, L).move_to([1.4, 2.6, 0])
        self.play(self.chip("eigenvectors as the columns of V"), FadeIn(eqn[0]), FadeIn(eqn[1]), run_time=0.9)
        self.play(FadeIn(eqn[2]), TransformFromCopy(eqn[1], eqn[3]), FadeIn(eqn[4]), run_time=1.2)
        self.step_done(top, eqn)

        # 2. expand u0
        e2 = M(("u", "u_0 = (1, 0)"), "=", ("a", "(0.6, 0.4)"), "+", ("b", "0.4(1, -1)"), size=0.9,
               colors={"a": TEAL_C, "b": PINK_C}).move_to([-2.6, 1.2, 0])
        P = Plane2([3.4, -0.6, 0], 1.25, 1.55, labels=("u₁", "u₂"))
        ss = Dot(P.p(0.6, 0.4), radius=0.09).set_fill(GREEN_C)
        l1 = P.line([0.6, 0.4], TEAL_C)
        l2 = P.line([1, -1], PINK_C)
        self.play(self.chip("c = V^-1 u0"), Write(e2), FadeIn(P), ShowCreation(l1), ShowCreation(l2), run_time=1.3)
        self.step_done(top, eqn, e2, P, l1, l2)

        # 3. powers
        pts = [np.array([0.6, 0.4]) + 0.4 * 0.5 ** k * np.array([1, -1]) for k in range(8)]
        dots = VGroup(*[Dot(P.p(*q), radius=0.07).set_fill(YELLOW_C) for q in pts])
        e3 = M(("u", "u_k"), "=", ("a", "(0.6, 0.4)"), "+", ("b", r"0.4\left(\frac{1}{2}\right)^k(1, -1)"), size=0.85,
               colors={"a": TEAL_C, "b": PINK_C}).move_to([-2.6, 0.0, 0])
        st = label("→ steady state (0.6, 0.4)", 22, GREEN_C).move_to([-2.6, -0.9, 0])
        self.play(self.chip("each step halves the pink part"), Write(e3), run_time=1.0)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.35), run_time=2.0)
        self.play(FadeIn(ss), FadeIn(st), run_time=0.7)
        self.step_done(top, eqn, e2, P, l1, l2, e3, dots, ss, st)


# ======================================================================== Section 3

class SolveSystemSequence(ControlScene):
    SEQ_ID = "solve-system"

    def construct(self):
        P = Plane2([-2.8, -0.2, 0], 2.6, 1.0)
        A = Mat([["-1", "2"], ["1", "-2"]], size=0.8)
        top = row(M(("A", "A ="), size=0.85), A, M(("t", r"\lambda = 0,\ -3"), size=0.85)).move_to([3.3, 2.7, 0])
        self.start(P, top)

        # 1. lines
        l0 = P.line([2, 1], TEAL_C, 4)
        l3 = P.line([1, -1], PINK_C, 3)
        t0 = label("λ = 0: (2, 1) steady", 20, TEAL_C).move_to([3.3, 1.7, 0])
        t3 = label("λ = −3: (1, −1) decays", 20, PINK_C).move_to([3.3, 1.2, 0])
        self.play(self.chip("eigenvector lines"), ShowCreation(l0), FadeIn(t0), run_time=0.9)
        self.play(ShowCreation(l3), FadeIn(t3), run_time=0.9)
        self.step_done(P, top, l0, l3, t0, t3)

        # 2. trajectories
        sol = M(("y", "y"), "=", ("a", "c_1(2, 1)"), "+", ("b", "c_2e^{-3t}(1, -1)"), size=0.85,
                colors={"a": TEAL_C, "b": PINK_C}).move_to([3.3, 0.2, 0])
        starts = [(-2, 1.5), (1.5, 2.2), (2.2, -1.2), (-1.0, -2.2), (0.5, 1.8), (-2.3, -0.6)]
        trajs, ends = VGroup(), VGroup()
        Am = np.array([[-1, 2], [1, -2]], float)
        for s in starts:
            y0 = np.array(s, float)
            c1 = (y0[0] + y0[1]) / 3.0  # y0 = c1 (2, 1) + c2 (1, -1)
            end = c1 * np.array([2.0, 1.0])
            ts = np.linspace(0, 2.5, 60)
            pts = [end + np.exp(-3 * t) * (y0 - end) for t in ts]
            trajs.add(VMobject().set_points_as_corners([P.p(*q) for q in pts]).set_stroke(YELLOW_C, 3))
            ends.add(Dot(P.p(*end), radius=0.07).set_fill(GREEN_C))
        self.play(self.chip("decay parallel to (1, -1)"), Write(sol), run_time=1.0)
        self.play(LaggedStart(*[ShowCreation(t) for t in trajs], lag_ratio=0.15), run_time=2.0)
        self.step_done(P, top, l0, l3, t0, t3, sol, trajs)

        # 3. steady states
        fin = M(("f", "y(t) \\to c_1(2, 1)"), size=0.9, colors={"f": GREEN_C}).move_to([3.3, -0.8, 0])
        self.play(self.chip("land on the steady line"), FadeIn(ends), Write(fin), run_time=1.1)
        self.step_done(P, top, l0, l3, t0, t3, sol, trajs, ends, fin)


# ======================================================================== Section 4

class ExpmSeriesSequence(ControlScene):
    SEQ_ID = "expm-series"

    def construct(self):
        s = M(("e", "e^{At}"), "=", ("I", "I"), "+", ("a", "At"), "+", ("b", r"\frac{1}{2}(At)^2"), "+", ("c", r"\frac{1}{6}(At)^3"), "+", r"\cdots",
              size=1.05).move_to([0, 2.6, 0])
        self.start(s)

        # 1. A^2 = 0
        A = Mat([["0", "1"], ["0", "0"]], size=0.8)
        sq = row(M(("A", "A^2 ="), size=0.85), A, Mat([["0", "1"], ["0", "0"]], size=0.8), M("="), Mat([["0", "0"], ["0", "0"]], size=0.8)).move_to([0, 1.2, 0])
        self.play(self.chip("square the matrix"), FadeIn(sq[:3]), run_time=0.9)
        self.play(FadeIn(sq[3:]), run_time=0.8)
        self.step_done(s, sq)

        # 2. series stops
        x1, x2 = strike(s.span("b", "c"), RED_C), strike(s.k(r"\cdots"), RED_C)
        res = row(M(("e", "e^{At} = I + At ="), size=0.95), Mat([["1", "t"], ["0", "1"]], size=0.9)).move_to([0, -0.2, 0])
        res[1].e[0][1].set_color(GREEN_C)
        self.play(self.chip("A^2, A^3, ... are zero"), ShowCreation(x1), ShowCreation(x2), run_time=0.8)
        self.play(FadeIn(res), run_time=1.0)
        self.step_done(s, sq, x1, x2, res)

        # 3. check with the equations
        ch1 = M(("a", "y_2' = 0"), ",", ("b", "y_1' = y_2"), size=0.9).move_to([0, -1.5, 0])
        ch2 = M(("y", r"y(t) = (y_1(0) + t\,y_2(0),\ y_2(0))"), size=0.9, colors={"y": GREEN_C}).move_to([0, -2.3, 0])
        self.play(self.chip("the factor t"), Write(ch1), run_time=0.9)
        self.play(Write(ch2), run_time=1.0)
        self.step_done(s, sq, x1, x2, res, ch1, ch2)


# ======================================================================== Section 5

class SymmetricSequence(ControlScene):
    SEQ_ID = "symmetric"

    def construct(self):
        P = Plane2([-2.8, -0.3, 0], 3.0, 0.75, labels=("x₁", "x₂"))
        S = Mat([["3", "1"], ["1", "3"]], size=0.85)
        top = row(M(("S", "S ="), size=0.9), S).move_to([3.4, 2.6, 0])
        circ = Circle(radius=0.75).move_to(P.p(0, 0)).set_stroke(DIM, 3)
        self.start(P, top, circ)

        # 1. eigenvalues
        e1 = M(("a", r"\lambda = 4:\ (1, 1)"), size=0.85, colors={"a": TEAL_C}).move_to([3.4, 1.5, 0])
        e2 = M(("b", r"\lambda = 2:\ (1, -1)"), size=0.85, colors={"b": PINK_C}).move_to([3.4, 0.9, 0])
        l1, l2 = P.line([1, 1], TEAL_C), P.line([1, -1], PINK_C)
        self.play(self.chip("trace 6, determinant 8"), Write(e1), ShowCreation(l1), run_time=1.0)
        self.play(Write(e2), ShowCreation(l2), run_time=1.0)
        self.step_done(P, top, circ, e1, e2, l1, l2)

        # 2. circle to ellipse
        Sm = np.array([[3, 1], [1, 3]], float)
        ell = VMobject().set_points_as_corners([P.p(*(Sm @ np.array([np.cos(a), np.sin(a)]))) for a in np.linspace(0, 2 * np.pi, 200)]).set_stroke(YELLOW_C, 4)
        ax1 = arrow(P.p(0, 0), P.p(4 / np.sqrt(2), 4 / np.sqrt(2)), color=TEAL_C)
        ax2 = arrow(P.p(0, 0), P.p(2 / np.sqrt(2), -2 / np.sqrt(2)), color=PINK_C)
        dot = M(("d", "(1, 1)\\cdot(1, -1) = 0"), size=0.8).move_to([3.4, 0.1, 0])
        self.play(self.chip("apply S to the unit circle"), TransformFromCopy(circ, ell), run_time=1.5)
        self.play(grow_arrow(ax1), grow_arrow(ax2), Write(dot), run_time=1.1)
        self.step_done(P, top, circ, e1, e2, l1, l2, ell, ax1, ax2, dot)

        # 3. spectral form
        sf = M(("s", r"S = Q\Lambda Q^T"), size=0.95, colors={"s": GREEN_C}).move_to([3.4, -0.9, 0])
        qq = row(M(("q", "Q ="), size=0.8), M(("r", r"\frac{1}{\sqrt{2}}"), size=0.8), Mat([["1", "1"], ["1", "-1"]], size=0.75)).move_to([3.4, -1.9, 0])
        self.play(self.chip("perpendicular unit eigenvectors"), Write(sf), run_time=0.9)
        self.play(FadeIn(qq), run_time=0.9)
        self.step_done(P, top, circ, e1, e2, l1, l2, ell, ax1, ax2, dot, sf, qq)


# ======================================================================== Section 6

class ModesSequence(ControlScene):
    SEQ_ID = "modes"

    def construct(self):
        K = Mat([["2", "-1"], ["-1", "2"]], size=0.8)
        top = row(M(("e", "y'' + "), size=0.9), K, M(("y", "y = 0"), size=0.9)).move_to([-3.4, 2.7, 0])
        self.start(top)

        # 1. eigenvalue problem
        e1 = M(("a", r"y = \cos(\omega t)\,x"), r"\Rightarrow", ("b", r"Kx = \omega^2x"), size=0.9, colors={"b": YELLOW_C}).move_to([3.0, 2.7, 0])
        self.play(self.chip("try a pure oscillation"), Write(e1), run_time=1.2)
        self.step_done(top, e1)

        # 2. the modes: two mass-spring rows
        def springs(y, d1, d2, color):
            xs = [-5.8, -3.6 + d1, -1.4 + d2, 0.8]
            g = VGroup()
            for a, b in zip(xs[:-1], xs[1:]):
                pts = [[a + 0.25, y, 0]] + [[a + 0.25 + (b - a - 0.5) * k / 8, y + (0.15 if k % 2 else -0.15), 0] for k in range(1, 8)] + [[b - 0.25, y, 0]]
                g.add(VMobject().set_points_as_corners(pts).set_stroke(DIM, 2))
            g.add(Square(0.45).move_to([xs[1], y, 0]).set_fill(color, 0.8).set_stroke(color, 2))
            g.add(Square(0.45).move_to([xs[2], y, 0]).set_fill(color, 0.8).set_stroke(color, 2))
            g.add(Line([-5.8, y - 0.35, 0], [-5.8, y + 0.35, 0]).set_stroke(FG, 4), Line([0.8, y - 0.35, 0], [0.8, y + 0.35, 0]).set_stroke(FG, 4))
            return g
        m1 = springs(1.2, 0.4, 0.4, TEAL_C)
        m2 = springs(-0.2, 0.4, -0.4, PINK_C)
        t1 = M(("a", r"\omega^2 = 1:\ (1, 1)"), size=0.8, colors={"a": TEAL_C}).move_to([3.4, 1.2, 0])
        t2 = M(("b", r"\omega^2 = 3:\ (1, -1)"), size=0.8, colors={"b": PINK_C}).move_to([3.4, -0.2, 0])
        self.play(self.chip("eigenvalues 1 and 3"), FadeIn(m1), Write(t1), run_time=1.1)
        self.play(FadeIn(m2), Write(t2), run_time=1.1)
        self.step_done(top, e1, m1, m2, t1, t2)

        # 3. response from y(0) = (1, 0)
        p = Plot(t_max=12, y_min=-1.1, y_max=1.1, width=5.0, height=1.5, t_label="t").move_to([-3.3, -2.0, 0])
        c1 = p.curve(lambda t: 0.5 * (np.cos(t) + np.cos(np.sqrt(3) * t)), color=TEAL_C, width=3)
        c2 = p.curve(lambda t: 0.5 * (np.cos(t) - np.cos(np.sqrt(3) * t)), color=PINK_C, width=3)
        e3 = M(("y", r"y = \frac{1}{2}\cos t\,(1, 1) + \frac{1}{2}\cos\sqrt{3}t\,(1, -1)"), size=0.62).move_to([3.4, -1.6, 0])
        nl = label("mass 1 (teal), mass 2 (pink)", 18, DIM).move_to([3.4, -2.3, 0])
        self.play(self.chip("y(0) = (1, 0) splits equally"), Write(e3), FadeIn(p), run_time=1.0)
        self.play(ShowCreation(c1), ShowCreation(c2), FadeIn(nl), run_time=1.8)
        self.step_done(top, e1, m1, m2, t1, t2, p, c1, c2, e3, nl)
