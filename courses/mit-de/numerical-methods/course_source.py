"""Source of courses/mit-de/numerical-methods/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\numerical-methods\\course_source.py

Unit 11 of the MIT Learn Differential Equations companion: playlist videos 57-65 (Cleve Moler,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Sections 3.4-3.5.
All text is original, written for this guide; it paraphrases the lectures and the book without
quoting. Examples marked "authored" are not from the lectures. Book references give printed
pages; the local PDF page is printed + 12. The explorer replaces MATLAB: every method is
implemented in JavaScript (dist/study_math.js) and drawn stage by stage.
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
    (57, "aW-e04zwTnc", "Euler, ODE1", "15:22"),
    (58, "x0Ap2kDsGRQ", "Midpoint Method, ODE2", "6:46"),
    (59, "Mva9UIz_wwA", "Classical Runge-Kutta, ODE4", "9:38"),
    (60, "6O9D6am_RK4", "Order, Naming Conventions", "5:26"),
    (61, "ScZMBOB_qYQ", "Estimating Error, ODE23", "10:37"),
    (62, "DkOgvZywshI", "ODE45", "6:47"),
    (63, "gwmIksA7aXM", "Stiffness, ODE23s, ODE15s", "7:15"),
    (64, "NNhVVk244ZA", "Systems of Equations", "14:17"),
    (65, "cQKR5m5pTTg", "The MATLAB ODE Suite", "5:35"),
]

SECTIONS = [
    {
        "nav": "Euler's method",
        "v": 57,
        "title": r"Euler's method: follow the tangent line",
        "summary": r"For $y' = f(t, y)$, Euler's method steps along the slope at the start of each interval: $y_{n+1} = y_n + hf(t_n, y_n)$. For $y' = 2y$, $y(0) = 10$, $h = 1$: slopes $20, 60, 180$ and values $30, 90, 270$, far below the exact $10e^{2t}$.",
        "time": [0, 922],
        "goals": [
            r"Derive Euler's step from the tangent line.",
            r"Carry out Euler steps by hand.",
            r"See why one evaluation of $f$ per step gives low accuracy."
        ],
        "notes": [
            {"heading": "The idea",
             "paragraphs": [
                 r"Most differential equations have no formula for their solution, so we compute approximations $y_n \approx y(t_n)$ at points $t_n = t_0 + nh$. The derivative $y'(t_0) = f(t_0, y_0)$ is the slope of the tangent line; moving a step $h$ along it gives $y(t_0 + h) \approx y_0 + hf(t_0, y_0)$. Repeating this is Euler's method (Moler's ODE1):",
                 r"$s_1 = f(t_n, y_n), \qquad y_{n+1} = y_n + h\,s_1.$"
             ]},
            {"heading": "Examples from the lecture",
             "paragraphs": [
                 r"Compound interest $y' = 0.06y$ with monthly steps: $100$ dollars become about $182$ after ten years (the exact continuous value is $100e^{0.6} \approx 182.21$), against $160$ with simple interest.",
                 r"$y' = 2y$, $y(0) = 10$, $h = 1$ on $[0, 3]$: the slope is $20$, so $y_1 = 30$; then slope $60$, $y_2 = 90$; then slope $180$, $y_3 = 270$. The exact value $10e^6 \approx 4034$ is far away: each step uses only the slope at its left end, which for a growing solution is the smallest slope on the interval.",
                 r"Equations with no closed form, such as $y' = t^2 + y^2$, are exactly where numerical methods are needed."
             ]}
        ],
        "keyIdeas": [
            r"$y_{n+1} = y_n + hf(t_n, y_n)$.",
            r"One slope per step, taken at the left end.",
            r"$y' = 2y$, $h = 1$: $10, 30, 90, 270$.",
            r"Accuracy improves only in proportion to $h$."
        ],
        "example": {
            "title": "Euler for a decaying solution (authored)",
            "problem": r"Take two Euler steps of size $h = 0.5$ for $y' = -y$, $y(0) = 1$, and compare with $e^{-1}$.",
            "steps": [
                {"text": "Each step multiplies y by 1 + h(-1).", "tex": r"y_1 = 1 + 0.5(-1) = 0.5"},
                {"text": "Second step.", "tex": r"y_2 = 0.5 + 0.5(-0.5) = 0.25"},
                {"text": "Exact value.", "tex": r"y(1) = e^{-1} \approx 0.368"}
            ],
            "answer": r"Euler gives $0.25$; the error $0.118$ halves roughly each time $h$ is halved (first order)."
        },
        "sources": {
            "video": [vs(57, 0, "Secant and tangent"),
                      vs(57, 120, "Tangent line step"),
                      vs(57, 180, "Examples: interest, logistic, t^2 + y^2"),
                      vs(57, 300, "Euler's method"),
                      vs(57, 360, "ODE1 code"),
                      vs(57, 630, "y' = 2y, h = 1: 30, 90, 270"),
                      vs(57, 870, "Exercise")],
            "book": [bk(184, "Section 3.4: the basic Euler methods")]
        },
        "tutorNotes": "Video 57 (Moler). y' = f(t, y). Euler (ODE1): s1 = f(t_n, y_n), y_(n+1) = y_n + h s1. Interest y' = .06y: $100 -> about $182 in 10 years (simple interest $160). y' = 2y, y(0) = 10, h = 1: slopes 20, 60, 180; y = 30, 90, 270 (exact 10 e^6). y' = t^2 + y^2 has no formula."
    },
    {
        "nav": "Midpoint and RK4",
        "v": 58,
        "title": r"Better slopes: the midpoint method and classical Runge-Kutta",
        "summary": r"The midpoint method (ODE2) uses Euler to reach the middle of the interval and steps with the slope found there. Classical Runge-Kutta (ODE4) samples four slopes (start, two at the midpoint, end) and steps with $\tfrac{h}{6}(s_1 + 2s_2 + 2s_3 + s_4)$.",
        "time": [0, 406],
        "goals": [
            r"Write the midpoint and RK4 stages.",
            r"Run them by hand on $y' = 2y$, $h = 1$.",
            r"Count function evaluations per step as the cost."
        ],
        "notes": [
            {"heading": "Midpoint (ODE2)",
             "paragraphs": [
                 r"$s_1 = f(t_n, y_n)$, $\;s_2 = f\!\left(t_n + \tfrac h2,\ y_n + \tfrac h2s_1\right)$, $\;y_{n+1} = y_n + h\,s_2$. Two evaluations of $f$ per step. For $y' = 2y$, $y(0) = 10$, $h = 1$: $s_1 = 20$, half step to $20$, $s_2 = 40$, so $y_1 = 50$; then $250$ and $1250$, much closer to the exact values than Euler's $270$ at $t = 3$ (exact $\approx 4034$)."
             ]},
            {"heading": "Classical Runge-Kutta (ODE4)",
             "paragraphs": [
                 r"$s_1 = f(t_n, y_n)$, $s_2 = f(t_n + \tfrac h2, y_n + \tfrac h2s_1)$, $s_3 = f(t_n + \tfrac h2, y_n + \tfrac h2s_2)$, $s_4 = f(t_n + h, y_n + hs_3)$, and",
                 r"$y_{n+1} = y_n + \dfrac h6\left(s_1 + 2s_2 + 2s_3 + s_4\right).$ Four evaluations per step. When $f$ depends only on $t$ this is Simpson's rule. (Runge 1895, Kutta 1901.)",
                 r"Moler's showcase is the flame equation $y' = y^2 - y^3$, $y(0) = \delta$: a small ball of flame grows slowly, then explodes near $t = 1/\delta$ and levels off at radius $1$."
             ]}
        ],
        "keyIdeas": [
            r"Midpoint: slope at $t + \tfrac h2$ from an Euler half step.",
            r"RK4: $\tfrac h6(s_1 + 2s_2 + 2s_3 + s_4)$.",
            r"Cost = evaluations of $f$ per step.",
            r"Flame: $y' = y^2 - y^3$."
        ],
        "example": {
            "title": "One RK4 step for y' = 2y (authored)",
            "problem": r"Take one RK4 step of size $h = 1$ from $y_0 = 10$ for $y' = 2y$.",
            "steps": [
                {"text": "Four slopes.", "tex": r"s_1 = 20,\ s_2 = 2(10 + 10) = 40,\ s_3 = 2(10 + 20) = 60,\ s_4 = 2(10 + 60) = 140"},
                {"text": "Weighted average.", "tex": r"\tfrac16(20 + 80 + 120 + 140) = 60"},
                {"text": "Step.", "tex": r"y_1 = 10 + 60 = 70\quad(\text{exact } 10e^2 \approx 73.9)"}
            ],
            "answer": r"RK4 gives $70$; Euler $30$, midpoint $50$, exact $73.9$. The growth factor $1 + 2 + 2 + \tfrac43 + \tfrac23 = 7$ is the Taylor series of $e^2$ through the $h^4$ term."
        },
        "sources": {
            "video": [vs(58, 0, "Midpoint method: two slopes"),
                      vs(58, 60, "Example y' = sqrt(1 - y^2): 0.997"),
                      vs(58, 210, "Animation on y' = 2y: 50, 250, 1250"),
                      vs(58, 330, "Exercise: trapezoid ODE2t"),
                      vs(59, 0, "Classical Runge-Kutta: four slopes"),
                      vs(59, 150, "Runge and Kutta"),
                      vs(59, 165, "Flame equation y' = y^2 - y^3"),
                      vs(59, 450, "Exercises")],
            "book": [bk(191, "Section 3.5: higher accuracy with Runge-Kutta"),
                     bk(192, "The four stages of RK4")]
        },
        "tutorNotes": "Videos 58-59. Midpoint ODE2: s1 = f(t, y), s2 = f(t + h/2, y + h/2 s1), y += h s2 (2 evaluations); y' = 2y, h = 1: 50, 250, 1250. y' = sqrt(1 - y^2), h = pi/32: 0.997 at pi/2. RK4 ODE4: s1..s4 (start, mid, mid, end), y += h (s1 + 2s2 + 2s3 + s4)/6 (4 evaluations); Simpson when f = f(t). Flame y' = y^2 - y^3, y(0) = delta, tfinal = 2/delta."
    },
    {
        "nav": "Order of accuracy",
        "v": 60,
        "title": r"Order: halve $h$, divide the error by $2^p$",
        "summary": r"A method of order $p$ makes an error of size $h^{p+1}$ in one step and $h^p$ over a whole interval. Moler's experiment integrates $y' = 1/(1+t)^2$ from $0$ to $1$ (exact $\tfrac12$) with $h = 0.1$ and $0.05$: the error ratios $2, 4, 16$ reveal orders $1, 2, 4$ for ODE1, ODE2, ODE4. The name odePQ means orders $P$ and $Q$.",
        "time": [0, 326],
        "goals": [
            r"Relate local error $h^{p+1}$ and global error $h^p$.",
            r"Determine the order experimentally from two step sizes.",
            r"Decode the names ode23 and ode45."
        ],
        "notes": [
            {"heading": "Order",
             "paragraphs": [
                 r"Taylor series show that one step of a method of order $p$ is wrong by about $Ch^{p+1}$. Crossing a fixed interval takes $1/h$ steps, so the total error is about $Ch^p$. Halving $h$ should divide the error by $2^p$."
             ]},
            {"heading": "The experiment",
             "paragraphs": [
                 r"Integrate $y' = 1/(1 + t)^2$, $y(0) = 0$, to $t = 1$, where the exact value is $\tfrac12$. (The program comment on screen shows $1/(1+t)^2$; the narration says $1/(1 + t^2)$, whose integral would be $\pi/4$.) With $h = 0.1$ and $h = 0.05$: ODE1 gives $0.5390$ and $0.5191$, error ratio about $2$, order $1$. ODE2 gives $0.49927$ and $0.49982$, ratio about $4$, order $2$. ODE4 gives a ratio near $16$, order $4$.",
                 r"Since the right side depends only on $t$, these are the left-endpoint, midpoint and Simpson rules for an integral."
             ]},
            {"heading": "Names",
             "paragraphs": [
                 r"Moler named ODE1, ODE2, ODE4 after their orders. In the MATLAB suite, odePQ uses a pair of methods of orders $P$ and $Q$: ode23 pairs orders $2$ and $3$, ode45 orders $4$ and $5$. The pair is used to estimate the error."
             ]}
        ],
        "keyIdeas": [
            r"Local error $\sim h^{p+1}$, global $\sim h^p$.",
            r"Error ratio for $h \to h/2$: $2^p$.",
            r"ODE1, ODE2, ODE4: orders $1, 2, 4$.",
            r"odePQ: orders $P$ and $Q$."
        ],
        "example": {
            "title": "Reading the order from data (authored)",
            "problem": r"A solver's errors are $3.2\times10^{-5}$ with $h = 0.1$ and $2.0\times10^{-6}$ with $h = 0.05$. What is its order?",
            "steps": [
                {"text": "Error ratio.", "tex": r"\frac{3.2\times10^{-5}}{2.0\times10^{-6}} = 16"},
                {"text": "Order from the ratio.", "tex": r"p = \log_2 16 = 4"},
                {"text": "Prediction for h = 0.025.", "tex": r"2.0\times10^{-6}/16 \approx 1.25\times10^{-7}"}
            ],
            "answer": r"Order $4$; each halving of $h$ should divide the error by $16$."
        },
        "sources": {
            "video": [vs(60, 0, "Order: error proportional to h^p"),
                      vs(60, 60, "Experiment to determine the order"),
                      vs(60, 90, "Integral from 0 to 1, exact value 1/2"),
                      vs(60, 150, "ODE1: .5389 and .5191, order 1"),
                      vs(60, 180, "ODE2: ratio 4"),
                      vs(60, 210, "ODE4: ratio 16"),
                      vs(60, 240, "Naming: ode PQ")],
            "book": [bk(185, "Accuracy and order of Euler's method"),
                     bk(192, "Runge-Kutta accuracy")]
        },
        "tutorNotes": "Video 60. Order p: one-step error ~ h^(p+1), global ~ h^p; halving h divides error by 2^p. Experiment: integrate y' = 1/(1+t)^2 from 0 to 1 (exact 1/2; the narration says 1/(1+t^2), the screen shows 1/(1+t)^2), h = 0.1 and 0.05. ODE1: .5389, .5191 (ratio 2, order 1); ODE2: ratio 4; ODE4: ratio 16. odePQ: orders P and Q."
    },
    {
        "nav": "ode23 and ode45",
        "v": 61,
        "title": r"Error estimates and automatic step size: BS23 and Dormand-Prince",
        "summary": r"ode23 (Bogacki-Shampine) takes a third-order step with three slopes, evaluates a fourth slope at the new point, and estimates the error as $e = \tfrac{h}{72}(-5s_1 + 6s_2 + 8s_3 - 9s_4)$. If $e$ is within the tolerance the step is accepted and $s_4$ becomes the next $s_1$ (FSAL); either way $h$ is adjusted. ode45 (Dormand-Prince) does the same with orders $4$ and $5$ and six new slopes per step.",
        "time": [0, 637],
        "goals": [
            r"Write the BS23 stages and error estimate.",
            r"Explain accept/reject and the step-size update.",
            r"Describe FSAL and continuous (interpolated) output.",
            r"Compare ode23 and ode45 in cost and accuracy."
        ],
        "notes": [
            {"heading": "BS23",
             "paragraphs": [
                 r"$s_1 = f(t_n, y_n)$, $s_2 = f(t_n + \tfrac h2, y_n + \tfrac h2s_1)$, $s_3 = f(t_n + \tfrac34h, y_n + \tfrac34hs_2)$, $y_{n+1} = y_n + \tfrac h9(2s_1 + 3s_2 + 4s_3)$ (third order). Then $s_4 = f(t_{n+1}, y_{n+1})$ and $e_{n+1} = \tfrac{h}{72}(-5s_1 + 6s_2 + 8s_3 - 9s_4)$: the difference between the third-order step and an embedded second-order one."
             ]},
            {"heading": "Step-size control",
             "paragraphs": [
                 r"Compare $|e|$ (relative to $|y|$) with the tolerance, by default $10^{-3}$. If it is small enough, accept $y_{n+1}$; otherwise reject it and try again. Either way choose the next $h$ from $h\cdot0.8\,(\text{tol}/\text{err})^{1/3}$, limited to at most five times larger. Because $s_4$ is evaluated at the accepted point, it is the next step's $s_1$ (first same as last), so a step costs only three new evaluations.",
                 r"On $y' = y$, $[0, 1]$, the first step is about $0.08$, then about $0.1$, and $y(1) \approx 2.718$. On the near-singular problem $y' = 2(a - t)y^2$ with $a = \tfrac14$ and $y(0) = 15.9$, the solution climbs to $1/(1/15.9 - 1/16) \approx 2544$ at $t = a$ (a start of $16 = 1/a^2$ would blow up there); the steps shrink near $t = a$ and grow again afterwards. A cubic Hermite interpolant through the step ends gives smooth output between steps."
             ]},
            {"heading": "ode45",
             "paragraphs": [
                 r"Dormand-Prince evaluates slopes at $t_n + \tfrac h5, \tfrac{3h}{10}, \tfrac{4h}{5}, \tfrac{8h}{9}, h$ and combines them into fifth- and fourth-order results; their difference estimates the error. Seven slopes per step, one reused (FSAL), so six new evaluations, versus four for RK4, buying an error estimate and order $5$. ode45 is the first solver to try."
             ]}
        ],
        "keyIdeas": [
            r"BS23: $y_{n+1} = y_n + \tfrac h9(2s_1 + 3s_2 + 4s_3)$.",
            r"$e = \tfrac{h}{72}(-5s_1 + 6s_2 + 8s_3 - 9s_4)$.",
            r"Accept if error $\le$ tol; $h \leftarrow 0.8h(\text{tol}/\text{err})^{1/3}$.",
            r"FSAL; ode45: orders 4 and 5, six new slopes."
        ],
        "example": {
            "title": "One BS23 step for y' = y (authored)",
            "problem": r"Take one BS23 step with $h = 0.1$ from $y_0 = 1$ for $y' = y$ and estimate its error.",
            "steps": [
                {"text": "Slopes.", "tex": r"s_1 = 1,\ s_2 = 1.05,\ s_3 = 1 + 0.075(1.05) = 1.07875"},
                {"text": "Third-order step and the new slope.", "tex": r"y_1 = 1 + \tfrac{0.1}{9}(2 + 3.15 + 4.315) = 1.105167,\quad s_4 = y_1"},
                {"text": "Error estimate.", "tex": r"e = \tfrac{0.1}{72}(-5 + 6.3 + 8.63 - 9.946503) \approx -2.3\times10^{-5}"}
            ],
            "answer": r"$y_1 \approx 1.1051667$ (exact $e^{0.1} = 1.1051709$, error $4.2\times10^{-6}$); the estimate $2.3\times10^{-5}$ is the error of the embedded second-order formula, a cautious bound, well below the default tolerance $10^{-3}$, so the step is accepted."
        },
        "sources": {
            "video": [vs(61, 60, "Error estimate, step size, interpolant"),
                      vs(61, 90, "Bogacki-Shampine, order 3 and 2"),
                      vs(61, 150, "The BS23 formulas"),
                      vs(61, 240, "Accept or reject; adjust h"),
                      vs(61, 270, "y' = y: steps 0.08 and 0.1"),
                      vs(61, 390, "Near-singular problem, a = 1/4"),
                      vs(61, 540, "Hermite interpolation"),
                      vs(62, 0, "Dormand-Prince ode45"),
                      vs(62, 120, "Order 5 needs six evaluations"),
                      vs(62, 270, "Refine: interpolated output")],
            "book": [bk(193, "ode45 and adaptive methods")]
        },
        "tutorNotes": "Videos 61-62. BS23 (ode23): s1 = f(t, y), s2 = f(t + h/2, y + h/2 s1), s3 = f(t + 3h/4, y + 3h/4 s2), y_new = y + h/9 (2s1 + 3s2 + 4s3), s4 = f(t + h, y_new), e = h/72 (-5s1 + 6s2 + 8s3 - 9s4). Accept if err <= tol (default rtol 1e-3, relative to max(|y|, threshold)); h_new = h min(5, 0.8 (tol/err)^(1/3)); FSAL (s4 -> next s1). y' = y on [0, 1]: h0 ~ 0.08 then 0.1; near-singular y' = 2(a - t) y^2, a = 1/4, y0 = 15.9: exact y = 1/(1/y0 - 2at + t^2), peak 1/(1/15.9 - 1/16) ~ 2544 at t = 1/4 (y0 = 16 would blow up), small steps there. Hermite cubic interpolant. ode45 Dormand-Prince: nodes h/5, 3h/10, 4h/5, 8h/9, h; orders 4/5; 6 new evaluations per step (FSAL)."
    },
    {
        "nav": "Stiffness",
        "v": 63,
        "title": r"Stiff problems need implicit methods",
        "summary": r"A problem is stiff when the solution varies slowly but nearby solutions vary rapidly. Explicit methods must then take tiny steps for stability, not accuracy. The flame equation with $\delta = 10^{-6}$ makes ode45 crawl near $y = 1$, while the implicit ode23s turns the corner in a few steps. Backward Euler, $y_{n+1} - hf(t_{n+1}, y_{n+1}) = y_n$, is the simplest implicit method.",
        "time": [0, 435],
        "goals": [
            r"Define stiffness.",
            r"See why explicit steps are limited: $|1 + h\lambda| \le 1$.",
            r"Write backward Euler and solve its equation by Newton's method.",
            r"Name the stiff solvers ode23s and ode15s."
        ],
        "notes": [
            {"heading": "What stiffness is",
             "paragraphs": [
                 r"For the flame with a tiny $\delta$, the solution sits at $y \approx 1$ for a long time. Solutions that start slightly off $1$ return to it very fast (the slope $f'(1) = 2 - 3 = -1$, but on a time scale of $2/\delta$ that is extremely fast). Moler's image: a slot canyon whose walls are steep while the floor is nearly flat. An explicit method bounces from wall to wall unless its steps are tiny.",
                 r"Stability makes this precise. For $y' = \lambda y$ with $\lambda < 0$, Euler multiplies by $1 + h\lambda$ each step and blows up unless $h < 2/|\lambda|$. The book's example $y' = -100y$ needs $h < 0.02$, however smooth the solution is. RK4's limit is about $h|\lambda| < 2.78$."
             ]},
            {"heading": "Implicit methods",
             "paragraphs": [
                 r"Backward Euler uses the slope at the end of the step: $y_{n+1} = y_n + hf(t_{n+1}, y_{n+1})$. For $y' = \lambda y$ this gives $y_{n+1} = y_n/(1 - h\lambda)$, which decays for every $h > 0$ when $\lambda < 0$. The price is an equation to solve at each step, usually by Newton's method with the Jacobian $\partial f/\partial y$.",
                 r"ode23s is an implicit (Rosenbrock) method of orders $2$ and $3$ that evaluates the Jacobian each step; ode15s uses numerical differentiation formulas of orders $1$ to $5$. On the flame with $\delta = 10^{-6}$ and tolerance $10^{-5}$, they take a handful of steps where ode45 takes thousands."
             ]}
        ],
        "keyIdeas": [
            r"Stiff: slow solution, fast nearby solutions.",
            r"Euler on $y' = \lambda y$: stable only if $|1 + h\lambda| \le 1$.",
            r"Backward Euler: $y_{n+1} = y_n/(1 - h\lambda)$, stable for all $h$.",
            r"ode23s, ode15s: implicit, use the Jacobian."
        ],
        "example": {
            "title": "Explicit against implicit (authored)",
            "problem": r"For $y' = -100y$, $y(0) = 1$, take steps $h = 0.05$ with Euler and with backward Euler.",
            "steps": [
                {"text": "Euler multiplies by 1 + h lambda.", "tex": r"1 - 0.05\cdot100 = -4:\quad 1,\ -4,\ 16,\ -64,\ \ldots"},
                {"text": "Backward Euler divides by 1 - h lambda.", "tex": r"\frac{1}{1 + 5} = \frac16:\quad 1,\ 0.167,\ 0.028,\ \ldots"},
                {"text": "Euler's stability limit.", "tex": r"h < \frac{2}{100} = 0.02"}
            ],
            "answer": r"Euler explodes with alternating signs; backward Euler decays like the true solution $e^{-100t}$."
        },
        "sources": {
            "video": [vs(63, 0, "Flame with delta = 1e-6"),
                      vs(63, 90, "ode45 crawls near y = 1"),
                      vs(63, 150, "ode23s turns the corner"),
                      vs(63, 210, "Definition of stiffness"),
                      vs(63, 240, "Implicit Euler"),
                      vs(63, 300, "Slot canyon"),
                      vs(63, 330, "ode23s and ode15s")],
            "book": [bk(187, "Stiff equations and backward Euler")]
        },
        "tutorNotes": "Video 63. Stiff: slowly varying solution with rapidly varying nearby solutions. Flame y' = y^2 - y^3, y0 = 1e-6, RelTol 1e-5: ode45 takes very many steps near y = 1; ode23s few. Euler on y' = lambda y stable iff |1 + h lambda| <= 1 (y' = -100y needs h < 0.02); RK4 limit h|lambda| < 2.78. Backward (implicit) Euler y_(n+1) - h f(t_(n+1), y_(n+1)) = y_n, Newton iteration; y_(n+1) = y_n/(1 - h lambda). ode23s Rosenbrock orders 2/3 with Jacobian; ode15s NDF orders 1-5."
    },
    {
        "nav": "Systems and the suite",
        "v": 64,
        "title": r"Systems: the harmonic oscillator and Van der Pol; choosing a solver",
        "summary": r"A second order equation becomes a first order system with $y = (x, x')$. The harmonic oscillator $x'' + x = 0$ traces a circle in the phase plane. Van der Pol's $x'' - \mu(1 - x^2)x' + x = 0$ with large $\mu$ is stiff: ode45 needs thousands of steps, ode15s a few hundred. Start with ode45; switch to ode15s when it is slow.",
        "time": [0, 857],
        "goals": [
            r"Write a second order equation as a system.",
            r"Interpret the phase-plane picture of the oscillator.",
            r"Recognise stiffness in Van der Pol.",
            r"Choose among the MATLAB solvers."
        ],
        "notes": [
            {"heading": "Systems",
             "paragraphs": [
                 r"For $x'' + x = 0$ let $y_1 = x$, $y_2 = x'$. Then $y_1' = y_2$ and $y_2' = -y_1$: $y' = f(t, y)$ with a vector $y$. Every method above works unchanged with vectors. From $y(0) = (0, 1)$ the solution is $(\sin t, \cos t)$, a circle in the $(y_1, y_2)$ plane, completed at $t = 2\pi$."
             ]},
            {"heading": "Van der Pol",
             "paragraphs": [
                 r"$y_1' = y_2$, $y_2' = \mu(1 - y_1^2)y_2 - y_1$: negative damping for small $|y_1|$, positive for large. The solution settles onto a limit cycle. For $\mu = 100$ the cycle has slow drifts and sudden jumps: a stiff problem. Moler reports ode45 needing about $15000$ steps on an interval where the stiff solver used about $500$."
             ]},
            {"heading": "The suite",
             "paragraphs": [
                 r"Nonstiff: ode45 (first choice), ode23 (crude tolerances), ode113 (Adams, orders $1$-$13$, expensive $f$). Stiff: ode15s (first choice), ode23s, ode23t, ode23tb. Options (odeset) set RelTol, AbsTol, events, Jacobian, mass matrix and maximum step."
             ]}
        ],
        "keyIdeas": [
            r"$x'' + x = 0$: $y = (x, x')$, $y' = (y_2, -y_1)$.",
            r"Oscillator: a circle in the phase plane.",
            r"Van der Pol, large $\mu$: stiff limit cycle.",
            r"Try ode45; if slow, ode15s."
        ],
        "example": {
            "title": "Energy drift of Euler on the oscillator (authored)",
            "problem": r"Apply one Euler step of size $h$ to $y' = (y_2, -y_1)$ and compare $y_1^2 + y_2^2$ before and after.",
            "steps": [
                {"text": "Euler step.", "tex": r"(y_1, y_2) \to (y_1 + hy_2,\ y_2 - hy_1)"},
                {"text": "New squared radius.", "tex": r"(y_1 + hy_2)^2 + (y_2 - hy_1)^2 = (1 + h^2)(y_1^2 + y_2^2)"},
                {"text": "After n steps.", "tex": r"r_n^2 = (1 + h^2)^n\,r_0^2"}
            ],
            "answer": r"Euler spirals outwards: the radius grows by $\sqrt{1 + h^2}$ per step, while the exact solution stays on the circle."
        },
        "sources": {
            "video": [vs(64, 0, "Harmonic oscillator x'' + x = 0"),
                      vs(64, 90, "y = (x, x'), f = (y2, -y1)"),
                      vs(64, 210, "Phase plane: a circle"),
                      vs(64, 330, "Van der Pol, mu = 100"),
                      vs(64, 510, "ode45 is very slow"),
                      vs(64, 660, "A stiff solver: about 500 steps"),
                      vs(65, 0, "The MATLAB ODE suite"),
                      vs(65, 120, "Stiff solvers"),
                      vs(65, 240, "odeset options")],
            "book": [bk(185, "Systems and the Euler methods")]
        },
        "tutorNotes": "Videos 64-65. x'' + x = 0 as y1 = x, y2 = x': y' = (y2, -y1), y(0) = (0, 1) gives (sin t, cos t), a circle. Van der Pol y1' = y2, y2' = mu(1 - y1^2) y2 - y1; mu = 100 stiff (ode45 ~15000 steps vs ~500 for the stiff solver). Suite: ode45, ode23, ode113 (nonstiff); ode15s, ode23s, ode23t, ode23tb (stiff); odeset RelTol, AbsTol, Events, Jacobian, Mass, MaxStep."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-euler", r"Euler with $h = 1$ on $y' = 2y$, $y(0) = 10$: what is $y_2$?", [
        (r"$90$", True, r"Right. $10 \to 30 \to 90$: each step multiplies by $1 + 2h = 3$."),
        (r"$73.9$", False, r"No. That is the exact $y(1) = 10e^2$."),
        (r"$40$", False, r"No. Euler multiplies by $3$, not adds $20$ twice."),
        (r"$250$", False, r"No. That is the midpoint method's value at $t = 2$.")]),
    q("q-midpoint", r"In the midpoint method, where is the second slope evaluated?", [
        (r"At $t_n + \tfrac h2$, after an Euler half step $y_n + \tfrac h2s_1$", True, r"Right. Then $y_{n+1} = y_n + hs_2$."),
        (r"At $t_n + h$, after a full Euler step", False, r"No. That is the trapezoid (Heun) variant's second slope."),
        (r"At $t_n$ again", False, r"No. That would repeat $s_1$."),
        (r"At the exact midpoint value $y(t_n + h/2)$", False, r"No. That value is unknown; Euler predicts it.")]),
    q("q-rk4", r"What is the RK4 update?", [
        (r"$y_n + \tfrac h6(s_1 + 2s_2 + 2s_3 + s_4)$", True, r"Right. Simpson-like weights $1, 2, 2, 1$."),
        (r"$y_n + \tfrac h4(s_1 + s_2 + s_3 + s_4)$", False, r"No. Equal weights lose accuracy."),
        (r"$y_n + h\,s_4$", False, r"No. That uses only the last slope."),
        (r"$y_n + \tfrac h2(s_1 + s_4)$", False, r"No. That is the trapezoid idea, second order.")]),
    q("q-order", r"Halving $h$ divides the error by about $4$. What is the order?", [
        (r"$2$", True, r"Right. $2^p = 4$."),
        (r"$4$", False, r"No. Order $4$ would divide by $16$."),
        (r"$1$", False, r"No. Order $1$ divides by $2$."),
        (r"$3$", False, r"No. That would divide by $8$.")]),
    q("q-local", r"A method of order $p$ has what error in one step?", [
        (r"About $Ch^{p+1}$", True, r"Right. Summed over $1/h$ steps it becomes $Ch^p$."),
        (r"About $Ch^p$", False, r"No. That is the global error over an interval."),
        (r"About $Ch^{p-1}$", False, r"No. The one-step error is smaller than the global error."),
        (r"Zero", False, r"No. Only exact solutions have zero error.")]),
    q("q-names", r"What does the name ode45 mean?", [
        (r"A pair of methods of orders $4$ and $5$, used to estimate the error", True, r"Right. Dormand-Prince."),
        (r"It needs $45$ evaluations per step.", False, r"No. Six new evaluations per step."),
        (r"It works up to $45$ equations.", False, r"No. It handles systems of any size."),
        (r"It is order $45$.", False, r"No. Orders $4$ and $5$.")]),
    q("q-fsal", r"Why does BS23 cost only three new evaluations per step although it uses four slopes?", [
        (r"The fourth slope, at the accepted new point, is the next step's first slope (FSAL).", True, r"Right. First same as last."),
        (r"The fourth slope is not computed.", False, r"No. It is needed for the error estimate."),
        (r"Two slopes are always equal.", False, r"No. They are evaluated at different points."),
        (r"It reuses slopes from two steps back.", False, r"No. Only the last slope is reused.")]),
    q("q-reject", r"An adaptive step has an error estimate larger than the tolerance. What happens?", [
        (r"The step is rejected and retried with a smaller $h$.", True, r"Right. $h \leftarrow 0.8h(\text{tol}/\text{err})^{1/p}$."),
        (r"The step is accepted and $h$ doubles.", False, r"No. Steps that fail the test are not kept."),
        (r"The solver switches to Euler.", False, r"No. It keeps its formula and shrinks $h$."),
        (r"The tolerance is raised.", False, r"No. The user's tolerance is fixed.")]),
    q("q-stiff", r"Euler on $y' = -100y$ is stable for which step sizes?", [
        (r"$h < 0.02$", True, r"Right. $|1 - 100h| \le 1$."),
        (r"Any $h$", False, r"No. That is backward Euler."),
        (r"$h < 0.1$", False, r"No. $h = 0.05$ gives a factor $-4$: blow-up."),
        (r"$h < 2$", False, r"No. The limit is $2/|\lambda|$, not $2$.")]),
    q("q-system", r"How is $x'' + x = 0$ written for an ODE solver?", [
        (r"$y = (x, x')$, $y' = (y_2, -y_1)$", True, r"Right. A first order system of two equations."),
        (r"$y' = -y$", False, r"No. That loses the second derivative."),
        (r"$y = x''$", False, r"No. Solvers need first derivatives of the state."),
        (r"$y' = (y_1, y_2)$", False, r"No. Then $x' = x$, a different equation.")]),
]

EXPLORER = {
    "methods": [
        {"id": "euler", "label": "Euler (ODE1)", "order": 1, "stages": 1},
        {"id": "midpoint", "label": "Midpoint (ODE2)", "order": 2, "stages": 2},
        {"id": "heun", "label": "Trapezoid / Heun (ODE2t)", "order": 2, "stages": 2},
        {"id": "rk4", "label": "Classical RK4 (ODE4)", "order": 4, "stages": 4},
        {"id": "bs23", "label": "Bogacki-Shampine (ode23, adaptive)", "order": 3, "stages": 4, "adaptive": True},
        {"id": "dp45", "label": "Dormand-Prince (ode45, adaptive)", "order": 5, "stages": 7, "adaptive": True},
        {"id": "beuler", "label": "Backward Euler (implicit)", "order": 1, "stages": 1, "implicit": True}
    ],
    "problems": [
        {"id": "exp2", "label": "y' = 2y, y(0) = 10 (lecture)"},
        {"id": "circle", "label": "y' = √(1 − y²), y(0) = 0 (exact sin t)"},
        {"id": "order", "label": "y' = 1/(1+t)², y(0) = 0 (order experiment)"},
        {"id": "flame", "label": "Flame y' = y² − y³, y(0) = δ"},
        {"id": "nearsing", "label": "y' = 2(a − t)y², a = 1/4, y(0) = 15.9"},
        {"id": "stiffcos", "label": "y' = −100(y − cos t) − sin t (stiff, exact cos t)"},
        {"id": "oscillator", "label": "x'' + x = 0 as a system (exact circle)"},
        {"id": "vdp", "label": "Van der Pol, parameter μ"}
    ],
    "h": {"min": 0.01, "max": 1.0, "step": 0.01, "default": 0.25},
    "logTol": {"min": -8, "max": -1, "step": 0.5, "default": -3},
    "delta": {"min": 0.001, "max": 0.1, "step": 0.001, "default": 0.02},
    "mu": {"min": 0.5, "max": 30, "step": 0.5, "default": 5},
    "presets": [
        {"id": "euler2y", "label": "Euler on y' = 2y", "method": "euler", "problem": "exp2", "h": 1,
         "note": "Section 1: slopes $20, 60, 180$; values $30, 90, 270$."},
        {"id": "mid2y", "label": "Midpoint on y' = 2y", "method": "midpoint", "problem": "exp2", "h": 1,
         "note": "Section 2: $50, 250, 1250$."},
        {"id": "rk42y", "label": "RK4 on y' = 2y", "method": "rk4", "problem": "exp2", "h": 1,
         "note": "Section 2 example: $70$ after one step."},
        {"id": "order", "label": "Order experiment", "method": "rk4", "problem": "order", "h": 0.1,
         "note": "Section 3: compare errors for $h$ and $h/2$; the ratio shows the order."},
        {"id": "bs23", "label": "ode23 near a singularity", "method": "bs23", "problem": "nearsing", "logTol": -3,
         "note": "Section 4: steps shrink near $t = 1/4$, where $y$ peaks near $2544$."},
        {"id": "flame", "label": "Flame with ode45", "method": "dp45", "problem": "flame", "delta": 0.01, "logTol": -4,
         "note": "Sections 2 and 5: count the steps near $y = 1$; try smaller $\\delta$."},
        {"id": "stiff", "label": "Stiff: Euler vs implicit", "method": "euler", "problem": "stiffcos", "h": 0.03,
         "note": "Section 5: $h = 0.03 > 0.02$, so Euler oscillates and grows; switch to backward Euler."},
        {"id": "vdp", "label": "Van der Pol", "method": "dp45", "problem": "vdp", "mu": 10, "logTol": -4,
         "note": "Section 6: larger $\\mu$ makes the problem stiff; watch the step count."}
    ],
    "tutorContext": "The explorer implements the methods in JavaScript (no MATLAB): Euler, midpoint, trapezoid/Heun, classical RK4 with a fixed step h; adaptive Bogacki-Shampine (ode23: stages at h/2 and 3h/4, y_new = y + h/9(2s1 + 3s2 + 4s3), error h/72(-5s1 + 6s2 + 8s3 - 9s4), FSAL) and Dormand-Prince (ode45, orders 4/5, FSAL) with relative tolerance 10^logTol, error measured as max |e| / max(|y|, |y_new|, threshold = 1e-3), accept if <= tol, h_new = h min(5, max(0.1, 0.8 (tol/err)^(1/(q+1)))) with q the lower order; and backward Euler solved by Newton's method with a finite-difference Jacobian. Problems: y' = 2y (y0 = 10, t in [0, 3], exact 10e^(2t)); y' = sqrt(1 - y^2) (exact sin t on [0, pi/2]); y' = 1/(1+t)^2 (exact t/(1+t), value 1/2 at t = 1); flame y' = y^2 - y^3, y0 = delta, t in [0, 2/delta]; y' = 2(a - t) y^2, a = 1/4, y0 = 15.9 (exact 1/(1/y0 - 2at + t^2)); stiff y' = -100(y - cos t) - sin t, y0 = 1 (exact cos t); oscillator y = (x, x'), y0 = (0, 1) (exact (sin t, cos t)); Van der Pol with mu. The live view animates each step stage by stage: slope arrows at each stage point, the weighted slope, the step, the error estimate against the tolerance with accept/reject, a strip of step sizes, the error against the exact or reference solution, the number of function evaluations, and an order plot (error at h and h/2 on y' = 1/(1+t)^2)."
}

COURSE = {
    "version": 1,
    "title": "Numerical Methods for ODEs",
    "subtitle": "Unit 11 of a study companion to MIT Learn Differential Equations (Cleve Moler), videos 57-65, with Strang's Differential Equations and Linear Algebra, Sections 3.4-3.5",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 57-65", "duration": "1:21:43", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, 3.4-3.5",
             "edition": "Wellesley-Cambridge Press, 2014 (Sections 3.4-3.5)", "onlineUrl": "",
             "pageNote": "Page references give the printed page and the page of the local PDF (printed page + 12). The book is not freely available online, so only a local copy can be opened."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide; examples marked authored are not from the lectures. They summarize MIT OpenCourseWare's Learn Differential Equations videos (Cleve Moler, CC BY-NC-SA) and Strang's textbook; for the original wording, watch the videos and read the book. Captions, video and book text are not included in this guide. MATLAB is not needed: the explorer implements the methods itself.",
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
