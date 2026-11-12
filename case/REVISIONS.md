# Revision log

Naming: letter revisions (A, B, C ...) for design iterations, the usual
mechanical-drawing convention. Files carry the revision in the name, e.g.
`unoq-case_revA_base.stl`. Each revision is frozen under `revisions/rev<X>/`
and never edited; the working copy lives in `build/` and is not in git.

| Rev | Date | Status | Summary |
|-----|------|--------|---------|
| A | 2026-10-31 | Printed, fit on the first print | First design. Two-part snap-fit shell, 4 cantilever hooks, pegs through mounting holes, header hold-down ribs, LED window with separate clear plate, USB-C notch, flexible power-button tab, vents. Board thickness 1.0 mm, 5.5 mm under-board clearance, 0.15 mm fit clearance. Interference-checked against the official STEP model. |

## What a revision folder contains

- `stl/` print files: base, lid in print orientation, window, plus the board model for reference
- `step/` CAD for SolidWorks, lid in mounted orientation
- `preview/` renders

Rev A also has `source/`, a copy of the scripts as they were on 2026-10-31,
because it was made before the project was in git. Later revisions rely on a
git tag instead.

## Releasing a revision

From `case/`, after the design change is built, checked and rendered:

```bash
python scripts/freeze_revision.py B
```

Then add a row to the table above, commit, and tag the commit `case-revB`.

## Print results

- Rev A: printed on a QIDI Q1 Pro and reported on 2026-11-12. It fit on the
  first print with the default values. The board seats on the pegs, the lid
  snaps shut and the USB-C opening lines up. The clear window insert was not
  printed; the window was left open.

Still assumptions rather than measurements: the power button nub height
(`BTN_TOP`, assumed 4.3 mm switch) and the board thickness (`PCB_T = 1.0`
per datasheet). The lid fit (`CLR = 0.15`) depends on printer and filament.
