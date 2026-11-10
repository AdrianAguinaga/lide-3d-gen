# Eval results

| Fecha | Caso | Con skill | Modelo agente | Resultado | Notas |
|---|---|---|---|---|---|
| 2026-11-09 | 1 mesa de laboratorio | sí (en la sesión que creó el skill: contaminado, no ciego) | claude-opus-5-5 | passed; aceptada por el usuario (golden.json) | live MCP build + `look` + headless export + tests OK. 4 partes / 680 tris / 4 materiales. Altura 0.90 m por defecto (no pedida). Sin corrida "sin skill" todavía. |
| 2026-11-09 | 1 mesa de laboratorio | **no** (subagente aislado, sin repo ni skill) | claude-opus-5-5 | passed técnico (auto-reportado) | 1 malla / 3 materiales / 224 tris / 1.2×0.6×0.9, UVs por proyección de caja, bisel en cubierta, sugiere BoxCollider. Solo GLB (sin FBX: Unity necesita glTFast). No reproducible fuera del scratch, sin validación ni pruebas, nombres en español. Mismo supuesto de altura 0.90 m. |

## Comparación caso 1 (n = 1, no concluyente)
| Criterio | Con skill | Sin skill |
|---|---|---|
| Dimensiones | ✔ | ✔ |
| Formatos Unity | GLB + FBX (nativo) | solo GLB |
| Eficiencia | 680 tris, 4 draw calls | **224 tris, 3 draw calls** |
| UVs | **no** | sí (caja) |
| Reproducible / versionado / probado | sí (repo, golden, round-trip) | script suelto, verificación manual |
| Collider | no mencionado | **sugerido** |

Acciones derivadas para el skill — **aplicadas 2026-11-09** (aprobadas): UVs automáticos en `Model.part` + validación de UV;
`unity_box_collider` y `tri_hotspots` en report.json + paso "Deliver" en el skill; guía de segmentos por tamaño.
LabTable 680 → 424 tris (patas 16 → 8 segmentos; golden regenerado). Sigue por encima de 224 (sin skill): una sola malla y niveladores más simples; diferencia no investigada a detalle.

## Motor 4 cilindros en línea (2026-11-09)
Con skill, mismo autor del skill (no ciego). Aclaración del usuario: educativo, en línea, cortes, piezas separables.
74 partes / 30 960 tris / 7 materiales; booleanos exactos con caras de corte rojas; jerarquía pistón > perno, biela.
Defecto encontrado con `look`: piñones de levas superpuestos (válvulas verticales) → válvulas a 15°, levas a 92 mm.
Separabilidad verificada en vivo con vista explosionada temporal. Unity sin verificar (licencia). Aceptado por el usuario.
Añadidos: banda de distribución, múltiple de admisión (escape omitido: lado del corte). 76 partes / 33 800 tris / 8 mat.
Defecto encontrado midiendo en Blender: alzada calculada con el radio del lóbulo (≈3 mm de error en flancos) →
función soporte (taqué plano). Pico 8.0 mm vs 7.94 medido. Scripts Unity compilan con Roslyn de Unity; comportamiento sin verificar.
