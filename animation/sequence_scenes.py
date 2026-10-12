"""ManimGL scenes for the browser guide's animated derivations (one scene per sequence).

Rendered offscreen by build_sequences.py (see README.md). Each scene is a
single master video. `self.start()` marks the end of the still opening state and every
`self.step_done()` marks the end of one step, after a short hold, so the build script can
cut the master into one short clip per step at exact frame boundaries.

Look: near-black canvas, bright math, with consistent colours for term identities:
    teal    the exponential / power being guessed (e^{rt}, t^m, e^{-t}, ...)
    yellow  roots, exponents and values being substituted; highlights
    blue    the constants C1, C2, A, B being determined
    red     only to strike out terms that cancel
The step's relation (substitution, identity, equivalence, ...) is shown in the chip at the
bottom left, matching sequence_specs.RELATIONS.

Substring selection: ManimGL's Tex["x"] also matches letters inside command names
(the "a" and "c" of \\frac, the "m" of \\pm, the "r"s of \\Rightarrow). STex refuses any
such ambiguous selector, and any selector that matches nothing, so every highlighted or
moved part is the glyph group the author meant.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "native"))  # ode_math (read-only use)

from manimlib import *  # noqa: E402,F403
from manimlib.animation.animation import prepare_animation  # noqa: E402

import ode_math  # noqa: E402
from sequence_specs import SEQUENCES  # noqa: E402

BG = "#0B0F17"
FG = "#F4F6FB"
DIM = "#8C96AB"
TEAL_C = "#2EC4B6"
BLUE_C = "#5AA9FF"
YELLOW_C = "#FFD166"
RED_C = "#FF6B6B"
GREEN_C = "#7BD389"
UI_FONT = "Segoe UI"

HOLD = 0.35          # still frames at the end of every step (the stable final state)
SPEED = 0.7          # playback factor applied to every authored run_time (keeps steps short)
MAX_W = 12.8         # widest an equation may be (frame is 14.2 units wide)
HEADER_Y = 3.25

CHIP_WORDS = {
    "assume": ("TRY", BLUE_C),
    "substitute": ("SUBSTITUTE", YELLOW_C),
    "equal": ("REWRITE  =", BLUE_C),
    "equivalent": ("EQUIVALENT  \u21d4", TEAL_C),
    "implies": ("THEREFORE  \u21d2", TEAL_C),
    "solve": ("SOLVE", TEAL_C),
    "check": ("CHECK", GREEN_C),
}

CMD_RE = re.compile(r"\\[A-Za-z]+")


def honest_count(tex, key):
    """Occurrences of `key` in `tex` that do not start or end inside a command name."""
    cmds = [(m.start(), m.end()) for m in CMD_RE.finditer(tex)]
    n = 0
    for m in re.finditer(re.escape(key), tex):
        a, b = m.start(), m.end()
        if any(cs < a < ce or cs < b < ce for cs, ce in cmds):
            continue
        n += 1
    return n


class STex(Tex):
    """Tex with checked substring selection.

    - Refuses selectors that also match inside command names.
    - Refuses any string selection in a formula containing \\frac: there ManimGL maps the
      selected span to glyphs shifted by the fraction bar (verified with drawn boxes), so
      fraction formulas use the geometric helpers frac_bars / over / under / sym instead.
      Colour maps (t2c) are skipped on such formulas rather than misapplied.
    """
    def __init__(self, *args, **kwargs):
        self._strict = False
        super().__init__(*args, **kwargs)
        self._strict = True

    def select_parts(self, selector):
        if isinstance(selector, str) and R"\frac" in self.tex_string:
            if self._strict:
                raise ValueError(f"string selection {selector!r} inside a \\frac formula {self.tex_string!r}; "
                                 "use frac_bars/over/under/sym")
            return VGroup()
        parts = super().select_parts(selector)
        if isinstance(selector, str):
            honest = honest_count(self.tex_string, selector)
            if len(parts) != honest:
                raise ValueError(f"ambiguous selector {selector!r} in {self.tex_string!r}: "
                                 f"ManimGL found {len(parts)}, {honest} outside command names")
        return parts

    def __getitem__(self, value):
        if isinstance(value, str):
            parts = self.select_parts(value)
            if len(parts) == 0:
                raise KeyError(f"selector {value!r} not found in {self.tex_string!r}")
            return parts
        return super().__getitem__(value)


def glyphs(*mobs):
    out = []
    for m in mobs:
        out.extend(m.family_members_with_points())
    return out


def others(m, *parts):
    used = set(glyphs(*parts))
    return VGroup(*[g for g in glyphs(m) if g not in used])


def by_x(gs):
    return sorted(gs, key=lambda g: g.get_x())


def frac_bars(m):
    """Fraction bars of m, left to right: thin wide glyphs with glyphs directly above and below."""
    gs = glyphs(m)
    out = []
    for g in gs:
        if g.get_height() > 0.06 or g.get_width() < 0.2:
            continue
        half = g.get_width() / 2
        col = [o for o in gs if o is not g and abs(o.get_x() - g.get_x()) < half]
        if any(o.get_y() > g.get_y() + 0.1 for o in col) and any(o.get_y() < g.get_y() - 0.1 for o in col):
            out.append(g)
    return by_x(out)


def over(m, bar):
    """Numerator glyphs of the fraction whose bar is `bar`, left to right."""
    return by_x([g for g in glyphs(m) if g is not bar and bar.get_left()[0] <= g.get_x() <= bar.get_right()[0]
                 and g.get_y() > bar.get_y()])


def under(m, bar):
    return by_x([g for g in glyphs(m) if g is not bar and bar.get_left()[0] <= g.get_x() <= bar.get_right()[0]
                 and g.get_y() < bar.get_y()])


def quadratic_parts(q, a, b, c):
    """For r = (-b ± sqrt(b^2 - 4ac)) / (2a) drawn with \\frac: the glyph groups of the two a's,
    the two b's, the c, and the discriminant b^2 - 4ac (without the root's overline)."""
    bar = frac_bars(q)[0]
    ga, gb, gc = sym(q, a), sym(q, b), sym(q, c)
    assert len(ga) == 2 and len(gb) == 2 and len(gc) == 1, (len(ga), len(gb), len(gc))
    lo, hi = gb[1].get_left()[0] - 0.01, gc[0].get_right()[0] + 0.01
    disc = [g for g in over(q, bar) if lo <= g.get_x() <= hi and not (g.get_height() < 0.06 and g.get_width() > 0.6)]
    return VGroup(*ga), VGroup(*gb), VGroup(*gc), VGroup(*disc)


def after_pm(m):
    """Numerator glyphs to the right of the ± sign (for (-b ± ...)/2a), including any root sign."""
    bar = frac_bars(m)[0]
    pm = sym(m, R"\pm")[0]
    return VGroup(*[g for g in over(m, bar) if g.get_x() > pm.get_right()[0]])


def radicand(m):
    """Glyphs under the square root in the numerator: after the ± sign, without the root sign
    (the leftmost glyph there) and its overline."""
    ap = by_x(list(after_pm(m)))
    return VGroup(*[g for g in ap[1:] if not (g.get_height() < 0.06 and g.get_width() > 0.6)])


_SYM_CACHE = {}


def sym(m, tex):
    """Glyphs of m drawn with the same shape as the single-glyph formula `tex`, left to right."""
    if tex not in _SYM_CACHE:
        ref = Tex(tex).family_members_with_points()
        assert len(ref) == 1, f"{tex!r} is not a single glyph"
        _SYM_CACHE[tex] = ref[0]
    ref = _SYM_CACHE[tex]
    rp = (ref.get_all_points() - ref.get_center()) / ref.get_height()

    ref_aspect = ref.get_width() / ref.get_height()

    def same(g):
        # Same outline up to scale: equal aspect ratio and every normalised outline point close
        # to some reference point and vice versa (independent of where the outline starts).
        if g.get_height() == 0 or abs(g.get_width() / g.get_height() - ref_aspect) > 0.02:
            return False
        gp = (g.get_all_points() - g.get_center()) / g.get_height()
        dist = np.linalg.norm(gp[:, None, :2] - rp[None, :, :2], axis=2)
        return bool(max(dist.min(axis=1).max(), dist.min(axis=0).max()) < 0.12)
    return by_x([g for g in glyphs(m) if same(g)])


def fit(m, max_w=MAX_W):
    if m.get_width() > max_w:
        m.set_width(max_w)
    return m


def box(m, color=YELLOW_C, buff=0.1):
    return SurroundingRectangle(m, buff=buff).set_stroke(color, 3)


def strike(m, color=RED_C):
    return Line(m.get_corner(DL) + 0.04 * DL, m.get_corner(UR) + 0.04 * UR).set_stroke(color, 5)


def boxes_in(scene):
    """Highlight boxes on screen, whether added singly or as a VGroup of boxes."""
    def is_box(m):
        if isinstance(m, SurroundingRectangle):
            return True
        return isinstance(m, VGroup) and len(m) > 0 and all(isinstance(s, SurroundingRectangle) for s in m)
    return [m for m in scene.mobjects if is_box(m)]


class SequenceScene(Scene):
    SEQ_ID = None
    T2C = {}

    def setup(self):
        super().setup()
        self.frame_count = 0
        self.boundaries = []
        self.layout = []
        self.spec = next(s for s in SEQUENCES if s["id"] == self.SEQ_ID)
        self.chip_mob = None
        self.step_index = 0

    def play(self, *proto_animations, run_time=None, **kwargs):
        """Every animation runs at SPEED x its authored duration (holds are not scaled)."""
        anims = [prepare_animation(a) for a in proto_animations]
        if run_time is None:
            run_time = max(a.get_run_time() for a in anims)
        super().play(*anims, run_time=run_time * SPEED, **kwargs)

    def emit_frame(self):
        super().emit_frame()
        if not self.skip_animations:
            self.frame_count += 1

    # ---------------------------------------------------------------- building blocks

    def T(self, s, size=64, color=FG, t2c=None, max_w=MAX_W):
        m = STex(s, font_size=size, fill_color=color, t2c={**self.T2C, **(t2c or {})})
        return fit(m, max_w)

    def sel(self, m, key):
        if isinstance(key, tuple):
            return m[key[0]][key[1]]
        if isinstance(key, str):
            return m[key]
        return key

    def morph(self, src, tgt, pairs=(), run_time=1.5, **kw):
        """TransformMatchingTex with explicit identity pairs (selectors on src and tgt)."""
        matched = [(self.sel(src, a), self.sel(tgt, b)) for a, b in pairs]
        return TransformMatchingTex(src, tgt, matched_pairs=matched, run_time=run_time, **kw)

    def morph_copy(self, src, tgt, pairs=(), run_time=1.5, **kw):
        """Like morph, but the source stays on screen (pairs are selected from the copy)."""
        return self.morph(src.copy(), tgt, pairs, run_time=run_time, **kw)

    def fly(self, src, a, tgt, b, arc=0.0):
        return TransformFromCopy(self.sel(src, a), self.sel(tgt, b), path_arc=arc)

    def chip(self, detail=None):
        """Animation that swaps the bottom-left chip to the current step's relation."""
        rel = self.spec["steps"][self.step_index]["relation"]
        word, color = CHIP_WORDS[rel]
        label = Text(word, font=UI_FONT, font_size=22, weight=BOLD).set_color(color)
        parts = [label]
        if detail:
            parts.append(Tex(detail, font_size=34, fill_color=FG))
        content = VGroup(*parts).arrange(RIGHT, buff=0.3)
        frame = RoundedRectangle(width=content.get_width() + 0.5, height=content.get_height() + 0.32,
                                 corner_radius=0.16).set_stroke(color, 2, opacity=0.8).set_fill(BG, 1)
        frame.move_to(content)
        new = VGroup(frame, content).to_corner(DL, buff=0.35)
        old, self.chip_mob = self.chip_mob, new
        if old is None:
            return FadeIn(new, shift=0.15 * UP)
        return FadeTransform(old, new)

    def settle(self, *mobs):
        """Make the scene contain exactly `mobs` (+ the chip); invisible bookkeeping."""
        self.clear()
        if self.chip_mob is not None:
            self.add(self.chip_mob)
        self.add(*mobs)

    def record_layout(self, mobs):
        rows = []
        for m in mobs:
            for sub in m.get_family():
                if isinstance(sub, Tex) and not any(sub is c for c in (self.chip_mob.get_family() if self.chip_mob else [])):
                    rows.append({"tex": sub.tex_string, "font": round(float(sub.font_size), 1),
                                 "width": round(float(sub.get_width()), 2),
                                 "left": round(float(sub.get_left()[0]), 2), "right": round(float(sub.get_right()[0]), 2),
                                 "top": round(float(sub.get_top()[1]), 2), "bottom": round(float(sub.get_bottom()[1]), 2)})
        self.layout.append(rows)

    def start(self, *mobs):
        self.add(*mobs)
        self.wait(0.25)
        self.boundaries.append(self.frame_count)
        self.record_layout(mobs)

    def step_done(self, *final_mobs):
        if final_mobs:
            self.settle(*final_mobs)
        self.wait(HOLD)
        self.boundaries.append(self.frame_count)
        self.record_layout(final_mobs)
        self.step_index += 1

    def tear_down(self):
        super().tear_down()
        steps = len(self.spec["steps"])
        if len(self.boundaries) != steps + 1:
            raise RuntimeError(f"{self.SEQ_ID}: {len(self.boundaries) - 1} steps recorded, spec has {steps}")
        path = getattr(self.file_writer, "movie_file_path", None)
        if path:
            with open(os.path.splitext(str(path))[0] + ".boundaries.json", "w", encoding="utf-8") as f:
                json.dump({"sequence": self.SEQ_ID, "scene": type(self).__name__, "fps": self.camera.fps,
                           "boundaries": self.boundaries, "frames": self.frame_count,
                           "layout": self.layout}, f)

    # ---------------------------------------------------------------- shared moves

    def characteristic_from(self, ode, char, pairs, header_items, detail=R"y = e^{rt}", run_time=1.8):
        """ODE moves to the header while a copy morphs into the characteristic equation."""
        header = VGroup(*header_items)
        header.generate_target()
        header.target.arrange(RIGHT, buff=0.7).scale(0.55).move_to(UP * HEADER_Y)
        self.play(MoveToTarget(header), self.morph_copy(ode, char, pairs, run_time=run_time),
                  self.chip(detail), run_time=run_time)
        return header


