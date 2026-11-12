# Arduino UNO Q snap-fit case

Two-part snap-fit shell with a clear LED window, USB-C opening and a built-in
flexible power button. No screws. Designed for the QIDI Q1 Pro in PLA or PETG.

Board geometry comes from Arduino's official STEP model (ABX00162), kept in
`reference/`, and the mechanical drawing in the datasheet. The case is
checked against that model for interference (none).

Revision A has been printed on a QIDI Q1 Pro and fit on the first print: the
board seats on the pegs, the lid snaps shut and the USB-C opening lines up.

Overall size: 77.6 x 62.3 x 21.5 mm. Base 18.0 mm tall, lid 12.0 mm, parting
line 1 mm above the board surface.

## Files to print

Take them from the latest frozen revision, currently `revisions/revA/stl/`.

| File | What it is |
|------|------------|
| `unoq-case_revA_base.stl` | Bottom shell. Print as-is (floor on the bed). |
| `unoq-case_revA_lid_print.stl` | Lid, already flipped so the top face is on the bed. |
| `unoq-case_revA_window.stl` | 31 x 20 x 1 mm clear plate for the LED matrix window. |
| `unoq-case_revA_board_reference.stl` | Official board model in case coordinates. Reference only, do not print. |

`revisions/revA/step/` has the same parts for SolidWorks, with the lid in its
mounted orientation. `revisions/revA/preview/` has renders.

## Print settings (QIDI Studio, 0.4 mm nozzle)

- Layer height 0.2 mm, 3 walls, 4 top/bottom layers, 15 to 20 % infill.
- No supports needed on any part. All openings are either vertical or open
  toward the parting line.
- Base: floor down. Lid: use the `lid_print` file exactly as exported, the
  decorative top face lands on the textured plate.
- Window: print flat in transparent PLA or PETG, 100 % infill, 0.1 to 0.12 mm
  layers for best clarity. Slow down the top layer. Or skip it entirely and
  print the whole lid in clear PETG.
- PETG is the better choice for the lid because the snap hooks and the button
  tab flex. PLA works too, just avoid over-bending the hooks during assembly.

## Assembly

1. Drop the clear window into the pocket on the inside of the lid. It is a
   light press fit. A drop of CA glue or PETG-safe adhesive on two corners
   keeps it from rattling.
2. Place the board in the base, USB-C toward the notched end. The four pegs
   go through the mounting holes.
3. Lower the lid straight down until the four hooks click. The ribs in the
   lid press on the pin-header housings and hold the board down.
4. To open: pull up at the pry notch on the end opposite USB-C.

## If your print needs tuning

Revision A fit on the first print with the default values. Printers and
filaments differ, so these are the parameters to adjust if yours does not.

- Power button: the nub under the lid tab sits 5.3 mm above the board,
  assuming a 4.3 mm tall switch. Press the tab and make sure the board
  reboots only on a deliberate long press. If the nub never reaches the
  switch, lower `BTN_TOP` in the script. If it presses by itself, raise it.
- Board thickness: the design uses 1.0 mm (the value in Arduino's datasheet
  and STEP). If your board measures 1.6 mm, set `PCB_T = 1.6`.
- Lid fit: if the lid is too tight on the base, raise `CLR` from 0.15 to 0.2.
- Clearance under the board is 5.5 mm for the two 1.27 mm pitch headers on
  the underside. If your board has shorter parts there, `UNDER_PARTS` can
  come down to lower the whole case.

## Changing the design

All parameters are constants at the top of `scripts/unoq_case.py`. Run from
this folder:

```bash
pip install -r requirements.txt
```

```bash
python scripts/unoq_case.py
```

```bash
python scripts/check_fit.py
```

The first writes STL and STEP files into `build/`. The second checks the
result against the board model and must report 0 interfering solids. Preview
renders need Blender:

```bash
"C:/Program Files/Blender Foundation/Blender 4.5/blender.exe" -b --python scripts/render_previews.py
```

`build/` is a scratch area and is not kept in git. Releasing a new revision
is described in [REVISIONS.md](REVISIONS.md).
