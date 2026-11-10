"""Shared building blocks for the Control Bootcamp ManimGL scenes (LaTeX-free).

Math typesetting
----------------
No LaTeX is installed, so formulas are typeset by matplotlib's mathtext (Computer Modern
glyphs) into SVG and loaded with ManimGL's SVGMobject. To let a student follow the identity of
each term, a formula is written as a list of *tokens*:

    Mx("xdot", ("=", "="), "A", "x", ("+", "+"), "B", "u")

The whole formula is rendered once (so spacing is mathtext's own), then its glyphs are split
back into one VGroup per token: mathtext emits glyphs left to right in token order, followed by
any rules (fraction bars, overlines), which are assigned to the token they sit inside. Every
token's glyph count is measured by rendering that token alone, and a mismatch raises instead of
silently mis-grouping. A tiny marker path appended to each SVG records the baseline, so separate
formulas, fractions and hand-built matrices can be aligned on a common baseline / math axis.

Scenes
------
ControlScene mirrors the ODE guide's SequenceScene: `start()` ends the still opening state,
each `step_done()` ends one step after a short hold, and the frame indices are written to
<Scene>.boundaries.json so build_control.py can cut exact clips. `settle()` makes the scene
contain exactly the listed mobjects, so a step's final frame is a clean, reproducible state.
"""
import json
import os
import re
import sys
from io import BytesIO

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "cm"
matplotlib.rcParams["svg.fonttype"] = "path"
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.mathtext import math_to_image  # noqa: E402

from manimlib import *  # noqa: E402,F403
from manimlib.animation.animation import prepare_animation  # noqa: E402

from control_specs import RELATIONS, SEQUENCES  # noqa: E402

BG = "#0B0F17"
FG = "#F4F6FB"
DIM = "#8C96AB"
FAINT = "#3A4458"
TEAL_C = "#2EC4B6"     # the state x and its pieces
BLUE_C = "#5AA9FF"     # the input u, actuators, B
YELLOW_C = "#FFD166"   # gains K, values being substituted, highlights
PINK_C = "#F78FB3"     # outputs y, sensors, C
RED_C = "#FF6B6B"      # instability, right half-plane, struck terms
GREEN_C = "#7BD389"    # stable, left half-plane, checks
ORANGE_C = "#FFA45B"   # disturbances d
UI_FONT = "Segoe UI"

HOLD = 0.4             # seconds of still frames at the end of every step
SPEED = 0.8            # factor applied to every authored run_time
FONT_PT = 40           # mathtext render size; 1.0 "em" below = this many SVG px
EM = 0.56              # manim units per em at size=1.0

CHIP = {
    "define": ("DEFINE", BLUE_C),
    "model": ("MODEL", TEAL_C),
    "classify": ("CLASSIFY", TEAL_C),
    "diagram": ("BUILD THE DIAGRAM", PINK_C),
    "substitute": ("SUBSTITUTE", YELLOW_C),
    "identity": ("REWRITE  =", BLUE_C),
    "equivalent": ("EQUIVALENT  ⇔", TEAL_C),
    "solve": ("SOLVE", TEAL_C),
    "compute": ("COMPUTE", YELLOW_C),
    "implies": ("THEREFORE  ⇒", TEAL_C),
    "compare": ("COMPARE", GREEN_C),
    "caution": ("CAUTION", ORANGE_C),
    "recap": ("RECAP", GREEN_C),
}
assert set(CHIP) == set(RELATIONS), "chip words and relation labels must cover the same relations"

# ---------------------------------------------------------------------------- mathtext SVG

_SVG_CACHE = {}
_TRANSLATE = re.compile(r'<g style="fill: [^"]*" transform="translate\(([-\d.e]+) ([-\d.e]+)\)')


