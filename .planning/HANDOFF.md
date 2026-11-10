# HANDOFF — 2026-11-09

Leer primero: `AGENTS.md` (índice) → `.planning/STATE.md` (estado) → este archivo (contexto de la sesión).
Repo: https://github.com/AdrianAguinaga/lide-3d-gen · `main` al día (7eb1a48) · árbol limpio.

## Cómo retomar
1. Abrir Claude Code **en** `E:\skills\LIDE-Skills\lide-3d-gen` (la sesión anterior se abrió en la carpeta vieja y no cargaba el skill).
2. `/` → confirmar que aparece el skill `lide-3d-gen`.
3. Bootstrap ligero: `python scripts/sync_skills.py --check` y `python -m unittest` (debe dar OK, 2 tests, ~35 s).
4. Blender 5.1 con add-on MCP 1.8: `get_addon_status`; si el primer intento falla (WinError 10054) reintentar una vez.

## Hecho en la sesión
| Modelo | Fuente | Partes / tris / mat | Golden |
|---|---|---|---|
| `heli-rotor` | procedural (migrado del script original) | 62 / 12 356 / 7 | sí |
| `lab-table` | procedural (eval 1) | 4 / 424 / 4 | sí |
| `lab-stool` | Poly Haven `metal_stool_01` (CC0) | 1 / 8 334 / 1 | **no (pendiente de aprobación)** |
| `inline-four-engine` | procedural, corte educativo | 76 / 33 800 / 8 | sí |

- Lib `lide3d`: geometría (lathe, prism, box, loft, coil, hull2d), `Model.part(cut=…)` booleanos exactos con
  cara de corte roja, `import_file`, UVs automáticos, validación (presupuesto, materiales, UV, escala, nombres),
  report.json con `size`, `tri_hotspots`, `unity_box_collider`.
- Unity: `unity/Editor/LideImportCheck.cs` + `scripts/unity_check.py` (import real batchmode);
  `unity/Runtime/LideExplode.cs`, `LideEngineKinematics.cs`. **Compilan con el Roslyn de Unity; nunca ejecutados en Unity.**
- Evals: caso 1 con y sin skill (`evals/results.md`), mejoras aplicadas.

## Pendiente (en orden sugerido)
1. **Licencia Unity**: el usuario inicia sesión en Unity Hub y activa Personal. Sin eso batchmode sale con 198.
   Luego `python scripts/unity_check.py` (crea proyecto en `%TEMP%\lide3d-unity-check`; el primer intento dejó
   un proyecto a medias ahí — si falla, borrar esa carpeta y repetir).
2. Probar en Unity el motor: `InlineFour.fbx` + `LideEngineKinematics` + `LideExplode` en `InlineFour_Root`.
   Verificar sentido de giro (lóbulos deben empujar taqués; si no, `reverse`) y signo de bielas.
3. Aprobar `lab-stool` → `--fingerprint models/lab-stool/golden.json`.
4. Opcional: agarre XR (XRGrabInteractable + collider por pieza), LICENSE del repo, evals 2–11, CI.
5. Borrar la carpeta vacía `E:\skills\LIDE-Skills\rotor-helicoptero-quest` (estaba bloqueada por la sesión).

## Decisiones tomadas (no re-discutir sin motivo)
- Nombre `lide-3d-gen`; destino Unity/Meta Quest; cualquier modelo; MCP for Blender.
- Cada modelo reproducible desde `models/<name>/build.py`; `out/` fuera de git; golden solo con aprobación.
- Skill canónico en `agent-capabilities/`, copias generadas por `scripts/sync_skills.py`.
- Motor: 1.6 L genérico, DOHC 16v con válvulas a 15°, orden 1-3-4-2, sin múltiple de escape (lado del corte),
  alzada = función soporte del lóbulo (taqué plano).
- Modelos estáticos: una malla por material; educativos: una pieza por objeto con jerarquía de movimiento.

## Trampas conocidas (detalle en `references/pipeline.md`)
- `blender --python` necesita `--python-exit-code 1` o devuelve 0 con excepciones.
- En este PC `look` con shading material/rendered sale vacío → solid + `color_type="MATERIAL"`.
- Toggles de bibliotecas del add-on (Poly Haven, etc.) son por escena: se apagan al reiniciar Blender.
- `| tail` en un comando enmascara el código de salida: no concluir "pasó" por exit 0 con pipe.
- El instalador `uvx mcp-for-blender install-addon` falla al imprimir en cp1252: usar `PYTHONIOENCODING=utf-8`.
