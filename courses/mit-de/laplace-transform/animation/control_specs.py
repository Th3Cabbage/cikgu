"""Step-by-step content of the Unit 5 animations, The Laplace Transform (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-3). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 24-26 and Strang, Sections 2.7 and 8.5-8.6.

The module name is kept from the shared scaffold (ctl_common.py imports it).
"""

RELATIONS = {
    "define": "Definition / choice",
    "model": "Modelling step",
    "classify": "Classification",
    "diagram": "Picture",
    "substitute": "Substitution",
    "identity": "Identity (=)",
    "equivalent": "Equivalent statement (⇔)",
    "solve": "Solve",
    "compute": "Computation",
    "implies": "Consequence (⇒)",
    "compare": "Check",
    "caution": "Caveat",
    "recap": "Recap",
}

SEQUENCES = [
    {
        "id": "transform-exp",
        "scene": "TransformExpSequence",
        "section": 1,
        "title": "The transform of $e^{at}$ has a pole at $s = a$",
        "summary": "Combine the exponentials, integrate, and evaluate the limits; the exponent becomes the pole.",
        "initial": {"title": "Definition", "tex": r"F(s) = \int_0^\infty f(t)\,e^{-st}\,dt",
                    "explanation": "Weight $f$ by $e^{-st}$ and integrate over all $t \\ge 0$."},
        "steps": [
            {"title": "Put in $f = e^{at}$", "relation": "substitute",
             "tex": r"\int_0^\infty e^{at}e^{-st}\,dt = \int_0^\infty e^{(a - s)t}\,dt",
             "explanation": "Exponents add."},
            {"title": "Integrate and evaluate", "relation": "compute",
             "tex": r"\left[\frac{e^{(a-s)t}}{a - s}\right]_0^\infty = 0 - \frac{1}{a - s} = \frac{1}{s - a}",
             "explanation": "For $s > a$ the upper limit vanishes."},
            {"title": "The pole", "relation": "diagram",
             "tex": r"F(s) = \frac{1}{s - a}\ \text{ is infinite at } s = a",
             "explanation": "Exponent $a$ in time becomes a pole at $a$ in the $s$-plane."},
        ],
    },
    {
        "id": "derivative-rule",
        "scene": "DerivativeRuleSequence",
        "section": 1,
        "title": "Integration by parts: $\\mathcal{L}[y'] = sY - y(0)$",
        "summary": "Move the derivative from $y$ onto $e^{-st}$; the boundary term brings in $y(0)$.",
        "initial": {"title": "Transform of a derivative", "tex": r"\mathcal{L}[y'] = \int_0^\infty y'\,e^{-st}\,dt",
                    "explanation": "We want it in terms of $Y(s)$."},
        "steps": [
            {"title": "Integrate by parts", "relation": "identity",
             "tex": r"= \Big[\,y\,e^{-st}\Big]_0^\infty - \int_0^\infty y\,(-s)e^{-st}\,dt",
             "explanation": "$\\int u\\,dv = uv - \\int v\\,du$ with $u = e^{-st}$, $dv = y'dt$."},
            {"title": "Boundary term", "relation": "compute",
             "tex": r"\Big[\,y\,e^{-st}\Big]_0^\infty = 0 - y(0)",
             "explanation": "At infinity $e^{-st}$ wins (for large enough $s$); at $0$ it equals $1$."},
            {"title": "The rule", "relation": "implies",
             "tex": r"\mathcal{L}[y'] = s\,Y(s) - y(0)",
             "explanation": "The remaining integral is $s$ times $Y(s)$. Derivatives become multiplication by $s$."},
        ],
    },
    {
        "id": "solve-first",
        "scene": "SolveFirstSequence",
        "section": 1,
        "title": "Transform, solve, split, invert: $y' - ay = e^{ct}$",
        "summary": "The differential equation becomes algebra; partial fractions turn each pole back into an exponential.",
        "initial": {"title": "The equation", "tex": r"y' - a\,y = e^{ct}",
                    "explanation": "Constant rate $a$, exponential input."},
        "steps": [
            {"title": "Transform", "relation": "substitute",
             "tex": r"s\,Y - y(0) - a\,Y = \frac{1}{s - c}",
             "explanation": "Use the derivative rule and $\\mathcal{L}[e^{ct}] = 1/(s - c)$."},
            {"title": "Solve for $Y$", "relation": "solve",
             "tex": r"Y = \frac{y(0)}{s - a} + \frac{1}{(s - a)(s - c)}",
             "explanation": "Algebra only. Two poles: $a$ (null) and $c$ (input)."},
            {"title": "Partial fractions", "relation": "identity",
             "tex": r"\frac{1}{(s - a)(s - c)} = \frac{1}{c - a}\left(\frac{1}{s - c} - \frac{1}{s - a}\right)",
             "explanation": "Combine the right side to check."},
            {"title": "Invert", "relation": "implies",
             "tex": r"y = y(0)\,e^{at} + \frac{e^{ct} - e^{at}}{c - a}",
             "explanation": "Each $1/(s - p)$ is the transform of $e^{pt}$."},
        ],
    },
    {
        "id": "cos-transform",
        "scene": "CosTransformSequence",
        "section": 2,
        "title": "$\\mathcal{L}[\\cos\\omega t]$ from $e^{i\\omega t}$",
        "summary": "Multiply $1/(s - i\\omega)$ by its conjugate; the real part is the cosine transform, the imaginary part the sine.",
        "initial": {"title": "Complex exponential", "tex": r"\mathcal{L}[e^{i\omega t}] = \frac{1}{s - i\omega}",
                    "explanation": "The rule for $e^{at}$ with $a = i\\omega$."},
        "steps": [
            {"title": "Multiply by the conjugate", "relation": "identity",
             "tex": r"\frac{1}{s - i\omega}\cdot\frac{s + i\omega}{s + i\omega} = \frac{s + i\omega}{s^2 + \omega^2}",
             "explanation": "$(s - i\\omega)(s + i\\omega) = s^2 + \\omega^2$ is real."},
            {"title": "Real and imaginary parts", "relation": "implies",
             "tex": r"\mathcal{L}[\cos\omega t] = \frac{s}{s^2 + \omega^2},\qquad \mathcal{L}[\sin\omega t] = \frac{\omega}{s^2 + \omega^2}",
             "explanation": "$e^{i\\omega t} = \\cos\\omega t + i\\sin\\omega t$, and the transform is linear."},
            {"title": "Poles at $\\pm i\\omega$", "relation": "diagram",
             "tex": r"s^2 + \omega^2 = 0 \;\Rightarrow\; s = \pm i\omega",
             "explanation": "Oscillation in time means poles on the imaginary axis."},
        ],
    },
    {
        "id": "convolution",
        "scene": "ConvolutionSequence",
        "section": 3,
        "title": "Convolution reproduces the partial-fraction answer",
        "summary": "For $G = 1/(s - a)$ and $F = 1/(s - c)$, $\\int_0^t e^{a(t-T)}e^{cT}dT$ equals the inverse of $GF$.",
        "initial": {"title": "Product of transforms", "tex": r"Y = G\,F = \frac{1}{s - a}\cdot\frac{1}{s - c}",
                    "explanation": "From rest: output transform = transfer function times input transform."},
        "steps": [
            {"title": "Convolution integral", "relation": "define",
             "tex": r"y(t) = \int_0^t g(t - T)\,f(T)\,dT = \int_0^t e^{a(t - T)}\,e^{cT}\,dT",
             "explanation": "Each input at time $T$ grows by $e^{a(t - T)}$."},
            {"title": "Pull out $e^{at}$", "relation": "compute",
             "tex": r"= e^{at}\int_0^t e^{(c - a)T}\,dT = e^{at}\,\frac{e^{(c - a)t} - 1}{c - a}",
             "explanation": "One exponential integral."},
            {"title": "Same answer", "relation": "compare",
             "tex": r"y = \frac{e^{ct} - e^{at}}{c - a}",
             "explanation": "Identical to the partial-fraction result with $y(0) = 0$."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