# ==================================================================== Lesson 1

class NormalFormSequence(SequenceScene):
    SEQ_ID = "normal-form"
    T2C = {"a(t)": YELLOW_C, "C_1": BLUE_C, "C_2": BLUE_C}

    def construct(self):
        e0 = self.T(R"a(t)\,y'' + b(t)\,y' + c(t)\,y = g(t)", 66).shift(0.3 * UP)
        cond = self.T(R"a(t) \neq 0 \text{ on the interval}", 40).next_to(e0, DOWN, buff=0.8)
        self.start(e0, cond)

        # 1. divide every term by a(t): the leading a(t) splits into three denominators
        e1 = self.T(R"y'' + \frac{b(t)}{a(t)}\,y' + \frac{c(t)}{a(t)}\,y = \frac{g(t)}{a(t)}", 66).shift(0.3 * UP)
        bars = frac_bars(e1)
        dens = VGroup(*[g for b in bars for g in under(e1, b)])          # the three a(t)
        fracs = [VGroup(*over(e1, b), b, *under(e1, b)) for b in bars]
        dens.set_color(YELLOW_C)
        self.play(FlashAround(e0["a(t)"], color=YELLOW_C), self.chip(R"\text{divide by }a(t)"), run_time=0.8)
        self.play(self.morph(e0, e1, [("a(t)", dens)]), cond.animate.next_to(e1, DOWN, buff=0.7), run_time=1.6)
        self.step_done(e1, cond)

        # 2. name the fractions p, q, f
        e2 = self.T(R"y'' + p(t)\,y' + q(t)\,y = f(t)", 72, t2c={"p(t)": TEAL_C, "q(t)": TEAL_C, "f(t)": TEAL_C})
        e2.shift(0.6 * UP)
        defs = self.T(R"p = \frac{b}{a}, \qquad q = \frac{c}{a}, \qquad f = \frac{g}{a}", 50).shift(1.5 * DOWN)
        for ch in ("p", "q", "f"):
            VGroup(*sym(defs, ch)).set_color(TEAL_C)
        self.play(
            self.morph(e1, e2, [(fracs[0], "p(t)"), (fracs[1], "q(t)"), (fracs[2], "f(t)")]),
            FadeTransform(cond, defs), self.chip(), run_time=1.6)
        self.step_done(e2, defs)

        # 3. the left side is an operator L[y]
        e3 = self.T(R"L[y] = {y''} + p\,{y'} + q\,{y}", 70).move_to(1.2 * UP)
        self.play(self.morph(e2, e3, [("y''", "{y''}"), ("p(t)", "p"), ("q(t)", "q")]),
                  FadeOut(defs, shift=DOWN), self.chip(R"L[y] = 0 \text{ is homogeneous}"), run_time=1.6)
        self.step_done(e3)

        # 4. substitute y = C1 y1 + C2 y2 into each slot (three rows, one per slot)
        combo = self.T(R"y = C_1 y_1 + C_2 y_2", 54)
        self.play(e3.animate.scale(0.8).move_to(2.75 * UP + 2.6 * LEFT), self.chip(R"y = C_1 y_1 + C_2 y_2"),
                  run_time=0.8)
        combo.move_to(2.75 * UP + 3.9 * RIGHT)
        self.play(FadeIn(combo, shift=0.2 * LEFT), run_time=0.5)
        lhs = self.T(R"L[C_1 y_1 + C_2 y_2]", 60)
        r1 = self.T(R"= (C_1 y_1 + C_2 y_2)''", 60)
        r2 = self.T(R"+\, p\,(C_1 y_1 + C_2 y_2)'", 60)
        r3 = self.T(R"+\, q\,(C_1 y_1 + C_2 y_2)", 60)
        rows = VGroup(r1, r2, r3).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        block = VGroup(lhs, rows).arrange(RIGHT, buff=0.3, aligned_edge=UP).move_to(0.35 * DOWN)
        lhs.align_to(r1, DOWN)
        slots = [r["C_1 y_1 + C_2 y_2"] for r in (r1, r2, r3)]
        self.play(
            self.fly(e3, "L[y]", lhs, "L[C_1 y_1 + C_2 y_2]"),
            *[TransformFromCopy(combo["C_1 y_1 + C_2 y_2"], sl, path_arc=-0.4) for sl in slots],
            self.fly(e3, "p", r2, "p"), self.fly(e3, "q", r3, "q"),
            *[Write(others(r, sl, *( [r["p"]] if r is r2 else [r["q"]] if r is r3 else []))) for r, sl in zip((r1, r2, r3), slots)],
            run_time=1.8)
        self.step_done(e3, combo, lhs, r1, r2, r3)

        # 5. regroup: constants pass through derivatives, collect C1 terms and C2 terms
        n1 = self.T(R"= C_1\,(y_1'' + p\,y_1' + q\,y_1)", 60)
        n2 = self.T(R"+\, C_2\,(y_2'' + p\,y_2' + q\,y_2)", 60)
        nrows = VGroup(n1, n2).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        nrows.move_to(rows, aligned_edge=UL)
        src = VGroup(r1, r2, r3)
        pairs = [(VGroup(*[r["C_1"] for r in (r1, r2, r3)]), n1["C_1"]),
                 (VGroup(*[r["C_2"] for r in (r1, r2, r3)]), n2["C_2"]),
                 (r2["p"], VGroup(n1["p"], n2["p"])), (r3["q"], VGroup(n1["q"], n2["q"])),
                 (r1["="], n1["="])]
        self.play(TransformMatchingShapes(src, nrows, matched_pairs=pairs), FadeOut(combo, shift=UP),
                  self.chip(R"(C\,y)' = C\,y'"), run_time=1.9)
        self.step_done(e3, lhs, n1, n2)

        # 6. each bracket is L of one function
        b1 = R"(y_1'' + p\,y_1' + q\,y_1)"
        b2 = R"(y_2'' + p\,y_2' + q\,y_2)"
        self.play(ShowCreation(box(n1[b1], TEAL_C)), ShowCreation(box(n2[b2], TEAL_C)), self.chip(), run_time=0.7)
        m1 = self.T(R"= C_1\,L[y_1]", 60).move_to(n1, aligned_edge=LEFT)
        m2 = self.T(R"+\, C_2\,L[y_2]", 60).move_to(n2, aligned_edge=LEFT)
        self.play(self.morph(n1, m1, [(b1, "L[y_1]")]), self.morph(n2, m2, [(b2, "L[y_2]")]),
                  *[FadeOut(b) for b in boxes_in(self)], run_time=1.5)
        line = self.T(R"L[C_1 y_1 + C_2 y_2] = C_1\,L[y_1] + C_2\,L[y_2]", 66).move_to(0.3 * DOWN)
        self.play(TransformMatchingShapes(VGroup(lhs, m1, m2), line), run_time=1.0)
        self.step_done(e3, line)

        # 7. superposition: both brackets are zero
        prem = self.T(R"L[y_1] = 0,\ \ L[y_2] = 0", 60).move_to(1.4 * UP)
        self.play(FadeOut(e3, shift=UP), Write(prem), self.chip(), run_time=1.0)
        z0 = self.T(R"L[C_1 y_1 + C_2 y_2] = C_1 \cdot 0 + C_2 \cdot 0", 66).move_to(0.3 * DOWN)
        self.play(self.morph(line, z0, [("L[y_1]", ("0", 0)), ("L[y_2]", ("0", 1))]),
                  Indicate(prem["0"][0], color=YELLOW_C), Indicate(prem["0"][1], color=YELLOW_C), run_time=1.4)
        z = self.T(R"\Rightarrow \quad{} L[C_1 y_1 + C_2 y_2] = 0", 72).move_to(0.3 * DOWN)
        self.play(self.morph(z0, z), run_time=1.2)
        result = box(z, TEAL_C, buff=0.2)
        self.play(ShowCreation(result), run_time=0.5)
        self.step_done(prem, z, result)


# ==================================================================== Lesson 2

