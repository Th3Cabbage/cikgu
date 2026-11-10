"""Step-by-step content of the Unit 9 animations, Positive Definite Matrices and the SVD (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-3). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 48-49 and Strang, Section 7.2.

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
        "id": "ata-nonnegative",
        "scene": "AtANonnegativeSequence",
        "section": 1,
        "title": "Why $A^TA$ has no negative eigenvalues",
        "summary": "Multiply $A^TAx = \\lambda x$ by $x^T$ and recognise a squared length.",
        "initial": {"title": "An eigenvector of $A^TA$", "tex": r"A^TA\,x = \lambda x",
                    "explanation": "$A$ can be any rectangular matrix."},
        "steps": [
            {"title": "Multiply by $x^T$", "relation": "substitute",
             "tex": r"x^TA^TAx = \lambda\,x^Tx",
             "explanation": "Both sides become numbers."},
            {"title": "A squared length", "relation": "identity",
             "tex": r"x^TA^TAx = (Ax)^T(Ax) = \|Ax\|^2",
             "explanation": "Group the factors in pairs."},
            {"title": "The sign of $\\lambda$", "relation": "implies",
             "tex": r"\lambda = \frac{\|Ax\|^2}{\|x\|^2} \ge 0",
             "explanation": "Strictly positive when $Ax \\neq 0$, that is, when $A$ has independent columns."},
        ],
    },
    {
        "id": "five-tests",
        "scene": "FiveTestsSequence",
        "section": 2,
        "title": "Pivots, determinants and energy for $\\begin{bmatrix}4&6\\\\6&10\\end{bmatrix}$",
        "summary": "Elimination gives pivots $4, 1$; completing the square shows the same pivots in the energy.",
        "initial": {"title": "The matrix", "tex": r"S = \begin{bmatrix}4 & 6\\ 6 & 10\end{bmatrix}",
                    "explanation": "Symmetric. Is it positive definite?"},
        "steps": [
            {"title": "Elimination", "relation": "compute",
             "tex": r"\text{row}_2 - \tfrac32\,\text{row}_1:\quad \begin{bmatrix}4 & 6\\ 0 & 1\end{bmatrix},\ \text{pivots } 4,\ 1",
             "explanation": "Both pivots positive."},
            {"title": "Upper-left determinants", "relation": "compute",
             "tex": r"\det[4] = 4,\qquad \det S = 40 - 36 = 4",
             "explanation": "The second determinant is the product of the pivots."},
            {"title": "Energy", "relation": "identity",
             "tex": r"x^TSx = 4x_1^2 + 12x_1x_2 + 10x_2^2 = 4\left(x_1 + \tfrac32x_2\right)^2 + 1\cdot x_2^2",
             "explanation": "Completing the square puts the pivots in front of the squares: positive for $x \\neq 0$."},
        ],
    },
    {
        "id": "energy-bowl",
        "scene": "EnergyBowlSequence",
        "section": 2,
        "title": "Level curves: ellipses for a bowl, hyperbolas for a saddle",
        "summary": "Positive definite energy has elliptic level curves around a minimum; an indefinite matrix gives hyperbolas.",
        "initial": {"title": "Energy levels", "tex": r"x^TSx = c",
                    "explanation": "Draw the curves of equal energy."},
        "steps": [
            {"title": "Positive definite", "relation": "diagram",
             "tex": r"4x_1^2 + 12x_1x_2 + 10x_2^2 = c:\ \text{ellipses}",
             "explanation": "Tilted ellipses, axes along the eigenvectors; the minimum is at $0$."},
            {"title": "Indefinite", "relation": "diagram",
             "tex": r"3x_1^2 + 8x_1x_2 + 5x_2^2 = c:\ \text{hyperbolas}",
             "explanation": "Determinant $-1$: the energy is negative in some directions."},
            {"title": "The test", "relation": "classify",
             "tex": r"\text{bowl} \Leftrightarrow \lambda_1, \lambda_2 > 0 \Leftrightarrow \text{pivots} > 0",
             "explanation": "A negative eigenvalue tilts the bowl into a saddle."},
        ],
    },
    {
        "id": "svd-geometry",
        "scene": "SVDGeometrySequence",
        "section": 3,
        "title": "Turn, stretch, turn: the unit circle under $U\\Sigma V^T$",
        "summary": "For $A = \\begin{bmatrix}3&0\\\\4&5\\end{bmatrix}$: $V^T$ turns $v_1, v_2$ to the axes, $\\Sigma$ stretches by $3\\sqrt5, \\sqrt5$, $U$ turns the ellipse into place.",
        "initial": {"title": "Unit circle", "tex": r"\|x\| = 1,\quad v_1 = \tfrac{1}{\sqrt2}(1, 1),\ v_2 = \tfrac{1}{\sqrt2}(1, -1)",
                    "explanation": "The right singular vectors are marked."},
        "steps": [
            {"title": "Turn by $V^T$", "relation": "compute",
             "tex": r"V^Tv_1 = e_1,\qquad V^Tv_2 = e_2",
             "explanation": "The circle is unchanged; the marked vectors move to the axes."},
            {"title": "Stretch by $\\Sigma$", "relation": "compute",
             "tex": r"\Sigma = \begin{bmatrix}3\sqrt5 & 0\\ 0 & \sqrt5\end{bmatrix}",
             "explanation": "The circle becomes an ellipse with half-axes $\\sigma_1$, $\\sigma_2$."},
            {"title": "Turn by $U$", "relation": "compute",
             "tex": r"Av_i = \sigma_iu_i:\quad u_1 = \tfrac{1}{\sqrt{10}}(1, 3),\ u_2 = \tfrac{1}{\sqrt{10}}(3, -1)",
             "explanation": "The final ellipse is $A$ applied to the circle. Here both orthogonal factors are rotations; in general either may be a reflection."},
        ],
    },
    {
        "id": "svd-example",
        "scene": "SVDExampleSequence",
        "section": 3,
        "title": "The SVD of the singular matrix $\\begin{bmatrix}2&2\\\\1&1\\end{bmatrix}$",
        "summary": "$A^TA$ gives $\\sigma = \\sqrt{10}, 0$ and $V$; $u_1 = Av_1/\\sigma_1$; one rank-one piece rebuilds $A$.",
        "initial": {"title": "A rank-one matrix", "tex": r"A = \begin{bmatrix}2 & 2\\ 1 & 1\end{bmatrix}",
                    "explanation": "The second row is half the first."},
        "steps": [
            {"title": "$A^TA$", "relation": "compute",
             "tex": r"A^TA = \begin{bmatrix}5 & 5\\ 5 & 5\end{bmatrix}:\ \sigma_1^2 = 10,\ \sigma_2^2 = 0",
             "explanation": "Eigenvectors $(1, 1)/\\sqrt2$ and $(1, -1)/\\sqrt2$."},
            {"title": "Left singular vector", "relation": "compute",
             "tex": r"u_1 = \frac{Av_1}{\sigma_1} = \frac{(4, 2)/\sqrt2}{\sqrt{10}} = \frac{(2, 1)}{\sqrt5}",
             "explanation": "The board shows $-1$ in $U$ from an earlier version; for this $A$, $u_1 = (2, 1)/\\sqrt5$."},
            {"title": "One piece is enough", "relation": "identity",
             "tex": r"A = \sigma_1u_1v_1^T = \sqrt{10}\,\frac{(2, 1)}{\sqrt5}\,\frac{(1, 1)^T}{\sqrt2}",
             "explanation": "$\\sigma_2 = 0$, so the second piece is zero."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
