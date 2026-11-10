"""ManimGL scenes for Unit 6, Phase Plane, Linearization and Stability (one scene per sequence).

Colour code: trajectories teal, straight-line (eigenvector) solutions yellow, stable green,
unstable red, centers/neutral pink. Formulas use matplotlib mathtext (no \\tfrac, \\text, \\Big,
\\begin{bmatrix}: matrices use Mat). Stage bounds: |x| <= 6.3, -2.8 <= y <= 3.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"st": GREEN_C, "un": RED_C, "ce": PINK_C, "ev": YELLOW_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


class Plane(VGroup):
    """Axes centred at `center`; p(x, y) maps plane coordinates to the scene."""
    def __init__(self, center, half_w, half_h, unit, xl="y", yl="y'"):
        self.o, self.unit, self.hw, self.hh = np.array(center, float), unit, half_w, half_h
        ax = VGroup(Line(self.p(-half_w, 0), self.p(half_w, 0)).set_stroke(DIM, 2),
                    Line(self.p(0, -half_h), self.p(0, half_h)).set_stroke(DIM, 2))
        labs = VGroup(label(xl, 20, DIM).next_to(self.p(half_w, 0), DOWN, buff=0.08),
                      label(yl, 20, DIM).next_to(self.p(0, half_h), RIGHT, buff=0.08))
        super().__init__(ax, labs)

    def p(self, x, y):
        return self.o + np.array([x * self.unit, y * self.unit, 0])

    def inside(self, x, y):
        return abs(x) <= self.hw and abs(y) <= self.hh

    def path(self, pts, color=TEAL_C, width=3.5):
        segs, cur = [], []
        for x, y in pts:
            if self.inside(x, y):
                cur.append(self.p(x, y))
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

    def line(self, slope, color=YELLOW_C, width=3):
        # the line y' = slope * y inside the box
        xm = min(self.hw, self.hh / abs(slope)) if slope else self.hw
        return Line(self.p(-xm, -slope * xm), self.p(xm, slope * xm)).set_stroke(color, width)


def flow(f, u0, t1, n=600):
    """RK4 trajectory of u' = f(u) for t in [0, t1] (t1 may be negative)."""
    h = t1 / n
    u = np.array(u0, float)
    pts = [u.copy()]
    for _ in range(n):
        k1 = f(u)
        k2 = f(u + h * k1 / 2)
        k3 = f(u + h * k2 / 2)
        k4 = f(u + h * k3)
        u = u + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if not np.all(np.isfinite(u)) or np.max(np.abs(u)) > 1e3:
            break
        pts.append(u.copy())
    return pts


def lin(A):
    A = np.array(A, float)
    return lambda u: A @ u


# ======================================================================== Section 1

class DirectionFieldSequence(ControlScene):
    SEQ_ID = "direction-field"

    def construct(self):
        p = Plot(t_max=5, y_min=-0.5, y_max=4.5, width=7.0, height=5.0, t_label="t", y_label="y").move_to([-2.4, 0.2, 0])
        eq = M(("e", r"\frac{dy}{dt}"), "=", ("f", "2 - y"), size=1.1).move_to([4.2, 2.6, 0])
        self.start(p, eq)

        # 1. arrows on rows
        rows = VGroup()
        for yv in [0, 1, 2, 3, 4]:
            slope = 2 - yv
            for tv in np.arange(0.4, 5, 0.8):
                d = np.array([1.0, slope * (5.0 / 5.0) * (5.0 / 7.0)])  # scene-space direction (scaled axes)
                v = np.array([p.c2p(tv + 0.25, yv + 0.25 * slope)[0] - p.c2p(tv, yv)[0],
                              p.c2p(tv + 0.25, yv + 0.25 * slope)[1] - p.c2p(tv, yv)[1], 0])
                v = v / np.linalg.norm(v) * 0.32
                c = p.c2p(tv, yv)
                rows.add(arrow(c - v, c + v, color=BLUE_C, width=2.5))
        tab = M(("t", r"y = 0:\ 2,\ \ y = 1:\ 1,\ \ y = 4:\ -2"), size=0.7).move_to([4.2, 1.7, 0])
        self.play(self.chip("slope 2 - y at each height"), LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.02), run_time=2.0)
        self.play(FadeIn(tab), run_time=0.6)
        self.step_done(p, eq, rows, tab)

        # 2. the steady line
        st = Line(p.c2p(0, 2), p.c2p(5, 2)).set_stroke(GREEN_C, 5)
        stl = label("y = 2: flat arrows, steady", 20, GREEN_C).move_to([4.2, 0.8, 0])
        self.play(self.chip("y' = 0 on y = 2"), ShowCreation(st), FadeIn(stl), run_time=1.0)
        self.step_done(p, eq, rows, tab, st, stl)

        # 3. solutions
        sols = VGroup(*[p.curve(lambda t, C=C: 2 + C * np.exp(-t), color=TEAL_C, width=4) for C in (-2, -1, 1, 2)])
        sf = M(("y", "y"), "=", ("s", "2 + C e^{-t}"), size=1.0, colors={"s": TEAL_C}).move_to([4.2, -0.2, 0])
        self.play(self.chip("follow the arrows"), LaggedStart(*[ShowCreation(s) for s in sols], lag_ratio=0.3), run_time=2.0)
        self.play(Write(sf), run_time=0.8)
        self.step_done(p, eq, rows, tab, st, stl, sols, sf)


