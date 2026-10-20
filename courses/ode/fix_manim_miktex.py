"""Let ManimGL 1.7.2's `latex` template work with MiKTeX, in this project's .venv only.

ManimGL passes `-no-pdf` to every LaTeX compiler, but that option exists only for xelatex.
MiKTeX's `latex` rejects it ("unknown option"), so every Tex/TexText fails. This script
edits .venv/Lib/site-packages/manimlib/utils/tex_file_writing.py to pass `-no-pdf` only
when compiler == "xelatex". All other compiler arguments stay the same.

Run it again after reinstalling ManimGL:

    .\\.venv\\Scripts\\python.exe courses\\ode\\fix_manim_miktex.py

It is idempotent. It exits 0 if the fix is already present, and exits 1 without writing
anything if the module is outside this project's .venv or its source isn't the expected code.
"""
import shutil
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
VENV_DIR = PROJECT_DIR / ".venv"
TARGET = VENV_DIR / "Lib" / "site-packages" / "manimlib" / "utils" / "tex_file_writing.py"
BACKUP = PROJECT_DIR / "backup" / "tex_file_writing.py.orig-manimgl-1.7.2"

ORIGINAL = '''            [
                compiler,
                "-no-pdf",
                "-interaction=batchmode",
'''
FIXED = '''            [
                compiler,
                *(["-no-pdf"] if compiler == "xelatex" else []),
                "-interaction=batchmode",
'''


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    target = TARGET.resolve()
    if not target.is_relative_to(VENV_DIR.resolve()):
        fail(f"{target} is not inside this project's venv ({VENV_DIR}); refusing to change it")
    if not target.is_file():
        fail(f"{target} not found; is ManimGL installed in {VENV_DIR}?")

    with open(target, encoding="utf-8", newline="") as f:
        source = f.read()

    if source.count(FIXED) == 1 and ORIGINAL not in source:
        print(f"Already applied: {target}")
        return
    if source.count(ORIGINAL) != 1 or FIXED in source:
        fail(
            f"{target} does not contain the expected ManimGL 1.7.2 compiler arguments; "
            "not changing it. Check the installed ManimGL version."
        )

    if not BACKUP.exists():
        BACKUP.parent.mkdir(exist_ok=True)
        shutil.copy2(target, BACKUP)
        print(f"Backed up original to {BACKUP}")

    with open(target, "w", encoding="utf-8", newline="") as f:
        f.write(source.replace(ORIGINAL, FIXED))
    print(f"Applied: -no-pdf now passed only for xelatex in {target}")


if __name__ == "__main__":
    main()