def math_svg(tex):
    """(svg_string, glyph_count) for the mathtext formula `tex`, white fill, background removed,
    with a 0.01-px marker square appended at the baseline origin."""
    if tex in _SVG_CACHE:
        return _SVG_CACHE[tex]
    buf = BytesIO()
    math_to_image("$" + tex + "$", buf, prop=FontProperties(size=FONT_PT), format="svg", color="white")
    s = buf.getvalue().decode()
    s = re.sub(r'<g id="patch_1">.*?</g>', "", s, count=1, flags=re.S)
    m = _TRANSLATE.search(s)
    if not m:
        raise RuntimeError(f"no text transform in mathtext SVG for {tex!r}")
    x0, y0 = float(m.group(1)), float(m.group(2))
    marker = (f'<path d="M {x0} {y0} L {x0 + 0.01} {y0} L {x0 + 0.01} {y0 - 0.01} L {x0} {y0 - 0.01} z" '
              f'style="fill: #ffffff"/>')
    s = s.replace("</svg>", marker + "</svg>")
    glyph_count = s.count("<use ")
    _SVG_CACHE[tex] = (s, glyph_count)
    return _SVG_CACHE[tex]


class _RawSVG(SVGMobject):
    height = None
    width = None


def _raw(tex, size):
    """Glyph mobjects (glyphs first, then rules) and the baseline-origin point, scaled so that
    the baseline origin sits at ORIGIN."""
    s, n_glyphs = math_svg(tex)
    mob = _RawSVG(svg_string=s, should_center=False)
    subs = list(mob.submobjects)
    marker = subs.pop()
    origin = marker.get_corner(DL).copy()
    k = size * EM / FONT_PT
    for g in subs:
        g.shift(-origin)
        g.scale(k, about_point=ORIGIN)
    return subs, n_glyphs


def count_glyphs(tex):
    return math_svg(tex)[1]


class Tok(VGroup):
    """One token of a formula: its glyphs, its key and its tex."""
    def __init__(self, key, tex, glyphs):
        super().__init__(*glyphs)
        self.key = key
        self.tex = tex


def _norm(tok):
    """A token spec is 'tex', (key, tex) or (key, tex, color)."""
    if isinstance(tok, str):
        return tok, tok, None
    if len(tok) == 2:
        return tok[0], tok[1], None
    return tok[0], tok[1], tok[2]


PALETTE = {"x": TEAL_C, "xdot": TEAL_C, "u": BLUE_C, "B": BLUE_C, "K": YELLOW_C, "y": PINK_C,
           "C": PINK_C, "d": ORANGE_C}


class Mx(VGroup):
    """A formula made of named tokens (see the module docstring). Tokens whose key is in
    PALETTE (or in `colors`) get that colour; others get `color`."""
    def __init__(self, *tokens, size=1.0, color=FG, colors=None):
        colors = {**PALETTE, **(colors or {})}
        specs = [_norm(t) for t in tokens]
        full = ""
        for _, t, _ in specs:      # keep "\cdot" + "u" from fusing into the unknown "\cdotu"
            full += (" " if re.search(r"\\[A-Za-z]+$", full) and re.match(r"[A-Za-z]", t) else "") + t
        glyphs, n_glyphs = _raw(full, size)
        counts = [count_glyphs(t) for _, t, _ in specs]
        if sum(counts) != n_glyphs:
            raise ValueError(f"token glyph counts {counts} do not add up to {n_glyphs} for {full!r}")
        letters, rules = glyphs[:n_glyphs], glyphs[n_glyphs:]
        groups, i = [], 0
        for c in counts:
            groups.append(letters[i:i + c])
            i += c
        for r in rules:                     # a rule belongs to the token whose glyphs straddle it
            cx = r.get_x()

            def dist(j):
                gs = groups[j]
                if not gs:
                    return 1e9
                if min(g.get_left()[0] for g in gs) - 0.02 <= cx <= max(g.get_right()[0] for g in gs) + 0.02:
                    return 0.0
                return 1 + min(abs(cx - g.get_x()) for g in gs)
            groups[min(range(len(groups)), key=dist)].append(r)
        self.toks = []
        for (key, tex, col), gs in zip(specs, groups):
            t = Tok(key, tex, gs)
            t.set_fill(col or colors.get(key, color), 1).set_stroke(width=0)
            self.toks.append(t)
        super().__init__(*[t for t in self.toks if len(t) > 0])
        self.tex = full
        self.size = size
        self._base_off = np.array(ORIGIN) - self.get_corner(DL)
        self._h0 = max(self.get_height(), 1e-6)

    # -- token access
    def k(self, key, n=0):
        hits = [t for t in self.toks if t.key == key]
        if len(hits) <= n:
            raise KeyError(f"token {key!r}#{n} not in {self.tex!r} (keys {[t.key for t in self.toks]})")
        return hits[n]

    def ks(self, *keys):
        return VGroup(*[self.k(k) for k in keys])

    def all(self, key):
        return [t for t in self.toks if t.key == key]

    def span(self, a, b):
        """Tokens with index a..b inclusive, by key (first occurrence)."""
        ia = self.toks.index(self.k(a))
        ib = self.toks.index(self.k(b))
        return VGroup(*[t for t in self.toks[ia:ib + 1] if len(t)])

    # -- geometry
    def baseline(self):
        scale = self.get_height() / self._h0
        return self.get_corner(DL)[1] + self._base_off[1] * scale

    def axis(self):
        """Height of the math axis (centre of '=' and '+' and of matrices)."""
        return self.baseline() + AXIS * self.size

    def set_baseline(self, y):
        self.shift((y - self.baseline()) * UP)
        return self

    def set_axis(self, y):
        self.shift((y - self.axis()) * UP)
        return self


