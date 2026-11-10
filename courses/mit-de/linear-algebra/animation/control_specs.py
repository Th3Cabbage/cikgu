"""Step-by-step content of the Unit 7 animations, Column Space, Basis and Graphs (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-5). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 35-39 and Strang, Sections 5.1 and 5.4-5.6.

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
        "id": "column-combination",
        "scene": "ColumnCombinationSequence",
        "section": 1,
        "title": "$Av$ is a combination of columns",
        "summary": "Split $Av$ into column pieces, spot column 3 = column 1 + column 2, and read off the null space and a particular solution.",
        "initial": {"title": "The lecture's matrix", "tex": r"A = \begin{bmatrix}1 & 1 & 2\\ 1 & 2 & 3\\ 1 & 2 & 3\end{bmatrix}",
                    "explanation": "Three columns in $\\mathbb{R}^3$."},
        "steps": [
            {"title": "Columns times weights", "relation": "identity",
             "tex": r"Av = v_1\begin{bmatrix}1\\1\\1\end{bmatrix} + v_2\begin{bmatrix}1\\2\\2\end{bmatrix} + v_3\begin{bmatrix}2\\3\\3\end{bmatrix}",
             "explanation": "Each $v_j$ multiplies column $j$."},
            {"title": "A dependent column", "relation": "compute",
             "tex": r"\text{col}_3 = \text{col}_1 + \text{col}_2 \;\Rightarrow\; A(-1, -1, 1) = 0",
             "explanation": "So $C(A)$ is only a plane and $N(A)$ is a line."},
            {"title": "Complete solution", "relation": "solve",
             "tex": r"Av = (3, 4, 4):\quad v = (2, 1, 0) + c(-1, -1, 1)",
             "explanation": "Two of column 1 plus one of column 2 reach $b$; add any null vector."},
        ],
    },
    {
        "id": "independence",
        "scene": "IndependenceSequence",
        "section": 2,
        "title": "Dependent or independent: $a_3$ in or out of the plane",
        "summary": "$a_3 = a_1 + a_2$ lies in the plane of $a_1, a_2$; replacing it by $(1, 0, 0)$ gives a basis of $\\mathbb{R}^3$.",
        "initial": {"title": "Two vectors", "tex": r"a_1 = (2, 1, 5),\quad a_2 = (4, 2, 0)",
                    "explanation": "They span a plane through the origin."},
        "steps": [
            {"title": "A third in the plane", "relation": "compute",
             "tex": r"a_3 = a_1 + a_2 = (6, 3, 5):\quad a_1 + a_2 - a_3 = 0",
             "explanation": "A nonzero combination gives zero: dependent."},
            {"title": "A third out of the plane", "relation": "classify",
             "tex": r"a_3 = (1, 0, 0):\quad Av = 0 \text{ only for } v = 0",
             "explanation": "Independent: the three columns form a basis."},
            {"title": "Dimension", "relation": "implies",
             "tex": r"\dim(\text{plane}) = 2,\qquad \dim \mathbb{R}^3 = 3",
             "explanation": "Every basis of a space has the same number of vectors."},
        ],
    },
    {
        "id": "four-subspaces",
        "scene": "FourSubspacesSequence",
        "section": 3,
        "title": "The big picture for $A = \\begin{bmatrix}1 & 2 & 3\\\\ 4 & 5 & 6\\end{bmatrix}$",
        "summary": "Row space and null space in $\\mathbb{R}^3$, column space and left null space in $\\mathbb{R}^2$, with dimensions $r, n - r, r, m - r$.",
        "initial": {"title": "A 2 by 3 matrix", "tex": r"A = \begin{bmatrix}1 & 2 & 3\\ 4 & 5 & 6\end{bmatrix},\quad r = 2",
                    "explanation": "$m = 2$ rows, $n = 3$ columns."},
        "steps": [
            {"title": "Null space", "relation": "compute",
             "tex": r"A(1, -2, 1) = (1 - 4 + 3,\ 4 - 10 + 6) = (0, 0)",
             "explanation": "A line in $\\mathbb{R}^3$, dimension $n - r = 1$."},
            {"title": "Perpendicular to the rows", "relation": "implies",
             "tex": r"N(A) \perp C(A^T)",
             "explanation": "Each row has dot product zero with $(1, -2, 1)$."},
            {"title": "The four dimensions", "relation": "recap",
             "tex": r"\dim C(A^T) = 2,\ \dim N(A) = 1,\ \dim C(A) = 2,\ \dim N(A^T) = 0",
             "explanation": "In general $r$, $n - r$, $r$, $m - r$."},
        ],
    },
    {
        "id": "incidence",
        "scene": "IncidenceSequence",
        "section": 4,
        "title": "Building the incidence matrix edge by edge",
        "summary": "Each edge gives a row with $-1$ at its start and $+1$ at its end; $Av$ takes potential differences.",
        "initial": {"title": "Four nodes, five edges", "tex": r"1\to2,\ 1\to3,\ 2\to3,\ 1\to4,\ 2\to4",
                    "explanation": "Directed edges; the arrows fix the signs."},
        "steps": [
            {"title": "Rows of $A$", "relation": "define",
             "tex": r"A = \begin{bmatrix}-1&1&0&0\\-1&0&1&0\\0&-1&1&0\\-1&0&0&1\\0&-1&0&1\end{bmatrix}",
             "explanation": "Row $k$ = edge $k$."},
            {"title": "Potential differences", "relation": "compute",
             "tex": r"(Av)_1 = v_2 - v_1,\ \ (Av)_2 = v_3 - v_1,\ \ldots",
             "explanation": "Each entry of $Av$ is a difference across an edge."},
            {"title": "Constant potentials", "relation": "implies",
             "tex": r"A(1, 1, 1, 1) = 0 \;\Rightarrow\; \operatorname{rank} A = 3",
             "explanation": "Equal potentials give no differences: the null space is the constants."},
        ],
    },
    {
        "id": "loops",
        "scene": "LoopsSequence",
        "section": 5,
        "title": "Loop currents solve $A^Tw = 0$",
        "summary": "A current around a loop balances at every node; independent loops number $m - n + 1$.",
        "initial": {"title": "Kirchhoff's current law", "tex": r"A^T w = 0",
                    "explanation": "Net current into each node is zero."},
        "steps": [
            {"title": "A loop current", "relation": "define",
             "tex": r"1\to2\to4\to1:\quad w = (1, 0, 0, -1, 1)",
             "explanation": "Edge $4$ ($1\\to4$) is travelled backwards, so $w_4 = -1$."},
            {"title": "Check each node", "relation": "compare",
             "tex": r"\text{node 1: } -w_1 - w_2 - w_4 = -1 - 0 + 1 = 0",
             "explanation": "The same balance holds at nodes $2$, $3$, $4$."},
            {"title": "Count the loops", "relation": "compute",
             "tex": r"\dim N(A^T) = m - r = 5 - 3 = 2 = m - n + 1",
             "explanation": "The loop $1\\to3\\to2\\to4\\to1$ is the difference of the two small loop vectors: the shared edge cancels."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
