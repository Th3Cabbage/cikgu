"""Step-by-step content of the Unit 12 animations, Tumbling Box, Predator-Prey and Chaos (pure data).

Each sequence is one ManimGL scene in sequence_scenes.py. State 0 is the opening picture; step k
is the transition from state k-1 to state k. `tex` is the display formula of the state a step
reaches. `section` is the course section (1-3). Explanations are original paraphrases of Cleve
Moler's MIT Learn Differential Equations videos 66-68 and Strang, Section 3.3.

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
        "id": "box-axes",
        "scene": "BoxAxesSequence",
        "section": 1,
        "title": "Three starts: two steady spins and one flip",
        "summary": "Time plots from starts near the short, long and middle axes.",
        "initial": {"title": "The box equations", "tex": r"x' = yz,\quad y' = -2xz,\quad z' = xy",
                    "explanation": "Starts are unit vectors close to one axis."},
        "steps": [
            {"title": "Near the short axis", "relation": "compute",
             "tex": r"x \approx 1,\quad y, z \text{ small},\ \text{period} \approx \frac{2\pi}{\sqrt2}",
             "explanation": "Small oscillations: a steady spin."},
            {"title": "Near the long axis", "relation": "compute",
             "tex": r"z \approx 1,\quad x, y \text{ small}",
             "explanation": "Also a steady spin."},
            {"title": "Near the middle axis", "relation": "caution",
             "tex": r"y:\ +1 \to -1 \to +1",
             "explanation": "The box flips over and back: the middle axis is unstable."},
        ],
    },
    {
        "id": "predprey-cycle",
        "scene": "PredPreyCycleSequence",
        "section": 2,
        "title": "Predator-prey: a closed cycle around $(\\mu_1, \\mu_2)$",
        "summary": "With $\\mu = (300, 200)$ from $(400, 100)$: prey peak, then predators peak, and the orbit closes after about $6.5$.",
        "initial": {"title": "The model", "tex": r"y_1' = y_1\left(1 - \frac{y_2}{\mu_2}\right),\quad y_2' = -y_2\left(1 - \frac{y_1}{\mu_1}\right)",
                    "explanation": "$\\mu_1 = 300$, $\\mu_2 = 200$, start $(400, 100)$."},
        "steps": [
            {"title": "Time series", "relation": "diagram",
             "tex": r"\text{prey peak, then predator peak}",
             "explanation": "Predators lag behind the prey they eat."},
            {"title": "Phase plane", "relation": "diagram",
             "tex": r"(y_1, y_2) \text{ circles } (\mu_1, \mu_2)",
             "explanation": "Counterclockwise around the critical point."},
            {"title": "Why it closes", "relation": "implies",
             "tex": r"H = \ln y_1 - \frac{y_1}{\mu_1} + \ln y_2 - \frac{y_2}{\mu_2} = \text{constant},\quad T \approx 6.5",
             "explanation": "A conserved quantity; small orbits have period $2\\pi$, this large one a little more."},
        ],
    },
    {
        "id": "lorenz-butterfly",
        "scene": "LorenzButterflySequence",
        "section": 3,
        "title": "The butterfly and the butterfly effect",
        "summary": "The Lorenz solution winds around two critical points; a second start $10^{-6}$ away stays close, then separates.",
        "initial": {"title": "Lorenz", "tex": r"x' = 10(y - x),\quad y' = 28x - y - xz,\quad z' = xy - \tfrac83 z",
                    "explanation": "Critical points $(\\pm8.49, \\pm8.49, 27)$."},
        "steps": [
            {"title": "The attractor", "relation": "diagram",
             "tex": r"(x, z) \text{ projection}",
             "explanation": "Loops around one critical point, then the other, irregularly."},
            {"title": "A second start", "relation": "compare",
             "tex": r"x(0) + 10^{-6}",
             "explanation": "Indistinguishable at first."},
            {"title": "Separation", "relation": "caution",
             "tex": r"|y_A - y_B| \text{ grows to the size of the attractor}",
             "explanation": "Sensitive dependence: long-range prediction fails."},
        ],
    },
]

SECTION_SEQUENCES = {}
for _s in SEQUENCES:
    SECTION_SEQUENCES.setdefault(_s["section"], []).append(_s["id"])
