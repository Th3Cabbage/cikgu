"""Source of courses/mit-de/phase-plane/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\phase-plane\\course_source.py

Unit 6 of the MIT Learn Differential Equations companion: playlist videos 27-34 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Chapter 3.
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
    (27, "cDfWtSqGiBY", "Pictures of Solutions", "21:01"),
    (28, "VqXKa11IA6A", "Phase Plane Pictures: Source, Sink, Saddle", "18:26"),
    (29, "n9H-6TQIEJc", "Phase Plane Pictures: Spirals and Centers", "13:46"),
    (30, "fd7ioT_wwPE", "Two First Order Equations: Stability", "10:32"),
    (31, "0hx59wYpFyY", "Linearization at Critical Points", "15:08"),
    (32, "N6pc8Axv3Gs", "Linearization of two nonlinear equations", "21:41"),
    (33, "GAOjfd5QJZE", "Eigenvalues and Stability: 2 by 2 Matrix, A", "19:30"),
    (34, "Jy5XpZqy56U", "The Tumbling Box in 3-D", "22:54"),
]

SECTIONS = [
    {
        "nav": "Pictures of solutions",
        "v": 27,
        "title": r"Direction fields and isoclines for $y' = f(t, y)$",
        "summary": r"At every point $(t, y)$ the equation gives a slope $f(t, y)$; small arrows with those slopes form the direction field, and solutions follow the arrows. Isoclines, the curves $f(t, y) = $ constant, carry arrows of equal slope and organise the picture.",
        "time": [0, 1261],
        "goals": [
            r"Draw arrows of slope $f(t, y)$ and sketch solutions that follow them.",
            r"Find steady states as horizontal lines of arrows.",
            r"Use isoclines $f(t, y) = m$ to draw the field quickly."
        ],
        "notes": [
            {"heading": "Arrows that show the slope",
             "paragraphs": [
                 r"An equation $dy/dt = f(t, y)$ prescribes the slope of the solution through each point. Draw a short arrow with that slope at many points of the $t,y$ plane: the direction field. A solution curve is tangent to every arrow it passes; you can sketch it without a formula.",
                 r"For $y' = 2 - y$ the slope depends only on $y$: $2$ on the line $y = 0$, $1$ on $y = 1$, $0$ on $y = 2$ and $-2$ on $y = 4$. All arrows on $y = 2$ are flat, so $y = 2$ is a steady solution, and the solutions $y = 2 + Ce^{-t}$ approach it from above and below."
             ]},
            {"heading": "The logistic picture",
             "paragraphs": [
                 r"For $y' = y - y^2$ the arrows are flat on $y = 0$ and $y = 1$. Between them the slope is positive (largest, $\tfrac14$, at $y = \tfrac12$): the S-curves of Unit 2 rise from $0$ to $1$. Above $1$ the arrows point down towards $1$; below $0$ they point further down, and those solutions fall away to $-\infty$."
             ]},
            {"heading": "Isoclines",
             "paragraphs": [
                 r"When $f$ depends on $t$ too, the curves $f(t, y) = m$ (isoclines) are where every arrow has the same slope $m$. For $y' = 1 + t - y$ the isoclines are the parallel lines $y = 1 + t - m$. The isocline $m = 1$ is $y = t$, and on it the arrows have slope $1$, pointing along the line itself: $y = t$ is a solution. All solutions $y = t + Ce^{-t}$ approach it."
             ]}
        ],
        "keyIdeas": [
            r"Arrow slope at $(t, y)$ is $f(t, y)$.",
            r"Flat rows of arrows: steady states.",
            r"Isocline: $f(t, y) = m$, all arrows of slope $m$.",
            r"An isocline whose slope matches its own direction is a solution."
        ],
        "example": {
            "title": "An isocline that is a solution (authored)",
            "problem": r"For $y' = t - y$, find the isoclines and the one straight-line solution.",
            "steps": [
                {"text": "Isoclines t - y = m are lines of slope 1.", "tex": r"y = t - m"},
                {"text": "A line of slope 1 is a solution where the arrows also have slope m = 1.", "tex": r"y = t - 1:\quad y' = 1 = t - (t - 1)"},
                {"text": "General solution and the approach.", "tex": r"y = t - 1 + Ce^{-t} \;\to\; t - 1"}
            ],
            "answer": r"The isocline $y = t - 1$ is itself a solution, and every other solution approaches it."
        },
        "sources": {
            "video": [vs(27, 0, "Pictures of solutions: arrows with slope f(t, y)"),
                      vs(27, 60, "Example dy/dt = 2 - y"),
                      vs(27, 240, "Arrows on y = 0, 1, 2, 4"),
                      vs(27, 360, "Solutions approach y = 2"),
                      vs(27, 510, "Logistic dy/dt = y - y^2"),
                      vs(27, 660, "S-curves between 0 and 1"),
                      vs(27, 780, "Below 0: falling away"),
                      vs(27, 900, "dy/dt = 1 + t - y and isoclines"),
                      vs(27, 1080, "The isocline y = t is a solution")],
            "book": [bk(154, "Section 3.1: the direction field and isoclines")]
        },
        "tutorNotes": "Video 27. Direction field: arrow of slope f(t, y). y' = 2 - y: slopes 2, 1, 0, -2 at y = 0, 1, 2, 4; y = 2 + Ce^(-t). y' = y - y^2: flat at 0 and 1, max slope 1/4 at y = 1/2. Isoclines f(t, y) = m. y' = 1 + t - y: isoclines y = 1 + t - m; m = 1 gives y = t, a solution; y = t + Ce^(-t)."
    },
    {
        "nav": "Source, sink, saddle",
        "v": 28,
        "title": r"The phase plane $(y, y')$: sources, sinks and saddles",
        "summary": r"Plot $y'$ against $y$ instead of $y$ against $t$. For $y'' + By' + Cy = 0$ with real roots $s_1, s_2$, the pure solutions travel on the straight lines $y' = s_1y$ and $y' = s_2y$. Two positive roots give a source, two negative roots a sink, opposite signs a saddle.",
        "time": [0, 1106],
        "goals": [
            r"Draw a solution in the phase plane with axes $y$ and $y'$.",
            r"Find the straight-line solutions $y' = s y$ from the roots.",
            r"Classify source, sink and saddle by the signs of $s_1, s_2$."
        ],
        "notes": [
            {"heading": "A new picture",
             "paragraphs": [
                 r"A second order equation needs two numbers at each moment, $y$ and $y'$. The phase plane plots the point $(y(t), y'(t))$ as $t$ runs; time is hidden, and the curve is a trajectory."
             ]},
            {"heading": "Example: two positive roots",
             "paragraphs": [
                 r"$y'' - 3y' + 2y = 0$ has $s = 1, 2$, so $y = c_1e^{t} + c_2e^{2t}$ and $y' = c_1e^t + 2c_2e^{2t}$. With $c_2 = 0$ the point moves on the line $y' = y$; with $c_1 = 0$ on $y' = 2y$. With $c_1 = c_2 = 1$ the start is $(2, 3)$; as $t \to -\infty$ the $e^t$ term dominates and the curve leaves the origin along slope $1$; as $t \to +\infty$ the $e^{2t}$ term dominates and it bends to slope $2$. Everything moves away from the origin: a source."
             ]},
            {"heading": "Sink and saddle",
             "paragraphs": [
                 r"Positive damping, $y'' + 3y' + 2y = 0$, has $s = -1, -2$: the same lines with arrows reversed, all trajectories enter the origin. That is a sink, a stable critical point.",
                 r"$y'' = 4y$ has $s = 2$ and $s = -2$. On the line $y' = -2y$ solutions come in; on $y' = 2y$ they go out. Every other trajectory comes in near the first line and leaves near the second. That is a saddle: unstable, because almost every start eventually leaves."
             ]}
        ],
        "keyIdeas": [
            r"Phase plane: the point $(y, y')$.",
            r"Real roots: straight-line solutions $y' = s_iy$.",
            r"Both $s > 0$: source; both $s < 0$: sink.",
            r"$s_1 > 0 > s_2$: saddle (unstable)."
        ],
        "example": {
            "title": "A sink from a resting start (authored)",
            "problem": r"Solve $y'' + 3y' + 2y = 0$ with $y(0) = 1$, $y'(0) = 0$, and describe the trajectory.",
            "steps": [
                {"text": "Roots -1 and -2; match y(0) = 1, y'(0) = 0.", "tex": r"y = 2e^{-t} - e^{-2t},\quad y' = -2e^{-t} + 2e^{-2t}"},
                {"text": "Late times: the slower e^(-t) term dominates.", "tex": r"y' \approx -y \quad (t \to \infty)"},
                {"text": "So the trajectory starts at (1, 0) and enters the origin along y' = -y.", "tex": r"(y, y') \to (0, 0)"}
            ],
            "answer": r"A sink: the curve from $(1, 0)$ dips below the axis and comes into the origin tangent to the slow line $y' = -y$."
        },
        "sources": {
            "video": [vs(28, 0, "Axes y and y'"),
                      vs(28, 60, "y'' - 3y' + 2y = 0, s = 1 and 2"),
                      vs(28, 240, "Straight lines y' = y and y' = 2y"),
                      vs(28, 390, "c1 = c2 = 1: start at (2, 3)"),
                      vs(28, 600, "Slope 1 at the start, slope 2 later"),
                      vs(28, 720, "A source"),
                      vs(28, 750, "Positive damping: sink"),
                      vs(28, 780, "y'' = 4y: s = 2 and -2"),
                      vs(28, 840, "The saddle")],
            "book": [bk(160, "Section 3.2: sources, sinks, saddles and spirals")]
        },
        "tutorNotes": "Video 28. Phase plane (y, y'). y'' - 3y' + 2y = 0: s = 1, 2, y = c1 e^t + c2 e^(2t), lines y' = y and y' = 2y; c1 = c2 = 1 starts at (2, 3); source. y'' + 3y' + 2y = 0: sink. y'' = 4y: s = +-2, saddle: in along y' = -2y, out along y' = 2y. (Board writes e^(2t) where e^(-2t) is meant at one point.)"
    },
    {
        "nav": "Spirals and centers",
        "v": 29,
        "title": r"Complex roots: spirals and centers",
        "summary": r"Roots $s = a \pm i\omega$ make trajectories turn. With $a < 0$ they spiral into the origin (spiral sink), with $a > 0$ out of it (spiral source), and with $a = 0$ they close into ellipses around a center. Six cases cover every $2\times2$ picture.",
        "time": [0, 826],
        "goals": [
            r"Draw the center of $y'' + \omega^2y = 0$ as an ellipse.",
            r"Draw spirals for $y'' \pm 2y' + 2y = 0$.",
            r"List the six cases: source, sink, saddle, spiral source, spiral sink, center."
        ],
        "notes": [
            {"heading": "Center",
             "paragraphs": [
                 r"$y'' + \omega^2y = 0$ gives $y = c_1\cos\omega t + c_2\sin\omega t$ and $y' = -c_1\omega\sin\omega t + c_2\omega\cos\omega t$. The point $(y, y')$ travels around the ellipse $y^2 + (y'/\omega)^2 = c_1^2 + c_2^2$, forever: a center. With $\omega = 1$ it is a circle; with $\omega = 2$ the ellipse is twice as tall as it is wide."
             ]},
            {"heading": "Spirals",
             "paragraphs": [
                 r"$y'' + 2y' + 2y = 0$ has $s = -1 \pm i$, so $y = e^{-t}(c_1\cos t + c_2\sin t)$. The rotation from $\cos t, \sin t$ combined with the shrinking factor $e^{-t}$ gives a spiral into the origin, a spiral sink. With $-2y'$ instead, $s = 1 \pm i$ and the spiral unwinds outward: a spiral source."
             ]},
            {"heading": "Six pictures",
             "paragraphs": [
                 r"Real roots: source (both positive), sink (both negative), saddle (opposite signs). Complex roots $a \pm i\omega$: spiral source ($a > 0$), spiral sink ($a < 0$), center ($a = 0$). Asymptotically stable (every nearby solution approaches the critical point) means sink or spiral sink. A center is stable in the weaker sense: nearby solutions stay nearby but do not approach. It is called neutrally stable."
             ]}
        ],
        "keyIdeas": [
            r"$a \pm i\omega$: rotation $\times$ $e^{at}$.",
            r"$a < 0$ spiral sink, $a > 0$ spiral source.",
            r"$a = 0$: center (closed ellipses).",
            r"Six cases in all."
        ],
        "example": {
            "title": "How fast a spiral closes in (authored)",
            "problem": r"For $y'' + 2y' + 5y = 0$, classify the origin and find how much the distance shrinks in one turn.",
            "steps": [
                {"text": "Roots.", "tex": r"s = -1 \pm 2i"},
                {"text": "Real part -1 < 0: spiral sink. One turn of the angle 2t takes t = pi.", "tex": r"T = \frac{2\pi}{\omega} = \pi"},
                {"text": "Each turn multiplies the size by e^(a T).", "tex": r"e^{-\pi} \approx 0.043"}
            ],
            "answer": r"A spiral sink; each full turn shrinks the trajectory by the factor $e^{-\pi} \approx 0.04$."
        },
        "sources": {
            "video": [vs(29, 0, "Complex roots: the six cases"),
                      vs(29, 210, "Center: y'' + omega^2 y = 0"),
                      vs(29, 300, "y and y' trace an ellipse"),
                      vs(29, 420, "Height omega: ellipse, circle when omega = 1"),
                      vs(29, 450, "y'' + 2y' + 2y = 0: s = -1 +- i"),
                      vs(29, 570, "Spiral sink"),
                      vs(29, 660, "Spiral source with s = 1 +- i")],
            "book": [bk(161, "Spirals and centers"),
                     bk(165, "The six pictures")]
        },
        "tutorNotes": "Video 29. Complex roots a +- i omega. Center y'' + omega^2 y = 0: ellipse y^2 + (y'/omega)^2 = const. y'' + 2y' + 2y = 0: s = -1 +- i, spiral sink; y'' - 2y' + 2y = 0: s = 1 +- i, spiral source. Six cases: source, sink, saddle, spiral source, spiral sink, center."
    },
    {
        "nav": "2 by 2 stability",
        "v": 30,
        "title": r"Systems $y' = Ay$: trace, determinant and stability",
        "summary": r"A second order equation becomes a first order system with the companion matrix $\begin{bmatrix}0 & 1\\ -C & -B\end{bmatrix}$. For any $2\times2$ matrix, $\lambda^2 - (\text{trace})\lambda + \det = 0$, so the eigenvalues have sum $=$ trace and product $=$ det. The system is asymptotically stable exactly when trace $< 0$ and det $> 0$.",
        "time": [0, 632],
        "goals": [
            r"Write $y'' + By' + Cy = 0$ as a system with the companion matrix.",
            r"Find eigenvalues from $\lambda^2 - T\lambda + D = 0$ with $T$ = trace, $D$ = det.",
            r"Decide stability from the signs of $T$ and $D$.",
            r"Place a matrix in the trace-determinant plane."
        ],
        "notes": [
            {"heading": "Companion matrix",
             "paragraphs": [
                 r"Let the vector be $\mathbf{z} = (y, y')$. Then $y' = y'$ and $y'' = -Cy - By'$, which is $\mathbf{z}' = A\mathbf{z}$ with $A = \begin{bmatrix}0 & 1\\ -C & -B\end{bmatrix}$. Its eigenvalue equation is $\lambda^2 + B\lambda + C = 0$: the old $s$ is the new $\lambda$. Second order stability was $B > 0$ and $C > 0$."
             ]},
            {"heading": "Any 2 by 2 matrix",
             "paragraphs": [
                 r"Try $\mathbf{z} = e^{\lambda t}\mathbf{x}$: then $A\mathbf{x} = \lambda\mathbf{x}$, and $\det(A - \lambda I) = 0$. For $A = \begin{bmatrix}a & b\\ c & d\end{bmatrix}$ this is $\lambda^2 - (a + d)\lambda + (ad - bc) = 0$. So $\lambda_1 + \lambda_2 = a + d$ (the trace $T$) and $\lambda_1\lambda_2 = ad - bc$ (the determinant $D$). Example: $\begin{bmatrix}2 & 4\\ 4 & 2\end{bmatrix}$ has $T = 4$, $D = -12$, so $\lambda = 6$ and $-2$."
             ]},
            {"heading": "The stability test",
             "paragraphs": [
                 r"Asymptotically stable means every solution goes to $\mathbf{0}$, which happens when both eigenvalues have negative real part. (A center, trace $0$ and det $> 0$, is stable in the weaker sense: solutions stay bounded but keep circling.) If the eigenvalues are real, both are negative exactly when their sum is negative and their product positive. If they are complex, $a \pm i\omega$, the product $a^2 + \omega^2$ is automatically positive and the sum $2a$ is negative exactly when $a < 0$. Either way: asymptotically stable $\Leftrightarrow$ $T < 0$ and $D > 0$.",
                 r"The trace-determinant plane draws all cases at once: $D < 0$ saddles; above the parabola $T^2 = 4D$ spirals (centers on the $D$ axis); below it nodes (sources for $T > 0$, sinks for $T < 0$)."
             ]}
        ],
        "keyIdeas": [
            r"Companion matrix $\begin{bmatrix}0 & 1\\ -C & -B\end{bmatrix}$.",
            r"$\lambda^2 - T\lambda + D = 0$.",
            r"Asymptotically stable $\Leftrightarrow$ $T < 0$ and $D > 0$.",
            r"$D < 0$: saddle; $T^2 < 4D$: spiral."
        ],
        "example": {
            "title": "Classify a matrix (authored)",
            "problem": r"Classify $\mathbf{z}' = A\mathbf{z}$ for $A = \begin{bmatrix}1 & 2\\ -3 & -4\end{bmatrix}$.",
            "steps": [
                {"text": "Trace and determinant.", "tex": r"T = -3,\qquad D = -4 + 6 = 2"},
                {"text": "Eigenvalues.", "tex": r"\lambda^2 + 3\lambda + 2 = 0 \;\Rightarrow\; \lambda = -1,\ -2"},
                {"text": "Eigenvectors from (A - lambda I) x = 0.", "tex": r"\lambda = -1:\ (1, -1),\qquad \lambda = -2:\ (2, -3)"}
            ],
            "answer": r"$T < 0$, $D > 0$, $T^2 > 4D$: a stable node (sink), with straight-line solutions along $(1, -1)$ and $(2, -3)$."
        },
        "sources": {
            "video": [vs(30, 0, "y'' + By' + Cy = 0 as two first order equations"),
                      vs(30, 150, "Companion matrix [0 1; -C -B]"),
                      vs(30, 270, "s becomes lambda"),
                      vs(30, 300, "Stability: B > 0 and C > 0"),
                      vs(30, 450, "z = e^(lambda t) x, A x = lambda x"),
                      vs(33, 30, "A x = lambda x, det(A - lambda I) = 0"),
                      vs(33, 300, "lambda^2 - (a + d) lambda + (ad - bc)"),
                      vs(33, 480, "Example [2 4; 4 2]: 6 and -2"),
                      vs(33, 930, "Stable: trace < 0 and det > 0"),
                      vs(33, 1050, "Complex case: product a^2 + omega^2")],
            "book": [bk(165, "Stability for 2 by 2 matrices"),
                     bk(166, "The trace-determinant plane")]
        },
        "tutorNotes": "Videos 30 and 33. Companion matrix [0 1; -C -B] for y'' + By' + Cy = 0; eigenvalues solve lambda^2 + B lambda + C = 0. General 2x2: lambda^2 - (a + d) lambda + (ad - bc) = 0, sum = trace, product = det. [2 4; 4 2]: T = 4, D = -12, lambda = 6, -2. Asymptotically stable iff T < 0 and D > 0 (a center, T = 0 and D > 0, is only neutrally stable). D < 0 saddle; T^2 < 4D spiral; T = 0, D > 0 center."
    },
    {
        "nav": "Linearization",
        "v": 31,
        "title": r"Linearization at critical points: the Jacobian",
        "summary": r"Near a critical point a nonlinear system behaves like its linear part. For one equation the rate is $f'(Y)$; for two equations $y' = f(y, z)$, $z' = g(y, z)$ it is the Jacobian matrix of partial derivatives. Predator-prey $y' = y - yz$, $z' = yz - z$ has a saddle at $(0, 0)$ and a center at $(1, 1)$.",
        "time": [0, 908],
        "goals": [
            r"Find critical points by solving $f = g = 0$.",
            r"Compute the Jacobian $J = \begin{bmatrix}f_y & f_z\\ g_y & g_z\end{bmatrix}$ at each.",
            r"Classify each critical point from $J$.",
            r"Apply the method to predator-prey and to a pendulum."
        ],
        "notes": [
            {"heading": "One equation",
             "paragraphs": [
                 r"For $y' = f(y)$ with $f(Y) = 0$, the tangent line gives $f(y) \approx f'(Y)(y - Y)$, so $y - Y \approx Ce^{f'(Y)t}$ (Unit 2). Example $y' = 3y - y^2$: $Y = 0$ with $f' = 3$ (unstable), $Y = 3$ with $f' = -3$ (stable)."
             ]},
            {"heading": "Two equations",
             "paragraphs": [
                 r"For $y' = f(y, z)$, $z' = g(y, z)$, a critical point $(Y, Z)$ has $f = g = 0$. Near it, the tangent plane approximations give the linear system $\begin{bmatrix}y - Y\\ z - Z\end{bmatrix}' \approx J\begin{bmatrix}y - Y\\ z - Z\end{bmatrix}$ with the Jacobian $J = \begin{bmatrix}\partial f/\partial y & \partial f/\partial z\\ \partial g/\partial y & \partial g/\partial z\end{bmatrix}$ evaluated at $(Y, Z)$. Then Section 4 applies to $J$."
             ]},
            {"heading": "Predator and prey",
             "paragraphs": [
                 r"Rabbits $y$ grow and are eaten; foxes $z$ die out without rabbits and grow by eating: $y' = y - yz$, $z' = yz - z$. Critical points: $y(1 - z) = 0$ and $z(y - 1) = 0$ give $(0, 0)$ and $(1, 1)$. The Jacobian is $J = \begin{bmatrix}1 - z & -y\\ z & y - 1\end{bmatrix}$.",
                 r"At $(0, 0)$: $J = \begin{bmatrix}1 & 0\\ 0 & -1\end{bmatrix}$, eigenvalues $1, -1$: a saddle. At $(1, 1)$: $J = \begin{bmatrix}0 & -1\\ 1 & 0\end{bmatrix}$, eigenvalues $\pm i$: a center for the linearization. The populations cycle around $(1, 1)$. (For a center the linear test alone does not settle the nonlinear behaviour; here a conserved quantity shows the orbits really close.)"
             ]}
        ],
        "keyIdeas": [
            r"Critical point: $f = g = 0$.",
            r"$J = \begin{bmatrix}f_y & f_z\\ g_y & g_z\end{bmatrix}$ at the point.",
            r"Predator-prey: saddle at $(0,0)$, center at $(1,1)$.",
            r"A linear center is a borderline case for the nonlinear system."
        ],
        "example": {
            "title": "A damped pendulum (authored)",
            "problem": r"Linearize $\theta' = \omega$, $\omega' = -\sin\theta - \tfrac12\omega$ at $(0, 0)$ and at $(\pi, 0)$.",
            "steps": [
                {"text": "Jacobian: partial derivatives of (omega, -sin theta - omega/2).", "tex": r"J = \begin{bmatrix}0 & 1\\ -\cos\theta & -\tfrac12\end{bmatrix}"},
                {"text": "Hanging down, theta = 0: T = -1/2, D = 1, T^2 < 4D.", "tex": r"\lambda = -\tfrac14 \pm i\sqrt{15}/4\quad\text{(spiral sink)}"},
                {"text": "Upside down, theta = pi: D = -1 < 0.", "tex": r"J = \begin{bmatrix}0 & 1\\ 1 & -\tfrac12\end{bmatrix}\quad\text{(saddle)}"}
            ],
            "answer": r"The hanging position is a stable spiral; the inverted position is a saddle (unstable)."
        },
        "sources": {
            "video": [vs(31, 0, "Critical points, f(Y) = 0"),
                      vs(31, 270, "Tangent line f(y) ~ (y - Y) f'(Y)"),
                      vs(31, 510, "Example 3y - y^2: Y = 0 and Y = 3"),
                      vs(31, 750, "Preview: two equations"),
                      vs(32, 120, "Predator-prey y' = y - yz, z' = yz - z"),
                      vs(32, 300, "Critical points (0, 0) and (1, 1)"),
                      vs(32, 720, "Jacobian matrix of first derivatives"),
                      vs(32, 900, "At (0, 0): a saddle"),
                      vs(32, 990, "At (1, 1): eigenvalues +-i, a center")],
            "book": [bk(170, "Section 3.3: linearization and stability in 2D and 3D"),
                     bk(172, "Predator-prey and its critical points")]
        },
        "tutorNotes": "Videos 31-32. y' = f(y): f(y) ~ f'(Y)(y - Y); 3y - y^2 at 0 (f' = 3, unstable) and 3 (f' = -3, stable). Two equations: Jacobian J = [f_y f_z; g_y g_z] at the critical point. Predator-prey y' = y - yz, z' = yz - z: critical (0,0), (1,1); J = [1 - z, -y; z, y - 1]; (0,0): diag(1, -1) saddle; (1,1): [0 -1; 1 0], eigenvalues +-i, center of the linearization (orbits close; linear test alone is inconclusive for centers)."
    },
    {
        "nav": "The tumbling box",
        "v": 34,
        "title": r"Three dimensions: the tumbling box",
        "summary": r"A box spinning about its axes obeys $x' = yz$, $y' = -2xz$, $z' = xy$. The six critical points $(\pm1, 0, 0)$, $(0, \pm1, 0)$, $(0, 0, \pm1)$ are spins about the three axes. The Jacobian gives a center about the shortest and longest axes and a saddle about the middle axis: the middle spin tumbles.",
        "time": [0, 1374],
        "goals": [
            r"Show that $x^2 + y^2 + z^2$ is constant, so solutions stay on a sphere.",
            r"Find further conserved quantities such as $2x^2 + y^2$.",
            r"Compute the $3\times3$ Jacobian at $(1, 0, 0)$ and $(0, 1, 0)$ and compare."
        ],
        "notes": [
            {"heading": "The equations",
             "paragraphs": [
                 r"Euler's equations for a rigid body, in Strang's simplest form, are $x' = yz$, $y' = -2xz$, $z' = xy$, where $x, y, z$ measure the spin about the three axes of a box (short, middle, long). A spin about one axis alone, such as $(1, 0, 0)$, makes every right side zero: the six points $(\pm1, 0, 0)$, $(0, \pm1, 0)$, $(0, 0, \pm1)$ are critical points (the origin too)."
             ]},
            {"heading": "Conserved quantities",
             "paragraphs": [
                 r"Multiply each equation by its variable and add: $xx' + yy' + zz' = xyz - 2xyz + xyz = 0$. So $x^2 + y^2 + z^2$ never changes and the motion stays on a sphere. Similarly $\tfrac{d}{dt}(2x^2 + y^2) = 4xyz - 4xyz = 0$ and $\tfrac{d}{dt}(x^2 - z^2) = 0$. Take a start with $x^2 + y^2 + z^2 = 1$, so the motion stays on the unit sphere. Each trajectory lies where the sphere meets a level surface of these quantities: closed loops around $(\pm1,0,0)$ and around $(0,0,\pm1)$. The level curves through $(0,\pm1,0)$ cross there, but no trajectory passes through those points, which are equilibria. Instead, separate branches (separatrices) approach the saddle points as $t \to \pm\infty$, and they divide the loops of one kind from the loops of the other."
             ]},
            {"heading": "Linearization",
             "paragraphs": [
                 r"The Jacobian is $J = \begin{bmatrix}0 & z & y\\ -2z & 0 & -2x\\ y & x & 0\end{bmatrix}$. At $(1, 0, 0)$: $\lambda = 0, \pm i\sqrt2$, a center (neutrally stable): the box spins steadily. At $(0, 1, 0)$: $J = \begin{bmatrix}0 & 0 & 1\\ 0 & 0 & 0\\ 1 & 0 & 0\end{bmatrix}$ with $\lambda = 0, 1, -1$: a saddle. A small error grows like $e^t$, and the box tumbles. Throwing a book (with a rubber band) shows it: clean spins about the long and short axes, a flip about the middle one."
             ]}
        ],
        "keyIdeas": [
            r"$x' = yz$, $y' = -2xz$, $z' = xy$.",
            r"$x^2 + y^2 + z^2$ is conserved: motion on a sphere.",
            r"$(1,0,0)$, $(0,0,1)$: $\lambda = 0, \pm i\sqrt2$ (stable spin).",
            r"$(0,1,0)$: $\lambda = 0, \pm1$ (tumbles)."
        ],
        "example": {
            "title": "Check a conserved quantity (authored)",
            "problem": r"Show that $y^2 + 2z^2$ is constant along solutions, and find the Jacobian eigenvalues at $(0, 0, 1)$.",
            "steps": [
                {"text": "Differentiate and substitute.", "tex": r"\frac{d}{dt}(y^2 + 2z^2) = 2y(-2xz) + 4z(xy) = 0"},
                {"text": "Jacobian at (0, 0, 1).", "tex": r"J = \begin{bmatrix}0 & 1 & 0\\ -2 & 0 & 0\\ 0 & 0 & 0\end{bmatrix}"},
                {"text": "Characteristic polynomial.", "tex": r"-\lambda(\lambda^2 + 2) = 0 \;\Rightarrow\; \lambda = 0,\ \pm i\sqrt2"}
            ],
            "answer": r"$y^2 + 2z^2$ is conserved; at $(0,0,1)$ the eigenvalues $0, \pm i\sqrt2$ give a neutrally stable spin."
        },
        "sources": {
            "video": [vs(34, 30, "x' = yz, y' = -2xz, z' = xy"),
                      vs(34, 210, "Multiply and add: a sphere"),
                      vs(34, 600, "More conserved quantities"),
                      vs(34, 660, "Critical points on the axes"),
                      vs(34, 780, "The 3 by 3 Jacobian"),
                      vs(34, 900, "At (1, 0, 0): imaginary eigenvalues"),
                      vs(34, 1020, "At (0, 1, 0): a saddle"),
                      vs(34, 1140, "Throwing a book")],
            "book": [bk(176, "A special 3 by 3 system: a tumbling box"),
                     bk(177, "Conserved quantities and the sphere")]
        },
        "tutorNotes": "Video 34. x' = yz, y' = -2xz, z' = xy. Conserved: x^2 + y^2 + z^2 (sphere), 2x^2 + y^2, y^2 + 2z^2, x^2 - z^2. Critical points (+-1,0,0), (0,+-1,0), (0,0,+-1), origin. J = [0 z y; -2z 0 -2x; y x 0]. At (1,0,0): lambda = 0, +-i sqrt2 (center, stable spin); at (0,0,1): same; at (0,1,0): lambda = 0, 1, -1 (saddle, tumbles)."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-field", r"For $y' = 2 - y$, what is the slope of the direction-field arrows on the line $y = 4$?", [
        (r"$-2$", True, r"Right. $f = 2 - 4 = -2$ at every $t$ on that line."),
        (r"$2$", False, r"No. That is the slope on $y = 0$."),
        (r"$0$", False, r"No. Arrows are flat only on the steady state $y = 2$."),
        (r"$4$", False, r"No. The slope is $f(t, y)$, not $y$.")]),
    q("q-isocline", r"For $y' = 1 + t - y$, which isocline is itself a solution?", [
        (r"$y = t$ (slope $m = 1$)", True, r"Right. On $y = t$ the arrows have slope $1 + t - t = 1$, the line's own slope."),
        (r"$y = 1 + t$ (slope $m = 0$)", False, r"No. Its arrows are flat but the line rises with slope $1$."),
        (r"$y = t - 1$ (slope $m = 2$)", False, r"No. The arrows have slope $2$, the line slope $1$."),
        (r"None of them.", False, r"No. Check $y = t$: $y' = 1 = 1 + t - t$.")]),
    q("q-saddle", r"What kind of critical point does $y'' = 9y$ have at the origin of the phase plane?", [
        (r"A saddle", True, r"Right. $s = \pm3$: one root positive, one negative."),
        (r"A center", False, r"No. A center needs $y'' = -9y$, with imaginary roots."),
        (r"A sink", False, r"No. A sink needs both roots negative."),
        (r"A source", False, r"No. A source needs both roots positive.")]),
    q("q-lines", r"For $y'' - 3y' + 2y = 0$, along which lines do the straight-line trajectories run in the $(y, y')$ plane?", [
        (r"$y' = y$ and $y' = 2y$", True, r"Right. With only $e^{st}$ present, $y' = sy$; the roots are $1$ and $2$."),
        (r"$y' = -y$ and $y' = -2y$", False, r"No. Those belong to $y'' + 3y' + 2y = 0$."),
        (r"$y = t$ and $y = 2t$", False, r"No. The phase plane has $y$ and $y'$ on its axes, not $t$."),
        (r"The axes $y = 0$ and $y' = 0$", False, r"No. The axes are not invariant here.")]),
    q("q-spiral", r"The roots are $s = 0.3 \pm 2i$. What does the phase-plane picture look like?", [
        (r"A spiral source", True, r"Right. Complex roots rotate; the positive real part $0.3$ makes the spiral grow."),
        (r"A spiral sink", False, r"No. A sink needs a negative real part."),
        (r"A center", False, r"No. A center needs real part exactly $0$."),
        (r"A saddle", False, r"No. Saddles have real roots of opposite signs.")]),
    q("q-companion", r"What is the companion matrix of $y'' + 5y' + 6y = 0$ for $\mathbf{z} = (y, y')$?", [
        (r"$\begin{bmatrix}0 & 1\\ -6 & -5\end{bmatrix}$", True, r"Right. $y' = y'$ and $y'' = -6y - 5y'$."),
        (r"$\begin{bmatrix}0 & 1\\ 6 & 5\end{bmatrix}$", False, r"No. Moving $5y' + 6y$ to the right side brings minus signs."),
        (r"$\begin{bmatrix}1 & 0\\ -5 & -6\end{bmatrix}$", False, r"No. The first row must say $y' = 0\cdot y + 1\cdot y'$."),
        (r"$\begin{bmatrix}-5 & -6\\ 1 & 0\end{bmatrix}$", False, r"No. That orders the vector as $(y', y)$.")]),
    q("q-tracedet", r"Which matrix makes $\mathbf{z}' = A\mathbf{z}$ asymptotically stable (every solution tends to $\mathbf{0}$)?", [
        (r"$\begin{bmatrix}-2 & 1\\ -3 & -1\end{bmatrix}$", True, r"Right. Trace $-3 < 0$ and det $2 + 3 = 5 > 0$."),
        (r"$\begin{bmatrix}-2 & 1\\ 3 & -1\end{bmatrix}$", False, r"No. Det $= 2 - 3 = -1 < 0$: a saddle."),
        (r"$\begin{bmatrix}2 & 1\\ -3 & -1\end{bmatrix}$", False, r"No. Trace $= 1 > 0$."),
        (r"$\begin{bmatrix}0 & 1\\ -1 & 0\end{bmatrix}$", False, r"No. Trace $0$: a center, neutrally stable, not asymptotically stable.")]),
    q("q-eig-sum", r"$A = \begin{bmatrix}2 & 4\\ 4 & 2\end{bmatrix}$. What are its eigenvalues?", [
        (r"$6$ and $-2$", True, r"Right. Sum $= 4$ (trace), product $= -12$ (det)."),
        (r"$2$ and $2$", False, r"No. Those are the diagonal entries, not eigenvalues (the matrix is not triangular)."),
        (r"$4$ and $-4$", False, r"No. Their sum is $0$, but the trace is $4$."),
        (r"$6$ and $2$", False, r"No. Their product is $12$, but the determinant is $4 - 16 = -12$.")]),
    q("q-jacobian", r"For predator-prey $y' = y - yz$, $z' = yz - z$, what is the Jacobian at $(1, 1)$?", [
        (r"$\begin{bmatrix}0 & -1\\ 1 & 0\end{bmatrix}$", True, r"Right. $J = \begin{bmatrix}1 - z & -y\\ z & y - 1\end{bmatrix}$ at $y = z = 1$."),
        (r"$\begin{bmatrix}1 & 0\\ 0 & -1\end{bmatrix}$", False, r"No. That is the Jacobian at $(0, 0)$."),
        (r"$\begin{bmatrix}1 & -1\\ 1 & -1\end{bmatrix}$", False, r"No. The diagonal entries $1 - z$ and $y - 1$ vanish at $(1, 1)$."),
        (r"$\begin{bmatrix}0 & 1\\ -1 & 0\end{bmatrix}$", False, r"No. Check the signs: $\partial f/\partial z = -y = -1$.")]),
    q("q-tumble", r"Why does the box tumble when spun about its middle axis, $(0, 1, 0)$?", [
        (r"The Jacobian there has eigenvalues $0, 1, -1$: a saddle, so small errors grow like $e^t$.", True, r"Right. About the other two axes the eigenvalues are $0, \pm i\sqrt2$ and the spin stays steady."),
        (r"Because $x^2 + y^2 + z^2$ is not conserved there.", False, r"No. It is conserved everywhere."),
        (r"Because $(0, 1, 0)$ is not a critical point.", False, r"No. All right sides vanish there."),
        (r"Because the eigenvalues there are $\pm i\sqrt2$.", False, r"No. Imaginary eigenvalues give a neutral center, not tumbling.")]),
]

EXPLORER = {
    "modes": [
        {"id": "linear", "label": "Linear system z' = A z"},
        {"id": "predprey", "label": "Predator-prey y' = y − yz, z' = yz − z"},
        {"id": "pendulum", "label": "Pendulum θ' = ω, ω' = −sin θ − k ω"}
    ],
    "defaultMode": "linear",
    "a": {"min": -3, "max": 3, "step": 0.25, "default": 1},
    "b": {"min": -3, "max": 3, "step": 0.25, "default": 2},
    "c": {"min": -3, "max": 3, "step": 0.25, "default": -3},
    "d": {"min": -3, "max": 3, "step": 0.25, "default": -4},
    "k": {"min": 0, "max": 1.5, "step": 0.05, "default": 0.5},
    "tMax": 12,
    "presets": [
        {"id": "sink", "label": "Node sink", "mode": "linear", "a": 1, "b": 2, "c": -3, "d": -4,
         "note": "Section 4 example: $\\lambda = -1, -2$."},
        {"id": "source", "label": "Source (y'' − 3y' + 2y)", "mode": "linear", "a": 0, "b": 1, "c": -2, "d": 3,
         "note": "Section 2: companion matrix, $\\lambda = 1, 2$."},
        {"id": "saddle", "label": "Saddle (y'' = 4y)", "mode": "linear", "a": 0, "b": 1, "c": 3, "d": 0,
         "note": "Use $c = 3$ here (slider range); the lecture's $y'' = 4y$ has $\\lambda = \\pm 2$."},
        {"id": "spiral", "label": "Spiral sink", "mode": "linear", "a": 0, "b": 1, "c": -2, "d": -2,
         "note": "Section 3: $y'' + 2y' + 2y = 0$, $\\lambda = -1 \\pm i$."},
        {"id": "center", "label": "Center", "mode": "linear", "a": 0, "b": 1, "c": -2, "d": 0,
         "note": "$y'' + 2y = 0$: ellipses, $\\lambda = \\pm i\\sqrt2$."},
        {"id": "pp", "label": "Predator-prey", "mode": "predprey",
         "note": "Section 5: saddle at $(0,0)$, center at $(1,1)$; orbits close."},
        {"id": "pend", "label": "Damped pendulum", "mode": "pendulum", "k": 0.5,
         "note": "Section 5 example: spiral sink at $(0,0)$, saddle at $(\\pi, 0)$."}
    ],
    "tutorContext": "Phase plane explorer. Linear mode: z' = A z with A = [a b; c d]; it shows trace T, determinant D, discriminant T^2 - 4D, eigenvalues and real eigenvectors, the classification (saddle if D < 0; node source/sink if T^2 > 4D; spiral source/sink if T^2 < 4D; center if T = 0 and D > 0; degenerate cases on the boundaries), a direction field, eigenvector lines, and trajectories computed by RK4 from points the user clicks (or presets), plus a trace-determinant plane with the parabola T^2 = 4D and the current matrix marked. Nonlinear modes: predator-prey y' = y - yz, z' = yz - z (critical points (0,0) saddle and (1,1) center) and damped pendulum theta' = omega, omega' = -sin(theta) - k omega (critical points (0,0) and (pi,0)); critical points are marked with their Jacobian eigenvalues."
}

COURSE = {
    "version": 1,
    "title": "Phase Plane, Linearization and Stability",
    "subtitle": "Unit 6 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 27-34, with Strang's Differential Equations and Linear Algebra, Chapter 3",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 27-34", "duration": "2:22:58", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 3",
             "edition": "Wellesley-Cambridge Press, 2014 (Chapter 3, Sections 3.1-3.3)", "onlineUrl": "",
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