# ======================================================================== Section 2

class SourceSinkSaddleSequence(ControlScene):
    SEQ_ID = "source-sink-saddle"

    def construct(self):
        P = Plane([-2.8, -0.1, 0], 3.2, 3.0, 0.88)
        eq = M(("e", "y'' - 3y' + 2y = 0"), size=0.9).move_to([3.6, 2.7, 0])
        rt = M(("s", "s = 1,\\ 2"), size=0.85).move_to([3.6, 2.05, 0])
        self.start(P, eq, rt)

        # 1. two lines
        l1, l2 = P.line(1), P.line(2)
        t1 = label("y' = y", 20, YELLOW_C).next_to(P.p(2.4, 2.4), RIGHT, buff=0.05)
        t2 = label("y' = 2y", 20, YELLOW_C).next_to(P.p(1.4, 2.8), RIGHT, buff=0.05)
        self.play(self.chip("pure exponentials: y' = s y"), ShowCreation(l1), FadeIn(t1), run_time=1.0)
        self.play(ShowCreation(l2), FadeIn(t2), run_time=1.0)
        self.step_done(P, eq, rt, l1, l2, t1, t2)

        # 2. source: y = e^t + e^{2t}
        A = [[0, 1], [-2, 3]]
        trajs = VGroup()
        for u0 in [(0.02, 0.03), (0.03, 0.035), (-0.02, -0.03), (0.02, -0.01), (-0.03, 0.02)]:
            trajs.add(P.path(flow(lin(A), u0, 6), color=TEAL_C))
        main = P.path(flow(lin(A), (2e-3 * 2, 3e-3), 8), color=GREEN_C, width=5)
        tag = M(("t", "y = e^{t} + e^{2t}"), size=0.8, colors={"t": GREEN_C}).move_to([3.6, 1.0, 0])
        src = label("source: all trajectories leave", 20, RED_C).move_to([3.6, 0.4, 0])
        self.play(self.chip("both roots positive"), LaggedStart(*[ShowCreation(t) for t in trajs], lag_ratio=0.2), run_time=2.0)
        self.play(ShowCreation(main), Write(tag), FadeIn(src), run_time=1.4)
        self.step_done(P, eq, rt, l1, l2, t1, t2, trajs, main, tag, src)

        # 3. saddle y'' = 4y
        eq2 = M(("e", "y'' = 4y"), ",", ("s", r"s = \pm 2"), size=0.9).move_to([3.6, -0.6, 0])
        m1, m2 = P.line(2, color=RED_C), P.line(-2, color=GREEN_C)
        A2 = [[0, 1], [4, 0]]
        sad = VGroup()
        for u0 in [(1.5, -2.6), (-1.5, 2.6), (1.2, -2.5), (-1.2, 2.5), (0.5, -1.2), (-0.5, 1.2)]:
            sad.add(P.path(flow(lin(A2), u0, 2.2), color=TEAL_C))
        sl = label("saddle: in along y' = −2y, out along y' = 2y", 20, YELLOW_C).move_to([3.4, -1.3, 0])
        self.play(self.chip("roots of opposite sign"), FadeOut(VGroup(trajs, main, l1, t1, t2, src)), FadeOut(l2), run_time=0.8)
        self.play(Write(eq2), ShowCreation(m1), ShowCreation(m2), run_time=1.1)
        self.play(LaggedStart(*[ShowCreation(s) for s in sad], lag_ratio=0.2), FadeIn(sl), run_time=2.0)
        self.step_done(P, eq, rt, tag, eq2, m1, m2, sad, sl)


