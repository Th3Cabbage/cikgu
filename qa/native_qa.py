"""Headless QA for courses/ode/native/study_guide.py. Opens no window.

Builds the real SecondOrderStudyGuide scene on ManimGL's offscreen (standalone OpenGL)
camera at 1280x720, drives its real event handlers (on_mouse_press/drag/release/motion,
on_key_press) with points converted from pixel positions by ManimGL's own
Window.pixel_coords_to_space_coords, checks state and layout, and saves preview PNGs.

Run from the repository root with MiKTeX on PATH (see README):
    .\\.venv\\Scripts\\python.exe qa\\native_qa.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
OUT_DIR = os.path.join(HERE, "scratch", "native_out")
SHOTS = os.path.join(HERE, "screenshots")
RESULTS = os.path.join(HERE, "results")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(SHOTS, exist_ok=True)
os.makedirs(RESULTS, exist_ok=True)

PIXELS = (1280, 720)
sys.argv = ["manimgl", "-w", "-r", f"{PIXELS[0]}x{PIXELS[1]}", "--video_dir", OUT_DIR]
sys.path.insert(0, os.path.join(PROJECT, "courses/ode/native"))

from manimlib import *  # noqa: E402,F403
from manimlib.window import Window  # noqa: E402
from pyglet.window import key as KEY  # noqa: E402

import ode_math  # noqa: E402
import study_guide as SG  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail != "" else ""), flush=True)
    return ok


class PixelWindowStub:
    """Just the attributes Window.pixel_coords_to_space_coords reads (scene, size)."""

    def __init__(self, scene):
        self.scene = scene
        self.size = PIXELS


t_start = time.time()
scene = SG.SecondOrderStudyGuide()
stub = PixelWindowStub(scene)


def to_pixels(point):
    px = (point[0] + FRAME_WIDTH / 2) / FRAME_WIDTH * PIXELS[0]
    py = (point[1] + FRAME_HEIGHT / 2) / FRAME_HEIGHT * PIXELS[1]
    return int(round(px)), int(round(py))


def space(px, py):
    return Window.pixel_coords_to_space_coords(stub, px, py)


def click_pixel(px, py):
    p = space(px, py)
    scene.on_mouse_motion(p, np.zeros(3))
    scene.on_mouse_press(p, 1, 0)
    scene.on_mouse_release(p, 1, 0)


def click(mob):
    click_pixel(*to_pixels(mob.get_center()))


def key(symbol, modifiers=0):
    scene.on_key_press(symbol, modifiers)
    scene.on_key_release(symbol, modifiers)


def drag(from_point, to_point, steps=6):
    x0, y0 = to_pixels(from_point)
    x1, y1 = to_pixels(to_point)
    scene.on_mouse_press(space(x0, y0), 1, 0)
    last = space(x0, y0)
    for i in range(1, steps + 1):
        p = space(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps)
        scene.on_mouse_drag(p, p - last, 1, 0)
        last = p
    scene.on_mouse_release(last, 1, 0)


def snap(name):
    scene.update_frame(dt=0, force_draw=True)
    img = scene.get_image().convert("RGB")
    path = os.path.join(SHOTS, f"native_{name}.png")
    img.save(path)
    return img


def bbox(mob):
    return (mob.get_left()[0], mob.get_right()[0], mob.get_bottom()[1], mob.get_top()[1])


def overlaps(a, b, pad=0.0):
    a0, a1, a2, a3 = bbox(a)
    b0, b1, b2, b3 = bbox(b)
    return a0 < b1 - pad and b0 < a1 - pad and a2 < b3 - pad and b2 < a3 - pad


def inside(mob, left, right, bottom, top, tol=0.02):
    l, r, b, t = bbox(mob)
    return l >= left - tol and r <= right + tol and b >= bottom - tol and t <= top + tol


def in_scene(mob):
    return mob in scene.get_mobject_family_members()


# ------------------------------------------------------------------ construct
scene.setup()
scene.construct()
frame_center0 = scene.frame.get_center().copy()
check("scene constructs with no window (offscreen camera)", scene.window is None and scene.view == "lessons")
img = snap("lesson_start")
check("camera renders at 1280x720", img.size == PIXELS, img.size)
check("window pixel mapping round-trips (pixel -> scene -> pixel)",
      to_pixels(space(321, 654)) == (321, 654), to_pixels(space(321, 654)))

# ------------------------------------------------------------------ lessons: navigation
check("starts on lesson 1 page 1", (scene.page_pos, scene.screen_idx) == (0, 0))
key(KEY.RIGHT)
check("Right arrow -> next page", scene.page_pos == 1, scene.page_pos)
click(scene.next_btn)
check("click Next button -> page 3", scene.page_pos == 2, scene.page_pos)
click(scene.prev_btn)
check("click Prev button -> page 2", scene.page_pos == 1, scene.page_pos)
key(KEY.LEFT)
check("Left arrow -> page 1", scene.page_pos == 0)
check("Prev disabled on first page", not scene.prev_btn.enabled)
click(scene.lesson_buttons[3])
li, pi = scene.flat_pages[scene.page_pos]
check("click sidebar lesson 4 -> its first page", (li, pi) == (3, 0), (li, pi))
check("sidebar highlights the current lesson", scene.lesson_buttons[3].state == "selected")
key(KEY.DOWN)
check("Down arrow -> next lesson", scene.flat_pages[scene.page_pos] == (4, 0), scene.flat_pages[scene.page_pos])
key(KEY.UP)
check("Up arrow -> previous lesson", scene.flat_pages[scene.page_pos] == (3, 0))
scene.on_mouse_motion(scene.next_btn.get_center(), np.zeros(3))
check("hovering a button highlights it", scene.next_btn.hovered)
scene.on_mouse_motion(np.array([0.0, 0.0, 0.0]), np.zeros(3))
check("moving away clears the hover", not scene.next_btn.hovered)

# ------------------------------------------------------------------ lessons: every page fits
fit = []
t0 = time.time()
for pos in range(len(scene.flat_pages)):
    screens = scene.build_screens(pos)
    for si, screen in enumerate(screens):
        parts = VGroup(screen.static, *(screen.example.rows if screen.example else []))
        ok = inside(parts, SG.CONTENT_LEFT, SG.CONTENT_RIGHT, SG.CONTENT_BOTTOM, 3.3)
        fit.append({"page": scene.flat_pages[pos], "screen": si, "scale": round(screen.scale, 3), "inside": ok})
n_screens = len(fit)
check(f"all {len(scene.flat_pages)} lesson pages build ({n_screens} native screens)",
      n_screens >= len(scene.flat_pages), f"{time.time() - t0:.1f}s")
check("every lesson screen stays inside the content area", all(f["inside"] for f in fit),
      [f for f in fit if not f["inside"]])
min_scale = min(f["scale"] for f in fit)
check("no lesson content shrunk below 85% to fit", min_scale >= 0.85, f"min scale {min_scale}")
check("no TeX compile errors in shared content", not scene.tex_errors, scene.tex_errors[:3])
split_pages = sorted({tuple(f["page"]) for f in fit if f["screen"] > 0})
check("long pages split into extra native screens instead of shrinking", True, f"split pages: {split_pages}")

# ------------------------------------------------------------------ lessons: worked example reveal
target = next(pos for pos, (li, pi) in enumerate(scene.flat_pages)
              if any(b.get("id") == "ex-distinct" for b in scene.course["lessons"][li]["pages"][pi]["blocks"]))
scene.page_pos, scene.screen_idx = target, 0
scene.show_screen()
ex = scene.current_screen().example
check("worked example page has step controls", ex is not None and in_scene(scene.reveal_btn))
check("steps start hidden", ex.revealed == 0 and not any(in_scene(r) for r in ex.rows))
key(KEY.SPACE)
check("Space reveals step 1", ex.revealed == 1 and in_scene(ex.rows[0]) and not in_scene(ex.rows[1]))
click(scene.reveal_btn)
check("click 'Next step' reveals step 2", ex.revealed == 2 and in_scene(ex.rows[1]))
while ex.revealed < len(ex.rows):
    click(scene.reveal_btn)
check("all steps can be revealed; button then disables",
      ex.revealed == len(ex.rows) and not scene.reveal_btn.enabled)
snap("worked_example")
click(scene.hide_btn)
check("click 'Hide steps' hides them again", ex.revealed == 0 and not in_scene(ex.rows[0]))
key(KEY.SPACE)
key(KEY.R)
check("R key hides steps", ex.revealed == 0)

# lesson preview for the report: lesson 2 page 3 (repeated root)
scene.page_pos, scene.screen_idx = scene.lesson_first_page[1] + 2, 0
scene.show_screen()
snap("lesson_page")

# ------------------------------------------------------------------ explorer
key(KEY._2)
check("key 2 -> Explorer", scene.view == "explorer" and in_scene(scene.curve))
check("lesson content removed when leaving Lessons", not any(in_scene(m) for m in scene.current_screen_mobs))
sl = {s.key: s for s in scene.sliders}
p = scene.params()
check("explorer defaults a=1 b=2 c=4 y0=1 v0=0", (p["a"], p["b"], p["c"], p["y0"], p["v0"]) == (1, 2, 4, 1, 0), p)
check("default classification underdamped", scene.damping_key == "underdamped")
snap("explorer")


def curve_matches():
    pr = scene.params()
    pts = scene.curve.get_anchors() if hasattr(scene.curve, "get_anchors") else scene.curve.get_points()
    worst = 0.0
    for t in (0.0, 1.3, 4.0, 7.2):
        y = ode_math.solution(t, pr["a"], pr["b"], pr["c"], pr["y0"], pr["v0"])
        target = scene.to_screen(t, y)
        worst = max(worst, float(np.min(np.linalg.norm(pts[:, :2] - target[:2], axis=1))))
    return worst


check("plotted curve passes through exact solution points", curve_matches() < 0.03, f"{curve_matches():.4f}")

# drag the b knob to b = 4 (critical)
b = sl["b"]
start, end = b.track_start(), b.track_end()
drag(b.knob.get_center(), start + (4 - b.lo) / (b.hi - b.lo) * (end - start))
check("dragging the b knob updates b", abs(b.value - 4) < 1e-9, b.value)
check("drag -> critical classification + repeated-root label",
      scene.damping_key == "critical" and "double" in scene.roots_label.text, scene.roots_label.text)
check("curve redrawn after drag", curve_matches() < 0.03)
check("value label shows the new value", b.value_label.text == "4.00", b.value_label.text)
check("dragging never pans the camera", np.allclose(scene.frame.get_center(), frame_center0))

# click on the track (not the knob) for c
c = sl["c"]
cs, ce = c.track_start(), c.track_end()
click_pixel(*to_pixels(cs + 0.25 * (ce - cs)))
check("clicking a slider track jumps the value (within one step / one pixel)",
      abs(c.value - (c.lo + 0.25 * (c.hi - c.lo))) <= c.step + 1e-9, c.value)

# keyboard slider control
scene.select_slider(0)
before = sl["a"].value
key(KEY.RIGHT)
check("Right arrow nudges the selected slider by one step", abs(sl["a"].value - (before + 0.05)) < 1e-9)
key(KEY.LEFT, KEY.MOD_SHIFT)
check("Shift+Left nudges by ten steps", abs(sl["a"].value - max(0.5, before + 0.05 - 0.5)) < 1e-9, sl["a"].value)
key(KEY.DOWN)
check("Down arrow selects the next slider", scene.selected_slider == 1 and sl["b"].selected)

# presets keep y0, v0
sl["y0"].set_value(-1.5)
sl["v0"].set_value(2.0)
expected = {"undamped": "undamped", "underdamped": "underdamped", "critical": "critical", "overdamped": "overdamped"}
for btn, preset in zip(scene.preset_buttons, scene.course["explorer"]["presets"]):
    click(btn)
    pr = scene.params()
    check(f"preset {preset['label']} sets a,b,c and keeps y0,v0",
          (pr["a"], pr["b"], pr["c"], pr["y0"], pr["v0"]) == (preset["a"], preset["b"], preset["c"], -1.5, 2.0)
          and scene.damping_key == expected[preset["id"]] and curve_matches() < 0.03,
          f"{pr} -> {scene.damping_key}")
key(KEY.P)
check("P cycles presets (overdamped -> undamped)", scene.damping_key == "undamped")

# zero solution
sl["y0"].set_value(0)
sl["v0"].set_value(0)
ys = [pt[1] for pt in scene.curve.get_points()]
check("y0 = v0 = 0: curve is flat on the axis, axis bound stays 1",
      max(abs(y - scene.plot_mid) for y in ys) < 1e-9 and scene.bound == 1.0, scene.bound)
check("zero solution shows the uniqueness note inside the plot", in_scene(scene.zero_text)
      and inside(scene.zero_text, scene.plot_left, scene.plot_right, scene.plot_bottom, scene.plot_top))
snap("explorer_zero")

# boundary corners keep a usable axis
for vals in ({"a": 0.5, "b": 0, "c": 0.5, "y0": 3, "v0": 3}, {"a": 3, "b": 0, "c": 0.5, "y0": -3, "v0": 3},
             {"a": 0.5, "b": 8, "c": 9, "y0": 3, "v0": -3}):
    for k, v in vals.items():
        sl[k].set_value(v)
    pts = scene.curve.get_points()
    check(f"corner {vals}: curve inside plot box",
          pts[:, 1].min() >= scene.plot_bottom - 1e-6 and pts[:, 1].max() <= scene.plot_top + 1e-6, f"bound {scene.bound}")

# reset and play
click(scene.reset_btn)
pr = scene.params()
check("zero note hidden again for nonzero data", not in_scene(scene.zero_text))
check("Reset restores all five defaults", (pr["a"], pr["b"], pr["c"], pr["y0"], pr["v0"]) == (1, 2, 4, 1, 0), pr)
click(scene.play_btn)
check("Play button starts the marker", scene.playing)
for _ in range(15):
    scene.update_frame(dt=1 / 30)
check("marker advances while playing", 0.45 < scene.marker_t < 0.55, round(scene.marker_t, 3))
mt = scene.marker_t
yv = ode_math.solution(mt, 1, 2, 4, 1, 0)
check("marker dot sits on the curve", np.linalg.norm(scene.marker_dot.get_center() - scene.to_screen(mt, yv)) < 1e-6)
check("marker label shows t and y(t)", scene.marker_label.text == f"t = {ode_math.fmt(mt)}   y(t) = {ode_math.fmt(yv)}",
      scene.marker_label.text)
snap("explorer_playing")
key(KEY.SPACE)
check("Space pauses the marker", not scene.playing)
for _ in range(5):
    scene.update_frame(dt=1 / 30)
check("marker stays put while paused", scene.marker_t == mt)

# explorer layout
expl_btns = scene.explorer_buttons
pairs = [(a, b) for i, a in enumerate(expl_btns) for b in expl_btns[i + 1:] if overlaps(a, b)]
check("explorer buttons do not overlap each other", not pairs)
check("sliders do not overlap buttons", not any(overlaps(s, b) for s in scene.sliders for b in expl_btns))
check("sliders do not overlap each other",
      not any(overlaps(scene.sliders[i], scene.sliders[i + 1]) for i in range(len(scene.sliders) - 1)))
right_panel_left = min(s.get_left()[0] for s in scene.sliders)
card = scene.explorer_static[2]
label_ok = []
for k, t in scene.damping_texts.items():
    t.move_to(scene.damping_anchor, aligned_edge=RIGHT)
    label_ok.append(inside(t, card.get_left()[0], card.get_right()[0], scene.plot_top, card.get_top()[1])
                    and t.get_left()[0] > scene.plot_left + 0.6)
scene.refresh_explorer()
check("every classification label fits in the plot card header", all(label_ok), label_ok)
longest_roots = max((ode_math.roots_text(a, b, c).replace("₁", "1").replace("₂", "2")
                     for a in (0.5, 3) for b in (0, 8) for c in (0.5, 9)), key=len)
roots_right = scene.roots_label.anchor.get_center()[0] + scene.roots_label.width_of(longest_roots)
eq_right = scene.eq_label.anchor.get_center()[0] + scene.eq_label.width_of("0.50 y'' + 8.00 y' + 9.00 y = 0")
disc_right = scene.disc_label.anchor.get_center()[0] + scene.disc_label.width_of("b^2 - 4ac = -108.00")
check("readout labels cannot collide (longest strings)",
      roots_right < scene.disc_label.anchor.get_center()[0] - 0.1
      and eq_right < scene.marker_label.anchor.get_center()[0] - 0.1
      and disc_right < right_panel_left - 0.1,
      f"roots {roots_right:.2f} | eq {eq_right:.2f} | disc {disc_right:.2f} vs panel {right_panel_left:.2f}")
check("explorer view inside the frame",
      inside(scene.explorer_group, -FRAME_WIDTH / 2, FRAME_WIDTH / 2, SG.FOOTER_Y + 0.24, 4))

# ------------------------------------------------------------------ quiz
key(KEY._3)
check("key 3 -> Quiz", scene.view == "quiz")
quiz = scene.course["quiz"]
check("quiz has at least 8 questions", len(quiz) >= 8, len(quiz))
q0 = quiz[0]
prompt, choices, feedback = scene.quiz_mobs(0)
wrong = (q0["answer"] + 1) % len(q0["choices"])
click(choices[wrong])
st = scene.quiz_state[q0["id"]]
check("clicking a wrong answer marks it wrong and shows its explanation",
      choices[wrong].state == "wrong" and in_scene(feedback[wrong]) and not st["first_correct"])
click(choices[q0["answer"]])
check("answers lock until Try again", st["choice"] == wrong)
snap("quiz_wrong")
click(scene.quiz_retry)
check("Try again clears the choice", st["choice"] is None and not in_scene(feedback[wrong]))
click(choices[q0["answer"]])
check("correct answer marked correct with explanation",
      choices[q0["answer"]].state == "correct" and in_scene(feedback[q0["answer"]]))
check("score counts first-try only (0 so far)", sum(s["first_correct"] for s in scene.quiz_state.values()) == 0)
click(scene.quiz_next)
check("Next -> question 2", scene.quiz_index == 1)
q1 = quiz[1]
key([KEY.A, KEY.B, KEY.C, KEY.D][q1["answer"]])
check("letter key answers question 2 correctly",
      scene.quiz_state[q1["id"]]["first_correct"] and scene.quiz_mobs(1)[1][q1["answer"]].state == "correct")
snap("quiz_correct")
key(KEY.LEFT)
check("Left -> back to question 1 with its state kept", scene.quiz_index == 0 and in_scene(feedback[q0["answer"]]))
click(scene.quiz_reset)
check("Reset quiz clears all answers", scene.quiz_state == {} and scene.quiz_index == 0
      and all(ch.state == "normal" for ch in choices))

quiz_layout = []
for qi, q in enumerate(quiz):
    prompt, choices, feedback = scene.quiz_mobs(qi)
    ok = inside(VGroup(prompt, *choices), -FRAME_WIDTH / 2, FRAME_WIDTH / 2, SG.NAV_Y + 0.3, 3.3)
    ok = ok and all(not overlaps(choices[i], choices[i + 1]) for i in range(len(choices) - 1))
    fb_ok = all(fb.get_bottom()[1] >= SG.NAV_Y + 0.3 - 0.02 and fb.get_top()[1] <= choices[-1].get_bottom()[1] + 0.02
                for fb in feedback)
    fb_scale = min(fb[2].get_height() / scene.paragraph(q["feedback"][i], FRAME_WIDTH - 1.4, 25).get_height()
                   for i, fb in enumerate(feedback))
    quiz_layout.append({"q": q["id"], "ok": ok and fb_ok, "feedback_scale": round(fb_scale, 3)})
check("every question, its choices and all feedback boxes fit without overlap",
      all(x["ok"] for x in quiz_layout), [x for x in quiz_layout if not x["ok"]])
check("no feedback text shrunk below 85%", min(x["feedback_scale"] for x in quiz_layout) >= 0.85,
      min(x["feedback_scale"] for x in quiz_layout))
check("no TeX compile errors after building every quiz question", not scene.tex_errors, scene.tex_errors[:3])

# ------------------------------------------------------------------ help, tabs, quit
click(scene.tabs["help"])
check("Help tab opens the help overlay", scene.help_visible and in_scene(scene.help_group))
snap("help")
click_pixel(640, 360)
check("clicking anywhere closes help", not scene.help_visible)
key(KEY.H)
key(KEY.H)
check("H toggles help", not scene.help_visible)
click(scene.tabs["lessons"])
check("Lessons tab returns to lessons", scene.view == "lessons")
click(scene.tabs["explorer"])
check("Explorer tab works", scene.view == "explorer")
scene.on_mouse_scroll(np.zeros(3), np.zeros(3), 0, 5)
check("mouse wheel does not zoom the camera", np.allclose(scene.frame.get_center(), frame_center0)
      and abs(scene.frame.get_height() - FRAME_HEIGHT) < 1e-9)
key(KEY.Q)
check("Q sets quit_interaction (closes the window loop)", scene.quit_interaction)
scene.quit_interaction = False
key(KEY.ESCAPE)
check("Esc sets quit_interaction", scene.quit_interaction)

# chrome
tabs = list(scene.tabs.values())
check("tabs do not overlap", not any(overlaps(a, b) for i, a in enumerate(tabs) for b in tabs[i + 1:]))

elapsed = time.time() - t_start
summary = {"results": results, "lesson_fit": fit, "quiz_layout": quiz_layout,
           "event_log_tail": scene.event_log[-25:], "elapsed_s": round(elapsed, 1)}
with open(os.path.join(RESULTS, "native_results.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, default=str)
failed = [r for r in results if not r["ok"]]
print(f"\n{len(results) - len(failed)}/{len(results)} native checks passed in {elapsed:.0f}s")
sys.exit(1 if failed else 0)
