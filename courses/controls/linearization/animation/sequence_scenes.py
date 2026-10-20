"""ManimGL scenes for the Linearizing Around a Fixed Point study companion (one scene per sequence in control_specs).

Rendered by build_sequences.py. Every step starts by swapping the relation chip, animates the actual
operation (tokens moving and cancelling, partial derivatives dropping into their matrix cells, the origin
sliding to the fixed point, a remainder shrinking, phase-line arrows, pendulums rotating, eigenvalues moving
as the friction changes) and ends with `step_done(...)`, which settles the scene to exactly the listed mobjects.

Colour code: state / offset eta teal, fixed points yellow, Jacobian / A blue, f_1 row yellow and f_2 row pink,
remainder and friction orange, stable green, unstable red. Angles are measured from the downward vertical.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403
from scipy.linalg import expm  # noqa: E402

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"x": TEAL_C, "xdot": TEAL_C, "eta": TEAL_C, "etad": TEAL_C, "nu": TEAL_C, "xb": YELLOW_C, "fx": YELLOW_C,
       "A": BLUE_C, "J": BLUE_C, "R": ORANGE_C, "fr": ORANGE_C, "dd": ORANGE_C, "B": BLUE_C, "du": BLUE_C,
       "C": PINK_C, "D": PINK_C, "dy": PINK_C, "y": PINK_C, "g": PINK_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def note(text, color=DIM, size=22):
    return label(text, size, color)


def mixed(tex, color=DIM, size=0.75):
    """A caption mixing words (\\mathrm{...}) and math, typeset as one mathtext line so baselines agree."""
    return M(("all", tex), size=size, color=color)


def fit(m, x0=-6.8, x1=6.8):
    """Shrink m (if needed) to fit between x0 and x1, then shift it horizontally inside that span."""
    if m.get_width() > x1 - x0:
        m.set_width(x1 - x0)
    if m.get_left()[0] < x0:
        m.shift((x0 - m.get_left()[0]) * RIGHT)
    if m.get_right()[0] > x1:
        m.shift((x1 - m.get_right()[0]) * RIGHT)
    return m


def cross(p, color=FG, s=0.12):
    return pole_cross(color, s=s, width=5).move_to(p)


def polyline(points, color, width=4):
    return VMobject().set_points_as_corners([np.array(p, dtype=float) for p in points]).set_stroke(color, width).set_fill(opacity=0)


def hanging(theta, length=2.0, pivot=ORIGIN, bob=TEAL_C, rod_color=FG):
    """A pendulum with its angle theta measured from the DOWNWARD vertical (theta = pi is upright)."""
    pv = np.array(pivot, dtype=float)
    tip = pv + length * np.array([np.sin(theta), -np.cos(theta), 0])
    plate = Rectangle(width=0.9, height=0.16).set_stroke(DIM, 2).set_fill(FAINT, 1).move_to(pv)
    rod = Line(pv, tip).set_stroke(rod_color, 6)
    ball = Circle(radius=0.2).set_stroke(rod_color, 2).set_fill(bob, 1).move_to(tip)
    hinge = Dot(pv, radius=0.07).set_fill(rod_color, 1)
    g = VGroup(plate, rod, ball, hinge)
    g.plate, g.rod, g.ball, g.hinge, g.pivot, g.swing = plate, rod, ball, hinge, pv, VGroup(rod, ball)
    return g


def h_arrow(x0, x1, y, color=TEAL_C, width=4):
    return arrow([x0, y, 0], [x1, y, 0], color=color, width=width)


def v_arrow(x, y0, y1, color=TEAL_C, width=4):
    return arrow([x, y0, 0], [x, y1, 0], color=color, width=width)


def ring(p, color, r=0.13):
    return Circle(radius=r).move_to(p).set_stroke(color, 4).set_fill(BG, 1)


def disc(p, color, r=0.13):
    return Circle(radius=r).move_to(p).set_stroke(color, 2).set_fill(color, 1)


def lin_traj(A, x0, t1, box, n=160):
    """Points of exp(At) x0 for 0 <= t <= t1 (or -t1 <= t <= 0 if t1 < 0), cut where they leave the box."""
    pts = []
    for t in np.linspace(0, t1, n):
        p = expm(A * t) @ np.array(x0, dtype=float)
        if abs(p[0]) > box or abs(p[1]) > box:
            break
        pts.append(p)
    return pts


class Portrait:
    """A small (eta, nu) phase plane with linear trajectories and direction arrows."""
    def __init__(self, center, half=1.25, box=1.0):
        self.o, self.k, self.box = np.array([center[0], center[1], 0.0]), half / box, box
        frame = Square(side_length=2 * half).move_to(self.o).set_stroke(FAINT, 1.5).set_fill(opacity=0)
        ax = VGroup(Line(self.p(-box, 0), self.p(box, 0)), Line(self.p(0, -box), self.p(0, box))).set_stroke(DIM, 1.5)
        names = VGroup(label("η", 20, DIM).next_to(self.p(box, 0), DOWN, buff=0.08).shift(0.15 * LEFT),
                       label("ν", 20, DIM).next_to(self.p(0, box), RIGHT, buff=0.08).shift(0.15 * DOWN))
        self.axes = VGroup(frame, ax, names)

    def p(self, a, b):
        return self.o + self.k * np.array([a, b, 0.0])

    def flow(self, A, starts, color, t1=8.0, both=False, width=3):
        g = VGroup()
        for s in starts:
            for sign in ((1, -1) if both else (1,)):
                pts = lin_traj(A, s, sign * t1, self.box)
                if len(pts) < 3:
                    continue
                if sign < 0:
                    pts = pts[::-1]
                line = polyline([self.p(*q) for q in pts], color, width)
                g.add(line)
                i = len(pts) // 2
                a, b = self.p(*pts[i]), self.p(*pts[min(i + 2, len(pts) - 1)])
                d = b - a
                if np.linalg.norm(d) > 1e-6:
                    d = d / np.linalg.norm(d)
                    nrm = np.array([-d[1], d[0], 0])
                    tip = Polygon(a + 0.13 * d, a - 0.09 * d + 0.08 * nrm, a - 0.09 * d - 0.08 * nrm)
                    g.add(tip.set_fill(color, 1).set_stroke(color, 1))
        return g


# ======================================================================== Section 1

class FixedPointSequence(ControlScene):
    SEQ_ID = "fixed-points"

    def construct(self):
        e0 = M(("xdot", r"\dot{x}"), "=", ("f", "f(x)"), ("sep", r",\qquad"), ("Rn", r"x \in \mathbb{R}^n"), size=1.5).move_to([0, 0.9, 0])
        goal = mixed(r"\mathrm{goal:\ a\ linear\ model}\ \dot{x} = Ax\ \mathrm{valid\ near\ a\ chosen\ point}", DIM, 0.8).move_to([0, -0.7, 0])
        self.start(e0, goal)

        # 1. f(xbar) = 0
        e1 = M(("xdot", r"\dot{x}"), ("at", r"\vert_{\bar{x}}"), "=", ("f", r"f(\bar{x})"), ("eq0", "="), ("zero", "0"), size=1.4,
               colors={"zero": YELLOW_C, "f": YELLOW_C}).move_to([0, 2.6, 0])
        self.play(self.chip("the velocity vanishes"), FadeOut(goal), self.tmorph(e0, e1, pairs=[("xdot", "xdot"), ("f", "f")]), run_time=1.3)
        O, P = np.array([-3.4, -1.2, 0]), np.array([1.9, -1.2, 0])
        oax = VGroup(Line(O + 0.6 * LEFT, O + 0.6 * RIGHT), Line(O + 0.6 * DOWN, O + 0.6 * UP)).set_stroke(DIM, 2)
        olab = note("origin 0", DIM).next_to(O, DOWN, buff=0.7)
        field = VGroup()
        for gx in range(-2, 3):
            for gy in range(-1, 2):
                if gx == 0 and gy == 0:
                    continue
                c = P + np.array([gx * 0.95, gy * 0.8, 0])
                v = 0.33 * np.array([gx * 0.95, -gy * 0.8, 0])
                field.add(arrow(c - v / 2, c + v / 2, color=TEAL_C, width=3))
        pdot = disc(P, YELLOW_C, 0.12)
        plab = M(("xb", r"\bar{x}"), size=1.0).next_to(P, UR, buff=0.12)
        flab = note("arrows: velocity f(x); it shrinks to zero at x̄", DIM).move_to([1.9, -2.75, 0])
        self.play(FadeIn(oax), FadeIn(olab), FadeIn(field, lag_ratio=0.05), run_time=1.2)
        self.play(GrowFromCenter(pdot), FadeIn(plab), FadeIn(flab), Indicate(e1.k("zero"), color=YELLOW_C), run_time=1.0)
        note1 = note("x̄ need not be the origin", YELLOW_C).next_to(olab, UP, buff=1.45)
        self.play(FadeIn(note1, shift=0.1 * UP), run_time=0.6)
        fp = VGroup(oax, olab, field, pdot, plab, flab, note1)
        self.step_done(e1, fp)

        # 2. pendulum down and up
        self.play(self.chip("two pendulum fixed points"), FadeOut(fp), run_time=0.6)
        pd = hanging(0.7, 1.8, [-3.2, 0.0, 0])
        pu = hanging(PI - 0.7, 1.8, [3.2, 0.0, 0])
        vref = DashedLine([-3.2, 0, 0], [-3.2, -2.1, 0]).set_stroke(DIM, 2)
        vtxt = note("θ measured from the downward vertical", DIM, 20).move_to([0, -0.9, 0])
        self.play(FadeIn(pd), FadeIn(pu), ShowCreation(vref), FadeIn(vtxt), run_time=0.8)
        self.play(Rotate(pd.swing, -0.7, about_point=pd.pivot), Rotate(pu.swing, 0.7, about_point=pu.pivot), run_time=1.4)
        ld = mixed(r"\bar{\theta} = 0\ \mathrm{(down)},\ \dot{\theta} = 0", FG, 0.8).move_to([-3.2, -2.55, 0])
        lu = mixed(r"\bar{\theta} = \pi\ \mathrm{(up)},\ \dot{\theta} = 0", FG, 0.8).move_to([3.2, -2.55, 0])
        both = note("both stay put if placed exactly there", YELLOW_C).move_to([0, 1.55, 0])
        self.play(FadeIn(ld), FadeIn(lu), FadeIn(both), run_time=0.8)
        pend = VGroup(pd, pu, vref, vtxt, ld, lu, both)
        self.step_done(e1, pend)

        # 3. solve x(1 - x) = 0
        q1 = M(("xdot", r"\dot{x}"), "=", ("a", "x"), ("b", "(1-x)"), ("e", "="), ("z", "0"), size=1.3).move_to([0, 1.25, 0])
        self.play(self.chip("solve f(x) = 0  (authored example)"), FadeOut(pend), run_time=0.6)
        self.play(FadeIn(q1, shift=0.1 * DOWN), run_time=0.7)
        L = M(("a", "x"), ("e", "="), ("z", "0"), size=1.2).move_to([-2.6, -0.15, 0])
        R = M(("b", "1-x"), ("e", "="), ("z", "0"), size=1.2).move_to([2.6, -0.15, 0])
        orl = note("or", DIM, 26).move_to([0, -0.15, 0])
        self.play(TransformFromCopy(q1.k("a"), L.k("a")), TransformFromCopy(q1.k("b"), R.k("b")),
                  TransformFromCopy(q1.ks("e", "z"), L.ks("e", "z")), TransformFromCopy(q1.ks("e", "z"), R.ks("e", "z")), FadeIn(orl), run_time=1.3)
        s1 = M(("xb", r"\bar{x} = 0"), size=1.2).move_to([-2.6, -1.5, 0])
        s2 = M(("xb", r"\bar{x} = 1"), size=1.2).move_to([2.6, -1.5, 0])
        self.play(TransformFromCopy(L, s1), TransformFromCopy(R, s2), run_time=1.0)
        self.step_done(e1, q1, L, R, orl, s1, s2)

        # 4. arrows: fixed is not stable
        def X(x):
            return -4.6 + (x + 0.6) * 4.1

        y0 = -0.35
        self.play(self.chip("arrows show the sign of ẋ"), FadeOut(VGroup(e1, L, R, orl)), q1.animate.scale(0.75).move_to([0, 2.75, 0]), run_time=0.8)
        axis = Line([X(-0.6), y0, 0], [X(1.6), y0, 0]).set_stroke(DIM, 2)
        curve = polyline([[X(x), y0 + 2.2 * x * (1 - x), 0] for x in np.linspace(-0.6, 1.6, 80)], YELLOW_C, 3)
        clab = M(("f", r"f(x) = x(1-x)"), size=0.7, color=YELLOW_C).move_to([X(0.5), 0.75, 0])
        xl = note("x", DIM).next_to(axis, RIGHT, buff=0.12)
        t0 = M(("xb", r"\bar{x} = 0"), size=0.8).move_to([X(0) - 0.95, y0 + 0.45, 0])
        t1 = M(("xb", r"\bar{x} = 1"), size=0.8).move_to([X(1) + 0.95, y0 + 0.45, 0])
        self.play(ShowCreation(axis), FadeIn(xl), ReplacementTransform(s1, t0), ReplacementTransform(s2, t1), run_time=0.9)
        self.play(ShowCreation(curve), FadeIn(clab), run_time=1.0)
        arr = VGroup(h_arrow(X(-0.15), X(-0.5), y0), h_arrow(X(0.3), X(0.7), y0), h_arrow(X(1.5), X(1.15), y0))
        d0, d1 = ring([X(0), y0, 0], RED_C), disc([X(1), y0, 0], GREEN_C)
        self.play(LaggedStart(*[grow_arrow(a) for a in arr], lag_ratio=0.3), FadeIn(d0), FadeIn(d1), run_time=1.3)
        u0 = note("unstable: offsets grow", RED_C).move_to([X(0), y0 - 1.9, 0])
        u1 = note("stable: offsets return", GREEN_C).move_to([X(1), y0 - 1.9, 0])
        self.play(FadeIn(u0, shift=0.1 * UP), FadeIn(u1, shift=0.1 * UP), run_time=0.7)
        line_grp = VGroup(axis, xl, curve, clab, arr, d0, d1, t0, t1)
        self.step_done(q1, line_grp, u0, u1)

        # 5. one local model per fixed point: the tangent lines
        fp = M(("fp", r"f'(x) = 1 - 2x"), size=0.9, color=BLUE_C).move_to([0, 1.85, 0])
        self.play(self.chip("zoom in at each fixed point"), FadeOut(VGroup(u0, u1, t0, t1, clab)), FadeIn(fp), run_time=0.8)
        line_grp = VGroup(axis, xl, curve, arr, d0, d1)
        s = 2.2 / 4.1
        tan0 = Line([X(-0.45), y0 - 0.45 * 4.1 * s * 1, 0], [X(0.45), y0 + 0.45 * 4.1 * s * 1, 0]).set_stroke(RED_C, 4)
        tan1 = Line([X(0.55), y0 + 0.45 * 4.1 * s, 0], [X(1.45), y0 - 0.45 * 4.1 * s, 0]).set_stroke(GREEN_C, 4)
        z0 = DashedVMobject(Circle(radius=0.95).move_to([X(0), y0, 0]), num_dashes=30).set_stroke(RED_C, 2)
        z1 = DashedVMobject(Circle(radius=0.95).move_to([X(1), y0, 0]), num_dashes=30).set_stroke(GREEN_C, 2)
        self.play(ShowCreation(z0), ShowCreation(z1), run_time=0.8)
        self.play(ShowCreation(tan0), ShowCreation(tan1), run_time=1.0)
        m0 = M(("m", r"\dot{\eta} \approx +\eta"), size=0.9, color=RED_C).move_to([X(0), y0 - 1.55, 0])
        m1 = M(("m", r"\dot{\eta} \approx -\eta"), size=0.9, color=GREEN_C).move_to([X(1), y0 - 1.55, 0])
        a0 = mixed(r"A = f'(0) = +1", RED_C, 0.7).move_to([X(0) - 2.1, 0.9, 0])
        a1 = mixed(r"A = f'(1) = -1", GREEN_C, 0.7).move_to([X(1) + 2.1, 0.9, 0])
        self.play(TransformFromCopy(fp, a0), TransformFromCopy(fp, a1), run_time=1.0)
        self.play(FadeIn(m0, shift=0.1 * UP), FadeIn(m1, shift=0.1 * UP), run_time=0.7)
        self.step_done(q1, line_grp, fp, z0, z1, tan0, tan1, a0, a1, m0, m1)


# ======================================================================== Section 2

class JacobianSequence(ControlScene):
    SEQ_ID = "jacobian-cells"

    def construct(self):
        c1, c2 = {"f1": YELLOW_C, "g1": YELLOW_C}, {"f2": PINK_C, "g2": PINK_C}
        E1 = M(("x1d", r"\dot{x}_1"), "=", ("f1", "f_1"), ("e", "="), ("g1", "x_1x_2"), size=1.0, colors=c1)
        E2 = M(("x2d", r"\dot{x}_2"), "=", ("f2", "f_2"), ("e", "="), ("g2", "x_1^2 + x_2^2"), size=1.0, colors=c2)
        E1.move_to([-3.9, 2.95, 0])
        E2.next_to(E1, DOWN, buff=0.35).align_to(E1, LEFT)
        self.start(E1, E2)

        def pc(i, j, size=0.85):
            return M(("p", rf"\partial f_{i}/\partial x_{j}"), size=size, color=YELLOW_C if i == 1 else PINK_C)

        # 1. rows f_i, columns x_j
        lhs = M(("J", r"\frac{Df}{Dx}"), "=", size=1.0)
        J0 = Mat([[pc(1, 1), pc(1, 2)], [pc(2, 1), pc(2, 2)]], size=0.85)
        dx = Mat([[(r"dx1", r"\Delta x_1")], [("dx2", r"\Delta x_2")]], size=0.85, colors={"dx1": TEAL_C, "dx2": BLUE_C})
        row = place_row(lhs, J0, dx, buff=0.3, y=-0.25).shift(0.3 * LEFT)
        self.play(self.chip("rows f_i, columns x_j"), FadeIn(lhs), FadeIn(VGroup(J0.lb, J0.rb)), run_time=0.7)
        self.play(TransformFromCopy(E1.k("f1"), J0.row(0)), TransformFromCopy(E2.k("f2"), J0.row(1)), run_time=1.2)
        self.play(FadeIn(dx), run_time=0.6)
        b1 = VGroup(hbox(J0.col(0), TEAL_C, 0.1), hbox(dx.e[0][0], TEAL_C, 0.08))
        b2 = VGroup(hbox(J0.col(1), BLUE_C, 0.1), hbox(dx.e[1][0], BLUE_C, 0.08))
        cl = note("column j holds ∂/∂xⱼ because it multiplies Δxⱼ", DIM).move_to([0, -1.95, 0])
        rl = VGroup(note("row 1: f₁", YELLOW_C).next_to(J0.row(0), LEFT, buff=1.9),
                    note("row 2: f₂", PINK_C).next_to(J0.row(1), LEFT, buff=1.9))
        rl.set_x(-5.7)
        self.play(ShowCreation(b1), run_time=0.7)
        self.play(ShowCreation(b2), FadeIn(cl), FadeIn(rl), run_time=0.8)
        self.step_done(E1, E2, row, b1, b2, cl, rl)

        # 2. row 1
        self.play(self.chip("differentiate f₁ = x₁x₂"), FadeOut(VGroup(b1, b2, cl, dx, rl)), run_time=0.6)
        D1 = M(("n", r"\partial(x_1x_2)/\partial x_1"), "=", ("r", "x_2"), size=0.85, color=YELLOW_C).move_to([3.6, 0.55, 0])
        D2 = M(("n", r"\partial(x_1x_2)/\partial x_2"), "=", ("r", "x_1"), size=0.85, color=YELLOW_C).move_to([3.6, -0.45, 0])
        self.play(TransformFromCopy(E1.k("g1"), D1.k("n")), TransformFromCopy(E1.k("g1"), D2.k("n")), run_time=1.0)
        self.play(FadeIn(D1.ks("=", "r")), FadeIn(D2.ks("=", "r")), run_time=0.7)
        J1 = Mat([[M(("r", "x_2"), size=0.85, color=YELLOW_C), M(("r", "x_1"), size=0.85, color=YELLOW_C)], [pc(2, 1), pc(2, 2)]], size=0.85)
        J1.next_to(lhs, RIGHT, buff=0.3).set_y(J0.get_y())
        self.play(FadeOut(J0.e[0][0]), FadeOut(J0.e[0][1]), TransformFromCopy(D1.k("r"), J1.e[0][0]), TransformFromCopy(D2.k("r"), J1.e[0][1]),
                  ReplacementTransform(J0.lb, J1.lb), ReplacementTransform(J0.rb, J1.rb),
                  ReplacementTransform(J0.e[1][0], J1.e[1][0]), ReplacementTransform(J0.e[1][1], J1.e[1][1]), run_time=1.3)
        self.step_done(E1, E2, lhs, J1, D1, D2)

        # 3. row 2
        self.play(self.chip("differentiate f₂ = x₁² + x₂²"), FadeOut(VGroup(D1, D2)), run_time=0.6)
        D3 = M(("n", r"\partial(x_1^2+x_2^2)/\partial x_1"), "=", ("r", "2x_1"), size=0.85, color=PINK_C).move_to([3.5, 0.55, 0])
        D4 = M(("n", r"\partial(x_1^2+x_2^2)/\partial x_2"), "=", ("r", "2x_2"), size=0.85, color=PINK_C).move_to([3.5, -0.45, 0])
        self.play(TransformFromCopy(E2.k("g2"), D3.k("n")), TransformFromCopy(E2.k("g2"), D4.k("n")), run_time=1.0)
        self.play(FadeIn(D3.ks("=", "r")), FadeIn(D4.ks("=", "r")), run_time=0.7)
        J2 = Mat([[M(("r", "x_2"), size=0.85, color=YELLOW_C), M(("r", "x_1"), size=0.85, color=YELLOW_C)],
                  [M(("r", "2x_1"), size=0.85, color=PINK_C), M(("r", "2x_2"), size=0.85, color=PINK_C)]], size=0.85)
        J2.next_to(lhs, RIGHT, buff=0.3).set_y(J1.get_y())
        self.play(FadeOut(J1.e[1][0]), FadeOut(J1.e[1][1]), TransformFromCopy(D3.k("r"), J2.e[1][0]), TransformFromCopy(D4.k("r"), J2.e[1][1]),
                  ReplacementTransform(J1.lb, J2.lb), ReplacementTransform(J1.rb, J2.rb),
                  ReplacementTransform(J1.e[0][0], J2.e[0][0]), ReplacementTransform(J1.e[0][1], J2.e[0][1]), run_time=1.3)
        jn = note("the Jacobian: still a function of x", DIM).next_to(VGroup(lhs, J2), DOWN, buff=0.45)
        self.play(FadeIn(jn), run_time=0.5)
        self.step_done(E1, E2, lhs, J2, D3, D4, jn)

        # 4. fixed point and evaluation
        self.play(self.chip("plug in the fixed point"), FadeOut(VGroup(D3, D4, jn)), run_time=0.6)
        F1 = mixed(r"x_1x_2 = 0,\quad x_1^2 + x_2^2 = 0", FG, 0.85).move_to([3.4, 0.6, 0])
        F2 = M(("imp", r"\Rightarrow"), ("xb", r"\bar{x} = (0, 0)"), size=0.95).move_to([3.4, -0.25, 0])
        self.play(TransformFromCopy(VGroup(E1.k("g1"), E2.k("g2")), F1), run_time=1.0)
        self.play(FadeIn(F2, shift=0.1 * RIGHT), run_time=0.6)
        lA = M(("A", "A"), "=", ("Jat", r"\left.\frac{Df}{Dx}\right|_{(0,0)}"), ("e2", "="), size=0.9)
        Z = Mat([[M(("z", "0"), size=0.85, color=YELLOW_C), M(("z", "0"), size=0.85, color=YELLOW_C)],
                 [M(("z", "0"), size=0.85, color=YELLOW_C), M(("z", "0"), size=0.85, color=YELLOW_C)]], size=0.85)
        arow = place_row(lA, Z, buff=0.3, y=-2.25).shift(0.6 * LEFT)
        self.play(FadeIn(lA), FadeIn(VGroup(Z.lb, Z.rb)), run_time=0.6)
        self.play(*[TransformFromCopy(J2.e[i][j], Z.e[i][j]) for i in range(2) for j in range(2)], Indicate(F2.k("xb"), color=YELLOW_C), run_time=1.4)
        self.step_done(E1, E2, lhs, J2, F1, F2, arow)

        # 5. A = 0 is inconclusive
        self.play(self.chip("A = 0 decides nothing"), FadeOut(VGroup(F1, F2)), run_time=0.6)
        X0, Y0 = 4.4, -0.35
        ax2 = Line([X0, Y0 - 1.6, 0], [X0, Y0 + 1.8, 0]).set_stroke(DIM, 2)
        o2 = disc([X0, Y0, 0], YELLOW_C, 0.1)
        ups = VGroup(*[v_arrow(X0, Y0 + y, Y0 + y + 0.18 + 0.45 * y * y, TEAL_C, 3.5) for y in (-1.3, -0.6, 0.45, 1.0)])
        n2 = VGroup(mixed(r"x_2\ \mathrm{axis:}\ \dot{x}_2 = x_2^2 \geq 0", DIM, 0.7),
                    note("positive offsets escape: unstable", DIM, 20)).arrange(DOWN, buff=0.12).move_to([X0, Y0 + 2.45, 0])
        self.play(ShowCreation(ax2), FadeIn(o2), FadeIn(n2), run_time=0.7)
        self.play(LaggedStart(*[grow_arrow(a) for a in ups], lag_ratio=0.2), run_time=1.2)
        warn = mixed(r"A = 0:\ \mathrm{no\ linear\ prediction;\ the\ quadratic\ terms\ decide}", ORANGE_C, 0.75)
        warn.move_to([0, -3.05, 0]).set_x(-2.2 + warn.get_width() / 2)
        fit(warn, -2.4, 6.9)
        self.play(FadeIn(warn, shift=0.1 * UP), Indicate(Z, color=ORANGE_C, scale_factor=1.08), run_time=1.0)
        self.step_done(E1, E2, lhs, J2, arow, ax2, o2, ups, n2, warn)


# ======================================================================== Section 3

class ShiftExpandSequence(ControlScene):
    SEQ_ID = "shift-expand"

    def construct(self):
        e0 = M(("xdot", r"\dot{x}"), "=", ("f", "f(x)"), ("sep", r",\qquad"), ("fx", r"f(\bar{x}) = 0"), size=1.2).move_to([0, 2.9, 0])
        O, P, X = np.array([-6.1, -2.5, 0]), np.array([-4.1, -0.8, 0]), np.array([-2.7, 0.15, 0])
        oax = VGroup(Line(O, O + 4.0 * RIGHT), Line(O, O + 3.9 * UP)).set_stroke(DIM, 2)
        onames = VGroup(mixed("x_1", DIM, 0.7).next_to(O + 4.0 * RIGHT, DOWN, buff=0.1), mixed("x_2", DIM, 0.7).next_to(O + 3.9 * UP, LEFT, buff=0.1))
        flow = VGroup(arrow(P + 1.2 * UP, P + 0.3 * UP, DIM, 3), arrow(P + 1.2 * DOWN, P + 0.3 * DOWN, DIM, 3),
                      arrow(P + 0.3 * RIGHT, P + 1.3 * RIGHT, DIM, 3), arrow(P + 0.3 * LEFT, P + 1.3 * LEFT, DIM, 3))
        pdot = disc(P, YELLOW_C, 0.11)
        plab = M(("xb", r"\bar{x}"), size=0.95).next_to(P, DL, buff=0.08)
        xdot = disc(X, TEAL_C, 0.09)
        xlab = M(("x", "x"), size=0.95).next_to(X, UR, buff=0.06)
        plane = VGroup(oax, onames, flow, pdot, plab, xdot, xlab)
        self.start(e0, plane)

        # 1. eta = x - xbar
        self.play(self.chip("put the origin at x̄"), run_time=0.5)
        nax = oax.copy()
        self.play(nax.animate.shift(P - O).set_stroke(YELLOW_C, 2.5), oax.animate.set_stroke(FAINT, 2), onames.animate.set_fill(FAINT), run_time=1.4)
        nnames = VGroup(mixed(r"\eta_1", YELLOW_C, 0.7).next_to(P + 3.9 * RIGHT, DOWN, buff=0.1),
                        mixed(r"\eta_2", YELLOW_C, 0.7).next_to(P + 2.6 * UP, LEFT, buff=0.1))
        ea = arrow(P, X, TEAL_C, 4)
        elab = M(("eta", r"\eta"), size=1.0).move_to((P + X) / 2 + 0.35 * UL)
        self.play(FadeIn(nnames), grow_arrow(ea), FadeIn(elab), run_time=1.0)
        q = M(("eta", r"\eta"), "=", ("x", "x"), "-", ("xb", r"\bar{x}"), size=1.4).move_to([3.4, 1.0, 0])
        self.play(TransformFromCopy(elab, q.k("eta")), TransformFromCopy(xlab, q.k("x")), TransformFromCopy(plab, q.k("xb")), FadeIn(q.ks("=", "-")), run_time=1.2)
        nax.set_stroke(YELLOW_C, 2.5)
        plane2 = VGroup(oax, onames, flow, pdot, plab, xdot, xlab, nax, nnames, ea, elab)
        self.step_done(e0, plane2, q)

        # 2. eta dot = x dot
        q2 = M(("etad", r"\dot{\eta}"), "=", ("xd", r"\dot{x}"), "-", ("xbd", r"\dot{\bar{x}}"), ("e2", "="), ("xd2", r"\dot{x}"), ("e3", "="),
               ("f", r"f(\bar{x}+\eta)"), size=1.1, colors={"xbd": YELLOW_C, "f": FG}).move_to([3.3, -1.75, 0])
        self.play(self.chip("differentiate the shift"), TransformFromCopy(q.k("eta"), q2.k("etad")), TransformFromCopy(q.k("x"), q2.k("xd")),
                  TransformFromCopy(q.k("xb"), q2.k("xbd")), FadeIn(q2.k("=")), FadeIn(q2.k("-")), run_time=1.2)
        st = strike(q2.k("xbd"))
        zl = note("= 0: x̄ does not move", YELLOW_C).next_to(q2.k("xbd"), DOWN, buff=0.35)
        self.play(ShowCreation(st), FadeIn(zl), run_time=0.7)
        self.play(FadeIn(q2.ks("e2", "xd2", "e3", "f"), shift=0.1 * RIGHT), run_time=0.9)
        self.step_done(e0, plane2, q, q2, st, zl)

        # 3. Taylor
        T = M(("etad", r"\dot{\eta}"), "=", ("c", r"f(\bar{x})"), ("p1", "+"), ("J", r"\left.\frac{Df}{Dx}\right|_{\bar{x}}"), ("eta", r"\eta"), ("p2", "+"),
              ("R", r"\mathcal{O}(\Vert\eta\Vert^2)"), size=1.25, colors={"c": YELLOW_C}).move_to([0, 1.1, 0])
        self.play(self.chip("Taylor series about x̄"), FadeOut(VGroup(plane2, q, st, zl)), q2.animate.move_to([0, 2.55, 0]).scale(0.85), run_time=0.9)
        self.play(TransformFromCopy(q2.k("etad"), T.k("etad")), FadeIn(T.k("=")),
                  TransformFromCopy(q2.k("f"), T.k("c")), TransformFromCopy(q2.k("f"), T.k("J")), TransformFromCopy(q2.k("f"), T.k("R")),
                  TransformFromCopy(q2.k("f"), T.k("eta")), FadeIn(T.ks("p1", "p2")), run_time=1.6)
        bc, bl, br = under_bracket(T.k("c"), YELLOW_C), under_bracket(T.ks("J", "eta"), BLUE_C), under_bracket(T.k("R"), ORANGE_C)
        lc = note("constant", YELLOW_C).next_to(bc, DOWN, buff=0.15)
        ll = note("linear in η", BLUE_C).next_to(bl, DOWN, buff=0.15)
        lr = note("remainder", ORANGE_C).next_to(br, DOWN, buff=0.15)
        sm = note("needs a smooth f (twice continuously differentiable is enough)", DIM, 20).move_to([0.8, -2.2, 0])
        self.play(ShowCreation(bc), ShowCreation(bl), ShowCreation(br), FadeIn(lc), FadeIn(ll), FadeIn(lr), run_time=1.0)
        self.play(FadeIn(sm), run_time=0.5)
        braces = VGroup(bc, bl, br, lc, ll, lr)
        self.step_done(q2, T, braces, sm)

        # 4. f(xbar) = 0
        self.play(self.chip("f(x̄) = 0 at a fixed point"), FadeOut(sm), run_time=0.5)
        sc = strike(T.k("c"))
        z = note("= 0", YELLOW_C).next_to(lc, DOWN, buff=0.15)
        self.play(ShowCreation(sc), FadeIn(z), run_time=0.8)
        T2 = M(("etad", r"\dot{\eta}"), "=", ("A", "A"), ("eta", r"\eta"), ("p2", "+"), ("R", r"\mathcal{O}(\Vert\eta\Vert^2)"), size=1.25).move_to([0, 1.1, 0])
        Ad = M(("A", "A"), "=", ("J", r"\left.\frac{Df}{Dx}\right|_{\bar{x}}"), size=1.05).move_to([0, -0.85, 0])
        self.play(FadeOut(VGroup(braces, z, sc, T.k("c"), T.k("p1"))), TransformFromCopy(T.k("J"), Ad.k("J")), run_time=0.9)
        self.play(ReplacementTransform(T.k("J"), T2.k("A")), ReplacementTransform(T.k("etad"), T2.k("etad")), ReplacementTransform(T.k("="), T2.k("=")),
                  ReplacementTransform(T.k("eta"), T2.k("eta")), ReplacementTransform(T.k("p2"), T2.k("p2")), ReplacementTransform(T.k("R"), T2.k("R")),
                  FadeIn(Ad.ks("A", "=")), run_time=1.2)
        cst = note("a constant matrix: the Jacobian evaluated at x̄", BLUE_C).next_to(Ad, DOWN, buff=0.35)
        self.play(FadeIn(cst), run_time=0.5)
        self.step_done(q2, T2, Ad, cst)

        # 5. the remainder shrinks faster (sin, authored)
        self.play(self.chip("halve η: compare the two terms"), FadeOut(VGroup(q2, Ad, cst)), T2.animate.scale(0.85).move_to([0, 2.9, 0]), run_time=0.8)

        def S(e, v):
            return np.array([-5.6 + (e + 0.1) * 4.0, -2.5 + (v + 0.1) * 2.9, 0])

        ax = VGroup(Line(S(-0.1, 0), S(1.45, 0)), Line(S(0, -0.1), S(0, 1.55))).set_stroke(DIM, 2)
        names = VGroup(mixed(r"\eta", DIM, 0.75).next_to(S(1.45, 0), DOWN, buff=0.1), mixed("f", DIM, 0.75).next_to(S(0, 1.55), LEFT, buff=0.1))
        lin = Line(S(0, 0), S(1.45, 1.45)).set_stroke(BLUE_C, 4)
        sinc = polyline([S(e, np.sin(e)) for e in np.linspace(0, 1.45, 60)], TEAL_C, 4)
        kl = mixed(r"A\eta = \eta", BLUE_C, 0.75).next_to(S(1.45, 1.45), LEFT, buff=0.15)
        ks = mixed(r"\sin\eta", TEAL_C, 0.75).next_to(S(1.45, np.sin(1.45)), DOWN, buff=0.15)
        self.play(ShowCreation(ax), FadeIn(names), ShowCreation(lin), ShowCreation(sinc), FadeIn(kl), FadeIn(ks), run_time=1.3)
        g1 = Line(S(1.2, np.sin(1.2)), S(1.2, 1.2)).set_stroke(RED_C, 6)
        g2 = Line(S(0.6, np.sin(0.6)), S(0.6, 0.6)).set_stroke(RED_C, 6)
        d1 = DashedLine(S(1.2, 0), S(1.2, np.sin(1.2))).set_stroke(DIM, 1.5)
        d2 = DashedLine(S(0.6, 0), S(0.6, np.sin(0.6))).set_stroke(DIM, 1.5)
        tl = VGroup(mixed("1.2", DIM, 0.6).next_to(S(1.2, 0), DOWN, buff=0.1), mixed("0.6", DIM, 0.6).next_to(S(0.6, 0), DOWN, buff=0.1))
        self.play(ShowCreation(d1), ShowCreation(g1), FadeIn(tl[0]), run_time=0.8)
        r1 = mixed(r"\eta = 1.2:\ \ A\eta = 1.2,\ \ |r| \approx 0.268", FG, 0.72).move_to([4.1, 0.9, 0])
        fit(r1, 1.2, 6.9)
        self.play(FadeIn(r1, shift=0.1 * LEFT), run_time=0.6)
        self.play(ShowCreation(d2), ShowCreation(g2), FadeIn(tl[1]), run_time=0.8)
        r2 = mixed(r"\eta = 0.6:\ \ A\eta = 0.6,\ \ |r| \approx 0.035", FG, 0.72).move_to([4.1, 0.0, 0])
        fit(r2, 1.2, 6.9)
        self.play(FadeIn(r2, shift=0.1 * LEFT), run_time=0.6)
        r3 = mixed(r"\mathrm{halve}\ \eta:\ A\eta \div 2,\ \ |r| \div 7.6", YELLOW_C, 0.8).move_to([4.1, -1.1, 0])
        fit(r3, 1.2, 6.9)
        r4 = note("(red gaps: the remainder r = sin η − η)", RED_C, 20).move_to([4.1, -1.9, 0])
        self.play(FadeIn(r3), FadeIn(r4), run_time=0.7)
        plot = VGroup(ax, names, lin, sinc, kl, ks, g1, g2, d1, d2, tl)
        self.step_done(T2, plot, r1, r2, r3, r4)

        # 6. truncate
        self.play(self.chip("drop the remainder"), FadeOut(VGroup(plot, r1, r2, r3, r4)), T2.animate.scale(1 / 0.85).move_to([0, 0.9, 0]), run_time=0.8)
        T3 = M(("etad", r"\dot{\eta}"), ("ap", r"\approx"), ("A", "A"), ("eta", r"\eta"), size=1.6).move_to([0, 0.9, 0])
        self.play(T2.k("R").animate.scale(0.05).set_opacity(0), T2.k("p2").animate.set_opacity(0), run_time=0.9)
        self.play(ReplacementTransform(T2.k("etad"), T3.k("etad")), FadeTransform(T2.k("="), T3.k("ap")),
                  ReplacementTransform(T2.k("A"), T3.k("A")), ReplacementTransform(T2.k("eta"), T3.k("eta")), run_time=1.0)
        c1 = note("a local approximation, not an identity", YELLOW_C, 26).move_to([0, -0.6, 0])
        c2 = note("it improves as η → 0; the lecture writes Δẋ = A Δx, or just ẋ = Ax", DIM).move_to([0, -1.4, 0])
        self.play(FadeIn(c1, shift=0.1 * UP), FadeIn(c2), run_time=0.8)
        self.step_done(T3, c1, c2)


class AffineSequence(ControlScene):
    SEQ_ID = "affine-abcd"

    def construct(self):
        e0 = M(("etad", r"\dot{\eta}"), "=", ("c", r"f(x_0)"), ("p1", "+"), ("J", r"\left.\frac{Df}{Dx}\right|_{x_0}"), ("eta", r"\eta"), ("p2", "+"),
               ("R", r"\mathcal{O}(\Vert\eta\Vert^2)"), size=1.15, colors={"c": ORANGE_C}).move_to([0, 2.7, 0])
        n0 = note("about any point x₀, fixed or not", DIM).move_to([0, 1.6, 0])
        self.start(e0, n0)

        # 1. affine residual
        self.play(self.chip("x₀ = 0.5 is not fixed  (authored)"), FadeOut(n0), run_time=0.5)
        e1 = M(("etad", r"\dot{\eta}"), "=", ("c", "0.25"), ("p1", "+"), ("J", r"0\cdot"), ("eta", r"\eta"), ("R", r"-\eta^2"), size=1.2,
               colors={"c": ORANGE_C}).move_to([0, 1.35, 0])
        ex = mixed(r"\dot{x} = x(1-x),\ \ x_0 = 0.5", DIM, 0.8).next_to(e1, LEFT, buff=0.6)
        VGroup(ex, e1).move_to([0, 1.35, 0])
        self.play(FadeIn(ex), self.tmorph(e0, e1, pairs=[("c", "c"), ("J", "J"), ("R", "R"), ("etad", "etad"), ("eta", "eta"), ("p1", "p1")], keep_src=True), run_time=1.5)

        def X(x):
            return -5.4 + (x + 0.3) * 4.4

        y0 = -0.4
        ax = Line([X(-0.3), y0, 0], [X(1.3), y0, 0]).set_stroke(DIM, 2)
        dts = VGroup(ring([X(0), y0, 0], RED_C, 0.11), disc([X(1), y0, 0], GREEN_C, 0.11))
        tk = VGroup(mixed("0", DIM, 0.65).next_to([X(0), y0, 0], DOWN, buff=0.22), mixed("1", DIM, 0.65).next_to([X(1), y0, 0], DOWN, buff=0.22))
        p0 = disc([X(0.5), y0, 0], ORANGE_C, 0.12)
        pl = mixed("x_0", ORANGE_C, 0.7).next_to(p0, DOWN, buff=0.22)
        drift = h_arrow(X(0.5) + 0.15, X(0.5) + 1.2, y0 + 0.45, ORANGE_C, 4)
        dl = mixed(r"\dot{x} = 0.25 \neq 0", ORANGE_C, 0.7).next_to(drift, UP, buff=0.12)
        self.play(ShowCreation(ax), FadeIn(dts), FadeIn(tk), GrowFromCenter(p0), FadeIn(pl), run_time=0.9)
        self.play(grow_arrow(drift), FadeIn(dl), Indicate(e1.k("c"), color=ORANGE_C), run_time=1.0)
        w = mixed(r"\mathrm{truncated:}\ \dot{\eta} \approx 0.25\ \ \mathrm{(constant\ drift:\ affine,\ not\ linear)}", ORANGE_C, 0.8).move_to([0, -2.0, 0])
        fit(w, -6.8, 6.8)
        w2 = note("linearize about fixed points, where the constant term is 0", DIM).move_to([0, -2.75, 0]).shift(1.2 * RIGHT)
        self.play(FadeIn(w, shift=0.1 * UP), FadeIn(w2), run_time=0.8)
        self.step_done(e0, ex, e1, ax, dts, tk, p0, pl, drift, dl, w, w2)

        # 2. inputs: A and B
        m1 = M(("xd", r"\dot{x}"), "=", ("f", "f(x,u)"), ("sep", r",\qquad"), ("eq", r"f(\bar{x},\bar{u}) = 0"), size=1.15,
               colors={"u": BLUE_C}).move_to([0, 2.7, 0])
        self.play(self.chip("add an input  (book Eq. 8.8)"), FadeOut(VGroup(e0, ex, e1, ax, dts, tk, p0, pl, drift, dl, w, w2)), run_time=0.7)
        self.play(FadeIn(m1, shift=0.1 * DOWN), run_time=0.7)
        dA = M(("A", "A"), "=", ("pa", r"\left.\frac{\partial f}{\partial x}\right|_{\bar{x},\bar{u}}"), size=0.95).move_to([-2.9, 0.0, 0])
        dB = M(("B", "B"), "=", ("pb", r"\left.\frac{\partial f}{\partial u}\right|_{\bar{x},\bar{u}}"), size=0.95).move_to([2.9, 0.0, 0])
        self.play(TransformFromCopy(m1.k("f"), dA.k("pa")), TransformFromCopy(m1.k("f"), dB.k("pb")), FadeIn(dA.ks("A", "=")), FadeIn(dB.ks("B", "=")), run_time=1.3)
        m2 = M(("etad", r"\dot{\eta}"), ("ap", r"\approx"), ("A", "A"), ("eta", r"\eta"), "+", ("B", "B"), ("du", r"\delta u"), size=1.3).move_to([0, 1.45, 0])
        self.play(TransformFromCopy(dA.k("A"), m2.k("A")), TransformFromCopy(dB.k("B"), m2.k("B")), FadeIn(m2.ks("etad", "ap", "eta", "+", "du")), run_time=1.1)
        tag = mixed(r"\delta u = u - \bar{u}\ \ \mathrm{(input\ offset;\ book\ extension,\ the\ lecture\ adds}\ +Bu\ \mathrm{later)}", DIM, 0.7).move_to([0, -1.4, 0])
        fit(tag, -6.8, 6.8)
        self.play(FadeIn(tag), run_time=0.6)
        self.step_done(m1, dA, dB, m2, tag)

        # 3. outputs: C and D
        self.play(self.chip("add an output  (book Eq. 8.9)"), FadeOut(VGroup(m1, tag)), m2.animate.move_to([-3.2, 2.7, 0]).scale(0.9),
                  dA.animate.scale(0.85).move_to([-4.9, 1.2, 0]), dB.animate.scale(0.85).move_to([-1.6, 1.2, 0]), run_time=1.0)
        g = M(("y", "y"), "=", ("g", "g(x,u)"), size=1.1).move_to([3.2, 2.7, 0])
        self.play(FadeIn(g, shift=0.1 * DOWN), run_time=0.6)
        dC = M(("C", "C"), "=", ("pc", r"\left.\frac{\partial g}{\partial x}\right|_{\bar{x},\bar{u}}"), size=0.8).move_to([1.6, 1.2, 0])
        dD = M(("D", "D"), "=", ("pd", r"\left.\frac{\partial g}{\partial u}\right|_{\bar{x},\bar{u}}"), size=0.8).move_to([4.9, 1.2, 0])
        self.play(TransformFromCopy(g.k("g"), dC.k("pc")), TransformFromCopy(g.k("g"), dD.k("pd")), FadeIn(dC.ks("C", "=")), FadeIn(dD.ks("D", "=")), run_time=1.2)
        m4 = M(("dy", r"\delta y"), ("ap", r"\approx"), ("C", "C"), ("eta", r"\eta"), "+", ("D", "D"), ("du", r"\delta u"), size=1.17).move_to([3.2, 2.7, 0])
        self.play(FadeOut(g), TransformFromCopy(dC.k("C"), m4.k("C")), TransformFromCopy(dD.k("D"), m4.k("D")), FadeIn(m4.ks("dy", "ap", "eta", "+", "du")), run_time=1.1)
        pe = mixed(r"\mathrm{pendulum,\ angle\ output}\ y = \theta:\quad C = [\,1\ \ 0\,],\ \ D = 0", PINK_C, 0.85).move_to([0, -0.5, 0])
        fit(pe, -6.8, 6.8)
        bk = mixed(r"\mathrm{book\ Eq.\ 8.10,\ shifted\ coordinates:}\ \ \dot{x} = Ax + Bu,\quad y = Cx + Du", DIM, 0.8).move_to([0, -1.6, 0])
        fit(bk, -6.8, 6.8)
        self.play(FadeIn(pe, shift=0.1 * UP), run_time=0.6)
        self.play(FadeIn(bk), run_time=0.6)
        self.step_done(m2, dA, dB, m4, dC, dD, pe, bk)


# ======================================================================== Section 4

class HyperbolicSequence(ControlScene):
    SEQ_ID = "hyperbolic"

    def construct(self):
        e0 = M(("etad", r"\dot{\eta}"), "=", ("A", "A"), ("eta", r"\eta"), "+", ("R", r"\mathcal{O}(\Vert\eta\Vert^2)"), size=1.25).move_to([0, 2.85, 0])
        qn = note("small near x̄, but not zero: can it change the picture?", DIM).move_to([0, 1.8, 0])
        self.start(e0, qn)

        # 1. hyperbolic
        self.play(self.chip("hyperbolic: Re λ ≠ 0"), FadeOut(qn), run_time=0.5)
        sp = splane(xr=(-3, 2), yr=(-2, 2), unit=0.72).move_to([-3.2, -0.45, 0])
        axis = Line(sp.p(0, -2), sp.p(0, 2)).set_stroke(ORANGE_C, 7)
        self.play(FadeIn(sp), run_time=0.7)
        dfn = mixed(r"\mathrm{hyperbolic:}\ \ \mathrm{Re}\,\lambda_i \neq 0\ \ \mathrm{for\ all}\ i", FG, 0.8).move_to([3.3, 1.0, 0])
        fit(dfn, -0.5, 6.9)
        ex = note("excluded: the imaginary axis", ORANGE_C).next_to(sp.p(0, 2), UP, buff=0.12)
        self.play(ShowCreation(axis), FadeIn(ex), FadeIn(dfn, shift=0.1 * LEFT), run_time=1.1)
        self.play(axis.animate.set_stroke(ORANGE_C, 4, opacity=0.6), run_time=0.4)
        self.step_done(e0, sp, axis, ex, dfn)

        # 2. all negative
        c1, c2, c3 = cross(sp.p(-1, 1.2), GREEN_C), cross(sp.p(-1, -1.2), GREEN_C), cross(sp.p(-2, 0), GREEN_C)
        t2 = mixed(r"\mathrm{all}\ \mathrm{Re}\,\lambda < 0 \Rightarrow \mathrm{locally\ asymptotically\ stable}", GREEN_C, 0.72).move_to([3.3, 0.0, 0])
        fit(t2, -0.5, 6.9)
        self.play(self.chip("all real parts negative"), FadeIn(c1, scale=0.5), FadeIn(c2, scale=0.5), FadeIn(c3, scale=0.5), run_time=0.9)
        self.play(FadeIn(t2, shift=0.1 * LEFT), run_time=0.6)
        self.step_done(e0, sp, axis, ex, dfn, c1, c2, c3, t2)

        # 3. one positive
        c3r = cross(sp.p(1, 0), RED_C)
        t3 = mixed(r"\mathrm{one}\ \mathrm{Re}\,\lambda > 0 \Rightarrow \mathrm{unstable}", RED_C, 0.72).move_to([3.3, -0.9, 0])
        fit(t3, -0.5, 6.9)
        self.play(self.chip("one real part positive"), Transform(c3, c3r, path_arc=-0.6), run_time=1.3)
        self.play(FadeIn(t3, shift=0.1 * LEFT), run_time=0.6)
        self.step_done(e0, sp, axis, ex, dfn, c1, c2, c3, t2, t3)

        # 4. on the axis
        c1o, c2o, c3o = cross(sp.p(0, 1.2), ORANGE_C), cross(sp.p(0, -1.2), ORANGE_C), cross(sp.p(-1.5, 0), GREEN_C)
        t4 = mixed(r"\mathrm{Re}\,\lambda = 0\ \mathrm{(none > 0)}:\ \mathrm{not\ decided\ by}\ A", ORANGE_C, 0.72).move_to([3.3, -1.8, 0])
        fit(t4, -0.5, 6.9)
        qm = VGroup(note("?", ORANGE_C, 30).next_to(sp.p(0, 1.2), RIGHT, buff=0.18), note("?", ORANGE_C, 30).next_to(sp.p(0, -1.2), RIGHT, buff=0.18))
        self.play(self.chip("on the imaginary axis"), Transform(c1, c1o), Transform(c2, c2o), Transform(c3, c3o, path_arc=0.6), run_time=1.3)
        self.play(FadeIn(t4, shift=0.1 * LEFT), FadeIn(qm), run_time=0.6)
        self.step_done(e0, sp, axis, ex, dfn, c1, c2, c3, t2, t3, t4, qm)

        # 5. -x^3 and +x^3
        self.play(self.chip("same A = 0  (authored pair)"), FadeOut(VGroup(e0, sp, axis, ex, dfn, c1, c2, c3, t2, t3, t4, qm)), run_time=0.7)
        fm = M(("f", r"\dot{x} = -x^3"), size=1.15, color=GREEN_C).move_to([-4.7, 1.55, 0])
        fp = M(("f", r"\dot{x} = +x^3"), size=1.15, color=RED_C).move_to([-4.7, -0.95, 0])
        am = M(("A", r"A = -3x^2\vert_{0} = 0"), size=0.95, color=BLUE_C).move_to([2.6, 1.55, 0])
        ap = M(("A", r"A = +3x^2\vert_{0} = 0"), size=0.95, color=BLUE_C).move_to([2.6, -0.95, 0])
        self.play(FadeIn(fm), FadeIn(fp), run_time=0.7)
        self.play(TransformFromCopy(fm, am), TransformFromCopy(fp, ap), run_time=1.2)
        same = mixed(r"\mathrm{identical\ linear\ model:}\ \dot{\eta} = 0\cdot\eta", YELLOW_C, 0.85).move_to([0.6, -2.55, 0])
        self.play(FadeIn(same, shift=0.1 * UP), run_time=0.6)
        self.step_done(fm, fp, am, ap, same)

        # 6. arrows decide
        self.play(self.chip("the cubic terms decide"), am.animate.scale(0.75).next_to(fm, DOWN, buff=0.2), ap.animate.scale(0.75).next_to(fp, DOWN, buff=0.2),
                  FadeOut(same), run_time=0.8)

        def line_at(y, inward, color):
            ln = Line([-2.2, y, 0], [5.6, y, 0]).set_stroke(DIM, 2)
            o = disc([1.7, y, 0], color, 0.11)
            arrs = VGroup()
            for x, L in ((1.1, 0.35), (2.6, 0.9)):        # |x^3| grows: longer arrows further out
                for sgn in (-1, 1):
                    a = 1.7 + sgn * x
                    b = a - sgn * L if inward else a + sgn * L
                    arrs.add(h_arrow(a, b, y, color, 4))
            return ln, o, arrs

        l1, o1, a1 = line_at(1.55, True, GREEN_C)
        l2, o2, a2 = line_at(-0.95, False, RED_C)
        self.play(ShowCreation(l1), ShowCreation(l2), FadeIn(o1), FadeIn(o2), run_time=0.7)
        self.play(LaggedStart(*[grow_arrow(a) for a in a1], lag_ratio=0.15), LaggedStart(*[grow_arrow(a) for a in a2], lag_ratio=0.15), run_time=1.4)
        s1 = note("offsets return: stable", GREEN_C).move_to([1.7, 2.25, 0])
        s2 = note("offsets escape: unstable", RED_C).move_to([1.7, -0.25, 0])
        hg = note("Hartman–Grobman: at a hyperbolic point (all Re λ ≠ 0) the local picture matches, qualitatively", DIM, 20).move_to([0.9, -2.55, 0])
        fit(hg, -2.3, 6.9)
        self.play(FadeIn(s1), FadeIn(s2), run_time=0.6)
        self.play(FadeIn(hg), run_time=0.6)
        self.step_done(fm, fp, am, ap, l1, l2, o1, o2, a1, a2, s1, s2, hg)


# ======================================================================== Section 5

class PendulumStateSequence(ControlScene):
    SEQ_ID = "pendulum-state"

    def construct(self):
        PV, LEN, TH = np.array([-4.5, 1.7, 0]), 2.4, 0.55
        pd = hanging(TH, LEN, PV)
        vref = DashedLine(PV, PV + 2.7 * DOWN).set_stroke(DIM, 2)
        arc = Arc(start_angle=-PI / 2, angle=TH, radius=0.85, arc_center=PV).set_stroke(YELLOW_C, 3)
        thl = M(("th", r"\theta"), size=0.95, color=YELLOW_C).move_to(PV + 1.15 * np.array([np.sin(TH / 2), -np.cos(TH / 2), 0]))
        gar = v_arrow(-6.5, 1.0, -0.2, DIM, 3)
        gl = mixed("g", DIM, 0.8).next_to(gar, RIGHT, buff=0.1)
        ll = mixed("L", DIM, 0.8).move_to(PV + 1.4 * np.array([np.sin(TH), -np.cos(TH), 0]) + 0.3 * RIGHT + 0.1 * UP)
        draw = VGroup(pd, vref, arc, thl, gar, gl, ll)
        e0 = M(("tdd", r"\ddot{\theta}"), "=", ("m", "-"), ("gl", r"\frac{g}{L}"), ("s", r"\sin\theta"), size=1.3).move_to([2.4, 2.4, 0])
        rad = note("θ in radians, from the downward vertical", DIM, 20).move_to([2.4, 1.3, 0])
        self.start(draw, e0, rad)

        # 1. friction
        e1 = M(("tdd", r"\ddot{\theta}"), "=", ("m", "-"), ("gl", r"\frac{g}{L}"), ("s", r"\sin\theta"), ("fr", r"-\,d\,\dot{\theta}"), size=1.3).move_to([2.4, 2.4, 0])
        self.play(self.chip("viscous friction"), FadeOut(rad), self.tmorph(e0, e1), run_time=1.2)
        bob = pd.ball.get_center()
        fa = arc_arrow(bob + 0.45 * RIGHT + 0.2 * UP, bob + 0.35 * LEFT + 0.35 * DOWN, angle=-TAU / 8, color=ORANGE_C)
        fl = note("friction opposes θ̇", ORANGE_C, 20).next_to(bob, RIGHT, buff=0.55).shift(0.2 * DOWN)
        bd = mixed(r"d > 0\quad\mathrm{(board:}\ \delta\mathrm{;\ MATLAB:}\ d\mathrm{)}", DIM, 0.75).move_to([2.4, 1.3, 0])
        self.play(FadeIn(fa), FadeIn(fl), FadeIn(bd), run_time=0.9)
        self.step_done(draw, e1, fa, fl, bd)

        # 2. g/L = 1
        ql = M(("q", r"q = \frac{g}{L} = 1"), size=1.0, color=YELLOW_C).move_to([2.4, 1.0, 0])
        e2 = M(("tdd", r"\ddot{\theta}"), "=", ("m", "-"), ("s", r"\sin\theta"), ("fr", r"-\,d\,\dot{\theta}"), size=1.3).move_to([2.4, 2.4, 0])
        self.play(self.chip("normalize g/L = 1"), FadeOut(bd), TransformFromCopy(e1.k("gl"), ql), run_time=1.0)
        self.play(self.tmorph(e1, e2), run_time=1.0)
        self.step_done(draw, e2, fa, fl, ql)

        # 3. state vector
        self.play(self.chip("state x = (θ, θ̇)"), FadeOut(VGroup(fa, fl, ql)), run_time=0.5)
        sx = M(("x", "x"), "=", size=0.95)
        S1 = Mat([["x_1"], ["x_2"]], size=0.9)
        se = M("=", size=0.95)
        S2 = Mat([[r"\theta"], [r"\dot{\theta}"]], size=0.9)
        srow = place_row(sx, S1, se, S2, buff=0.25, y=0.0).shift(2.4 * RIGHT)
        self.play(FadeIn(srow), run_time=0.8)
        ddt = M(("ddt", r"\frac{d}{dt}"), size=0.95)
        L1 = Mat([["x_1"], ["x_2"]], size=0.9)
        le = M("=", size=0.95)
        r2 = M(("s", r"-\sin x_1"), ("fr", r"-\,d\,x_2"), size=0.9)
        R1 = Mat([[M(("x2", "x_2"), size=0.9)], [r2]], size=0.9)
        sysr = place_row(ddt, L1, le, R1, buff=0.25, y=-1.75).shift(2.4 * RIGHT)
        self.play(FadeIn(VGroup(ddt, L1, le, R1.lb, R1.rb)), TransformFromCopy(S2.e[1][0], R1.e[0][0]), run_time=1.1)
        self.play(TransformFromCopy(e2.k("s"), r2.k("s")), TransformFromCopy(e2.k("fr"), r2.k("fr")), run_time=1.2)
        self.step_done(draw, e2, srow, sysr)

        # 4. fixed points
        self.play(self.chip("solve f(x̄) = 0"), FadeOut(VGroup(e2, srow)), sysr.animate.scale(0.85).move_to([3.4, 2.55, 0]), run_time=0.9)
        f1 = mixed(r"\mathrm{row\ 1:}\ \ x_2 = 0", FG, 0.78).move_to([3.4, 1.15, 0])
        fit(f1, -1.3, 6.9)
        f2 = mixed(r"\mathrm{row\ 2:}\ \ -\sin x_1 - d\cdot 0 = 0\ \Rightarrow\ \sin x_1 = 0", FG, 0.78).move_to([3.4, 0.35, 0])
        fit(f2, -1.3, 6.9)
        f3 = mixed(r"\bar{x} = (k\pi, 0):\ (0, 0)\ \mathrm{down},\ (\pi, 0)\ \mathrm{up}\ \ (\mathrm{mod}\ 2\pi)", YELLOW_C, 0.75).move_to([3.4, -0.55, 0])
        fit(f3, -1.3, 6.9)
        self.play(FadeIn(f1, shift=0.1 * DOWN), run_time=0.6)
        self.play(FadeIn(f2, shift=0.1 * DOWN), run_time=0.7)
        PU = np.array([-2.2, -1.3, 0])
        pu = hanging(PI, 2.0, PU)
        self.play(FadeOut(VGroup(arc, thl, ll)), Rotate(pd.swing, -TH, about_point=PV), FadeIn(pu), run_time=1.2)
        ld = mixed(r"\bar{\theta} = 0", FG, 0.8).next_to(pd.ball, DOWN, buff=0.25)
        lu = mixed(r"\bar{\theta} = \pi", FG, 0.8).next_to(PU, DOWN, buff=0.3)
        self.play(FadeIn(f3), FadeIn(ld), FadeIn(lu), run_time=0.8)
        self.step_done(pd, vref, gar, gl, sysr, f1, f2, f3, pu, ld, lu)

        # 5. offset at pi
        self.play(self.chip("near the top, the offset η is small"), FadeOut(VGroup(f1, f2)), f3.animate.set_y(1.35),
                  lu.animate.move_to(PU + np.array([1.15, -0.45, 0])), run_time=0.7)
        up_ref = DashedLine(PU, PU + 2.4 * UP).set_stroke(DIM, 2)
        dn_ref = DashedLine(PU, PU + 1.2 * DOWN).set_stroke(DIM, 2)
        self.play(ShowCreation(up_ref), ShowCreation(dn_ref), run_time=0.5)
        self.play(Rotate(pu.swing, 0.15, about_point=PU), run_time=0.8)
        big = Arc(start_angle=-PI / 2, angle=PI + 0.15, radius=0.65, arc_center=PU).set_stroke(YELLOW_C, 3)
        sm = Arc(start_angle=PI / 2, angle=0.15, radius=1.45, arc_center=PU).set_stroke(TEAL_C, 5)
        self.play(ShowCreation(big), run_time=0.9)
        self.play(ShowCreation(sm), run_time=0.6)
        t1 = M(("th", r"\theta = \pi + \eta \approx 3.29\ \mathrm{rad}"), size=0.95, color=YELLOW_C).move_to([3.4, 0.2, 0])
        t2 = M(("eta", r"\eta = \theta - \pi = 0.15"), size=0.95, color=TEAL_C).move_to([3.4, -0.75, 0])
        t3 = note("the local model at the top is written in η, not θ", DIM).move_to([3.4, -1.7, 0])
        self.play(FadeIn(t1), FadeIn(t2), FadeIn(t3), run_time=0.8)
        self.step_done(pd, vref, gar, gl, sysr, f3, pu, ld, lu, up_ref, dn_ref, big, sm, t1, t2, t3)


# ======================================================================== Section 6

SEEDS = [(0.45 * np.cos(a), 0.45 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 8, endpoint=False) + np.pi / 8]


def eig_down(d, q=1.0):
    disc_ = d * d - 4 * q
    if disc_ < 0:
        w = np.sqrt(-disc_) / 2
        return complex(-d / 2, w), complex(-d / 2, -w)
    r = np.sqrt(disc_) / 2
    return complex(-d / 2 + r, 0), complex(-d / 2 - r, 0)


def eig_up(d, q=1.0):
    r = np.sqrt(d * d + 4 * q) / 2
    return complex(-d / 2 + r, 0), complex(-d / 2 - r, 0)


class TwoJacobiansSequence(ControlScene):
    SEQ_ID = "two-jacobians"

    def construct(self):
        fl = M(("f", "f(x)"), "=", size=0.9)
        F = Mat([[M(("x2", "x_2"), size=0.85)], [M(("a", r"-q\sin x_1"), ("b", r"-\,d\,x_2"), size=0.85, colors={"b": ORANGE_C})]], size=0.85)
        frow = place_row(fl, F, buff=0.25, y=2.35).shift(3.6 * LEFT)
        self.start(frow)

        # 1. Jacobian
        jl = M(("J", r"\frac{Df}{Dx}"), "=", size=0.9)
        J = Mat([[M(("z", "0"), size=0.85), M(("o", "1"), size=0.85)],
                 [M(("c", r"-q\cos x_1"), size=0.85, color=BLUE_C), M(("dd", "-d"), size=0.85)]], size=0.85)
        jrow = place_row(jl, J, buff=0.25, y=2.35).shift(3.3 * RIGHT)
        cap = note("column 1: ∂/∂x₁,  column 2: ∂/∂x₂", DIM).move_to([0, 0.95, 0])
        self.play(self.chip("four partial derivatives"), FadeIn(jl), FadeIn(VGroup(J.lb, J.rb)), FadeIn(cap), run_time=0.7)
        self.play(TransformFromCopy(F.e[0][0], J.e[0][0]), TransformFromCopy(F.e[0][0], J.e[0][1]), run_time=1.0)
        self.play(TransformFromCopy(F.e[1][0].k("a"), J.e[1][0]), run_time=1.0)
        self.play(TransformFromCopy(F.e[1][0].k("b"), J.e[1][1]), run_time=0.9)
        self.step_done(frow, jrow, cap)

        # 2. evaluate at 0 and pi
        self.play(self.chip("cos 0 = 1,  cos π = −1"), FadeOut(cap), run_time=0.5)

        def amat(entry, name, x):
            l = M(("A", name), "=", size=0.9)
            m = Mat([[M("0", size=0.85), M("1", size=0.85)], [entry, M(("dd", "-d"), size=0.85)]], size=0.85)
            r = place_row(l, m, buff=0.25, y=-0.15).shift(x * RIGHT)
            return l, m, r

        ld_, Ad, rowd = amat(M(("c", "-q"), size=0.85, color=GREEN_C), "A_d", -3.4)
        lu_, Au, rowu = amat(M(("c", "q"), size=0.85, color=RED_C), "A_u", 3.4)
        midd = M(("c", r"-q\cos 0"), size=0.85, color=BLUE_C).move_to(Ad.e[1][0])
        midu = M(("c", r"-q\cos \pi"), size=0.85, color=BLUE_C).move_to(Au.e[1][0])
        self.play(FadeIn(VGroup(ld_, lu_, Ad.lb, Ad.rb, Au.lb, Au.rb)),
                  *[TransformFromCopy(J.e[i][j], Ad.e[i][j]) for (i, j) in ((0, 0), (0, 1), (1, 1))],
                  *[TransformFromCopy(J.e[i][j], Au.e[i][j]) for (i, j) in ((0, 0), (0, 1), (1, 1))],
                  TransformFromCopy(J.e[1][0], midd), TransformFromCopy(J.e[1][0], midu), run_time=1.3)
        nd = mixed(r"\cos 0 = 1", GREEN_C, 0.8).move_to([-3.1, -1.55, 0])
        nu_ = mixed(r"\cos \pi = -1", RED_C, 0.8).move_to([3.7, -1.55, 0])
        self.play(FadeIn(nd), FadeIn(nu_), run_time=0.6)
        self.play(ReplacementTransform(midd, Ad.e[1][0]), ReplacementTransform(midu, Au.e[1][0]), run_time=1.0)
        self.play(Indicate(Au.e[1][0], color=RED_C, scale_factor=1.4), run_time=0.8)
        pdn = note("down: gravity pulls back", GREEN_C, 20).move_to([-3.1, -2.2, 0])
        pup = note("up: gravity pushes away", RED_C, 20).move_to([3.7, -2.2, 0])
        self.play(FadeIn(pdn), FadeIn(pup), run_time=0.5)
        self.step_done(frow, jrow, rowd, rowu, nd, nu_, pdn, pup)

        # 3. local coordinates
        self.play(self.chip("offsets from each fixed point"), FadeOut(VGroup(pdn, pup)), run_time=0.5)
        td = mixed(r"\mathrm{acts\ on}\ \eta = \theta - 0", GREEN_C, 0.8).move_to(nd.get_center())
        tu = mixed(r"\mathrm{acts\ on}\ \eta = \theta - \pi", RED_C, 0.8).move_to(nu_.get_center())
        self.play(FadeTransform(nd, td), FadeTransform(nu_, tu), run_time=0.9)
        loc = M(("def", r"\eta = \theta - \bar{\theta},\ \ \nu = \omega:"), ("e1", r"\quad\dot{\eta} = \nu,"), ("e2", r"\quad\dot{\nu} \approx \mp q\,\eta - d\,\nu"),
                size=0.9, colors={"def": TEAL_C}).move_to([0, -2.55, 0])
        self.play(FadeIn(loc, shift=0.1 * UP), run_time=0.8)
        self.step_done(frow, jrow, rowd, rowu, td, tu, loc)

        # 4. characteristic equations
        self.play(self.chip("det(λI − A) = 0"), FadeOut(VGroup(loc, frow)), run_time=0.5)
        cd = mixed(r"\lambda^2 + d\lambda + q = 0", GREEN_C, 0.85).move_to(td.get_center())
        cu = mixed(r"\lambda^2 + d\lambda - q = 0", RED_C, 0.85).move_to(tu.get_center())
        self.play(FadeTransform(td, cd), FadeTransform(tu, cu), run_time=1.0)
        rd = M(("r", r"\lambda = \frac{-d \pm \sqrt{d^2 - 4q}}{2}"), size=0.95, color=GREEN_C).move_to([-2.4, -2.5, 0])
        ru = M(("r", r"\lambda = \frac{-d \pm \sqrt{d^2 + 4q}}{2}"), size=0.95, color=RED_C).move_to([3.7, -2.5, 0])
        self.play(TransformFromCopy(cd, rd), TransformFromCopy(cu, ru), run_time=1.2)
        self.step_done(jrow, rowd, rowu, cd, cu, rd, ru)

        # 5. d = 0: center vs saddle (q = 1)
        self.play(self.chip("no friction, q = 1"), FadeOut(VGroup(jrow, cd, cu, rd, ru)),
                  rowd.animate.scale(0.75).move_to([-4.7, 2.85, 0]), rowu.animate.scale(0.75).move_to([4.7, 2.85, 0]), run_time=0.9)
        sp = splane(xr=(-4, 2), yr=(-2, 2), unit=0.55).move_to([0, 0.45, 0])
        pdn_, pup_ = Portrait([-4.7, -0.5], 1.3), Portrait([4.7, -0.5], 1.3)
        A0d, A0u = np.array([[0, 1], [-1, 0.0]]), np.array([[0, 1], [1, 0.0]])
        fdn = pdn_.flow(A0d, [(0.35, 0), (0.7, 0)], GREEN_C, t1=6.3)
        fup = pup_.flow(A0u, [(0.9, -0.75), (-0.9, 0.75), (0.75, -0.9), (-0.75, 0.9), (0.15, -0.95), (-0.15, 0.95)], RED_C, t1=4.0)
        evs = VGroup(DashedLine(pup_.p(-1, -1), pup_.p(1, 1)).set_stroke(RED_C, 2), DashedLine(pup_.p(-1, 1), pup_.p(1, -1)).set_stroke(GREEN_C, 2))
        self.play(FadeIn(sp), FadeIn(pdn_.axes), FadeIn(pup_.axes), run_time=0.8)
        xs_d = [cross(sp.p(0, 1), YELLOW_C), cross(sp.p(0, -1), YELLOW_C)]
        xs_u = [cross(sp.p(1, 0), RED_C), cross(sp.p(-1, 0), GREEN_C)]
        dl0 = mixed("d = 0", FG, 0.8).move_to([0, -1.25, 0])
        self.play(*[FadeIn(c, scale=0.5) for c in xs_d + xs_u], FadeIn(dl0), run_time=0.8)
        self.play(ShowCreation(fdn), ShowCreation(fup), ShowCreation(evs), run_time=1.6)
        tdn = mixed(r"\pm i:\ \mathrm{linear\ center\ (not\ decided\ by}\ A\mathrm{)}", YELLOW_C, 0.68).move_to([-4.0, -2.3, 0])
        fit(tdn, -6.8, -1.6)
        tup = mixed(r"\pm 1:\ \mathrm{saddle,\ unstable}", RED_C, 0.68).move_to([4.7, -2.3, 0])
        self.play(FadeIn(tdn), FadeIn(tup), run_time=0.6)
        xd, xu = VGroup(*xs_d), VGroup(*xs_u)
        self.step_done(rowd, rowu, sp, pdn_.axes, pup_.axes, fdn, fup, evs, xd, xu, dl0, tdn, tup)

        # 6. friction sweep
        self.play(self.chip("increase the friction d"), FadeOut(VGroup(tdn, tup)), run_time=0.5)
        trace_d = VGroup()
        trace_u = VGroup()

        def place(d):
            for c, z in zip(xd, eig_down(d)):
                c.move_to(sp.p(z.real, z.imag))
            for c, z in zip(xu, eig_up(d)):
                c.move_to(sp.p(z.real, z.imag))

        def sweep(d0, d1):
            dlab = {"m": dl0}

            def upd(m, a):
                d = d0 + (d1 - d0) * a
                place(d)
                new = mixed(f"d = {d:.2f}", FG, 0.8).move_to([0, -1.25, 0])
                dlab["m"].become(new)
            return UpdateFromAlphaFunc(VGroup(xd, xu, dl0), upd)

        def locus(fn, d0, d1, color):
            pts = [[sp.p(z.real, z.imag) for z in fn(d)] for d in np.linspace(d0, d1, 80)]
            return VGroup(polyline([p[0] for p in pts], color, 2.5), polyline([p[1] for p in pts], color, 2.5))

        for c in xd:
            c.set_stroke(GREEN_C)
        ld1, lu1 = locus(eig_down, 0, 0.5, GREEN_C), locus(eig_up, 0, 0.5, RED_C)
        self.play(sweep(0, 0.5), ShowCreation(ld1), ShowCreation(lu1), run_time=1.6)
        A5 = np.array([[0, 1], [-1, -0.5]])
        fdn2 = pdn_.flow(A5, [(0.9, 0)], GREEN_C, t1=14)
        fup2 = pup_.flow(np.array([[0, 1], [1, -0.5]]), SEEDS, RED_C, t1=10.0, both=True)
        self.play(FadeTransform(fdn, fdn2), FadeTransform(fup, fup2), FadeOut(evs), run_time=1.0)
        fd5 = note("d = 0.5: decaying spiral", GREEN_C, 20).move_to([-4.7, -2.25, 0])
        self.play(FadeIn(fd5), run_time=0.4)
        ld2, lu2 = locus(eig_down, 0.5, 3.0, GREEN_C), locus(eig_up, 0.5, 3.0, RED_C)
        self.play(sweep(0.5, 3.0), ShowCreation(ld2), ShowCreation(lu2), run_time=2.6)
        A3 = np.array([[0, 1], [-1, -3.0]])
        fdn3 = pdn_.flow(A3, SEEDS, GREEN_C, t1=10.0, both=True)
        fup3 = pup_.flow(np.array([[0, 1], [1, -3.0]]), SEEDS, RED_C, t1=10.0, both=True)
        fd3 = note("d = 3 > 2√q: node, no oscillation", GREEN_C, 20).move_to([-4.7, -2.25, 0])
        self.play(FadeTransform(fdn2, fdn3), FadeTransform(fup2, fup3), FadeTransform(fd5, fd3), run_time=1.0)
        up3 = note("up: λ₊ = 0.30 > 0 for d = 3, still a saddle", RED_C, 20).move_to([4.7, -2.25, 0])
        ff = note("down eigenvalues meet at −1 when d = 2√q = 2, then split along the real axis", DIM, 20).move_to([0.8, -2.95, 0])
        fit(ff, -2.6, 6.9)
        self.play(FadeIn(up3), FadeIn(ff), run_time=0.6)
        self.step_done(rowd, rowu, sp, pdn_.axes, pup_.axes, fdn3, fup3, xd, xu, dl0, ld1, lu1, ld2, lu2, fd3, up3, ff)


# ======================================================================== Section 7

class MatlabSequence(ControlScene):
    SEQ_ID = "matlab-check"

    def construct(self):
        box = RoundedRectangle(width=5.5, height=6.0, corner_radius=0.15).set_stroke(DIM, 2).set_fill("#111827", 1).move_to([-4.0, 0.35, 0])
        head = note("MATLAB, re-typed from the lecture", DIM, 18).next_to(box.get_top(), DOWN, buff=0.15)
        mono = "Consolas"

        def tline(text, i, color=FG):
            return Text(text, font=mono, font_size=22).set_color(color).move_to([-6.5, 2.65 - 0.52 * i, 0], aligned_edge=LEFT)

        cmds = VGroup(tline(">> d = 0.1;", 0), tline(">> Ad = [0 1; -1 -d];", 1), tline(">> Au = [0 1;  1 -d];", 2))

        def amat(name, a21, x):
            l = M(("A", name), "=", size=0.8)
            m = Mat([[M("0", size=0.75), M("1", size=0.75)], [M(("a", a21), size=0.75), M(("dd", "-0.1"), size=0.75, color=ORANGE_C)]], size=0.75)
            return l, m, place_row(l, m, buff=0.2, y=2.55).shift(x * RIGHT)

        _, Ad, rowd = amat("A_d", "-1", 1.25)
        _, Au, rowu = amat("A_u", "1", 4.9)
        sp = splane(xr=(-2, 2), yr=(-1.5, 1.5), unit=0.8).move_to([3.1, -1.85, 0])
        self.start(box, head, cmds, rowd, rowu, sp)

        # 1. down polynomial
        pd = M(("det", r"\det(\lambda I - A_d) ="), ("l2", r"\lambda^2"), "+", ("b", "0.1"), ("l", r"\lambda"), "+", ("c", "1"), ("z", "= 0"), size=0.72,
               colors={"b": ORANGE_C}).move_to([3.1, 1.5, 0])
        self.play(self.chip("λ² + dλ + q with d = 0.1, q = 1"), FadeIn(pd.ks("det", "l2", "l", "z")), FadeIn(pd.k("+")), FadeIn(pd.k("+", 1)), run_time=0.8)
        self.play(TransformFromCopy(Ad.e[1][1], pd.k("b")), TransformFromCopy(Ad.e[1][0], pd.k("c")), run_time=1.2)
        self.step_done(box, head, cmds, rowd, rowu, sp, pd)

        # 2. down eigenvalues
        rd = mixed(r"\lambda = -0.05 \pm i\sqrt{1 - 0.0025} = -0.05 \pm 0.998749\,i", GREEN_C, 0.62).move_to([3.0, 0.8, 0])
        fit(rd, -1.0, 6.9)
        ghost = VGroup(DashedVMobject(Circle(radius=0.14).move_to(sp.p(0, 1)), num_dashes=10).set_stroke(DIM, 2),
                       DashedVMobject(Circle(radius=0.14).move_to(sp.p(0, -1)), num_dashes=10).set_stroke(DIM, 2))
        cd = VGroup(cross(sp.p(0, 1), YELLOW_C), cross(sp.p(0, -1), YELLOW_C))
        self.play(self.chip("quadratic formula"), FadeIn(rd, shift=0.1 * DOWN), FadeIn(ghost), FadeIn(cd), run_time=0.9)
        w = float(np.sqrt(0.9975))
        self.play(cd[0].animate.move_to(sp.p(-0.05, w)).set_stroke(GREEN_C), cd[1].animate.move_to(sp.p(-0.05, -w)).set_stroke(GREEN_C), run_time=1.0)
        out = VGroup(tline(">> eig(Ad)", 3), tline("  -0.0500 + 0.9987i", 4, GREEN_C), tline("  -0.0500 - 0.9987i", 5, GREEN_C))
        self.play(FadeIn(out, lag_ratio=0.3), run_time=1.0)
        lbd = note("just left of the axis: Re λ = −0.05", GREEN_C, 18).next_to(sp.p(-0.05, w), LEFT, buff=0.3).shift(0.35 * DOWN)
        self.play(FadeIn(lbd), run_time=0.4)
        self.step_done(box, head, cmds, rowd, rowu, sp, pd, rd, ghost, cd, out, lbd)

        # 3. up polynomial
        self.play(self.chip("only the constant term changes sign"), FadeOut(VGroup(pd, lbd)), rd.animate.set_y(1.5), run_time=0.7)
        pu = M(("det", r"\det(\lambda I - A_u) ="), ("l2", r"\lambda^2"), "+", ("b", "0.1"), ("l", r"\lambda"), ("c", "- 1"), ("z", "= 0"), size=0.72,
               colors={"b": ORANGE_C}).move_to([3.1, 0.8, 0])
        self.play(FadeIn(pu.ks("det", "l2", "l", "z")), FadeIn(pu.k("+")), run_time=0.6)
        self.play(TransformFromCopy(Au.e[1][1], pu.k("b")), TransformFromCopy(Au.e[1][0], pu.k("c")), Indicate(Au.e[1][0], color=RED_C), run_time=1.2)
        self.step_done(box, head, cmds, rowd, rowu, sp, rd, ghost, cd, out, pu)

        # 4. up eigenvalues
        ru = mixed(r"\lambda = -0.05 \pm \sqrt{0.0025 + 1} = -1.051249,\ \ 0.951249", RED_C, 0.62).move_to([3.0, 0.1, 0])
        fit(ru, -1.0, 6.9)
        ghost2 = VGroup(DashedVMobject(Circle(radius=0.14).move_to(sp.p(1, 0)), num_dashes=10).set_stroke(DIM, 2),
                        DashedVMobject(Circle(radius=0.14).move_to(sp.p(-1, 0)), num_dashes=10).set_stroke(DIM, 2))
        cu = VGroup(cross(sp.p(1, 0), RED_C), cross(sp.p(-1, 0), GREEN_C))
        self.play(self.chip("quadratic formula"), FadeIn(ru, shift=0.1 * DOWN), FadeIn(ghost2), FadeIn(cu), run_time=0.9)
        r = float(np.sqrt(1.0025))
        self.play(cu[0].animate.move_to(sp.p(-0.05 + r, 0)), cu[1].animate.move_to(sp.p(-0.05 - r, 0)), run_time=1.0)
        out2 = VGroup(tline(">> eig(Au)", 6), tline("  -1.0512", 7, GREEN_C), tline("   0.9512", 8, RED_C))
        self.play(FadeIn(out2, lag_ratio=0.3), run_time=1.0)
        self.step_done(box, head, cmds, rowd, rowu, sp, rd, ghost, cd, out, pu, ru, ghost2, cu, out2)

        # 5. recap
        self.play(self.chip("read the eigenvalues"), FadeOut(VGroup(rd, pu, ru)), run_time=0.6)
        k1 = note("down: −0.05 ± 0.9987i → stable focus (decaying oscillation)", GREEN_C, 20).move_to([3.0, 1.5, 0])
        k2 = note("up: 0.9512 > 0 → saddle, unstable", RED_C, 20).move_to([3.0, 0.9, 0])
        k3 = mixed(r"\mathrm{next\ lectures:}\ \dot{x} = Ax + Bu\ \mathrm{and\ feedback}", BLUE_C, 0.7).move_to([3.0, 0.25, 0])
        fit(k3, -1.0, 6.9)
        self.play(FadeIn(k1, shift=0.1 * DOWN), Indicate(cd, color=GREEN_C), run_time=0.8)
        self.play(FadeIn(k2, shift=0.1 * DOWN), Indicate(cu[0], color=RED_C), run_time=0.8)
        self.play(FadeIn(k3), run_time=0.6)
        self.step_done(box, head, cmds, rowd, rowu, sp, ghost, cd, out, ghost2, cu, out2, k1, k2, k3)
