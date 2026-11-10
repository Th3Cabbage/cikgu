"""Step-by-step content of the Unit 3 animations, Second Order Equations (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-6). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 14-19 and Strang, Sections 2.1-2.4.

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
        "id": "free-oscillation",
        "scene": "FreeOscillationSequence",
        "section": 1,
        "title": "Free harmonic motion from two initial conditions",
        "summary": "Cosine and sine solve $y'' + \\omega_n^2y = 0$; $y(0)$ and $y'(0)$ fix the mix, which is one shifted cosine.",
        "initial": {"title": "No damping, no force", "tex": r"y'' + \omega_n^2\,y = 0,\qquad \omega_n^2 = k/m",
                    "explanation": "The example uses $\\omega_n = 2$, $y(0) = 1$, $y'(0) = 2$."},
        "steps": [
            {"title": "Two null solutions", "relation": "compute",
             "tex": r"(\cos\omega_n t)'' = -\omega_n^2\cos\omega_n t,\quad (\sin\omega_n t)'' = -\omega_n^2\sin\omega_n t",
             "explanation": "Two derivatives bring out $-\\omega_n^2$, which the $\\omega_n^2y$ term cancels."},
            {"title": "Match $y(0)$ and $y'(0)$", "relation": "solve",
             "tex": r"y = y(0)\cos\omega_n t + \frac{y'(0)}{\omega_n}\sin\omega_n t = \cos 2t + \sin 2t",
             "explanation": "At $t = 0$ only the cosine counts for $y$ and only the sine for $y'$."},
            {"title": "One cosine with a lag", "relation": "identity",
             "tex": r"\cos 2t + \sin 2t = \sqrt2\,\cos\left(2t - \tfrac{\pi}{4}\right)",
             "explanation": "$R = \\sqrt{c_1^2 + c_2^2}$ and $\\tan\\alpha = c_2/c_1$. The amplitude never changes."},
        ],
    },
    {
        "id": "forced-cosine",
        "scene": "ForcedCosineSequence",
        "section": 2,
        "title": "Forcing at frequency $\\omega$: the frequency response",
        "summary": "Substitute $Y\\cos\\omega t$, match cosines, and watch $Y$ blow up as $\\omega \\to \\omega_n$.",
        "initial": {"title": "Driven spring", "tex": r"m y'' + k y = \cos\omega t",
                    "explanation": "Outside frequency $\\omega$, natural frequency $\\omega_n = \\sqrt{k/m}$."},
        "steps": [
            {"title": "Try $Y\\cos\\omega t$", "relation": "substitute",
             "tex": r"-m\omega^2 Y\cos\omega t + kY\cos\omega t = \cos\omega t",
             "explanation": "Two derivatives give $-\\omega^2$; without damping no sine appears."},
            {"title": "Match the cosines", "relation": "solve",
             "tex": r"Y = \frac{1}{k - m\omega^2} = \frac{1}{m(\omega_n^2 - \omega^2)}",
             "explanation": "Use $k = m\\omega_n^2$."},
            {"title": "Graph of $Y(\\omega)$", "relation": "diagram",
             "tex": r"|Y| \to \infty \text{ as } \omega \to \omega_n",
             "explanation": "Pushing near the natural rhythm gives a huge response; at $\\omega = \\omega_n$ (resonance) a new formula is needed."},
        ],
    },
    {
        "id": "damping-roots",
        "scene": "DampingRootsSequence",
        "section": 3,
        "title": "Raising the parabola $s^2 + 2s + C$",
        "summary": "Two real roots, then a double root, then complex roots: overdamped, critical, underdamped.",
        "initial": {"title": "Characteristic equation", "tex": r"y = e^{st}:\quad s^2 + 2s + C = 0",
                    "explanation": "Here $A = 1$, $B = 2$; the spring constant $C$ will grow."},
        "steps": [
            {"title": "$C = 0$: roots $0$ and $-2$", "relation": "diagram",
             "tex": r"s^2 + 2s = s(s + 2)",
             "explanation": "The parabola crosses zero twice: two real exponents."},
            {"title": "$C = 1$: a double root", "relation": "diagram",
             "tex": r"s^2 + 2s + 1 = (s + 1)^2",
             "explanation": "It just touches zero at $-1$: critical damping, $e^{-t}$ and $te^{-t}$."},
            {"title": "$C = 2$: complex roots", "relation": "diagram",
             "tex": r"s^2 + 2s + 2 = 0 \;\Rightarrow\; s = -1 \pm i",
             "explanation": "No real roots: the motion oscillates while its amplitude decays like $e^{-t}$."},
            {"title": "The four cases", "relation": "classify",
             "tex": r"B^2 > 4AC,\quad B^2 = 4AC,\quad B^2 < 4AC,\quad B = 0",
             "explanation": "Overdamped, critical, underdamped, undamped."},
        ],
    },
    {
        "id": "impulse-step",
        "scene": "ImpulseStepSequence",
        "section": 4,
        "title": "From the impulse response to the step response",
        "summary": "Build $g$ from two exponentials with $g(0) = 0$, $g'(0) = 1$, then integrate it to get $r$.",
        "initial": {"title": "An example", "tex": r"y'' + 3y' + 2y,\qquad s_1 = -1,\ s_2 = -2",
                    "explanation": "Overdamped: two negative real roots."},
        "steps": [
            {"title": "Impulse response", "relation": "compute",
             "tex": r"g(t) = \frac{e^{s_1t} - e^{s_2t}}{s_1 - s_2} = e^{-t} - e^{-2t}",
             "explanation": "The difference starts at $0$; dividing by $s_1 - s_2$ makes the starting slope $1$."},
            {"title": "Step = integral of impulse", "relation": "implies",
             "tex": r"r(t) = \int_0^t g(s)\,ds",
             "explanation": "The step function is the integral of the delta function."},
            {"title": "The step response", "relation": "compute",
             "tex": r"r(t) = \tfrac12 - e^{-t} + \tfrac12e^{-2t} \;\to\; \tfrac{1}{C} = \tfrac12",
             "explanation": "Area under $g$ so far. It settles at $1/C$."},
        ],
    },
    {
        "id": "resonance-limit",
        "scene": "ResonanceLimitSequence",
        "section": 5,
        "title": "Resonance by l'Hôpital: $te^{s_1t}/P'(s_1)$",
        "summary": "Subtract a null solution so the quotient becomes $0/0$, then differentiate top and bottom in $s$.",
        "initial": {"title": "Exponential input", "tex": r"P(D)\,y = e^{st},\qquad y_p = \frac{e^{st}}{P(s)}",
                    "explanation": "Fails when $P(s_1) = 0$."},
        "steps": [
            {"title": "Subtract a null solution", "relation": "substitute",
             "tex": r"y = \frac{e^{st} - e^{s_1t}}{P(s)}",
             "explanation": "$e^{s_1t}/P(s)$ solves the null equation, so $y$ still solves $P(D)y = e^{st}$."},
            {"title": "Let $s \\to s_1$: $0/0$", "relation": "caution",
             "tex": r"\frac{e^{s_1t} - e^{s_1t}}{P(s_1)} = \frac{0}{0}",
             "explanation": "Top and bottom both vanish at the root."},
            {"title": "Differentiate in $s$", "relation": "compute",
             "tex": r"y_p = \frac{\partial_s(e^{st} - e^{s_1t})}{P'(s)}\Big|_{s = s_1} = \frac{t\,e^{s_1t}}{P'(s_1)}",
             "explanation": "The derivative of $e^{st}$ with respect to $s$ is $te^{st}$: the factor $t$ of resonance."},
        ],
    },
    {
        "id": "gain-phase",
        "scene": "GainPhaseSequence",
        "section": 6,
        "title": "Rectangular to polar: $M\\cos + N\\sin = G\\cos(\\omega t - \\alpha)$",
        "summary": "For $y'' + y' + 2y = \\cos t$: $M = N = \\tfrac12$, so $G = 1/\\sqrt2$ and $\\alpha = \\pi/4$.",
        "initial": {"title": "Damped, driven", "tex": r"y'' + y' + 2y = \cos t",
                    "explanation": "The $y'$ term turns cosines into sines."},
        "steps": [
            {"title": "Match cos and sin", "relation": "solve",
             "tex": r"M = \frac{C - A\omega^2}{D} = \tfrac12,\quad N = \frac{B\omega}{D} = \tfrac12,\quad D = 2",
             "explanation": "$C - A\\omega^2 = 1$ and $B\\omega = 1$."},
            {"title": "The point $(M, N)$", "relation": "diagram",
             "tex": r"G = \sqrt{M^2 + N^2} = \tfrac{1}{\sqrt2},\qquad \tan\alpha = \frac{N}{M} = 1",
             "explanation": "Length and angle of the vector from the origin to $(M, N)$."},
            {"title": "The response lags", "relation": "implies",
             "tex": r"y_p = \tfrac{1}{\sqrt2}\cos\left(t - \tfrac{\pi}{4}\right)",
             "explanation": "Smaller by $G$ and later by $\\alpha/\\omega$ than the input $\\cos t$."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
