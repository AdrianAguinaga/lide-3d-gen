# STATE

Actualizado: 2026-11-09 · Metodología: perfil A (GSD + Ponytail + Grill; Graphify opcional) — REQUIREMENTS v3 §4

## Hecho
- Estructura `lide-3d-gen` creada; HeliRotor migrado con caracterización (golden) y round-trip GLB/FBX.
- Skill `lide-3d-gen` (canónico + copias Claude/Codex), plantilla de modelo, `import_file` para assets importados/generados.

## Pendiente / decisiones del usuario
- LabTable aceptada (golden.json, 2026-11-09). Add-on MCP 1.8 instalado.
- Activar Poly Haven (gratis) / Sketchfab / generadores en el panel MCP de Blender para probar import_asset y generate_3d.
- Probar `import_asset` y (con aprobación por créditos) `generate_3d` con un modelo real.
- Verificar HeliRotor dentro de Unity (FBX nativo; GLB requiere glTFast).
- Repo público: https://github.com/AdrianAguinaga/lide-3d-gen (commit inicial 168d7fc, 2026-11-09). Sin LICENSE aún.
- `../rotor-helicoptero-quest/`: archivos enviados a la Papelera (2026-11-09, aprobado); carpeta vacía pendiente de borrar fuera de la sesión.
- Evals del skill (§14): casos en `evals/cases.md`, sin ejecutar.

## Siguiente acción
Unity (rotor + mesa); eval 1 sin skill para comparar; import_asset con Poly Haven.
