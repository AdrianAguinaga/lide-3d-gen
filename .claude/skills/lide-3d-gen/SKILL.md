---
name: lide-3d-gen
description: Create or modify 3D models for Unity on Meta Quest with Blender (MCP for Blender live, or headless). Procedural geometry by code, library assets (Poly Haven, Sketchfab, Poly Pizza) or AI-generated models, each reproducible from models/<name>/build.py and exported to GLB + FBX with validation. Use when the user asks to model, generate, build, fix or re-export a 3D model/asset/part ("haz un modelo 3D de…", "genera el rotor", "exporta para Quest"). Do not use for renders/animation films, Unity scene or C# work, or targets other than Unity/Quest.
---

# LIDE 3D Gen

Every model lives in `models/<kebab-name>/`: `model.toml` (spec), `build.py` (`def build(m)`), `golden.json`
(accepted fingerprint, optional), `source/` (imported/generated files), `out/` (exports, not versioned).
The engine is `lib/lide3d/` + `scripts/build.py`. Put reusable geometry in `lib/`, model-specific in `build.py`;
never leave a model only in the live Blender scene.

## 1. Start
- Live: `get_addon_status`, then `get_scene_info`. If Blender is not reachable, work headless (section 4) and say so.
- Existing model? Read its `model.toml` + `build.py` first; build it once before changing anything.

## 2. Clarify (only what is missing)
Object and purpose in the experience · real-world size (metres) · which parts move and about which axis
(→ group empties + pivots) · detail level → `tri_budget`. Do not ask what has a sensible default
(units m, Z up in Blender, 8 materials max).

## 3. Choose the source (references/sources.md)
1. **procedural** — default for mechanical/engineering parts and anything with exact dimensions.
2. **imported** — `search_assets` → `import_asset`. Record provider, URL and license in `model.toml`.
3. **generated** — `generate_3d`. One object per call, 1–3 min, **may cost the user a credit: ask first**.
For 2–3: save the file to `models/<name>/source/` and load it in `build.py` with `m.import_file(...)`.

## 4. Build loop
- New model: copy `templates/model/` to `models/<name>/`, fill `model.toml`.
- Educational / exploded models: every part the user may grab is its own object; moving chains as a hierarchy
  (piston > pin, conrod) so a parent drags its children; sections with `part(cut=..., cut_mat=red)`; moving parts whole.
  Check separability live by offsetting parts, `look`, then rebuild (exploded preview is never saved).
- Geometry density: segments by visible size, not by habit — revolved parts < 3 cm: 8 · < 10 cm: 12–16 ·
  large/close-up: 32–48. Static props: merge parts per material (one mesh per material). UVs are automatic.
- Live (iterate): `execute_blender_code` with
  `import runpy, sys; sys.argv = ["", "--", r"<abs>/models/<name>", "--no-export"]; runpy.run_path(r"<abs>/scripts/build.py")`
  then `look` (`mode="angles"`, small `max_size`; if tiles are blank see pipeline.md gotchas). Re-run freely: only the model's collection is rebuilt.
- Canonical (exports): `blender --background --factory-startup --python-exit-code 1 --python scripts/build.py -- models/<name>`
  → `out/<Name>.glb`, `.fbx`, `.blend`, `report.json`. Validation failure = nothing exported.
- Verify: `python -m unittest -v` (characterization vs `golden.json`, GLB/FBX round-trip counts and orientation).

## 5. Deliver (every time)
Tell the user: files in `out/`, parts / triangles / materials, dimensions, how it was verified (`look`, tests),
what is unverified (Unity, headset), assumptions you made (e.g. a height nobody gave), and the collider suggestion
from `report.json` → `unity_box_collider` (static props: one BoxCollider on the root; moving assemblies: colliders
per moving empty or none; never MeshCollider on high-poly parts). If over budget, start from `tri_hotspots`.

## 6. Accepting a model
Only when the user accepts it: write `golden.json` with `--fingerprint models/<name>/golden.json`.
Later geometry changes make the test fail on purpose; regenerate golden only for an intended change, and say so.

## 7. Limits — ask first
- `generate_3d` (credits), assets without a clear license, deleting/renaming models, raising `tri_budget`
  or `max_materials`, weakening `lide3d/validate.py` checks, editing `golden.json` to make a test pass.
- Report validation and test failures verbatim. A model not checked with `look` is "unverified visually".
- Conventions and Quest budgets: references/unity-quest.md. Pipeline details: references/pipeline.md.