class CharacteristicSequence(SequenceScene):
    SEQ_ID = "characteristic"
    T2C = {"e^{rt}": TEAL_C}

    def construct(self):
        ode = self.T(R"a\,{y''} + b\,{y'} + c\,{y} = 0", 76).shift(0.3 * UP)
        self.start(ode)

        # 1. trial y = e^{rt}; each derivative brings down an r
        t0 = self.T(R"y = e^{rt}", 60)
        t1 = self.T(R"y' = r\,e^{rt}", 60)
        t2 = self.T(R"y'' = r^2 e^{rt}", 60)
        VGroup(t0, t1, t2).arrange(RIGHT, buff=1.1).move_to(0.4 * UP)
        t1["r"][0].set_color(YELLOW_C)
        t2["r^2"].set_color(YELLOW_C)
        self.play(ode.animate.scale(0.85).move_to(2.35 * UP), Write(t0), self.chip(R"y = e^{rt}"), run_time=1.1)
        self.play(TransformMatchingTex(t0.copy(), t1, path_arc=-0.3), run_time=0.9)
        self.play(TransformMatchingTex(t1.copy(), t2, path_arc=-0.3), run_time=0.9)
        self.step_done(ode, t0, t1, t2)

        # 2. substitute into the equation
        s = self.T(R"a\,r^2 e^{rt} + b\,r\,e^{rt} + c\,e^{rt} = 0", 64).move_to(1.5 * DOWN)
        s["r^2"].set_color(YELLOW_C)
        s["r"][2].set_color(YELLOW_C)
        slots = [ode["{y''}"], ode["{y'}"], ode["{y}"]]
        rhs = [t2[R"r^2 e^{rt}"], t1[R"r\,e^{rt}"], t0["e^{rt}"]]
        bxs = VGroup(*[box(m, YELLOW_C, 0.06) for m in slots + rhs])
        self.play(ShowCreation(bxs), self.chip(R"y,\ y',\ y''"), run_time=0.7)
        self.play(
            TransformFromCopy(rhs[0], s[R"r^2 e^{rt}"], path_arc=0.4),
            TransformFromCopy(rhs[1], s[R"r\,e^{rt}"], path_arc=0.4),
            TransformFromCopy(rhs[2], s["e^{rt}"][2], path_arc=0.4),
            *[self.fly(ode, k, s, k) for k in ("a", "b", "c", "= 0")],
            self.fly(ode, ("+", 0), s, ("+", 0)), self.fly(ode, ("+", 1), s, ("+", 1)),
            FadeOut(bxs), run_time=1.8)
        self.step_done(ode, t0, t1, t2, s)

        # 3. factor out the common e^{rt}
        f = self.T(R"(a\,r^2 + b\,r + c)\,e^{rt} = 0", 72).move_to(0.2 * DOWN)
        f["r^2"].set_color(YELLOW_C)
        f["r"][1].set_color(YELLOW_C)
        self.play(FadeOut(VGroup(t0, t1, t2), shift=0.4 * UP), s.animate.move_to(0.2 * DOWN), self.chip(),
                  run_time=0.8)
        eb = VGroup(*[box(m, YELLOW_C, 0.06) for m in s["e^{rt}"]])
        self.play(ShowCreation(eb), run_time=0.5)
        self.play(self.morph(s, f, [("e^{rt}", "e^{rt}")]), FadeOut(eb), run_time=1.6)
        self.step_done(ode, f)

        # 4. e^{rt} is never zero (real or complex r): divide it out
        nz = self.T(R"e^{rt} \neq 0", 48, color=YELLOW_C, t2c={"e^{rt}": YELLOW_C})
        nz.next_to(f["e^{rt}"], DOWN, buff=0.55)
        hb = box(f["e^{rt}"], YELLOW_C, 0.08)
        self.play(ShowCreation(hb), FadeIn(nz, shift=0.2 * UP), self.chip(R"\text{divide by }e^{rt} \neq 0"), run_time=0.8)
        d = self.T(R"\frac{(a\,r^2 + b\,r + c)\,e^{rt}}{e^{rt}} = \frac{0}{e^{rt}}", 66).move_to(0.2 * DOWN)
        b0, b1 = frac_bars(d)
        num0, den0, den1 = over(d, b0), under(d, b0), under(d, b1)
        assert len(num0) == 13 and len(den0) == 3 and len(den1) == 3   # ( a r 2 + b r + c ) e r t
        VGroup(num0[2], num0[3], num0[6]).set_color(YELLOW_C)
        num_e, den_e = VGroup(*num0[-3:]), VGroup(*den0)
        VGroup(num_e, den_e, *den1).set_color(TEAL_C)
        self.play(self.morph(f, d, [("e^{rt}", num_e)]), FadeOut(hb), FadeOut(nz), run_time=1.3)
        cross = VGroup(strike(num_e), strike(den_e))
        self.play(ShowCreation(cross, lag_ratio=0.3), run_time=0.6)
        ce = self.T(R"a\,r^2 + b\,r + c = 0", 80).move_to(0.2 * DOWN)
        ce["r^2"].set_color(YELLOW_C)
        ce["r"][1].set_color(YELLOW_C)
        self.play(self.morph(d, ce), FadeOut(cross), run_time=1.4)
        cbox = box(ce, BLUE_C, 0.25)
        self.play(ShowCreation(cbox), run_time=0.5)
        self.step_done(ode, ce, cbox)

        # 5. quadratic formula: a, b, c fly into place
        q = self.T(R"r = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", 72).move_to(1.1 * DOWN)
        q_a, q_b, q_c, q_disc = quadratic_parts(q, "a", "b", "c")
        top = VGroup(ce, cbox)
        self.play(FadeOut(ode, shift=UP), top.animate.scale(0.8).move_to(2.0 * UP), self.chip(), run_time=0.8)
        self.play(
            TransformFromCopy(ce["a"], q_a, path_arc=0.3),
            TransformFromCopy(ce["b"], q_b, path_arc=0.3),
            TransformFromCopy(ce["c"], q_c, path_arc=0.3),
            Write(others(q, q_a, q_b, q_c)), run_time=1.8)
        self.step_done(top, q)

        # 6. the discriminant picks the case
        disc = self.T(R"\Delta = b^2 - 4ac", 60).move_to(0.6 * UP)
        db = box(q_disc, YELLOW_C, 0.08)
        self.play(ShowCreation(db), self.chip(R"\Delta = b^2 - 4ac"), run_time=0.6)
        self.play(FadeOut(top, shift=UP), q.animate.scale(0.7).move_to(2.55 * UP), FadeOut(db), run_time=0.8)
        self.play(TransformFromCopy(q_disc, disc["b^2 - 4ac"], path_arc=0.3),
                  Write(disc[R"\Delta ="]), run_time=1.0)
        cols = VGroup()
        specs = [(R"\Delta > 0", R"r_1 \neq r_2 \text{ real}", R"e^{r_1 t},\ e^{r_2 t}", BLUE_C),
                 (R"\Delta = 0", R"r_1 = r_2 = r", R"e^{rt},\ t\,e^{rt}", TEAL_C),
                 (R"\Delta < 0", R"r = \alpha \pm i\omega", R"e^{\alpha t}\cos\omega t,\ e^{\alpha t}\sin\omega t", YELLOW_C)]
        for sign, roots, sols, col in specs:
            g = VGroup(self.T(sign, 54, color=col), self.T(roots, 40), self.T(sols, 36, max_w=4.2))
            g.arrange(DOWN, buff=0.32)
            cols.add(g)
        cols.arrange(RIGHT, buff=0.9).move_to(1.5 * DOWN)
        self.play(*[TransformFromCopy(disc[R"\Delta"], g[0][R"\Delta"], path_arc=0.3) for g in cols],
                  *[Write(others(g[0], g[0][R"\Delta"])) for g in cols], run_time=1.0)
        self.play(LaggedStart(*[FadeIn(VGroup(g[1], g[2]), shift=0.25 * DOWN) for g in cols], lag_ratio=0.25),
                  run_time=1.3)
        self.step_done(q, disc, cols)


# ==================================================================== Lesson 3: IVPs

class IVPBase(SequenceScene):
    T2C = {"C_1": BLUE_C, "C_2": BLUE_C}

    def problem(self, ode_tex, ic_tex):
        ode = self.T(ode_tex, 76).move_to(0.7 * UP)
        ic = self.T(ic_tex, 56).move_to(0.8 * DOWN)
        self.start(ode, ic)
        return ode, ic

    def check_marks(self, *lines):
        return VGroup(*[Tex(R"\checkmark", font_size=60, fill_color=GREEN_C).next_to(l, RIGHT, buff=0.4)
                        for l in lines])

    def char_pairs(self):
        # y'' -> r^2 and the y' of the middle term -> r ("y'" also matches the first half of y'')
        return [("y''", "r^2"), (("y'", 1), ("r", 1))]


