"""Source of courses/controls/linearization/dist/course.json (section notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\controls\\linearization\\course_source.py

Text is original, written for this companion. It paraphrases S. L. Brunton's Control Bootcamp lecture
"Linearizing Around a Fixed Point" and Brunton & Kutz, Section 8.2 (printed pp. 330 and 335), without
quoting. Worked-example numbers are authored for the guide. The lecture has no English captions on
YouTube; timestamps come from a local Whisper transcript in 30-second segments and from video frames
(see SOURCE_REVIEW.md), so they are accurate to about half a minute.
Companion material the lecture does not teach is labelled: the +-x^3 pair, the general damping formula,
the NumPy check, and the book's input/output extension (B, C, D).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "course.json")

B330 = {"printed": 330, "pdf": 350}
B335 = {"printed": 335, "pdf": 355}


def book(ref, label):
    return dict(ref, label=label)


SECTIONS = [
    # ------------------------------------------------------------------ 1
    {
        "nav": "Fixed points",
        "title": r"Fixed points: $f(\bar x) = 0$",
        "time": [0, 180],
        "summary": r"The recipe for a linear model of $\dot x = f(x)$ starts with a fixed point $\bar x$, a state where the velocity vanishes: $f(\bar x) = 0$. The pendulum hanging down and the pendulum balanced upright are both fixed points, though only one is stable. Each fixed point gets its own local model.",
        "goals": [
            r"State the fixed-point condition $f(\bar x) = 0$ and explain why it is not $\bar x = 0$.",
            r"Find the fixed points of a simple system by setting every component of $f$ to zero.",
            r"Distinguish a fixed point from a stable one, and explain why each fixed point needs its own linear model.",
        ],
        "notes": [
            {"heading": "What this lecture covers",
             "paragraphs": [
                 r"Earlier lectures solved linear systems $\dot x = Ax$. Most real systems are nonlinear, $\dot x = f(x)$, and this 30:46 lecture shows how to get a linear model from them: find a fixed point, compute the Jacobian there, and use it as the matrix $A$ of a local linear model. The general recipe (Sections 1 to 4) is then worked out for the pendulum by hand (Sections 5 and 6) and checked in MATLAB (Section 7).",
                 r"The lecture treats autonomous dynamics without an input. The book's version (Section 8.2, Eqs. 8.7 to 8.10) also linearizes an input $u$ and an output $y$; this guide shows that as a labelled extension in Section 3 and in the explorer.",
             ]},
            {"heading": "Where the velocity vanishes",
             "paragraphs": [
                 r"A fixed point (equilibrium) is a state $\bar x$ with $f(\bar x) = 0$. Since $\dot x = f(x)$, a solution that starts exactly at $\bar x$ never moves. The condition is on the value of $f$, not on the position: $\bar x$ can be anywhere in $\mathbb{R}^n$, and the origin is a fixed point only if $f(0) = 0$.",
                 r"To find fixed points, set every component of $f$ to zero and solve the resulting algebraic equations. There may be none, one, several or infinitely many. The pendulum has infinitely many angles $k\pi$, but only two physically different positions.",
             ]},
            {"heading": "Fixed is not the same as stable",
             "paragraphs": [
                 r"A pendulum balanced exactly upright stays put in perfect conditions, but small perturbations can grow. A pendulum hanging down also stays put, and small offsets there do not run away. Fixed describes the point; stable describes what happens to nearby starts.",
                 r"Because the dynamics near different fixed points can be completely different, the linear model is built separately at each one. Section 3 shows that the model at $\bar x$ uses the Jacobian evaluated at $\bar x$.",
             ]},
        ],
        "keyIdeas": [
            r"Fixed point: $f(\bar x) = 0$. Started there, the state does not move.",
            r"Fixed points need not be at the origin; solve every component of $f(x) = 0$.",
            r"Fixed does not mean stable: the upright pendulum is fixed and unstable.",
        ],
        "example": {
            "title": "Three fixed points (authored)",
            "problem": r"Find the fixed points of $\dot x_1 = x_2$, $\dot x_2 = x_1 - x_1^3$.",
            "steps": [
                {"text": r"The first component vanishes only if $x_2 = 0$.",
                 "tex": r"\dot x_1 = x_2 = 0"},
                {"text": r"Then the second component must vanish too; factor it.",
                 "tex": r"x_1 - x_1^3 = x_1(1 - x_1)(1 + x_1) = 0"},
                {"text": r"Each factor gives one fixed point.",
                 "tex": r"\bar x \in \{(0, 0),\ (1, 0),\ (-1, 0)\}"},
            ],
            "answer": r"Three fixed points: $(0, 0)$, $(1, 0)$ and $(-1, 0)$. Two of them are away from the origin. Their stability is decided later, from the Jacobian at each one (Section 4 example).",
        },
        "sources": {
            "video": [{"t": 0, "label": "From x dot = Ax to nonlinear dynamics x dot = f(x)"},
                      {"t": 30, "label": "Plan: work it out on the pendulum; step 1, find fixed points"},
                      {"t": 60, "label": "Fixed point: f(x bar) = 0, the state does not move"},
                      {"t": 90, "label": "Pendulum perfectly vertical; pendulum down"},
                      {"t": 120, "label": "Sun–earth balance point: fixed but unstable"},
                      {"t": 150, "label": "Step 2: linearize about x bar with Df/Dx"}],
            "book": [book(B330, "Linearize near a fixed point (x̄, ū) where f(x̄, ū) = 0 (Eq. 8.7)")],
        },
        "tutorNotes": "Book p.330 (Section 8.2, Eq. 8.7): linear systems are generally obtained by linearizing a nonlinear system about a fixed point; for dx/dt = f(x, u), y = g(x, u), a fixed point (x bar, u bar) satisfies f(x bar, u bar) = 0. Lecture 0:00-3:00: step 1 find fixed points x bar with f(x bar) = 0; examples are the inverted and hanging pendulum and the sun-earth balance point (unstable). Authored examples: x dot = x(1 - x) in the animation (fixed points 0 unstable, 1 stable) and (x2, x1 - x1^3) in the worked example (fixed points (0,0), (+-1,0)).",
    },
    # ------------------------------------------------------------------ 2
    {
        "nav": "The Jacobian",
        "title": r"The Jacobian $Df/Dx$: rows $f_i$, columns $x_j$",
        "time": [180, 405],
        "summary": r"The Jacobian collects every first partial derivative: entry $(i, j)$ is $\partial f_i/\partial x_j$. For the lecture's example $f = (x_1x_2,\ x_1^2 + x_2^2)$ it is $\begin{bmatrix}x_2 & x_1\\ 2x_1 & 2x_2\end{bmatrix}$. Evaluated at a fixed point it becomes a matrix of numbers, the $A$ of the local model.",
        "goals": [
            r"Place each partial derivative in its cell: row $i$ for $f_i$, column $j$ for $x_j$.",
            r"Compute a Jacobian symbolically, then evaluate it at a point.",
            r"Recognize that a zero Jacobian at a fixed point (as in the lecture's example) leaves stability undecided.",
        ],
        "notes": [
            {"heading": "A matrix of partial derivatives",
             "paragraphs": [
                 r"For $f: \mathbb{R}^n \to \mathbb{R}^n$ the Jacobian $\frac{Df}{Dx}$ is the $n \times n$ matrix with entries $\partial f_i/\partial x_j$. Row $i$ lists how the $i$-th component of $f$ changes with each state variable; column $j$ lists how every component changes with $x_j$. The lecture writes $Df/Dx$; other texts use $\partial f/\partial x$, $J$ or $\nabla f$.",
                 r"The lecturer's memory aid: the Jacobian will multiply a small step $\Delta x = (\Delta x_1, \Delta x_2)$. In a matrix-vector product, column $j$ meets $\Delta x_j$, so column $j$ must hold derivatives with respect to $x_j$. Then $\frac{Df}{Dx}\Delta x$ is the first-order change of $f$.",
             ]},
            {"heading": "The lecture's example",
             "paragraphs": [
                 r"With $f_1 = x_1x_2$ and $f_2 = x_1^2 + x_2^2$: $\partial f_1/\partial x_1 = x_2$ (treat $x_2$ as a constant), $\partial f_1/\partial x_2 = x_1$, $\partial f_2/\partial x_1 = 2x_1$ and $\partial f_2/\partial x_2 = 2x_2$. The Jacobian is $\begin{bmatrix}x_2 & x_1\\ 2x_1 & 2x_2\end{bmatrix}$, which still depends on $x$.",
                 r"Plugging in the coordinates of a point turns it into an ordinary matrix of numbers. To build a linear model, the point must be a fixed point. Here $x_1^2 + x_2^2 = 0$ forces $\bar x = (0, 0)$, the only real fixed point, and every entry of the Jacobian vanishes there.",
             ]},
            {"heading": "When A is zero",
             "paragraphs": [
                 r"A zero matrix predicts that offsets do not move at all; that only says the first-order terms vanish, so the quadratic terms take over. In this example they make the origin unstable: on the $x_2$ axis $\dot x_2 = x_2^2$, so a positive offset grows (an authored check; the lecture only computes the Jacobian). Section 4 explains exactly when $A$ decides stability.",
             ]},
        ],
        "keyIdeas": [
            r"$\left(\frac{Df}{Dx}\right)_{ij} = \partial f_i/\partial x_j$: rows are components of $f$, columns are state variables.",
            r"Memory aid: $\frac{Df}{Dx}\Delta x$ must pair column $j$ with $\Delta x_j$.",
            r"Evaluated at a fixed point, the Jacobian is a constant matrix $A$.",
        ],
        "example": {
            "title": "Jacobian at two fixed points (authored)",
            "problem": r"$f(x) = \begin{bmatrix}x_1 - x_1x_2\\ -x_2 + x_1^2\end{bmatrix}$. Find the fixed points, the Jacobian, and $A$ at each fixed point.",
            "steps": [
                {"text": r"Fixed points: $x_1(1 - x_2) = 0$ and $x_2 = x_1^2$. Either $x_1 = 0$ (then $x_2 = 0$) or $x_2 = 1$ (then $x_1 = \pm 1$).",
                 "tex": r"\bar x \in \{(0, 0),\ (1, 1),\ (-1, 1)\}"},
                {"text": r"Differentiate each component with respect to each variable.",
                 "tex": r"\frac{Df}{Dx} = \begin{bmatrix}1 - x_2 & -x_1\\ 2x_1 & -1\end{bmatrix}"},
                {"text": r"Evaluate at the origin.",
                 "tex": r"A_{(0,0)} = \begin{bmatrix}1 & 0\\ 0 & -1\end{bmatrix}"},
                {"text": r"Evaluate at $(\pm 1, 1)$.",
                 "tex": r"A_{(1,1)} = \begin{bmatrix}0 & -1\\ 2 & -1\end{bmatrix},\qquad A_{(-1,1)} = \begin{bmatrix}0 & 1\\ -2 & -1\end{bmatrix}"},
            ],
            "answer": r"Three fixed points with three different matrices $A$. Section 4's example classifies them.",
        },
        "sources": {
            "video": [{"t": 180, "label": "Example: f1 = x1 x2, f2 = x1² + x2²"},
                      {"t": 210, "label": "Df/Dx: a matrix of partial derivatives"},
                      {"t": 240, "label": "Memory aid: Df/Dx multiplies Δx"},
                      {"t": 270, "label": "Rows share f_i, columns share x_j"},
                      {"t": 300, "label": "Entries x2, x1, 2x1, 2x2"},
                      {"t": 330, "label": "The Jacobian; plug in x bar for a matrix of numbers"},
                      {"t": 360, "label": "Shorthand: [∂f_i/∂x_j] evaluated at x bar (frame 6:00)"},
                      {"t": 390, "label": "Recap: fixed points, Jacobian, plug in"}],
            "book": [book(B330, "A = df/dx evaluated at (x̄, ū) in the Taylor expansion (Eq. 8.8)")],
        },
        "tutorNotes": "Book p.330 Eq. 8.8: the Taylor expansion of f about (x bar, u bar) has A = df/dx and B = df/du evaluated there. Lecture 3:00-6:45 (frame at 6:00 shows the board): Jacobian Df/Dx = [partial f_i / partial x_j]; example f1 = x1 x2, f2 = x1^2 + x2^2 gives [[x2, x1], [2 x1, 2 x2]]; memory aid via multiplying by delta x; evaluating at x bar gives a matrix of numbers. The only real fixed point of that example is (0, 0), where the Jacobian is zero (nonhyperbolic; the guide adds that the origin is unstable because x2 dot = x2^2 on the x2 axis). Worked example f = (x1 - x1 x2, -x2 + x1^2) is authored.",
    },
    # ------------------------------------------------------------------ 3
    {
        "nav": "Shift, expand, truncate",
        "title": r"Shift, expand, truncate: $\dot\eta \approx A\eta$",
        "time": [405, 780],
        "summary": r"Measure the state from the fixed point, $\eta = x - \bar x$. Then $\dot\eta = f(\bar x + \eta) = f(\bar x) + A\eta + \mathcal{O}(\|\eta\|^2)$ with $A$ the Jacobian at $\bar x$. The constant vanishes because $f(\bar x) = 0$, and close to $\bar x$ the remainder is small: $\dot\eta \approx A\eta$. The book adds inputs and outputs the same way.",
        "goals": [
            r"Explain why $\dot\eta = \dot x$ after shifting the origin to a fixed point.",
            r"Identify the constant, linear and remainder terms of the Taylor expansion and say why each one is kept or dropped.",
            r"Explain why expanding about a point that is not fixed leaves an affine model, and how $B$, $C$, $D$ extend the recipe.",
        ],
        "notes": [
            {"heading": "Zoom in and shift the origin",
             "paragraphs": [
                 r"The lecturer's picture: zoom into a small window around $\bar x$ and the curved flow looks like a linear one (he sketches a saddle). To write this down, measure the state from the fixed point, $\eta = x - \bar x$. The lecture calls the offset $\Delta x$ and then, to save writing, just $x$ again; this guide keeps the name $\eta$ so the shifted and original states are never confused.",
                 r"Because $\bar x$ is a constant, $\dot{\bar x} = 0$ and $\dot\eta = \dot x = f(\bar x + \eta)$: the shifted state obeys the same vector field, read off at $\bar x + \eta$. The lecture skips this detail.",
             ]},
            {"heading": "Taylor expansion and truncation",
             "paragraphs": [
                 r"For a smooth $f$ (twice continuously differentiable is enough), $f(\bar x + \eta) = f(\bar x) + \frac{Df}{Dx}\big|_{\bar x}\eta + \mathcal{O}(\|\eta\|^2)$: a constant, a linear term and a remainder bounded by a constant times $\|\eta\|^2$ near $\bar x$.",
                 r"At a fixed point the constant is $f(\bar x) = 0$. Writing $A = \frac{Df}{Dx}\big|_{\bar x}$ gives $\dot\eta = A\eta + r(\eta)$, with $\|r(\eta)\| \leq C\|\eta\|^2$ locally for a twice continuously differentiable $f$. Thus the error is small relative to $\|\eta\|$ as $\eta \to 0$. It need not be small relative to $A\eta$ when that term vanishes, as the zero-Jacobian examples show. Dropping the remainder defines the local linear model, written $\dot\eta \approx A\eta$ here; this is generally an approximation, not an identity.",
                 r"The lecture adds a control motivation (12:30 to 13:00): the upright pendulum's linear model is only valid near the top, but good feedback keeps the state near the top, where the model stays useful. Feedback design itself comes in later lectures.",
             ]},
            {"heading": "Not at a fixed point; inputs and outputs (book extension)",
             "paragraphs": [
                 r"The same expansion works about any point $x_0$, but if $f(x_0) \neq 0$ the constant survives: $\dot\eta \approx f(x_0) + A\eta$ is affine, and the state drifts away immediately. That is why the recipe starts with fixed points.",
                 r"With an input, $\dot x = f(x, u)$, expand about an equilibrium pair with $f(\bar x, \bar u) = 0$: $\dot\eta \approx A\eta + B\,\delta u$ with $B = \partial f/\partial u$ at $(\bar x, \bar u)$ and $\delta u = u - \bar u$ (book Eq. 8.8). An output $y = g(x, u)$ gives $\delta y \approx C\eta + D\,\delta u$ (Eq. 8.9). The book then drops the offset labels and writes $\dot x = Ax + Bu$, $y = Cx + Du$ in shifted coordinates (Eq. 8.10). For the pendulum with the angle as output, $C = [1\ \ 0]$ and $D = 0$.",
             ]},
        ],
        "keyIdeas": [
            r"$\eta = x - \bar x$ and $\dot\eta = \dot x$ because $\dot{\bar x} = 0$.",
            r"$\dot\eta = f(\bar x) + A\eta + \mathcal{O}(\|\eta\|^2)$; at a fixed point $f(\bar x) = 0$.",
            r"$\dot\eta \approx A\eta$ is a local approximation. Book extension: $\dot\eta \approx A\eta + B\,\delta u$, $\delta y \approx C\eta + D\,\delta u$.",
        ],
        "example": {
            "title": "An exact expansion (authored)",
            "problem": r"$\dot x = x^2 - 1$. Linearize at $\bar x = 1$ and compare the linear term with the remainder at $\eta = 0.1$ and $\eta = 0.5$.",
            "steps": [
                {"text": r"$f(1) = 0$, so $\bar x = 1$ is a fixed point. Substitute $x = 1 + \eta$ and expand.",
                 "tex": r"\dot\eta = f(1 + \eta) = (1 + \eta)^2 - 1 = 2\eta + \eta^2"},
                {"text": r"The Jacobian (here a derivative) at $\bar x = 1$ is $A = f'(1) = 2$; the remainder is exactly $\eta^2$.",
                 "tex": r"\dot\eta = \underbrace{2\eta}_{A\eta} + \underbrace{\eta^2}_{\text{remainder}} \approx 2\eta"},
                {"text": r"Compare the sizes.",
                 "tex": r"\eta = 0.1:\ 0.2\ \text{vs}\ 0.01\ (5\%);\qquad \eta = 0.5:\ 1\ \text{vs}\ 0.25\ (25\%)"},
            ],
            "answer": r"$\dot\eta \approx 2\eta$: offsets grow, so $\bar x = 1$ is unstable. The remainder's share falls in proportion to $\eta$ as $\eta$ shrinks. (At the other fixed point $\bar x = -1$, $\dot\eta = -2\eta + \eta^2$.)",
        },
        "sources": {
            "video": [{"t": 420, "label": "Zoom in near a fixed point: the flow looks linear (saddle sketch)"},
                      {"t": 480, "label": "Shift coordinates so that x bar is at the origin"},
                      {"t": 510, "label": "Expand f in powers of the offset"},
                      {"t": 540, "label": "Taylor series: f(x bar) + Df/Dx (x - x bar) + higher order"},
                      {"t": 570, "label": "x bar dot glossed over; f(x bar) = 0 by definition"},
                      {"t": 600, "label": "Higher-order terms are small close to x bar"},
                      {"t": 630, "label": "Δx dot = Df/Dx|x bar · Δx"},
                      {"t": 660, "label": "A matrix of numbers; written x dot = Ax"},
                      {"t": 750, "label": "Pendulum up: control keeps the state where the model is valid"}],
            "book": [book(B330, "Taylor expansion (Eqs. 8.8–8.9), dropping higher-order terms and shifting coordinates (Eq. 8.10)")],
        },
        "tutorNotes": "Book p.330 Eqs. 8.8-8.10: f(x bar + dx, u bar + du) = f(x bar, u bar) + (df/dx) dx + (df/du) du + ...; similarly g with C = dg/dx and D = dg/du; for small displacements the higher-order terms are negligible; dropping the deltas and shifting coordinates gives dx/dt = Ax + Bu, y = Cx + Du. The book also says an effective stabilizing controller keeps the state in a small neighbourhood where the linear approximation is valid. Lecture 6:45-13:00: zoom in, shift x bar to the origin, Taylor series, f(x bar) = 0, higher-order terms small, delta x dot = A delta x. This guide uses eta = x - x bar. Authored: the sin remainder illustration, the non-fixed expansion point x0 = 0.5 of x(1 - x), and the example x dot = x^2 - 1.",
    },
    # ------------------------------------------------------------------ 4
    {
        "nav": "Validity: hyperbolic points",
        "title": r"When the linear model can be trusted: hyperbolic fixed points",
        "time": [780, 960],
        "summary": r"For a continuously differentiable system, a hyperbolic fixed point has every eigenvalue of $A$ off the imaginary axis, and the linear model captures its local qualitative behaviour. All real parts negative means locally asymptotically stable; any positive real part means unstable, even if other eigenvalues are on the axis. Zero real parts with none positive leave stability undecided.",
        "goals": [
            r"Define a hyperbolic fixed point correctly (nonzero real parts, any signs).",
            r"Use the eigenvalues of $A$ to conclude local asymptotic stability or instability when they are off the imaginary axis.",
            r"Explain, with $\dot x = \mp x^3$, why imaginary or zero eigenvalues leave stability undecided.",
        ],
        "notes": [
            {"heading": "Hyperbolic means off the imaginary axis",
             "paragraphs": [
                 r"The lecturer calls this section a catch: the linearization does not always describe the nonlinear system. A fixed point is hyperbolic when every eigenvalue of $A$ has a nonzero real part. The signs do not matter: all negative, all positive, or a mixture as in a saddle all count.",
                 r"For hyperbolic points two statements follow for a continuously differentiable $f$. If every real part is negative, the nonlinear fixed point is locally asymptotically stable. If some real part is positive, it is unstable. The Hartman–Grobman theorem says more: near a hyperbolic fixed point, the nonlinear flow is a continuous deformation of the linear flow (they are topologically equivalent).",
             ]},
            {"heading": "What it does not promise",
             "paragraphs": [
                 r"The statements are local and qualitative. They hold in some neighbourhood of $\bar x$ whose size the theorem does not give; they do not say trajectories, periods or decay rates match exactly, and they say nothing about large offsets. The explorer shows how quickly the pendulum's linear model loses accuracy as the offset grows.",
             ]},
            {"heading": "On the imaginary axis, all bets are off",
             "paragraphs": [
                 r"If some eigenvalue has zero real part (purely imaginary like $\pm i$, or zero) and none has a positive real part, the linearization is inconclusive. The neglected terms may yield asymptotic stability, stability without attraction, or instability. The lecturer's example is the undamped pendulum, whose linearization at the bottom is a center with eigenvalues $\pm i$.",
                 r"Authored illustration: $\dot x = -x^3$ and $\dot x = +x^3$ both have the fixed point $0$ and the same Jacobian $A = 0$. Yet offsets return to $0$ in the first and run away in the second. Same linear model, opposite behaviour, so the eigenvalues alone cannot decide.",
                 r"For the undamped pendulum, a separate argument settles it: its energy $\tfrac12\dot\theta^2 + q(1 - \cos\theta)$ is conserved and has a strict minimum at the bottom, so the hanging position is stable but not asymptotically stable. That conclusion comes from the energy, not from the eigenvalues.",
             ]},
        ],
        "keyIdeas": [
            r"Hyperbolic: $\mathrm{Re}\,\lambda_i \neq 0$ for every eigenvalue (signs may differ).",
            r"Hyperbolic and all $\mathrm{Re}\,\lambda < 0$: locally asymptotically stable. Any $\mathrm{Re}\,\lambda > 0$: unstable.",
            r"Imaginary or zero eigenvalues (none positive): not decided by $A$, as $\dot x = \mp x^3$ shows.",
        ],
        "example": {
            "title": "Classifying the Section 2 example (authored)",
            "problem": r"Classify the fixed points $(0, 0)$ and $(\pm 1, 1)$ of $\dot x_1 = x_1 - x_1x_2$, $\dot x_2 = -x_2 + x_1^2$ from their matrices $A$.",
            "steps": [
                {"text": r"At the origin $A$ is diagonal.",
                 "tex": r"A_{(0,0)} = \begin{bmatrix}1&0\\0&-1\end{bmatrix}:\ \lambda = 1,\ -1\ \Rightarrow\ \text{hyperbolic saddle, unstable}"},
                {"text": r"At $(\pm 1, 1)$ both matrices have trace $-1$ and determinant $2$.",
                 "tex": r"\lambda^2 + \lambda + 2 = 0\ \Rightarrow\ \lambda = \frac{-1 \pm i\sqrt 7}{2}"},
                {"text": r"Both real parts are $-\tfrac12 \neq 0$: hyperbolic, and negative.",
                 "tex": r"(\pm 1, 1):\ \text{locally asymptotically stable (spiralling in)}"},
            ],
            "answer": r"The origin is an unstable saddle; $(1, 1)$ and $(-1, 1)$ are locally asymptotically stable. All three points are hyperbolic, so these conclusions hold for the nonlinear system near each point.",
        },
        "sources": {
            "video": [{"t": 780, "label": "Good control keeps the state near x bar; the catches"},
                      {"t": 810, "label": "Hartman–Grobman: hyperbolic (nonzero real parts) means the linearization works close enough"},
                      {"t": 840, "label": "Purely imaginary eigenvalues: all bets are off"},
                      {"t": 870, "label": "Neutral stability, e.g. the undamped pendulum"},
                      {"t": 900, "label": "Next: work it out for the pendulum; controllability later"},
                      {"t": 930, "label": "Inverted-pendulum hardware and landing rockets"}],
            "book": [book(B330, "The linear approximation is valid in a small neighbourhood of the fixed point; instability can carry the state away")],
        },
        "tutorNotes": "Book p.330: linear systems come from linearizing about a fixed point, but instability may quickly take a trajectory far away; an effective stabilizing controller keeps the state in a small neighbourhood where the linear approximation is valid. Lecture 13:00-16:00 (the ASR writes 'Hartman-Growman'): if the linearization is hyperbolic (all eigenvalues have nonzero real part, any mix of signs) it describes the neighbourhood if we zoom in close enough; purely imaginary eigenvalues such as +-i: all bets are off; example of neutral stability: undamped pendulum. The guide adds: C^1 smoothness, the theorem is local and qualitative, the authored x dot = -x^3 / +x^3 pair with identical A = 0, and the energy argument for the undamped pendulum. Worked example is authored.",
    },
    # ------------------------------------------------------------------ 5
    {
        "nav": "Pendulum: state and equilibria",
        "title": r"The pendulum in state-space form and its equilibria",
        "time": [960, 1350],
        "summary": r"With $\theta$ measured from the downward vertical, the damped pendulum is $\ddot\theta = -\frac{g}{L}\sin\theta - d\,\dot\theta$. The lecture sets $g/L = 1$, writes $x = (\theta, \dot\theta)$ so $\dot x = (x_2,\ -\sin x_1 - d\,x_2)$, and solves $f(\bar x) = 0$: $x_2 = 0$ and $\sin x_1 = 0$, giving down $(0, 0)$ and up $(\pi, 0)$.",
        "goals": [
            r"Rewrite a second-order equation as a first-order state-space system.",
            r"Solve $f(\bar x) = 0$ for the pendulum and identify the physical equilibria modulo $2\pi$.",
            r"Measure a state near the top as an offset from $\pi$, not as a small absolute angle.",
        ],
        "notes": [
            {"heading": "The model, with friction",
             "paragraphs": [
                 r"The lecture draws a pendulum of length $L$ with angle $\theta$ (radians) from the downward vertical and states $\ddot\theta = -\frac{g}{L}\sin\theta$, a nonlinear equation because of $\sin\theta$. He then adds viscous friction, $-d\,\dot\theta$ with a small $d > 0$ (written $\delta$ on the board, $d$ in MATLAB), so a real pendulum eventually stops. The book's example (Eq. 8.23) has no friction and an input $u$: $\ddot\theta = -\frac{g}{L}\sin\theta + u$.",
                 r"To keep the algebra short the lecture sets $q = g/L = 1$. The explorer keeps $q$ as a slider; everything below holds with $q$ in place of $1$.",
             ]},
            {"heading": "Physical intuition first",
             "paragraphs": [
                 r"The lecturer predicts the answer before computing: kicked slightly from the bottom, the pendulum oscillates and slowly comes to rest, so the down eigenvalues should have negative real parts and imaginary parts. Kicked from the top, it falls away exponentially (at least for small angles and short times), so the up linearization should have a positive eigenvalue. The math in Sections 6 and 7 confirms both.",
             ]},
            {"heading": "State-space form and fixed points",
             "paragraphs": [
                 r"With $x_1 = \theta$ and $x_2 = \dot\theta$: $\dot x_1 = x_2$ restates the definition, and $\dot x_2 = \ddot\theta = -\sin x_1 - d\,x_2$. So $f(x) = (x_2,\ -\sin x_1 - d\,x_2)$.",
                 r"Fixed points: the first row forces $x_2 = 0$, which also removes the friction term; the second then needs $\sin x_1 = 0$, so $x_1 = k\pi$. Angles that differ by $2\pi$ describe the same physical position, leaving two physical equilibria: down $(0, 0)$ and up $(\pi, 0)$.",
                 r"Near the top, the state is $\theta = \pi + \eta$ with a small offset $\eta$. A pendulum tilted $0.15$ rad past upright has $\theta \approx 3.29$ rad. The local model at the top is written in $\eta$; treating $\theta$ itself as small there would be wrong.",
             ]},
        ],
        "keyIdeas": [
            r"$\theta$ from the downward vertical, in radians; friction $-d\,\dot\theta$; lecture uses $q = g/L = 1$.",
            r"$x = (\theta, \dot\theta)$: $\dot x = (x_2,\ -\sin x_1 - d\,x_2)$.",
            r"Equilibria $(k\pi, 0)$: down $(0, 0)$ and up $(\pi, 0)$ modulo $2\pi$. Near up, use $\eta = \theta - \pi$.",
        ],
        "example": {
            "title": "Which equilibrium, and how far? (authored)",
            "problem": r"A pendulum with $q = 4$ and $d = 0.5$ is at $\theta = 6.2$ rad. Write its state equations, list its equilibria, and find the nearest one and the offset.",
            "steps": [
                {"text": r"State equations with $q = 4$, $d = 0.5$.",
                 "tex": r"\dot x_1 = x_2,\qquad \dot x_2 = -4\sin x_1 - 0.5\,x_2"},
                {"text": r"Equilibria do not depend on $q$ or $d$: $x_2 = 0$, $\sin x_1 = 0$.",
                 "tex": r"\bar x = (k\pi, 0)"},
                {"text": r"$6.2$ is close to $2\pi \approx 6.2832$, which is the down position again.",
                 "tex": r"\eta = 6.2 - 2\pi \approx -0.083\ \text{rad}"},
            ],
            "answer": r"It is $0.083$ rad short of hanging straight down (one full turn later). Equivalently $\theta \equiv -0.083$ rad modulo $2\pi$, a small offset from the down equilibrium.",
        },
        "sources": {
            "video": [{"t": 960, "label": "Drawing the pendulum: angle θ, gravity, length L"},
                      {"t": 990, "label": "θ double dot = −(g/L) sin θ"},
                      {"t": 1020, "label": "Nonlinear; fixed points at 0, π, 2π, ..."},
                      {"t": 1050, "label": "Add friction −δ θ dot"},
                      {"t": 1110, "label": "Intuition: down oscillates and decays, up falls away"},
                      {"t": 1140, "label": "State x1 = θ, x2 = θ dot"},
                      {"t": 1170, "label": "x1 dot = x2; set g/L = 1"},
                      {"t": 1230, "label": "x2 dot = −sin x1 − δ x2"},
                      {"t": 1290, "label": "Fixed points: x2 = 0 and sin x1 = 0, so x1 = 0 or π"},
                      {"t": 1320, "label": "All the multiples of π; physically down and up (frame 22:00)"}],
            "book": [book(B335, "Pendulum θ̈ = −(g/L) sin θ + u and its state-space form (Eqs. 8.23–8.24), undamped")],
        },
        "tutorNotes": "Book p.335 Eqs. 8.23-8.24: theta double dot = -(g/L) sin(theta) + u (no friction; the figure labels u as a torque at the base, in the normalized equation it acts as an angular acceleration), state x = (theta, theta dot), dx/dt = (x2, -(g/L) sin x1 + u). Lecture 16:00-22:30 (frames 18:00, 22:00): theta double dot = -(g/L) sin theta, friction -delta theta dot added at about 17:30, g/L = 1 at about 19:30-20:00, f = (x2, -sin x1 - delta x2); fixed points x2 = 0, sin x1 = 0: (0, 0) down and (pi, 0) up, modulo 2 pi. The guide writes d for delta. Worked example (q = 4, d = 0.5, theta = 6.2) is authored.",
    },
    # ------------------------------------------------------------------ 6
    {
        "nav": "Two Jacobians, two behaviours",
        "title": r"Down and up: $A_d$, $A_u$ and their eigenvalues",
        "time": [1350, 1650],
        "summary": r"$\frac{Df}{Dx} = \begin{bmatrix}0 & 1\\ -q\cos x_1 & -d\end{bmatrix}$. At the bottom $\cos 0 = 1$, at the top $\cos\pi = -1$: one sign flips. Without friction the bottom is a linear center ($\pm i\sqrt q$) and the top a saddle ($\pm\sqrt q$). With friction the bottom becomes asymptotically stable while the top stays a saddle.",
        "goals": [
            r"Compute the pendulum Jacobian and evaluate it at $0$ and $\pi$.",
            r"Write the local models in offset coordinates $\eta = \theta - \bar\theta$, $\nu = \omega$.",
            r"Find and interpret the eigenvalues for $d = 0$ and $d > 0$, including the overdamped case.",
        ],
        "notes": [
            {"heading": "One Jacobian, two evaluations",
             "paragraphs": [
                 r"Differentiate $f = (x_2,\ -q\sin x_1 - d\,x_2)$: row 1 gives $0$ and $1$; row 2 gives $-q\cos x_1$ and $-d$. The lecturer admits he is never sure about the sign until the eigenvalues confirm the physics.",
                 r"At the bottom $\cos 0 = 1$: $A_d = \begin{bmatrix}0&1\\-q&-d\end{bmatrix}$. At the top $\cos\pi = -1$: $A_u = \begin{bmatrix}0&1\\q&-d\end{bmatrix}$. Only the gravity term changes sign: at the bottom it pulls an offset back, at the top it pushes it further. These are the book's matrices (Eq. 8.25) with friction added.",
                 r"Each matrix acts on the offset from its own equilibrium: $\eta = \theta - \bar\theta$ and $\nu = \omega = \dot\theta$. So $\dot\eta = \nu$, $\dot\nu \approx -q\eta - d\nu$ at the bottom and $\dot\nu \approx +q\eta - d\nu$ at the top, where $\eta = \theta - \pi$.",
             ]},
            {"heading": "Eigenvalues",
             "paragraphs": [
                 r"$\det(\lambda I - A) = \lambda^2 + d\lambda + q$ at the bottom and $\lambda^2 + d\lambda - q$ at the top. The quadratic formula gives the companion formulas $\lambda = \frac{-d \pm \sqrt{d^2 - 4q}}{2}$ (down) and $\lambda = \frac{-d \pm \sqrt{d^2 + 4q}}{2}$ (up). The lecture does the $d = 0$ case in his head: $\lambda^2 + 1 = 0$ gives $\pm i$ down, and $\lambda^2 - 1 = 0$ gives $\pm 1$ up.",
                 r"No friction ($d = 0$): down, $\pm i\sqrt q$ is a linear center, the frictionless oscillation at frequency $\sqrt q$. It is not hyperbolic, so the Jacobian alone does not decide (Section 4); conservation of energy shows the hanging pendulum is stable but not asymptotically stable. The book calls it a stable center. Up, $\pm\sqrt q$ is a saddle; the eigenvalue $+\sqrt q$ grows like $e^{\sqrt q\,t}$, so the top is unstable.",
                 r"With friction ($d > 0$): down, both real parts are negative, so the point is hyperbolic and locally asymptotically stable. For $0 < d < 2\sqrt q$ the eigenvalues are $-d/2 \pm i\sqrt{q - d^2/4}$ (decaying oscillation); at $d = 2\sqrt q$ they meet (critical damping); for $d > 2\sqrt q$ both are real and negative (overdamped, no oscillation). Friction does not always give complex eigenvalues. Up, $\sqrt{d^2 + 4q} > d$, so one eigenvalue stays positive for every $d \ge 0$: the top is always a saddle.",
                 r"All of this is local. The linear models describe small offsets near each equilibrium; they say nothing about a pendulum swinging over the top.",
             ]},
        ],
        "keyIdeas": [
            r"$\frac{Df}{Dx} = \begin{bmatrix}0&1\\-q\cos x_1&-d\end{bmatrix}$; $\cos\pi = -1$ flips the gravity term at the top.",
            r"$d = 0$: down $\pm i\sqrt q$ (linear center, decided by energy), up $\pm\sqrt q$ (saddle, unstable).",
            r"$d > 0$: down locally asymptotically stable (focus if $d < 2\sqrt q$, node if $d > 2\sqrt q$); up always a saddle.",
        ],
        "example": {
            "title": "A shorter, stiffer pendulum (authored)",
            "problem": r"$q = 4$, $d = 1$. Find $A_d$, $A_u$ and their eigenvalues, and the friction at which the down oscillation disappears.",
            "steps": [
                {"text": r"Substitute into the two matrices.",
                 "tex": r"A_d = \begin{bmatrix}0&1\\-4&-1\end{bmatrix},\qquad A_u = \begin{bmatrix}0&1\\4&-1\end{bmatrix}"},
                {"text": r"Down: $\lambda^2 + \lambda + 4 = 0$.",
                 "tex": r"\lambda = \frac{-1 \pm i\sqrt{15}}{2} \approx -0.5 \pm 1.936\,i"},
                {"text": r"Up: $\lambda^2 + \lambda - 4 = 0$.",
                 "tex": r"\lambda = \frac{-1 \pm \sqrt{17}}{2} \approx 1.562,\ -2.562"},
                {"text": r"The down eigenvalues become real when $d^2 \ge 4q$.",
                 "tex": r"d \ge 2\sqrt q = 4"},
            ],
            "answer": r"Down: a decaying oscillation (stable focus). Up: a saddle, unstable. With $d \ge 4$ the down response no longer oscillates; the up position stays unstable for any friction.",
        },
        "sources": {
            "video": [{"t": 1350, "label": "Step 2: linearize about each fixed point"},
                      {"t": 1380, "label": "Partial derivatives: 0 and 1 in the first row"},
                      {"t": 1410, "label": "−cos x1 and −δ in the second row"},
                      {"t": 1440, "label": "Plug each fixed point into the symbolic Jacobian"},
                      {"t": 1470, "label": "A_down = [0 1; −1 −δ]"},
                      {"t": 1500, "label": "A_up = [0 1; 1 −δ] since cos π = −1"},
                      {"t": 1530, "label": "δ = 0: λ² + 1 = 0"},
                      {"t": 1560, "label": "±i down (damping adds a negative real part); ±1 up (frame 26:00)"},
                      {"t": 1590, "label": "The +1 eigenvalue grows like e^t: unstable"},
                      {"t": 1620, "label": "Recap of the procedure"}],
            "book": [book(B335, "Jacobian (Eq. 8.25); up λ = ±√(g/L) saddle, down λ = ±i√(g/L) center")],
        },
        "tutorNotes": "Book p.335 Eq. 8.25: df/dx = [[0, 1], [-(g/L) cos x1, 0]], df/du = [0; 1]; pendulum up (x1 = pi): [[0, 1], [g/L, 0]] with lambda = +-sqrt(g/L), an unstable saddle; down (x1 = 0): [[0, 1], [-g/L, 0]] with lambda = +-i sqrt(g/L), which the book calls a stable center oscillating at sqrt(g/L) (undamped). Lecture 22:30-27:30 (frame 26:00): J = [[0, 1], [-cos x1, -delta]], A_d = [[0, 1], [-1, -delta]], A_u = [[0, 1], [1, -delta]]; delta = 0 gives +-i and +-1; damping adds a negative real part down; positive eigenvalue up means unstable. Companion: general formulas lambda = (-d +- sqrt(d^2 - 4q))/2 down and (-d +- sqrt(d^2 + 4q))/2 up, overdamped for d > 2 sqrt(q), and the energy argument for the undamped center. Worked example q = 4, d = 1 is authored.",
    },
    # ------------------------------------------------------------------ 7
    {
        "nav": "MATLAB check, d = 0.1",
        "title": r"The MATLAB check with $d = 0.1$",
        "time": [1650, 1846],
        "summary": r"With $q = 1$ and $d = 0.1$, MATLAB gives eig($A_d$) $= -0.0500 \pm 0.9987i$ (a lightly damped, stable oscillation) and eig($A_u$) $= -1.0512,\ 0.9512$ (a saddle). The signs confirm the intuition and the Jacobian. Next lectures add an input $Bu$ and feedback.",
        "goals": [
            r"Reproduce the lecture's eigenvalues by hand and with any numerical tool.",
            r"Read stability from the computed eigenvalues of $A_d$ and $A_u$.",
            r"Place this lecture in the course: linear models now, control with $Bu$ next.",
        ],
        "notes": [
            {"heading": "The numbers",
             "paragraphs": [
                 r"The lecture types d = 0.1, Ad = [0 1; -1 -d] and Au = [0 1; 1 -d] and calls eig. By hand: $\lambda^2 + 0.1\lambda + 1 = 0$ gives $\lambda = -0.05 \pm i\sqrt{1 - 0.0025} = -0.05 \pm 0.998749i$, and $\lambda^2 + 0.1\lambda - 1 = 0$ gives $\lambda = -0.05 \pm \sqrt{1.0025} = -1.051249,\ 0.951249$. MATLAB prints these to four decimals.",
                 r"Down: the eigenvalues moved from $\pm i$ just into the left half-plane, an oscillation at angular frequency about $0.9987$ inside the envelope $e^{-0.05t}$: stable, decaying slowly. Up: one stable eigenvalue $-1.0512$ and one unstable $0.9512$, a saddle. In continuous time any positive real part is unstable, so a small kick near the top grows, until the nonlinear terms take over.",
             ]},
            {"heading": "Without MATLAB (companion)",
             "paragraphs": [
                 r"Any linear-algebra library gives the same numbers. A NumPy equivalent (not shown in the video): import numpy as np; d = 0.1; np.linalg.eigvals([[0, 1], [-1, -d]]) returns −0.05 ± 0.99875i, and np.linalg.eigvals([[0, 1], [1, -d]]) returns 0.95125 and −1.05125 (the order may differ). The explorer reproduces both with its defaults $q = 1$, $d = 0.1$ and lets you compare the nonlinear pendulum with each linear model.",
             ]},
            {"heading": "What comes next",
             "paragraphs": [
                 r"The lecture closes by adding $+Bu$: with an input, feedback can move the unstable eigenvalue of the upright pendulum and keep it near the top, where the linear model is valid. Controllability and controller design are the topics of the following lectures; nothing is designed here.",
             ]},
        ],
        "keyIdeas": [
            r"$d = 0.1$, $q = 1$: eig$(A_d) = -0.05 \pm 0.9987i$, stable, lightly damped.",
            r"eig$(A_u) = -1.0512,\ 0.9512$: a saddle, unstable.",
            r"Next: $\dot x = Ax + Bu$ and feedback to stabilize the top (later lectures).",
        ],
        "example": {
            "title": "Predict before you compute (authored)",
            "problem": r"Predict eig$(A_d)$ and eig$(A_u)$ for $q = 1$ and $d = 0.4$, then check them.",
            "steps": [
                {"text": r"Down: real part $-d/2$, imaginary part $\sqrt{q - d^2/4}$.",
                 "tex": r"\lambda = -0.2 \pm i\sqrt{1 - 0.04} \approx -0.2 \pm 0.9798\,i"},
                {"text": r"Up: $-d/2 \pm \sqrt{d^2/4 + q}$.",
                 "tex": r"\lambda = -0.2 \pm \sqrt{1.04} \approx 0.8198,\ -1.2198"},
                {"text": r"Check: the sum of the eigenvalues is the trace, $-d$; the product is the determinant, $\pm q$.",
                 "tex": r"0.8198 + (-1.2198) = -0.4,\qquad 0.8198 \times (-1.2198) \approx -1"},
            ],
            "answer": r"More friction decays the down oscillation faster ($e^{-0.2t}$) and slightly lowers its frequency; the up position remains a saddle with a positive eigenvalue $\approx 0.82$.",
        },
        "sources": {
            "video": [{"t": 1650, "label": "MATLAB: pick a small friction d = 0.1"},
                      {"t": 1680, "label": "Ad = [0 1; −1 −d]; eig(Ad)"},
                      {"t": 1710, "label": "Small negative real part ± i: lightly damped and stable"},
                      {"t": 1740, "label": "Au = [0 1; 1 −d]; eig(Au) ≈ −1.05 and 0.95"},
                      {"t": 1770, "label": "A saddle; locally unstable near the top"},
                      {"t": 1800, "label": "Next: add +Bu and stabilize the up position (frame 30:00 shows eig values)"},
                      {"t": 1830, "label": "Feedback for stability and robustness to disturbances"}],
            "book": [book(B335, "Down: center at ±i√(g/L); up: unstable saddle ±√(g/L) (undamped, for comparison)")],
        },
        "tutorNotes": "Book p.335: undamped pendulum down eigenvalues +-i sqrt(g/L) (the book calls it a stable center), up +-sqrt(g/L) unstable saddle. Lecture 27:30-30:46 (frame 30:00 shows the MATLAB window): d = 0.1; Ad = [0 1; -1 -d], eig(Ad) = -0.0500 +- 0.9987i; Au = [0 1; 1 -d], eig(Au) = -1.0512, 0.9512; up is a saddle, unstable locally; next lecture adds +Bu and feedback to stabilize the up position. The NumPy snippet in the notes is a companion, not shown in the video. Worked example d = 0.4 is authored.",
    },
]

for i, s in enumerate(SECTIONS, 1):
    s["number"] = i
    s["id"] = f"s{i}"

ORDER = ["number", "id", "nav", "title", "time", "summary", "goals", "notes", "keyIdeas", "example", "sources", "tutorNotes"]
SECTIONS = [{k: s[k] for k in ORDER} for s in SECTIONS]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-fixed", r"Which condition defines a fixed point $\bar x$ of $\dot x = f(x)$?", [
        (r"$f(\bar x) = 0$", True, r"Right. The velocity $\dot x = f(x)$ vanishes there, so a solution started at $\bar x$ never moves."),
        (r"$\bar x = 0$", False, r"No. The origin is a fixed point only if $f(0) = 0$; the upright pendulum $(\pi, 0)$ is a fixed point away from the origin."),
        (r"$\frac{Df}{Dx}\big|_{\bar x} = 0$", False, r"No. That is a condition on the derivative. The pendulum's fixed points have nonzero Jacobians."),
        (r"Small offsets from $\bar x$ decay back to $\bar x$.", False, r"No, that describes local asymptotic stability, a stronger property than being fixed. The upright pendulum is fixed but unstable.")]),
    q("q-jacobian-cell", r"In the Jacobian $\frac{Df}{Dx}$, where does $\partial f_2/\partial x_1$ go?", [
        (r"Row 2, column 1", True, r"Right. Rows belong to components $f_i$, columns to variables $x_j$; column 1 must meet $\Delta x_1$ in $\frac{Df}{Dx}\Delta x$."),
        (r"Row 1, column 2", False, r"No. That cell holds $\partial f_1/\partial x_2$. Swapping them gives the transpose."),
        (r"On the diagonal", False, r"No. Diagonal entries are $\partial f_i/\partial x_i$; here the component and the variable differ."),
        (r"It does not matter, the Jacobian is symmetric.", False, r"No. Jacobians are generally not symmetric: the pendulum's is $\begin{bmatrix}0&1\\-q\cos x_1&-d\end{bmatrix}$.")]),
    q("q-jacobian-eval", r"For $f = (x_1x_2,\ x_1^2 + x_2^2)$, what is the Jacobian at the point $(1, 2)$ (an arbitrary point, not a fixed point)?", [
        (r"$\begin{bmatrix}2&1\\2&4\end{bmatrix}$", True, r"Right. $\begin{bmatrix}x_2&x_1\\2x_1&2x_2\end{bmatrix}$ at $x_1 = 1$, $x_2 = 2$."),
        (r"$\begin{bmatrix}1&2\\2&4\end{bmatrix}$", False, r"No. The first row is $(\partial f_1/\partial x_1, \partial f_1/\partial x_2) = (x_2, x_1) = (2, 1)$; the entries were swapped."),
        (r"$\begin{bmatrix}2&2\\1&4\end{bmatrix}$", False, r"No. This is the transpose: rows and columns were interchanged."),
        (r"$\begin{bmatrix}0&0\\0&0\end{bmatrix}$", False, r"No. That is the value at the fixed point $(0, 0)$, not at $(1, 2)$.")]),
    q("q-shift", r"With $\eta = x - \bar x$ at a fixed point, why is $\dot\eta = f(\bar x + \eta)$?", [
        (r"Because $\bar x$ is constant, so $\dot\eta = \dot x - \dot{\bar x} = \dot x = f(x)$ with $x = \bar x + \eta$.", True, r"Right. Shifting by a constant does not change velocities."),
        (r"Because $f(\bar x) = 0$.", False, r"No. $f(\bar x) = 0$ is used later, to remove the constant term of the expansion; the shift itself only needs $\bar x$ constant."),
        (r"Because $\eta$ is small.", False, r"No. $\dot\eta = f(\bar x + \eta)$ is exact for any $\eta$; smallness matters only when truncating."),
        (r"It is an approximation that holds only near $\bar x$.", False, r"No. This step is exact. The approximation comes when the remainder is dropped.")]),
    q("q-truncate", r"Which statement about $\dot\eta \approx A\eta$ is correct?", [
        (r"For a twice continuously differentiable system, it neglects a remainder bounded by a constant times $\|\eta\|^2$ near $\bar x$.", True, r"Right. This gives a first-order local approximation. The remainder is small relative to $\|\eta\|$ near zero, but can still determine the motion when $A\eta$ vanishes; it need not vanish identically."),
        (r"It equals the nonlinear dynamics exactly near $\bar x$.", False, r"No. The Taylor expansion generally includes a nonzero higher-order remainder. Special cases can agree exactly, but equality is not guaranteed by linearization."),
        (r"It holds for all offsets once $A$ is evaluated at $\bar x$.", False, r"No. For the pendulum the linear model drifts badly for large swings; try the explorer's large-swing preset."),
        (r"It works the same about any point, fixed or not.", False, r"No. About a non-fixed point the constant $f(x_0) \neq 0$ survives and the model is affine.")]),
    q("q-hyperbolic", r"At a fixed point of a smooth system, $A$ has eigenvalues $-2$ and $0.5$. What can you conclude?", [
        (r"The fixed point is unstable (a saddle), and this holds for the nonlinear system.", True, r"Right. Both real parts are nonzero (hyperbolic) and one is positive, so the nonlinear fixed point is unstable."),
        (r"Nothing, because the eigenvalues are not all negative.", False, r"No. Hyperbolic means nonzero real parts with any signs; a saddle is hyperbolic, and the positive eigenvalue decides instability."),
        (r"It is stable, because the negative eigenvalue is larger in size.", False, r"No. One eigenvalue with positive real part is enough for instability, whatever the other is."),
        (r"Only a simulation of the nonlinear system can tell.", False, r"No. For hyperbolic points the linearization decides local stability; a finite simulation could not prove stability anyway.")]),
    q("q-neutral", r"The linearization at a fixed point has eigenvalues $\pm i$. What does that say about the nonlinear fixed point?", [
        (r"Nothing definite: the neglected terms decide, as $\dot x = \mp x^3$ (same $A = 0$, opposite behaviour) illustrates.", True, r"Right. Eigenvalues on the imaginary axis make the point nonhyperbolic, so the linearization is inconclusive."),
        (r"It is a stable center, because the linear model oscillates.", False, r"No. Nonlinear terms can make it spiral in or out. For the undamped pendulum stability follows from energy, not from $\pm i$."),
        (r"It is asymptotically stable.", False, r"That may be true for particular nonlinear terms, but $\pm i$ alone cannot establish it. The linearized model has no decaying envelope."),
        (r"It is unstable.", False, r"No. Without a positive real part the eigenvalues do not prove instability either.")]),
    q("q-offset-pi", r"A pendulum is tilted $0.15$ rad past upright. In the local model about the top, what is the state variable?", [
        (r"$\eta = \theta - \pi = 0.15$, the small offset from $\pi$.", True, r"Right. $\theta \approx 3.29$ rad is not small; the local model at the top uses the offset $\eta$."),
        (r"$\theta = 0.15$", False, r"No. With $\theta$ measured from the downward vertical, $\theta = 0.15$ is a pendulum hanging almost straight down."),
        (r"$\theta = 3.29$, treated as small", False, r"No. The linearization at the top is accurate for small $\theta - \pi$, not for small $\theta$."),
        (r"$\eta = \pi - 0.15$", False, r"No. That is an absolute angle short of upright, not the offset from the top.")]),
    q("q-damping", r"For the pendulum with $q > 0$ and friction $d > 0$, which statement is correct?", [
        (r"Down is locally asymptotically stable for every $d > 0$; it oscillates only if $d < 2\sqrt q$. Up stays a saddle.", True, r"Right. Down: real parts $< 0$ (complex for $d < 2\sqrt q$, real for $d > 2\sqrt q$). Up: $\sqrt{d^2 + 4q} > d$ keeps one eigenvalue positive."),
        (r"Damping always gives complex eigenvalues.", False, r"No. For $d > 2\sqrt q$ the down eigenvalues are real and negative (overdamped), as in the explorer's $d = 3$ preset."),
        (r"Enough friction makes the up position stable.", False, r"No. The up eigenvalue $\frac{-d + \sqrt{d^2 + 4q}}{2}$ is positive for every finite $d$."),
        (r"Friction only changes the oscillation frequency.", False, r"No. In the underdamped case it also gives the decaying envelope $e^{-dt/2}$; sufficiently large damping removes oscillation.")]),
    q("q-matlab", r"The lecture's MATLAB gives eig($A_u$) $= -1.0512$ and $0.9512$ for $d = 0.1$. What does that mean?", [
        (r"A saddle: one decaying and one growing direction, so the upright position is unstable.", True, r"Right. In continuous time a single positive real part, here $0.9512$, means instability."),
        (r"Stable, because the eigenvalues add up to $-0.1$.", False, r"No. A negative trace does not rule out a positive eigenvalue. Here $0.9512 > 0$ still makes the upright fixed point unstable."),
        (r"Stable, because $|-1.0512| > |0.9512|$.", False, r"No. Sizes do not cancel; the positive eigenvalue's mode $e^{0.9512t}$ still grows."),
        (r"Marginally stable, because both are close to $\pm 1$.", False, r"No. Neither eigenvalue is on the imaginary axis; $0.9512 > 0$ is clearly unstable.")]),
]

EXPLORER = {
    "playRate": 1,
    "limits": "Scope: the planar pendulum θ̇ = ω, ω̇ = −q sin θ − dω + u about the zero-input references θ̄ = 0 (down) and θ̄ = π (up), with ω̄ = ū = 0. Defaults q = 1, d = 0.1 are the lecture's MATLAB example; d = 0 is the book's undamped example. The constant input δu and the angle output are the book's input/output extension (u is the book's normalized input). Eigenvalue verdicts are about the zero-input reference; with δu ≠ 0 the curves compare input responses and prove nothing about stability under drive. The linear model's accuracy depends on the start, q, d and the time horizon; there is no universal offset cutoff. Numerics: RK4 with step ≤ 0.004 for the nonlinear model, a closed-form 2×2 matrix exponential for the linear model, both checked against SciPy. A finite plotted window cannot prove stability.",
    "tutorContext": "The explorer compares the nonlinear pendulum theta dot = omega, omega dot = -q sin(theta) - d omega + u with its linearization at a chosen zero-input reference theta bar = 0 (down) or pi (up), omega bar = u bar = 0: eta dot = nu, nu dot = -q cos(theta bar) eta - d nu + delta u, with eta = theta - theta bar, nu = omega. Sliders: initial offset eta(0) in [-1.5, 1.5] rad, initial angular velocity nu(0) in [-1.5, 1.5], q = g/L in [0.25, 4] (default 1), damping d in [0, 4] (default 0.1, the lecture's MATLAB value; the book example uses d = 0), time t in [0, 12] s, and, as a labelled book extension, a constant input delta u in [-0.5, 0.5] (default 0). It shows A = [[0, 1], [-q cos theta bar, -d]], its eigenvalues, B = [0; 1], C = [1 0], D = 0, the absolute angles theta = theta bar + eta of both models and their (unwrapped) difference, two pendulum drawings, eta(t) for both models, and the (eta, nu) phase plane. Verdicts for the zero-input reference: down with d = 0 is a linear center; the Jacobian is inconclusive and conserved energy gives Lyapunov stability, not asymptotic; down with d > 0 is locally asymptotically stable (focus if d < 2 sqrt q, critical at d = 2 sqrt q, node if larger); up is a saddle, unstable, for all d >= 0. With delta u not 0 the reference is no longer a fixed point and the plots are an input-response comparison. Presets: lecture down (d = 0.1), lecture up (d = 0.1), undamped down (book), large swing down, overdamped down (d = 3), exactly at equilibrium. The student's current slider values are not sent.",
}

COURSE = {
    "version": 1,
    "title": "Linearizing Around a Fixed Point",
    "subtitle": "A study companion to Steve Brunton's Control Bootcamp lecture on linearization and Section 8.2 of Brunton & Kutz",
    "video": {"id": "1YMTkELi3tE", "title": "Linearizing Around a Fixed Point [Control Bootcamp] (Steve Brunton, University of Washington)",
              "duration": "30:46", "url": "https://www.youtube.com/watch?v=1YMTkELi3tE"},
    "book": {"title": "Data-Driven Science and Engineering: Machine Learning, Dynamical Systems, and Control",
             "authors": "S. L. Brunton and J. N. Kutz", "edition": "2017 preprint (Chapter 8, Linear Control Theory, Section 8.2)",
             "onlineUrl": "http://databookuw.com/databook.pdf",
             "pageNote": "Page references give the printed page and the PDF page (printed page + 20 for these pages), checked against the local copy of databookuw.com/databook.pdf. A later revision of the online file could paginate differently."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide, and the worked-example numbers are authored for it. Material the lecture does not teach is labelled: authored examples, companion formulas, the NumPy check and the book's input/output extension. YouTube offers no English captions for this lecture, so timestamps were located with a local speech-recognition transcript in 30-second segments and checked against video frames at 6:00, 10:00, 14:00, 18:00, 22:00, 26:00 and 30:00; treat them as accurate to about half a minute. The video, transcript and chapter text are not included in this guide.",
    "explorer": EXPLORER,
    "sections": SECTIONS,
    "quiz": QUIZ,
}

# The correct answer is written first above; place it at a fixed, varied position per question.
for _i, _q in enumerate(QUIZ):
    _r = [2, 0, 3, 1, 1, 3, 0, 2, 3, 1][_i % 10]
    _q["choices"] = _q["choices"][-_r:] + _q["choices"][:-_r] if _r else _q["choices"]

if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(COURSE, f, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(SECTIONS)} sections, {len(QUIZ)} questions")
