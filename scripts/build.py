"""Build, validate and export one model.

Headless:  blender --background --factory-startup --python-exit-code 1 --python scripts/build.py -- models/<name> [--no-export] [--fingerprint out.json]
Live MCP:  import runpy, sys; sys.argv = ["", "--", "<abs>/models/<name>"]; runpy.run_path("<abs>/scripts/build.py")
Fails (exit 1 headless / RuntimeError live) when validation fails; nothing is exported then.
"""
import sys, json, runpy, tomllib, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

import bpy
from lide3d import export, validate
from lide3d.scene import Model

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv or not (Path(argv[0]) / "model.toml").is_file():
    raise SystemExit(f"usage: ... -- models/<name>   (got {argv})")
model_dir = Path(argv[0]).resolve()
spec = tomllib.loads((model_dir / "model.toml").read_text(encoding="utf-8"))

m = Model(spec["name"])
runpy.run_path(str(model_dir / "build.py"))["build"](m)

st = validate.stats(m.coll)
problems = validate.check(m.coll, spec["unity"])
print(f"[lide3d] {spec['name']}: parts {st['parts']} | triangles {st['triangles']} | materials {len(st['materials'])}")
for p in problems:
    print("[lide3d] FAIL", p)

if "--fingerprint" in argv:
    fp = Path(argv[argv.index("--fingerprint") + 1])
    fp.write_text(json.dumps({"stats": st, "objects": validate.fingerprint(m.coll)}, indent=1, sort_keys=True))

if not problems and "--no-export" not in argv:
    out = model_dir / "out"
    out.mkdir(exist_ok=True)
    stem = out / spec["name"]
    export.glb(m.coll, stem.with_suffix(".glb"))
    export.fbx(m.coll, stem.with_suffix(".fbx"))
    if bpy.app.background:  # live session: don't copy the user's whole scene
        export.blend(stem.with_suffix(".blend"))
    (out / "report.json").write_text(json.dumps({
        "model": spec["name"], "stats": st, "blender": bpy.app.version_string,
        "built_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "files": sorted(p.name for p in out.iterdir() if p.suffix in (".glb", ".fbx", ".blend")),
    }, indent=1))
    print("[lide3d] exported ->", out)

if problems:
    if bpy.app.background:
        sys.exit(1)
    raise RuntimeError(f"{spec['name']}: {len(problems)} validation problem(s): {problems}")