class DistinctIVPSequence(IVPBase):
    SEQ_ID = "ivp-distinct"

    def construct(self):
        ode, ic = self.problem(R"y'' - 3y' + 2y = 0", R"y(0) = 1, \quad y'(0) = 0")

        # 1. characteristic equation: y'' -> r^2, y' -> r, y -> 1
        ch = self.T(R"r^2 - 3r + 2 = 0", 80).move_to(0.2 * DOWN)
        ch["r"].set_color(YELLOW_C)
        header = self.characteristic_from(ode, ch, self.char_pairs(), [ode, ic])
        self.step_done(header, ch)

        # 2. factor and read off the roots
        full = self.T(R"(r - 1)(r - 2) = 0 \quad \Rightarrow \quad r = 1,\ 2", 72).move_to(0.2 * DOWN)
        left = self.T(R"(r - 1)(r - 2) = 0", 72)
        left.move_to(full["(r - 1)(r - 2) = 0"])
        full[R"1,\ 2"].set_color(YELLOW_C)
        self.play(self.morph(ch, left, [("r^2", ("r", 0))]), self.chip(), run_time=1.5)
        self.play(TransformFromCopy(left["1"], full["1"][1], path_arc=-0.5),
                  TransformFromCopy(left["2"], full["2"][1], path_arc=-0.5),
                  Write(VGroup(full[R"\Rightarrow"], full["r ="], full[","])), run_time=1.1)
        self.step_done(header, full)

        # 3. general solution from the roots, then its derivative
        g = self.T(R"y = C_1 e^{t} + C_2 e^{2t}", 68).move_to(0.2 * UP)
        gp = self.T(R"y' = C_1 e^{t} + 2C_2 e^{2t}", 68).move_to(1.4 * DOWN)
        for m in (g, gp):
            m["e^{t}"].set_color(TEAL_C)
            m["e^{2t}"].set_color(TEAL_C)
        gp["2"][0].set_color(YELLOW_C)
        self.play(full.animate.scale(0.6).move_to(2.15 * UP), self.chip(R"r = 1,\ 2"), run_time=0.7)
        self.play(TransformFromCopy(full["1"][1], g["e^{t}"], path_arc=0.4),
                  TransformFromCopy(full["2"][1], g["e^{2t}"], path_arc=0.4),
                  Write(others(g, g["e^{t}"], g["e^{2t}"])), run_time=1.5)
        self.play(self.morph_copy(g, gp, [(R"C_2 e^{2t}", R"2C_2 e^{2t}")], run_time=1.4, path_arc=0.2))
        self.step_done(header, full, g, gp)

        # 4. set t = 0: every exponential becomes e^0 = 1
        g0 = self.T(R"y(0) = C_1 e^{0} + C_2 e^{0}", 64).move_to(g)
        gp0 = self.T(R"y'(0) = C_1 e^{0} + 2C_2 e^{0}", 64).move_to(gp)
        for m in (g0, gp0):
            m["0"].set_color(YELLOW_C)
        self.play(self.morph(g, g0), self.morph(gp, gp0), self.chip(R"t = 0,\ \ e^{0} = 1"), run_time=1.3)
        e1 = self.T(R"C_1 + C_2 = 1", 68).move_to(g)
        e2 = self.T(R"C_1 + 2C_2 = 0", 68).move_to(gp)
        ic_vals = VGroup(box(ic["y(0) = 1"], YELLOW_C, 0.06), box(ic["y'(0) = 0"], YELLOW_C, 0.06))
        self.play(ShowCreation(ic_vals), run_time=0.5)
        self.play(self.morph(g0, e1, [("y(0)", ("1", 1))]), self.morph(gp0, e2, [("y'(0)", "0")]),
                  FadeOut(ic_vals), run_time=1.5)
        self.step_done(header, full, e1, e2)

        # 5. subtract the equations: C1 cancels
        self.play(VGroup(e1, e2).animate.arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to(1.15 * UP),
                  FadeOut(full, shift=UP), self.chip(R"(2) - (1)"), run_time=0.8)
        rule = Line(LEFT, RIGHT).set_width(e2.get_width() + 0.4).next_to(e2, DOWN, buff=0.25).set_stroke(DIM, 2)
        minus = self.T("-", 64, color=DIM).next_to(e1, LEFT, buff=0.35)
        cancels = VGroup(strike(e1["C_1"]), strike(e2["C_1"]))
        self.play(ShowCreation(rule), FadeIn(minus), ShowCreation(cancels, lag_ratio=0.3), run_time=0.8)
        r2 = self.T(R"C_2 = -1", 68).next_to(rule, DOWN, buff=0.35)
        self.play(TransformFromCopy(VGroup(e2["2C_2"], e1["C_2"]), r2["C_2"]),
                  TransformFromCopy(VGroup(e2["0"], e1["1"][1]), r2["-1"]), Write(r2["="]), run_time=1.3)
        r1 = self.T(R"C_1 = 1 - (-1) = 2", 60)
        res = VGroup(r2.copy(), r1).arrange(RIGHT, buff=1.2).move_to(2.15 * DOWN)
        self.play(r2.animate.move_to(res[0]), TransformFromCopy(e1["C_1"], r1["C_1"]),
                  TransformFromCopy(e1["1"][1], r1["1"][1]), TransformFromCopy(r2["-1"], r1["-1"]),
                  Write(others(r1, r1["C_1"], r1["1"][1], r1["-1"])), FadeOut(rule), run_time=1.4)
        r1b = self.T(R"C_1 = 2", 68).move_to(r1, aligned_edge=LEFT)
        self.play(self.morph(r1, r1b), FadeOut(cancels), FadeOut(minus), run_time=1.0)
        self.step_done(header, e1, e2, r2, r1b)

        # 6. substitute C1 = 2, C2 = -1 into the general solution
        g = self.T(R"y = C_1 e^{t} + C_2 e^{2t}", 68).move_to(0.6 * UP)
        g["e^{t}"].set_color(TEAL_C)
        g["e^{2t}"].set_color(TEAL_C)
        self.play(FadeOut(VGroup(e1, e2), shift=UP), FadeIn(g, shift=0.3 * DOWN), self.chip(R"C_1 = 2,\ C_2 = -1"),
                  run_time=0.8)
        y1 = self.T(R"y = 2\,e^{t} + (-1)\,e^{2t}", 68).move_to(0.6 * UP)
        y1["e^{t}"].set_color(TEAL_C)
        y1["e^{2t}"].set_color(TEAL_C)
        y1["2"][0].set_color(YELLOW_C)
        y1["(-1)"].set_color(YELLOW_C)
        self.play(self.morph(g, y1, [("C_1", ("2", 0)), ("C_2", "(-1)")]),
                  Indicate(r1b["2"], color=YELLOW_C), Indicate(r2["-1"], color=YELLOW_C), run_time=1.5)
        y2 = self.T(R"y(t) = 2e^{t} - e^{2t}", 80).move_to(0.2 * DOWN)
        y2["e^{t}"].set_color(TEAL_C)
        y2["e^{2t}"].set_color(TEAL_C)
        self.play(self.morph(y1, y2), FadeOut(VGroup(r1b, r2), shift=DOWN), run_time=1.4)
        ans = box(y2, TEAL_C, 0.25)
        self.play(ShowCreation(ans), run_time=0.5)
        self.step_done(header, y2, ans)

        # 7. check both initial conditions
        k1 = self.T(R"y(0) = 2 - 1 = 1", 60)
        k2 = self.T(R"y'(0) = 2 - 2 = 0", 60)
        VGroup(k1, k2).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(1.6 * DOWN)
        top = VGroup(y2, ans)
        self.play(top.animate.scale(0.8).move_to(1.4 * UP), self.chip(R"t = 0"), run_time=0.7)
        self.play(TransformFromCopy(y2[R"2e^{t} - e^{2t}"], k1["2 - 1"], path_arc=0.3),
                  TransformFromCopy(y2[R"2e^{t} - e^{2t}"], k2["2 - 2"], path_arc=0.3),
                  Write(others(k1, k1["2 - 1"])), Write(others(k2, k2["2 - 2"])), run_time=1.6)
        marks = self.check_marks(k1, k2)
        self.play(Write(marks), Indicate(header[1], color=GREEN_C), run_time=0.8)
        self.step_done(header, top, k1, k2, marks)


class RepeatedIVPSequence(IVPBase):
    SEQ_ID = "ivp-repeated"
    T2C = {"C_1": BLUE_C, "C_2": BLUE_C, "e^{-t}": TEAL_C}

    def construct(self):
        ode, ic = self.problem(R"y'' + 2y' + y = 0", R"y(0) = 1, \quad y'(0) = 0")

        # 1. characteristic equation
        ch = self.T(R"r^2 + 2r + 1 = 0", 80).move_to(0.2 * DOWN)
        ch["r"].set_color(YELLOW_C)
        header = self.characteristic_from(ode, ch, self.char_pairs(), [ode, ic])
        self.step_done(header, ch)

        # 2. perfect square, double root
        full = self.T(R"(r + 1)^2 = 0 \quad \Rightarrow \quad r = -1 \text{ (double)}", 72).move_to(0.2 * DOWN)
        sq = self.T(R"(r + 1)^2 = 0", 72)
        sq.move_to(full["(r + 1)^2 = 0"])
        sq["r"].set_color(YELLOW_C)
        full["-1"].set_color(YELLOW_C)
        root_one = full["-1"][0][1]
        self.play(self.morph(ch, sq), self.chip(R"b^2 - 4ac = 0"), run_time=1.5)
        self.play(TransformFromCopy(sq["1"], root_one, path_arc=-0.5),
                  Write(others(full, full["(r + 1)^2 = 0"], root_one)), run_time=1.1)
        self.step_done(header, full)

        # 3. e^{-t} and t e^{-t}, then factor out the shared exponential
        g1 = self.T(R"y = C_1 e^{-t} + C_2\,t\,e^{-t}", 68).move_to(0.2 * DOWN)
        self.play(full.animate.scale(0.6).move_to(2.15 * UP), self.chip(R"r = -1,\ \text{double}"), run_time=0.7)
        self.play(TransformFromCopy(full["-1"], g1["e^{-t}"][0], path_arc=0.4),
                  TransformFromCopy(full["-1"], g1["e^{-t}"][1], path_arc=0.4),
                  Write(others(g1, g1["e^{-t}"])), run_time=1.5)
        g2 = self.T(R"y = (C_1 + C_2 t)\,e^{-t}", 72).move_to(0.2 * DOWN)
        eb = VGroup(*[box(m, YELLOW_C, 0.06) for m in g1["e^{-t}"]])
        self.play(ShowCreation(eb), run_time=0.4)
        self.play(self.morph(g1, g2, [("e^{-t}", "e^{-t}")]), FadeOut(eb), run_time=1.4)
        self.step_done(header, full, g2)

        # 4. product rule, then collect over e^{-t}
        self.play(g2.animate.move_to(1.0 * UP), FadeOut(full, shift=UP), self.chip(R"(uv)' = u'v + uv'"), run_time=0.7)
        d1 = self.T(R"y' = C_2\,e^{-t} - (C_1 + C_2 t)\,e^{-t}", 66).move_to(0.6 * DOWN)
        ub = box(g2["(C_1 + C_2 t)"], YELLOW_C, 0.06)
        vb = box(g2["e^{-t}"], TEAL_C, 0.06)
        self.play(ShowCreation(ub), ShowCreation(vb), run_time=0.5)
        self.play(self.morph_copy(g2, d1, run_time=1.4, path_arc=0.2), FadeOut(ub), FadeOut(vb))
        d2 = self.T(R"y' = (C_2 - C_1 - C_2 t)\,e^{-t}", 70).move_to(0.6 * DOWN)
        self.play(self.morph(d1, d2, [("e^{-t}", "e^{-t}")]), run_time=1.4)
        self.step_done(header, g2, d2)

        # 5. t = 0
        e1 = self.T(R"C_1 = 1", 68)
        e2 = self.T(R"C_2 - C_1 = 0 \quad \Rightarrow \quad C_2 = 1", 68)
        VGroup(e1, e2).arrange(DOWN, buff=0.55).move_to(0.4 * DOWN)
        y0 = self.T(R"y(0) = C_1 \cdot e^{0} = 1", 64).move_to(e1)
        yp0 = self.T(R"y'(0) = (C_2 - C_1)\,e^{0} = 0", 64).move_to(e2)
        self.play(self.morph(g2, y0, [("e^{-t}", "e^{0}")]), self.morph(d2, yp0, [("e^{-t}", "e^{0}")]),
                  self.chip(R"t = 0,\ \ e^{0} = 1"), run_time=1.5)
        e2a = self.T(R"C_2 - C_1 = 0", 68).move_to(e2["C_2 - C_1 = 0"])
        self.play(self.morph(y0, e1), self.morph(yp0, e2a), run_time=1.2)
        self.play(TransformFromCopy(e1["1"][1], e2["1"][1], path_arc=-0.6),
                  Write(VGroup(e2[R"\Rightarrow"], e2["C_2"][1], e2["="][1])), run_time=1.0)
        self.step_done(header, e1, e2)

        # 6. substitute the constants
        g = self.T(R"y = (C_1 + C_2 t)\,e^{-t}", 72).move_to(0.8 * UP)
        self.play(VGroup(e1, e2).animate.scale(0.7).arrange(RIGHT, buff=1.0).move_to(2.3 * DOWN),
                  FadeIn(g, shift=0.3 * DOWN), self.chip(R"C_1 = 1,\ C_2 = 1"), run_time=0.8)
        y = self.T(R"y(t) = (1 + t)\,e^{-t}", 80).move_to(0.6 * UP)
        y["1"].set_color(YELLOW_C)
        self.play(self.morph(g, y, [("C_1", "1")]), Indicate(e1["1"][1], color=YELLOW_C),
                  Indicate(e2["1"][1], color=YELLOW_C), run_time=1.5)
        ans = box(y, TEAL_C, 0.25)
        self.play(ShowCreation(ans), FadeOut(VGroup(e1, e2), shift=DOWN), run_time=0.6)
        self.step_done(header, y, ans)

        # 7. check
        top = VGroup(y, ans)
        dy = self.T(R"y' = (1 - 1 - t)\,e^{-t} = -t\,e^{-t}", 60).move_to(0.4 * DOWN)
        k = self.T(R"y(0) = 1, \quad y'(0) = 0", 60).move_to(1.9 * DOWN)
        self.play(top.animate.scale(0.8).move_to(1.6 * UP), self.chip(R"C_1 = C_2 = 1"), run_time=0.7)
        self.play(TransformFromCopy(y["e^{-t}"], dy["e^{-t}"][0], path_arc=0.3),
                  Write(others(dy, dy["e^{-t}"][0])), run_time=1.4)
        self.play(TransformFromCopy(dy, k), run_time=1.0)
        marks = self.check_marks(k)
        self.play(Write(marks), Indicate(header[1], color=GREEN_C), run_time=0.8)
        self.step_done(header, top, dy, k, marks)


