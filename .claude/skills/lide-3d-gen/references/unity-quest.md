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
- Materials are plain Principled BSDF colours (no textures yet). Unity material remapping happens in the importer.

## Performance budget (orientative — verify against current Meta docs for the target headset)
Whole frame on Quest-class hardware is commonly quoted around ~1M triangles and ~100–200 draw calls.
Per model, set `tri_budget` in `model.toml` from the scene it lives in.
Draw calls ≈ mesh objects × materials per object. Many small parts are fine for an inspectable/educational
asset; for a background or many-instances asset, prefer merging static parts per material.
Moving parts cannot be statically batched in Unity: keep them few.

## Not covered yet (expand when needed)
LODs, texture baking/atlases, colliders, lightmap UVs, other engines/headsets.
