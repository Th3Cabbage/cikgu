# Linear Systems study companion

From the project root, open the browser guide with:

```powershell
.\launch_linear_systems.ps1
```

It opens `http://127.0.0.1:8780/`, or the next free port. Keep the terminal open;
Ctrl+C stops the server. Viewing uses standard-library Python; no rendering installation
or API key is needed. Open the page through the launcher, rather than opening index.html directly.

The guide covers the full 24:47 [Linear Systems lecture](https://www.youtube.com/watch?v=nyqJJdhReiA):
six sections, 33 rendered ManimGL steps, notes, worked examples, an interactive eigenbasis
explorer, and ten quiz questions with explanations for every choice. Section 6 covers the
linked 22:22 explanation. Use Next step, Back, Replay and Restart to control each derivation.
Themes and progress are saved locally in your browser.

Book links use the supplied `databook.pdf` at the repository root: printed pages 331–332, PDF pages 351–352,
Section 8.2, Eqs. 8.11–8.19. The lecture uses D for the diagonal matrix; the book uses Lambda.
The numerical worked example is authored for this guide. The explorer uses the exact family
T = [[1,s],[0,1]] and A = T D T^-1; it illustrates the coordinate pipeline without covering
every possible 2×2 matrix. Defective matrices are discussed in a note.

The optional **Ask GPT** panel is ready to enable later. To enable it, configure
`OPENAI_API_KEY` locally before launching; `OPENAI_MODEL` optionally selects the model.
Without a key, lessons, animations, the explorer and quiz still work. Live chat was not tested
against a paid API.

Course content is maintained in `course_source.py`; regenerate JSON with:

```powershell
.\.venv\Scripts\python.exe courses\controls\linear-systems\course_source.py
```

Animations are authored in `animation/sequence_scenes.py`, with metadata in
`animation/control_specs.py`. Render using the existing root environment:

```powershell
.\.venv\Scripts\python.exe courses\controls\linear-systems\animation\build_sequences.py --jobs 2
```

For a focused revision, add `--only sequence-id`. The delivered media are already rendered.
Source downloads and local Whisper transcription are cached outside the web bundle.
See [the reusable workflow](../../../tools/README.md) for download, scaffolding and Claude commands.

Validation commands, from the project root:

```powershell
.\.venv\Scripts\python.exe qa\linear_systems_qa.py
node qa\linear_systems_browser_qa.js
node qa\linear_explorer_regression.js
.\.venv\Scripts\python.exe tools\check_study.py --package linear-systems --decode
```

The Python QA also needs Node and Git (PATH or the usual Windows Git installation).
[Review notes](REVIEW.md) record the results.
