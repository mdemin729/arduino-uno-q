"""
Arduino UNO Q snap-fit case, parametric, built with CadQuery.

Coordinate system
  x, y : board coordinates in mm. (0,0) = board corner at the USB-C edge (x=0)
         on the ANALOG/POWER header side (y=0). Board is 68.58 x 53.34.
  z    : 0 = underside of the case floor.

All board geometry below was measured from the official Arduino STEP model
(ABX00162, "UNO Q simplified.stp") and the datasheet mechanical drawing.

Run:  python unoq_case.py   -> writes STL + STEP into ./output
"""
import os
import cadquery as cq

# ---------------------------------------------------------------- board data
BOARD_W, BOARD_L = 68.58, 53.34          # x, y
PCB_T = 1.0                              # datasheet + STEP both say 1.0 mm
HOLES = [(13.97, 2.54), (15.24, 50.80), (66.04, 7.62), (66.04, 35.56)]
HOLE_D = 3.2
# USB-C receptacle: on the x=0 edge, y 33.4..42.3, 3 mm tall above board
USB_Y0, USB_Y1 = 33.4, 42.3
# Power button (6x6 tact) centre, and top of its actuator above the board
BTN_X, BTN_Y = 5.84, 49.40
BTN_TOP = 4.3                             # typical 6x6x4.3 SMD switch
# LED matrix, body extent of the 13x8 LEDs
LED_X0, LED_X1, LED_Y0, LED_Y1 = 31.41, 58.32, 4.63, 20.33
# Header rows (tops are 8.5 mm above board top)
DIG_X0, DIG_X1, DIG_Y0, DIG_Y1 = 17.3, 65.1, 49.56, 52.06
ANA_X0, ANA_X1, ANA_Y0, ANA_Y1 = 26.4, 65.1, 1.30, 3.80
HEADER_H = 8.5
TALLEST_TOP = 10.0                        # JCTL 2x5 header
UNDER_PARTS = 5.0                         # 2x30 1.27 mm headers on the bottom
# SoC / memory region (for vents)
HOT_X0, HOT_X1, HOT_Y0, HOT_Y1 = 27.0, 42.0, 23.5, 47.0

# ---------------------------------------------------------------- case params
WALL = 2.0
FLOOR = 2.0
TOP = 2.0
GAP = 2.5            # board edge -> inner wall face (room for the hooks)
R_OUT = 3.0          # outer vertical corner radius
H_UNDER = UNDER_PARTS + 0.5
LID_INNER = TALLEST_TOP + 1.0            # inner height above board top
SPLIT_ABOVE_BOARD = 1.0                  # parting line above board top
LIP_H = 1.5
CLR = 0.15           # sliding-fit clearance (PLA / PETG, 0.4 nozzle)

HOOK_W, HOOK_T, HOOK_H, CATCH = 8.0, 1.0, 8.5, 0.5
HOOK_XS = [12.0, 56.0]                   # along the long (header) walls

WIN_MARGIN = 1.0                         # LED body -> window opening
WIN_PLATE_T = 1.0

# derived levels
ZB = FLOOR + H_UNDER                     # board underside
ZT = ZB + PCB_T                          # board top
ZS = ZT + SPLIT_ABOVE_BOARD              # parting plane
ZLI = ZT + LID_INNER                     # lid ceiling
ZLO = ZLI + TOP                          # lid outer top

OX0, OY0 = -GAP - WALL, -GAP - WALL      # outer box corner
OX1, OY1 = BOARD_W + GAP + WALL, BOARD_L + GAP + WALL
IX0, IY0 = -GAP, -GAP                    # inner wall faces
IX1, IY1 = BOARD_W + GAP, BOARD_L + GAP


def rrect(x0, y0, x1, y1, z0, z1, r):
    """Rounded-corner box between two xy corners and two z levels."""
    w, l = x1 - x0, y1 - y0
    b = (cq.Workplane("XY").workplane(offset=z0)
         .center((x0 + x1) / 2, (y0 + y1) / 2).rect(w, l).extrude(z1 - z0))
    if r > 0:
        b = b.edges("|Z").fillet(r)
    return b


def box(x0, y0, x1, y1, z0, z1):
    return rrect(x0, y0, x1, y1, z0, z1, 0)


def cyl(x, y, z0, z1, d):
    return (cq.Workplane("XY").workplane(offset=z0).center(x, y)
            .circle(d / 2).extrude(z1 - z0))


