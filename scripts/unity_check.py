"""Import every models/*/out/*.fbx into a throwaway Unity project (batchmode) and compare with report.json.

python scripts/unity_check.py [--project <dir>]     (default project dir: %TEMP%/lide3d-unity-check)
Env LIDE3D_UNITY overrides the editor path. Build the models first (scripts/build.py).
Checks: triangles and part count equal Blender's, height axis is Unity Y, size in metres.
"""
import os, sys, json, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNITY = os.environ.get("LIDE3D_UNITY", r"C:\Program Files\Unity\Hub\Editor\6000.3.8f1\Editor\Unity.exe")
proj = Path(sys.argv[sys.argv.index("--project") + 1]) if "--project" in sys.argv else Path(tempfile.gettempdir()) / "lide3d-unity-check"


def unity(*args):
    log = proj.parent / (proj.name + ".log")
    r = subprocess.run([UNITY, "-batchmode", "-nographics", "-quit", "-logFile", str(log), *args], timeout=1800)
    if r.returncode:
        sys.exit(f"Unity exit {r.returncode}; see {log}")


if not (proj / "Assets").is_dir():
    unity("-createProject", str(proj))
lide = proj / "Assets/Lide"
shutil.rmtree(lide, ignore_errors=True)
(lide / "Editor").mkdir(parents=True)
shutil.copy(ROOT / "unity/Editor/LideImportCheck.cs", lide / "Editor")
shutil.copytree(ROOT / "unity/Runtime", lide / "Runtime")  # compiled by Unity too
expected = {}
for rep in ROOT.glob("models/*/out/report.json"):
    r = json.loads(rep.read_text())
    shutil.copy(rep.parent / f"{r['model']}.fbx", lide)
    expected[f"{r['model']}.fbx"] = {**r["stats"], "size": r["size"]}

out = proj / "lide_check.json"
out.unlink(missing_ok=True)
unity("-projectPath", str(proj), "-executeMethod", "LideImportCheck.Run", "-lideOut", str(out))
rep = json.loads(out.read_text(encoding="utf-8-sig"))
print("Unity", rep["unity"])
bad = 0
for it in rep["items"]:
    exp = expected[it["file"]]
    ok_t = it["triangles"] == exp["triangles"]
    ok_p = it["renderers"] == exp["parts"]
    bx, by, bz = exp["size"]  # Blender world size, Z up  ->  Unity (x, y, z) = (x, z, y)
    ok_s = all(abs(u - b) < 0.005 for u, b in zip(it["size"], (bx, bz, by)))
    print(f"{it['file']}: tris {it['triangles']}/{exp['triangles']} {'ok' if ok_t else 'FAIL'} | parts {it['renderers']}/{exp['parts']} "
          f"{'ok' if ok_p else 'FAIL'} | size {[round(s, 3) for s in it['size']]} vs {[bx, bz, by]} {'ok' if ok_s else 'FAIL'} "
          f"| root euler {[round(e, 1) for e in it['rootEuler']]} | materials {it['materials']} textures {it['textures']}")
    for u in it["upOfEmpties"]:
        print("   ", u)
    bad += not (ok_t and ok_p and ok_s)
sys.exit(1 if bad else 0)
