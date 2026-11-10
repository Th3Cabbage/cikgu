"""Source of courses/mit-de/linear-algebra/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\linear-algebra\\course_source.py

Unit 7 of the MIT Learn Differential Equations companion: playlist videos 35-39 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Sections 5.1, 5.4-5.6.
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
    (35, "n98ilenWoak", "The Column Space of a Matrix", "12:44"),
    (36, "eeMJg4uI7o0", "Independence, Basis, and Dimension", "13:20"),
    (37, "ggWYkes-n6E", "The Big Picture of Linear Algebra", "15:57"),
    (38, "RwBCrVB98s8", "Graphs", "15:27"),
    (39, "nGKeHq_kRQA", "Incidence Matrices of Graphs", "19:51"),
]

SECTIONS = [
    {
        "nav": "Column space and null space",
        "v": 35,
        "title": r"$Av = b$ is solvable when $b$ is in the column space",
        "summary": r"$Av$ is a combination of the columns of $A$, so the column space $C(A)$ is the set of all $b$ that $Av = b$ can reach. The null space $N(A)$ holds every $v$ with $Av = 0$. The complete solution is one particular solution plus the whole null space.",
        "time": [0, 764],
        "goals": [
            r"Read $Av$ as a combination of the columns of $A$.",
            r"Decide whether $b$ is in $C(A)$.",
            r"Find the null space of a $3\times3$ matrix with dependent columns.",
            r"Write the complete solution $v = v_p + v_n$."
        ],
        "notes": [
            {"heading": "Combinations of columns",
             "paragraphs": [
                 r"Multiplying $A$ by $v$ takes $v_1$ of the first column, plus $v_2$ of the second, and so on. All those combinations, for every $v$, form the column space $C(A)$. The equation $Av = b$ has a solution exactly when $b$ is one of them: $b \in C(A)$.",
                 r"Strang's matrix $A = \begin{bmatrix}1 & 1 & 2\\ 1 & 2 & 3\\ 1 & 2 & 3\end{bmatrix}$ has column 3 $=$ column 1 $+$ column 2, so the third column adds nothing new. $C(A)$ is a plane in $\mathbb{R}^3$, not the whole space. Since rows 2 and 3 are equal, every $b$ in the plane has $b_2 = b_3$."
             ]},
            {"heading": "The null space",
             "paragraphs": [
                 r"$N(A)$ contains all solutions of $Av = 0$. Here column 1 $+$ column 2 $-$ column 3 $= 0$, so $v = (-1, -1, 1)$ is in it, and so is every multiple, such as $(-10, -10, 10)$. $N(A)$ is a line through the origin. The column space has dimension $2$ and the null space dimension $1$; together they make $3$, the number of columns."
             ]},
            {"heading": "The complete solution",
             "paragraphs": [
                 r"Take $b = (3, 4, 4)$: two of column 1 plus one of column 2 gives it, so $v_p = (2, 1, 0)$ is a particular solution. Adding any null solution changes nothing in $Av$. All solutions: $v = v_p + v_n = (2, 1, 0) + c(-1, -1, 1)$. This is the same pattern as $y = y_p + y_n$ for differential equations."
             ]}
        ],
        "keyIdeas": [
            r"$Av$ = combination of columns.",
            r"$Av = b$ solvable $\Leftrightarrow$ $b \in C(A)$.",
            r"$N(A)$: all $v$ with $Av = 0$.",
            r"$v = v_p + v_n$."
        ],
        "example": {
            "title": "A plane of right sides (authored)",
            "problem": r"For $A = \begin{bmatrix}1 & 0 & 1\\ 0 & 1 & 1\\ 1 & 1 & 2\end{bmatrix}$, solve $Av = (1, 2, 3)$ completely.",
            "steps": [
                {"text": "Column 3 = column 1 + column 2, so the null space is a line.", "tex": r"v_n = c\,(-1, -1, 1)"},
                {"text": "b = 1 * column 1 + 2 * column 2.", "tex": r"v_p = (1, 2, 0)"},
                {"text": "All solutions.", "tex": r"v = (1, 2, 0) + c\,(-1, -1, 1)"}
            ],
            "answer": r"$v = (1, 2, 0) + c(-1, -1, 1)$. A right side with $b_3 \neq b_1 + b_2$, such as $(1, 2, 4)$, has no solution."
        },
        "sources": {
            "video": [vs(35, 0, "Av is a combination of the columns"),
                      vs(35, 90, "Example matrix with 1, 1, 2 / 1, 2, 3 / 1, 2, 3"),
                      vs(35, 180, "Column 3 = column 1 + column 2: a plane"),
                      vs(35, 270, "Av = b has a solution when b is in C(A)"),
                      vs(35, 390, "Null space N(A): all solutions of Av = 0"),
                      vs(35, 540, "A line of solutions, dimensions 2 + 1 = 3"),
                      vs(35, 600, "Complete solution v = v_p + v_n"),
                      vs(35, 690, "v_p = (2, 1, 0)")],
            "book": [bk(251, "Section 5.1: the column space of a matrix")]
        },
        "tutorNotes": "Video 35. Av = combination of columns; C(A) = all Av. A = [1 1 2; 1 2 3; 1 2 3]: col3 = col1 + col2, C(A) is a plane (b2 = b3). Av = b solvable iff b in C(A). N(A) = line through (-1, -1, 1) (board shows (-10, -10, 10)). dim C(A) + dim N(A) = 2 + 1 = 3. b = (3, 4, 4): v_p = (2, 1, 0), v = v_p + c(-1, -1, 1)."
    },
    {
        "nav": "Independence, basis, dimension",
        "v": 36,
        "title": r"Independent columns, a basis, and the dimension",
        "summary": r"Vectors are independent when no combination except the zero combination gives the zero vector; equivalently $Av = 0$ only for $v = 0$. A basis of a space is an independent set that spans it, and every basis has the same number of vectors: the dimension.",
        "time": [0, 800],
        "goals": [
            r"Test independence by solving $Av = 0$.",
            r"Recognise a dependent third vector, such as $a_3 = a_1 + a_2$.",
            r"Find a basis and the dimension of a subspace of $\mathbb{R}^3$."
        ],
        "notes": [
            {"heading": "Independence",
             "paragraphs": [
                 r"Take $a_1 = (2, 1, 5)$ and $a_2 = (4, 2, 0)$. They point in different directions and span a plane. A third vector $a_3 = a_1 + a_2 = (6, 3, 5)$ lies in that plane: the three are dependent, because $a_1 + a_2 - a_3 = 0$. Choose instead $a_3 = (1, 0, 0)$, off the plane, and the three are independent.",
                 r"With the vectors as columns of $A$, independence means $Av = 0$ has only the solution $v = 0$: the null space is just the zero vector. For $A = \begin{bmatrix}2 & 4 & 1\\ 1 & 2 & 0\\ 5 & 0 & 0\end{bmatrix}$ that holds."
             ]},
            {"heading": "Basis and dimension",
             "paragraphs": [
                 r"A basis for a subspace is a set of vectors that is independent and spans the subspace: every vector in it is exactly one combination of the basis vectors. Bases are not unique, but they all have the same size. That number is the dimension.",
                 r"Subspaces of $\mathbb{R}^3$: the origin alone (dimension $0$), lines through the origin ($1$), planes through the origin ($2$), and $\mathbb{R}^3$ itself ($3$). Three independent vectors in $\mathbb{R}^3$ always form a basis."
             ]}
        ],
        "keyIdeas": [
            r"Independent: $Av = 0$ only for $v = 0$.",
            r"$a_3 = a_1 + a_2$ $\Rightarrow$ dependent.",
            r"Basis: independent and spanning.",
            r"Dimension = number of basis vectors."
        ],
        "example": {
            "title": "Three vectors in a plane (authored)",
            "problem": r"Are $(1, 2, 3)$, $(4, 5, 6)$, $(7, 8, 9)$ independent? What space do they span?",
            "steps": [
                {"text": "Look for a combination giving zero.", "tex": r"(7, 8, 9) = 2\,(4, 5, 6) - (1, 2, 3)"},
                {"text": "So v = (1, -2, 1) solves Av = 0.", "tex": r"1\cdot a_1 - 2\cdot a_2 + 1\cdot a_3 = 0"},
                {"text": "The first two are independent (not multiples).", "tex": r"\dim = 2"}
            ],
            "answer": r"Dependent; they span a plane through the origin, with basis $(1, 2, 3)$, $(4, 5, 6)$."
        },
        "sources": {
            "video": [vs(36, 0, "Vectors a1 = (2, 1, 5) and a2 = (4, 2, 0)"),
                      vs(36, 150, "a3 = a1 + a2 is dependent"),
                      vs(36, 240, "a3 = (1, 0, 0): independent"),
                      vs(36, 330, "Independent columns: Av = 0 only for v = 0"),
                      vs(36, 480, "Subspaces of R^3 and their dimensions"),
                      vs(36, 570, "Basis: independent and spanning"),
                      vs(36, 690, "Every basis has the same size")],
            "book": [bk(285, "Section 5.4: independence, basis and dimension")]
        },
        "tutorNotes": "Video 36. a1 = (2, 1, 5), a2 = (4, 2, 0); a3 = a1 + a2 = (6, 3, 5) dependent; a3 = (1, 0, 0) independent, A = [2 4 1; 1 2 0; 5 0 0] has Av = 0 only for v = 0. Subspaces of R^3: dims 0-3. Basis = independent + spanning; dimension = size of every basis."
    },
    {
        "nav": "The four subspaces",
        "v": 37,
        "title": r"The big picture: four fundamental subspaces",
        "summary": r"An $m\times n$ matrix of rank $r$ has four subspaces: the row space $C(A^T)$ and null space $N(A)$ in $\mathbb{R}^n$, with dimensions $r$ and $n - r$, and the column space $C(A)$ and left null space $N(A^T)$ in $\mathbb{R}^m$, with dimensions $r$ and $m - r$. The null space is perpendicular to the row space.",
        "time": [0, 957],
        "goals": [
            r"Name the four subspaces and where they live.",
            r"State their dimensions $r$, $n - r$, $r$, $m - r$.",
            r"Show that the null space is perpendicular to the row space."
        ],
        "notes": [
            {"heading": "Example",
             "paragraphs": [
                 r"$A = \begin{bmatrix}1 & 2 & 3\\ 4 & 5 & 6\end{bmatrix}$ is $2\times3$ with rank $2$. Its rows span a plane in $\mathbb{R}^3$ (the row space). Its null space is the line through $(1, -2, 1)$: indeed $1 - 4 + 3 = 0$ and $4 - 10 + 6 = 0$. Its columns fill $\mathbb{R}^2$, so $C(A) = \mathbb{R}^2$, and $N(A^T)$ contains only the zero vector."
             ]},
            {"heading": "Perpendicular",
             "paragraphs": [
                 r"$Av = 0$ says that each row of $A$ has dot product zero with $v$. So every vector in the null space is perpendicular to every row, and to every combination of rows: $N(A) \perp C(A^T)$. In the example the line through $(1, -2, 1)$ is perpendicular to the plane of the rows."
             ]},
            {"heading": "Dimensions",
             "paragraphs": [
                 r"The row space is $C(A^T)$, the column space of $A^T$. For rank $r$: $\dim C(A^T) = r$ and $\dim N(A) = n - r$, adding to $n$; $\dim C(A) = r$ and $\dim N(A^T) = m - r$, adding to $m$. Row rank equals column rank. For the example: $2, 1, 2, 0$."
             ]}
        ],
        "keyIdeas": [
            r"In $\mathbb{R}^n$: row space ($r$) $\perp$ null space ($n - r$).",
            r"In $\mathbb{R}^m$: column space ($r$) $\perp$ left null space ($m - r$).",
            r"Row rank = column rank = $r$.",
            r"$Av = 0$: $v$ is perpendicular to every row."
        ],
        "example": {
            "title": "A rank-one matrix (authored)",
            "problem": r"Find the four subspaces of $A = \begin{bmatrix}1 & 2\\ 2 & 4\\ 3 & 6\end{bmatrix}$.",
            "steps": [
                {"text": "Every row is a multiple of (1, 2): rank r = 1, m = 3, n = 2.", "tex": r"C(A^T) = \text{line through } (1, 2),\quad N(A) = \text{line through } (2, -1)"},
                {"text": "Every column is a multiple of (1, 2, 3).", "tex": r"C(A) = \text{line through } (1, 2, 3)"},
                {"text": "Left null space: y with A^T y = 0, i.e. y1 + 2y2 + 3y3 = 0.", "tex": r"N(A^T) = \text{plane } y_1 + 2y_2 + 3y_3 = 0"}
            ],
            "answer": r"Dimensions $1, 1, 1, 2$, matching $r$, $n - r$, $r$, $m - r$."
        },
        "sources": {
            "video": [vs(37, 0, "Example A = [1 2 3; 4 5 6]"),
                      vs(37, 30, "Row space: a plane in R^3"),
                      vs(37, 150, "Null space: the line through (1, -2, 1)"),
                      vs(37, 330, "Check: perpendicular to the rows"),
                      vs(37, 390, "Column space is all of R^2"),
                      vs(37, 510, "Row space = column space of A transpose"),
                      vs(37, 570, "Left null space"),
                      vs(37, 750, "The big picture"),
                      vs(37, 810, "Dimensions r, n - r, r, m - r")],
            "book": [bk(300, "Section 5.5: the four fundamental subspaces")]
        },
        "tutorNotes": "Video 37. A = [1 2 3; 4 5 6], rank 2. Row space plane in R^3, N(A) line through (1, -2, 1), perpendicular to the rows. C(A) = R^2, N(A^T) = {0}. Dimensions: row space r, null space n - r, column space r, left null space m - r."
    },
    {
        "nav": "Graphs",
        "v": 38,
        "title": r"Graphs and their incidence matrices",
        "summary": r"A graph with $n$ nodes and $m$ edges has an $m\times n$ incidence matrix $A$: each row has $-1$ at the start node and $+1$ at the end node of its edge. $Av$ gives potential differences across edges; $A^Tw = 0$ is Kirchhoff's current law; $A^TA$ is the graph Laplacian.",
        "time": [0, 927],
        "goals": [
            r"Build the incidence matrix of a directed graph.",
            r"Interpret $Av$ as potential differences.",
            r"Read $A^Tw = 0$ as current balance at every node."
        ],
        "notes": [
            {"heading": "The incidence matrix",
             "paragraphs": [
                 r"Strang's graph has $4$ nodes and $5$ edges: $1\to2$, $1\to3$, $2\to3$, $1\to4$, $2\to4$. Row $k$ of $A$ describes edge $k$: $-1$ in the column of the node it leaves, $+1$ in the column it enters. So $A$ is $5\times4$ with two nonzeros per row."
             ]},
            {"heading": "Potentials and currents",
             "paragraphs": [
                 r"Give each node a potential $v_j$ (a voltage, a height, a pressure). Then $(Av)_k = v_{\text{end}} - v_{\text{start}}$: the difference across edge $k$. Ohm's law turns differences into edge currents $w$ (with conductances $C$: $w = -CAv$ up to sign convention).",
                 r"The transpose goes the other way. $(A^Tw)_j$ adds the currents into node $j$ and subtracts those leaving. Kirchhoff's current law, $A^Tw = 0$, says current is balanced at every node.",
                 r"Combining the three steps gives $A^TCA$, and with all conductances $1$ the graph Laplacian $A^TA$: degrees on the diagonal, $-1$ for each edge off the diagonal."
             ]}
        ],
        "keyIdeas": [
            r"Row of $A$: $-1$ at start, $+1$ at end.",
            r"$Av$ = potential differences.",
            r"$A^Tw = 0$: Kirchhoff's current law.",
            r"$A^TA$ = graph Laplacian."
        ],
        "example": {
            "title": "A triangle (authored)",
            "problem": r"Edges $1\to2$, $2\to3$, $1\to3$. Write $A$, compute $Av$ for $v = (0, 1, 3)$, and check a loop current.",
            "steps": [
                {"text": "Incidence matrix (rows = edges).", "tex": r"A = \begin{bmatrix}-1 & 1 & 0\\ 0 & -1 & 1\\ -1 & 0 & 1\end{bmatrix}"},
                {"text": "Potential differences.", "tex": r"Av = (1 - 0,\ 3 - 1,\ 3 - 0) = (1, 2, 3)"},
                {"text": "Current 1 around 1 to 2 to 3, back along edge 3 reversed.", "tex": r"w = (1, 1, -1):\quad A^Tw = (0, 0, 0)"}
            ],
            "answer": r"$Av = (1, 2, 3)$; the loop current $w = (1, 1, -1)$ satisfies Kirchhoff's law."
        },
        "sources": {
            "video": [vs(38, 0, "Graphs: nodes and edges"),
                      vs(38, 120, "Four nodes, five edges"),
                      vs(38, 210, "Incidence matrix: -1 and +1 in each row"),
                      vs(38, 360, "Av: potential differences"),
                      vs(38, 570, "A transpose w = 0: Kirchhoff's current law"),
                      vs(38, 720, "Ohm's law"),
                      vs(38, 870, "A transpose A: the graph Laplacian")],
            "book": [bk(313, "Section 5.6: graphs and networks")]
        },
        "tutorNotes": "Video 38. Graph 4 nodes, 5 edges 1->2, 1->3, 2->3, 1->4, 2->4; A (5x4) rows [-1 1 0 0], [-1 0 1 0], [0 -1 1 0], [-1 0 0 1], [0 -1 0 1]. Av = potential differences; A^T w = 0 is Kirchhoff's current law; Ohm's law links them; A^T A graph Laplacian."
    },
    {
        "nav": "Null spaces of a graph",
        "v": 39,
        "title": r"Null spaces of the incidence matrix: constants and loops",
        "summary": r"$Av = 0$ means equal potentials: for a connected graph, $N(A)$ is the line of constant vectors, so $\operatorname{rank}A = n - 1$. $A^Tw = 0$ is solved by currents around loops; there are $m - n + 1$ independent loops. That is Euler's formula: nodes $-$ edges $+$ loops $= 1$.",
        "time": [0, 1191],
        "goals": [
            r"Find $N(A)$ for a connected graph and ground a node.",
            r"Find loop currents that solve $A^Tw = 0$.",
            r"Count independent loops: $m - (n - 1)$."
        ],
        "notes": [
            {"heading": "Constant potentials",
             "paragraphs": [
                 r"$Av = 0$ asks for every edge difference to vanish. Along connected edges the potentials must be equal, so for a connected graph $v = c(1, 1, 1, 1)$: $N(A)$ is a line and the rank is $n - 1 = 3$. Only differences matter, so we may ground one node, $v_4 = 0$, and remove its column: the $5\times3$ matrix that remains has independent columns."
             ]},
            {"heading": "Loops",
             "paragraphs": [
                 r"$A^T$ is $4\times5$. Its row for node $1$ says $-w_1 - w_2 - w_4 = 0$: the three edges leaving node $1$ carry no net current. A current of $1$ around the loop $1\to2\to4\to1$ is $w = (1, 0, 0, -1, 1)$ (edge $4$ is traversed backwards), and it satisfies all four node equations. The small loops $1\to2\to3\to1$, with $w = (1, -1, 1, 0, 0)$, and $1\to2\to4\to1$, with $w = (1, 0, 0, -1, 1)$, are independent. Orientation matters when loops are combined: both use edge $1$ forwards, so their difference $(0, 1, -1, -1, 1)$ cancels the shared edge. That difference is the larger loop $1\to3\to2\to4\to1$ (equivalently, add the first loop reversed to the second)."
             ]},
            {"heading": "Counting",
             "paragraphs": [
                 r"$\dim N(A^T) = m - r = 5 - 3 = 2$ independent loops. In general, for a connected graph, loops $= m - n + 1$, which rearranges to Euler's formula: (nodes) $-$ (edges) $+$ (loops) $= 1$. All four subspaces of the incidence matrix have a meaning on the graph."
             ]}
        ],
        "keyIdeas": [
            r"Connected: $N(A)$ = constants, rank $n - 1$.",
            r"Ground a node to remove the constant.",
            r"Loops solve $A^Tw = 0$.",
            r"Loops $= m - n + 1$ (Euler)."
        ],
        "example": {
            "title": "The complete graph on four nodes (authored)",
            "problem": r"Every pair of $4$ nodes is joined by an edge. Find $m$, the rank of $A$, and the number of independent loops.",
            "steps": [
                {"text": "Number of pairs.", "tex": r"m = \binom{4}{2} = 6,\qquad n = 4"},
                {"text": "Connected graph.", "tex": r"\operatorname{rank} A = n - 1 = 3"},
                {"text": "Independent loops.", "tex": r"m - n + 1 = 6 - 4 + 1 = 3"}
            ],
            "answer": r"$6$ edges, rank $3$, $3$ independent loops (for instance the three triangles through one chosen node)."
        },
        "sources": {
            "video": [vs(39, 0, "Incidence matrix again"),
                      vs(39, 90, "Av = 0 for v = (1, 1, 1, 1)"),
                      vs(39, 210, "Ground node 4: a 5 by 3 matrix"),
                      vs(39, 390, "A transpose"),
                      vs(39, 480, "Node 1: -(w1 + w2 + w4) = 0"),
                      vs(39, 660, "Loop current w = (1, 0, 0, -1, 1)"),
                      vs(39, 840, "A bigger loop from the small loops"),
                      vs(39, 990, "m - n + 1 = 2 independent loops")],
            "book": [bk(315, "Incidence matrix: the four subspaces"),
                     bk(318, "Kirchhoff's laws and Euler's formula")]
        },
        "tutorNotes": "Video 39. Connected graph: Av = 0 for v = c(1, 1, 1, 1), rank n - 1 = 3; ground node 4 to get a 5x3 matrix. A^T row for node 1: -(w1 + w2 + w4) = 0. Loop current w = (1, 0, 0, -1, 1) for 1->2->4->1. Combining loops needs orientation: (1, 0, 0, -1, 1) - (1, -1, 1, 0, 0) = (0, 1, -1, -1, 1) is the loop 1->3->2->4->1 (shared edge cancels). Independent loops m - n + 1 = 2 = dim N(A^T); Euler: nodes - edges + loops = 1."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-colspace", r"When does $Av = b$ have a solution?", [
        (r"When $b$ is a combination of the columns of $A$.", True, r"Right. $Av$ is exactly such a combination, with weights $v$."),
        (r"Only when $A$ is square.", False, r"No. Rectangular systems are solvable when $b \in C(A)$."),
        (r"When $b$ is in the null space.", False, r"No. The null space holds solutions $v$ of $Av = 0$, not right sides."),
        (r"Always.", False, r"No. If $C(A)$ is a plane, right sides off the plane cannot be reached.")]),
    q("q-null", r"For $A = \begin{bmatrix}1 & 1 & 2\\ 1 & 2 & 3\\ 1 & 2 & 3\end{bmatrix}$, which vector is in $N(A)$?", [
        (r"$(-1, -1, 1)$", True, r"Right. Column 1 $+$ column 2 $-$ column 3 $= 0$."),
        (r"$(1, 1, 1)$", False, r"No. $A(1,1,1) = (4, 6, 6)$."),
        (r"$(2, 1, 0)$", False, r"No. That is a particular solution for $b = (3, 4, 4)$."),
        (r"$(1, 1, -1)$ is not, but $(1, -1, 1)$ is", False, r"No. $(1, 1, -1)$ is in $N(A)$ (it is $-1$ times $(-1, -1, 1)$), and $(1, -1, 1)$ is not.")]),
    q("q-complete", r"$Av = b$ has a particular solution $v_p$ and $N(A)$ is a line through $u$. What are all solutions?", [
        (r"$v_p + cu$ for every number $c$", True, r"Right. Adding a null solution does not change $Av$."),
        (r"$v_p$ only", False, r"No. Any $v_p + cu$ also solves it."),
        (r"$cu$ for every $c$", False, r"No. Those solve $Av = 0$, not $Av = b$."),
        (r"$c\,v_p$ for every $c$", False, r"No. $A(cv_p) = cb \neq b$ unless $c = 1$.")]),
    q("q-indep", r"Which statement means the columns of $A$ are independent?", [
        (r"$Av = 0$ only for $v = 0$.", True, r"Right. No nonzero combination of the columns gives zero."),
        (r"$Av = b$ has a solution for every $b$.", False, r"No. That says the columns span $\mathbb{R}^m$, a different property."),
        (r"$A$ has no zero entries.", False, r"No. $\begin{bmatrix}1 & 2\\ 2 & 4\end{bmatrix}$ has dependent columns."),
        (r"$A$ is square.", False, r"No. Square matrices can have dependent columns.")]),
    q("q-dim", r"What is the dimension of the plane through the origin spanned by $(2, 1, 5)$ and $(4, 2, 0)$?", [
        (r"$2$", True, r"Right. Two independent vectors form a basis for the plane."),
        (r"$3$", False, r"No. A plane in $\mathbb{R}^3$ is two-dimensional."),
        (r"$1$", False, r"No. The vectors are not multiples of each other."),
        (r"It depends on the basis.", False, r"No. Every basis of a space has the same number of vectors.")]),
    q("q-four", r"$A$ is $3\times5$ with rank $2$. What is $\dim N(A)$?", [
        (r"$3$", True, r"Right. $n - r = 5 - 2$."),
        (r"$1$", False, r"No. $m - r = 1$ is the dimension of $N(A^T)$."),
        (r"$2$", False, r"No. $2$ is the rank, the dimension of the row and column spaces."),
        (r"$5$", False, r"No. Only the whole of $\mathbb{R}^5$ has dimension $5$.")]),
    q("q-perp", r"Why is every vector in $N(A)$ perpendicular to every row of $A$?", [
        (r"Because $Av = 0$ says each row has dot product zero with $v$.", True, r"Right. Each entry of $Av$ is a row times $v$."),
        (r"Because $A$ is symmetric.", False, r"No. The statement holds for every matrix."),
        (r"Because the columns are independent.", False, r"No. Independence is not needed."),
        (r"It is not true in general.", False, r"No. It is always true: $N(A) \perp C(A^T)$.")]),
    q("q-incidence", r"An edge goes from node $2$ to node $4$ in a $4$-node graph. What is its row in the incidence matrix?", [
        (r"$[0,\ -1,\ 0,\ 1]$", True, r"Right. $-1$ at the start node $2$, $+1$ at the end node $4$."),
        (r"$[0,\ 1,\ 0,\ -1]$", False, r"No. The convention puts $-1$ at the start."),
        (r"$[0,\ 1,\ 0,\ 1]$", False, r"No. Then $Av$ would add potentials instead of taking differences."),
        (r"$[2,\ 4]$", False, r"No. The row has one entry per node.")]),
    q("q-graph-null", r"For a connected graph with $n$ nodes, what is $N(A)$?", [
        (r"The constant vectors $c(1, 1, \ldots, 1)$", True, r"Right. Zero differences on every edge force equal potentials."),
        (r"Only the zero vector", False, r"No. Adding the same constant to every potential changes no difference."),
        (r"The loop currents", False, r"No. Loop currents form $N(A^T)$."),
        (r"All of $\mathbb{R}^n$", False, r"No. A nonzero difference on any edge gives $Av \neq 0$.")]),
    q("q-loops", r"A connected graph has $7$ nodes and $10$ edges. How many independent loops?", [
        (r"$4$", True, r"Right. $m - n + 1 = 10 - 7 + 1$."),
        (r"$3$", False, r"No. Remember the $+1$: the rank is $n - 1$."),
        (r"$17$", False, r"No. Loops are $m - r$, not $m + n$."),
        (r"$10$", False, r"No. Not every edge closes its own loop.")]),
]

EXPLORER = {
    "modes": [
        {"id": "matrix", "label": "Four subspaces of a matrix"},
        {"id": "graph", "label": "Graph and incidence matrix"}
    ],
    "defaultMode": "matrix",
    "entryRange": [-9, 9],
    "maxRows": 4,
    "maxCols": 4,
    "matrices": [
        {"id": "lecture35", "label": "Video 35: [1 1 2; 1 2 3; 1 2 3]", "A": [[1, 1, 2], [1, 2, 3], [1, 2, 3]], "b": [3, 4, 4]},
        {"id": "lecture36", "label": "Video 36: columns (2,1,5), (4,2,0), (1,0,0)", "A": [[2, 4, 1], [1, 2, 0], [5, 0, 0]], "b": [1, 0, 0]},
        {"id": "lecture37", "label": "Video 37: [1 2 3; 4 5 6]", "A": [[1, 2, 3], [4, 5, 6]], "b": [1, 1]},
        {"id": "rank1", "label": "Rank one [1 2; 2 4; 3 6]", "A": [[1, 2], [2, 4], [3, 6]], "b": [1, 2, 3]}
    ],
    "graphNodes": [[0.15, 0.2], [0.85, 0.2], [0.5, 0.85], [0.5, 0.45]],
    "candidateEdges": [[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [3, 4]],
    "defaultEdges": [[1, 2], [1, 3], [2, 3], [1, 4], [2, 4]],
    "presets": [
        {"id": "m35", "label": "Column space example", "mode": "matrix", "matrix": "lecture35",
         "note": "Section 1: $C(A)$ is a plane, $N(A)$ the line through $(-1,-1,1)$."},
        {"id": "m37", "label": "Big picture example", "mode": "matrix", "matrix": "lecture37",
         "note": "Section 3: dimensions $2, 1, 2, 0$."},
        {"id": "g38", "label": "Strang's graph", "mode": "graph", "edges": [[1, 2], [1, 3], [2, 3], [1, 4], [2, 4]],
         "note": "Sections 4-5: rank $3$, $2$ independent loops."},
        {"id": "k4", "label": "Complete graph K4", "mode": "graph", "edges": [[1, 2], [1, 3], [2, 3], [1, 4], [2, 4], [3, 4]],
         "note": "Section 5 example: $6$ edges, $3$ loops."}
    ],
    "tutorContext": "Two modes. Matrix: the user edits an m x n integer matrix (up to 4 x 4) and a right side b; the explorer computes the reduced row echelon form exactly with fractions, the rank r, pivot columns, bases for the column space C(A) (pivot columns of A), the row space (nonzero rows of R), the null space N(A) (special solutions) and the left null space N(A^T), their dimensions r, n - r, r, m - r, whether b is in C(A), and if so a particular solution and the complete solution v_p + combinations of the null space basis. Graph: four nodes with selectable directed edges among 1->2, 1->3, 2->3, 1->4, 2->4, 3->4; it shows the incidence matrix A (row = edge, -1 at start, +1 at end), its rank (n minus the number of connected components), N(A) (constant on each component), a basis of loop currents for N(A^T) with m - r loops, and the graph Laplacian A^T A."
}

COURSE = {
    "version": 1,
    "title": "Column Space, Basis and Graphs",
    "subtitle": "Unit 7 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 35-39, with Strang's Differential Equations and Linear Algebra, Sections 5.1 and 5.4-5.6",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 35-39", "duration": "1:17:19", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 5",
             "edition": "Wellesley-Cambridge Press, 2014 (Sections 5.1, 5.4-5.6)", "onlineUrl": "",
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
