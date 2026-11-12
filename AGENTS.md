# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this is

Hardware project around the Arduino UNO Q. So far it holds one thing: a
3D-printable snap-fit case, modelled as code with CadQuery. The repo root is
kept free for future UNO Q work (sketches, apps); anything case-related lives
under `case/`.

## Layout

```
AGENTS.md              this file
README.md              project overview
case/
  README.md            print settings, assembly, what to verify on a print
  REVISIONS.md         revision log (one row per frozen revision)
  requirements.txt     Python dependencies
  scripts/
    unoq_case.py         the parametric model, single source of truth
    check_fit.py         interference check against the official board model
    render_previews.py   Blender headless renders
    freeze_revision.py   copies build/ into revisions/rev<X>/
  reference/           official Arduino board STEP model (input for the fit check)
  build/               generated STL / STEP / previews. Git-ignored, regenerable
  revisions/revA/      frozen release. Never edit
```

## Commands

Run everything from `case/`.

```bash
pip install -r requirements.txt
python scripts/unoq_case.py          # build -> build/stl, build/step
python scripts/check_fit.py          # must print 0 interfering solids, exits 1 otherwise
"C:/Program Files/Blender Foundation/Blender 4.5/blender.exe" -b --python scripts/render_previews.py
python scripts/freeze_revision.py B  # only when the user asks to release a revision
```

There are no unit tests. A change is verified when all of these hold:

1. `unoq_case.py` reports `solids 1` for every part. More than one means a
   feature is floating and would print detached.
2. `check_fit.py` exits 0.
3. You looked at the renders in `build/preview/`. Booleans can silently produce
   wrong geometry that still passes 1 and 2.

## Model conventions

- Units are millimetres.
- Board coordinates: `(0,0)` is the board corner at the USB-C edge (`x=0`) on
  the ANALOG/POWER header side (`y=0`). Board is 68.58 x 53.34. `z=0` is the
  underside of the case floor.
- All tunable values are constants at the top of `unoq_case.py`, in two
  blocks: board data (measured, do not guess) and case parameters (design
  choices). Change values there, not inside the build functions.
- Board data came from `reference/unoq_board_simplified.stp` and the datasheet
  drawing. If a dimension is needed that is not in the script, measure it from
  the STEP with CadQuery. Do not estimate from photos.
- Booleans with coincident faces are unreliable. Overlap unions and overshoot
  cuts by a small amount, as the existing code does.
- `render_previews.py` runs in Blender's Python and cannot import the model.
  Its `LID_CEILING_Z` must be kept equal to the `ceiling` level the build prints.

## Printing constraints (design rules)

Target printer: QIDI Q1 Pro, 0.4 mm nozzle, PLA or PETG, sliced in QIDI Studio.

- No supports. Every opening is vertical or open toward the parting line.
- The lid prints upside down with its top face on the bed, so nothing may
  protrude from the lid top. Use recesses, not raised marks.
- Minimum wall 0.8 mm (two perimeters). Sliding-fit clearance is `CLR` (0.15).
- Flexing features (snap hooks, button tab) are sized for about 1.5 % strain.
  Recheck with `strain = 3*t*deflection / (2*L^2)` before changing their
  length or thickness.

## Revisions

- Letter revisions: A, B, C. File names carry it: `unoq-case_revB_base.stl`.
- `revisions/rev<X>/` is frozen once created. Never modify, rename or delete
  files in it. A fix is a new revision.
- `build/` is the working copy and is not committed.
- To release: build, check, render, run `freeze_revision.py <letter>`, add a
  row to `case/REVISIONS.md`, commit, tag the commit `case-rev<X>`. The tag
  preserves the exact source, so new revisions do not need a `source/` copy
  (Rev A has one because it predates git).
- Do not release a revision unless the user asks for it.

## Licensing

The repository is public. Three licences apply; the README has the summary.

- Python scripts: MIT (`LICENSE`).
- Case design files and documentation: CC BY-SA 4.0 (`LICENSE-CC-BY-SA-4.0`).
- `case/reference/unoq_board_simplified.stp` and every
  `..._board_reference.stl` derived from it are Arduino's, CC BY-SA 4.0.
  Keep the attribution in `case/reference/README.md`.

Before adding any third-party file (a datasheet page, a vendor model, an
image, a font), confirm its licence allows redistribution and record the
source and licence next to it. If that cannot be confirmed, link to it
instead of copying it.

## Known unknowns

Rev A was printed on a QIDI Q1 Pro and fit on the first print with the values
below (owner's report, 2026-11-12): the board seats on the pegs, the lid
snaps shut, the USB-C opening lines up. None of these values has been
measured on the physical board, and the power-button tab was not reported on
separately. Treat them as "worked once on one printer", not as facts, and
update this list and `case/REVISIONS.md` when the user reports more.

- `BTN_TOP = 4.3`: the STEP models the power switch body without its actuator.
- `PCB_T = 1.0`: from the datasheet and STEP; typical boards are 1.6.
- `CLR = 0.15`: lid-to-base fit. Printer and filament dependent.

## Working in this environment

- Windows 11. Both PowerShell and Git Bash are available. Python 3.13 with
  CadQuery 2.8 is installed system-wide.
- Bash heredocs containing apostrophes have failed here. Write multi-line
  files with a file-write tool instead of `cat <<EOF`.
- `python -I` ignores `PYTHONIOENCODING`. Scripts that print non-ASCII call
  `sys.stdout.reconfigure(encoding="utf-8")`.
- Git: commit only when the user asks. Never commit `build/`.
- Commits in this repository use the owner's GitHub noreply address, set in
  the repository's local git config. Do not change it.
- Line endings are fixed by `.gitattributes`: text is LF everywhere, and
  STEP/STL/PNG files are never converted so frozen revisions stay byte-exact.
  Add any new binary or CAD file type there before committing it.
