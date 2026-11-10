"""Smoke + characterization for every model.  python -m unittest -v   (from repo root)

Needs Blender 5.1+. Override path with env LIDE3D_BLENDER.
"""
import os, sys, json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLENDER = os.environ.get("LIDE3D_BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
MODELS = sorted(p.parent for p in (ROOT / "models").glob("*/model.toml"))


def blender(script, *args):
    r = subprocess.run([BLENDER, "--background", "--factory-startup", "--python-exit-code", "1",
                        "--python", str(script), "--", *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    return r.returncode, r.stdout + r.stderr


class TestModels(unittest.TestCase):
    def test_build_validate_export(self):
        for md in MODELS:
            with self.subTest(model=md.name), tempfile.TemporaryDirectory() as tmp:
                fp = Path(tmp) / "fp.json"
                code, log = blender(ROOT / "scripts/build.py", md, "--fingerprint", fp)
                self.assertEqual(code, 0, log[-3000:])
                golden = md / "golden.json"
                if golden.is_file():  # characterization: geometry must not drift unintentionally
                    self.assertEqual(json.loads(fp.read_text()), json.loads(golden.read_text()),
                                     "fingerprint differs from golden.json (regenerate only if the change is intended)")
                built = json.loads(fp.read_text())["stats"]
                dims = {}
                for ext in (".glb", ".fbx"):
                    f = md / "out" / (json.loads((md / "out/report.json").read_text())["model"] + ext)
                    code, log = blender(ROOT / "tests/reimport.py", f)
                    self.assertEqual(code, 0, log[-3000:])
                    got = json.loads(log.split("REIMPORT ", 1)[1].splitlines()[0])
                    self.assertEqual(got["parts"], built["parts"], f"{ext} part count")
                    self.assertEqual(got["triangles"], built["triangles"], f"{ext} triangle count")
                    dims[ext] = got["world_dims"]
                # same size AND orientation after round-trip (catches tipped-over FBX)
                self.assertEqual(dims[".glb"], dims[".fbx"], "GLB/FBX round-trip bounds differ")


class TestSkillMirror(unittest.TestCase):
    def test_skill_copies_in_sync(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts/sync_skills.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + "run: python scripts/sync_skills.py")


if __name__ == "__main__":
    unittest.main()
