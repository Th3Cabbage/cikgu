"""Step-by-step content of the Unit 2 animations, Nonlinear First Order Equations (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-3). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 11-13 and Strang, Sections 1.7-1.8.

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
        "id": "logistic-z",
        "scene": "LogisticZSequence",
        "section": 1,
        "title": "The substitution $z = 1/y$ makes the logistic equation linear",
        "summary": "The chain rule, one division by $y^2$, a linear solve, and a flip back to $y$.",
        "initial": {"title": "Growth with competition", "tex": r"y' = a\,y - b\,y^2",
                    "explanation": "Births minus competition. The $y^2$ term makes it nonlinear."},
        "steps": [
            {"title": "Chain rule for $z = 1/y$", "relation": "define",
             "tex": r"z = \frac{1}{y} \;\Rightarrow\; z' = -\frac{y'}{y^2}",
             "explanation": "The derivative of $y^{-1}$ is $-y^{-2}$, times $y'$."},
            {"title": "Substitute $y'$", "relation": "substitute",
             "tex": r"z' = -\frac{a y - b y^2}{y^2} = -\frac{a}{y} + b = -a z + b",
             "explanation": "Divide each term by $y^2$. What remains is $1/y = z$ to the first power: a linear equation."},
            {"title": "Solve, then flip", "relation": "solve",
             "tex": r"z = \frac{b}{a} + \Big(z(0) - \frac{b}{a}\Big)e^{-at} \;\Rightarrow\; y = \frac{a}{b + d\,e^{-at}}",
             "explanation": "Steady value $b/a$ plus a decaying null part. Then $y = 1/z$, with $d = a/y(0) - b$."},
        ],
    },
    {
        "id": "s-curve",
        "scene": "SCurveSequence",
        "section": 1,
        "title": "S-curves between the steady states $0$ and $a/b$",
        "summary": "From $y(0) = 1/4$ the solution bends at half capacity; every positive start ends at $a/b$.",
        "initial": {"title": "Axes for $y' = y - y^2$", "tex": r"y' = y - y^2 \quad (a = b = 1)",
                    "explanation": "Carrying capacity $a/b = 1$."},
        "steps": [
            {"title": "One S-curve", "relation": "diagram",
             "tex": r"y = \frac{1}{1 + 3e^{-t}}",
             "explanation": "Starting at $1/4$: slow, fast, slow."},
            {"title": "The bend at half capacity", "relation": "compute",
             "tex": r"y'' = (1 - 2y)\,y' = 0 \;\text{ at } y = \tfrac12,\ t = \ln 3",
             "explanation": "Growth is fastest where $y = a/(2b)$."},
            {"title": "Other starting values", "relation": "implies",
             "tex": r"y(0) > 0 \;\Rightarrow\; y(t) \to \frac{a}{b}",
             "explanation": "From below the curve rises, from above it falls; $0$ repels and $1$ attracts."},
        ],
    },
    {
        "id": "stability-test",
        "scene": "StabilityTestSequence",
        "section": 2,
        "title": "The slope $f'(Y)$ decides stability",
        "summary": "Tangent lines of $f(y) = y - y^2$ at its roots: slope $+1$ at $0$, $-1$ at $1$.",
        "initial": {"title": "Graph of $f$", "tex": r"y' = f(y) = y - y^2",
                    "explanation": "The height of the graph is the velocity of $y$."},
        "steps": [
            {"title": "Steady states are roots", "relation": "solve",
             "tex": r"f(Y) = Y(1 - Y) = 0 \;\Rightarrow\; Y = 0,\ Y = 1",
             "explanation": "Where the graph crosses zero, $y$ does not move."},
            {"title": "Tangent lines at the roots", "relation": "compute",
             "tex": r"f'(y) = 1 - 2y:\quad f'(0) = +1,\quad f'(1) = -1",
             "explanation": "Near each root, $f$ looks like its tangent line."},
            {"title": "The linear equation for the gap", "relation": "implies",
             "tex": r"(y - Y)' \approx f'(Y)\,(y - Y) \;\Rightarrow\; y - Y \approx C\,e^{f'(Y)t}",
             "explanation": "Negative slope: the gap decays (stable). Positive slope: it grows (unstable)."},
        ],
    },
    {
        "id": "stability-line",
        "scene": "StabilityLineSequence",
        "section": 2,
        "title": "The stability line for $y' = y - y^3$",
        "summary": "The sign of $f$ on each interval sets an arrow; arrows into a point mean stable.",
        "initial": {"title": "Three steady states", "tex": r"f(y) = y - y^3 = y(1 - y)(1 + y)",
                    "explanation": "Roots at $-1$, $0$ and $1$."},
        "steps": [
            {"title": "Sign of $f$ on each interval", "relation": "classify",
             "tex": r"f > 0 \text{ on } (-\infty,-1) \cup (0,1),\qquad f < 0 \text{ on } (-1,0) \cup (1,\infty)",
             "explanation": "Positive $f$ moves $y$ up (right on the line), negative $f$ moves it down."},
            {"title": "Arrows on the line", "relation": "diagram",
             "tex": r"\longrightarrow\ -1\ \longleftarrow\ \ 0\ \longrightarrow\ 1\ \longleftarrow",
             "explanation": "The arrows copy the signs onto one line of $y$ values."},
            {"title": "Read off stability", "relation": "implies",
             "tex": r"-1,\ 1 \text{ stable } (f' = -2),\qquad 0 \text{ unstable } (f' = 1)",
             "explanation": "Arrows point into $\\pm1$ and away from $0$, which agrees with the slope test."},
        ],
    },
    {
        "id": "separate",
        "scene": "SeparateSequence",
        "section": 3,
        "title": "Separating $y' = t/y$",
        "summary": "Move $y$ to one side and $t$ to the other, integrate, and solve for $y$; from $y(0) = 0$ two solutions appear.",
        "initial": {"title": "A separable equation", "tex": r"\frac{dy}{dt} = \frac{t}{y}",
                    "explanation": "A function of $t$ divided by a function of $y$."},
        "steps": [
            {"title": "Separate", "relation": "identity",
             "tex": r"y\,dy = t\,dt",
             "explanation": "Multiply both sides by $y\\,dt$."},
            {"title": "Integrate from the start", "relation": "compute",
             "tex": r"\tfrac12 y^2 - \tfrac12 y(0)^2 = \tfrac12 t^2",
             "explanation": "Integrate $y$ from $y(0)$ to $y(t)$ and $t$ from $0$ to $t$."},
            {"title": "Solve for $y$", "relation": "solve",
             "tex": r"y(t) = \sqrt{y(0)^2 + t^2}",
             "explanation": "Positive root for a positive start: hyperbola branches."},
            {"title": "A start at zero", "relation": "caution",
             "tex": r"y(0) = 0:\quad y = t \ \text{ and } \ y = -t \quad (t \neq 0)",
             "explanation": "At the start $t/y$ is $0/0$. Both lines satisfy the equation for $t \\neq 0$ and run into the origin, but neither is a solution at $t = 0$ itself: the guarantee of one solution is lost."},
        ],
    },
    {
        "id": "partial-fractions",
        "scene": "PartialFractionsSequence",
        "section": 3,
        "title": "The logistic equation by partial fractions",
        "summary": "Split $1/(y - y^2)$ into two simple fractions, integrate to logarithms, and solve.",
        "initial": {"title": "Separated logistic equation", "tex": r"\frac{dy}{y - y^2} = dt",
                    "explanation": "Here $g(t) = 1$ and $f(y) = 1/(y - y^2)$."},
        "steps": [
            {"title": "Factor and split", "relation": "identity",
             "tex": r"\frac{1}{y(1 - y)} = \frac{A}{y} + \frac{B}{1 - y}",
             "explanation": "Two simple poles, at $y = 0$ and $y = 1$."},
            {"title": "Find $A$ and $B$", "relation": "compute",
             "tex": r"1 = A(1 - y) + B\,y \;\Rightarrow\; A = 1 \ (y = 0),\ \ B = 1 \ (y = 1)",
             "explanation": "Multiply through by $y(1-y)$ and put in the two roots."},
            {"title": "Integrate to logarithms", "relation": "compute",
             "tex": r"\ln|y| - \ln|1 - y| = t + C",
             "explanation": "$\\int dy/(1-y) = -\\ln|1-y|$. Absolute values keep starts below $0$ and above $1$."},
            {"title": "Solve for $y$", "relation": "solve",
             "tex": r"\frac{y}{1 - y} = K e^{t} \;\Rightarrow\; y = \frac{1}{1 + e^{-t}/K}",
             "explanation": "Here $K = y(0)/(1 - y(0))$ may have either sign, and $1/K = d$. The constant solutions $y = 0$ and $y = 1$, lost by the division, are added back. The $z = 1/y$ route was shorter."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
