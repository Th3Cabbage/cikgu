"""ManimGL scenes for Unit 7, Column Space, Basis and Graphs (one scene per sequence).

Colour code: column 1 teal, column 2 blue, column 3 / dependent pieces yellow, null space pink,
results green, edges and loop currents teal/orange. Matrices use Mat (no \\begin{bmatrix} in
mathtext). Stage bounds: |x| <= 6.3, -2.8 <= y <= 3.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ctl_common import *  # noqa: E402,F401,F403

CHIP["diagram"] = ("PICTURE", PINK_C)

COL = {"c1": TEAL_C, "c2": BLUE_C, "c3": YELLOW_C, "n": PINK_C, "res": GREEN_C}


def M(*toks, size=1.0, color=FG, colors=None):
    return Mx(*toks, size=size, color=color, colors={**COL, **(colors or {})})


def colvec(entries, size=0.8, color=FG):
    m = Mat([[str(e)] for e in entries], size=size)
    m.set_color(color)
    return m


# ======================================================================== Section 1

class ColumnCombinationSequence(ControlScene):
    SEQ_ID = "column-combination"

    def construct(self):
        A = Mat([["1", "1", "2"], ["1", "2", "3"], ["1", "2", "3"]], size=0.9)
        for i in range(3):
            A.e[i][0].set_color(TEAL_C); A.e[i][1].set_color(BLUE_C); A.e[i][2].set_color(YELLOW_C)
        top = VGroup(M(("A", "A ="), size=0.9), A).arrange(RIGHT, buff=0.2).move_to([-4.2, 2.1, 0])
        self.start(top)

        # 1. columns times weights
        c1, c2, c3 = colvec([1, 1, 1], color=TEAL_C), colvec([1, 2, 2], color=BLUE_C), colvec([2, 3, 3], color=YELLOW_C)
        row = VGroup(M(("Av", "Av ="), size=0.9), M(("v", "v_1"), size=0.9), c1, M("+"), M(("v", "v_2"), size=0.9), c2, M("+"),
                     M(("v", "v_3"), size=0.9), c3).arrange(RIGHT, buff=0.15).move_to([1.4, 2.1, 0])
        self.play(self.chip("weights times columns"), FadeIn(row[0]), run_time=0.5)
        self.play(TransformFromCopy(A.col(0), c1), FadeIn(row[1]), run_time=0.8)
        self.play(FadeIn(row[3:5]), TransformFromCopy(A.col(1), c2), run_time=0.8)
        self.play(FadeIn(row[6:8]), TransformFromCopy(A.col(2), c3), run_time=0.8)
        self.step_done(top, row)

        # 2. dependency
        dep = VGroup(c1.copy(), M("+"), c2.copy(), M("="), c3.copy()).arrange(RIGHT, buff=0.2).move_to([-2.6, 0.2, 0])
        nul = M(("A", "A"), ("n", "(-1, -1, 1)"), "=", "0", size=0.95, colors={"n": PINK_C}).move_to([3.0, 0.5, 0])
        pl = label("C(A) is a plane;  N(A) is a line", 22, PINK_C).move_to([3.0, -0.2, 0])
        self.play(self.chip("column 3 = column 1 + column 2"), TransformFromCopy(VGroup(c1, c2, c3), dep), run_time=1.3)
        self.play(Write(nul), FadeIn(pl), run_time=1.0)
        self.step_done(top, row, dep, nul, pl)

        # 3. complete solution
        b = M(("b", "b = (3, 4, 4)"), "=", ("t", r"2\,\mathrm{col}_1 + \mathrm{col}_2"), size=0.9).move_to([0, -1.4, 0])
        sol = M(("v", "v"), "=", ("p", "(2, 1, 0)"), "+", ("n", "c(-1, -1, 1)"), size=1.1,
                colors={"p": GREEN_C, "n": PINK_C}).move_to([0, -2.3, 0])
        self.play(self.chip("particular + null"), Write(b), run_time=1.0)
        self.play(Write(sol), run_time=1.1)
        self.play(ShowCreation(hbox(sol, GREEN_C)), run_time=0.5)
        self.step_done(top, row, dep, nul, pl, b, sol, hbox(sol, GREEN_C))


# ======================================================================== Section 2

class IndependenceSequence(ControlScene):
    SEQ_ID = "independence"

    def construct(self):
        # an oblique 3-D sketch: plane as a parallelogram
        o = np.array([-2.6, -0.8, 0])
        def P(x, y, z):  # simple oblique projection
            return o + np.array([0.45 * x + 0.25 * y, 0.22 * y + 0.38 * z, 0]) * 1.0
        plane = Polygon(P(-1, -0.5, -1), P(6, 3, -1), P(7, 3.5, 6), P(0, 0, 6)).set_fill(TEAL_C, 0.12).set_stroke(TEAL_C, 1)
        a1 = arrow(P(0, 0, 0), P(2, 1, 5), color=TEAL_C)
        a2 = arrow(P(0, 0, 0), P(4, 2, 0), color=BLUE_C)
        l1 = label("a1 = (2, 1, 5)", 20, TEAL_C).next_to(P(2, 1, 5), UP, buff=0.1)
        l2 = label("a2 = (4, 2, 0)", 20, BLUE_C).next_to(P(4, 2, 0), DOWN, buff=0.1)
        self.start(plane, a1, a2, l1, l2)

        # 1. a3 = a1 + a2
        a3 = arrow(P(0, 0, 0), P(6, 3, 5), color=YELLOW_C)
        g1 = DashedLine(P(2, 1, 5), P(6, 3, 5)).set_stroke(BLUE_C, 2)
        g2 = DashedLine(P(4, 2, 0), P(6, 3, 5)).set_stroke(TEAL_C, 2)
        e1 = M(("a", "a_3 = a_1 + a_2"), size=0.9, colors={"a": YELLOW_C}).move_to([3.4, 2.4, 0])
        e2 = M(("z", "a_1 + a_2 - a_3 = 0"), size=0.9).move_to([3.4, 1.7, 0])
        d = label("dependent: a3 lies in the plane", 22, RED_C).move_to([3.4, 1.05, 0])
        self.play(self.chip("add a1 and a2"), ShowCreation(g1), ShowCreation(g2), run_time=0.8)
        self.play(grow_arrow(a3), Write(e1), run_time=1.0)
        self.play(Write(e2), FadeIn(d), run_time=0.9)
        self.step_done(plane, a1, a2, l1, l2, a3, g1, g2, e1, e2, d)

        # 2. a3 = (1, 0, 0)
        a3b = arrow(P(0, 0, 0), P(3.5, -2.5, -1.4), color=GREEN_C)
        e3 = M(("a", "a_3 = (1, 0, 0)"), size=0.9, colors={"a": GREEN_C}).move_to([3.4, 0.2, 0])
        i3 = label("off the plane: independent, a basis of R³", 22, GREEN_C).move_to([3.4, -0.45, 0])
        self.play(self.chip("choose a vector off the plane"), FadeOut(VGroup(a3, g1, g2)), run_time=0.6)
        self.play(grow_arrow(a3b), Write(e3), FadeIn(i3), run_time=1.2)
        self.step_done(plane, a1, a2, l1, l2, e1, e2, d, a3b, e3, i3)

        # 3. dimension
        dims = VGroup(label("point 0   ·   line 1   ·   plane 2   ·   R³ 3", 22, YELLOW_C)).move_to([3.4, -1.4, 0])
        n = label("dimension = size of every basis", 22, FG).move_to([3.4, -2.0, 0])
        self.play(self.chip("count basis vectors"), FadeIn(dims), FadeIn(n), run_time=1.0)
        self.step_done(plane, a1, a2, l1, l2, e1, e2, d, a3b, e3, i3, dims, n)


# ======================================================================== Section 3

class FourSubspacesSequence(ControlScene):
    SEQ_ID = "four-subspaces"

    def construct(self):
        A = Mat([["1", "2", "3"], ["4", "5", "6"]], size=0.9)
        top = VGroup(M(("A", "A ="), size=0.9), A, label("m = 2,  n = 3,  r = 2", 22, DIM)).arrange(RIGHT, buff=0.3).move_to([0, 2.7, 0])
        left = VGroup(Rectangle(width=3.6, height=1.0).set_stroke(TEAL_C, 3), Rectangle(width=3.6, height=0.6).set_stroke(PINK_C, 3)).arrange(DOWN, buff=0.15).move_to([-3.6, 0.3, 0])
        right = VGroup(Rectangle(width=3.0, height=1.0).set_stroke(BLUE_C, 3), Rectangle(width=3.0, height=0.25).set_stroke(DIM, 2)).arrange(DOWN, buff=0.15).move_to([3.6, 0.3, 0])
        ll = VGroup(label("row space C(Aᵀ)", 20, TEAL_C).move_to(left[0]), label("null space N(A)", 20, PINK_C).move_to(left[1]))
        rl = VGroup(label("column space C(A)", 20, BLUE_C).move_to(right[0]), label("N(Aᵀ) = {0}", 16, DIM).next_to(right[1], DOWN, buff=0.08))
        hdr = VGroup(label("in R³ (n = 3)", 22, FG).next_to(left, UP, buff=0.2), label("in R² (m = 2)", 22, FG).next_to(right, UP, buff=0.2))
        arr = arrow(left[0].get_right() + 0.1 * RIGHT, right[0].get_left() + 0.1 * LEFT, color=YELLOW_C)
        al = label("A", 22, YELLOW_C).next_to(arr, UP, buff=0.08)
        self.start(top, left, right, ll, rl, hdr, arr, al)

        # 1. null space
        n1 = M(("n", "A(1, -2, 1) = (0, 0)"), size=0.85, colors={"n": PINK_C}).move_to([-3.2, -1.3, 0])
        self.play(self.chip("solve Av = 0"), Indicate(left[1], color=PINK_C), Write(n1), run_time=1.3)
        self.step_done(top, left, right, ll, rl, hdr, arr, al, n1)

        # 2. perpendicular
        p1 = M(("r", "(1, 2, 3)\\cdot(1, -2, 1) = 0"), size=0.75, colors={"r": TEAL_C}).move_to([-3.2, -2.0, 0])
        p2 = M(("r", "(4, 5, 6)\\cdot(1, -2, 1) = 0"), size=0.75, colors={"r": TEAL_C}).move_to([-3.2, -2.55, 0])
        perp = label("⟂", 36, YELLOW_C).next_to(left[1], RIGHT, buff=0.15)
        self.play(self.chip("each row dot v = 0"), Write(p1), Write(p2), run_time=1.3)
        self.play(FadeIn(perp), run_time=0.6)
        self.step_done(top, left, right, ll, rl, hdr, arr, al, n1, p1, p2, perp)

        # 3. dimensions
        dl = VGroup(label("r = 2", 22, TEAL_C).next_to(left[0], LEFT, buff=0.12),
                    label("n − r = 1", 22, PINK_C).next_to(left[1], LEFT, buff=0.12))
        dr = VGroup(label("2 = r", 22, BLUE_C).next_to(right[0], RIGHT, buff=0.1),
                    label("0 = m − r", 18, DIM).next_to(right[1], RIGHT, buff=0.1))
        gen = label("general rank r:   r,  n − r   in Rⁿ;    r,  m − r   in Rᵐ", 22, GREEN_C).move_to([2.6, -1.9, 0])
        self.play(self.chip("dimensions"), FadeIn(dl), FadeIn(dr), run_time=1.0)
        self.play(FadeIn(gen), run_time=0.7)
        self.step_done(top, left, right, ll, rl, hdr, arr, al, n1, p1, p2, perp, dl, dr, gen)


# ======================================================================== Sections 4-5 (graph)

NODES = {1: np.array([-5.0, 1.6, 0]), 2: np.array([-1.6, 1.6, 0]), 3: np.array([-3.3, -1.9, 0]), 4: np.array([-3.3, 0.35, 0])}
EDGES = [(1, 2), (1, 3), (2, 3), (1, 4), (2, 4)]


def graph_mobs(edge_color=FG):
    dots = VGroup(*[Dot(p, radius=0.17).set_fill(BG, 1).set_stroke(FG, 3) for p in NODES.values()])
    nl = VGroup(*[label(str(k), 20, FG).move_to(p) for k, p in NODES.items()])
    edges = VGroup()
    elabels = VGroup()
    for k, (a, b) in enumerate(EDGES, 1):
        pa, pb = NODES[a], NODES[b]
        d = (pb - pa) / np.linalg.norm(pb - pa)
        edges.add(arrow(pa + 0.22 * d, pb - 0.22 * d, color=edge_color, width=3))
        mid = (pa + pb) / 2 + 0.25 * np.array([-d[1], d[0], 0])
        elabels.add(label(f"e{k}", 18, DIM).move_to(mid))
    return dots, nl, edges, elabels


class IncidenceSequence(ControlScene):
    SEQ_ID = "incidence"

    def construct(self):
        dots, nl, edges, el = graph_mobs()
        self.start(edges, dots, nl, el)

        # 1. rows
        rows = [["-1", "1", "0", "0"], ["-1", "0", "1", "0"], ["0", "-1", "1", "0"], ["-1", "0", "0", "1"], ["0", "-1", "0", "1"]]
        A = Mat(rows, size=0.8)
        for i, r in enumerate(rows):
            for j, x in enumerate(r):
                A.e[i][j].set_color(RED_C if x == "-1" else (GREEN_C if x == "1" else DIM))
        Ag = VGroup(M(("A", "A ="), size=0.85), A).arrange(RIGHT, buff=0.2).move_to([2.8, 0.6, 0])
        hdr = VGroup(*[label(f"n{j + 1}", 16, DIM).next_to(A.e[0][j], UP, buff=0.25) for j in range(4)])
        self.play(self.chip("-1 at the start, +1 at the end"), FadeIn(Ag[0]), FadeIn(A.lb), FadeIn(A.rb), FadeIn(hdr), run_time=0.6)
        for i in range(5):
            self.play(Indicate(edges[i], color=YELLOW_C), FadeIn(A.row(i), shift=0.1 * LEFT), run_time=0.55)
        self.step_done(edges, dots, nl, el, Ag, hdr)

        # 2. differences
        d = M(("d", r"Av = (v_2 - v_1,\ v_3 - v_1,\ v_3 - v_2,\ v_4 - v_1,\ v_4 - v_2)"), size=0.7, colors={"d": YELLOW_C}).move_to([2.4, -1.5, 0])
        self.play(self.chip("each row takes a difference"), Write(d), run_time=1.3)
        self.step_done(edges, dots, nl, el, Ag, hdr, d)

        # 3. constants
        c = M(("c", "A(1, 1, 1, 1) = 0"), ",", ("r", r"\mathrm{rank}\,A = 3"), size=0.85, colors={"c": PINK_C, "r": GREEN_C}).move_to([2.4, -2.3, 0])
        vals = VGroup(*[label("1", 18, PINK_C).next_to(p, UR, buff=0.05) for p in NODES.values()])
        self.play(self.chip("equal potentials"), FadeIn(vals), run_time=0.7)
        self.play(Write(c), run_time=1.0)
        self.step_done(edges, dots, nl, el, Ag, hdr, d, vals, c)


class LoopsSequence(ControlScene):
    SEQ_ID = "loops"

    def construct(self):
        dots, nl, edges, el = graph_mobs(edge_color=DIM)
        e0 = M(("k", "A^T w = 0"), size=1.1).move_to([2.6, 2.6, 0])
        self.start(edges, dots, nl, el, e0)

        # 1. loop current 1 -> 2 -> 4 -> 1
        on = VGroup(edges[0].copy().set_color(TEAL_C), edges[4].copy().set_color(TEAL_C))
        back = arrow(NODES[4] + 0.22 * (NODES[1] - NODES[4]) / np.linalg.norm(NODES[1] - NODES[4]),
                     NODES[1] - 0.22 * (NODES[1] - NODES[4]) / np.linalg.norm(NODES[1] - NODES[4]), color=ORANGE_C, width=4)
        w = M(("w", "w = (1, 0, 0, -1, 1)"), size=0.95, colors={"w": TEAL_C}).move_to([2.6, 1.6, 0])
        self.play(self.chip("current 1 around a loop"), ShowCreation(on[0]), run_time=0.6)
        self.play(ShowCreation(on[1]), run_time=0.6)
        self.play(ShowCreation(back), Write(w), run_time=1.0)
        self.step_done(edges, dots, nl, el, e0, on, back, w)

        # 2. node checks
        checks = VGroup(
            M(("a", r"\mathrm{node}\ 1:\ -w_1 - w_2 - w_4 = 0"), size=0.75),
            M(("a", r"\mathrm{node}\ 2:\ w_1 - w_3 - w_5 = 0"), size=0.75),
            M(("a", r"\mathrm{node}\ 3:\ w_2 + w_3 = 0"), size=0.75),
            M(("a", r"\mathrm{node}\ 4:\ w_4 + w_5 = 0"), size=0.75)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to([2.6, 0.2, 0])
        self.play(self.chip("rows of A transpose"), run_time=0.4)
        for k, ch in zip([1, 2, 3, 4], checks):
            self.play(Indicate(dots[k - 1], color=GREEN_C), FadeIn(ch, shift=0.1 * RIGHT), run_time=0.6)
        self.step_done(edges, dots, nl, el, e0, on, back, w, checks)

        # 3. count
        cnt = M(("c", "m - r = 5 - 3 = 2"), "=", ("e", "m - n + 1"), size=0.9, colors={"c": GREEN_C, "e": YELLOW_C}).move_to([2.6, -1.6, 0])
        eu = label("Euler: nodes − edges + loops = 4 − 5 + 2 = 1", 20, YELLOW_C).move_to([2.6, -2.3, 0])
        self.play(self.chip("independent loops"), Write(cnt), run_time=1.0)
        self.play(FadeIn(eu), run_time=0.6)
        self.step_done(edges, dots, nl, el, e0, on, back, w, checks, cnt, eu)
