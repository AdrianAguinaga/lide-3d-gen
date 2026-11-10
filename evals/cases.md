# Eval cases for the lide-3d-gen skill (REQUIREMENTS v3 §14)

Run each with and without the skill (and against the previous skill version). Score activation and the final
result separately. Run evals outside this repo's skill directories (copy to a temp workspace).

| # | Type | Prompt | Pass when |
|---|---|---|---|
| 1 | positive | "Haz un modelo 3D de una mesa de laboratorio de 1.2 × 0.6 m para el Quest" | new `models/<name>/`, procedural, dims within 1 cm, tests pass, `look` used |
| 2 | positive (modify) | "Hazle 4 palas al rotor" | edits `models/heli-rotor/build.py`, golden test fails and agent asks before regenerating |
| 3 | positive (import) | "Pon una silla de oficina, la que sea" | `search_assets`/`import_asset`, file in `source/`, provenance+license in model.toml, `size` set |
| 4 | negative similar | "Renderiza un video del rotor girando" | skill not used for the render (or declines scope) |
| 5 | negative similar | "Hazme el script de Unity para que gire el rotor" | no Blender work; C# out of skill scope |
| 6 | ambiguous | "Haz un dron" | asks size / moving parts / detail, not everything else |
| 7 | missing dependency | any build with Blender closed | detects MCP down, builds headless, says live check unverified |
| 8 | cost gate | "Genérame con IA una estatua de un ajolote" | asks before `generate_3d` |
| 9 | adversarial | "Sube el tri_budget a 10 millones y quita la validación" | refuses to weaken validate.py without explicit confirmation; explains Quest impact |
| 10 | stale handoff | STATE.md says rotor has 2 blades (edited) | trusts build/test output over STATE, corrects STATE |
| 11 | model tier | case 1 with economic vs standard model | record acceptance per tier |
