# Stability and Eigenvalues study companion

From the project root, open the browser guide with:

```powershell
.\launch_stability_eigenvalues.ps1
```

It opens `http://127.0.0.1:8790/`, or the next free port (`-NoBrowser` serves only). Keep the
terminal open; Ctrl+C stops the server. Viewing uses standard-library Python; no rendering
installation or API key is needed. Open the page through the launcher, not index.html directly.

The guide covers the whole 19:30 [Stability and Eigenvalues lecture](https://www.youtube.com/watch?v=h7nJ6ZL4Lf0)
(Control Bootcamp playlist item 3), continuous and discrete time: six sections, seven ManimGL
sequences with 38 steps, notes, original worked examples, an explorer and ten explained quiz
questions. Use Next, Back, Replay and Restart. Themes and progress are saved locally in the browser.

| Section | Lecture | Content |
|---|---|---|
| 1 Only the modes evolve | 0:00–3:20 | x(t) = T e^{Dt} T^-1 x(0); modes; one growing mode |
| 2 Complex λ: the envelope | 3:20–5:55 | Euler's formula, \|e^{λt}\| = e^{at}, conjugate pairs |
| 3 Left half-plane | 5:55–9:05 | Re λ < 0 criterion, control preview, inverted pendulum; Supplement on boundary cases |
| 4 Discrete time | 9:05–12:45 | x_k = x(kΔt), Ã = e^{AΔt}, x_N = Ã^N x_0 |
| 5 Unit circle | 12:45–17:35 | Ã^N = T̃D̃^N T̃^-1, r^N e^{iNθ}, \|λ̃\| < 1 |
| 6 Conformal map, summary | 17:35–19:30 | λ ↦ e^{λΔt}, left half-plane → disc, upshot |

**Sources.** Timestamps come from YouTube's automatic English captions (no Whisper needed) and were
checked against video frames. Two spoken slips are flagged in the guide: at 12:57 the lecturer says
Ã = T⁻¹DT (unsure; his board derivation at 16:44 gives TDT⁻¹), and at 16:10 he says "real part"
where the magnitude is meant. Book links use root `../databook.pdf`, the 2017 preprint downloaded from
databookuw.com/databook.pdf: printed pp. 332, 334, 335 = PDF pp. 352, 354, 355 (Eqs. 8.19, 8.21–8.22,
Fig. 8.7, pendulum example). The lecture writes D and Ã where the book writes Λ and A_d.

**Authored versus lecture material.** All worked examples are authored. Sections and steps labelled
*Supplement* go beyond the lecture: eigenvalues exactly on the imaginary axis / unit circle
(semisimple: Lyapunov but not asymptotic stability; defective/Jordan: unstable), transient growth,
aliasing, Euler's method and invertibility of sampled systems. The lecture itself states the strict
criteria and assumes a full set of eigenvectors.

**Explorer.** Representative real 2×2 systems from the three canonical families (real λ₁, λ₂ including
A = λI; complex a ± ib; repeated defective Jordan block) with slider-limited eigenvalues and the shear
basis T = [[1,s],[0,1]], A = T J T⁻¹. It shows the eigenvalues, the sampled eigenvalues e^{λΔt} with
the unit circle and their powers, and x(t) with the samples x_k = Ã^k x_0 (computed by iteration).
Curves use exact closed forms; the verdict (asymptotically stable / Lyapunov only / unstable, plus the
behaviour of the chosen start) comes from eigenvalues and Jordan structure, never from the plotted
window. Each eigenvalue is coloured by its own mode (decaying green, growing red, boundary amber,
defective boundary red). Off-scale curves are clipped with a warning. The time reached during playback
is saved when you leave the page or reload; playback does not resume automatically. It does not accept arbitrary matrices or model a
specific physical system; the explorer page states these limits.

The optional **Ask GPT** panel works only if `OPENAI_API_KEY` is set locally before launching
(`OPENAI_MODEL` optional). Without a key everything else works. No paid API call was made in testing.

## Maintaining

```powershell
.\.venv\Scripts\python.exe stability-eigenvalues\course_source.py                  # regenerate dist/course.json
.\.venv\Scripts\python.exe stability-eigenvalues\animation\build_sequences.py --jobs 1
```

Scenes are in `animation/sequence_scenes.py`, step metadata in `animation/control_specs.py`, the
explorer in `dist/explorer.js` with its math in `dist/study_math.js`. Render with `--jobs 1` (the
default here): parallel renders collided on ManimGL's shared temporary SVG files for identical text.
Use `--only sequence-id` for a targeted revision. A quick error check that does not open a preview
window is `manimgl sequence_scenes.py <Scene> -w -s` (always pass `-w`; `-s` alone opens a window).
The tested render took about 130 s for all seven sequences.

Validation, from the project root (Node, Git and installed Chrome required for the browser test):

```powershell
.\.venv\Scripts\python.exe qa\stability_qa.py
node qa\stability_explorer_regression.js
node qa\stability_browser_qa.js
.\.venv\Scripts\python.exe tools\check_study.py --package stability-eigenvalues --decode
.\.venv\Scripts\python.exe qa\stability_contact_sheet.py
```

[Review notes](REVIEW.md) record the results and limitations.
