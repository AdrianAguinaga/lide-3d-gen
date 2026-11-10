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
    for o in coll.all_objects:
        if "." in o.name:
            problems.append(f"{o.name}: duplicate-suffix name (re-run leak?)")
    return problems
