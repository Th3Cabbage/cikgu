"""Step-by-step content of the Stability and Eigenvalues animations (pure data, standard library only).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k is the
transition from state k-1 to state k. The scene calls `self.step_done()` once per step and
build_sequences.py checks that the recorded boundaries match len(steps).

Strings use $...$ for inline math (KaTeX in the browser). `tex` is the display formula of the state a
step reaches; the browser shows it on the step card and as the media fallback, so it must say the same
thing as the stage. `section` is the course section (1-6) a sequence belongs to.

All explanations are original paraphrases written for this guide; they summarize S. L. Brunton's
Control Bootcamp lecture "Stability and Eigenvalues" and Section 8.2 of Brunton & Kutz, "Data-Driven
Science and Engineering" (2017 preprint, pp. 332 and 334), without quoting them. Numerical examples are
authored for this guide. The "boundary-cases" sequence is a Supplement: the lecture does not cover it.

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
    # ------------------------------------------------------------------ section 1
    {
        "id": "modes-mix",
        "scene": "ModesSequence",
        "section": 1,
        "title": "Only $e^{Dt}$ changes with time",
        "summary": "In $x(t) = Te^{Dt}T^{-1}x(0)$ the eigenvector matrices are constant; the diagonal $e^{Dt}$ holds one exponential per eigenvalue, and $x(t)$ is a blend of those modes. One growing mode takes over almost every start.",
        "initial": {
            "title": "The solution from the last lecture",
            "tex": r"x(t) = T\,e^{Dt}\,T^{-1}x(0)",
            "explanation": "With $[T, D] = \\mathrm{eig}(A)$ the solution of $\\dot x = Ax$ is $x(t) = Te^{Dt}T^{-1}x(0)$. Stability asks what this does as $t \\to \\infty$."},
        "steps": [
            {"title": "Only $e^{Dt}$ depends on $t$", "relation": "define",
             "tex": r"x(t) = \underbrace{T}_{\text{const}}\;\underbrace{e^{Dt}}_{\text{changes}}\;\underbrace{T^{-1}x(0)}_{\text{const}}",
             "explanation": "$T$, $T^{-1}$ and $x(0)$ are fixed numbers. Whatever happens as $t \\to \\infty$ must come from $e^{Dt}$."},
            {"title": "$e^{Dt}$ is diagonal", "relation": "identity",
             "tex": r"e^{Dt} = \begin{bmatrix} e^{\lambda_1 t} & & \\ & \ddots & \\ & & e^{\lambda_n t} \end{bmatrix}",
             "explanation": "$D$ holds the eigenvalues on its diagonal, so $e^{Dt}$ holds one exponential $e^{\\lambda_i t}$ per eigenvalue and zeros elsewhere. Each is a mode with its own rate."},
            {"title": "$x(t)$ is a blend of modes", "relation": "compute",
             "tex": r"x(t) = z_1(0)\,e^{\lambda_1 t}c_1 + \cdots + z_n(0)\,e^{\lambda_n t}c_n,\qquad z(0) = T^{-1}x(0)",
             "explanation": "Split $T$ into its eigenvector columns $c_i$ and write $z(0) = T^{-1}x(0)$. Each mode $e^{\\lambda_i t}$ is carried along its eigenvector with the fixed weight $z_i(0)$: the lecturer's mixture."},
            {"title": "One growing mode takes over", "relation": "diagram",
             "tex": r"z_1 = 1,\ z_2 = 0.08:\quad e^{-t} + 0.08\,e^{0.6t} \to \infty",
             "explanation": "Example rates $\\lambda_1 = -1$, $\\lambda_2 = 0.6$ and weights $z_1 = 1$, $z_2 = 0.08$ (the plotted curves). The decaying mode fades while the growing one, however small at first, dominates the blend. Any $z_2 \\neq 0$ makes $|x(t)|$ grow without bound; a random start has $z_2 \\neq 0$."},
            {"title": "Unless the start avoids that mode", "relation": "caution",
             "tex": r"z_2(0) = 0 \;\Rightarrow\; x(t) = z_1(0)\,e^{-t}c_1 \to 0",
             "explanation": "A start with no component along the unstable eigenvector decays. But stability is a property of all starts, so the system is still unstable. Rounding errors or disturbances may still give this start a small unstable component."},
        ],
    },
    # ------------------------------------------------------------------ section 2
    {
        "id": "euler-envelope",
        "scene": "EulerSequence",
        "section": 2,
        "title": "Complex eigenvalues: envelope times rotation",
        "summary": "Euler's formula splits $e^{(a+ib)t}$ into the envelope $e^{at}$ and a factor of size one; the real part decides growth or decay. Conjugate pairs give real solutions.",
        "initial": {
            "title": "A complex eigenvalue",
            "tex": r"\lambda = a + ib",
            "explanation": "Eigenvalues may be complex: real part $a$, imaginary part $b$."},
        "steps": [
            {"title": "Put $\\lambda$ in the exponent", "relation": "substitute",
             "tex": r"e^{\lambda t} = e^{(a + ib)t}",
             "explanation": "The mode of this eigenvalue is $e^{\\lambda t}$. Substitute $\\lambda = a + ib$."},
            {"title": "Split the exponent", "relation": "identity",
             "tex": r"e^{(a+ib)t} = e^{at}\,e^{ibt}",
             "explanation": "$e^{u + v} = e^u e^v$ also holds for complex numbers: a real exponential times a purely imaginary one."},
            {"title": "Euler's formula", "relation": "identity",
             "tex": r"e^{ibt} = \cos bt + i\sin bt",
             "explanation": "$e^{ibt}$ is the point at angle $bt$ on the unit circle. As $t$ grows it just goes round and round."},
            {"title": "The size is $e^{at}$", "relation": "implies",
             "tex": r"|e^{\lambda t}| = e^{at}\,|\cos bt + i\sin bt| = e^{at}",
             "explanation": "$|\\cos bt + i\\sin bt| = 1$ for every $t$, so only the real part $a$ sets the amplitude."},
            {"title": "$a > 0$: growing envelope", "relation": "diagram",
             "tex": r"a = 0.3:\quad e^{at}\cos bt \ \text{inside}\ \pm e^{at}\ \text{(grows)}",
             "explanation": "The real part of the mode oscillates at frequency $b$ inside the envelope $\\pm e^{at}$. With $a > 0$ the envelope grows exponentially: the oscillation blows up."},
            {"title": "$a < 0$: decaying envelope", "relation": "diagram",
             "tex": r"a = -0.5:\quad e^{at}\cos bt \to 0",
             "explanation": "Slide $a$ through zero to $-0.5$: the same oscillation now sits inside a shrinking envelope and decays to zero. $b$ never changes the verdict."},
            {"title": "Conjugate pairs: imaginary parts cancel", "relation": "identity",
             "tex": r"e^{(a+ib)t} + e^{(a-ib)t} = 2e^{at}\cos bt",
             "explanation": "A real $A$ has complex eigenvalues in pairs $a \\pm ib$. Adding the pair, the $\\pm i\\sin bt$ terms cancel and a real oscillation in the envelope remains."},
        ],
    },
    # ------------------------------------------------------------------ section 3
    {
        "id": "left-half-plane",
        "scene": "HalfPlaneSequence",
        "section": 3,
        "title": "The stable left half-plane",
        "summary": "Draw the eigenvalues in the complex plane: all in the open left half-plane means every solution decays; one in the right half-plane means unstable. Control later moves eigenvalues left.",
        "initial": {
            "title": "Where are the eigenvalues?",
            "tex": r"\lambda \in \mathbb{C}",
            "explanation": "Each eigenvalue is a point in the complex plane: real part across, imaginary part up."},
        "steps": [
            {"title": "Eigenvalues as points", "relation": "diagram",
             "tex": r"\lambda_1 = -1,\quad \lambda_{2,3} = -0.5 \pm 1.5i",
             "explanation": "An example with one real eigenvalue and a conjugate pair, mirror images across the real axis."},
            {"title": "Left half-plane: every mode decays", "relation": "classify",
             "tex": r"\mathrm{Re}\,\lambda_i < 0\ \text{for all } i \;\Leftrightarrow\; \text{asymptotically stable}",
             "explanation": "All three eigenvalues have negative real part, so every $e^{\\lambda_i t}$ shrinks and every solution decays to $0$. The lecturer states this as stable if and only if all real parts are negative."},
            {"title": "Cross the axis: unstable", "relation": "classify",
             "tex": r"\mathrm{Re}\,\lambda_{2,3} = 0.4 > 0 \;\Rightarrow\; \text{unstable}",
             "explanation": "Move the pair to $0.4 \\pm 1.5i$. One eigenvalue (here a pair) in the right half-plane is enough: its growing envelope blows up."},
            {"title": "Preview: control moves eigenvalues", "relation": "diagram",
             "tex": r"\dot x = Ax + Bu:\ \text{choose } u \text{ to drag eigenvalues left (later lectures)}",
             "explanation": "As the lecturer sketches at 7:59, the goal of feedback control will be to push unstable eigenvalues back into the left half-plane. How is taught in later lectures."},
            {"title": "The inverted pendulum", "relation": "diagram",
             "tex": r"\text{pendulum up:}\quad \lambda = \pm\sqrt{g/L}\ \Rightarrow\ \text{unstable}",
             "explanation": "The upright pendulum has a positive real eigenvalue, so it falls. The book's example (p. 335) gives $\\lambda = \\pm\\sqrt{g/L}$; here drawn with $g/L = 2.25$."},
        ],
    },
    {
        "id": "boundary-cases",
        "scene": "BoundarySequence",
        "section": 3,
        "title": "Supplement: eigenvalues on the boundary",
        "summary": "Not covered in the lecture. With the largest real part exactly $0$, semisimple eigenvalues give bounded solutions that never decay (Lyapunov stability), while a Jordan block grows like $t$. The discrete-time twin lives on the unit circle.",
        "initial": {
            "title": "Supplement: what if the largest real part is 0?",
            "tex": r"\max_i \mathrm{Re}\,\lambda_i = 0\ ?",
            "explanation": "The lecture's criterion covers strictly negative and positive real parts. This supplement looks at the case in between."},
        "steps": [
            {"title": "Pendulum down: onto the imaginary axis", "relation": "diagram",
             "tex": r"\text{pendulum down:}\quad \lambda = \pm i\sqrt{g/L}",
             "explanation": "Flipping the pendulum to hang down rotates its eigenvalues from $\\pm\\sqrt{g/L}$ to $\\pm i\\sqrt{g/L}$ (book p. 335): exactly on the imaginary axis."},
            {"title": "Semisimple: bounded, never decaying", "relation": "classify",
             "tex": r"e^{Jt} = \begin{bmatrix}\cos\omega t & -\sin\omega t\\ \sin\omega t & \cos\omega t\end{bmatrix},\quad |x(t)| = |x(0)|",
             "explanation": "For $J = \\begin{bmatrix}0&-\\omega\\\\ \\omega&0\\end{bmatrix}$ ($\\lambda = \\pm i\\omega$) the exponential is a rotation: solutions circle forever. Bounded but not decaying: Lyapunov stable, not asymptotically stable."},
            {"title": "Defective: a Jordan block grows", "relation": "caution",
             "tex": r"J = \begin{bmatrix}0&1\\0&0\end{bmatrix}:\quad e^{Jt} = I + Jt = \begin{bmatrix}1&t\\0&1\end{bmatrix}",
             "explanation": "A repeated eigenvalue $0$ with only one eigenvector: $J^2 = 0$, so the series stops after $I + Jt$. Then $x_1(t) = x_1(0) + t\\,x_2(0)$ grows linearly: unstable, with no positive real part anywhere."},
            {"title": "Discrete twin and summary", "relation": "recap",
             "tex": r"|\tilde\lambda| = 1:\ \text{bounded if semisimple};\quad \begin{bmatrix}1&1\\0&1\end{bmatrix}^N = \begin{bmatrix}1&N\\0&1\end{bmatrix}\ \text{grows}",
             "explanation": "On the unit circle the same split happens: semisimple eigenvalues keep $|\\tilde\\lambda^N| = 1$, a Jordan block grows like $N$. Summary: asymptotic needs all strictly inside; boundary is Lyapunov only if semisimple."},
        ],
    },
    # ------------------------------------------------------------------ section 4
    {
        "id": "sampling",
        "scene": "SamplingSequence",
        "section": 4,
        "title": "Sampling: $x_{k+1} = \\tilde A x_k$",
        "summary": "Measuring every $\\Delta t$ turns the flow into a one-step map: $x_{k+1} = e^{A\\Delta t}x_k$, so $x_N = \\tilde A^N x_0$.",
        "initial": {
            "title": "A continuous solution",
            "tex": r"x(t) = e^{At}x(0)",
            "explanation": "The state varies continuously in time. An experiment or a digital controller does not see all of it."},
        "steps": [
            {"title": "Measure every $\\Delta t$", "relation": "define",
             "tex": r"x_k = x(k\,\Delta t),\qquad k = 0, 1, 2, \dots",
             "explanation": "Keep only the values at the sample times $0, \\Delta t, 2\\Delta t, \\dots$ and number them $x_0, x_1, x_2, \\dots$"},
            {"title": "One step is a matrix exponential", "relation": "identity",
             "tex": r"x_{k+1} = e^{A(k+1)\Delta t}x(0) = e^{A\Delta t}\,e^{Ak\Delta t}x(0) = e^{A\Delta t}\,x_k",
             "explanation": "Split the exponential with $e^{A(s+t)} = e^{As}e^{At}$; the right-hand factor applied to $x(0)$ is exactly $x_k$. No approximation is involved."},
            {"title": "Name the step matrix $\\tilde A$", "relation": "define",
             "tex": r"x_{k+1} = \tilde A\,x_k,\qquad \tilde A = e^{A\Delta t}",
             "explanation": "The lecture calls it $\\tilde A$; the book writes $A_d$ (Eq. 8.22a). Each hop from one sample to the next is multiplication by $\\tilde A$."},
            {"title": "Iterate", "relation": "substitute",
             "tex": r"x_1 = \tilde A x_0,\quad x_2 = \tilde A x_1 = \tilde A^2 x_0,\quad x_3 = \tilde A^3 x_0",
             "explanation": "Substitute $x_1 = \\tilde Ax_0$ into $x_2 = \\tilde Ax_1$ to get $\\tilde A^2x_0$, and so on."},
            {"title": "Powers replace the exponential", "relation": "implies",
             "tex": r"x_N = \tilde A^N x_0 \quad\text{vs.}\quad x(t) = e^{At}x(0)",
             "explanation": "In discrete time the question of stability becomes: what happens to $\\tilde A^N$ as $N \\to \\infty$?"},
        ],
    },
    # ------------------------------------------------------------------ section 5
    {
        "id": "powers-unit-circle",
        "scene": "PowersSequence",
        "section": 5,
        "title": "Powers of $\\tilde\\lambda$ and the unit circle",
        "summary": "$\\tilde A^N = \\tilde T\\tilde D^N\\tilde T^{-1}$, and $\\tilde\\lambda^N = r^Ne^{iN\\theta}$: the radius decides. Stable if and only if every eigenvalue is inside the unit circle.",
        "initial": {
            "title": "Powers of the step matrix",
            "tex": r"x_N = \tilde A^N x_0,\qquad \tilde A\tilde T = \tilde T\tilde D",
            "explanation": "Diagonalize $\\tilde A$ exactly like $A$: its eigenvectors go in the columns of $\\tilde T$, its eigenvalues on the diagonal of $\\tilde D$."},
        "steps": [
            {"title": "Solve for $\\tilde A$", "relation": "identity",
             "tex": r"\tilde A\tilde T = \tilde T\tilde D \;\Rightarrow\; \tilde A = \tilde T\tilde D\tilde T^{-1}",
             "explanation": "Multiply on the right by $\\tilde T^{-1}$; $\\tilde T\\tilde T^{-1} = I$ on the left. This is the board derivation at 16:44 (aloud at 12:57 the lecturer says $T^{-1}DT$, unsure of the order)."},
            {"title": "Inner pairs cancel", "relation": "compute",
             "tex": r"\tilde A^3 = \tilde T\tilde D\cancel{\tilde T^{-1}\tilde T}\tilde D\cancel{\tilde T^{-1}\tilde T}\tilde D\tilde T^{-1} = \tilde T\tilde D^3\tilde T^{-1},\qquad \tilde A^N = \tilde T\tilde D^N\tilde T^{-1}",
             "explanation": "Writing $\\tilde A$ three times, each adjacent $\\tilde T^{-1}\\tilde T$ is $I$. Only the diagonal matrix gets powered: $\\tilde D^N = \\mathrm{diag}(\\tilde\\lambda_i^N)$."},
            {"title": "Radius and angle", "relation": "define",
             "tex": r"\tilde\lambda = r\,e^{i\theta},\qquad r = |\tilde\lambda|",
             "explanation": "Any complex number is a radius $r$ and an angle $\\theta$; real part $r\\cos\\theta$, imaginary part $r\\sin\\theta$."},
            {"title": "Powers turn and scale", "relation": "compute",
             "tex": r"\tilde\lambda^N = r^N e^{iN\theta}",
             "explanation": "Each multiplication adds $\\theta$ to the angle and multiplies the radius by $r$. With $r = 0.88$ the powers spiral in; with $r = 1.1$ they spiral out."},
            {"title": "Inside the unit circle", "relation": "classify",
             "tex": r"|\tilde\lambda_i| < 1\ \text{for all } i \;\Leftrightarrow\; \text{asymptotically stable}",
             "explanation": "Stable if and only if every eigenvalue of $\\tilde A$ is strictly inside the unit circle; one outside makes the system unstable."},
            {"title": "Magnitude, not real part", "relation": "caution",
             "tex": r"\tilde\lambda = 0.5 + 0.9i:\ \mathrm{Re} = 0.5 < 1,\ \text{but } |\tilde\lambda| = \sqrt{1.06} \approx 1.03 > 1",
             "explanation": "At 16:10 the lecturer says real part, but the radius is what counts. This eigenvalue has a small real part and still lies outside the circle: unstable."},
        ],
    },
    # ------------------------------------------------------------------ section 6
    {
        "id": "conformal-map",
        "scene": "ConformalSequence",
        "section": 6,
        "title": "$e^{\\lambda\\Delta t}$: left half-plane to unit disc",
        "summary": "The eigenvalues of $e^{A\\Delta t}$ are $e^{\\lambda\\Delta t}$. Vertical lines become circles, the imaginary axis the unit circle, horizontal lines rays: the two stability criteria agree.",
        "initial": {
            "title": "Two complex planes",
            "tex": r"\tilde A = e^{A\Delta t}",
            "explanation": "Left: eigenvalues $\\lambda$ of $A$. Right: eigenvalues $\\tilde\\lambda$ of the sampled $\\tilde A$, with the unit circle."},
        "steps": [
            {"title": "Same eigenvectors, eigenvalues $e^{\\lambda\\Delta t}$", "relation": "identity",
             "tex": r"e^{A\Delta t} = T\,e^{D\Delta t}\,T^{-1} \;\Rightarrow\; \tilde\lambda_i = e^{\lambda_i\Delta t}",
             "explanation": "From $A = TDT^{-1}$, the exponential keeps the eigenvectors and exponentiates each eigenvalue."},
            {"title": "Radius from Re, angle from Im", "relation": "compute",
             "tex": r"e^{(a+ib)\Delta t} = e^{a\Delta t}\,e^{ib\Delta t}:\quad |\tilde\lambda| = e^{a\Delta t},\ \arg\tilde\lambda = b\Delta t",
             "explanation": "Here $\\Delta t = 1$: $\\lambda = -0.5 + 1.2i$ lands at radius $e^{-0.5} \\approx 0.61$ and angle $1.2$ rad."},
            {"title": "Vertical lines become circles", "relation": "diagram",
             "tex": r"\mathrm{Re}\,\lambda = a \;\mapsto\; |\tilde\lambda| = e^{a\Delta t}",
             "explanation": "Every point of the line $\\mathrm{Re}\\,\\lambda = -0.5$ has the same radius after the map, so the line wraps onto a circle of radius $e^{-0.5}$."},
            {"title": "Imaginary axis to unit circle, half-plane to disc", "relation": "diagram",
             "tex": r"\mathrm{Re}\,\lambda = 0 \mapsto |\tilde\lambda| = 1,\qquad \mathrm{Re}\,\lambda < 0 \mapsto |\tilde\lambda| < 1",
             "explanation": "Lines further left give smaller circles; the imaginary axis gives the unit circle. The left half-plane fills the inside of the disc, every point except the centre: $e^{\\lambda\\Delta t}$ is never $0$."},
            {"title": "Horizontal lines become rays", "relation": "diagram",
             "tex": r"\mathrm{Im}\,\lambda = b \;\mapsto\; \arg\tilde\lambda = b\Delta t \pmod{2\pi}",
             "explanation": "Horizontal lines map to rays from the origin (the angle $b\\Delta t$ is taken modulo $2\\pi$). Circles and rays still meet at right angles, as the grid did: the map is conformal."},
            {"title": "The upshot", "relation": "recap",
             "tex": r"\mathrm{Re}\,\lambda < 0 \;\Leftrightarrow\; |e^{\lambda\Delta t}| < 1",
             "explanation": "Continuous time: negative real parts. Discrete time: inside the unit circle. They are the same condition: asymptotic stability depends only on the eigenvalues (exactly on the boundary, the Jordan structure matters too)."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
