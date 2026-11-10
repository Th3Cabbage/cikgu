"""Step-by-step content of the Unit 11 animations, Numerical Methods for ODEs (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-6). Explanations are original paraphrases of Cleve
Moler's MIT Learn Differential Equations videos 57-65 and Strang, Sections 3.4-3.5.

The module name is kept from the shared scaffold (ctl_common.py imports it).
"""

RELATIONS = {
    "define": "Definition / choice",
    "model": "Modelling step",
    "classify": "Classification",
    "diagram": "Picture",
    "substitute": "Substitution",
    "identity": "Identity (=)",
    "equivalent": "Equivalent statement (⇔)",
    "solve": "Solve",
    "compute": "Computation",
    "implies": "Consequence (⇒)",
    "compare": "Check",
    "caution": "Caveat",
    "recap": "Recap",
}

SEQUENCES = [
    {
        "id": "euler-steps",
        "scene": "EulerStepsSequence",
        "section": 1,
        "title": "Euler on $y' = 2y$, $y(0) = 10$, $h = 1$",
        "summary": "Each step follows the tangent at its left end: $30$, $90$, $270$, falling ever further below $10e^{2t}$.",
        "initial": {"title": "Exact solution", "tex": r"y = 10e^{2t}",
                    "explanation": "The values grow fast; Euler will lag behind."},
        "steps": [
            {"title": "First step", "relation": "compute",
             "tex": r"s_1 = 2\cdot10 = 20,\quad y_1 = 10 + 1\cdot20 = 30",
             "explanation": "Follow the tangent line for one unit of time."},
            {"title": "Two more steps", "relation": "compute",
             "tex": r"y_2 = 30 + 60 = 90,\qquad y_3 = 90 + 180 = 270",
             "explanation": "Each step multiplies by $1 + 2h = 3$."},
            {"title": "The error", "relation": "compare",
             "tex": r"y(3) = 10e^6 \approx 4034 \gg 270",
             "explanation": "The left-end slope is the smallest slope on each interval of a growing solution."},
        ],
    },
    {
        "id": "rk4-stages",
        "scene": "RK4StagesSequence",
        "section": 2,
        "title": "Midpoint and RK4: better slopes inside the step",
        "summary": "From $y_0 = 10$ with $h = 1$: midpoint gives $50$, RK4's four slopes $20, 40, 60, 140$ give $70$ (exact $73.9$).",
        "initial": {"title": "One step of $y' = 2y$", "tex": r"y_0 = 10,\quad h = 1,\quad y(1) = 10e^2 \approx 73.9",
                    "explanation": "Compare three ways of choosing the slope."},
        "steps": [
            {"title": "Midpoint", "relation": "compute",
             "tex": r"s_2 = f(\tfrac12,\ 10 + \tfrac12\cdot20) = 40,\quad y_1 = 10 + 40 = 50",
             "explanation": "An Euler half step finds the midpoint; its slope carries the full step."},
            {"title": "Four RK4 slopes", "relation": "compute",
             "tex": r"s_1 = 20,\ s_2 = 40,\ s_3 = 60,\ s_4 = 140",
             "explanation": "Start, midpoint twice (the second using $s_2$), end (using $s_3$)."},
            {"title": "Weighted average", "relation": "implies",
             "tex": r"y_1 = 10 + \tfrac16(20 + 80 + 120 + 140) = 70",
             "explanation": "Weights $1, 2, 2, 1$; the closest of the three to $73.9$."},
        ],
    },
    {
        "id": "order-plot",
        "scene": "OrderPlotSequence",
        "section": 3,
        "title": "Reading the order from a log-log plot",
        "summary": "On $y' = 1/(1+t)^2$, errors at $h = 0.1$ and $0.05$ fall by factors $2$, $4$, $16$: slopes $1$, $2$, $4$.",
        "initial": {"title": "The experiment", "tex": r"\int_0^1\frac{dt}{(1+t)^2} = \frac12",
                    "explanation": "Integrate with $h = 0.1$ and $h = 0.05$ and compare errors."},
        "steps": [
            {"title": "ODE1", "relation": "compute",
             "tex": r"0.5390,\ 0.5191:\ \text{ratio} \approx 2,\ p = 1",
             "explanation": "Halving $h$ halves the error."},
            {"title": "ODE2", "relation": "compute",
             "tex": r"0.49927,\ 0.49982:\ \text{ratio} \approx 4,\ p = 2",
             "explanation": "The midpoint error falls by $4$."},
            {"title": "ODE4", "relation": "compute",
             "tex": r"\text{ratio} \approx 16,\ p = 4",
             "explanation": "On a log-log plot of error against $h$, the slope is the order."},
        ],
    },
    {
        "id": "bs23-control",
        "scene": "BS23ControlSequence",
        "section": 4,
        "title": "An adaptive step: estimate, test, adjust",
        "summary": "BS23 computes three slopes, a third-order step, a fourth slope and an error estimate; the step is accepted or rejected and $h$ is rescaled.",
        "initial": {"title": "BS23 stages", "tex": r"s_1,\ s_2\ (t + \tfrac h2),\ s_3\ (t + \tfrac34h)",
                    "explanation": "Three slopes inside the step."},
        "steps": [
            {"title": "Step and new slope", "relation": "compute",
             "tex": r"y_{n+1} = y_n + \tfrac h9(2s_1 + 3s_2 + 4s_3),\quad s_4 = f(t_{n+1}, y_{n+1})",
             "explanation": "Third-order result; $s_4$ will be reused (FSAL)."},
            {"title": "Error estimate", "relation": "compute",
             "tex": r"e = \tfrac{h}{72}(-5s_1 + 6s_2 + 8s_3 - 9s_4)",
             "explanation": "The difference from an embedded second-order formula."},
            {"title": "Test and adjust", "relation": "classify",
             "tex": r"\frac{|e|}{|y|} \le \text{tol}:\ \text{accept};\quad h \leftarrow 0.8\,h\left(\frac{\text{tol}}{\text{err}}\right)^{1/3}",
             "explanation": "Too large: reject and retry with a smaller $h$; small: accept and grow $h$ (at most $5$ times)."},
        ],
    },
    {
        "id": "stiff-euler",
        "scene": "StiffEulerSequence",
        "section": 5,
        "title": "Stiffness: explicit Euler explodes, implicit Euler decays",
        "summary": "For $y' = -100y$ with $h = 0.05$: Euler multiplies by $-4$ each step; backward Euler by $\\tfrac16$.",
        "initial": {"title": "A fast decay", "tex": r"y' = -100y,\quad y(0) = 1,\quad h = 0.05",
                    "explanation": "The true solution $e^{-100t}$ is essentially zero after $t = 0.05$."},
        "steps": [
            {"title": "Explicit Euler", "relation": "caution",
             "tex": r"y_{n+1} = (1 - 100h)y_n = -4y_n:\ 1, -4, 16, -64",
             "explanation": "Alternating and growing: unstable because $|1 + h\\lambda| > 1$."},
            {"title": "Backward Euler", "relation": "solve",
             "tex": r"y_{n+1} = y_n - 100h\,y_{n+1}\ \Rightarrow\ y_{n+1} = \tfrac{1}{6}y_n",
             "explanation": "The slope at the end of the step; stable for every $h$."},
            {"title": "The limit", "relation": "implies",
             "tex": r"\text{Euler stable} \Leftrightarrow h \le \frac{2}{|\lambda|} = 0.02",
             "explanation": "Stability, not accuracy, limits explicit methods on stiff problems."},
        ],
    },
    {
        "id": "oscillator-drift",
        "scene": "OscillatorDriftSequence",
        "section": 6,
        "title": "A system: Euler spirals off the circle, RK4 stays on it",
        "summary": "$x'' + x = 0$ as $y' = (y_2, -y_1)$: Euler's radius grows by $\\sqrt{1 + h^2}$ per step.",
        "initial": {"title": "The oscillator", "tex": r"y_1' = y_2,\quad y_2' = -y_1,\quad y(0) = (0, 1)",
                    "explanation": "The exact solution goes round the unit circle."},
        "steps": [
            {"title": "Exact circle", "relation": "diagram",
             "tex": r"y = (\sin t,\ \cos t)",
             "explanation": "Period $2\\pi$."},
            {"title": "Euler", "relation": "caution",
             "tex": r"r_{n+1}^2 = (1 + h^2)\,r_n^2",
             "explanation": "With $36$ steps per turn the radius grows by about $1.7$ in one turn."},
            {"title": "RK4", "relation": "compare",
             "tex": r"|r - 1| < 10^{-5} \text{ after one turn}",
             "explanation": "Same step size, four slopes per step: indistinguishable from the circle."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
