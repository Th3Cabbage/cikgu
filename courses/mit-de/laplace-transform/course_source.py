"""Source of courses/mit-de/laplace-transform/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\laplace-transform\\course_source.py

Unit 5 of the MIT Learn Differential Equations companion: playlist videos 24-26 (Gilbert Strang,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Sections 2.7, 8.5-8.6.
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
    (24, "9RJml41PFnc", "Laplace Transform: First Order Equation", "22:38"),
    (25, "kcLc4FsshO4", "Laplace Transform: Second Order Equation", "16:31"),
    (26, "WZMQdLW4COQ", "Laplace Transforms and Convolution", "10:29"),
]

SECTIONS = [
    {
        "nav": "First order by Laplace",
        "v": 24,
        "title": r"The transform $F(s) = \int_0^\infty f(t)e^{-st}\,dt$ and $y' - ay = f$",
        "summary": r"The Laplace transform turns $e^{at}$ into $1/(s - a)$ and the derivative $y'$ into $sY - y(0)$. A differential equation becomes algebra: transform, solve for $Y(s)$, split into partial fractions, and read each $1/(s - p)$ back as $e^{pt}$.",
        "time": [0, 1358],
        "goals": [
            r"Compute the transform of $e^{at}$ and see its pole at $s = a$.",
            r"Derive $\mathcal{L}[y'] = sY(s) - y(0)$ by integration by parts.",
            r"Solve $y' - ay = e^{ct}$ by transforming, solving and inverting.",
            r"Split $\dfrac{1}{(s-a)(s-c)}$ into partial fractions."
        ],
        "notes": [
            {"heading": "The transform",
             "paragraphs": [
                 r"The Laplace transform takes a function of time $f(t)$, $t \ge 0$, to a function of $s$: $F(s) = \displaystyle\int_0^\infty f(t)\,e^{-st}\,dt$. Capital letters denote transforms: $y(t) \to Y(s)$.",
                 r"The key example is $f = e^{at}$: $\displaystyle\int_0^\infty e^{(a - s)t}\,dt = \left[\frac{e^{(a-s)t}}{a - s}\right]_0^\infty = \frac{1}{s - a}$, valid for $s > a$ so that the upper limit gives zero. The transform has a pole at $s = a$: the exponent of the function becomes the location of the pole. With $a = 0$, $\mathcal{L}[1] = 1/s$."
             ]},
            {"heading": "The derivative rule",
             "paragraphs": [
                 r"Integrate by parts: $\displaystyle\int_0^\infty y'\,e^{-st}\,dt = \Big[y\,e^{-st}\Big]_0^\infty + s\int_0^\infty y\,e^{-st}\,dt = sY(s) - y(0).$ Differentiation in $t$ becomes multiplication by $s$, and the initial value enters automatically. Applied twice: $\mathcal{L}[y''] = s^2Y - sy(0) - y'(0)$."
             ]},
            {"heading": "Transform, solve, invert",
             "paragraphs": [
                 r"For $y' - ay = 0$: $sY - y(0) - aY = 0$, so $Y = \dfrac{y(0)}{s - a}$ and $y = y(0)e^{at}$.",
                 r"For $y' - ay = e^{ct}$: $(s - a)Y - y(0) = \dfrac{1}{s - c}$, so $Y = \dfrac{y(0)}{s - a} + \dfrac{1}{(s - a)(s - c)}$. Two poles, at $a$ and $c$: the null exponent and the input exponent."
             ]},
            {"heading": "Partial fractions",
             "paragraphs": [
                 r"To invert, split the product: $\dfrac{1}{(s - a)(s - c)} = \dfrac{1}{c - a}\left(\dfrac{1}{s - c} - \dfrac{1}{s - a}\right)$ (check by combining the right side). Each simple fraction inverts to an exponential:",
                 r"$y(t) = y(0)e^{at} + \dfrac{e^{ct} - e^{at}}{c - a},$ exactly the Unit 1 answer. If $c = a$ the two poles merge into a double pole $1/(s - a)^2$, whose inverse is $te^{at}$: resonance again."
             ]}
        ],
        "keyIdeas": [
            r"$\mathcal{L}[e^{at}] = \dfrac{1}{s - a}$: exponent $\to$ pole.",
            r"$\mathcal{L}[y'] = sY - y(0)$.",
            r"Transform, solve for $Y$, partial fractions, invert.",
            r"$\dfrac{1}{(s-a)(s-c)} = \dfrac{1}{c-a}\left(\dfrac{1}{s-c} - \dfrac{1}{s-a}\right)$."
        ],
        "example": {
            "title": "Two poles (authored)",
            "problem": r"Solve $y' - 2y = e^{-t}$, $y(0) = 1$, by the Laplace transform.",
            "steps": [
                {"text": "Transform both sides.", "tex": r"(s - 2)Y - 1 = \frac{1}{s + 1}"},
                {"text": "Solve for Y and split the product (c = -1, a = 2).", "tex": r"Y = \frac{1}{s - 2} + \frac{1}{3}\left(\frac{1}{s - 2} - \frac{1}{s + 1}\right)"},
                {"text": "Invert each fraction.", "tex": r"y = \tfrac43 e^{2t} - \tfrac13 e^{-t}"}
            ],
            "answer": r"$y = \tfrac43e^{2t} - \tfrac13e^{-t}$; check $y(0) = 1$ and $y' - 2y = e^{-t}$."
        },
        "sources": {
            "video": [vs(24, 0, "Plan: f(t) to F(s), y(t) to Y(s)"),
                      vs(24, 30, "Definition: integral of f e^(-st)"),
                      vs(24, 90, "Transform of e^(at) is 1/(s - a)"),
                      vs(24, 240, "Pole at s = a"),
                      vs(24, 300, "Transform of the derivative"),
                      vs(24, 480, "Integration by parts: sY - y(0)"),
                      vs(24, 570, "Strategy: transform, solve, invert"),
                      vs(24, 630, "y' - ay = 0 gives Y = y(0)/(s - a)"),
                      vs(24, 810, "Input e^(ct): two poles"),
                      vs(24, 1050, "Partial fractions"),
                      vs(24, 1230, "Back to e^(ct) and e^(at)")],
            "book": [bk(139, "Section 2.7: Laplace transforms Y(s) and F(s)"),
                     bk(141, "Table of transforms; transform of the derivative"),
                     bk(143, "Partial fractions")]
        },
        "tutorNotes": "Video 24. F(s) = integral_0^inf f(t) e^(-st) dt. L[e^(at)] = 1/(s - a) for s > a, pole at a. L[y'] = sY - y(0) by parts; L[y''] = s^2 Y - s y(0) - y'(0). y' - ay = e^(ct): Y = y(0)/(s - a) + 1/((s - a)(s - c)); partial fractions 1/((s-a)(s-c)) = (1/(c - a))(1/(s - c) - 1/(s - a)); y = y(0) e^(at) + (e^(ct) - e^(at))/(c - a). Double pole 1/(s-a)^2 -> t e^(at)."
    },
    {
        "nav": "Second order by Laplace",
        "v": 25,
        "title": r"Transfer function $G(s) = 1/(s^2 + Bs + C)$ and cosine inputs",
        "summary": r"For $y'' + By' + Cy = \delta(t)$ from rest, $\mathcal{L}[\delta] = 1$ gives $(s^2 + Bs + C)G = 1$: the transfer function. Partial fractions return the impulse response $g = \dfrac{e^{s_1t} - e^{s_2t}}{s_1 - s_2}$. A cosine input has $\mathcal{L}[\cos\omega t] = \dfrac{s}{s^2 + \omega^2}$, adding poles at $\pm i\omega$.",
        "time": [0, 991],
        "goals": [
            r"Use $\mathcal{L}[\delta] = 1$ to find the transfer function.",
            r"Invert $G(s)$ by partial fractions to get $g(t)$.",
            r"Find $\mathcal{L}[\cos\omega t]$ and $\mathcal{L}[\sin\omega t]$ from $e^{i\omega t}$.",
            r"Predict the partial-fraction form for a cosine input and name each part."
        ],
        "notes": [
            {"heading": "The impulse and the transfer function",
             "paragraphs": [
                 r"The delta function at $t = 0$ has transform $\displaystyle\int_0^\infty \delta(t)e^{-st}\,dt = e^0 = 1$. Initial values here mean values just before the impulse ($t = 0^-$); the impulse itself makes $g'$ jump from $0$ to $1$. With zero initial conditions the equation $g'' + Bg' + Cg = \delta$ becomes $(s^2 + Bs + C)\,G(s) = 1$, so $G(s) = \dfrac{1}{s^2 + Bs + C}$.",
                 r"This is the transfer function: it multiplies the input's transform to give the output's transform. Its poles $s_1, s_2$ are the roots of $s^2 + Bs + C$, the null exponents."
             ]},
            {"heading": "Back to the impulse response",
             "paragraphs": [
                 r"For distinct roots, $G = \dfrac{1}{(s - s_1)(s - s_2)} = \dfrac{1}{s_1 - s_2}\left(\dfrac{1}{s - s_1} - \dfrac{1}{s - s_2}\right)$, and inverting gives $g(t) = \dfrac{e^{s_1t} - e^{s_2t}}{s_1 - s_2}$, the formula of Unit 3, found now by algebra."
             ]},
            {"heading": "Cosine and sine",
             "paragraphs": [
                 r"$\cos\omega t$ is the real part of $e^{i\omega t}$, whose transform is $\dfrac{1}{s - i\omega}$. Multiply top and bottom by $s + i\omega$: $\dfrac{s + i\omega}{s^2 + \omega^2}$. The real and imaginary parts give $\mathcal{L}[\cos\omega t] = \dfrac{s}{s^2 + \omega^2}$ and $\mathcal{L}[\sin\omega t] = \dfrac{\omega}{s^2 + \omega^2}$."
             ]},
            {"heading": "A cosine input",
             "paragraphs": [
                 r"From rest, $y'' + By' + Cy = \cos\omega t$ gives $Y = \dfrac{s}{(s^2 + Bs + C)(s^2 + \omega^2)}$: four poles. When the four poles are distinct, partial fractions have the shape $\dfrac{A_1}{s - s_1} + \dfrac{A_2}{s - s_2} + \dfrac{Ms + N\omega}{s^2 + \omega^2}$. The first two terms are null solutions; with damping ($B > 0$) they decay, so they are transients. The last term is the steady oscillation $M\cos\omega t + N\sin\omega t$ of Unit 3. The lecture stops at the shape; the explorer computes the numbers.",
                 r"Repeated poles change the shape. Critical damping ($s_1 = s_2$) gives a term $\dfrac{A}{(s - s_1)^2}$, whose inverse is $te^{s_1t}$. Without damping and with $\omega = \omega_n$, the poles $\pm i\omega$ are double: $Y = \dfrac{s}{(s^2 + \omega^2)^2}$ inverts to $\dfrac{t\sin\omega t}{2\omega}$, which grows. That is resonance, not a steady oscillation, and with $B = 0$ nothing is transient."
             ]}
        ],
        "keyIdeas": [
            r"$\mathcal{L}[\delta] = 1$.",
            r"$G(s) = 1/(s^2 + Bs + C)$, poles $s_1, s_2$.",
            r"$\mathcal{L}[\cos\omega t] = \dfrac{s}{s^2+\omega^2}$, $\mathcal{L}[\sin\omega t] = \dfrac{\omega}{s^2+\omega^2}$.",
            r"Cosine input: transient poles $s_1, s_2$ plus steady poles $\pm i\omega$."
        ],
        "example": {
            "title": "A step input from rest (authored)",
            "problem": r"Solve $y'' + 3y' + 2y = 1$ for $t > 0$, $y(0) = y'(0) = 0$.",
            "steps": [
                {"text": "L[1] = 1/s, and s^2 + 3s + 2 = (s + 1)(s + 2).", "tex": r"Y = \frac{1}{s(s + 1)(s + 2)}"},
                {"text": "Cover-up: the residue at each pole is the rest of the fraction evaluated there.", "tex": r"Y = \frac{1/2}{s} - \frac{1}{s + 1} + \frac{1/2}{s + 2}"},
                {"text": "Invert term by term.", "tex": r"y = \tfrac12 - e^{-t} + \tfrac12e^{-2t}"}
            ],
            "answer": r"$y = \tfrac12 - e^{-t} + \tfrac12e^{-2t}$, the step response of Unit 3."
        },
        "sources": {
            "video": [vs(25, 0, "y'' + By' + Cy = delta, zero initial conditions"),
                      vs(25, 30, "Transform of delta is 1"),
                      vs(25, 90, "(s^2 + Bs + C) G = 1"),
                      vs(25, 150, "G(s) is the transfer function"),
                      vs(25, 210, "Partial fractions give g(t)"),
                      vs(25, 390, "Cosine input: real part of e^(i omega t)"),
                      vs(25, 600, "Multiply by s + i omega"),
                      vs(25, 660, "Transforms of cos and sin"),
                      vs(25, 720, "Y for the cosine input"),
                      vs(25, 870, "Form of the partial fractions")],
            "book": [bk(141, "Transforms of delta, cos and sin"),
                     bk(144, "Second order equations and the transfer function")]
        },
        "tutorNotes": "Video 25. L[delta] = 1. g'' + B g' + C g = delta from rest: (s^2 + Bs + C) G = 1, G = transfer function. G = 1/((s - s1)(s - s2)) = (1/(s1 - s2))(1/(s - s1) - 1/(s - s2)), g = (e^(s1 t) - e^(s2 t))/(s1 - s2). L[cos wt] = s/(s^2 + w^2), L[sin wt] = w/(s^2 + w^2) from 1/(s - iw) = (s + iw)/(s^2 + w^2). Cosine input from rest: Y = s/((s^2 + Bs + C)(s^2 + w^2)) = A1/(s - s1) + A2/(s - s2) + (Ms + Nw)/(s^2 + w^2) when the four poles are distinct; the s1, s2 terms are transients only when B > 0. Repeated poles: critical damping gives t e^(s1 t); B = 0 with w = w_n gives double poles at +-iw and t sin(wt)/(2w) (resonance)."
    },
    {
        "nav": "Convolution",
        "v": 26,
        "title": r"Products of transforms are convolutions: $Y = GF \Leftrightarrow y = g * f$",
        "summary": r"With zero initial conditions $Y(s) = G(s)F(s)$. Multiplying transforms corresponds to convolving functions: $y(t) = (g * f)(t) = \int_0^t g(t - T)\,f(T)\,dT$, the formula found by variation of parameters in Unit 4.",
        "time": [0, 629],
        "goals": [
            r"Write the output transform as $G(s)F(s)$.",
            r"Define the convolution $g * f$ and read it as superposed impulse responses.",
            r"Check the rule on $y' - ay = e^{ct}$."
        ],
        "notes": [
            {"heading": "Multiply transforms",
             "paragraphs": [
                 r"From rest, $y'' + By' + Cy = f(t)$ transforms to $(s^2 + Bs + C)Y = F$, so $Y(s) = G(s)\,F(s)$. The question is what function has the transform $G\cdot F$. It is not $g(t)f(t)$."
             ]},
            {"heading": "The convolution rule",
             "paragraphs": [
                 r"The answer is the convolution $(g * f)(t) = \displaystyle\int_0^t g(t - T)\,f(T)\,dT$. Each input $f(T)\,dT$ at time $T$ starts an impulse response that has run for time $t - T$; adding them gives $y$. The book proves the rule by exchanging the order of the two integrals; the lecture states it."
             ]},
            {"heading": "A check",
             "paragraphs": [
                 r"For $y' - ay = e^{ct}$ from rest: $G = 1/(s - a)$ so $g = e^{at}$, and $F = 1/(s - c)$. The convolution is $\displaystyle\int_0^t e^{a(t - T)}e^{cT}\,dT = e^{at}\int_0^t e^{(c - a)T}\,dT = \frac{e^{ct} - e^{at}}{c - a}$, which agrees with partial fractions in Section 1."
             ]}
        ],
        "keyIdeas": [
            r"From rest: $Y = G(s)F(s)$.",
            r"$(g * f)(t) = \int_0^t g(t - T)f(T)\,dT$.",
            r"$\mathcal{L}[g * f] = G\cdot F$, not $\mathcal{L}[gf]$.",
            r"$e^{at} * e^{ct} = \dfrac{e^{ct} - e^{at}}{c - a}$."
        ],
        "example": {
            "title": "Convolving a step with a sine (authored)",
            "problem": r"Compute $1 * \sin t$ directly and check it with transforms.",
            "steps": [
                {"text": "Direct integral (g = 1, f = sin).", "tex": r"\int_0^t 1\cdot\sin T\,dT = 1 - \cos t"},
                {"text": "Product of transforms.", "tex": r"\frac{1}{s}\cdot\frac{1}{s^2 + 1}"},
                {"text": "Partial fractions of the product.", "tex": r"\frac{1}{s(s^2 + 1)} = \frac{1}{s} - \frac{s}{s^2 + 1} = \mathcal{L}[1 - \cos t]"}
            ],
            "answer": r"$1 * \sin t = 1 - \cos t$, and its transform is $\dfrac{1}{s}\cdot\dfrac{1}{s^2+1}$."
        },
        "sources": {
            "video": [vs(26, 0, "Y = G(s) F(s)"),
                      vs(26, 60, "What function has transform G times F?"),
                      vs(26, 150, "Convolution integral"),
                      vs(26, 270, "Multiply transforms, convolve functions"),
                      vs(26, 330, "Proof is in the book"),
                      vs(26, 360, "Example: y' - ay = e^(ct)"),
                      vs(26, 480, "Same answer as partial fractions")],
            "book": [bk(141, "Convolution in Section 2.7"),
                     bk(476, "Section 8.5: the convolution rule"),
                     bk(479, "Section 8.6: convolution, Fourier and Laplace")]
        },
        "tutorNotes": "Video 26. From rest Y = G F. y = g * f = integral_0^t g(t - T) f(T) dT. L[g * f] = G F. Example y' - ay = e^(ct): g = e^(at), f = e^(ct), convolution = (e^(ct) - e^(at))/(c - a)."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-exp", r"What is $\mathcal{L}[e^{-3t}]$?", [
        (r"$\dfrac{1}{s + 3}$", True, r"Right. $\mathcal{L}[e^{at}] = 1/(s - a)$ with $a = -3$."),
        (r"$\dfrac{1}{s - 3}$", False, r"No. That is the transform of $e^{3t}$."),
        (r"$\dfrac{-3}{s}$", False, r"No. The exponent becomes the pole location."),
        (r"$e^{-3s}$", False, r"No. $e^{-sT}$ is the transform of a delayed delta, not of an exponential.")]),
    q("q-deriv", r"What is the transform of $y'$?", [
        (r"$sY(s) - y(0)$", True, r"Right. Integration by parts gives the boundary term $-y(0)$."),
        (r"$sY(s)$", False, r"No. The initial value appears from the boundary term."),
        (r"$Y(s)/s$", False, r"No. Dividing by $s$ corresponds to integrating."),
        (r"$Y'(s)$", False, r"No. $-Y'(s)$ is the transform of $t\,y(t)$.")]),
    q("q-pole", r"A transform $Y(s)$ has poles at $s = -1$ and $s = 2$ (both simple). Which functions appear in $y(t)$?", [
        (r"$e^{-t}$ and $e^{2t}$", True, r"Right. Each simple pole $p$ contributes a multiple of $e^{pt}$."),
        (r"$e^{t}$ and $e^{-2t}$", False, r"No. The signs do not flip: the pole is the exponent."),
        (r"$\sin t$ and $\sin 2t$", False, r"No. Sines come from imaginary poles $\pm i\omega$."),
        (r"$t$ and $t^2$", False, r"No. Powers of $t$ come from a pole at $0$ of higher order.")]),
    q("q-pf", r"Which split is correct?", [
        (r"$\dfrac{1}{(s-a)(s-c)} = \dfrac{1}{c-a}\left(\dfrac{1}{s-c} - \dfrac{1}{s-a}\right)$", True, r"Right. Combining the right side gives $\dfrac{(s - a) - (s - c)}{(c - a)(s-a)(s-c)} = \dfrac{1}{(s-a)(s-c)}$."),
        (r"$\dfrac{1}{(s-a)(s-c)} = \dfrac{1}{s-a} + \dfrac{1}{s-c}$", False, r"No. Combining gives $\dfrac{2s - a - c}{(s-a)(s-c)}$."),
        (r"$\dfrac{1}{(s-a)(s-c)} = \dfrac{1}{s-a}\cdot\dfrac{1}{s-c}$, already split", False, r"No. A product is not a sum; the inverse of a product is a convolution."),
        (r"$\dfrac{1}{(s-a)(s-c)} = \dfrac{1}{a-c}\left(\dfrac{1}{s-c} - \dfrac{1}{s-a}\right)$", False, r"No. The sign of the factor is reversed.")]),
    q("q-delta", r"What is $\mathcal{L}[\delta(t)]$?", [
        (r"$1$", True, r"Right. The integral picks out $e^{-s\cdot 0} = 1$."),
        (r"$0$", False, r"No. The delta has total integral $1$."),
        (r"$1/s$", False, r"No. That is the transform of the step function, the integral of delta."),
        (r"$s$", False, r"No. Multiplying by $s$ would mean differentiating the step a second time.")]),
    q("q-transfer", r"For $y'' + 4y' + 3y$ from rest, what is the transfer function?", [
        (r"$\dfrac{1}{(s + 1)(s + 3)}$", True, r"Right. $s^2 + 4s + 3 = (s + 1)(s + 3)$."),
        (r"$(s + 1)(s + 3)$", False, r"No. The transfer function is the reciprocal: $Y = GF$."),
        (r"$\dfrac{1}{(s - 1)(s - 3)}$", False, r"No. The roots of $s^2 + 4s + 3$ are $-1$ and $-3$."),
        (r"$\dfrac{s}{s^2 + 4s + 3}$", False, r"No. There is no $s$ on top for a delta input from rest.")]),
    q("q-cos", r"What is $\mathcal{L}[\cos 2t]$?", [
        (r"$\dfrac{s}{s^2 + 4}$", True, r"Right. $s/(s^2 + \omega^2)$ with $\omega = 2$."),
        (r"$\dfrac{2}{s^2 + 4}$", False, r"No. That is $\mathcal{L}[\sin 2t]$."),
        (r"$\dfrac{1}{s - 2i}$", False, r"No. That is $\mathcal{L}[e^{2it}]$; take the real part."),
        (r"$\dfrac{s}{s^2 - 4}$", False, r"No. That is $\mathcal{L}[\cosh 2t]$.")]),
    q("q-transient", r"For a cosine input $\cos\omega t$ into a damped system from rest, which poles of $Y$ give the steady oscillation?", [
        (r"$\pm i\omega$", True, r"Right. They come from $s^2 + \omega^2$, the input's transform."),
        (r"$s_1$ and $s_2$", False, r"No. Those are the system's poles; with damping their terms decay (transients)."),
        (r"$s = 0$", False, r"No. A pole at $0$ would give a constant."),
        (r"There are no poles for an oscillation.", False, r"No. Imaginary poles give oscillations.")]),
    q("q-conv", r"From rest, $Y(s) = G(s)F(s)$. What is $y(t)$?", [
        (r"$\int_0^t g(t - T)\,f(T)\,dT$", True, r"Right. A product of transforms is the transform of a convolution."),
        (r"$g(t)\,f(t)$", False, r"No. Products of functions do not correspond to products of transforms."),
        (r"$g(t) + f(t)$", False, r"No. Sums correspond to sums, not products."),
        (r"$\int_0^\infty g(T)f(T)\,dT$", False, r"No. That is a single number, not a function of $t$.")]),
    q("q-conv-ex", r"What is $e^{at} * e^{ct}$ for $a \neq c$?", [
        (r"$\dfrac{e^{ct} - e^{at}}{c - a}$", True, r"Right. $e^{at}\int_0^t e^{(c-a)T}dT$; also the inverse of $\dfrac{1}{(s-a)(s-c)}$."),
        (r"$e^{(a + c)t}$", False, r"No. That would be the product $e^{at}e^{ct}$."),
        (r"$\dfrac{e^{ct} + e^{at}}{c + a}$", False, r"No. Check $t = 0$: a convolution from $0$ to $0$ is zero."),
        (r"$te^{at}$", False, r"No. That is the case $c = a$, the double pole.")]),
]

EXPLORER = {
    "orders": [
        {"id": "first", "label": "First order  y' − a y = f"},
        {"id": "second", "label": "Second order  y'' + B y' + C y = f"}
    ],
    "defaultOrder": "second",
    "inputs": [
        {"id": "none", "label": "0"},
        {"id": "delta", "label": "δ(t)"},
        {"id": "step", "label": "1 (step)"},
        {"id": "exp", "label": "e^(ct)"},
        {"id": "cos", "label": "cos ωt"},
        {"id": "sin", "label": "sin ωt"}
    ],
    "defaultInput": "cos",
    "a": {"min": -3, "max": 2, "step": 0.25, "default": 2},
    "B": {"min": 0, "max": 5, "step": 0.25, "default": 1},
    "C": {"min": 0.25, "max": 9, "step": 0.25, "default": 2},
    "c": {"min": -3, "max": 2, "step": 0.25, "default": -1},
    "omega": {"min": 0.25, "max": 4, "step": 0.25, "default": 1},
    "y0": {"min": -2, "max": 2, "step": 0.25, "default": 0},
    "v0": {"min": -2, "max": 2, "step": 0.25, "default": 0},
    "tMax": 10,
    "presets": [
        {"id": "first", "label": "y' − 2y = e^(−t)", "order": "first", "a": 2, "input": "exp", "c": -1, "y0": 1,
         "note": "Section 1 example: poles $2$ and $-1$; $y = \\tfrac43e^{2t} - \\tfrac13e^{-t}$."},
        {"id": "double", "label": "Double pole", "order": "first", "a": -1, "input": "exp", "c": -1, "y0": 0,
         "note": "$c = a$: $Y = 1/(s+1)^2$ and $y = te^{-t}$."},
        {"id": "impulse", "label": "Impulse response", "order": "second", "B": 3, "C": 2, "input": "delta", "y0": 0, "v0": 0,
         "note": "Section 2: $G = 1/((s+1)(s+2))$, $g = e^{-t} - e^{-2t}$."},
        {"id": "step", "label": "Step response", "order": "second", "B": 3, "C": 2, "input": "step", "y0": 0, "v0": 0,
         "note": "Section 2 example: poles $0, -1, -2$."},
        {"id": "cos", "label": "Cosine input", "order": "second", "B": 1, "C": 2, "input": "cos", "omega": 1, "y0": 0, "v0": 0,
         "note": "Four poles: transients at $s_{1,2}$, steady oscillation at $\\pm i$."},
        {"id": "res", "label": "Undamped resonance", "order": "second", "B": 0, "C": 1, "input": "cos", "omega": 1, "y0": 0, "v0": 0,
         "note": "Double poles at $\\pm i$: the response $\\tfrac12 t\\sin t$ grows."}
    ],
    "tutorContext": "The explorer builds Y(s) for y' - a y = f (first order) or y'' + B y' + C y = f (second order) with initial values y(0-) = y0, y'(0-) = v0 taken just before t = 0 (for the impulse input the delta adds 1 to y in the first order case, so y(0+) = y0 + 1, and adds 1 to y' in the second order case, so y'(0+) = v0 + 1) and f = 0, delta(t), 1, e^(ct), cos(omega t) or sin(omega t): Y = [F(s) + y0] / (s - a) or Y = [F(s) + (s + B) y0 + v0] / (s^2 + B s + C). It shows the poles of the reduced Y(s) in the complex s-plane (system poles and input poles, with multiplicities; a pole cancelled by the numerator is removed; poles closer than 1e-5 are merged into one repeated pole for a stable evaluation), the partial-fraction terms with their residues (higher coefficients for repeated poles), and plots y(t) = sum of residue * t^j e^(p t) / j! (real part) against a numerical solution for t in [0, 10]."
}

COURSE = {
    "version": 1,
    "title": "The Laplace Transform",
    "subtitle": "Unit 5 of a study companion to MIT Learn Differential Equations (Gilbert Strang), videos 24-26, with Strang's Differential Equations and Linear Algebra, Sections 2.7 and 8.5-8.6",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 24-26", "duration": "49:38", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, 2.7, 8.5-8.6",
             "edition": "Wellesley-Cambridge Press, 2014 (Sections 2.7, 8.5-8.6)", "onlineUrl": "",
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
