# Contrato de tarea — copiar al inicio de cada `PLAN.md` (REQUIREMENTS-AGENTES-v3 §11)

```yaml
task_id: null              # p.ej. 07-01
objective: null
acceptance: []             # criterios observables, cada uno con cómo se verifica
scope_allowed: []          # = files_modified; nada fuera de aquí sin justificar
scope_excluded: []
flow_owner: GSD
executor: null             # persona o agente
risk: unknown              # low | medium | high (datos personales/seguridad = high)
methodology: perfil-A      # GSD + Grill + Ponytail (+ Graphify opcional) + skill lide-3d-gen
model_tier: null           # D0 | M1 | M2 | M3
requested_model: null
resolved_model: null
reasoning: null
base_revision: null        # commit sobre el que se planificó
context_manifest: null     # archivos/§ del contrato cargados y por qué
verification_result: pending   # passed | failed | unverifiable
evidence: []               # comandos ejecutados y su resultado real
approvals: []              # instalaciones, push, merge, etc. aprobados por el usuario
next_action: null
```

`SUMMARY.md` al cerrar: `verification_result` final, `evidence` con salida real (p.ej. `python -m unittest -v → OK`) y lo que quedó `unverifiable` con motivo.