def _axis_height():
    gs, n = _raw("=", 1.0)
    return float(np.mean([g.get_y() for g in gs[:n]]))


AXIS = _axis_height()


def tex_mx(tex, size=1.0, color=FG):
    """A formula with a single token (no term identity needed)."""
    return Mx(("all", tex), size=size, color=color)


def label(text, size=26, color=FG, weight=NORMAL):
    return Text(text, font=UI_FONT, font_size=size, weight=weight).set_color(color)


def place_row(*pieces, buff=0.18, y=0.0):
    """Arrange formula pieces left to right, Mx pieces on a common baseline and other pieces
    (matrices, fractions) centred on the math axis. Returns the VGroup centred horizontally."""
    x = 0.0
    for p in pieces:
        p.move_to([x + p.get_width() / 2, 0, 0], coor_mask=np.array([1, 0, 0]))
        x += p.get_width() + buff
        if isinstance(p, Mx):
            p.set_baseline(y)
        elif isinstance(p, Frac):
            p.shift((y + AXIS * p.size - p.bar.get_y()) * UP)
        else:
            p.set_y(y + AXIS * getattr(p, "size", 1.0))
    g = VGroup(*pieces)
    g.shift((-(g.get_left()[0] + g.get_right()[0]) / 2) * RIGHT)
    return g


class Mat(VGroup):
    """A bracketed matrix built from individual Mx entries: m.e[i][j]."""
    def __init__(self, rows, size=1.0, color=FG, col_buff=0.45, row_buff=0.22, colors=None):
        self.size = size
        self.e = []
        cells = VGroup()
        h = 0.62 * size
        for i, row in enumerate(rows):
            r = []
            for j, entry in enumerate(row):
                m = entry if isinstance(entry, Mx) else Mx(entry, size=size, color=color, colors=colors)
                r.append(m)
                cells.add(m)
            self.e.append(r)
        nr, nc = len(rows), len(rows[0])
        colw = [max(self.e[i][j].get_width() for i in range(nr)) for j in range(nc)]
        x = 0
        xs = []
        for j in range(nc):
            xs.append(x + colw[j] / 2)
            x += colw[j] + col_buff * size
        total_w = x - col_buff * size
        for i in range(nr):
            yb = -(i * (h + row_buff * size))
            for j in range(nc):
                m = self.e[i][j]
                m.move_to([xs[j] - total_w / 2, 0, 0], coor_mask=np.array([1, 0, 0]))
                m.set_axis(yb)
        cells.set_y(0)
        top, bot = cells.get_top()[1] + 0.12 * size, cells.get_bottom()[1] - 0.12 * size
        lx, rx = cells.get_left()[0] - 0.14 * size, cells.get_right()[0] + 0.14 * size
        arm = 0.12 * size
        sw = 3.2 * size
        self.lb = VMobject().set_points_as_corners([[lx + arm, top, 0], [lx, top, 0], [lx, bot, 0], [lx + arm, bot, 0]])
        self.rb = VMobject().set_points_as_corners([[rx - arm, top, 0], [rx, top, 0], [rx, bot, 0], [rx - arm, bot, 0]])
        for b in (self.lb, self.rb):
            b.set_stroke(color, sw).set_fill(opacity=0)
        self.cells = cells
        super().__init__(self.lb, cells, self.rb)

    def row(self, i):
        return VGroup(*self.e[i])

    def col(self, j):
        return VGroup(*[r[j] for r in self.e])


