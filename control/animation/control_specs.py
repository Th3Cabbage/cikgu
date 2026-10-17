"""Step-by-step content of the Control Bootcamp animations (pure data, standard library only).

Each sequence is one ManimGL scene in control_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. The scene calls `self.step_done()` once per step and
build_control.py checks that the recorded boundaries match len(steps).

Strings use $...$ for inline math (KaTeX in the browser). `tex` is the display formula of the
state a step reaches; the browser shows it on the step card and as the media fallback, so it
must say the same thing as the stage. `section` is the course section (1-6) a sequence belongs to.

All explanations are original paraphrases written for this guide; they summarize S. L. Brunton's
Control Bootcamp overview lecture and Section 8.1 of Brunton & Kutz, "Data-Driven Science and
Engineering" (2017 preprint), without quoting them.
"""

RELATIONS = {
    "define": "Definition / choice",
    "model": "Modelling step",
    "classify": "Classification",
    "diagram": "Block diagram",
    "substitute": "Substitution",
    "identity": "Identity (=)",
    "equivalent": "Equivalent equation (⇔)",
    "solve": "Solve",
    "compute": "Computation",
    "implies": "Consequence (⇒)",
    "compare": "Comparison",
    "caution": "Caveat",
    "recap": "Recap",
}

SEQUENCES = [
    # ------------------------------------------------------------------ section 1
    {
        "id": "state-io",
        "scene": "StateIOSequence",
        "section": 1,
        "title": "State, dynamics, input and output",
        "summary": "Describe an inverted pendulum the way control theory does: a state that evolves, an input we choose and an output we measure.",
        "initial": {
            "title": "An inverted pendulum",
            "tex": r"\theta(t)",
            "explanation": "A rod balanced upright on a hinge. Its tilt from vertical, $\\theta$, changes with time $t$. Before we can steer it we need a precise description of what it is doing.",
        },
        "steps": [
            {"title": "The state collects what we need to know", "relation": "define",
             "tex": r"x = \begin{bmatrix} \theta \\ \dot\theta \end{bmatrix}",
             "explanation": "The tilt $\\theta$ alone does not tell us what happens next: a rod passing upright while swinging fast behaves differently from one at rest. Angle and angular velocity $\\dot\\theta = d\\theta/dt$ together form the state vector $x$."},
            {"title": "A model predicts how the state changes", "relation": "model",
             "tex": r"\dot x = f(x)",
             "explanation": "A model gives the rate of change $\\dot x$ from the current state. Followed forward in time it predicts the motion: upright is an equilibrium, but a tiny tilt grows and the rod falls. The upright position is unstable."},
            {"title": "Add an input we can choose", "relation": "model",
             "tex": r"\dot x = f(x, u)",
             "explanation": "Control adds an input $u$ that we set ourselves, for example a torque at the hinge or a motion of the base. The model now says how the state responds to both its own dynamics and to $u$."},
            {"title": "Measure an output", "relation": "model",
             "tex": r"y = g(x)",
             "explanation": "Sensors report an output $y$ that depends on the state, perhaps only the angle. Later in this overview we assume the whole state is measured, $y = x$."},
            {"title": "State the goal", "relation": "define",
             "tex": r"\text{choose } u \text{ so that } x(t) \to 0",
             "explanation": "With the upright position placed at $x = 0$, the control goal is to pick the input so the state returns to zero and stays near it, even though the uncontrolled rod would fall."},
        ],
    },
    # ------------------------------------------------------------------ section 2
    {
        "id": "control-types",
        "scene": "ControlTypesSequence",
        "section": 2,
        "title": "Types of control and the feedback loop",
        "summary": "From passive design to active control, open loop versus closed loop, assembled into a feedback block diagram.",
        "initial": {
            "title": "Ways to change behaviour",
            "tex": r"\text{control}",
            "explanation": "There are many ways to make a system behave better. The overview sorts them by two questions: do we spend energy while it runs, and do we measure what it is doing?",
        },
        "steps": [
            {"title": "Passive or active", "relation": "classify",
             "tex": r"\text{control} \to \{\text{passive},\ \text{active}\}",
             "explanation": "Passive control is designed in once and needs no energy while running, like the streamlined tail fairing on a truck that reduces drag. Active control keeps putting energy in through an actuator."},
            {"title": "Active: open loop or closed loop", "relation": "classify",
             "tex": r"\text{active} \to \{\text{open loop},\ \text{closed-loop feedback}\}",
             "explanation": "Open-loop control plays a preplanned input without looking at the system. Closed-loop feedback uses sensors to decide the input. The book's diagram also lists disturbance feedforward: measuring an incoming disturbance and feeding it into a planned input."},
            {"title": "Open loop: plan the input from a model", "relation": "diagram",
             "tex": r"r \to \text{controller} \to u \to \text{system} \to y",
             "explanation": "Given a desired output $r$, an open-loop controller uses a model of the system to compute the input $u$ that should produce it. Nothing flows back: if the model is wrong or something pushes the system, the controller never finds out."},
            {"title": "Closed loop: measure and feed back", "relation": "diagram",
             "tex": r"e = r - y, \qquad u = \text{controller}(e)",
             "explanation": "Now the measured output $y$ returns along the feedback path and is subtracted from the reference: the error $e = r - y$ drives the controller. The input reacts to what the system is actually doing."},
            {"title": "The overview's regulator", "relation": "diagram",
             "tex": r"r = 0,\quad y = x,\quad u = -Kx",
             "explanation": "For balancing, the reference is the upright state $r = 0$, every state is measured ($y = x$) and the controller is a gain matrix: $u = -Kx$. This is the loop analysed in the rest of the overview."},
        ],
    },
    # ------------------------------------------------------------------ section 3
    {
        "id": "why-feedback",
        "scene": "WhyFeedbackSequence",
        "section": 3,
        "title": "Why feedback?",
        "summary": "Four reasons from the lecture, each with the condition under which it holds.",
        "initial": {
            "title": "Why measure and feed back?",
            "tex": r"\text{why feedback?}",
            "explanation": "Sensors, wiring and a control law add cost and complexity. The lecture lists four reasons they can be worth it. Each is a possibility that good design unlocks, not a guarantee.",
        },
        "steps": [
            {"title": "1. Uncertainty inside the model", "relation": "compare",
             "tex": r"a_{\text{true}} \neq a_{\text{model}}",
             "explanation": "A plan computed from a slightly wrong model (the rod a little taller, a car a little heavier) misses its target, and open loop cannot notice. Feedback measures the miss and corrects it without needing a perfect model."},
            {"title": "2. Instability", "relation": "compare",
             "tex": r"\dot x = Ax + Bu(t):\ \text{eigenvalues of } A \text{ unchanged}",
             "explanation": "Adding a preplanned input to a fixed linear model does not change $A$, so an eigenvalue at $\\lambda = +1$ stays there. Feedback $u = -Kx$ makes the input depend on the state and changes the matrix itself, so it can move eigenvalues. (The vibrating-base pendulum works through a different, parametric effect.)"},
            {"title": "3. Disturbances from outside", "relation": "compare",
             "tex": r"\dot x = Ax + Bu + d",
             "explanation": "A gust of wind $d$ is external forcing that may be too hard to predict or measure directly. Its effect shows up in the measured output, so a well-designed feedback loop can counteract it. Uncertainty is internal (the model is wrong); disturbance is external."},
            {"title": "4. Efficiency, and the fine print", "relation": "caution",
             "tex": r"\text{good design} \Rightarrow \text{small corrections}",
             "explanation": "A good balancing controller acts early, so it needs only small corrections instead of constant pumping. But feedback is not automatically better: a poorly chosen gain can destabilize a loop, and high gain also amplifies sensor noise."},
        ],
    },
    {
        "id": "cruise-model",
        "scene": "CruiseSequence",
        "section": 3,
        "title": "A static cruise-control teaching model",
        "summary": "Derive open-loop and proportional closed-loop speed for a deliberately crude static model.",
        "initial": {
            "title": "A crude static model",
            "tex": r"y = a\,u + d",
            "explanation": "A teaching model, not a vehicle simulator: speed $y$ responds instantly to throttle $u$ with gain $a$, plus a disturbance $d$ such as a hill. There are no dynamics, so it can show tracking error but not instability.",
        },
        "steps": [
            {"title": "Open loop: invert the model", "relation": "substitute",
             "tex": r"u = \frac{r}{a_m} \;\Rightarrow\; y = \frac{a}{a_m}\,r + d",
             "explanation": "To reach the reference speed $r$, the open-loop plan inverts the model gain $a_m$. If the true gain $a$ differs from $a_m$, the speed is off by the ratio $a/a_m$, and the whole disturbance $d$ passes straight through."},
            {"title": "Closed loop: throttle from the error", "relation": "substitute",
             "tex": r"u = K(r - y) \;\Rightarrow\; y = aK(r - y) + d",
             "explanation": "A proportional controller opens the throttle in proportion to the speed error $r - y$. Substituting it into the model puts $y$ on both sides."},
            {"title": "Collect the $y$ terms", "relation": "equivalent",
             "tex": r"(1 + aK)\,y = aK\,r + d",
             "explanation": "Expand $aK(r - y)$, move $-aKy$ to the left and factor out $y$. Each step keeps exactly the same solutions."},
            {"title": "Solve and compare", "relation": "solve",
             "tex": r"y = \frac{aK}{1 + aK}\,r + \frac{1}{1 + aK}\,d",
             "explanation": "Divide by $1 + aK > 0$. The model mismatch is no longer needed and the disturbance is divided by $1 + aK$. With $a = 0.5$, $K = 50$: $y = \\tfrac{25}{26}r + \\tfrac{1}{26}d$. The error $(r - d)/(1 + aK)$ shrinks with gain but generally stays nonzero at finite $K$: proportional control alone cannot guarantee zero tracking error for every reference and disturbance."},
        ],
    },
    # ------------------------------------------------------------------ section 4
    {
        "id": "state-space",
        "scene": "StateSpaceSequence",
        "section": 4,
        "title": "The language of state space",
        "summary": "From $\\dot x = Ax$ to $\\dot x = Ax + Bu$, $y = Cx$, with the sizes of every matrix.",
        "initial": {
            "title": "A linear system",
            "tex": r"\dot x = A\,x",
            "explanation": "Near an equilibrium many systems are well described by linear equations: each component of $\\dot x$ is a fixed linear combination of the components of $x$, collected in the matrix $A$.",
        },
        "steps": [
            {"title": "The unforced solution", "relation": "implies",
             "tex": r"x(t) = e^{At}\,x(0)",
             "explanation": "The solution is the matrix exponential $e^{At}$ applied to the initial state. We will not compute it; what matters is that the eigenvalues of $A$ decide its behaviour: all real parts negative means decay to zero, any positive real part means growth."},
            {"title": "Add the control knob", "relation": "model",
             "tex": r"\dot x = A\,x + B\,u",
             "explanation": "The input $u$ is the knob we turn: a motor voltage, a torque, the position of the base. The matrix $B$ says how each input component pushes the rate of change of the state."},
            {"title": "Measure with $C$", "relation": "model",
             "tex": r"y = C\,x",
             "explanation": "Sensors read linear combinations of the state, $y = Cx$, possibly far fewer numbers than $x$ has. The general form adds $Du$; the overview assumes no direct feedthrough, $D = 0$."},
            {"title": "Check the sizes", "relation": "define",
             "tex": r"x \in \mathbb{R}^n,\ u \in \mathbb{R}^m,\ y \in \mathbb{R}^p;\quad A_{n\times n},\ B_{n\times m},\ C_{p\times n}",
             "explanation": "With $n$ states, $m$ inputs and $p$ outputs, $Ax$ and $Bu$ must both be $n$-vectors so they can be added to give $\\dot x$, and $Cx$ is a $p$-vector."},
            {"title": "The pendulum in matrix form", "relation": "substitute",
             "tex": r"\begin{bmatrix}\dot\theta\\ \ddot\theta\end{bmatrix} = \begin{bmatrix}0&1\\1&0\end{bmatrix}\begin{bmatrix}\theta\\ \dot\theta\end{bmatrix} + \begin{bmatrix}0\\1\end{bmatrix}u",
             "explanation": "For the linearized, normalized inverted pendulum ($g/L = 1$, no damping), row times column gives $\\dot\\theta = \\dot\\theta$ (a bookkeeping row) and $\\ddot\\theta = \\theta + u$: gravity amplifies the tilt and the torque $u$ pushes back."},
        ],
    },
    # ------------------------------------------------------------------ section 5
    {
        "id": "close-loop",
        "scene": "CloseLoopSequence",
        "section": 5,
        "title": "Closing the loop: $A - BK$",
        "summary": "Substitute full-state feedback and factor the state out on the right.",
        "initial": {
            "title": "Controlled system, full state measured",
            "tex": r"\dot x = A\,x + B\,u, \qquad y = x",
            "explanation": "Assume every state is measured, $y = x$. A human balancing a broom has a good sense of both its angle and how fast it is moving, so this is a reasonable first model.",
        },
        "steps": [
            {"title": "Choose a feedback law", "relation": "define",
             "tex": r"u = -K\,x",
             "explanation": "Let the input be a fixed linear combination of the measured states: $u = -Kx$. Here $K$ is an $m \\times n$ gain matrix, so $Kx$ has the size of $u$."},
            {"title": "Substitute", "relation": "substitute",
             "tex": r"\dot x = A\,x + B\,(-K\,x)",
             "explanation": "Replace $u$ in the dynamics by $-Kx$. The input is no longer an outside signal: it is now determined by the state itself."},
            {"title": "Move the sign", "relation": "identity",
             "tex": r"\dot x = A\,x - B\,K\,x",
             "explanation": "$B(-Kx) = -BKx$. Keep the order $B$ then $K$: matrix products do not commute."},
            {"title": "Factor $x$ on the right", "relation": "identity",
             "tex": r"\dot x = (A - B\,K)\,x",
             "explanation": "Both terms end in $x$, so factor it out on the right: $Ax - BKx = (A - BK)x$. $BK$ is $n\\times m$ times $m\\times n$, an $n\\times n$ matrix like $A$. Writing $x(A - BK)$ or $A - KB$ would be wrong."},
            {"title": "The closed-loop matrix decides stability", "relation": "implies",
             "tex": r"A_{\text{cl}} = A - BK:\ \operatorname{Re}\lambda_i < 0\ \forall i \;\Rightarrow\; x(t) \to 0",
             "explanation": "The closed loop is again $\\dot x = A_{\\text{cl}}x$, so the eigenvalues of $A - BK$, not of $A$, decide stability. All real parts negative: asymptotically stable. Any positive real part: unstable. Eigenvalues on the imaginary axis need further analysis."},
        ],
    },
    # ------------------------------------------------------------------ section 6
    {
        "id": "pendulum-poles",
        "scene": "PendulumPolesSequence",
        "section": 6,
        "title": "Moving the pendulum's eigenvalues",
        "summary": "The book's example: $K = [4\\ \\ 4]$ moves the eigenvalues from $\\pm 1$ to $-1$ and $-3$.",
        "initial": {
            "title": "The normalized pendulum and a gain",
            "tex": r"A = \begin{bmatrix}0&1\\1&0\end{bmatrix},\ B = \begin{bmatrix}0\\1\end{bmatrix},\ K = \begin{bmatrix}4&4\end{bmatrix}",
            "explanation": "The linearized upright pendulum with $g/L = 1$ and no damping, a single torque input, and the gain from Brunton & Kutz (printed p. 328): $u = -4\\theta - 4\\dot\\theta$.",
        },
        "steps": [
            {"title": "Open-loop eigenvalues", "relation": "compute",
             "tex": r"\det(\lambda I - A) = \lambda^2 - 1 = 0 \;\Rightarrow\; \lambda = \pm 1",
             "explanation": "Without feedback the eigenvalues are $+1$ and $-1$: a saddle. The $+1$ in the right half-plane means almost every small tilt grows like $e^{t}$."},
            {"title": "Compute $BK$", "relation": "compute",
             "tex": r"BK = \begin{bmatrix}0\\1\end{bmatrix}\begin{bmatrix}4&4\end{bmatrix} = \begin{bmatrix}0&0\\4&4\end{bmatrix}",
             "explanation": "A column ($2\\times1$) times a row ($1\\times2$) is a $2\\times2$ matrix: entry $(i,j)$ is $B_i K_j$. Only the second row is non-zero because the torque acts only on $\\ddot\\theta$."},
            {"title": "Subtract: $A - BK$", "relation": "compute",
             "tex": r"A - BK = \begin{bmatrix}0-0&1-0\\1-4&0-4\end{bmatrix} = \begin{bmatrix}0&1\\-3&-4\end{bmatrix}",
             "explanation": "Subtract entry by entry. The closed loop reads $\\ddot\\theta = -3\\theta - 4\\dot\\theta$: a restoring spring and damping created by feedback."},
            {"title": "Characteristic polynomial", "relation": "compute",
             "tex": r"\det(\lambda I - A_{\text{cl}}) = \lambda(\lambda + 4) + 3 = \lambda^2 + 4\lambda + 3 = (\lambda + 1)(\lambda + 3)",
             "explanation": "For $\\lambda I - A_{\\text{cl}} = \\begin{bmatrix}\\lambda & -1\\\\ 3 & \\lambda + 4\\end{bmatrix}$ the determinant is $\\lambda(\\lambda+4) - (-1)(3)$. It factors with roots $-1$ and $-3$."},
            {"title": "The eigenvalues move", "relation": "compare",
             "tex": r"\{+1,\,-1\} \;\longrightarrow\; \{-1,\,-3\}",
             "explanation": "Both closed-loop eigenvalues are in the left half-plane, so the linearized closed loop is asymptotically stable: a small tilt now decays instead of growing. This holds for the small-angle model; large tilts need the nonlinear equations."},
            {"title": "Recap and what comes next", "relation": "recap",
             "tex": r"\dot x = Ax + Bu,\ \ u = -Kx \;\Rightarrow\; \dot x = (A - BK)\,x",
             "explanation": "Model, feedback law, closed-loop matrix, eigenvalues. Next in the bootcamp: when can $K$ place the eigenvalues anywhere (controllability), how to choose $K$ well (LQR), and what to do when only $y = Cx$ is measured (estimation, the Kalman filter)."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
