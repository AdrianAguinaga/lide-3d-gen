# BOOTSTRAP.md — Registro de base reproducible (REQUIREMENTS v3 §6, §9)

Bootstrap completo: 2026-11-09. Repetir solo ante cambio material (Blender, MCP, metodología). Por sesión basta el
bootstrap ligero de `AGENTS.md` (STATE + sync check).

```yaml
template_id: null              # brownfield: migrado desde ../rotor-helicoptero-quest (script suelto)
source: E:/skills/LIDE-Skills/rotor-helicoptero-quest/build_rotor.py
revision: null                 # sin git al adoptar
license: unknown
compatible_versions:
  blender: "5.1.0 (build 2026-03-17)"
  python_host: "3.11.9 (tests; solo stdlib)"
  blender_python: "3.13 (tomllib)"
  git: "2.51.0"
  mcp_for_blender_addon: unknown   # no conectado durante el bootstrap
setup_command: null            # sin dependencias que instalar
smoke_command: python -m unittest -v
last_verified_at: 2026-11-09
limitations:
  - MCP for Blender no estaba conectado (Blender cerrado); flujo en vivo sin verificar.
  - Export FBX/GLB verificado por re-importación en Blender, no dentro de Unity ni en un Quest.
  - generate_3d / import_asset no probados (requieren MCP; generate_3d puede gastar créditos).
  - import_file probado con el propio HeliRotor.glb (escala 2 m, escala de objeto 1).
```

## Diagnóstico G0 (2026-11-09)
- **Hechos**: el script original produce 62 partes / 12 356 tris / 7 materiales / 65 objetos y es idempotente
  (dos ejecuciones → mismo fingerprint). Ese fingerprint es `models/heli-rotor/golden.json` (caracterización).
- **Refactor**: geometría idéntica al golden tras extraer `lib/lide3d`. GLB del pipeline = mismo tamaño en bytes que el original.
- **Cambio deliberado**: FBX ahora con ejes Unity (Y up, -Z forward, escala 1). El FBX original no tenía ajustes registrados.
- **Origen retirado**: `../rotor-helicoptero-quest/` enviado a la Papelera el 2026-11-09 con aprobación del usuario; su lógica vive en `models/heli-rotor/` + `golden.json`.
