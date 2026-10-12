"""Native interactive ManimGL study guide: second-order linear differential equations.

Launch with launch_native.ps1, or from the repository root:
    .\\.venv\\Scripts\\manimgl.exe native\\study_guide.py SecondOrderStudyGuide --config_file native\\guide_config.yml

Everything on screen comes from ../course.json (shared with the browser guide) and
ode_math.py. Interaction uses the Scene event hooks (on_mouse_press/drag/release/motion,
on_key_press) that ManimGL's window calls while Scene.interact() runs after construct().

Controls: click tabs/buttons, drag sliders.  1/2/3 switch Lessons/Explorer/Quiz,
Left/Right change page (or nudge the selected slider), Up/Down change lesson (or select
a slider), Space reveals a worked step (or plays the time marker), R resets,
A-D answer quiz questions, H toggles help, Q or Esc quits.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)  # so the ManimGL CLI can import the sibling ode_math module

from manimlib import *  # noqa: E402,F403
from pyglet.window import key as KEY  # noqa: E402

import ode_math  # noqa: E402

COURSE_FILE = os.path.join(os.path.dirname(HERE), "course.json")

PAPER = "#FBF7EE"
PANEL = "#F4EDDF"
CARD = "#FFFDF8"
NAVY = "#1F2A44"
MUTED = "#5B6475"
TEAL = "#0F8B8D"
TEAL_TINT = "#DDEFEE"
BLUE = "#2B6CB0"
CORAL = "#C8553D"
CORAL_TINT = "#F8E3DC"
GREEN = "#2F7D4F"
GREEN_TINT = "#E1F1E6"
RULE = "#D8CDB8"
WHITE_ = "#FFFFFF"
UI_FONT = "Segoe UI"
MONO_FONT = "Consolas"

# Measured with TexText(r"\rule{10cm}{1pt}"): scene units per cm per font-size point.
TEX_UNITS_PER_CM_PER_FS = 0.0283465

# Screen regions (frame is 14.22 x 8 units; 1 unit = 90 px at 1280x720).
FW, FH = FRAME_WIDTH, FRAME_HEIGHT
LEFT_X, RIGHT_X = -FW / 2, FW / 2
TOPBAR_H = 0.62
CONTENT_LEFT, CONTENT_RIGHT = -3.6, 6.8
CONTENT_BOTTOM = -2.62
CRUMB_Y = 3.07
NAV_Y = -3.12
FOOTER_Y = -3.74

BODY_FS = 28
MATH_FS = 32


# ---------------------------------------------------------------- helpers

def ui_text(s, size=20, color=NAVY, weight=NORMAL, font=UI_FONT, line_width=None):
    t = Text(s, font=font, font_size=size, weight=weight, line_width=line_width)
    return t.set_color(color)


def minipage(body, width_units, size):
    # 1.5% margin: italic glyphs can overhang the minipage edge slightly
    width_cm = 0.985 * width_units / (TEX_UNITS_PER_CM_PER_FS * size)
    return r"\begin{minipage}{%.2fcm}\raggedright %s\end{minipage}" % (width_cm, body)


class GlyphFont:
    """Per-character Pango (monospace) glyph templates for labels that change every frame.

    Building a label copies cached glyphs instead of rendering a new Text, so dragging a
    slider or playing the time marker never re-runs Pango or writes new cache entries.
    """

    def __init__(self, size, color=NAVY):
        self.size = size
        self.color = color
        one = Text("0", font=MONO_FONT, font_size=size)
        two = Text("00", font=MONO_FONT, font_size=size)
        self.advance = two.get_width() - one.get_width()
        self.height = Text("0", font=MONO_FONT, font_size=size).get_height()
        self.templates = {}

    def glyph(self, ch):
        if ch == " ":
            return None
        if ch not in self.templates:
            full = Text("H" + ch, font=MONO_FONT, font_size=self.size)
            h, g = full[0], VGroup(*full[1:])
            if len(g.get_points()) == 0 and not g.submobjects:
                self.templates[ch] = None
                return None
            dx = g.get_left()[0] - h.get_left()[0] - self.advance
            dy = g.get_bottom()[1] - h.get_bottom()[1]
            g.shift(-g.get_corner(DL))
            self.templates[ch] = (g, dx, dy)
        return self.templates[ch]


class GlyphLabel(VGroup):
    """A label built from GlyphFont templates, anchored at its left baseline."""

    def __init__(self, font, text="", color=None):
        super().__init__()
        self.font = font
        self.color_ = color or font.color
        self.anchor = VectorizedPoint(ORIGIN)
        self.glyphs = VGroup()
        self.add(self.anchor, self.glyphs)
        self.text = None
        self.set_text(text)

    def set_text(self, text, color=None):
        if color is not None:
            self.color_ = color
        if text == self.text and color is None:
            return self
        self.text = text
        origin = self.anchor.get_center()
        pieces = []
        for i, ch in enumerate(text):
            tpl = self.font.glyph(ch)
            if tpl is None:
                continue
            g, dx, dy = tpl
            pieces.append(g.copy().shift(origin + RIGHT * (i * self.font.advance + dx) + UP * dy))
        self.glyphs.set_submobjects(pieces)
        self.glyphs.set_fill(self.color_, 1).set_stroke(width=0)
        return self

    def width_of(self, text=None):
        return len(self.text if text is None else text) * self.font.advance

    def place(self, left_baseline):
        self.shift(np.array(left_baseline) - self.anchor.get_center())
        return self


class Button(VGroup):
    STYLES = {
        # kind/state: (fill, stroke, text)
        "normal": (CARD, RULE, NAVY),
        "primary": (TEAL, TEAL, WHITE_),
        "tab": ("#2C3A5A", "#2C3A5A", "#E8EDF6"),
        "tab_active": (TEAL, TEAL, WHITE_),
        "selected": (TEAL_TINT, TEAL, NAVY),
        "correct": (GREEN_TINT, GREEN, NAVY),
        "wrong": (CORAL_TINT, CORAL, NAVY),
        "disabled": (PANEL, RULE, "#A5A9B3"),
    }

    def __init__(self, label, width, height, action=None, size=20, kind="normal",
                 label_mob=None, align="center", name=None):
        super().__init__()
        self.action = action
        self.name = name or (label if isinstance(label, str) else "button")
        self.kind = kind
        self.state = kind
        self.enabled = True
        self.hovered = False
        self.bg = RoundedRectangle(width=width, height=height, corner_radius=min(0.1, height / 3))
        self.label = label_mob if label_mob is not None else ui_text(label, size)
        max_w, max_h = width - 0.24, height - 0.1
        if self.label.get_width() > max_w:
            self.label.set_width(max_w)
        if self.label.get_height() > max_h:
            self.label.set_height(max_h)
        if align == "left":
            self.label.move_to(self.bg).align_to(self.bg, LEFT).shift(0.16 * RIGHT)
        else:
            self.label.move_to(self.bg)
        self.add(self.bg, self.label)
        self.apply_style()

    def set_state(self, state):
        self.state = state
        self.apply_style()
        return self

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.apply_style()
        return self

    def apply_style(self):
        fill, stroke, text = self.STYLES["disabled" if not self.enabled else self.state]
        self.bg.set_fill(fill, 1)
        width = 2.5
        if self.hovered and self.enabled:
            stroke, width = BLUE, 3.5
        self.bg.set_stroke(stroke, width)
        self.label.set_fill(text, 1)
        self.label.set_stroke(width=0)

    def set_hover(self, hovered):
        if hovered != self.hovered:
            self.hovered = hovered
            self.apply_style()

    def contains(self, point):
        x, y = point[0], point[1]
        left, right = self.bg.get_left()[0], self.bg.get_right()[0]
        bottom, top = self.bg.get_bottom()[1], self.bg.get_top()[1]
        return left <= x <= right and bottom <= y <= top

    def click(self):
        if self.enabled and self.action is not None:
            self.action()
            return True
        return False


class Slider(VGroup):
    def __init__(self, spec, width, glyphs, on_change):
        super().__init__()
        self.key = spec["key"]
        self.lo, self.hi, self.step = spec["min"], spec["max"], spec["step"]
        self.default = spec["default"]
        self.on_change = on_change
        self.value = self.default
        self.selected = False
        self.name = ui_text(spec["label"], 20, NAVY)
        # Filled rectangles, not stroked lines: ManimGL renders a group's strokes after its
        # fills, so a stroked track would show through the knob.
        self.width = width
        self.track = Rectangle(width=width, height=0.075).set_fill(RULE, 1).set_stroke(width=0)
        self.track.move_to(width / 2 * RIGHT)
        self.fill_line = Rectangle(width=0.01, height=0.075).set_fill(TEAL, 1).set_stroke(width=0)
        self.knob = Circle(radius=0.13).set_fill(TEAL, 1).set_stroke(WHITE_, 2.5)
        self.value_label = GlyphLabel(glyphs, ode_math.fmt(self.value))
        self.name.next_to(self.track_start(), UP, buff=0.16, aligned_edge=LEFT)
        self.value_label.place(self.track_end() + UP * 0.2 + LEFT * self.value_label.width_of("-0.00"))
        self.add(self.track, self.fill_line, self.name, self.value_label, self.knob)
        self.set_value(self.value, notify=False)

    def track_start(self):
        return self.track.get_left()

    def track_end(self):
        return self.track.get_right()

    def snap(self, v):
        v = min(max(v, self.lo), self.hi)
        v = self.lo + round((v - self.lo) / self.step) * self.step
        return round(min(max(v, self.lo), self.hi), 10)

    def set_value(self, v, notify=True):
        self.value = self.snap(v)
        p = (self.value - self.lo) / (self.hi - self.lo)
        start, end = self.track_start(), self.track_end()
        pos = start + p * (end - start)
        self.knob.move_to(pos)
        self.fill_line.set_width(max(p * self.width, 0.01), stretch=True)
        self.fill_line.move_to(start, aligned_edge=LEFT)
        self.value_label.set_text(ode_math.fmt(self.value))
        if notify:
            self.on_change()
        return self

    def value_from_x(self, x):
        start, end = self.track_start()[0], self.track_end()[0]
        return self.lo + (x - start) / (end - start) * (self.hi - self.lo)

    def hit(self, point):
        start, end = self.track_start(), self.track_end()
        return (start[0] - 0.2 <= point[0] <= end[0] + 0.2) and abs(point[1] - start[1]) <= 0.26

    def set_selected(self, selected):
        self.selected = selected
        self.name.set_color(TEAL if selected else NAVY)
        self.knob.set_stroke(NAVY if selected else WHITE_, 3 if selected else 2.5)


class Screen:
    """One native screen of a lesson page (long pages are split into several)."""

    def __init__(self, static, example=None, scale=1.0):
        self.static = static
        self.example = example
        self.scale = scale


class ExampleState:
    def __init__(self, example_id, rows, badges):
        self.id = example_id
        self.rows = rows
        self.badges = badges
        self.revealed = 0


# ---------------------------------------------------------------- the scene

class SecondOrderStudyGuide(Scene):
    drag_to_pan = False
    default_camera_config = dict(background_color=PAPER)

    # ---- setup

    def setup(self):
        with open(COURSE_FILE, encoding="utf-8") as f:
            self.course = json.load(f)
        self.examples = {ex["id"]: ex for ex in self.course["examples"]}
        self.flat_pages = [(li, pi) for li, lesson in enumerate(self.course["lessons"])
                           for pi in range(len(lesson["pages"]))]
        self.lesson_first_page = {}
        for pos, (li, pi) in enumerate(self.flat_pages):
            self.lesson_first_page.setdefault(li, pos)
        self.view = None
        self.page_pos = 0
        self.screen_idx = 0
        self.screens_cache = {}
        self.current_screen_mobs = []
        self.tex_errors = []
        self.help_visible = False
        self.active_slider = None
        self.hovered_button = None
        self.selected_slider = 0
        self.playing = False
        self.marker_t = 0.0
        self.quiz_index = 0
        self.quiz_state = {}
        self.quiz_cache = {}
        self.current_quiz_mobs = []
        self.event_log = []
        self.glyphs = GlyphFont(20, NAVY)
        self.glyphs_small = GlyphFont(17, MUTED)

    def construct(self):
        self.build_chrome()
        self.build_lessons_view()
        self.build_explorer_view()
        self.build_quiz_view()
        self.build_help_overlay()
        self.show_view("lessons")

    # ---- TeX builders (static content only; compiled once, then cached by ManimGL)

    def safe_texttext(self, body, size, fallback):
        try:
            mob = TexText(body, font_size=size)
        except Exception as err:  # keep the guide usable if one string fails to compile
            self.tex_errors.append(f"{fallback[:60]}: {err}")
            mob = ui_text(fallback, 18, CORAL, line_width=10)
        return mob.set_color(NAVY)

    def paragraph(self, text, width, size=BODY_FS):
        return self.safe_texttext(minipage(text, width, size), size, text)

    def bullet_list(self, items, width, size=BODY_FS):
        body = (r"\begin{itemize}\setlength{\itemsep}{2pt}\setlength{\parskip}{0pt}"
                + "".join(r"\item " + it for it in items) + r"\end{itemize}")
        return self.safe_texttext(minipage(body, width, size), size, " / ".join(items))

    def display_math(self, tex, max_width, size=MATH_FS):
        try:
            mob = Tex(tex, font_size=size).set_color(NAVY)
        except Exception as err:
            self.tex_errors.append(f"{tex[:60]}: {err}")
            mob = ui_text(tex, 18, CORAL)
        if mob.get_width() > max_width:
            mob.set_width(max_width)
        return mob

    # ---- chrome: top bar, tabs, footer

    def build_chrome(self):
        bar = Rectangle(width=FW, height=TOPBAR_H).set_fill(NAVY, 1).set_stroke(width=0)
        bar.to_edge(UP, buff=0)
        title = ui_text("Second-Order Linear ODEs", 22, WHITE_, BOLD)
        title.move_to(bar).align_to(bar, LEFT).shift(0.3 * RIGHT)
        self.tabs = {}
        x = RIGHT_X - 0.25
        for key, label in reversed([("lessons", "Lessons  1"), ("explorer", "Explorer  2"),
                                    ("quiz", "Quiz  3"), ("help", "Help  H")]):
            action = self.toggle_help if key == "help" else (lambda k=key: self.show_view(k))
            btn = Button(label, 1.75, 0.44, action, size=18, kind="tab", name=f"tab:{key}")
            btn.move_to([x - 0.875, bar.get_center()[1], 0])
            x -= 1.9
            self.tabs[key] = btn
        footer = ui_text("Left/Right page or slider  ·  Up/Down lesson or slider  ·  Space step/play"
                         "  ·  R reset  ·  A-D answer  ·  H help  ·  Q or Esc quit", 17, MUTED)
        footer.move_to([0, FOOTER_Y, 0])
        rule = Line([LEFT_X + 0.3, FOOTER_Y + 0.24, 0], [RIGHT_X - 0.3, FOOTER_Y + 0.24, 0]).set_stroke(RULE, 1.5)
        self.chrome = VGroup(bar, title, *self.tabs.values(), rule, footer)
        self.add(self.chrome)

    def show_view(self, view):
        if self.help_visible:
            self.toggle_help()
        if self.view == view:
            return
        self.active_slider = None
        if self.view is not None:
            self.remove(self.view_groups[self.view])
            if self.view == "lessons":
                self.remove(*self.current_screen_mobs)
            if self.view == "quiz":
                self.remove(*self.current_quiz_mobs)
        if self.view == "explorer":
            self.playing = False
            self.update_play_button()
        self.view = view
        self.add(self.view_groups[view])
        for key, tab in self.tabs.items():
            if key != "help":
                tab.set_state("tab_active" if key == view else "tab")
        if view == "lessons":
            self.show_screen()
        elif view == "quiz":
            self.show_question()
        self.log(f"view:{view}")

    @property
    def view_groups(self):
        return {"lessons": self.lessons_group, "explorer": self.explorer_group, "quiz": self.quiz_group}

    # ---- lessons

    def build_lessons_view(self):
        side = RoundedRectangle(width=3.05, height=6.35, corner_radius=0.12)
        side.set_fill(PANEL, 1).set_stroke(RULE, 1.5)
        side.move_to([LEFT_X + 0.2 + 1.525, 0.05, 0])
        head = ui_text("Lessons", 20, MUTED, BOLD).move_to(side.get_top() + DOWN * 0.3).align_to(side, LEFT).shift(0.2 * RIGHT)
        self.lesson_buttons = []
        y = head.get_bottom()[1] - 0.48
        for li, lesson in enumerate(self.course["lessons"]):
            num = ui_text(str(lesson["number"]), 20, NAVY, BOLD)
            name = ui_text(lesson.get("nav", lesson["title"]), 19, NAVY, line_width=2.1)
            label = VGroup(num, name)
            name.next_to(num, RIGHT, buff=0.18).align_to(num, UP)
            btn = Button(None, 2.8, 0.78, lambda li=li: self.go_lesson(li), label_mob=label, align="left",
                         name=f"lesson:{li}")
            btn.move_to([side.get_center()[0], y, 0])
            y -= 0.88
            self.lesson_buttons.append(btn)
        self.page_label = ui_text(" ", 18, MUTED)
        self.prev_btn = Button("◀  Prev", 1.6, 0.48, self.prev_page, name="prev")
        self.next_btn = Button("Next  ▶", 1.6, 0.48, self.next_page, kind="primary", name="next")
        self.prev_btn.move_to([CONTENT_LEFT + 0.8, NAV_Y, 0])
        self.next_btn.move_to([CONTENT_RIGHT - 0.8, NAV_Y, 0])
        self.reveal_btn = Button("Next step  (Space)", 2.45, 0.48, self.reveal_step, kind="primary",
                                 name="reveal")
        self.hide_btn = Button("Hide steps  (R)", 1.95, 0.48, self.hide_steps, name="hide")
        self.reveal_btn.move_to([0.8, NAV_Y, 0])
        self.hide_btn.move_to([3.2, NAV_Y, 0])
        self.lessons_group = VGroup(side, head, *self.lesson_buttons, self.prev_btn, self.next_btn)
        self.step_controls = VGroup(self.reveal_btn, self.hide_btn)

    def lesson_buttons_active(self):
        btns = list(self.lesson_buttons) + [self.prev_btn, self.next_btn]
        screen = self.current_screen()
        if screen is not None and screen.example is not None:
            btns += [self.reveal_btn, self.hide_btn]
        return btns

    def build_screens(self, pos):
        if pos in self.screens_cache:
            return self.screens_cache[pos]
        li, pi = self.flat_pages[pos]
        lesson = self.course["lessons"][li]
        page = lesson["pages"][pi]
        width = CONTENT_RIGHT - CONTENT_LEFT
        units = []  # (mobject, centered?, ExampleState or None)
        for block in page["blocks"]:
            kind = block["type"]
            if kind == "p":
                units.append((self.paragraph(block["text"], width), False, None))
            elif kind == "math":
                units.append((self.display_math(block["tex"], width), True, None))
            elif kind == "list":
                units.append((self.bullet_list(block["items"], width), False, None))
            elif kind == "note":
                units.append((self.note_box(block["text"], width), False, None))
            elif kind == "video":
                name = os.path.basename(block["src"])
                txt = self.paragraph(r"\textit{Animated in the browser guide (" + name + "):} " + block["caption"],
                                     width, 22)
                txt.set_color(MUTED)
                units.append((txt, False, None))
            elif kind == "example":
                mob, state = self.example_unit(self.examples[block["id"]], width)
                units.append((mob, False, state))
        crumb = ui_text(f"Lesson {lesson['number']} of {len(self.course['lessons'])}  ·  {lesson['title']}",
                        18, TEAL, BOLD)
        screens, current, used = [], [], 0.0
        gap = 0.26

        def heading(cont):
            h = ui_text(page["heading"] + ("  (continued)" if cont else ""), 30, NAVY, BOLD)
            if h.get_width() > width:
                h.set_width(width)
            return h

        def body_top(cont):
            h = heading(cont)
            return CRUMB_Y - crumb.get_height() / 2 - 0.14 - h.get_height() - 0.26

        def finish(items, cont):
            crumb_c = crumb.copy().move_to([0, CRUMB_Y, 0]).align_to([CONTENT_LEFT, 0, 0], LEFT)
            h = heading(cont).next_to(crumb_c, DOWN, buff=0.14, aligned_edge=LEFT)
            top = h.get_bottom()[1] - 0.26
            body = VGroup()
            example, scale = None, 1.0
            avail = top - CONTENT_BOTTOM
            for mob, centered, state in items:
                if mob.get_height() > avail:
                    scale = min(scale, avail / mob.get_height())
                    mob.scale(avail / mob.get_height())
                mob.next_to([CONTENT_LEFT, top, 0], DOWN, buff=0, aligned_edge=LEFT)
                mob.align_to([CONTENT_LEFT, 0, 0], LEFT)
                if centered:
                    mob.set_x((CONTENT_LEFT + CONTENT_RIGHT) / 2)
                top = mob.get_bottom()[1] - gap
                body.add(mob)
                if state is not None:
                    example = state
            static = VGroup(crumb_c, h)
            for mob, _, state in items:
                if state is None:
                    static.add(mob)
                else:
                    static.add(*[m for m in mob.submobjects if m not in state.rows])
            screens.append(Screen(static, example, scale))

        for unit in units:
            h = unit[0].get_height()
            if current and used + gap + h > body_top(len(screens) > 0) - CONTENT_BOTTOM:
                finish(current, cont=len(screens) > 0)
                current, used = [], 0.0
            used += (gap if current else 0) + h
            current.append(unit)
        finish(current, cont=len(screens) > 0)
        self.screens_cache[pos] = screens
        return screens

    def note_box(self, text, width):
        body = self.paragraph(text, width - 0.5, 26)
        box = RoundedRectangle(width=width, height=body.get_height() + 0.34, corner_radius=0.1)
        box.set_fill(TEAL_TINT, 1).set_stroke(TEAL, 0)
        bar = Rectangle(width=0.07, height=box.get_height()).set_fill(TEAL, 1).set_stroke(width=0)
        bar.align_to(box, LEFT).align_to(box, UP)
        body.move_to(box).align_to(box, LEFT).shift(0.3 * RIGHT)
        return VGroup(box, bar, body)

    def example_unit(self, ex, width):
        problem = self.paragraph(r"\textbf{Worked example: " + ex["title"] + r".}\ " + ex["problem"], width)
        problem.move_to([CONTENT_LEFT, 0, 0], aligned_edge=UL)
        rows, badges = [], []
        group = VGroup(problem)
        top = problem.get_bottom()[1] - 0.24
        text_w, math_x, math_w = 4.75, CONTENT_LEFT + 5.45, width - 5.45
        for k, step in enumerate(ex["steps"], start=1):
            badge = VGroup(Circle(radius=0.17).set_fill(TEAL, 1).set_stroke(width=0),
                           ui_text(str(k), 18, WHITE_, BOLD))
            text = self.paragraph(step["text"], text_w if step["tex"] else width - 0.55, 25)
            parts = [text]
            text.next_to([CONTENT_LEFT + 0.5, top, 0], DOWN, buff=0, aligned_edge=LEFT)
            if step["tex"]:
                formula = self.display_math(step["tex"], math_w, 29)
                formula.next_to([math_x, top, 0], DOWN, buff=0, aligned_edge=LEFT)
                if formula.get_height() < text.get_height():
                    formula.set_y(text.get_center()[1])
                parts.append(formula)
            row = VGroup(*parts)
            badge.move_to([CONTENT_LEFT + 0.18, row.get_top()[1] - 0.17, 0])
            badge[1].move_to(badge[0])
            rows.append(row)
            badges.append(badge)
            group.add(badge, row)
            top = row.get_bottom()[1] - 0.2
        group.move_to(ORIGIN, aligned_edge=UL)
        return group, ExampleState(ex["id"], rows, badges)

    def current_screen(self):
        screens = self.screens_cache.get(self.page_pos)
        if not screens:
            return None
        return screens[self.screen_idx]

    def show_screen(self):
        self.remove(*self.current_screen_mobs)
        screens = self.build_screens(self.page_pos)
        self.screen_idx = min(self.screen_idx, len(screens) - 1)
        screen = screens[self.screen_idx]
        li, pi = self.flat_pages[self.page_pos]
        lesson = self.course["lessons"][li]
        part = f"  ·  part {self.screen_idx + 1}/{len(screens)}" if len(screens) > 1 else ""
        new_label = ui_text(f"Page {pi + 1} of {len(lesson['pages'])}{part}", 18, MUTED)
        mobs = [screen.static]
        if screen.example is not None:
            ex = screen.example
            for i, (badge, row) in enumerate(zip(ex.badges, ex.rows)):
                badge[0].set_fill(TEAL if i < ex.revealed else RULE, 1)
            mobs += ex.rows[:ex.revealed]
            mobs.append(self.step_controls)
            self.reveal_btn.set_enabled(ex.revealed < len(ex.rows))
            self.hide_btn.set_enabled(ex.revealed > 0)
            if new_label.get_width() > 1.8:
                new_label.set_width(1.8)
            new_label.move_to([-1.42, NAV_Y, 0])
        else:
            new_label.move_to([(CONTENT_LEFT + CONTENT_RIGHT) / 2, NAV_Y, 0])
        self.page_label = new_label
        mobs.append(self.page_label)
        self.current_screen_mobs = mobs
        self.add(*mobs)
        for i, btn in enumerate(self.lesson_buttons):
            btn.set_state("selected" if i == li else "normal")
        last = self.page_pos == len(self.flat_pages) - 1 and self.screen_idx == len(screens) - 1
        self.prev_btn.set_enabled(not (self.page_pos == 0 and self.screen_idx == 0))
        self.next_btn.set_enabled(not last)

    def next_page(self):
        screens = self.build_screens(self.page_pos)
        if self.screen_idx < len(screens) - 1:
            self.screen_idx += 1
        elif self.page_pos < len(self.flat_pages) - 1:
            self.page_pos += 1
            self.screen_idx = 0
        self.show_screen()
        self.log(f"page:{self.page_pos}.{self.screen_idx}")

    def prev_page(self):
        if self.screen_idx > 0:
            self.screen_idx -= 1
        elif self.page_pos > 0:
            self.page_pos -= 1
            self.screen_idx = len(self.build_screens(self.page_pos)) - 1
        self.show_screen()
        self.log(f"page:{self.page_pos}.{self.screen_idx}")

    def go_lesson(self, li):
        li = max(0, min(li, len(self.course["lessons"]) - 1))
        self.page_pos = self.lesson_first_page[li]
        self.screen_idx = 0
        self.show_screen()
        self.log(f"lesson:{li}")

    def reveal_step(self):
        screen = self.current_screen()
        if screen is None or screen.example is None:
            return
        ex = screen.example
        if ex.revealed < len(ex.rows):
            ex.revealed += 1
            self.show_screen()
            self.log(f"reveal:{ex.id}:{ex.revealed}")

    def hide_steps(self):
        screen = self.current_screen()
        if screen is None or screen.example is None:
            return
        screen.example.revealed = 0
        self.show_screen()
        self.log(f"hide:{screen.example.id}")

    # ---- explorer

    def build_explorer_view(self):
        cfg = self.course["explorer"]
        self.t_max = float(cfg["t_max"])
        title = ui_text(cfg["title"], 24, NAVY, BOLD).move_to([0, 3.12, 0]).align_to([LEFT_X + 0.4, 0, 0], LEFT)
        scope = self.paragraph(cfg["scope"], FW - 0.8, 23).set_color(MUTED)
        scope.next_to(title, DOWN, buff=0.12, aligned_edge=LEFT)

        # plot frame
        self.plot_left, self.plot_right = LEFT_X + 1.05, 0.95
        self.plot_top, self.plot_bottom = 1.6, -2.0
        self.plot_mid = (self.plot_top + self.plot_bottom) / 2
        card = RoundedRectangle(width=self.plot_right - self.plot_left + 1.15,
                                height=self.plot_top - self.plot_bottom + 1.0, corner_radius=0.12)
        card.set_fill(CARD, 1).set_stroke(RULE, 1.5)
        card.move_to([(self.plot_left + self.plot_right) / 2 - 0.3, self.plot_mid + 0.1, 0])
        self.axes_group = VGroup()
        self.bound = None
        self.curve = VMobject().set_stroke(TEAL, 4.5)
        self.marker_line = Line(UP, DOWN).set_stroke(BLUE, 2, opacity=0.6)
        self.marker_dot = Dot(radius=0.09).set_fill(BLUE, 1).set_stroke(WHITE_, 2)

        # readouts under the plot
        ry = self.plot_bottom - 0.86
        self.eq_label = GlyphLabel(self.glyphs).place([self.plot_left - 0.6, ry, 0])
        self.roots_label = GlyphLabel(self.glyphs).place([self.plot_left - 0.6, ry - 0.4, 0])
        self.disc_label = GlyphLabel(self.glyphs).place([self.plot_left + 3.35, ry - 0.4, 0])
        self.marker_label = GlyphLabel(self.glyphs, color=BLUE).place([self.plot_left + 3.35, ry, 0])
        self.damping_texts = {k: ui_text(v, 19, TEAL, BOLD) for k, v in ode_math.DAMPING_LABELS.items()}
        self.damping_anchor = np.array([self.plot_right, self.plot_top + 0.32, 0])
        self.damping_label = VGroup()
        self.zero_text = ui_text(cfg["zero_note"], 18, BLUE)
        self.zero_text.move_to([self.plot_left + 0.25, self.plot_mid + 0.45, 0], aligned_edge=LEFT)
        self.zero_note = VGroup()

        # sliders and buttons on the right
        px0, pw = 1.85, 4.85
        self.sliders = []
        y = 1.62
        for spec in cfg["sliders"]:
            s = Slider(spec, pw, self.glyphs, self.on_slider_change)
            s.shift(np.array([px0, y, 0]) - s.track_start())
            self.sliders.append(s)
            y -= 0.62
        y += 0.62 - 0.5
        self.preset_buttons = []
        bw = (pw - 0.15) / 2
        for i, preset in enumerate(cfg["presets"]):
            btn = Button(preset["label"], bw, 0.46, lambda p=preset: self.apply_preset(p), size=19,
                         name=f"preset:{preset['id']}")
            btn.move_to([px0 + bw / 2 + (i % 2) * (bw + 0.15), y - (i // 2) * 0.53, 0])
            self.preset_buttons.append(btn)
        y -= 1.0
        self.reset_btn = Button("Reset  (R)", bw, 0.46, self.reset_explorer, size=19, name="reset")
        self.play_btn = Button("Play marker  (Space)", bw, 0.46, self.toggle_play, kind="primary", size=19,
                               name="play")
        self.reset_btn.move_to([px0 + bw / 2, y, 0])
        self.play_btn.move_to([px0 + bw * 1.5 + 0.15, y, 0])
        policy = ui_text(cfg["preset_policy"], 17, MUTED, line_width=pw)
        policy.next_to(self.reset_btn, DOWN, buff=0.12).align_to([px0, 0, 0], LEFT)
        self.explorer_buttons = self.preset_buttons + [self.reset_btn, self.play_btn]
        self.explorer_static = VGroup(title, scope, card, policy)
        self.explorer_group = VGroup(
            self.explorer_static, self.axes_group, self.curve, self.marker_line, self.marker_dot,
            self.eq_label, self.roots_label, self.disc_label, self.damping_label, self.zero_note, self.marker_label,
            *self.sliders, *self.explorer_buttons,
        )
        self.add_updater_for_marker()
        self.sliders[self.selected_slider].set_selected(True)
        self.refresh_explorer()

    def add_updater_for_marker(self):
        def advance(mob, dt):
            if self.playing and dt > 0:
                self.marker_t = (self.marker_t + dt) % self.t_max
                self.update_marker()
        self.marker_dot.add_updater(advance)

    def params(self):
        return {s.key: s.value for s in self.sliders}

    def to_screen(self, t, y):
        x = self.plot_left + (t / self.t_max) * (self.plot_right - self.plot_left)
        half = (self.plot_top - self.plot_bottom) / 2
        return np.array([x, self.plot_mid + (y / self.bound) * half, 0])

    def rebuild_axes(self):
        g = VGroup()
        half = (self.plot_top - self.plot_bottom) / 2
        for frac in (-1, -0.5, 0.5, 1):
            yy = self.plot_mid + frac * half
            g.add(Line([self.plot_left, yy, 0], [self.plot_right, yy, 0]).set_stroke(RULE, 1))
            lab = ui_text(ode_math.fmt(frac * self.bound).rstrip("0").rstrip("."), 16, MUTED)
            g.add(lab.next_to([self.plot_left, yy, 0], LEFT, buff=0.12))
        for t in range(0, int(self.t_max) + 1):
            x = self.to_screen(t, 0)[0]
            g.add(Line([x, self.plot_mid - 0.06, 0], [x, self.plot_mid + 0.06, 0]).set_stroke(MUTED, 1.5))
            if t > 0:
                g.add(ui_text(str(t), 16, MUTED).next_to([x, self.plot_bottom, 0], DOWN, buff=0.1))
        g.add(Line([self.plot_left, self.plot_mid, 0], [self.plot_right + 0.1, self.plot_mid, 0]).set_stroke(MUTED, 2))
        g.add(Line([self.plot_left, self.plot_bottom, 0], [self.plot_left, self.plot_top, 0]).set_stroke(MUTED, 2))
        g.add(ui_text("0", 16, MUTED).next_to([self.plot_left, self.plot_mid, 0], LEFT, buff=0.12))
        g.add(ui_text("t", 18, MUTED, font=MONO_FONT).next_to([self.plot_right + 0.1, self.plot_mid, 0], RIGHT, buff=0.08))
        g.add(ui_text("y(t)", 18, MUTED, font=MONO_FONT).next_to([self.plot_left, self.plot_top, 0], UP, buff=0.08))
        self.axes_group.set_submobjects(g.submobjects)

    def refresh_explorer(self):
        p = self.params()
        a, b, c, y0, v0 = p["a"], p["b"], p["c"], p["y0"], p["v0"]
        pts = ode_math.sample(a, b, c, y0, v0, self.t_max, 400)
        bound = ode_math.nice_bound(max(abs(y) for _, y in pts))
        if bound != self.bound:
            self.bound = bound
            self.rebuild_axes()
        self.curve.set_points_as_corners([self.to_screen(t, y) for t, y in pts])
        self.curve_samples = pts
        self.eq_label.set_text(f"{ode_math.fmt(a)} y'' + {ode_math.fmt(b)} y' + {ode_math.fmt(c)} y = 0")
        self.roots_label.set_text(ode_math.roots_text(a, b, c).replace("₁", "1").replace("₂", "2"))
        self.disc_label.set_text(f"b^2 - 4ac = {ode_math.fmt(b * b - 4 * a * c)}")
        self.damping_key = ode_math.analyze(a, b, c)["damping"]
        new = self.damping_texts[self.damping_key]
        if not self.damping_label.submobjects or self.damping_label[0] is not new:
            new.move_to(self.damping_anchor, aligned_edge=RIGHT)
            self.damping_label.set_submobjects([new])
        self.is_zero_solution = y0 == 0 and v0 == 0
        self.zero_note.set_submobjects([self.zero_text] if self.is_zero_solution else [])
        self.update_marker()

    def update_marker(self):
        p = self.params()
        y = ode_math.solution(self.marker_t, p["a"], p["b"], p["c"], p["y0"], p["v0"])
        pos = self.to_screen(self.marker_t, y)
        self.marker_dot.move_to(pos)
        self.marker_line.put_start_and_end_on(np.array([pos[0], self.plot_bottom, 0.0]),
                                              np.array([pos[0], self.plot_top, 0.0]))
        self.marker_label.set_text(f"t = {ode_math.fmt(self.marker_t)}   y(t) = {ode_math.fmt(y)}")

    def on_slider_change(self):
        self.refresh_explorer()

    def apply_preset(self, preset):
        for s in self.sliders:
            if s.key in ("a", "b", "c"):
                s.set_value(preset[s.key], notify=False)
        self.refresh_explorer()
        self.log(f"preset:{preset['id']}")

    def reset_explorer(self):
        for s in self.sliders:
            s.set_value(s.default, notify=False)
        self.playing = False
        self.marker_t = 0.0
        self.update_play_button()
        self.refresh_explorer()
        self.log("explorer:reset")

    def toggle_play(self):
        self.playing = not self.playing
        self.update_play_button()
        self.log(f"play:{self.playing}")

    def update_play_button(self):
        if not hasattr(self, "play_btn"):
            return
        label = ui_text("Pause marker  (Space)" if self.playing else "Play marker  (Space)", 19, WHITE_)
        label.move_to(self.play_btn.bg)
        self.play_btn.label.become(label)
        self.play_btn.apply_style()

    def select_slider(self, idx):
        self.sliders[self.selected_slider].set_selected(False)
        self.selected_slider = idx % len(self.sliders)
        self.sliders[self.selected_slider].set_selected(True)

    # ---- quiz

    def build_quiz_view(self):
        self.quiz_prev = Button("◀  Prev", 1.6, 0.48, lambda: self.go_question(self.quiz_index - 1), name="quiz:prev")
        self.quiz_retry = Button("Try again  (R)", 2.2, 0.48, self.retry_question, name="quiz:retry")
        self.quiz_next = Button("Next  ▶", 1.6, 0.48, lambda: self.go_question(self.quiz_index + 1),
                                kind="primary", name="quiz:next")
        self.quiz_reset = Button("Reset quiz", 1.9, 0.48, self.reset_quiz, name="quiz:reset")
        self.quiz_prev.move_to([LEFT_X + 1.2, NAV_Y, 0])
        self.quiz_retry.move_to([-2.3, NAV_Y, 0])
        self.quiz_reset.move_to([0.1, NAV_Y, 0])
        self.quiz_next.move_to([RIGHT_X - 1.2, NAV_Y, 0])
        self.quiz_group = VGroup(self.quiz_prev, self.quiz_retry, self.quiz_reset, self.quiz_next)

    def quiz_mobs(self, qi):
        if qi in self.quiz_cache:
            return self.quiz_cache[qi]
        q = self.course["quiz"][qi]
        width = FW - 0.9
        prompt = self.paragraph(q["prompt"], width, 30)
        prompt.move_to([0, 2.55, 0], aligned_edge=UP).align_to([LEFT_X + 0.45, 0, 0], LEFT)
        choices = []
        top = prompt.get_bottom()[1] - 0.3
        for i, choice in enumerate(q["choices"]):
            label = self.paragraph(r"\textbf{" + "ABCD"[i] + r".}\quad " + choice, width - 0.5, 27)
            h = max(0.6, label.get_height() + 0.26)
            btn = Button(None, width, h, lambda i=i: self.answer(i), label_mob=label, align="left",
                         name=f"choice:{i}")
            btn.move_to([0, top - h / 2, 0])
            top -= h + 0.13
            choices.append(btn)
        feedback = []
        for i, text in enumerate(q["feedback"]):
            ok = i == q["answer"]
            head = ui_text("Correct" if ok else "Not quite", 20, GREEN if ok else CORAL, BOLD)
            body = self.paragraph(text, width - 0.5, 25)
            box = RoundedRectangle(width=width, height=head.get_height() + body.get_height() + 0.5,
                                   corner_radius=0.1)
            box.set_fill(GREEN_TINT if ok else CORAL_TINT, 1).set_stroke(GREEN if ok else CORAL, 2)
            box.move_to([0, top - 0.12 - box.get_height() / 2, 0])
            head.move_to(box.get_top() + DOWN * 0.26).align_to(box, LEFT).shift(0.25 * RIGHT)
            body.next_to(head, DOWN, buff=0.12, aligned_edge=LEFT)
            fb = VGroup(box, head, body)
            if fb.get_bottom()[1] < NAV_Y + 0.35:  # keep clear of the button row
                fb.scale((top - 0.12 - (NAV_Y + 0.35)) / fb.get_height(), about_edge=UP)
            feedback.append(fb)
        self.quiz_cache[qi] = (prompt, choices, feedback)
        return self.quiz_cache[qi]

    def show_question(self):
        self.remove(*self.current_quiz_mobs)
        q = self.course["quiz"][self.quiz_index]
        prompt, choices, feedback = self.quiz_mobs(self.quiz_index)
        st = self.quiz_state.get(q["id"])
        n = len(self.course["quiz"])
        header = ui_text(f"Question {self.quiz_index + 1} of {n}  ·  {q['topic']}", 20, TEAL, BOLD)
        header.move_to([0, 3.07, 0]).align_to([LEFT_X + 0.45, 0, 0], LEFT)
        answered = len(self.quiz_state)
        first = sum(1 for s in self.quiz_state.values() if s["first_correct"])
        score_txt = f"First-try correct: {first} / {answered} answered" + (
            f"  ·  finished ({first}/{n})" if answered == n else "")
        score = ui_text(score_txt, 18, MUTED).move_to([0, 3.07, 0]).align_to([RIGHT_X - 0.45, 0, 0], RIGHT)
        mobs = [header, score, prompt, *choices]
        for i, btn in enumerate(choices):
            if st is None or st["choice"] is None:
                btn.set_state("normal")
            elif i == st["choice"]:
                btn.set_state("correct" if i == q["answer"] else "wrong")
            else:
                btn.set_state("normal")
            btn.set_enabled(st is None or st["choice"] is None)
            if st is not None and st["choice"] is not None and i == st["choice"]:
                btn.set_enabled(True)  # keep the chosen answer coloured, but it is locked below
        if st is not None and st["choice"] is not None:
            mobs.append(feedback[st["choice"]])
        self.quiz_prev.set_enabled(self.quiz_index > 0)
        self.quiz_next.set_enabled(self.quiz_index < n - 1)
        self.quiz_retry.set_enabled(st is not None and st["choice"] is not None and st["choice"] != q["answer"])
        self.current_quiz_mobs = mobs
        self.add(*mobs)

    def answer(self, i):
        q = self.course["quiz"][self.quiz_index]
        st = self.quiz_state.get(q["id"])
        if st is not None and st["choice"] is not None:
            return  # locked until "Try again"
        if st is None:
            st = {"choice": None, "attempts": 0, "first_correct": i == q["answer"]}
            self.quiz_state[q["id"]] = st
        st["choice"] = i
        st["attempts"] += 1
        self.show_question()
        self.log(f"answer:{q['id']}:{i}:{'correct' if i == q['answer'] else 'wrong'}")

    def retry_question(self):
        q = self.course["quiz"][self.quiz_index]
        st = self.quiz_state.get(q["id"])
        if st is not None and st["choice"] is not None and st["choice"] != q["answer"]:
            st["choice"] = None
            self.show_question()
            self.log(f"retry:{q['id']}")

    def go_question(self, qi):
        n = len(self.course["quiz"])
        if 0 <= qi < n and qi != self.quiz_index:
            self.quiz_index = qi
            self.show_question()
            self.log(f"question:{qi}")

    def reset_quiz(self):
        self.quiz_state = {}
        self.quiz_index = 0
        self.show_question()
        self.log("quiz:reset")

    def quiz_buttons_active(self):
        _, choices, _ = self.quiz_mobs(self.quiz_index)
        return list(choices) + [self.quiz_prev, self.quiz_retry, self.quiz_reset, self.quiz_next]

    # ---- help overlay

    def build_help_overlay(self):
        lines = [
            ("Mouse", "Click tabs, lesson names and buttons. Drag the explorer sliders."),
            ("1  2  3", "Lessons, Explorer, Quiz"),
            ("Left / Right", "Lessons: previous / next page.  Explorer: nudge the selected slider (Shift x10)"),
            ("Up / Down", "Lessons: previous / next lesson.  Explorer: select a slider"),
            ("Space / Enter", "Lessons: reveal the next worked step.  Explorer: play / pause the time marker"),
            ("R", "Lessons: hide steps.  Explorer: reset all sliders.  Quiz: try the question again"),
            ("P", "Explorer: cycle through the four presets"),
            ("A  B  C  D", "Quiz: choose an answer.  N / Left / Right: next or previous question"),
            ("H", "Show or hide this help"),
            ("Q  or  Esc", "Close the guide"),
        ]
        rows = VGroup()
        for k, v in lines:
            row = VGroup(ui_text(k, 20, TEAL, BOLD), ui_text(v, 19, NAVY))
            row[1].next_to(row[0], RIGHT, buff=0.3)
            row[1].shift((2.4 - row[1].get_left()[0] + row[0].get_left()[0]) * RIGHT)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        title = ui_text("Controls", 26, NAVY, BOLD)
        close = ui_text("Press H or click anywhere to close", 17, MUTED)
        content = VGroup(title, rows, close).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        box = RoundedRectangle(width=content.get_width() + 0.8, height=content.get_height() + 0.6,
                               corner_radius=0.15).set_fill(CARD, 1).set_stroke(NAVY, 2)
        shade = Rectangle(width=FW, height=FH).set_fill(NAVY, 0.35).set_stroke(width=0)
        content.move_to(box)
        self.help_group = VGroup(shade, box, content).move_to(ORIGIN)

    def toggle_help(self):
        self.help_visible = not self.help_visible
        if self.help_visible:
            self.add(self.help_group)
        else:
            self.remove(self.help_group)
        self.tabs["help"].set_state("tab_active" if self.help_visible else "tab")
        self.log(f"help:{self.help_visible}")

    # ---- event plumbing

    def log(self, msg):
        self.event_log.append(msg)

    def active_buttons(self):
        btns = [t for t in self.tabs.values()]
        if self.view == "lessons":
            btns += self.lesson_buttons_active()
        elif self.view == "explorer":
            btns += self.explorer_buttons
        elif self.view == "quiz":
            btns += self.quiz_buttons_active()
        return btns

    def on_mouse_motion(self, point, d_point):
        self.mouse_point.move_to(point)
        hovered = None
        if not self.help_visible:
            for btn in self.active_buttons():
                if btn.enabled and btn.contains(point):
                    hovered = btn
                    break
        if hovered is not self.hovered_button:
            if self.hovered_button is not None:
                self.hovered_button.set_hover(False)
            if hovered is not None:
                hovered.set_hover(True)
            self.hovered_button = hovered

    def on_mouse_press(self, point, button, mods):
        self.mouse_drag_point.move_to(point)
        if self.help_visible:
            self.toggle_help()
            return
        if self.view == "explorer":
            for i, s in enumerate(self.sliders):
                if s.hit(point):
                    self.active_slider = s
                    self.select_slider(i)
                    s.set_value(s.value_from_x(point[0]))
                    self.log(f"slider:{s.key}:{s.value}")
                    return
        for btn in self.active_buttons():
            if btn.contains(point):
                btn.click()
                return

    def on_mouse_drag(self, point, d_point, buttons, modifiers):
        self.mouse_drag_point.move_to(point)
        if self.active_slider is not None:
            self.active_slider.set_value(self.active_slider.value_from_x(point[0]))

    def on_mouse_release(self, point, button, mods):
        if self.active_slider is not None:
            self.log(f"slider:{self.active_slider.key}:{self.active_slider.value}")
        self.active_slider = None

    def on_mouse_scroll(self, point, offset, x_pixel_offset, y_pixel_offset):
        pass  # the layout is fixed; no camera zoom

    def on_key_press(self, symbol, modifiers):
        if symbol in (KEY.Q, KEY.ESCAPE):
            self.quit_interaction = True
            self.log("quit")
            return
        if symbol == KEY.H:
            self.toggle_help()
            return
        if self.help_visible:
            return
        if symbol in (KEY._1, KEY.NUM_1):
            self.show_view("lessons")
        elif symbol in (KEY._2, KEY.NUM_2):
            self.show_view("explorer")
        elif symbol in (KEY._3, KEY.NUM_3):
            self.show_view("quiz")
        elif self.view == "lessons":
            self.lessons_key(symbol)
        elif self.view == "explorer":
            self.explorer_key(symbol, modifiers)
        elif self.view == "quiz":
            self.quiz_key(symbol)

    def lessons_key(self, symbol):
        li = self.flat_pages[self.page_pos][0]
        if symbol in (KEY.RIGHT, KEY.PAGEDOWN):
            self.next_page()
        elif symbol in (KEY.LEFT, KEY.PAGEUP):
            self.prev_page()
        elif symbol == KEY.DOWN:
            self.go_lesson(li + 1)
        elif symbol == KEY.UP:
            self.go_lesson(li - 1)
        elif symbol in (KEY.SPACE, KEY.ENTER, KEY.RETURN):
            self.reveal_step()
        elif symbol == KEY.R:
            self.hide_steps()

    def explorer_key(self, symbol, modifiers):
        s = self.sliders[self.selected_slider]
        steps = 10 if modifiers & KEY.MOD_SHIFT else 1
        if symbol == KEY.RIGHT:
            s.set_value(s.value + steps * s.step)
        elif symbol == KEY.LEFT:
            s.set_value(s.value - steps * s.step)
        elif symbol == KEY.DOWN:
            self.select_slider(self.selected_slider + 1)
        elif symbol == KEY.UP:
            self.select_slider(self.selected_slider - 1)
        elif symbol in (KEY.SPACE, KEY.ENTER, KEY.RETURN):
            self.toggle_play()
        elif symbol == KEY.R:
            self.reset_explorer()
        elif symbol == KEY.P:
            presets = self.course["explorer"]["presets"]
            p = self.params()
            current = next((i for i, pr in enumerate(presets)
                            if (pr["a"], pr["b"], pr["c"]) == (p["a"], p["b"], p["c"])), -1)
            self.apply_preset(presets[(current + 1) % len(presets)])

    def quiz_key(self, symbol):
        letters = {KEY.A: 0, KEY.B: 1, KEY.C: 2, KEY.D: 3}
        if symbol in letters and letters[symbol] < len(self.course["quiz"][self.quiz_index]["choices"]):
            self.answer(letters[symbol])
        elif symbol in (KEY.RIGHT, KEY.N):
            self.go_question(self.quiz_index + 1)
        elif symbol == KEY.LEFT:
            self.go_question(self.quiz_index - 1)
        elif symbol == KEY.R:
            self.retry_question()
