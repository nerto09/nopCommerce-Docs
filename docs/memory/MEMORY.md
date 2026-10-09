# Memoria del proyecto

Decisiones que afectan a mas de un rol. Las escribe el coordinador. Lo mas reciente
arriba. Lo que es una decision de arquitectura con alternativas va en un ADR
(`docs/adr/`), no aqui; aqui queda el registro corto y el enlace.

## 2026-10-09 — Propiedad de rutas por rol

Se adopta un modelo de **un dueno por ruta** para que varios agentes trabajen en
paralelo sin pisarse. Fuente de verdad: `.claude/ownership.json`. Tabla legible:
`AGENTS.md`.

Decisiones tomadas al implementarlo:

- **Resolucion por prefijo mas especifico** en lugar de listas de excepciones. Asi
  `docs/qa/` es de qa y `docs/` del documentador sin que ninguno de los dos tenga que
  enumerar al otro, y añadir un dueno nuevo no obliga a editar las reglas existentes.
- **`docs/memory/` se saca de `docs/`** y pasa al coordinador. En la tabla original
  caia bajo el `docs/*` del documentador y al mismo tiempo se listaba como del
  coordinador: era el unico solapamiento real de la propuesta.
- **`.github/` se asigna al coordinador, `.github/workflows/` a cicd.** La tabla solo
  cubria `workflows/`, asi que `CODEOWNERS`, plantillas de PR e issues quedaban sin
  dueno.
- **Las rutas existentes del repo se reparten**: `en/`, `templates/`, `docfx.json`,
  `toc.yml`, `.markdownlint.json`, `crowdin_nopcommerce.yml`, `README.md` y
  `CONTRIBUTING.md` al documentador (son documentacion y su publicacion);
  `web.config` a devops (sirve el sitio); `.gitignore` al coordinador. La tabla
  original hablaba de `services/`, `clients/`, `web/` y `contracts/`, que en este repo
  no existen.
- **No se crearon directorios vacios** para ninguna ruta declarada que aun no
  existe (`services/`, `clients/`, `web/`, `contracts/`, `tests/`, `infra/`,
  `design/`, `docs/research/`, `docs/adr/`, `docs/qa/`, `docs/design/`). Ademas de
  que git no versiona directorios vacios, el coordinador no puede sembrar un
  `.gitkeep` en `docs/qa/` sin violar la regla que esta estableciendo. Cada rol crea
  su directorio al escribir por primera vez.
- **`.github/workflows/ownership.yml` no se creo**: es de cicd y el coordinador no
  escribe ahi. Queda pedido en `.agents-work/coordinador/peticiones.md`. Hasta que
  exista, el chequeo se corre a mano o con un hook local.
