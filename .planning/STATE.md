# STATE

Actualizado: 2026-11-09 · Metodología: perfil A (GSD + Ponytail + Grill; Graphify opcional) — REQUIREMENTS v3 §4
Repo público: https://github.com/AdrianAguinaga/lide-3d-gen (último push 2dc24b3). Sin LICENSE.

## Hecho
- HeliRotor migrado con caracterización (golden) y round-trip GLB/FBX. Origen `../rotor-helicoptero-quest/` en la Papelera.
- Skill `lide-3d-gen` (canónico + copias Claude/Codex), plantilla de modelo, `import_file`.
- Add-on MCP for Blender 1.8 (protocol 15). Poly Haven activado.
- LabTable aceptada (golden). LabStool importada de Poly Haven `metal_stool_01` (CC0).
- Eval 1 con y sin skill (`evals/results.md`). Mejoras aplicadas: UVs automáticos + validación, `unity_box_collider`
  y `tri_hotspots` en report.json, guía de segmentos (LabTable 680 → 424 tris), recarga de `lide3d` en Blender vivo.
- `scripts/unity_check.py` + `unity/Editor/LideImportCheck.cs` listos.
- InlineFour (motor 4 en línea, corte educativo) aceptado: 76 partes / 33 800 tris; lib con `part(cut=...)`, `coil`, `hull2d`.
- `unity/Runtime/LideExplode.cs` y `LideEngineKinematics.cs`: compilan (Roslyn de Unity), comportamiento sin verificar.

## Pendiente / decisiones del usuario
- Unity sin licencia en batchmode: iniciar sesión en Unity Hub y activar Personal → `python scripts/unity_check.py`.
- Aceptar LabStool (→ golden.json).
- Commit/push de los cambios desde 2dc24b3.
- `generate_3d`: generadores apagados; requieren cuenta/clave y pueden costar créditos.
- Evals restantes de `evals/cases.md` (2–11).
- Borrar la carpeta vacía `../rotor-helicoptero-quest/` fuera de esta sesión.

## Siguiente acción
Licencia Unity → unity_check (4 modelos + compila scripts) → probar animación y explosión del motor en Unity.
