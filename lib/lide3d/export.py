"""Unity / Meta Quest exports of one collection. Paths are created by the caller."""
import bpy


def _select(coll):
    for o in bpy.context.scene.objects:  # view_layer can hold stale refs to objects removed this run
        o.select_set(False)
    for o in coll.all_objects:
        o.select_set(True)


def glb(coll, path):
    _select(coll)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)


def fbx(coll, path):
    """Unity convention: Y up, -Z forward, scale 1, no leaf bones.
    No bake_space_transform (experimental): it tipped the model over on round-trip."""
    _select(coll)
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={"EMPTY", "MESH"},
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                             add_leaf_bones=False)


def blend(path):
    """Copy of the current file. Only meaningful headless (factory scene + this model)."""
    bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