class Frac(VGroup):
    """num over den with a drawn bar; num and den are Mx (token access preserved)."""
    def __init__(self, num, den, size=None, color=FG):
        size = num.size if size is None else size
        self.size = size
        self.num, self.den = num, den
        w = max(num.get_width(), den.get_width()) + 0.16 * size
        self.bar = Line(LEFT * w / 2, RIGHT * w / 2).set_stroke(color, 2.6 * size)
        num.move_to(ORIGIN, coor_mask=np.array([1, 0, 0])).set_y(0)
        den.move_to(ORIGIN, coor_mask=np.array([1, 0, 0])).set_y(0)
        num.next_to(self.bar, UP, buff=0.12 * size)
        den.next_to(self.bar, DOWN, buff=0.12 * size)
        super().__init__(num, self.bar, den)
        self.shift(-self.bar.get_center())


# ---------------------------------------------------------------------------- diagrams

def block(text, w=2.4, h=1.0, color=FG, size=28, fill=None):
    box = RoundedRectangle(width=w, height=h, corner_radius=0.14).set_stroke(color, 3)
    box.set_fill(fill or BG, 1)
    t = label(text, size, color=FG)
    if t.get_width() > w - 0.3:
        t.set_width(w - 0.3)
    t.move_to(box)
    g = VGroup(box, t)
    g.box, g.text = box, t
    return g


def grow_arrow(a):
    """Grow a poly_arrow from its first point."""
    return GrowFromPoint(a, a[0].get_points()[0])


def arrow(a, b, color=FG, width=3.5):
    return poly_arrow([a, b], color=color, width=width)


class Plot(VGroup):
    """Minimal axes for a time response: curves are sampled polylines, and a curve that leaves
    the plotted y-range is drawn only up to the boundary (never squashed into the box)."""
    def __init__(self, t_max=5.0, y_min=-1.0, y_max=1.0, width=4.5, height=2.6, t_label="t", y_label=None):
        self.t_max, self.y_min, self.y_max, self.w, self.h = t_max, y_min, y_max, width, height
        self._o = Dot(ORIGIN, radius=0).set_opacity(0)
        frame = Rectangle(width=width, height=height).set_stroke(FAINT, 1.5).set_fill(opacity=0)
        frame.move_to([width / 2, height / 2 - self._ypix(0), 0])
        zero = Line(self._pt(0, 0), self._pt(t_max, 0)).set_stroke(DIM, 2)
        yax = Line(self._pt(0, y_min), self._pt(0, y_max)).set_stroke(DIM, 2)
        parts = [self._o, frame, zero, yax]
        tl = label(t_label, 20, DIM).next_to(self._pt(t_max, 0), DOWN, buff=0.1).shift(0.1 * LEFT)
        parts.append(tl)
        if y_label:
            parts.append(label(y_label, 20, DIM).next_to(self._pt(0, y_max), RIGHT, buff=0.12).shift(0.15 * DOWN))
        super().__init__(*parts)

    def _yfrac(self, y):
        return (y - self.y_min) / (self.y_max - self.y_min)

    def _ypix(self, y):
        return self._yfrac(y) * self.h

    def _pt(self, t, y):
        # coordinates relative to the (t=0, y=0) point, which starts at ORIGIN
        return np.array([t / self.t_max * self.w, self._ypix(y) - self._ypix(0), 0])

    def c2p(self, t, y):
        return self._o.get_center() + self._pt(t, y)

    def curve(self, f, t0=0.0, t1=None, color=TEAL_C, width=4, n=240):
        t1 = self.t_max if t1 is None else t1
        pts = []
        for t in np.linspace(t0, t1, n):
            y = float(f(t))
            if not (self.y_min <= y <= self.y_max):
                # stop at the boundary crossing (linear interpolation from the last point)
                if pts:
                    tp, yp = pts[-1]
                    yb = self.y_max if y > self.y_max else self.y_min
                    tb = tp + (t - tp) * (yb - yp) / (y - yp)
                    pts.append((tb, yb))
                break
            pts.append((t, y))
        m = VMobject().set_points_as_corners([self.c2p(t, y) for t, y in pts])
        m.set_stroke(color, width).set_fill(opacity=0)
        m.left_range = len(pts) < n
        return m


