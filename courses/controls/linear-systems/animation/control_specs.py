"""Step-by-step content of the Linear Systems animations (pure data, standard library only).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. The scene calls `self.step_done()` once per step and
build_sequences.py checks that the recorded boundaries match len(steps).

Strings use $...$ for inline math (KaTeX in the browser). `tex` is the display formula of the
state a step reaches; the browser shows it on the step card and as the media fallback, so it
must say the same thing as the stage. `section` is the course section (1-6) a sequence belongs to.

All explanations are original paraphrases written for this guide; they summarize S. L. Brunton's
Control Bootcamp lecture "Linear Systems" and Section 8.2 of Brunton & Kutz, "Data-Driven Science
and Engineering" (2017 preprint, Eqs. 8.11-8.19), without quoting them. The numerical example
(T = [[1, 1], [0, 1]], D = diag(-1, -2), x(0) = [2, 1]) is authored for this guide, not taken
from the lecture.

The module name is kept from the shared scaffold (ctl_common.py imports it).
"""

RELATIONS = {
    "define": "Definition / choice",
    "model": "Modelling step",
    "classify": "Classification",
    "diagram": "Picture",
    "substitute": "Substitution",
    "identity": "Identity (=)",
    "equivalent": "Equivalent equation (⇔)",
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
        "id": "matrix-exponential",
        "scene": "MatrixExponentialSequence",
        "section": 1,
        "title": "From $\\dot x = Ax$ to the matrix exponential",
        "summary": "The solution of a linear system is a matrix exponential applied to the initial state, and the exponential of a matrix is defined by the same Taylor series as for a number.",
        "initial": {
            "title": "A linear system of ODEs",
            "tex": r"\dot x = A x",
            "explanation": "The whole lecture is about this one equation: the rate of change of the state is a fixed matrix times the state. It is the cornerstone for everything later in the bootcamp.",
        },
        "steps": [
            {"title": "Sizes: a vector and a square matrix", "relation": "define",
             "tex": r"\dot x = A x, \qquad x \in \mathbb{R}^n,\quad A \in \mathbb{R}^{n\times n}",
             "explanation": "$x$ stacks $n$ state variables in a column. $A$ is $n \\times n$: entry $a_{ij}$ says how much variable $j$ pushes on the rate of change of variable $i$."},
            {"title": "The solution: a matrix exponential", "relation": "solve",
             "tex": r"x(t) = e^{At}\,x(0)",
             "explanation": "The state at time $t$ is the matrix $e^{At}$ times the initial state $x(0)$. Order matters: a matrix acting on a column vector, so $e^{At}$ is on the left."},
            {"title": "Recall the scalar Taylor series", "relation": "identity",
             "tex": r"e^{at} = 1 + at + \frac{a^2t^2}{2!} + \frac{a^3t^3}{3!} + \cdots",
             "explanation": "For a number $a$ the exponential is an infinite sum of powers. Only products and sums appear, and those also make sense for square matrices."},
            {"title": "Plug in the matrix $At$", "relation": "substitute",
             "tex": r"e^{At} = I + At + \frac{A^2t^2}{2!} + \frac{A^3t^3}{3!} + \cdots",
             "explanation": "Replace $a$ by $A$. The $1$ becomes the identity matrix $I$ and every term is an $n\\times n$ matrix, so $e^{At}$ is an infinite sum of matrices. At $t = 0$ only $I$ survives, so $x(0) = I\\,x(0)$ as it must."},
            {"title": "Not the exponential of each entry", "relation": "caution",
             "tex": r"e^{At} \neq \begin{bmatrix} e^{a_{11}t} & e^{a_{12}t} \\ e^{a_{21}t} & e^{a_{22}t} \end{bmatrix}",
             "explanation": "Powers $A^2, A^3, \\dots$ mix the entries, so the matrix exponential is not computed entry by entry (an off-diagonal $0$ in $A$ would wrongly give $e^0 = 1$). Summing the series by hand is impractical for a $5 \\times 5$ matrix, which motivates the eigenvector route."},
        ],
    },
    # ------------------------------------------------------------------ section 2
    {
        "id": "eigen-at-td",
        "scene": "EigenSequence",
        "section": 2,
        "title": "Eigenvectors, eigenvalues and $AT = TD$",
        "summary": "Eigenvectors are the directions that $A$ only stretches. Collecting them as the columns of $T$ and the eigenvalues on the diagonal of $D$ gives $AT = TD$.",
        "initial": {
            "title": "The eigenvalue equation",
            "tex": r"A c = \lambda c, \qquad c \neq 0",
            "explanation": "A nonzero vector $c$ is an eigenvector of $A$ if multiplying by $A$ only rescales it by the number $\\lambda$, its eigenvalue."},
        "steps": [
            {"title": "Most vectors turn, eigenvectors do not", "relation": "diagram",
             "tex": r"A = \begin{bmatrix} -1 & -1 \\ 0 & -2 \end{bmatrix}:\quad A c_1 = -1\,c_1,\quad A c_2 = -2\,c_2",
             "explanation": "For this example matrix a generic vector $v$ comes out pointing in a new direction. $c_1 = (1, 0)$ and $c_2 = (1, 1)$ stay on their own lines; a negative $\\lambda$ flips them to the opposite side and rescales."},
            {"title": "Collect eigenvectors and eigenvalues", "relation": "define",
             "tex": r"T = \begin{bmatrix} c_1 & c_2 & \cdots & c_n \end{bmatrix}, \qquad D = \begin{bmatrix} \lambda_1 & 0 & 0 \\ 0 & \ddots & 0 \\ 0 & 0 & \lambda_n \end{bmatrix}",
             "explanation": "$T$ has the eigenvectors as columns. $D$ is diagonal with the matching eigenvalues in the same order and zeros everywhere else."},
            {"title": "$A$ acts on each column of $T$", "relation": "compute",
             "tex": r"AT = \begin{bmatrix} Ac_1 & Ac_2 & \cdots & Ac_n \end{bmatrix} = \begin{bmatrix} \lambda_1 c_1 & \lambda_2 c_2 & \cdots & \lambda_n c_n \end{bmatrix}",
             "explanation": "A matrix times $T$ multiplies each column of $T$ separately. Each column is an eigenvector, so column $i$ becomes $\\lambda_i c_i$."},
            {"title": "Right-multiplying by $D$ scales columns", "relation": "identity",
             "tex": r"TD = \begin{bmatrix} \lambda_1 c_1 & \lambda_2 c_2 & \cdots & \lambda_n c_n \end{bmatrix} \;\Rightarrow\; AT = TD",
             "explanation": "Multiplying $T$ on the right by a diagonal matrix scales column $i$ by $\\lambda_i$. That is exactly the previous result, so $AT = TD$. Note the order: $DT$ would scale rows instead."},
            {"title": "When does this work?", "relation": "caution",
             "tex": r"\text{need } n \text{ independent eigenvectors: } \det T \neq 0",
             "explanation": "Distinct eigenvalues are enough but not required: $A = 2I$ has a repeated eigenvalue and is still diagonal. A defective matrix such as $\\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}$ has only one eigenvector direction; it needs generalized eigenvectors and a Jordan form, which the lecture only mentions."},
        ],
    },
    # ------------------------------------------------------------------ section 3
    {
        "id": "change-coordinates",
        "scene": "CoordinatesSequence",
        "section": 3,
        "title": "Eigenvector coordinates: $x = Tz$ gives $\\dot z = Dz$",
        "summary": "Describe the state by how much of each eigenvector it contains. In those coordinates the dynamics matrix becomes the diagonal $D$.",
        "initial": {
            "title": "A change of coordinates",
            "tex": r"x = T z",
            "explanation": "$z$ lists how much of each eigenvector (each column of $T$) is needed to build $x$. With the example $T$, the point $x = (2, 1)$ is $1\\cdot c_1 + 1\\cdot c_2$."},
        "steps": [
            {"title": "New axes along the eigenvectors", "relation": "diagram",
             "tex": r"x = z_1 c_1 + z_2 c_2, \qquad \begin{bmatrix}2\\1\end{bmatrix} = 1\begin{bmatrix}1\\0\end{bmatrix} + 1\begin{bmatrix}1\\1\end{bmatrix}",
             "explanation": "The grid of $z$ coordinates is the standard grid sheared by $T$: its lines run along $c_1$ and $c_2$. The axes are not perpendicular, which is fine as long as they are independent."},
            {"title": "Going back: $z = T^{-1}x$", "relation": "implies",
             "tex": r"z = T^{-1}x, \qquad T^{-1} = \begin{bmatrix} 1 & -1 \\ 0 & 1 \end{bmatrix} \neq T^{\top} = \begin{bmatrix} 1 & 0 \\ 1 & 1 \end{bmatrix}",
             "explanation": "Independent eigenvectors make $T$ invertible. Use the inverse, not the transpose: they agree only when the eigenvectors are orthonormal, which this example's are not."},
            {"title": "Differentiate: $T$ is constant", "relation": "identity",
             "tex": r"x = Tz \;\Rightarrow\; \dot x = T\dot z",
             "explanation": "$T$ does not change with time, so the derivative passes straight through it."},
            {"title": "Substitute into $\\dot x = Ax$", "relation": "substitute",
             "tex": r"T\dot z = A x = A T z",
             "explanation": "Replace $\\dot x$ by $T\\dot z$ on the left and $x$ by $Tz$ on the right. $T$ stays to the right of $A$."},
            {"title": "Multiply by $T^{-1}$ on the left", "relation": "equivalent",
             "tex": r"\dot z = T^{-1} A T\, z",
             "explanation": "Multiply both sides on the left by $T^{-1}$; on the left side $T^{-1}T = I$. Multiplying on the right instead would not make sense for the vector $\\dot z$."},
            {"title": "The dynamics are diagonal", "relation": "identity",
             "tex": r"T^{-1}AT = D \;\Rightarrow\; \dot z = D z",
             "explanation": "From $AT = TD$, multiplying on the left by $T^{-1}$ gives $T^{-1}AT = D$. In eigenvector coordinates the system is $\\dot z = Dz$: the boxed result of the lecture."},
        ],
    },
    # ------------------------------------------------------------------ section 4
    {
        "id": "decoupled",
        "scene": "DecoupledSequence",
        "section": 4,
        "title": "Decoupled modes and $e^{Dt}$",
        "summary": "A diagonal system splits into $n$ separate scalar equations, each solved by one exponential. Stacked, they form $e^{Dt}$.",
        "initial": {
            "title": "The diagonal system",
            "tex": r"\dot z = D z",
            "explanation": "This is the equation from the previous section. Writing it out shows why diagonal is so convenient."},
        "steps": [
            {"title": "Write it out", "relation": "identity",
             "tex": r"\frac{d}{dt}\begin{bmatrix} z_1 \\ z_2 \\ \vdots \\ z_n \end{bmatrix} = \begin{bmatrix} \lambda_1 & 0 & 0 & 0 \\ 0 & \lambda_2 & 0 & 0 \\ 0 & 0 & \ddots & 0 \\ 0 & 0 & 0 & \lambda_n \end{bmatrix} \begin{bmatrix} z_1 \\ z_2 \\ \vdots \\ z_n \end{bmatrix}",
             "explanation": "All off-diagonal entries of $D$ are zero. Read row by row: row $i$ of $D$ has one nonzero entry, $\\lambda_i$, in column $i$."},
            {"title": "Each row involves one variable", "relation": "implies",
             "tex": r"\dot z_1 = \lambda_1 z_1,\quad \dot z_2 = \lambda_2 z_2,\quad \ldots,\quad \dot z_n = \lambda_n z_n",
             "explanation": "The equations are decoupled: $\\dot z_1$ depends only on $z_1$, $\\dot z_2$ only on $z_2$, and so on. Each mode evolves independently of the others."},
            {"title": "Solve each scalar equation", "relation": "solve",
             "tex": r"z_i(t) = e^{\lambda_i t}\, z_i(0)",
             "explanation": "Each line is the scalar equation $\\dot y = \\lambda y$, solved by an exponential times its own initial value."},
            {"title": "Stack them: $e^{Dt}$", "relation": "identity",
             "tex": r"z(t) = e^{Dt} z(0), \qquad e^{Dt} = \begin{bmatrix} e^{\lambda_1 t} & 0 & 0 \\ 0 & \ddots & 0 \\ 0 & 0 & e^{\lambda_n t} \end{bmatrix}",
             "explanation": "Exponentials on the diagonal and zeros off it (the off-diagonal entries are $0$, not $e^0 = 1$). For diagonal $D$ every power $D^k$ is diagonal with entries $\\lambda_i^k$, so the series gives exactly this. The book writes $\\Lambda$ for the lecture's $D$."},
            {"title": "Each mode on its own clock", "relation": "diagram",
             "tex": r"z_1(t) = e^{-t},\qquad z_2(t) = e^{-2t} \qquad (z(0) = (1, 1))",
             "explanation": "In the guide's example ($\\lambda_1 = -1$, $\\lambda_2 = -2$) both modes decay, the second twice as fast. Changing $z_1(0)$ would not affect $z_2$ at all."},
        ],
    },
    # ------------------------------------------------------------------ section 5
    {
        "id": "similarity-proof",
        "scene": "SimilaritySequence",
        "section": 5,
        "title": "Why $e^{At} = T e^{Dt} T^{-1}$",
        "summary": "Rewrite $A$ as $TDT^{-1}$, watch the inner $T^{-1}T$ pairs cancel in every power, and factor $T$ and $T^{-1}$ out of the series.",
        "initial": {
            "title": "Start from the series",
            "tex": r"e^{At} = I + At + \frac{A^2t^2}{2!} + \frac{A^3t^3}{3!} + \cdots",
            "explanation": "We want a formula for $e^{At}$ that only needs $e^{Dt}$, which is easy. The tool is the eigen relation $AT = TD$."},
        "steps": [
            {"title": "Solve $AT = TD$ for $A$", "relation": "identity",
             "tex": r"AT = TD \;\Rightarrow\; A = T D T^{-1}",
             "explanation": "Multiply both sides on the right by $T^{-1}$: $ATT^{-1} = A$. The $T^{-1}$ must go on the right, because that is where $T$ sits next to $A$."},
            {"title": "Square it and cancel the middle", "relation": "compute",
             "tex": r"A^2 = (TDT^{-1})(TDT^{-1}) = TD\,(T^{-1}T)\,DT^{-1} = T D^2 T^{-1}",
             "explanation": "Matrix products are associative, so the adjacent pair $T^{-1}T$ in the middle can be grouped and equals $I$. Only that adjacent pair cancels; the outer $T$ and $T^{-1}$ stay."},
            {"title": "Every power works the same way", "relation": "implies",
             "tex": r"A^k = T D^k T^{-1}",
             "explanation": "In $(TDT^{-1})(TDT^{-1})\\cdots(TDT^{-1})$ each inner $T^{-1}T$ cancels, leaving $k$ copies of $D$ between one $T$ and one $T^{-1}$."},
            {"title": "Substitute into the series", "relation": "substitute",
             "tex": r"e^{At} = TT^{-1} + TDT^{-1}t + \frac{TD^2T^{-1}t^2}{2!} + \frac{TD^3T^{-1}t^3}{3!} + \cdots",
             "explanation": "Replace each $A^k$ by $TD^kT^{-1}$, and write the identity as $I = TT^{-1}$ so that the first term has the same shape as the others."},
            {"title": "Factor $T$ left and $T^{-1}$ right", "relation": "identity",
             "tex": r"e^{At} = T\left[ I + Dt + \frac{D^2t^2}{2!} + \frac{D^3t^3}{3!} + \cdots \right] T^{-1}",
             "explanation": "Every term has $T$ on the far left and $T^{-1}$ on the far right; the powers of $t$ and the factorials are scalars and can sit anywhere. Factor $T$ out to the left and $T^{-1}$ to the right, keeping the order."},
            {"title": "Recognize $e^{Dt}$", "relation": "identity",
             "tex": r"e^{At} = T\, e^{Dt}\, T^{-1}",
             "explanation": "The bracket is the series of $e^{Dt}$, the easy diagonal exponential. So the hard exponential $e^{At}$ costs one diagonal exponential and two matrix products."},
        ],
    },
    # ------------------------------------------------------------------ section 6
    {
        "id": "map-evolve-map",
        "scene": "PipelineSequence",
        "section": 6,
        "title": "Map, evolve, map back (the linked 22:22 moment)",
        "summary": "Read $x(t) = Te^{Dt}T^{-1}x(0)$ from right to left: into eigenvector coordinates, forward in time there, back to physical coordinates. Worked with numbers.",
        "initial": {
            "title": "The solution in physical coordinates",
            "tex": r"x(t) = e^{At}x(0) = T\,e^{Dt}\,T^{-1}\,x(0)",
            "explanation": "Combine $x(t) = e^{At}x(0)$ with $e^{At} = Te^{Dt}T^{-1}$. Read it from right to left, the order in which the matrices act on $x(0)$."},
        "steps": [
            {"title": "Three stages", "relation": "diagram",
             "tex": r"x(0) \xrightarrow{\;T^{-1}\;} z(0) \xrightarrow{\;e^{Dt}\;} z(t) \xrightarrow{\;T\;} x(t)",
             "explanation": "$T^{-1}x(0) = z(0)$ maps the start into eigenvector coordinates, $e^{Dt}$ advances it there (decoupled and easy), and $T$ maps the result back. This is the interpretation at 22:22 in the lecture."},
            {"title": "Map: $z(0) = T^{-1}x(0)$", "relation": "compute",
             "tex": r"z(0) = \begin{bmatrix} 1 & -1 \\ 0 & 1 \end{bmatrix}\begin{bmatrix} 2 \\ 1 \end{bmatrix} = \begin{bmatrix} 1 \\ 1 \end{bmatrix}",
             "explanation": "Guide's example: $T = \\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}$, $D = \\mathrm{diag}(-1, -2)$, $A = TDT^{-1} = \\begin{bmatrix}-1&-1\\\\0&-2\\end{bmatrix}$, $x(0) = (2, 1)$. Then $z(0) = (2 - 1,\\ 1) = (1, 1)$. (The transpose would give $(2, 3)$, which is wrong.)"},
            {"title": "Evolve: $z(t) = e^{Dt}z(0)$", "relation": "compute",
             "tex": r"z(t) = \begin{bmatrix} e^{-t} & 0 \\ 0 & e^{-2t} \end{bmatrix}\begin{bmatrix} 1 \\ 1 \end{bmatrix} = \begin{bmatrix} e^{-t} \\ e^{-2t} \end{bmatrix} \overset{t=\ln 2}{=} \begin{bmatrix} 1/2 \\ 1/4 \end{bmatrix}",
             "explanation": "Each eigen-coordinate decays on its own. At $t = \\ln 2$, $e^{-t} = 1/2$ and $e^{-2t} = 1/4$."},
            {"title": "Map back: $x(t) = Tz(t)$", "relation": "compute",
             "tex": r"x(t) = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}\begin{bmatrix} e^{-t} \\ e^{-2t} \end{bmatrix} = \begin{bmatrix} e^{-t} + e^{-2t} \\ e^{-2t} \end{bmatrix} \overset{t=\ln 2}{=} \begin{bmatrix} 3/4 \\ 1/4 \end{bmatrix}",
             "explanation": "Multiply by $T$: $x_1 = z_1 + z_2$ and $x_2 = z_2$. In physical coordinates the two exponentials are mixed, which is why $A$ is not diagonal."},
            {"title": "Check against $\\dot x = Ax$", "relation": "compare",
             "tex": r"\dot x(0) = \begin{bmatrix} -1 - 2 \\ -2 \end{bmatrix} = \begin{bmatrix} -1 & -1 \\ 0 & -2 \end{bmatrix}\begin{bmatrix} 2 \\ 1 \end{bmatrix} = \begin{bmatrix} -3 \\ -2 \end{bmatrix}",
             "explanation": "Differentiate the formula at $t = 0$: $(-e^{-t} - 2e^{-2t},\\ -2e^{-2t}) \\to (-3, -2)$. The right-hand side $Ax(0)$ gives the same vector, and $x(0) = (1 + 1, 1) = (2, 1)$ matches too."},
            {"title": "Recap and what comes next", "relation": "recap",
             "tex": r"x(t) = T\,e^{Dt}\,T^{-1}x(0), \qquad \dot z = D z",
             "explanation": "Think in eigenvector coordinates, where the modes are decoupled; map back when you need physical values. The lecture closes by deferring stability, discrete time and control inputs $+Bu$ to the next videos."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
