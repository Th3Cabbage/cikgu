"""Source of courses/controls/controllability/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\controls\\controllability\\course_source.py

Text is original, written for this companion. It paraphrases S. L. Brunton's Control Bootcamp
lecture "Controllability" and Brunton & Kutz, Section 8.3 (printed pp. 336-337, Eqs. 8.26-8.31),
without quoting. Examples marked "authored" are not from the lecture. The book's fourth example
(B = [1, 1]^T) is in the book but not worked in the lecture.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "course.json")

A_UNC = r"\begin{bmatrix}1&0\\0&2\end{bmatrix}"
A_CPL = r"\begin{bmatrix}1&1\\0&2\end{bmatrix}"
B01 = r"\begin{bmatrix}0\\1\end{bmatrix}"
BOOK = [{"printed": 336, "pdf": 356, "label": "Section 8.3: Eq. (8.26) controllability matrix; three equivalent conditions; ctrb and rank"},
        {"printed": 337, "pdf": 357, "label": "Eqs. (8.28)-(8.31): the worked 2-state examples"}]

SECTIONS = [
    {
        "nav": "Adding control",
        "title": r"From $\dot x = Ax$ to $\dot x = Ax + Bu$",
        "time": [0, 180],
        "summary": r"After several lectures on $\dot x = Ax$, the input term $Bu$ is added. The state $x$ has $n$ entries, the input $u$ has $q$ entries, so $B$ is $n \times q$. For now every state is assumed to be measured: $y = x$.",
        "goals": [
            r"Write $\dot x = Ax + Bu$ and give the shapes of $x$, $u$, $A$ and $B$.",
            r"Explain why $B$ must have $n$ rows and $q$ columns.",
            r"State the full-state measurement assumption $y = x$ (that is, $C = I$) used in this lecture."
        ],
        "notes": [
            {"heading": "Why add an input",
             "paragraphs": [
                 r"The previous lectures showed that the behaviour of $\dot x = Ax$ is fixed by the eigenvalues of $A$: an eigenvalue with positive real part means the system runs away. The aim now is to bend that behaviour with a control input, so the equation gains a forcing term $Bu$.",
                 r"Two questions organise the rest of the bootcamp: when is it possible to change the behaviour with feedback (controllability, this lecture), and if it is possible, how do we design the input (later lectures)."
             ]},
            {"heading": "Shapes",
             "paragraphs": [
                 r"$x \in \mathbb{R}^n$ and $A$ is $n \times n$, as before. The input $u \in \mathbb{R}^q$ may be a vector of $q$ separate actuator signals; often the lecture pretends $q = 1$, a single scalar input.",
                 r"$Bu$ is added to $Ax$, so it must also be an $n$-vector. A matrix times a $q$-vector gives an $n$-vector only if the matrix is $n \times q$: $n$ tall, $q$ wide. Each column of $B$ is the direction in state space that one actuator pushes."
             ]},
            {"heading": "Measurements, for later",
             "paragraphs": [
                 r"Later lectures add measurements $y = Cx$ with $y \in \mathbb{R}^p$. (This $C$ is the measurement matrix; the controllability matrix later in this lecture is a different object, written as a curly $\mathcal{C}$.) Here the lecture assumes $C = I$, so $y = x$: the whole state is available for feedback."
             ]}
        ],
        "keyIdeas": [
            r"$\dot x = Ax + Bu$, $\;x \in \mathbb{R}^n$, $u \in \mathbb{R}^q$, $A$ is $n\times n$, $B$ is $n\times q$.",
            r"One column of $B$ per actuator.",
            r"Assumed here: full-state measurement $y = x$."
        ],
        "example": {
            "title": "Checking shapes (authored)",
            "problem": r"A system has $n = 3$ states and $q = 2$ actuators. What are the shapes of $A$, $B$ and $Bu$?",
            "steps": [
                {"text": "The state equation must return a 3-vector.", "tex": r"\dot x \in \mathbb{R}^{3} \;\Rightarrow\; A \in \mathbb{R}^{3\times 3}"},
                {"text": "B multiplies the 2-vector u and must return a 3-vector.", "tex": r"\underbrace{B}_{3\times 2}\,\underbrace{u}_{2\times 1} = \underbrace{Bu}_{3\times 1}"}
            ],
            "answer": r"$A$ is $3\times3$, $B$ is $3\times2$, and $Bu$ is a $3\times1$ column like $Ax$."
        },
        "sources": {
            "video": [{"t": 0, "label": "From x' = Ax to adding control"},
                      {"t": 30, "label": "Add Bu; u may be a vector in R^q"},
                      {"t": 60, "label": "Sizes: A is n x n, B is n x q"},
                      {"t": 120, "label": "Measurements y = Cx deferred; assume y = x"}],
            "book": BOOK[:1]
        },
        "tutorNotes": "Lecture 0:00-3:00. x in R^n, u in R^q, A n-by-n, B n-by-q (n tall, q wide). Measurements y = Cx with y in R^p are deferred; this lecture assumes full-state measurement y = x (C = I). The measurement matrix C differs from the curly controllability matrix introduced later."
    },
    {
        "nav": "Feedback and controllability",
        "title": r"Feedback $u = -Kx$ and what controllability promises",
        "time": [180, 660],
        "summary": r"Substituting the proportional feedback $u = -Kx$ gives $\dot x = (A - BK)x$. Roughly, the pair $(A, B)$ is controllable when a suitable $K$ can put the eigenvalues of $A - BK$ anywhere, and, equivalently, when some input can steer the state to any point of $\mathbb{R}^n$ in finite time. Only $A$ and $B$ decide this.",
        "goals": [
            r"Substitute $u = -Kx$ and simplify to $\dot x = (A - BK)x$, with $K$ of size $q \times n$.",
            r"State the two meanings of controllability: arbitrary eigenvalue placement and reachability of every state.",
            r"Explain why the test uses only $A$ and $B$."
        ],
        "notes": [
            {"heading": "The closed-loop matrix",
             "paragraphs": [
                 r"With full-state measurements, the lecture proposes the linear proportional law $u = -Kx$: measure the state and push back in proportion to how far it is from where it should be. Since $u$ is $q \times 1$ and $x$ is $n \times 1$, the gain $K$ is $q \times n$.",
                 r"Substituting: $\dot x = Ax + B(-Kx) = Ax - BKx = (A - BK)x$. The factor keeps $B$ to the left of $K$ (and $BK$ is $n \times n$, as it must be to subtract from $A$). The closed-loop system is again of the form $\dot x = (\text{matrix})\,x$, so its behaviour is set by the eigenvalues of $A - BK$, which we can influence through $K$."
             ]},
            {"heading": "“Optimal”, with care",
             "paragraphs": [
                 r"The lecture says that for linear systems a linear law $u = -Kx$ is, in a certain sense, the best one can do, so there is no need for exotic nonlinear feedback. That sense needs a stated cost and assumptions (it is made precise later with LQR); the claim is not that $u = -Kx$ is best for every possible goal."
             ]},
            {"heading": "What controllable means",
             "paragraphs": [
                 r"Loosely: the system is controllable if (1) a suitable $K$ can place the eigenvalues of $A - BK$ anywhere we like, and (2) some input $u(t)$ can steer the state from where it is to any target in $\mathbb{R}^n$ in finite time. The book lists these, together with the rank test of Section 4, as three equivalent conditions. Reachability also holds for open-loop inputs, not only feedback.",
                 r"Two fine points: for real $A$, $B$, $K$ the closed-loop eigenvalues of a real matrix come in complex-conjugate pairs, so “anywhere” means any conjugate-symmetric set. And classical controllability ignores actuator limits: a controllable system may still need very large inputs.",
                 r"The lecture's analogy: a car is more or less controllable, since parallel parking gets it to where you want it, even though you cannot slide sideways directly."
             ]},
            {"heading": "A and B are given; only u is ours",
             "paragraphs": [
                 r"A control engineer is usually handed a finished system: the dynamics $A$ (an aircraft, say) and the actuators $B$ (its ailerons, rudder and elevators) are fixed. So controllability is a property of the pair $(A, B)$, not of $A$ alone and not of $K$. A test using only $A$ and $B$ lets you say “this cannot be controlled with these actuators; place them differently” rather than “I tried and failed”. MATLAB's version is ctrb(A,B) (Section 6)."
             ]}
        ],
        "keyIdeas": [
            r"$u = -Kx \;\Rightarrow\; \dot x = (A - BK)x$, $\;K$ is $q\times n$.",
            r"Controllable $\Leftrightarrow$ eigenvalues of $A - BK$ assignable $\Leftrightarrow$ every state reachable in finite time.",
            r"A property of the pair $(A, B)$."
        ],
        "example": {
            "title": "One state, one gain (authored)",
            "problem": r"For the scalar system $\dot x = 3x + u$, which gain $k$ in $u = -kx$ gives the closed-loop eigenvalue $-2$?",
            "steps": [
                {"text": "Substitute the feedback law.", "tex": r"\dot x = 3x + (-kx) = (3 - k)\,x"},
                {"text": "The closed-loop eigenvalue is the single entry 3 - k; set it to -2.", "tex": r"3 - k = -2 \;\Rightarrow\; k = 5"}
            ],
            "answer": r"$k = 5$ gives $\dot x = -2x$. With one state and $b = 1 \neq 0$, any eigenvalue is reachable; the interesting question is what happens with more states than inputs."
        },
        "sources": {
            "video": [{"t": 180, "label": "Design u = -Kx; 'optimal in some sense'"},
                      {"t": 300, "label": "Substitute: x' = (A - BK)x"},
                      {"t": 360, "label": "Controllability: place eigenvalues anywhere"},
                      {"t": 420, "label": "Also: steer the state anywhere in R^n"},
                      {"t": 480, "label": "A and B are usually given (aircraft example)"},
                      {"t": 570, "label": "A test using only A and B; ctrb(A,B)"}],
            "book": BOOK[:1]
        },
        "tutorNotes": "Lecture 3:00-11:00. u = -Kx with K q-by-n gives x' = (A - BK)x. Controllable (loosely): eigenvalues of A - BK can be placed arbitrarily (for real matrices, conjugate-symmetric sets) and any state reachable in finite time; book p.336-337 states these with the rank test as equivalent conditions, reachability also open-loop. Optimality of u = -Kx needs a specified cost (LQR later). Actuator bounds are ignored. A and B fixed by design; only u is chosen. No pole-placement algorithm is derived in this lecture (book mentions place(A,B,neweigs))."
    },
    {
        "nav": "Three examples",
        "title": "Uncoupled, more actuators, coupled",
        "time": [660, 1050],
        "summary": r"With $A = \mathrm{diag}(1, 2)$ and $B = [0, 1]^T$ the input never reaches $x_1$, so the pair is uncontrollable. A second actuator ($B = I$) fixes it. Keeping one actuator but adding a coupling entry, $A = \begin{bmatrix}1&1\\0&2\end{bmatrix}$, also makes the same $B$ controllable.",
        "goals": [
            r"Read off from the row equations why $A = \mathrm{diag}(1,2)$, $B = [0,1]^T$ is uncontrollable.",
            r"Explain how extra actuators (columns of $B$) add control authority.",
            r"Explain how coupling in $A$ lets one input reach both states."
        ],
        "notes": [
            {"heading": "Uncontrollable: the input never reaches x₁",
             "paragraphs": [
                 r"Write $\dot x = \begin{bmatrix}1&0\\0&2\end{bmatrix}x + \begin{bmatrix}0\\1\end{bmatrix}u$ row by row: $\dot x_1 = x_1$ and $\dot x_2 = 2x_2 + u$. The first equation contains neither $u$ nor $x_2$, so nothing we do affects $x_1$. It grows like $e^{t}$ whatever the input, so we can neither stabilise it nor steer it.",
                 r"The lecture treats both continuous and discrete time as equally good for this reasoning; the examples are written in continuous time."
             ]},
            {"heading": "Fix 1: another actuator",
             "paragraphs": [
                 r"With two inputs and $B = I$: $\dot x_1 = x_1 + u_1$ and $\dot x_2 = 2x_2 + u_2$. Each state now has its own knob, so each can be stabilised independently. Every column of $B$ is another actuator, more control authority."
             ]},
            {"heading": "Fix 2: coupling",
             "paragraphs": [
                 r"Keep the single input $B = [0, 1]^T$ but add an off-diagonal 1: $\dot x_1 = x_1 + x_2$, $\dot x_2 = 2x_2 + u$. The input drives $x_2$ directly, and $x_2$ now drives $x_1$, so by scheduling how $x_2$ moves we can also steer $x_1$. The lecture asks us to take controllability on trust at this point; Section 5 proves it with the rank test.",
                 r"The wider lesson: if the states are tightly coupled through $A$, a few actuators can control many states, which is why complicated systems are often controlled with relatively few actuators and sensors.",
                 r"Coupling alone is not a guarantee (authored observation): with this coupled $A$, the input $B = [1, 1]^T$ points along the eigenvector of the eigenvalue $2$, and the pair is uncontrollable again. Try the “Along an eigenvector” preset in the explorer."
             ]}
        ],
        "keyIdeas": [
            r"Uncoupled with $B = [0,1]^T$: $\dot x_1 = x_1$ ignores $u$.",
            r"More columns of $B$ = more actuators.",
            r"Coupling lets $u \to x_2 \to x_1$."
        ],
        "example": {
            "title": "The fixed eigenvalue (authored check)",
            "problem": r"Compute $A - BK$ for $K = [k_1\ \ k_2]$ in the uncoupled and the coupled examples with $B = [0, 1]^T$. Which eigenvalues can $K$ move?",
            "steps": [
                {"text": r"$BK$ puts $K$ into the second row only.", "tex": r"BK = \begin{bmatrix}0\\1\end{bmatrix}\begin{bmatrix}k_1 & k_2\end{bmatrix} = \begin{bmatrix}0&0\\k_1&k_2\end{bmatrix}"},
                {"text": r"Uncoupled: $A - BK$ is lower triangular, so its eigenvalues are the diagonal entries.", "tex": r"A - BK = \begin{bmatrix}1&0\\-k_1&2-k_2\end{bmatrix} \;\Rightarrow\; \lambda = 1,\ 2 - k_2"},
                {"text": "Coupled: both coefficients of the characteristic polynomial depend on K.", "tex": r"A - BK = \begin{bmatrix}1&1\\-k_1&2-k_2\end{bmatrix} \;\Rightarrow\; \lambda^2 - (3 - k_2)\lambda + (2 - k_2 + k_1)"},
                {"text": r"Matching $\lambda^2 + 3\lambda + 2$ (eigenvalues $-1, -2$) is possible.", "tex": r"k_2 = 6,\quad k_1 = 6:\quad \begin{bmatrix}1&1\\-6&-4\end{bmatrix},\ \ \mathrm{tr} = -3,\ \det = 2\ \checkmark"}
            ],
            "answer": r"In the uncoupled case the unstable eigenvalue $1$ cannot be moved by any $K$. In the coupled case both eigenvalues can be placed (here at $-1$ and $-2$). This is only a check of the claim; systematic gain design comes in later lectures."
        },
        "sources": {
            "video": [{"t": 660, "label": "Example: A = diag(1,2), B = [0,1]^T"},
                      {"t": 750, "label": "x1 is uncoupled from u: uncontrollable"},
                      {"t": 810, "label": "Two actuators, B = I: controllable"},
                      {"t": 900, "label": "Coupling term: same B becomes controllable"},
                      {"t": 990, "label": "Few actuators can control many coupled states"}],
            "book": BOOK[1:]
        },
        "tutorNotes": "Lecture 11:00-17:30; book Eqs. (8.28)-(8.30). Uncoupled A = diag(1,2), B = [0,1]^T: x1' = x1, uncontrollable (unstable mode 1 is fixed: A - BK = [[1,0],[-k1,2-k2]]). B = I: controllable. Coupled A = [[1,1],[0,2]], same B: controllable. Authored: with coupled A, B = [1,1]^T lies along the eigenvector of eigenvalue 2 and is uncontrollable; K = [6, 6] places coupled eigenvalues at -1, -2 (check only)."
    },
    {
        "nav": "Controllability matrix",
        "title": r"The controllability matrix $\mathcal{C}$ and the rank test",
        "time": [1050, 1290],
        "summary": r"Stack $B$, $AB$, $A^2B$, ..., $A^{n-1}B$ side by side to form $\mathcal{C}$, an $n \times nq$ matrix. The pair $(A, B)$ is controllable if and only if $\operatorname{rank}\mathcal{C} = n$, that is, the columns of $\mathcal{C}$ span all of $\mathbb{R}^n$.",
        "goals": [
            r"Build $\mathcal{C} = [B\ \ AB\ \ \cdots\ \ A^{n-1}B]$ and state its size $n \times nq$.",
            r"State the test $\operatorname{rank}\mathcal{C} = n$ and why it means full row rank.",
            r"Interpret the columns as the input direction passed repeatedly through the dynamics."
        ],
        "notes": [
            {"heading": "Building the matrix",
             "paragraphs": [
                 r"The controllability matrix (curly $\mathcal{C}$, not the measurement matrix $C$) is $\mathcal{C} = [B\ \ AB\ \ A^2B\ \ \cdots\ \ A^{n-1}B]$. Each block is $A$ times the previous block, with $A$ on the left, and has the same $n \times q$ shape as $B$. With $n$ blocks, $\mathcal{C}$ is $n \times nq$; for one input it is square, $n \times n$.",
                 r"The lecture presents the matrix first and promises the justification later; for small systems it is easy to build by hand."
             ]},
            {"heading": "The test",
             "paragraphs": [
                 r"$(A, B)$ is controllable if and only if $\operatorname{rank}\mathcal{C} = n$: there are $n$ linearly independent columns, so the columns span $\mathbb{R}^n$. If the rank is smaller, some directions in $\mathbb{R}^n$ are outside the column space and no input $Bu$ can push the state there.",
                 r"Precision: the lecture says “full column rank” around 19:00. For an $n \times nq$ matrix the right condition is rank $n$, i.e. full row rank. With $q > 1$ there are more columns than $n$, so the columns cannot all be independent; only in the single-input (square) case do full row and full column rank coincide."
             ]},
            {"heading": "Why these columns: kick and let it ring",
             "paragraphs": [
                 r"The lecture's intuition: kick the system in the $B$ direction and let the dynamics act on it repeatedly, like an impulse response. In discrete time this is literal (authored illustration): for $x_{k+1} = Ax_k + Bu_k$ starting from $x_0 = 0$, $x_1 = Bu_0$, $x_2 = ABu_0 + Bu_1$, $x_3 = A^2Bu_0 + ABu_1 + Bu_2$. Every reachable state is a combination of the columns of $\mathcal{C}$, so the reachable set from the origin is the column space of $\mathcal{C}$.",
                 r"From a nonzero initial state, the free motion of the initial condition is added on top of that set. The lecture shows why the rank test works in discrete time in later material and points to references for the continuous-time proof."
             ]},
            {"heading": "A yes/no answer",
             "paragraphs": [
                 r"The rank test is binary: controllable or not. It does not say how controllable, which matters a great deal in practice. Section 6 previews how the singular value decomposition of $\mathcal{C}$ starts to answer that."
             ]}
        ],
        "keyIdeas": [
            r"$\mathcal{C} = [B\ \ AB\ \ \cdots\ \ A^{n-1}B]$, $\;n \times nq$.",
            r"Controllable $\Leftrightarrow \operatorname{rank}\mathcal{C} = n$ (full row rank).",
            r"Reachable from $x_0 = 0$: the column space of $\mathcal{C}$."
        ],
        "example": {
            "title": "A three-state chain (authored)",
            "problem": r"$A = \begin{bmatrix}0&1&0\\0&0&1\\0&0&0\end{bmatrix}$. Find $\operatorname{rank}\mathcal{C}$ for $B = e_3 = [0,0,1]^T$ and for $B = e_1 = [1,0,0]^T$.",
            "steps": [
                {"text": r"$B = e_3$: multiplying by $A$ moves the 1 up one row each time.", "tex": r"AB = \begin{bmatrix}0\\1\\0\end{bmatrix},\ A^2B = \begin{bmatrix}1\\0\\0\end{bmatrix},\ \mathcal{C} = \begin{bmatrix}0&0&1\\0&1&0\\1&0&0\end{bmatrix}"},
                {"text": "Three independent columns.", "tex": r"\operatorname{rank}\mathcal{C} = 3 = n \;\Rightarrow\; \text{controllable}"},
                {"text": r"$B = e_1$: the first column of $A$ is zero, so $Ae_1 = 0$.", "tex": r"\mathcal{C} = \begin{bmatrix}1&0&0\\0&0&0\\0&0&0\end{bmatrix},\quad \operatorname{rank}\mathcal{C} = 1"}
            ],
            "answer": r"Pushing the end of the chain ($e_3$) reaches every state; pushing the start ($e_1$) reaches only $x_1$, because nothing flows from $x_1$ to the others."
        },
        "sources": {
            "video": [{"t": 1050, "label": "Curly C = [B AB A^2B ... A^(n-1)B]"},
                      {"t": 1140, "label": "Rank test (said as 'full column rank'; correct: rank n)"},
                      {"t": 1170, "label": "Discrete-time intuition: B passed through the dynamics"},
                      {"t": 1200, "label": "Directions outside the column space cannot be reached"},
                      {"t": 1230, "label": "rank C = n iff controllable; binary test"}],
            "book": BOOK[:1]
        },
        "tutorNotes": "Lecture 17:30-21:30; book Eq. (8.26). Curly C = [B AB ... A^(n-1)B], n-by-nq. Controllable iff rank C = n (full ROW rank; lecturer says 'full column rank', only equivalent for single input). Columns span the Krylov subspace; reachable set from x0 = 0 is col(C). Discrete-time illustration x2 = AB u0 + B u1 is authored. Test is binary; degree of controllability later."
    },
    {
        "nav": "Computing the rank",
        "title": r"Building $\mathcal{C}$ for the two examples",
        "time": [1290, 1470],
        "summary": r"For the uncoupled pair, $AB = [0, 2]^T$ and $\mathcal{C} = \begin{bmatrix}0&0\\1&2\end{bmatrix}$: determinant $0$, rank $1$, uncontrollable. For the coupled pair, $AB = [1, 2]^T$ and $\mathcal{C} = \begin{bmatrix}0&1\\1&2\end{bmatrix}$: determinant $-1$, rank $2$, controllable.",
        "goals": [
            r"Compute $AB$ (with $A$ on the left) and assemble $\mathcal{C}$ for both examples.",
            r"Decide rank from the determinant of a square $\mathcal{C}$ and from the geometry of its columns.",
            r"Explain why higher powers $A^kB$, $k \ge n$, cannot raise the rank."
        ],
        "notes": [
            {"heading": "Uncoupled pair",
             "paragraphs": [
                 r"$B = [0, 1]^T$ is the first column. Then $AB = \begin{bmatrix}1&0\\0&2\end{bmatrix}\begin{bmatrix}0\\1\end{bmatrix} = \begin{bmatrix}0\\2\end{bmatrix}$. With $n = 2$ we can stop: $\mathcal{C} = \begin{bmatrix}0&0\\1&2\end{bmatrix}$.",
                 r"Both columns point purely along $x_2$; the second is twice the first. $\det\mathcal{C} = 0$, $\operatorname{rank}\mathcal{C} = 1$, uncontrollable. The top row of zeros is the missing $x_1$ direction."
             ]},
            {"heading": "Going further does not help",
             "paragraphs": [
                 r"Multiplying again gives $A^2B = [0, 4]^T$, then $[0, 8]^T$, $[0, 16]^T$: the top entry is always zero. In general, the Cayley-Hamilton theorem (named here as background; the lecture does not prove it) writes $A^n$ as a combination of $I, A, \dots, A^{n-1}$, so columns $A^kB$ with $k \ge n$ never add a new direction. That is why $\mathcal{C}$ stops at $A^{n-1}B$."
             ]},
            {"heading": "Coupled pair",
             "paragraphs": [
                 r"Same $B$, new $A$: $AB = \begin{bmatrix}1&1\\0&2\end{bmatrix}\begin{bmatrix}0\\1\end{bmatrix} = \begin{bmatrix}1\\2\end{bmatrix}$. The coupling entry put a 1 into the top row. $\mathcal{C} = \begin{bmatrix}0&1\\1&2\end{bmatrix}$ has $\det\mathcal{C} = 0\cdot2 - 1\cdot1 = -1 \neq 0$, so rank $2$ and the pair is controllable.",
                 r"Order matters: $AB$ is $A$ (2$\times$2) times $B$ (2$\times$1). The lecture says “B times A” aloud once, but the board multiplies $A$ on the left; $BA$ is not even defined for a column $B$."
             ]},
            {"heading": "The consequences",
             "paragraphs": [
                 r"Once the rank is $n$, the conclusions of Section 2 follow: eigenvalues of $A - BK$ can be placed by choosing $K$, and an appropriate input drives the state anywhere. Why the rank implies this is the hard part; the lecture sketches it in discrete time later and defers the continuous-time proof to references."
             ]}
        ],
        "keyIdeas": [
            r"Uncoupled: $\mathcal{C} = \begin{bmatrix}0&0\\1&2\end{bmatrix}$, rank 1.",
            r"Coupled: $\mathcal{C} = \begin{bmatrix}0&1\\1&2\end{bmatrix}$, $\det = -1$, rank 2.",
            r"Powers beyond $A^{n-1}B$ add no new directions."
        ],
        "example": {
            "title": "The book's fourth example",
            "problem": r"Book Eq. (8.31), not worked in the lecture: $A = \mathrm{diag}(1, 2)$ (uncoupled) with $B = [1, 1]^T$. Is it controllable?",
            "steps": [
                {"text": "Multiply B by A.", "tex": r"AB = \begin{bmatrix}1&0\\0&2\end{bmatrix}\begin{bmatrix}1\\1\end{bmatrix} = \begin{bmatrix}1\\2\end{bmatrix}"},
                {"text": "Assemble and take the determinant.", "tex": r"\mathcal{C} = \begin{bmatrix}1&1\\1&2\end{bmatrix},\quad \det\mathcal{C} = 2 - 1 = 1 \neq 0"}
            ],
            "answer": r"Rank $2$: controllable, even though $A$ is uncoupled. The single actuator touches both states, and the two states have different rates ($1$ and $2$), so $B$ and $AB$ point in different directions. With equal rates ($A = I$) it would fail: $AB = B$."
        },
        "sources": {
            "video": [{"t": 1290, "label": "Compute C for the uncoupled example"},
                      {"t": 1320, "label": "A^2 B = [0,4]: always a row of zeros"},
                      {"t": 1350, "label": "Rank 1, determinant 0: uncontrollable"},
                      {"t": 1380, "label": "Coupled example: AB = [1,2], rank 2"},
                      {"t": 1440, "label": "Consequences: place poles, steer the state"}],
            "book": BOOK[1:]
        },
        "tutorNotes": "Lecture 21:30-24:30; book Eqs. (8.28), (8.30), (8.31). Uncoupled: AB = [0,2], C = [[0,0],[1,2]], det 0, rank 1; A^2B = [0,4] etc. Coupled: AB = [1,2], C = [[0,1],[1,2]], det -1, rank 2. Lecturer once says 'B * A' but computes A*B. Higher powers add nothing by Cayley-Hamilton (background, not proved in lecture). Book example B = [1,1], A = diag(1,2): C = [[1,1],[1,2]], det 1, controllable (not in lecture)."
    },
    {
        "nav": "MATLAB and limits",
        "title": "ctrb in MATLAB, limits of the test and what comes next",
        "time": [1470, 1949],
        "summary": r"MATLAB builds $\mathcal{C}$ with ctrb(A,B) and rank(ctrb(A,B)) gives $1$ and $2$ for the two examples. The test is for linear(ized) systems and only gives yes/no; the singular value decomposition of $\mathcal{C}$ will later rank directions from most to least controllable.",
        "goals": [
            r"Use ctrb and rank to test a pair $(A, B)$ and interpret the result.",
            r"Explain why an uncontrollable linearization does not settle controllability of the nonlinear system.",
            r"Distinguish the binary rank test from a degree of controllability, and treat numerical rank with a tolerance."
        ],
        "notes": [
            {"heading": "The computer test",
             "paragraphs": [
                 r"In MATLAB, ctrb(A,B) returns $\mathcal{C}$ and rank(ctrb(A,B)) its rank. In the demo, A = [1 0; 0 2], B = [0; 1] gives the matrix [0 0; 1 2] with rank 1 (not controllable), and A = [1 1; 0 2] with the same B gives [0 1; 1 2] with rank 2 (controllable), matching the board.",
                 r"For a large system you cannot judge the rank by eye, which is the point of the command. Numerically, rank is decided with a tolerance on the singular values: a tiny but nonzero coupling may be full rank in exact arithmetic while being nearly uncontrollable in practice. The explorer shows singular values next to the rank for that reason."
             ]},
            {"heading": "Linearizations and nonlinear systems",
             "paragraphs": [
                 r"The test applies to the linear model, often a linearization at a fixed point. A nonlinear system whose linearization is uncontrollable may still be controllable by exploiting the neglected nonlinear terms, or it may not; nonlinear controllability is a hard research question. This lecture sticks to linear controllability."
             ]},
            {"heading": "How controllable? (preview)",
             "paragraphs": [
                 r"Different $B$ matrices can make a system mathematically controllable to different degrees. The lecture previews that the singular value decomposition of $\mathcal{C}$ (which is $n$ tall) gives left singular vectors ordered from the most to the least controllable directions of $\mathbb{R}^n$; the gallon-of-gas analogy asks which directions you can travel furthest on a fixed budget.",
                 r"Careful: the singular values of $\mathcal{C}$ describe how coefficient vectors are amplified by $\mathcal{C}$. Exact continuous-time energy and reachability over a time horizon need the controllability Gramian, which comes in a later lecture. The explorer labels its coefficient sliders as an illustration, not an energy measure."
             ]},
            {"heading": "What else is related",
             "paragraphs": [
                 r"Uncontrollable is not always a disaster: if every uncontrollable mode is already stable, feedback can still stabilise the system (it is stabilizable). The lecture's uncoupled example is not, because its uncontrollable mode is the unstable $+1$.",
                 r"Coming next: why $\mathcal{C}$ is the right matrix, degrees of controllability via the SVD, and the actual design of $u = -Kx$, plus more MATLAB tools based on $A$ and $B$ (state-space models, impulse and frequency responses, pole placement)."
             ]}
        ],
        "keyIdeas": [
            r"rank(ctrb(A,B)) $= n$ $\Leftrightarrow$ controllable.",
            r"Linearization uncontrollable $\not\Rightarrow$ nonlinear system uncontrollable.",
            r"Rank is yes/no; SVD of $\mathcal{C}$ previews degree."
        ],
        "example": {
            "title": "Barely controllable (authored)",
            "problem": r"Replace the coupling 1 by $0.1$: $A = \begin{bmatrix}1&0.1\\0&2\end{bmatrix}$, $B = [0, 1]^T$. Find $\mathcal{C}$, its rank and its singular values.",
            "steps": [
                {"text": "Build the matrix.", "tex": r"AB = \begin{bmatrix}0.1\\2\end{bmatrix},\quad \mathcal{C} = \begin{bmatrix}0&0.1\\1&2\end{bmatrix},\quad \det\mathcal{C} = -0.1"},
                {"text": "Singular values (square roots of the eigenvalues of CᵀC).", "tex": r"\sigma_1 \approx 2.238,\quad \sigma_2 \approx 0.0447,\quad \sigma_1/\sigma_2 \approx 50"}
            ],
            "answer": r"Rank $2$, so controllable, but the small $\sigma_2$ warns that one direction (mostly $x_1$) is weakly affected. The rank test alone cannot tell this apart from the coupling-1 case."
        },
        "sources": {
            "video": [{"t": 1500, "label": "ctrb(A,B) and rank in MATLAB"},
                      {"t": 1530, "label": "Uncontrollable linearization, nonlinear may differ"},
                      {"t": 1590, "label": "Binary test; SVD of C previews degree of controllability"},
                      {"t": 1650, "label": "Gallon-of-gas analogy"},
                      {"t": 1710, "label": "Next: justification, SVD, designing u = -Kx"},
                      {"t": 1800, "label": "MATLAB demo: rank 1, then rank 2"},
                      {"t": 1920, "label": "Outlook: more MATLAB tools for A, B"}],
            "book": BOOK[:1]
        },
        "tutorNotes": "Lecture 24:30-32:29. ctrb(A,B), rank(ctrb(A,B)) returns 1 for A = [1 0;0 2], B = [0;1] and 2 for A = [1 1;0 2]. Nonlinear system may be controllable despite an uncontrollable linearization (open problem in general). Rank is binary; SVD of C previews most/least controllable directions (left singular vectors). Singular values of C are not continuous-time energy measures (needs Gramian, later). Numerical rank uses a tolerance. Stabilizability if uncontrollable modes are stable; lecture's uncontrollable mode +1 is unstable."
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
    q("q-bshape", r"A system has $n$ states and $q$ inputs. What is the shape of $B$ in $\dot x = Ax + Bu$?", [
        (r"$n \times q$", True, r"Right. $Bu$ must be an $n$-vector like $Ax$, and $u$ has $q$ entries, so $B$ is $n$ tall and $q$ wide: one column per actuator."),
        (r"$q \times n$", False, r"No. A $q \times n$ matrix cannot multiply the $q$-vector $u$ (unless $q = n$), and its result would have $q$ entries, not $n$."),
        (r"$n \times n$", False, r"No. That is the shape of $A$. $B$ is square only when there are as many inputs as states."),
        (r"$1 \times q$", False, r"No. That would turn $u$ into a single number, but $Bu$ is added to the $n$-vector $Ax$.")]),
    q("q-closed", r"Substitute $u = -Kx$ into $\dot x = Ax + Bu$. Which is correct?", [
        (r"$\dot x = (A - BK)x$", True, r"Right. $B(-Kx) = -BKx$ and factoring $x$ on the right gives $(A - BK)x$; $BK$ is $n \times n$."),
        (r"$\dot x = (A - KB)x$", False, r"No. Matrix products do not commute: the input matrix $B$ acts on $u = -Kx$, so $B$ stays on the left of $K$. ($KB$ is $q \times q$ and generally cannot even be subtracted from $A$.)"),
        (r"$\dot x = (A + BK)x$", False, r"No. The sign comes from $u = -Kx$. (Some books use $u = Kx$, but then the closed loop is $A + BK$ with that convention.)"),
        (r"$\dot x = A(I - BK)x$", False, r"No. Expanding gives $Ax - ABKx$, which has an extra $A$ in the feedback term.")]),
    q("q-depends", "Which quantities decide whether a linear system is controllable?", [
        (r"Only the pair $A$ and $B$.", True, r"Right. The test uses $\mathcal{C} = [B\ AB\ \cdots\ A^{n-1}B]$, built from $A$ and $B$ only. The gain $K$ is what controllability lets you choose."),
        (r"$A$ alone.", False, r"No. The same $A = \mathrm{diag}(1,2)$ is uncontrollable with $B = [0,1]^T$ and controllable with $B = I$ or $B = [1,1]^T$."),
        (r"The gain $K$ that we choose.", False, r"No. Controllability says whether a suitable $K$ exists; it does not depend on which $K$ you try."),
        (r"The initial state $x(0)$.", False, r"No. Controllability is a property of the system: it asks whether every target can be reached, from any start.")]),
    q("q-fixed", r"For $A = \mathrm{diag}(1, 2)$ and $B = [0, 1]^T$, what happens to the eigenvalue $1$ under any feedback $u = -Kx$?", [
        (r"It stays at $1$ for every $K$.", True, r"Right. $A - BK = \begin{bmatrix}1&0\\-k_1&2-k_2\end{bmatrix}$ is lower triangular, so $1$ is always an eigenvalue: the unstable mode is uncontrollable."),
        (r"It moves to $1 - k_1$.", False, r"No. $k_1$ only appears below the diagonal, which does not change the eigenvalues of a triangular matrix."),
        (r"It can be placed anywhere with a large enough $K$.", False, r"No. Gain size is irrelevant when the input never reaches $x_1$: $\dot x_1 = x_1$ in closed loop too."),
        (r"It becomes $2 - k_2$.", False, r"No. $2 - k_2$ is the other eigenvalue, the one $K$ can move.")]),
    q("q-csize", r"For $n = 4$ states and $q = 2$ inputs, what is the size of $\mathcal{C} = [B\ AB\ A^2B\ A^3B]$?", [
        (r"$4 \times 8$", True, r"Right. Each of the $n = 4$ blocks is $4 \times 2$, side by side: $n \times nq = 4 \times 8$."),
        (r"$4 \times 4$", False, r"No. That holds only for a single input; here each block has two columns."),
        (r"$8 \times 4$", False, r"No. The blocks sit next to each other, not stacked; every column lives in $\mathbb{R}^4$."),
        (r"$4 \times 6$", False, r"No. The powers run from $A^0$ to $A^{n-1} = A^3$, which is four blocks, not three.")]),
    q("q-rank", r"With $\mathcal{C}$ of size $n \times nq$ and $q > 1$, which statement is the correct controllability test?", [
        (r"$\operatorname{rank}\mathcal{C} = n$ (full row rank).", True, r"Right. The columns must span $\mathbb{R}^n$. The lecture says “full column rank”, which coincides with this only when $\mathcal{C}$ is square ($q = 1$)."),
        (r"$\operatorname{rank}\mathcal{C} = nq$ (full column rank).", False, r"No. An $n \times nq$ matrix has rank at most $n$, so with $q > 1$ this can never hold, even for the controllable $B = I$."),
        (r"$\det\mathcal{C} \neq 0$.", False, r"No. The determinant is defined only for square $\mathcal{C}$ (single input). For $q > 1$ use the rank."),
        (r"$\mathcal{C}$ has no zero entries.", False, r"No. $\mathcal{C} = \begin{bmatrix}0&1\\1&2\end{bmatrix}$ has a zero entry and is full rank; what matters is linear independence.")]),
    q("q-compute", r"$A = \begin{bmatrix}1&1\\0&2\end{bmatrix}$, $B = \begin{bmatrix}0\\1\end{bmatrix}$. What is $\mathcal{C}$?", [
        (r"$\begin{bmatrix}0&1\\1&2\end{bmatrix}$", True, r"Right. $AB = (0 + 1,\ 0 + 2) = (1, 2)$, so $\mathcal{C} = [B\ AB]$, with determinant $-1$: rank 2, controllable."),
        (r"$\begin{bmatrix}0&0\\1&2\end{bmatrix}$", False, r"No. That is the uncoupled example, where $A = \mathrm{diag}(1,2)$. The coupling entry adds $1 \cdot 1$ to the top of $AB$."),
        (r"$\begin{bmatrix}1&0\\2&1\end{bmatrix}$", False, r"No. The columns are in the wrong order: $B$ comes first, then $AB$. (Order does not change the rank, but it is not the defined $\mathcal{C}$.)"),
        (r"$\begin{bmatrix}0&1\\1&1\end{bmatrix}$", False, r"No. The second entry of $AB$ is $0\cdot0 + 2\cdot1 = 2$.")]),
    q("q-powers", r"For the uncoupled example, why doesn't adding $A^2B = [0, 4]^T$ make $\mathcal{C}$ full rank?", [
        (r"Every $A^kB$ has a zero top entry, so no column ever leaves the $x_2$ axis.", True, r"Right. In general Cayley-Hamilton makes $A^kB$ for $k \ge n$ a combination of earlier columns, which is why $\mathcal{C}$ stops at $A^{n-1}B$."),
        (r"Because $A^2B$ is too large.", False, r"No. Size is irrelevant to rank; direction is what counts, and $[0,4]^T$ points the same way as $B$."),
        (r"It would, if we kept going to $A^{10}B$.", False, r"No. $A^kB = [0, 2^k]^T$ for every $k$; the $x_1$ component stays zero."),
        (r"Because $\mathcal{C}$ must be square.", False, r"No. $\mathcal{C}$ is $n \times nq$; extra columns are allowed in principle, they just add nothing new here.")]),
    q("q-nonlinear", "A nonlinear system's linearization at a fixed point is uncontrollable. What follows?", [
        (r"Nothing definite: the nonlinear system may or may not be controllable.", True, r"Right. Neglected nonlinear terms can sometimes provide control authority; deciding nonlinear controllability is hard in general."),
        (r"The nonlinear system is certainly uncontrollable.", False, r"No. The lecture stresses that nonlinear terms might restore controllability."),
        (r"The nonlinear system is certainly controllable.", False, r"No. It might be, but nothing guarantees it."),
        (r"The linearization must have been computed wrongly.", False, r"No. Uncontrollable linearizations are common and perfectly valid.")]),
    q("q-svd", r"Two pairs both give $\operatorname{rank}\mathcal{C} = 2$, but one has singular values $(2.24, 0.045)$ and the other $(2.41, 0.41)$. What does this suggest?", [
        (r"Both are controllable, but the first has a much more weakly actuated direction.", True, r"Right. The rank test is yes/no. The singular values of $\mathcal{C}$ hint at degree; precise energy statements need the Gramian (later lecture)."),
        (r"The first is uncontrollable because $0.045 < 0.1$.", False, r"No. Any nonzero singular value counts towards the rank (up to numerical tolerance). Small means hard, not impossible."),
        (r"They are equally controllable, since the rank is the same.", False, r"No. That is exactly the limitation of the binary test that the SVD preview addresses."),
        (r"The singular values are the closed-loop eigenvalues.", False, r"No. They describe the column geometry of $\mathcal{C}$; closed-loop eigenvalues depend on $K$.")]),
]

EXPLORER = {
    "c": {"min": -2, "max": 2, "step": 0.1, "default": 0},
    "b1": {"min": -2, "max": 2, "step": 0.1, "default": 0},
    "b2": {"min": -2, "max": 2, "step": 0.1, "default": 1},
    "alpha": {"min": -2, "max": 2, "step": 0.1, "default": 1},
    "beta": {"min": -2, "max": 2, "step": 0.1, "default": 0.5},
    "dual": {"default": False},
    "range": 6,
    "relTol": 1e-9,
    "presets": [
        {"id": "uncoupled", "label": "Uncoupled", "c": 0, "b1": 0, "b2": 1, "dual": False, "alpha": 1, "beta": 0.5,
         "note": "Lecture example (8.28): $b$ and $Ab = (0, 2)$ both lie on the $x_2$ axis. Rank 1; the $x_1$ direction is unreachable."},
        {"id": "coupled", "label": "Coupled", "c": 1, "b1": 0, "b2": 1, "dual": False, "alpha": 1, "beta": 0.5,
         "note": "Lecture example (8.30): the coupling puts a 1 on top of $Ab = (1, 2)$. Rank 2, $\\det\\mathcal{C} = -1$."},
        {"id": "two", "label": "Two actuators", "c": 0, "b1": 0, "b2": 1, "dual": True, "alpha": 1, "beta": 0.5,
         "note": "Lecture example (8.29): $B = I$, so $\\mathcal{C} = [B\\ AB]$ is $2\\times4$ and has rank 2. The sliders move only the $b$, $Ab$ coefficients; the rank uses all four columns."},
        {"id": "book", "label": "Book: B = [1, 1]", "c": 0, "b1": 1, "b2": 1, "dual": False, "alpha": 1, "beta": 0.5,
         "note": "Book Eq. (8.31), not worked in the lecture: uncoupled $A$, but $b = (1, 1)$ touches both states with different rates. $\\det\\mathcal{C} = 1$."},
        {"id": "eigen", "label": "Along an eigenvector", "c": 1, "b1": 1, "b2": 1, "dual": False, "alpha": 1, "beta": 0.5,
         "note": "Authored: with the coupled $A$, $b = (1, 1)$ is an eigenvector ($Ab = 2b$), so $Ab$ adds no new direction. Coupling alone does not guarantee controllability."},
        {"id": "weak", "label": "Weak coupling", "c": 0.1, "b1": 0, "b2": 1, "dual": False, "alpha": 1, "beta": 0.5,
         "note": "Authored: rank 2, but $\\sigma_2 \\approx 0.045$: mathematically controllable, nearly uncontrollable in practice."}
    ],
    "tutorContext": "The explorer uses the authored family A = [[1, c], [0, 2]] (eigenvalues 1 and 2) with one input column b = (b1, b2), or, with the 'second actuator' box, B = [e1, b] (c = 0, b = (0,1) gives B = I). It computes AB explicitly, the controllability matrix C = [B, AB], its singular values (one-sided Jacobi), the numerical rank (sigma_i > 1e-9 * sigma_max; zero matrix has rank 0) and, for one input, det C = b2 (b1 - c b2). Single-input rank drops exactly when b2 = 0 (b along eigenvector (1,0) of eigenvalue 1) or b1 = c b2 (b along eigenvector (c,1) of eigenvalue 2). The plot shows b, Ab, the reachable set from x0 = 0 (point, line or plane = col C), the unreachable direction w (w^T C = 0) when rank 1, and the point alpha*b + beta*Ab. That point is a bounded coefficient illustration; read as a separate discrete-time companion x_(k+1) = A x_k + B u_k with x0 = 0 it is x_2 with u_1 = alpha, u_0 = beta. It is not a continuous-time energy or reachability measure (that needs the Gramian, later lecture). In dual mode the two coefficients act on the b and Ab columns only; the e1 columns are used for the rank."
}

COURSE = {
    "version": 1,
    "title": "Controllability: when can feedback steer a linear system?",
    "subtitle": "A study companion to Steve Brunton's Control Bootcamp lecture on controllability and Section 8.3 of Brunton & Kutz",
    "video": {"id": "u5Sv7YKAkt4", "title": "Controllability [Control Bootcamp] (Steve Brunton, University of Washington)",
              "duration": "32:29", "url": "https://www.youtube.com/watch?v=u5Sv7YKAkt4"},
    "book": {"title": "Data-Driven Science and Engineering: Machine Learning, Dynamical Systems, and Control",
             "authors": "S. L. Brunton and J. N. Kutz", "edition": "2017 preprint (Chapter 8, Linear Control Theory, Section 8.3)",
             "onlineUrl": "http://databookuw.com/databook.pdf",
             "pageNote": "Page references give the printed page and the page of the local PDF (printed page + 20 for these pages). The online copy may be a different revision with different PDF page numbers."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide; examples marked authored are not from the lecture. They summarize the lecture and the book; for the original wording, watch the lecture and read the chapter. Lecture captions, the video and the chapter text are not included in this guide.",
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
