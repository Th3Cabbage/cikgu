"""Step-by-step content of the Controllability animations (pure data, standard library only).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. The scene calls `self.step_done()` once per step and
build_sequences.py checks that the recorded boundaries match len(steps).

Strings use $...$ for inline math (KaTeX in the browser). `tex` is the display formula of the
state a step reaches (shown on the step card and as the media fallback). `section` is the course
section (1-6). Explanations are original paraphrases of S. L. Brunton's Control Bootcamp lecture
"Controllability" and Brunton & Kutz Section 8.3 (Eqs. 8.26-8.31); the c = 0.1 example is authored.

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

UNC = r"\begin{bmatrix}1&0\\0&2\end{bmatrix}"
CPL = r"\begin{bmatrix}1&1\\0&2\end{bmatrix}"
B01 = r"\begin{bmatrix}0\\1\end{bmatrix}"

SEQUENCES = [
    {
        "id": "input-sizes",
        "scene": "InputSizesSequence",
        "section": 1,
        "title": "Adding the input $Bu$",
        "summary": "The input term joins the dynamics, and its shapes are forced: $B$ must be $n \\times q$ so that $Bu$ is an $n$-vector like $Ax$.",
        "initial": {"title": "Where we were", "tex": r"\dot x = Ax",
                    "explanation": "The previous lectures studied $\\dot x = Ax$: the eigenvalues of $A$ alone decide whether the state decays or grows."},
        "steps": [
            {"title": "Add a control term", "relation": "model", "tex": r"\dot x = Ax + Bu",
             "explanation": "A forcing term $Bu$ is added. $u$ is the signal we choose; $B$ says how it enters each state equation."},
            {"title": "Shapes of every factor", "relation": "define",
             "tex": r"\underbrace{A}_{n\times n}\underbrace{x}_{n\times 1} + \underbrace{B}_{n\times q}\underbrace{u}_{q\times 1}",
             "explanation": "$x \\in \\mathbb{R}^n$ and $u \\in \\mathbb{R}^q$ ($q$ actuators). For $Bu$ to be an $n \\times 1$ column like $Ax$, $B$ must be $n$ tall and $q$ wide: one column per actuator."},
            {"title": "Assume the full state is measured", "relation": "caution", "tex": r"y = Cx,\quad C = I \;\Rightarrow\; y = x",
             "explanation": "Measurements $y = Cx$ come later. In this lecture $C = I$: every state is available for feedback. (This $C$ is not the controllability matrix $\\mathcal{C}$.)"},
        ],
    },
    {
        "id": "feedback-substitution",
        "scene": "FeedbackSequence",
        "section": 2,
        "title": "Substituting $u = -Kx$",
        "summary": "Proportional state feedback turns $\\dot x = Ax + Bu$ into $\\dot x = (A - BK)x$; controllability is about how freely $K$ can move its eigenvalues.",
        "initial": {"title": "System and feedback law", "tex": r"\dot x = Ax + Bu,\qquad u = -Kx",
                    "explanation": "With the whole state measured, the lecture uses the linear law $u = -Kx$, where $K$ is a $q \\times n$ gain matrix."},
        "steps": [
            {"title": "Put $-Kx$ in place of $u$", "relation": "substitute", "tex": r"\dot x = Ax + B(-Kx)",
             "explanation": "The input $u$ is replaced by the feedback $-Kx$. $B$ still acts on it from the left."},
            {"title": "Pull out the minus sign", "relation": "identity", "tex": r"\dot x = Ax - BKx",
             "explanation": "$B(-Kx) = -BKx$. $BK$ is $(n\\times q)(q\\times n) = n \\times n$, the same shape as $A$."},
            {"title": "Factor $x$ on the right", "relation": "identity", "tex": r"\dot x = (A - BK)\,x",
             "explanation": "Both terms end in $x$, so $x$ factors out on the right. The closed loop is again $\\dot x = (\\text{matrix})x$ with the new matrix $A - BK$."},
            {"title": "What controllability promises", "relation": "equivalent",
             "tex": r"(A,B)\ \text{controllable} \Leftrightarrow \text{eig}(A-BK)\ \text{assignable} \Leftrightarrow \text{every state reachable}",
             "explanation": "If $(A, B)$ is controllable, a suitable $K$ places the eigenvalues of $A - BK$ anywhere (as conjugate pairs for real matrices), and some input steers $x$ to any point in finite time. Only $A$ and $B$ decide this."},
        ],
    },
    {
        "id": "three-examples",
        "scene": "ThreeExamplesSequence",
        "section": 3,
        "title": "Blocked, more actuators, coupled",
        "summary": "Writing the examples row by row shows when the input can reach every state: never for $x_1$ in the uncoupled case, directly with two actuators, and indirectly through coupling.",
        "initial": {"title": "Uncoupled dynamics, one input", "tex": r"\dot x = " + UNC + r"x + " + B01 + r"u",
                    "explanation": "The lecture's first example: diagonal $A$ with eigenvalues $1$ and $2$ (both unstable) and a single actuator $B = [0, 1]^T$."},
        "steps": [
            {"title": "Expand row by row", "relation": "identity", "tex": r"\dot x_1 = x_1,\qquad \dot x_2 = 2x_2 + u",
             "explanation": "Row 1: $1\\cdot x_1 + 0\\cdot x_2 + 0\\cdot u = x_1$. Row 2: $0\\cdot x_1 + 2x_2 + 1\\cdot u$."},
            {"title": "$x_1$ is out of reach", "relation": "implies", "tex": r"\dot x_1 = x_1 \;\Rightarrow\; \text{uncontrollable}",
             "explanation": "The $x_1$ equation contains neither $u$ nor $x_2$, so no input affects $x_1$: it grows like $e^t$ regardless. The pair is uncontrollable."},
            {"title": "Fix 1: a second actuator", "relation": "compare", "tex": r"B = I:\quad \dot x_1 = x_1 + u_1,\quad \dot x_2 = 2x_2 + u_2",
             "explanation": "With $B = I$ each state has its own input, so both can be stabilised independently: controllable. Every column of $B$ is another actuator."},
            {"title": "Fix 2: coupling, one actuator", "relation": "compare", "tex": r"A = " + CPL + r":\quad \dot x_1 = x_1 + x_2,\quad \dot x_2 = 2x_2 + u",
             "explanation": "Back to one input $B = [0, 1]^T$, but now $x_2$ drives $x_1$. The input reaches $x_1$ through $x_2$, and the pair is controllable (proved by the rank test later)."},
        ],
    },
    {
        "id": "controllability-matrix",
        "scene": "ControllabilityMatrixSequence",
        "section": 4,
        "title": "The controllability matrix and its rank",
        "summary": "Repeatedly multiplying $B$ by $A$ produces the blocks of $\\mathcal{C}$; controllability is the statement that these columns span $\\mathbb{R}^n$.",
        "initial": {"title": "Start from the input direction", "tex": r"B", "explanation": "Everything is built from $B$, the directions the actuators push, and $A$, which moves those directions around."},
        "steps": [
            {"title": "Multiply by $A$, again and again", "relation": "define",
             "tex": r"\mathcal{C} = \begin{bmatrix} B & AB & A^2B & \cdots & A^{n-1}B \end{bmatrix}",
             "explanation": "Each block is $A$ times the previous one, with $A$ on the left. The list stops at $A^{n-1}B$: $n$ blocks."},
            {"title": "Size of $\\mathcal{C}$", "relation": "define", "tex": r"\mathcal{C} \in \mathbb{R}^{n \times nq}",
             "explanation": "Every block has the shape of $B$, $n \\times q$. Side by side, $n$ blocks make $n \\times nq$; square only for a single input."},
            {"title": "The rank test", "relation": "equivalent", "tex": r"\text{controllable} \Leftrightarrow \mathrm{rank}\,\mathcal{C} = n",
             "explanation": "Controllable exactly when $\\mathcal{C}$ has $n$ independent columns, so its columns span $\\mathbb{R}^n$: full ROW rank. (The lecture says \u201cfull column rank\u201d; that matches only for one input.)"},
            {"title": "Why: kick and let it ring (discrete time)", "relation": "diagram",
             "tex": r"x_1 = Bu_0,\quad x_2 = ABu_0 + Bu_1,\quad x_3 = A^2Bu_0 + ABu_1 + Bu_2",
             "explanation": "Authored illustration with $x_{k+1} = Ax_k + Bu_k$, $x_0 = 0$: each step passes earlier kicks through $A$ once more. Reachable states are combinations of the columns of $\\mathcal{C}$."},
        ],
    },
    {
        "id": "compare-ranks",
        "scene": "CompareRanksSequence",
        "section": 5,
        "title": "Computing $\\mathcal{C}$: rank 1 versus rank 2",
        "summary": "Multiplying $A$ into $B$ entry by entry for both examples: the uncoupled columns stay on the $x_2$ axis (rank 1), the coupled ones span the plane (rank 2).",
        "initial": {"title": "Uncoupled pair", "tex": r"A = " + UNC + r",\quad B = " + B01,
                    "explanation": "The lecture's first example, now tested with $\\mathcal{C} = [B\\ \\ AB]$ since $n = 2$."},
        "steps": [
            {"title": "Multiply $A$ into $B$", "relation": "compute",
             "tex": UNC + B01 + r" = \begin{bmatrix}1\cdot0 + 0\cdot1\\0\cdot0 + 2\cdot1\end{bmatrix} = \begin{bmatrix}0\\2\end{bmatrix}",
             "explanation": "Row times column: top $1\\cdot0 + 0\\cdot1 = 0$, bottom $0\\cdot0 + 2\\cdot1 = 2$. So $AB = [0, 2]^T$."},
            {"title": "Assemble and look at the columns", "relation": "compute", "tex": r"\mathcal{C} = \begin{bmatrix}0&0\\1&2\end{bmatrix}",
             "explanation": "$B$ and $AB$ both lie on the $x_2$ axis; $AB = 2B$."},
            {"title": "Determinant 0, rank 1", "relation": "implies",
             "tex": r"\det\mathcal{C} = 0\cdot2 - 0\cdot1 = 0 \;\Rightarrow\; \mathrm{rank}\,\mathcal{C} = 1,\quad A^2B = \begin{bmatrix}0\\4\end{bmatrix}",
             "explanation": "Rank 1 < 2: uncontrollable. More powers do not help: $A^2B = [0, 4]^T$, $[0, 8]^T$, ... keep a zero on top."},
            {"title": "Coupled $A$, same $B$", "relation": "compute",
             "tex": CPL + B01 + r" = \begin{bmatrix}1\cdot0 + 1\cdot1\\0\cdot0 + 2\cdot1\end{bmatrix} = \begin{bmatrix}1\\2\end{bmatrix}",
             "explanation": "The coupling entry contributes $1 \\cdot 1$ to the top row, so $AB = [1, 2]^T$ now has an $x_1$ component."},
            {"title": "Determinant $-1$, rank 2", "relation": "compare",
             "tex": r"\mathcal{C} = \begin{bmatrix}0&1\\1&2\end{bmatrix},\quad \det\mathcal{C} = 0\cdot2 - 1\cdot1 = -1 \neq 0",
             "explanation": "Two independent columns span the plane: rank 2, controllable."},
        ],
    },
    {
        "id": "ctrb-limits",
        "scene": "CtrbLimitsSequence",
        "section": 6,
        "title": "ctrb in MATLAB and the limits of a yes/no test",
        "summary": "The computer reproduces the board, but the rank test is binary and linear: degree of controllability and nonlinear effects need more.",
        "initial": {"title": "The command", "tex": r"\texttt{rank(ctrb(A,B))}", "explanation": "ctrb builds $\\mathcal{C}$; rank tests it. Useful when the system is too big to check by hand."},
        "steps": [
            {"title": "The two examples on the computer", "relation": "compute",
             "tex": r"\texttt{A=[1 0;0 2]} \to 1,\qquad \texttt{A=[1 1;0 2]} \to 2",
             "explanation": "With B = [0; 1], the uncoupled A gives rank 1 (not controllable) and the coupled A gives rank 2 (controllable), matching the board."},
            {"title": "Linearizations only", "relation": "caution", "tex": r"\text{linearization uncontrollable} \;\not\Rightarrow\; \text{nonlinear system uncontrollable}",
             "explanation": "Neglected nonlinear terms may still give control authority, or not; nonlinear controllability is hard in general."},
            {"title": "Yes/no hides the degree", "relation": "caution",
             "tex": r"c = 0.1:\ \mathcal{C} = \begin{bmatrix}0&0.1\\1&2\end{bmatrix},\ \sigma \approx (2.24,\ 0.045);\quad c = 1:\ \sigma \approx (2.41,\ 0.41)",
             "explanation": "Authored comparison: both have rank 2, but a weak coupling leaves one direction barely actuated. The SVD of $\\mathcal{C}$ previews this; exact energy measures need the Gramian (later)."},
            {"title": "What comes next", "relation": "recap", "tex": r"\text{why }\mathcal{C}\text{ works}\;\to\;\text{degree of controllability}\;\to\;\text{design } u = -Kx",
             "explanation": "Following lectures justify the matrix, measure how controllable a system is, and finally design the feedback gain."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
