# AGENTS.md — Roles y propiedad de rutas

Este repositorio se trabaja con varios agentes en paralelo. Para que no se pisen,
cada ruta tiene **un solo dueno**: el rol que puede escribirla. Todos los demas la
leen.

La fuente de verdad legible por maquina es [`.claude/ownership.json`](.claude/ownership.json).
Esta tabla y ese archivo deben decir lo mismo; si difieren, manda el JSON.

## Tabla de roles

| Rol | Dueno de (escribe) | Solo lee |
|---|---|---|
| investigador | `docs/research/`, `docs/adr/` (estado `proposed`) | todo |
| documentador | `docs/*` salvo `research/`, `adr/`, `qa/`, `design/`, `memory/`; `en/`, `templates/`, `README.md`, `CONTRIBUTING.md`, `docfx.json`, `toc.yml`, `.markdownlint.json`, `crowdin_nopcommerce.yml` | todo |
| desarrollador | `services/`, `clients/`, `web/`, `contracts/` | docs, tests |
| tester | `tests/` | services, contracts |
| disenador | `design/`, `docs/design/` | todo |
| qa | `docs/qa/` | todo (revisa PRs) |
| devops | `infra/` salvo `infra/ci/`; `web.config` | contracts, services |
| cicd | `.github/workflows/`, `infra/ci/` | todo |
| coordinador (humano / Claude principal) | `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.agents-work/`, `docs/memory/`, `.github/` salvo `workflows/`, `.gitignore` | todo |

## Regla de resolucion

Gana **el patron mas especifico** (el prefijo mas largo que coincide). Eso es lo que
elimina los solapamientos sin necesidad de listas de excepciones:

- `docs/running-your-store.md` -> `docs/` -> **documentador**
- `docs/qa/informe-sprint-3.md` -> `docs/qa/` -> **qa**
- `docs/memory/MEMORY.md` -> `docs/memory/` -> **coordinador**
- `infra/main.tf` -> `infra/` -> **devops**
- `infra/ci/build.yml` -> `infra/ci/` -> **cicd**

Las entradas que terminan en `/` son prefijos de directorio; el resto son rutas de
archivo exactas (`web.config`, `README.md`).

Una ruta **sin dueno declarado** no se escribe. Se pide al coordinador que la asigne
en `.claude/ownership.json` primero.

## Como se verifica

```bash
# el dueno de unas rutas concretas
.claude/scripts/check-ownership.py --who en/index.md docs/qa/a.md

# los cambios que llevo hechos pertenecen a mi rol?
.claude/scripts/check-ownership.py --role documentador

# solo lo que esta en el indice, antes de hacer commit
.claude/scripts/check-ownership.py --role tester --staged

# la propia configuracion no tiene patrones duplicados
.claude/scripts/check-ownership.py --audit
```

Devuelve `0` si todo esta en orden y `1` si hay una violacion, asi que sirve igual en
un hook local o en CI.

## Flujo de trabajo

1. **Antes de escribir**: confirma tu rol y corre `--who` sobre las rutas que piensas tocar.
2. **Mientras trabajas**: las notas, borradores y hallazgos intermedios van en
   `.agents-work/<rol>/`, no en las rutas de producto.
3. **Si necesitas un cambio fuera de tu propiedad**: no lo hagas tu. Dejalo pedido en
   `.agents-work/<tu-rol>/peticiones.md` y avisa al rol dueno (o al coordinador).
4. **Antes de commit**: corre `--role <tu-rol> --staged`. Debe salir en verde.
5. **Un PR, un rol.** Si un trabajo necesita dos roles, son dos PRs.

## Limites que no dependen de las rutas

- **investigador**: los ADR nacen en estado `proposed`. Pasarlos a `accepted` o
  `rejected` es decision del coordinador, no del investigador.
- **qa**: revisa los PRs de todos los roles y escribe sus hallazgos en `docs/qa/`.
  No corrige el codigo ajeno; lo reporta.
- **coordinador**: unico rol que edita `.claude/ownership.json`, y por tanto el unico
  que puede cambiar quien es dueno de que.

## Rutas declaradas que todavia no existen

Buena parte de la tabla apunta a rutas que no estan en el arbol: `services/`,
`clients/`, `web/`, `contracts/`, `tests/`, `infra/`, `infra/ci/`, `design/`,
`docs/research/`, `docs/adr/`, `docs/qa/` y `docs/design/`. Este repo es, hoy,
documentacion (`en/`, `templates/`, docfx).

**No se crearon directorios vacios a proposito**, por dos razones: git no versiona
directorios vacios, y el coordinador tampoco puede sembrar un `.gitkeep` en
`docs/qa/` sin escribir en territorio de qa. Cada rol crea su directorio la primera
vez que escribe en el. La propiedad ya esta declarada y entra en vigor sola el dia
que la ruta aparezca.