# ======================================================================== Section 3

class SpiralCenterSequence(ControlScene):
    SEQ_ID = "spiral-center"

    def construct(self):
        P = Plane([-2.8, -0.1, 0], 3.0, 3.0, 0.9)
        eq = M(("e", "y'' + 4y = 0"), ",", ("s", r"s = \pm 2i"), size=0.9).move_to([3.6, 2.7, 0])
        self.start(P, eq)

        # 1. center
        ell = P.path([(np.cos(t), -2 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 200)], color=PINK_C, width=5)
        ell2 = P.path([(0.6 * np.cos(t), -1.2 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 200)], color=PINK_C, width=3)
        e1 = M(("c", r"y^2 + \left(\frac{y'}{2}\right)^2 = 1"), size=0.85, colors={"c": PINK_C}).move_to([3.6, 1.8, 0])
        dot = Dot(P.p(1, 0), radius=0.08).set_fill(PINK_C)
        self.play(self.chip("closed curves: a center"), FadeIn(dot), run_time=0.5)
        self.play(ShowCreation(ell), MoveAlongPath(dot, ell[0]), run_time=2.0)
        self.play(ShowCreation(ell2), Write(e1), run_time=1.0)
        self.step_done(P, eq, ell, ell2, e1)

        # 2. spiral sink
        eq2 = M(("e", "y'' + 2y' + 2y = 0"), ",", ("s", r"s = -1 \pm i"), size=0.85, colors={"s": GREEN_C}).move_to([3.6, 0.8, 0])
        A = [[0, 1], [-2, -2]]
        sp_ = P.path(flow(lin(A), (2.6, 0), 9, 900), color=GREEN_C, width=5)
        sp2 = P.path(flow(lin(A), (-1.5, 2.8), 9, 900), color=TEAL_C, width=3)
        self.play(self.chip("rotation times e^(-t)"), FadeOut(VGroup(ell, ell2)), Write(eq2), run_time=1.0)
        self.play(ShowCreation(sp_), run_time=2.0)
        self.play(ShowCreation(sp2), run_time=1.3)
        self.step_done(P, eq, e1, eq2, sp_, sp2)

        # 3. six pictures
        names = VGroup(
            label("real roots:    source · sink · saddle", 22, YELLOW_C),
            label("complex roots: spiral source · spiral sink · center", 22, PINK_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        names.set_width(5.6).move_to([3.4, -1.2, 0])
        self.play(self.chip("six cases"), LaggedStart(*[FadeIn(n, shift=0.1 * RIGHT) for n in names], lag_ratio=0.4), run_time=1.3)
        self.step_done(P, eq, e1, eq2, sp_, sp2, names)


# ======================================================================== Section 4

class TraceDeterminantSequence(ControlScene):
    SEQ_ID = "trace-determinant"

    def construct(self):
        A = Mat([["a", "b"], ["c", "d"]], size=0.9)
        lhs = M(("z", r"\mathbf{z}' = "), size=0.9)
        top = VGroup(lhs, A, M(("z", r"\mathbf{z}"), size=0.9)).arrange(RIGHT, buff=0.15).move_to([-3.2, 2.6, 0])
        self.start(top)

        # 1. characteristic equation
        ch = M(("l", r"\lambda^2"), "-", ("T", "(a + d)"), ("l2", r"\lambda"), "+", ("D", "(ad - bc)"), "=", "0", size=0.9,
               colors={"T": YELLOW_C, "D": BLUE_C}).move_to([-3.0, 1.5, 0])
        td = M(("T", r"T = \lambda_1 + \lambda_2"), ",", ("D", r"D = \lambda_1\lambda_2"), size=0.8,
               colors={"T": YELLOW_C, "D": BLUE_C}).move_to([-3.0, 0.75, 0])
        self.play(self.chip("det(A - lambda I) = 0"), TransformFromCopy(A, ch), run_time=1.4)
        self.play(FadeIn(td), run_time=0.7)
        self.step_done(top, ch, td)

        # 2. the plane
        o = np.array([3.2, -0.9, 0])
        u = 0.42
        def q(T, D):
            return o + np.array([T * u, D * u, 0])
        ax = VGroup(Line(q(-6, 0), q(6, 0)).set_stroke(DIM, 2), Line(q(0, -4), q(0, 9)).set_stroke(DIM, 2))
        axl = VGroup(label("T", 20, YELLOW_C).next_to(q(6, 0), DOWN, buff=0.08), label("D", 20, BLUE_C).next_to(q(0, 9), RIGHT, buff=0.08))
        par = VMobject().set_points_as_corners([q(T, T * T / 4) for T in np.linspace(-6, 6, 100)]).set_stroke(PINK_C, 3)
        regs = VGroup(label("saddles", 20, RED_C).move_to(q(3.5, -2.5)),
                      label("spirals", 20, PINK_C).move_to(q(0, 6.5)),
                      label("nodes", 20, YELLOW_C).move_to(q(-4.8, 2.2)),
                      label("nodes", 20, YELLOW_C).move_to(q(4.8, 2.2)))
        self.play(self.chip("D < 0 saddle, above T^2 = 4D spiral"), FadeIn(ax), FadeIn(axl), run_time=0.7)
        self.play(ShowCreation(par), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(r) for r in regs], lag_ratio=0.25), run_time=1.0)
        self.step_done(top, ch, td, ax, axl, par, regs)

        # 3. stable quarter + example
        poly = Polygon(q(-6, 0.02), q(-0.02, 0.02), q(-0.02, 8.9), q(-6, 8.9)).set_fill(GREEN_C, 0.15).set_stroke(width=0)
        st = M(("s", r"\mathrm{stable}:\ T < 0,\ D > 0"), size=0.85, colors={"s": GREEN_C}).move_to([-3.0, -0.4, 0])
        ex = Mat([["1", "2"], ["-3", "-4"]], size=0.75)
        exg = VGroup(ex, label("T = −3,  D = 2:  sink", 20, GREEN_C)).arrange(RIGHT, buff=0.3).move_to([-3.0, -1.6, 0])
        dot = Dot(q(-3, 2), radius=0.1).set_fill(GREEN_C)
        self.play(self.chip("left half, above the axis"), FadeIn(poly), Write(st), run_time=1.0)
        self.play(FadeIn(exg), TransformFromCopy(exg[1], dot), run_time=1.2)
        self.step_done(top, ch, td, ax, axl, par, regs, poly, st, exg, dot)


