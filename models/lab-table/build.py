# LabTable: static furniture, so parts are merged per material (4 meshes = 4 draw calls on Quest).
import bmesh
from lide3d.geometry import box, lathe, T
from lide3d.scene import material

L, W, H = 1.2, 0.6, 0.90      # top length, depth, working height (standing bench)
TOP_T = 0.025                 # top thickness
TUBE = 0.04                   # square leg tube
INSET = 0.05                  # leg outer face to top edge
FOOT_H = 0.03                 # levelling foot height under the leg
SHELF_Z = 0.17                # shelf upper rail top

LX = L / 2 - INSET - TUBE / 2  # leg centre x
LY = W / 2 - INSET - TUBE / 2  # leg centre y
LEGS = [(sx * LX, sy * LY) for sx in (-1, 1) for sy in (-1, 1)]


def rails(bm, z0, z1):
    """Perimeter rails (40 x 20 mm) between the legs."""
    i, o = TUBE / 2, TUBE / 4  # rail runs from leg face; rail is half a tube deep, centred on the leg line
    for sy in (-1, 1):
        box(bm, -LX + i, LX - i, sy * LY - o, sy * LY + o, z0, z1)
    for sx in (-1, 1):
        box(bm, sx * LX - o, sx * LX + o, -LY + i, LY - i, z0, z1)


def build(m):
    EPOXY = material("M_EpoxyTop", (0.04, 0.04, 0.045), 0.0, 0.3)
    FRAME = material("M_PowderCoat", (0.80, 0.81, 0.82), 0.0, 0.55)
    SHELF = material("M_Melamine", (0.72, 0.73, 0.70), 0.0, 0.6)
    STEEL = material("M_Steel", (0.62, 0.63, 0.65), 1.0, 0.35)

    root = m.group("LabTable_Root")

    bm = bmesh.new()
    box(bm, -L / 2, L / 2, -W / 2, W / 2, H - TOP_T, H)
    m.part("Top", bm, EPOXY, root)

    bm = bmesh.new()
    for x, y in LEGS:
        box(bm, x - TUBE / 2, x + TUBE / 2, y - TUBE / 2, y + TUBE / 2, FOOT_H, H - TOP_T)
    rails(bm, H - TOP_T - TUBE, H - TOP_T)          # apron under the top
    rails(bm, SHELF_Z - TUBE, SHELF_Z)              # shelf supports
    m.part("Frame", bm, FRAME, root)

    bm = bmesh.new()
    box(bm, -LX + TUBE / 2, LX - TUBE / 2, -LY - TUBE / 4, LY + TUBE / 4, SHELF_Z, SHELF_Z + 0.018)
    m.part("Shelf", bm, SHELF, root)

    bm = bmesh.new()
    for x, y in LEGS:
        lathe(bm, [(0, 0), (0.022, 0), (0.022, 0.012), (0.006, 0.012), (0.006, FOOT_H), (0, FOOT_H)], 8, T(x, y))  # 2 cm parts: 8 segments read as round in VR
    m.part("Feet", bm, STEEL, root)
