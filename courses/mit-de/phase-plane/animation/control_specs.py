"""Step-by-step content of the Unit 6 animations, Phase Plane, Linearization and Stability (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-6). Explanations are original paraphrases of Gilbert
Strang's MIT Learn Differential Equations videos 27-34 and Strang, Chapter 3.

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
        "id": "direction-field",
        "scene": "DirectionFieldSequence",
        "section": 1,
        "title": "Arrows first, then solutions: $y' = 2 - y$",
        "summary": "Rows of arrows with slopes $2, 1, 0, -2$; solutions follow them to the steady line $y = 2$.",
        "initial": {"title": "The equation", "tex": r"\frac{dy}{dt} = 2 - y",
                    "explanation": "The slope depends only on the height $y$."},
        "steps": [
            {"title": "Arrows along rows", "relation": "diagram",
             "tex": r"y = 0:\ 2,\quad y = 1:\ 1,\quad y = 2:\ 0,\quad y = 4:\ -2",
             "explanation": "Each arrow has slope $2 - y$."},
            {"title": "The steady line", "relation": "implies",
             "tex": r"y = 2:\ \ y' = 0",
             "explanation": "Flat arrows: a constant solution."},
            {"title": "Solutions follow the arrows", "relation": "solve",
             "tex": r"y = 2 + C e^{-t}",
             "explanation": "From above and below, every solution approaches $2$."},
        ],
    },
    {
        "id": "source-sink-saddle",
        "scene": "SourceSinkSaddleSequence",
        "section": 2,
        "title": "Straight-line solutions in the $(y, y')$ plane",
        "summary": "Real roots give lines $y' = sy$; their signs make a source, a sink or a saddle.",
        "initial": {"title": "Phase plane", "tex": r"y'' - 3y' + 2y = 0,\qquad s = 1,\ 2",
                    "explanation": "Axes $y$ and $y'$; time is hidden."},
        "steps": [
            {"title": "Two lines", "relation": "diagram",
             "tex": r"y = c_1e^{t}:\ y' = y,\qquad y = c_2e^{2t}:\ y' = 2y",
             "explanation": "A pure exponential keeps $y'/y = s$ fixed."},
            {"title": "A source", "relation": "classify",
             "tex": r"y = e^{t} + e^{2t}:\ (2, 3) \text{ at } t = 0",
             "explanation": "Leaves the origin along slope $1$, turns to slope $2$: everything moves out."},
            {"title": "A saddle: $y'' = 4y$", "relation": "classify",
             "tex": r"s = \pm 2:\ \text{in along } y' = -2y,\ \text{out along } y' = 2y",
             "explanation": "Opposite signs: trajectories come in, then leave. Unstable."},
        ],
    },
    {
        "id": "spiral-center",
        "scene": "SpiralCenterSequence",
        "section": 3,
        "title": "Complex roots: ellipse, then spirals",
        "summary": "Pure imaginary roots close the curve; a real part makes it spiral in or out.",
        "initial": {"title": "No damping", "tex": r"y'' + 4y = 0,\qquad s = \pm 2i",
                    "explanation": "$y = \\cos 2t$, $y' = -2\\sin 2t$."},
        "steps": [
            {"title": "A center", "relation": "diagram",
             "tex": r"y^2 + \left(\frac{y'}{2}\right)^2 = 1",
             "explanation": "The point goes round an ellipse twice as tall as wide."},
            {"title": "Damping: a spiral sink", "relation": "diagram",
             "tex": r"y'' + 2y' + 2y = 0,\quad s = -1 \pm i",
             "explanation": "Rotation times $e^{-t}$: the curve winds into the origin."},
            {"title": "Six pictures", "relation": "classify",
             "tex": r"\text{source, sink, saddle, spiral source, spiral sink, center}",
             "explanation": "Real roots give the first three, complex roots the last three."},
        ],
    },
    {
        "id": "trace-determinant",
        "scene": "TraceDeterminantSequence",
        "section": 4,
        "title": "Stability from the trace and the determinant",
        "summary": "$\\lambda^2 - T\\lambda + D = 0$ places every $2\\times2$ matrix in the $(T, D)$ plane.",
        "initial": {"title": "A 2 by 2 system", "tex": r"\mathbf{z}' = A\mathbf{z},\qquad A = \begin{bmatrix}a & b\\ c & d\end{bmatrix}",
                    "explanation": "Try $\\mathbf{z} = e^{\\lambda t}\\mathbf{x}$."},
        "steps": [
            {"title": "Characteristic equation", "relation": "compute",
             "tex": r"\det(A - \lambda I) = \lambda^2 - (a + d)\lambda + (ad - bc) = 0",
             "explanation": "Sum of eigenvalues $T = a + d$; product $D = ad - bc$."},
            {"title": "The $(T, D)$ plane", "relation": "diagram",
             "tex": r"D < 0:\ \text{saddle};\quad T^2 < 4D:\ \text{spiral};\quad T^2 > 4D > 0:\ \text{node}",
             "explanation": "The parabola $T^2 = 4D$ separates real from complex eigenvalues."},
            {"title": "The stable quarter", "relation": "implies",
             "tex": r"\text{stable} \;\Leftrightarrow\; T < 0 \text{ and } D > 0",
             "explanation": "Example $\\begin{bmatrix}1 & 2\\\\ -3 & -4\\end{bmatrix}$: $T = -3$, $D = 2$, a sink."},
        ],
    },
    {
        "id": "jacobian-predprey",
        "scene": "JacobianPredPreySequence",
        "section": 5,
        "title": "Linearizing predator-prey with the Jacobian",
        "summary": "Partial derivatives, then the matrix at each critical point.",
        "initial": {"title": "Rabbits and foxes", "tex": r"y' = y - yz,\qquad z' = yz - z",
                    "explanation": "Critical points: $(0, 0)$ and $(1, 1)$."},
        "steps": [
            {"title": "Partial derivatives", "relation": "compute",
             "tex": r"J = \begin{bmatrix}1 - z & -y\\ z & y - 1\end{bmatrix}",
             "explanation": "Row 1 differentiates $f = y - yz$, row 2 $g = yz - z$."},
            {"title": "At $(0, 0)$", "relation": "substitute",
             "tex": r"J = \begin{bmatrix}1 & 0\\ 0 & -1\end{bmatrix}:\ \lambda = 1, -1\ \ \text{(saddle)}",
             "explanation": "Rabbits alone grow, foxes alone die."},
            {"title": "At $(1, 1)$", "relation": "substitute",
             "tex": r"J = \begin{bmatrix}0 & -1\\ 1 & 0\end{bmatrix}:\ \lambda = \pm i\ \ \text{(center)}",
             "explanation": "The populations cycle around $(1, 1)$."},
        ],
    },
    {
        "id": "tumbling-box",
        "scene": "TumblingBoxSequence",
        "section": 6,
        "title": "The tumbling box: a sphere and a saddle",
        "summary": "Multiply and add to find the sphere; the Jacobian at the middle axis has eigenvalues $0, \\pm1$.",
        "initial": {"title": "Euler's equations (simplest form)", "tex": r"x' = yz,\quad y' = -2xz,\quad z' = xy",
                    "explanation": "Spins about the short, middle and long axes."},
        "steps": [
            {"title": "Conserved length", "relation": "compute",
             "tex": r"xx' + yy' + zz' = xyz - 2xyz + xyz = 0",
             "explanation": "So $x^2 + y^2 + z^2$ is constant: motion on a sphere."},
            {"title": "Jacobian at $(1, 0, 0)$", "relation": "substitute",
             "tex": r"\lambda = 0,\ \pm i\sqrt2\quad\text{(steady spin)}",
             "explanation": "Imaginary eigenvalues: a center."},
            {"title": "Jacobian at $(0, 1, 0)$", "relation": "substitute",
             "tex": r"J = \begin{bmatrix}0 & 0 & 1\\ 0 & 0 & 0\\ 1 & 0 & 0\end{bmatrix}:\ \lambda = 0,\ 1,\ -1",
             "explanation": "A saddle: the middle-axis spin tumbles."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
