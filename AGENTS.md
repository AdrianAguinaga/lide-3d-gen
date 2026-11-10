# lide-3d-gen (LIDE 3D Gen): agent index

3D models for Unity on Meta Quest, built with Blender 5.1 (MCP for Blender live, or headless). Each model is
reproducible from `models/<name>/build.py`; the engine is `lib/lide3d/` + `scripts/build.py`.

## Commands
- Start of a session (light bootstrap): read `.planning/STATE.md`; `python scripts/sync_skills.py --check`.
- Build one model: `blender --background --factory-startup --python-exit-code 1 --python scripts/build.py -- models/<name>`
  (Blender: `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`; tests read env `LIDE3D_BLENDER`)
- Quality gate: `python -m unittest -v` (all models: validate, golden, GLB/FBX round-trip; skill copies in sync)
- Model work: skill `lide-3d-gen` (canonical `agent-capabilities/lide-3d-gen/`).

## Boundaries
- Edit the skill only in `agent-capabilities/`, then `python scripts/sync_skills.py` (don't edit `.claude/skills` or `.agents/skills`).
- `golden.json` changes only for an intended geometry change the user accepted. Never relax `lide3d/validate.py` to pass.
- Ask before: `generate_3d` (credits), assets without clear license, deleting models, installs, global config.
- `models/*/out/` is build output: regenerate, never hand-edit.

## Map
`lib/lide3d/`: `geometry` (lathe, prism, box, loft) · `scene` (Model, part, group, material, import_file) · `validate` · `export`
`models/<name>/`: `model.toml` · `build.py` · `golden.json` · `source/` · `out/`  —  new model from `templates/model/`
`.planning/`: `BOOTSTRAP.md` · `STATE.md` · `templates/TASK-CONTRACT.md`  —  `evals/`: skill eval cases
Engineering policy: `E:\skills\REQUIREMENTS_v3_investigacion_comparativa_agentes.md` (cite sections; don't load whole).