def shell_ring(inset_outer, inset_inner, z0, z1):
    """Ring between two insets of the outer outline."""
    o = rrect(OX0 + inset_outer, OY0 + inset_outer, OX1 - inset_outer, OY1 - inset_outer,
              z0, z1, max(R_OUT - inset_outer, 0.3))
    i = rrect(OX0 + inset_inner, OY0 + inset_inner, OX1 - inset_inner, OY1 - inset_inner,
              z0 - 1, z1 + 1, max(R_OUT - inset_inner, 0.3))
    return o.cut(i)


def vent_slots(z0, z1, n=7, slot_w=1.4):
    ys = [HOT_Y0 + 2 + i * (HOT_Y1 - HOT_Y0 - 4) / (n - 1) for i in range(n)]
    cutter = None
    for y in ys:
        s = rrect(HOT_X0, y - slot_w / 2, HOT_X1, y + slot_w / 2, z0, z1, slot_w / 2 - 0.01)
        cutter = s if cutter is None else cutter.union(s)
    return cutter


# ---------------------------------------------------------------- hooks
def hook(xc, side):
    """Cantilever snap hook rising from the base wall, catch facing outward.
    side = -1 for the y-min wall, +1 for the y-max wall."""
    yo = -GAP + 0.2                 # outer face, 0.2 clear of the lid wall
    yi = yo + HOOK_T                # inner face (toward the board)
    yc = yo - CATCH                 # catch tip
    z0 = ZS
    pts = [(yi, z0), (yo, z0),
           (yo, z0 + HOOK_H - 1.5),
           (yc, z0 + HOOK_H - 1.0),
           (yc, z0 + HOOK_H - 0.5),
           (yo + 0.3, z0 + HOOK_H),
           (yi, z0 + HOOK_H)]
    if side > 0:
        pts = [(BOARD_L - y, z) for (y, z) in pts]
    prof = (cq.Workplane("YZ").workplane(offset=xc - HOOK_W / 2)
            .polyline(pts).close().extrude(HOOK_W))
    # root block that fuses the hook to the lip
    if side < 0:
        root = box(xc - HOOK_W / 2, -GAP - 0.5, xc + HOOK_W / 2, yi, ZS - 0.5, ZS + LIP_H)
    else:
        root = box(xc - HOOK_W / 2, BOARD_L - yi, xc + HOOK_W / 2, BOARD_L + GAP + 0.5,
                   ZS - 0.5, ZS + LIP_H)
    return prof.union(root)


def hook_pocket(xc, side):
    """Blind pocket in the lid wall that the catch snaps into."""
    w = HOOK_W + 2 * 0.2
    z0 = ZS + HOOK_H - 1.6
    z1 = ZS + HOOK_H + 0.4
    d = CATCH + 0.15
    if side < 0:
        return box(xc - w / 2, -GAP - d, xc + w / 2, -GAP + 0.3, z0, z1)
    return box(xc - w / 2, BOARD_L + GAP - 0.3, xc + w / 2, BOARD_L + GAP + d, z0, z1)


# ---------------------------------------------------------------- base
def build_base():
    base = rrect(OX0, OY0, OX1, OY1, 0, ZS, R_OUT)
    base = base.edges("<Z").fillet(1.0)
    cavity = rrect(IX0, IY0, IX1, IY1, FLOOR, ZS + 1, R_OUT - WALL)
    base = base.cut(cavity)
    # lip on the inner half of the wall
    base = base.union(shell_ring(WALL / 2, WALL, ZS - 0.1, ZS + LIP_H))
    # posts + locating pegs
    for (hx, hy) in HOLES:
        base = base.union(cyl(hx, hy, FLOOR - 0.1, ZB, 6.0))
        peg = cyl(hx, hy, ZB - 0.1, ZT + 0.8, HOLE_D - 0.3)
        peg = peg.faces(">Z").chamfer(0.4)
        base = base.union(peg)
    # snap hooks on both long walls
    for xc in HOOK_XS:
        base = base.union(hook(xc, -1)).union(hook(xc, +1))
    # USB-C notch (open to the parting plane)
    base = base.cut(box(OX0 - 1, USB_Y0 - 3.1, IX0 + 0.5, USB_Y1 + 3.1, ZT - 2.0, ZS + 5))
    # floor vents under the SoC
    base = base.cut(vent_slots(-1, FLOOR + 1))
    return base


