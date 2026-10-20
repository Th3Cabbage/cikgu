# Controllability review — 20 October 2026

Playlist lecture 5, [Controllability](https://www.youtube.com/watch?v=u5Sv7YKAkt4), 32:29.
Six sections, six original ManimGL sequences (24 steps / 30 stills), six worked examples,
ten explanatory quiz questions and a column-space explorer. Public path:
`/controls/controllability/`; standalone `launch_controllability.ps1`, port 8820.

Codex reviewed the cached English auto-captions, board/MATLAB frames and the local textbook
PDF pages 356–357 (printed 336–337), then supplied a compact source capsule. Claude Opus 5.5
implemented the lesson-specific content, math, scenes and explorer in one fresh session.
Codex owned rendering, independent numerical references, browser checks and site integration.
The source distinctions and corrections are in [SOURCE_REVIEW.md](SOURCE_REVIEW.md).

## Verification

- Independent NumPy/SciPy check: 469 cases, including random multi-input/higher-dimensional
  pairs, zero/weak/eigenvector actuators, left singular vectors and two-step states.
  Maximum singular-value absolute error 2.274e-13. The authored K=[6,6] example has closed-loop
  eigenvalues -1,-2; three-state chain examples are checked by the same controllability formula.
- Reusable media/content audit: all 24 clips fully decoded, referenced files present,
  consistent sections/steps/quiz, no source files in dist; all 669 formulas typeset by KaTeX.
- All stable-state contact sheets inspected. Preview caught a 2D/3D coordinate mismatch;
  final review staggered overlapping dimension labels and clarified free motion from x1(0).
  Only affected sequences were rebuilt after these fixes.
- Shared standalone browser contract passed 50 checks: every animation step, back/replay,
  quiz retries/completion, saved steps, responsive layout, reduced motion and no-key tutor.
  An additional explorer-only run passed 36 checks, including all six presets, zero input,
  actuator toggles, off-scale points, persistence and rejection of corrupt saved settings.
  The final unified run, including the lesson-specific explorer hook, passed 75/75 checks.
- Combined website: 104/104 browser checks and 7/7 build tests passed. After the last media
  revision the site was rebuilt and all 7 build tests passed again. All 509 referenced media
  files resolve; final output is 968 files / 51.3 MB, six guides in two courses.
- Routed-workflow/source tests: 10/10; layout/scaffold checks include all six guides and the
  corrected renderer. The real PowerShell launcher served the expected identity, video ID
  and six sections on port 8820; Ctrl+C stopped the owned server.

## Efficiency trial

`tools/study_pipeline.py` routes the registered playlist to the Controls/controllability recipe,
caches sources, generates a bounded brief, tracks stages, and forwards a Claude API budget cap.
Checkpoint updates now merge under a lock so concurrent author/render stages do not lose state.
Preview renders one scene without publishing a partial manifest; the full build can reuse its
master when the source hash is unchanged. Shared QA replaces copied lesson-wide harnesses.

Claude run `controllability-efficient`: 823.1 s (13m43s), 87,256 output tokens,
2,895,749 cached-input tokens and 151,303 cache-creation input tokens; reported list-price
estimate $3.5349498 against a CLI budget of $4. Previous Linearization authoring used two runs,
323,667 output tokens and a combined $18.975378 list estimate. This trial used about 73% fewer
Claude output tokens and an 81% lower estimate. These are different lessons (24 vs 41 steps),
not a controlled benchmark; Codex usage, source preparation, tooling and review time are excluded.
Cached input is repeated context reading, not unique text. Estimates are not confirmed bills.

This first run used medium effort. Long thinking pauses remained noticeable; subsequent pipeline
authoring defaults to low effort with independent review retained. Raw logs and checkpoints stay
under ignored qa/scratch and sources. Durable commands/contracts are in tools/README.md.

No live tutor API call, commit, push or deployment was made. GPT is ready for local configuration;
it is disabled on the static shared site. Rendering was tested on this Windows environment.
