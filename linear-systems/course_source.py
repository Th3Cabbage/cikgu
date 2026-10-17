"""Source of linear-systems/dist/course.json (section notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe linear-systems\\course_source.py

Text is original, written for this companion. It paraphrases S. L. Brunton's Control Bootcamp
lecture "Linear Systems" and Brunton & Kutz, Section 8.2 (printed pp. 331-332), without quoting.
The numbers in the worked examples are authored for the guide, not taken from the lecture.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "course.json")

EX = r"T = \begin{bmatrix}1&1\\0&1\end{bmatrix},\ D = \begin{bmatrix}-1&0\\0&-2\end{bmatrix}"

SECTIONS = [
    {
        "nav": "Matrix exponential",
        "title": "$\\dot x = Ax$ and the matrix exponential",
        "time": [0, 270],
        "summary": "The lecture's subject is the linear system $\\dot x = Ax$. Its solution is $x(t) = e^{At}x(0)$, where the matrix exponential is defined by the Taylor series of $e^{x}$ with $At$ plugged in. (Following the link at 22:22? That interpretation is Section 6.)",
        "goals": [
            "State the sizes in $\\dot x = Ax$: $x \\in \\mathbb{R}^n$, $A \\in \\mathbb{R}^{n \\times n}$.",
            "Write the solution $x(t) = e^{At}x(0)$ and the series definition of $e^{At}$.",
            "Explain why $e^{At}$ is not the matrix of entrywise exponentials."
        ],
        "notes": [
            {"heading": "What the lecture covers (and defers)",
             "paragraphs": [
                 "The introduction lists a whole agenda: linearizing nonlinear systems at fixed points, stability from eigenvalues, discrete time, and controllability of $\\dot x = Ax + Bu$. The lecture itself (24:47) only does the first piece of mathematics, the solution of $\\dot x = Ax$ through eigenvectors, and closes by deferring the rest to the following videos. This guide follows what is actually derived.",
                 "Why spend a lecture on it: every later topic (stability, controllability, LQR, observers) is built on understanding $\\dot x = Ax$."
             ]},
            {"heading": "The equation and its solution",
             "paragraphs": [
                 "$x$ is a column of $n$ state variables and $A$ is a constant $n\\times n$ matrix that says how the rate of change of each variable depends on all the others. The solution starting from $x(0)$ is $x(t) = e^{At}x(0)$. The lecture writes $x_0$ for the initial state; the board writes $x(0)$; they mean the same thing.",
                 "For a scalar, $e^{at} = 1 + at + a^2t^2/2! + \\cdots$. Because only sums and products appear, the same recipe defines $e^{At} = I + At + A^2t^2/2! + A^3t^3/3! + \\cdots$ for a square matrix. Each term is an $n\\times n$ matrix and the series always converges.",
                 "Two quick checks: at $t = 0$ only $I$ remains, so $x(0) = Ix(0)$. Differentiating the series term by term gives $\\frac{d}{dt}e^{At} = Ae^{At}$, so $\\dot x = Ax$ indeed holds."
             ]},
            {"heading": "Not entry by entry",
             "paragraphs": [
                 "$A^2$ mixes the entries of $A$ (each entry of $A^2$ is a row of $A$ times a column of $A$), so $e^{At}$ is not obtained by exponentiating each entry. A zero entry of $A$ does not become $e^0 = 1$. The only easy case is a diagonal matrix, which is exactly where the lecture is heading.",
                 "Summing the series by hand is impractical even for a $5\\times5$ matrix. The lecture's route is the eigendecomposition, which also explains the dynamics. Numerical libraries (for example MATLAB's expm or SciPy's scipy.linalg.expm) use robust general algorithms such as scaling and squaring; the eigenvector formula is the analytical picture, and it requires a diagonalizable $A$."
             ]}
        ],
        "keyIdeas": [
            "$x(t) = e^{At}x(0)$, with $e^{At} = I + At + A^2t^2/2! + \\cdots$.",
            "$e^{A\\cdot 0} = I$ and $\\frac{d}{dt}e^{At} = Ae^{At}$.",
            "The matrix exponential is not entrywise exponentiation."
        ],
        "example": {
            "title": "The series for a diagonal matrix",
            "problem": "Let $A = \\begin{bmatrix}-1&0\\\\0&-2\\end{bmatrix}$. Use the series to find $e^{At}$, and compare with the wrong entrywise answer.",
            "steps": [
                {"text": "Powers of a diagonal matrix are diagonal, with the entries raised to the power.",
                 "tex": "A^k = \\begin{bmatrix}(-1)^k&0\\\\0&(-2)^k\\end{bmatrix}"},
                {"text": "Add the series entry by entry on the diagonal; the off-diagonal entries stay $0$ in every term.",
                 "tex": "e^{At} = \\begin{bmatrix}\\sum_k \\frac{(-t)^k}{k!}&0\\\\0&\\sum_k \\frac{(-2t)^k}{k!}\\end{bmatrix} = \\begin{bmatrix}e^{-t}&0\\\\0&e^{-2t}\\end{bmatrix}"},
                {"text": "Entrywise exponentiation would put $e^{0\\cdot t} = 1$ off the diagonal, which is wrong already at $t = 0$ (it would not give $I$).",
                 "tex": "\\begin{bmatrix}e^{-t}&1\\\\1&e^{-2t}\\end{bmatrix} \\neq e^{At}"}
            ],
            "answer": "$e^{At} = \\mathrm{diag}(e^{-t}, e^{-2t})$. Only for diagonal matrices does the exponential act entry by entry on the diagonal, and even then the off-diagonal zeros stay zero."
        },
        "sources": {
            "video": [{"t": 0, "label": "Lecture agenda (most items deferred to later videos)"},
                      {"t": 105, "label": "x in R^n, A is n by n"},
                      {"t": 150, "label": "Solution x(t) = e^{At} x0"},
                      {"t": 180, "label": "Taylor series of the matrix exponential"},
                      {"t": 240, "label": "Why the series is impractical by hand"}],
            "book": [{"printed": 331, "pdf": 351, "label": "Eqs. (8.11)-(8.13): unforced system, solution and the series for e^{At}"}]
        },
        "tutorNotes": "Book p.331: with u = 0 and y = x the system is dx/dt = Ax (8.11), solved by x(t) = e^{At}x(0) (8.12), with e^{At} = I + At + A^2t^2/2! + A^3t^3/3! + ... (8.13). The lecture introduction announces linearization, stability, discrete time and controllability but the lecture itself only derives the solution of xdot = Ax; the rest is deferred."
    },
    {
        "nav": "Eigenpairs, AT = TD",
        "title": "Eigenvectors, eigenvalues and $AT = TD$",
        "time": [270, 495],
        "summary": "An eigenvector is a direction that $A$ only stretches or flips. Put $n$ independent eigenvectors in the columns of $T$ and the eigenvalues on the diagonal of $D$: then $AT = TD$.",
        "goals": [
            "State $Ac = \\lambda c$ with $c \\neq 0$ and interpret it geometrically.",
            "Explain column by column why $AT = TD$ (and why not $DT$).",
            "Know when $T$ is invertible, and what happens for a defective matrix."
        ],
        "notes": [
            {"heading": "Special directions",
             "paragraphs": [
                 "Most vectors change direction when multiplied by $A$. An eigenvector $c \\neq 0$ does not: $Ac = \\lambda c$, so it only gets longer, shorter, or flipped when $\\lambda < 0$. The number $\\lambda$ is the eigenvalue. In MATLAB, [T, D] = eig(A) returns both; in Python, numpy.linalg.eig."
             ]},
            {"heading": "From n equations to one matrix equation",
             "paragraphs": [
                 "Stack the eigenvectors as columns, $T = [c_1\\ c_2\\ \\cdots\\ c_n]$, and the eigenvalues on the diagonal of $D$ in the same order. Then $AT = [Ac_1\\ \\cdots\\ Ac_n] = [\\lambda_1c_1\\ \\cdots\\ \\lambda_nc_n]$.",
                 "Multiplying a matrix on the right by a diagonal matrix scales its columns, so $TD = [\\lambda_1c_1\\ \\cdots\\ \\lambda_nc_n]$ as well. Hence $AT = TD$. Multiplying on the left, $DT$, would scale rows instead, which is a different matrix."
             ]},
            {"heading": "When this works",
             "paragraphs": [
                 "We need $n$ linearly independent eigenvectors so that $T$ is invertible. Distinct eigenvalues guarantee that. Repeated eigenvalues may or may not: $A = 2I$ has $\\lambda = 2$ twice and every vector is an eigenvector, so it is diagonalizable.",
                 "A defective matrix such as $\\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}$ has a repeated eigenvalue but only one eigenvector direction. The lecture mentions that such cases need generalized eigenvectors and a Jordan form (entries above the diagonal of $D$); its exponential then contains terms like $te^{\\lambda t}$. The rest of this guide assumes $A$ is diagonalizable."
             ]}
        ],
        "keyIdeas": [
            "$Ac = \\lambda c$, $c \\neq 0$: a direction $A$ does not turn.",
            "$AT = TD$: column $i$ says $Ac_i = \\lambda_ic_i$.",
            "Diagonalizable means $n$ independent eigenvectors; distinct eigenvalues suffice but are not necessary."
        ],
        "example": {
            "title": "Checking eigenpairs and $AT = TD$",
            "problem": "For $A = \\begin{bmatrix}-1&-1\\\\0&-2\\end{bmatrix}$ check that $c_1 = (1, 0)$ and $c_2 = (1, 1)$ are eigenvectors, and verify $AT = TD$.",
            "steps": [
                {"text": "Multiply each candidate by $A$.",
                 "tex": "Ac_1 = \\begin{bmatrix}-1\\\\0\\end{bmatrix} = -1\\,c_1, \\qquad Ac_2 = \\begin{bmatrix}-1-1\\\\-2\\end{bmatrix} = -2\\,c_2"},
                {"text": "Collect them: columns of $T$, eigenvalues in the same order in $D$.",
                 "tex": EX},
                {"text": "Compute both sides.",
                 "tex": "AT = \\begin{bmatrix}-1&-2\\\\0&-2\\end{bmatrix} = TD"}
            ],
            "answer": "Both columns check, so $AT = TD$ with eigenvalues $-1$ and $-2$. Since $\\det T = 1 \\neq 0$, $T$ is invertible and $A$ is diagonalizable."
        },
        "sources": {
            "video": [{"t": 270, "label": "Eigenvalues and eigenvectors to change coordinates"},
                      {"t": 300, "label": "A c = lambda c: same direction, rescaled"},
                      {"t": 345, "label": "T of eigenvectors, D of eigenvalues"},
                      {"t": 375, "label": "A T = T D, column by column"},
                      {"t": 420, "label": "Caveat: generalized eigenvectors and Jordan blocks"}],
            "book": [{"printed": 331, "pdf": 351, "label": "Eq. (8.14) AT = TΛ; Jordan form for repeated eigenvalues"}]
        },
        "tutorNotes": "Book p.331, Eq. (8.14): AT = T Lambda (the lecture writes D). In the simplest case Lambda is diagonal with distinct eigenvalues and T has linearly independent eigenvectors; for repeated eigenvalues Lambda may need Jordan form with generalized eigenvectors."
    },
    {
        "nav": "Change coordinates",
        "title": "Eigenvector coordinates: $x = Tz$",
        "time": [495, 690],
        "summary": "Describe the state by its components along the eigenvectors: $x = Tz$. Substituting into $\\dot x = Ax$ and multiplying by $T^{-1}$ on the left gives $\\dot z = T^{-1}ATz = Dz$.",
        "goals": [
            "Read $x = Tz$ as a combination of eigenvectors and $z = T^{-1}x$ as its inverse.",
            "Derive $\\dot z = T^{-1}ATz$ with every matrix in the right order.",
            "Explain why $T^{-1}$ is not $T^{\\top}$ in general."
        ],
        "notes": [
            {"heading": "A new set of axes",
             "paragraphs": [
                 "$x = Tz = z_1c_1 + \\cdots + z_nc_n$: the entries of $z$ say how much of each eigenvector builds $x$. Geometrically the $z$ grid is the standard grid sheared or stretched by $T$; its axes run along the eigenvectors and need not be perpendicular.",
                 "Because $T$ is invertible, $z = T^{-1}x$. Use the inverse. The transpose equals the inverse only when the columns are orthonormal (for example for symmetric $A$ with normalized eigenvectors); the guide's example has $T^{-1} = \\begin{bmatrix}1&-1\\\\0&1\\end{bmatrix}$ but $T^{\\top} = \\begin{bmatrix}1&0\\\\1&1\\end{bmatrix}$."
             ]},
            {"heading": "The derivation",
             "paragraphs": [
                 "$T$ is constant, so $\\dot x = T\\dot z$. Substitute both $\\dot x$ and $x$ into $\\dot x = Ax$: $T\\dot z = ATz$.",
                 "Multiply both sides on the left by $T^{-1}$: $\\dot z = T^{-1}ATz$. From $AT = TD$, $T^{-1}AT = T^{-1}TD = D$. So $\\dot z = Dz$, the boxed result of the lecture. Every step keeps matrices in order; nothing is divided by a matrix."
             ]}
        ],
        "keyIdeas": [
            "$x = Tz$ and $z = T^{-1}x$ (inverse, not transpose).",
            "$\\dot z = T^{-1}AT\\,z = Dz$.",
            "Matrix order is kept at every step; $T^{-1}$ multiplies from the left."
        ],
        "example": {
            "title": "Coordinates of a point",
            "problem": "With $T = \\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}$, find the eigen-coordinates $z$ of $x = (2, 1)$ and check them. What would the transpose give?",
            "steps": [
                {"text": "Invert $T$ (for a $2\\times2$ matrix swap the diagonal, negate the off-diagonal, divide by $\\det T = 1$).",
                 "tex": "T^{-1} = \\begin{bmatrix}1&-1\\\\0&1\\end{bmatrix}"},
                {"text": "Map the point.",
                 "tex": "z = T^{-1}x = \\begin{bmatrix}2-1\\\\1\\end{bmatrix} = \\begin{bmatrix}1\\\\1\\end{bmatrix}"},
                {"text": "Check by rebuilding $x$ from the eigenvectors.",
                 "tex": "1\\begin{bmatrix}1\\\\0\\end{bmatrix} + 1\\begin{bmatrix}1\\\\1\\end{bmatrix} = \\begin{bmatrix}2\\\\1\\end{bmatrix}\\ \\checkmark"},
                {"text": "The transpose gives a different, wrong vector.",
                 "tex": "T^{\\top}x = \\begin{bmatrix}2\\\\3\\end{bmatrix}, \\quad T\\begin{bmatrix}2\\\\3\\end{bmatrix} = \\begin{bmatrix}5\\\\3\\end{bmatrix} \\neq x"}
            ],
            "answer": "$z = (1, 1)$: one unit along each eigenvector. Using $T^{\\top}$ would give $(2, 3)$, which does not rebuild $x$."
        },
        "sources": {
            "video": [{"t": 495, "label": "Why change coordinates"},
                      {"t": 525, "label": "x = T z with an invertible T"},
                      {"t": 570, "label": "T^{-1} A T is the diagonal matrix"},
                      {"t": 600, "label": "x dot = T z dot = A T z"},
                      {"t": 630, "label": "z dot = D z, boxed"}],
            "book": [{"printed": 332, "pdf": 352, "label": "Eq. (8.18): x = Tz gives z dot = T^{-1}ATz = Λz"}]
        },
        "tutorNotes": "Book p.332, Eq. (8.18): x = Tz implies zdot = T^{-1} xdot = T^{-1}Ax = T^{-1}ATz, hence zdot = Lambda z: in eigenvector coordinates the dynamics are diagonal. The lecture names the diagonal matrix D."
    },
    {
        "nav": "Decoupled modes",
        "title": "Decoupled dynamics and $e^{Dt}$",
        "time": [690, 885],
        "summary": "With $D$ diagonal, $\\dot z = Dz$ is $n$ separate equations $\\dot z_i = \\lambda_iz_i$, solved by $z_i(t) = e^{\\lambda_it}z_i(0)$. Together: $z(t) = e^{Dt}z(0)$ with exponentials on the diagonal and zeros elsewhere.",
        "goals": [
            "Write $\\dot z = Dz$ row by row and explain decoupling.",
            "Solve each mode and assemble $e^{Dt}$.",
            "Connect the lecture's $D$ to the book's $\\Lambda$."
        ],
        "notes": [
            {"heading": "Row by row",
             "paragraphs": [
                 "Row $i$ of $D$ has a single nonzero entry $\\lambda_i$ in column $i$, so $\\dot z_i = \\lambda_iz_i$. The rate of change of $z_1$ depends on $z_1$ only, of $z_2$ on $z_2$ only, and so on. The modes are decoupled: changing the initial amount of one eigenvector has no effect on the others.",
                 "Each line is the scalar equation $\\dot y = \\lambda y$, solved by $y(t) = e^{\\lambda t}y(0)$. A negative $\\lambda$ decays, a positive one grows, and $|\\lambda|$ sets how fast."
             ]},
            {"heading": "The diagonal exponential",
             "paragraphs": [
                 "Stacking the modes: $z(t) = e^{Dt}z(0)$ with $e^{Dt} = \\mathrm{diag}(e^{\\lambda_1t}, \\ldots, e^{\\lambda_nt})$. The series agrees: every $D^k$ is diagonal with entries $\\lambda_i^k$, so each diagonal entry of the series is a scalar exponential and every off-diagonal entry is $0$ (not $1$).",
                 "Notation: the lecture writes $D$ for the diagonal matrix of eigenvalues; the book writes $\\Lambda$. They are the same object. (If the eigenvalues are complex, $e^{\\lambda t}$ oscillates; stability from eigenvalues is the subject of the next lecture.)"
             ]}
        ],
        "keyIdeas": [
            "$\\dot z_i = \\lambda_i z_i$: each mode evolves on its own.",
            "$e^{Dt} = \\mathrm{diag}(e^{\\lambda_1t}, \\ldots, e^{\\lambda_nt})$, zeros off the diagonal.",
            "Lecture $D$ = book $\\Lambda$."
        ],
        "example": {
            "title": "Two modes, two clocks",
            "problem": "For $D = \\mathrm{diag}(-1, -2)$ and $z(0) = (1, 1)$, find $z(t)$ and the time at which $z_1$ has halved. What is $z_2$ then?",
            "steps": [
                {"text": "Solve each mode separately.",
                 "tex": "z_1(t) = e^{-t},\\qquad z_2(t) = e^{-2t}"},
                {"text": "$z_1$ halves when $e^{-t} = 1/2$.",
                 "tex": "t = \\ln 2 \\approx 0.693"},
                {"text": "At that time the faster mode is at a quarter.",
                 "tex": "z_2(\\ln 2) = e^{-2\\ln 2} = \\tfrac14"}
            ],
            "answer": "$z(t) = (e^{-t}, e^{-2t})$; at $t = \\ln 2$, $z = (1/2, 1/4)$. The second mode decays twice as fast, independently of the first."
        },
        "sources": {
            "video": [{"t": 690, "label": "Diagonal dynamics are uncoupled"},
                      {"t": 735, "label": "Written out: d/dt z = diag(lambda) z"},
                      {"t": 765, "label": "z_i(t) = e^{lambda_i t} z_i(0)"},
                      {"t": 795, "label": "e^{Dt}: exponentials on the diagonal"},
                      {"t": 840, "label": "Thinking in eigenvector coordinates"}],
            "book": [{"printed": 331, "pdf": 351, "label": "Eq. (8.15): e^{Λt} for diagonal Λ"}]
        },
        "tutorNotes": "Book p.331, Eq. (8.15): for diagonal Lambda, e^{Lambda t} is diagonal with entries e^{lambda_k t} and zeros elsewhere; computing e^{Lambda t} is easier than e^{At}. Non-trivial Jordan blocks need extensions involving nilpotent matrices."
    },
    {
        "nav": "Proof: factor out T, T⁻¹",
        "title": "Why $e^{At} = Te^{Dt}T^{-1}$",
        "time": [885, 1245],
        "summary": "Write $A = TDT^{-1}$. In every power the inner $T^{-1}T$ pairs cancel, $A^k = TD^kT^{-1}$; substitute into the series, factor $T$ to the left and $T^{-1}$ to the right, and the middle is $e^{Dt}$.",
        "goals": [
            "Derive $A = TDT^{-1}$ from $AT = TD$.",
            "Show $A^k = TD^kT^{-1}$ by cancelling only adjacent $T^{-1}T$.",
            "Factor the series and recognize $e^{Dt}$."
        ],
        "notes": [
            {"heading": "Powers of A",
             "paragraphs": [
                 "Multiply $AT = TD$ on the right by $T^{-1}$: $A = TDT^{-1}$. Then $A^2 = (TDT^{-1})(TDT^{-1})$. Matrix multiplication is associative, so we may regroup as $TD(T^{-1}T)DT^{-1}$ and replace the adjacent pair by $I$: $A^2 = TD^2T^{-1}$. We may not move $T$ past $D$ or swap factors; only the adjacent $T^{-1}T$ cancels.",
                 "With $k$ factors every inner pair cancels: $A^k = TD^kT^{-1}$. For $k = 0$, write $I = TT^{-1}$ so the first term has the same shape."
             ]},
            {"heading": "Factor the series",
             "paragraphs": [
                 "$e^{At} = TT^{-1} + TDT^{-1}t + TD^2T^{-1}t^2/2! + \\cdots$. Every term has $T$ on the far left and $T^{-1}$ on the far right; the powers of $t$ and the factorials are scalars and commute with everything. Factor: $e^{At} = T[I + Dt + D^2t^2/2! + \\cdots]T^{-1}$, and the bracket is $e^{Dt}$.",
                 "Result: $e^{At} = Te^{Dt}T^{-1}$ (book Eq. 8.17). The hard exponential reduces to one diagonal exponential and two matrix products. This is an analytical identity for diagonalizable $A$; numerically, an ill-conditioned $T$ (nearly parallel eigenvectors, which the lecture mentions) makes it inaccurate, which is one reason libraries use other algorithms."
             ]}
        ],
        "keyIdeas": [
            "$A = TDT^{-1}$ and $A^k = TD^kT^{-1}$.",
            "Only adjacent $T^{-1}T$ pairs cancel; order is preserved.",
            "$e^{At} = Te^{Dt}T^{-1}$."
        ],
        "example": {
            "title": "Compute $e^{At}$ for the guide's example",
            "problem": "With $" + EX + "$, compute $A = TDT^{-1}$ and $e^{At} = Te^{Dt}T^{-1}$. Check $t = 0$.",
            "steps": [
                {"text": "Build $A$.",
                 "tex": "A = \\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}\\begin{bmatrix}-1&0\\\\0&-2\\end{bmatrix}\\begin{bmatrix}1&-1\\\\0&1\\end{bmatrix} = \\begin{bmatrix}-1&-1\\\\0&-2\\end{bmatrix}"},
                {"text": "Exponential: replace $D$ by $e^{Dt}$ in the same product.",
                 "tex": "e^{At} = \\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}\\begin{bmatrix}e^{-t}&0\\\\0&e^{-2t}\\end{bmatrix}\\begin{bmatrix}1&-1\\\\0&1\\end{bmatrix} = \\begin{bmatrix}e^{-t}&e^{-2t}-e^{-t}\\\\0&e^{-2t}\\end{bmatrix}"},
                {"text": "Check $t = 0$: the off-diagonal entry is $1 - 1 = 0$.",
                 "tex": "e^{A\\cdot0} = \\begin{bmatrix}1&0\\\\0&1\\end{bmatrix} = I\\ \\checkmark"}
            ],
            "answer": "$e^{At} = \\begin{bmatrix}e^{-t}&e^{-2t}-e^{-t}\\\\0&e^{-2t}\\end{bmatrix}$. Note the off-diagonal entry: it is neither $0$ nor $e^{-t}$, it mixes both modes."
        },
        "sources": {
            "video": [{"t": 900, "label": "Back to physical coordinates: x(t) = e^{At} x0"},
                      {"t": 930, "label": "A = T D T^{-1}"},
                      {"t": 975, "label": "Identity written as T T^{-1}"},
                      {"t": 1005, "label": "A^2: the middle T^{-1} T cancels"},
                      {"t": 1095, "label": "Factor T left and T^{-1} right"},
                      {"t": 1185, "label": "e^{At} = T e^{Dt} T^{-1}"}],
            "book": [{"printed": 331, "pdf": 351, "label": "Eqs. (8.16a-c): A = TΛT^{-1}, A^k = TΛ^kT^{-1}"},
                     {"printed": 332, "pdf": 352, "label": "Eqs. (8.17a-c): e^{At} = T e^{Λt} T^{-1}"}]
        },
        "tutorNotes": "Book pp.331-332, Eqs. (8.16a-c): A = T Lambda T^{-1}, A^2 = (T Lambda T^{-1})(T Lambda T^{-1}) = T Lambda^2 T^{-1}, A^k = T Lambda^k T^{-1}. Eqs. (8.17a-c): substituting into the series, e^{At} = TT^{-1} + T Lambda T^{-1} t + ... = T[I + Lambda t + Lambda^2 t^2/2! + ...]T^{-1} = T e^{Lambda t} T^{-1}."
    },
    {
        "nav": "Map, evolve, map back",
        "title": "Map, evolve, map back (22:22)",
        "time": [1245, 1487],
        "summary": "The linked moment, 22:22: read $x(t) = Te^{Dt}T^{-1}x(0)$ from right to left. $T^{-1}$ maps the start into eigenvector coordinates, $e^{Dt}$ advances the decoupled modes, $T$ maps back to physical coordinates.",
        "goals": [
            "Name the three stages of $x(t) = Te^{Dt}T^{-1}x(0)$ and the coordinates at each stage.",
            "Carry out the stages by hand on a $2\\times2$ example.",
            "Check a closed-form solution against $\\dot x = Ax$ and $x(0)$."
        ],
        "notes": [
            {"heading": "Reading the formula",
             "paragraphs": [
                 "Matrices act on $x(0)$ from right to left. Stage 1: $z(0) = T^{-1}x(0)$, the initial state in eigenvector coordinates (for a pendulum, $x(0)$ would hold the initial angle and angular velocity). Stage 2: $z(t) = e^{Dt}z(0)$, each mode multiplied by its own exponential. Stage 3: $x(t) = Tz(t)$, back to the physical variables someone actually cares about.",
                 "The lecture apologizes for one notational clash: $t$ is time, $T$ is the matrix of eigenvectors. The book draws the three stages as nested underbraces in Eq. (8.19)."
             ]},
            {"heading": "Worked numbers (authored for this guide)",
             "paragraphs": [
                 "Take $T = \\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}$, $D = \\mathrm{diag}(-1, -2)$, so $A = \\begin{bmatrix}-1&-1\\\\0&-2\\end{bmatrix}$, and $x(0) = (2, 1)$. Then $z(0) = (1, 1)$, $z(t) = (e^{-t}, e^{-2t})$ and $x(t) = (e^{-t} + e^{-2t},\\ e^{-2t})$. At $t = \\ln 2$: $z = (1/2, 1/4)$ and $x = (3/4, 1/4)$.",
                 "Check: $x(0) = (2, 1)$ and $\\dot x(0) = (-1 - 2, -2) = (-3, -2) = Ax(0)$. In $x$ the two exponentials are mixed, which is exactly why $A$ is not diagonal; in $z$ they are separate."
             ]},
            {"heading": "What comes next",
             "paragraphs": [
                 "The lecture ends by deferring the rest of its agenda to the following videos: what the eigenvalues say about stability, the discrete-time version $x_{k+1} = A_dx_k$, and adding control $+Bu$ (controllability). Linearizing a nonlinear system at a fixed point, mentioned in the introduction, also belongs to those later parts."
             ]}
        ],
        "keyIdeas": [
            "$x(0) \\xrightarrow{T^{-1}} z(0) \\xrightarrow{e^{Dt}} z(t) \\xrightarrow{T} x(t)$.",
            "Eigen-coordinates: simple and decoupled; physical coordinates: what we measure.",
            "Always check $x(0)$ and $\\dot x(0) = Ax(0)$."
        ],
        "example": {
            "title": "The full pipeline by hand",
            "problem": "With $" + EX + "$ and $x(0) = (2, 1)$, find $x(t)$ through the three stages and evaluate it at $t = \\ln 2$.",
            "steps": [
                {"text": "Map into eigenvector coordinates.",
                 "tex": "z(0) = T^{-1}x(0) = \\begin{bmatrix}1&-1\\\\0&1\\end{bmatrix}\\begin{bmatrix}2\\\\1\\end{bmatrix} = \\begin{bmatrix}1\\\\1\\end{bmatrix}"},
                {"text": "Evolve each mode.",
                 "tex": "z(t) = \\begin{bmatrix}e^{-t}\\\\e^{-2t}\\end{bmatrix} \\;\\Rightarrow\\; z(\\ln 2) = \\begin{bmatrix}1/2\\\\1/4\\end{bmatrix}"},
                {"text": "Map back with $T$.",
                 "tex": "x(t) = Tz(t) = \\begin{bmatrix}e^{-t}+e^{-2t}\\\\e^{-2t}\\end{bmatrix} \\;\\Rightarrow\\; x(\\ln 2) = \\begin{bmatrix}3/4\\\\1/4\\end{bmatrix}"},
                {"text": "Check the derivative at $t = 0$ against $Ax(0)$.",
                 "tex": "\\dot x(0) = \\begin{bmatrix}-3\\\\-2\\end{bmatrix} = \\begin{bmatrix}-1&-1\\\\0&-2\\end{bmatrix}\\begin{bmatrix}2\\\\1\\end{bmatrix}\\ \\checkmark"}
            ],
            "answer": "$x(t) = (e^{-t} + e^{-2t},\\ e^{-2t})$ and $x(\\ln 2) = (3/4, 1/4)$. Try the same numbers in the explorer's \u201cworked example\u201d preset."
        },
        "sources": {
            "video": [{"t": 1342, "label": "★ Linked moment 22:22: T^{-1} x0 maps into eigenvector coordinates"},
                      {"t": 1245, "label": "Equivalence of the two ways of writing the solution"},
                      {"t": 1290, "label": "x(t) = T e^{Dt} T^{-1} x0 (t is time, T is the matrix)"},
                      {"t": 1365, "label": "e^{Dt} advances z; T maps back to x"},
                      {"t": 1410, "label": "Why this is how to think about linear systems"},
                      {"t": 1440, "label": "Next: stability, discrete time, adding Bu"}],
            "book": [{"printed": 332, "pdf": 352, "label": "Eq. (8.19): the three stages z(0), z(t), x(t)"}]
        },
        "tutorNotes": "Book p.332, Eq. (8.19): x(t) = T e^{Lambda t} T^{-1} x(0). First T^{-1} maps the initial condition in physical coordinates x(0) into eigenvector coordinates z(0); then the diagonal update e^{Lambda t} advances it; finally T maps z(t) back to x(t). The guide's numerical example (T=[[1,1],[0,1]], D=diag(-1,-2), x(0)=(2,1)) is authored, not from the lecture."
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
    q("q-sizes", "In $\\dot x = Ax$ with $n$ state variables, what are the shapes of $x$ and $A$?", [
        ("$x$ is $n\\times1$ and $A$ is $n\\times n$.", True, "Right. $A$ must take an $n$-vector to an $n$-vector (the rate of change of every state variable), so it is square."),
        ("$x$ is $n\\times1$ and $A$ is $1\\times n$.", False, "No. A $1\\times n$ matrix times $x$ is a single number, but $\\dot x$ has $n$ entries."),
        ("$x$ is $n\\times n$ and $A$ is $n\\times1$.", False, "No. The state is a vector of $n$ quantities; $A$ is the matrix of interactions."),
        ("Any shapes, as long as the product is defined.", False, "No. The product must also have the same shape as $\\dot x$, which forces $A$ to be $n\\times n$.")]),
    q("q-entrywise", "$A = \\begin{bmatrix}0&1\\\\0&0\\end{bmatrix}$. Which is $e^{At}$?", [
        ("$\\begin{bmatrix}1&t\\\\0&1\\end{bmatrix}$", True, "Right. $A^2 = 0$, so the series stops: $e^{At} = I + At$. (This $A$ is defective, so the eigenvector formula does not apply, but the series always does.)"),
        ("$\\begin{bmatrix}1&e^{t}\\\\1&1\\end{bmatrix}$", False, "No. That exponentiates each entry of $At$. At $t = 0$ it is not even $I$."),
        ("$\\begin{bmatrix}e^{t}&0\\\\0&e^{t}\\end{bmatrix}$", False, "No. The eigenvalues of $A$ are both $0$, and the series gives $I + At$, with no exponential growth."),
        ("$I$ for all $t$", False, "No. That would mean $\\dot x = 0$, but $A \\neq 0$: the second state drives the first, $\\dot x_1 = x_2$.")]),
    q("q-eigen", "What does $Ac = \\lambda c$ (with $c \\neq 0$) say geometrically?", [
        ("$A$ maps $c$ onto its own line: it only stretches, shrinks or flips it.", True, "Right. The direction is preserved up to sign; $\\lambda$ is the scale factor (negative means flipped)."),
        ("$A$ rotates $c$ by the angle $\\lambda$.", False, "No. A rotation changes the direction; an eigenvector's direction is kept (up to a flip)."),
        ("Every vector $c$ satisfies it for some $\\lambda$.", False, "No. Only special directions do; a generic vector is turned by $A$."),
        ("$c$ must be the zero vector.", False, "No. $c = 0$ satisfies $A0 = \\lambda 0$ for every $\\lambda$, which is why eigenvectors are required to be nonzero.")]),
    q("q-attd", "Why is $AT = TD$ and not $AT = DT$?", [
        ("Right-multiplying by a diagonal $D$ scales the columns of $T$, giving $\\lambda_ic_i$ in column $i$.", True, "Right. Column $i$ of $AT$ is $Ac_i = \\lambda_ic_i$, which is column $i$ of $TD$."),
        ("Because $TD = DT$ for any diagonal $D$.", False, "No. $DT$ scales the rows of $T$; in general it is a different matrix."),
        ("Because $D$ is always the identity.", False, "No. $D$ holds the eigenvalues, which are usually not all $1$."),
        ("Both are correct; it is a convention.", False, "No. Matrix products do not commute, and only $TD$ reproduces $Ac_i = \\lambda_ic_i$ column by column.")]),
    q("q-diag", "Which matrix CANNOT be written as $TDT^{-1}$ with $D$ diagonal and $T$ invertible?", [
        ("$\\begin{bmatrix}3&1\\\\0&3\\end{bmatrix}$", True, "Right. The eigenvalue $3$ is repeated but there is only one eigenvector direction, $(1, 0)$; it is defective and needs a Jordan form."),
        ("$\\begin{bmatrix}3&0\\\\0&3\\end{bmatrix}$", False, "No. It is already diagonal ($T = I$). A repeated eigenvalue does not by itself prevent diagonalization."),
        ("$\\begin{bmatrix}-1&-1\\\\0&-2\\end{bmatrix}$", False, "No. Its eigenvalues $-1$ and $-2$ are distinct, which guarantees independent eigenvectors."),
        ("$\\begin{bmatrix}0&1\\\\1&0\\end{bmatrix}$", False, "No. Eigenvalues $\\pm1$ are distinct; eigenvectors $(1, 1)$ and $(1, -1)$.")]),
    q("q-inverse", "With $x = Tz$ and $T = \\begin{bmatrix}1&1\\\\0&1\\end{bmatrix}$, how do you get $z$ from $x$?", [
        ("$z = T^{-1}x$ with $T^{-1} = \\begin{bmatrix}1&-1\\\\0&1\\end{bmatrix}$.", True, "Right. Check: $T T^{-1} = I$, and $x = (2, 1)$ gives $z = (1, 1)$."),
        ("$z = T^{\\top}x$.", False, "No. The transpose is the inverse only for orthonormal columns. Here $T^{\\top}(2, 1) = (2, 3)$, and $T(2, 3) \\neq (2, 1)$."),
        ("$z = xT^{-1}$.", False, "No. $x$ is a column vector; $xT^{-1}$ is not defined. The inverse must act from the left."),
        ("$z = x / T$.", False, "No. There is no division by a matrix; you multiply by the inverse on the correct side.")]),
    q("q-left", "From $T\\dot z = ATz$, which step gives $\\dot z = T^{-1}ATz$?", [
        ("Multiply both sides on the left by $T^{-1}$.", True, "Right. On the left side $T^{-1}T\\dot z = \\dot z$; on the right $T^{-1}$ lands in front of $ATz$."),
        ("Multiply both sides on the right by $T^{-1}$.", False, "No. $\\dot z$ is a column vector; $\\dot zT^{-1}$ is not defined."),
        ("Cancel $T$ on both sides.", False, "No. $T$ is not next to $\\dot z$ on the right side (it is $ATz$); you cannot cancel through $A$."),
        ("Replace $A$ by $D$.", False, "No. $A$ and $D$ are different matrices; $D$ appears only after forming $T^{-1}AT$.")]),
    q("q-edt", "$D = \\mathrm{diag}(-1, 3)$. What is $e^{Dt}$?", [
        ("$\\begin{bmatrix}e^{-t}&0\\\\0&e^{3t}\\end{bmatrix}$", True, "Right. Diagonal exponentials, zeros off the diagonal: the modes are decoupled; the first decays, the second grows."),
        ("$\\begin{bmatrix}e^{-t}&1\\\\1&e^{3t}\\end{bmatrix}$", False, "No. The off-diagonal entries of every $D^k$ are $0$, so they stay $0$; $e^0 = 1$ would be entrywise exponentiation."),
        ("$\\begin{bmatrix}e^{-t}&e^{3t}\\\\0&0\\end{bmatrix}$", False, "No. Each eigenvalue's exponential stays in its own diagonal position."),
        ("$e^{2t}I$", False, "No. You cannot add the eigenvalues; each mode keeps its own rate.")]),
    q("q-cancel", "In $A^2 = (TDT^{-1})(TDT^{-1})$, which simplification is valid?", [
        ("The adjacent pair $T^{-1}T$ in the middle equals $I$, giving $TD^2T^{-1}$.", True, "Right. Associativity lets you group the adjacent pair; nothing else is moved."),
        ("The outer $T$ and $T^{-1}$ cancel, giving $D^2$.", False, "No. They are not adjacent and $T$ does not commute with $D$; $A^2 \\neq D^2$ in general."),
        ("$T$ and $D$ commute, so $A^2 = T^2D^2T^{-2}$.", False, "No. Matrices generally do not commute, and no step here needs them to."),
        ("Nothing cancels; $A^2$ has to be multiplied out.", False, "No. Multiplying out works but misses the point: the middle $T^{-1}T = I$ is what makes $A^k = TD^kT^{-1}$.")]),
    q("q-pipeline", "In $x(t) = Te^{Dt}T^{-1}x(0)$, what does $T^{-1}x(0)$ represent (the linked 22:22 moment)?", [
        ("The initial state written in eigenvector coordinates, $z(0)$.", True, "Right. It is the first of the three stages: map, evolve with $e^{Dt}$, map back with $T$."),
        ("The state at time $t$ in physical coordinates.", False, "No. That is the whole product, $x(t)$, after all three stages."),
        ("The eigenvalues of $A$.", False, "No. The eigenvalues sit in $D$; $T^{-1}x(0)$ is a vector of coordinates."),
        ("The derivative $\\dot x(0)$.", False, "No. The derivative is $Ax(0) = TDT^{-1}x(0)$, which also involves $D$.")]),
]

EXPLORER = {
    "l1": {"min": -3, "max": 2, "step": 0.1, "default": -1},
    "l2": {"min": -3, "max": 2, "step": 0.1, "default": -2},
    "s": {"min": -2, "max": 2, "step": 0.1, "default": 1},
    "x1": {"min": -3, "max": 3, "step": 0.1, "default": 2},
    "x2": {"min": -3, "max": 3, "step": 0.1, "default": 1},
    "t": {"min": 0, "max": 4, "step": 0.01, "default": 0.69},
    "tMax": 4,
    "range": 4,
    "playRate": 0.8,
    "presets": [
        {"id": "worked", "label": "Worked example", "l1": -1, "l2": -2, "s": 1, "x1": 2, "x2": 1, "t": 0.69,
         "note": "The guide's example: $T = [c_1\\ c_2]$ with $c_2 = (1, 1)$, $D = \\mathrm{diag}(-1, -2)$, $x(0) = (2, 1)$, so $z(0) = (1, 1)$. At $t \\approx \\ln 2 = 0.693$, $z \\approx (1/2, 1/4)$ and $x \\approx (3/4, 1/4)$."},
        {"id": "decay", "label": "Both decay", "l1": -0.4, "l2": -2.5, "s": -1.2, "x1": -1.5, "x2": 2.5, "t": 1,
         "note": "A fast and a slow mode. The fast mode ($z_2$) dies first, so the physical trajectory bends onto the slow eigenvector line $c_1$ before reaching the origin."},
        {"id": "saddle", "label": "Saddle", "l1": 0.5, "l2": -1.5, "s": 1, "x1": 1.2, "x2": 2.5, "t": 1.5,
         "note": "$\\lambda_1 > 0 > \\lambda_2$: the $c_2$ component decays while the $c_1$ component grows, so the trajectory approaches the $c_1$ line and leaves along it."},
        {"id": "repeated", "label": "Repeated, diagonalizable", "l1": -1, "l2": -1, "s": 1, "x1": 2, "x2": 1, "t": 1,
         "note": "Equal eigenvalues: $A = TDT^{-1} = -I$ whatever $T$ is (the $s(\\lambda_2 - \\lambda_1)$ entry is $0$). Every direction is an eigenvector and the trajectory is a straight line to the origin."}
    ],
    "defectiveNote": "Not shown by the sliders: a defective matrix such as $\\begin{bmatrix}-1&1\\\\0&-1\\end{bmatrix}$ has only one eigenvector direction, so no invertible $T$ makes it diagonal. Its exponential is the Jordan-form result $e^{-t}\\begin{bmatrix}1&t\\\\0&1\\end{bmatrix}$, with a $te^{-t}$ term that no diagonal $e^{Dt}$ can produce.",
    "tutorContext": "The explorer builds A = T D T^{-1} from sliders: eigenvalues l1, l2 in D = diag(l1, l2) and eigenvector c2 = (s, 1) with c1 = (1, 0), so T = [[1, s], [0, 1]], T^{-1} = [[1, -s], [0, 1]] and A = [[l1, s(l2 - l1)], [0, l2]]. For the initial state x(0) = (x1, x2) and time t it shows z(0) = T^{-1}x(0), z(t) = e^{Dt}z(0) and x(t) = T z(t) in a physical plane (with the eigenvector lines) and an eigenvector-coordinate plane, using exact formulas. Presets: worked example (l1=-1, l2=-2, s=1, x0=(2,1)), both decay, saddle, repeated but diagonalizable (A = -I). A defective Jordan example is described in a note only. The student's current slider values are not sent."
}

COURSE = {
    "version": 1,
    "title": "Linear Systems: solving ẋ = Ax with eigenvectors",
    "subtitle": "A study companion to Steve Brunton's Control Bootcamp lecture on linear systems and Section 8.2 of Brunton & Kutz",
    "video": {"id": "nyqJJdhReiA", "title": "Linear Systems [Control Bootcamp] (Steve Brunton, University of Washington)",
              "duration": "24:47", "url": "https://www.youtube.com/watch?v=nyqJJdhReiA"},
    "book": {"title": "Data-Driven Science and Engineering: Machine Learning, Dynamical Systems, and Control",
             "authors": "S. L. Brunton and J. N. Kutz", "edition": "2017 preprint (Chapter 8, Linear Control Theory, Section 8.2)",
             "onlineUrl": "http://databookuw.com/databook.pdf",
             "pageNote": "Page references give the printed page and the page of the local PDF (printed page + 20 for these pages). The online copy may be a different revision with different PDF page numbers."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide, and the numerical examples are authored for it. They summarize the lecture and the book; for the original wording, watch the lecture and read the chapter. Lecture captions, the video and the chapter text are not included in this guide.",
    "explorer": EXPLORER,
    "sections": SECTIONS,
    "quiz": QUIZ,
}

# The correct answer is written first above; place it at a fixed, varied position per question.
for _i, _q in enumerate(QUIZ):
    _r = [1, 3, 0, 2, 2, 1, 3, 0, 1, 2][_i % 10]
    _q["choices"] = _q["choices"][-_r:] + _q["choices"][:-_r] if _r else _q["choices"]

if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(COURSE, f, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(SECTIONS)} sections, {len(QUIZ)} questions")
