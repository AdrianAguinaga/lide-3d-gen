"""Run inside Blender: import an exported file into an empty scene and print a JSON summary."""
import sys, json, bpy

path = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
if path.endswith(".glb"):
    bpy.ops.import_scene.gltf(filepath=path)
else:
    bpy.ops.import_scene.fbx(filepath=path)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
dims = [max(v[i] for o in ms for v in [o.matrix_world @ c.co for c in o.data.vertices]) -
        min(v[i] for o in ms for v in [o.matrix_world @ c.co for c in o.data.vertices]) for i in range(3)]
print("REIMPORT", json.dumps({
    "parts": len(ms),
    "triangles": sum(len(p.vertices) - 2 for o in ms for p in o.data.polygons),
    "names": sorted(o.name for o in bpy.context.scene.objects),
    "world_dims": [round(d, 3) for d in dims],
}))
