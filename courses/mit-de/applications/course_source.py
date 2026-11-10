"""Source of courses/mit-de/applications/dist/course.json (notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe courses\\mit-de\\applications\\course_source.py

Unit 12 of the MIT Learn Differential Equations companion: playlist videos 66-68 (Cleve Moler,
MIT OpenCourseWare) and Strang, Differential Equations and Linear Algebra, Section 3.3 and its
problems. All text is original, written for this guide; it paraphrases the lectures and the book
without quoting. Examples marked "authored" are not from the lectures. Book references give
printed pages; the local PDF page is printed + 12. MATLAB is not needed: the explorer integrates
the equations in JavaScript.
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
    (66, "ttCKLZ2fWWE", "Tumbling Box", "9:52"),
    (67, "zrFJKy5l_PY", "Predator-Prey Equations", "14:17"),
    (68, "Q_f1vRLAENA", "Lorenz Attractor and Chaos", "10:25"),
]

SECTIONS = [
    {
        "nav": "Tumbling box",
        "v": 66,
        "title": r"Computing the tumbling box: orbits on a sphere",
        "summary": r"Moler integrates $x' = yz$, $y' = -2xz$, $z' = xy$ from starts near each axis. Near $(\pm1, 0, 0)$ and $(0, 0, \pm1)$ the solution circles close by; near $(0, 1, 0)$ it swings all the way to $(0, -1, 0)$ and back. Because $x^2 + y^2 + z^2$ is conserved, every orbit lies on the unit sphere.",
        "time": [0, 592],
        "goals": [
            r"Set up the box equations for an ODE solver.",
            r"Interpret the time plots from starts near each axis.",
            r"See the orbits on the sphere and the separatrices through the middle axis."
        ],
        "notes": [
            {"heading": "The computation",
             "paragraphs": [
                 r"The state is $y = (x, y, z)$, the spin about the short, middle and long axes, and $f = (yz, -2xz, xy)$ (Unit 6). Moler starts at a random unit vector near $(1, 0, 0)$: $(1, 0, 0)$ plus a small random perturbation, normalised to length $1$. He integrates with ode23 on $0 \le t \le 10$; the problem is not stiff."
             ]},
            {"heading": "What the plots show",
             "paragraphs": [
                 r"Near the short axis $(1, 0, 0)$, $x$ stays near $1$ while $y$ and $z$ oscillate with small amplitude: a stable spin. The same near the long axis $(0, 0, 1)$. Near the middle axis $(0, 1, 0)$ the component $y$ moves all the way from about $+1$ to about $-1$ and back, again and again: the box flips over. The motion is periodic but far from the starting spin: unstable.",
                 r"Since $x^2 + y^2 + z^2$ stays $1$, the orbits are curves on the unit sphere: small loops around the stable axes and, through the unstable points $(0, \pm1, 0)$, the separating curves. Starts near the middle axis follow those separatrices almost all the way around."
             ]}
        ],
        "keyIdeas": [
            r"$f = (yz, -2xz, xy)$; start near an axis, normalised.",
            r"Short and long axes: small oscillations (stable).",
            r"Middle axis: $y$ swings from $+1$ to $-1$ (tumbles).",
            r"Orbits lie on the unit sphere."
        ],
        "example": {
            "title": "Small oscillations about the short axis (authored)",
            "problem": r"Near $(1, 0, 0)$, let $x \approx 1$ and linearize. What frequency do $y$ and $z$ oscillate at?",
            "steps": [
                {"text": "With x = 1, the y and z equations become linear.", "tex": r"y' = -2z,\qquad z' = y"},
                {"text": "Differentiate the second and substitute.", "tex": r"z'' = y' = -2z"},
                {"text": "Harmonic motion.", "tex": r"\omega = \sqrt2,\qquad T = \frac{2\pi}{\sqrt2} \approx 4.44"}
            ],
            "answer": r"$y$ and $z$ oscillate with period about $4.44$, matching the eigenvalues $\pm i\sqrt2$ of Unit 6."
        },
        "sources": {
            "video": [vs(66, 0, "Throwing a box; the equations"),
                      vs(66, 60, "Start near (1, 0, 0), normalised"),
                      vs(66, 120, "Smaller perturbation"),
                      vs(66, 150, "Start near (0, 0, 1)"),
                      vs(66, 180, "Start near (0, 1, 0): y goes to -1 and back"),
                      vs(66, 270, "Stable x and z, unstable y"),
                      vs(66, 330, "Orbits on the unit sphere"),
                      vs(66, 390, "Orbits around each axis")],
            "book": [bk(176, "A special 3 by 3 system: a tumbling box")]
        },
        "tutorNotes": "Video 66. Tumbling box x' = yz, y' = -2xz, z' = xy, start near an axis plus a small random perturbation normalised to length 1, ode23 on [0, 10]. Near (1,0,0) and (0,0,1): small oscillations (period 2 pi/sqrt2 ~ 4.44 near (1,0,0)). Near (0,1,0): y swings between about +1 and -1 (tumbling). x^2 + y^2 + z^2 = 1: orbits on the unit sphere; separatrices through (0, +-1, 0)."
    },
    {
        "nav": "Predator and prey",
        "v": 67,
        "title": r"Lotka-Volterra: $y_1' = y_1(1 - y_2/\mu_2)$, $y_2' = -y_2(1 - y_1/\mu_1)$",
        "summary": r"Prey $y_1$ grow and are eaten; predators $y_2$ starve without prey and grow by eating. The fixed point is $(\mu_1, \mu_2)$; near it the orbits are ellipses with period $2\pi$. Far from it they are still closed curves, because $\ln y_1 - y_1/\mu_1 + \ln y_2 - y_2/\mu_2$ is conserved, but the period is longer. Moler's run with $\mu = (300, 200)$ from $(400, 100)$ has period about $6.5$.",
        "time": [0, 857],
        "goals": [
            r"Explain each term of the predator-prey equations.",
            r"Find the critical point and its linearization (eigenvalues $\pm i$).",
            r"Use the conserved quantity to show the orbits close.",
            r"Measure the period with an event."
        ],
        "notes": [
            {"heading": "The model",
             "paragraphs": [
                 r"With time and population units chosen so the growth and death rates are $1$: $y_1' = y_1(1 - y_2/\mu_2)$ says prey grow exponentially unless predators approach $\mu_2$; $y_2' = -y_2(1 - y_1/\mu_1)$ says predators die out unless prey exceed $\mu_1$. Four parameters: $\mu_1, \mu_2$ and the initial values $\eta_1, \eta_2$."
             ]},
            {"heading": "Critical point and period",
             "paragraphs": [
                 r"Both right sides vanish at $(\mu_1, \mu_2)$ (and at the origin). The Jacobian there is $\begin{bmatrix}0 & -\mu_1/\mu_2\\ \mu_2/\mu_1 & 0\end{bmatrix}$, with eigenvalues $\pm i$: a center, so nearby orbits are close to ellipses with period $2\pi \approx 6.28$. Moler's GUI shows $6.2867$ for a start near the critical point. Far away the orbits are not ellipses and the period is longer."
             ]},
            {"heading": "Why the orbits close",
             "paragraphs": [
                 r"Divide the equations: $\dfrac{dy_1}{dy_2} = \dfrac{y_1(1 - y_2/\mu_2)}{-y_2(1 - y_1/\mu_1)}$, which separates into $\left(\tfrac{1}{y_1} - \tfrac{1}{\mu_1}\right)dy_1 = -\left(\tfrac{1}{y_2} - \tfrac{1}{\mu_2}\right)dy_2$. Integrating, $H = \ln y_1 - \tfrac{y_1}{\mu_1} + \ln y_2 - \tfrac{y_2}{\mu_2}$ is constant along every solution, and its level curves are closed loops around $(\mu_1, \mu_2)$, where $H$ is largest."
             ]},
            {"heading": "Computing the period",
             "paragraphs": [
                 r"With $\mu = (300, 200)$ and $\eta = (400, 100)$, ode45 with a tight tolerance shows populations cycling with period about $6.5$. Moler measures it with an event function (pitstop) that stops the integration when the solution returns to its starting angle around $(\mu_1, \mu_2)$."
             ]}
        ],
        "keyIdeas": [
            r"Critical point $(\mu_1, \mu_2)$; eigenvalues $\pm i$.",
            r"Near it: ellipses, period $2\pi$.",
            r"$H = \ln y_1 - y_1/\mu_1 + \ln y_2 - y_2/\mu_2$ is conserved.",
            r"Large orbits: closed, period longer than $2\pi$."
        ],
        "example": {
            "title": "Linearize at the fixed point (authored)",
            "problem": r"Compute the Jacobian at $(\mu_1, \mu_2)$ and its eigenvalues.",
            "steps": [
                {"text": "Partial derivatives of f1 = y1 - y1 y2/mu2 and f2 = -y2 + y1 y2/mu1.", "tex": r"J = \begin{bmatrix}1 - y_2/\mu_2 & -y_1/\mu_2\\ y_2/\mu_1 & -1 + y_1/\mu_1\end{bmatrix}"},
                {"text": "At (mu1, mu2) the diagonal vanishes.", "tex": r"J = \begin{bmatrix}0 & -\mu_1/\mu_2\\ \mu_2/\mu_1 & 0\end{bmatrix}"},
                {"text": "Trace 0, determinant 1.", "tex": r"\lambda^2 + 1 = 0 \;\Rightarrow\; \lambda = \pm i"}
            ],
            "answer": r"A center with period $2\pi$ for small orbits, whatever $\mu_1, \mu_2$ are."
        },
        "sources": {
            "video": [vs(67, 0, "Lotka-Volterra predator-prey"),
                      vs(67, 30, "Prey y1, predators y2, unit coefficients"),
                      vs(67, 150, "Four parameters mu and eta"),
                      vs(67, 180, "Critical point (mu1, mu2)"),
                      vs(67, 240, "Locally periodic, period 2 pi"),
                      vs(67, 300, "ode45 run from (400, 100)"),
                      vs(67, 390, "Tolerance and three periods"),
                      vs(67, 450, "Event function pitstop"),
                      vs(67, 600, "predprey GUI")],
            "book": [bk(172, "Predator-prey and its critical points"),
                     bk(174, "The conserved quantity and closed orbits")]
        },
        "tutorNotes": "Video 67. y1' = y1(1 - y2/mu2), y2' = -y2(1 - y1/mu1); critical points (mu1, mu2) and (0, 0). Jacobian at (mu1, mu2): [0, -mu1/mu2; mu2/mu1, 0], eigenvalues +-i, small orbits ~ ellipses, period 2 pi (GUI shows 6.2867 near the point). Conserved H = ln y1 - y1/mu1 + ln y2 - y2/mu2: orbits close; large orbits have longer periods. mu = (300, 200), eta = (400, 100): period about 6.5 (event function pitstop). The caption's '100 and 300' at 5:30 should read 400 and 100."
    },
    {
        "nav": "Lorenz and chaos",
        "v": 68,
        "title": r"The Lorenz equations: a strange attractor",
        "summary": r"Lorenz's model $x' = \sigma(y - x)$, $y' = \rho x - y - xz$, $z' = xy - \beta z$ with $\sigma = 10$, $\rho = 28$, $\beta = \tfrac83$ never settles and never repeats. Trajectories wind around two unstable critical points $(\pm\eta, \pm\eta, \rho - 1)$, $\eta = \sqrt{\beta(\rho - 1)}$, and nearby starts separate exponentially: the butterfly effect. For some other $\rho$, such as $160$, the motion becomes periodic.",
        "time": [0, 625],
        "goals": [
            r"Write the Lorenz equations and find their critical points.",
            r"Describe the attractor and sensitive dependence on initial conditions.",
            r"See how changing $\rho$ changes chaos to periodic motion."
        ],
        "notes": [
            {"heading": "The equations",
             "paragraphs": [
                 r"Edward Lorenz (1963) reduced a model of convection in the atmosphere to three equations: $x' = \sigma(y - x)$, $y' = \rho x - y - xz$, $z' = xy - \beta z$, with $\sigma = 10$, $\rho = 28$, $\beta = 8/3$. The nonlinear terms are $-xz$ and $xy$.",
                 r"Moler writes the system as $y' = A(y)\,y$ with a matrix whose entries depend on the solution, ordering the state as $(z, x, y)$: $A = \begin{bmatrix}-\beta & 0 & x\\ 0 & -\sigma & \sigma\\ -x & \rho & -1\end{bmatrix}$. A critical point needs $A(u)\,u = 0$. The origin is one. A nonzero critical point needs $A(u)$ to be singular, which happens when $x = \pm\eta$ with $\eta = \sqrt{\beta(\rho - 1)}$; but singularity alone is not enough (for example $(\eta, 0, 0)$ is not an equilibrium), and the equations also force $y = x$ and $z = \rho - 1$. So the nonzero critical points are $(x, y, z) = (\pm\eta, \pm\eta, \rho - 1)$."
             ]},
            {"heading": "Chaos",
             "paragraphs": [
                 r"Starting near a critical point (Moler adds $(3, 2, -4)$), the solution spirals outward around one point, jumps to circle the other, and keeps switching in an irregular pattern: the butterfly-shaped Lorenz attractor. The motion is bounded but not periodic. Two starts that differ by $10^{-6}$ follow each other for a while, then separate completely: long-range prediction is impossible, which was Lorenz's point about weather."
             ]},
            {"heading": "Other values of rho",
             "paragraphs": [
                 r"Moler's GUI offers $\rho = 28, 99.65, 100.5, 160, 350$. For $\rho = 160$ and $350$, after a transient the solution settles onto a periodic orbit; $99.65$ and $100.5$ show more complicated (period-doubled) behaviour. Chaos lives only in certain parameter ranges."
             ]}
        ],
        "keyIdeas": [
            r"$x' = \sigma(y - x)$, $y' = \rho x - y - xz$, $z' = xy - \beta z$.",
            r"Critical points $(\pm\eta, \pm\eta, \rho - 1)$, $\eta = \sqrt{\beta(\rho - 1)}$.",
            r"Bounded, non-periodic, sensitive to initial conditions.",
            r"$\rho = 160$: periodic after a transient."
        ],
        "example": {
            "title": "The critical points for rho = 28 (authored)",
            "problem": r"Find the nonzero critical points of the Lorenz system with $\sigma = 10$, $\rho = 28$, $\beta = 8/3$.",
            "steps": [
                {"text": "x' = 0 forces y = x; then z' = 0 gives x^2 = beta z.", "tex": r"y = x,\qquad z = x^2/\beta"},
                {"text": "y' = 0: rho x - x - x z = 0, so z = rho - 1.", "tex": r"z = 27,\qquad x^2 = \beta(\rho - 1) = 72"},
                {"text": "Both signs.", "tex": r"(x, y, z) = (\pm6\sqrt2,\ \pm6\sqrt2,\ 27) \approx (\pm8.49, \pm8.49, 27)"}
            ],
            "answer": r"$(\pm8.49, \pm8.49, 27)$: the centres of the two wings of the butterfly."
        },
        "sources": {
            "video": [vs(68, 0, "Lorenz 1963 and the butterfly effect"),
                      vs(68, 90, "The equations with sigma, rho, beta"),
                      vs(68, 120, "Matrix form y' = A(y) y"),
                      vs(68, 150, "Critical points where A is singular"),
                      vs(68, 210, "Start near a critical point"),
                      vs(68, 300, "Time series"),
                      vs(68, 330, "lorenzgui: the attractor"),
                      vs(68, 510, "Other values of rho"),
                      vs(68, 540, "rho = 160: periodic")],
            "book": [bk(181, "Problem: the Lorenz equations")]
        },
        "tutorNotes": "Video 68. Lorenz x' = sigma(y - x), y' = rho x - y - xz, z' = xy - beta z, sigma = 10, rho = 28, beta = 8/3. Moler orders the state (z, x, y) and writes y' = A(y) y with A = [-beta 0 x; 0 -sigma sigma; -x rho -1]; critical points need A(u) u = 0: the origin, and nonzero points where A is singular (x = +-eta, eta = sqrt(beta(rho - 1))) with also y = x and z = rho - 1, i.e. (+-eta, +-eta, rho - 1) (~ (+-8.49, +-8.49, 27)); singular A alone is not enough ((eta, 0, 0) is not an equilibrium). Start = critical point + (3, 2, -4), [0, 30]. Chaotic, bounded, not periodic; sensitive dependence. rho menu 28, 99.65, 100.5, 160, 350; 160 periodic after a transient. The caption's 'beta times the square root of rho minus one' should be sqrt(beta(rho - 1))."
    },
]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-box-axis", r"Starting near which axis does the box tumble?", [
        (r"The middle axis $(0, 1, 0)$", True, r"Right. $y$ swings between about $+1$ and $-1$."),
        (r"The short axis $(1, 0, 0)$", False, r"No. Near it the oscillations stay small."),
        (r"The long axis $(0, 0, 1)$", False, r"No. That spin is stable too."),
        (r"All three", False, r"No. Only the middle axis is a saddle.")]),
    q("q-box-sphere", r"Why do the computed box orbits lie on a sphere?", [
        (r"$xx' + yy' + zz' = 0$, so $x^2 + y^2 + z^2$ stays constant.", True, r"Right. The start is normalised to length $1$, so the radius stays $1$."),
        (r"Because the solver projects onto the sphere.", False, r"No. The conservation comes from the equations themselves."),
        (r"Because $x$, $y$, $z$ are always between $-1$ and $1$.", False, r"No. That is a consequence, not the reason."),
        (r"They do not; they spiral outwards.", False, r"No. An accurate solver keeps them on the sphere.")]),
    q("q-box-period", r"Near $(1, 0, 0)$, the linearized box equations are $y' = -2z$, $z' = y$. What is the period?", [
        (r"$2\pi/\sqrt2 \approx 4.44$", True, r"Right. $z'' = -2z$."),
        (r"$2\pi$", False, r"No. The factor $2$ changes the frequency to $\sqrt2$."),
        (r"$\pi$", False, r"No. That would need $\omega = 2$."),
        (r"There is no oscillation.", False, r"No. The eigenvalues are $\pm i\sqrt2$.")]),
    q("q-pp-fixed", r"What is the nonzero critical point of $y_1' = y_1(1 - y_2/\mu_2)$, $y_2' = -y_2(1 - y_1/\mu_1)$?", [
        (r"$(\mu_1, \mu_2)$", True, r"Right. Both brackets vanish there."),
        (r"$(\mu_2, \mu_1)$", False, r"No. $y_1' = 0$ needs $y_2 = \mu_2$."),
        (r"$(1, 1)$", False, r"No. That is the unscaled model of Unit 6."),
        (r"$(\eta_1, \eta_2)$", False, r"No. Those are the initial values.")]),
    q("q-pp-period", r"What is the period of small orbits around $(\mu_1, \mu_2)$?", [
        (r"$2\pi$", True, r"Right. The Jacobian has eigenvalues $\pm i$ for every $\mu$."),
        (r"$2\pi\mu_1/\mu_2$", False, r"No. The determinant of the Jacobian is $1$ regardless of $\mu$."),
        (r"$6.5$ for every orbit", False, r"No. $6.5$ is for the large orbit from $(400, 100)$; larger orbits take longer."),
        (r"It depends on the initial values only.", False, r"No. Small orbits all have period close to $2\pi$.")]),
    q("q-pp-closed", r"Why are predator-prey orbits closed curves?", [
        (r"$H = \ln y_1 - y_1/\mu_1 + \ln y_2 - y_2/\mu_2$ is constant along solutions, and its level curves are closed.", True, r"Right. A conserved quantity traps each orbit on one loop."),
        (r"Because the critical point is stable.", False, r"No. A linear center alone does not prove closure for a nonlinear system."),
        (r"Because ode45 is accurate.", False, r"No. Accuracy shows it numerically; the conserved quantity proves it."),
        (r"Because populations are positive.", False, r"No. Positivity alone does not close the orbits.")]),
    q("q-lorenz-cp", r"For $\sigma = 10$, $\rho = 28$, $\beta = 8/3$, what is $z$ at the nonzero critical points?", [
        (r"$27$", True, r"Right. $z = \rho - 1$."),
        (r"$28$", False, r"No. $y' = 0$ gives $x(\rho - 1 - z) = 0$."),
        (r"$8/3$", False, r"No. $\beta$ enters $x^2 = \beta z$."),
        (r"$72$", False, r"No. $72$ is $x^2 = \beta(\rho - 1)$.")]),
    q("q-chaos", r"What does sensitive dependence on initial conditions mean for the Lorenz system?", [
        (r"Two starts $10^{-6}$ apart eventually follow completely different paths.", True, r"Right. Small differences grow exponentially until they are as large as the attractor."),
        (r"The solution blows up.", False, r"No. Lorenz solutions stay bounded."),
        (r"The solution is periodic.", False, r"No. For $\rho = 28$ it never repeats."),
        (r"Numerical methods cannot compute it at all.", False, r"No. They compute it well for a while; long-term details are what cannot be trusted.")]),
    q("q-lorenz-rho", r"What happens for $\rho = 160$?", [
        (r"After a transient, the solution settles onto a periodic orbit.", True, r"Right. Chaos occurs only for some ranges of $\rho$."),
        (r"It is chaotic, like $\rho = 28$.", False, r"No. Moler shows periodic behaviour for $\rho = 160$."),
        (r"It goes to the origin.", False, r"No. The origin is unstable for $\rho > 1$."),
        (r"It blows up.", False, r"No. The solutions stay bounded.")]),
    q("q-lorenz-nonlinear", r"Which terms make the Lorenz system nonlinear?", [
        (r"$-xz$ in $y'$ and $xy$ in $z'$", True, r"Right. Every other term is linear."),
        (r"$\sigma(y - x)$", False, r"No. That is linear."),
        (r"$-\beta z$", False, r"No. That is linear."),
        (r"$\rho x$", False, r"No. That is linear.")]),
]

EXPLORER = {
    "modes": [
        {"id": "box", "label": "Tumbling box"},
        {"id": "pp", "label": "Predator-prey"},
        {"id": "lorenz", "label": "Lorenz attractor"}
    ],
    "defaultMode": "lorenz",
    "rho": {"options": [28, 99.65, 100.5, 160, 350], "default": 28},
    "eps": {"min": -9, "max": -1, "step": 1, "default": -6},
    "tEnd": {"min": 5, "max": 60, "step": 1, "default": 30},
    "axis": {"options": ["x", "y", "z"], "default": "y"},
    "perturb": {"min": 0.01, "max": 0.4, "step": 0.01, "default": 0.1},
    "mu1": {"min": 100, "max": 500, "step": 10, "default": 300},
    "mu2": {"min": 100, "max": 500, "step": 10, "default": 200},
    "eta1": {"min": 20, "max": 800, "step": 10, "default": 400},
    "eta2": {"min": 20, "max": 800, "step": 10, "default": 100},
    "presets": [
        {"id": "lorenz28", "label": "Lorenz, ρ = 28", "mode": "lorenz", "rho": 28, "eps": -6, "tEnd": 30,
         "note": "Section 3: two starts $10^{-6}$ apart; watch them separate."},
        {"id": "lorenz160", "label": "Lorenz, ρ = 160", "mode": "lorenz", "rho": 160, "eps": -6, "tEnd": 30,
         "note": "Section 3: periodic after a transient."},
        {"id": "boxmid", "label": "Box near the middle axis", "mode": "box", "axis": "y", "perturb": 0.1, "tEnd": 30,
         "note": "Section 1: $y$ swings from $+1$ to $-1$."},
        {"id": "boxshort", "label": "Box near the short axis", "mode": "box", "axis": "x", "perturb": 0.1, "tEnd": 30,
         "note": "Section 1: small oscillations, period about $4.44$."},
        {"id": "pp", "label": "Moler's predator-prey", "mode": "pp", "mu1": 300, "mu2": 200, "eta1": 400, "eta2": 100, "tEnd": 25,
         "note": "Section 2: period about $6.5$; $H$ stays constant."},
        {"id": "ppsmall", "label": "Near the fixed point", "mode": "pp", "mu1": 300, "mu2": 200, "eta1": 310, "eta2": 200, "tEnd": 25,
         "note": "Section 2: a small orbit; period close to $2\\pi$."}
    ],
    "tutorContext": "Three modes, integrated in JavaScript by classical RK4 with step 0.002 (Lorenz, box) or 0.001 (predator-prey) and drawn progressively (a comet that can be paused). Tumbling box: x' = yz, y' = -2xz, z' = xy from (1,0,0), (0,1,0) or (0,0,1) plus a fixed perturbation of size 'perturb', normalised to length 1; shows the three time series and the orbit on the sphere (orthographic view, slowly rotatable), with x^2 + y^2 + z^2 reported. Predator-prey: y1' = y1(1 - y2/mu2), y2' = -y2(1 - y1/mu1) with mu1, mu2, eta1, eta2 sliders; phase plane and time series, the conserved H, the critical point, and the measured period (time between successive returns to the starting angle around (mu1, mu2)). Lorenz: sigma = 10, beta = 8/3, rho from the list 28, 99.65, 100.5, 160, 350; start = critical point (eta, eta, rho - 1) + (3, 2, -4) and a second start shifted by 10^eps in x; shows the x-z projection (butterfly), the x time series of both runs and log10 of their distance against time."
}

COURSE = {
    "version": 1,
    "title": "Tumbling Box, Predator-Prey and Chaos",
    "subtitle": "Unit 12 of a study companion to MIT Learn Differential Equations (Cleve Moler), videos 66-68, with Strang's Differential Equations and Linear Algebra, Section 3.3",
    "video": {"id": VIDEOS[0][1], "title": "MIT Learn Differential Equations, videos 66-68", "duration": "34:34", "url": PLAYLIST},
    "videos": [{"n": n, "id": vid, "title": title, "duration": dur, "url": f"https://www.youtube.com/watch?v={vid}"}
               for n, vid, title, dur in VIDEOS],
    "book": {"title": "Differential Equations and Linear Algebra", "authors": "Gilbert Strang", "short": "Strang, 3.3",
             "edition": "Wellesley-Cambridge Press, 2014 (Section 3.3 and problems)", "onlineUrl": "",
             "pageNote": "Page references give the printed page and the page of the local PDF (printed page + 12). The book is not freely available online, so only a local copy can be opened."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide; examples marked authored are not from the lectures. They summarize MIT OpenCourseWare's Learn Differential Equations videos (Cleve Moler, CC BY-NC-SA) and Strang's textbook; for the original wording, watch the videos and read the book. Captions, video and book text are not included in this guide. MATLAB is not needed: the explorer integrates the equations itself.",
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
