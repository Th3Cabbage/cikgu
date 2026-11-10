"""Source of courses/mit-de/positive-definite-svd/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\positive-definite-svd\\course_source.py

Unit 9 of the MIT Learn Differential Equations companion: playlist videos 48-49 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Section 7.2.
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
    (48, "ojUQk_GNQbQ", "Positive Definite Matrices", "21:41"),
    (49, "mBcLRGuAFUk", "Singular Value Decomposition (the SVD)", "14:11"),
]

SECTIONS = [
    {
        "nav": "Positive definite matrices",
        "v": 48,
        "title": r"Symmetric matrices with positive eigenvalues; $S = A^TA$",
        "summary": r"Oscillation $y'' + Sy = 0$ needs the eigenvalues $\lambda = \omega^2$ of the symmetric $S$ to be nonnegative. $S$ is positive definite when all its eigenvalues are positive, semidefinite when they are $\ge 0$. Every $A^TA$ is at least semidefinite, because $x^TA^TAx = \|Ax\|^2$.",
        "time": [0, 270],
        "goals": [
            r"Explain why $y'' + Sy = 0$ needs $\lambda \ge 0$.",
            r"Define positive definite and positive semidefinite.",
            r"Show that the eigenvalues of $A^TA$ are $\ge 0$."
        ],
        "notes": [
            {"heading": "Why positive eigenvalues matter",
             "paragraphs": [
                 r"In $y'' + Sy = 0$, try $y = e^{i\omega t}x$: $-\omega^2x + Sx = 0$, so $Sx = \omega^2x$. A real frequency $\omega$ needs $\lambda = \omega^2 \ge 0$. A negative eigenvalue would give $e^{\pm\sqrt{-\lambda}t}$, exponential growth instead of oscillation.",
                 r"$S$ is positive definite if it is symmetric and every eigenvalue is positive; positive semidefinite if every eigenvalue is $\ge 0$ (zero allowed)."
             ]},
            {"heading": "Every A transpose A",
             "paragraphs": [
                 r"$S = A^TA$ is symmetric for any rectangular $A$. If $Sx = \lambda x$, multiply by $x^T$: $x^TA^TAx = \lambda x^Tx$. The left side is $(Ax)^T(Ax) = \|Ax\|^2 \ge 0$ and $x^Tx > 0$, so $\lambda \ge 0$. If the columns of $A$ are independent, $Ax \neq 0$ for $x \neq 0$ and every $\lambda > 0$: $A^TA$ is positive definite."
             ]}
        ],
        "keyIdeas": [
            r"$y'' + Sy = 0$: $\lambda = \omega^2 \ge 0$.",
            r"Positive definite: $S = S^T$, all $\lambda > 0$.",
            r"$x^TA^TAx = \|Ax\|^2 \ge 0$.",
            r"Independent columns $\Rightarrow$ $A^TA$ positive definite."
        ],
        "example": {
            "title": "A transpose A (authored)",
            "problem": r"For $A = \begin{bmatrix}1 & 2\\ 0 & 1\\ 1 & 0\end{bmatrix}$, find $S = A^TA$ and its eigenvalues.",
            "steps": [
                {"text": "Dot products of the columns (1, 0, 1) and (2, 1, 0).", "tex": r"S = \begin{bmatrix}2 & 2\\ 2 & 5\end{bmatrix}"},
                {"text": "Trace 7, determinant 6.", "tex": r"\lambda^2 - 7\lambda + 6 = 0 \;\Rightarrow\; \lambda = 1,\ 6"},
                {"text": "Both positive, as the independent columns guarantee.", "tex": r"S \text{ is positive definite}"}
            ],
            "answer": r"$S = \begin{bmatrix}2&2\\2&5\end{bmatrix}$ with eigenvalues $1$ and $6$."
        },
        "sources": {
            "video": [vs(48, 0, "y'' + Sy = 0 needs lambda = omega^2 >= 0"),
                      vs(48, 60, "Positive definite and semidefinite"),
                      vs(48, 90, "S = A transpose A"),
                      vs(48, 150, "x^T A^T A x = ||Ax||^2")],
            "book": [bk(396, "Section 7.2: positive definite matrices and the SVD")]
        },
        "tutorNotes": "Video 48, first part. y'' + Sy = 0, y = e^(i omega t) x: Sx = omega^2 x, need lambda >= 0. Positive definite: symmetric, all lambda > 0; semidefinite: lambda >= 0. S = A^T A: x^T A^T A x = ||Ax||^2 >= 0 so lambda >= 0; independent columns give lambda > 0."
    },
    {
        "nav": "Five tests and the energy",
        "v": 48,
        "title": r"Five equivalent tests, and the energy bowl $x^TSx$",
        "summary": r"For symmetric $S$ these are equivalent: all eigenvalues $> 0$; all pivots $> 0$; all upper-left determinants $> 0$; $S = A^TA$ with independent columns; energy $x^TSx > 0$ for every $x \neq 0$. For $S = \begin{bmatrix}4&6\\6&10\end{bmatrix}$ the energy $4x_1^2 + 12x_1x_2 + 10x_2^2$ is a bowl with its minimum at the origin.",
        "time": [270, 1301],
        "goals": [
            r"Apply all five tests to a $2\times2$ matrix.",
            r"Write the energy $x^TSx$ as a quadratic.",
            r"Picture positive definite energy as a bowl.",
            r"Test a $3\times3$ correlation matrix with determinants."
        ],
        "notes": [
            {"heading": "Five tests",
             "paragraphs": [
                 r"$S = \begin{bmatrix}4 & 6\\ 6 & 10\end{bmatrix}$. (1) Eigenvalues: trace $14$, determinant $4$, both roots positive. (2) Pivots: elimination subtracts $\tfrac32$ of row 1 from row 2, leaving pivots $4$ and $10 - 9 = 1$. (3) Upper-left determinants: $4$ and $40 - 36 = 4$. (4) $S = A^TA$ for an $A$ with independent columns, for instance from elimination ($S = LDL^T$ gives $A = \sqrt{D}L^T$). (5) Energy: $x^TSx > 0$ for $x \neq 0$.",
                 r"The tests agree for every symmetric matrix; use whichever is easiest. In practice the pivots (elimination) are the fastest."
             ]},
            {"heading": "Energy",
             "paragraphs": [
                 r"$x^TSx = 4x_1^2 + 12x_1x_2 + 10x_2^2$ (the off-diagonal $6$ appears twice). At $x = (1, 1)$: $4 + 12 + 10 = 26$; at $x = (1, -1)$: $4 - 12 + 10 = 2$. Completing the square, $4(x_1 + \tfrac32x_2)^2 + x_2^2$: the pivots $4$ and $1$ appear as the coefficients, and both squares are positive.",
                 r"The graph of the energy is a bowl opening upward with its minimum at $x = 0$; its level curves are ellipses whose axes are the eigenvectors. This is the second-derivative test for a minimum in two variables."
             ]},
            {"heading": "A 3 by 3 test",
             "paragraphs": [
                 r"A correlation matrix $\begin{bmatrix}1 & a & b\\ a & 1 & c\\ b & c & 1\end{bmatrix}$ is positive definite when its upper-left determinants are positive: $1 > 0$, $1 - a^2 > 0$, and $1 + 2abc - a^2 - b^2 - c^2 > 0$."
             ]}
        ],
        "keyIdeas": [
            r"Tests: $\lambda > 0$; pivots $> 0$; leading determinants $> 0$; $S = A^TA$; $x^TSx > 0$.",
            r"$\begin{bmatrix}4&6\\6&10\end{bmatrix}$: pivots $4, 1$; determinants $4, 4$.",
            r"Energy $= 4(x_1 + \tfrac32x_2)^2 + x_2^2$.",
            r"Positive definite energy: a bowl, elliptic level curves."
        ],
        "example": {
            "title": "A matrix that fails (authored)",
            "problem": r"Is $S = \begin{bmatrix}3 & 4\\ 4 & 5\end{bmatrix}$ positive definite? Find an $x$ with negative energy.",
            "steps": [
                {"text": "Upper-left determinants.", "tex": r"3 > 0,\qquad 15 - 16 = -1 < 0"},
                {"text": "Pivots: 3 and 5 - 16/3.", "tex": r"5 - \tfrac{16}{3} = -\tfrac13 < 0"},
                {"text": "Energy at x = (4, -3).", "tex": r"3\cdot16 - 2\cdot4\cdot12 + 5\cdot9 = 48 - 96 + 45 = -3"}
            ],
            "answer": r"No: the determinant and the second pivot are negative, and $x = (4, -3)$ has energy $-3$. The energy surface is a saddle, not a bowl."
        },
        "sources": {
            "video": [vs(48, 270, "Five tests on S = [4 6; 6 10]"),
                      vs(48, 390, "Eigenvalues positive"),
                      vs(48, 450, "Pivots 4 and 1"),
                      vs(48, 510, "Upper-left determinants 4 and 4"),
                      vs(48, 570, "S = A transpose A"),
                      vs(48, 660, "Energy x^T S x > 0"),
                      vs(48, 720, "4x1^2 + 12 x1 x2 + 10 x2^2"),
                      vs(48, 840, "x = (1, 1) gives 26"),
                      vs(48, 930, "The bowl and its minimum"),
                      vs(48, 1020, "Correlation matrix test")],
            "book": [bk(397, "Tests for positive definite matrices"),
                     bk(396, "Energy x^T S x")]
        },
        "tutorNotes": "Video 48. Five equivalent tests for symmetric S: eigenvalues > 0, pivots > 0, upper-left determinants > 0, S = A^T A with independent columns, energy x^T S x > 0 for x != 0. S = [4 6; 6 10]: trace 14, det 4, pivots 4 and 1, determinants 4 and 4; energy 4x1^2 + 12x1x2 + 10x2^2 = 4(x1 + 1.5 x2)^2 + x2^2; x = (1,1) gives 26, (1,-1) gives 2. Bowl, elliptic level curves. Correlation matrix [1 a b; a 1 c; b c 1]: 1 - a^2 > 0, 1 + 2abc - a^2 - b^2 - c^2 > 0."
    },
    {
        "nav": "The SVD",
        "v": 49,
        "title": r"The singular value decomposition $A = U\Sigma V^T$",
        "summary": r"Every matrix, even rectangular, factors as $A = U\Sigma V^T$: rotate or reflect ($V^T$), stretch ($\Sigma$, the singular values $\sigma_i \ge 0$), rotate ($U$). The $v$'s are eigenvectors of $A^TA$, the $u$'s eigenvectors of $AA^T$, and $\sigma_i^2$ are their eigenvalues. $A = \sigma_1u_1v_1^T + \sigma_2u_2v_2^T + \cdots$, and the first piece carries the most information.",
        "time": [0, 851],
        "goals": [
            r"Describe $A = U\Sigma V^T$ as rotate (or reflect), stretch, rotate (or reflect).",
            r"Find $V$ and $\sigma$ from $A^TA$, and $U$ from $Av_i = \sigma_iu_i$.",
            r"Compute the SVD of a singular $2\times2$ matrix.",
            r"Write $A$ as a sum of rank-one pieces and explain their use for data."
        ],
        "notes": [
            {"heading": "Rotate, stretch, rotate (or reflect)",
             "paragraphs": [
                 r"Eigenvectors need a square matrix and may fail to be orthogonal. The SVD works for every $m\times n$ matrix with orthogonal matrices on both sides: $A = U\Sigma V^T$ with $U$ ($m\times m$) and $V$ ($n\times n$) orthogonal and $\Sigma$ ($m\times n$) diagonal with $\sigma_1 \ge \sigma_2 \ge \cdots \ge 0$. Geometrically, $A$ turns the unit circle into an ellipse: $V^T$ turns the plane, $\Sigma$ stretches along the axes, $U$ turns it again. Each orthogonal factor is a rotation or a reflection: for $A = \mathrm{diag}(1, -1)$, which flips the plane, no pair of rotations can do it, and $U$ (or $V$) must be a reflection."
             ]},
            {"heading": "Where U, Sigma and V come from",
             "paragraphs": [
                 r"$A^TA = V\Sigma^TU^TU\Sigma V^T = V(\Sigma^T\Sigma)V^T$: this is the diagonalization of the symmetric semidefinite $A^TA$. So the $v$'s are its orthonormal eigenvectors and $\sigma_i^2$ its eigenvalues. Likewise $AA^T = U(\Sigma\Sigma^T)U^T$ gives the $u$'s. In practice, find $v_i$ and $\sigma_i$ from $A^TA$ and then $u_i = Av_i/\sigma_i$ for $\sigma_i > 0$."
             ]},
            {"heading": "The lecture's example",
             "paragraphs": [
                 r"$A = \begin{bmatrix}2 & 2\\ 1 & 1\end{bmatrix}$ is singular (rank $1$). $A^TA = \begin{bmatrix}5 & 5\\ 5 & 5\end{bmatrix}$ has eigenvalues $10$ and $0$, so $\sigma_1 = \sqrt{10}$, $\sigma_2 = 0$, with $v_1 = (1, 1)/\sqrt2$, $v_2 = (1, -1)/\sqrt2$. Then $u_1 = Av_1/\sigma_1 = (2, 1)/\sqrt5$, and $u_2 = (-1, 2)/\sqrt5$ completes an orthonormal basis.",
                 r"Note: on the board the matrix is first written with a $-1$ and then corrected to make it singular; the lower-left entry of $U$ keeps the old sign there. For the singular $A$, $u_1 = (2, 1)/\sqrt5$."
             ]},
            {"heading": "Rank-one pieces and data",
             "paragraphs": [
                 r"Multiplying out, $A = \sigma_1u_1v_1^T + \sigma_2u_2v_2^T + \cdots$, a sum of rank-one matrices ordered by importance. For a data matrix (say, gene expressions: genes $\times$ people), the first piece $\sigma_1u_1v_1^T$ captures the strongest pattern linking a combination of genes to a combination of people. Keeping only the largest few pieces is principal component analysis."
             ]}
        ],
        "keyIdeas": [
            r"$A = U\Sigma V^T$: rotate or reflect, stretch, rotate or reflect.",
            r"$A^TA = V\Sigma^T\Sigma V^T$: $\sigma_i^2$ are its eigenvalues.",
            r"$u_i = Av_i/\sigma_i$.",
            r"$A = \sum\sigma_iu_iv_i^T$; $\sigma_1u_1v_1^T$ is the most important piece."
        ],
        "example": {
            "title": "SVD of an invertible matrix (authored)",
            "problem": r"Find the SVD of $A = \begin{bmatrix}3 & 0\\ 4 & 5\end{bmatrix}$.",
            "steps": [
                {"text": "A^T A and its eigenvalues.", "tex": r"A^TA = \begin{bmatrix}25 & 20\\ 20 & 25\end{bmatrix}:\ \sigma_1^2 = 45,\ \sigma_2^2 = 5"},
                {"text": "Right singular vectors.", "tex": r"v_1 = \tfrac{1}{\sqrt2}(1, 1),\qquad v_2 = \tfrac{1}{\sqrt2}(1, -1)"},
                {"text": "Left singular vectors u = Av / sigma.", "tex": r"u_1 = \tfrac{1}{\sqrt{10}}(1, 3),\qquad u_2 = \tfrac{1}{\sqrt{10}}(3, -1)"}
            ],
            "answer": r"$\sigma_1 = 3\sqrt5$, $\sigma_2 = \sqrt5$; their product $15 = |\det A|$."
        },
        "sources": {
            "video": [vs(49, 0, "A = U Sigma V^T for any matrix"),
                      vs(49, 60, "Rotate, stretch, rotate"),
                      vs(49, 180, "A^T A = V Sigma^T Sigma V^T"),
                      vs(49, 300, "Sigma squared are eigenvalues of A^T A"),
                      vs(49, 330, "A A^T gives U"),
                      vs(49, 390, "Example [2 2; 1 1]"),
                      vs(49, 480, "Singular values sqrt 10 and 0"),
                      vs(49, 540, "Data matrices: genes and people"),
                      vs(49, 660, "The first rank-one piece")],
            "book": [bk(398, "The singular value decomposition"),
                     bk(399, "Rank-one pieces and principal components")]
        },
        "tutorNotes": "Video 49. A = U Sigma V^T for any m x n A: U, V orthogonal, Sigma diagonal sigma1 >= sigma2 >= ... >= 0; rotate/reflect-stretch-rotate. A^T A = V Sigma^T Sigma V^T (v's, sigma^2), A A^T = U Sigma Sigma^T U^T (u's); u_i = A v_i / sigma_i. Example A = [2 2; 1 1] (singular; board first had a -1): sigma = sqrt10, 0; v1 = (1,1)/sqrt2, v2 = (1,-1)/sqrt2; u1 = (2,1)/sqrt5, u2 = (-1,2)/sqrt5. A = sum sigma_i u_i v_i^T; first piece most important (gene expression data, PCA)."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-why", r"Why does $y'' + Sy = 0$ oscillate only when the eigenvalues of $S$ are $\ge 0$?", [
        (r"$Sx = \omega^2x$, and a real frequency $\omega$ needs $\omega^2 \ge 0$.", True, r"Right. A negative eigenvalue gives exponential growth $e^{\sqrt{-\lambda}t}$."),
        (r"Because $S$ must be diagonal.", False, r"No. Any symmetric $S$ works."),
        (r"Because $\det S$ must be $1$.", False, r"No. Only the signs of the eigenvalues matter."),
        (r"Because $y''$ is always positive.", False, r"No. $y''$ changes sign as $y$ oscillates.")]),
    q("q-ata", r"Why are the eigenvalues of $A^TA$ never negative?", [
        (r"$x^TA^TAx = \|Ax\|^2 \ge 0$, and this equals $\lambda\|x\|^2$ for an eigenvector.", True, r"Right. A squared length cannot be negative."),
        (r"Because $A^TA$ is diagonal.", False, r"No. $A^TA$ is symmetric, not usually diagonal."),
        (r"Because $A$ has positive entries.", False, r"No. Entries of any sign give the same conclusion."),
        (r"Because $\det(A^TA) = 1$.", False, r"No. Its determinant is $(\det A)^2$ for square $A$, which can be anything $\ge 0$.")]),
    q("q-pivots", r"What are the pivots of $\begin{bmatrix}4 & 6\\ 6 & 10\end{bmatrix}$?", [
        (r"$4$ and $1$", True, r"Right. $10 - \tfrac{6}{4}\cdot6 = 1$."),
        (r"$4$ and $10$", False, r"No. Elimination changes the second diagonal entry."),
        (r"$4$ and $4$", False, r"No. $4$ and $4$ are the upper-left determinants."),
        (r"$2$ and $12$", False, r"No. Those are close to the eigenvalues ($7 \pm 3\sqrt5$), not pivots.")]),
    q("q-energy", r"For $S = \begin{bmatrix}4 & 6\\ 6 & 10\end{bmatrix}$, what is the energy at $x = (1, -1)$?", [
        (r"$2$", True, r"Right. $4 - 12 + 10$."),
        (r"$26$", False, r"No. That is at $x = (1, 1)$."),
        (r"$-2$", False, r"No. Positive definite energy is never negative."),
        (r"$14$", False, r"No. The cross term $12x_1x_2$ is $-12$ here.")]),
    q("q-fail", r"Which symmetric matrix is NOT positive definite?", [
        (r"$\begin{bmatrix}3 & 4\\ 4 & 5\end{bmatrix}$", True, r"Right. Its determinant is $15 - 16 = -1$."),
        (r"$\begin{bmatrix}2 & 1\\ 1 & 2\end{bmatrix}$", False, r"No. Determinants $2$ and $3$, eigenvalues $1$ and $3$."),
        (r"$\begin{bmatrix}4 & 6\\ 6 & 10\end{bmatrix}$", False, r"No. Pivots $4$ and $1$."),
        (r"$\begin{bmatrix}1 & 0\\ 0 & 5\end{bmatrix}$", False, r"No. A diagonal matrix with positive entries.")]),
    q("q-bowl", r"What does the graph of a positive definite energy $x^TSx$ look like?", [
        (r"A bowl with its minimum at the origin, elliptic level curves", True, r"Right. Positive in every direction away from $0$."),
        (r"A saddle", False, r"No. A saddle has negative energy in some direction (indefinite $S$)."),
        (r"A plane", False, r"No. The energy is quadratic, not linear."),
        (r"A bowl with its maximum at the origin", False, r"No. That would be negative definite.")]),
    q("q-svd", r"Which describes $A = U\Sigma V^T$?", [
        (r"Rotate or reflect by $V^T$, stretch by $\Sigma$, rotate or reflect by $U$", True, r"Right. Orthogonal, diagonal, orthogonal; an orthogonal factor can be a reflection, as for $A = \mathrm{diag}(1, -1)$."),
        (r"Stretch, rotate, stretch", False, r"No. Only $\Sigma$ stretches."),
        (r"It exists only for square symmetric matrices.", False, r"No. Every matrix, even rectangular, has an SVD."),
        (r"$U = V$ always", False, r"No. $U = V$ only when $A$ is symmetric positive semidefinite.")]),
    q("q-sigma", r"Where do the singular values come from?", [
        (r"$\sigma_i^2$ are the eigenvalues of $A^TA$.", True, r"Right. $A^TA = V\Sigma^T\Sigma V^T$."),
        (r"$\sigma_i$ are the eigenvalues of $A$.", False, r"No. For nonsymmetric $A$ they differ; $[2\ 2;\ 1\ 1]$ has eigenvalues $3, 0$ but $\sigma = \sqrt{10}, 0$."),
        (r"$\sigma_i$ are the diagonal entries of $A$.", False, r"No. They come from $A^TA$."),
        (r"$\sigma_i^2$ are the pivots of $A$.", False, r"No. Pivots are a different factorization.")]),
    q("q-example", r"What are the singular values of $\begin{bmatrix}2 & 2\\ 1 & 1\end{bmatrix}$?", [
        (r"$\sqrt{10}$ and $0$", True, r"Right. $A^TA = \begin{bmatrix}5&5\\5&5\end{bmatrix}$ has eigenvalues $10$ and $0$."),
        (r"$3$ and $0$", False, r"No. $3$ and $0$ are the eigenvalues of $A$."),
        (r"$10$ and $0$", False, r"No. Take square roots of the eigenvalues of $A^TA$."),
        (r"$2$ and $1$", False, r"No. Those are entries of $A$.")]),
    q("q-rank1", r"In $A = \sigma_1u_1v_1^T + \sigma_2u_2v_2^T + \cdots$, which piece matters most for a data matrix?", [
        (r"$\sigma_1u_1v_1^T$, with the largest singular value", True, r"Right. It captures the strongest pattern; keeping the top pieces is principal component analysis."),
        (r"The last piece", False, r"No. It has the smallest $\sigma$."),
        (r"All pieces matter equally.", False, r"No. Their sizes are the singular values."),
        (r"The piece with the largest entry of $u$", False, r"No. Every $u_i$ is a unit vector; $\sigma_i$ measures the size.")]),
]

EXPLORER = {
    "modes": [
        {"id": "pd", "label": "Positive definite tests and energy"},
        {"id": "svd", "label": "SVD: rotate or reflect, stretch, rotate or reflect"}
    ],
    "defaultMode": "pd",
    "s11": {"min": -2, "max": 10, "step": 0.5, "default": 4},
    "s12": {"min": -8, "max": 8, "step": 0.5, "default": 6},
    "s22": {"min": -2, "max": 12, "step": 0.5, "default": 10},
    "a": {"min": -4, "max": 4, "step": 0.5, "default": 2},
    "b": {"min": -4, "max": 4, "step": 0.5, "default": 2},
    "c": {"min": -4, "max": 4, "step": 0.5, "default": 1},
    "d": {"min": -4, "max": 4, "step": 0.5, "default": 1},
    "presets": [
        {"id": "lec48", "label": "[4 6; 6 10]", "mode": "pd", "s11": 4, "s12": 6, "s22": 10,
         "note": "Section 2: pivots $4, 1$; determinants $4, 4$; a bowl."},
        {"id": "fail", "label": "[3 4; 4 5]", "mode": "pd", "s11": 3, "s12": 4, "s22": 5,
         "note": "Section 2 example: determinant $-1$, a saddle."},
        {"id": "semi", "label": "[1 2; 2 4] (semidefinite)", "mode": "pd", "s11": 1, "s12": 2, "s22": 4,
         "note": "Determinant $0$: a trough, eigenvalue $0$ along $(2, -1)$."},
        {"id": "lec49", "label": "SVD of [2 2; 1 1]", "mode": "svd", "a": 2, "b": 2, "c": 1, "d": 1,
         "note": "Section 3: $\\sigma = \\sqrt{10}, 0$; the circle collapses to a segment."},
        {"id": "inv", "label": "SVD of [3 0; 4 5]", "mode": "svd", "a": 3, "b": 0, "c": 4, "d": 5,
         "note": "Section 3 example: $\\sigma = 3\\sqrt5, \\sqrt5$."}
    ],
    "tutorContext": "Two modes. Positive definite: a symmetric 2x2 S = [s11 s12; s12 s22]; the explorer shows the five tests (eigenvalues, pivots s11 and s22 - s12^2/s11, upper-left determinants s11 and det S, a factor A with S = A^T A from Cholesky when positive definite, and the energy x^T S x), the classification (positive definite, positive semidefinite, indefinite, negative (semi)definite), and a contour plot of the energy over [-2, 2]^2 with the eigenvector axes. SVD: a 2x2 A = [a b; c d]; it shows U, Sigma, V from the eigen-decomposition of A^T A (u_i = A v_i / sigma_i, completed orthonormally when sigma = 0), and animates the unit circle under V^T (rotation or reflection), Sigma (stretch) and U (rotation or reflection) to the ellipse A(circle), plus the rank-one pieces sigma_i u_i v_i^T."
}

COURSE = {
    "version": 1,
    "title": "Positive Definite Matrices and the SVD",
    "subtitle": "Unit 9 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 48-49, with Strang's Differential Equations and Linear Algebra, Section 7.2",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 48-49", "duration": "35:52", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, 7.2",
             "edition": "Wellesley-Cambridge Press, 2014 (Section 7.2)", "onlineUrl": "",
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