def poly_arrow(points, color=FG, width=3.5, tip=True):
    """A polyline through `points`, with an arrow tip on the last segment."""
    pts = [np.array(p, dtype=float) for p in points]
    line = VMobject().set_points_as_corners(pts[:-1] + [pts[-1]])
    line.set_stroke(color, width).set_fill(opacity=0)
    if not tip:
        return VGroup(line)
    d = pts[-1] - pts[-2]
    d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0], 0])
    s = 0.16
    tri = Polygon(pts[-1], pts[-1] - s * 1.6 * d + s * n, pts[-1] - s * 1.6 * d - s * n)
    tri.set_fill(color, 1).set_stroke(color, 1)
    line.set_points_as_corners(pts[:-1] + [pts[-1] - s * 1.4 * d])
    return VGroup(line, tri)


def sum_junction(r=0.22, color=FG):
    c = Circle(radius=r).set_stroke(color, 3).set_fill(BG, 1)
    x1 = Line(c.point_from_proportion(1 / 8), c.point_from_proportion(5 / 8)).set_stroke(color, 2)
    x2 = Line(c.point_from_proportion(3 / 8), c.point_from_proportion(7 / 8)).set_stroke(color, 2)
    return VGroup(c, x1, x2)


def under_bracket(m, color=YELLOW_C, buff=0.12, depth=0.16):
    """A square bracket drawn under `m` (LaTeX-free stand-in for an underbrace)."""
    l, r, b = m.get_left()[0], m.get_right()[0], m.get_bottom()[1] - buff
    mid = (l + r) / 2
    pts = [[l, b, 0], [l, b - depth, 0], [mid - 0.1, b - depth, 0], [mid, b - depth - 0.12, 0],
           [mid + 0.1, b - depth, 0], [r, b - depth, 0], [r, b, 0]]
    return VMobject().set_points_as_corners(pts).set_stroke(color, 3).set_fill(opacity=0)


def arc_arrow(a, b, angle=TAU / 6, color=FG, width=3.5):
    """Curved arrow from a to b along a circular arc (tip drawn as a filled triangle)."""
    full = ArcBetweenPoints(np.array(a, dtype=float), np.array(b, dtype=float), angle=angle)
    pts = full.get_points()
    end = pts[-1]
    d = end - full.point_from_proportion(0.95)
    d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0], 0])
    s = 0.15
    line = full.copy().pointwise_become_partial(full, 0, 0.93).set_stroke(color, width).set_fill(opacity=0)
    tip = Polygon(end, end - 1.6 * s * d + s * n, end - 1.6 * s * d - s * n).set_fill(color, 1).set_stroke(color, 1)
    return VGroup(line, tip)


def pole_cross(color=RED_C, s=0.13, width=5):
    return VGroup(Line(s * (UL), s * (DR)), Line(s * (UR), s * (DL))).set_stroke(color, width)


