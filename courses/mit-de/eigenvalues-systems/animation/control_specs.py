"""Step-by-step content of the Unit 8 animations, Eigenvalues and Linear Systems (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-6). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 40-47 and Strang, Chapter 6.

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
        "id": "eig-check",
        "scene": "EigCheckSequence",
        "section": 1,
        "title": "Checking $Ax = \\lambda x$ for $A = \\begin{bmatrix}5&1\\\\3&3\\end{bmatrix}$",
        "summary": "Multiply out $A(1,1)$ and $A(1,-3)$ and see each output is a multiple of the input.",
        "initial": {"title": "The system", "tex": r"y_1' = 5y_1 + y_2,\quad y_2' = 3y_1 + 3y_2",
                    "explanation": "Try $y = e^{\\lambda t}x$."},
        "steps": [
            {"title": "First eigenvector", "relation": "compute",
             "tex": r"\begin{bmatrix}5&1\\3&3\end{bmatrix}\begin{bmatrix}1\\1\end{bmatrix} = \begin{bmatrix}6\\6\end{bmatrix} = 6\begin{bmatrix}1\\1\end{bmatrix}",
             "explanation": "Row times column: $5 + 1$ and $3 + 3$."},
            {"title": "Second eigenvector", "relation": "compute",
             "tex": r"\begin{bmatrix}5&1\\3&3\end{bmatrix}\begin{bmatrix}1\\-3\end{bmatrix} = \begin{bmatrix}2\\-6\end{bmatrix} = 2\begin{bmatrix}1\\-3\end{bmatrix}",
             "explanation": "$5 - 3 = 2$ and $3 - 9 = -6$."},
            {"title": "The solution", "relation": "implies",
             "tex": r"y(t) = c_1e^{6t}(1, 1) + c_2e^{2t}(1, -3)",
             "explanation": "Each eigenvector grows at its own rate."},
        ],
    },
    {
        "id": "diag-markov",
        "scene": "DiagMarkovSequence",
        "section": 2,
        "title": "$AV = V\\Lambda$ and the steady state of a Markov matrix",
        "summary": "Eigenvectors as columns diagonalize $A$; powers keep the $\\lambda = 1$ part and shrink the $\\lambda = \\tfrac12$ part.",
        "initial": {"title": "A Markov matrix", "tex": r"A = \begin{bmatrix}0.8 & 0.3\\ 0.2 & 0.7\end{bmatrix}",
                    "explanation": "Columns add to $1$."},
        "steps": [
            {"title": "Eigenvectors as columns", "relation": "identity",
             "tex": r"A\begin{bmatrix}0.6 & 1\\ 0.4 & -1\end{bmatrix} = \begin{bmatrix}0.6 & 1\\ 0.4 & -1\end{bmatrix}\begin{bmatrix}1 & 0\\ 0 & \tfrac12\end{bmatrix}",
             "explanation": "$AV = V\\Lambda$: each column is multiplied by its eigenvalue."},
            {"title": "Expand the start", "relation": "compute",
             "tex": r"u_0 = (1, 0) = (0.6, 0.4) + 0.4\,(1, -1)",
             "explanation": "$c = V^{-1}u_0$."},
            {"title": "Powers", "relation": "implies",
             "tex": r"u_k = (0.6, 0.4) + 0.4\left(\tfrac12\right)^k(1, -1) \to (0.6, 0.4)",
             "explanation": "The steady state is the $\\lambda = 1$ eigenvector."},
        ],
    },
    {
        "id": "solve-system",
        "scene": "SolveSystemSequence",
        "section": 3,
        "title": "Trajectories of $y' = Ay$ for $A = \\begin{bmatrix}-1&2\\\\1&-2\\end{bmatrix}$",
        "summary": "A line of steady states ($\\lambda = 0$) and decay along $(1, -1)$ ($\\lambda = -3$).",
        "initial": {"title": "Eigenvalues", "tex": r"T = -3,\ D = 0:\quad \lambda = 0,\ -3",
                    "explanation": "Columns add to $0$, so $0$ is an eigenvalue."},
        "steps": [
            {"title": "Eigenvector lines", "relation": "diagram",
             "tex": r"\lambda = 0:\ (2, 1),\qquad \lambda = -3:\ (1, -1)",
             "explanation": "Points on the first line do not move."},
            {"title": "Solutions", "relation": "solve",
             "tex": r"y(t) = c_1(2, 1) + c_2e^{-3t}(1, -1)",
             "explanation": "The second part decays; every trajectory is a straight segment parallel to $(1, -1)$."},
            {"title": "The steady state", "relation": "implies",
             "tex": r"y(t) \to c_1(2, 1)",
             "explanation": "Where it lands depends on $c_1$, fixed by $y(0)$."},
        ],
    },
    {
        "id": "expm-series",
        "scene": "ExpmSeriesSequence",
        "section": 4,
        "title": "The series for $e^{At}$ when $A^2 = 0$",
        "summary": "For $A = \\begin{bmatrix}0&1\\\\0&0\\end{bmatrix}$ the series stops after two terms: $e^{At} = I + At$.",
        "initial": {"title": "The series", "tex": r"e^{At} = I + At + \tfrac12(At)^2 + \tfrac16(At)^3 + \cdots",
                    "explanation": "Copied from the scalar exponential."},
        "steps": [
            {"title": "Square the matrix", "relation": "compute",
             "tex": r"A^2 = \begin{bmatrix}0&1\\0&0\end{bmatrix}\begin{bmatrix}0&1\\0&0\end{bmatrix} = 0",
             "explanation": "All higher powers vanish too."},
            {"title": "The series stops", "relation": "implies",
             "tex": r"e^{At} = I + At = \begin{bmatrix}1 & t\\ 0 & 1\end{bmatrix}",
             "explanation": "No exponential growth, only a factor $t$."},
            {"title": "Check: $y' = Ay$", "relation": "compare",
             "tex": r"y_2' = 0,\quad y_1' = y_2 \;\Rightarrow\; y = (y_1(0) + t\,y_2(0),\ y_2(0))",
             "explanation": "The defective matrix has one eigenvector $(1, 0)$; the factor $t$ replaces the missing one."},
        ],
    },
    {
        "id": "symmetric",
        "scene": "SymmetricSequence",
        "section": 5,
        "title": "Symmetric $S$: perpendicular eigenvectors",
        "summary": "$S = \\begin{bmatrix}3&1\\\\1&3\\end{bmatrix}$ stretches along $(1,1)$ by $4$ and along $(1,-1)$ by $2$; the unit circle becomes an ellipse with perpendicular axes.",
        "initial": {"title": "A symmetric matrix", "tex": r"S = S^T = \begin{bmatrix}3 & 1\\ 1 & 3\end{bmatrix}",
                    "explanation": "Real eigenvalues are guaranteed."},
        "steps": [
            {"title": "Eigenvalues", "relation": "compute",
             "tex": r"\lambda = 4:\ (1, 1),\qquad \lambda = 2:\ (1, -1)",
             "explanation": "Trace $6$, determinant $8$."},
            {"title": "The circle becomes an ellipse", "relation": "diagram",
             "tex": r"(1, 1)\cdot(1, -1) = 0",
             "explanation": "The ellipse's axes are the perpendicular eigenvectors, with half-lengths $4$ and $2$."},
            {"title": "Spectral form", "relation": "identity",
             "tex": r"S = Q\Lambda Q^T,\qquad Q = \tfrac{1}{\sqrt2}\begin{bmatrix}1 & 1\\ 1 & -1\end{bmatrix}",
             "explanation": "Rotate, stretch along the axes, rotate back."},
        ],
    },
    {
        "id": "modes",
        "scene": "ModesSequence",
        "section": 6,
        "title": "Two masses, two modes",
        "summary": "$K = \\begin{bmatrix}2&-1\\\\-1&2\\end{bmatrix}$: in-phase mode at $\\omega = 1$, out-of-phase mode at $\\omega = \\sqrt3$ (with $k/m = 1$).",
        "initial": {"title": "Newton's law", "tex": r"y'' + K y = 0,\qquad K = \begin{bmatrix}2 & -1\\ -1 & 2\end{bmatrix}",
                    "explanation": "Equal masses, three equal springs, ends fixed."},
        "steps": [
            {"title": "Eigenvalue problem", "relation": "substitute",
             "tex": r"y = \cos(\omega t)\,x \;\Rightarrow\; Kx = \omega^2x",
             "explanation": "Two derivatives of the cosine bring $-\\omega^2$."},
            {"title": "The modes", "relation": "compute",
             "tex": r"\omega^2 = 1:\ (1, 1),\qquad \omega^2 = 3:\ (1, -1)",
             "explanation": "Together (slow) or against each other (fast)."},
            {"title": "Pull one mass and let go", "relation": "solve",
             "tex": r"y(t) = \tfrac12\cos t\,(1, 1) + \tfrac12\cos\sqrt3t\,(1, -1)",
             "explanation": "$y(0) = (1, 0)$ splits equally between the two modes."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