# ======================================================================== Section 5

class JacobianPredPreySequence(ControlScene):
    SEQ_ID = "jacobian-predprey"

    def construct(self):
        eq = M(("f", "y' = y - yz"), ",", ("g", "z' = yz - z"), size=1.0).move_to([-3.0, 2.7, 0])
        P = Plane([3.3, -0.4, 0], 2.6, 2.6, 0.95, xl="y", yl="z")
        P.shift(np.array([-1.2 * 0.95, -1.2 * 0.95, 0]))  # put (0, 0) near the lower left
        P.o = P.o + np.array([-1.2 * 0.95, -1.2 * 0.95, 0])
        orbits = VGroup(*[P.path(flow(lambda u: np.array([u[0] - u[0] * u[1], u[0] * u[1] - u[1]]), u0, 7, 700), color=TEAL_C, width=3)
                          for u0 in [(0.5, 0.5), (0.3, 0.6), (0.7, 0.8)]])
        self.start(eq, P, orbits)

        # 1. Jacobian
        J = Mat([["1 - z", "-y"], ["z", "y - 1"]], size=0.85)
        Jg = VGroup(M(("J", "J ="), size=0.85), J).arrange(RIGHT, buff=0.15).move_to([-3.0, 1.4, 0])
        lab = VGroup(label("∂/∂y", 18, DIM).next_to(J.col(0), UP, buff=0.12), label("∂/∂z", 18, DIM).next_to(J.col(1), UP, buff=0.12))
        self.play(self.chip("partial derivatives"), FadeIn(Jg[0]), FadeIn(J.lb), FadeIn(J.rb), FadeIn(lab), run_time=0.7)
        self.play(TransformFromCopy(eq.k("f"), J.row(0)), run_time=1.0)
        self.play(TransformFromCopy(eq.k("g"), J.row(1)), run_time=1.0)
        self.step_done(eq, P, orbits, Jg, lab)

        # 2. at (0, 0)
        J0 = Mat([["1", "0"], ["0", "-1"]], size=0.8)
        g0 = VGroup(M(("p", "(0,0):"), size=0.8), J0, label("λ = 1, −1: saddle", 20, RED_C)).arrange(RIGHT, buff=0.2).move_to([-3.0, 0.0, 0])
        d0 = Dot(P.p(0, 0), radius=0.1).set_fill(RED_C)
        self.play(self.chip("put y = z = 0"), TransformFromCopy(J, J0), FadeIn(g0[0]), run_time=1.1)
        self.play(FadeIn(g0[2]), GrowFromCenter(d0), run_time=0.8)
        self.step_done(eq, P, orbits, Jg, lab, g0, d0)

        # 3. at (1, 1)
        J1 = Mat([["0", "-1"], ["1", "0"]], size=0.8)
        g1 = VGroup(M(("p", "(1,1):"), size=0.8), J1, label("λ = ±i: center", 20, PINK_C)).arrange(RIGHT, buff=0.2).move_to([-3.0, -1.4, 0])
        d1 = Dot(P.p(1, 1), radius=0.1).set_fill(PINK_C)
        self.play(self.chip("put y = z = 1"), TransformFromCopy(J, J1), FadeIn(g1[0]), run_time=1.1)
        self.play(FadeIn(g1[2]), GrowFromCenter(d1), Indicate(orbits, color=PINK_C), run_time=1.0)
        self.step_done(eq, P, orbits, Jg, lab, g0, d0, g1, d1)


