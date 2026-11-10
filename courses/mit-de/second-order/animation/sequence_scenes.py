"""ManimGL scenes for Unit 3, Second Order Equations (one scene per sequence in control_specs).

Colour code: y and responses teal, inputs blue, frequencies/roots yellow, null parts pink,
results green, blow-ups and resonance red. Formulas use matplotlib mathtext (no \\tfrac, \\text, \\Big).
Stage bounds: content stays within |x| <= 6.3 and -2.8 <= y <= 3.3 (chip sits bottom-left).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"y": TEAL_C, "w": YELLOW_C, "in": BLUE_C, "res": GREEN_C, "Y": GREEN_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def note(text, y, color=DIM, size=24, x=0.0):
    return label(text, size, color).move_to([x, y, 0])


class XPlot(Plot):
    """Plot whose horizontal variable runs over [x0, x1]; xcurve clips to the y-range piecewise."""
    def __init__(self, x0, x1, y_min, y_max, width, height, x_label="x", y_label=None):
        self.x0 = x0
        super().__init__(t_max=x1 - x0, y_min=y_min, y_max=y_max, width=width, height=height,
                         t_label=x_label, y_label=y_label)
        self[3].set_stroke(FAINT, 1)
        if x0 < 0 < x1:
            self.add(Line(self.xp(0, y_min), self.xp(0, y_max)).set_stroke(DIM, 2))

    def xp(self, x, y):
        return self.c2p(x - self.x0, y)

    def xcurve(self, f, color=TEAL_C, width=4, n=300):
        x1 = self.x0 + self.t_max
        segs, cur = [], []
        for x in np.linspace(self.x0, x1, n):
            y = float(f(x))
            if np.isfinite(y) and self.y_min <= y <= self.y_max:
                cur.append(self.xp(x, y))
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


# ======================================================================== Section 1

class FreeOscillationSequence(ControlScene):
    SEQ_ID = "free-oscillation"

    def construct(self):
        e0 = M(("ypp", "y''"), "+", ("w", r"\omega_n^2"), ("y", "y"), "=", "0", size=1.2).move_to([-3.2, 2.7, 0])
        ic = M(("ic", r"\omega_n = 2,\ y(0) = 1,\ y'(0) = 2"), size=0.75, colors={"ic": DIM}).move_to([-3.2, 1.95, 0])
        self.start(e0, ic)

        # 1. cos and sin
        c = M(("c", r"(\cos\omega_n t)''"), "=", ("m", r"-\omega_n^2"), ("cc", r"\cos\omega_n t"), size=0.85,
              colors={"m": YELLOW_C}).move_to([-3.2, 1.0, 0])
        s = M(("c", r"(\sin\omega_n t)''"), "=", ("m", r"-\omega_n^2"), ("cc", r"\sin\omega_n t"), size=0.85,
              colors={"m": YELLOW_C}).move_to([-3.2, 0.2, 0])
        self.play(self.chip("two derivatives bring out -wn^2"), run_time=0.5)
        self.play(Write(c), run_time=1.1)
        self.play(Write(s), run_time=1.1)
        self.play(Indicate(c.k("m"), color=YELLOW_C), Indicate(s.k("m"), color=YELLOW_C), Indicate(e0.k("w"), color=YELLOW_C), run_time=0.8)
        self.step_done(e0, ic, c, s)

        # 2. match initial conditions
        y1 = M(("y", "y"), "=", ("c1", "y(0)"), r"\cos\omega_n t", "+", ("c2", r"\frac{y'(0)}{\omega_n}"), r"\sin\omega_n t",
               size=0.85, colors={"c1": PINK_C, "c2": PINK_C}).move_to([-3.0, -0.8, 0])
        y2 = M(("y", "y"), "=", ("c1", r"\cos 2t"), "+", ("c2", r"\sin 2t"), size=0.95).move_to([-3.0, -1.7, 0])
        self.play(self.chip("t = 0 fixes c1 and c2"), run_time=0.5)
        self.play(TransformFromCopy(VGroup(c.k("cc"), s.k("cc")), y1), run_time=1.3)
        self.play(TransformFromCopy(y1, y2), run_time=1.1)
        self.step_done(e0, ic, c, s, y1, y2)

        # 3. polar form and the graph
        p = Plot(t_max=2 * np.pi, y_min=-1.6, y_max=1.6, width=5.0, height=3.6, t_label="t", y_label="y").move_to([3.4, 0.6, 0])
        curve = p.curve(lambda t: np.cos(2 * t) + np.sin(2 * t), color=TEAL_C, width=5)
        env = VGroup(DashedLine(p.c2p(0, np.sqrt(2)), p.c2p(2 * np.pi, np.sqrt(2))).set_stroke(GREEN_C, 2),
                     DashedLine(p.c2p(0, -np.sqrt(2)), p.c2p(2 * np.pi, -np.sqrt(2))).set_stroke(GREEN_C, 2))
        y3 = M("=", ("R", r"\sqrt{2}"), ("c", r"\cos\left(2t - \frac{\pi}{4}\right)"), size=0.95,
               colors={"R": GREEN_C}).next_to(y2, DOWN, buff=0.25).align_to(y2, LEFT).shift(0.6 * RIGHT)
        self.play(self.chip("R = sqrt(c1^2 + c2^2), tan a = c2/c1"), FadeIn(p), run_time=0.7)
        self.play(ShowCreation(curve), run_time=1.6)
        self.play(Write(y3), ShowCreation(env), run_time=1.1)
        self.step_done(e0, ic, c, s, y1, y2, p, curve, env, y3)


# ======================================================================== Section 2

class ForcedCosineSequence(ControlScene):
    SEQ_ID = "forced-cosine"

    def construct(self):
        e0 = M(("m", "m"), ("ypp", "y''"), "+", ("k", "k"), ("y", "y"), "=", ("in", r"\cos\omega t"), size=1.2).move_to([0, 2.7, 0])
        self.start(e0)

        # 1. substitute
        e1 = M(("a", r"-m\omega^2 Y"), ("c1", r"\cos\omega t"), "+", ("b", "kY"), ("c2", r"\cos\omega t"), "=",
               ("in", r"\cos\omega t"), size=1.0, colors={"a": YELLOW_C, "b": TEAL_C}).move_to([0, 1.6, 0])
        self.play(self.chip("y = Y cos wt"), run_time=0.5)
        self.play(TransformFromCopy(e0, e1), run_time=1.4)
        self.play(*[Indicate(e1.k(k), color=BLUE_C) for k in ("c1", "c2", "in")], run_time=0.8)
        self.step_done(e0, e1)

        # 2. match
        e2 = M(("Y", "Y"), "=", ("f", r"\frac{1}{k - m\omega^2}"), "=", ("g", r"\frac{1}{m(\omega_n^2 - \omega^2)}"),
               size=1.05, colors={"g": GREEN_C}).move_to([0, 0.4, 0])
        self.play(self.chip("cancel cos wt, use k = m wn^2"), run_time=0.5)
        self.play(TransformFromCopy(e1.ks("a", "b"), e2.k("f")), FadeIn(e2.ks("Y", "=")), run_time=1.3)
        self.play(FadeIn(e2.all("=")[1]), TransformFromCopy(e2.k("f"), e2.k("g")), run_time=1.1)
        self.step_done(e0, e1, e2)

        # 3. graph of Y(omega) for m = 1, omega_n = 1
        p = XPlot(0, 2.5, -3, 3, width=6.0, height=2.8, x_label="ω", y_label="Y").move_to([0, -1.35, 0])
        cur = p.xcurve(lambda w: 1 / (1 - w * w) if abs(1 - w * w) > 1e-6 else np.nan, color=GREEN_C, width=4)
        asym = DashedLine(p.xp(1, -3), p.xp(1, 3)).set_stroke(RED_C, 3)
        lab = label("ω = ωn: resonance", 20, RED_C).next_to(p.xp(1, 3), UP, buff=0.05).shift(0.9 * RIGHT)
        self.play(self.chip("frequency response, m = 1, wn = 1"), FadeOut(e1), e2.animate.move_to([0, 1.6, 0]), run_time=0.8)
        self.play(FadeIn(p), run_time=0.5)
        self.play(ShowCreation(cur), run_time=1.8)
        self.play(ShowCreation(asym), FadeIn(lab), run_time=0.8)
        self.step_done(e0, e2, p, cur, asym, lab)


# ======================================================================== Section 3

class DampingRootsSequence(ControlScene):
    SEQ_ID = "damping-roots"

    def construct(self):
        p = XPlot(-3, 1, -1.5, 3, width=6.0, height=4.4, x_label="s", y_label="s²+2s+C").move_to([-2.7, 0.2, 0])
        e0 = M(("s", "s^2 + 2s + C"), "=", "0", size=1.0).move_to([3.4, 2.7, 0])
        self.start(p, e0)

        def par(C):
            return p.xcurve(lambda s: s * s + 2 * s + C, color=TEAL_C, width=5)

        # 1. C = 0
        c0 = par(0)
        r0 = VGroup(Dot(p.xp(0, 0), radius=0.09).set_fill(YELLOW_C), Dot(p.xp(-2, 0), radius=0.09).set_fill(YELLOW_C))
        t0 = M(("a", "C = 0:"), ("b", "s(s + 2)"), size=0.85).move_to([3.4, 1.7, 0])
        l0 = label("two real roots: overdamped", 20, YELLOW_C).move_to([3.4, 1.15, 0])
        self.play(self.chip("C = 0"), ShowCreation(c0), run_time=1.2)
        self.play(GrowFromCenter(r0), Write(t0), FadeIn(l0), run_time=0.9)
        self.step_done(p, e0, c0, r0, t0, l0)

        # 2. C = 1
        c1 = par(1)
        r1 = Dot(p.xp(-1, 0), radius=0.11).set_fill(GREEN_C)
        t1 = M(("a", "C = 1:"), ("b", "(s + 1)^2"), size=0.85).move_to([3.4, 0.4, 0])
        l1 = label("double root: critical", 20, GREEN_C).move_to([3.4, -0.15, 0])
        self.play(self.chip("raise by 1"), ReplacementTransform(c0, c1), ReplacementTransform(r0, r1), run_time=1.4)
        self.play(Write(t1), FadeIn(l1), run_time=0.9)
        self.step_done(p, e0, c1, r1, t1, l1, t0, l0)

        # 3. C = 2
        c2 = par(2)
        gap = DashedLine(p.xp(-1, 0), p.xp(-1, 1)).set_stroke(RED_C, 3)
        t2 = M(("a", "C = 2:"), ("b", r"s = -1 \pm i"), size=0.85, colors={"b": PINK_C}).move_to([3.4, -0.9, 0])
        l2 = label("no real roots: underdamped", 20, PINK_C).move_to([3.4, -1.45, 0])
        self.play(self.chip("raise again"), ReplacementTransform(c1, c2), FadeOut(r1), run_time=1.4)
        self.play(ShowCreation(gap), Write(t2), FadeIn(l2), run_time=1.0)
        self.step_done(p, e0, c2, gap, t0, l0, t1, l1, t2, l2)

        # 4. classification table
        tab = VGroup(
            label("B² > 4AC   overdamped", 22, YELLOW_C),
            label("B² = 4AC   critical", 22, GREEN_C),
            label("B² < 4AC   underdamped", 22, PINK_C),
            label("B = 0        undamped", 22, BLUE_C)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([3.4, -0.4, 0])
        self.play(self.chip("sign of B^2 - 4AC"), FadeOut(VGroup(t0, l0, t1, l1, t2, l2)), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(m, shift=0.1 * RIGHT) for m in tab], lag_ratio=0.3), run_time=1.4)
        self.step_done(p, e0, c2, gap, tab)


# ======================================================================== Section 4

class ImpulseStepSequence(ControlScene):
    SEQ_ID = "impulse-step"

    def construct(self):
        e0 = M(("P", "y'' + 3y' + 2y"), ",", ("r", r"s_1 = -1,\ s_2 = -2"), size=0.95,
               colors={"r": YELLOW_C}).move_to([0, 2.8, 0])
        p = Plot(t_max=6, y_min=-0.05, y_max=0.6, width=6.2, height=3.8, t_label="t").move_to([-2.4, -0.5, 0])
        self.start(e0, p)

        # 1. g
        g = lambda t: np.exp(-t) - np.exp(-2 * t)
        e1 = M(("g", "g"), "=", ("f", r"\frac{e^{s_1t} - e^{s_2t}}{s_1 - s_2}"), "=", ("v", r"e^{-t} - e^{-2t}"),
               size=0.9, colors={"g": TEAL_C, "v": TEAL_C}).move_to([3.5, 1.7, 0])
        cg = p.curve(g, color=TEAL_C, width=5)
        sl = Line(p.c2p(0, 0), p.c2p(0.35, 0.35)).set_stroke(YELLOW_C, 3)
        sll = label("g(0) = 0, g'(0) = 1", 20, YELLOW_C).move_to([3.5, 0.75, 0])
        self.play(self.chip("difference of exponentials"), Write(e1), run_time=1.3)
        self.play(ShowCreation(cg), ShowCreation(sl), FadeIn(sll), run_time=1.5)
        self.step_done(e0, p, e1, cg, sl, sll)

        # 2. area under g
        ts = np.linspace(0, 6, 120)
        area = Polygon(*([p.c2p(0, 0)] + [p.c2p(t, g(t)) for t in ts] + [p.c2p(6, 0)]))
        area.set_fill(TEAL_C, 0.25).set_stroke(width=0)
        e2 = M(("r", "r(t)"), "=", ("i", r"\int_0^t g(s)\,ds"), size=0.95, colors={"r": GREEN_C}).move_to([3.5, -0.2, 0])
        self.play(self.chip("step = integral of delta"), FadeOut(VGroup(sl, sll)), run_time=0.5)
        self.play(FadeIn(area), Write(e2), run_time=1.4)
        self.step_done(e0, p, e1, cg, area, e2)

        # 3. r(t)
        r = lambda t: 0.5 - np.exp(-t) + 0.5 * np.exp(-2 * t)
        cr = p.curve(r, color=GREEN_C, width=5)
        lim = DashedLine(p.c2p(0, 0.5), p.c2p(6, 0.5)).set_stroke(GREEN_C, 2)
        e3 = M(("r", "r"), "=", ("v", r"\frac{1}{2} - e^{-t} + \frac{1}{2}e^{-2t}"), size=0.9,
               colors={"r": GREEN_C}).move_to([3.5, -1.2, 0])
        e4 = label("settles at 1/C = 1/2", 20, GREEN_C).move_to([3.5, -2.0, 0])
        self.play(self.chip("accumulate the area"), run_time=0.5)
        self.play(ShowCreation(cr), Write(e3), run_time=1.6)
        self.play(ShowCreation(lim), FadeIn(e4), run_time=0.8)
        self.step_done(e0, p, e1, cg, area, e2, cr, lim, e3, e4)


# ======================================================================== Section 5

class ResonanceLimitSequence(ControlScene):
    SEQ_ID = "resonance-limit"

    def construct(self):
        e0 = M(("P", "P(D)y"), "=", ("in", "e^{st}"), ",", ("yp", "y_p"), "=", ("f", r"\frac{e^{st}}{P(s)}"),
               size=1.1).move_to([0, 2.7, 0])
        self.start(e0)

        # 1. subtract a null solution
        e1 = M(("y", "y"), "=", ("f", r"\frac{e^{st} - e^{s_1t}}{P(s)}"), size=1.2).move_to([0, 1.45, 0])
        n1 = label("e^(s1 t) is a null solution: P(D) e^(s1 t) = 0", 20, PINK_C).move_to([0, 0.6, 0])
        self.play(self.chip("subtract a null solution"), TransformFromCopy(e0.k("f"), e1.k("f")), FadeIn(e1.ks("y", "=")), run_time=1.4)
        self.play(FadeIn(n1), run_time=0.6)
        self.step_done(e0, e1, n1)

        # 2. 0/0
        e2 = M(("q", r"\frac{e^{s_1t} - e^{s_1t}}{P(s_1)}"), "=", ("z", r"\frac{0}{0}"), size=1.1,
               colors={"z": RED_C}).move_to([0, -0.4, 0])
        self.play(self.chip("s -> s1"), FadeOut(n1), run_time=0.5)
        self.play(TransformFromCopy(e1.k("f"), e2.k("q")), run_time=1.2)
        self.play(FadeIn(e2.ks("=", "z")), run_time=0.7)
        self.step_done(e0, e1, e2)

        # 3. l'Hopital
        e3 = M(("yp", "y_p"), "=", ("n", r"\frac{t\,e^{s_1t}}{P'(s_1)}"), size=1.3, colors={"n": GREEN_C}).move_to([-1.6, -1.75, 0])
        d = M(("d", r"\partial_s\, e^{st} = t\,e^{st}"), size=0.85, colors={"d": YELLOW_C}).move_to([3.3, -1.75, 0])
        self.play(self.chip("differentiate top and bottom in s"), Write(d), run_time=1.0)
        self.play(TransformFromCopy(e2.k("q"), e3.k("n")), FadeIn(e3.ks("yp", "=")), run_time=1.4)
        box = hbox(e3, GREEN_C)
        self.play(ShowCreation(box), run_time=0.6)
        self.step_done(e0, e1, e2, e3, d, box)


# ======================================================================== Section 6

class GainPhaseSequence(ControlScene):
    SEQ_ID = "gain-phase"

    def construct(self):
        e0 = M(("e", "y'' + y' + 2y"), "=", ("in", r"\cos t"), size=1.1).move_to([-3.0, 2.7, 0])
        self.start(e0)

        # 1. M and N
        e1 = M(("D", "D = 1^2 + 1^2 = 2"), size=0.85).move_to([-3.0, 1.8, 0])
        e2 = M(("M", r"M = \frac{1}{2}"), ",", ("N", r"N = \frac{1}{2}"), size=0.95,
               colors={"M": TEAL_C, "N": PINK_C}).move_to([-3.0, 0.95, 0])
        self.play(self.chip("C - A w^2 = 1, B w = 1"), Write(e1), run_time=1.0)
        self.play(TransformFromCopy(e1, e2), run_time=1.2)
        self.step_done(e0, e1, e2)

        # 2. the vector (M, N)
        o = np.array([1.2, -0.6, 0])
        u = 3.2
        ax = VGroup(Line(o + 0.3 * LEFT, o + 2.4 * RIGHT).set_stroke(DIM, 2), Line(o + 0.3 * DOWN, o + 2.4 * UP).set_stroke(DIM, 2))
        mx = Line(o, o + 0.5 * u * RIGHT).set_stroke(TEAL_C, 5)
        ny = Line(o + 0.5 * u * RIGHT, o + 0.5 * u * (RIGHT + UP)).set_stroke(PINK_C, 5)
        vec = arrow(o, o + 0.5 * u * (RIGHT + UP), color=GREEN_C, width=5)
        ang = Arc(radius=0.6, start_angle=0, angle=PI / 4, arc_center=o).set_stroke(YELLOW_C, 3)
        al = label("α = π/4", 22, YELLOW_C).move_to(o + 0.95 * RIGHT + 0.3 * UP)
        gl = label("G = 1/√2", 22, GREEN_C).move_to(o + 0.35 * u * (RIGHT + UP) + 0.55 * LEFT + 0.25 * UP)
        e3 = M(("G", r"G = \sqrt{M^2 + N^2}"), size=0.85, colors={"G": GREEN_C}).move_to([-3.0, -0.1, 0])
        self.play(self.chip("length and angle of (M, N)"), FadeIn(ax), run_time=0.5)
        self.play(TransformFromCopy(e2.k("M"), mx), run_time=0.9)
        self.play(TransformFromCopy(e2.k("N"), ny), run_time=0.9)
        self.play(grow_arrow(vec), ShowCreation(ang), FadeIn(al), FadeIn(gl), Write(e3), run_time=1.3)
        self.step_done(e0, e1, e2, ax, mx, ny, vec, ang, al, gl, e3)

        # 3. input vs response
        p = Plot(t_max=4 * np.pi, y_min=-1.1, y_max=1.1, width=6.0, height=1.9, t_label="t").move_to([-3.0, -1.9, 0])
        cin = p.curve(lambda t: np.cos(t), color=BLUE_C, width=3)
        cout = p.curve(lambda t: np.cos(t - np.pi / 4) / np.sqrt(2), color=GREEN_C, width=5)
        e4 = M(("y", "y_p"), "=", ("v", r"\frac{1}{\sqrt{2}}\cos\left(t - \frac{\pi}{4}\right)"), size=0.9,
               colors={"v": GREEN_C}).move_to([3.4, -2.3, 0])
        self.play(self.chip("smaller by G, later by a"), FadeOut(e3), run_time=0.5)
        self.play(FadeIn(p), ShowCreation(cin), run_time=1.0)
        self.play(ShowCreation(cout), Write(e4), run_time=1.5)
        self.step_done(e0, e1, e2, ax, mx, ny, vec, ang, al, gl, p, cin, cout, e4)
