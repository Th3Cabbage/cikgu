"""Source of courses/mit-de/second-order/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\second-order\\course_source.py

Unit 3 of the MIT Learn Differential Equations companion: playlist videos 14-19 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Sections 2.1-2.4.
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
    (14, "xCCeV-glFdM", "Second Order Equations", "19:20"),
    (15, "zkFZY6esNOU", "Forced Harmonic Motion", "15:32"),
    (16, "zqks_JcU0cM", "Unforced Damped Motion", "14:04"),
    (17, "PoHO4PZtW78", "Impulse Response and Step Response", "16:02"),
    (18, "o93axeQJqJ8", "Exponential Response - Possible Resonance", "12:20"),
    (19, "SMQPt7t0bHk", "Second Order Equations with Damping", "13:14"),
]

SECTIONS = [
    {
        "nav": "Free harmonic motion",
        "v": 14,
        "title": r"Free oscillation: $my'' + ky = 0$",
        "summary": r"A mass on a spring with no friction oscillates forever at the natural frequency $\omega_n = \sqrt{k/m}$. Two initial conditions fix the two constants: $y = y(0)\cos\omega_n t + \dfrac{y'(0)}{\omega_n}\sin\omega_n t$.",
        "time": [0, 1160],
        "goals": [
            r"Explain why a second order equation needs two initial conditions.",
            r"Find the null solutions $\cos\omega_n t$ and $\sin\omega_n t$ of $my'' + ky = 0$.",
            r"Match $c_1$ and $c_2$ to $y(0)$ and $y'(0)$, and write the answer as $R\cos(\omega_n t - \alpha)$.",
            r"Relate $\omega$ (radians per second), frequency $f = \omega/2\pi$ (hertz) and period $T = 2\pi/\omega$."
        ],
        "notes": [
            {"heading": "Two derivatives, two conditions",
             "paragraphs": [
                 r"Newton's law $F = ma$ makes acceleration $y''$ the natural unknown in mechanics. A second order equation $Ay'' + By' + Cy = f(t)$ has two null solutions, so its complete solution $y = y_p + c_1y_1 + c_2y_2$ has two constants. They come from two initial conditions: the starting position $y(0)$ and the starting velocity $y'(0)$.",
                 r"In this unit the coefficients are constants: $A = m$ (mass), $B = b$ (damping) and $C = k$ (spring constant)."
             ]},
            {"heading": "No damping, no force",
             "paragraphs": [
                 r"With $B = 0$ and $f = 0$, $my'' + ky = 0$ says the spring force $-ky$ is the only force. Divide by $m$: $y'' + \omega_n^2 y = 0$ with $\omega_n^2 = k/m$. We need functions whose second derivative is $-\omega_n^2$ times themselves: $\cos\omega_n t$ and $\sin\omega_n t$.",
                 r"Then $y = c_1\cos\omega_n t + c_2\sin\omega_n t$. At $t = 0$ the cosine is $1$ and the sine is $0$, so $c_1 = y(0)$. The derivative at $0$ is $c_2\omega_n$, so $c_2 = y'(0)/\omega_n$."
             ]},
            {"heading": "One cosine with a phase",
             "paragraphs": [
                 r"A sum of a cosine and a sine with the same frequency is one shifted cosine: $c_1\cos\omega t + c_2\sin\omega t = R\cos(\omega t - \alpha)$ with $R = \sqrt{c_1^2 + c_2^2}$ and $\tan\alpha = c_2/c_1$. The amplitude $R$ never changes: energy (kinetic plus potential) is conserved when there is no friction.",
                 r"Units matter. $\omega$ is in radians per second; the frequency $f = \omega/2\pi$ counts full cycles per second (hertz); the period is $T = 2\pi/\omega = 1/f$."
             ]},
            {"heading": "The exponential form",
             "paragraphs": [
                 r"Euler's formula gives the same null solutions as $e^{i\omega_n t}$ and $e^{-i\omega_n t}$. Substituting $y = e^{st}$ gives $ms^2 + k = 0$, so $s = \pm i\omega_n$: pure imaginary exponents mean pure oscillation. Section 3 adds damping and the exponents get a negative real part."
             ]}
        ],
        "keyIdeas": [
            r"$\omega_n = \sqrt{k/m}$: the natural frequency.",
            r"$y = y(0)\cos\omega_n t + \dfrac{y'(0)}{\omega_n}\sin\omega_n t$.",
            r"$c_1\cos\omega t + c_2\sin\omega t = R\cos(\omega t - \alpha)$.",
            r"$f = \omega/2\pi$ hertz, $T = 2\pi/\omega$."
        ],
        "example": {
            "title": "Amplitude and phase (authored)",
            "problem": r"Solve $y'' + 4y = 0$ with $y(0) = 1$, $y'(0) = 2$, and write the answer as $R\cos(2t - \alpha)$.",
            "steps": [
                {"text": "Here omega_n = 2. Then c1 = y(0) = 1 and c2 = y'(0)/omega_n = 1.", "tex": r"y = \cos 2t + \sin 2t"},
                {"text": "Amplitude and phase from c1 and c2.", "tex": r"R = \sqrt{1 + 1} = \sqrt2,\qquad \tan\alpha = 1 \;\Rightarrow\; \alpha = \tfrac{\pi}{4}"},
                {"text": "Period: one cycle takes 2 pi / omega.", "tex": r"T = \pi,\qquad f = \tfrac{1}{\pi}\ \text{Hz}"}
            ],
            "answer": r"$y = \sqrt2\cos(2t - \pi/4)$, period $\pi$."
        },
        "sources": {
            "video": [vs(14, 0, "Second order equations: two null solutions"),
                      vs(14, 120, "Two initial conditions y(0), y'(0)"),
                      vs(14, 240, "No damping: perpetual motion"),
                      vs(14, 300, "m y'' + k y = 0: cosine and sine"),
                      vs(14, 420, "Free harmonic motion"),
                      vs(14, 540, "Divide by m: omega_n squared = k/m"),
                      vs(14, 600, "c1 from y(0)"),
                      vs(14, 660, "c2 from the initial velocity"),
                      vs(14, 720, "Energy is constant"),
                      vs(14, 780, "Graph of cos omega t, the period"),
                      vs(14, 900, "Units: radians per second"),
                      vs(14, 1020, "Frequency in hertz"),
                      vs(14, 1080, "Exponential form with i omega_n t")],
            "book": [bk(73, "Section 2.1: second derivatives in science and engineering"),
                     bk(75, "Free harmonic motion; amplitude and phase")]
        },
        "tutorNotes": "Video 14. m y'' + k y = 0, omega_n = sqrt(k/m), y = c1 cos(omega_n t) + c2 sin(omega_n t), c1 = y(0), c2 = y'(0)/omega_n. R cos(omega t - alpha) with R = sqrt(c1^2 + c2^2), tan alpha = c2/c1. f = omega/(2 pi) Hz, T = 2 pi / omega. Exponential form e^(+-i omega_n t)."
    },
    {
        "nav": "Forced harmonic motion",
        "v": 15,
        "title": r"Forcing $\cos\omega t$ and the impulse response",
        "summary": r"Driving $my'' + ky = \cos\omega t$ gives the particular solution $Y\cos\omega t$ with $Y = \dfrac{1}{m(\omega_n^2 - \omega^2)}$, which explodes as $\omega \to \omega_n$ (resonance). A hammer blow $\delta(t)$ gives the impulse response $g(t) = \dfrac{\sin\omega_n t}{m\,\omega_n}$.",
        "time": [0, 932],
        "goals": [
            r"Find the particular solution of $my'' + ky = \cos\omega t$ by trying $Y\cos\omega t$.",
            r"Explain the frequency response $1/(m(\omega_n^2 - \omega^2))$ and resonance $\omega = \omega_n$.",
            r"Turn $my'' + ky = \delta(t)$ into a null problem with $g(0) = 0$, $g'(0) = 1/m$, and solve it."
        ],
        "notes": [
            {"heading": "Try a cosine",
             "paragraphs": [
                 r"The input $\cos\omega t$ has a frequency $\omega$ set from outside; the spring has its own natural frequency $\omega_n$. Try $y_p = Y\cos\omega t$. Two derivatives give $-\omega^2 Y\cos\omega t$, and there is no $y'$ term to bring in a sine, so cosines alone balance: $-m\omega^2 Y + kY = 1$.",
                 r"Hence $Y = \dfrac{1}{k - m\omega^2} = \dfrac{1}{m(\omega_n^2 - \omega^2)}$ using $k = m\omega_n^2$. This number, as a function of $\omega$, is the frequency response."
             ]},
            {"heading": "Complete solution and resonance",
             "paragraphs": [
                 r"$y = Y\cos\omega t + c_1\cos\omega_n t + c_2\sin\omega_n t$: two frequencies together. The constants come from $y(0)$ and $y'(0)$, not from $Y$. Starting from rest, $y = Y(\cos\omega t - \cos\omega_n t)$.",
                 r"When $\omega$ is close to $\omega_n$ the denominator $\omega_n^2 - \omega^2$ is small and $Y$ is large: the system is pushed at almost its own rhythm. At $\omega = \omega_n$ the formula breaks down; that case, resonance, needs an extra factor $t$ (Section 5)."
             ]},
            {"heading": "A sudden blow",
             "paragraphs": [
                 r"$my'' + ky = \delta(t)$ means an impulse at $t = 0$, starting from rest. For $t > 0$ there is no force, so $g$ is a null solution. The delta function changes the momentum $mg'$ by $1$ at the instant $t = 0$: the problem is the same as $mg'' + kg = 0$ with $g(0) = 0$ and $g'(0) = 1/m$.",
                 r"Using Section 1 with $c_1 = 0$, $c_2 = (1/m)/\omega_n$: $g(t) = \dfrac{\sin\omega_n t}{m\,\omega_n}$. This impulse response returns in Section 4 and in the Laplace transform unit."
             ]}
        ],
        "keyIdeas": [
            r"$y_p = \dfrac{\cos\omega t}{m(\omega_n^2 - \omega^2)}$.",
            r"Resonance: $\omega = \omega_n$.",
            r"$\delta(t)$ input $\Leftrightarrow$ $g(0) = 0$, $g'(0) = 1/m$.",
            r"$g = \sin(\omega_n t)/(m\,\omega_n)$."
        ],
        "example": {
            "title": "Two frequencies from rest (authored)",
            "problem": r"Solve $y'' + 4y = \cos t$ with $y(0) = y'(0) = 0$.",
            "steps": [
                {"text": "m = 1, omega_n = 2, omega = 1.", "tex": r"Y = \frac{1}{4 - 1} = \frac13"},
                {"text": "Null part must cancel y(0) and keep y'(0) = 0.", "tex": r"c_1 = -\tfrac13,\quad c_2 = 0"},
                {"text": "Add them.", "tex": r"y = \tfrac13\left(\cos t - \cos 2t\right)"}
            ],
            "answer": r"$y = (\cos t - \cos 2t)/3$: the driving frequency $1$ and the natural frequency $2$ together."
        },
        "sources": {
            "video": [vs(15, 0, "Forced motion, constant coefficients"),
                      vs(15, 60, "omega_n = omega is resonance"),
                      vs(15, 120, "Cosine on the right side"),
                      vs(15, 180, "Input and response"),
                      vs(15, 240, "-omega^2 m Y + k Y = 1"),
                      vs(15, 300, "y = y_p + y_n"),
                      vs(15, 360, "Frequency response 1/(m(omega_n^2 - omega^2))"),
                      vs(15, 420, "Forcing near the natural frequency"),
                      vs(15, 480, "C1 and C2 from initial conditions"),
                      vs(15, 540, "Impulse: m y'' + k y = delta"),
                      vs(15, 660, "Impulse response g(t)"),
                      vs(15, 720, "Start from rest"),
                      vs(15, 780, "g = sin(omega_n t)/(m omega_n)")],
            "book": [bk(75, "Section 2.1: forced oscillation"),
                     bk(78, "Impulse response = fundamental solution")]
        },
        "tutorNotes": "Video 15. m y'' + k y = cos(omega t): y_p = Y cos(omega t), Y = 1/(k - m omega^2) = 1/(m(omega_n^2 - omega^2)). Resonance at omega = omega_n. y = y_p + c1 cos(omega_n t) + c2 sin(omega_n t). m y'' + k y = delta(t) from rest: g(0) = 0, g'(0) = 1/m, g = sin(omega_n t)/(m omega_n)."
    },
    {
        "nav": "Unforced damped motion",
        "v": 16,
        "title": r"Damping: the roots of $As^2 + Bs + C = 0$",
        "summary": r"With damping, $y = e^{st}$ gives $As^2 + Bs + C = 0$. The sign of $B^2 - 4AC$ sorts the motion: overdamped (two negative real roots), critically damped (a double root, solutions $e^{st}$ and $te^{st}$), underdamped (complex roots $-B/2A \pm i\omega_d$, a decaying oscillation).",
        "time": [0, 844],
        "goals": [
            r"Substitute $y = e^{st}$ and get the characteristic equation $As^2 + Bs + C = 0$.",
            r"Classify the four cases by $B$ and $B^2 - 4AC$.",
            r"Write the null solutions in each case, including $te^{st}$ for a double root.",
            r"Read the roots from the graph of the parabola $As^2 + Bs + C$."
        ],
        "notes": [
            {"heading": "The characteristic equation",
             "paragraphs": [
                 r"Unforced means $f = 0$. Put $y = e^{st}$ into $Ay'' + By' + Cy = 0$: every term carries $e^{st}$, which is never zero, so $As^2 + Bs + C = 0$. The quadratic formula gives $s_{1,2} = \dfrac{-B \pm \sqrt{B^2 - 4AC}}{2A}$, and $y = c_1e^{s_1t} + c_2e^{s_2t}$.",
                 r"Two useful checks: $s_1 + s_2 = -B/A$ and $s_1s_2 = C/A = \omega_n^2$."
             ]},
            {"heading": "Four cases",
             "paragraphs": [
                 r"Undamped, $B = 0$: $s = \pm i\omega_n$, pure oscillation (Section 1).",
                 r"Underdamped, $B^2 < 4AC$: $s = -\dfrac{B}{2A} \pm i\omega_d$ with $\omega_d = \sqrt{\dfrac{C}{A} - \dfrac{B^2}{4A^2}}$. The solution $e^{-Bt/2A}(c_1\cos\omega_d t + c_2\sin\omega_d t)$ oscillates while it decays; damping also slows the oscillation, $\omega_d < \omega_n$.",
                 r"Critically damped, $B^2 = 4AC$: one double root $s = -B/2A$. The second solution is $te^{st}$.",
                 r"Overdamped, $B^2 > 4AC$: two different negative real roots, two decaying exponentials and no oscillation."
             ]},
            {"heading": "Roots from a parabola",
             "paragraphs": [
                 r"Strang graphs $As^2 + Bs + C$ against $s$. For $s^2 + 2s$ it crosses zero at $0$ and $-2$. Raise it by $1$: $s^2 + 2s + 1 = (s+1)^2$ just touches zero at $-1$, a double root. Raise it again: $s^2 + 2s + 2$ never reaches zero, and the roots $-1 \pm i$ are complex. Increasing $C$ (a stiffer spring) moves the motion from overdamped through critical to underdamped."
             ]},
            {"heading": "Damping ratio",
             "paragraphs": [
                 r"The case is decided by one dimensionless number, the damping ratio $\zeta = \dfrac{B}{\sqrt{4AC}}$: $\zeta = 0$ undamped, $\zeta < 1$ underdamped, $\zeta = 1$ critical, $\zeta > 1$ overdamped (Section 6)."
             ]}
        ],
        "keyIdeas": [
            r"$y = e^{st}$ $\Rightarrow$ $As^2 + Bs + C = 0$.",
            r"$B^2 < 4AC$: $s = -B/2A \pm i\omega_d$, decaying oscillation.",
            r"$B^2 = 4AC$: $e^{st}$ and $te^{st}$.",
            r"$B^2 > 4AC$: two real negative exponents."
        ],
        "example": {
            "title": "An underdamped spring (authored)",
            "problem": r"Solve $y'' + 2y' + 5y = 0$ with $y(0) = 1$, $y'(0) = 0$.",
            "steps": [
                {"text": "Characteristic equation.", "tex": r"s^2 + 2s + 5 = 0 \;\Rightarrow\; s = -1 \pm 2i"},
                {"text": "B^2 - 4AC = 4 - 20 < 0: underdamped, omega_d = 2.", "tex": r"y = e^{-t}\left(c_1\cos 2t + c_2\sin 2t\right)"},
                {"text": "y(0) = c1 = 1; y'(0) = -c1 + 2c2 = 0.", "tex": r"y = e^{-t}\left(\cos 2t + \tfrac12\sin 2t\right)"}
            ],
            "answer": r"$y = e^{-t}(\cos 2t + \tfrac12\sin 2t)$, oscillating at $\omega_d = 2$ inside the envelope $\pm\tfrac{\sqrt5}{2}e^{-t}$ (here $\omega_n = \sqrt5$). The decay factor is $e^{-t}$; the amplitude $\sqrt{1 + 1/4} = \sqrt5/2$ comes from the two coefficients."
        },
        "sources": {
            "video": [vs(16, 0, "Unforced, damped: null solutions"),
                      vs(16, 60, "Substitute y = e^(st)"),
                      vs(16, 120, "Quadratic formula for s1, s2"),
                      vs(16, 180, "No damping: oscillation forever"),
                      vs(16, 240, "Damping brings exponential decay"),
                      vs(16, 300, "Critical damping: equal roots"),
                      vs(16, 360, "Graph of A s^2 + B s + C"),
                      vs(16, 480, "(s + 1)^2: repeated root"),
                      vs(16, 540, "No real roots: complex s"),
                      vs(16, 600, "Underdamping"),
                      vs(16, 660, "The four possibilities"),
                      vs(16, 780, "Damping ratio")],
            "book": [bk(90, "Section 2.3: constant coefficients A, B, C"),
                     bk(96, "The four cases and their roots")]
        },
        "tutorNotes": "Video 16. A y'' + B y' + C y = 0, y = e^(st): A s^2 + B s + C = 0, s = (-B +- sqrt(B^2 - 4AC))/(2A). s1 + s2 = -B/A, s1 s2 = C/A. Cases: B = 0 undamped (+-i omega_n); B^2 < 4AC underdamped s = -B/2A +- i omega_d; B^2 = 4AC critical (e^(st), t e^(st)); B^2 > 4AC overdamped. Parabola s^2 + 2s, s^2 + 2s + 1, s^2 + 2s + 2 (roots -1 +- i)."
    },
    {
        "nav": "Impulse and step response",
        "v": 17,
        "title": r"Impulse response $g(t)$ and step response $r(t)$",
        "summary": r"For $y'' + By' + Cy$, the impulse response is $g = \dfrac{e^{s_1t} - e^{s_2t}}{s_1 - s_2}$ (from $g(0) = 0$, $g'(0) = 1$). The step response, the answer to a unit step from rest, is the integral of $g$: $r(t) = \dfrac{1}{C} + \dfrac{s_2e^{s_1t} - s_1e^{s_2t}}{C(s_1 - s_2)}$.",
        "time": [0, 962],
        "goals": [
            r"Solve $g'' + Bg' + Cg = \delta(t)$ by the equivalent conditions $g(0) = 0$, $g'(0) = 1$.",
            r"Specialise $g$ to the undamped, underdamped and critical cases.",
            r"Find the step response $r(t)$ and check that $r' = g$."
        ],
        "notes": [
            {"heading": "The impulse response",
             "paragraphs": [
                 r"With $A = 1$, the impulse $\delta(t)$ starts the system from rest with velocity $1$. So $g$ is the null solution with $g(0) = 0$ and $g'(0) = 1$. In $g = c_1e^{s_1t} + c_2e^{s_2t}$: $c_1 + c_2 = 0$ and $c_1s_1 + c_2s_2 = 1$, so $c_1 = -c_2 = 1/(s_1 - s_2)$:",
                 r"$g(t) = \dfrac{e^{s_1t} - e^{s_2t}}{s_1 - s_2}.$ This is a difference quotient, and that explains the special cases."
             ]},
            {"heading": "The special cases",
             "paragraphs": [
                 r"No damping: $s = \pm i\omega_n$ and $g = \dfrac{\sin\omega_n t}{\omega_n}$ (Section 2 with $m = 1$). Underdamped: $s = -\tfrac{B}{2} \pm i\omega_d$ and $g = e^{-Bt/2}\dfrac{\sin\omega_d t}{\omega_d}$. Critical damping: $s_2 \to s_1$, and the difference quotient becomes a derivative with respect to $s$: $g = te^{s_1t} = te^{-Bt/2}$."
             ]},
            {"heading": "The step response",
             "paragraphs": [
                 r"Now the input is a unit step $H(t)$, switched on at $t = 0$ from rest: $r'' + Br' + Cr = 1$ with $r(0) = r'(0) = 0$. A constant particular solution is $1/C$. The null part must cancel the starting value $1/C$ and keep the slope $0$. That gives",
                 r"$r(t) = \dfrac{1}{C} + \dfrac{s_2e^{s_1t} - s_1e^{s_2t}}{C\,(s_1 - s_2)}$, using $s_1s_2 = C$. In the lecture the board is written for $C = 1$, where the leading term is $1$.",
                 r"The step is the integral of the delta function, so the step response is the integral of the impulse response: $r(t) = \int_0^t g(s)\,ds$. With damping, $r(t)$ settles at $1/C$."
             ]}
        ],
        "keyIdeas": [
            r"$g(0) = 0$, $g'(0) = 1$.",
            r"$g = \dfrac{e^{s_1t} - e^{s_2t}}{s_1 - s_2}$.",
            r"Critical: $g = te^{-Bt/2}$.",
            r"$r = \int_0^t g$, settling at $1/C$."
        ],
        "example": {
            "title": "Overdamped responses (authored)",
            "problem": r"Find $g$ and $r$ for $y'' + 3y' + 2y$.",
            "steps": [
                {"text": "Roots of s^2 + 3s + 2 = (s + 1)(s + 2).", "tex": r"s_1 = -1,\quad s_2 = -2,\quad s_1 - s_2 = 1"},
                {"text": "Impulse response.", "tex": r"g(t) = e^{-t} - e^{-2t}"},
                {"text": "Step response: integrate g from 0 to t (or use the formula with C = 2).", "tex": r"r(t) = \tfrac12 - e^{-t} + \tfrac12 e^{-2t}"}
            ],
            "answer": r"$g = e^{-t} - e^{-2t}$ and $r = \tfrac12 - e^{-t} + \tfrac12e^{-2t}$; indeed $r' = g$ and $r \to 1/C = \tfrac12$."
        },
        "sources": {
            "video": [vs(17, 0, "Impulse and step response, second order"),
                      vs(17, 60, "Step response starts from rest"),
                      vs(17, 120, "Delta input: no initial conditions needed"),
                      vs(17, 180, "s^2 + B s + C = 0 gives s1, s2"),
                      vs(17, 240, "Initial slope one"),
                      vs(17, 300, "Compare the first order growth factor"),
                      vs(17, 360, "Pure oscillation case"),
                      vs(17, 420, "Underdamped: real and imaginary parts"),
                      vs(17, 480, "Damping slows the frequency"),
                      vs(17, 540, "Critical case"),
                      vs(17, 600, "Step response"),
                      vs(17, 660, "Particular solution plus null solutions"),
                      vs(17, 840, "Comments on r(t)"),
                      vs(17, 900, "Step response = integral of the impulse response")],
            "book": [bk(97, "Fundamental solution = growth factor = impulse response"),
                     bk(98, "Impulse response in the three cases")]
        },
        "tutorNotes": "Video 17. g'' + B g' + C g = delta: g(0) = 0, g'(0) = 1, g = (e^(s1 t) - e^(s2 t))/(s1 - s2). B = 0: sin(omega_n t)/omega_n. Underdamped: e^(-Bt/2) sin(omega_d t)/omega_d. Critical: t e^(-Bt/2). Step response r'' + B r' + C r = 1 from rest: r = 1/C + (s2 e^(s1 t) - s1 e^(s2 t))/(C (s1 - s2)); board written for C = 1. r = integral of g."
    },
    {
        "nav": "Exponential response and resonance",
        "v": 18,
        "title": r"Exponential input: $Y = 1/P(s)$ and resonance",
        "summary": r"For $P(D)y = e^{st}$, the particular solution is $y_p = e^{st}/P(s)$, where $P(s) = As^2 + Bs + C$ and $1/P(s)$ is the transfer function. If $s$ is a root of $P$ (resonance) the formula fails and $y_p = \dfrac{te^{st}}{P'(s)}$.",
        "time": [0, 740],
        "goals": [
            r"Find $Y = 1/P(s)$ by substituting $Ye^{st}$, for any order.",
            r"Recognise resonance: the input exponent equals a null exponent.",
            r"Derive $te^{st}/P'(s)$ by letting $s$ approach the root (l'Hôpital)."
        ],
        "notes": [
            {"heading": "The transfer function",
             "paragraphs": [
                 r"Write $D = d/dt$ and $P(D) = AD^2 + BD + C$; the same idea works for any degree $N$. Since $D e^{st} = se^{st}$, the input $e^{st}$ passes through $P(D)$ as multiplication by $P(s)$: $P(D)(Ye^{st}) = YP(s)e^{st}$. Matching $e^{st}$ gives $Y = 1/P(s)$, the transfer function. One division solves the problem."
             ]},
            {"heading": "Resonance",
             "paragraphs": [
                 r"The formula fails when $P(s) = 0$, that is, when $s$ is one of the null exponents $s_1, s_2$. Then $e^{st}$ already solves the null equation and cannot produce a nonzero right side. This is resonance: the input exponent hits a pole of $1/P$."
             ]},
            {"heading": "Finding the new solution",
             "paragraphs": [
                 r"Take $s$ close to $s_1$ and use the particular solution that starts like a null solution: $y = \dfrac{e^{st} - e^{s_1t}}{P(s)}$. It still solves $P(D)y = e^{st}$, because the subtracted term is a null solution. As $s \to s_1$ it is $0/0$. L'Hôpital's rule, differentiating top and bottom with respect to $s$, gives",
                 r"$y_p = \dfrac{te^{s_1t}}{P'(s_1)}$, and for a second order equation $P'(s) = 2As + B$. The extra factor $t$ is the signature of resonance. A double root ($P'(s_1) = 0$ too) brings $t^2$."
             ]}
        ],
        "keyIdeas": [
            r"$P(D)e^{st} = P(s)e^{st}$.",
            r"$y_p = e^{st}/P(s)$; $1/P(s)$ is the transfer function.",
            r"Resonance: $P(s) = 0$.",
            r"Then $y_p = te^{st}/P'(s)$."
        ],
        "example": {
            "title": "With and without resonance (authored)",
            "problem": r"Find particular solutions of $y'' + 3y' + 2y = e^{t}$ and $y'' + 3y' + 2y = e^{-t}$.",
            "steps": [
                {"text": "P(s) = s^2 + 3s + 2 = (s + 1)(s + 2).", "tex": r"P(1) = 6 \;\Rightarrow\; y_p = \tfrac16 e^{t}"},
                {"text": "For e^(-t): P(-1) = 0, resonance. P'(s) = 2s + 3.", "tex": r"P'(-1) = 1 \;\Rightarrow\; y_p = t\,e^{-t}"},
                {"text": "Check the resonant one.", "tex": r"(te^{-t})'' + 3(te^{-t})' + 2te^{-t} = e^{-t}"}
            ],
            "answer": r"$y_p = e^{t}/6$; at resonance $y_p = te^{-t}$."
        },
        "sources": {
            "video": [vs(18, 0, "Exponential forcing"),
                      vs(18, 60, "Try Y e^(st)"),
                      vs(18, 120, "Any degree: P(s)"),
                      vs(18, 180, "One thing can go wrong"),
                      vs(18, 240, "Resonance: forcing exponent is a null exponent"),
                      vs(18, 300, "When s equals s1"),
                      vs(18, 420, "Particular solution divided by P(s)"),
                      vs(18, 480, "Let s sneak up on s1"),
                      vs(18, 540, "Derivative over derivative: l'Hopital"),
                      vs(18, 600, "t e^(s1 t) over P'(s1)"),
                      vs(18, 660, "Summary: transfer function")],
            "book": [bk(103, "Section 2.4: forced oscillations and exponential response"),
                     bk(108, "Resonance: y_p = t e^(ct)/P'(c)")]
        },
        "tutorNotes": "Video 18. P(D) y = e^(st): y_p = e^(st)/P(s), transfer function 1/P(s), any order. Resonance when P(s) = 0 (s is a null exponent). y = (e^(st) - e^(s1 t))/P(s), l'Hopital as s -> s1: y_p = t e^(s1 t)/P'(s1), P'(s) = 2As + B. Double root gives t^2."
    },
    {
        "nav": "Damped cosine forcing",
        "v": 19,
        "title": r"Cosine forcing with damping: gain $G$ and phase $\alpha$",
        "summary": r"For $Ay'' + By' + Cy = \cos\omega t$, $y_p = M\cos\omega t + N\sin\omega t$ with $M = (C - A\omega^2)/D$, $N = B\omega/D$, $D = (C - A\omega^2)^2 + (B\omega)^2$. In polar form $y_p = G\cos(\omega t - \alpha)$ with gain $G = 1/\sqrt D$ and $\tan\alpha = B\omega/(C - A\omega^2)$.",
        "time": [0, 794],
        "goals": [
            r"Match cosine and sine terms to find $M$ and $N$.",
            r"Convert to the polar form $G\cos(\omega t - \alpha)$.",
            r"Use $\omega_n = \sqrt{C/A}$ and the damping ratio $\zeta = B/\sqrt{4AC}$."
        ],
        "notes": [
            {"heading": "Rectangular form",
             "paragraphs": [
                 r"Damping adds a $y'$ term, which turns cosines into sines, so the trial solution needs both: $y_p = M\cos\omega t + N\sin\omega t$. Substituting and matching the $\cos$ and $\sin$ terms gives two linear equations, $(C - A\omega^2)M + B\omega N = 1$ and $-B\omega M + (C - A\omega^2)N = 0$. Their solution:",
                 r"$M = \dfrac{C - A\omega^2}{D}, \qquad N = \dfrac{B\omega}{D}, \qquad D = (C - A\omega^2)^2 + (B\omega)^2.$"
             ]},
            {"heading": "Polar form",
             "paragraphs": [
                 r"One term is better than two: $M\cos\omega t + N\sin\omega t = G\cos(\omega t - \alpha)$ with $G = \sqrt{M^2 + N^2} = 1/\sqrt D$ and $\tan\alpha = N/M = B\omega/(C - A\omega^2)$. The gain $G$ says how much the amplitude is magnified; the phase lag $\alpha$ says how far the response trails the input.",
                 r"With $B > 0$ the denominator $D$ is never zero, so there is no true resonance. The gain has a peak at $\omega = \sqrt{C/A - B^2/(2A^2)}$, just below $\omega_n$, only when $B^2 < 2AC$. With stronger damping, $B^2 \ge 2AC$, the gain is largest at $\omega = 0$ and decreases as $\omega$ grows."
             ]},
            {"heading": "The lecture's example",
             "paragraphs": [
                 r"$y'' + y' + 2y = \cos t$: $C - A\omega^2 = 2 - 1 = 1$ and $B\omega = 1$, so $D = 2$ and $M = N = \tfrac12$. Then $G = 1/\sqrt2$ and $\alpha = \pi/4$: $y_p = \tfrac{1}{\sqrt2}\cos(t - \tfrac{\pi}{4})$."
             ]},
            {"heading": "Better letters",
             "paragraphs": [
                 r"Two combinations carry the physics: the natural frequency $\omega_n = \sqrt{C/A}$ and the damping ratio $\zeta = \dfrac{B}{\sqrt{4AC}}$, which has no units. Engineers write the equation as $y'' + 2\zeta\omega_n y' + \omega_n^2y = f/A$."
             ]}
        ],
        "keyIdeas": [
            r"$y_p = M\cos\omega t + N\sin\omega t$.",
            r"$D = (C - A\omega^2)^2 + (B\omega)^2$.",
            r"$G = 1/\sqrt D$, $\tan\alpha = \dfrac{B\omega}{C - A\omega^2}$.",
            r"$\omega_n = \sqrt{C/A}$, $\zeta = B/\sqrt{4AC}$."
        ],
        "example": {
            "title": "Gain and lag (authored)",
            "problem": r"Find $G$ and $\alpha$ for $y'' + 2y' + 2y = \cos t$.",
            "steps": [
                {"text": "C - A omega^2 = 1, B omega = 2.", "tex": r"D = 1^2 + 2^2 = 5"},
                {"text": "Rectangular coefficients.", "tex": r"M = \tfrac15,\qquad N = \tfrac25"},
                {"text": "Polar form.", "tex": r"G = \tfrac{1}{\sqrt5},\qquad \tan\alpha = 2,\ \ \alpha \approx 1.107"}
            ],
            "answer": r"$y_p = \tfrac{1}{\sqrt5}\cos(t - \alpha)$ with $\tan\alpha = 2$."
        },
        "sources": {
            "video": [vs(19, 0, "The number one example: cosine forcing with damping"),
                      vs(19, 60, "Substitute and match cos and sin"),
                      vs(19, 120, "M and N over D"),
                      vs(19, 180, "A better form of the solution"),
                      vs(19, 240, "Gain G and angle alpha"),
                      vs(19, 300, "tan alpha = N/M"),
                      vs(19, 360, "Example y'' + y' + 2y = cos t"),
                      vs(19, 420, "Rectangular form: one half and one half"),
                      vs(19, 480, "1/sqrt 2 times cos(t - pi/4)"),
                      vs(19, 540, "Better notation"),
                      vs(19, 600, "Mass, damping, spring constant"),
                      vs(19, 660, "Damping ratio B/sqrt(4mk)")],
            "book": [bk(104, "Section 2.4: real solutions from cos and sin"),
                     bk(106, "Gain G and phase alpha")]
        },
        "tutorNotes": "Video 19. A y'' + B y' + C y = cos(omega t): M = (C - A omega^2)/D, N = B omega/D, D = (C - A omega^2)^2 + (B omega)^2. G = 1/sqrt(D), tan alpha = B omega/(C - A omega^2). Example y'' + y' + 2y = cos t: D = 2, M = N = 1/2, G = 1/sqrt 2, alpha = pi/4. omega_n = sqrt(C/A), zeta = B/sqrt(4AC)."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-wn", r"A mass $m = 2$ on a spring with $k = 18$ and no damping oscillates at what natural frequency $\omega_n$?", [
        (r"$3$ radians per second", True, r"Right. $\omega_n = \sqrt{k/m} = \sqrt{9} = 3$."),
        (r"$9$ radians per second", False, r"No. $9$ is $\omega_n^2 = k/m$; take the square root."),
        (r"$\sqrt{36} = 6$", False, r"No. Divide $k$ by $m$, do not multiply."),
        (r"$3/(2\pi)$ radians per second", False, r"No. $3/(2\pi)$ is the frequency in hertz, cycles per second.")]),
    q("q-c2", r"For $y'' + \omega_n^2 y = 0$, what is the coefficient of $\sin\omega_n t$?", [
        (r"$y'(0)/\omega_n$", True, r"Right. The derivative of $c_2\sin\omega_n t$ at $0$ is $c_2\omega_n$, which must equal $y'(0)$."),
        (r"$y'(0)$", False, r"No. Differentiating the sine brings out a factor $\omega_n$."),
        (r"$y(0)$", False, r"No. $y(0)$ is the cosine coefficient."),
        (r"$\omega_n\,y'(0)$", False, r"No. You divide by $\omega_n$, not multiply.")]),
    q("q-forced", r"For $my'' + ky = \cos\omega t$ with $\omega \neq \omega_n$, what is the particular solution?", [
        (r"$\dfrac{\cos\omega t}{m(\omega_n^2 - \omega^2)}$", True, r"Right. $-m\omega^2Y + kY = 1$ and $k = m\omega_n^2$."),
        (r"$\dfrac{\cos\omega t}{m(\omega^2 - \omega_n^2)}$", False, r"No. The sign is reversed: $k - m\omega^2 = m(\omega_n^2 - \omega^2)$."),
        (r"$M\cos\omega t + N\sin\omega t$ with $N \neq 0$", False, r"No. Without a $y'$ term no sine is needed: $N = 0$."),
        (r"$\dfrac{\cos\omega_n t}{k}$", False, r"No. The response follows the driving frequency $\omega$.")]),
    q("q-impulse", r"Why is $my'' + ky = \delta(t)$ from rest the same as a null problem with $g(0) = 0$, $g'(0) = 1/m$?", [
        (r"The impulse changes the momentum $mg'$ by $1$ instantly, while the position has no time to move.", True, r"Right. Integrating the equation across $t = 0$ gives a jump of $1$ in $mg'$; afterwards there is no force."),
        (r"Because $\delta(0) = 1/m$.", False, r"No. The delta function is not a number at $0$; its integral is $1$."),
        (r"Because $g$ starts at $1/m$.", False, r"No. Position starts at $0$; it is the velocity that jumps."),
        (r"It is not; the delta adds a particular solution $1/k$.", False, r"No. $1/k$ would answer a constant force, a step.")]),
    q("q-cases", r"Which equation is critically damped?", [
        (r"$y'' + 4y' + 4y = 0$", True, r"Right. $B^2 - 4AC = 16 - 16 = 0$: double root $s = -2$."),
        (r"$y'' + 2y' + 5y = 0$", False, r"No. $4 - 20 < 0$: underdamped."),
        (r"$y'' + 5y' + 4y = 0$", False, r"No. $25 - 16 > 0$: overdamped, roots $-1$ and $-4$."),
        (r"$y'' + 4y = 0$", False, r"No. $B = 0$: undamped.")]),
    q("q-double", r"When $As^2 + Bs + C$ has a double root $s_1$, what is the second null solution?", [
        (r"$te^{s_1t}$", True, r"Right. A double root gives $e^{s_1t}$ and $te^{s_1t}$."),
        (r"$e^{2s_1t}$", False, r"No. $2s_1$ is not a root."),
        (r"$e^{-s_1t}$", False, r"No. $-s_1$ is not a root either."),
        (r"There is only one.", False, r"No. A second order equation always has two independent null solutions.")]),
    q("q-g", r"What is the impulse response of $y'' + 3y' + 2y$?", [
        (r"$e^{-t} - e^{-2t}$", True, r"Right. $s_1 = -1$, $s_2 = -2$, and $g = (e^{s_1t} - e^{s_2t})/(s_1 - s_2)$."),
        (r"$e^{-t} + e^{-2t}$", False, r"No. That starts at $g(0) = 2$, but $g(0)$ must be $0$."),
        (r"$\tfrac12 - e^{-t} + \tfrac12e^{-2t}$", False, r"No. That is the step response $r$, the integral of $g$."),
        (r"$te^{-t}$", False, r"No. That is for a double root.")]),
    q("q-step", r"With damping ($B > 0$, $C > 0$), what value does the step response of $y'' + By' + Cy = H(t)$ approach?", [
        (r"$1/C$", True, r"Right. The constant particular solution $1/C$ remains when the null part decays."),
        (r"$1$", False, r"No. That is only when $C = 1$, as on the lecture's board."),
        (r"$0$", False, r"No. The step keeps pushing; the impulse response goes to $0$."),
        (r"$1/B$", False, r"No. With $y' = y'' = 0$ the equation reads $Cy = 1$.")]),
    q("q-resonance", r"What is a particular solution of $y'' - y = e^{t}$?", [
        (r"$\tfrac12te^{t}$", True, r"Right. $P(s) = s^2 - 1$ vanishes at $s = 1$, and $P'(1) = 2$, so $y_p = te^t/2$."),
        (r"$\tfrac12e^{t}$", False, r"No. $e^t$ is a null solution, so it gives zero on the left side."),
        (r"$te^{t}$", False, r"No. Divide by $P'(1) = 2$."),
        (r"There is none.", False, r"No. Resonance changes the form to $te^{t}$; it does not prevent a solution.")]),
    q("q-gain", r"For $y'' + y' + 2y = \cos t$, what are the gain $G$ and lag $\alpha$?", [
        (r"$G = 1/\sqrt2$, $\alpha = \pi/4$", True, r"Right. $D = 1^2 + 1^2 = 2$, $M = N = \tfrac12$, and $\tan\alpha = 1$."),
        (r"$G = \tfrac12$, $\alpha = \pi/4$", False, r"No. $\tfrac12$ is $M$ (and $N$); $G = \sqrt{M^2 + N^2}$."),
        (r"$G = 1/\sqrt2$, $\alpha = 0$", False, r"No. Damping makes the response lag: $\tan\alpha = N/M = 1$."),
        (r"$G = 1$, $\alpha = \pi/2$", False, r"No. That would need $C - A\omega^2 = 0$.")]),
]

EXPLORER = {
    "inputs": [
        {"id": "none", "label": "No input (free motion)"},
        {"id": "cos", "label": "cos ωt"},
        {"id": "exp", "label": "e^(st)"},
        {"id": "step", "label": "Unit step"},
        {"id": "impulse", "label": "Impulse δ(t)"}
    ],
    "defaultInput": "none",
    "B": {"min": 0, "max": 5, "step": 0.05, "default": 0.5},
    "C": {"min": 0.25, "max": 9, "step": 0.05, "default": 4},
    "y0": {"min": -2, "max": 2, "step": 0.05, "default": 1},
    "v0": {"min": -3, "max": 3, "step": 0.05, "default": 0},
    "omega": {"min": 0.1, "max": 5, "step": 0.05, "default": 1},
    "s": {"min": -3, "max": 1, "step": 0.05, "default": -0.5},
    "tMax": 16,
    "presets": [
        {"id": "free", "label": "Free oscillation", "input": "none", "B": 0, "C": 4, "y0": 1, "v0": 2,
         "note": "Section 1 example: $y = \\sqrt2\\cos(2t - \\pi/4)$."},
        {"id": "beats", "label": "Two frequencies", "input": "cos", "B": 0, "C": 4, "omega": 1, "y0": 0, "v0": 0,
         "note": "Section 2 example: $(\\cos t - \\cos 2t)/3$ from rest."},
        {"id": "under", "label": "Underdamped", "input": "none", "B": 2, "C": 5, "y0": 1, "v0": 0,
         "note": "Section 3 example: roots $-1 \\pm 2i$."},
        {"id": "critical", "label": "Critical damping", "input": "none", "B": 4, "C": 4, "y0": 1, "v0": 0,
         "note": "Double root $-2$: $e^{-2t}$ and $te^{-2t}$."},
        {"id": "step", "label": "Step response", "input": "step", "B": 3, "C": 2, "y0": 0, "v0": 0,
         "note": "Section 4 example: $r = \\tfrac12 - e^{-t} + \\tfrac12e^{-2t}$."},
        {"id": "resonance", "label": "Resonance e^(−t)", "input": "exp", "B": 3, "C": 2, "s": -1, "y0": 0, "v0": 0,
         "note": "Section 5: $s = -1$ is a root, so $y_p = te^{-t}/P'(-1) = te^{-t}$."},
        {"id": "gain", "label": "Gain and lag", "input": "cos", "B": 1, "C": 2, "omega": 1, "y0": 0.5, "v0": 0.5,
         "note": "Section 6: $G = 1/\\sqrt2$, $\\alpha = \\pi/4$; this start is exactly on the steady oscillation."}
    ],
    "tutorContext": "The explorer solves y'' + B y' + C y = f(t) (A = 1) for 0 <= t <= 16 with y(0) = y0, y'(0) = v0, and f = 0, cos(omega t), e^(s t), the unit step H(t), or the impulse delta(t) (which adds 1 to y'(0)). It shows the roots s1, s2 of s^2 + B s + C in the complex plane with the damping case (undamped, underdamped, critical, overdamped), omega_n = sqrt(C), zeta = B/(2 sqrt C), the response y(t) with the particular part dashed, and for cos inputs the gain G = 1/sqrt(D), D = (C - omega^2)^2 + (B omega)^2, the lag alpha, and a gain curve G(omega). For e^(st) it uses Y = 1/P(s), or t e^(st)/P'(s) at resonance (P(s) = 0); at a double root with P'(s) = 0 it uses t^2 e^(st)/2. The step response settles at 1/C when B > 0."
}

COURSE = {
    "version": 1,
    "title": "Second Order Equations and Oscillation",
    "subtitle": "Unit 3 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 14-19, with Strang's Differential Equations and Linear Algebra, Sections 2.1-2.4",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 14-19", "duration": "1:30:32", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 2",
             "edition": "Wellesley-Cambridge Press, 2014 (Chapter 2, Sections 2.1-2.4)", "onlineUrl": "",
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
