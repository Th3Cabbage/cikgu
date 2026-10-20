"""Short explanatory ManimGL scenes, rendered offscreen and embedded in the browser guide.

Render from the repository root (see README.md):
    .\\.venv\\Scripts\\manimgl.exe courses\\ode\\native\\explanation_scenes.py CharacteristicEquation -w -m --video_dir media
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *  # noqa: E402,F403

import ode_math  # noqa: E402

PAPER = "#FBF7EE"
NAVY = "#1F2A44"
TEAL = "#0F8B8D"
BLUE = "#2B6CB0"
CORAL = "#C8553D"
MUTED = "#5B6475"
FONT = "Segoe UI"


def label(s, size=28, color=NAVY, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, weight=weight).set_color(color)


class PaperScene(Scene):
    default_camera_config = dict(background_color=PAPER)

    def title(self, s):
        t = label(s, 40, NAVY, BOLD).to_edge(UP, buff=0.45)
        rule = Line(LEFT, RIGHT).set_width(t.get_width() + 0.6).next_to(t, DOWN, buff=0.15)
        rule.set_stroke(TEAL, 3)
        return VGroup(t, rule)


class CharacteristicEquation(PaperScene):
    def construct(self):
        head = self.title("Where the characteristic equation comes from")
        self.play(FadeIn(head, shift=0.2 * DOWN))

        ode = Tex(R"a y'' + b y' + c y = 0", font_size=52).set_color(NAVY).shift(2.0 * UP)
        self.play(Write(ode))
        guess = label("Guess an exponential, since it keeps its shape:", 28, MUTED).next_to(ode, DOWN, buff=0.5)
        derivs = Tex(R"y = e^{rt}, \qquad y' = r e^{rt}, \qquad y'' = r^2 e^{rt}",
                     font_size=44, t2c={"e^{rt}": TEAL}).next_to(guess, DOWN, buff=0.3)
        derivs.set_color(NAVY)
        derivs.set_color_by_tex_to_color_map({"e^{rt}": TEAL})
        self.play(FadeIn(guess), Write(derivs))
        self.wait(1.2)

        sub = Tex(R"a r^2 e^{rt} + b r e^{rt} + c e^{rt} = 0", font_size=48).set_color(NAVY)
        sub.set_color_by_tex_to_color_map({"e^{rt}": TEAL})
        sub.next_to(derivs, DOWN, buff=0.6)
        self.play(TransformFromCopy(ode, sub))
        self.wait(1.0)

        factored = Tex(R"(a r^2 + b r + c)\, e^{rt} = 0", font_size=48).set_color(NAVY)
        factored.set_color_by_tex_to_color_map({"e^{rt}": TEAL})
        factored.move_to(sub)
        self.play(TransformMatchingTex(sub, factored))
        never = label("never zero", 26, TEAL).next_to(factored[R"e^{rt}"], DOWN, buff=0.35)
        arrow = Arrow(never.get_top(), factored[R"e^{rt}"].get_bottom(), buff=0.05).set_color(TEAL)
        self.play(FadeIn(never), GrowArrow(arrow))
        self.wait(1.2)

        char = Tex(R"a r^2 + b r + c = 0", font_size=56).set_color(NAVY)
        char.next_to(factored, DOWN, buff=0.8)
        box = SurroundingRectangle(char, buff=0.2).set_stroke(BLUE, 3)
        self.play(TransformFromCopy(factored[R"(a r^2 + b r + c)"], char), FadeOut(arrow), FadeOut(never))
        self.play(ShowCreation(box))
        self.wait(0.8)

        formula = Tex(R"r = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", font_size=44).set_color(NAVY)
        formula.next_to(box, RIGHT, buff=0.7)
        group = VGroup(char, box, formula)
        self.play(group.animate.move_to(DOWN * 2.55), FadeOut(guess, shift=UP), run_time=1)
        formula.set_x(2.6)
        VGroup(char, box).set_x(-2.6)
        self.play(Write(formula))
        note = label("Each root r gives a solution e^(rt). The sign of b² - 4ac picks the case.", 26, MUTED)
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note))
        self.wait(2.5)


class ThreeRootCases(PaperScene):
    CASES = [
        ("Distinct real", "b² > 4ac", (1, 5, 4), "y'' + 5y' + 4y = 0", R"C_1 e^{r_1 t} + C_2 e^{r_2 t}", BLUE),
        ("Repeated real", "b² = 4ac", (1, 4, 4), "y'' + 4y' + 4y = 0", R"(C_1 + C_2 t)\, e^{rt}", TEAL),
        ("Complex pair", "b² < 4ac", (1, 1, 4), "y'' + y' + 4y = 0",
         R"e^{\alpha t}(C_1 \cos \omega t + C_2 \sin \omega t)", CORAL),
    ]

    def construct(self):
        head = self.title("Three root cases, three solution shapes")
        self.play(FadeIn(head, shift=0.2 * DOWN))

        columns = []
        for i, (name, cond, (a, b, c), ode_text, basis, color) in enumerate(self.CASES):
            x = (i - 1) * 4.6
            title = label(name, 30, color, BOLD).move_to([x, 2.55, 0])
            sub = label(cond, 24, MUTED).next_to(title, DOWN, buff=0.12)

            plane = Axes(x_range=[-5, 1, 1], y_range=[-2.5, 2.5, 1], width=3.4, height=2.0,
                         axis_config=dict(stroke_color=MUTED, stroke_width=2, include_tip=False,
                                          include_ticks=True, tick_size=0.04))
            plane.move_to([x, 0.75, 0])
            re_lab = label("Re", 18, MUTED).next_to(plane.x_axis.get_right(), UP, buff=0.08)
            im_lab = label("Im", 18, MUTED).next_to(plane.y_axis.get_top(), RIGHT, buff=0.08)
            info = ode_math.analyze(a, b, c)
            dots = VGroup(*[Dot(plane.c2p(re, im), radius=0.08).set_fill(color) for re, im in info["roots"]])
            if info["case"] == "repeated":
                dots.add(Circle(radius=0.15).move_to(dots[0]).set_stroke(color, 2))

            graph_axes = Axes(x_range=[0, 8, 2], y_range=[-1.2, 1.2, 1], width=3.6, height=1.6,
                              axis_config=dict(stroke_color=MUTED, stroke_width=2, include_tip=False,
                                               tick_size=0.04))
            graph_axes.move_to([x, -1.55, 0])
            curve = graph_axes.get_graph(lambda t: ode_math.solution(t, a, b, c, 1.0, 0.0),
                                         x_range=[0, 8, 0.02]).set_stroke(color, 4)
            form = Tex(basis, font_size=26).set_color(NAVY).move_to([x, -2.85, 0])
            eq = label(ode_text, 20, MUTED).next_to(graph_axes, UP, buff=0.06)
            columns.append((VGroup(title, sub), VGroup(plane, re_lab, im_lab), dots,
                            VGroup(graph_axes, eq), curve, form))

        for heads, plane, dots, gaxes, curve, form in columns:
            self.play(FadeIn(heads), FadeIn(plane), run_time=0.6)
            self.play(LaggedStartMap(GrowFromCenter, dots), run_time=0.7)
            self.play(FadeIn(gaxes), run_time=0.4)
            self.play(ShowCreation(curve), Write(form), run_time=1.6)
            self.wait(0.6)

        caption = label("Roots on the left half of the plane mean decay.  An imaginary part means oscillation.",
                        24, NAVY).to_edge(DOWN, buff=0.18)
        self.play(FadeIn(caption))
        self.wait(3)


class Resonance(PaperScene):
    def construct(self):
        head = self.title("Resonance: forcing at the natural frequency")
        self.play(FadeIn(head, shift=0.2 * DOWN))
        eq = Tex(R"y'' + y = \sin t \qquad y_p = -\frac{t}{2}\cos t", font_size=42).set_color(NAVY)
        eq.next_to(head, DOWN, buff=0.35)
        self.play(Write(eq))

        axes = Axes(x_range=[0, 30, 5], y_range=[-16, 16, 4], width=12, height=4.6,
                    axis_config=dict(stroke_color=MUTED, stroke_width=2, include_tip=False))
        axes.add_coordinate_labels(font_size=18)
        for lab in axes.coordinate_labels.family_members_with_points():
            lab.set_color(MUTED)
        axes.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(axes))
        upper = axes.get_graph(lambda t: t / 2, x_range=[0, 30]).set_stroke(MUTED, 2)
        lower = axes.get_graph(lambda t: -t / 2, x_range=[0, 30]).set_stroke(MUTED, 2)
        envelope = VGroup(DashedVMobject(upper, num_dashes=40), DashedVMobject(lower, num_dashes=40))
        env_lab = Tex(R"\text{dashed: } y = \pm\frac{t}{2}", font_size=30).set_color(MUTED)
        env_lab.move_to(axes.c2p(5.5, 11))
        self.play(ShowCreation(envelope), FadeIn(env_lab))
        curve = axes.get_graph(lambda t: -t / 2 * math.cos(t), x_range=[0, 30, 0.02]).set_stroke(CORAL, 4)
        self.play(ShowCreation(curve), run_time=5, rate_func=linear)
        note = label("The particular solution grows without bound: undamped resonance.", 26, NAVY)
        note.next_to(eq, DOWN, buff=0.2)
        self.play(FadeIn(note))
        self.wait(2.5)
