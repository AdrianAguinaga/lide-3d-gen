"""Stats, fingerprint and Unity/Quest checks for a built model collection."""
import bpy


def meshes(coll):
    return [o for o in coll.all_objects if o.type == "MESH"]


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def stats(coll):
    ms = meshes(coll)
    return {
        "parts": len(ms),
        "triangles": sum(tris(o) for o in ms),
        "materials": sorted({s.material.name for o in ms for s in o.material_slots if s.material}),
    }


def world_size(coll, nd=4):
    """World bounding-box size (x, y, z) in metres of all mesh vertices."""
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ v.co for o in meshes(coll) for v in o.data.vertices]
    return [round(max(p[i] for p in pts) - min(p[i] for p in pts), nd) for i in range(3)]


def fingerprint(coll, nd=5):
    """Per-object geometry/transform summary; used as characterization golden."""
    r = lambda v: [round(x, nd) + 0.0 for x in v]
    bpy.context.view_layer.update()  # o.dimensions is stale until the depsgraph re-evaluates
    out = {}
    for o in sorted(coll.all_objects, key=lambda o: o.name):
        d = {"type": o.type, "parent": o.parent.name if o.parent else None,
             "location": r(o.location), "rotation": r(o.rotation_euler), "scale": r(o.scale)}
        if o.type == "MESH":
            d.update(verts=len(o.data.vertices), tris=tris(o), dims=r(o.dimensions),
                     materials=[s.material.name if s.material else None for s in o.material_slots])
        out[o.name] = d
    return out


def check(coll, spec):
    """Return list of problems (empty = passes). spec = [unity] table of model.toml."""
    problems = []
    st = stats(coll)
    if st["parts"] == 0:
        problems.append("no mesh parts")
    if st["triangles"] > spec["tri_budget"]:
        problems.append(f"triangles {st['triangles']} > tri_budget {spec['tri_budget']}")
    if len(st["materials"]) > spec["max_materials"]:
        problems.append(f"materials {len(st['materials'])} > max_materials {spec['max_materials']}")
    for o in meshes(coll):
        if not o.material_slots or any(s.material is None for s in o.material_slots):
            problems.append(f"{o.name}: missing material")
        if any(abs(s - 1) > 1e-6 for s in o.scale):
            problems.append(f"{o.name}: unapplied scale {tuple(o.scale)}")
        if not o.data.uv_layers:
            problems.append(f"{o.name}: no UV map (Unity textures/lightmaps need one)")
    for o in coll.all_objects:
        if "." in o.name:
            problems.append(f"{o.name}: duplicate-suffix name (re-run leak?)")
    return problems


def tri_hotspots(coll, n=5):
    """Heaviest parts first: where to cut segments when over budget."""
    return sorted(((o.name, tris(o)) for o in meshes(coll)), key=lambda t: -t[1])[:n]


def box_collider(coll):
    """Suggested Unity BoxCollider on the model root, in Unity axes (Y up), metres.
    size = (X, Z, Y) of the Blender bounds; center y = mid height. x/z centre given only as a
    warning when the model is off-centre (axis sign mapping unverified in Unity)."""
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ v.co for o in meshes(coll) for v in o.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    mid = [(a + b) / 2 for a, b in zip(lo, hi)]
    r = lambda x: round(x, 4) + 0.0
    out = {"size": [r(hi[0] - lo[0]), r(hi[2] - lo[2]), r(hi[1] - lo[1])], "center_y": r(mid[2])}
    if abs(mid[0]) > 0.005 or abs(mid[1]) > 0.005:
        out["warning"] = f"bounds off-centre in plan (Blender x={r(mid[0])}, y={r(mid[1])}); place the collider by hand"
    return out
