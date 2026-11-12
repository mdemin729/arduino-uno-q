"""Interference check: official UNO Q STEP model vs. the generated case parts.

Usage: python scripts/check_fit.py [path to board STEP]
Default board model: case/reference/unoq_board_simplified.stp

Exits with status 1 if any board solid intersects the base or the lid.
Also writes build/stl/unoq_board.stl (board placed in case coordinates),
which the preview renders use.
"""
import os
import sys
import cadquery as cq
import unoq_case as C

sys.stdout.reconfigure(encoding="utf-8")
default_step = os.path.join(C.CASE_DIR, "reference", "unoq_board_simplified.stp")
step = sys.argv[1] if len(sys.argv) > 1 else default_step
os.makedirs(C.STL_DIR, exist_ok=True)

board = cq.importers.importStep(step)
solids = board.solids().vals()
pcb = max(solids, key=lambda s: s.BoundingBox().xlen * s.BoundingBox().ylen)
pb = pcb.BoundingBox()
dx, dy, dz = -pb.xmin, -pb.ymin, C.ZB - pb.zmin
placed = cq.Workplane("XY").newObject([s.translate((dx, dy, dz)) for s in solids])
bb = cq.Compound.makeCompound(placed.vals()).BoundingBox()
print("board placed: x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f"
      % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
cq.exporters.export(placed, os.path.join(C.STL_DIR, "unoq_board.stl"),
                    tolerance=0.05, angularTolerance=0.2)

total_hits = 0
for name, part in [("base", C.build_base()), ("lid", C.build_lid())]:
    hits = []
    for s in placed.vals():
        v = part.val().intersect(s).Volume()
        if v > 1e-3:
            hits.append((v, s.BoundingBox()))
    total_hits += len(hits)
    print(f"{name}: {len(hits)} interfering solids")
    for v, b in sorted(hits, key=lambda h: -h[0])[:15]:
        print("   vol %.2f mm3 at x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f"
              % (v, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))

# clearances that matter
print("peg top z %.2f vs board top %.2f" % (C.ZT + 0.8, C.ZT))
print("nub bottom z %.2f = %.2f above board top (switch top assumed %.1f)"
      % (C.ZT + C.BTN_TOP + 1.0, C.BTN_TOP + 1.0, C.BTN_TOP))
print("lid ceiling %.2f = %.2f above board top; tallest part top at %.2f"
      % (C.ZLI, C.LID_INNER, C.ZT + C.TALLEST_TOP))
sys.exit(1 if total_hits else 0)