class ComplexIVPSequence(IVPBase):
    SEQ_ID = "ivp-complex"
    T2C = {"C_1": BLUE_C, "C_2": BLUE_C, "e^{-t}": TEAL_C}

    def construct(self):
        ode, ic = self.problem(R"y'' + 2y' + 5y = 0", R"y(0) = 1, \quad y'(0) = 0")

        # 1. characteristic equation
        ch = self.T(R"r^2 + 2r + 5 = 0", 80).move_to(0.2 * DOWN)
        ch["r"].set_color(YELLOW_C)
        header = self.characteristic_from(ode, ch, self.char_pairs(), [ode, ic])
        self.step_done(header, ch)

        # 2. quadratic formula, simplified one move at a time
        self.play(ch.animate.scale(0.7).move_to(1.9 * UP), self.chip(R"r = \frac{-b \pm \sqrt{\Delta}}{2a}"),
                  run_time=0.6)
        q1 = self.T(R"r = \frac{-2 \pm \sqrt{4 - 20}}{2}", 72).move_to(0.4 * DOWN)
        q2 = self.T(R"r = \frac{-2 \pm \sqrt{-16}}{2}", 72).move_to(0.4 * DOWN)
        q3 = self.T(R"r = \frac{-2 \pm 4i}{2}", 72).move_to(0.4 * DOWN)
        bar1 = frac_bars(q1)[0]
        num_twos = [g for g in sym(q1, "2") if g.get_y() > bar1.get_y()]     # the 2 of -2 and of 20
        twenty = VGroup(num_twos[1], sym(q1, "0")[0])
        self.play(TransformFromCopy(ch["2"][1], num_twos[0], path_arc=0.4),
                  TransformFromCopy(ch["5"], twenty, path_arc=0.4),
                  Write(others(q1, num_twos[0], twenty)), run_time=1.3)
        self.play(self.morph(q1, q2, [(radicand(q1), radicand(q2))]), run_time=0.9)
        self.play(self.morph(q2, q3, [(after_pm(q2), after_pm(q3))]), run_time=0.9)
        q4 = self.T(R"r = -1 \pm 2i", 80).move_to(0.4 * DOWN)
        q4["-1"].set_color(TEAL_C)
        q4["2i"].set_color(YELLOW_C)
        self.play(self.morph(q3, q4), run_time=0.9)
        lab = self.T(R"\alpha = -1, \quad \omega = 2", 52, t2c={R"\alpha": TEAL_C, R"\omega": YELLOW_C})
        lab.next_to(q4, DOWN, buff=0.6)
        self.play(TransformFromCopy(q4["-1"], lab["-1"]), TransformFromCopy(q4["2"], lab["2"]),
                  Write(VGroup(lab[R"\alpha ="], lab[","], lab[R"\omega ="])), run_time=1.0)
        self.step_done(header, ch, q4, lab)

        # 3. general solution: alpha sets the envelope, omega the frequency
        g = self.T(R"y = e^{-t}\,(C_1 \cos 2t + C_2 \sin 2t)", 68).move_to(0.4 * DOWN)
        g["2t"].set_color(YELLOW_C)
        self.play(FadeOut(ch, shift=UP), VGroup(q4, lab).animate.scale(0.7).arrange(RIGHT, buff=0.8).move_to(1.9 * UP),
                  self.chip(R"e^{\alpha t}\cos\omega t,\ e^{\alpha t}\sin\omega t"), run_time=0.7)
        self.play(TransformFromCopy(lab["-1"], g["e^{-t}"], path_arc=0.4),
                  TransformFromCopy(lab["2"], g["2t"][0], path_arc=0.4),
                  TransformFromCopy(lab["2"], g["2t"][1], path_arc=0.4),
                  Write(others(g, g["e^{-t}"], g["2t"])), run_time=1.6)
        self.step_done(header, q4, lab, g)

        # 4. product rule (two rows), then collect cos and sin
        self.play(FadeOut(VGroup(q4, lab), shift=UP), g.animate.scale(0.85).move_to(2.2 * UP),
                  self.chip(R"(uv)' = u'v + uv'"), run_time=0.7)
        d1a = self.T(R"y' = -e^{-t}(C_1 \cos 2t + C_2 \sin 2t)", 58)
        d1b = self.T(R"+\, e^{-t}(-2C_1 \sin 2t + 2C_2 \cos 2t)", 58)
        VGroup(d1a, d1b).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(0.6 * UP)
        d1b.shift(1.2 * RIGHT)
        self.play(self.morph_copy(g, d1a, path_arc=0.15), self.morph_copy(g, d1b, path_arc=-0.15), run_time=1.6)
        d2 = self.T(R"y' = e^{-t}\big((2C_2 - C_1)\cos 2t - (2C_1 + C_2)\sin 2t\big)", 58).move_to(1.5 * DOWN)
        coss = VGroup(d1a[R"\cos 2t"], d1b[R"\cos 2t"])
        sins = VGroup(d1a[R"\sin 2t"], d1b[R"\sin 2t"])
        cb = VGroup(*[box(m, BLUE_C, 0.05) for m in coss])
        sb = VGroup(*[box(m, YELLOW_C, 0.05) for m in sins])
        self.play(ShowCreation(cb), ShowCreation(sb), run_time=0.5)
        src = VGroup(d1a, d1b).copy()
        self.play(TransformMatchingShapes(src, d2, matched_pairs=[
                      (VGroup(src[0][R"\cos 2t"], src[1][R"\cos 2t"]), d2[R"\cos 2t"]),
                      (VGroup(src[0][R"\sin 2t"], src[1][R"\sin 2t"]), d2[R"\sin 2t"])]),
                  FadeOut(cb), FadeOut(sb), run_time=1.6)
        self.play(FadeOut(VGroup(d1a, d1b), shift=UP), g.animate.move_to(0.9 * UP), d2.animate.move_to(0.6 * DOWN),
                  run_time=0.7)
        self.step_done(header, g, d2)

        # 5. t = 0: e^0 = 1, cos 0 = 1, sin 0 = 0
        y0 = self.T(R"y(0) = C_1 = 1", 66).move_to(0.9 * UP)
        yp0 = self.T(R"y'(0) = 2C_2 - C_1 = 0", 66).move_to(0.6 * DOWN)
        sinz = VGroup(strike(g[R"C_2 \sin 2t"]), strike(d2[R"(2C_1 + C_2)\sin 2t"]))
        self.play(ShowCreation(sinz, lag_ratio=0.3), self.chip(R"e^{0} = \cos 0 = 1,\ \sin 0 = 0"), run_time=0.8)
        self.play(self.morph(g, y0, [("C_1", "C_1")]), self.morph(d2, yp0, [("(2C_2 - C_1)", "2C_2 - C_1")]),
                  FadeOut(sinz), run_time=1.6)
        res = self.T(R"\Rightarrow \quad{} C_2 = \tfrac{1}{2}", 66).next_to(yp0, DOWN, buff=0.5)
        self.play(TransformFromCopy(yp0["2C_2"], res[R"C_2 = \tfrac{1}{2}"], path_arc=-0.4),
                  Write(res[R"\Rightarrow"]), run_time=1.1)
        self.step_done(header, y0, yp0, res)

        # 6. substitute
        g = self.T(R"y = e^{-t}\,(C_1 \cos 2t + C_2 \sin 2t)", 68).move_to(0.6 * UP)
        self.play(FadeOut(VGroup(y0, yp0), shift=UP), res.animate.scale(0.8).move_to(2.4 * DOWN),
                  FadeIn(g, shift=0.3 * DOWN), self.chip(R"C_1 = 1,\ C_2 = \tfrac{1}{2}"), run_time=0.8)
        y = self.T(R"y(t) = e^{-t}\left(\cos 2t + \tfrac{1}{2}\sin 2t\right)", 72).move_to(0.6 * UP)
        y[R"\tfrac{1}{2}"].set_color(YELLOW_C)
        self.play(self.morph(g, y, [("C_2", R"\tfrac{1}{2}")]), Indicate(res[R"\tfrac{1}{2}"], color=YELLOW_C),
                  run_time=1.5)
        ans = box(y, TEAL_C, 0.25)
        self.play(ShowCreation(ans), FadeOut(res, shift=DOWN), run_time=0.6)
        self.step_done(header, y, ans)

        # 7. check
        top = VGroup(y, ans)
        k = self.T(R"y(0) = 1, \quad y'(0) = 2 \cdot \tfrac{1}{2} - 1 = 0", 62).move_to(1.0 * DOWN)
        self.play(top.animate.scale(0.85).move_to(1.3 * UP), self.chip(R"t = 0"), run_time=0.7)
        self.play(TransformFromCopy(y[R"\tfrac{1}{2}"], k[R"\tfrac{1}{2}"], path_arc=0.4),
                  Write(others(k, k[R"\tfrac{1}{2}"])), run_time=1.4)
        marks = self.check_marks(k)
        self.play(Write(marks), Indicate(header[1], color=GREEN_C), run_time=0.8)
        self.step_done(header, top, k, marks)


# ==================================================================== Lesson 4

