# Model sources

| Source | When | Cost / risk | Reproducible via |
|---|---|---|---|
| procedural | exact dimensions, mechanical, parametric, many variants | none | `build.py` code only |
| imported (`search_assets` + `import_asset`) | common props, environments, materials | license per asset | `source/<file>` + `m.import_file` |
| generated (`generate_3d`) | organic/unique single objects | 1–3 min, **may cost a credit: ask** | `source/<file>` + `m.import_file` |

Mixing is fine: e.g. a procedural rig with an imported decorative shell, all under one `<Name>_Root`.

## Imported / generated workflow
1. Live: `search_assets` (or `generate_3d` after the user agrees). Check license and provider terms.
2. Export just that object from the live scene to `models/<name>/source/<name>.glb`
   (select it, `bpy.ops.export_scene.gltf(filepath=..., export_format="GLB", use_selection=True)`).
3. `build.py`:
   ```python
   from pathlib import Path
   def build(m):
       root = m.group("Chair_Root")
       m.import_file(Path(__file__).parent / "source/chair.glb", root, size=0.9)  # longest side, metres
   ```
   `import_file` bakes transforms into the mesh (scale 1), drops empties, centres on XY and grounds at Z = 0.
4. Record `provenance` in `model.toml`. Generated/imported assets arrive at arbitrary scale: always pass `size`.
5. Materials come from the asset; check `max_materials` and textures in the report.
6. Rename the imported mesh/material to the naming convention in `build.py` (see `models/lab-stool/`).

Tested 2026-11-09: Poly Haven `metal_stool_01` (CC0) → `models/lab-stool`. Poly Haven .blend files newer than
the local Blender are imported via glTF (materials are the glTF conversion).