class SPlane(VGroup):
    """A small complex plane with shaded stable (left) and unstable (right) half-planes."""
    def __init__(self, xr=(-4, 2), yr=(-2, 2), unit=0.8, shade=True, labels=True):
        self.unit = unit
        self.xr, self.yr = xr, yr
        w, h = (xr[1] - xr[0]) * unit, (yr[1] - yr[0]) * unit
        self.o = np.array([-(xr[0] + xr[1]) / 2 * unit, -(yr[0] + yr[1]) / 2 * unit, 0])
        parts = []
        if shade:
            left = Rectangle(width=-xr[0] * unit, height=h).set_stroke(width=0).set_fill(GREEN_C, 0.13)
            left.move_to(self.o + np.array([xr[0] * unit / 2, 0, 0]))
            right = Rectangle(width=xr[1] * unit, height=h).set_stroke(width=0).set_fill(RED_C, 0.13)
            right.move_to(self.o + np.array([xr[1] * unit / 2, 0, 0]))
            parts += [left, right]
            self.left, self.right = left, right
        re_ax = Line(self.p(xr[0], 0), self.p(xr[1], 0)).set_stroke(DIM, 2)
        im_ax = Line(self.p(0, yr[0]), self.p(0, yr[1])).set_stroke(GREEN_C if shade else DIM, 3 if shade else 2)
        ticks = VGroup()
        for x in range(xr[0], xr[1] + 1):
            if x == 0:
                continue
            ticks.add(Line(self.p(x, 0) + 0.07 * DOWN, self.p(x, 0) + 0.07 * UP).set_stroke(DIM, 2))
            n = label(str(x).replace("-", "−"), 18, DIM).next_to(self.p(x, 0), DOWN, buff=0.12)
            ticks.add(n)
        parts += [re_ax, im_ax, ticks]
        if labels:
            parts.append(label("Re λ", 20, DIM).next_to(self.p(xr[1], 0), UP, buff=0.12).shift(0.25 * LEFT))
            parts.append(label("Im λ", 20, DIM).next_to(self.p(0, yr[1]), RIGHT, buff=0.12).shift(0.2 * DOWN))
        super().__init__(*parts)

    def p(self, x, y=0.0):
        return self.get_center_ref() + np.array([x * self.unit, y * self.unit, 0])

    def get_center_ref(self):
        # self.o is the plane origin relative to the group's initial centre; track moves
        if not hasattr(self, "_anchor"):
            return self.o
        return self._anchor.get_center()

    def finalize(self):
        """Call once after construction: add an invisible anchor at the origin so p() follows moves."""
        self._anchor = Dot(self.o, radius=0).set_opacity(0)
        self.add(self._anchor)
        return self


def splane(**kw):
    return SPlane(**kw).finalize()


def pendulum(theta=0.0, length=2.0, color=FG, bob=TEAL_C):
    """Inverted pendulum: pivot at the group's `pivot` point, rod up at angle theta from vertical."""
    pivot = np.array([0, 0, 0.0])
    tip = pivot + length * np.array([np.sin(theta), np.cos(theta), 0])
    base = Rectangle(width=1.1, height=0.32).set_stroke(DIM, 2).set_fill(FAINT, 1).move_to(pivot + 0.16 * DOWN)
    ground = Line(pivot + 1.1 * LEFT + 0.32 * DOWN, pivot + 1.1 * RIGHT + 0.32 * DOWN).set_stroke(DIM, 2)
    rod = Line(pivot, tip).set_stroke(color, 6)
    ball = Circle(radius=0.2).set_stroke(color, 2).set_fill(bob, 1).move_to(tip)
    hinge = Dot(pivot, radius=0.07).set_fill(color, 1)
    g = VGroup(ground, base, rod, ball, hinge)
    g.rod, g.ball, g.hinge, g.base = rod, ball, hinge, base
    return g


# ---------------------------------------------------------------------------- the scene base