class ForcedExpSequence(SequenceScene):
    SEQ_ID = "forced-exp"
    T2C = {"C_1": BLUE_C, "C_2": BLUE_C, "A": BLUE_C, "e^{3t}": TEAL_C}

    def construct(self):
        ode = self.T(R"{y''} - {y'} - 2{y} = 4e^{3t}", 80).shift(0.3 * UP)
        self.start(ode)

        # 1. homogeneous part (two rows: characteristic equation, then y_c)
        self.play(ode.animate.scale(0.6).move_to(UP * HEADER_Y), self.chip(R"y'' - y' - 2y = 0"), run_time=0.8)
        ch = self.T(R"r^2 - r - 2 = (r - 2)(r + 1) = 0", 66).move_to(1.2 * UP)
        self.play(self.morph_copy(ode, ch, [("{y''}", "r^2"), ("{y'}", ("r", 1))], run_time=1.4))
        yc = self.T(R"y_c = C_1 e^{2t} + C_2 e^{-t}", 68).move_to(0.4 * DOWN)
        yc["e^{2t}"].set_color(TEAL_C)
        yc["e^{-t}"].set_color(TEAL_C)
        self.play(TransformFromCopy(ch["2"][2], yc["e^{2t}"], path_arc=0.4),
                  TransformFromCopy(ch["+ 1"], yc["e^{-t}"], path_arc=0.4),
                  Write(others(yc, yc["e^{2t}"], yc["e^{-t}"])), run_time=1.4)
        self.step_done(ode, ch, yc)

        # 2. trial y_p = A e^{3t}: 3 is not a root
        trial = VGroup(self.T(R"y_p = A e^{3t}", 60), self.T(R"y_p' = 3A e^{3t}", 60), self.T(R"y_p'' = 9A e^{3t}", 60))
        trial.arrange(RIGHT, buff=0.9).move_to(0.6 * UP)
        trial[1]["3"][0].set_color(YELLOW_C)
        trial[2]["9"].set_color(YELLOW_C)
        self.play(FadeOut(ch, shift=UP), yc.animate.scale(0.7).move_to(2.15 * UP + 3.6 * RIGHT),
                  self.chip(R"3 \ne 2,\ 3 \ne -1"), run_time=0.8)
        self.play(TransformFromCopy(ode["e^{3t}"], trial[0]["e^{3t}"], path_arc=0.4),
                  Write(others(trial[0], trial[0]["e^{3t}"])), run_time=1.0)
        self.play(TransformMatchingTex(trial[0].copy(), trial[1], path_arc=-0.3), run_time=0.8)
        self.play(TransformMatchingTex(trial[1].copy(), trial[2], path_arc=-0.3), run_time=0.8)
        self.step_done(ode, yc, trial)

        # 3. substitute
        s = self.T(R"9A e^{3t} - 3A e^{3t} - 2A e^{3t} = 4e^{3t}", 66).move_to(1.4 * DOWN)
        s["9"].set_color(YELLOW_C)
        s["3A"][0][0].set_color(YELLOW_C)
        s["2"].set_color(YELLOW_C)
        self.play(self.chip(R"y \to y_p"), *[ShowCreation(box(m, YELLOW_C, 0.06)) for m in
                  (ode["{y''}"], ode["{y'}"], ode["{y}"])], run_time=0.6)
        self.play(TransformFromCopy(trial[2]["9A e^{3t}"], s["9A e^{3t}"], path_arc=0.3),
                  TransformFromCopy(trial[1]["3A e^{3t}"], s["3A e^{3t}"], path_arc=0.3),
                  TransformFromCopy(trial[0]["A e^{3t}"], s["A e^{3t}"][2], path_arc=0.3),
                  self.fly(ode, "2", s, "2"), self.fly(ode, ("-", 0), s, ("-", 0)),
                  self.fly(ode, ("-", 1), s, ("-", 1)), self.fly(ode, R"= 4e^{3t}", s, R"= 4e^{3t}"),
                  *[FadeOut(b) for b in boxes_in(self)], run_time=1.8)
        self.step_done(ode, yc, trial, s)

        # 4. combine like terms: 9A - 3A - 2A = 4A
        c = self.T(R"4A\,e^{3t} = 4e^{3t}", 76).move_to(0.2 * DOWN)
        self.play(FadeOut(trial, shift=UP), s.animate.move_to(0.2 * DOWN), self.chip(R"9 - 3 - 2 = 4"), run_time=0.7)
        lhs_e = VGroup(*s["e^{3t}"][:3])
        self.play(ShowCreation(VGroup(*[box(m, YELLOW_C, 0.05) for m in lhs_e])), run_time=0.4)
        self.play(TransformMatchingTex(s, c, matched_pairs=[(lhs_e, c["e^{3t}"][0]),
                                                           (VGroup(s["9"], s["3A"][0][0], s["2"]), c["4"][0]),
                                                           (s["A"], c["A"])]),
                  *[FadeOut(b) for b in boxes_in(self)], run_time=1.5)
        self.step_done(ode, yc, c)

        # 5. divide by 4 e^{3t} (never zero)
        self.play(ShowCreation(box(c[R"4e^{3t}"], YELLOW_C, 0.08)), self.chip(R"\text{divide by }4e^{3t} \neq 0"), run_time=0.6)
        cross = VGroup(strike(c["4"][0]), strike(c["e^{3t}"][0]), strike(c[R"4e^{3t}"]))
        self.play(ShowCreation(cross, lag_ratio=0.3), *[FadeOut(b) for b in boxes_in(self)], run_time=0.8)
        a = self.T(R"A = 1", 84).move_to(0.2 * DOWN)
        self.play(TransformMatchingTex(c, a, matched_pairs=[(c["A"], a["A"]), (c[R"4e^{3t}"], a["1"])]),
                  FadeOut(cross), run_time=1.3)
        yp = self.T(R"y_p = e^{3t}", 60).next_to(a, DOWN, buff=0.7)
        self.play(TransformFromCopy(a, yp), run_time=0.9)
        self.step_done(ode, yc, a, yp)

        # 6. y = y_c + y_p
        g0 = self.T(R"y = y_c + y_p", 70).move_to(0.6 * UP)
        g = self.T(R"y = C_1 e^{2t} + C_2 e^{-t} + e^{3t}", 72).move_to(0.9 * DOWN)
        g["e^{2t}"].set_color(TEAL_C)
        g["e^{-t}"].set_color(TEAL_C)
        self.play(FadeOut(a, shift=UP), yp.animate.scale(0.9).move_to(2.15 * UP + 3.6 * LEFT), Write(g0),
                  self.chip(), run_time=0.9)
        self.play(TransformFromCopy(yc[R"C_1 e^{2t} + C_2 e^{-t}"], g[R"C_1 e^{2t} + C_2 e^{-t}"], path_arc=0.3),
                  TransformFromCopy(yp["e^{3t}"], g["e^{3t}"], path_arc=-0.3),
                  TransformFromCopy(g0["y ="], g["y ="]), TransformFromCopy(g0["+"], g["+"][1]), run_time=1.6)
        ans = box(g, TEAL_C, 0.25)
        self.play(ShowCreation(ans), run_time=0.5)
        self.step_done(ode, yc, yp, g0, g, ans)


