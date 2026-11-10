# MyModel: geometry only. Run via scripts/build.py (see agent-capabilities/lide-3d-gen/SKILL.md).
import bmesh
from lide3d.geometry import box
from lide3d.scene import material


def build(m):
    mat = material("M_Base", (0.8, 0.8, 0.8), 0.0, 0.5)
    root = m.group("MyModel_Root")
    bm = bmesh.new()
    box(bm, -0.5, 0.5, -0.5, 0.5, 0.0, 1.0)  # 1 m cube resting on the ground
    m.part("Body", bm, mat, root)
