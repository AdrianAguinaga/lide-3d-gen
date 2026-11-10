# LIDE 3D Gen

Skill + pipeline para crear modelos 3D para **Unity / Meta Quest** con **Blender 5.1** (MCP for Blender en vivo o headless).

## Uso rápido
```sh
# construir, validar y exportar un modelo → models/<nombre>/out/{.glb,.fbx,.blend,report.json}
"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --factory-startup --python-exit-code 1 \
  --python scripts/build.py -- models/heli-rotor

# pruebas de todos los modelos
python -m unittest -v
```

Con Claude Code o Codex basta pedir el modelo ("haz un modelo 3D de …"); el skill `lide-3d-gen` guía el flujo.

## Estructura
```
agent-capabilities/lide-3d-gen/   skill canónico (SKILL.md + references/)  → sync a .claude/ y .agents/
lib/lide3d/                       motor reutilizable: geometría, escena, validación, export
scripts/build.py                  build → validate → export de un modelo
scripts/sync_skills.py            copia el skill a .claude/skills y .agents/skills
models/<nombre>/                  model.toml · build.py · golden.json · source/ · out/ (no versionado)
templates/model/                  plantilla para un modelo nuevo
tests/                            smoke + caracterización + round-trip GLB/FBX
unity/ + scripts/unity_check.py   importación real en Unity (batchmode, requiere licencia)
evals/                            casos para evaluar el skill (REQUIREMENTS v3 §14)
.planning/                        BOOTSTRAP, STATE, contrato de tarea
```

## Modelos
| Modelo | Fuente | Partes | Triángulos | Materiales |
|---|---|---|---|---|
| `heli-rotor` (HeliRotor) | procedural | 62 | 12 356 | 7 |
| `lab-table` (LabTable) | procedural | 4 | 424 | 4 |
| `lab-stool` (LabStool) | Poly Haven `metal_stool_01` (CC0) | 1 | 8 334 | 1 (texturas 1k) |
