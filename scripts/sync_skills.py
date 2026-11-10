"""Copy the canonical skill (agent-capabilities/) to .claude/skills and .agents/skills. Idempotent.

python scripts/sync_skills.py          # sync
python scripts/sync_skills.py --check  # exit 1 if copies are out of date
"""
import sys, shutil, filecmp
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "agent-capabilities"
DESTS = [ROOT / ".claude/skills", ROOT / ".agents/skills"]


def stale():
    out = []
    for skill in (p for p in SRC.iterdir() if p.is_dir()):
        for dest in DESTS:
            d = dest / skill.name
            src_files = {p.relative_to(skill) for p in skill.rglob("*") if p.is_file()}
            dst_files = {p.relative_to(d) for p in d.rglob("*") if p.is_file()} if d.is_dir() else set()
            if src_files != dst_files or any(not filecmp.cmp(skill / f, d / f, shallow=False) for f in src_files):
                out.append((skill, d))
    return out


if __name__ == "__main__":
    todo = stale()
    if "--check" in sys.argv:
        for s, d in todo:
            print("out of date:", d.relative_to(ROOT))
        sys.exit(1 if todo else 0)
    for s, d in todo:
        shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(s, d)
        print("synced", d.relative_to(ROOT))
