"""Source of courses/mit-de/networks-and-methods/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\networks-and-methods\\course_source.py

Unit 4 of the MIT Learn Differential Equations companion: playlist videos 20-23 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Sections 2.5-2.6.
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
    (20, "6b9AW6QxXt0", "Electrical Networks: Voltages and Currents", "16:33"),
    (21, "mKYlNJhK_2o", "Method of Undetermined Coefficients", "16:32"),
    (22, "u_XsCvhzzbg", "An Example of Undetermined Coefficients", "15:49"),
    (23, "0f15AVSQ770", "Variation of Parameters", "19:22"),
]

SECTIONS = [
    {
        "nav": "RLC networks",
        "v": 20,
        "title": r"An RLC loop and its complex impedance $Z$",
        "summary": r"Kirchhoff's voltage law around a loop with resistor $R$, inductor $L$ and capacitor $C$ gives $LI'' + RI' + I/C = $ (derivative of the source). With the source $Ve^{i\omega t}$ the current is $I = \dfrac{V}{Z}e^{i\omega t}$, where $Z = R + i\left(\omega L - \dfrac{1}{\omega C}\right)$ is the complex impedance.",
        "time": [0, 993],
        "goals": [
            r"Write the loop equation from the three voltage drops $LI'$, $RI$ and $\frac1C\int I$.",
            r"Match $L, R, 1/C$ with mass, damping and spring constant $m, b, k$.",
            r"Find the impedance $Z$ and its size $|Z| = \sqrt{R^2 + (\omega L - 1/\omega C)^2}$.",
            r"Find the frequency where the loop resonates: $\omega L = 1/(\omega C)$."
        ],
        "notes": [
            {"heading": "Voltage drops around a loop",
             "paragraphs": [
                 r"Kirchhoff's voltage law: around a closed loop the voltage drops add up to the applied voltage. A resistor drops $RI$ (Ohm's law), an inductor $L\,dI/dt$, and a capacitor $Q/C$ where the charge $Q$ is the integral of the current. With a source $Ve^{i\omega t}$:",
                 r"$L\dfrac{dI}{dt} + RI + \dfrac{1}{C}\displaystyle\int I\,dt = Ve^{i\omega t}.$ Differentiating once removes the integral: $LI'' + RI' + \dfrac{1}{C}I = i\omega V e^{i\omega t}$."
             ]},
            {"heading": "The mechanical twin",
             "paragraphs": [
                 r"This is the spring equation of Unit 3 with $L \leftrightarrow m$, $R \leftrightarrow b$ and $1/C \leftrightarrow k$. Inductance resists changes in current as mass resists changes in velocity; resistance dissipates energy like friction; the capacitor stores energy like a spring. Early analog computers used exactly this match to solve mechanical problems with circuits."
             ]},
            {"heading": "Impedance",
             "paragraphs": [
                 r"Try $I = We^{i\omega t}$ in the integral form. The derivative gives $i\omega L$, the integral gives $1/(i\omega C)$, so $\left(i\omega L + R + \dfrac{1}{i\omega C}\right)W = V$. Since $1/i = -i$, the bracket is",
                 r"$Z = R + i\left(\omega L - \dfrac{1}{\omega C}\right), \qquad W = \dfrac{V}{Z}.$ The real part is resistance; the imaginary part, the reactance, comes from the inductor and the capacitor with opposite signs.",
                 r"The size is $|Z|^2 = R^2 + \left(\omega L - \dfrac{1}{\omega C}\right)^2$, a sum of squares (not a difference). The current amplitude is $|V|/|Z|$, and the current lags the voltage by the angle of $Z$."
             ]},
            {"heading": "Tuning and networks",
             "paragraphs": [
                 r"$|Z|$ is smallest, equal to $R$, when the reactance vanishes: $\omega L = 1/(\omega C)$, that is $\omega_0 = 1/\sqrt{LC}$. A radio is tuned by changing $C$ until $\omega_0$ matches the station. Real circuits have many loops and nodes; Kirchhoff's current law at nodes leads to matrices (incidence matrices, Unit 7)."
             ]}
        ],
        "keyIdeas": [
            r"$LI' + RI + \frac1C\int I = V e^{i\omega t}$.",
            r"$L, R, 1/C \leftrightarrow m, b, k$.",
            r"$Z = R + i(\omega L - 1/\omega C)$, $I = (V/Z)e^{i\omega t}$.",
            r"Resonance: $\omega_0 = 1/\sqrt{LC}$, $|Z| = R$."
        ],
        "example": {
            "title": "Impedance at two frequencies (authored, book values)",
            "problem": r"$R = 10$, $L = 0.1$, $C = 10^{-4}$. Find $\omega_0$, and $Z$ and $|Z|$ at $\omega = 100$.",
            "steps": [
                {"text": "Resonant frequency.", "tex": r"\omega_0 = \frac{1}{\sqrt{LC}} = \frac{1}{\sqrt{10^{-5}}} \approx 316.2"},
                {"text": "At omega = 100: omega L = 10 and 1/(omega C) = 100.", "tex": r"Z = 10 + i(10 - 100) = 10 - 90i"},
                {"text": "Size of Z.", "tex": r"|Z| = \sqrt{100 + 8100} = \sqrt{8200} \approx 90.6"}
            ],
            "answer": r"$\omega_0 \approx 316$; at $\omega = 100$ the capacitor dominates, $Z = 10 - 90i$, and the current is about $9$ times smaller than at resonance."
        },
        "sources": {
            "video": [vs(20, 0, "An RLC loop with a switch"),
                      vs(20, 120, "Kirchhoff's voltage law: L dI/dt + R I + (1/C) integral of I"),
                      vs(20, 240, "Differentiate to remove the integral"),
                      vs(20, 300, "Analogy with m, b, k"),
                      vs(20, 360, "Analog computers"),
                      vs(20, 390, "Try I = W e^(i omega t)"),
                      vs(20, 540, "Impedance Z"),
                      vs(20, 690, "|Z| squared, using 1/i = -i"),
                      vs(20, 810, "Many loops: Kirchhoff's current law")],
            "book": [bk(118, "Section 2.5: electrical networks and mechanical systems"),
                     bk(121, "Complex impedance")]
        },
        "tutorNotes": "Video 20. RLC loop: L I' + R I + (1/C) int I = V e^(i omega t); differentiate: L I'' + R I' + I/C = i omega V e^(i omega t). L, R, 1/C like m, b, k. I = W e^(i omega t): (i omega L + R + 1/(i omega C)) W = V, Z = R + i(omega L - 1/(omega C)), W = V/Z. |Z|^2 = R^2 + (omega L - 1/(omega C))^2. Resonance omega_0 = 1/sqrt(LC), |Z| = R."
    },
    {
        "nav": "Undetermined coefficients",
        "v": 21,
        "title": r"Undetermined coefficients: guess the form, find the numbers",
        "summary": r"For $Ay'' + By' + Cy = f(t)$ with a nice $f$ (exponentials, sines and cosines, polynomials and their products), $y_p$ has the same form as $f$ with unknown coefficients. Substitute and match terms. If $f$ contains a null solution (resonance), multiply the guess by $t$.",
        "time": [0, 992],
        "goals": [
            r"Name the right-hand sides for which the method works.",
            r"Choose the trial form for $t$, $\sin t$, $e^{st}$ and $t\sin t$.",
            r"Match coefficients to find $y_p$.",
            r"Recognise resonance and add the factor $t$."
        ],
        "notes": [
            {"heading": "Nice functions",
             "paragraphs": [
                 r"The method works when differentiating $f$ keeps it inside a small family: $e^{st}$ stays $e^{st}$; $\cos\omega t$ and $\sin\omega t$ turn into each other; a polynomial of degree $n$ stays a polynomial of degree at most $n$. Products of these also work. For other functions, such as $\sec t$ or $\ln t$, the guess never closes up, and variation of parameters (Section 4) is needed."
             ]},
            {"heading": "The trial forms",
             "paragraphs": [
                 r"$f = e^{st}$: try $Ye^{st}$, which gives $Y = 1/(As^2 + Bs + C)$ (Unit 3).",
                 r"$f = t$: try $y_p = a + bt$. For $y'' + y' + y = t$: $0 + b + (a + bt) = t$, so $b = 1$ and $a + b = 0$: $y_p = t - 1$.",
                 r"$f = \sin t$: the damping term mixes sines and cosines, so try $C_1\cos t + C_2\sin t$.",
                 r"$f = t\sin t$: try $(a + bt)\cos t + (c + dt)\sin t$: four coefficients from four matching equations."
             ]},
            {"heading": "Resonance",
             "paragraphs": [
                 r"If $f$ itself solves the null equation, the trial form gives zero on the left side and cannot match. Example: $y'' - y = e^t$, where $e^t$ is a null solution. Multiply the guess by $t$: try $Y\,te^{t}$. In general, multiply by $t^m$ where $m$ is how many times the exponent is a root of $As^2 + Bs + C$."
             ]}
        ],
        "keyIdeas": [
            r"Works for $e^{st}$, $\cos$, $\sin$, polynomials, products.",
            r"$f = t$: try $a + bt$.",
            r"$f = t\sin t$: $(a + bt)\cos t + (c + dt)\sin t$.",
            r"Resonance: multiply the guess by $t$."
        ],
        "example": {
            "title": "A quadratic input (authored)",
            "problem": r"Find $y_p$ for $y'' + y' + y = t^2$.",
            "steps": [
                {"text": "Try a + bt + ct^2: y'' = 2c, y' = b + 2ct.", "tex": r"2c + (b + 2ct) + (a + bt + ct^2) = t^2"},
                {"text": "Match t^2, then t, then constants.", "tex": r"c = 1,\qquad 2c + b = 0 \Rightarrow b = -2,\qquad 2c + b + a = 0 \Rightarrow a = 0"},
                {"text": "Assemble.", "tex": r"y_p = t^2 - 2t"}
            ],
            "answer": r"$y_p = t^2 - 2t$; check: $2 + (2t - 2) + (t^2 - 2t) = t^2$."
        },
        "sources": {
            "video": [vs(21, 0, "y'' + y' + y = f(t) with a nice function"),
                      vs(21, 60, "f = e^(st): try Y e^(st)"),
                      vs(21, 150, "f = t: try a + bt"),
                      vs(21, 240, "Match coefficients: y_p = t - 1"),
                      vs(21, 330, "f = sin t: cosine and sine"),
                      vs(21, 420, "Euler's formula link"),
                      vs(21, 450, "f = t sin t: four coefficients"),
                      vs(21, 720, "Resonance: try Y t e^t")],
            "book": [bk(130, "Section 2.6: the method of undetermined coefficients"),
                     bk(133, "Summary of the method")]
        },
        "tutorNotes": "Video 21. Undetermined coefficients for y'' + y' + y = f: f = e^(st) -> Y e^(st); f = t -> a + bt gives y_p = t - 1; f = sin t -> C1 cos t + C2 sin t; f = t sin t -> (a + bt) cos t + (c + dt) sin t. Resonance y'' - y = e^t -> try Y t e^t. Method works only for exponentials, sin/cos, polynomials and products."
    },
    {
        "nav": "A worked example",
        "v": 22,
        "title": r"$y'' - 3y' + 2y = 4t$ and its family",
        "summary": r"The null solutions are $e^t$ and $e^{2t}$. The input $4t$ gives $y_p = 3 + 2t$; $4t^2$ needs $a + bt + ct^2$; $e^{st}$ gives $e^{st}/(s^2 - 3s + 2)$, except at the resonant exponents $s = 1$ and $s = 2$, where $te^{st}$ appears.",
        "time": [0, 949],
        "goals": [
            r"Find the null solutions from $s^2 - 3s + 2 = (s-1)(s-2)$.",
            r"Solve for $y_p$ with a linear and a quadratic input.",
            r"Handle exponential and cosine inputs through $Y = 1/P(s)$, and resonance."
        ],
        "notes": [
            {"heading": "Linear equations, two routes",
             "paragraphs": [
                 r"Strang's big picture: nonlinear equations go to numerical methods (Unit 11). Linear equations with constant coefficients have formulas: either the integral with the impulse response (Section 4), or, for nice inputs, undetermined coefficients."
             ]},
            {"heading": "Null solutions and a polynomial input",
             "paragraphs": [
                 r"$s^2 - 3s + 2 = (s - 1)(s - 2)$ gives $y_n = c_1e^t + c_2e^{2t}$. For $f = 4t$ try $a + bt$: $0 - 3b + 2(a + bt) = 4t$. Matching $t$: $2b = 4$, so $b = 2$. Matching constants: $2a - 3b = 0$, so $a = 3$. Thus $y_p = 3 + 2t$.",
                 r"For $f = 4t^2$ the guess needs all lower powers: $a + bt + ct^2$, three coefficients."
             ]},
            {"heading": "Exponentials, cosines and resonance",
             "paragraphs": [
                 r"$f = e^{st}$ gives $y_p = e^{st}/(s^2 - 3s + 2)$. With $s = i\omega$ the real part answers $\cos\omega t$, and in real form the guess is $M\cos\omega t + N\sin\omega t$.",
                 r"At $s = 1$ or $s = 2$ the denominator is zero: the input is a null solution. Then the guess is $Y\,te^{st}$, and Unit 3 gives $Y = 1/P'(s)$ with $P'(s) = 2s - 3$.",
                 r"The list of nice inputs: $e^{st}$, $\cos\omega t$ and $\sin\omega t$, polynomials, and their products such as $te^{st}$ or $t\cos\omega t$ (whose guess $(a + bt)\cos\omega t + (c + dt)\sin\omega t$ has four coefficients)."
             ]}
        ],
        "keyIdeas": [
            r"$y_n = c_1e^t + c_2e^{2t}$.",
            r"$f = 4t$: $y_p = 3 + 2t$.",
            r"$f = e^{st}$: $y_p = e^{st}/(s^2 - 3s + 2)$.",
            r"$s = 1, 2$: resonance, $y_p = te^{st}/(2s - 3)$."
        ],
        "example": {
            "title": "Resonance at s = 2 (authored)",
            "problem": r"Find $y_p$ for $y'' - 3y' + 2y = e^{2t}$.",
            "steps": [
                {"text": "P(2) = 4 - 6 + 2 = 0: e^(2t) is a null solution.", "tex": r"\text{try } y_p = Y\,t\,e^{2t}"},
                {"text": "Unit 3's resonance formula with P'(s) = 2s - 3.", "tex": r"Y = \frac{1}{P'(2)} = \frac{1}{1} = 1"},
                {"text": "Check: (t e^(2t))' = (1 + 2t)e^(2t), (t e^(2t))'' = (4 + 4t)e^(2t).", "tex": r"(4 + 4t) - 3(1 + 2t) + 2t = 1"}
            ],
            "answer": r"$y_p = te^{2t}$."
        },
        "sources": {
            "video": [vs(22, 0, "Nonlinear goes numerical; linear has formulas"),
                      vs(22, 60, "y'' - 3y' + 2y = 4t: null solutions e^t, e^(2t)"),
                      vs(22, 120, "Try a + bt"),
                      vs(22, 180, "b = 2, a = 3"),
                      vs(22, 240, "f = 4t^2: a + bt + ct^2"),
                      vs(22, 270, "f = e^(st): Y = 1/(s^2 - 3s + 2)"),
                      vs(22, 360, "s = i omega gives cos and sin"),
                      vs(22, 450, "s = 1 or 2: resonance"),
                      vs(22, 510, "The nice functions"),
                      vs(22, 750, "t cos omega t: four coefficients"),
                      vs(22, 810, "Resonance with e^t: try Y t e^t")],
            "book": [bk(131, "Undetermined coefficients: examples"),
                     bk(132, "Resonance: the extra factor t")]
        },
        "tutorNotes": "Video 22. y'' - 3y' + 2y = 4t: null e^t, e^(2t); try a + bt: -3b + 2a + 2bt = 4t, b = 2, a = 3, y_p = 3 + 2t. 4t^2: a + bt + ct^2. e^(st): y_p = e^(st)/(s^2 - 3s + 2); s = i omega gives cos/sin. s = 1, 2 resonance: Y t e^(st), Y = 1/P'(s) = 1/(2s - 3). t cos(omega t): (a + bt) cos + (c + dt) sin."
    },
    {
        "nav": "Variation of parameters",
        "v": 23,
        "title": r"Variation of parameters: $y = c_1(t)y_1 + c_2(t)y_2$",
        "summary": r"Let the constants in the null solution vary. Requiring $c_1'y_1 + c_2'y_2 = 0$ and $c_1'y_1' + c_2'y_2' = f$ gives $c_1' = -y_2f/W$ and $c_2' = y_1f/W$, with the Wronskian $W = y_1y_2' - y_2y_1'$. For constant coefficients this is the integral $\int_0^t g(t - T)f(T)\,dT$ with the impulse response.",
        "time": [0, 1162],
        "goals": [
            r"Set up the two conditions on $c_1'$ and $c_2'$.",
            r"Solve them with the Wronskian.",
            r"Apply the method to an input the guessing method cannot handle.",
            r"See that, for constant coefficients, it reproduces $\int g(t - T)f(T)\,dT$."
        ],
        "notes": [
            {"heading": "Varying the constants",
             "paragraphs": [
                 r"Start from the null solutions $y_1, y_2$ of $y'' + B(t)y' + C(t)y = 0$ (here the leading coefficient is $1$). Look for $y = c_1(t)y_1 + c_2(t)y_2$. Its derivative has four terms; impose $c_1'y_1 + c_2'y_2 = 0$ so that $y' = c_1y_1' + c_2y_2'$. Differentiating again and using the null equations, the remaining condition is $c_1'y_1' + c_2'y_2' = f$."
             ]},
            {"heading": "The Wronskian",
             "paragraphs": [
                 r"Two linear equations for $c_1', c_2'$ with determinant $W = y_1y_2' - y_2y_1'$, the Wronskian. It is never zero when $y_1, y_2$ are independent. Cramer's rule:",
                 r"$c_1' = -\dfrac{y_2 f}{W}, \qquad c_2' = \dfrac{y_1 f}{W}, \qquad y_p = -y_1\displaystyle\int\frac{y_2f}{W}\,dt + y_2\int\frac{y_1f}{W}\,dt.$"
             ]},
            {"heading": "Constant coefficients: the impulse response again",
             "paragraphs": [
                 r"With distinct roots $s_1 \neq s_2$, take $y_1 = e^{s_1t}$ and $y_2 = e^{s_2t}$: $W = (s_2 - s_1)e^{(s_1 + s_2)t}$. Taking the integrals from $0$ to $t$, the exponentials combine into $e^{s_i(t - T)}$, and the answer is",
                 r"$y_p(t) = \displaystyle\int_0^t \frac{e^{s_2(t-T)} - e^{s_1(t-T)}}{s_2 - s_1}\,f(T)\,dT = \int_0^t g(t - T)\,f(T)\,dT.$",
                 r"With a double root $s_1 = s_2 = r$ that quotient is $0/0$ and the exponentials are not independent. The null solutions are then $e^{rt}$ and $te^{rt}$, with $W = e^{2rt}$, and the same computation gives $g(t) = te^{rt}$, the limit of the quotient as $s_2 \to s_1$.",
                 r"Each input $f(T)\,dT$ at time $T$ starts its own impulse response $g$, which runs for the time $t - T$. This is the second order version of the Unit 1 formula, and the convolution of Unit 5."
             ]}
        ],
        "keyIdeas": [
            r"$c_1'y_1 + c_2'y_2 = 0$, $c_1'y_1' + c_2'y_2' = f$.",
            r"$W = y_1y_2' - y_2y_1'$.",
            r"$c_1' = -y_2f/W$, $c_2' = y_1f/W$.",
            r"Constant coefficients: $y_p = \int_0^t g(t - T)f(T)\,dT$."
        ],
        "example": {
            "title": "An input with no good guess (authored)",
            "problem": r"Find $y_p$ for $y'' + y = \sec t$ on $|t| < \pi/2$.",
            "steps": [
                {"text": "y1 = cos t, y2 = sin t, W = cos^2 t + sin^2 t = 1.", "tex": r"c_1' = -\sin t\sec t = -\tan t,\qquad c_2' = \cos t\sec t = 1"},
                {"text": "Integrate.", "tex": r"c_1 = \ln|\cos t|,\qquad c_2 = t"},
                {"text": "Assemble.", "tex": r"y_p = \cos t\,\ln|\cos t| + t\sin t"}
            ],
            "answer": r"$y_p = \cos t\ln(\cos t) + t\sin t$ on $|t| < \pi/2$; undetermined coefficients could not find it, because $\sec t$ is not a nice function."
        },
        "sources": {
            "video": [vs(23, 0, "Variation of parameters needs y1 and y2"),
                      vs(23, 120, "Any f(t), even varying coefficients"),
                      vs(23, 240, "y = c1(t) y1 + c2(t) y2"),
                      vs(23, 300, "Two conditions and the solution"),
                      vs(23, 360, "The Wronskian W"),
                      vs(23, 510, "Constant coefficients: e^(s1 t), e^(s2 t)"),
                      vs(23, 600, "W = (s2 - s1) e^((s1 + s2) t)"),
                      vs(23, 720, "Combine the integrals"),
                      vs(23, 990, "The impulse response g(t - T)"),
                      vs(23, 1050, "Each input starts a response")],
            "book": [bk(133, "Variation of parameters"),
                     bk(134, "Example: y'' + y = t, and the impulse response")]
        },
        "tutorNotes": "Video 23. y = c1(t) y1 + c2(t) y2 with c1' y1 + c2' y2 = 0, c1' y1' + c2' y2' = f. W = y1 y2' - y2 y1'. c1' = -y2 f/W, c2' = y1 f/W. Constant coefficients with distinct roots: y1 = e^(s1 t), y2 = e^(s2 t), W = (s2 - s1) e^((s1 + s2) t), y_p = integral_0^t g(t - T) f(T) dT with g = (e^(s2 t) - e^(s1 t))/(s2 - s1); double root r: null solutions e^(rt), t e^(rt), W = e^(2rt), g = t e^(rt). Example y'' + y = sec t: y_p = cos t ln|cos t| + t sin t."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-analogy", r"In the analogy between $LI'' + RI' + I/C$ and $my'' + by' + ky$, what matches the spring constant $k$?", [
        (r"$1/C$", True, r"Right. The capacitor stores energy like a spring; its coefficient is $1/C$."),
        (r"$C$", False, r"No. The capacitance appears as $1/C$ in the equation."),
        (r"$L$", False, r"No. Inductance matches mass $m$."),
        (r"$R$", False, r"No. Resistance matches damping $b$.")]),
    q("q-impedance", r"What is the impedance of the RLC loop at frequency $\omega$?", [
        (r"$R + i\left(\omega L - \dfrac{1}{\omega C}\right)$", True, r"Right. $i\omega L + R + 1/(i\omega C)$, and $1/i = -i$."),
        (r"$R + i\left(\omega L + \dfrac{1}{\omega C}\right)$", False, r"No. $1/(i\omega C) = -i/(\omega C)$: the capacitor term has a minus sign."),
        (r"$R + \omega L + \dfrac{1}{\omega C}$", False, r"No. The inductor and capacitor terms are imaginary."),
        (r"$R\,\omega L/(\omega C)$", False, r"No. The three voltage drops add; they do not multiply.")]),
    q("q-tune", r"At which frequency is $|Z|$ smallest?", [
        (r"$\omega_0 = 1/\sqrt{LC}$, where $|Z| = R$", True, r"Right. The reactance $\omega L - 1/(\omega C)$ vanishes there."),
        (r"$\omega = 0$", False, r"No. At low frequency $1/(\omega C)$ is huge."),
        (r"$\omega = R/L$", False, r"No. $R$ does not affect where the reactance is zero."),
        (r"$|Z|$ is the same at every frequency.", False, r"No. Only the real part $R$ is fixed.")]),
    q("q-guess-t", r"For $y'' + y' + y = t$, what is $y_p$?", [
        (r"$t - 1$", True, r"Right. With $a + bt$: $b + a + bt = t$, so $b = 1$ and $a = -1$."),
        (r"$t$", False, r"No. Then $y' = 1$ adds a constant: $0 + 1 + t \neq t$."),
        (r"$t + 1$", False, r"No. That gives $1 + t + 1 = t + 2$."),
        (r"$\tfrac12 t^2$", False, r"No. A polynomial input of degree $1$ needs a guess of degree $1$ here.")]),
    q("q-guess-form", r"What trial form does $f = t\sin t$ need (no resonance)?", [
        (r"$(a + bt)\cos t + (c + dt)\sin t$", True, r"Right. Derivatives of $t\sin t$ produce $\cos t$, $t\cos t$, $\sin t$ and $t\sin t$."),
        (r"$bt\sin t$", False, r"No. Derivatives bring in cosines and terms without $t$."),
        (r"$(a + bt)\sin t$", False, r"No. Differentiating $\sin t$ produces $\cos t$ terms too."),
        (r"$a\cos t + c\sin t$", False, r"No. The factor $t$ in the input must appear in the guess.")]),
    q("q-example", r"For $y'' - 3y' + 2y = 4t$, what is $y_p$?", [
        (r"$3 + 2t$", True, r"Right. $-3b + 2a + 2bt = 4t$ gives $b = 2$, $a = 3$."),
        (r"$2t$", False, r"No. Then $-3(2) + 2(2t) = 4t - 6 \neq 4t$."),
        (r"$2 + 3t$", False, r"No. Match $t$ first: $2b = 4$, so $b = 2$."),
        (r"$4t$", False, r"No. Substitution gives $-12 + 8t$.")]),
    q("q-resonance", r"Which input makes $y'' - 3y' + 2y = f$ resonant?", [
        (r"$e^{2t}$", True, r"Right. $2$ is a root of $s^2 - 3s + 2$, so $e^{2t}$ is a null solution."),
        (r"$e^{3t}$", False, r"No. $P(3) = 2 \neq 0$, so $y_p = e^{3t}/2$."),
        (r"$\cos t$", False, r"No. The roots are real, so $\pm i$ are not roots."),
        (r"$t$", False, r"No. $s = 0$ is not a root because $C = 2 \neq 0$.")]),
    q("q-nice", r"For which input does the method of undetermined coefficients fail?", [
        (r"$\sec t$", True, r"Right. Its derivatives ($\sec t\tan t$, ...) never close into a finite family; use variation of parameters."),
        (r"$t^2e^{-t}$", False, r"No. A polynomial times an exponential is a nice function."),
        (r"$e^{t}\cos 3t$", False, r"No. An exponential times a cosine is nice: try $e^t(M\cos 3t + N\sin 3t)$."),
        (r"$5$", False, r"No. A constant is a polynomial of degree $0$.")]),
    q("q-wronskian", r"In variation of parameters, what is $c_2'$?", [
        (r"$y_1f/W$", True, r"Right. Cramer's rule on $c_1'y_1 + c_2'y_2 = 0$, $c_1'y_1' + c_2'y_2' = f$."),
        (r"$-y_2f/W$", False, r"No. That is $c_1'$."),
        (r"$y_2f/W$", False, r"No. Check the sign and which null solution appears."),
        (r"$f/W$", False, r"No. The other null solution multiplies $f$.")]),
    q("q-convolution", r"For constant coefficients, variation of parameters (integrals from $0$ to $t$) gives which formula?", [
        (r"$y_p(t) = \int_0^t g(t - T)f(T)\,dT$", True, r"Right. Each input at time $T$ starts an impulse response that runs for time $t - T$."),
        (r"$y_p(t) = g(t)\,f(t)$", False, r"No. The response depends on the whole past of $f$, not only its present value."),
        (r"$y_p(t) = \int_0^t g(T)\,dT$", False, r"No. That is the step response, for $f = 1$ only."),
        (r"$y_p(t) = f(t)/W(t)$", False, r"No. The Wronskian sits inside the integrals for $c_1$ and $c_2$.")]),
]

EXPLORER = {
    "modes": [
        {"id": "rlc", "label": "RLC loop: impedance"},
        {"id": "uc", "label": "Undetermined coefficients"}
    ],
    "defaultMode": "uc",
    "R": {"min": 0.5, "max": 50, "step": 0.5, "default": 10},
    "L": {"min": 0.01, "max": 1, "step": 0.01, "default": 0.1},
    "Cexp": {"min": -6, "max": -2, "step": 0.1, "default": -4, "label": "log10 C"},
    "omega": {"min": 10, "max": 1000, "step": 5, "default": 100},
    "B": {"min": -4, "max": 4, "step": 0.5, "default": -3},
    "Cc": {"min": -4, "max": 6, "step": 0.5, "default": 2},
    "forms": [
        {"id": "poly", "label": "t^k (polynomial)"},
        {"id": "exp", "label": "t^k e^(st)"},
        {"id": "cos", "label": "t^k cos(ωt)"}
    ],
    "k": {"min": 0, "max": 2, "step": 1, "default": 1},
    "s": {"min": -3, "max": 3, "step": 0.5, "default": 2},
    "w": {"min": 0.5, "max": 4, "step": 0.5, "default": 1},
    "amp": {"min": -4, "max": 4, "step": 0.5, "default": 4},
    "tMax": 3,
    "presets": [
        {"id": "lecture22", "label": "y'' − 3y' + 2y = 4t", "mode": "uc", "B": -3, "Cc": 2, "form": "poly", "k": 1, "amp": 4,
         "note": "Section 3: $y_p = 3 + 2t$."},
        {"id": "lecture21", "label": "y'' + y' + y = t", "mode": "uc", "B": 1, "Cc": 1, "form": "poly", "k": 1, "amp": 1,
         "note": "Section 2: $y_p = t - 1$."},
        {"id": "quad", "label": "y'' + y' + y = t²", "mode": "uc", "B": 1, "Cc": 1, "form": "poly", "k": 2, "amp": 1,
         "note": "Section 2 example: $y_p = t^2 - 2t$."},
        {"id": "res2", "label": "Resonance e^(2t)", "mode": "uc", "B": -3, "Cc": 2, "form": "exp", "k": 0, "s": 2, "amp": 1,
         "note": "Section 3 example: $s = 2$ is a root, so $y_p = te^{2t}$."},
        {"id": "tcos", "label": "t cos t, damped", "mode": "uc", "B": 1, "Cc": 1, "form": "cos", "k": 1, "w": 1, "amp": 1,
         "note": "Four coefficients: $(a + bt)\\cos t + (c + dt)\\sin t$."},
        {"id": "radio", "label": "Book circuit", "mode": "rlc", "R": 10, "L": 0.1, "Cexp": -4, "omega": 100,
         "note": "Section 1 example: $Z = 10 - 90i$ at $\\omega = 100$; resonance near $316$."}
    ],
    "tutorContext": "Two modes. RLC: Z = R + i(omega L - 1/(omega C)) drawn as a vector in the complex plane, |Z|, phase angle, current amplitude |V|/|Z| for V = 1, resonance omega_0 = 1/sqrt(LC), and the curve |I|(omega) on a log frequency axis. Undetermined coefficients: y'' + B y' + C y = amp * f with f = t^k, t^k e^(st) or t^k cos(omega t) (k = 0, 1, 2). It finds the root multiplicity m of the input exponent (s, 0 or i omega) in P(s) = s^2 + B s + C, shows the trial form t^m (a0 + ... + ak t^k) e^(st) (real form with cos and sin for the cosine family), the solved coefficients, y_p, a residual check P(D) y_p - f at sample points, and plots y_p with the convolution solution integral_0^t g(t - T) f(T) dT (zero initial conditions), which differs from y_p by a null solution."
}

COURSE = {
    "version": 1,
    "title": "Electrical Networks and Solution Methods",
    "subtitle": "Unit 4 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 20-23, with Strang's Differential Equations and Linear Algebra, Sections 2.5-2.6",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 20-23", "duration": "1:08:16", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, Ch. 2",
             "edition": "Wellesley-Cambridge Press, 2014 (Chapter 2, Sections 2.5-2.6)", "onlineUrl": "",
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
