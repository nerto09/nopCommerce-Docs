# .agents-work/

Espacio de trabajo intermedio de los agentes. Una carpeta por rol.

Aqui van los borradores, notas, resultados de exploracion y peticiones a otros roles:
todo lo que ayuda a trabajar pero no es producto. El contenido de `docs/`, `en/`,
`services/` y compania debe poder leerse sin pasar por aqui.

## Peticiones entre roles

Nadie escribe fuera de sus rutas (ver [`AGENTS.md`](../AGENTS.md)). Cuando necesites un
cambio en territorio ajeno, anotalo en `.agents-work/<tu-rol>/peticiones.md` con:

- la ruta exacta,
- que hace falta y por que,
- el rol dueno (`.claude/scripts/check-ownership.py --who <ruta>`).

El rol dueno vacia su bandeja leyendo las `peticiones.md` de los demas. Cuando atiende
una, la tacha en el archivo de quien la pidio.

Este directorio es del coordinador: la estructura la define el, pero cada rol escribe
dentro de su propia carpeta.
