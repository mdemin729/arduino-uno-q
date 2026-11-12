# Reference data

Input the case model is checked against. This file is Arduino's work, not
mine.

| File | Source |
|------|--------|
| `unoq_board_simplified.stp` | "UNO Q simplified.stp" from https://docs.arduino.cc/resources/models/ABX00162-step.zip, linked on https://docs.arduino.cc/hardware/uno-q/. Downloaded 2026-10-31, unmodified apart from the file name. |

Licence: Creative Commons Attribution-ShareAlike 4.0, © Arduino. The archive
is part of the Arduino documentation repository
(https://github.com/arduino/docs-content, under
`content/hardware/uno/boards/uno-q/downloads/`), which is published under
CC BY-SA 4.0. The licence text is in `LICENSE-CC-BY-SA-4.0` at the root of
this repository.

`scripts/check_fit.py` reads the STEP file to check the case for
interference. It also writes a tessellated copy, moved into case
coordinates. The frozen copy of that file,
`revisions/revA/stl/unoq-case_revA_board_reference.stl`, is therefore a
derivative of Arduino's model and carries the same licence.

Board dimensions that are not in the STEP model came from the mechanical
drawing in the UNO Q datasheet, section 12 "Mechanical Information":
https://docs.arduino.cc/resources/datasheets/ABX00162-datasheet.pdf
The drawing is not copied here.

Notes on the STEP model:

- It is a simplified model. Small passives are missing, and the power switch
  is a 2.1 mm block without its actuator.
- The PCB solid is 1.0 mm thick.
- The two 3 x 38.5 mm solids under the board, 5 mm tall, are the 2x30
  1.27 mm pitch headers.
