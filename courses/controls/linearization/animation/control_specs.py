"""Step-by-step content of the Linearizing Around a Fixed Point animations (pure data, standard library only).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k is the
transition from state k-1 to state k. The scene calls `self.step_done()` once per step and
build_sequences.py checks that the recorded boundaries match len(steps).

Strings use $...$ for inline math (KaTeX in the browser). `tex` is the display formula of the state a
step reaches; the browser shows it on the step card and as the media fallback, so it must say the same
thing as the stage. `section` is the course section (1-7) a sequence belongs to.

All explanations are original paraphrases written for this guide; they summarize S. L. Brunton's
Control Bootcamp lecture "Linearizing Around a Fixed Point" and Section 8.2 of Brunton & Kutz,
"Data-Driven Science and Engineering" (2017 preprint, printed pp. 330 and 335), without quoting them.
Examples marked "authored" (x(1 - x), the +-x^3 pair, the sin remainder table, the non-fixed expansion
point) are not from the lecture. Input/output matrices B, C, D are the book's extension (Eqs. 8.8-8.10).

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
    # ------------------------------------------------------------------ section 1
    {
        "id": "fixed-points",
        "scene": "FixedPointSequence",
        "section": 1,
        "title": "Fixed points: where the velocity vanishes",
        "summary": "A fixed point satisfies $f(\\bar x) = 0$; it need not be the origin. The pendulum has two physical ones. Being fixed is not the same as being stable, and each fixed point gets its own local model.",
        "initial": {
            "title": "Nonlinear dynamics",
            "tex": r"\dot x = f(x),\qquad x \in \mathbb{R}^n",
            "explanation": "The lecture's starting point: a nonlinear vector field $f$ gives the velocity at every state. The goal is a linear model $\\dot x = Ax$ that is valid near a chosen point."},
        "steps": [
            {"title": "A fixed point: $f(\\bar x) = 0$", "relation": "define",
             "tex": r"\dot x\,\big|_{\bar x} = f(\bar x) = 0",
             "explanation": "A fixed point $\\bar x$ is a state where the velocity is zero: started exactly there, nothing moves. The condition is $f(\\bar x) = 0$, not $\\bar x = 0$."},
            {"title": "The pendulum: hanging and balanced", "relation": "diagram",
             "tex": r"\bar\theta = 0\ (\text{down}),\qquad \bar\theta = \pi\ (\text{up}),\qquad \dot\theta = 0",
             "explanation": "A pendulum hanging straight down, or balanced exactly upright, stays put if it has no velocity and nothing disturbs it. Both positions are fixed points."},
            {"title": "Solve $f(x) = 0$ (authored example)", "relation": "solve",
             "tex": r"\dot x = x(1 - x) = 0 \;\Rightarrow\; \bar x = 0\ \text{or}\ \bar x = 1",
             "explanation": "For the authored one-dimensional example $\\dot x = x(1 - x)$, a product is zero when one factor is: two fixed points, one of them away from the origin."},
            {"title": "Fixed does not mean stable", "relation": "compare",
             "tex": r"\bar x = 0:\ \text{offsets grow (unstable)},\qquad \bar x = 1:\ \text{offsets return (stable)}",
             "explanation": "Arrows show the sign of $\\dot x$: positive between $0$ and $1$, negative elsewhere. A small push leaves $0$ but returns to $1$. Both are fixed points; only one is stable. The upright pendulum is another fixed but unstable state."},
            {"title": "One local model per fixed point", "relation": "implies",
             "tex": r"f'(x) = 1 - 2x:\qquad \bar x = 0:\ \dot\eta \approx +\eta,\qquad \bar x = 1:\ \dot\eta \approx -\eta",
             "explanation": "Zooming in at each fixed point gives a different linear model, with the slope $f'(\\bar x)$ as its one-by-one matrix $A$ ($\\eta$ is the offset from that point; Section 3). The signs $+1$ and $-1$ agree with the arrows."},
        ],
    },
    # ------------------------------------------------------------------ section 2
    {
        "id": "jacobian-cells",
        "scene": "JacobianSequence",
        "section": 2,
        "title": "The Jacobian, one cell at a time",
        "summary": "Entry $(i, j)$ of $Df/Dx$ is $\\partial f_i/\\partial x_j$. For $f = (x_1x_2,\\ x_1^2 + x_2^2)$ each partial derivative drops into its cell; at the only fixed point $(0, 0)$ every entry vanishes, which decides nothing.",
        "initial": {
            "title": "Two nonlinear equations",
            "tex": r"\dot x_1 = f_1 = x_1x_2,\qquad \dot x_2 = f_2 = x_1^2 + x_2^2",
            "explanation": "The lecture's example of a two-state nonlinear system."},
        "steps": [
            {"title": "Rows $f_i$, columns $x_j$", "relation": "define",
             "tex": r"\frac{Df}{Dx} = \begin{bmatrix}\partial f_1/\partial x_1 & \partial f_1/\partial x_2\\ \partial f_2/\partial x_1 & \partial f_2/\partial x_2\end{bmatrix},\qquad \frac{Df}{Dx}\begin{bmatrix}\Delta x_1\\ \Delta x_2\end{bmatrix}",
             "explanation": "Each row belongs to one component $f_i$, each column to one state $x_j$. The lecturer's memory aid: the matrix multiplies a small step $\\Delta x$, so the entries of column $j$ must meet $\\Delta x_j$, and therefore be derivatives with respect to $x_j$."},
            {"title": "Row 1: differentiate $x_1x_2$", "relation": "compute",
             "tex": r"\frac{Df}{Dx} = \begin{bmatrix} x_2 & x_1\\ \partial f_2/\partial x_1 & \partial f_2/\partial x_2\end{bmatrix}",
             "explanation": "With $x_2$ held fixed, $x_1x_2$ changes at rate $x_2$; with $x_1$ held fixed, at rate $x_1$. These fill row 1."},
            {"title": "Row 2: differentiate $x_1^2 + x_2^2$", "relation": "compute",
             "tex": r"\frac{Df}{Dx} = \begin{bmatrix} x_2 & x_1\\ 2x_1 & 2x_2\end{bmatrix}",
             "explanation": "Each square differentiates to twice its variable, and the other square is a constant for that partial derivative. The matrix is the Jacobian of $f$; it still depends on where it is evaluated."},
            {"title": "Evaluate at the fixed point", "relation": "substitute",
             "tex": r"x_1x_2 = 0,\ x_1^2 + x_2^2 = 0 \;\Rightarrow\; \bar x = (0, 0),\qquad A = \frac{Df}{Dx}\Big|_{(0,0)} = \begin{bmatrix}0&0\\0&0\end{bmatrix}",
             "explanation": "$x_1^2 + x_2^2 = 0$ forces both coordinates to zero, so the origin is the only real fixed point. Plugging in its coordinates turns the symbolic Jacobian into a matrix of numbers; here every entry vanishes."},
            {"title": "$A = 0$ decides nothing", "relation": "caution",
             "tex": r"A = 0:\ \dot\eta \approx 0\ \ (\text{both eigenvalues } 0)\;\Rightarrow\;\text{inconclusive}",
             "explanation": "With $A = 0$ the linear model predicts no motion at all, so the quadratic terms decide. Here they make the origin unstable: on the $x_2$ axis $\\dot x_2 = x_2^2$ pushes any positive offset away (authored check). Section 4 explains when $A$ can be trusted."},
        ],
    },
    # ------------------------------------------------------------------ section 3
    {
        "id": "shift-expand",
        "scene": "ShiftExpandSequence",
        "section": 3,
        "title": "Shift, expand, truncate",
        "summary": "Move the origin to the fixed point, expand $f(\\bar x + \\eta)$ in a Taylor series, drop the constant $f(\\bar x) = 0$ and neglect the small remainder: $\\dot\\eta \\approx A\\eta$ with $A$ the Jacobian at $\\bar x$.",
        "initial": {
            "title": "Zoom in on a fixed point",
            "tex": r"\dot x = f(x),\qquad f(\bar x) = 0",
            "explanation": "Near a fixed point the lecturer zooms in: in a small enough window the flow looks linear. The Taylor series makes this precise."},
        "steps": [
            {"title": "Move the origin to $\\bar x$", "relation": "define",
             "tex": r"\eta = x - \bar x",
             "explanation": "Measure the state from the fixed point. The lecture calls the offset $\\Delta x$ and later just $x$; this guide writes $\\eta$ so the shifted and original states are never confused."},
            {"title": "$\\dot\\eta = \\dot x$ because $\\bar x$ is constant", "relation": "identity",
             "tex": r"\dot\eta = \dot x - \dot{\bar x} = \dot x = f(\bar x + \eta)",
             "explanation": "The fixed point does not move, so $\\dot{\\bar x} = 0$ and the shift leaves velocities unchanged. The lecture glosses over this step; it is why $\\eta$ obeys the same $f$, evaluated at $\\bar x + \\eta$."},
            {"title": "Taylor expansion about $\\bar x$", "relation": "identity",
             "tex": r"\dot\eta = f(\bar x) + \frac{Df}{Dx}\Big|_{\bar x}\,\eta + \mathcal{O}(\|\eta\|^2)",
             "explanation": "For a smooth $f$ (twice continuously differentiable is enough) the expansion has a constant term, a linear term with the Jacobian at $\\bar x$, and a remainder bounded by a constant times $\\|\\eta\\|^2$ near $\\bar x$."},
            {"title": "The constant term vanishes", "relation": "substitute",
             "tex": r"\dot\eta = \underbrace{f(\bar x)}_{0} + A\,\eta + \mathcal{O}(\|\eta\|^2),\qquad A = \frac{Df}{Dx}\Big|_{\bar x}",
             "explanation": "At a fixed point $f(\\bar x) = 0$ by definition, and the Jacobian evaluated there is a constant matrix, called $A$."},
            {"title": "The remainder shrinks faster", "relation": "compare",
             "tex": r"\sin\eta = \eta + r(\eta):\quad \eta = 1.2:\ |r| \approx 0.268;\qquad \eta = 0.6:\ |r| \approx 0.035",
             "explanation": "Authored illustration with $f = \\sin$ at $\\bar x = 0$: halving $\\eta$ from $1.2$ to $0.6$ halves the retained term $A\\eta = \\eta$ but cuts the remainder by about $7.6$. For a twice continuously differentiable vector field the general remainder is bounded by a constant times $\\|\\eta\\|^2$, so it is small relative to $\\|\\eta\\|$ near zero. If $A\\eta$ vanishes, higher-order terms can still decide the motion."},
            {"title": "Truncate: the local linear model", "relation": "implies",
             "tex": r"\dot\eta \approx A\,\eta\qquad(\text{local approximation, not an identity})",
             "explanation": "Dropping the remainder gives the model the lecture writes as $\\Delta\\dot x = A\\,\\Delta x$, or simply $\\dot x = Ax$. It improves as $\\eta \\to 0$; the nonlinear and truncated dynamics are not equal."},
        ],
    },
    {
        "id": "affine-abcd",
        "scene": "AffineSequence",
        "section": 3,
        "title": "Away from a fixed point; inputs and outputs",
        "summary": "About a point that is not fixed, the constant term survives and the model is affine. With an input and an output (book extension), expanding about an equilibrium pair gives $A$, $B$, $C$ and $D$.",
        "initial": {
            "title": "Expanding about any point",
            "tex": r"\dot\eta = f(x_0) + \frac{Df}{Dx}\Big|_{x_0}\eta + \mathcal{O}(\|\eta\|^2)",
            "explanation": "The same expansion works about any point $x_0$, but the constant term $f(x_0)$ only disappears at a fixed point."},
        "steps": [
            {"title": "Not a fixed point: a constant drift remains", "relation": "caution",
             "tex": r"\dot x = x(1 - x),\ x_0 = 0.5:\quad \dot\eta = 0.25 + 0\cdot\eta - \eta^2",
             "explanation": "Authored example: about $x_0 = 0.5$ the velocity is $0.25$, so the state drifts away at once and the truncated model $\\dot\\eta \\approx 0.25$ is affine, not linear. Linearize about fixed points (with inputs, about an equilibrium pair)."},
            {"title": "Inputs: $B = \\partial f/\\partial u$ (book extension)", "relation": "model",
             "tex": r"\dot x = f(x, u),\ f(\bar x, \bar u) = 0:\quad \dot\eta \approx A\eta + B\,\delta u,\quad B = \frac{\partial f}{\partial u}\Big|_{\bar x, \bar u}",
             "explanation": "Book Eq. 8.8: expand in the state and in the input offset $\\delta u = u - \\bar u$ about an equilibrium pair. The lecture treats the unforced case and promises $+Bu$ for the next lectures."},
            {"title": "Outputs: $C$ and $D$", "relation": "model",
             "tex": r"y = g(x, u):\quad \delta y \approx C\eta + D\,\delta u,\quad C = \frac{\partial g}{\partial x}\Big|_{\bar x, \bar u},\ D = \frac{\partial g}{\partial u}\Big|_{\bar x, \bar u}",
             "explanation": "Book Eq. 8.9. Dropping the offsets' $\\delta$ labels in shifted coordinates gives the book's $\\dot x = Ax + Bu$, $y = Cx + Du$ (Eq. 8.10). For the pendulum with angle output, $C = [1\\ \\ 0]$ and $D = 0$."},
        ],
    },
    # ------------------------------------------------------------------ section 4
    {
        "id": "hyperbolic",
        "scene": "HyperbolicSequence",
        "section": 4,
        "title": "When can the linear model be trusted?",
        "summary": "If every eigenvalue of $A$ has a nonzero real part (hyperbolic), the linearization decides local stability: all negative gives local asymptotic stability, any positive real part instability. On the imaginary axis it decides nothing, as $\\dot x = \\mp x^3$ shows.",
        "initial": {
            "title": "The neglected remainder",
            "tex": r"\dot\eta = A\eta + \mathcal{O}(\|\eta\|^2)",
            "explanation": "The remainder is small near $\\bar x$ but not zero. Whether it can change the qualitative picture depends on the eigenvalues of $A$."},
        "steps": [
            {"title": "Hyperbolic: no eigenvalue on the imaginary axis", "relation": "define",
             "tex": r"\text{hyperbolic} \;\Leftrightarrow\; \mathrm{Re}\,\lambda_i \neq 0\ \text{for every eigenvalue } \lambda_i \text{ of } A",
             "explanation": "Hyperbolic means every eigenvalue has a nonzero real part, whatever the signs: all negative, all positive or a mixture. It does not mean all eigenvalues are negative."},
            {"title": "All real parts negative: locally asymptotically stable", "relation": "classify",
             "tex": r"\mathrm{Re}\,\lambda_i < 0\ \text{for all } i \;\Rightarrow\; \bar x\ \text{locally asymptotically stable}",
             "explanation": "Then small offsets of the nonlinear system decay to $\\bar x$, as in the linear model. This needs a continuously differentiable $f$."},
            {"title": "One positive real part: unstable", "relation": "classify",
             "tex": r"\mathrm{Re}\,\lambda_j > 0\ \text{for some } j \;\Rightarrow\; \bar x\ \text{unstable}",
             "explanation": "A single eigenvalue with positive real part makes the nonlinear fixed point unstable, as for a saddle. Eigenvalues in the left half-plane do not rescue it."},
            {"title": "On the axis: inconclusive", "relation": "caution",
             "tex": r"\mathrm{Re}\,\lambda = 0\ \text{(none positive)}:\ \text{not decided by } A",
             "explanation": "With purely imaginary or zero eigenvalues, and none in the right half-plane, the neglected terms can tip the balance either way; in the lecturer's words, all bets are off. His example is the undamped pendulum."},
            {"title": "Same $A = 0$, two systems (authored)", "relation": "compare",
             "tex": r"\dot x = -x^3\ \text{and}\ \dot x = +x^3:\qquad A = \frac{d(\mp x^3)}{dx}\Big|_{0} = \mp 3x^2\Big|_{0} = 0",
             "explanation": "Both have the fixed point $0$ and exactly the same linearization $\\dot\\eta = 0$."},
            {"title": "The nonlinear terms decide", "relation": "diagram",
             "tex": r"-x^3:\ \text{offsets return (stable)},\qquad +x^3:\ \text{offsets escape (unstable)}",
             "explanation": "Arrows point toward the origin for $-x^3$ and away for $+x^3$: identical $A$, opposite behaviour. For hyperbolic points the Hartman–Grobman theorem guarantees the nonlinear flow near $\\bar x$ is a continuous deformation of the linear one. That is local and qualitative: no exact trajectories, periods or radius of validity."},
        ],
    },
    # ------------------------------------------------------------------ section 5
    {
        "id": "pendulum-state",
        "scene": "PendulumStateSequence",
        "section": 5,
        "title": "The pendulum in state-space form",
        "summary": "Add friction, normalize $g/L = 1$, write $x = (\\theta, \\dot\\theta)$ and solve $f(\\bar x) = 0$: $x_2 = 0$ and $\\sin x_1 = 0$ give the down and up equilibria. Near the top, the small quantity is the offset from $\\pi$.",
        "initial": {
            "title": "The pendulum",
            "tex": r"\ddot\theta = -\frac{g}{L}\sin\theta",
            "explanation": "The angle $\\theta$ (radians) is measured from the downward vertical. The lecture states the equation of motion without deriving it."},
        "steps": [
            {"title": "Add viscous friction", "relation": "model",
             "tex": r"\ddot\theta = -\frac{g}{L}\sin\theta - d\,\dot\theta,\qquad d > 0",
             "explanation": "A friction term proportional to the angular velocity, so a real pendulum eventually stops. The board writes $\\delta$; the MATLAB part uses $d$. The book's example (Eq. 8.23) has no friction."},
            {"title": "Normalize $g/L = 1$", "relation": "substitute",
             "tex": r"q = \frac{g}{L} = 1:\qquad \ddot\theta = -\sin\theta - d\,\dot\theta",
             "explanation": "The lecturer sets $g/L = 1$ to keep the algebra short. The explorer keeps $q = g/L$ as a slider."},
            {"title": "Second order to first order", "relation": "define",
             "tex": r"x = \begin{bmatrix}x_1\\ x_2\end{bmatrix} = \begin{bmatrix}\theta\\ \dot\theta\end{bmatrix} \;\Rightarrow\; \frac{d}{dt}\begin{bmatrix}x_1\\ x_2\end{bmatrix} = \begin{bmatrix}x_2\\ -\sin x_1 - d\,x_2\end{bmatrix}",
             "explanation": "One second-order equation becomes two first-order ones: $\\dot x_1 = x_2$ restates the definition of $x_2$, and $\\dot x_2 = \\ddot\\theta$ carries the physics."},
            {"title": "Fixed points: $x_2 = 0$ and $\\sin x_1 = 0$", "relation": "solve",
             "tex": r"x_2 = 0,\ \sin x_1 = 0 \;\Rightarrow\; \bar x = (k\pi, 0):\ (0, 0)\ \text{down},\ (\pi, 0)\ \text{up}\ \ (\mathrm{mod}\ 2\pi)",
             "explanation": "The first row forces $x_2 = 0$, which also removes the friction term; then $\\sin x_1 = 0$. Angles that differ by $2\\pi$ are the same physical position, so there are two distinct physical equilibria."},
            {"title": "Near up, measure the offset from $\\pi$", "relation": "caution",
             "tex": r"\theta = \pi + \eta,\quad \eta = 0.15:\quad \theta \approx 3.29\ \text{rad (a small tilt past upright)}",
             "explanation": "A pendulum slightly past upright has $\\theta \\approx 3.29$ rad, not a small angle. The small quantity is the offset $\\eta = \\theta - \\pi$; the local model at the top is written in $\\eta$."},
        ],
    },
    # ------------------------------------------------------------------ section 6
    {
        "id": "two-jacobians",
        "scene": "TwoJacobiansSequence",
        "section": 6,
        "title": "Two Jacobians, two behaviours",
        "summary": "$Df/Dx = [[0, 1], [-q\\cos x_1, -d]]$. Evaluating at $0$ and $\\pi$ flips one sign. Down is a center without friction and decays with it; up is a saddle for every $d \\ge 0$.",
        "initial": {
            "title": "The pendulum vector field",
            "tex": r"f(x) = \begin{bmatrix}x_2\\ -q\sin x_1 - d\,x_2\end{bmatrix}",
            "explanation": "Keep $q = g/L$ general for now (the lecture uses $q = 1$)."},
        "steps": [
            {"title": "Four partial derivatives", "relation": "compute",
             "tex": r"\frac{Df}{Dx} = \begin{bmatrix}0 & 1\\ -q\cos x_1 & -d\end{bmatrix}",
             "explanation": "Row 1: $x_2$ does not contain $x_1$ ($0$) and has slope $1$ in $x_2$. Row 2: $-q\\sin x_1$ differentiates to $-q\\cos x_1$, and the friction term gives $-d$."},
            {"title": "Evaluate down and up", "relation": "substitute",
             "tex": r"A_d = \begin{bmatrix}0&1\\-q&-d\end{bmatrix}\ (\cos 0 = 1),\qquad A_u = \begin{bmatrix}0&1\\q&-d\end{bmatrix}\ (\cos\pi = -1)",
             "explanation": "Only one entry changes: $\\cos\\pi = -1$ flips the sign of the gravity term. Down, gravity pulls an offset back; up, it pushes it further. Book Eq. 8.25 has the same matrices with $d = 0$."},
            {"title": "Local coordinates at each point", "relation": "define",
             "tex": r"\eta = \theta - \bar\theta,\ \nu = \omega:\qquad \dot\eta = \nu,\quad \dot\nu \approx \mp q\,\eta - d\,\nu",
             "explanation": "Each matrix acts on the offset from its own fixed point; at the top $\\eta = \\theta - \\pi$. Upper sign down ($-q$), lower sign up ($+q$)."},
            {"title": "Characteristic equations", "relation": "compute",
             "tex": r"\text{down: } \lambda = \frac{-d \pm \sqrt{d^2 - 4q}}{2},\qquad \text{up: } \lambda = \frac{-d \pm \sqrt{d^2 + 4q}}{2}",
             "explanation": "$\\det(\\lambda I - A) = \\lambda^2 + d\\lambda \\pm q$ (plus down, minus up). Companion formula: the lecture does the $d = 0$ case in his head and the $d = 0.1$ case in MATLAB."},
            {"title": "No friction: center versus saddle", "relation": "classify",
             "tex": r"d = 0:\quad \lambda_d = \pm i\sqrt q\ \ (\text{linear center}),\qquad \lambda_u = \pm\sqrt q\ \ (\text{saddle})",
             "explanation": "Down, the linear model has closed orbits, but the point is not hyperbolic, so the Jacobian alone does not decide (the conserved energy shows it is stable, not asymptotically). Up, the eigenvalue $+\\sqrt q > 0$ makes it unstable."},
            {"title": "With friction: down decays, up stays a saddle", "relation": "classify",
             "tex": r"d > 0:\ \mathrm{Re}\,\lambda_d < 0\ (\text{focus if } d < 2\sqrt q,\ \text{node if } d > 2\sqrt q);\qquad \lambda_u = \tfrac{-d + \sqrt{d^2 + 4q}}{2} > 0",
             "explanation": "Any friction moves both down eigenvalues into the left half-plane: hyperbolic, locally asymptotically stable. Small $d$ keeps the oscillation, $d > 2\\sqrt q$ removes it (overdamped). Up, $\\sqrt{d^2 + 4q} > d$, so one eigenvalue stays positive. All of this is local: it says nothing about large swings."},
        ],
    },
    # ------------------------------------------------------------------ section 7
    {
        "id": "matlab-check",
        "scene": "MatlabSequence",
        "section": 7,
        "title": "The MATLAB check with $d = 0.1$",
        "summary": "With $q = 1$, $d = 0.1$: eig($A_d$) $= -0.05 \\pm 0.9987i$ (decaying oscillation) and eig($A_u$) $= -1.0512, 0.9512$ (saddle), as the lecture's MATLAB session shows.",
        "initial": {
            "title": "The lecture's matrices",
            "tex": r"d = 0.1:\quad A_d = \begin{bmatrix}0&1\\-1&-0.1\end{bmatrix},\qquad A_u = \begin{bmatrix}0&1\\1&-0.1\end{bmatrix}",
            "explanation": "With $q = 1$ and a small friction $d = 0.1$ the lecturer types the two matrices into MATLAB and asks for their eigenvalues."},
        "steps": [
            {"title": "Down: the characteristic polynomial", "relation": "substitute",
             "tex": r"\det(\lambda I - A_d) = \lambda^2 + 0.1\,\lambda + 1 = 0",
             "explanation": "Substitute $q = 1$, $d = 0.1$ into $\\lambda^2 + d\\lambda + q$."},
            {"title": "eig(Ad) $= -0.05 \\pm 0.9987i$", "relation": "compute",
             "tex": r"\lambda = -0.05 \pm i\sqrt{1 - 0.0025} = -0.05 \pm 0.998749\,i",
             "explanation": "The eigenvalues move from $\\pm i$ slightly into the left half-plane: an oscillation at angular frequency about $0.9987$ inside the decaying envelope $e^{-0.05t}$. MATLAB prints $-0.0500 \\pm 0.9987i$."},
            {"title": "Up: the characteristic polynomial", "relation": "substitute",
             "tex": r"\det(\lambda I - A_u) = \lambda^2 + 0.1\,\lambda - 1 = 0",
             "explanation": "Only the sign of the constant term changes."},
            {"title": "eig(Au) $= -1.0512,\\ 0.9512$", "relation": "compute",
             "tex": r"\lambda = -0.05 \pm \sqrt{0.0025 + 1} = -1.051249,\ \ 0.951249",
             "explanation": "From $\\pm 1$ both eigenvalues shift left by about $0.05$, but one stays positive. MATLAB prints $-1.0512$ and $0.9512$: a saddle, so the upright position is unstable."},
            {"title": "What the numbers say, and what comes next", "relation": "recap",
             "tex": r"\text{down: stable focus},\qquad \text{up: saddle (unstable)},\qquad \text{next lectures: } \dot x = Ax + Bu",
             "explanation": "The signs match the physical intuition, which also confirms the Jacobian signs. The next lectures add an input $Bu$ and feedback to stabilize the upright position; no controller is designed here."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
