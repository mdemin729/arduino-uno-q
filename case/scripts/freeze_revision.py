"""Freeze the current build as a lettered revision.

Usage (run from case/, after building, checking and rendering):
    python scripts/freeze_revision.py B

Copies build/ into revisions/rev<X>/ with the revision in every file name.
Refuses to overwrite an existing revision: frozen revisions are never edited.
Afterwards add a row to REVISIONS.md, commit, and tag the commit case-rev<X>.
"""
import os
import shutil
import sys

CASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(CASE_DIR, "build")

# (build file, frozen name suffix). Only the files someone needs: the lid STL
# in print orientation, the lid STEP in mounted orientation.
FILES = [
    ("stl/unoq_base.stl", "stl", "base.stl"),
    ("stl/unoq_lid_print.stl", "stl", "lid_print.stl"),
    ("stl/unoq_window.stl", "stl", "window.stl"),
    ("stl/unoq_board.stl", "stl", "board_reference.stl"),
    ("step/unoq_base.step", "step", "base.step"),
    ("step/unoq_lid_assembled.step", "step", "lid_assembled.step"),
    ("step/unoq_window.step", "step", "window.step"),
]


def main():
    if len(sys.argv) != 2 or not (len(sys.argv[1]) == 1 and sys.argv[1].isalpha()):
        sys.exit("usage: python scripts/freeze_revision.py <single letter, e.g. B>")
    rev = sys.argv[1].upper()
    dest = os.path.join(CASE_DIR, "revisions", "rev" + rev)
    if os.path.exists(dest):
        sys.exit(f"revisions/rev{rev} already exists; revisions are frozen, pick the next letter")
    missing = [f for f, _, _ in FILES if not os.path.isfile(os.path.join(BUILD, f))]
    previews = sorted(os.listdir(os.path.join(BUILD, "preview"))) if os.path.isdir(
        os.path.join(BUILD, "preview")) else []
    if missing or not previews:
        sys.exit("build is incomplete, run unoq_case.py, check_fit.py and render_previews.py first.\n"
                 "missing: " + ", ".join(missing or ["build/preview/*.png"]))
    for src, sub, suffix in FILES:
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
        shutil.copy2(os.path.join(BUILD, src), os.path.join(dest, sub, f"unoq-case_rev{rev}_{suffix}"))
    os.makedirs(os.path.join(dest, "preview"))
    for p in previews:
        shutil.copy2(os.path.join(BUILD, "preview", p), os.path.join(dest, "preview", p))
    print(f"frozen revisions/rev{rev}: {len(FILES)} model files, {len(previews)} previews")
    print(f"next: add a row to REVISIONS.md, commit, then: git tag case-rev{rev}")


if __name__ == "__main__":
    main()
