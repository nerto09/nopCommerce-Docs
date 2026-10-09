# CLAUDE.md

## Que es este repo

La documentacion de nopCommerce, publicada con docfx en
[docs.nopCommerce.com](https://docs.nopCommerce.com). El contenido vive en `en/`
(incluida la traduccion en `en/spanish/`), las plantillas del sitio en `templates/`,
y la estructura de navegacion en `toc.yml` y `docfx.json`.

## Antes de escribir cualquier archivo

Este repo se trabaja con varios agentes a la vez y **cada ruta tiene un solo dueno**.
Lee [`AGENTS.md`](AGENTS.md) y, antes de tocar algo, comprueba de quien es:

```bash
.claude/scripts/check-ownership.py --who <ruta> [<ruta> ...]
```

Si la ruta no es de tu rol, no la edites: pide el cambio a su dueno en
`.agents-work/<tu-rol>/peticiones.md`. Si no tiene dueno declarado, es el coordinador
quien lo asigna en `.claude/ownership.json`.

Si trabajas sin un rol asignado, actuas como **coordinador** y tu alcance de escritura
es solo: `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.agents-work/`, `docs/memory/`,
`.github/` (salvo `workflows/`) y `.gitignore`.

## Antes de cada commit

```bash
.claude/scripts/check-ownership.py --role <tu-rol> --staged
```

Debe salir en verde. Un PR, un rol.

## Convenciones de contenido

- Markdown segun `.markdownlint.json` (sin limite de ancho de linea, un solo `h1`,
  sin puntuacion final en los titulos).
- Las imagenes van en el `_static/` de la carpeta de su pagina, como ya hace `en/`.
- Si añades o mueves una pagina, actualiza el `toc.yml` que la contiene.
- Las traducciones siguen la estructura de `en/`; el mapeo lo define
  `crowdin_nopcommerce.yml`.

## Memoria del proyecto

Las decisiones que afectan a mas de un rol se anotan en
[`docs/memory/MEMORY.md`](docs/memory/MEMORY.md) (lo escribe el coordinador). Leelo
antes de proponer un cambio estructural: probablemente ya se discutio.
