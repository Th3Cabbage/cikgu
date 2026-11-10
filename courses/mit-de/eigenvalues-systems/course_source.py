"""Source of courses/mit-de/eigenvalues-systems/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\eigenvalues-systems\\course_source.py

Unit 8 of the MIT Learn Differential Equations companion: playlist videos 40-47 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Chapter 6.
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
    (40, "DzqE7tj7eIM", "Eigenvalues and Eigenvectors", "19:01"),
    (41, "U8R54zOTVLw", "Diagonalizing a Matrix", "11:37"),
    (42, "xtMzTXHO_zA", "Powers of Matrices and Markov Matrices", "17:54"),
    (43, "iVlHPDER0FA", "Solving Linear Systems", "15:48"),
    (44, "LwSk9M5lJx4", "The Matrix Exponential", "15:32"),
    (45, "LKMGo8G7-vk", "Similar Matrices", "14:51"),
    (46, "ZTNniGvY5IQ", "Symmetric Matrices, Real Eigenvalues, Orthogonal Eigenvectors", "15:55"),
    (47, "Ku2zZ5Vfpzo", "Second Order Systems", "16:50"),
]

SECTIONS = [
    {
        "nav": "Eigenvalues and eigenvectors",
        "v": 40,
        "title": r"$Ax = \lambda x$: directions that $A$ only stretches",
        "summary": r"For $y' = Ay$, try $y = e^{\lambda t}x$: the exponential cancels and leaves $Ax = \lambda x$. An eigenvector keeps its direction under $A$, and $\lambda$ is the stretching factor. With two eigenvectors the solution is $c_1e^{\lambda_1t}x_1 + c_2e^{\lambda_2t}x_2$.",
        "time": [0, 1141],
        "goals": [
            r"Derive $Ax = \lambda x$ from the trial solution $e^{\lambda t}x$.",
            r"Find eigenvalues and eigenvectors of a $2\times2$ matrix.",
            r"Write the general solution of $y' = Ay$ and fit $y(0)$.",
            r"Know the eigenvalues of $A^2$, $A^n$ and $A + cI$."
        ],
        "notes": [
            {"heading": "From the equation to Ax = lambda x",
             "paragraphs": [
                 r"A system $y' = Ay$ of $n$ equations couples the unknowns. Try the simplest possible solution, a fixed vector $x$ times a scalar exponential: $y = e^{\lambda t}x$. Then $y' = \lambda e^{\lambda t}x$ and $Ay = e^{\lambda t}Ax$. Cancel $e^{\lambda t}$: $Ax = \lambda x$.",
                 r"So the right $x$ is a vector whose direction is unchanged by $A$; $\lambda$ is how much it is stretched (or shrunk, or reversed if negative)."
             ]},
            {"heading": "The lecture's example",
             "paragraphs": [
                 r"$y_1' = 5y_1 + y_2$, $y_2' = 3y_1 + 3y_2$, so $A = \begin{bmatrix}5 & 1\\ 3 & 3\end{bmatrix}$. The vector $x_1 = (1, 1)$ gives $Ax_1 = (6, 6) = 6x_1$, so $\lambda_1 = 6$. The vector $x_2 = (1, -3)$ gives $Ax_2 = (2, -6) = 2x_2$, so $\lambda_2 = 2$. The general solution is $y(t) = c_1e^{6t}(1, 1) + c_2e^{2t}(1, -3)$, and $y(0) = c_1(1,1) + c_2(1,-3)$ fixes the constants."
             ]},
            {"heading": "Simple consequences",
             "paragraphs": [
                 r"If $Ax = \lambda x$ then $A^2x = \lambda^2x$ and $A^nx = \lambda^nx$: same eigenvectors, eigenvalues raised to the power ($36$ and $4$ for $A^2$ above). Also $(A + cI)x = (\lambda + c)x$: shifting by $cI$ shifts every eigenvalue by $c$.",
                 r"A caution: the eigenvalues of $A + B$ are usually not the sums of eigenvalues of $A$ and $B$, because their eigenvectors are usually different."
             ]}
        ],
        "keyIdeas": [
            r"$y = e^{\lambda t}x$ $\Rightarrow$ $Ax = \lambda x$.",
            r"$\begin{bmatrix}5&1\\3&3\end{bmatrix}$: $\lambda = 6$, $x = (1,1)$; $\lambda = 2$, $x = (1,-3)$.",
            r"$y = c_1e^{\lambda_1t}x_1 + c_2e^{\lambda_2t}x_2$.",
            r"$A^n$: $\lambda^n$; $A + cI$: $\lambda + c$."
        ],
        "example": {
            "title": "Eigenvalues from trace and determinant (authored)",
            "problem": r"Find the eigenvalues and eigenvectors of $A = \begin{bmatrix}4 & 1\\ 2 & 3\end{bmatrix}$.",
            "steps": [
                {"text": "det(A - lambda I) = lambda^2 - 7 lambda + 10.", "tex": r"(\lambda - 5)(\lambda - 2) = 0"},
                {"text": "lambda = 5: (A - 5I)x = 0 has rows (-1, 1).", "tex": r"x_1 = (1, 1)"},
                {"text": "lambda = 2: rows (2, 1).", "tex": r"x_2 = (1, -2):\quad A x_2 = (2, -4) = 2x_2"}
            ],
            "answer": r"$\lambda = 5$ with $(1, 1)$ and $\lambda = 2$ with $(1, -2)$; the sum $7$ is the trace and the product $10$ the determinant."
        },
        "sources": {
            "video": [vs(40, 0, "n equations y' = Ay"),
                      vs(40, 60, "Try y = e^(lambda t) x"),
                      vs(40, 150, "Cancel e^(lambda t): Ax = lambda x"),
                      vs(40, 270, "Example y1' = 5y1 + y2, y2' = 3y1 + 3y2"),
                      vs(40, 420, "Eigenvector (1, 1), eigenvalue 6"),
                      vs(40, 510, "Eigenvector (1, -3), eigenvalue 2"),
                      vs(40, 600, "General solution and y(0)"),
                      vs(40, 720, "A squared: eigenvalues 36 and 4"),
                      vs(40, 900, "A^n x = lambda^n x"),
                      vs(40, 960, "A + cI: eigenvalues lambda + c"),
                      vs(40, 1080, "Caution about A + B")],
            "book": [bk(325, "Section 6.1: introduction to eigenvalues")]
        },
        "tutorNotes": "Video 40. y' = Ay, y = e^(lambda t) x gives Ax = lambda x. A = [5 1; 3 3]: lambda 6, x (1, 1); lambda 2, x (1, -3). y = c1 e^(6t)(1, 1) + c2 e^(2t)(1, -3). A^2: 36, 4; A^n x = lambda^n x; A + cI: lambda + c. Eigenvalues of A + B are not sums in general."
    },
    {
        "nav": "Diagonalizing, powers, Markov",
        "v": 41,
        "title": r"$A = V\Lambda V^{-1}$, powers $A^k$, and Markov matrices",
        "summary": r"Put the eigenvectors in the columns of $V$ and the eigenvalues in the diagonal $\Lambda$: $AV = V\Lambda$, so $A = V\Lambda V^{-1}$ and $A^k = V\Lambda^kV^{-1}$. For $u_{k+1} = Au_k$, write $u_0 = \sum c_ix_i$; then $u_k = \sum c_i\lambda_i^kx_i$. A Markov matrix has $\lambda = 1$ and its eigenvector is the steady state.",
        "time": [0, 697],
        "goals": [
            r"Build $V$ and $\Lambda$ and check $AV = V\Lambda$.",
            r"Compute $A^k$ from $V\Lambda^kV^{-1}$.",
            r"Solve $u_{k+1} = Au_k$ with $c = V^{-1}u_0$.",
            r"Find the steady state of a Markov matrix."
        ],
        "notes": [
            {"heading": "Diagonalization",
             "paragraphs": [
                 r"$A$ times each eigenvector column is $\lambda$ times that column: $AV = V\Lambda$ with $V = [x_1\ x_2\ \cdots]$ and $\Lambda = \operatorname{diag}(\lambda_1, \lambda_2, \ldots)$. If the $n$ eigenvectors are independent, $V$ is invertible and $V^{-1}AV = \Lambda$, $A = V\Lambda V^{-1}$.",
                 r"Then $A^2 = V\Lambda V^{-1}V\Lambda V^{-1} = V\Lambda^2V^{-1}$, and $A^k = V\Lambda^kV^{-1}$. Powers grow when some $|\lambda| > 1$, decay when every $|\lambda| < 1$, and $\lambda = 1$ gives a part that stays fixed. (A matrix without $n$ independent eigenvectors is called defective and cannot be diagonalized.)"
             ]},
            {"heading": "Difference equations",
             "paragraphs": [
                 r"$u_{k+1} = Au_k$ is the discrete twin of $y' = Ay$. Expand the start in eigenvectors, $u_0 = c_1x_1 + \cdots + c_nx_n$ (so $c = V^{-1}u_0$). Each piece is multiplied by its own $\lambda$ at each step: $u_k = c_1\lambda_1^kx_1 + \cdots + c_n\lambda_n^kx_n$."
             ]},
            {"heading": "Markov matrices",
             "paragraphs": [
                 r"$A = \begin{bmatrix}0.8 & 0.3\\ 0.2 & 0.7\end{bmatrix}$ has nonnegative entries and columns adding to $1$. Its characteristic equation is $\lambda^2 - 1.5\lambda + 0.5 = (\lambda - 1)(\lambda - \tfrac12)$. For $\lambda = 1$: $x_1 = (0.6, 0.4)$ (check: $0.48 + 0.12 = 0.6$). For $\lambda = \tfrac12$: $x_2 = (1, -1)$.",
                 r"So $u_k = c_1(0.6, 0.4) + c_2(\tfrac12)^k(1, -1) \to c_1(0.6, 0.4)$, the steady state. Google's PageRank is the steady state of a giant Markov matrix."
             ]}
        ],
        "keyIdeas": [
            r"$AV = V\Lambda$, $A = V\Lambda V^{-1}$.",
            r"$A^k = V\Lambda^kV^{-1}$.",
            r"$u_k = \sum c_i\lambda_i^kx_i$, $c = V^{-1}u_0$.",
            r"Markov: $\lambda = 1$ gives the steady state."
        ],
        "example": {
            "title": "Following a Markov chain (authored)",
            "problem": r"For the lecture's Markov matrix, find $u_k$ from $u_0 = (1, 0)$.",
            "steps": [
                {"text": "Expand u0 in the eigenvectors.", "tex": r"(1, 0) = 1\cdot(0.6, 0.4) + 0.4\cdot(1, -1)"},
                {"text": "Multiply each piece by lambda^k.", "tex": r"u_k = (0.6, 0.4) + 0.4\left(\tfrac12\right)^k(1, -1)"},
                {"text": "Let k grow.", "tex": r"u_k \to (0.6, 0.4)"}
            ],
            "answer": r"$u_k = (0.6, 0.4) + 0.4(\tfrac12)^k(1, -1)$; the second part halves each step and the chain settles at $(0.6, 0.4)$."
        },
        "sources": {
            "video": [vs(41, 0, "AV = V Lambda"),
                      vs(41, 270, "V^-1 A V = Lambda"),
                      vs(41, 330, "A = V Lambda V^-1"),
                      vs(41, 390, "A^2 and A^n"),
                      vs(41, 570, "Growth and decay of powers"),
                      vs(42, 0, "Need n independent eigenvectors"),
                      vs(42, 120, "u_(k+1) = A u_k"),
                      vs(42, 240, "Expand u0 in eigenvectors"),
                      vs(42, 480, "c = V^-1 u0"),
                      vs(42, 630, "Markov matrix [.8 .3; .2 .7]"),
                      vs(42, 840, "Steady state (.6, .4)"),
                      vs(42, 930, "PageRank")],
            "book": [bk(337, "Section 6.2: diagonalizing a matrix"),
                     bk(327, "Markov matrices in Section 6.1")]
        },
        "tutorNotes": "Videos 41-42. AV = V Lambda, A = V Lambda V^-1 (needs n independent eigenvectors), A^k = V Lambda^k V^-1. u_(k+1) = A u_k: u0 = sum c_i x_i, c = V^-1 u0, u_k = sum c_i lambda_i^k x_i. Markov A = [.8 .3; .2 .7]: lambda 1, x (.6, .4); lambda 1/2, x (1, -1); steady state c1 (.6, .4). PageRank."
    },
    {
        "nav": "Solving y' = Ay",
        "v": 43,
        "title": r"Solving $y' = Ay$ with eigenvectors",
        "summary": r"$y(t) = c_1e^{\lambda_1t}x_1 + \cdots + c_ne^{\lambda_nt}x_n$ with $c = V^{-1}y(0)$. Stability requires every $\operatorname{Re}\lambda < 0$; an eigenvalue $0$ gives a steady state. For $A = \begin{bmatrix}-1 & 2\\ 1 & -2\end{bmatrix}$, $\lambda = 0$ and $-3$, and solutions approach a multiple of $(2, 1)$.",
        "time": [0, 948],
        "goals": [
            r"Solve $y' = Ay$ from the eigenvalues and eigenvectors.",
            r"Relate stability to the real parts of the eigenvalues.",
            r"Use column sums: if every column of $A$ adds to $s$, then $s$ is an eigenvalue."
        ],
        "notes": [
            {"heading": "The solution",
             "paragraphs": [
                 r"Each eigenvector solution $e^{\lambda_it}x_i$ solves $y' = Ay$, and so does any combination. Matching $y(0) = c_1x_1 + \cdots + c_nx_n$ means $Vc = y(0)$. The parts with $\operatorname{Re}\lambda < 0$ die out; parts with $\operatorname{Re}\lambda > 0$ blow up. Stability needs every real part negative."
             ]},
            {"heading": "Example",
             "paragraphs": [
                 r"$A = \begin{bmatrix}-1 & 2\\ 1 & -2\end{bmatrix}$ has trace $-3$ and determinant $0$, so $\lambda = 0$ and $\lambda = -3$. For $\lambda = 0$: $Ax = 0$ gives $x_1 = (2, 1)$. For $\lambda = -3$: $x_2 = (1, -1)$. Then $y(t) = c_1(2, 1) + c_2e^{-3t}(1, -1) \to c_1(2, 1)$: a steady state (as for a Markov process in continuous time)."
             ]},
            {"heading": "Column and row sums",
             "paragraphs": [
                 r"Each column of this $A$ adds to $0$. In general, if every column adds to $s$, then $(1, \ldots, 1)A = s(1, \ldots, 1)$: $s$ is an eigenvalue of $A^T$, and $A$ and $A^T$ have the same eigenvalues (same determinant of $A - \lambda I$). If every row adds to $s$, then $A(1, \ldots, 1) = s(1, \ldots, 1)$ directly."
             ]}
        ],
        "keyIdeas": [
            r"$y = \sum c_ie^{\lambda_it}x_i$, $Vc = y(0)$.",
            r"Stable $\Leftrightarrow$ all $\operatorname{Re}\lambda_i < 0$.",
            r"$\lambda = 0$: a steady state.",
            r"Columns sum to $s$ $\Rightarrow$ $s$ is an eigenvalue."
        ],
        "example": {
            "title": "Fit an initial condition (authored)",
            "problem": r"Solve $y' = Ay$ for $A = \begin{bmatrix}4 & 1\\ 2 & 3\end{bmatrix}$ with $y(0) = (2, -1)$.",
            "steps": [
                {"text": "From Section 1: lambda = 5 with (1, 1), lambda = 2 with (1, -2).", "tex": r"y(0) = c_1(1, 1) + c_2(1, -2)"},
                {"text": "Solve c1 + c2 = 2, c1 - 2c2 = -1.", "tex": r"c_1 = 1,\quad c_2 = 1"},
                {"text": "Assemble.", "tex": r"y(t) = e^{5t}(1, 1) + e^{2t}(1, -2)"}
            ],
            "answer": r"$y(t) = e^{5t}(1, 1) + e^{2t}(1, -2)$; both eigenvalues are positive, so the system is unstable."
        },
        "sources": {
            "video": [vs(43, 0, "y' = Ay with n eigenvectors"),
                      vs(43, 180, "Stability: real parts negative"),
                      vs(43, 210, "Example [-1 2; 1 -2]"),
                      vs(43, 300, "lambda = 0 with (2, 1), lambda = -3 with (1, -1)"),
                      vs(43, 360, "y = c1 (2, 1) + c2 e^(-3t) (1, -1)"),
                      vs(43, 450, "Steady state"),
                      vs(43, 570, "Columns adding to the same number"),
                      vs(43, 630, "A and A transpose: same eigenvalues"),
                      vs(43, 780, "Rows adding to s: eigenvector of ones")],
            "book": [bk(349, "Section 6.3: linear systems y' = Ay")]
        },
        "tutorNotes": "Video 43. y = sum c_i e^(lambda_i t) x_i, Vc = y(0). Stable iff all Re lambda < 0. A = [-1 2; 1 -2]: trace -3, det 0, lambda 0 with (2, 1), lambda -3 with (1, -1); y -> c1 (2, 1). Columns summing to s: s eigenvalue (of A^T, same eigenvalues as A). Rows summing to s: A(1,...,1) = s(1,...,1)."
    },
    {
        "nav": "Matrix exponential, similar matrices",
        "v": 44,
        "title": r"$e^{At}$, and matrices with the same eigenvalues",
        "summary": r"$e^{At} = I + At + \tfrac12(At)^2 + \cdots$ solves $Y' = AY$ with $Y(0) = I$, so $y(t) = e^{At}y(0)$, even for defective $A$. With eigenvectors, $e^{At} = Ve^{\Lambda t}V^{-1}$. Similar matrices $B = M^{-1}AM$ share eigenvalues; but $e^Ae^B \neq e^{A+B}$ unless $AB = BA$.",
        "time": [0, 932],
        "goals": [
            r"Define $e^{At}$ by its series and differentiate it.",
            r"Compute $e^{At}$ for $A = \begin{bmatrix}0 & 1\\ 0 & 0\end{bmatrix}$.",
            r"Use $e^{At} = Ve^{\Lambda t}V^{-1}$ when $A$ has $n$ eigenvectors.",
            r"Explain why similar matrices have the same eigenvalues."
        ],
        "notes": [
            {"heading": "The series",
             "paragraphs": [
                 r"Copy the scalar series: $e^{At} = I + At + \dfrac{(At)^2}{2} + \dfrac{(At)^3}{6} + \cdots$. Differentiating term by term gives $A + A^2t + \tfrac12A^3t^2 + \cdots = Ae^{At}$. So $y(t) = e^{At}y(0)$ solves $y' = Ay$ for every square $A$, with or without a full set of eigenvectors."
             ]},
            {"heading": "Two ways to compute it",
             "paragraphs": [
                 r"With $A = V\Lambda V^{-1}$, every power is $V\Lambda^kV^{-1}$, so the series collapses to $e^{At} = Ve^{\Lambda t}V^{-1}$, where $e^{\Lambda t}$ is diagonal with entries $e^{\lambda_it}$.",
                 r"For the defective $A = \begin{bmatrix}0 & 1\\ 0 & 0\end{bmatrix}$ (double eigenvalue $0$, only one eigenvector $(1, 0)$), $A^2 = 0$ and the series stops: $e^{At} = I + At = \begin{bmatrix}1 & t\\ 0 & 1\end{bmatrix}$. In equations: $y_2' = 0$ keeps $y_2$ constant and $y_1' = y_2$ grows linearly, the factor $t$ again."
             ]},
            {"heading": "Similar matrices",
             "paragraphs": [
                 r"$B = M^{-1}AM$ for an invertible $M$ is similar to $A$. If $Bx = \lambda x$ then $A(Mx) = \lambda(Mx)$: the same eigenvalues, with eigenvectors $Mx$. Strang's family $\begin{bmatrix}2&3\\0&4\end{bmatrix}, \begin{bmatrix}2&0\\0&4\end{bmatrix}, \begin{bmatrix}4&0\\0&2\end{bmatrix}, \begin{bmatrix}0&2\\-4&6\end{bmatrix}$ all have $\lambda = 2, 4$ (trace $6$, determinant $8$).",
                 r"Matrices with a repeated eigenvalue can fail to be similar: $\begin{bmatrix}2&1\\0&2\end{bmatrix}$ is not similar to $2I$, since $M^{-1}(2I)M = 2I$ always. The best form for a defective matrix is the Jordan form.",
                 r"A caution: $e^Ae^B$, $e^Be^A$ and $e^{A+B}$ differ in general; they agree when $AB = BA$. Likewise $y' = a(t)y$ has solution $e^{\int a}$, but for matrices $y' = A(t)y$ this fails unless the $A(t)$ commute."
             ]}
        ],
        "keyIdeas": [
            r"$e^{At} = \sum (At)^k/k!$, $\tfrac{d}{dt}e^{At} = Ae^{At}$.",
            r"$e^{At} = Ve^{\Lambda t}V^{-1}$.",
            r"$\begin{bmatrix}0&1\\0&0\end{bmatrix}$: $e^{At} = \begin{bmatrix}1&t\\0&1\end{bmatrix}$.",
            r"$B = M^{-1}AM$: same eigenvalues."
        ],
        "example": {
            "title": "A rotation (authored)",
            "problem": r"Compute $e^{At}$ for $A = \begin{bmatrix}0 & 1\\ -1 & 0\end{bmatrix}$.",
            "steps": [
                {"text": "Powers repeat: A^2 = -I, A^3 = -A, A^4 = I.", "tex": r"e^{At} = I\left(1 - \frac{t^2}{2} + \cdots\right) + A\left(t - \frac{t^3}{6} + \cdots\right)"},
                {"text": "Recognise the cosine and sine series.", "tex": r"e^{At} = \cos t\,I + \sin t\,A"},
                {"text": "Write it out.", "tex": r"e^{At} = \begin{bmatrix}\cos t & \sin t\\ -\sin t & \cos t\end{bmatrix}"}
            ],
            "answer": r"A rotation matrix: $y(t) = e^{At}y(0)$ turns $y(0)$ clockwise at unit speed; the eigenvalues are $\pm i$."
        },
        "sources": {
            "video": [vs(44, 0, "e^(At) by its series"),
                      vs(44, 90, "Derivative is A e^(At)"),
                      vs(44, 210, "Works even without enough eigenvectors"),
                      vs(44, 240, "e^(At) = V e^(Lambda t) V^-1"),
                      vs(44, 570, "Example [0 1; 0 0]"),
                      vs(44, 690, "e^(At) = I + At"),
                      vs(44, 840, "A 3 by 3 example"),
                      vs(45, 0, "B = M^-1 A M: similar matrices"),
                      vs(45, 180, "A family with eigenvalues 2 and 4"),
                      vs(45, 450, "Jordan form [2 1; 0 2]"),
                      vs(45, 540, "e^A e^B and e^(A+B)"),
                      vs(45, 750, "Matrix y' = A(t) y")],
            "book": [bk(362, "Section 6.4: the exponential of a matrix"),
                     bk(365, "Similar matrices A and B")]
        },
        "tutorNotes": "Videos 44-45. e^(At) = I + At + (At)^2/2 + ..., d/dt e^(At) = A e^(At), y = e^(At) y(0) for any A. e^(At) = V e^(Lambda t) V^-1 with n eigenvectors. A = [0 1; 0 0]: A^2 = 0, e^(At) = [1 t; 0 1]. Similar B = M^-1 A M: same eigenvalues, eigenvectors Mx. Family [2 3; 0 4], [2 0; 0 4], [4 0; 0 2], [0 2; -4 6]: lambda 2, 4. [2 1; 0 2] not similar to 2I (Jordan form). e^A e^B != e^(A+B) unless AB = BA."
    },
    {
        "nav": "Symmetric and complex matrices",
        "v": 46,
        "title": r"Symmetric $S$: real eigenvalues, orthogonal eigenvectors",
        "summary": r"A symmetric matrix $S = S^T$ has real eigenvalues and perpendicular eigenvectors, so $S = Q\Lambda Q^T$ with an orthogonal $Q$. Antisymmetric matrices have imaginary eigenvalues; orthogonal matrices have $|\lambda| = 1$. Complex vectors need the conjugate in the length: $\|x\|^2 = \bar{x}^Tx$.",
        "time": [0, 955],
        "goals": [
            r"Find the eigenvalues and orthogonal eigenvectors of $\begin{bmatrix}3&1\\1&3\end{bmatrix}$.",
            r"Write $S = Q\Lambda Q^T$.",
            r"Find eigenvalues of antisymmetric and orthogonal matrices.",
            r"Measure complex vectors with $\bar{x}^Tx$."
        ],
        "notes": [
            {"heading": "Symmetric matrices",
             "paragraphs": [
                 r"$S = \begin{bmatrix}3 & 1\\ 1 & 3\end{bmatrix}$: $\lambda = 4$ with $(1, 1)$ and $\lambda = 2$ with $(1, -1)$. The eigenvalues are real and the eigenvectors are perpendicular: $(1,1)\cdot(1,-1) = 0$. This holds for every real symmetric matrix. Normalising the eigenvectors to unit length gives an orthogonal $Q$ ($Q^TQ = I$, so $Q^{-1} = Q^T$) and $S = Q\Lambda Q^T$."
             ]},
            {"heading": "Antisymmetric and orthogonal",
             "paragraphs": [
                 r"$A = \begin{bmatrix}0 & -1\\ 1 & 0\end{bmatrix}$ has $A^T = -A$. Its equation $\lambda^2 + 1 = 0$ gives $\lambda = \pm i$, with eigenvectors $(1, -i)$ and $(1, i)$: purely imaginary eigenvalues. Adding $3I$: $\begin{bmatrix}3 & -1\\ 1 & 3\end{bmatrix}$ has $\lambda = 3 \pm i$.",
                 r"The rotation by $45°$, $Q = \tfrac{1}{\sqrt2}\begin{bmatrix}1 & -1\\ 1 & 1\end{bmatrix}$, is orthogonal; its eigenvalues $\tfrac{1 \pm i}{\sqrt2}$ have absolute value $1$, as for every orthogonal matrix: $Q$ preserves lengths, so it cannot stretch an eigenvector."
             ]},
            {"heading": "Complex lengths",
             "paragraphs": [
                 r"For $\lambda = a + ib$, $|\lambda|^2 = \lambda\bar\lambda = a^2 + b^2$. For a complex vector the length squared is $\bar{x}^Tx = |x_1|^2 + \cdots + |x_n|^2$; plain $x^Tx$ can be zero, as for $(1, i)$. Complex matrices with $\bar{S}^T = S$ (Hermitian) behave like real symmetric ones: real eigenvalues, orthogonal eigenvectors."
             ]}
        ],
        "keyIdeas": [
            r"$S = S^T$: real $\lambda$, orthogonal $x$.",
            r"$S = Q\Lambda Q^T$, $Q^TQ = I$.",
            r"$A^T = -A$: imaginary $\lambda$; $Q^TQ = I$: $|\lambda| = 1$.",
            r"Complex length: $\bar{x}^Tx$."
        ],
        "example": {
            "title": "Spectral form of a symmetric matrix (authored)",
            "problem": r"Write $S = \begin{bmatrix}2 & 1\\ 1 & 2\end{bmatrix}$ as $Q\Lambda Q^T$.",
            "steps": [
                {"text": "Eigenvalues and eigenvectors.", "tex": r"\lambda = 3:\ (1, 1),\qquad \lambda = 1:\ (1, -1)"},
                {"text": "Normalise to unit length.", "tex": r"Q = \frac{1}{\sqrt2}\begin{bmatrix}1 & 1\\ 1 & -1\end{bmatrix}"},
                {"text": "Assemble.", "tex": r"S = Q\begin{bmatrix}3 & 0\\ 0 & 1\end{bmatrix}Q^T"}
            ],
            "answer": r"$S = Q\Lambda Q^T$ with $\Lambda = \operatorname{diag}(3, 1)$; the columns of $Q$ are perpendicular unit vectors."
        },
        "sources": {
            "video": [vs(46, 0, "Symmetric, antisymmetric, orthogonal"),
                      vs(46, 150, "S = [3 1; 1 3]: eigenvalues 2 and 4"),
                      vs(46, 240, "Orthogonal eigenvectors"),
                      vs(46, 330, "A = [0 -1; 1 0]: eigenvalues +-i"),
                      vs(46, 420, "Add 3I: 3 +- i"),
                      vs(46, 480, "Orthogonal Q: |lambda| = 1"),
                      vs(46, 570, "|lambda|^2 = a^2 + b^2"),
                      vs(46, 660, "Length of a complex vector")],
            "book": [bk(375, "Symmetric matrices: real eigenvalues, orthogonal eigenvectors"),
                     bk(377, "Complex and Hermitian matrices")]
        },
        "tutorNotes": "Video 46. S = [3 1; 1 3]: lambda 2 (1, -1), 4 (1, 1), orthogonal; S = Q Lambda Q^T. A = [0 -1; 1 0]: lambda +-i, eigenvectors (1, -i), (1, i). B = [3 -1; 1 3]: 3 +- i. Q = (1/sqrt2)[1 -1; 1 1]: (1 +- i)/sqrt2, |lambda| = 1. |lambda|^2 = a^2 + b^2; complex length x-bar^T x. Hermitian: real eigenvalues."
    },
    {
        "nav": "Second order systems",
        "v": 47,
        "title": r"Oscillating systems $My'' + Ky = 0$",
        "summary": r"Masses and springs give $My'' + Ky = 0$. Pure oscillations $y = (\cos\omega t)x$ require $Kx = \omega^2Mx$: the eigenvalues are squared frequencies, and the eigenvectors are the mode shapes. For $y'' + \tfrac{k}{m}\begin{bmatrix}2&-1\\-1&2\end{bmatrix}y = 0$ the modes are $(1, 1)$ with $\omega^2 = k/m$ and $(1, -1)$ with $\omega^2 = 3k/m$.",
        "time": [0, 1010],
        "goals": [
            r"Turn $My'' + Ky = 0$ into the eigenvalue problem $Kx = \omega^2Mx$.",
            r"Find the two modes of a two-mass system.",
            r"Write the solution from $y(0)$ and $y'(0)$ as a sum of modes."
        ],
        "notes": [
            {"heading": "Modes",
             "paragraphs": [
                 r"Newton's law for $n$ masses connected by springs is $My'' + Ky = 0$, with a diagonal mass matrix $M$ and a symmetric stiffness matrix $K$. Try $y = e^{i\omega t}x$: $-\omega^2Mx + Kx = 0$, that is $Kx = \omega^2Mx$. Each eigenvector $x_i$ is a mode shape, and $\omega_i$ its frequency.",
                 r"Since there are $2n$ initial values ($y(0)$ and $y'(0)$), the solution is $y(t) = \sum (A_i\cos\omega_it + B_i\sin\omega_it)\,x_i$. Starting from rest ($y'(0) = 0$) all $B_i = 0$."
             ]},
            {"heading": "Two masses",
             "paragraphs": [
                 r"Equal masses $m$ between three springs $k$ (fixed at both ends): $y'' + \tfrac{k}{m}\begin{bmatrix}2 & -1\\ -1 & 2\end{bmatrix}y = 0$. The matrix has trace $4$ and determinant $3$, so its eigenvalues are $1$ and $3$, giving $\omega^2 = k/m$ and $3k/m$. The slow mode $(1, 1)$ moves both masses together; the fast mode $(1, -1)$ moves them against each other.",
                 r"From rest: $y(t) = A_1\cos\left(\sqrt{k/m}\,t\right)(1, 1) + A_2\cos\left(\sqrt{3k/m}\,t\right)(1, -1)$."
             ]}
        ],
        "keyIdeas": [
            r"$My'' + Ky = 0$, $y = e^{i\omega t}x$ $\Rightarrow$ $Kx = \omega^2Mx$.",
            r"Eigenvalues = squared frequencies; eigenvectors = mode shapes.",
            r"$\begin{bmatrix}2&-1\\-1&2\end{bmatrix}$: $1$ with $(1,1)$, $3$ with $(1,-1)$.",
            r"$y = \sum(A_i\cos\omega_it + B_i\sin\omega_it)x_i$."
        ],
        "example": {
            "title": "Pull one mass and let go (authored)",
            "problem": r"With $k/m = 1$, solve $y'' + \begin{bmatrix}2&-1\\-1&2\end{bmatrix}y = 0$ from $y(0) = (1, 0)$, $y'(0) = 0$.",
            "steps": [
                {"text": "Expand y(0) in the modes.", "tex": r"(1, 0) = \tfrac12(1, 1) + \tfrac12(1, -1)"},
                {"text": "Each mode oscillates at its own frequency (from rest: cosines).", "tex": r"\omega_1 = 1,\qquad \omega_2 = \sqrt3"},
                {"text": "Assemble.", "tex": r"y(t) = \tfrac12\cos t\,(1, 1) + \tfrac12\cos\sqrt3 t\,(1, -1)"}
            ],
            "answer": r"$y_1 = \tfrac12(\cos t + \cos\sqrt3t)$ and $y_2 = \tfrac12(\cos t - \cos\sqrt3t)$: the energy moves back and forth between the masses."
        },
        "sources": {
            "video": [vs(47, 0, "M y'' + K y = 0"),
                      vs(47, 150, "y = e^(i omega t) x gives K x = omega^2 M x"),
                      vs(47, 270, "2n initial conditions"),
                      vs(47, 330, "Masses and springs picture"),
                      vs(47, 660, "Solution as a sum of modes"),
                      vs(47, 690, "Example (k/m)[2 -1; -1 2]"),
                      vs(47, 780, "Eigenvalues k/m and 3k/m"),
                      vs(47, 870, "Start from rest: cosines")],
            "book": [bk(372, "Section 6.5: second order systems and symmetric matrices")]
        },
        "tutorNotes": "Video 47. M y'' + K y = 0; y = e^(i omega t) x gives K x = omega^2 M x; eigenvalues are omega^2, eigenvectors are mode shapes. y = sum (A_i cos omega_i t + B_i sin omega_i t) x_i; from rest B_i = 0. Example y'' + (k/m)[2 -1; -1 2] y = 0: omega^2 = k/m with (1, 1), 3k/m with (1, -1)."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-trial", r"Why does $y = e^{\lambda t}x$ lead to $Ax = \lambda x$ for $y' = Ay$?", [
        (r"$y' = \lambda e^{\lambda t}x$ and $Ay = e^{\lambda t}Ax$; cancelling $e^{\lambda t}$ leaves $\lambda x = Ax$.", True, r"Right. The scalar exponential is never zero, so it cancels."),
        (r"Because $A$ is diagonal.", False, r"No. $A$ can be any square matrix."),
        (r"Because $x$ must be the zero vector.", False, r"No. $x = 0$ gives only the zero solution; eigenvectors are nonzero."),
        (r"Because $\lambda$ is always $1$.", False, r"No. $\lambda$ is whatever number makes $A - \lambda I$ singular.")]),
    q("q-eig", r"$A = \begin{bmatrix}5 & 1\\ 3 & 3\end{bmatrix}$. Which pair is an eigenvalue and eigenvector?", [
        (r"$\lambda = 2$, $x = (1, -3)$", True, r"Right. $A(1, -3) = (2, -6) = 2(1, -3)$."),
        (r"$\lambda = 6$, $x = (1, -1)$", False, r"No. $A(1, -1) = (4, 0)$, not a multiple of $(1, -1)$."),
        (r"$\lambda = 5$, $x = (1, 0)$", False, r"No. $A(1, 0) = (5, 3)$."),
        (r"$\lambda = 2$, $x = (1, 1)$", False, r"No. $A(1, 1) = (6, 6) = 6(1, 1)$.")]),
    q("q-power", r"If $Ax = 3x$, what is $(A^2 + 2I)x$?", [
        (r"$11x$", True, r"Right. $A^2x = 9x$ and $2Ix = 2x$."),
        (r"$5x$", False, r"No. $A^2$ squares the eigenvalue: $9$, not $3$."),
        (r"$9x$", False, r"No. Add the $2x$ from $2I$."),
        (r"$(3 + 2)^2x$", False, r"No. That would be $(A + 2I)^2$.")]),
    q("q-diag", r"With $A = V\Lambda V^{-1}$, what is $A^{10}$?", [
        (r"$V\Lambda^{10}V^{-1}$", True, r"Right. Inner $V^{-1}V$ pairs cancel."),
        (r"$V^{10}\Lambda^{10}V^{-10}$", False, r"No. The $V$ and $V^{-1}$ cancel between factors; they are not raised to powers."),
        (r"$\Lambda^{10}$", False, r"No. That is $V^{-1}A^{10}V$, not $A^{10}$."),
        (r"$10\,V\Lambda V^{-1}$", False, r"No. Powers multiply, they do not add.")]),
    q("q-markov", r"For the Markov matrix $\begin{bmatrix}0.8 & 0.3\\ 0.2 & 0.7\end{bmatrix}$, where does $u_k$ go?", [
        (r"To a multiple of $(0.6, 0.4)$, the eigenvector for $\lambda = 1$", True, r"Right. The $\lambda = \tfrac12$ part shrinks to zero."),
        (r"To zero", False, r"No. The eigenvalue $1$ part stays."),
        (r"To infinity", False, r"No. No eigenvalue exceeds $1$ in size."),
        (r"It oscillates forever", False, r"No. Both eigenvalues are real and positive.")]),
    q("q-stable", r"Which $y' = Ay$ has every solution approaching $0$?", [
        (r"Eigenvalues $-1$ and $-3$", True, r"Right. Both exponentials decay."),
        (r"Eigenvalues $0$ and $-3$", False, r"No. The $\lambda = 0$ part stays constant: a steady state, not $0$."),
        (r"Eigenvalues $-1 \pm 2i$ and $1$", False, r"No. The eigenvalue $1$ grows."),
        (r"Eigenvalues $\pm 2i$", False, r"No. Pure oscillation does not decay.")]),
    q("q-expm", r"What is $e^{At}$ for $A = \begin{bmatrix}0 & 1\\ 0 & 0\end{bmatrix}$?", [
        (r"$\begin{bmatrix}1 & t\\ 0 & 1\end{bmatrix}$", True, r"Right. $A^2 = 0$, so the series stops at $I + At$."),
        (r"$\begin{bmatrix}1 & e^t\\ 0 & 1\end{bmatrix}$", False, r"No. Entries of $e^{At}$ are not exponentials of entries of $A$."),
        (r"$\begin{bmatrix}e^0 & e^t\\ e^0 & e^0\end{bmatrix}$", False, r"No. Same mistake: exponentiate the matrix, not each entry."),
        (r"It does not exist: $A$ has only one eigenvector.", False, r"No. The series defines $e^{At}$ for every square matrix.")]),
    q("q-similar", r"Why do $A$ and $B = M^{-1}AM$ have the same eigenvalues?", [
        (r"If $Bx = \lambda x$, then $A(Mx) = \lambda(Mx)$.", True, r"Right. Multiply $M^{-1}AMx = \lambda x$ by $M$."),
        (r"Because $M$ is diagonal.", False, r"No. $M$ is any invertible matrix."),
        (r"Because $A = B$.", False, r"No. Similar matrices are usually different."),
        (r"They do not; only the determinants agree.", False, r"No. All eigenvalues agree (and so trace and determinant).")]),
    q("q-sym", r"What is true for every real symmetric matrix?", [
        (r"Real eigenvalues and perpendicular eigenvectors", True, r"Right. Hence $S = Q\Lambda Q^T$ with orthogonal $Q$."),
        (r"All eigenvalues positive", False, r"No. $\begin{bmatrix}0&1\\1&0\end{bmatrix}$ has $\lambda = \pm1$; positive eigenvalues define positive definite matrices (Unit 9)."),
        (r"Imaginary eigenvalues", False, r"No. That is for antisymmetric matrices."),
        (r"$|\lambda| = 1$", False, r"No. That is for orthogonal matrices.")]),
    q("q-modes", r"For $y'' + \begin{bmatrix}2&-1\\-1&2\end{bmatrix}y = 0$, what are the two frequencies?", [
        (r"$1$ and $\sqrt3$", True, r"Right. Eigenvalues $1$ and $3$ are $\omega^2$."),
        (r"$1$ and $3$", False, r"No. The eigenvalues are the squares of the frequencies."),
        (r"$2$ and $2$", False, r"No. Those are the diagonal entries."),
        (r"$\sqrt2$ and $\sqrt2$", False, r"No. The off-diagonal coupling splits the frequencies.")]),
]

EXPLORER = {
    "modes": [
        {"id": "eig", "label": "Ax against x"},
        {"id": "powers", "label": "Powers u(k+1) = A u(k)"},
        {"id": "flow", "label": "y' = A y and e^(At)"}
    ],
    "defaultMode": "eig",
    "a": {"min": -3, "max": 6, "step": 0.1, "default": 5},
    "b": {"min": -3, "max": 6, "step": 0.1, "default": 1},
    "c": {"min": -3, "max": 6, "step": 0.1, "default": 3},
    "d": {"min": -3, "max": 6, "step": 0.1, "default": 3},
    "steps": 12,
    "tMax": 3,
    "presets": [
        {"id": "lec40", "label": "[5 1; 3 3]", "mode": "eig", "a": 5, "b": 1, "c": 3, "d": 3,
         "note": "Section 1: eigenvalues $6$ and $2$, eigenvectors $(1,1)$ and $(1,-3)$."},
        {"id": "markov", "label": "Markov [.8 .3; .2 .7]", "mode": "powers", "a": 0.8, "b": 0.3, "c": 0.2, "d": 0.7,
         "note": "Section 2: $u_k \\to$ a multiple of $(0.6, 0.4)$."},
        {"id": "lec43", "label": "[-1 2; 1 -2]", "mode": "flow", "a": -1, "b": 2, "c": 1, "d": -2,
         "note": "Section 3: $\\lambda = 0, -3$; solutions settle on the line through $(2, 1)$."},
        {"id": "shear", "label": "Defective [0 1; 0 0]", "mode": "flow", "a": 0, "b": 1, "c": 0, "d": 0,
         "note": "Section 4: $e^{At} = I + At$, only one eigenvector."},
        {"id": "rot", "label": "Rotation [0 1; -1 0]", "mode": "flow", "a": 0, "b": 1, "c": -1, "d": 0,
         "note": "Section 4 example: $e^{At}$ is a rotation, $\\lambda = \\pm i$."},
        {"id": "sym", "label": "Symmetric [3 1; 1 3]", "mode": "eig", "a": 3, "b": 1, "c": 1, "d": 3,
         "note": "Section 5: perpendicular eigenvectors $(1,1)$, $(1,-1)$."}
    ],
    "tutorContext": "Three modes for a 2x2 matrix A = [a b; c d] (entries from -3 to 6). Ax against x: a unit vector x sweeps the circle (animation or angle slider) and Ax is drawn; eigenvectors are where Ax is parallel to x, and the ellipse traced by Ax is shown; readouts give the eigenvalues (real or complex), eigenvectors, trace, determinant, and V, Lambda when A is diagonalizable (otherwise 'defective'). Powers: u_(k+1) = A u_k for k = 0..12 from a chosen u0, with the eigenvector decomposition u_k = sum c_i lambda_i^k x_i. Flow: y' = A y with e^(At) computed in closed form (e^(st)[cosh(qt) I + sinh(qt)/q (A - sI)], s = trace/2, q^2 = s^2 - det, cos/sin when q^2 < 0, I + t(A - sI) when q = 0), trajectories from several starts, and the matrix e^(At) at the chosen time."
}

COURSE = {
    "version": 1,
    "title": "Eigenvalues and Linear Systems y' = Ay",
    "subtitle": "Unit 8 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 40-47, with Strang's Differential Equations and Linear Algebra, Chapter 6",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 40-47", "duration": "2:07:28", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 6",
             "edition": "Wellesley-Cambridge Press, 2014 (Chapter 6)", "onlineUrl": "",
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
