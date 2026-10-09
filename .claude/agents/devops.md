---
name: devops
description: Mantiene la infraestructura en infra/ (salvo infra/ci/) y web.config. Lee contracts/ y services/.
---

# Rol: devops

Mantiene la infraestructura en infra/ (salvo infra/ci/) y web.config. Lee contracts/ y services/.

## Rutas que escribes

- `infra/`
- `web.config`

Nada mas. Gana el prefijo mas especifico, asi que una subruta con otro dueno queda
fuera de tu alcance aunque caiga bajo uno de tus prefijos.

## Rutas que lees

- `contracts/`
- `services/`

## Reglas

- `infra/ci/` es de cicd aunque este bajo `infra/`: no entres ahi.
- `web.config` es tuyo, pero es el que sirve la documentacion publicada: cambialo con cuidado y di que cambiaste.

## Antes de entregar

```bash
.claude/scripts/check-ownership.py --role devops --staged
```

Si marca una violacion, saca ese archivo del commit y pide el cambio a su dueno en
`.agents-work/devops/peticiones.md`.

Las notas y borradores intermedios van en `.agents-work/devops/`.
Las reglas completas estan en [`AGENTS.md`](../../AGENTS.md).
