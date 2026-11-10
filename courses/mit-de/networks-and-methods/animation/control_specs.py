"""Step-by-step content of the Unit 4 animations, Electrical Networks and Solution Methods (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-4). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 20-23 and Strang, Sections 2.5-2.6.

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
        "id": "rlc-impedance",
        "scene": "RLCImpedanceSequence",
        "section": 1,
        "title": "Kirchhoff's law to the impedance $Z$",
        "summary": "Three voltage drops, the trial current $We^{i\\omega t}$, and the complex number $Z$ drawn in the plane.",
        "initial": {"title": "One loop", "tex": r"L\,I' + R\,I + \frac{1}{C}\int I\,dt = V e^{i\omega t}",
                    "explanation": "Inductor, resistor and capacitor drops add to the source voltage."},
        "steps": [
            {"title": "Try $I = We^{i\\omega t}$", "relation": "substitute",
             "tex": r"\left(i\omega L + R + \frac{1}{i\omega C}\right)W = V",
             "explanation": "The derivative brings $i\\omega$; the integral divides by $i\\omega$."},
            {"title": "Collect real and imaginary parts", "relation": "identity",
             "tex": r"Z = R + i\left(\omega L - \frac{1}{\omega C}\right),\qquad W = \frac{V}{Z}",
             "explanation": "$1/i = -i$ turns the capacitor term negative."},
            {"title": "Draw $Z$", "relation": "diagram",
             "tex": r"|Z|^2 = R^2 + \left(\omega L - \frac{1}{\omega C}\right)^2",
             "explanation": "Resistance along the real axis, reactance up (inductor) or down (capacitor). At $\\omega_0 = 1/\\sqrt{LC}$ the reactance vanishes."},
        ],
    },
    {
        "id": "uc-match",
        "scene": "UCMatchSequence",
        "section": 2,
        "title": "Matching coefficients for $y'' + y' + y = t$",
        "summary": "Substitute $a + bt$, collect powers of $t$, and solve two equations.",
        "initial": {"title": "A polynomial input", "tex": r"y'' + y' + y = t",
                    "explanation": "Derivatives of a linear polynomial stay polynomials."},
        "steps": [
            {"title": "Guess $a + bt$", "relation": "define",
             "tex": r"y_p = a + bt,\quad y_p' = b,\quad y_p'' = 0",
             "explanation": "Same form as the input, unknown numbers."},
            {"title": "Substitute", "relation": "substitute",
             "tex": r"0 + b + (a + bt) = t",
             "explanation": "Put the three pieces into the equation."},
            {"title": "Match powers of $t$", "relation": "solve",
             "tex": r"t:\ b = 1,\qquad 1:\ a + b = 0 \;\Rightarrow\; y_p = t - 1",
             "explanation": "Both sides must agree term by term."},
        ],
    },
    {
        "id": "uc-example",
        "scene": "UCExampleSequence",
        "section": 3,
        "title": "$y'' - 3y' + 2y = 4t$, then a resonant input",
        "summary": "Match to get $y_p = 3 + 2t$; then $e^{2t}$ hits a root and needs the factor $t$.",
        "initial": {"title": "Null solutions", "tex": r"s^2 - 3s + 2 = (s - 1)(s - 2)",
                    "explanation": "$y_n = c_1e^{t} + c_2e^{2t}$."},
        "steps": [
            {"title": "Substitute $a + bt$", "relation": "substitute",
             "tex": r"-3b + 2(a + bt) = 4t",
             "explanation": "$y'' = 0$, $y' = b$."},
            {"title": "Match", "relation": "solve",
             "tex": r"2b = 4,\quad 2a - 3b = 0 \;\Rightarrow\; y_p = 3 + 2t",
             "explanation": "Powers of $t$ first, then constants."},
            {"title": "Input $e^{2t}$: resonance", "relation": "caution",
             "tex": r"P(2) = 0 \;\Rightarrow\; y_p = \frac{t\,e^{2t}}{P'(2)} = t\,e^{2t}",
             "explanation": "$e^{2t}$ is a null solution, so $Ye^{2t}$ gives zero. Multiply by $t$."},
        ],
    },
    {
        "id": "vp-wronskian",
        "scene": "VPWronskianSequence",
        "section": 4,
        "title": "Varying the constants: two equations and the Wronskian",
        "summary": "Write the two conditions as a $2\\times2$ system and solve by Cramer's rule.",
        "initial": {"title": "Let the constants move", "tex": r"y = c_1(t)\,y_1 + c_2(t)\,y_2",
                    "explanation": "$y_1, y_2$ are null solutions."},
        "steps": [
            {"title": "Two conditions", "relation": "define",
             "tex": r"\begin{bmatrix} y_1 & y_2 \\ y_1' & y_2' \end{bmatrix}\begin{bmatrix} c_1' \\ c_2' \end{bmatrix} = \begin{bmatrix} 0 \\ f \end{bmatrix}",
             "explanation": "The first keeps $y'$ simple; the second makes $y$ solve the equation."},
            {"title": "The determinant", "relation": "compute",
             "tex": r"W = y_1y_2' - y_2y_1'",
             "explanation": "The Wronskian is nonzero for independent null solutions."},
            {"title": "Cramer's rule", "relation": "solve",
             "tex": r"c_1' = -\frac{y_2 f}{W},\qquad c_2' = \frac{y_1 f}{W}",
             "explanation": "Replace a column by the right side and divide by $W$; then integrate."},
        ],
    },
    {
        "id": "vp-convolution",
        "scene": "VPConvolutionSequence",
        "section": 4,
        "title": "Each input starts its own impulse response",
        "summary": "For constant coefficients the answer is $\\int_0^t g(t - T)f(T)\\,dT$: a sum of delayed, scaled copies of $g$.",
        "initial": {"title": "Impulse response", "tex": r"g(t) = \frac{e^{s_2t} - e^{s_1t}}{s_2 - s_1}",
                    "explanation": "Example $y'' + 3y' + 2y$: $g = e^{-t} - e^{-2t}$."},
        "steps": [
            {"title": "Inputs at times $T$", "relation": "model",
             "tex": r"f(T)\,dT \;\longrightarrow\; f(T)\,g(t - T)\,dT",
             "explanation": "A slice of input at time $T$ responds like a small impulse."},
            {"title": "Add the responses", "relation": "compute",
             "tex": r"y(t) = \int_0^t g(t - T)\,f(T)\,dT",
             "explanation": "Superposition: the equation is linear."},
            {"title": "Example $f = 1$", "relation": "compare",
             "tex": r"y = \int_0^t g = \tfrac12 - e^{-t} + \tfrac12e^{-2t}",
             "explanation": "With a constant input the sum is the step response of Unit 3."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
