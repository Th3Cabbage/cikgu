"""Source of courses/mit-de/first-order-linear/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\first-order-linear\\course_source.py

Unit 1 of the MIT Learn Differential Equations companion: playlist videos 1-10 (Gilbert Strang
and Cleve Moler, MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra,
Sections 1.1-1.6. All text is original, written for this guide; it paraphrases the lectures and
the book without quoting. Examples marked "authored" are not from the lectures. Book references
give printed pages; the local PDF page is printed + 12.
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
    (1, "ZvL88xqYSak", "Gilbert and Cleve Introduction", "2:53"),
    (2, "ghjOS7Q82s0", "Overview of Differential Equations", "14:04"),
    (3, "f0BxAtprWts", "The Calculus You Need", "14:48"),
    (4, "CB9I4mwpQ5E", "Response to Exponential Input", "13:20"),
    (5, "xw3ccgYhFis", "Response to Oscillating Input", "15:55"),
    (6, "0r2L3wTqkBc", "Solution for Any Input", "13:59"),
    (7, "ECslmuGlu-U", "Step Function and Delta Function", "15:41"),
    (8, "kIT2uMxYh6M", "Response to Complex Exponential", "12:51"),
    (9, "MJUjSKew4nQ", "Integrating Factor for Constant Rate", "13:47"),
    (10, "qJOQOkJ7rI8", "Integrating Factor for a Varying Rate", "11:23"),
]

SECTIONS = [
    {
        "nav": "The map of the course",
        "v": 2,
        "title": "What differential equations this series solves",
        "time": [0, 844],
        "summary": r"A differential equation links how a quantity changes to what it is now. The series moves from first order equations $y' = ay + q(t)$ and $y' = f(y)$, through second order equations $my'' + by' + ky = f(t)$, to systems $y' = Ay$ with matrices, numerical methods and finally partial differential equations.",
        "goals": [
            r"Tell a first order equation from a second order one, and a linear one from a nonlinear one.",
            r"Name the parts of $y' = ay + q(t)$: the growth rate $a$, the input (source) $q(t)$ and the initial value $y(0)$.",
            r"Explain why linear equations with constant coefficients are the ones solved by formulas, and why the rest are solved numerically."
        ],
        "notes": [
            {"heading": "Why two teachers",
             "paragraphs": [
                 r"The first video introduces the two halves of the series. Gilbert Strang works at the blackboard and finds solutions as formulas. Cleve Moler, who wrote the first MATLAB, explains how the numerical solvers work, so that a solver such as ode45 is less of a black box. Both are matrix people, and that is no accident: systems of equations, written with matrices, are where modern applications of differential equations live."
             ]},
            {"heading": "First order equations",
             "paragraphs": [
                 r"A first order equation contains $dy/dt$ and no higher derivatives. The model equation of the whole unit is $\dfrac{dy}{dt} = a\,y + q(t)$. Read it as a bank balance: $a\,y$ is interest added in proportion to the balance, and $q(t)$ is a stream of deposits (or withdrawals when negative). The equation is linear because $y$ appears only to the first power.",
                 r"Change the right side to $f(y)$, for example $y^2$ or $\sin y$, and the equation becomes nonlinear. The most general first order equation lets the right side depend on both $t$ and $y$: $y' = f(t, y)$."
             ]},
            {"heading": "Second order equations",
             "paragraphs": [
                 r"The second derivative measures acceleration, or how a graph bends away from its tangent line. Newton's law gives the central example $m y'' + b y' + k y = f(t)$: mass times acceleration, a damping force proportional to velocity, a spring force proportional to position, and an outside force $f(t)$.",
                 r"Each step up in difficulty (higher order, nonlinear terms, coefficients that change with time) makes exact formulas rarer. The equations we can solve completely and understand are linear with constant coefficients."
             ]},
            {"heading": "Good inputs and the rest",
             "paragraphs": [
                 r"Some inputs give answers we recognise at once. Exponentials $e^{st}$, $e^{i\omega t}$ and the sines and cosines they contain are the best: the output is an exponential of the same kind. For a general input the solution is still a formula, but it contains an integral of $f$ that we may have to look up or compute numerically. For nonlinear or variable-coefficient problems we usually go straight to numerical methods."
             ]},
            {"heading": "Systems, numerics and PDEs",
             "paragraphs": [
                 r"A real system has many parts, so $y$ becomes a vector of $n$ unknowns and the equation becomes $y' = Ay$ with an $n \times n$ matrix $A$ (or $y'' + Sy = 0$ with a symmetric $S$). Eigenvalues and eigenvectors uncouple such a system into $n$ separate equations we already know how to solve.",
                 r"Numerical methods start from Euler's simple step (ODE1) and lead to ode45, MATLAB's standard solver. The series ends with partial differential equations: the heat equation $u_t = u_{xx}$, the wave equation $u_{tt} = u_{xx}$ and Laplace's equation."
             ]}
        ],
        "keyIdeas": [
            r"Model equation: $y' = a y + q(t)$ with $y(0)$ given.",
            r"Linear with constant coefficients: solvable by formulas.",
            r"Systems use matrices; eigenvalues uncouple them.",
            r"Nonlinear and variable coefficients: usually numerical."
        ],
        "example": {
            "title": "Sorting equations (authored)",
            "problem": r"Classify $\;(1)\ y' = 3y + \cos t,\quad (2)\ y' = y^2,\quad (3)\ 2y'' + y' + 5y = 0,\quad (4)\ y' = t\,y.$",
            "steps": [
                {"text": "Order: count the highest derivative.", "tex": r"(1),(2),(4)\ \text{first order};\quad (3)\ \text{second order}"},
                {"text": "Linear means y and its derivatives appear only to the first power, never multiplied together.", "tex": r"(2)\ \text{has } y^2 \Rightarrow \text{nonlinear};\ (1),(3),(4)\ \text{linear}"},
                {"text": "Constant coefficients: the numbers multiplying y, y', y'' do not depend on t.", "tex": r"(4)\ \text{has coefficient } t \Rightarrow \text{variable coefficient}"}
            ],
            "answer": r"(1) first order, linear, constant coefficient, with input $\cos t$. (2) first order, nonlinear. (3) second order, linear, constant coefficients, no input. (4) first order, linear, variable coefficient (Section 8 solves this type)."
        },
        "sources": {
            "video": [vs(1, 0, "Strang and Moler introduce the series"),
                      vs(1, 90, "Turning solver black boxes into gray boxes"),
                      vs(1, 120, "Why matrices matter for differential equations"),
                      vs(2, 30, "First order: dy/dt = ay + q(t)"),
                      vs(2, 90, "Nonlinear: dy/dt = f(y)"),
                      vs(2, 180, "Second derivative: acceleration and bending"),
                      vs(2, 240, "Newton's law: my'' + by' + ky = f(t)"),
                      vs(2, 300, "Linear with constant coefficients: the good equations"),
                      vs(2, 330, "Exponentials give nice solutions"),
                      vs(2, 450, "Systems: y' = Ay and eigenvalues"),
                      vs(2, 570, "Numerical solutions: Euler to ode45"),
                      vs(2, 690, "Goal: heat, wave and Laplace equations")],
            "book": [bk(1, "Section 1.1: four examples, linear versus nonlinear")]
        },
        "tutorNotes": "Videos 1-2 (overview). Model equation y' = ay + q(t); nonlinear y' = f(y) or f(t,y); second order my'' + by' + ky = f(t); systems y' = Ay, y'' + Sy = 0 with eigenvalues; numerical methods (Euler ODE1 to ode45, Moler's parallel videos); PDEs: heat u_t = u_xx, wave u_tt = u_xx, Laplace. Linear constant-coefficient equations are the ones with full formula solutions; exponential inputs give exponential outputs."
    },
    {
        "nav": "The calculus you need",
        "v": 3,
        "title": r"Derivatives, the fundamental theorem and Taylor's tangent line",
        "time": [0, 888],
        "summary": r"Three pieces of calculus carry the course: the derivatives of $e^t$ and friends with the product and chain rules; the fundamental theorem, which checks that $y(t) = \int_0^t e^{t-s}q(s)\,ds$ solves $y' = y + q$; and the tangent line $f(t+\Delta t) \approx f(t) + \Delta t\, f'(t)$, the first term of the Taylor series.",
        "goals": [
            r"Use the product rule and the fundamental theorem to verify that $y(t) = \int_0^t e^{t-s} q(s)\,ds$ solves $y' = y + q(t)$.",
            r"Write the tangent line and the tangent parabola of $f$ at $t$.",
            r"State the Taylor series and explain why $e^t$ equals its series."
        ],
        "notes": [
            {"heading": "Facts and rules",
             "paragraphs": [
                 r"The facts are short: the derivatives of $x^n$, of $\sin$ and $\cos$, of $\ln x$ (which is $1/x$), and above all $\dfrac{d}{dt}e^t = e^t$, which says that $y = e^t$ solves $y' = y$.",
                 r"The rules turn those few facts into derivatives of almost everything: the derivative is linear, the product rule $(fg)' = f'g + fg'$, the quotient rule, and the chain rule $\dfrac{d}{dx}f(g(x)) = f'(g(x))\,g'(x)$. Chains of functions are what make the list of reachable functions so long."
             ]},
            {"heading": "The fundamental theorem as a working tool",
             "paragraphs": [
                 r"The fundamental theorem says that integrating and then differentiating gives the function back: $\dfrac{d}{dt}\displaystyle\int_0^t g(s)\,ds = g(t)$. The variable $s$ inside is a dummy; only the upper limit $t$ matters.",
                 r"Strang uses it at once on a formula that will return many times: $y(t) = \displaystyle\int_0^t e^{t-s} q(s)\,ds$. Pull $e^t$ out of the integral so $y = e^t \cdot \displaystyle\int_0^t e^{-s} q(s)\,ds$ is a product. The product rule gives two terms. Differentiating $e^t$ leaves $e^t$, so the first term is $y$ itself. The fundamental theorem turns the derivative of the integral into $e^{-t}q(t)$, and $e^t e^{-t} = 1$ leaves $q(t)$. So $y' = y + q$: the formula solves the equation, and $y(0) = 0$ because the integral over $[0, 0]$ is empty."
             ]},
            {"heading": "Tangent line, tangent parabola, Taylor series",
             "paragraphs": [
                 r"Over a short step $\Delta t$ the change in $f$ is about the step times the slope: $f(t + \Delta t) \approx f(t) + \Delta t\, f'(t)$. That is the tangent line, and dividing by $\Delta t$ gives back the definition $\Delta f/\Delta t \approx f'$. Euler's numerical method in the later videos is exactly this step.",
                 r"For a longer step the line drifts away from the curve, because the curve bends. Adding $\tfrac12 (\Delta t)^2 f''(t)$ accounts for the bending and gives the tangent parabola. Continuing with $\tfrac{1}{n!}(\Delta t)^n f^{(n)}(t)$ for every $n$ gives the Taylor series. For $e^t$ every derivative is $e^t$, so the series at $0$ is $1 + t + t^2/2! + t^3/3! + \cdots$, and it equals $e^t$ for every $t$. For most functions the higher derivatives are impractical, but the line and parabola are always useful."
             ]}
        ],
        "keyIdeas": [
            r"$(e^t)' = e^t$; product, quotient and chain rules.",
            r"$\dfrac{d}{dt}\int_0^t g(s)\,ds = g(t)$.",
            r"$y = \int_0^t e^{t-s}q(s)\,ds$ solves $y' = y + q$, $y(0) = 0$.",
            r"$f(t+\Delta t) = f(t) + \Delta t f'(t) + \tfrac12 \Delta t^2 f''(t) + \cdots$"
        ],
        "example": {
            "title": "Check the formula for a constant deposit (authored)",
            "problem": r"Take $q(t) = 1$ in $y(t) = \int_0^t e^{t-s} q(s)\,ds$. Find $y(t)$ and confirm that $y' = y + 1$ and $y(0) = 0$.",
            "steps": [
                {"text": "Pull out e^t and integrate e^{-s} from 0 to t.", "tex": r"y = e^t \int_0^t e^{-s}\,ds = e^t\left(1 - e^{-t}\right) = e^t - 1"},
                {"text": "Differentiate and compare with y + 1.", "tex": r"y' = e^t = (e^t - 1) + 1 = y + 1"},
                {"text": "Starting value.", "tex": r"y(0) = e^0 - 1 = 0"}
            ],
            "answer": r"$y = e^t - 1$. Each unit deposited at time $s$ has grown by the factor $e^{t-s}$ at time $t$; adding all deposits gives $e^t - 1$."
        },
        "sources": {
            "video": [vs(3, 30, "Derivatives you must know, especially of e^x"),
                      vs(3, 90, "Rules: linearity, product, quotient, chain"),
                      vs(3, 150, "The fundamental theorem of calculus"),
                      vs(3, 210, "y = integral of e^(t-s) q(s) solves y' = y + q"),
                      vs(3, 330, "Product rule on e^t times the integral"),
                      vs(3, 420, "Fundamental theorem gives e^(-t) q(t); terms are y and q"),
                      vs(3, 510, "Tangent line f(t + dt) = f(t) + dt f'(t)"),
                      vs(3, 600, "Picture: tangent line to e^t"),
                      vs(3, 660, "Bending: tangent parabola with (1/2) dt^2 f''"),
                      vs(3, 750, "Taylor series with 1/n! terms")],
            "book": [bk(4, "Section 1.2: the calculus you need, the fundamental theorem"),
                     bk(6, "Section 1.2: tangent line, tangent parabola and Taylor series")]
        },
        "tutorNotes": "Video 3. Product-rule check: y = e^t * integral_0^t e^(-s) q(s) ds; derivative = y + e^t e^(-t) q(t) = y + q. Tangent line f(t+dt) ~ f(t) + dt f'(t); tangent parabola adds (1/2) dt^2 f''(t); Taylor series sum dt^n f^(n)(t)/n!; equals e^t for all t."
    },
    {
        "nav": "Exponential input",
        "v": 4,
        "title": r"The exponential response to $e^{st}$, and resonance",
        "time": [0, 800],
        "summary": r"For $y' = ay + e^{st}$ a particular solution is a multiple $Ye^{st}$, and substitution gives $Y = 1/(s-a)$. Adding the null solution $Ce^{at}$ and matching $y(0)$ gives $y(t) = y(0)e^{at} + \dfrac{e^{st} - e^{at}}{s - a}$. When $s = a$ (resonance) the fraction becomes $0/0$ and its limit is $t\,e^{at}$.",
        "goals": [
            r"Substitute $y_p = Ye^{st}$ and find the exponential response $Y = 1/(s-a)$.",
            r"Build the complete solution $y_p + y_n$ and match the initial condition.",
            r"Split the answer into the part from $y(0)$ and the very particular part that starts at $0$.",
            r"Recognise resonance $s = a$ and obtain $t e^{at}$ with l'Hôpital's rule."
        ],
        "notes": [
            {"heading": "Why exponentials are the best inputs",
             "paragraphs": [
                 r"The derivative of $e^{st}$ is $s\,e^{st}$: the same function times a number. So if the input is $e^{st}$, we can hope the output is also a multiple of $e^{st}$. The multiplier is called the exponential response."
             ]},
            {"heading": "Finding the particular solution",
             "paragraphs": [
                 r"Substitute $y = Ye^{st}$ into $y' = ay + e^{st}$: the left side is $sYe^{st}$ and the right side is $aYe^{st} + e^{st}$. Every term contains $e^{st}$, which is never zero, so divide it out: $sY = aY + 1$, that is $(s - a)Y = 1$ and $Y = \dfrac{1}{s-a}$."
             ]},
            {"heading": "Null solutions and the initial value",
             "paragraphs": [
                 r"$y_p = e^{st}/(s-a)$ solves the equation but usually has the wrong starting value. The null (homogeneous) equation $y' = ay$, with the source removed, has solutions $Ce^{at}$, and adding one to $y_p$ still solves the full equation. Choose $C$ so that $y(0)$ is right: at $t = 0$, $y(0) = \dfrac{1}{s-a} + C$, so $C = y(0) - \dfrac{1}{s-a}$. Note that $C$ is not $y(0)$ itself.",
                 r"Regrouping gives the clearest form, $y(t) = y(0)\,e^{at} + \dfrac{e^{st} - e^{at}}{s - a}$. The first term is the initial deposit growing on its own. The second term is what the deposits $e^{st}$ have built up; it is zero at $t = 0$. Strang calls it the very particular solution: of all the particular solutions, it is the one that starts from zero."
             ]},
            {"heading": "Resonance",
             "paragraphs": [
                 r"If $s = a$ the input grows at exactly the natural rate of the system, and $1/(s-a)$ is meaningless. But the very particular solution is $0/0$, not infinity: its top $e^{st} - e^{at}$ also vanishes. L'Hôpital's rule takes the ratio of derivatives with respect to $s$: the top gives $t e^{st}$, the bottom gives $1$. Letting $s \to a$ leaves $t\,e^{at}$.",
                 r"So at resonance $y(t) = y(0)e^{at} + t\,e^{at}$. The extra factor $t$ is the signature of resonance; you will see it again in second order equations."
             ]}
        ],
        "keyIdeas": [
            r"$y' = ay + e^{st}$: $\;y_p = \dfrac{e^{st}}{s-a}$.",
            r"$y = y(0)e^{at} + \dfrac{e^{st} - e^{at}}{s-a}$.",
            r"Very particular part starts at $0$.",
            r"Resonance $s = a$: $\;y_{vp} = t\,e^{at}$."
        ],
        "example": {
            "title": "A decaying system with growing deposits (authored)",
            "problem": r"Solve $y' = -2y + e^{t}$ with $y(0) = 1$. Then solve $y' = 2y + e^{2t}$ with $y(0) = 0$.",
            "steps": [
                {"text": "First problem: a = -2, s = 1, so s - a = 3.", "tex": r"y = e^{-2t} + \frac{e^{t} - e^{-2t}}{3}"},
                {"text": "Check: y(0) = 1 + 0 = 1, and the e^t part satisfies y' + 2y = e^t.", "tex": r"\left(\tfrac{e^t}{3}\right)' + 2\cdot\tfrac{e^t}{3} = e^t"},
                {"text": "Second problem: s = a = 2 is resonance, and y(0) = 0.", "tex": r"y = t\,e^{2t}"},
                {"text": "Check by substitution.", "tex": r"y' = e^{2t} + 2t e^{2t} = 2y + e^{2t}"}
            ],
            "answer": r"$y = e^{-2t} + (e^t - e^{-2t})/3$, which approaches $e^t/3$ as the transient dies out; at resonance, $y = t e^{2t}$."
        },
        "sources": {
            "video": [vs(4, 0, "Equation dy/dt = ay + e^(st), money in a bank"),
                      vs(4, 60, "Particular solution Y e^(st)"),
                      vs(4, 90, "Substitute and divide by e^(st)"),
                      vs(4, 150, "Exponential response Y = 1/(s - a)"),
                      vs(4, 180, "Null solutions C e^(at)"),
                      vs(4, 240, "Match y(0): C = y(0) - 1/(s - a)"),
                      vs(4, 330, "Regroup: initial part and deposit part"),
                      vs(4, 390, "The very particular solution starts from 0"),
                      vs(4, 450, "Breakdown at s = a: resonance"),
                      vs(4, 540, "Resonant answer t e^(at)"),
                      vs(4, 630, "L'Hôpital: derivative with respect to s")],
            "book": [bk(17, "Section 1.4: four particular solutions"),
                     bk(18, "Particular and complete solutions"),
                     bk(26, "Resonance")]
        },
        "tutorNotes": "Video 4. y' = ay + e^(st): Y = 1/(s - a); y = Y e^(st) + C e^(at), C = y(0) - 1/(s - a); regrouped y = y(0) e^(at) + (e^(st) - e^(at))/(s - a), the second term (very particular) is 0 at t = 0. Resonance s = a: 0/0, l'Hopital in s gives t e^(at)."
    },
    {
        "nav": "Cosine input",
        "v": 5,
        "title": r"The response to $\cos \omega t$: rectangular and polar forms",
        "time": [0, 955],
        "summary": r"For $y' = ay + \cos\omega t$ the particular solution needs both $M\cos\omega t$ and $N\sin\omega t$. Matching coefficients gives $M = \dfrac{-a}{\omega^2 + a^2}$ and $N = \dfrac{\omega}{\omega^2+a^2}$. The same answer is one shifted cosine $G\cos(\omega t - \alpha)$ with gain $G = 1/\sqrt{\omega^2 + a^2}$ and phase lag $\alpha$, where $\tan\alpha = N/M$.",
        "goals": [
            r"Explain why $y_p = M\cos\omega t$ alone fails, and why $N\sin\omega t$ is needed.",
            r"Match the cosine and sine coefficients to get two equations for $M$ and $N$, and solve them.",
            r"Convert $M\cos\omega t + N\sin\omega t$ to $G\cos(\omega t - \alpha)$ using $G = \sqrt{M^2 + N^2}$ and $\tan\alpha = N/M$."
        ],
        "notes": [
            {"heading": "Why a sine term appears",
             "paragraphs": [
                 r"An oscillating input models alternating current, sound, anything that goes round. The derivative of $\cos\omega t$ is $-\omega\sin\omega t$, so a pure cosine guess produces a sine term that nothing can cancel. The guess must allow both: $y_p = M\cos\omega t + N\sin\omega t$."
             ]},
            {"heading": "Matching coefficients",
             "paragraphs": [
                 r"Substitute into $y' = ay + \cos\omega t$. The left side is $-\omega M\sin\omega t + \omega N\cos\omega t$; the right side is $aM\cos\omega t + aN\sin\omega t + \cos\omega t$. This must hold at every time, so the cosine coefficients agree and so do the sine coefficients:",
                 r"$\cos$: $\;-aM + \omega N = 1, \qquad \sin$: $\;-\omega M - aN = 0.$",
                 r"Two linear equations, two unknowns. The solution is $M = \dfrac{-a}{\omega^2 + a^2}$, $N = \dfrac{\omega}{\omega^2 + a^2}$. Check the sine equation: $-\omega M = \dfrac{a\omega}{\omega^2+a^2}$ and $aN = \dfrac{a\omega}{\omega^2+a^2}$, so the difference is zero."
             ]},
            {"heading": "Steady oscillation and transient",
             "paragraphs": [
                 r"The complete solution adds $Ce^{at}$. In most applications $a < 0$, so that term dies away: it is the transient. What remains, and what your ear hears from a radio, is the particular oscillation at the input frequency."
             ]},
            {"heading": "One cosine with a phase lag",
             "paragraphs": [
                 r"Two out-of-phase terms combine into one shifted cosine. Expand $G\cos(\omega t - \alpha) = G\cos\alpha\cos\omega t + G\sin\alpha\sin\omega t$ and match: $M = G\cos\alpha$, $N = G\sin\alpha$. These are polar coordinates of the point $(M, N)$.",
                 r"Squaring and adding uses $\cos^2 + \sin^2 = 1$: $G = \sqrt{M^2 + N^2}$, which here simplifies to $G = \dfrac{1}{\sqrt{\omega^2 + a^2}}$. Dividing removes $G$: $\tan\alpha = N/M$. The book calls $M\cos\omega t + N\sin\omega t = G\cos(\omega t - \alpha)$ the sinusoidal identity. The gain $G$ is the number that matters most: how strongly the system passes on an input of frequency $\omega$.",
                 r"Careful with the angle: $\tan\alpha = N/M$ alone fixes $\alpha$ only up to $\pi$. Choose the angle of the point $(M, N)$ itself (MATLAB's atan2(N, M)). For a stable system, $a < 0$, both $M$ and $N$ are positive when $\omega > 0$, so $0 < \alpha < \pi/2$: the output lags the input."
             ]},
            {"heading": "Three forms",
             "paragraphs": [
                 r"The answer has three forms: rectangular ($M$ and $N$), polar ($G$ and $\alpha$), and complex, which uses $e^{i\omega t}$ and is the subject of Section 7."
             ]}
        ],
        "keyIdeas": [
            r"$y_p = M\cos\omega t + N\sin\omega t$.",
            r"$M = \dfrac{-a}{\omega^2 + a^2},\; N = \dfrac{\omega}{\omega^2 + a^2}$.",
            r"$y_p = G\cos(\omega t - \alpha)$, $\;G = \dfrac{1}{\sqrt{\omega^2+a^2}}$, $\;\tan\alpha = N/M$.",
            r"$Ce^{at}$ with $a < 0$ is the transient."
        ],
        "example": {
            "title": "Unit frequency, unit decay (authored)",
            "problem": r"Find the steady oscillation of $y' = -y + \cos t$ in both forms.",
            "steps": [
                {"text": "Here a = -1 and ω = 1, so ω² + a² = 2.", "tex": r"M = \frac{1}{2},\qquad N = \frac{1}{2}"},
                {"text": "Gain and phase from the point (M, N) = (1/2, 1/2).", "tex": r"G = \sqrt{\tfrac14 + \tfrac14} = \frac{1}{\sqrt 2},\qquad \alpha = \frac{\pi}{4}"},
                {"text": "Check the cosine equation -aM + ωN = 1.", "tex": r"\tfrac12 + \tfrac12 = 1"}
            ],
            "answer": r"$y_p = \tfrac12\cos t + \tfrac12\sin t = \tfrac{1}{\sqrt2}\cos\!\left(t - \tfrac{\pi}{4}\right)$: the output is smaller by $1/\sqrt2$ and lags by an eighth of a cycle."
        },
        "sources": {
            "video": [vs(5, 0, "Oscillating input: alternating current"),
                      vs(5, 30, "A cosine alone will not work"),
                      vs(5, 90, "Try y = M cos + N sin and substitute"),
                      vs(5, 180, "Match cosine terms"),
                      vs(5, 210, "Match sine terms"),
                      vs(5, 240, "Solve for M and N"),
                      vs(5, 330, "Transient C e^(at) dies away when a < 0"),
                      vs(5, 420, "Another form: one shifted cosine"),
                      vs(5, 540, "M = G cos(alpha), N = G sin(alpha)"),
                      vs(5, 630, "Gain G = sqrt(M^2 + N^2)"),
                      vs(5, 690, "tan(alpha) = N/M"),
                      vs(5, 750, "Sinusoidal identity and gain"),
                      vs(5, 810, "Three forms; complex numbers next")],
            "book": [bk(30, "Section 1.5: real and complex sinusoids"),
                     bk(35, "The sinusoidal identity")]
        },
        "tutorNotes": "Video 5. y' = ay + cos(wt): y_p = M cos + N sin; cos: -aM + wN = 1; sin: -wM - aN = 0; M = -a/(w^2 + a^2), N = w/(w^2 + a^2). Polar: M = G cos(alpha), N = G sin(alpha); G = sqrt(M^2 + N^2) = 1/sqrt(w^2 + a^2); tan(alpha) = N/M (use the angle of the point (M, N)). Transient C e^(at) when a < 0."
    },
    {
        "nav": "Any input",
        "v": 6,
        "title": r"One formula for every input $q(t)$",
        "time": [0, 839],
        "summary": r"For $y' = ay + q(t)$ the complete solution is $y(t) = e^{at}y(0) + \int_0^t e^{a(t-s)}q(s)\,ds$. The first term is the starting balance growing; the integral adds every deposit $q(s)\,ds$, each grown by $e^{a(t-s)}$ over the time it has been in the account. The product rule and the fundamental theorem confirm it.",
        "goals": [
            r"Write the general formula and explain each factor as a deposit and its growth.",
            r"Verify the formula with the product rule and the fundamental theorem.",
            r"Recover the special answers (constant, exponential, cosine) by putting those inputs into the integral."
        ],
        "notes": [
            {"heading": "Deposits that never stop",
             "paragraphs": [
                 r"Think of $q(t)$ as money paid in continuously, at a rate per unit time, not once a month. The starting deposit $y(0)$ grows by itself to $e^{at}y(0)$: that is the null solution that matches the initial condition.",
                 r"A small deposit $q(s)\,ds$ made at time $s$ has the remaining time $t - s$ to grow, so at time $t$ it is worth $e^{a(t-s)}q(s)\,ds$. The equation is linear, so the contributions simply add, and adding continuously is integrating over $s$ from $0$ to $t$:",
                 r"$y(t) = e^{at}\,y(0) + \displaystyle\int_0^t e^{a(t-s)}\,q(s)\,ds.$",
                 r"The variable $s$ is the clock that runs over the deposit times; $t$ is the moment when we look at the balance."
             ]},
            {"heading": "Checking it",
             "paragraphs": [
                 r"The first term solves $y' = ay$. For the integral, take $e^{at}$ outside, because it does not depend on $s$: $y_p = e^{at}\int_0^t e^{-as}q(s)\,ds$. The product rule gives two terms. Differentiating $e^{at}$ gives $a\,y_p$. Differentiating the integral gives, by the fundamental theorem, $e^{-at}q(t)$, and $e^{at}e^{-at} = 1$ leaves $q(t)$. Together, $y_p' = a\,y_p + q$. This is Section 2's check with a general rate $a$."
             ]},
            {"heading": "The special inputs fit inside",
             "paragraphs": [
                 r"The nice inputs of the earlier sections (constants, $e^{st}$, $\cos\omega t$ and $\sin\omega t$, and also powers of $t$ and $t\,e^{st}$) give answers we can recognise without the integral. Put any of them into the general formula and the integral produces the same answers. The step and delta inputs of the next section are two more nice functions, and Section 8 derives the same formula a second way, with an integrating factor."
             ]}
        ],
        "keyIdeas": [
            r"$y = e^{at}y(0) + \int_0^t e^{a(t-s)}q(s)\,ds$.",
            r"Deposit at time $s$ grows by $e^{a(t-s)}$.",
            r"Linear: contributions add, so integrate.",
            r"Check: product rule plus fundamental theorem."
        ],
        "example": {
            "title": "A deposit rate that rises steadily (authored)",
            "problem": r"Solve $y' = -y + t$ with $y(0) = 0$ by the general formula.",
            "steps": [
                {"text": "Here a = -1 and q(s) = s.", "tex": r"y(t) = \int_0^t e^{-(t-s)}\,s\,ds = e^{-t}\int_0^t s\,e^{s}\,ds"},
                {"text": "Integrate s e^s by parts: its antiderivative is (s - 1)e^s.", "tex": r"y = e^{-t}\left[(s-1)e^{s}\right]_0^t = e^{-t}\left((t-1)e^{t} + 1\right) = t - 1 + e^{-t}"},
                {"text": "Check by substitution.", "tex": r"y' = 1 - e^{-t} = -\left(t - 1 + e^{-t}\right) + t"}
            ],
            "answer": r"$y = t - 1 + e^{-t}$: after the transient $e^{-t}$ dies away, the balance follows the line $t - 1$."
        },
        "sources": {
            "video": [vs(6, 0, "A formula for any source term"),
                      vs(6, 60, "Deposits made continuously"),
                      vs(6, 90, "y(0) grows as e^(at): the null solution"),
                      vs(6, 150, "Each deposit at time s grows over t - s"),
                      vs(6, 180, "Growth factor e^(a(t - s)); add by integrating"),
                      vs(6, 240, "The complete formula"),
                      vs(6, 270, "Special inputs: constant, exponential, cosine"),
                      vs(6, 360, "Coming: step and delta functions"),
                      vs(6, 420, "Powers of t and t e^(st) are also nice"),
                      vs(6, 480, "Special answers fit inside the general formula"),
                      vs(6, 540, "Derivation by integrating factor comes later"),
                      vs(6, 570, "Check: take e^(at) out of the integral"),
                      vs(6, 630, "Product rule: a y from the first term"),
                      vs(6, 690, "Fundamental theorem gives e^(-at) q(t)"),
                      vs(6, 750, "Result: a y + q(t)")],
            "book": [bk(19, "Section 1.4: inputs q(t) and responses y(t)"),
                     bk(41, "Section 1.6: the particular solution from q(t)")]
        },
        "tutorNotes": "Video 6. y(t) = e^(at) y(0) + integral_0^t e^(a(t - s)) q(s) ds. Deposit q(s) ds at time s grows by e^(a(t - s)); linearity lets contributions add. Check: y_p = e^(at) integral_0^t e^(-as) q(s) ds; product rule gives a y_p + e^(at) e^(-at) q(t) = a y_p + q. Special nice inputs (constant, e^(st), cos/sin, t^n, t e^(st), step, delta) fit inside the formula."
    },
    {
        "nav": "Step and delta",
        "v": 7,
        "title": r"The step function $H(t)$ and its derivative, the delta function $\delta(t)$",
        "time": [0, 941],
        "summary": r"The step $H(t)$ jumps from $0$ to $1$ at $t = 0$; its derivative $\delta(t)$ is zero except for an instant impulse. A delta function is known through integrals: $\int \delta(t)\,dt = 1$ and $\int \delta(t)f(t)\,dt = f(0)$. A single deposit $\delta(t - T)$ in $y' = ay + \delta(t-T)$, $y(0) = 0$, gives the impulse response $y = e^{a(t-T)}$ for $t \ge T$.",
        "goals": [
            r"Draw $H(t)$ and the shifted step $H(t - T)$.",
            r"Explain why $\delta = H'$ is defined through its integrals, and evaluate $\int \delta(t - T) f(t)\,dt = f(T)$.",
            r"Solve $y' = ay + \delta(t - T)$ from $y(0) = 0$ and recognise the impulse response."
        ],
        "notes": [
            {"heading": "The step and its shift",
             "paragraphs": [
                 r"The unit step (Heaviside) function is $H(t) = 0$ for $t < 0$ and $H(t) = 1$ for $t \ge 0$. Replacing $t$ by $t - T$ moves the whole graph right by $T$: $H(t - T)$ jumps where $t - T = 0$, at $t = T$. As an input, a step is a switch that turns on a constant source and leaves it on."
             ]},
            {"heading": "The delta function",
             "paragraphs": [
                 r"The slope of $H$ is zero everywhere except at the jump, where it is infinite. That derivative is the delta function $\delta(t)$. Saying “infinite” is not precise enough to compute with, so a delta function is described by what happens when it is integrated, the direction in which calculus is gentle.",
                 r"Integrating $\delta$ gives back $H$, which goes from $0$ at $-\infty$ to $1$ at $+\infty$: $\displaystyle\int_{-\infty}^{\infty}\delta(t)\,dt = 1$. As an input it deposits one full unit in one instant, like a golf club striking a ball. More generally, because $\delta$ acts only at $t = 0$, $\displaystyle\int_{-\infty}^{\infty}\delta(t)f(t)\,dt = f(0)$ for any continuous $f$. So $\int\delta(t)\sin t\,dt = \sin 0 = 0$, $\int \delta(t)e^t\,dt = 1$, and the shifted version picks out the value at $T$: $\int \delta(t - T) e^t\,dt = e^T$."
             ]},
            {"heading": "The impulse response",
             "paragraphs": [
                 r"Solve $y' = ay + \delta(t - T)$ with $y(0) = 0$. Before $T$ nothing has been deposited and $y = 0$. At $T$ one unit arrives, and from then on it grows at rate $a$: $y(t) = e^{a(t - T)}$ for $t \ge T$. In one line, $y(t) = H(t - T)\,e^{a(t - T)}$. (On the board the factor $a$ is first left out of the exponent and then corrected.)",
                 r"For $a = 1$ (100% interest) the deposit is worth $e \approx 2.718$ a year later, not $2$, because the interest is compounded continuously. This response to a single impulse is called the impulse response; for second order equations it becomes the central function of the subject."
             ]},
            {"heading": "The step response",
             "paragraphs": [
                 r"Integrating the impulse response over all deposit times gives the response to a step. For $y' = ay + H(t - T)$, $y(0) = 0$ and $a \neq 0$: $y = 0$ before $T$ and $y = \dfrac{e^{a(t-T)} - 1}{a}$ after $T$. When $a < 0$ this rises to the steady state $-1/a$."
             ]}
        ],
        "keyIdeas": [
            r"$H(t - T)$ jumps from $0$ to $1$ at $t = T$; $\;\delta = H'$.",
            r"$\int\delta = 1$, $\;\int\delta(t - T)f(t)\,dt = f(T)$.",
            r"Impulse response: $y = H(t-T)\,e^{a(t-T)}$.",
            r"Step response: $y = \dfrac{e^{a(t-T)}-1}{a}$ for $t \ge T$."
        ],
        "example": {
            "title": "An impulse and a step (authored)",
            "problem": r"Solve $y' = -y + 3\,\delta(t - 2)$ and $y' = -y + H(t - 2)$, both with $y(0) = 0$.",
            "steps": [
                {"text": "The impulse deposits 3 units at t = 2, which then decay at rate a = -1.", "tex": r"y = 3\,H(t - 2)\,e^{-(t-2)}"},
                {"text": "The step turns on a unit source at t = 2.", "tex": r"y = H(t-2)\left(1 - e^{-(t-2)}\right)"},
                {"text": "Check the step answer for t > 2.", "tex": r"y' = e^{-(t-2)} = -\left(1 - e^{-(t-2)}\right) + 1"}
            ],
            "answer": r"The impulse response jumps to $3$ at $t = 2$ and decays; the step response starts at $0$ at $t = 2$ and rises towards the steady state $1$."
        },
        "sources": {
            "video": [vs(7, 30, "Step function H(t): 0 then 1"),
                      vs(7, 60, "Shifted step H(t - T)"),
                      vs(7, 120, "The derivative of the step is the delta function"),
                      vs(7, 210, "Delta as an input: one deposit in an instant"),
                      vs(7, 270, "Golf club: a model of an instant hit"),
                      vs(7, 330, "The integral of delta is the step"),
                      vs(7, 390, "Total integral of delta is 1"),
                      vs(7, 480, "Integral of delta times f is f(0)"),
                      vs(7, 540, "Examples with sin t and e^t"),
                      vs(7, 630, "Shifted delta picks out e^T"),
                      vs(7, 660, "Solve dy/dt = ay + delta(t - T), y(0) = 0"),
                      vs(7, 750, "Growth e^(a(t - T)) after the deposit"),
                      vs(7, 870, "The impulse response")],
            "book": [bk(21, "Section 1.4: the step function"),
                     bk(23, "The delta function"),
                     bk(24, "The impulse response solves y' - ay = delta")]
        },
        "tutorNotes": "Video 7. H(t) = 0 for t < 0, 1 for t >= 0; H(t - T) shifts the jump to T. delta = H' is defined through integrals: integral of delta = 1, integral of delta(t - T) f(t) dt = f(T). y' = ay + delta(t - T), y(0) = 0: y = H(t - T) e^(a(t - T)) (the board first omitted a and corrected it). Step: y = (e^(a(t - T)) - 1)/a for t >= T."
    },
    {
        "nav": "Complex exponential",
        "v": 8,
        "title": r"Complex input $e^{i\omega t}$: one exponential gives both real answers",
        "time": [0, 771],
        "summary": r"Euler's formula $e^{i\omega t} = \cos\omega t + i\sin\omega t$ turns an oscillating input into an exponential. Then $Y = \dfrac{1}{i\omega - a}$, and writing $i\omega - a = Re^{i\alpha}$ in polar form gives $y = \dfrac{1}{R}e^{i(\omega t - \alpha)}$. Its real part, $\dfrac{1}{R}\cos(\omega t - \alpha)$, answers the cosine input; its imaginary part answers the sine input.",
        "goals": [
            r"Find $Y = 1/(i\omega - a)$ by substituting $Ye^{i\omega t}$.",
            r"Write $i\omega - a$ in polar form: $R = \sqrt{a^2 + \omega^2}$ and angle $\alpha$.",
            r"Take real and imaginary parts to solve the cosine and sine problems at once."
        ],
        "notes": [
            {"heading": "Back to exponentials",
             "paragraphs": [
                 r"Euler's formula $\cos\omega t + i\sin\omega t = e^{i\omega t}$ is why complex numbers help. With the input $e^{i\omega t}$ the equation $y' = ay + e^{i\omega t}$ is the exponential problem of Section 3 with $s = i\omega$. Its solution is complex; call it $y_c$.",
                 r"Substitute $y_c = Ye^{i\omega t}$: $i\omega Y = aY + 1$, so $Y = \dfrac{1}{i\omega - a}$. Because the equation has real coefficients, the real part of $y_c$ solves the equation with input $\cos\omega t$ and the imaginary part solves it with input $\sin\omega t$. One calculation, two real answers."
             ]},
            {"heading": "Polar form of the awkward number",
             "paragraphs": [
                 r"The number $i\omega - a$ sits in the complex plane at real part $-a$ and imaginary part $\omega$. Its length is $R = \sqrt{a^2 + \omega^2}$ by Pythagoras, and its angle $\alpha$ from the positive real axis has $\tan\alpha = \omega/(-a)$. So $i\omega - a = Re^{i\alpha}$.",
                 r"Dividing by $Re^{i\alpha}$ divides by $R$ and changes the sign of the angle: $Y = \dfrac{1}{R}e^{-i\alpha}$. Multiplying exponentials adds exponents: $y_c = \dfrac{1}{R}e^{i(\omega t - \alpha)}$."
             ]},
            {"heading": "Real and imaginary parts",
             "paragraphs": [
                 r"The real part of $e^{i\theta}$ is $\cos\theta$, so the response to $\cos\omega t$ is $\dfrac{1}{R}\cos(\omega t - \alpha)$: gain $G = 1/R = 1/\sqrt{a^2 + \omega^2}$ and phase lag $\alpha$, exactly what Section 4 found with more work. The imaginary part gives $\dfrac{1}{R}\sin(\omega t - \alpha)$ for the input $\sin\omega t$.",
                 r"The angle here agrees with Section 4: the point $(M, N)$ was $(-a, \omega)/(\omega^2 + a^2)$, a positive multiple of $(-a, \omega)$, so both have the same angle $\alpha$."
             ]}
        ],
        "keyIdeas": [
            r"$e^{i\omega t} = \cos\omega t + i\sin\omega t$.",
            r"$Y = \dfrac{1}{i\omega - a} = \dfrac{1}{R}e^{-i\alpha}$, $\;R = \sqrt{a^2 + \omega^2}$.",
            r"$\operatorname{Re}\,y_c = \dfrac{1}{R}\cos(\omega t - \alpha)$ answers $\cos\omega t$.",
            r"$\operatorname{Im}\,y_c$ answers $\sin\omega t$."
        ],
        "example": {
            "title": "Section 4's example the complex way (authored)",
            "problem": r"Use $e^{it}$ to find the steady responses of $y' = -y + \cos t$ and $y' = -y + \sin t$.",
            "steps": [
                {"text": "Here a = -1, ω = 1, so iω - a = 1 + i.", "tex": r"Y = \frac{1}{1 + i} = \frac{1 - i}{2}"},
                {"text": "Multiply by e^{it} = cos t + i sin t and collect.", "tex": r"y_c = \frac{(1-i)(\cos t + i\sin t)}{2} = \frac{\cos t + \sin t}{2} + i\,\frac{\sin t - \cos t}{2}"},
                {"text": "Polar form: 1 + i has R = √2 and α = π/4.", "tex": r"y_c = \frac{1}{\sqrt2}\,e^{i(t - \pi/4)}"}
            ],
            "answer": r"Cosine input: $\tfrac12(\cos t + \sin t) = \tfrac{1}{\sqrt2}\cos(t - \tfrac{\pi}{4})$, as in Section 4. Sine input: $\tfrac12(\sin t - \cos t) = \tfrac{1}{\sqrt2}\sin(t - \tfrac{\pi}{4})$."
        },
        "sources": {
            "video": [vs(8, 0, "Complex input cos + i sin"),
                      vs(8, 30, "Euler's formula: e^(i w t)"),
                      vs(8, 60, "Look for Y e^(i w t)"),
                      vs(8, 150, "Y = 1/(i w - a)"),
                      vs(8, 210, "Real part answers cosine, imaginary part answers sine"),
                      vs(8, 300, "Polar form r e^(i alpha)"),
                      vs(8, 330, "The complex plane"),
                      vs(8, 390, "R = sqrt(a^2 + w^2)"),
                      vs(8, 420, "The angle alpha"),
                      vs(8, 480, "Dividing gives e^(-i alpha)/R"),
                      vs(8, 540, "Combine into e^(i(w t - alpha))"),
                      vs(8, 600, "Real part: cos(w t - alpha)/R"),
                      vs(8, 660, "Gain and phase lag")],
            "book": [bk(30, "Section 1.5: complex sinusoids, Y = 1/(i omega - a)"),
                     bk(33, "Polar form and the unit circle")]
        },
        "tutorNotes": "Video 8. y' = ay + e^(iwt): Y = 1/(iw - a). iw - a = R e^(i alpha), R = sqrt(a^2 + w^2), alpha = angle of the point (-a, w). y_c = e^(i(wt - alpha))/R; Re gives response to cos(wt): cos(wt - alpha)/R; Im gives response to sin(wt). Same G and alpha as the M, N method."
    },
    {
        "nav": "Integrating factors",
        "v": 9,
        "title": r"Integrating factors, and a growth rate $a(t)$ that changes",
        "time": [0, 827],
        "summary": r"For $y' = a(t)\,y + q(t)$ multiply by $M(t) = e^{-\int_0^t a}$, which solves $M' = -aM$. The product rule then turns the equation into $(My)' = Mq$, which integrates directly. The result is $y(t) = e^{\int_0^t a}\,y(0) + \int_0^t e^{\int_s^t a}\,q(s)\,ds$: growth factors from $0$ to $t$ and from $s$ to $t$.",
        "goals": [
            r"Find the integrating factor $M(t)$ from $M' = -a(t)M$, for constant $a$ and for $a = 2t$.",
            r"Show that $(My)' = Mq$ and integrate it.",
            r"Read the solution as initial value times growth factor plus deposits times their own growth factors."
        ],
        "notes": [
            {"heading": "The idea",
             "paragraphs": [
                 r"Let the interest rate change with time: $y' = a(t)\,y + q(t)$. The exponential guesses of earlier sections no longer work, but a new method does. Choose $M(t)$ to solve the null equation with a minus sign, $M' = -a(t)\,M$, starting from $M(0) = 1$. For constant $a$ that is $M = e^{-at}$. In general the derivative of the exponent must be $-a(t)$, so $M(t) = e^{-\int_0^t a(\tau)\,d\tau}$."
             ]},
            {"heading": "Why it works",
             "paragraphs": [
                 r"Differentiate the product $My$: $(My)' = My' + M'y = M\,(y' - a y) = Mq$. The two $y$ terms cancel because of how $M$ was chosen. Now the equation says that a derivative equals a known function, so integrate from $0$ to $t$: $M(t)y(t) - M(0)y(0) = \displaystyle\int_0^t M(s)q(s)\,ds$, with $M(0) = 1$.",
                 r"Divide by $M(t)$. Since $1/M(t) = e^{+\int_0^t a}$ and $M(s)/M(t) = e^{\int_s^t a}$ (the exponents subtract, leaving the integral from $s$ to $t$):",
                 r"$y(t) = e^{\int_0^t a}\,y(0) + \displaystyle\int_0^t e^{\int_s^t a}\,q(s)\,ds.$"
             ]},
            {"heading": "Growth factors",
             "paragraphs": [
                 r"Read the formula as a bank statement. The initial deposit grows by the factor $G(0, t) = e^{\int_0^t a}$. A deposit made at time $s$ has only the time from $s$ to $t$ to grow, so it is multiplied by $G(s, t) = e^{\int_s^t a}$, and all deposits are added up. With constant $a$, $G(s, t) = e^{a(t-s)}$ and the formula is the one from Sections 2 and 3."
             ]},
            {"heading": "Example: a = 2t",
             "paragraphs": [
                 r"An interest rate $a(t) = 2t$ that climbs forever models runaway inflation. Then $\int_0^t 2\tau\,d\tau = t^2$, so $M = e^{-t^2}$ and $G(s, t) = e^{t^2 - s^2}$. The solution is $y(t) = e^{t^2}y(0) + \displaystyle\int_0^t e^{t^2 - s^2}q(s)\,ds$. (Video 10 names the factor $I$ instead of $M$; it is the same function.)"
             ]}
        ],
        "keyIdeas": [
            r"$M' = -a(t)M$, $\;M = e^{-\int_0^t a}$.",
            r"$(My)' = Mq$.",
            r"$y = e^{\int_0^t a}y(0) + \int_0^t e^{\int_s^t a}q(s)\,ds$.",
            r"$a = 2t$: growth factor $e^{t^2 - s^2}$."
        ],
        "example": {
            "title": "Rising rate, rising deposits (authored)",
            "problem": r"Solve $y' = 2t\,y + 2t$ with $y(0) = 0$.",
            "steps": [
                {"text": "Growth factor for a = 2t; q(s) = 2s and y(0) = 0.", "tex": r"y(t) = \int_0^t e^{t^2 - s^2}\,2s\,ds = e^{t^2}\int_0^t 2s\,e^{-s^2}\,ds"},
                {"text": "The inner integral is exact: 2s e^{-s^2} is the derivative of -e^{-s^2}.", "tex": r"y = e^{t^2}\left(1 - e^{-t^2}\right) = e^{t^2} - 1"},
                {"text": "Check by substitution.", "tex": r"y' = 2t\,e^{t^2} = 2t\left(e^{t^2} - 1\right) + 2t"}
            ],
            "answer": r"$y = e^{t^2} - 1$."
        },
        "sources": {
            "video": [vs(9, 30, "Let the interest rate a(t) change"),
                      vs(9, 60, "Integrating factor: dM/dt = -a(t) M"),
                      vs(9, 90, "Constant a: M = e^(-at)"),
                      vs(9, 120, "Varying a: M = e^(-integral of a)"),
                      vs(9, 180, "Product rule: (My)' = Mq"),
                      vs(9, 270, "Integrate both sides"),
                      vs(9, 300, "Example a = 2t: M = e^(-t^2)"),
                      vs(9, 450, "M(0) = 1; divide by M"),
                      vs(9, 570, "M(s)/M(t): integral from s to t"),
                      vs(9, 660, "Growth factor e^(t^2 - s^2)"),
                      vs(10, 0, "Same idea, factor called I"),
                      vs(10, 90, "Chain rule: derivative of e^(-t^2)"),
                      vs(10, 150, "Derivative of I y"),
                      vs(10, 240, "Integrate; I(0) = 1"),
                      vs(10, 390, "Growth from 0 to t and from s to t"),
                      vs(10, 510, "General rule I = e^(-integral of a)"),
                      vs(10, 630, "Constant a gives e^(-at)")],
            "book": [bk(19, "Section 1.4: solving linear equations by an integrating factor"),
                     bk(42, "Section 1.6: changing growth rate a(t)"),
                     bk(43, "Growth factor G(s, t)")]
        },
        "tutorNotes": "Videos 9-10. y' = a(t) y + q(t). Integrating factor M (called I in video 10): M' = -a M, M = exp(-integral_0^t a), M(0) = 1. (My)' = Mq. y = exp(integral_0^t a) y(0) + integral_0^t exp(integral_s^t a) q(s) ds. a = 2t: M = e^(-t^2), growth factor e^(t^2 - s^2). Constant a: e^(a(t - s)). The playlist titles say constant/varying, but both videos use a = 2t."
    },
]

# ---------------------------------------------------------------- quiz

def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-linear", r"Which equation is nonlinear?", [
        (r"$y' = y^2 + t$", True, r"Right. $y^2$ makes it nonlinear; doubling a solution does not give a solution."),
        (r"$y' = t\,y + \cos t$", False, r"No. The coefficient $t$ varies, but $y$ appears only to the first power: linear with a variable coefficient."),
        (r"$y'' + 4y = e^t$", False, r"No. This is linear, second order, with constant coefficients."),
        (r"$y' = -3y$", False, r"No. This is the simplest linear equation, with solutions $Ce^{-3t}$.")]),
    q("q-ftc", r"Why does $y(t) = \int_0^t e^{t-s}q(s)\,ds$ satisfy $y' = y + q$?", [
        (r"Write it as $e^t\int_0^t e^{-s}q(s)\,ds$; the product rule gives $y$ from $(e^t)'$ and $e^te^{-t}q(t) = q(t)$ from the fundamental theorem.", True, r"Right. The two terms of the product rule are exactly the two terms of the equation."),
        (r"Because the derivative of an integral is always zero.", False, r"No. The fundamental theorem says the derivative of $\int_0^t g$ is $g(t)$, not zero."),
        (r"Because $e^{t-s} = e^t - e^s$.", False, r"No. Exponents subtract inside one exponential: $e^{t-s} = e^t e^{-s}$, a product, which is what lets $e^t$ come outside."),
        (r"It does not; it only satisfies $y' = q$.", False, r"No. The factor $e^{t-s}$ makes each deposit grow, which produces the extra $y$ term.")]),
    q("q-taylor", r"Which expression is the tangent parabola to $f$ at $t$?", [
        (r"$f(t) + \Delta t\, f'(t) + \tfrac12(\Delta t)^2 f''(t)$", True, r"Right. The line uses the slope; the parabola adds the bending term with $\tfrac{1}{2!}$."),
        (r"$f(t) + \Delta t\, f'(t) + (\Delta t)^2 f''(t)$", False, r"No. The second-order Taylor coefficient is $1/2! = 1/2$; without it the parabola bends twice too much."),
        (r"$f(t) + \Delta t\, f'(t)$", False, r"No. That is the tangent line; it ignores bending."),
        (r"$f(t)\,e^{\Delta t}$", False, r"No. That is exact only for $f = Ce^t$; it is not the general tangent parabola.")]),
    q("q-expresp", r"For $y' = ay + e^{st}$ with $s \ne a$, what is the particular solution $Ye^{st}$?", [
        (r"$\dfrac{e^{st}}{s - a}$", True, r"Right. Substituting gives $sY = aY + 1$, so $Y = 1/(s - a)$."),
        (r"$\dfrac{e^{st}}{a - s}$", False, r"No. Check the sign: $sY - aY = 1$, so $Y(s - a) = 1$."),
        (r"$\dfrac{e^{at}}{s - a}$", False, r"No. The particular solution follows the input $e^{st}$; $e^{at}$ belongs to the null solution."),
        (r"$s\,e^{st}$", False, r"No. That is the derivative of the input, not the response.")]),
    q("q-vp", r"In $y = y(0)e^{at} + \dfrac{e^{st} - e^{at}}{s-a}$, what is special about the second term?", [
        (r"It is zero at $t = 0$: it is the part built by the input alone (the very particular solution).", True, r"Right. At $t = 0$ the top is $1 - 1 = 0$, so the initial value comes only from the first term."),
        (r"It is a null solution.", False, r"No. It contains $e^{st}/(s-a)$, which responds to the input; it is not a solution of $y' = ay$."),
        (r"It is the transient that always dies out.", False, r"No. Whether it dies out depends on $s$ and $a$; with $s > 0$ it grows."),
        (r"It equals $y(0)$ when $t = 0$.", False, r"No. It equals $0$ at $t = 0$.")]),
    q("q-resonance", r"What is the very particular solution of $y' = 3y + e^{3t}$?", [
        (r"$t\,e^{3t}$", True, r"Right. Here $s = a = 3$, so the fraction is $0/0$ and its limit as $s \to a$ is $te^{at}$. Check: $(te^{3t})' = e^{3t} + 3te^{3t}$."),
        (r"$e^{3t}/0$: there is no solution.", False, r"No. Resonance breaks the formula, not the equation; the factor $t$ appears instead."),
        (r"$\tfrac13 e^{3t}$", False, r"No. Substituting $Ce^{3t}$ gives $3C = 3C + 1$, which is impossible, so a pure exponential fails at resonance."),
        (r"$e^{3t} - 1$", False, r"No. Its derivative is $3e^{3t}$, but $3y + e^{3t} = 4e^{3t} - 3$.")]),
    q("q-gain", r"For $y' = ay + \cos\omega t$, what is the gain $G$ of the steady oscillation?", [
        (r"$\dfrac{1}{\sqrt{\omega^2 + a^2}}$", True, r"Right. $G = \sqrt{M^2 + N^2}$ with $M, N$ over $\omega^2 + a^2$, which simplifies to $1/\sqrt{\omega^2 + a^2}$."),
        (r"$\dfrac{1}{\omega^2 + a^2}$", False, r"No. That is the common denominator of $M$ and $N$; the numerators contribute $\sqrt{a^2 + \omega^2}$."),
        (r"$\dfrac{1}{\omega - a}$", False, r"No. That mixes the real exponential response $1/(s - a)$ with an oscillation; the frequency enters as $i\omega$."),
        (r"$1$, because the input has amplitude $1$.", False, r"No. The system changes the amplitude; $G = 1$ only when $\omega^2 + a^2 = 1$.")]),
    q("q-complex", r"Why may we solve $y' = ay + e^{i\omega t}$ and take the real part to answer $y' = ay + \cos\omega t$?", [
        (r"The equation has real coefficients, so real and imaginary parts of a complex solution solve the equation with the real and imaginary parts of the input.", True, r"Right. Linearity with real $a$ keeps the two parts separate."),
        (r"Because complex numbers are always equal to their real parts.", False, r"No. A complex number has an imaginary part that is usually not zero."),
        (r"Because $\cos\omega t = e^{i\omega t}$.", False, r"No. $\cos\omega t$ is only the real part of $e^{i\omega t}$."),
        (r"It works for any equation, linear or not.", False, r"No. For nonlinear equations the real part of a solution is generally not a solution.")]),
    q("q-delta", r"What is $\int_{-\infty}^{\infty}\delta(t - 2)\,e^{3t}\,dt$?", [
        (r"$e^{6}$", True, r"Right. The shifted delta picks out the value of $e^{3t}$ at $t = 2$."),
        (r"$1$", False, r"No. That would be the integral of $\delta$ alone (or with $f(T) = 1$)."),
        (r"$e^{3}$", False, r"No. That is the value at $t = 1$; the delta acts at $t = 2$."),
        (r"$0$", False, r"No. The delta is zero away from $t = 2$, but its integral against $f$ is $f(2) \ne 0$.")]),
    q("q-if", r"For $y' = a(t)y + q(t)$, which integrating factor $M$ makes $(My)' = Mq$?", [
        (r"$M = e^{-\int_0^t a(\tau)\,d\tau}$", True, r"Right. It solves $M' = -aM$, which cancels the $y$ terms in $(My)' = My' + M'y$."),
        (r"$M = e^{+\int_0^t a(\tau)\,d\tau}$", False, r"No. That is the growth factor $1/M$; with it $(My)'$ would contain $2aMy$."),
        (r"$M = e^{-a(t)\,t}$", False, r"No. That is right only for constant $a$; for varying $a$ the exponent must be an integral."),
        (r"$M = q(t)$", False, r"No. The factor depends on $a$, not on the input.")]),
]

# ---------------------------------------------------------------- explorer

EXPLORER = {
    "a": {"min": -2, "max": 1, "step": 0.1, "default": -0.5},
    "y0": {"min": -2, "max": 2, "step": 0.1, "default": 1},
    "s": {"min": -2, "max": 1, "step": 0.1, "default": 0.5},
    "omega": {"min": 0.5, "max": 4, "step": 0.1, "default": 2},
    "T": {"min": 0, "max": 6, "step": 0.1, "default": 2},
    "amp": {"min": 0, "max": 2, "step": 0.1, "default": 1},
    "inputs": ["constant", "exp", "cos", "step", "delta"],
    "defaultInput": "cos",
    "tMax": 10,
    "presets": [
        {"id": "deposit", "label": "Constant deposit", "input": "constant", "a": -0.5, "y0": 0, "amp": 1,
         "note": "Authored: $y' = -0.5y + 1$ from $0$ rises to the steady state $q/(-a) = 2$."},
        {"id": "resonance", "label": "Resonance", "input": "exp", "a": 0.5, "s": 0.5, "y0": 0, "amp": 1,
         "note": "Section 3: $s = a$, so the very particular solution is $t\\,e^{at}$, with the resonant factor $t$."},
        {"id": "cosine", "label": "Cosine: gain and lag", "input": "cos", "a": -1, "omega": 1, "y0": 1, "amp": 1,
         "note": "Section 4 example: $G = 1/\\sqrt2$, $\\alpha = \\pi/4$; the transient $Ce^{-t}$ dies away."},
        {"id": "impulse", "label": "Impulse response", "input": "delta", "a": -0.5, "T": 2, "y0": 0, "amp": 1,
         "note": "Section 6: one unit at $T = 2$, then $e^{a(t-T)}$."},
        {"id": "step", "label": "Step response", "input": "step", "a": -1, "T": 2, "y0": 0, "amp": 1,
         "note": "Section 6 example: $1 - e^{-(t-2)}$ after the switch."},
        {"id": "growth", "label": "Growing system", "input": "cos", "a": 0.3, "omega": 2, "y0": 0, "amp": 1,
         "note": "With $a > 0$ the null solution grows, so the oscillation is never steady: the formula still holds."}
    ],
    "tutorContext": "The explorer solves y' = a y + q(t), y(0) = y0, on 0 <= t <= 10 with exact formulas: constant q = A gives y = y0 e^(at) + A(e^(at) - 1)/a (A t when a = 0); exponential A e^(st) gives y0 e^(at) + A(e^(st) - e^(at))/(s - a), or A t e^(at) at resonance |s - a| < 1e-9; cosine A cos(wt) gives the steady part A G cos(wt - alpha) with G = 1/sqrt(a^2 + w^2), alpha = atan2(w, -a), plus the null part chosen to match y0; step A H(t - T) gives A(e^(a(t - T)) - 1)/a after T; delta A delta(t - T) gives A e^(a(t - T)) after T (y jumps by A). It plots the null part y0 e^(at), the input-driven (very particular) part that starts at 0, and their sum, and lists the formula used. Saved state: input kind and the sliders a, y0, s, omega, T, amp."
}

COURSE = {
    "version": 1,
    "title": "First Order Linear Equations",
    "subtitle": "Unit 1 of a study companion to MIT Learn Differential Equations (Gilbert Strang and Cleve Moler), videos 1-10, with Strang's Differential Equations and Linear Algebra, Sections 1.1-1.6",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 1-10", "duration": "2:08:41",
              "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 1",
             "edition": "Wellesley-Cambridge Press, 2014 (Chapter 1, First Order Equations)",
             "onlineUrl": "",
             "pageNote": "Page references give the printed page and the page of the local PDF (printed page + 12). The book is not freely available online, so only a local copy can be opened."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide; examples marked authored are not from the lectures. They summarize MIT OpenCourseWare's Learn Differential Equations videos (Gilbert Strang and Cleve Moler, CC BY-NC-SA) and Strang's textbook; for the original wording, watch the videos and read the book. Captions, video and book text are not included in this guide.",
    "explorer": EXPLORER,
    "sections": SECTIONS,
    "quiz": QUIZ,
}

# The correct answer is written first above; place it at a fixed, varied position per question.
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
