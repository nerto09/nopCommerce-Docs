# Peticiones de coordinador

Cambios que este rol necesita en rutas de las que no es dueno.
Formato: `- [ ] <ruta> — <que hace falta> (dueno: <rol>)`

- [ ] `.github/workflows/ownership.yml` — workflow que corra, en cada PR,
      `.claude/scripts/check-ownership.py --audit` y
      `.claude/scripts/check-ownership.py --role <rol> --base origin/master`,
      tomando el rol de una etiqueta del PR o del prefijo de la rama. El coordinador
      no escribe en `workflows/`. (dueno: cicd)
