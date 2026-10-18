"""Source of stability-eigenvalues/dist/course.json (section notes, worked examples, quiz, explorer config).

    .venv\\Scripts\\python.exe stability-eigenvalues\\course_source.py

Text is original, written for this companion. It paraphrases S. L. Brunton's Control Bootcamp lecture
"Stability and Eigenvalues" and Brunton & Kutz, Section 8.2 (printed pp. 332, 334 and the example on
p. 335), without quoting. The numbers in the worked examples are authored for the guide. Material the
lecture does not cover (eigenvalues exactly on the imaginary axis / unit circle, Jordan blocks, aliasing,
transient growth) is labelled "Supplement".
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dist", "course.json")

B332 = {"printed": 332, "pdf": 352}
B334 = {"printed": 334, "pdf": 354}
B335 = {"printed": 335, "pdf": 355}


def book(ref, label):
    return dict(ref, label=label)


SECTIONS = [
    # ------------------------------------------------------------------ 1
    {
        "nav": "Only the modes evolve",
        "title": r"Stability is decided by $e^{Dt}$",
        "time": [0, 200],
        "summary": r"Recap: with $[T, D] = \mathrm{eig}(A)$ the solution of $\dot x = Ax$ is $x(t) = Te^{Dt}T^{-1}x(0)$. Stability asks what happens as $t \to \infty$. The only factor that changes with time is the diagonal $e^{Dt}$, whose entries $e^{\lambda_i t}$ are the modes that $T$ and $T^{-1}$ mix together.",
        "goals": [
            r"Explain why the eigenvalues alone decide growth or decay, while $T$ only mixes.",
            r"Write $x(t) = \sum_i z_i(0)\,e^{\lambda_i t}\,c_i$ with $z(0) = T^{-1}x(0)$.",
            r"Explain why one growing mode makes almost every solution blow up, and which starts avoid it.",
        ],
        "notes": [
            {"heading": "What this lecture covers",
             "paragraphs": [
                 r"The 19:30 lecture gives what the lecturer calls the bare minimum for stability: continuous time through the real parts of the eigenvalues (Sections 1 to 3), then discrete time, where the eigenvalues must lie inside the unit circle (Sections 4 to 6), and the matrix exponential that links the two pictures. It deliberately skips phase portraits, saddles, nodes and centers, and it assumes, as in the previous lecture, that $A$ has a full set of eigenvectors.",
                 r"Two things are added by this guide and labelled Supplement: what happens when an eigenvalue sits exactly on the boundary (the imaginary axis or the unit circle, including Jordan blocks), and a few numerical cautions. The lecture does not discuss them; the explorer lets you try them.",
             ]},
            {"heading": "Only the diagonal factor moves",
             "paragraphs": [
                 r"In $x(t) = Te^{Dt}T^{-1}x(0)$ the matrices $T$ and $T^{-1}$ are constant. Because $D = \mathrm{diag}(\lambda_1, \dots, \lambda_n)$ is diagonal, $e^{Dt} = \mathrm{diag}(e^{\lambda_1 t}, \dots, e^{\lambda_n t})$: each eigenvalue gets its own exponential and nothing couples them.",
                 r"Write $c_i$ for the columns of $T$ (the eigenvectors) and $z(0) = T^{-1}x(0)$. Multiplying out gives $x(t) = z_1(0)e^{\lambda_1 t}c_1 + \cdots + z_n(0)e^{\lambda_n t}c_n$. This is the lecturer's mixture: every solution is a fixed blend of the modes $e^{\lambda_i t}$. $T$ can make a mode look big or small in $x$, but it cannot change whether that mode grows or decays.",
             ]},
            {"heading": "One bad mode is enough",
             "paragraphs": [
                 r"If some $e^{\lambda_j t}$ grows without bound, every start with $z_j(0) \neq 0$ grows too. A randomly chosen $x(0)$ has a component along every eigenvector, so in the lecturer's words it almost certainly excites the unstable direction. The book adds that disturbances excite all eigenvectors in practice.",
                 r"A start with $z_j(0) = 0$ exactly (lying in the span of the other eigenvectors) never excites that mode in exact arithmetic. Stability, however, is a statement about all initial states, so one unbounded solution already makes the system unstable. In a floating-point simulation, or with any disturbance, such a start may still pick up a tiny component along the unstable eigenvector, which then grows.",
             ]},
        ],
        "keyIdeas": [
            r"$x(t) = Te^{Dt}T^{-1}x(0)$: only $e^{Dt} = \mathrm{diag}(e^{\lambda_i t})$ depends on $t$.",
            r"$x(t) = \sum_i z_i(0)e^{\lambda_i t}c_i$: a blend of modes, fixed by $x(0)$.",
            r"One unbounded mode makes the system unstable, even though some special starts avoid it.",
        ],
        "example": {
            "title": "An unstable system with one decaying start (authored)",
            "problem": r"$A = \begin{bmatrix}1&2\\2&1\end{bmatrix}$. Find its modes and compare the starts $x(0) = (1, -1)$ and $x(0) = (1, 0)$.",
            "steps": [
                {"text": r"Multiply the candidate eigenvectors by $A$: $(1, 1)$ is stretched by $3$, $(1, -1)$ is flipped.",
                 "tex": r"A\begin{bmatrix}1\\1\end{bmatrix} = 3\begin{bmatrix}1\\1\end{bmatrix},\qquad A\begin{bmatrix}1\\-1\end{bmatrix} = -1\begin{bmatrix}1\\-1\end{bmatrix}"},
                {"text": r"Start on the second eigenvector: only the decaying mode is excited.",
                 "tex": r"x(0) = \begin{bmatrix}1\\-1\end{bmatrix} \;\Rightarrow\; x(t) = e^{-t}\begin{bmatrix}1\\-1\end{bmatrix} \to 0"},
                {"text": r"A generic start is a blend: $z(0) = T^{-1}x(0) = (\tfrac12, \tfrac12)$.",
                 "tex": r"x(0) = \begin{bmatrix}1\\0\end{bmatrix} = \tfrac12\begin{bmatrix}1\\1\end{bmatrix} + \tfrac12\begin{bmatrix}1\\-1\end{bmatrix} \;\Rightarrow\; x(t) = \tfrac12 e^{3t}\begin{bmatrix}1\\1\end{bmatrix} + \tfrac12 e^{-t}\begin{bmatrix}1\\-1\end{bmatrix}"},
                {"text": r"The $e^{3t}$ term takes over: at $t = 1$ it is already about $10$, the other term about $0.18$.",
                 "tex": r"\tfrac12 e^{3} \approx 10.04,\qquad \tfrac12 e^{-1} \approx 0.18"},
            ],
            "answer": r"The system is unstable ($\lambda = 3 > 0$). The start $(1, -1)$ decays only because it has no component along the unstable eigenvector; almost every other start grows like $e^{3t}$.",
        },
        "sources": {
            "video": [{"t": 0, "label": "Recap: x dot = Ax and [T, D] = eig(A)"},
                      {"t": 60, "label": "x(t) = T e^{Dt} T^{-1} x(0)"},
                      {"t": 77, "label": "Stability: what does the system do as t goes to infinity?"},
                      {"t": 100, "label": "Only the bare minimum (no phase portraits, saddles, centers)"},
                      {"t": 131, "label": "e^{Dt} is diagonal: e^{lambda_i t} on the diagonal"},
                      {"t": 157, "label": "T and T^{-1} mix the modes"},
                      {"t": 189, "label": "One growing mode: a random start blows up"}],
            "book": [book(B332, "Only e^{Λt} varies in time (Eq. 8.19); random starts and disturbances excite the unstable direction")],
        },
        "tutorNotes": "Book p.332: from x(t) = T e^{Lambda t} T^{-1} x(0) (8.19) the only time-varying part is e^{Lambda t}. If even one eigenvalue has positive real part the system is unstable and diverges along the corresponding eigenvector; a random initial condition is likely to have a component in that direction, and disturbances excite all eigenvectors. Lecture notation: D for the eigenvalue matrix (book: Lambda). The example A = [[1,2],[2,1]] is authored for the guide.",
    },
    # ------------------------------------------------------------------ 2
    {
        "nav": "Complex λ: the envelope",
        "title": r"Complex eigenvalues: $e^{\lambda t} = e^{at}(\cos bt + i\sin bt)$",
        "time": [200, 355],
        "summary": r"For $\lambda = a + ib$, Euler's formula splits $e^{\lambda t}$ into a real envelope $e^{at}$ times a factor of size one. Only the real part $a$ decides growth ($a > 0$) or decay ($a < 0$); $b$ sets the oscillation. A real matrix has complex eigenvalues in conjugate pairs, and their imaginary parts cancel in $x(t)$.",
        "goals": [
            r"Split $e^{\lambda t}$ with Euler's formula and show $|e^{\lambda t}| = e^{at}$.",
            r"Explain why a real system can have complex eigenvalues and still give real solutions.",
            r"Sketch an oscillation inside a growing or decaying envelope.",
        ],
        "notes": [
            {"heading": "Euler's formula",
             "paragraphs": [
                 r"With $\lambda = a + ib$ ($a$, $b$ real), $e^{\lambda t} = e^{at}e^{ibt} = e^{at}(\cos bt + i\sin bt)$. The bracket has size $\sqrt{\cos^2 bt + \sin^2 bt} = 1$ for every $t$: it only turns around the unit circle. So $|e^{\lambda t}| = e^{at}$, and the real part alone sets the amplitude.",
             ]},
            {"heading": "Why imaginary parts appear in a real system",
             "paragraphs": [
                 r"If $A$ and $x$ are real, $x(t)$ must stay real. The characteristic polynomial of a real matrix has real coefficients, so its complex roots come in pairs $\lambda = a \pm ib$ with conjugate eigenvectors. For a real start the two coefficients are conjugate too, and the pair adds up to $2\,\mathrm{Re}\big(z\,e^{\lambda t}c\big)$, which is real: a combination of $e^{at}\cos bt$ and $e^{at}\sin bt$.",
                 r"The lecturer calls this a little deeper and only states the outcome: the imaginary parts cancel. The worked example below shows it for a concrete matrix.",
             ]},
            {"heading": "Growing or decaying envelope",
             "paragraphs": [
                 r"$a > 0$: the solution may oscillate (when $b \neq 0$), but inside an envelope $\pm Ce^{at}$ that grows exponentially, so it eventually blows up. $a < 0$: the envelope shrinks and the solution decays to zero. The frequency $b$ changes how fast it wiggles, never whether it grows.",
                 r"The case $a = 0$ (a pure oscillation of constant amplitude) is not treated in the lecture; see the Supplement in Section 3.",
             ]},
        ],
        "keyIdeas": [
            r"$e^{(a+ib)t} = e^{at}(\cos bt + i\sin bt)$ and $|\cos bt + i\sin bt| = 1$.",
            r"Real part $a$: growth or decay. Imaginary part $b$: oscillation frequency.",
            r"Real $A$: complex eigenvalues in conjugate pairs; real solutions $e^{at}(\alpha\cos bt + \beta\sin bt)$.",
        ],
        "example": {
            "title": "A decaying rotation (authored)",
            "problem": r"$A = \begin{bmatrix}-1&2\\-2&-1\end{bmatrix}$. Find the eigenvalues, $e^{At}$ and $|x(t)|$ for $x(0) = (3, 4)$.",
            "steps": [
                {"text": r"Characteristic polynomial and eigenvalues.",
                 "tex": r"\det(A - \lambda I) = (\lambda + 1)^2 + 4 = 0 \;\Rightarrow\; \lambda = -1 \pm 2i"},
                {"text": r"$A = -I + 2R$ with $R = \begin{bmatrix}0&1\\-1&0\end{bmatrix}$, and $-I$ commutes with $R$, so the exponential factors into an envelope and a clockwise rotation by angle $2t$.",
                 "tex": r"e^{At} = e^{-t}\begin{bmatrix}\cos 2t & \sin 2t\\ -\sin 2t & \cos 2t\end{bmatrix}"},
                {"text": r"A rotation keeps lengths, so the length shrinks exactly like the envelope. Everything stays real.",
                 "tex": r"|x(t)| = e^{-t}\,|x(0)| = 5e^{-t},\qquad |x(1.3)| = 5e^{-1.3} \approx 1.36"},
            ],
            "answer": r"$\lambda = -1 \pm 2i$: the state rotates clockwise with period $\pi$ while its length decays like $e^{-t}$. The real part $-1$ decides the decay; the imaginary part $2$ only sets the rotation rate.",
        },
        "sources": {
            "video": [{"t": 213, "label": "Each eigenvalue has a real and an imaginary part: lambda = a + ib"},
                      {"t": 227, "label": "Euler's formula: e^{lambda t} = e^{at}(cos bt + i sin bt)"},
                      {"t": 245, "label": "Why imaginary parts in a real system?"},
                      {"t": 272, "label": "Plus-or-minus pairs: the imaginary parts cancel"},
                      {"t": 305, "label": "cos + i sin has size one, so a decides growth or decay"},
                      {"t": 329, "label": "a > 0: oscillation in a growing envelope"},
                      {"t": 347, "label": "a < 0: decaying envelope"}],
            "book": [book(B332, "λ = a + ib gives e^{λt} = e^{at}(cos bt + i sin bt)")],
        },
        "tutorNotes": "Book p.332: eigenvalues lambda = a + ib may be complex, so solutions involve e^{lambda t} = e^{at}(cos(bt) + i sin(bt)). The lecture (3:33-5:50) adds that a real system has complex eigenvalues in plus/minus pairs whose imaginary parts cancel, that cos + i sin has amplitude one, and sketches growing (a > 0) and decaying (a < 0) envelopes. The example A = [[-1,2],[-2,-1]] is authored for the guide.",
    },
    # ------------------------------------------------------------------ 3
    {
        "nav": "Left half-plane",
        "title": r"Asymptotically stable if and only if every $\mathrm{Re}\,\lambda < 0$",
        "time": [355, 545],
        "summary": r"Plot the eigenvalues in the complex plane: if all of them lie in the open left half-plane, every solution decays; one eigenvalue in the right half-plane makes the system unstable. Control will later move eigenvalues to the left. What happens exactly on the imaginary axis is a Supplement here.",
        "goals": [
            r"State the continuous-time criterion and apply it to eigenvalues drawn in the complex plane.",
            r"Explain how the inverted pendulum fits the picture.",
            r"Supplement: distinguish asymptotic from Lyapunov stability on the imaginary axis, and recognise a defective (Jordan) case.",
        ],
        "notes": [
            {"heading": "The criterion",
             "paragraphs": [
                 r"All $\mathrm{Re}\,\lambda_i < 0$: every mode is multiplied by $e^{(\text{negative})t} \to 0$, so every solution decays to $0$. The lecturer states this as stable if and only if all real parts are strictly negative. The precise name for every solution tends to zero is asymptotic stability.",
                 r"Any $\mathrm{Re}\,\lambda_j > 0$: that mode blows up and the system is unstable. This half needs no assumption about eigenvectors.",
             ]},
            {"heading": "Eigenvalues as points in the plane",
             "paragraphs": [
                 r"Draw each eigenvalue at the point $(\mathrm{Re}\,\lambda, \mathrm{Im}\,\lambda)$. The left half-plane is stable, the right half-plane unstable, and conjugate pairs sit mirror-symmetrically about the real axis. In this picture, the behaviour of $\dot x = Ax$ is almost entirely described by where its eigenvalues are.",
                 r"Preview, not taught here: with a control input, $\dot x = Ax + Bu$, later lectures choose $u$ to move unstable eigenvalues into the left half-plane. The board at 7:59 shows arrows dragging two eigenvalues across the imaginary axis.",
             ]},
            {"heading": "The inverted pendulum",
             "paragraphs": [
                 r"The lecturer notes that the upright pendulum has an eigenvalue with positive real part, which is why it falls. The book's example on p. 335 (linearization is the next lecture) gives $\lambda = \pm\sqrt{g/L}$ for the upright position, one in each half-plane, and $\lambda = \pm i\sqrt{g/L}$ for the hanging position, exactly on the imaginary axis.",
             ]},
            {"heading": "Supplement: eigenvalues on the imaginary axis",
             "paragraphs": [
                 r"Not covered in the lecture. Suppose the largest real part is exactly $0$. If each eigenvalue on the axis has as many independent eigenvectors as its multiplicity (semisimple; automatic when it is not repeated), its modes neither grow nor decay: $e^{\pm i\omega t}$ rotates, $e^{0t} = 1$ stays put. Every solution stays bounded but not every solution tends to $0$. This is Lyapunov (marginal) stability, not asymptotic stability. The frictionless hanging pendulum is the standard example.",
                 r"If an eigenvalue on the axis is defective (a Jordan block), the exponential contains $t\,e^{\lambda t}$. For $J = \begin{bmatrix}0&1\\0&0\end{bmatrix}$, $e^{Jt} = \begin{bmatrix}1&t\\0&1\end{bmatrix}$, so $x_1(t) = x_1(0) + t\,x_2(0)$ grows linearly: unstable. The lecture's criterion is exactly the test for asymptotic stability and holds even for defective matrices (a $t^k e^{\lambda t}$ term still decays when $\mathrm{Re}\,\lambda < 0$). Only the boundary case needs this extra check.",
             ]},
            {"heading": "Supplement: a plot is not a proof",
             "paragraphs": [
                 r"A finite time window can mislead. $e^{0.02t}$ looks flat for $0 \le t \le 10$ but is unbounded; a stable non-normal system (eigenvectors nearly parallel) can grow for a while before it decays. The verdict comes from the eigenvalues and, on the boundary, from the eigenvector count, not from the picture. The explorer's transient-growth preset shows this.",
             ]},
        ],
        "keyIdeas": [
            r"All $\mathrm{Re}\,\lambda < 0$ $\Leftrightarrow$ asymptotically stable (every solution $\to 0$).",
            r"Any $\mathrm{Re}\,\lambda > 0$ $\Rightarrow$ unstable.",
            r"Supplement: largest $\mathrm{Re}\,\lambda = 0$ is bounded (Lyapunov) if those eigenvalues are semisimple, unstable if defective.",
        ],
        "example": {
            "title": "Three verdicts from the characteristic polynomial (authored)",
            "problem": r"Classify $A_1 = \begin{bmatrix}0&1\\-2&-3\end{bmatrix}$, $A_2 = \begin{bmatrix}0&1\\2&-1\end{bmatrix}$ and $A_3 = \begin{bmatrix}0&1\\-4&0\end{bmatrix}$.",
            "steps": [
                {"text": r"For $\begin{bmatrix}0&1\\-q&-p\end{bmatrix}$ the characteristic polynomial is $\lambda^2 + p\lambda + q$.",
                 "tex": r"A_1:\ \lambda^2 + 3\lambda + 2 = (\lambda+1)(\lambda+2) \;\Rightarrow\; \lambda = -1, -2"},
                {"text": r"Both negative: asymptotically stable. For $A_2$ one root is positive.",
                 "tex": r"A_2:\ \lambda^2 + \lambda - 2 = (\lambda - 1)(\lambda + 2) \;\Rightarrow\; \lambda = 1, -2\ \text{(unstable)}"},
                {"text": r"$A_3$ has a purely imaginary pair: not covered by the lecture's two cases (Supplement).",
                 "tex": r"A_3:\ \lambda^2 + 4 = 0 \;\Rightarrow\; \lambda = \pm 2i"},
                {"text": r"The pair is distinct, hence semisimple: $x_1 = \alpha\cos 2t + \beta\sin 2t$ oscillates forever with constant amplitude.",
                 "tex": r"A_3:\ \text{bounded, does not decay} \;\Rightarrow\; \text{Lyapunov stable, not asymptotically stable}"},
            ],
            "answer": r"$A_1$: asymptotically stable. $A_2$: unstable (a saddle). $A_3$: on the boundary, bounded oscillation, Lyapunov but not asymptotically stable. The lecture's criterion settles $A_1$ and $A_2$; $A_3$ needs the Supplement.",
        },
        "sources": {
            "video": [{"t": 364, "label": "All eigenvalues with negative real part: all dynamics decay"},
                      {"t": 386, "label": "Stable if and only if all real parts are negative; one positive real part blows up"},
                      {"t": 410, "label": "Eigenvalues as points in the complex plane"},
                      {"t": 431, "label": "Left half-plane stable, right half-plane unstable"},
                      {"t": 479, "label": "Preview: adding + Bu to drive eigenvalues into the left half-plane"},
                      {"t": 503, "label": "Characterize A by where its eigenvalues are"},
                      {"t": 525, "label": "The inverted pendulum has an eigenvalue with positive real part"}],
            "book": [book(B332, "Stable if all Re(λ) < 0; unstable if even one Re(λ) > 0"),
                     book(B335, "Inverted pendulum example: up λ = ±√(g/L), down λ = ±i√(g/L) (a center)")],
        },
        "tutorNotes": "Book p.332: if all eigenvalues have negative real part the system is stable and solutions decay to 0; if even one has positive real part it is unstable. Book p.335 (example in Section 8.2, linearization is the next lecture): pendulum up has lambda = +-sqrt(g/L) (unstable saddle), down has lambda = +-i sqrt(g/L) (a stable center). Supplement, not in the lecture: on the imaginary axis, semisimple eigenvalues give Lyapunov (marginal) stability, defective ones (Jordan blocks) give polynomial growth, e.g. e^{Jt} = [[1,t],[0,1]] for J = [[0,1],[0,0]]. The A1/A2/A3 example is authored.",
    },
    # ------------------------------------------------------------------ 4
    {
        "nav": "Discrete time",
        "title": r"Discrete time: $x_{k+1} = \tilde A x_k$ with $\tilde A = e^{A\Delta t}$",
        "time": [545, 765],
        "summary": r"Measurements arrive every $\Delta t$. The samples $x_k = x(k\Delta t)$ obey $x_{k+1} = \tilde A x_k$ with $\tilde A = e^{A\Delta t}$, so $x_N = \tilde A^N x_0$: powers of a matrix take the place of the exponential.",
        "goals": [
            r"Define $x_k = x(k\Delta t)$ and derive $\tilde A = e^{A\Delta t}$ from $e^{A(s+t)} = e^{As}e^{At}$.",
            r"Iterate the one-step map to $x_N = \tilde A^N x_0$.",
            r"Relate the lecture's $\tilde A$ to the book's $A_d$.",
        ],
        "notes": [
            {"heading": "Why discrete time",
             "paragraphs": [
                 r"Physics writes $\dot x = Ax$ for a continuously varying $x(t)$, but an experiment or a digital controller only sees the state at fixed instants $0, \Delta t, 2\Delta t, \dots$. The lecturer calls discrete-time systems bread and butter in control theory, even if they are less familiar from a differential-equations course.",
             ]},
            {"heading": "From the flow to a one-step map",
             "paragraphs": [
                 r"Let $x_k = x(k\Delta t)$. Since $x(t) = e^{At}x(0)$ and $e^{A(s+t)} = e^{As}e^{At}$, we get $x_{k+1} = e^{A(k+1)\Delta t}x(0) = e^{A\Delta t}e^{Ak\Delta t}x(0) = e^{A\Delta t}x_k$. So $\tilde A = e^{A\Delta t}$: advancing by $\Delta t$ is multiplication by the matrix exponential, as derived in the previous lecture.",
                 r"Guide note: this is exact, not an approximation. Euler's method $x_{k+1} = (I + A\Delta t)x_k$ keeps only the first two terms of the series for $e^{A\Delta t}$ and can even turn a stable system unstable if $\Delta t$ is too large.",
             ]},
            {"heading": "Iterate",
             "paragraphs": [
                 r"Starting from $x_0$: $x_1 = \tilde A x_0$, $x_2 = \tilde A x_1 = \tilde A^2 x_0$, $x_3 = \tilde A^3 x_0$, and in general $x_N = \tilde A^N x_0$. The question of stability becomes: what happens to $\tilde A^N$ as $N \to \infty$? The lecturer stresses that the answer looks different from the continuous one.",
             ]},
            {"heading": "Notation and scope",
             "paragraphs": [
                 r"The book writes $A_d = e^{A\Delta t}$ in Eq. (8.22a), together with the input matrix $B_d$ of a forced discrete system $x_{k+1} = A_dx_k + B_du_k$. Inputs are not part of this lecture.",
                 r"Supplement: every sampled system has an invertible $\tilde A$, and a negative real eigenvalue of $\tilde A$ can only come from a complex pair, so it is repeated. A general discrete-time system can have eigenvalues such as $0$ or a single $-0.5$ that no sampled real system produces. The stability rule in the next section applies to any $\tilde A$.",
             ]},
        ],
        "keyIdeas": [
            r"$x_k = x(k\Delta t)$ and $x_{k+1} = \tilde A x_k$ with $\tilde A = e^{A\Delta t}$ exactly.",
            r"$x_N = \tilde A^N x_0$: stability is about powers of $\tilde A$.",
            r"Book notation: $A_d = e^{A\Delta t}$ (Eq. 8.22a).",
        ],
        "example": {
            "title": "Sampling a stable system at Δt = ln 2 (authored)",
            "problem": r"For $A = \begin{bmatrix}0&1\\-2&-3\end{bmatrix}$ (eigenvalues $-1, -2$) and $\Delta t = \ln 2$, find $\tilde A$, then $x_1$ and $x_2$ from $x_0 = (1, 0)$, and compare with $x(t)$.",
            "steps": [
                {"text": r"Eigenvectors $(1, -1)$ and $(1, -2)$. At $\Delta t = \ln 2$ the diagonal factor is $\mathrm{diag}(e^{-\ln 2}, e^{-2\ln 2})$.",
                 "tex": r"T = \begin{bmatrix}1&1\\-1&-2\end{bmatrix},\quad T^{-1} = \begin{bmatrix}2&1\\-1&-1\end{bmatrix},\quad e^{D\Delta t} = \begin{bmatrix}\tfrac12&0\\0&\tfrac14\end{bmatrix}"},
                {"text": r"Multiply out $\tilde A = Te^{D\Delta t}T^{-1}$. Check: trace $\tfrac34 = \tfrac12 + \tfrac14$ and determinant $\tfrac18 = \tfrac12\cdot\tfrac14$.",
                 "tex": r"\tilde A = \begin{bmatrix}\tfrac34&\tfrac14\\-\tfrac12&0\end{bmatrix}"},
                {"text": r"Iterate twice.",
                 "tex": r"x_1 = \tilde A x_0 = \begin{bmatrix}\tfrac34\\-\tfrac12\end{bmatrix},\qquad x_2 = \tilde A x_1 = \begin{bmatrix}\tfrac{7}{16}\\-\tfrac38\end{bmatrix}"},
                {"text": r"The continuous solution from $(1, 0)$ is $x(t) = 2e^{-t}(1, -1) - e^{-2t}(1, -2)$. Evaluate at $\ln 2$ and $2\ln 2$.",
                 "tex": r"x(\ln 2) = \begin{bmatrix}1 - \tfrac14\\-1 + \tfrac12\end{bmatrix} = x_1,\qquad x(2\ln 2) = \begin{bmatrix}\tfrac12 - \tfrac1{16}\\-\tfrac12 + \tfrac18\end{bmatrix} = x_2\ \checkmark"},
            ],
            "answer": r"$\tilde A = \begin{bmatrix}3/4&1/4\\-1/2&0\end{bmatrix}$, $x_1 = (3/4, -1/2)$, $x_2 = (7/16, -3/8)$: exactly the continuous solution at the sample times. The eigenvalues of $\tilde A$ are $\tfrac12 = e^{-\ln 2}$ and $\tfrac14 = e^{-2\ln 2}$.",
        },
        "sources": {
            "video": [{"t": 548, "label": "Discrete-time systems: bread and butter in control theory"},
                      {"t": 585, "label": "Real data: measurements at fixed Δt increments"},
                      {"t": 597, "label": "x_{k+1} = Ã x_k"},
                      {"t": 605, "label": "x_k = x(kΔt)"},
                      {"t": 644, "label": "Ã = e^{AΔt}"},
                      {"t": 670, "label": "A different notion of stability in discrete time"},
                      {"t": 705, "label": "x_1 = Ã x_0"},
                      {"t": 728, "label": "x_2 = Ã x_1 = Ã² x_0"},
                      {"t": 754, "label": "x_N = Ã^N x_0"}],
            "book": [book(B334, "Discrete-time systems: x_{k+1} = A_d x_k + B_d u_k, x_k = x(kΔt), A_d = e^{AΔt} (Eqs. 8.21-8.22)")],
        },
        "tutorNotes": "Book p.334: digital control uses discrete-time systems x_{k+1} = A_d x_k + B_d u_k (8.21a) with x_k = x(k dt); A_d = e^{A dt} (8.22a), B_d = integral_0^{dt} e^{A tau} B d tau (8.22b), C_d = C, D_d = D. The lecture writes A-tilde for A_d and only treats the unforced case: x_1 = A~ x_0, x_2 = A~^2 x_0, ..., x_N = A~^N x_0. The worked example (A = [[0,1],[-2,-3]], dt = ln 2, A~ = [[3/4,1/4],[-1/2,0]]) is authored.",
    },
    # ------------------------------------------------------------------ 5
    {
        "nav": "Unit circle",
        "title": r"Powers $\tilde\lambda^N = r^N e^{iN\theta}$ and the unit circle",
        "time": [765, 1055],
        "summary": r"With $\tilde A = \tilde T\tilde D\tilde T^{-1}$, $\tilde A^N = \tilde T\tilde D^N\tilde T^{-1}$, so only the powers of the eigenvalues evolve. Writing $\tilde\lambda = re^{i\theta}$, $\tilde\lambda^N = r^Ne^{iN\theta}$: the angle turns and the radius decides. The system is asymptotically stable if and only if every $|\tilde\lambda| < 1$, inside the unit circle.",
        "goals": [
            r"Derive $\tilde A^N = \tilde T\tilde D^N\tilde T^{-1}$ with the matrices in the right order.",
            r"Use the polar form to explain why the magnitude $|\tilde\lambda|$, not the real part, decides.",
            r"Supplement: recognise the boundary $|\tilde\lambda| = 1$ and its Jordan exception.",
        ],
        "notes": [
            {"heading": "Only the diagonal gets powered",
             "paragraphs": [
                 r"Diagonalize $\tilde A$ like $A$: $\tilde A\tilde T = \tilde T\tilde D$, so $\tilde A = \tilde T\tilde D\tilde T^{-1}$ with eigenvectors as the columns of $\tilde T$. Then $\tilde A^2 = \tilde T\tilde D\tilde T^{-1}\tilde T\tilde D\tilde T^{-1} = \tilde T\tilde D^2\tilde T^{-1}$, and in general $\tilde A^N = \tilde T\tilde D^N\tilde T^{-1}$ with $\tilde D^N = \mathrm{diag}(\tilde\lambda_1^N, \dots, \tilde\lambda_n^N)$.",
                 r"Order of the factors: at 12:57 the lecturer says aloud that he forgets whether it is $T^{-1}DT$ or $TDT^{-1}$ and uses $T^{-1}DT$. At 16:44 he derives it on the board from $AT = TD$, which gives $A = TDT^{-1}$ (then puts tildes on everything). This guide uses that board version. Either way the powers land only on the diagonal matrix in the middle.",
                 r"The lecture reuses the letter $\lambda$ for the eigenvalues of $\tilde A$; this guide writes $\tilde\lambda$ to keep them apart from the eigenvalues of $A$.",
             ]},
            {"heading": "Radius and angle",
             "paragraphs": [
                 r"Any complex number can be written $\tilde\lambda = re^{i\theta}$ with $r = |\tilde\lambda|$, so $\mathrm{Re} = r\cos\theta$ and $\mathrm{Im} = r\sin\theta$. Multiplying $N$ times gives $\tilde\lambda^N = r^Ne^{iN\theta}$: each step multiplies the radius by $r$ and adds $\theta$ to the angle. The angle only rotates; $r > 1$ makes $r^N$ blow up and $r < 1$ makes it decay to $0$.",
                 r"Hence the discrete-time criterion: asymptotically stable if and only if every eigenvalue of $\tilde A$ lies strictly inside the unit circle, $|\tilde\lambda| < 1$. One eigenvalue outside makes the system unstable.",
             ]},
            {"heading": "Magnitude, not real part",
             "paragraphs": [
                 r"At 16:10 the lecturer says that an eigenvalue with real part bigger than one is unstable. His board picture and the derivation just before are about the radius, so read real part there as magnitude. The difference matters: $\tilde\lambda = 0.5 + 0.9i$ has real part $0.5$, yet $|\tilde\lambda| = \sqrt{1.06} \approx 1.03 > 1$, so it is unstable. $\tilde\lambda = -1.2$ has a negative real part but is outside the circle.",
             ]},
            {"heading": "Supplement: on the unit circle",
             "paragraphs": [
                 r"Not covered in the lecture. If the largest magnitude is exactly $1$ and those eigenvalues are semisimple, $|\tilde\lambda^N| = 1$ for all $N$: solutions stay bounded without decaying (Lyapunov stable). A defective eigenvalue on the circle grows like $N$: $\begin{bmatrix}1&1\\0&1\end{bmatrix}^N = \begin{bmatrix}1&N\\0&1\end{bmatrix}$. This is the discrete twin of the imaginary-axis case.",
             ]},
        ],
        "keyIdeas": [
            r"$\tilde A^N = \tilde T\tilde D^N\tilde T^{-1}$ (from $\tilde A\tilde T = \tilde T\tilde D$).",
            r"$\tilde\lambda = re^{i\theta} \Rightarrow \tilde\lambda^N = r^Ne^{iN\theta}$: radius decides, angle rotates.",
            r"All $|\tilde\lambda| < 1$ $\Leftrightarrow$ asymptotically stable. Magnitude, not real part.",
        ],
        "example": {
            "title": "Real part below one, still unstable (authored)",
            "problem": r"$\tilde A = \begin{bmatrix}0.5&-0.9\\0.9&0.5\end{bmatrix}$. Find the eigenvalues in polar form and $|x_N|$ for $x_0 = (1, 0)$.",
            "steps": [
                {"text": r"Eigenvalues of $\begin{bmatrix}p&-q\\q&p\end{bmatrix}$ are $p \pm iq$.",
                 "tex": r"\tilde\lambda = 0.5 \pm 0.9i,\qquad \mathrm{Re}\,\tilde\lambda = 0.5 < 1"},
                {"text": r"Polar form: radius and angle.",
                 "tex": r"r = \sqrt{0.5^2 + 0.9^2} = \sqrt{1.06} \approx 1.0296,\qquad \theta = \arctan\tfrac{0.9}{0.5} \approx 60.9^\circ"},
                {"text": r"$\tilde A = r\times$(rotation by $\theta$), so each step turns $x$ by $\theta$ and stretches it by $r$.",
                 "tex": r"|x_N| = r^N|x_0| = 1.06^{N/2},\qquad |x_{24}| = 1.06^{12} \approx 2.01"},
            ],
            "answer": r"$|\tilde\lambda| \approx 1.03 > 1$: unstable, although the real part is only $0.5$. The state spirals outwards and roughly doubles its length every 24 steps.",
        },
        "sources": {
            "video": [{"t": 765, "label": "The same eigenvector/eigenvalue relationship for Ã"},
                      {"t": 777, "label": "Spoken order T^{-1}DT (lecturer unsure; corrected at 16:44)"},
                      {"t": 814, "label": "λ, λ², λ³, …, λ^N: follow one eigenvalue"},
                      {"t": 840, "label": "Radius and angle in the complex plane"},
                      {"t": 863, "label": "λ = R e^{iθ}"},
                      {"t": 886, "label": "λ^N = R^N e^{iNθ}: the radius grows or decays, the angle rotates"},
                      {"t": 900, "label": "Radius bigger than one blows up; smaller decays"},
                      {"t": 944, "label": "Unit circle: inside is stable in discrete time"},
                      {"t": 970, "label": "Says 'real part bigger than one' (means magnitude)"},
                      {"t": 989, "label": "Glossing over a step: derive it yourself"},
                      {"t": 1004, "label": "AT = TD, so A = TDT^{-1}; the same with tildes"}],
            "book": [book(B334, "Stable if and only if all discrete-time eigenvalues are inside the unit circle")],
        },
        "tutorNotes": "Book p.334: the stability of the discrete-time system is determined by the eigenvalues of A_d; it is stable if and only if all discrete-time eigenvalues are inside the unit circle. Lecture 12:45-17:30: A~^N = T~ D~^N T~^{-1}, lambda = R e^{i theta}, lambda^N = R^N e^{i N theta}. Two spoken slips: at 12:57 he says A~ = T^{-1} D T (unsure); at 16:44 he derives A = T D T^{-1} on the board. At 16:10 he says 'real part bigger than one' where magnitude is meant. Supplement, not in the lecture: |lambda| = 1 semisimple gives bounded (Lyapunov) behaviour, defective grows like N. Example A~ = [[0.5,-0.9],[0.9,0.5]] is authored.",
    },
    # ------------------------------------------------------------------ 6
    {
        "nav": "Conformal map, summary",
        "title": r"$e^{\lambda\Delta t}$ maps the left half-plane into the unit disc",
        "time": [1055, 1170],
        "summary": r"Each eigenvalue $\lambda$ of $A$ becomes $\tilde\lambda = e^{\lambda\Delta t}$ of $\tilde A = e^{A\Delta t}$, and $|\tilde\lambda| = e^{\mathrm{Re}\,\lambda\,\Delta t}$. So $\mathrm{Re}\,\lambda < 0 \Leftrightarrow |\tilde\lambda| < 1$: both criteria say the same thing, and the imaginary axis maps onto the unit circle. The upshot: asymptotic stability is decided by the eigenvalues alone; exactly on the boundary, whether they are semisimple also matters.",
        "goals": [
            r"Show that $\tilde A = e^{A\Delta t}$ has eigenvalues $e^{\lambda_i\Delta t}$ and $|e^{\lambda\Delta t}| = e^{a\Delta t}$.",
            r"Map vertical lines to circles and horizontal lines to rays.",
            r"State the summary for both settings; Supplement: aliasing.",
        ],
        "notes": [
            {"heading": "Eigenvalues of the sampled system",
             "paragraphs": [
                 r"From $A = TDT^{-1}$, $e^{A\Delta t} = Te^{D\Delta t}T^{-1}$: the same eigenvectors, with eigenvalues $\tilde\lambda_i = e^{\lambda_i\Delta t}$. Every continuous eigenvalue has a discrete partner, and the map between the two complex planes is $\lambda \mapsto e^{\lambda\Delta t}$.",
             ]},
            {"heading": "What the map does",
             "paragraphs": [
                 r"For $\lambda = a + ib$: $e^{\lambda\Delta t} = e^{a\Delta t}e^{ib\Delta t}$, radius $e^{a\Delta t}$ and angle $b\Delta t$. A vertical line $\mathrm{Re}\,\lambda = a$ wraps onto the circle of radius $e^{a\Delta t}$; the imaginary axis ($a = 0$) onto the unit circle; the left half-plane ($a < 0$) into the inside of the disc. A horizontal line $\mathrm{Im}\,\lambda = b$ becomes the ray at angle $b\Delta t$ (taken modulo $2\pi$), and $\lambda = 0$ goes to $1$. The disc is filled except for its centre: $e^{\lambda\Delta t}$ is never $0$, which is why a sampled $\tilde A$ is always invertible.",
                 r"The lecturer calls this a conformal map: the exponential has a nonzero derivative everywhere, so it preserves angles locally (the grid lines stay perpendicular, as circles and rays). It is the book's Fig. 8.7.",
             ]},
            {"heading": "Supplement: many-to-one",
             "paragraphs": [
                 r"$e^{ib\Delta t}$ repeats when $b$ grows by $2\pi/\Delta t$, so $\lambda$ and $\lambda + 2\pi i/\Delta t$ give the same $\tilde\lambda$ (aliasing). Sampling too slowly therefore loses the oscillation frequency, although the radius, and with it the stability verdict, is preserved. On the strip $|\mathrm{Im}\,\lambda| < \pi/\Delta t$ the map is one-to-one.",
             ]},
            {"heading": "The upshot",
             "paragraphs": [
                 r"Continuous time: asymptotically stable when every eigenvalue of $A$ has negative real part, unstable if one has positive real part. Discrete time: asymptotically stable when every eigenvalue of $\tilde A$ has magnitude below one, unstable if one is outside the unit circle. Exactly on the boundary the Supplement applies (semisimple or defective). Given a continuous system there is an equivalent sampled one, and stability can be checked in either.",
                 r"Why bother with discrete time: the lecturer says several control ideas, controllability in particular, are easier to see as a discrete chain of steps $x_{k+1} = \tilde Ax_k + \tilde Bu_k$. The next lectures linearize nonlinear systems at fixed points and then add $Bu$; they are not part of this guide.",
             ]},
        ],
        "keyIdeas": [
            r"$\tilde\lambda = e^{\lambda\Delta t}$ and $|\tilde\lambda| = e^{\mathrm{Re}\,\lambda\,\Delta t}$.",
            r"Left half-plane $\to$ open unit disc, imaginary axis $\to$ unit circle.",
            r"Asymptotic stability depends only on the eigenvalues, in continuous and discrete time; on the boundary the Jordan structure matters too.",
        ],
        "example": {
            "title": "Mapping three eigenvalues (authored)",
            "problem": r"$A$ has eigenvalues $-1$ and $0.2 \pm 3i$. Sample with $\Delta t = 0.5$: where do they land, and do the two criteria agree?",
            "steps": [
                {"text": r"The real eigenvalue maps onto the positive real axis.",
                 "tex": r"\tilde\lambda_1 = e^{-0.5} \approx 0.607 \quad (\text{inside})"},
                {"text": r"The complex pair: radius from the real part, angle from the imaginary part.",
                 "tex": r"\tilde\lambda_{2,3} = e^{0.1}e^{\pm 1.5i},\qquad |\tilde\lambda_{2,3}| = e^{0.1} \approx 1.105 > 1 \quad (\text{outside})"},
                {"text": r"Both views agree: $\mathrm{Re} = 0.2 > 0$ in continuous time, radius $> 1$ in discrete time. Unstable.",
                 "tex": r"\mathrm{Re}\,\lambda > 0 \;\Leftrightarrow\; |e^{\lambda\Delta t}| = e^{0.2\cdot 0.5} > 1"},
                {"text": r"Supplement: adding $2\pi/\Delta t = 4\pi$ to the imaginary part lands on the same point.",
                 "tex": r"e^{(0.2 + (3 + 4\pi)i)\,0.5} = e^{0.1}e^{1.5i}e^{2\pi i} = \tilde\lambda_2"},
            ],
            "answer": r"$0.607$ inside the circle and a pair of radius $1.105$ outside: unstable, exactly as $\mathrm{Re}\,\lambda = 0.2 > 0$ predicts. The angle $1.5$ rad $\approx 86^\circ$ comes from $b\Delta t = 3 \times 0.5$.",
        },
        "sources": {
            "video": [{"t": 1063, "label": "e^{AΔt} is a conformal map: unit disc ↔ left half-plane"},
                      {"t": 1078, "label": "The upshot: stability depends only on the eigenvalues"},
                      {"t": 1093, "label": "Continuous: negative real part. Discrete: inside the unit circle"},
                      {"t": 1128, "label": "Why discrete time: + Bu, controllability is easier to see"},
                      {"t": 1155, "label": "Next: linear systems from nonlinear equations, adding Bu"}],
            "book": [book(B334, "exp(AΔt) is a conformal map from the left half-plane into the unit circle (Fig. 8.7)")],
        },
        "tutorNotes": "Book p.334 and Fig. 8.7: exp(A dt) defines a conformal mapping of the complex plane from continuous time to discrete time; eigenvalues in the left half-plane map inside the unit circle. Lecture 17:40-19:30: conformal map, then the upshot (continuous: negative real parts; discrete: magnitude less than one) and why discrete time helps with controllability. Supplement: aliasing, lambda and lambda + 2 pi i/dt map to the same point. The example (eigenvalues -1, 0.2 +- 3i, dt = 0.5) is authored.",
    },
]

for i, s in enumerate(SECTIONS, 1):
    s["number"] = i
    s["id"] = f"s{i}"

ORDER = ["number", "id", "nav", "title", "time", "summary", "goals", "notes", "keyIdeas", "example", "sources", "tutorNotes"]
SECTIONS = [{k: s[k] for k in ORDER} for s in SECTIONS]


def q(qid, question, choices):
    return {"id": qid, "question": question,
            "choices": [dict({"text": t, "why": w}, **({"correct": True} if ok else {})) for t, ok, w in choices]}


QUIZ = [
    q("q-only-d", r"In $x(t) = Te^{Dt}T^{-1}x(0)$, which factor decides whether solutions grow or decay as $t \to \infty$?", [
        (r"$e^{Dt}$, that is, the eigenvalues on the diagonal of $D$.", True, r"Right. $T$, $T^{-1}$ and $x(0)$ are constant; only $e^{Dt} = \mathrm{diag}(e^{\lambda_i t})$ changes with time."),
        (r"$T$, because it contains the eigenvectors.", False, r"No. $T$ is a constant matrix: it mixes the modes and sets their size in $x$, but cannot make a decaying mode grow."),
        (r"The initial state $x(0)$.", False, r"No. $x(0)$ selects how much of each mode is present. Whether each mode grows is fixed by its eigenvalue."),
        (r"$T^{-1}$, because it is applied first.", False, r"No. $T^{-1}$ only converts $x(0)$ into eigenvector coordinates $z(0)$; it does not depend on time.")]),
    q("q-one-bad", r"$A$ has eigenvalues $3$ and $-1$. Which statement is true?", [
        (r"The system is unstable; almost every start grows, but a start exactly on the $\lambda = -1$ eigenvector decays.", True, r"Right. Stability is about all starts; one unbounded solution is enough. A start with no component along the $\lambda = 3$ eigenvector decays (in exact arithmetic)."),
        (r"It is stable because one eigenvalue is negative.", False, r"No. Every eigenvalue must have negative real part. The $e^{3t}$ mode takes over any start that excites it."),
        (r"Every start grows, without exception.", False, r"No. A start along the eigenvector of $-1$ never excites $e^{3t}$; it decays like $e^{-t}$. The system is still unstable."),
        (r"It is stable for small enough $x(0)$.", False, r"No. For a linear system scaling $x(0)$ scales the whole solution; $e^{3t}$ times a small number still blows up.")]),
    q("q-envelope", r"A mode has $\lambda = -0.5 + 4i$. What does $e^{\lambda t}$ do?", [
        (r"It oscillates with angular frequency $4$ inside the decaying envelope $e^{-0.5t}$.", True, r"Right. $e^{\lambda t} = e^{-0.5t}(\cos 4t + i\sin 4t)$; the bracket has size one, so the size is $e^{-0.5t}$."),
        (r"It grows, because the imaginary part $4$ is positive.", False, r"No. The imaginary part only sets the oscillation. Growth depends on the real part, here $-0.5$."),
        (r"It decays without oscillating.", False, r"No. A nonzero imaginary part gives $\cos 4t$ and $\sin 4t$ factors: it wiggles while decaying."),
        (r"Its size is $|\lambda| = \sqrt{16.25}$ at all times.", False, r"No. $|e^{\lambda t}| = e^{\mathrm{Re}\,\lambda\, t} = e^{-0.5t}$, which shrinks with time.")]),
    q("q-conjugate", r"Why does a real matrix $A$ with complex eigenvalues still give real solutions $x(t)$?", [
        (r"Its complex eigenvalues come in conjugate pairs $a \pm ib$, and for a real start the imaginary parts cancel.", True, r"Right. The pair contributes $2\,\mathrm{Re}(z e^{\lambda t}c)$, a real combination of $e^{at}\cos bt$ and $e^{at}\sin bt$."),
        (r"Complex eigenvalues cannot occur for a real matrix.", False, r"No. $\begin{bmatrix}0&1\\-4&0\end{bmatrix}$ is real and has eigenvalues $\pm 2i$."),
        (r"Only the real part of each eigenvalue is used.", False, r"No. The imaginary part matters: it produces the oscillation $\cos bt$, $\sin bt$."),
        (r"The solution is complex, and we just ignore the imaginary part.", False, r"No. For a real $A$ and real $x(0)$ the exact solution is real; nothing is discarded.")]),
    q("q-lhp", r"Which eigenvalues give an asymptotically stable system $\dot x = Ax$?", [
        (r"$-0.1$ and $-3 \pm 5i$", True, r"Right. All real parts ($-0.1$, $-3$) are strictly negative, so every solution decays, the slowest like $e^{-0.1t}$."),
        (r"$-2$ and $0.01$", False, r"No. $0.01 > 0$: a slowly growing mode. It may look flat on a short plot, but it is unbounded."),
        (r"$-1$ and $\pm 2i$", False, r"No. $\pm 2i$ lie on the imaginary axis: that oscillation never decays. Bounded (Lyapunov stable), but not asymptotically stable."),
        (r"$0$ and $-1$", False, r"No. A zero eigenvalue gives a mode that stays constant, so not every solution tends to $0$.")]),
    q("q-jordan", r"Supplement. $A = \begin{bmatrix}0&1\\0&0\end{bmatrix}$ has eigenvalue $0$ twice but only one eigenvector. What is true?", [
        (r"It is unstable: $x_1(t) = x_1(0) + t\,x_2(0)$ grows linearly.", True, r"Right. $A^2 = 0$, so $e^{At} = I + At = \begin{bmatrix}1&t\\0&1\end{bmatrix}$. A defective eigenvalue on the imaginary axis gives polynomial growth."),
        (r"Lyapunov stable, because no eigenvalue has positive real part.", False, r"No. That rule needs semisimple boundary eigenvalues. Here the Jordan block adds a $t$ term."),
        (r"Asymptotically stable, because the eigenvalues are not positive.", False, r"No. Asymptotic stability needs strictly negative real parts; and here solutions even grow."),
        (r"It cannot be classified without a simulation.", False, r"No. The Jordan structure classifies it exactly; a simulation over a finite window cannot prove stability anyway.")]),
    q("q-sample", r"Sampling $\dot x = Ax$ every $\Delta t$ gives exactly $x_{k+1} = \tilde Ax_k$ with", [
        (r"$\tilde A = e^{A\Delta t}$", True, r"Right. $x((k+1)\Delta t) = e^{A\Delta t}e^{Ak\Delta t}x(0) = e^{A\Delta t}x(k\Delta t)$. The book writes $A_d$."),
        (r"$\tilde A = I + A\Delta t$", False, r"No. That is Euler's method, the first two terms of the series for $e^{A\Delta t}$: an approximation, not the exact sampled system."),
        (r"$\tilde A = A\Delta t$", False, r"No. That would make $x_{k+1}$ small whenever $\Delta t$ is small, but the state barely changes in a short step."),
        (r"$\tilde A = e^{A}\Delta t$", False, r"No. The time step belongs inside the exponential: $e^{A\Delta t}$.")]),
    q("q-powers", r"With $\tilde A = \tilde T\tilde D\tilde T^{-1}$ (eigenvectors in the columns of $\tilde T$), $\tilde A^N$ equals", [
        (r"$\tilde T\tilde D^N\tilde T^{-1}$", True, r"Right. In $(\tilde T\tilde D\tilde T^{-1})(\tilde T\tilde D\tilde T^{-1})\cdots$ each adjacent pair $\tilde T^{-1}\tilde T = I$ cancels."),
        (r"$\tilde T^N\tilde D^N\tilde T^{-N}$", False, r"No. Matrices do not commute; only the adjacent inner pairs cancel, leaving one $\tilde T$ on each side."),
        (r"$\tilde D^N$", False, r"No. The outer $\tilde T$ and $\tilde T^{-1}$ are not adjacent and do not cancel."),
        (r"$\tilde T^{-1}\tilde D^N\tilde T$", False, r"No, not for this $\tilde T$. This is the order the lecturer says aloud at 12:57 while unsure; his board derivation at 16:44 gives $\tilde T\tilde D\tilde T^{-1}$.")]),
    q("q-magnitude", r"A discrete-time system has eigenvalues $0.5 \pm 0.9i$. Is it stable?", [
        (r"No: $|\tilde\lambda| = \sqrt{1.06} \approx 1.03 > 1$, so it spirals outwards.", True, r"Right. The radius decides: $\tilde\lambda^N = r^Ne^{iN\theta}$ with $r \approx 1.03$ grows."),
        (r"Yes, because the real part $0.5$ is less than $1$.", False, r"No. This is the 'real part' wording at 16:10, which means magnitude. The magnitude is above one."),
        (r"Yes, because the real part is positive but small.", False, r"No. In discrete time the sign of the real part is not the test; the distance from the origin is."),
        (r"It is on the boundary, $|\tilde\lambda| = 1$.", False, r"No. $0.5^2 + 0.9^2 = 1.06$, not $1$.")]),
    q("q-map", r"$A$ has an eigenvalue $\lambda = -0.2 + 3i$ and is sampled with $\Delta t = 0.5$. Where is $\tilde\lambda$?", [
        (r"At radius $e^{-0.1} \approx 0.905$ and angle $1.5$ rad: inside the unit circle.", True, r"Right. $e^{\lambda\Delta t} = e^{-0.1}e^{1.5i}$. Negative real part maps inside the circle."),
        (r"At $-0.1 + 1.5i$.", False, r"No. That is $\lambda\Delta t$; the discrete eigenvalue is its exponential $e^{\lambda\Delta t}$."),
        (r"Outside the unit circle, because $|\lambda| > 1$.", False, r"No. Only the real part sets the radius: $|e^{\lambda\Delta t}| = e^{\mathrm{Re}\,\lambda\,\Delta t}$."),
        (r"On the unit circle, because the imaginary part dominates.", False, r"No. Only $\mathrm{Re}\,\lambda = 0$ lands on the unit circle.")]),
]

EXPLORER = {
    "kinds": [
        {"id": "real", "label": "Real λ₁, λ₂"},
        {"id": "complex", "label": "Complex a ± ib"},
        {"id": "jordan", "label": "Repeated, defective"},
    ],
    "kindDefault": "complex",
    "l1": {"min": -2, "max": 1, "step": 0.05, "default": -0.5},
    "l2": {"min": -2, "max": 1, "step": 0.05, "default": -1.5},
    "a": {"min": -2, "max": 1, "step": 0.05, "default": -0.3},
    "b": {"min": 0.2, "max": 4, "step": 0.05, "default": 2},
    "lj": {"min": -2, "max": 1, "step": 0.05, "default": -0.5},
    "s": {"min": -3, "max": 3, "step": 0.1, "default": 0},
    "x1": {"min": -2, "max": 2, "step": 0.1, "default": 1.5},
    "x2": {"min": -2, "max": 2, "step": 0.1, "default": 0},
    "dt": {"min": 0.05, "max": 1.5, "step": 0.05, "default": 0.25},
    "t": {"min": 0, "max": 10, "step": 0.01, "default": 4},
    "tMax": 10,
    "playRate": 1,
    "presets": [
        {"id": "spiral-in", "label": "Decaying spiral", "kind": "complex", "a": -0.3, "b": 2, "s": 0, "x1": 1.5, "x2": 0, "dt": 0.25, "t": 4,
         "expect": "asymptotic", "expectStart": "decays",
         "note": "$\\lambda = -0.3 \\pm 2i$: an oscillation inside the envelope $e^{-0.3t}$. The sampled eigenvalues sit inside the unit circle at radius $e^{-0.3\\Delta t}$."},
        {"id": "spiral-out", "label": "Growing spiral", "kind": "complex", "a": 0.15, "b": 2, "s": 0, "x1": 0.5, "x2": 0, "dt": 0.25, "t": 4,
         "expect": "unstable", "expectStart": "grows",
         "note": "$\\mathrm{Re}\\,\\lambda = 0.15 > 0$: a growing envelope. The discrete eigenvalues are just outside the unit circle, and the powers $\\tilde\\lambda^k$ spiral outwards."},
        {"id": "center", "label": "On the axis (center)", "kind": "complex", "a": 0, "b": 1.5, "s": 1, "x1": 1, "x2": 0.5, "dt": 0.5, "t": 6,
         "expect": "lyapunov", "expectStart": "bounded",
         "note": "Supplement: $\\lambda = \\pm 1.5i$ on the imaginary axis, $|\\tilde\\lambda| = 1$ on the unit circle. Bounded forever, never decaying: Lyapunov stable, not asymptotically stable."},
        {"id": "saddle", "label": "Saddle", "kind": "real", "l1": 0.4, "l2": -1, "s": 1, "x1": 1, "x2": 0.5, "dt": 0.5, "t": 5,
         "expect": "unstable", "expectStart": "grows",
         "note": "$\\lambda_1 = 0.4 > 0 > \\lambda_2 = -1$. This start has a component along the unstable eigenvector $c_1 = (1, 0)$, so it grows like $e^{0.4t}$."},
        {"id": "saddle-stable-start", "label": "Saddle, special start", "kind": "real", "l1": 0.4, "l2": -1, "s": 1, "x1": 1, "x2": 1, "dt": 0.5, "t": 5,
         "expect": "unstable", "expectStart": "decays",
         "note": "Same unstable system, but $x(0) = (1, 1)$ lies exactly on the stable eigenvector $c_2 = (s, 1)$, so $z_1(0) = 0$ and this one solution decays. The verdict for the system is still unstable. (The plot uses exact formulas; a floating-point simulation or a small disturbance may push the state off the eigenvector, after which it grows.)"},
        {"id": "zero-mode", "label": "Zero eigenvalue", "kind": "real", "l1": 0, "l2": -1, "s": 0.5, "x1": 1, "x2": 1, "dt": 0.5, "t": 6,
         "expect": "lyapunov", "expectStart": "bounded",
         "note": "Supplement: $\\lambda_1 = 0$ is semisimple, so its mode stays constant while the other decays: the state settles at a nonzero point. Lyapunov stable, not asymptotically stable; $\\tilde\\lambda_1 = 1$."},
        {"id": "jordan-zero", "label": "Defective at 0", "kind": "jordan", "lj": 0, "s": 0, "x1": 0, "x2": 1, "dt": 0.5, "t": 6,
         "expect": "unstable", "expectStart": "grows",
         "note": "Supplement: $J = \\begin{bmatrix}0&1\\\\0&0\\end{bmatrix}$ has $e^{Jt} = \\begin{bmatrix}1&t\\\\0&1\\end{bmatrix}$, so $x_1 = t$ grows linearly although no eigenvalue has positive real part. Unstable."},
        {"id": "transient", "label": "Stable, transient growth", "kind": "real", "l1": -0.2, "l2": -2, "s": 3, "x1": 0, "x2": 1, "dt": 0.25, "t": 1.3,
         "expect": "asymptotic", "expectStart": "decays",
         "note": "Supplement: both eigenvalues are negative, yet $|x_1|$ first grows to about $2.1$ before decaying, because the eigenvectors $(1, 0)$ and $(3, 1)$ are nearly parallel. Eigenvalues decide the long run, not the first few seconds."},
    ],
    "limits": "What the explorer covers: representative 2×2 systems from each of the three real canonical families (two real eigenvalues, including equal ones with A = λI; a complex pair a ± ib; a repeated defective eigenvalue with a Jordan block), with eigenvalues limited to the slider ranges (real parts −2 to 1, imaginary part 0.2 to 4) and a change of basis restricted to the shear T = [[1, s], [0, 1]]. You cannot type in an arbitrary matrix or model a particular physical system here. The classification rules themselves hold beyond these ranges: every real 2×2 matrix is similar to one of these families, and larger systems follow the same rules eigenvalue by eigenvalue, with the Jordan-block check on the boundary. The discrete-time panel shows sampled systems Ã = exp(AΔt); a general discrete system can have eigenvalues (0, or a single negative real one) that sampling never produces, but the unit-circle rule applies to it as well. Curves use exact closed forms; the verdict is computed from the eigenvalues and Jordan structure, never from the plotted window.",
    "tutorContext": "The explorer builds a real 2x2 system A = T J T^{-1} with T = [[1, s], [0, 1]] and one of three canonical forms J: real diag(l1, l2) (l1 = l2 gives A = l1 I); complex [[a, -b], [b, a]] with eigenvalues a +- ib (b > 0); or a defective Jordan block [[l, 1], [0, l]]. It plots the eigenvalues in the continuous-time plane (left half-plane shaded), the sampled eigenvalues e^{lambda dt} of A~ = e^{A dt} with the unit circle and the powers lambda~^k, and the time response x1(t), x2(t) from x(0) = (x1, x2) for 0 <= t <= 10 with the samples x_k = A~^k x_0 as dots. Verdicts: asymptotically stable (all Re < 0, all |lambda~| < 1), Lyapunov stable only (boundary eigenvalues semisimple), unstable (some Re > 0, or a defective eigenvalue on the boundary); plus the behaviour of the chosen start (decays, bounded, grows). Presets: decaying spiral, growing spiral, center (supplement), saddle, saddle with start on the stable eigenvector, zero eigenvalue (supplement), defective at 0 (supplement), stable with transient growth (supplement). The student's current slider values are not sent.",
}

COURSE = {
    "version": 1,
    "title": "Stability and Eigenvalues: continuous and discrete time",
    "subtitle": "A study companion to Steve Brunton's Control Bootcamp lecture on stability and Section 8.2 of Brunton & Kutz",
    "video": {"id": "h7nJ6ZL4Lf0", "title": "Stability and Eigenvalues [Control Bootcamp] (Steve Brunton, University of Washington)",
              "duration": "19:30", "url": "https://www.youtube.com/watch?v=h7nJ6ZL4Lf0"},
    "book": {"title": "Data-Driven Science and Engineering: Machine Learning, Dynamical Systems, and Control",
             "authors": "S. L. Brunton and J. N. Kutz", "edition": "2017 preprint (Chapter 8, Linear Control Theory, Section 8.2)",
             "onlineUrl": "http://databookuw.com/databook.pdf",
             "pageNote": "Page references give the printed page and the PDF page (printed page + 20 for these pages), checked against the copy downloaded from databookuw.com/databook.pdf on 18 October 2026. A later revision of the online file could paginate differently."},
    "attribution": "Course text, diagrams and animations here are original paraphrases and drawings made for this guide, and the numerical examples are authored for it. Sections marked Supplement go beyond what the lecture covers. They summarize the lecture and the book; for the original wording, watch the lecture and read the chapter. Lecture timestamps were located with YouTube's automatic captions and checked against video frames. The video, its captions and the chapter text are not included in this guide.",
    "explorer": EXPLORER,
    "sections": SECTIONS,
    "quiz": QUIZ,
}

# The correct answer is written first above; place it at a fixed, varied position per question.
for _i, _q in enumerate(QUIZ):
    _r = [2, 0, 3, 1, 1, 3, 0, 2, 3, 1][_i % 10]
    _q["choices"] = _q["choices"][-_r:] + _q["choices"][:-_r] if _r else _q["choices"]

if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(COURSE, f, indent=1, ensure_ascii=False)
    print(f"wrote {OUT}: {len(SECTIONS)} sections, {len(QUIZ)} questions")
