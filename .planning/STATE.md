# STATE

Actualizado: 2026-11-09 · Metodología: perfil A (GSD + Ponytail + Grill; Graphify opcional) — REQUIREMENTS v3 §4

## Hecho
- Estructura `lide-3d-gen` creada; HeliRotor migrado con caracterización (golden) y round-trip GLB/FBX.
- Skill `lide-3d-gen` (canónico + copias Claude/Codex), plantilla de modelo, `import_file` para assets importados/generados.

## Pendiente / decisiones del usuario
- Abrir Blender con el add-on MCP y probar el flujo en vivo (build con runpy + `look`).
- Probar `import_asset` y (con aprobación por créditos) `generate_3d` con un modelo real.
- Verificar HeliRotor dentro de Unity (FBX nativo; GLB requiere glTFast).
- Repo público: https://github.com/AdrianAguinaga/lide-3d-gen (commit inicial 168d7fc, 2026-11-09). Sin LICENSE aún.
- `../rotor-helicoptero-quest/`: archivos enviados a la Papelera (2026-11-09, aprobado); carpeta vacía pendiente de borrar fuera de la sesión.
- Evals del skill (§14): casos en `evals/cases.md`, sin ejecutar.

## Siguiente acción
Primer modelo nuevo con el skill (elige el usuario) → sirve también como eval positivo.
