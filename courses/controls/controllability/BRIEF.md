# Controllability: focused implementation

Read CLAUDE.md and .claude/skills/build-study-package/SKILL.md once. You are the implementer;
Codex reviews sources, mathematics, rendered output and shared browser integration.
Use a fresh session; do not launch other agents or Claude processes.

Package: courses/controls/controllability; video https://www.youtube.com/watch?v=u5Sv7YKAkt4; subject controls; strategy controllability.
Approach: Matrix construction with visible multiplication, rank and reachable-subspace geometry. Reuse the browser player; implement only the new mathematics and explorer.

Read sources/controllability/transcript.txt, sources/controllability/book.txt if present, and
sources/controllability/REVIEW.md (reviewed timestamps, source distinctions and corrections).
Do not read raw video.info.json, old BRIEF/HANDOVER logs or entire previous lesson implementations.
Read tools/README.md for contracts, ctl_common.py signatures and one relevant scene excerpt only.
The player/server/vendor/theme/render helper are already scaffolded: reuse them.

Author only course_source.py -> dist/course.json, animation/control_specs.py,
animation/sequence_scenes.py, dist/study_math.js, dist/explorer.js and a short package README.
Create source-backed sections covering the whole lecture, worked examples and 8-10 explanatory quiz
questions. Use the existing course schema and original paraphrases. Keep each animation operation
visible; use explicit safe stage bounds and split long formulas across rows. Aim for 5-6 sequences
of 3-5 clear operations when that covers the material; do not omit essential lecture topics.
The explorer needs validated saved state, immediate updates and correct edge cases.
Keep the mathematical core dependency-free and callable from Node for independent numerical QA.
Add a compact qa_cases.json with reference examples and the math export contract for review.

Do NOT render, run full browser suites, create duplicate QA harnesses, edit shared catalog/tools,
or commit/push. Codex handles these once. Run the content generator and basic syntax/math smoke
checks, then stop and report output paths, exports, assumptions and remaining concerns in <250 words.
Keep terminal output compact; avoid reading unchanged files repeatedly.