# ---------------------------------------------------------------- lid
def build_lid():
    lid = rrect(OX0, OY0, OX1, OY1, ZS, ZLO, R_OUT)
    lid = lid.edges(">Z").fillet(1.0)
    cavity = rrect(IX0, IY0, IX1, IY1, ZS - 1, ZLI, R_OUT - WALL)
    lid = lid.cut(cavity)
    # rebate for the base lip
    lid = lid.cut(rrect(OX0 + WALL / 2 - CLR, OY0 + WALL / 2 - CLR,
                        OX1 - WALL / 2 + CLR, OY1 - WALL / 2 + CLR,
                        ZS - 1, ZS + LIP_H + CLR, R_OUT - WALL / 2))
    # hook pockets
    for xc in HOOK_XS:
        lid = lid.cut(hook_pocket(xc, -1)).cut(hook_pocket(xc, +1))
    # USB-C notch
    lid = lid.cut(box(OX0 - 1, USB_Y0 - 3.1, IX0 + 0.5, USB_Y1 + 3.1, ZS - 1, ZT + 5.5))
    # LED window: through opening + pocket on the inside for the clear plate
    wx0, wx1 = LED_X0 - WIN_MARGIN, LED_X1 + WIN_MARGIN
    wy0, wy1 = LED_Y0 - WIN_MARGIN, LED_Y1 + WIN_MARGIN
    lid = lid.cut(rrect(wx0, wy0, wx1, wy1, ZLI - 1, ZLO + 1, 1.0))
    lid = lid.cut(rrect(wx0 - 1.2, wy0 - 1.2, wx1 + 1.2, wy1 + 1.2,
                        ZLI - 1, ZLI + WIN_PLATE_T, 1.5))
    # hold-down ribs pressing on the header housings (top of headers = ZT+8.5)
    rib_z0 = ZT + HEADER_H + 0.3
    dig_yc = (DIG_Y0 + DIG_Y1) / 2
    for (x0, x1) in [(22.0, 32.0), (53.0, 63.0)]:
        lid = lid.union(box(x0, dig_yc - 0.75, x1, dig_yc + 0.75, rib_z0, ZLI + 0.5))
    for (x0, x1) in [(26.5, 28.5), (61.5, 64.5)]:
        lid = lid.union(box(x0, ANA_Y0, x1, wy0 - 1.2 - 0.1, rib_z0, ZLI + 0.5))
    # power button: flexible tab in the top plate with a nub reaching the switch
    tab_x0, tab_x1 = 2.5, 19.0
    tab_y0, tab_y1 = BTN_Y - 4.0, BTN_Y + 4.0
    slot = (box(tab_x0 - 0.6, tab_y0 - 0.6, tab_x1, tab_y1 + 0.6, ZLI - 1, ZLO + 1)
            .cut(box(tab_x0, tab_y0, tab_x1 + 1, tab_y1, ZLI - 2, ZLO + 2)))
    lid = lid.cut(slot)
    lid = lid.cut(box(tab_x0 - 1, tab_y0 - 1, tab_x1 + 2.0, tab_y1 + 1, ZLI - 1, ZLI + 1.0))
    lid = lid.union(cyl(BTN_X, BTN_Y, ZT + BTN_TOP + 1.0, ZLI + 1.1, 3.5))   # nub
    lid = lid.cut(cyl(BTN_X, BTN_Y, ZLO - 0.4, ZLO + 1, 4.0))               # tactile dimple
    # vents over the SoC
    lid = lid.cut(vent_slots(ZLI - 1, ZLO + 1))
    # pry notch on the x-max end
    yc = BOARD_L / 2
    lid = lid.cut(box(OX1 - 1.0, yc - 6, OX1 + 1, yc + 6, ZS - 1, ZS + 1.2))
    return lid


def build_window():
    wx0 = LED_X0 - WIN_MARGIN - 1.2 + 0.1
    wx1 = LED_X1 + WIN_MARGIN + 1.2 - 0.1
    wy0 = LED_Y0 - WIN_MARGIN - 1.2 + 0.1
    wy1 = LED_Y1 + WIN_MARGIN + 1.2 - 0.1
    return rrect(wx0, wy0, wx1, wy1, 0, WIN_PLATE_T, 1.4)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out, exist_ok=True)
    base, lid, win = build_base(), build_lid(), build_window()
    # lid flipped for printing (top face on the bed)
    lid_print = lid.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, ZLO))
    parts = {"unoq_base": base, "unoq_lid_print": lid_print,
             "unoq_lid_assembled": lid, "unoq_window": win}
    for name, p in parts.items():
        cq.exporters.export(p, os.path.join(out, name + ".stl"),
                            tolerance=0.02, angularTolerance=0.1)
        cq.exporters.export(p, os.path.join(out, name + ".step"))
        bb = p.val().BoundingBox()
        print(f"{name:22s} {bb.xlen:6.2f} x {bb.ylen:6.2f} x {bb.zlen:6.2f} mm  "
              f"vol {p.val().Volume()/1000:.1f} cm3  solids {len(p.solids().vals())}")
    print("levels: board bottom %.2f, board top %.2f, split %.2f, ceiling %.2f, top %.2f"
          % (ZB, ZT, ZS, ZLI, ZLO))
