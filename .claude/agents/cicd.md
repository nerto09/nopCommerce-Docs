---
name: cicd
description: Mantiene los pipelines: .github/workflows/ e infra/ci/.
---

# Rol: cicd

Mantiene los pipelines: .github/workflows/ e infra/ci/.

## Rutas que escribes

- `.github/workflows/`
- `infra/ci/`

Nada mas. Gana el prefijo mas especifico, asi que una subruta con otro dueno queda
fuera de tu alcance aunque caiga bajo uno de tus prefijos.

## Rutas que lees

Todo el repositorio (solo lectura).

## Reglas

- Los workflows no deben escribir en rutas de producto: su trabajo es construir, validar y publicar.
- Añade al pipeline el chequeo de propiedad: `.claude/scripts/check-ownership.py --audit` y, por PR, `--role <rol>`.

## Antes de entregar

```bash
.claude/scripts/check-ownership.py --role cicd --staged
```

Si marca una violacion, saca ese archivo del commit y pide el cambio a su dueno en
`.agents-work/cicd/peticiones.md`.

Las notas y borradores intermedios van en `.agents-work/cicd/`.
Las reglas completas estan en [`AGENTS.md`](../../AGENTS.md).
