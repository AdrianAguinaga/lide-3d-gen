# Unity / Meta Quest conventions

## Space and naming
- Metres. Blender Z up; exporters convert to Unity Y up (GLB per glTF spec; FBX `axis_up=Y, axis_forward=-Z`).
- Model root empty `<Name>_Root`; moving assemblies as empties (`Rotating_Assembly`, `Door_Left`…), parts as
  children. Unity scripts rotate/translate the empties, never individual parts.
- Part names `PascalCase_Words_NN` (`Blade_01`), unique, no dots. Materials `M_<Name>`.
- Object scale 1 (validated). Pivots where the part moves.

## Formats
- **FBX**: imported natively by Unity. Root may come in with a -90° X rotation compensation; that is expected.
- **GLB**: needs a glTF importer package in Unity (e.g. glTFast). Materials map to PBR metallic-roughness.
- Procedural models: plain Principled colours. Imported models keep their textures: the FBX embeds base colour +
  normal maps (`embed_textures`); the metal/roughness (ARM) map survives only in the GLB.
- `python scripts/unity_check.py` imports every `out/*.fbx` into a throwaway Unity project (batchmode) and checks
  triangles, parts and size/axes against `report.json`. Needs an activated Unity license (Hub signed in).

## Performance budget (orientative — verify against current Meta docs for the target headset)
Whole frame on Quest-class hardware is commonly quoted around ~1M triangles and ~100–200 draw calls.
Per model, set `tri_budget` in `model.toml` from the scene it lives in.
Draw calls ≈ mesh objects × materials per object. Many small parts are fine for an inspectable/educational
asset; for a background or many-instances asset, prefer merging static parts per material.
Moving parts cannot be statically batched in Unity: keep them few.

## Unity scripts (`unity/Runtime/`, copy into the Unity project)
- `LideExplode.cs` — any model: `amount` 0..1 moves top-level parts away from the centre (children follow).
- `LideEngineKinematics.cs` — `inline-four-engine`: crank, pistons, conrods, cams (½ speed) and valves from the
  cam profile. Discovers axes from the imported hierarchy (flywheel → pulley, world up at Start). Pauses while
  `LideExplode.amount > 0`. `reverse` flips the spin if the lobes turn away from the tappets.
- Compile check without a Unity license: Unity's Roslyn (`Editor/Data/DotNetSdkRoslyn/csc.dll`) against
  `UnityEngine.CoreModule.dll` + `netstandard.dll`. Behaviour in Unity is still unverified until `unity_check` runs.
- Grabbing in VR (XR Interaction Toolkit) is not scripted here: add XRGrabInteractable + collider per part in Unity.

## Colliders
`report.json` → `unity_box_collider`: size in Unity axes (X, Y up, Z) and centre height. Static props: one
BoxCollider on the root. Moving assemblies (rotor): per moving empty, or none if not interactive. Avoid
MeshCollider on dense meshes (CPU cost on Quest); use convex only on simple parts.

## UVs
Procedural meshes get box-projected UVs (metres), fine for tiling textures; for lightmaps enable
"Generate Lightmap UVs" in the Unity model importer. Imported assets keep their own UVs.

## Not covered yet (expand when needed)
LODs, texture baking/atlases, artist UV unwraps, other engines/headsets.
