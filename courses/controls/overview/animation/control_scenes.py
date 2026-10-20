"""ManimGL scenes for the Control Bootcamp overview guide (one scene per sequence).

Rendered offscreen by build_control.py. Every scene calls `self.start()` once and
`self.step_done()` once per step of its spec in control_specs.py.

Colour identities (shared with the browser's step cards):
    teal    the state x, xdot, theta and their entries
    blue    the input u and the input matrix B, actuators
    yellow  the gain K, values being substituted, highlights
    pink    outputs y, sensors and C
    orange  disturbances d
    green / red   stable left half-plane / unstable right half-plane
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ctl_common import *  # noqa: E402,F403

XD = ("xdot", r"\dot{x}")
TH = ("th", r"\theta")
THD = ("thd", r"\dot{\theta}")
THDD = ("thdd", r"\ddot{\theta}")
LAM = ("lam", r"\lambda")
TEAL_KEYS = {"th": TEAL_C, "thd": TEAL_C, "thdd": TEAL_C}


def curved_arrow(center, radius, start_angle, angle, color=FG, width=4):
    """Arc around `center` with a triangular tip at its end."""
    full = Arc(start_angle=start_angle, angle=angle, radius=radius, arc_center=center)
    end = full.get_points()[-1]
    d = end - full.point_from_proportion(0.95)
    d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0], 0])
    s = 0.13
    arc = full.copy().pointwise_become_partial(full, 0, 0.9)
    tip = Polygon(end, end - 1.7 * s * d + s * n, end - 1.7 * s * d - s * n).set_fill(color, 1).set_stroke(color, 1)
    arc.set_stroke(color, width).set_fill(opacity=0)
    return VGroup(arc, tip)


def node(text, color=FG, size=26, w=None):
    t = label(text, size, FG)
    box = RoundedRectangle(width=w or t.get_width() + 0.5, height=t.get_height() + 0.36,
                           corner_radius=0.14).set_stroke(color, 2.5).set_fill(BG, 1)
    t.move_to(box)
    g = VGroup(box, t)
    g.box = box
    return g


def link(a, b, color=DIM):
    return Line(a.get_bottom(), b.get_top()).set_stroke(color, 3)


class PendRig(VGroup):
    """Inverted pendulum with dashed vertical, angle arc and theta label; set_theta() moves it."""
    def __init__(self, theta, pivot, L=2.4, arc_r=0.95):
        self.pivot, self.L, self.arc_r = np.array(pivot, dtype=float), L, arc_r
        p = self.pivot
        self.ground = Line(p + 1.4 * LEFT + 0.34 * DOWN, p + 1.4 * RIGHT + 0.34 * DOWN).set_stroke(DIM, 2)
        self.base = Rectangle(width=1.1, height=0.32).set_stroke(DIM, 2).set_fill(FAINT, 1).move_to(p + 0.17 * DOWN)
        self.vert = DashedLine(p, p + UP * (L + 0.35), dash_length=0.12).set_stroke(DIM, 2)
        self.rod = Line(p, p + UP * L).set_stroke(FG, 7)
        self.ball = Circle(radius=0.22).set_fill(TEAL_C, 1).set_stroke(FG, 2)
        self.hinge = Dot(p, radius=0.08).set_fill(FG, 1)
        self.arc = VMobject()
        self.th = Mx(TH, size=0.95, colors=TEAL_KEYS)
        super().__init__(self.ground, self.base, self.vert, self.rod, self.ball, self.hinge, self.arc, self.th)
        self.theta = theta
        self.set_theta(theta)

    def tip(self, th=None):
        th = self.theta if th is None else th
        return self.pivot + self.L * np.array([np.sin(th), np.cos(th), 0])

    def set_theta(self, th):
        self.theta = th
        self.rod.put_start_and_end_on(self.pivot, self.tip(th))
        self.ball.move_to(self.tip(th))
        a = Arc(start_angle=PI / 2, angle=-th if abs(th) > 1e-3 else -1e-3, radius=self.arc_r,
                arc_center=self.pivot).set_stroke(YELLOW_C, 3)
        self.arc.become(a)
        mid = PI / 2 - max(th, 0.5) / 2      # keep the label off the rod when nearly upright
        self.th.move_to(self.pivot + (self.arc_r + 0.3) * np.array([np.cos(mid), np.sin(mid), 0]))
        return self


def swing(rig, th1, rate=smooth):
    th0 = rig.theta
    return UpdateFromAlphaFunc(rig, lambda m, a: m.set_theta(th0 + (th1 - th0) * a), rate_func=rate)


# ======================================================================== Section 1

class StateIOSequence(ControlScene):
    SEQ_ID = "state-io"

    def construct(self):
        rig = PendRig(0.28, [-4.4, -1.55, 0])
        cap = label("inverted pendulum: tilt θ from vertical", 24, DIM).next_to(rig.ground, DOWN, buff=0.35)
        self.start(rig, cap)

        # 1. state vector from angle and angular velocity
        R = rig.L + 0.5
        a0 = PI / 2 - rig.theta + 0.12
        w = curved_arrow(rig.pivot, R, a0, -0.42, color=TEAL_C)
        wl = Mx(THD, size=0.95, colors=TEAL_KEYS).next_to(w[1], RIGHT, buff=0.12).shift(0.15 * UP)
        mat = Mat([[TH], [THD]], size=1.15, colors=TEAL_KEYS)
        lhs = Mx("x", "=", size=1.15)
        vec = place_row(lhs, mat, buff=0.2).move_to([2.6, 2.3, 0])
        vcap = label("state: angle and angular velocity", 22, DIM).next_to(vec, DOWN, buff=0.25)
        self.play(ShowCreation(w), FadeIn(wl, shift=0.1 * RIGHT), self.chip("angle and angular velocity"), run_time=0.9)
        self.play(TransformFromCopy(rig.th, mat.e[0][0], path_arc=-0.5),
                  TransformFromCopy(wl, mat.e[1][0], path_arc=-0.5),
                  ShowCreation(mat.lb), ShowCreation(mat.rb), FadeIn(lhs), run_time=1.5)
        self.play(FadeIn(vcap, shift=0.1 * UP), run_time=0.5)
        self.step_done(rig, cap, w, wl, vec, vcap)

        # 2. a model predicts the motion: upright is unstable, the rod falls
        sys_box = block("", w=3.6, h=1.25, color=TEAL_C).move_to([2.8, 0.25, 0])
        f0 = Mx(XD, "=", "f", "(", "x", ")", size=1.0).move_to(sys_box)
        plot = Plot(t_max=3.0, y_min=0.0, y_max=1.4, width=4.0, height=1.9, y_label="θ(t)")
        plot.move_to([2.8, -2.25, 0])
        th0, th1 = rig.theta, 1.25
        t_end = float(np.arccosh(th1 / th0))
        grow = plot.curve(lambda t: th0 * np.cosh(t), 0, t_end, color=RED_C)
        gl = label("a small tilt grows: upright is unstable", 20, RED_C).next_to(plot, UP, buff=0.12)
        self.play(FadeOut(w), FadeOut(wl), FadeIn(sys_box), Write(f0), self.chip("prediction"), run_time=1.0)
        self.play(FadeIn(plot), run_time=0.4)
        self.play(swing(rig, th1, rate=lambda a: a ** 2.2), ShowCreation(grow, rate_func=linear), run_time=2.2)
        self.play(FadeIn(gl), run_time=0.4)
        self.step_done(rig, cap, vec, vcap, sys_box, f0, plot, grow, gl)

        # 3. add an input u
        f1 = Mx(XD, "=", "f", "(", "x", ",", "u", ")", size=1.0).move_to(sys_box)
        u_in = arrow([-0.4, 0.25, 0], sys_box.get_left(), color=BLUE_C)
        ul = Mx("u", size=1.0).next_to(u_in, UP, buff=0.12)
        torque = curved_arrow(rig.pivot, 0.55, PI * 0.95, -1.0, color=BLUE_C)
        tl = Mx("u", size=0.9).next_to(torque, LEFT, buff=0.1).shift(0.1 * UP)
        self.play(FadeOut(VGroup(plot, grow, gl)), swing(rig, 0.28), self.chip("torque at the hinge"), run_time=1.1)
        self.play(self.tmorph(f0, f1), grow_arrow(u_in), FadeIn(ul),
                  ShowCreation(torque), FadeIn(tl), run_time=1.4)
        self.play(TransformFromCopy(ul, f1.k("u"), path_arc=-0.4), run_time=0.7)
        self.step_done(rig, cap, vec, vcap, sys_box, f1, u_in, ul, torque, tl)

        # 4. measure an output y
        y_out = arrow(sys_box.get_right(), [6.5, 0.25, 0], color=PINK_C)
        yl = Mx("y", size=1.0).next_to(y_out, UP, buff=0.12)
        g = Mx("y", "=", "g", "(", "x", ")", size=1.0).move_to([2.8, -1.25, 0])
        gcap = label("sensors: perhaps only the angle", 22, DIM).next_to(g, DOWN, buff=0.25)
        later = label("later in the overview: y = x (every state measured)", 22, PINK_C).next_to(gcap, DOWN, buff=0.35)
        self.play(grow_arrow(y_out), FadeIn(yl), self.chip("output"), run_time=0.9)
        self.play(TransformFromCopy(yl, g.k("y")), Write(VGroup(*[t for t in g.toks if t.key != "y"])), run_time=1.1)
        self.play(FadeIn(gcap), FadeIn(later, shift=0.1 * UP), run_time=0.7)
        self.step_done(rig, cap, vec, vcap, sys_box, f1, u_in, ul, torque, tl, y_out, yl, g, gcap, later)

        # 5. the goal: return to x = 0 (upright, at rest)
        goal = label("goal: choose u so that x(t) → 0", 28, GREEN_C, weight=BOLD).move_to([2.8, -2.3, 0])
        zero = Mx("x", "=", "0", size=0.9).next_to(rig.vert, UP, buff=0.12)
        zcap = label("upright and at rest", 20, GREEN_C).next_to(zero, RIGHT, buff=0.2)
        self.play(FadeOut(VGroup(gcap, later)), self.chip("regulate to the upright state"), run_time=0.6)
        self.play(swing(rig, 0.0, rate=lambda a: 1 - (1 - a) ** 2), FadeIn(zero), FadeIn(zcap), run_time=1.6)
        self.play(Write(goal), run_time=1.0)
        self.step_done(rig, cap, vec, vcap, sys_box, f1, u_in, ul, torque, tl, y_out, yl, g, goal, zero, zcap)


# ======================================================================== Section 2

def truck():
    cab = RoundedRectangle(width=0.6, height=0.62, corner_radius=0.08).set_fill(FAINT, 1).set_stroke(FG, 2)
    trailer = Rectangle(width=1.7, height=0.86).set_fill(FAINT, 1).set_stroke(FG, 2)
    trailer.next_to(cab, LEFT, buff=0.05, aligned_edge=DOWN)
    tail = Polygon(trailer.get_corner(UL), trailer.get_corner(UL) + 0.42 * LEFT + 0.2 * DOWN,
                   trailer.get_corner(DL) + 0.42 * LEFT + 0.12 * UP, trailer.get_corner(DL))
    tail.set_fill(TEAL_C, 0.6).set_stroke(TEAL_C, 2)
    wheels = VGroup(*[Circle(radius=0.11).set_fill(DIM, 1).set_stroke(FG, 1).move_to(p)
                      for p in (cab.get_bottom() + 0.02 * DOWN, trailer.get_corner(DL) + 0.35 * RIGHT,
                                trailer.get_corner(DR) + 0.35 * LEFT)])
    road = Line(LEFT * 1.6, RIGHT * 1.6).set_stroke(DIM, 2).next_to(wheels, DOWN, buff=0.0)
    air = VGroup(*[VMobject().set_points_smoothly([[-0.8 + 0.2 * k, 0.55 + 0.15 * k, 0], [-1.6, 0.6 + 0.12 * k, 0],
                                                   [-2.4, 0.35 + 0.1 * k, 0]]).set_stroke(TEAL_C, 2, opacity=0.6)
                   for k in range(2)])
    g = VGroup(road, trailer, cab, tail, wheels)
    air.move_to(trailer.get_corner(UL) + 0.15 * UP + 0.45 * LEFT)
    g.add(air)
    g.tail = tail
    return g


class ControlTypesSequence(ControlScene):
    SEQ_ID = "control-types"

    def construct(self):
        root = node("control", FG, 30).move_to([0, 2.75, 0])
        q = label("energy in while running?  measurements used?", 22, DIM).next_to(root, DOWN, buff=0.35)
        self.start(root, q)

        # 1. passive / active
        passive = node("passive", TEAL_C).move_to([-4.2, 1.15, 0])
        active = node("active", BLUE_C).move_to([2.6, 1.15, 0])
        lp, la = link(root, passive), link(root, active)
        pt = truck().scale(0.85).move_to([-4.2, -0.5, 0])
        pcap = label("designed in once, no energy input", 20, DIM).next_to(pt, DOWN, buff=0.25)
        pcap2 = label("e.g. a truck's tail fairing cuts drag", 20, TEAL_C).next_to(pcap, DOWN, buff=0.12)
        acap = label("energy put in through actuators", 20, DIM).next_to(active, DOWN, buff=0.18)
        self.play(FadeOut(q), ShowCreation(lp), ShowCreation(la), self.chip(), run_time=0.8)
        self.play(FadeIn(passive, shift=0.2 * DOWN), FadeIn(active, shift=0.2 * DOWN), run_time=0.7)
        self.play(FadeIn(pt, shift=0.3 * RIGHT), FadeIn(pcap), FadeIn(pcap2), FadeIn(acap), run_time=1.0)
        self.step_done(root, passive, active, lp, la, pt, pcap, pcap2, acap)

        # 2. open loop / (disturbance feedforward) / closed loop
        ol = node("open loop", BLUE_C).move_to([-0.7, -0.75, 0])
        ff = node("disturbance feedforward", FAINT, 18).move_to([2.25, -0.75, 0])
        cl = node("closed-loop feedback", PINK_C).move_to([5.45, -0.75, 0])
        links = VGroup(link(active, ol), link(active, ff, FAINT), link(active, cl))
        olc = label("preplanned, no sensors", 20, DIM).next_to(ol, DOWN, buff=0.2)
        ffc = label("(book: measure the disturbance)", 16, DIM).next_to(ff, DOWN, buff=0.2)
        clc = label("sensor-based", 20, PINK_C).next_to(cl, DOWN, buff=0.2)
        halo = SurroundingRectangle(VGroup(cl, clc), buff=0.1).set_stroke(PINK_C, 2, opacity=0.7)
        self.play(FadeOut(acap), ShowCreation(links, lag_ratio=0.2), self.chip(), run_time=0.9)
        self.play(LaggedStart(FadeIn(ol, shift=0.2 * DOWN), FadeIn(ff, shift=0.2 * DOWN), FadeIn(cl, shift=0.2 * DOWN),
                              lag_ratio=0.25), run_time=1.0)
        self.play(FadeIn(olc), FadeIn(ffc), FadeIn(clc), ShowCreation(halo), run_time=0.8)
        tree = VGroup(root, passive, active, lp, la, ol, ff, cl, links, olc, ffc, clc)
        self.step_done(tree, pt, pcap, pcap2, halo)

        # 3. open-loop block diagram
        Y0 = -0.9
        ctrl = block("controller", w=2.5, h=1.0, color=BLUE_C).move_to([-2.3, Y0, 0])
        ctrl_sub = label("(inverts a model)", 18, DIM).next_to(ctrl, DOWN, buff=0.12)
        plant = block("system", w=2.3, h=1.0, color=TEAL_C).move_to([1.9, Y0, 0])
        r_l = Mx("r", size=1.0).move_to([-6.0, Y0 + 0.4, 0])
        r_in = arrow([-6.3, Y0, 0], ctrl.get_left())
        u_a = arrow(ctrl.get_right(), plant.get_left(), BLUE_C)
        u_l = Mx("u", size=1.0).next_to(u_a, UP, buff=0.1)
        y_a = arrow(plant.get_right(), [6.4, Y0, 0], PINK_C)
        y_l = Mx("y", size=1.0).next_to(y_a, UP, buff=0.1).shift(0.6 * RIGHT)
        none = label("nothing comes back", 22, DIM).move_to([0, Y0 - 1.55, 0])

        def crumb(text, color):
            """Legible corner reminder of where this diagram sits in the taxonomy."""
            t = label(text, 26, FG)
            fr = RoundedRectangle(width=t.get_width() + 0.5, height=t.get_height() + 0.32, corner_radius=0.14)
            fr.set_stroke(color, 2.5).set_fill(BG, 1)
            t.move_to(fr)
            return VGroup(fr, t).to_corner(UL, buff=0.45)

        where = crumb("active → open loop", BLUE_C)
        ol_node = ol.copy()
        self.play(FadeOut(VGroup(tree, pt, pcap, pcap2, halo)), ReplacementTransform(ol_node, where), self.chip(),
                  run_time=1.0)
        self.play(FadeIn(r_l), grow_arrow(r_in), FadeIn(ctrl), FadeIn(ctrl_sub), run_time=0.8)
        self.play(grow_arrow(u_a), FadeIn(u_l), FadeIn(plant), run_time=0.8)
        self.play(grow_arrow(y_a), FadeIn(y_l), run_time=0.6)
        pulse = Dot(radius=0.09).set_fill(YELLOW_C, 1).move_to([-6.3, Y0, 0])
        path = VMobject().set_points_as_corners([[-6.3, Y0, 0], [6.3, Y0, 0]])
        self.play(MoveAlongPath(pulse, path), run_time=1.5, rate_func=linear)
        self.play(FadeOut(pulse), FadeIn(none), run_time=0.5)
        diagram = VGroup(ctrl, ctrl_sub, plant, r_l, u_a, u_l, y_a, y_l)
        self.step_done(where, diagram, r_in, none)

        # 4. closed loop: tap y, return it, subtract at a summing junction
        jx = -4.75
        junc = sum_junction().move_to([jx, Y0, 0])
        r_in2 = arrow([-6.3, Y0, 0], junc.get_left())
        e_a = arrow(junc.get_right(), ctrl.get_left())
        e_l = Mx("e", size=0.9).next_to(e_a, UP, buff=0.1)
        tap = Dot([4.4, Y0, 0], radius=0.08).set_fill(PINK_C, 1)
        fb = poly_arrow([[4.4, Y0, 0], [4.4, Y0 - 1.75, 0], [jx, Y0 - 1.75, 0], junc.get_bottom()], color=PINK_C)
        sensor = block("sensor", w=1.6, h=0.62, color=PINK_C, size=22).move_to([0.0, Y0 - 1.75, 0])
        # Keep the signal wire below the label instead of drawing through its letters.
        sensor.text.shift(0.18 * UP)
        plus = Mx("+", size=0.75).next_to(junc, UL, buff=0.02)
        minus = Mx("-", size=0.75).next_to(junc, DR, buff=0.02).shift(0.12 * DOWN + 0.05 * LEFT)
        fb_l = label("feedback: measured y", 20, PINK_C).next_to(sensor, DOWN, buff=0.15)
        eq = Mx("e", "=", "r", "-", "y", size=0.9).move_to([-2.3, Y0 + 1.1, 0])
        where_cl = crumb("active → closed-loop feedback", PINK_C)
        ctrl_sub2 = label("(acts on the measured error e)", 18, DIM).next_to(ctrl, DOWN, buff=0.12)
        self.play(FadeOut(none), ReplacementTransform(where, where_cl), self.chip(), run_time=0.6)
        self.play(FadeIn(tap, scale=0.5), ShowCreation(fb[0]), FadeIn(fb[1]), FadeIn(sensor), run_time=1.3)
        self.play(ReplacementTransform(r_in, r_in2), FadeIn(junc), grow_arrow(e_a),
                  FadeIn(plus), FadeIn(minus), FadeIn(e_l), run_time=1.0)
        self.play(Write(eq), FadeIn(fb_l), FadeTransform(ctrl_sub, ctrl_sub2), run_time=0.8)
        pulse = Dot(radius=0.09).set_fill(YELLOW_C, 1)
        loop = VMobject().set_points_as_corners([[jx, Y0, 0], [4.4, Y0, 0], [4.4, Y0 - 1.75, 0], [jx, Y0 - 1.75, 0],
                                                 [jx, Y0 - 0.22, 0]])
        pulse.move_to(loop.get_start())
        self.play(MoveAlongPath(pulse, loop), run_time=2.4, rate_func=linear)
        self.play(FadeOut(pulse), run_time=0.3)
        loop_parts = VGroup(junc, r_in2, e_a, e_l, tap, fb, sensor, plus, minus, fb_l)
        diagram = VGroup(ctrl, ctrl_sub2, plant, r_l, u_a, u_l, y_a, y_l)
        self.step_done(where_cl, diagram, loop_parts, eq)

        # 5. relabel as the overview's regulator: r = 0, y = x, gain K, u = -Kx
        r0 = Mx("r", "=", "0", size=0.9).move_to([-6.2, Y0 + 0.45, 0])
        gain = block("gain  K", w=2.5, h=1.0, color=YELLOW_C).move_to(ctrl)
        gain_sub = VGroup(label("(u = K e, here e = −x)", 18, DIM)).next_to(gain, DOWN, buff=0.12)
        yx = Mx("y", "=", "x", size=0.9).move_to(y_l).shift(0.2 * RIGHT)
        ukx = Mx("u", "=", "K", "(", "0", "-", "x", ")", "=", "-", "K", "x", size=0.85).move_to([-2.5, Y0 + 1.15, 0])
        d_a = arrow(plant.get_top() + 1.1 * UP, plant.get_top(), ORANGE_C)
        d_l = Mx("d", size=0.9).next_to(d_a, RIGHT, buff=0.12)
        dcap = label("disturbance (next section)", 18, ORANGE_C).next_to(d_l, RIGHT, buff=0.15)
        self.play(self.chip("regulate to x = 0"), run_time=0.4)
        self.play(ReplacementTransform(r_l, r0), ReplacementTransform(ctrl, gain), FadeTransform(ctrl_sub2, gain_sub),
                  ReplacementTransform(y_l, yx), run_time=1.2)
        self.play(ReplacementTransform(eq, ukx), run_time=1.2)
        self.play(grow_arrow(d_a), FadeIn(d_l), FadeIn(dcap), run_time=0.8)
        diagram2 = VGroup(gain, gain_sub, plant, r0, u_a, u_l, y_a, yx)
        self.step_done(where_cl, diagram2, loop_parts, ukx, d_a, d_l, dcap)


# ======================================================================== Section 3

class WhyFeedbackSequence(ControlScene):
    SEQ_ID = "why-feedback"
    CX = 2.6

    def item(self, i, text):
        n = label(f"{i}", 30, FAINT, weight=BOLD)
        t = label(text, 30, FAINT)
        return VGroup(n, t).arrange(RIGHT, buff=0.3)

    def lit(self, it, color):
        return AnimationGroup(it[0].animate.set_color(color), it[1].animate.set_color(FG))

    def construct(self):
        head = label("Why feedback?", 40, FG, weight=BOLD).to_corner(UL, buff=0.5)
        items = VGroup(*[self.item(i + 1, t) for i, t in enumerate(["Uncertainty", "Instability", "Disturbances",
                                                                   "Efficiency"])])
        items.arrange(DOWN, buff=0.55, aligned_edge=LEFT).next_to(head, DOWN, buff=0.7, aligned_edge=LEFT)
        rule = Line(UP * 3.3, DOWN * 3.0).set_stroke(FAINT, 2).move_to([-1.7, 0, 0])
        self.start(head, items, rule)
        cx = self.CX

        # 1. uncertainty: bars from the static cruise numbers
        base_y = -2.3
        def bar(x, v, color, name, fill=0.75):
            h = v * 0.06
            r = Rectangle(width=1.1, height=h).set_fill(color, fill).set_stroke(color, 2)
            r.move_to([x, base_y + h / 2, 0])
            val = label(f"{v:g}", 22, FG).next_to(r, UP, buff=0.1)
            nm = label(name, 19, DIM).next_to([x, base_y, 0], DOWN, buff=0.15)
            return VGroup(r, val, nm)
        axis = Line([cx - 3.0, base_y, 0], [cx + 3.0, base_y, 0]).set_stroke(DIM, 2)
        b1 = bar(cx - 2.0, 60, FG, "target r", fill=0.15)
        b2 = bar(cx, 30, RED_C, "open loop")
        b3 = bar(cx + 2.0, 57.7, GREEN_C, "feedback, K = 50")
        ttl = label("internal: the model's gain is off by 2×", 24, FG).move_to([cx, 2.6, 0])
        sub = label("teaching model y = a u, planned with a = 1, true a = 0.5", 20, DIM).next_to(ttl, DOWN, buff=0.15)
        self.play(self.lit(items[0], YELLOW_C), FadeIn(ttl), FadeIn(sub), self.chip(), run_time=0.8)
        self.play(ShowCreation(axis), GrowFromEdge(b1[0], DOWN), FadeIn(b1[1:]), run_time=0.8)
        self.play(GrowFromEdge(b2[0], DOWN), FadeIn(b2[1:]), run_time=0.8)
        self.play(GrowFromEdge(b3[0], DOWN), FadeIn(b3[1:]), run_time=0.8)
        ill1 = VGroup(axis, b1, b2, b3, ttl, sub)
        self.step_done(head, items, rule, ill1)

        # 2. instability: the eigenvalue at +1 is unchanged by a planned input
        sp = splane(xr=(-4, 2), yr=(-2, 2), unit=0.72).move_to([cx, -0.35, 0])
        p1 = pole_cross(RED_C).move_to(sp.p(1, 0))
        p2 = pole_cross(FG).move_to(sp.p(-1, 0))
        ttl2 = label("an additive planned input leaves A unchanged", 24, FG).move_to([cx, 2.6, 0])
        wave_plot = Plot(t_max=4, y_min=-1, y_max=1, width=2.0, height=0.8, t_label="t").move_to([cx + 3.0, 1.55, 0])
        wave = wave_plot.curve(lambda t: 0.8 * np.sin(5 * t), color=BLUE_C, width=3)
        wl = Mx("u", "(", "t", ")", size=0.75).next_to(wave_plot, LEFT, buff=0.15)
        stays = label("λ = +1 stays", 22, RED_C).next_to(p1, UP, buff=0.35)
        self.play(FadeOut(ill1), items[0].animate.set_opacity(0.55), self.lit(items[1], YELLOW_C), FadeIn(ttl2),
                  self.chip(), run_time=0.8)
        self.play(FadeIn(sp), FadeIn(p1, scale=1.5), FadeIn(p2, scale=1.5), run_time=0.8)
        self.play(FadeIn(wave_plot), ShowCreation(wave), FadeIn(wl), run_time=1.0)
        self.play(WiggleOutThenIn(p1), FadeIn(stays), run_time=1.0)
        fb_arc = arc_arrow(sp.p(1, 0.3), sp.p(-2, 0.3), angle=TAU / 5, color=GREEN_C, width=3)
        fb_l = label("feedback u = −Kx changes the matrix", 20, GREEN_C).next_to(sp, DOWN, buff=0.2)
        self.play(ShowCreation(fb_arc), FadeIn(fb_l), run_time=1.0)
        ill2 = VGroup(sp, p1, p2, ttl2, wave_plot, wave, wl, stays, fb_arc, fb_l)
        self.step_done(head, items, rule, ill2)

        # 3. disturbances: a gust enters the system, the loop sees its effect
        Y = 0.2
        plant = block("system", w=2.4, h=1.0, color=TEAL_C).move_to([cx, Y, 0])
        ctrl = block("controller", w=2.4, h=0.9, color=BLUE_C).move_to([cx, Y - 2.0, 0])
        y_a = arrow(plant.get_right(), [cx + 3.4, Y, 0], PINK_C)
        y_l = Mx("y", size=0.9).next_to(y_a, UP, buff=0.1)
        fb = poly_arrow([[cx + 2.4, Y, 0], [cx + 2.4, Y - 2.0, 0], ctrl.get_right()], color=PINK_C)
        back = poly_arrow([ctrl.get_left(), [cx - 2.4, Y - 2.0, 0], [cx - 2.4, Y, 0], plant.get_left()], color=BLUE_C)
        u_l = Mx("u", size=0.9).next_to([cx - 2.4, Y - 1.0, 0], LEFT, buff=0.15)
        gusts = VGroup(*[VMobject().set_points_smoothly([[cx - 1.4 + 0.0, Y + 1.85 - 0.22 * k, 0],
                                                         [cx - 0.9, Y + 1.95 - 0.22 * k, 0],
                                                         [cx - 0.4, Y + 1.75 - 0.22 * k, 0],
                                                         [cx + 0.1, Y + 1.85 - 0.22 * k, 0]]).set_stroke(ORANGE_C, 3)
                         for k in range(3)])
        d_a = arrow([cx + 0.6, Y + 1.7, 0], plant.get_top() + 0.6 * RIGHT, ORANGE_C)
        d_l = Mx("d", size=0.9).next_to(d_a, RIGHT, buff=0.12)
        ttl3 = label("external: a gust d pushes the system", 24, FG).move_to([cx, 2.95, 0])
        note = label("too hard to predict, but its effect shows up in y", 20, DIM).move_to([cx, Y - 3.0, 0])
        self.play(FadeOut(ill2), items[1].animate.set_opacity(0.55), self.lit(items[2], YELLOW_C), FadeIn(ttl3),
                  self.chip(), run_time=0.8)
        self.play(FadeIn(plant), FadeIn(ctrl), grow_arrow(y_a), FadeIn(y_l),
                  ShowCreation(fb), ShowCreation(back), FadeIn(u_l), run_time=1.2)
        self.play(ShowCreation(gusts, lag_ratio=0.3), run_time=0.8)
        self.play(gusts.animate.shift(0.5 * RIGHT + 0.3 * DOWN).set_opacity(0), grow_arrow(d_a),
                  FadeIn(d_l), run_time=0.9)
        pulse = Dot(radius=0.09).set_fill(YELLOW_C, 1)
        loop = VMobject().set_points_as_corners([plant.get_right(), [cx + 2.4, Y, 0], [cx + 2.4, Y - 2.0, 0],
                                                 [cx - 2.4, Y - 2.0, 0], [cx - 2.4, Y, 0], plant.get_left()])
        pulse.move_to(loop.get_start())
        self.play(MoveAlongPath(pulse, loop), FadeIn(note), run_time=2.0, rate_func=linear)
        self.play(FadeOut(pulse), run_time=0.3)
        ill3 = VGroup(plant, ctrl, y_a, y_l, fb, back, u_l, d_a, d_l, ttl3, note)
        self.step_done(head, items, rule, ill3)

        # 4. efficiency, then the caveat
        pa = Plot(t_max=6, y_min=-1, y_max=1, width=2.9, height=1.5).move_to([cx - 1.75, 1.0, 0])
        pb = Plot(t_max=6, y_min=-1, y_max=1, width=2.9, height=1.5).move_to([cx + 1.75, 1.0, 0])
        ca = pa.curve(lambda t: 0.85 * np.sin(6 * t), color=BLUE_C, width=3, n=400)
        cb = pb.curve(lambda t: 0.45 * np.exp(-0.9 * t) * np.sin(3.5 * t), color=BLUE_C, width=3, n=400)
        la = label("open loop: keep pumping u", 20, DIM).next_to(pa, UP, buff=0.15)
        lb = label("good feedback: small corrections", 20, DIM).next_to(pb, UP, buff=0.15)
        ttl4 = label("effort u(t) needed to hold the rod up", 24, FG).move_to([cx, 2.75, 0])
        warn_box = RoundedRectangle(width=6.6, height=1.65, corner_radius=0.16).set_stroke(ORANGE_C, 2.5)
        warn_box.set_fill(BG, 1).move_to([cx, -1.75, 0])
        w1 = label("not automatic: a poorly chosen gain can destabilize the loop,", 21, FG)
        w2 = label("and high gain amplifies sensor noise", 21, FG)
        w0 = label("FINE PRINT", 18, ORANGE_C, weight=BOLD)
        wt = VGroup(w0, w1, w2).arrange(DOWN, buff=0.12).move_to(warn_box)
        self.play(FadeOut(ill3), items[2].animate.set_opacity(0.55), self.lit(items[3], YELLOW_C), FadeIn(ttl4),
                  self.chip(), run_time=0.8)
        self.play(FadeIn(pa), FadeIn(pb), FadeIn(la), FadeIn(lb), run_time=0.6)
        self.play(ShowCreation(ca, rate_func=linear), ShowCreation(cb, rate_func=linear), run_time=1.8)
        self.play(FadeIn(warn_box), Write(wt), run_time=1.2)
        ill4 = VGroup(pa, pb, ca, cb, la, lb, ttl4, warn_box, wt)
        self.step_done(head, items, rule, ill4)


class CruiseSequence(ControlScene):
    SEQ_ID = "cruise-model"
    COL = {"a": FG, "am": FG, "r": GREEN_C, "y": PINK_C, "u": BLUE_C, "d": ORANGE_C, "K": YELLOW_C}

    def M(self, *toks, size=1.15):
        return Mx(*toks, size=size, colors=self.COL)

    def construct(self):
        AM = ("am", r"a_m")
        model = self.M("y", "=", "a", "u", "+", "d", size=1.3).move_to([0, 1.6, 0])
        tag = label("static teaching model, no dynamics", 22, YELLOW_C).next_to(model, UP, buff=0.4)
        legend = VGroup(*[label(t, 20, c) for t, c in (("y  speed", PINK_C), ("u  throttle", BLUE_C),
                                                        ("a  true gain", FG), ("d  disturbance (hills)", ORANGE_C))])
        legend.arrange(RIGHT, buff=0.6).move_to([0, 0.2, 0])
        self.start(model, tag, legend)

        # 1. open loop: u = r / a_m, substitute, collect
        top = VGroup(model, tag)
        self.play(top.animate.scale(0.72).move_to([0, 2.95, 0]), FadeOut(legend), self.chip("plan from the model"),
                  run_time=0.8)
        plan_l = self.M("u", "=")
        plan_f = Frac(self.M("r"), self.M(AM))
        plan = place_row(plan_l, plan_f).move_to([-4.4, 1.3, 0])
        self.play(Write(plan_l), FadeIn(plan_f), run_time=0.8)
        slot = hbox(model.k("u"), BLUE_C, 0.06)
        self.play(ShowCreation(slot), run_time=0.4)
        s_l = self.M("y", "=", "a")
        s_f = Frac(self.M("r"), self.M(AM))
        s_r = self.M("+", "d")
        sub = place_row(s_l, s_f, s_r, buff=0.22).move_to([1.2, 1.2, 0])
        self.play(TransformFromCopy(model.ks("y", "=", "a"), s_l), TransformFromCopy(plan_f, s_f, path_arc=-0.5),
                  TransformFromCopy(model.ks("+", "d"), s_r), FadeOut(slot), run_time=1.5)
        o_l = self.M("y", "=")
        o_f = Frac(self.M("a"), self.M(AM))
        o_r = self.M("r", "+", "d")
        ol = place_row(o_l, o_f, o_r, buff=0.22).move_to([1.2, -0.35, 0])
        self.play(TransformFromCopy(s_l.ks("y", "="), o_l), TransformFromCopy(s_l.k("a"), o_f.num, path_arc=0.5),
                  TransformFromCopy(s_f.num, o_r.k("r"), path_arc=-0.5), TransformFromCopy(s_f.bar, o_f.bar),
                  TransformFromCopy(s_f.den, o_f.den), TransformFromCopy(s_r, o_r.ks("+", "d")), run_time=1.5)
        num = label("a = 0.5, aₘ = 1, r = 60:   y = 30 + d", 22, RED_C).next_to(ol, DOWN, buff=0.35)
        ol_tag = label("OPEN LOOP", 18, RED_C, weight=BOLD).next_to(ol, LEFT, buff=0.5)
        self.play(FadeIn(num), FadeIn(ol_tag), run_time=0.6)
        self.step_done(top, plan, sub, ol, num, ol_tag)

        # 2. closed loop: u = K(r - y), substitute into the model
        olg = VGroup(ol, ol_tag)
        law = self.M("u", "=", "K", "(", "r", "-", "y", ")").move_to([-3.6, 1.3, 0])
        self.play(FadeOut(VGroup(plan, sub, num)), olg.animate.scale(0.7).move_to([4.3, -2.85, 0]),
                  self.chip("proportional feedback"), run_time=0.9)
        self.play(Write(law), run_time=0.9)
        slot = hbox(model.k("u"), BLUE_C, 0.06)
        cl1 = self.M("y", "=", "a", "K", ("(", "("), "r", "-", ("y", "y"), (")", ")"), "+", "d").move_to([0.9, -0.1, 0])
        self.play(ShowCreation(slot), run_time=0.4)
        self.play(TransformFromCopy(model.ks("y", "=", "a"), cl1.ks("y", "=", "a")),
                  TransformFromCopy(law.span("K", ")"), VGroup(*cl1.toks[3:9]), path_arc=-0.4),
                  TransformFromCopy(model.ks("+", "d"), cl1.ks("+", "d")), FadeOut(slot), run_time=1.6)
        both = VGroup(hbox(cl1.k("y", 0), PINK_C, 0.05), hbox(cl1.k("y", 1), PINK_C, 0.05))
        bl = label("y on both sides", 20, PINK_C).next_to(cl1, DOWN, buff=0.3)
        self.play(ShowCreation(both), FadeIn(bl), run_time=0.6)
        self.step_done(top, olg, law, cl1, both, bl)

        # 3. expand, move -aKy across, factor y
        e1 = self.M("y", "=", ("a", "a"), ("K", "K"), "r", "-", ("a", "a"), ("K", "K"), ("y", "y"), "+", "d")
        e1.move_to([0.9, -0.1, 0])
        self.play(FadeOut(both), FadeOut(bl), self.chip("expand"), run_time=0.4)
        self.play(ReplacementTransform(cl1.ks("y", "=", "a", "K"), VGroup(e1.k("y"), e1.k("="), e1.k("a"), e1.k("K"))),
                  TransformFromCopy(cl1.ks("a", "K"), VGroup(e1.k("a", 1), e1.k("K", 1)), path_arc=-0.6),
                  ReplacementTransform(cl1.k("r"), e1.k("r")), ReplacementTransform(cl1.k("-"), e1.k("-")),
                  ReplacementTransform(cl1.k("y", 1), e1.k("y", 1)), ReplacementTransform(cl1.ks("+", "d"), e1.ks("+", "d")),
                  FadeOut(cl1.ks("(", ")")), run_time=1.4)
        self.settle(top, olg, law, e1)
        e2 =self.M("y", ("+", "+"), "a", "K", ("y", "y"), "=", "a", "K", "r", ("+", "+"), "d").move_to([0.9, -0.1, 0])
        self.play(self.chip("move −aKy to the left"), run_time=0.3)
        self.play(ReplacementTransform(e1.k("y"), e2.k("y")),
                  ReplacementTransform(e1.k("-"), e2.k("+"), path_arc=1.2),
                  ReplacementTransform(VGroup(e1.k("a", 1), e1.k("K", 1), e1.k("y", 1)),
                                       VGroup(e2.k("a"), e2.k("K"), e2.k("y", 1)), path_arc=1.2),
                  ReplacementTransform(e1.k("="), e2.k("=")),
                  ReplacementTransform(VGroup(e1.k("a"), e1.k("K"), e1.k("r")), VGroup(e2.k("a", 1), e2.k("K", 1), e2.k("r"))),
                  ReplacementTransform(e1.ks("+", "d"), VGroup(e2.k("+", 1), e2.k("d"))), run_time=1.5)
        self.settle(top, olg, law, e2)
        e3 =self.M("(", "1", ("+", "+"), "a", "K", ")", ("y", "y"), "=", "a", "K", "r", ("+", "+"), "d").move_to([0.9, -0.1, 0])
        ys = VGroup(hbox(e2.k("y"), PINK_C, 0.05), hbox(e2.k("y", 1), PINK_C, 0.05))
        self.play(ShowCreation(ys), self.chip("factor out y"), run_time=0.5)
        self.play(ReplacementTransform(e2.k("y", 1), e3.k("y")), Transform(e2.k("y"), e3.k("y").copy()),
                  FadeIn(e3.ks("(", "1", ")")), ReplacementTransform(e2.k("+"), e3.k("+")),
                  ReplacementTransform(e2.ks("a", "K"), e3.ks("a", "K")), ReplacementTransform(e2.k("="), e3.k("=")),
                  ReplacementTransform(VGroup(e2.k("a", 1), e2.k("K", 1), e2.k("r"), e2.k("+", 1), e2.k("d")),
                                       VGroup(e3.k("a", 1), e3.k("K", 1), e3.k("r"), e3.k("+", 1), e3.k("d"))),
                  FadeOut(ys), run_time=1.5)
        self.step_done(top, olg, law, e3)

        # 4. divide by 1 + aK; numbers; compare with open loop
        den = lambda: self.M("1", "+", "a", "K")  # noqa: E731
        f_l = self.M("y", "=")
        f1 = Frac(self.M("a", "K"), den())
        f_m = self.M("r", "+")
        f2 = Frac(self.M("1"), den())
        f_r = self.M("d")
        fin = place_row(f_l, f1, f_m, f2, f_r, buff=0.2).move_to([0.9, 0.05, 0])
        self.play(self.chip("divide by 1 + aK > 0"), run_time=0.3)
        self.play(ReplacementTransform(e3.k("y"), f_l.k("y"), path_arc=-0.8), ReplacementTransform(e3.k("="), f_l.k("=")),
                  ReplacementTransform(e3.ks("1", "+", "a", "K"), f1.den, path_arc=0.8),
                  TransformFromCopy(e3.ks("1", "+", "a", "K"), f2.den, path_arc=0.8),
                  FadeOut(e3.ks("(", ")")), ReplacementTransform(VGroup(e3.k("a", 1), e3.k("K", 1)), f1.num),
                  ReplacementTransform(e3.k("r"), f_m.k("r")), ReplacementTransform(e3.k("+", 1), f_m.k("+")),
                  ReplacementTransform(e3.k("d"), f_r), FadeIn(f1.bar), FadeIn(f2.bar), FadeIn(f2.num), run_time=1.7)
        self.settle(top, olg, law, fin)
        vals = label("a = 0.5, K = 50:   y = (25/26) r + (1/26) d  ≈  0.96 r + 0.04 d", 22, GREEN_C)
        vals.next_to(fin, DOWN, buff=0.45)
        err = label("error r − y = (r − d)/(1 + aK): small, generally nonzero at finite K", 22, FG).next_to(vals, DOWN, buff=0.22)
        cl_tag = label("CLOSED LOOP", 18, GREEN_C, weight=BOLD).next_to(fin, LEFT, buff=0.5)
        self.play(FadeIn(cl_tag), FadeIn(vals, shift=0.1 * UP), run_time=0.8)
        self.play(FadeIn(err, shift=0.1 * UP), Indicate(olg, color=RED_C, scale_factor=1.05), run_time=1.0)
        self.step_done(top, olg, law, fin, vals, err, cl_tag)


# ======================================================================== Section 4

class StateSpaceSequence(ControlScene):
    SEQ_ID = "state-space"

    def construct(self):
        S = 1.45
        e0 = Mx(XD, "=", "A", "x", size=S).move_to([0, 0.9, 0])
        self.start(e0)

        # 1. solution x(t) = e^{At} x(0); eigenvalues decide growth or decay
        sol = Mx(("x", "x"), ("(t)", "(t)"), "=", ("eAt", "e^{At}"), ("x0", "x(0)"), size=1.2,
                 colors={"(t)": TEAL_C, "x0": TEAL_C}).move_to([0, -0.6, 0])
        self.play(e0.animate.move_to([0, 1.7, 0]), self.chip("matrix exponential"), run_time=0.7)
        self.play(TransformFromCopy(e0.k("A"), sol.k("eAt"), path_arc=0.5), TransformFromCopy(e0.k("x"), sol.k("x0"), path_arc=0.5),
                  FadeIn(sol.ks("x", "(t)", "=")), run_time=1.5)
        p1 = Plot(t_max=3, y_min=-0.2, y_max=1.2, width=2.2, height=1.1).move_to([-2.6, -2.45, 0])
        p2 = Plot(t_max=3, y_min=-0.2, y_max=1.2, width=2.2, height=1.1).move_to([2.6, -2.45, 0])
        c1 = p1.curve(lambda t: np.exp(-1.2 * t), color=GREEN_C)
        c2 = p2.curve(lambda t: 0.1 * np.exp(1.1 * t), color=RED_C)
        l1 = label("all Re λ(A) < 0: decays", 22, GREEN_C).next_to(p1, UP, buff=0.15)
        l2 = label("any Re λ(A) > 0: grows", 22, RED_C).next_to(p2, UP, buff=0.15)
        self.play(FadeIn(VGroup(p1, p2, l1, l2)), ShowCreation(c1), ShowCreation(c2), run_time=1.3)
        self.step_done(e0, sol, p1, p2, c1, c2, l1, l2)

        # 2. add + Bu
        e1 = Mx(XD, "=", "A", "x", "+", "B", "u", size=S).move_to([0, 1.2, 0])
        ul = label("input u: the control knob", 22, BLUE_C)
        bl = label("B: how u pushes ẋ", 22, BLUE_C)
        self.play(FadeOut(VGroup(sol, p1, p2, c1, c2, l1, l2), shift=0.3 * DOWN), self.chip("actuation"), run_time=0.7)
        self.play(self.tmorph(e0, e1), run_time=1.3)
        ul.next_to(e1.k("u"), DOWN, buff=0.7).shift(1.0 * RIGHT)
        bl.next_to(e1.k("B"), DOWN, buff=0.7).shift(0.9 * LEFT)
        ua = arrow(ul.get_top() + 0.05 * UP, e1.k("u").get_bottom() + 0.08 * DOWN, BLUE_C, width=2.5)
        ba = arrow(bl.get_top() + 0.05 * UP, e1.k("B").get_bottom() + 0.08 * DOWN, BLUE_C, width=2.5)
        self.play(FadeIn(ul), FadeIn(bl), ShowCreation(ua), ShowCreation(ba), run_time=0.9)
        self.step_done(e1, ul, bl, ua, ba)

        # 3. measurement y = Cx (D = 0)
        e2 = Mx("y", "=", "C", "x", size=S).move_to([0, -0.6, 0])
        e2.align_to(e1, LEFT)
        cl = label("sensors read combinations of the state", 22, PINK_C).next_to(e2, RIGHT, buff=0.8)
        dl = label("overview: no direct feedthrough, D = 0", 20, DIM).next_to(e2, DOWN, buff=0.45).align_to(e2, LEFT)
        self.play(FadeOut(VGroup(ul, bl, ua, ba)), self.chip("measurement"), run_time=0.6)
        self.play(TransformFromCopy(e1.k("x"), e2.k("x"), path_arc=0.6), Write(e2.ks("y", "=", "C")), run_time=1.2)
        self.play(FadeIn(cl, shift=0.1 * LEFT), FadeIn(dl), run_time=0.7)
        self.step_done(e1, e2, cl, dl)

        # 4. sizes: tokens become rectangles of their shapes
        n, m, p = 1.6, 0.8, 0.55
        def R(w, h, color, txt):
            r = Rectangle(width=w, height=h).set_stroke(color, 3).set_fill(color, 0.18)
            t = Mx(txt, size=0.75, colors={txt: color}) if txt else None
            return VGroup(r, t.move_to(r)) if t else VGroup(r)
        col = 0.32
        top_y, bot_y = 1.25, -1.75
        row1 = [R(col, n, TEAL_C, XD), Mx("=", size=1.0), R(n, n, FG, "A"), R(col, n, TEAL_C, "x"), Mx("+", size=1.0),
                R(m, n, BLUE_C, "B"), R(col, m, BLUE_C, "u")]
        row2 = [R(col, p, PINK_C, "y"), Mx("=", size=1.0), R(n, p, PINK_C, "C"), R(col, n, TEAL_C, "x")]
        for r_ in (row1, row2):
            g = VGroup(*r_).arrange(RIGHT, buff=0.22)
            g.move_to([0, top_y if r_ is row1 else bot_y, 0])
            for piece in r_:
                if not isinstance(piece, Mx):
                    piece.align_to(r_[0] if r_ is row2 else r_[2], UP)
        dims1 = VGroup(
            label("n×1", 18, DIM).next_to(row1[0], DOWN, buff=0.12),
            label("n×n", 18, DIM).next_to(row1[2], DOWN, buff=0.12),
            label("n×1", 18, DIM).next_to(row1[3], DOWN, buff=0.12),
            label("n×m", 18, DIM).next_to(row1[5], DOWN, buff=0.12),
            label("m×1", 18, DIM).next_to(row1[6], DOWN, buff=0.12))
        dims2 = VGroup(
            label("p×1", 18, DIM).next_to(row2[0], DOWN, buff=0.12),
            label("p×n", 18, DIM).next_to(row2[2], DOWN, buff=0.12),
            label("n×1", 18, DIM).next_to(row2[3], DOWN, buff=0.12))
        self.play(FadeOut(VGroup(cl, dl)), self.chip("n states, m inputs, p outputs"), run_time=0.5)
        src1 = [e1.k("xdot"), e1.k("="), e1.k("A"), e1.k("x"), e1.k("+"), e1.k("B"), e1.k("u")]
        src2 = [e2.k("y"), e2.k("="), e2.k("C"), e2.k("x")]
        self.play(*[ReplacementTransform(a, b) for a, b in zip(src1, row1)],
                  *[ReplacementTransform(a, b) for a, b in zip(src2, row2)], run_time=1.6)
        self.play(FadeIn(dims1, lag_ratio=0.1), FadeIn(dims2, lag_ratio=0.1), run_time=0.8)
        rule1 = label("Ax and Bu are both n-vectors, so they add to give ẋ", 21, FG).move_to([0, -0.45, 0])
        rule2 = label("Cx is a p-vector", 21, FG).next_to(VGroup(*row2), RIGHT, buff=0.6)
        self.play(FadeIn(rule1), FadeIn(rule2), run_time=0.7)
        shapes = VGroup(*row1, *row2, dims1, dims2, rule1, rule2)
        self.step_done(shapes)

        # 5. the pendulum in matrix form, row times column
        SZ = 1.0
        lhs = Mat([[THD], [THDD]], size=SZ, colors=TEAL_KEYS)
        eqs = Mx("=", size=SZ)
        A = Mat([["0", "1"], ["1", "0"]], size=SZ)
        X = Mat([[TH], [THD]], size=SZ, colors=TEAL_KEYS)
        pl = Mx("+", size=SZ)
        Bm = Mat([["0"], ["1"]], size=SZ, colors={"0": BLUE_C, "1": BLUE_C})
        U = Mx("u", size=SZ)
        mrow = place_row(lhs, eqs, A, X, pl, Bm, U, buff=0.2).move_to([0, 1.4, 0])
        lab_a = label("A", 22, DIM).next_to(A, UP, buff=0.12)
        lab_b = label("B", 22, BLUE_C).next_to(Bm, UP, buff=0.12)
        self.play(FadeOut(shapes, shift=0.3 * DOWN), self.chip("linearized, g/L = 1, no damping"), run_time=0.7)
        self.play(FadeIn(mrow, lag_ratio=0.05), FadeIn(lab_a), FadeIn(lab_b), run_time=1.3)
        r2 = hbox(A.row(1), YELLOW_C, 0.1)
        c2 = hbox(X.cells, YELLOW_C, 0.1)
        b2 = hbox(Bm.e[1][0], YELLOW_C, 0.08)
        prod = Mx(THDD, "=", ("1a", "1"), r"\cdot", ("th", r"\theta"), "+", ("0a", "0"), r"\cdot", ("thd", r"\dot{\theta}"),
                  ("+", "+"), ("1b", "1"), r"\cdot", "u", size=1.0, colors=TEAL_KEYS).move_to([0, -0.5, 0])
        res = Mx(THDD, "=", TH, "+", "u", size=1.15, colors=TEAL_KEYS).move_to([0, -1.75, 0])
        row1 = VGroup(label("row 1:", 20, DIM), Mx(THD, "=", THD, size=0.7, colors=TEAL_KEYS),
                      label("(bookkeeping)", 20, DIM)).arrange(RIGHT, buff=0.2).move_to([0, -2.75, 0])
        self.play(ShowCreation(r2), ShowCreation(c2), ShowCreation(b2), run_time=0.6)
        self.play(TransformFromCopy(lhs.e[1][0], prod.k("thdd")), FadeIn(prod.k("=")),
                  TransformFromCopy(A.e[1][0], prod.k("1a")), TransformFromCopy(X.e[0][0], prod.k("th")),
                  TransformFromCopy(A.e[1][1], prod.k("0a")), TransformFromCopy(X.e[1][0], prod.k("thd")),
                  TransformFromCopy(Bm.e[1][0], prod.k("1b")), TransformFromCopy(U, prod.k("u")),
                  FadeIn(VGroup(*[t for t in prod.toks if t.key in (r"\cdot", "+")])), run_time=1.6)
        self.play(TransformFromCopy(prod.k("thdd"), res.k("thdd")), TransformFromCopy(prod.k("="), res.k("=")),
                  TransformFromCopy(prod.k("th"), res.k("th")), TransformFromCopy(prod.k("+", 1), res.k("+")),
                  TransformFromCopy(prod.k("u"), res.k("u")), FadeOut(VGroup(r2, c2, b2)), run_time=1.2)
        rl = label("gravity amplifies the tilt; the torque u pushes back", 20, FG).next_to(res, RIGHT, buff=0.5)
        self.play(FadeIn(rl), FadeIn(row1), run_time=0.6)
        self.step_done(mrow, lab_a, lab_b, prod, res, rl, row1)


# ======================================================================== Section 5

class CloseLoopSequence(ControlScene):
    SEQ_ID = "close-loop"

    def construct(self):
        S = 1.45
        Y = 1.0
        e0 = Mx(XD, "=", "A", "x", "+", "B", "u", size=S).move_to([0, Y, 0])
        yx = Mx("y", "=", "x", size=0.95)
        note = VGroup(yx, label("full state measured", 24, DIM)).arrange(RIGHT, buff=0.4).move_to([0, -1.0, 0])
        self.start(e0, note)

        # 1. u = -Kx
        law = Mx("u", "=", "-", "K", "x", size=1.25).move_to([0, -1.0, 0])
        kl = label("K: gain matrix, m × n", 22, YELLOW_C).next_to(law, DOWN, buff=0.4)
        self.play(note.animate.scale(0.75).to_corner(UR, buff=0.4), self.chip("a linear control law"), run_time=0.8)
        self.play(TransformFromCopy(e0.k("u"), law.k("u"), path_arc=0.5), TransformFromCopy(yx.k("x"), law.k("x"), path_arc=0.4),
                  FadeIn(law.ks("=", "-", "K")), run_time=1.4)
        self.play(FadeIn(kl, shift=0.1 * UP), run_time=0.5)
        self.step_done(e0, note, law, kl)

        # 2. substitute u
        e1 = Mx(XD, "=", "A", "x", "+", "B", "(", "-", "K", ("x", "x"), ")", size=S).move_to([0, Y, 0])
        b_u = hbox(e0.k("u"), BLUE_C)
        b_l = hbox(law.span("-", "x"), YELLOW_C)
        self.play(ShowCreation(b_u), ShowCreation(b_l), FadeOut(kl), self.chip("u → −Kx"), run_time=0.7)
        self.play(self.tmorph(e0, e1, pairs=[(("x", 0), ("x", 0))], skip=[e1.k("-"), e1.k("K"), e1.k("x", 1)]),
                  TransformFromCopy(law.k("-"), e1.k("-"), path_arc=-0.6), TransformFromCopy(law.k("K"), e1.k("K"), path_arc=-0.6),
                  TransformFromCopy(law.k("x"), e1.k("x", 1), path_arc=-0.6), FadeOut(b_u), FadeOut(b_l), run_time=1.6)
        self.step_done(e1, note, law)

        # 3. B(-Kx) = -BKx; law goes to the corner
        e2 = Mx(XD, "=", "A", "x", "-", "B", "K", ("x", "x"), size=S).move_to([0, Y, 0])
        self.play(law.animate.scale(0.7).to_corner(UL, buff=0.4), self.chip("B(−Kx) = −BKx"), run_time=0.7)
        self.play(self.tmorph(e1, e2, pairs=[("-", "-"), (("x", 0), ("x", 0)), (("x", 1), ("x", 1))], path_arc=0), run_time=1.5)
        order = label("order kept: B then K (matrix products do not commute)", 22, DIM).move_to([0, -0.6, 0])
        self.play(FadeIn(order, shift=0.1 * UP), Indicate(e2.ks("B", "K"), color=YELLOW_C), run_time=0.9)
        self.step_done(e2, note, law, order)

        # 4. factor x on the right
        e3 = Mx(XD, "=", "(", "A", "-", "B", "K", ")", "x", size=S).move_to([0, Y, 0])
        xs = VGroup(hbox(e2.k("x", 0), TEAL_C, 0.06), hbox(e2.k("x", 1), TEAL_C, 0.06))
        self.play(FadeOut(order), ShowCreation(xs), self.chip("common factor on the right"), run_time=0.7)
        self.play(self.tmorph(e2, e3, pairs=[(("x", 1), "x")], skip_src=[e2.k("x", 0)]),
                  Transform(e2.k("x", 0), e3.k("x").copy(), path_arc=-1.0), FadeOut(xs), run_time=1.7)
        bk = e3.ks("B", "K")
        br = under_bracket(bk, YELLOW_C)
        brl = label("(n×m)(m×n) = n×n, like A", 22, YELLOW_C).next_to(br, DOWN, buff=0.15)
        w1 = Mx("x", "(", "A", "-", "B", "K", ")", size=0.9)
        w2 = Mx("(", "A", "-", "K", "B", ")", "x", size=0.9)
        wrong = VGroup(w1, w2).arrange(RIGHT, buff=1.6).move_to([0, -2.2, 0])
        strikes = VGroup(strike(w1), strike(w2))
        wl = label("not these", 20, RED_C).next_to(wrong, DOWN, buff=0.2)
        self.play(ShowCreation(br), FadeIn(brl), run_time=0.8)
        self.play(FadeIn(wrong), run_time=0.5)
        self.play(ShowCreation(strikes, lag_ratio=0.3), FadeIn(wl), run_time=0.7)
        self.step_done(e3, note, law, br, brl, wrong, strikes, wl)

        # 5. A_cl = A - BK and the eigenvalue regions
        top = e3.copy()
        top.generate_target()
        acl = Mx(("Acl", r"A_{\mathrm{cl}}"), "=", "A", "-", "B", "K", size=1.15).move_to([-3.4, 1.15, 0])
        sp = splane(xr=(-4, 2), yr=(-2, 2), unit=0.62).move_to([1.9, -1.15, 0])
        ls = label("all Re λ < 0:\nasymptotically stable", 20, GREEN_C).next_to(sp, LEFT, buff=0.3).shift(0.2 * DOWN)
        lu = label("any Re λ > 0:\nunstable", 20, RED_C).next_to(sp, RIGHT, buff=0.3).shift(0.2 * DOWN)
        lb = label("on the imaginary axis: needs more analysis", 18, GREEN_C).next_to(sp, DOWN, buff=0.12)
        ev = label("eigenvalues of A − BK, not of A", 24, FG).move_to([2.5, 1.15, 0])
        self.play(FadeOut(VGroup(note, law, br, brl, wrong, strikes, wl)),
                  e3.animate.scale(0.7).move_to([0, 2.75, 0]), self.chip("closed-loop matrix"), run_time=0.9)
        self.play(TransformFromCopy(e3.span("A", "K"), acl.span("A", "K"), path_arc=0.4), FadeIn(acl.ks("Acl", "=")), run_time=1.3)
        self.play(FadeIn(sp), FadeIn(ev), run_time=0.8)
        self.play(FadeIn(ls, shift=0.1 * RIGHT), FadeIn(lu, shift=0.1 * LEFT), FadeIn(lb), run_time=0.8)
        self.step_done(e3, acl, sp, ls, lu, lb, ev)


# ======================================================================== Section 6

class PendulumPolesSequence(ControlScene):
    SEQ_ID = "pendulum-poles"

    def construct(self):
        SZ = 0.9
        A = Mat([["0", "1"], ["1", "0"]], size=SZ)
        B = Mat([["0"], ["1"]], size=SZ, colors={"0": BLUE_C, "1": BLUE_C})
        K = Mat([["4", "4"]], size=SZ, colors={"4": YELLOW_C})
        given = place_row(Mx("A", "=", size=SZ), A, Mx(",", size=SZ), Mx("B", "=", size=SZ), B, Mx(",", size=SZ),
                          Mx("K", "=", size=SZ), K, buff=0.18).move_to([0, 2.75, 0])
        gl =label("normalized inverted pendulum (g/L = 1, no damping), book printed p. 328", 20, DIM)
        gl.next_to(given, DOWN, buff=0.25)
        self.start(given, gl)
        W = 1.15   # work line height

        # 1. open-loop eigenvalues
        L = ("lam", r"\lambda")
        d1 = Mx(r"\det", size=1.0)
        M1 = Mat([[L, "-1"], ["-1", L]], size=1.0)
        d2 = Mx("=", ("l2", r"\lambda\!^2"), "-", "1", "=", "0", size=1.0)
        work = place_row(d1, M1, d2, buff=0.15).move_to([-1.0, W, 0])
        roots = Mx(r"\Rightarrow", ("lam", r"\lambda"), "=", ("pm", r"\pm 1"), size=1.0).next_to(work, RIGHT, buff=0.4)
        sp = splane(xr=(-4, 2), yr=(-1.5, 1.5), unit=0.62).move_to([2.9, -1.75, 0])
        p_plus = pole_cross(RED_C).move_to(sp.p(1, 0))
        p_minus = pole_cross(FG).move_to(sp.p(-1, 0))
        ol_l = label("open loop: saddle", 20, RED_C).next_to(sp, UP, buff=0.12)
        self.play(FadeOut(gl), self.chip("det(λI − A)"), run_time=0.4)
        self.play(FadeIn(d1), FadeIn(M1.lb), FadeIn(M1.rb),
                  TransformFromCopy(A.e[0][1], M1.e[0][1]), TransformFromCopy(A.e[1][0], M1.e[1][0]),
                  FadeIn(M1.e[0][0]), FadeIn(M1.e[1][1]), run_time=1.3)
        self.play(Write(d2), run_time=0.9)
        self.play(Write(roots), FadeIn(sp), run_time=0.9)
        self.play(TransformFromCopy(roots.k("pm"), p_plus), TransformFromCopy(roots.k("pm"), p_minus), FadeIn(ol_l), run_time=1.0)
        board1 = Mx(("lam", r"\lambda"), "=", "+1", ",", "-1", size=0.7).move_to([-4.9, -1.3, 0])
        b1l = label("open loop", 18, RED_C).next_to(board1, UP, buff=0.15)
        self.play(TransformFromCopy(VGroup(roots.k("lam"), roots.k("pm")), board1), FadeIn(b1l), run_time=0.8)
        self.step_done(given, work, roots, sp, p_plus, p_minus, ol_l, board1, b1l)

        # 2. BK as column times row
        Bc = Mat([["0"], ["1"]], size=1.0, colors={"0": BLUE_C, "1": BLUE_C})
        Kc = Mat([["4", "4"]], size=1.0, colors={"4": YELLOW_C})
        pc = {"b": BLUE_C, "k": YELLOW_C}
        P = Mat([[Mx(("b", bi), r"\cdot", ("k", "4"), colors=pc) for _ in range(2)] for bi in ("0", "1")], size=1.0)
        bk_row = place_row(Mx("B", "K", "=", size=1.0), Bc, Kc, Mx("=", size=1.0), P, buff=0.18).move_to([-1.2, W, 0])
        self.play(FadeOut(VGroup(work, roots)), self.chip("column × row"), run_time=0.5)
        self.play(FadeIn(bk_row[0]), TransformFromCopy(B, Bc), TransformFromCopy(K, Kc), FadeIn(bk_row[3]), run_time=1.2)
        self.play(FadeIn(P.lb), FadeIn(P.rb), *[
            AnimationGroup(TransformFromCopy(Bc.e[i][0], P.e[i][j].k("b"), path_arc=-0.3),
                           TransformFromCopy(Kc.e[0][j], P.e[i][j].k("k"), path_arc=0.3),
                           FadeIn(P.e[i][j].k(r"\cdot")))
            for i in range(2) for j in range(2)], run_time=1.6)
        R = Mat([["0", "0"], ["4", "4"]], size=1.0)
        R.move_to(P).align_to(P, LEFT)
        self.play(*[ReplacementTransform(P.e[i][j], R.e[i][j]) for i in range(2) for j in range(2)],
                  ReplacementTransform(P.lb, R.lb), ReplacementTransform(P.rb, R.rb), run_time=1.0)
        self.settle(given, sp, p_plus, p_minus, ol_l, board1, b1l, bk_row[:4], R)
        board2 = place_row(Mx("B", "K", "=", size=0.7), Mat([["0", "0"], ["4", "4"]], size=0.7), buff=0.12)
        board2.move_to([-1.9, -1.3, 0])
        self.play(TransformFromCopy(VGroup(bk_row[0], R), board2), run_time=0.9)
        self.step_done(given, sp, p_plus, p_minus, ol_l, board1, b1l, board2, bk_row[:4], R)

        # 3. A - BK entry by entry
        av = [["0", "1"], ["1", "0"]]
        bv = [["0", "0"], ["4", "4"]]
        D = Mat([[Mx(("a", av[i][j]), "-", ("bk", bv[i][j]), colors={"bk": YELLOW_C}) for j in range(2)] for i in range(2)],
                size=1.0)
        lhs3 = Mx("A", "-", "B", "K", "=", size=1.0)
        res3 = Mat([["0", "1"], ["-3", "-4"]], size=1.0)
        row3 = place_row(lhs3, D, Mx("=", size=1.0), res3, buff=0.18).move_to([-1.2, W, 0])
        self.play(FadeOut(VGroup(bk_row[:4], R)), self.chip("entry by entry"), run_time=0.5)
        self.play(FadeIn(lhs3), FadeIn(D.lb), FadeIn(D.rb), run_time=0.5)
        self.play(*[TransformFromCopy(A.e[i][j], D.e[i][j].k("a"), path_arc=0.3) for i in range(2) for j in range(2)],
                  run_time=1.0)
        bkm = board2[1]
        self.play(*[TransformFromCopy(bkm.e[i][j], D.e[i][j].k("bk"), path_arc=-0.3) for i in range(2) for j in range(2)],
                  *[FadeIn(D.e[i][j].k("-")) for i in range(2) for j in range(2)], run_time=1.0)
        self.play(FadeIn(row3[2]), FadeIn(res3.lb), FadeIn(res3.rb),
                  *[TransformFromCopy(D.e[i][j], res3.e[i][j]) for i in range(2) for j in range(2)], run_time=1.2)
        board3 = place_row(Mx(("Acl", r"A_{\mathrm{cl}}"), "=", size=0.7), Mat([["0", "1"], ["-3", "-4"]], size=0.7), buff=0.12)
        board3.move_to([-4.9, -2.55, 0])
        meaning = VGroup(Mx(THDD, "=", "-3", TH, "-", "4", THD, size=0.75, colors=TEAL_KEYS),
                         label("spring and damping made by feedback", 20, GREEN_C)).arrange(RIGHT, buff=0.3)
        meaning.next_to(row3, DOWN, buff=0.3)
        self.play(TransformFromCopy(res3, board3[1]), FadeIn(board3[0]), FadeIn(meaning), run_time=0.9)
        self.step_done(given, sp, p_plus, p_minus, ol_l, board1, b1l, board2, board3, row3, meaning)

        # 4. characteristic polynomial
        L2 = ("lam", r"\lambda")
        M4 = Mat([[L2, "-1"], ["3", ("lp4", r"\lambda+4")]], size=1.0)
        c1 = place_row(Mx(r"\det", size=1.0), M4, Mx("=", ("lam", r"\lambda"), "(", ("lam2", r"\lambda"), "+", "4", ")", "+", "3",
                                                     size=1.0), buff=0.15).move_to([-1.2, W + 0.05, 0])
        c2 = Mx("=", ("l2", r"\lambda\!^2"), "+", ("4l", r"4\lambda"), "+", "3", "=", "(", r"\lambda", "+", ("one", "1"), ")",
                "(", ("lam3", r"\lambda"), ("+3", "+"), ("three", "3"), ")", size=1.0)
        c2.move_to([-0.4, W - 1.2, 0])
        self.play(FadeOut(VGroup(row3, meaning)), self.chip("det(λI − A_cl)"), run_time=0.5)
        self.play(FadeIn(c1[0]), FadeIn(M4.lb), FadeIn(M4.rb), FadeIn(M4.cells), run_time=1.0)
        diag = VGroup(hbox(M4.e[0][0], YELLOW_C, 0.05), hbox(M4.e[1][1], YELLOW_C, 0.05))
        off = VGroup(hbox(M4.e[0][1], BLUE_C, 0.05), hbox(M4.e[1][0], BLUE_C, 0.05))
        self.play(ShowCreation(diag), run_time=0.4)
        self.play(TransformFromCopy(M4.e[0][0], c1[2].k("lam")), TransformFromCopy(M4.e[1][1], c1[2].span("(", ")")),
                  FadeIn(c1[2].k("=")), run_time=1.1)
        self.play(ReplacementTransform(diag, off), run_time=0.4)
        self.play(TransformFromCopy(VGroup(M4.e[0][1], M4.e[1][0]), VGroup(c1[2].k("+", 1), c1[2].k("3"))), run_time=1.0)
        self.play(FadeOut(off), Write(c2), run_time=1.6)
        board4 = Mx(("lam", r"\lambda"), "=", "-1", ",", "-3", size=0.7).move_to([-1.9, -2.55, 0])
        b4l = label("closed loop", 18, GREEN_C).next_to(board4, UP, buff=0.15)
        self.play(TransformFromCopy(VGroup(c2.k("one"), c2.k("three")), board4), FadeIn(b4l), run_time=0.9)
        self.step_done(given, sp, p_plus, p_minus, ol_l, board1, b1l, board2, board3, board4, b4l, c1, c2)

        # 5. the poles move; responses compare
        self.play(FadeOut(VGroup(c1, c2, board2, board3)), self.chip("open loop vs closed loop"),
                  VGroup(board4, b4l).animate.move_to([-4.9, -2.4, 0]), run_time=0.7)
        sp2 = splane(xr=(-4, 2), yr=(-1.5, 1.5), unit=0.72).move_to([0.2, 0.9, 0])
        self.play(ReplacementTransform(sp, sp2), p_plus.animate.move_to(sp2.p(1, 0)), p_minus.animate.move_to(sp2.p(-1, 0)),
                  FadeOut(ol_l), run_time=0.9)
        ghost = VGroup(pole_cross(RED_C, width=3).move_to(sp2.p(1, 0)), pole_cross(FG, width=3).move_to(sp2.p(-1, 0)))
        ghost.set_opacity(0.35)
        self.add(ghost)
        for pole, x in ((p_plus, -1), (p_minus, -3)):
            pole.generate_target()
            pole.target.move_to(sp2.p(x, 0)).set_color(GREEN_C)
        self.play(MoveToTarget(p_plus, path_arc=-0.9), MoveToTarget(p_minus, path_arc=-0.9), run_time=1.8)
        mv = VGroup(Mx(r"\{", "+1", ",", "-1", r"\}", size=0.8, color=RED_C), Mx(r"\longrightarrow", size=0.8),
                    Mx(r"\{", "-1", ",", "-3", r"\}", size=0.8, color=GREEN_C)).arrange(RIGHT, buff=0.2)
        mv.next_to(sp2, DOWN, buff=0.22)
        plot = Plot(t_max=5, y_min=-0.05, y_max=0.3, width=4.2, height=1.8, y_label="θ(t)").move_to([0.6, -2.3, 0])
        th0 = 0.1
        op = plot.curve(lambda t: th0 * np.cosh(t), color=RED_C)
        clc = plot.curve(lambda t: th0 * (1.5 * np.exp(-t) - 0.5 * np.exp(-3 * t)), color=GREEN_C)
        ol_lab = label("open loop: leaves the plotted range", 18, RED_C).next_to(plot, RIGHT, buff=0.2).shift(0.5 * UP)
        cl_lab = label("closed loop: decays", 18, GREEN_C).next_to(ol_lab, DOWN, buff=0.25, aligned_edge=LEFT)
        ic = label("θ(0) = 0.1 rad, θ̇(0) = 0", 18, DIM).next_to(cl_lab, DOWN, buff=0.25, aligned_edge=LEFT)
        self.play(FadeIn(mv), FadeIn(plot), run_time=0.6)
        self.play(ShowCreation(op, rate_func=linear), ShowCreation(clc, rate_func=linear), run_time=1.8)
        self.play(FadeIn(ol_lab), FadeIn(cl_lab), FadeIn(ic), run_time=0.6)
        self.step_done(given, board1, b1l, board4, b4l, sp2, ghost, p_plus, p_minus, mv, plot, op, clc,
                       ol_lab, cl_lab, ic)

        # 6. recap chain and next steps
        stuff = VGroup(given, board1, b1l, board4, b4l, sp2, ghost, p_plus, p_minus, mv, plot, op, clc,
                       ol_lab, cl_lab, ic)
        boxes = [("model", Mx(XD, "=", "A", "x", "+", "B", "u", size=0.75), TEAL_C),
                 ("feedback law", Mx("u", "=", "-", "K", "x", size=0.75), YELLOW_C),
                 ("closed loop", Mx(XD, "=", "(", "A", "-", "B", "K", ")", "x", size=0.75), BLUE_C),
                 ("stability", label("eigenvalues of A − BK", 20, FG), GREEN_C)]
        chain = VGroup()
        for name, content, color in boxes:
            ttl = label(name, 18, color, weight=BOLD)
            inner = VGroup(ttl, content).arrange(DOWN, buff=0.18)
            fr = RoundedRectangle(width=max(inner.get_width() + 0.4, 2.6), height=1.35, corner_radius=0.14)
            fr.set_stroke(color, 2.5).set_fill(BG, 1)
            inner.move_to(fr)
            chain.add(VGroup(fr, inner))
        chain.arrange(RIGHT, buff=0.5).move_to([0, 1.3, 0])
        if chain.get_width() > 13.4:
            chain.set_width(13.4)
        arrows = VGroup(*[arrow(chain[i].get_right() + 0.04 * RIGHT, chain[i + 1].get_left() + 0.04 * LEFT, DIM, 3)
                          for i in range(3)])
        nxt = label("next in the bootcamp", 22, DIM).move_to([0, -0.55, 0])
        nexts = VGroup(*[node(t, FAINT, 22) for t in ("controllability: can K place every eigenvalue?",
                                                      "LQR: choosing a good K",
                                                      "estimation: Kalman filter when y = Cx")])
        nexts.arrange(DOWN, buff=0.25).next_to(nxt, DOWN, buff=0.3)
        self.play(FadeOut(stuff, shift=0.2 * DOWN), self.chip(), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(c, shift=0.2 * RIGHT) for c in chain], lag_ratio=0.35),
                  LaggedStart(*[ShowCreation(a) for a in arrows], lag_ratio=0.35), run_time=2.0)
        self.play(FadeIn(nxt), LaggedStart(*[FadeIn(n_, shift=0.1 * UP) for n_ in nexts], lag_ratio=0.3), run_time=1.2)
        self.step_done(chain, arrows, nxt, nexts)
