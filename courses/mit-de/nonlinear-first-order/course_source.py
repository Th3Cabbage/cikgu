"""Source of courses/mit-de/nonlinear-first-order/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\nonlinear-first-order\\course_source.py

Unit 2 of the MIT Learn Differential Equations companion: playlist videos 11-13 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Sections 1.7-1.8.
All text is original, written for this guide; it paraphrases the lectures and the book without
quoting. Examples marked "authored" are not from the lectures. Book references give printed
pages; the local PDF page is printed + 12.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "course.json")
PLAYLIST = "https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG"


def bk(printed, label):
    return {"printed": printed, "pdf": printed + 12, "label": label}


def vs(v, t, label):
    return {"v": v, "t": t, "label": label}


VIDEOS = [
    (11, "TCkLSYxx21c", "The Logistic Equation", "13:27"),
    (12, "NmntYoB1uJg", "The Stability and Instability of Steady States", "21:15"),
    (13, "_FATUw506mE", "Separable Equations", "13:07"),
]

SECTIONS = [
    {
        "nav": "The logistic equation",
        "v": 11,
        "title": r"Growth limited by competition: $y' = ay - by^2$",
        "summary": r"The logistic equation adds a competition term $-by^2$ to exponential growth. The substitution $z = 1/y$ makes it linear, $z' = -az + b$, and gives $y(t) = \dfrac{a}{b + d\,e^{-at}}$. Every positive start approaches the carrying capacity $a/b$ along an S-shaped curve.",
        "time": [0, 807],
        "goals": [
            r"Explain the competition term $-by^2$ and why it stops growth.",
            r"Use $z = 1/y$ to turn the logistic equation into a linear one and solve it.",
            r"Find the steady states $0$ and $a/b$ and describe the S-curve between them."
        ],
        "notes": [
            {"heading": "The model",
             "paragraphs": [
                 r"For a population $y$ with more births than deaths, $y' = ay$ alone predicts exponential growth forever. Real populations compete for space and food. The number of possible encounters between members grows like $y \cdot y$, so the model subtracts a term $by^2$: $y' = ay - by^2$. When $y$ is small the linear term wins and growth is nearly exponential; when $y$ is large the square wins and growth stops."
             ]},
            {"heading": "The trick: z = 1/y",
             "paragraphs": [
                 r"Nonlinear equations rarely have formulas, but this one does. Let $z = 1/y$. By the chain rule $z' = -y^{-2}\,y'$. Substitute $y' = ay - by^2$: $z' = -\dfrac{ay - by^2}{y^2} = -\dfrac{a}{y} + b = -az + b$.",
                 r"That is a linear equation with a constant input, solved in Unit 1: $z(t) = \dfrac{b}{a} + \left(z(0) - \dfrac{b}{a}\right)e^{-at}$. Turning back with $y = 1/z$ puts the exponential in the denominator:",
                 r"$y(t) = \dfrac{a}{b + d\,e^{-at}}, \qquad d = \dfrac{a}{y(0)} - b.$"
             ]},
            {"heading": "The S-curve",
             "paragraphs": [
                 r"As $t \to \infty$ the term $d e^{-at}$ vanishes (for $a > 0$) and $y \to a/b$, the carrying capacity. Run time backwards, $t \to -\infty$, and the denominator becomes huge, so $y \to 0$. In between the solution rises slowly, then fast, then slowly again: an S-shaped or sigmoid curve. It bends over where $y'' = (a - 2by)\,y' = 0$, at half the capacity, $y = a/(2b)$.",
                 r"A population that starts above $a/b$ has $y' < 0$ and decreases towards $a/b$ from above."
             ]},
            {"heading": "Steady states",
             "paragraphs": [
                 r"A steady state is a constant solution: $y' = 0$, so $ay - by^2 = y(a - by) = 0$. The two are $Y = 0$ and $Y = a/b$. Start exactly at either and nothing ever changes. Start near $0$ (but positive) and the population leaves: $Y = 0$ is unstable. Start near $a/b$ and it returns: $Y = a/b$ is stable. The next section turns this into a test for any equation $y' = f(y)$."
             ]}
        ],
        "keyIdeas": [
            r"$y' = ay - by^2$: growth minus competition.",
            r"$z = 1/y$ gives $z' = -az + b$ (linear).",
            r"$y = \dfrac{a}{b + d e^{-at}}$, $d = a/y(0) - b$.",
            r"Steady states $0$ (unstable) and $a/b$ (stable)."
        ],
        "example": {
            "title": "A population at a quarter of capacity (authored)",
            "problem": r"Solve $y' = y - y^2$ with $y(0) = \tfrac14$. When does it reach half the capacity?",
            "steps": [
                {"text": "Here a = b = 1, so d = a/y(0) - b = 4 - 1 = 3.", "tex": r"y(t) = \frac{1}{1 + 3e^{-t}}"},
                {"text": "Half the capacity a/b = 1 is 1/2: solve 1 + 3e^{-t} = 2.", "tex": r"e^{-t} = \tfrac13 \;\Rightarrow\; t = \ln 3 \approx 1.10"},
                {"text": "That is also the inflection point y = a/(2b), where growth is fastest.", "tex": r"y'' = (1 - 2y)\,y' = 0 \text{ at } y = \tfrac12"}
            ],
            "answer": r"$y = 1/(1 + 3e^{-t})$; it reaches $\tfrac12$ at $t = \ln 3$, where the S-curve is steepest."
        },
        "sources": {
            "video": [vs(11, 0, "Growth cut off by competition"),
                      vs(11, 60, "y times y counts interactions"),
                      vs(11, 90, "The logistic equation has a neat trick"),
                      vs(11, 120, "z = 1/y gives a linear equation"),
                      vs(11, 180, "dz/dt = -y^(-2) dy/dt"),
                      vs(11, 210, "Result: dz/dt = -az + b"),
                      vs(11, 240, "Solve for z, then y = 1/z"),
                      vs(11, 300, "The constant d comes from y(0)"),
                      vs(11, 330, "It cannot grow forever"),
                      vs(11, 420, "Approach to a/b"),
                      vs(11, 450, "S-curve, sigmoid"),
                      vs(11, 510, "Steady states"),
                      vs(11, 600, "Y = 0 or Y = a/b"),
                      vs(11, 720, "a/b stable, 0 unstable"),
                      vs(11, 750, "Next: dy/dt = f(y)")],
            "book": [bk(53, "Section 1.7: the logistic equation"),
                     bk(54, "Solving with z = 1/y; the S-curve")]
        },
        "tutorNotes": "Video 11. y' = ay - by^2. z = 1/y: z' = -y^-2 y' = -az + b. z = b/a + (z0 - b/a) e^(-at). y = a/(b + d e^(-at)), d = a/y(0) - b. t -> infinity: a/b; t -> -infinity: 0; inflection at a/(2b). Steady states 0 (unstable) and a/b (stable)."
    },
    {
        "nav": "Stability of steady states",
        "v": 12,
        "title": r"Stable or unstable: the sign of $df/dy$",
        "summary": r"For $y' = f(y)$, a steady state $Y$ has $f(Y) = 0$. It is stable when $f'(Y) < 0$ and unstable when $f'(Y) > 0$, because near $Y$ the difference $y - Y$ behaves like $e^{f'(Y)t}$. A stability line with arrows shows every solution's direction at a glance.",
        "time": [0, 1275],
        "goals": [
            r"Find steady states by solving $f(Y) = 0$.",
            r"Apply the test: $f'(Y) < 0$ stable, $f'(Y) > 0$ unstable, $f'(Y) = 0$ undecided.",
            r"Explain the test by the linear approximation $f(y) \approx f'(Y)(y - Y)$.",
            r"Draw the stability line for $y - y^2$ and $y - y^3$."
        ],
        "notes": [
            {"heading": "Steady states and stability",
             "paragraphs": [
                 r"An autonomous equation $y' = f(y)$ has a right side that depends on $y$ alone. A steady state $Y$ is a root of $f$: if $y$ starts there, $y' = 0$ and it stays there. The question for every application is what happens when $y$ starts near $Y$. If it is pulled back, $Y$ is stable; if it is pushed away, $Y$ is unstable.",
                 r"Three examples carry the lecture: $y' = ay$ with $Y = 0$; the logistic $y' = y - y^2$ with $Y = 0$ and $1$; and $y' = y - y^3$ with $Y = 0, 1, -1$."
             ]},
            {"heading": "The test",
             "paragraphs": [
                 r"For the linear case the answer is known: $y = Ce^{at}$ goes to $0$ exactly when $a < 0$. For a nonlinear $f$, the number that plays the role of $a$ is the slope $f'(Y)$ at the steady state: stable if $f'(Y) < 0$, unstable if $f'(Y) > 0$.",
                 r"Logistic: $f = y - y^2$, $f' = 1 - 2y$. At $0$ it is $+1$ (unstable); at $1$ it is $-1$ (stable). Cubic: $f = y - y^3$, $f' = 1 - 3y^2$. At $0$ it is $+1$ (unstable); at $\pm1$ it is $-2$ (both stable)."
             ]},
            {"heading": "Why the slope decides",
             "paragraphs": [
                 r"Write $y = Y + \Delta$ with a small $\Delta$. Since $f(Y) = 0$, the tangent line gives $f(y) \approx f(Y) + f'(Y)\,\Delta = f'(Y)\,\Delta$. And $y' = \Delta'$ because $Y$ is constant. So $\Delta' \approx f'(Y)\,\Delta$: a linear equation with rate $f'(Y)$, whose solutions behave like $e^{f'(Y)t}$. A negative rate shrinks the gap; a positive one grows it.",
                 r"If $f'(Y) = 0$ the linear term gives no information, and the higher terms decide. The test is then silent."
             ]},
            {"heading": "A book in the air",
             "paragraphs": [
                 r"Strang throws a book spinning about each of its three axes. About the longest and the shortest axes it turns cleanly; about the middle axis it tumbles. This is stability in three dimensions, and it returns in Unit 12 with a system of equations."
             ]},
            {"heading": "The stability line",
             "paragraphs": [
                 r"Mark the steady states on a line of $y$ values and draw an arrow on each interval in the direction of the sign of $f$: right where $f > 0$ ($y$ increases), left where $f < 0$. Arrows pointing into a steady state from both sides mean stable; arrows pointing away mean unstable. For $y - y^3$ the arrows run into $-1$ and $1$ and away from $0$, without any formula for the solutions."
             ]}
        ],
        "keyIdeas": [
            r"Steady state: $f(Y) = 0$.",
            r"$f'(Y) < 0$ stable, $f'(Y) > 0$ unstable.",
            r"Near $Y$: $(y - Y)' \approx f'(Y)(y - Y)$.",
            r"Stability line: arrows follow the sign of $f$."
        ],
        "example": {
            "title": "Two steady states of y' = y^2 - 1 (authored)",
            "problem": r"Find and classify the steady states of $y' = y^2 - 1$. What happens to a solution that starts at $y(0) = 0$?",
            "steps": [
                {"text": "Steady states solve f(Y) = 0.", "tex": r"Y^2 - 1 = 0 \;\Rightarrow\; Y = -1,\ Y = 1"},
                {"text": "Slope f'(y) = 2y at each.", "tex": r"f'(-1) = -2 < 0 \ \text{(stable)},\qquad f'(1) = 2 > 0 \ \text{(unstable)}"},
                {"text": "At y = 0, f(0) = -1 < 0, so y decreases.", "tex": r"y(0) = 0 \;\longrightarrow\; y(t) \to -1"}
            ],
            "answer": r"$Y = -1$ is stable and $Y = 1$ unstable. Starting at $0$ (between them, where $f < 0$) the solution falls to $-1$."
        },
        "sources": {
            "video": [vs(12, 0, "Stability or instability of a steady state"),
                      vs(12, 30, "Steady state: f(Y) = 0"),
                      vs(12, 90, "Stable: nearby solutions return"),
                      vs(12, 120, "Example y' = ay"),
                      vs(12, 150, "Logistic y - y^2: Y = 0 or 1"),
                      vs(12, 210, "y - y^3: Y = 0, 1, -1"),
                      vs(12, 270, "Linear: stable when a < 0"),
                      vs(12, 330, "Test: df/dy negative at Y"),
                      vs(12, 390, "Logistic: 1 - 2y"),
                      vs(12, 480, "Cubic: 1 - 3y^2"),
                      vs(12, 600, "Why the test works"),
                      vs(12, 690, "Approximate f(y) - f(Y) by the slope"),
                      vs(12, 750, "A linear equation with rate f'(Y)"),
                      vs(12, 840, "Tumbling book experiment"),
                      vs(12, 990, "The stability line"),
                      vs(12, 1050, "Logistic on the line"),
                      vs(12, 1170, "Cubic: arrows into -1 and 1")],
            "book": [bk(58, "Section 1.7: stability of steady states, the sign of df/dy")]
        },
        "tutorNotes": "Video 12. y' = f(y); steady state f(Y) = 0; stable if f'(Y) < 0, unstable if f'(Y) > 0, undecided if 0. Reason: y = Y + D, D' ~ f'(Y) D. Logistic y - y^2: f' = 1 - 2y, 0 unstable, 1 stable. Cubic y - y^3: f' = 1 - 3y^2, 0 unstable, +-1 stable. Tumbling book: stable about longest and shortest axes, unstable about the middle axis. Stability line: arrows follow sign of f."
    },
    {
        "nav": "Separable equations",
        "v": 13,
        "title": r"Separable equations: $\int f(y)\,dy = \int g(t)\,dt$",
        "summary": r"When $y' = g(t)/f(y)$, the variables separate: $f(y)\,dy = g(t)\,dt$. Integrate both sides, then solve for $y$. For $y' = t/y$ this gives $y = \sqrt{y(0)^2 + t^2}$; at the start $y(0) = 0$ the equation is $0/0$ and uniqueness is lost. The logistic equation separates too, with partial fractions.",
        "time": [0, 787],
        "goals": [
            r"Recognise a separable equation and separate it.",
            r"Integrate both sides with matching limits and solve for $y$.",
            r"Notice where a solution can fail to be unique.",
            r"Use partial fractions $\dfrac{1}{y - y^2} = \dfrac{1}{y} + \dfrac{1}{1-y}$ for the logistic equation."
        ],
        "notes": [
            {"heading": "What separable means",
             "paragraphs": [
                 r"The right side is a function of $t$ times a function of $y$: write $y' = g(t)/f(y)$. Then $t$ and $y$ can be moved to different sides: $f(y)\,dy = g(t)\,dt$. The equation $y' = y + t$ is not separable, because a sum cannot be split this way.",
                 r"The simplest case $f = 1$ is $y' = g(t)$, which is just calculus: $y$ is an integral of $g$."
             ]},
            {"heading": "The method",
             "paragraphs": [
                 r"Integrate both sides from the start to the present: $\displaystyle\int_{y(0)}^{y(t)} f(y)\,dy = \int_0^t g(s)\,ds$. Two integrals, and then one more step: the left side is some function of $y$, which must be solved for $y$ itself. That last step is not always possible in closed form."
             ]},
            {"heading": "Example: y' = t/y",
             "paragraphs": [
                 r"Separate: $y\,dy = t\,dt$. Integrate: $\tfrac12 y(t)^2 - \tfrac12 y(0)^2 = \tfrac12 t^2$. Solve: $y(t) = \sqrt{y(0)^2 + t^2}$ (taking the positive root when $y(0) > 0$).",
                 r"Look for dangerous points. At $y = 0$ the right side $t/y$ is undefined, and the start $y(0) = 0$ at $t = 0$ makes it $0/0$. For every $t \neq 0$, both $y = t$ and $y = -t$ satisfy the equation ($y' = \pm 1 = t/y$), and both run into the origin. So the formula offers two candidates through one starting point, but neither is a classical solution at $t = 0$ itself, where the equation has no meaning. The existence and uniqueness guarantee needs a right side that behaves well at the start; here it does not."
             ]},
            {"heading": "The logistic equation, separated",
             "paragraphs": [
                 r"$y' = y - y^2$ is separable with $g = 1$: $\dfrac{dy}{y - y^2} = dt$. The left side needs partial fractions: split $\dfrac{1}{y - y^2} = \dfrac{1}{y(1-y)}$ into $\dfrac{A}{y} + \dfrac{B}{1-y}$. Here $A = B = 1$. Then each piece integrates to a logarithm: $\ln|y| - \ln|1 - y| = t + C$. Exponentiating gives $\dfrac{y}{1 - y} = Ke^{t}$ with $K = \dfrac{y(0)}{1 - y(0)}$ of either sign, which covers starts below $0$, between $0$ and $1$, and above $1$. Solving gives the logistic curve again.",
                 r"Dividing by $y - y^2$ assumed $y \neq 0$ and $y \neq 1$. Those two constant solutions are lost in the division and must be added back separately.",
                 r"It works, but the $z = 1/y$ trick of Section 1 was quicker. Partial fractions return with the Laplace transform in Unit 5."
             ]}
        ],
        "keyIdeas": [
            r"Separable: $y' = g(t)/f(y)$.",
            r"$\int_{y(0)}^{y} f\,dy = \int_0^t g\,dt$, then solve for $y$.",
            r"$y' = t/y$: $\;y = \sqrt{y(0)^2 + t^2}$.",
            r"$y(0) = 0$: $t/y$ is $0/0$; $y = \pm t$ fit for $t \neq 0$ but no unique solution starts there."
        ],
        "example": {
            "title": "A solution that blows up (authored)",
            "problem": r"Solve $y' = t\,y^2$ with $y(0) = \tfrac12$.",
            "steps": [
                {"text": "Separate: f(y) = 1/y^2, g(t) = t.", "tex": r"\int_{1/2}^{y} \frac{dy}{y^2} = \int_0^t s\,ds"},
                {"text": "Integrate both sides.", "tex": r"-\frac{1}{y} + 2 = \frac{t^2}{2}"},
                {"text": "Solve for y.", "tex": r"y(t) = \frac{1}{2 - t^2/2} = \frac{2}{4 - t^2}"}
            ],
            "answer": r"$y = 2/(4 - t^2)$, which becomes infinite at $t = 2$: a nonlinear equation can blow up in finite time, which a linear one cannot."
        },
        "sources": {
            "video": [vs(13, 0, "Separable equations, including nonlinear ones"),
                      vs(13, 30, "y' = y + t is not separable"),
                      vs(13, 60, "Simplest case dy/dt = g(t)"),
                      vs(13, 120, "Separate and integrate both sides"),
                      vs(13, 150, "Two integrals, then solve for y"),
                      vs(13, 210, "Example y' = t/y"),
                      vs(13, 240, "Integrate: (1/2) y^2"),
                      vs(13, 300, "y = sqrt(y(0)^2 + t^2)"),
                      vs(13, 330, "Dangerous points"),
                      vs(13, 390, "y = t solves it"),
                      vs(13, 420, "So does y = -t"),
                      vs(13, 450, "Logistic equation by separation"),
                      vs(13, 510, "Integral of 1/(y - y^2)"),
                      vs(13, 570, "Partial fractions"),
                      vs(13, 660, "Integrate to logarithms"),
                      vs(13, 690, "The z = 1/y trick was quicker")],
            "book": [bk(65, "Section 1.8: separable equations, Example 1"),
                     bk(66, "The logistic equation by separation"),
                     bk(56, "Section 1.7: partial fractions")]
        },
        "tutorNotes": "Video 13. Separable y' = g(t)/f(y): integral f(y) dy from y(0) to y = integral g dt from 0 to t, then solve for y. y' = y + t is not separable. y' = t/y: y = sqrt(y(0)^2 + t^2); from y(0) = 0 the right side is 0/0: y = t and y = -t satisfy the equation for t != 0 and both reach the origin, but neither is a classical solution at t = 0 (no existence/uniqueness guarantee there). Logistic by partial fractions: 1/(y - y^2) = 1/y + 1/(1 - y), ln|y| - ln|1 - y| = t + C, y/(1 - y) = K e^t with K = y0/(1 - y0); the constant solutions 0 and 1 are lost by the division and restored separately."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-competition", r"In $y' = ay - by^2$ with $a, b > 0$, why does the population stop growing?", [
        (r"For large $y$ the term $by^2$ outgrows $ay$, so $y'$ becomes $0$ at $y = a/b$ and negative above it.", True, r"Right. The square wins for large $y$; the balance point is the carrying capacity $a/b$."),
        (r"Because $b$ is negative.", False, r"No. With $b > 0$ the term $-by^2$ is what slows growth."),
        (r"It never stops; the solution grows like $e^{at}$.", False, r"No. That is the linear model without competition."),
        (r"Because $y$ reaches $a$.", False, r"No. Setting $ay - by^2 = 0$ gives $y = a/b$, not $a$ (unless $b = 1$).")]),
    q("q-z", r"With $z = 1/y$, what equation does $y' = ay - by^2$ become?", [
        (r"$z' = -az + b$", True, r"Right. $z' = -y^{-2}y' = -a/y + b = -az + b$: linear with a constant input."),
        (r"$z' = az - b$", False, r"No. The chain rule gives $z' = -y^{-2}y'$; the minus sign flips both terms."),
        (r"$z' = -az^2 + b$", False, r"No. Dividing $ay$ by $y^2$ leaves $a/y = az$, to the first power."),
        (r"$z' = 1/(ay - by^2)$", False, r"No. The derivative of $1/y$ is not $1/y'$.")]),
    q("q-limit", r"What does the logistic solution $y = \dfrac{a}{b + de^{-at}}$ approach as $t \to \infty$ (with $a > 0$)?", [
        (r"$a/b$", True, r"Right. $de^{-at} \to 0$, leaving $a/b$, the carrying capacity."),
        (r"$0$", False, r"No. That is the limit as $t \to -\infty$."),
        (r"$a/d$", False, r"No. The $d$ term is the one that disappears."),
        (r"Infinity", False, r"No. The competition term prevents unlimited growth.")]),
    q("q-test", r"For $y' = f(y)$ with $f(Y) = 0$, when is $Y$ stable?", [
        (r"When $f'(Y) < 0$.", True, r"Right. Near $Y$, $(y - Y)' \approx f'(Y)(y - Y)$, which decays when the rate is negative."),
        (r"When $f(Y) < 0$.", False, r"No. $f(Y) = 0$ at every steady state; it is the slope that matters."),
        (r"When $f'(Y) > 0$.", False, r"No. A positive rate makes the gap grow like $e^{f'(Y)t}$: unstable."),
        (r"Always, because $Y$ is a constant solution.", False, r"No. Constant solutions can be unstable, like $Y = 0$ for the logistic equation.")]),
    q("q-cubic", r"For $y' = y - y^3$, which steady states are stable?", [
        (r"$Y = 1$ and $Y = -1$", True, r"Right. $f' = 1 - 3y^2 = -2$ at $\pm1$; at $0$ it is $+1$, unstable."),
        (r"Only $Y = 0$", False, r"No. $f'(0) = 1 > 0$, so $0$ is unstable."),
        (r"All three", False, r"No. The sign of $f'$ differs at $0$."),
        (r"Only $Y = 1$", False, r"No. $f$ is odd, so $-1$ behaves like $1$: $f'(-1) = -2$.")]),
    q("q-zero-slope", r"What does the test say when $f'(Y) = 0$?", [
        (r"Nothing: the linear approximation is zero, so higher-order terms decide.", True, r"Right. For example $y' = -y^3$ is stable at $0$ and $y' = y^3$ is unstable, and both have $f'(0) = 0$."),
        (r"$Y$ is stable.", False, r"No. $y' = y^3$ has $f'(0) = 0$ and is unstable."),
        (r"$Y$ is unstable.", False, r"No. $y' = -y^3$ has $f'(0) = 0$ and is stable."),
        (r"$Y$ is not a steady state.", False, r"No. Being a steady state only needs $f(Y) = 0$.")]),
    q("q-line", r"On a stability line, arrows point away from $Y$ on both sides. What does that mean?", [
        (r"$Y$ is unstable: solutions starting near it move away.", True, r"Right. Arrows follow the sign of $f$; arrows leaving $Y$ mean $f$ pushes $y$ away."),
        (r"$Y$ is stable.", False, r"No. Stable steady states have arrows pointing into them."),
        (r"$f(Y) \ne 0$.", False, r"No. Every point marked on the line is a steady state."),
        (r"The solution oscillates around $Y$.", False, r"No. A first order autonomous equation cannot oscillate: $y$ moves monotonically.")]),
    q("q-separable", r"Which equation is separable?", [
        (r"$y' = t\,e^{y}$", True, r"Right. It is $g(t) = t$ times a function of $y$: $e^{-y}dy = t\,dt$."),
        (r"$y' = y + t$", False, r"No. A sum of a $y$ part and a $t$ part cannot be written as a product."),
        (r"$y' = \sin(ty)$", False, r"No. $\sin(ty)$ does not split into a function of $t$ times a function of $y$."),
        (r"$y' = y^2 + t^2$", False, r"No. Again a sum, not a product.")]),
    q("q-ty", r"What is the solution of $y' = t/y$ with $y(0) = 3$?", [
        (r"$y = \sqrt{9 + t^2}$", True, r"Right. $\tfrac12y^2 - \tfrac92 = \tfrac12t^2$, so $y^2 = 9 + t^2$, positive root since $y(0) > 0$."),
        (r"$y = 3 + t$", False, r"No. Then $y' = 1$ but $t/y = t/(3 + t) \ne 1$."),
        (r"$y = 3 + \tfrac12 t^2$", False, r"No. That would solve $y' = t$, without the division by $y$."),
        (r"$y = 3e^{t^2/2}$", False, r"No. That solves $y' = ty$, a different separable equation.")]),
    q("q-unique", r"What goes wrong for $y' = t/y$ with the start $y(0) = 0$?", [
        (r"The right side is $0/0$ at the start, so the usual guarantee of one solution fails: $y = t$ and $y = -t$ both satisfy the equation for $t \neq 0$ and both run into the origin.", True, r"Right. Neither is a classical solution at $t = 0$ itself, because the equation is undefined there. The formula gives two candidates, not a unique answer."),
        (r"Nothing: $y = 0$ is the unique solution.", False, r"No. $y = 0$ makes $t/y$ undefined for every $t$; it is not a solution."),
        (r"Nothing: $y = \sqrt{t^2}$ is the unique solution.", False, r"No. $|t|$ is not differentiable at $0$, and $y = -|t|$ fits just as well for $t \neq 0$."),
        (r"The separation method cannot be applied to $y' = t/y$.", False, r"No. The equation is separable; the trouble is only at points where $y = 0$.")]),
]

EXPLORER = {
    "models": [
        {"id": "logistic", "label": "Logistic  a y − b y²", "params": ["a", "b"]},
        {"id": "cubic", "label": "Cubic  y − y³", "params": []},
        {"id": "harvest", "label": "Harvesting  a y − b y² − h", "params": ["a", "b", "h"]},
        {"id": "square", "label": "y² − 1", "params": []}
    ],
    "defaultModel": "logistic",
    "a": {"min": 0.2, "max": 3, "step": 0.1, "default": 1},
    "b": {"min": 0.2, "max": 2, "step": 0.1, "default": 1},
    "h": {"min": 0, "max": 1.5, "step": 0.05, "default": 0.15},
    "y0": {"min": -2, "max": 3, "step": 0.05, "default": 0.25},
    "tMax": 8,
    "yRange": [-2, 3],
    "presets": [
        {"id": "quarter", "label": "Quarter capacity", "model": "logistic", "a": 1, "b": 1, "y0": 0.25,
         "note": "Section 1 example: $y = 1/(1 + 3e^{-t})$ reaches $\\tfrac12$ at $t = \\ln 3$."},
        {"id": "above", "label": "Start above capacity", "model": "logistic", "a": 1, "b": 0.5, "y0": 2.8,
         "note": "Above $a/b = 2$ the slope is negative and $y$ decreases to $2$."},
        {"id": "cubic", "label": "Three steady states", "model": "cubic", "y0": 0.1,
         "note": "Section 2: $0$ unstable, $\\pm1$ stable."},
        {"id": "harvest", "label": "Harvesting", "model": "harvest", "a": 1, "b": 1, "h": 0.15, "y0": 0.6,
         "note": "Book extension: a constant harvest $h$ moves both steady states; for $h > a^2/(4b)$ there are none and the population collapses."},
        {"id": "square", "label": "y² − 1 from 0", "model": "square", "y0": 0,
         "note": "Section 2 example: $-1$ stable, $1$ unstable; from $0$ the solution falls to $-1$."}
    ],
    "tutorContext": "The explorer studies autonomous equations y' = f(y): logistic f = a y - b y^2 (steady states 0 and a/b), cubic f = y - y^3 (0, 1, -1), harvesting f = a y - b y^2 - h (roots (a +- sqrt(a^2 - 4bh))/(2b) when a^2 >= 4bh, none otherwise), and f = y^2 - 1 (+-1). It draws f(y) against y with the stability line (steady states marked stable when f'(Y) < 0, unstable when f'(Y) > 0, undecided at a double root), and the solution y(t) from y0 on 0 <= t <= 8, computed by classical RK4 with step 0.01 (the logistic case is also compared with the exact formula a/(b + d e^(-at))). Solutions that leave the plotted range are clipped with a notice (y' = y^2 - 1 blows up in finite time from y0 > 1)."
}

COURSE = {
    "version": 1,
    "title": "Nonlinear First Order Equations",
    "subtitle": "Unit 2 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 11-13, with Strang's Differential Equations and Linear Algebra, Sections 1.7-1.8",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 11-13", "duration": "47:49", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 1",
             "edition": "Wellesley-Cambridge Press, 2014 (Chapter 1, Sections 1.7-1.8)", "onlineUrl": "",
             "pageNote": "Page references give the printed page and the page of the local PDF (printed page + 12). The book is not freely available online, so only a local copy can be opened."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide; examples marked authored are not from the lectures. They summarize MIT OpenCourseWare's Learn Differential Equations videos (Gilbert Strang, CC BY-NC-SA) and Strang's textbook; for the original wording, watch the videos and read the book. Captions, video and book text are not included in this guide.",
    "explorer": EXPLORER,
    "sections": SECTIONS,
    "quiz": QUIZ,
}

for _i, _q in enumerate(QUIZ):
    _r = [1, 3, 0, 2, 2, 1, 3, 0, 1, 2][_i % 10]
    _q["choices"] = _q["choices"][-_r:] + _q["choices"][:-_r] if _r else _q["choices"]

for _n, _s in enumerate(SECTIONS, 1):
    _s["id"] = f"s{_n}"
    _s["number"] = _n

if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(COURSE, f, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(SECTIONS)} sections, {len(QUIZ)} questions")
