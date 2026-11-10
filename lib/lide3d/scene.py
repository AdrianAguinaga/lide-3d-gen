"""Model = one owned collection. Re-running rebuilds only that collection."""
import bpy, bmesh
from math import radians
from mathutils import Vector, Matrix
from .geometry import Rz


def material(name, color, metallic=0.0, rough=0.5):
    """Principled material (looked up by node type, not localized name)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*color, 1)
    return m


def box_uv(bm):
    """Box projection, 1 UV unit = 1 m: each face is projected along its dominant normal axis.
    Enough for tiling textures and Unity lightmap UV generation; not an artist unwrap."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        u, v = [(1, 2), (0, 2), (0, 1)][ax]
        for lp in f.loops:
            lp[uv].uv = (lp.vert.co[u], lp.vert.co[v])


def _shade(bm, limit):
    """Outward normals, smooth faces, sharp edges above limit (radians), box UVs."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > limit:
            e.smooth = False
    box_uv(bm)


def _boolean_cut(ob, cutters, c, cut_mat, limit):
    """Apply an exact DIFFERENCE of cutter solids to ob (cutters given in ob's pre-pivot coordinates)."""
    tmp = bpy.data.collections.new("_lide3d_cut")
    bpy.context.scene.collection.children.link(tmp)
    objs = []
    for i, cbm in enumerate(cutters):
        for v in cbm.verts:
            v.co -= c
        _shade(cbm, limit)
        cme = bpy.data.meshes.new(f"_cut{i}")
        cbm.to_mesh(cme)
        cbm.free()
        if cut_mat:
            cme.materials.append(cut_mat)
        co = bpy.data.objects.new(f"_cut{i}", cme)
        tmp.objects.link(co)
        co.parent = ob  # identity local transform = ob's frame
        objs.append(co)
    mod = ob.modifiers.new("cut", "BOOLEAN")
    mod.operation, mod.operand_type, mod.collection, mod.solver = "DIFFERENCE", "COLLECTION", tmp, "EXACT"
    mod.material_mode = "TRANSFER"
    deps = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(deps))
    old = ob.data
    ob.modifiers.remove(mod)
    ob.data = new
    bpy.data.meshes.remove(old)
    new.name = ob.name
    for co in objs:
        me = co.data
        bpy.data.objects.remove(co, do_unlink=True)
        bpy.data.meshes.remove(me)
    bpy.data.collections.remove(tmp)
    bm = bmesh.new()
    bm.from_mesh(new)
    for e in bm.edges:  # re-mark sharp edges on the new section faces (keep existing UVs)
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > limit:
            e.smooth = False
    bm.to_mesh(new)
    bm.free()


class Model:
    def __init__(self, name):
        self.name = name
        coll = bpy.data.collections.get(name)
        if coll:
            for o in list(coll.objects):
                me = o.data if o.type == "MESH" else None
                bpy.data.objects.remove(o, do_unlink=True)
                if me and me.users == 0:  # keep mesh names free of .001 suffixes on re-run
                    bpy.data.meshes.remove(me)
        else:
            coll = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(coll)
        self.coll = coll
        cube = bpy.data.objects.get("Cube")  # untouched factory cube only
        if cube and cube.type == "MESH" and len(cube.data.vertices) == 8:
            bpy.data.objects.remove(cube, do_unlink=True)

    def group(self, name, parent=None):
        e = bpy.data.objects.new(name, None)
        e.empty_display_size = 0.1
        self.coll.objects.link(e)
        e.parent = parent
        return e

    def part(self, name, bm, mat, parent, angle=0.0, pivot=None, offset=(0, 0, 0), sharp_deg=35,
             cut=None, cut_mat=None):
        """Mesh object from bm. Origin = bounds centre (or local pivot); rotated by angle about Z.

        cut: list of bmesh solids (same coordinates as bm) subtracted with an exact boolean — holes,
        bores, cutaway sections. Faces created by the cut get cut_mat (e.g. red section colour).
        """
        if pivot is None:
            cs = [v.co for v in bm.verts]
            c = Vector([(min(p[i] for p in cs) + max(p[i] for p in cs)) / 2 for i in range(3)])
        else:
            c = Vector(pivot)
        limit = radians(sharp_deg)
        for v in bm.verts:
            v.co -= c
        _shade(bm, limit)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        self.coll.objects.link(ob)
        ob.parent = parent
        ob.location = (Rz(angle) @ c) + Vector(offset)
        ob.rotation_euler = (0, 0, angle)
        if cut:
            _boolean_cut(ob, cut, c, cut_mat, limit)
        return ob

    def import_file(self, path, parent=None, size=None, ground=True):
        """Bring a .glb/.gltf/.fbx/.obj into this model as static meshes (generated or library assets).

        Flattens the hierarchy: each mesh gets its world transform (times the fit scale) baked into
        its data, so object scale is 1 as Unity expects. size = target longest side in metres.
        ground = centre on XY and rest on Z = 0. Returns the mesh objects.
        """
        path = str(path)
        before = set(bpy.data.objects)
        ext = path.lower().rsplit(".", 1)[-1]
        if ext in ("glb", "gltf"):
            bpy.ops.import_scene.gltf(filepath=path)
        elif ext == "fbx":
            bpy.ops.import_scene.fbx(filepath=path)
        elif ext == "obj":
            bpy.ops.wm.obj_import(filepath=path)
        else:
            raise ValueError(f"unsupported format: {path}")
        new = [o for o in bpy.data.objects if o not in before]
        meshes = [o for o in new if o.type == "MESH"]
        if not meshes:
            raise ValueError(f"no meshes in {path}")
        pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
        lo = Vector([min(p[i] for p in pts) for i in range(3)])
        hi = Vector([max(p[i] for p in pts) for i in range(3)])
        s = size / max(hi - lo) if size else 1.0
        shift = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)) if ground else Vector()
        bake = Matrix.Scale(s, 4) @ Matrix.Translation(-shift)
        for o in meshes:
            if o.data.users > 1:
                o.data = o.data.copy()
            o.data.transform(bake @ o.matrix_world)
        for o in new:
            if o.type != "MESH":
                bpy.data.objects.remove(o, do_unlink=True)
        for o in meshes:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            self.coll.objects.link(o)
            o.parent = parent
            o.matrix_world = Matrix.Identity(4)
        return meshes
