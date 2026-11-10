# MIT Learn Differential Equations: build progress

Playlist: https://www.youtube.com/playlist?list=PLUl4u3cNGP63oTpyxCMLKt_JmB0WtSZfG (68 videos,
Strang videos 1-56, Moler videos 57-68). Unit map, video IDs and book pages: [units.json](units.json).
Local book: `docs/DIFFER~1.pdf` (ignored by Git; PDF page = printed page + 12, checked on every numbered page). Notes are original
paraphrases with page references only; never copy book or caption text.

## Decisions (user, 10 November 2026)

- 12 units, one study package each, in `courses/mit-de/<slug>/`; one series course on the site.
- Build all units (no pilot pause). Claude Opus is architect; Sonnet agents for bounded work;
  Codex reviews (adversarial after plan/maths, standard before commit). Commit only when asked.
- Unit 11 (Moler numerical methods): explorer in JavaScript with **real-time visuals** of each
  method stepping (slopes, stages, step-size control, error), no MATLAB required.

## Shell

- Scaffold: `tools/scaffold_study.py --slug <slug> --subject mit-de --title <title> --port 883<n>`
  then `courses/mit-de/adapt_shell.py <slug>` (multi-video sources `v` + `t`, Strang book, no
  online-copy link). Ports 8831-8842 = units 1-12.
- course.json extras: `videos` [{n, id, title, duration, url}], `book.short`; every
  `sources.video` item has `v` (playlist number) and `t` (seconds within that video).
- Sources: `tools/prepare_unit.py --units courses/mit-de/units.json [--unit N]` (720p, frame every
  60 s, video deleted after frames; 45 s pause after each new download because of HTTP 429).

## Status

Source maps for every unit are in source-maps/ (Sonnet source-reader; verify against frames before use).
Codex: adversarial maths review per unit; one standard review of the whole tree before the final commit.

History: sources missing (YouTube answered "Sign in to confirm you're not a bot"; retries stopped
10 November 2026): videos 6, 15, 17, 21, 24, 28, 40, 41, 42, 44, 51, 65, 66, 67, 68. Do not loop
retries. User chose the browser sign-in: `tools/prepare_unit.py ... --cookies-from-browser firefox`
(Firefox; cookies read by yt-dlp at run time, never saved). All 68 videos ready (294 MB in sources/).


| Unit | Slug | Sources | Plan | Codex 1 | Content | Renders | QA | Codex 2 |
|---|---|---|---|---|---|---|---|---|
| 1 | first-order-linear | 10/10 | done (8 sections) | done: maths/quiz clean; 1 tool bug fixed | done (10 sequences, 33 steps; explorer by package-builder, reviewed) | done (4.7 MB) | math 515/515, check_study ok, browser 65/65, site 7/7 + 104/104 | done: no Unit 1 findings |
| 2 | nonlinear-first-order | 3/3, map in source-maps/unit-02.md | done (3 sections) | done: 3 findings fixed | done (6 sequences, 20 steps; explorer by package-builder) | done (2.6 MB) | math 519/519, check_study ok, browser 43/43 | at final review |
| 3 | second-order | 6/6, map in source-maps/unit-03.md | done (6 sections) | done: 2 findings fixed | done (6 sequences, 19 steps) | done (2.4 MB) | math 405/405, check_study ok, browser 45/45 | at final review |
| 4 | networks-and-methods | | | | | | | |
| 5 | laplace-transform | | | | | | | |
| 6 | phase-plane | | | | | | | |
| 7 | linear-algebra | 5/5, map in source-maps/unit-07.md | | | | | | |
| 8 | eigenvalues-systems | | | | | | | |
| 9 | positive-definite-svd | 2/2, map in source-maps/unit-09.md (check SVD board frame) | | | | | | |
| 10 | fourier-pde | | | | | | | |
| 11 | numerical-methods | | | | | | | |
| 12 | applications | | | | | | | |

### Unit 1 plan (draft)

Sections: 1 Overview (v1-2) · 2 Calculus you need (v3: product-rule check of
y = ∫0^t e^(t-s) q(s) ds, tangent line/parabola, Taylor) · 3 Exponential input (v4: Y = 1/(s-a),
y = y(0)e^(at) + (e^(st) - e^(at))/(s-a), resonance s = a gives t e^(at) by L'Hôpital) · 4 Oscillating
input (v5: M = -a/(ω²+a²), N = ω/(ω²+a²) checked; gain G = sqrt(M²+N²) = 1/sqrt(ω²+a²), tan α = N/M)
· 5 Any input (v6) · 6 Step and delta (v7) · 7 Complex exponential (v8) · 8-9 Integrating factors
(v9-10). Book 1.1-1.6 = PDF 13-64 (printed 1-52); text layer has empty page labels; printed = PDF - 12.
Explorer: y' = a y + q(t) with constant / e^(st) / cos ωt / step / delta inputs, showing y_p, y_n,
total and the resonance case.

Unit 1 is scaffolded and adapted (launcher `launch_first_order_linear.ps1`, port 8831).
Team-role commit done (ffedb3a, author khishanrap <khishanrap@gmail.com>, repository-local config).

Codex review 1, Unit 1 (gpt-6.1-sol, adversarial): verdict needs-attention for one tool bug only.
- [medium] prepare_study.py accepted any frame as a complete dropped-video cache. Fixed: the cache is
  complete only if every requested frame exists (same frame_times rule as extraction). Complete-cache
  path tested offline; the incomplete path needs YouTube and was not tested while blocked.
- No formula, worked-example, quiz or timestamp error found; numerical QA 515/515.

Codex review 2 (standard, whole working tree): no Unit 1 findings. Only finding: the Unit 2 launcher
fails because Unit 2 is not complete yet (expected; Unit 2 is excluded from the Unit 1 commit).
