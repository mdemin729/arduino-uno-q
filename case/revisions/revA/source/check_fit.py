"""Interference check: official UNO Q STEP model vs. the generated case parts.
Usage: python check_fit.py <path to "UNO Q simplified.stp">
Also writes output/unoq_board.stl (board placed in case coordinates) for renders.
"""
import os
import sys
import cadquery as cq
import unoq_case as C

sys.stdout.reconfigure(encoding="utf-8")
step = sys.argv[1]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

board = cq.importers.importStep(step)
solids = board.solids().vals()
pcb = max(solids, key=lambda s: s.BoundingBox().xlen * s.BoundingBox().ylen)
pb = pcb.BoundingBox()
dx, dy, dz = -pb.xmin, -pb.ymin, C.ZB - pb.zmin
placed = cq.Workplane("XY").newObject([s.translate((dx, dy, dz)) for s in solids])
bb = placed.val().BoundingBox() if len(solids) == 1 else cq.Compound.makeCompound(placed.vals()).BoundingBox()
print("board placed: x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
cq.exporters.export(placed, os.path.join(out, "unoq_board.stl"), tolerance=0.05, angularTolerance=0.2)

base, lid = C.build_base(), C.build_lid()
for name, part in [("base", base), ("lid", lid)]:
    hits = []
    for s in placed.vals():
        try:
            inter = part.val().intersect(s)
            v = inter.Volume()
        except Exception as e:  # noqa
            v = -1
        if v > 1e-3:
            b = s.BoundingBox()
            hits.append((v, b))
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
