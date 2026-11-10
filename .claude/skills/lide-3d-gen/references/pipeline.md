# Pipeline

```
models/<name>/model.toml ─┐
models/<name>/build.py ───┼─> scripts/build.py ─> Model(name) reset ─> build(m) ─> validate.check ─┬─ FAIL → exit 1, no export
lib/lide3d/* ─────────────┘                                                                    └─ OK → out/: glb, fbx, blend*, report.json
```
`*` `.blend` only headless (a live session would copy the user's whole scene).

## model.toml
```toml
name = "HeliRotor"        # collection + export stem (PascalCase, no dots)
description = "..."
source = "procedural"     # procedural | imported | generated
units = "m"
# imported/generated only:
# provenance = { provider = "Poly Haven", url = "...", license = "CC0", retrieved = "2026-11-09" }

[unity]
tri_budget = 20000        # whole model
max_materials = 8

[rig]                     # optional: empties Unity scripts drive
rotating = "Rotating_Assembly"
```

## lib/lide3d API
| Module | Use |
|---|---|
| `geometry` | `lathe(bm, [(r,z)...], seg, M)`, `prism(bm, [(x,y)...], z0, z1, M)`, `box(...)`, `loft(bm, loops)`, `Rz(a)`, `T(x,y,z)`, `TO_X` |
| `scene` | `material(name, rgb, metallic, rough)`, `Model.group(name, parent)`, `Model.part(name, bm, mat, parent, angle, pivot, offset)`, `Model.import_file(path, parent, size, ground)` |
| `validate` | `stats`, `fingerprint`, `check(coll, spec["unity"])` |
| `export` | `glb`, `fbx` (Unity axes, scale 1), `blend` |

`part()` sets the origin at the bounds centre unless `pivot` is given. Use `pivot` for anything that rotates
(blade root, hinge, wheel axle) and when the part is not symmetric (bounds centre off-axis).

## Checks (validate.check)
tri_budget · max_materials · every mesh has a material and a UV map · object scale = 1 · no `.001` names (re-run leak).
`report.json` adds `size`, `tri_hotspots` (heaviest parts) and `unity_box_collider` (Unity axes; warns when off-centre).
`Model.part` writes box-projected UVs (1 UV unit = 1 m) to every procedural mesh.
Tests (`tests/test_models.py`) add: golden fingerprint, GLB and FBX re-import with the same parts/tris and
the same world bounds (catches a tipped-over FBX).

## Gotchas found in Blender 5.1
- `blender --python` exits 0 on a Python exception unless `--python-exit-code 1` is passed.
- After removing objects, `view_layer.objects` can yield `None`; iterate `scene.objects`.
- `o.dimensions` is stale until `view_layer.update()`.
- Live Blender caches `lide3d` in `sys.modules`; `scripts/build.py` purges it so library edits apply on the next run.
- FBX `bake_space_transform=True` tipped the model on round-trip; not used.
- On this lab PC `look` with `shading="material"` or `"rendered"` (EEVEE) returns blank tiles, also with add-on 1.8.
  Use solid shading with material colours: set the 3D view `shading.type="SOLID"`, `shading.color_type="MATERIAL"`, then `look`.
