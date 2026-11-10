# LabStool: imported asset (see model.toml provenance). Real height 0.883 m.
from pathlib import Path


def build(m):
    root = m.group("LabStool_Root")
    (stool,) = m.import_file(Path(__file__).parent / "source/metal_stool_01.glb", root, size=0.883)
    stool.name = stool.data.name = "Stool"
    stool.material_slots[0].material.name = "M_MetalStool"