# ======================================================================== Section 6

class TumblingBoxSequence(ControlScene):
    SEQ_ID = "tumbling-box"

    def construct(self):
        eq = M(("x", "x' = yz"), ",", ("y", "y' = -2xz"), ",", ("z", "z' = xy"), size=1.0).move_to([0, 2.7, 0])
        self.start(eq)

        # 1. sphere
        s1 = M(("a", "xx'"), "+", ("b", "yy'"), "+", ("c", "zz'"), "=", ("a2", "xyz"), "-", ("b2", "2xyz"), "+", ("c2", "xyz"), "=", "0",
               size=0.95, colors={"a2": TEAL_C, "b2": RED_C, "c2": TEAL_C}).move_to([0, 1.6, 0])
        sph = label("x² + y² + z² stays constant: motion on a sphere", 22, GREEN_C).move_to([0, 0.85, 0])
        self.play(self.chip("multiply each equation by its variable"), FadeIn(s1.ks("a", "+", "b", "c", "=")), run_time=0.9)
        self.play(TransformFromCopy(eq.k("x"), s1.k("a2")), TransformFromCopy(eq.k("y"), s1.k("b2")),
                  TransformFromCopy(eq.k("z"), s1.k("c2")), FadeIn(s1.all("+")[2] if len(s1.all("+")) > 2 else VGroup()),
                  FadeIn(s1.k("-")), run_time=1.3)
        self.play(FadeIn(s1.all("=")[1]), FadeIn(s1.k("0")), FadeIn(sph), run_time=0.8)
        self.step_done(eq, s1, sph)

        # 2. (1, 0, 0)
        J1 = Mat([["0", "0", "0"], ["0", "0", "-2"], ["0", "1", "0"]], size=0.6)
        g1 = VGroup(M(("p", "(1,0,0):"), size=0.8), J1, label("λ = 0, ±i√2: steady spin", 20, PINK_C)).arrange(RIGHT, buff=0.25).move_to([0, -0.15, 0])
        self.play(self.chip("Jacobian at the short axis"), FadeIn(g1[:2]), run_time=1.0)
        self.play(FadeIn(g1[2]), run_time=0.7)
        self.step_done(eq, s1, sph, g1)

        # 3. (0, 1, 0)
        J2 = Mat([["0", "0", "1"], ["0", "0", "0"], ["1", "0", "0"]], size=0.6)
        g2 = VGroup(M(("p", "(0,1,0):"), size=0.8), J2, label("λ = 0, 1, −1: saddle, tumbles", 20, RED_C)).arrange(RIGHT, buff=0.25).move_to([0, -1.75, 0])
        self.play(self.chip("Jacobian at the middle axis"), FadeIn(g2[:2]), run_time=1.0)
        self.play(FadeIn(g2[2], shift=0.1 * RIGHT), run_time=0.9)
        self.step_done(eq, s1, sph, g1, g2)
