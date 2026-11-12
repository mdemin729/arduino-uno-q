"""Blender headless render of the UNO Q case.

Usage (run from case/, after unoq_case.py and check_fit.py):
    blender -b --python scripts/render_previews.py
    blender -b --python scripts/render_previews.py -- <stl_dir> <preview_dir>

Reads build/stl/*.stl, writes build/preview/*.png. Runs inside Blender's own
Python, so it cannot import unoq_case: LID_CEILING_Z below must match ZLI
printed by unoq_case.py ("ceiling") if the case height ever changes.
"""
import bpy, sys, math, os
from mathutils import Vector

LID_CEILING_Z = 19.5

_case_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out_dir = argv[0] if len(argv) > 0 else os.path.join(_case_dir, "build", "stl")
prev_dir = argv[1] if len(argv) > 1 else os.path.join(_case_dir, "build", "preview")
os.makedirs(prev_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = 1600, 1100
scene.render.film_transparent = False
world = bpy.data.worlds.new("W"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.92, 0.94, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def mat(name, rgba, rough=0.5, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
    return m


def load(name, m, dz=0.0):
    bpy.ops.wm.stl_import(filepath=os.path.join(out_dir, name + ".stl"))
    o = bpy.context.selected_objects[0]
    o.name = name
    o.data.materials.append(m)
    o.location.z += dz
    return o


M_CASE = mat("case", (0.15, 0.17, 0.22, 1), 0.45)
M_LID = mat("lid", (0.85, 0.86, 0.88, 1), 0.4)
M_BOARD = mat("board", (0.05, 0.32, 0.42, 1), 0.6)
M_WIN = mat("win", (0.9, 0.95, 1.0, 1), 0.1, alpha=0.35)


def light():
    for (loc, e) in [((60, -80, 120), 3000), ((-80, 40, 90), 1500), ((120, 100, 60), 800)]:
        l = bpy.data.lights.new("l", "POINT"); l.energy = e * 1000; l.shadow_soft_size = 20
        lo = bpy.data.objects.new("l", l); lo.location = loc; scene.collection.objects.link(lo)


def camera(target, dist, az_deg, el_deg, lens=60):
    cam = bpy.data.cameras.new("c"); cam.lens = lens
    co = bpy.data.objects.new("cam", cam); scene.collection.objects.link(co)
    az, el = math.radians(az_deg), math.radians(el_deg)
    pos = Vector(target) + Vector((dist * math.cos(el) * math.cos(az), dist * math.cos(el) * math.sin(az), dist * math.sin(el)))
    co.location = pos
    d = Vector(target) - pos
    co.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    scene.camera = co
    return co


def clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def shot(fname):
    scene.render.filepath = os.path.join(prev_dir, fname)
    bpy.ops.render.render(write_still=True)


# 1. exploded assembly
clear(); light()
load("unoq_base", M_CASE); load("unoq_board", M_BOARD)
load("unoq_lid_assembled", M_LID, dz=28)
w = load("unoq_window", M_WIN, dz=0); w.location.z = LID_CEILING_Z + 28 + 10
camera((34, 27, 22), 230, -55, 32, 60); shot("01_exploded.png")

# 2. closed case
clear(); light()
load("unoq_base", M_CASE); load("unoq_board", M_BOARD); load("unoq_lid_assembled", M_LID)
w = load("unoq_window", M_WIN); w.location.z = LID_CEILING_Z
camera((34, 27, 10), 210, -55, 30, 60); shot("02_closed.png")

# 3. closed, USB-C end
clear(); light()
load("unoq_base", M_CASE); load("unoq_board", M_BOARD); load("unoq_lid_assembled", M_LID)
w = load("unoq_window", M_WIN); w.location.z = LID_CEILING_Z
camera((34, 27, 10), 210, 200, 22, 60); shot("03_usb_end.png")

# 4. base with board, top view-ish
clear(); light()
load("unoq_base", M_CASE); load("unoq_board", M_BOARD)
camera((34, 27, 8), 200, -70, 55, 60); shot("04_base_board.png")

# 5. base empty
clear(); light()
load("unoq_base", M_CASE)
camera((34, 27, 8), 200, -70, 50, 60); shot("05_base_empty.png")

# 6. lid underside (print orientation)
clear(); light()
load("unoq_lid_print", M_LID)
camera((34, -27, 6), 200, -70, 50, 60); shot("06_lid_underside.png")
print("RENDER DONE")