class ResonanceSequence(SequenceScene):
    SEQ_ID = "resonance"
    T2C = {"A": BLUE_C, "B": BLUE_C, "C_1": BLUE_C, "C_2": BLUE_C}

    def construct(self):
        ode = self.T(R"y'' + y = \sin t", 84).shift(0.3 * UP)
        self.start(ode)

        # 1. homogeneous part: r = +-i
        self.play(ode.animate.scale(0.55).move_to(UP * HEADER_Y), self.chip(R"y'' + y = 0"), run_time=0.8)
        ch = self.T(R"r^2 + 1 = 0 \quad \Rightarrow \quad r = \pm i", 66).move_to(1.2 * UP)
        yc = self.T(R"y_c = C_1 \cos t + C_2 \sin t", 68).move_to(0.4 * DOWN)
        self.play(self.morph_copy(ode, ch, [("y''", "r^2")], run_time=1.3))
        self.play(TransformFromCopy(ch[R"\pm i"], VGroup(yc[R"\cos t"], yc[R"\sin t"]), path_arc=0.4),
                  Write(others(yc, yc[R"\cos t"], yc[R"\sin t"])), run_time=1.3)
        self.step_done(ode, ch, yc)

        # 2. the usual trial lies in y_c: substituting it gives 0 for every t
        self.play(FadeOut(ch, shift=UP), yc.animate.scale(0.7).move_to(2.2 * UP + 3.4 * RIGHT),
                  self.chip(R"y_p = A\cos t + B\sin t\ ?"), run_time=0.8)
        s1 = self.T(R"(A\cos t + B\sin t)'' + (A\cos t + B\sin t)", 62).move_to(0.9 * UP)
        self.play(Write(s1), run_time=1.0)
        s2 = self.T(R"= -A\cos t - B\sin t + A\cos t + B\sin t", 62)
        s2.next_to(s1, DOWN, buff=0.45).align_to(s1, LEFT).shift(0.3 * RIGHT)
        self.play(self.morph_copy(s1, s2, run_time=1.3))
        pa = VGroup(s2[R"-A\cos t"], s2[R"+ A\cos t"])
        pb = VGroup(s2[R"- B\sin t"], s2[R"+ B\sin t"])
        self.play(ShowCreation(VGroup(*[box(m, RED_C, 0.05) for m in (*pa, *pb)])), run_time=0.4)
        ca, cb = pa.get_center() + 0.75 * DOWN, pb.get_center() + 0.75 * DOWN
        self.play(*[m.animate.move_to(ca) for m in pa], *[m.animate.move_to(cb) for m in pb],
                  *[FadeOut(b) for b in boxes_in(self)], run_time=1.0)
        res = self.T(R"= 0 \text{ for every } t", 62)
        res.move_to(s2, aligned_edge=LEFT)
        self.play(*[FadeOut(m, scale=0.2) for m in (*pa, *pb)], Flash(ca, color=RED_C), Flash(cb, color=RED_C),
                  ReplacementTransform(s2["="], res["="]), FadeIn(res["0"], scale=0.5), run_time=0.8)
        note = self.T(R"\text{identically zero, so it cannot equal } \sin t \text{ for all } t", 44, color=YELLOW_C)
        note.move_to(1.4 * DOWN)
        self.play(Write(others(res, res["="], res["0"])), FadeIn(note, shift=0.2 * UP), run_time=1.0)
        self.step_done(ode, yc, s1, res, note)

        # 3. multiply the trial by t
        tr1 = self.T(R"y_p = t\,u", 72).move_to(0.7 * UP)
        tr1["t"].set_color(YELLOW_C)
        tr2 = self.T(R"u = A\cos t + B\sin t, \quad u'' = -u", 60).move_to(0.6 * DOWN)
        self.play(FadeOut(VGroup(s1, res, note), shift=DOWN), self.chip(R"\pm i \text{ simple} \Rightarrow \times\, t"),
                  run_time=0.6)
        self.play(Write(tr1), Write(tr2), run_time=1.4)
        self.step_done(ode, yc, tr1, tr2)

        # 4. differentiate twice
        d1 = self.T(R"y_p'' = t\,u'' + 2u'", 70).move_to(2.0 * DOWN)
        d2 = self.T(R"y_p'' = -t\,u + 2u'", 70).move_to(2.0 * DOWN)
        self.play(TransformFromCopy(tr1, d1), self.chip(R"(tu)'' = 2u' + t\,u''"), run_time=1.3)
        ub = box(tr2["u'' = -u"], YELLOW_C, 0.06)
        self.play(ShowCreation(ub), run_time=0.4)
        self.play(self.morph(d1, d2, [(R"t\,u''", R"-t\,u")]), FadeOut(ub), run_time=1.3)
        self.step_done(ode, yc, tr1, tr2, d2)

        # 5. add y_p = t u: -tu and +tu cancel
        e = self.T(R"y_p'' + y_p = -t\,u + 2u' + t\,u", 70).move_to(0.55 * DOWN)
        self.play(FadeOut(VGroup(tr1, tr2), shift=UP), d2.animate.move_to(0.95 * UP), self.chip(R"+\, y_p = t\,u"),
                  run_time=0.7)
        self.play(TransformFromCopy(d2[R"-t\,u + 2u'"], e[R"-t\,u + 2u'"], path_arc=0.3),
                  Write(others(e, e[R"-t\,u + 2u'"])), run_time=1.2)
        a, b = e[R"-t\,u"], e[R"+ t\,u"]
        self.play(ShowCreation(box(a, RED_C, 0.05)), ShowCreation(box(b, RED_C, 0.05)), run_time=0.4)
        mid = VGroup(a, b).get_center() + 0.9 * DOWN
        self.play(a.animate.move_to(mid + 0.6 * LEFT), b.animate.move_to(mid + 0.6 * RIGHT),
                  *[FadeOut(x) for x in boxes_in(self)], run_time=0.8)
        self.play(a.animate.move_to(mid), b.animate.move_to(mid), run_time=0.5)
        self.play(FadeOut(a, scale=0.2), FadeOut(b, scale=0.2), Flash(mid, color=RED_C), run_time=0.6)
        e2 = self.T(R"y_p'' + y_p = 2u'", 76).move_to(0.55 * DOWN)
        rest = VGroup(*[g for g in glyphs(e) if g not in set(glyphs(a, b))])
        self.play(TransformMatchingShapes(rest, e2), run_time=1.1)
        self.step_done(ode, yc, d2, e2)

        # 6. compute 2u' and set equal to sin t
        self.play(FadeOut(d2, shift=UP), e2.animate.move_to(0.95 * UP), self.chip(R"u' = -A\sin t + B\cos t"),
                  run_time=0.7)
        m = self.T(R"2u' = -2A\sin t + 2B\cos t = \sin t", 66).move_to(0.45 * DOWN)
        self.play(TransformFromCopy(e2["2u'"], m["2u'"], path_arc=0.3),
                  Write(m[R"= -2A\sin t + 2B\cos t"]), run_time=1.3)
        self.play(TransformFromCopy(ode[R"\sin t"], m[R"\sin t"][1], path_arc=-0.4), Write(m["="][1]), run_time=1.0)
        self.step_done(ode, yc, e2, m)

        # 7. match coefficients (as functions of t: sin and cos are independent)
        sol = self.T(R"-2A = 1,\ \ 2B = 0 \quad \Rightarrow \quad A = -\tfrac{1}{2},\ \ B = 0", 62).move_to(1.8 * DOWN)
        sb = VGroup(box(m[R"-2A\sin t"], YELLOW_C, 0.05), box(m[R"\sin t"][1], YELLOW_C, 0.05))
        cb = box(m[R"2B\cos t"], BLUE_C, 0.05)
        self.play(ShowCreation(sb), ShowCreation(cb), self.chip(R"\sin t:\ -2A = 1,\ \ \cos t:\ 2B = 0"), run_time=0.6)
        self.play(TransformFromCopy(m["-2A"], sol["-2A"], path_arc=0.3), TransformFromCopy(m["2B"], sol["2B"], path_arc=0.3),
                  Write(VGroup(sol["= 1"], sol["= 0"][0])), *[FadeOut(x) for x in (*sb, cb)], run_time=1.3)
        self.play(Write(others(sol, sol["-2A"], sol["2B"], sol["= 1"], sol["= 0"][0])), run_time=1.0)
        self.step_done(ode, yc, e2, m, sol)

        # 8. the particular solution
        y1 = self.T(R"y_p = t\,(A\cos t + B\sin t)", 70).move_to(0.6 * UP)
        self.play(FadeOut(VGroup(e2, m), shift=UP), sol.animate.scale(0.8).move_to(2.4 * DOWN),
                  FadeIn(y1, shift=0.3 * DOWN), self.chip(R"A = -\tfrac{1}{2},\ B = 0"), run_time=0.8)
        y1b = self.T(R"y_p = t\,\left(-\tfrac{1}{2}\cos t + 0 \cdot \sin t\right)", 70).move_to(0.6 * UP)
        y1b[R"-\tfrac{1}{2}"].set_color(YELLOW_C)
        self.play(self.morph(y1, y1b, [("A", R"-\tfrac{1}{2}"), ("B", "0")]),
                  Indicate(sol[R"A = -\tfrac{1}{2}"], color=YELLOW_C), Indicate(sol["B = 0"][1], color=YELLOW_C),
                  run_time=1.3)
        zs = strike(y1b[R"+ 0 \cdot \sin t"])
        self.play(ShowCreation(zs), run_time=0.5)
        y2 = self.T(R"y_p = -\frac{t}{2}\cos t", 84).move_to(0.4 * UP)
        self.play(self.morph(y1b, y2), FadeOut(zs), FadeOut(sol, shift=DOWN), run_time=1.4)
        ans = box(y2, TEAL_C, 0.25)
        self.play(ShowCreation(ans), run_time=0.5)
        self.step_done(ode, yc, y2, ans)

        # 9. for t >= 0 the amplitude grows between the lines +-t/2
        top = VGroup(y2, ans)
        bound = self.T(R"|y_p| \le \frac{t}{2} \quad \text{for } t \ge 0", 48).move_to(2.05 * UP)
        axes = Axes(x_range=[0, 25, 5], y_range=[-13, 13, 5], width=11.0, height=3.6,
                    axis_config=dict(stroke_color=DIM, stroke_width=2, include_tip=False))
        axes.move_to(0.75 * DOWN + 0.4 * RIGHT)
        tl = Tex("t", font_size=36, fill_color=DIM).next_to(axes.x_axis.get_right(), UR, buff=0.1)
        up = axes.get_graph(lambda t: t / 2, x_range=[0, 25]).set_stroke(YELLOW_C, 2.5)
        lo = axes.get_graph(lambda t: -t / 2, x_range=[0, 25]).set_stroke(YELLOW_C, 2.5)
        env = VGroup(DashedVMobject(up, num_dashes=36), DashedVMobject(lo, num_dashes=36))
        envl = Tex(R"\pm\frac{t}{2}", font_size=40, fill_color=YELLOW_C).next_to(axes.c2p(25, 12.5), LEFT, buff=0.15)
        curve = axes.get_graph(lambda t: -t / 2 * math.cos(t), x_range=[0, 25, 0.02]).set_stroke(TEAL_C, 4)
        self.play(top.animate.scale(0.62).move_to(3.05 * UP), FadeOut(ode), FadeOut(yc), self.chip(R"|\cos t| \le 1"),
                  FadeIn(bound, shift=0.2 * DOWN), ShowCreation(axes), FadeIn(tl), run_time=0.9)
        self.play(ShowCreation(env), FadeIn(envl), run_time=0.7)
        self.play(ShowCreation(curve), run_time=2.2, rate_func=linear)
        self.step_done(top, bound, axes, tl, env, envl, curve)


# ==================================================================== Lesson 5

class DampingSequence(SequenceScene):
    SEQ_ID = "damping"

    def construct(self):
        ode = self.T(R"m\,{x''} + b\,{x'} + k\,{x} = 0", 80).shift(0.3 * UP)
        cond = self.T(R"m > 0, \quad b \ge 0, \quad k > 0", 44, color=DIM).next_to(ode, DOWN, buff=0.7)
        self.start(ode, cond)

        # 1. characteristic equation
        ch = self.T(R"m\,r^2 + b\,r + k = 0", 80).move_to(0.2 * DOWN)
        header = self.characteristic_from(ode, ch, [("{x''}", "r^2"), ("{x'}", ("r", 1))], [ode, cond],
                                          detail=R"x = e^{rt}")
        self.step_done(header, ch)

        # 2. roots
        q = self.T(R"r = \frac{-b \pm \sqrt{b^2 - 4mk}}{2m}", 76).move_to(1.0 * DOWN)
        q_m, q_b, q_k, q_disc = quadratic_parts(q, "m", "b", "k")
        self.play(ch.animate.scale(0.75).move_to(1.7 * UP), self.chip(), run_time=0.6)
        self.play(TransformFromCopy(ch["m"], q_m, path_arc=0.3), TransformFromCopy(ch["b"], q_b, path_arc=0.3),
                  TransformFromCopy(ch["k"], q_k, path_arc=0.3),
                  Write(others(q, q_m, q_b, q_k)), run_time=1.6)
        self.step_done(header, ch, q)

        # 3. four regimes: b = 0 is undamped; b > 0 splits by the sign of b^2 - 4mk
        db = box(q_disc, YELLOW_C, 0.08)
        self.play(ShowCreation(db), self.chip(R"\text{sign of } b^2 - 4mk"), run_time=0.5)
        rows = VGroup(
            self.T(R"b = 0:\ \text{undamped, constant amplitude}", 48),
            self.T(R"0 < b^2 < 4mk:\ \text{underdamped, decaying oscillation}", 48),
            self.T(R"b^2 = 4mk:\ \text{critically damped (double root)}", 48),
            self.T(R"b^2 > 4mk:\ \text{overdamped (two negative roots)}", 48),
        ).arrange(DOWN, buff=0.34, aligned_edge=LEFT).move_to(0.75 * DOWN)
        self.play(FadeOut(ch, shift=UP), q.animate.scale(0.65).move_to(2.2 * UP), FadeOut(db), run_time=0.7)
        self.play(TransformFromCopy(q_b[0], rows[0]["b"][0], path_arc=0.3),
                  *[TransformFromCopy(q_disc, VGroup(r["b^2"], r["4mk"]), path_arc=0.3) for r in rows[1:]],
                  run_time=1.1)
        self.play(LaggedStart(Write(others(rows[0], rows[0]["b"][0])),
                              *[Write(others(r, r["b^2"], r["4mk"])) for r in rows[1:]], lag_ratio=0.3), run_time=1.6)
        self.step_done(header, q, rows)

        # 4. critical damping coefficient
        cr = self.T(R"b^2 = 4mk", 76).move_to(0.4 * UP)
        bc = self.T(R"b_{\text{crit}} = 2\sqrt{mk}", 76).move_to(1.3 * DOWN)
        crit_row = rows[2]
        self.play(FadeOut(VGroup(q, rows[0], rows[1], rows[3]), shift=UP), self.chip(R"b \ge 0,\ mk > 0"),
                  TransformMatchingShapes(crit_row, cr), run_time=1.2)
        self.play(self.morph_copy(cr, bc, [("b^2", R"b_{\text{crit}}"), ("4", "2"), ("mk", "mk")], run_time=1.5,
                                  path_arc=0.2))
        ans = box(bc, TEAL_C, 0.22)
        self.play(ShowCreation(ans), run_time=0.5)
        self.step_done(header, cr, bc, ans)

        # 5. example m = 1, k = 4
        ex = self.T(R"b_{\text{crit}} = 2\sqrt{1 \cdot 4} = 4", 76).move_to(1.3 * DOWN)
        vals = self.T(R"m = 1,\ \ k = 4", 56, color=YELLOW_C).move_to(0.4 * UP)
        self.play(FadeOut(cr, shift=UP), FadeIn(vals, shift=0.2 * DOWN), self.chip(R"m = 1,\ k = 4"), run_time=0.7)
        self.play(self.morph(bc, ex, [("mk", R"1 \cdot 4")]), FadeOut(ans), Indicate(vals, color=YELLOW_C), run_time=1.6)
        self.step_done(header, vals, ex)

        # 6. three motions released from rest (all with b > 0)
        axes = Axes(x_range=[0, 6, 1], y_range=[-0.6, 1.1, 0.5], width=10.4, height=3.5,
                    axis_config=dict(stroke_color=DIM, stroke_width=2, include_tip=False))
        axes.move_to(0.85 * DOWN + 0.7 * RIGHT)
        tl = Tex("t", font_size=36, fill_color=DIM).next_to(axes.x_axis.get_right(), UR, buff=0.1)
        cases = [(2, BLUE_C), (4, TEAL_C), (5, YELLOW_C)]
        curves = VGroup(*[axes.get_graph(lambda t, b=b: ode_math.solution(t, 1.0, b, 4.0, 1.0, 0.0),
                                         x_range=[0, 6, 0.02]).set_stroke(col, 4) for b, col in cases])
        labels = VGroup(*[Tex(f"b = {b}", font_size=36, fill_color=col) for b, col in cases])
        labels.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to(axes.c2p(5.0, 0.75))
        eq = self.T(R"x'' + b\,x' + 4x = 0, \quad x(0) = 1,\ x'(0) = 0", 46).move_to(1.95 * UP)
        self.play(FadeOut(header, shift=UP), FadeOut(vals), ex.animate.scale(0.6).move_to(2.95 * UP),
                  FadeIn(eq), ShowCreation(axes), FadeIn(tl), self.chip(R"b = 2,\ 4,\ 5"), run_time=1.0)
        self.play(LaggedStart(*[ShowCreation(c) for c in curves], lag_ratio=0.35),
                  LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.35), run_time=2.4)
        self.step_done(ex, eq, axes, tl, curves, labels)


