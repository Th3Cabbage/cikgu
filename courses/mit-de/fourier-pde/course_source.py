"""Source of courses/mit-de/fourier-pde/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\fourier-pde\\course_source.py

Unit 10 of the MIT Learn Differential Equations companion: playlist videos 50-56 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Sections 7.3-7.4,
8.1, 8.3-8.4. All text is original, written for this guide; it paraphrases the lectures and the
book without quoting. Examples marked "authored" are not from the lectures. Book references give
printed pages; the local PDF page is printed + 12.
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
    (50, "E97SZm2ZrBo", "Boundary Conditions Replace Initial Conditions", "17:03"),
    (51, "-D4GDdxJrpg", "Laplace Equation", "13:17"),
    (52, "vA9dfINW4Rg", "Fourier Series", "16:36"),
    (53, "lL0oUZGMhXc", "Examples of Fourier Series", "13:56"),
    (54, "WWphCZkdByA", "Fourier Series Solution of Laplace's Equation", "14:04"),
    (55, "i8rnEl8O-r0", "Heat Equation", "10:48"),
    (56, "9TQCKWWAVjM", "Wave Equation", "15:14"),
]

SECTIONS = [
    {
        "nav": "Boundary value problems",
        "v": 50,
        "title": r"$-y'' = f(x)$ with $y(0) = y(1) = 0$",
        "summary": r"Boundary conditions at both ends replace initial conditions. For $-y'' = f$ on $0 \le x \le 1$ with fixed ends, $y = y_p + Cx + D$ and the two end values fix $C$ and $D$. A uniform load $f = 1$ gives the parabola $y = \tfrac12(x - x^2)$; a point load $\delta(x - a)$ gives two straight lines meeting at $a$, with the slope dropping by $1$.",
        "time": [0, 1023],
        "goals": [
            r"Solve $-y'' = f$ with $y(0) = y(1) = 0$.",
            r"Use the null solutions $Cx + D$ to meet both boundary conditions.",
            r"Solve the point-load problem $-y'' = \delta(x - a)$ by matching at $x = a$."
        ],
        "notes": [
            {"heading": "Two boundary conditions",
             "paragraphs": [
                 r"Second order equations need two conditions. In space (a bar, a string, a beam) they are naturally given at the two ends: $y(0) = 0$ and $y(1) = 0$. The null solutions of $-y'' = 0$ are $Cx + D$, so $y = y_p + Cx + D$."
             ]},
            {"heading": "Uniform load",
             "paragraphs": [
                 r"$f = 1$: $y_p = -\tfrac12x^2$. Then $y(0) = D = 0$ and $y(1) = -\tfrac12 + C = 0$, so $C = \tfrac12$ and $y = \tfrac12(x - x^2)$, a parabola that sags most in the middle, like a bar hanging between two supports."
             ]},
            {"heading": "Point load",
             "paragraphs": [
                 r"$f = \delta(x - a)$: away from $a$ there is no load, so $y$ is linear on each side. Fixed ends give $y = Cx$ on the left and $y = E(1 - x)$ on the right. Two conditions at $a$: $y$ is continuous, and integrating $-y'' = \delta$ across $a$ shows the slope drops by exactly $1$. Solving, $C = 1 - a$ and $E = a$:",
                 r"$y = (1 - a)x$ for $x \le a$, $\quad y = a(1 - x)$ for $x \ge a$. This is the Green's function: the response at $x$ to a unit load at $a$."
             ]}
        ],
        "keyIdeas": [
            r"$y = y_p + Cx + D$, two end conditions.",
            r"$f = 1$: $y = \tfrac12(x - x^2)$.",
            r"$\delta(x - a)$: slope drops by $1$ at $a$.",
            r"$y = (1-a)x$ then $a(1-x)$."
        ],
        "example": {
            "title": "A linearly increasing load (authored)",
            "problem": r"Solve $-y'' = x$ with $y(0) = y(1) = 0$.",
            "steps": [
                {"text": "Integrate twice.", "tex": r"y_p = -\tfrac16x^3"},
                {"text": "y(0) = D = 0 and y(1) = -1/6 + C = 0.", "tex": r"C = \tfrac16"},
                {"text": "Assemble.", "tex": r"y = \tfrac16(x - x^3)"}
            ],
            "answer": r"$y = (x - x^3)/6$, largest at $x = 1/\sqrt3$, to the right of centre where the load is heavier."
        },
        "sources": {
            "video": [vs(50, 0, "-y'' = f with y(0) = y(1) = 0"),
                      vs(50, 120, "Particular plus null solutions Cx + D"),
                      vs(50, 210, "f = 1: y = x/2 - x^2/2"),
                      vs(50, 330, "A bar hanging between supports"),
                      vs(50, 450, "Point load delta(x - a)"),
                      vs(50, 600, "Straight lines on each side"),
                      vs(50, 780, "Continuity and the slope jump"),
                      vs(50, 900, "Integrate across the delta")],
            "book": [bk(406, "Section 7.3: boundary conditions replace initial conditions")]
        },
        "tutorNotes": "Video 50. -y'' = f, y(0) = y(1) = 0, y = y_p + Cx + D. f = 1: y = (x - x^2)/2. f = delta(x - a): y = (1 - a)x for x <= a, a(1 - x) for x >= a; continuous, slope drops by 1 at a (Green's function)."
    },
    {
        "nav": "Laplace's equation",
        "v": 51,
        "title": r"$u_{xx} + u_{yy} = 0$: polynomials and $r^n\cos n\theta$",
        "summary": r"Laplace's equation has the solutions $1, x, y, x^2 - y^2, 2xy, x^3 - 3xy^2, \ldots$: the real and imaginary parts of $(x + iy)^n$. In polar coordinates these are $r^n\cos n\theta$ and $r^n\sin n\theta$, and combinations of them match boundary values on a circle.",
        "time": [0, 797],
        "goals": [
            r"Check that $x^2 - y^2$ and $2xy$ satisfy Laplace's equation.",
            r"Generate solutions from $(x + iy)^n$.",
            r"Write the general solution inside a circle with $r^n\cos n\theta$, $r^n\sin n\theta$."
        ],
        "notes": [
            {"heading": "Solutions you can guess",
             "paragraphs": [
                 r"$u_{xx} + u_{yy} = 0$ describes steady temperature, potential, or an ideal fluid. Degree $0$: $u = 1$. Degree $1$: $x$ and $y$. Degree $2$: $x^2$ fails ($u_{xx} = 2$), but $x^2 - y^2$ works ($2 - 2 = 0$), and so does $2xy$. Degree $3$: $x^3 - 3xy^2$ and $3x^2y - y^3$. Two new solutions at each degree."
             ]},
            {"heading": "The pattern",
             "paragraphs": [
                 r"$(x + iy)^2 = x^2 - y^2 + 2ixy$ and $(x + iy)^3 = x^3 - 3xy^2 + i(3x^2y - y^3)$: the real and imaginary parts of $(x + iy)^n$ always solve Laplace's equation. In polar form $x + iy = re^{i\theta}$, so $(x + iy)^n = r^ne^{in\theta}$, with real and imaginary parts $r^n\cos n\theta$ and $r^n\sin n\theta$."
             ]},
            {"heading": "Inside a circle",
             "paragraphs": [
                 r"Combine them: $u(r, \theta) = a_0 + \sum_{n\ge1}(a_nr^n\cos n\theta + b_nr^n\sin n\theta)$. On the boundary $r = 1$ this is a Fourier series in $\theta$; matching the given boundary values $u_0(\theta)$ is exactly the problem of finding Fourier coefficients (Sections 3 and 5). Example data: $u_0 = +1$ on the top half of the circle and $-1$ on the bottom half."
             ]}
        ],
        "keyIdeas": [
            r"$x^2 - y^2$, $2xy$, $x^3 - 3xy^2$, ...",
            r"$\operatorname{Re}$ and $\operatorname{Im}$ of $(x + iy)^n$.",
            r"Polar: $r^n\cos n\theta$, $r^n\sin n\theta$.",
            r"Boundary values on $r = 1$: a Fourier series."
        ],
        "example": {
            "title": "Harmonic or not (authored)",
            "problem": r"Which solve Laplace's equation: $e^x\cos y$, $x^2 + y^2$, $x^4 - 6x^2y^2 + y^4$?",
            "steps": [
                {"text": "e^x cos y: u_xx = e^x cos y, u_yy = -e^x cos y.", "tex": r"u_{xx} + u_{yy} = 0\ \checkmark\quad(\operatorname{Re}\,e^{x+iy})"},
                {"text": "x^2 + y^2: 2 + 2.", "tex": r"u_{xx} + u_{yy} = 4 \neq 0"},
                {"text": "x^4 - 6x^2y^2 + y^4 = Re (x + iy)^4.", "tex": r"(12x^2 - 12y^2) + (-12x^2 + 12y^2) = 0\ \checkmark"}
            ],
            "answer": r"$e^x\cos y$ and $x^4 - 6x^2y^2 + y^4$ are harmonic; $x^2 + y^2$ is not."
        },
        "sources": {
            "video": [vs(51, 0, "Laplace's equation with boundary values"),
                      vs(51, 60, "Solutions 1, x, y"),
                      vs(51, 120, "x^2 - y^2 and 2xy"),
                      vs(51, 150, "Pattern: (x + iy)^n"),
                      vs(51, 270, "Degree 3"),
                      vs(51, 420, "Polar form r^n cos n theta, r^n sin n theta"),
                      vs(51, 540, "Combination for a circle"),
                      vs(51, 660, "Boundary data +1 and -1")],
            "book": [bk(416, "Section 7.4: Laplace's equation and A^T A")]
        },
        "tutorNotes": "Video 51. u_xx + u_yy = 0. Solutions 1, x, y, x^2 - y^2, 2xy, x^3 - 3xy^2, 3x^2 y - y^3 = Re/Im (x + iy)^n = r^n cos(n theta), r^n sin(n theta). u = a0 + sum (a_n r^n cos n theta + b_n r^n sin n theta) inside the unit circle; boundary values -> Fourier coefficients."
    },
    {
        "nav": "Fourier series",
        "v": 52,
        "title": r"Fourier coefficients by orthogonality",
        "summary": r"$f(x) = a_0 + \sum(a_k\cos kx + b_k\sin kx)$ on $-\pi \le x \le \pi$. The cosines and sines are orthogonal, so multiplying by $\cos kx$ and integrating isolates one coefficient: $a_k = \tfrac1\pi\int f\cos kx\,dx$, $b_k = \tfrac1\pi\int f\sin kx\,dx$, $a_0 = \tfrac{1}{2\pi}\int f$ (the average). The delta function has $a_0 = \tfrac{1}{2\pi}$ and every $a_k = \tfrac1\pi$.",
        "time": [0, 996],
        "goals": [
            r"State the orthogonality of $\cos nx$ and $\cos kx$ on $[-\pi, \pi]$.",
            r"Derive the formulas for $a_0$, $a_k$, $b_k$.",
            r"Compute the Fourier series of $\delta(x)$."
        ],
        "notes": [
            {"heading": "Orthogonal functions",
             "paragraphs": [
                 r"For integers $n \neq k$, $\int_{-\pi}^{\pi}\cos nx\cos kx\,dx = 0$, and likewise for sines and for a sine against a cosine. This is the function version of perpendicular vectors: the integral of a product plays the role of the dot product $c_1d_1 + c_2d_2 + \cdots$. Each function has $\int\cos^2kx\,dx = \pi$ for $k \ge 1$ (and $\int 1\,dx = 2\pi$)."
             ]},
            {"heading": "The coefficient formulas",
             "paragraphs": [
                 r"Multiply $f(x) = a_0 + \sum(a_n\cos nx + b_n\sin nx)$ by $\cos kx$ and integrate from $-\pi$ to $\pi$. Every term but one integrates to zero, leaving $\int f\cos kx\,dx = \pi a_k$. So",
                 r"$a_k = \dfrac1\pi\displaystyle\int_{-\pi}^{\pi}f(x)\cos kx\,dx,\quad b_k = \dfrac1\pi\int_{-\pi}^{\pi}f(x)\sin kx\,dx,\quad a_0 = \dfrac{1}{2\pi}\int_{-\pi}^{\pi}f(x)\,dx.$",
                 r"In complex form, $f = \sum_{-\infty}^{\infty}c_ke^{ikx}$ with $c_k = \tfrac{1}{2\pi}\int f(x)e^{-ikx}\,dx$."
             ]},
            {"heading": "The delta function",
             "paragraphs": [
                 r"$\delta(x)$ is even, so all $b_k = 0$. The integrals pick out the value at $0$: $a_0 = \tfrac{1}{2\pi}$ and $a_k = \tfrac1\pi\cos 0 = \tfrac1\pi$. So $\delta(x) = \tfrac{1}{2\pi} + \tfrac1\pi(\cos x + \cos 2x + \cos 3x + \cdots)$. The coefficients do not decay at all: the delta function is as rough as possible.",
                 r"This equality holds in the sense of distributions, not point by point. The partial sums do not settle down to $0$ away from $x = 0$ (at $x = \pi$ they alternate between $\pm\tfrac{1}{2\pi}$). What does converge is the integral of the partial sums against any smooth periodic function $g$: it tends to $g(0)$, which is what $\delta$ means."
             ]}
        ],
        "keyIdeas": [
            r"$\int\cos nx\cos kx = 0$ for $n \neq k$.",
            r"$a_k = \tfrac1\pi\int f\cos kx$, $b_k = \tfrac1\pi\int f\sin kx$.",
            r"$a_0$ = average of $f$.",
            r"$\delta$: $a_0 = \tfrac{1}{2\pi}$, $a_k = \tfrac1\pi$, no decay."
        ],
        "example": {
            "title": "The sawtooth (authored)",
            "problem": r"Find the Fourier series of $f(x) = x$ on $-\pi < x < \pi$.",
            "steps": [
                {"text": "f is odd: all a_k = 0. Integrate by parts for b_k.", "tex": r"b_k = \frac1\pi\int_{-\pi}^{\pi}x\sin kx\,dx = \frac{2(-1)^{k+1}}{k}"},
                {"text": "Write the series.", "tex": r"x = 2\left(\sin x - \frac{\sin 2x}{2} + \frac{\sin 3x}{3} - \cdots\right)"},
                {"text": "The jump at x = pi makes the coefficients decay like 1/k.", "tex": r"|b_k| = 2/k"}
            ],
            "answer": r"$x = 2\sum(-1)^{k+1}\sin(kx)/k$ on $(-\pi, \pi)$."
        },
        "sources": {
            "video": [vs(52, 0, "Fourier series: cosines and sines"),
                      vs(52, 60, "Complex form c_k e^(ikx)"),
                      vs(52, 120, "Orthogonality of cosines"),
                      vs(52, 270, "Like a dot product of vectors"),
                      vs(52, 330, "Multiply by cos kx and integrate"),
                      vs(52, 480, "a_k, b_k, a_0 formulas"),
                      vs(52, 660, "Example: the delta function"),
                      vs(52, 780, "Coefficients 1/pi: no decay")],
            "book": [bk(434, "Section 8.1: Fourier series")]
        },
        "tutorNotes": "Video 52. f = a0 + sum (a_k cos kx + b_k sin kx) on [-pi, pi], or sum c_k e^(ikx). Orthogonality: integral cos nx cos kx = 0 (n != k), = pi (n = k >= 1). a_k = (1/pi) int f cos kx, b_k = (1/pi) int f sin kx, a0 = (1/2pi) int f (average), c_k = (1/2pi) int f e^(-ikx). delta(x) = 1/(2pi) + (1/pi)(cos x + cos 2x + ...) in the sense of distributions (partial sums do not converge pointwise; at x = pi they alternate +-1/(2pi))."
    },
    {
        "nav": "Square wave and ramp",
        "v": 53,
        "title": r"Square wave: $\tfrac4\pi(\sin x + \tfrac13\sin 3x + \cdots)$; ramp: $\tfrac1{k^2}$ decay",
        "summary": r"The odd square wave ($+1$ on $(0, \pi)$, $-1$ on $(-\pi, 0)$) has $b_k = \tfrac{4}{\pi k}$ for odd $k$. Integrating it gives the even ramp $|x|$, with coefficients that decay like $1/k^2$. Smoother functions have faster-decaying coefficients; differentiation multiplies $c_k$ by $ik$.",
        "time": [0, 836],
        "goals": [
            r"Compute the coefficients of the square wave.",
            r"Get the series of $|x|$ by integrating the square wave.",
            r"Relate smoothness to the decay of coefficients."
        ],
        "notes": [
            {"heading": "Square wave",
             "paragraphs": [
                 r"$SW(x)$ is odd, so only sines appear: $b_k = \tfrac2\pi\int_0^\pi\sin kx\,dx = \tfrac{2}{\pi k}(1 - \cos k\pi)$, which is $\tfrac{4}{\pi k}$ for odd $k$ and $0$ for even $k$:",
                 r"$SW(x) = \dfrac4\pi\left(\sin x + \dfrac{\sin 3x}{3} + \dfrac{\sin 5x}{5} + \cdots\right).$ Partial sums overshoot near each jump by about $9\%$ of the jump (the Gibbs phenomenon), however many terms are kept."
             ]},
            {"heading": "Integrate to a ramp",
             "paragraphs": [
                 r"The ramp $|x|$ has slope $SW(x)$. Integrating the series term by term turns $\sin kx$ into $-\cos kx/k$, so $|x| = \tfrac\pi2 - \tfrac4\pi\left(\cos x + \tfrac{\cos 3x}{9} + \tfrac{\cos 5x}{25} + \cdots\right)$. The constant $\tfrac\pi2$ is the average of $|x|$, added separately because integration does not produce it."
             ]},
            {"heading": "Smoothness and decay",
             "paragraphs": [
                 r"A jump gives coefficients like $1/k$ (square wave); a corner gives $1/k^2$ (ramp); the delta function gives no decay at all. In complex form, the derivative of $\sum c_ke^{ikx}$ is $\sum ikc_ke^{ikx}$: differentiation multiplies by $ik$ and makes coefficients larger, integration divides by $ik$. A shift $f(x - d)$ multiplies $c_k$ by $e^{-ikd}$."
             ]}
        ],
        "keyIdeas": [
            r"$SW = \tfrac4\pi\sum_{k\ \text{odd}}\sin kx/k$.",
            r"$|x| = \tfrac\pi2 - \tfrac4\pi\sum_{k\ \text{odd}}\cos kx/k^2$.",
            r"Jump: $1/k$; corner: $1/k^2$; delta: no decay.",
            r"$d/dx$: $c_k \to ikc_k$."
        ],
        "example": {
            "title": "A famous sum from the square wave (authored)",
            "problem": r"Evaluate the square wave series at $x = \pi/2$.",
            "steps": [
                {"text": "SW(pi/2) = 1; sin(k pi/2) = 1, -1, 1, ... for k = 1, 3, 5, ...", "tex": r"1 = \frac4\pi\left(1 - \frac13 + \frac15 - \frac17 + \cdots\right)"},
                {"text": "Rearrange.", "tex": r"1 - \frac13 + \frac15 - \cdots = \frac\pi4"},
                {"text": "From the ramp at x = 0 (|0| = 0) a second sum follows.", "tex": r"1 + \frac19 + \frac1{25} + \cdots = \frac{\pi^2}{8}"}
            ],
            "answer": r"Leibniz's series $\pi/4$ and the odd-square sum $\pi^2/8$."
        },
        "sources": {
            "video": [vs(53, 0, "The odd square wave"),
                      vs(53, 120, "b_k = (2/pi) integral of sin kx"),
                      vs(53, 210, "4/pi (sin x + sin 3x/3 + ...)"),
                      vs(53, 330, "Integrate to the ramp"),
                      vs(53, 450, "Constant pi/2 is the average"),
                      vs(53, 540, "Decay 1/k against 1/k^2"),
                      vs(53, 630, "Derivative multiplies by ik"),
                      vs(53, 720, "Shift f(x - d)")],
            "book": [bk(436, "Square wave and its integral"),
                     bk(438, "Smoothness and decay of coefficients")]
        },
        "tutorNotes": "Video 53. Square wave (odd, +1 on (0, pi)): b_k = 4/(pi k) for odd k, 0 even; SW = (4/pi)(sin x + sin 3x/3 + ...). Integrate: |x| = pi/2 - (4/pi)(cos x + cos 3x/9 + cos 5x/25 + ...). Decay 1/k (jump), 1/k^2 (corner), none (delta). d/dx multiplies c_k by ik; shift f(x - d) multiplies c_k by e^(-ikd). Gibbs overshoot ~9% of the jump."
    },
    {
        "nav": "Laplace on a disc",
        "v": 54,
        "title": r"Boundary data on a circle: the Poisson kernel",
        "summary": r"On the unit disc, boundary values $u(1, \theta) = \sum(a_n\cos n\theta + b_n\sin n\theta)$ extend inside as $u(r, \theta) = \sum r^n(a_n\cos n\theta + b_n\sin n\theta)$. For $u(1, \theta) = \delta(\theta)$ the sum is $\tfrac{1}{2\pi}\tfrac{1 - r^2}{1 + r^2 - 2r\cos\theta}$. The centre value is the average of the boundary values.",
        "time": [0, 844],
        "goals": [
            r"Extend a boundary Fourier series into the disc with factors $r^n$.",
            r"Sum the series for delta boundary data (geometric series).",
            r"Explain the mean value property and the maximum principle."
        ],
        "notes": [
            {"heading": "From the boundary inwards",
             "paragraphs": [
                 r"Each boundary term $\cos n\theta$ becomes the harmonic function $r^n\cos n\theta$, which equals $\cos n\theta$ at $r = 1$. So the Fourier coefficients of the boundary data are all that is needed: high frequencies are damped strongly inside by $r^n$."
             ]},
            {"heading": "A point source on the boundary",
             "paragraphs": [
                 r"Take $u(1, \theta) = \delta(\theta)$. Section 3 gives $a_0 = \tfrac{1}{2\pi}$, $a_n = \tfrac1\pi$. Then $u = \tfrac{1}{2\pi} + \tfrac1\pi\sum r^n\cos n\theta = \tfrac{1}{2\pi}\operatorname{Re}\left(1 + 2\sum(re^{i\theta})^n\right)$, a geometric series. Its sum is",
                 r"$u(r, \theta) = \dfrac{1}{2\pi}\,\dfrac{1 - r^2}{1 + r^2 - 2r\cos\theta}.$ At $\theta = 0$ this is $\tfrac{1}{2\pi}\tfrac{1 + r}{1 - r}$, which blows up as $r \to 1$, as a point source should."
             ]},
            {"heading": "Averages and extremes",
             "paragraphs": [
                 r"At the centre $r = 0$ only $a_0$ survives: $u(0) = a_0$, the average of the boundary values. A harmonic function therefore has no maximum or minimum inside; its extremes are on the boundary. The discrete version is the five-point scheme: the value at a grid point is the average of its four neighbours."
             ]}
        ],
        "keyIdeas": [
            r"$\cos n\theta \to r^n\cos n\theta$ inside.",
            r"$\delta$ data: $u = \tfrac{1}{2\pi}\tfrac{1 - r^2}{1 + r^2 - 2r\cos\theta}$.",
            r"$u(0)$ = average on the boundary.",
            r"Maximum principle; five-point average."
        ],
        "example": {
            "title": "Boundary data cos^2 theta (authored)",
            "problem": r"Solve Laplace's equation in the unit disc with $u(1, \theta) = \cos^2\theta$.",
            "steps": [
                {"text": "Write the boundary data as a Fourier series.", "tex": r"\cos^2\theta = \tfrac12 + \tfrac12\cos 2\theta"},
                {"text": "Multiply each term by r^n.", "tex": r"u = \tfrac12 + \tfrac12r^2\cos 2\theta"},
                {"text": "In x, y: r^2 cos 2 theta = x^2 - y^2.", "tex": r"u = \tfrac12 + \tfrac12(x^2 - y^2)"}
            ],
            "answer": r"$u = \tfrac12(1 + x^2 - y^2)$; the centre value $\tfrac12$ is the average of $\cos^2\theta$."
        },
        "sources": {
            "video": [vs(54, 0, "Disc with u(1, theta) = delta(theta)"),
                      vs(54, 120, "Even data: cosines only"),
                      vs(54, 240, "Coefficients 1/(2pi) and 1/pi"),
                      vs(54, 330, "Multiply by r^n and sum"),
                      vs(54, 450, "Check on theta = 0"),
                      vs(54, 570, "u at the centre is the average"),
                      vs(54, 660, "The +1, -1 example"),
                      vs(54, 690, "Five-point scheme")],
            "book": [bk(418, "Laplace's equation in a circle"),
                     bk(436, "Fourier series on the boundary")]
        },
        "tutorNotes": "Video 54. Unit disc: u(r, theta) = a0 + sum r^n (a_n cos n theta + b_n sin n theta). delta boundary: a0 = 1/(2pi), a_n = 1/pi, u = (1/2pi)(1 - r^2)/(1 + r^2 - 2r cos theta) (Poisson kernel); at theta = 0: (1/2pi)(1 + r)/(1 - r). u(0) = boundary average; maximum principle; five-point scheme averages four neighbours."
    },
    {
        "nav": "Heat equation",
        "v": 55,
        "title": r"$u_t = u_{xx}$: each sine mode decays by $e^{-k^2\pi^2t}$",
        "summary": r"With $u = 0$ at $x = 0$ and $x = 1$, separation $u = e^{\lambda t}S(x)$ gives $S'' = \lambda S$, so $S = \sin k\pi x$ and $\lambda = -k^2\pi^2$. The solution is $u = \sum B_ke^{-k^2\pi^2t}\sin k\pi x$, with $B_k$ the sine coefficients of the initial temperature. High frequencies die out first.",
        "time": [0, 648],
        "goals": [
            r"Separate variables in the heat equation.",
            r"Find the eigenfunctions $\sin k\pi x$ and eigenvalues $-k^2\pi^2$.",
            r"Expand the initial condition $u(0, x) = 1$ in sines."
        ],
        "notes": [
            {"heading": "Separation of variables",
             "paragraphs": [
                 r"Look for $u(t, x) = e^{\lambda t}S(x)$. Then $u_t = \lambda u$ and $u_{xx} = e^{\lambda t}S''$, so $S'' = \lambda S$: an eigenvalue problem for $d^2/dx^2$. The boundary conditions $S(0) = S(1) = 0$ allow only $S = \sin k\pi x$, with $\lambda = -k^2\pi^2$."
             ]},
            {"heading": "The solution",
             "paragraphs": [
                 r"$u(t, x) = \sum_{k\ge1}B_ke^{-k^2\pi^2t}\sin k\pi x$, and at $t = 0$ this must equal the initial temperature: $u(0, x) = \sum B_k\sin k\pi x$, a sine series. Each mode decays at its own rate; the factor $e^{-k^2\pi^2t}$ kills high $k$ almost at once, so the temperature quickly looks like a single arch $B_1e^{-\pi^2t}\sin\pi x$."
             ]},
            {"heading": "A uniform start",
             "paragraphs": [
                 r"For $u(0, x) = 1$ (a hot bar whose ends are suddenly held at $0$), the sine coefficients on $[0, 1]$ are $B_k = 2\int_0^1\sin k\pi x\,dx = \tfrac{4}{k\pi}$ for odd $k$ and $0$ for even $k$, the square wave again."
             ]}
        ],
        "keyIdeas": [
            r"$u = e^{\lambda t}S(x)$: $S'' = \lambda S$.",
            r"$S = \sin k\pi x$, $\lambda = -k^2\pi^2$.",
            r"$u = \sum B_ke^{-k^2\pi^2t}\sin k\pi x$.",
            r"$u(0, x) = 1$: $B_k = \tfrac{4}{k\pi}$, $k$ odd."
        ],
        "example": {
            "title": "Two modes (authored)",
            "problem": r"Solve $u_t = u_{xx}$, $u(t, 0) = u(t, 1) = 0$, $u(0, x) = \sin\pi x + \tfrac12\sin 3\pi x$.",
            "steps": [
                {"text": "The initial condition is already a sine series: B1 = 1, B3 = 1/2.", "tex": r"u = e^{-\pi^2t}\sin\pi x + \tfrac12e^{-9\pi^2t}\sin 3\pi x"},
                {"text": "Compare the decay rates.", "tex": r"\frac{e^{-9\pi^2t}}{e^{-\pi^2t}} = e^{-8\pi^2t}"},
                {"text": "At t = 0.05 the ratio is already small.", "tex": r"e^{-0.4\pi^2} \approx 0.019"}
            ],
            "answer": r"$u = e^{-\pi^2t}\sin\pi x + \tfrac12e^{-9\pi^2t}\sin 3\pi x$; after $t = 0.05$ the third mode is below $2\%$ of the first."
        },
        "sources": {
            "video": [vs(55, 0, "Heat equation u_t = u_xx"),
                      vs(55, 60, "Try e^(lambda t) S(x)"),
                      vs(55, 120, "S = sin k pi x, lambda = -k^2 pi^2"),
                      vs(55, 180, "Sum of modes with B_k"),
                      vs(55, 300, "Boundary values zero"),
                      vs(55, 360, "Initial temperature u(0, x) = 1"),
                      vs(55, 570, "Decay picture")],
            "book": [bk(455, "Section 8.3: the heat equation")]
        },
        "tutorNotes": "Video 55. u_t = u_xx on [0, 1], u = 0 at both ends. u = e^(lambda t) S(x): S'' = lambda S, S = sin(k pi x), lambda = -k^2 pi^2. u = sum B_k e^(-k^2 pi^2 t) sin(k pi x), B_k from the sine series of u(0, x). u(0, x) = 1: B_k = 4/(k pi) for odd k. High frequencies decay fastest."
    },
    {
        "nav": "Wave equation",
        "v": 56,
        "title": r"$u_{tt} = c^2u_{xx}$: waves travel and strings vibrate",
        "summary": r"On a whole line the wave equation moves shapes: $u = f(x - ct) + g(x + ct)$, and a delta start splits into two half-deltas moving at speed $c$ (heat would spread it into a Gaussian instead). On a string with fixed ends, released from rest, $u = \sum d_n\cos(nct)\sin nx$ with $d_n$ the sine coefficients of the initial shape.",
        "time": [0, 914],
        "goals": [
            r"Contrast the heat equation (smoothing) and the wave equation (travelling).",
            r"Check d'Alembert's solution $f(x - ct) + g(x + ct)$.",
            r"Solve the plucked string with a sine series."
        ],
        "notes": [
            {"heading": "Heat against waves",
             "paragraphs": [
                 r"Start both equations from $u(0, x) = \delta(x)$ on the whole line. Heat spreads it instantly into the bell curve $\tfrac{1}{\sqrt{4\pi t}}e^{-x^2/4t}$. The wave equation (from rest) keeps the spike sharp and splits it: $\tfrac12\delta(x - ct) + \tfrac12\delta(x + ct)$, two pulses travelling left and right at speed $c$."
             ]},
            {"heading": "d'Alembert",
             "paragraphs": [
                 r"Any $u = f(x - ct) + g(x + ct)$ solves $u_{tt} = c^2u_{xx}$: each piece has $u_{tt} = c^2f''$ and $u_{xx} = f''$. The initial conditions give $f + g = u(0, x)$ and $-cf' + cg' = u_t(0, x)$, which determine $f$ and $g$. A string released from rest ($u_t = 0$) has $f = g = \tfrac12u(0, x)$."
             ]},
            {"heading": "A string with fixed ends",
             "paragraphs": [
                 r"On $0 \le x \le \pi$ with $u = 0$ at both ends, separation gives modes $\sin nx$ oscillating as $\cos nct$ and $\sin nct$. Released from rest, $u(t, x) = \sum d_n\cos(nct)\sin nx$, where $u(0, x) = \sum d_n\sin nx$. Unlike heat, nothing decays: every mode keeps its amplitude, and the frequencies $nc$ are the harmonics of the string."
             ]}
        ],
        "keyIdeas": [
            r"Heat: $\delta \to$ Gaussian; wave: $\delta \to$ two half-deltas.",
            r"$u = f(x - ct) + g(x + ct)$.",
            r"Fixed string from rest: $\sum d_n\cos(nct)\sin nx$.",
            r"Wave modes do not decay."
        ],
        "example": {
            "title": "A two-mode string (authored)",
            "problem": r"Solve $u_{tt} = u_{xx}$ on $[0, \pi]$, fixed ends, $u(0, x) = \sin x + \tfrac12\sin 3x$, $u_t(0, x) = 0$.",
            "steps": [
                {"text": "c = 1; the sine coefficients are d1 = 1, d3 = 1/2.", "tex": r"u = \cos t\,\sin x + \tfrac12\cos 3t\,\sin 3x"},
                {"text": "Check d'Alembert: cos(nt) sin(nx) = [sin n(x - t) + sin n(x + t)]/2.", "tex": r"u = \tfrac12\left[u_0(x - t) + u_0(x + t)\right]"},
                {"text": "After t = pi every mode has cos(n pi) = -1 (n odd).", "tex": r"u(\pi, x) = -u(0, x)"}
            ],
            "answer": r"$u = \cos t\sin x + \tfrac12\cos 3t\sin 3x$; at $t = \pi$ the string is the upside-down initial shape, and at $t = 2\pi$ it is back."
        },
        "sources": {
            "video": [vs(56, 0, "Wave equation u_tt = c^2 u_xx"),
                      vs(56, 210, "Delta start: heat gives a Gaussian"),
                      vs(56, 330, "Wave: two half deltas at x = +-ct"),
                      vs(56, 570, "Free line: f(x - ct) + g(x + ct)"),
                      vs(56, 660, "Initial position and velocity"),
                      vs(56, 690, "String on [0, pi], fixed ends"),
                      vs(56, 780, "Released from rest: cos(nct) sin nx"),
                      vs(56, 840, "Coefficients d_n from u(0, x)")],
            "book": [bk(463, "Section 8.4: the wave equation")]
        },
        "tutorNotes": "Video 56. u_tt = c^2 u_xx. Delta start: heat gives (1/sqrt(4 pi t)) e^(-x^2/4t); wave (from rest) gives (1/2)[delta(x - ct) + delta(x + ct)]. d'Alembert u = f(x - ct) + g(x + ct); from rest f = g = u(0, x)/2. String on [0, pi], fixed ends, from rest: u = sum d_n cos(nct) sin(nx), d_n = sine coefficients of u(0, x). No decay."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-bvp", r"What solves $-y'' = 1$ with $y(0) = y(1) = 0$?", [
        (r"$y = \tfrac12(x - x^2)$", True, r"Right. $y'' = -1$ and both ends are zero."),
        (r"$y = \tfrac12x^2$", False, r"No. $y(1) = \tfrac12 \neq 0$, and $-y'' = -1$."),
        (r"$y = x - x^2$", False, r"No. Then $-y'' = 2$."),
        (r"$y = \sin\pi x$", False, r"No. Then $-y'' = \pi^2\sin\pi x$, not $1$.")]),
    q("q-point", r"For $-y'' = \delta(x - a)$ with fixed ends, what happens to the slope at $x = a$?", [
        (r"It drops by exactly $1$.", True, r"Right. Integrating $-y''$ across $a$ gives $-(y'(a^+) - y'(a^-)) = 1$."),
        (r"It is continuous.", False, r"No. The point load makes a corner."),
        (r"It rises by $1$.", False, r"No. $-y'' = \delta$ means $y'$ decreases."),
        (r"The value $y(a)$ jumps by $1$.", False, r"No. $y$ is continuous; only its slope jumps.")]),
    q("q-harmonic", r"Which function solves $u_{xx} + u_{yy} = 0$?", [
        (r"$x^3 - 3xy^2$", True, r"Right. $u_{xx} = 6x$, $u_{yy} = -6x$; it is $\operatorname{Re}(x + iy)^3$."),
        (r"$x^2 + y^2$", False, r"No. $2 + 2 = 4$."),
        (r"$x^3 + y^3$", False, r"No. $6x + 6y \neq 0$."),
        (r"$xy^2$", False, r"No. $0 + 2x \neq 0$.")]),
    q("q-coef", r"How is the Fourier coefficient $a_k$ ($k \ge 1$) found on $[-\pi, \pi]$?", [
        (r"$a_k = \tfrac1\pi\int_{-\pi}^{\pi}f(x)\cos kx\,dx$", True, r"Right. Orthogonality removes every other term, and $\int\cos^2kx = \pi$."),
        (r"$a_k = \tfrac{1}{2\pi}\int f(x)\cos kx\,dx$", False, r"No. $\tfrac{1}{2\pi}$ is for $a_0$, where $\int 1\,dx = 2\pi$."),
        (r"$a_k = f(k)$", False, r"No. Coefficients come from integrals of $f$."),
        (r"$a_k = \int f(x)\sin kx\,dx$", False, r"No. Sines give $b_k$.")]),
    q("q-delta", r"What are the Fourier cosine coefficients $a_k$ ($k \ge 1$) of $\delta(x)$?", [
        (r"All equal to $\tfrac1\pi$", True, r"Right. $\tfrac1\pi\int\delta(x)\cos kx\,dx = \tfrac1\pi\cos 0$."),
        (r"$\tfrac{1}{\pi k}$", False, r"No. That decay would mean a smoother function."),
        (r"$0$", False, r"No. $\delta$ is even, so the sines vanish, not the cosines."),
        (r"$\tfrac{1}{2\pi}$", False, r"No. That is $a_0$, the average.")]),
    q("q-square", r"Which terms appear in the odd square wave's series?", [
        (r"$\sin kx$ for odd $k$, with coefficients $\tfrac{4}{\pi k}$", True, r"Right. $b_k = \tfrac{2}{\pi k}(1 - \cos k\pi)$."),
        (r"$\cos kx$ for all $k$", False, r"No. An odd function has no cosine terms."),
        (r"$\sin kx$ for even $k$", False, r"No. $1 - \cos k\pi = 0$ for even $k$."),
        (r"$\sin kx$ with coefficients $\tfrac{4}{\pi k^2}$", False, r"No. $1/k^2$ belongs to the ramp, which has no jump.")]),
    q("q-decay", r"Why do the ramp's coefficients decay faster than the square wave's?", [
        (r"The ramp has a corner but no jump; integrating divides coefficients by $k$.", True, r"Right. $1/k$ becomes $1/k^2$."),
        (r"The ramp is odd.", False, r"No. $|x|$ is even."),
        (r"Because the ramp has a larger average.", False, r"No. The average only sets $a_0$."),
        (r"They decay at the same rate.", False, r"No. $1/k$ against $1/k^2$.")]),
    q("q-disc", r"Inside the unit disc, what does the boundary term $\cos 3\theta$ become?", [
        (r"$r^3\cos 3\theta$", True, r"Right. It is harmonic and equals $\cos 3\theta$ at $r = 1$."),
        (r"$\cos 3\theta$ unchanged", False, r"No. $\cos 3\theta$ alone is not harmonic in the disc."),
        (r"$r^{-3}\cos 3\theta$", False, r"No. That blows up at the centre."),
        (r"$e^{-9r}\cos 3\theta$", False, r"No. That is not a solution of Laplace's equation.")]),
    q("q-heat", r"In $u = \sum B_ke^{-k^2\pi^2t}\sin k\pi x$, which modes survive longest?", [
        (r"Low $k$: $e^{-k^2\pi^2t}$ decays slowest for $k = 1$.", True, r"Right. The temperature soon looks like one arch $\sin\pi x$."),
        (r"High $k$", False, r"No. High frequencies decay fastest."),
        (r"All decay equally.", False, r"No. The rate is $k^2\pi^2$."),
        (r"None decay.", False, r"No. That is the wave equation's behaviour.")]),
    q("q-wave", r"How does the wave equation (from rest) treat a delta start on the whole line?", [
        (r"It splits into two half-deltas moving left and right at speed $c$.", True, r"Right. $u = \tfrac12[\delta(x - ct) + \delta(x + ct)]$."),
        (r"It spreads into a Gaussian.", False, r"No. That is the heat equation."),
        (r"It stays at $x = 0$ and oscillates.", False, r"No. Waves travel."),
        (r"It decays to zero everywhere.", False, r"No. The wave equation conserves energy.")]),
]

EXPLORER = {
    "modes": [
        {"id": "series", "label": "Fourier partial sums"},
        {"id": "heat", "label": "Heat equation on [0, 1]"},
        {"id": "wave", "label": "Plucked string on [0, π]"}
    ],
    "defaultMode": "series",
    "functions": [
        {"id": "square", "label": "Square wave"},
        {"id": "ramp", "label": "Ramp |x|"},
        {"id": "saw", "label": "Sawtooth x"},
        {"id": "delta", "label": "Delta δ(x)"}
    ],
    "N": {"min": 1, "max": 60, "step": 1, "default": 5},
    "heatStarts": [
        {"id": "one", "label": "u(0, x) = 1"},
        {"id": "tent", "label": "Tent peak at 1/2"},
        {"id": "two", "label": "sin πx + ½ sin 3πx"}
    ],
    "t": {"min": 0, "max": 0.3, "step": 0.002, "default": 0.01},
    "pluck": {"min": 0.1, "max": 3.04, "step": 0.02, "default": 1.5708},
    "tw": {"min": 0, "max": 6.2832, "step": 0.02, "default": 0},
    "presets": [
        {"id": "sq5", "label": "Square wave, 5 terms", "mode": "series", "fn": "square", "N": 5,
         "note": "Section 4: $\\tfrac4\\pi(\\sin x + \\tfrac13\\sin 3x + \\tfrac15\\sin 5x)$; watch the overshoot near the jumps."},
        {"id": "gibbs", "label": "Gibbs with 59 terms", "mode": "series", "fn": "square", "N": 59,
         "note": "The overshoot stays near $9\\%$ of the jump."},
        {"id": "ramp", "label": "Ramp, 5 terms", "mode": "series", "fn": "ramp", "N": 5,
         "note": "Section 4: $1/k^2$ coefficients converge much faster."},
        {"id": "delta", "label": "Delta, 20 terms", "mode": "series", "fn": "delta", "N": 20,
         "note": "Section 3: coefficients do not decay; partial sums spike at $0$ and keep oscillating elsewhere. The series converges to $\\delta$ only as a distribution (in integrals against smooth functions)."},
        {"id": "hot", "label": "Hot bar", "mode": "heat", "start": "one", "t": 0.01,
         "note": "Section 6: $B_k = \\tfrac{4}{k\\pi}$ for odd $k$."},
        {"id": "pluck", "label": "Pluck at the middle", "mode": "wave", "pluck": 1.5708, "tw": 0.8,
         "note": "Section 7: $d_n = \\tfrac{8}{\\pi^2 n^2}\\sin\\tfrac{n\\pi}{2}$ for height $1$."}
    ],
    "tutorContext": "Three modes. Fourier partial sums on [-pi, pi]: square wave (b_k = 4/(pi k), odd k), ramp |x| (a0 = pi/2, a_k = -4/(pi k^2), odd k), sawtooth x (b_k = 2(-1)^(k+1)/k), delta (a0 = 1/(2pi), a_k = 1/pi; its partial sums do not converge pointwise, only as a distribution, i.e. integrals against smooth periodic functions tend to the value at 0); it plots f and S_N for N terms (N = 1..60), a bar chart of |coefficients| on a log scale, and the maximum overshoot near a jump (Gibbs, about 9% of the jump). Heat: u_t = u_xx on [0, 1] with zero ends; initial conditions 1 (B_k = 4/(k pi), odd k), a tent with peak 1 at x = 1/2 (B_k = 8 sin(k pi/2)/(k pi)^2), or sin(pi x) + sin(3 pi x)/2; u(t, x) = sum B_k e^(-k^2 pi^2 t) sin(k pi x) with 60 modes, time slider. Wave: string on [0, pi], c = 1, released from rest from a pluck of height 1 at x = p: d_n = 2 sin(n p) / (n^2 p (pi - p)); u = sum d_n cos(n t) sin(n x) with 80 modes, compared with d'Alembert's (u0(x - t) + u0(x + t))/2 using the odd 2 pi periodic extension."
}

COURSE = {
    "version": 1,
    "title": "Boundary Problems, Fourier Series and PDEs",
    "subtitle": "Unit 10 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 50-56, with Strang's Differential Equations and Linear Algebra, Sections 7.3-7.4, 8.1, 8.3-8.4",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 50-56", "duration": "1:40:58", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 7-8",
             "edition": "Wellesley-Cambridge Press, 2014 (Sections 7.3-7.4, 8.1, 8.3-8.4)", "onlineUrl": "",
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