class ControlScene(Scene):
    SEQ_ID = None

    def setup(self):
        super().setup()
        self.frame_count = 0
        self.boundaries = []
        self.spec = next(s for s in SEQUENCES if s["id"] == self.SEQ_ID)
        self.chip_mob = None
        self.step_index = 0

    def play(self, *proto, run_time=None, **kw):
        anims = [prepare_animation(a) for a in proto]
        if run_time is None:
            run_time = max(a.get_run_time() for a in anims)
        super().play(*anims, run_time=run_time * SPEED, **kw)

    def emit_frame(self):
        super().emit_frame()
        if not self.skip_animations:
            self.frame_count += 1

    # -- chips and bookkeeping
    def chip(self, detail=None):
        """Animation swapping the bottom-left chip to the current step's relation."""
        rel = self.spec["steps"][self.step_index]["relation"]
        word, color = CHIP[rel]
        parts = [label(word, 20, color, weight=BOLD)]
        if detail:
            parts.append(label(detail, 20, FG))
        content = VGroup(*parts).arrange(RIGHT, buff=0.28)
        frame = RoundedRectangle(width=content.get_width() + 0.45, height=content.get_height() + 0.3,
                                 corner_radius=0.14).set_stroke(color, 2, opacity=0.8).set_fill(BG, 1)
        frame.move_to(content)
        new = VGroup(frame, content).to_corner(DL, buff=0.32)
        old, self.chip_mob = self.chip_mob, new
        if old is None:
            return FadeIn(new, shift=0.15 * UP)
        return FadeTransform(old, new)

    def settle(self, *mobs):
        self.clear()
        if self.chip_mob is not None:
            self.add(self.chip_mob)
        self.add(*mobs)

    def start(self, *mobs):
        self.add(*mobs)
        self.wait(0.3)
        self.boundaries.append(self.frame_count)

    def step_done(self, *final):
        if final:
            self.settle(*final)
        self.wait(HOLD)
        self.boundaries.append(self.frame_count)
        self.step_index += 1

    def tear_down(self):
        super().tear_down()
        n = len(self.spec["steps"])
        if len(self.boundaries) != n + 1:
            raise RuntimeError(f"{self.SEQ_ID}: {len(self.boundaries) - 1} steps recorded, spec has {n}")
        path = getattr(self.file_writer, "movie_file_path", None)
        if path:
            with open(os.path.splitext(str(path))[0] + ".boundaries.json", "w", encoding="utf-8") as f:
                json.dump({"sequence": self.SEQ_ID, "scene": type(self).__name__, "fps": self.camera.fps,
                           "boundaries": self.boundaries, "frames": self.frame_count}, f)

    # -- token morphs
    def tmorph(self, src, tgt, pairs=(), run_time=1.4, keep_src=False, path_arc=0.0, skip=(), skip_src=()):
        """Animate formula `src` into `tgt` token by token. `pairs` maps src tokens to tgt
        tokens explicitly ((src_key_or_mob, tgt_key_or_mob)); remaining tgt tokens take the
        first unused src token with the same key; others fade in, unused src tokens fade out.
        With keep_src the source stays on screen and copies fly. Tokens in `skip` (target) and
        `skip_src` (source) are left to other animations."""
        def pick(m, key):
            if isinstance(key, tuple):
                return m.k(*key)
            if isinstance(key, str):
                return m.k(key)
            return key
        anims, used_s, used_t = [], set(), set()
        for m in skip:
            used_t.update(id(g) for g in m.family_members_with_points())
        for m in skip_src:
            used_s.update(id(g) for g in m.family_members_with_points())
        for a, b in pairs:
            sa, tb = pick(src, a), pick(tgt, b)
            anims.append(self._pair(sa, tb, keep_src, path_arc))
            for g in (sa.family_members_with_points()):
                used_s.add(id(g))
            for g in tb.family_members_with_points():
                used_t.add(id(g))
        src_toks = [t for t in getattr(src, "toks", []) if len(t)]
        for t in [t for t in getattr(tgt, "toks", []) if len(t)]:
            if any(id(g) in used_t for g in t.family_members_with_points()):
                continue
            match = next((s for s in src_toks if s.key == t.key and
                          not any(id(g) in used_s for g in s.family_members_with_points())), None)
            if match is not None:
                anims.append(self._pair(match, t, keep_src, path_arc))
                for g in match.family_members_with_points():
                    used_s.add(id(g))
            else:
                anims.append(FadeIn(t, shift=0.12 * UP))
        if not keep_src:
            for s in src_toks:
                if not any(id(g) in used_s for g in s.family_members_with_points()):
                    anims.append(FadeOut(s, shift=0.12 * DOWN))
        return AnimationGroup(*anims, run_time=run_time)

    @staticmethod
    def _pair(a, b, keep, arc):
        if keep:
            return TransformFromCopy(a, b, path_arc=arc)
        return ReplacementTransform(a, b, path_arc=arc)


def hbox(m, color=YELLOW_C, buff=0.08):
    return SurroundingRectangle(m, buff=buff).set_stroke(color, 3)


def strike(m, color=RED_C):
    return Line(m.get_corner(DL) + 0.04 * DL, m.get_corner(UR) + 0.04 * UR).set_stroke(color, 5)