# ==================================================================== Lesson 6

class CauchyEulerSequence(SequenceScene):
    SEQ_ID = "cauchy-euler"
    T2C = {"C_1": BLUE_C, "C_2": BLUE_C}

    def construct(self):
        ode = self.T(R"t^2 {y''} + 3t\,{y'} + {y} = 0", 80).shift(0.4 * UP)
        dom = self.T(R"t > 0", 48, color=DIM).next_to(ode, DOWN, buff=0.7)
        self.start(ode, dom)
        header = VGroup(ode, dom)

        # 1. trial y = t^m
        t0 = self.T(R"y = t^m", 58)
        t1 = self.T(R"y' = m\,t^{m-1}", 58)
        t2 = self.T(R"y'' = m(m-1)\,t^{m-2}", 58)
        row = VGroup(t0, t1, t2).arrange(RIGHT, buff=0.9).move_to(0.6 * UP)
        for m in (t0, t1, t2):
            m["t^"].set_color(TEAL_C)
        self.play(header.animate.arrange(RIGHT, buff=0.7).scale(0.55).move_to(UP * HEADER_Y), Write(t0),
                  self.chip(R"y = t^m"), run_time=1.1)
        self.play(TransformMatchingTex(t0.copy(), t1, path_arc=-0.3), run_time=0.9)
        self.play(TransformMatchingTex(t1.copy(), t2, path_arc=-0.3), run_time=0.9)
        self.step_done(header, row)

        # 2. substitute
        s = self.T(R"t^2 \cdot m(m-1)\,t^{m-2} + 3t \cdot m\,t^{m-1} + t^m = 0", 58).move_to(1.3 * DOWN)
        bx = VGroup(*[box(m, YELLOW_C, 0.06) for m in (ode["{y''}"], ode["{y'}"], ode["{y}"])])
        self.play(ShowCreation(bx), self.chip(R"y,\ y',\ y''"), run_time=0.5)
        self.play(TransformFromCopy(t2[R"m(m-1)\,t^{m-2}"], s[R"m(m-1)\,t^{m-2}"], path_arc=0.3),
                  TransformFromCopy(t1[R"m\,t^{m-1}"], s[R"m\,t^{m-1}"], path_arc=0.3),
                  TransformFromCopy(t0["t^m"], s["t^m"], path_arc=0.3),
                  self.fly(ode, "t^2", s, "t^2"), self.fly(ode, "3t", s, "3t"),
                  self.fly(ode, ("+", 0), s, ("+", 0)), self.fly(ode, ("+", 1), s, ("+", 1)),
                  self.fly(ode, "= 0", s, "= 0"),
                  Write(s[R"\cdot"]), FadeOut(bx), run_time=1.8)
        self.step_done(header, row, s)

        # 3. powers of t combine
        self.play(FadeOut(row, shift=UP), s.animate.move_to(0.9 * UP), self.chip(R"t^a \cdot t^b = t^{a+b}"),
                  run_time=0.7)
        c = self.T(R"m(m-1)\,t^m + 3m\,t^m + t^m = 0", 66).move_to(0.9 * DOWN)
        c["t^m"].set_color(TEAL_C)
        sc = s.copy()
        p1 = VGroup(sc["t^2"], sc["t^{m-2}"])
        p2 = VGroup(sc["3t"][0][1], sc["t^{m-1}"])
        self.play(ShowCreation(box(s["t^2"], YELLOW_C, 0.05)), ShowCreation(box(s["t^{m-2}"], YELLOW_C, 0.05)),
                  ShowCreation(box(s["3t"][0][1], BLUE_C, 0.05)), ShowCreation(box(s["t^{m-1}"], BLUE_C, 0.05)),
                  run_time=0.5)
        self.play(TransformMatchingTex(sc, c, matched_pairs=[(p1, c["t^m"][0]), (p2, c["t^m"][1])], path_arc=0.2),
                  *[FadeOut(b) for b in boxes_in(self)], run_time=1.6)
        self.play(FadeOut(s, shift=UP), c.animate.move_to(0.2 * UP), run_time=0.6)
        self.step_done(header, c)

        # 4. factor out t^m
        f = self.T(R"\big(m(m-1) + 3m + 1\big)\,t^m = 0", 70).move_to(0.2 * UP)
        f["t^m"].set_color(TEAL_C)
        self.play(ShowCreation(VGroup(*[box(m, YELLOW_C, 0.05) for m in c["t^m"]])), self.chip(), run_time=0.5)
        self.play(self.morph(c, f, [("t^m", "t^m")]), *[FadeOut(b) for b in boxes_in(self)], run_time=1.5)
        self.step_done(header, f)

        # 5. divide by t^m > 0, expand, factor
        pos = self.T(R"t^m > 0", 46, color=YELLOW_C).next_to(f["t^m"], DOWN, buff=0.5)
        self.play(ShowCreation(box(f["t^m"], YELLOW_C, 0.08)), FadeIn(pos, shift=0.2 * UP),
                  self.chip(R"\text{divide by }t^m \neq 0"), run_time=0.7)
        g = self.T(R"m(m-1) + 3m + 1 = 0", 72).move_to(0.2 * UP)
        self.play(self.morph(f, g), FadeOut(pos), *[FadeOut(b) for b in boxes_in(self)], run_time=1.2)
        h = self.T(R"m^2 + 2m + 1 = (m + 1)^2 = 0", 72).move_to(0.2 * UP)
        self.play(self.morph(g, h), run_time=1.4)
        self.step_done(header, h)

        # 6. double exponent: y1 = t^{-1}, y2 = t^{-1} ln t
        d = self.T(R"m = -1 \text{ (double)}", 66).move_to(1.4 * UP)
        d["-1"].set_color(YELLOW_C)
        ys = self.T(R"y_1 = t^{-1}, \quad y_2 = t^{-1}\ln t", 70).move_to(0.4 * DOWN)
        ys["t^{-1}"].set_color(TEAL_C)
        exps = VGroup(*[VGroup(*occ[1:]) for occ in ys["t^{-1}"]])
        self.play(self.morph(h, d, [("(m + 1)^2", "m = -1")]), self.chip(R"\text{repeated} \Rightarrow \ln t"),
                  run_time=1.3)
        self.play(TransformFromCopy(d["-1"], exps[0], path_arc=0.4), TransformFromCopy(d["-1"], exps[1], path_arc=0.4),
                  Write(others(ys, exps)), run_time=1.5)
        self.step_done(header, d, ys)

        # 7. check y2: the numerators cancel
        k = self.T(R"\frac{2\ln t - 3}{t} + \frac{3(1 - \ln t)}{t} + \frac{\ln t}{t}", 64).move_to(0.6 * UP)
        self.play(FadeOut(d, shift=UP), ys.animate.scale(0.7).move_to(2.2 * UP), self.chip(R"y = y_2"), run_time=0.7)
        self.play(Write(k), run_time=1.2)
        # Written as (...)/t, not \frac: highlight boxes inside a \frac numerator land one glyph off.
        n = self.T(R"\big(2\ln t - 3 + 3 - 3\ln t + \ln t\big) \,/\, t", 64).move_to(0.6 * UP)
        self.play(self.morph(k, n), run_time=1.3)
        consts = VGroup(n["- 3"][0], n["+ 3"])
        self.play(ShowCreation(VGroup(*[box(m, RED_C, 0.05) for m in consts])),
                  ShowCreation(VGroup(*[box(m, BLUE_C, 0.05) for m in n[R"\ln t"]])), run_time=0.5)
        z = self.T(R"\big((2 - 3 + 1)\ln t + (-3 + 3)\big) \,/\, t = 0", 64).move_to(1.0 * DOWN)
        self.play(self.morph_copy(n, z, run_time=1.6, path_arc=0.2), *[FadeOut(b) for b in boxes_in(self)])
        mark = Tex(R"\checkmark", font_size=60, fill_color=GREEN_C).next_to(z, RIGHT, buff=0.4)
        self.play(Write(mark), run_time=0.5)
        self.step_done(header, ys, n, z, mark)

        # 8. general solution
        g1 = self.T(R"y = C_1 t^{-1} + C_2 t^{-1}\ln t", 70).move_to(0.95 * UP)
        g1["t^{-1}"].set_color(TEAL_C)
        self.play(FadeOut(VGroup(n, z, mark), shift=DOWN), self.chip(R"y = C_1 y_1 + C_2 y_2"),
                  TransformFromCopy(ys[R"t^{-1}"][0], g1[R"t^{-1}"][0], path_arc=0.3),
                  TransformFromCopy(ys[R"t^{-1}\ln t"], g1[R"t^{-1}\ln t"], path_arc=0.3),
                  Write(others(g1, g1[R"t^{-1}"][0], g1[R"t^{-1}\ln t"])), run_time=1.5)
        g2 = self.T(R"y = \frac{C_1 + C_2 \ln t}{t}", 80).move_to(1.25 * DOWN)
        g2_num = over(g2, frac_bars(g2)[0])                  # C 1 + C 2 l n t
        VGroup(g2_num[0], g2_num[1], g2_num[3], g2_num[4]).set_color(BLUE_C)
        gc = g1.copy()
        self.play(TransformMatchingTex(gc, g2, matched_pairs=[(gc["t^{-1}"], VGroup(*under(g2, frac_bars(g2)[0])))], path_arc=0.2),
                  run_time=1.6)
        ans = box(g2, TEAL_C, 0.25)
        self.play(ShowCreation(ans), run_time=0.5)
        self.step_done(header, ys, g1, g2, ans)


SCENES = [NormalFormSequence, CharacteristicSequence, DistinctIVPSequence, RepeatedIVPSequence,
          ComplexIVPSequence, ForcedExpSequence, ResonanceSequence, DampingSequence, CauchyEulerSequence]
