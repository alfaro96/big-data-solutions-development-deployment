# Flujo de Git

> Estas reglas concretan el principio rector del `CLAUDE.md` raíz. Son un mínimo: ante lo que no cubran, se aplica la mejor práctica del ámbito.

Un único repositorio privado con todo el curso. Las buenas prácticas de Git se aplican igual a `code/` y al resto.

## Ramas

- `main`: siempre estable. No se commitea directamente.
- Ramas con prefijo y nombre corto en `kebab-case`: `feat/`, `fix/`, `refactor/`, `docs/`, `chore/`, `test/` (p. ej. `feat/inference-spine`, `refactor/centralize-config`).
- Una rama = un propósito. Vida corta; se integra en `main` y se borra.
- Integrar con *squash merge*: cada rama entra en `main` como un único commit, así que `main` tiene una historia lineal con un commit por cambio. Se hace en local para firmarlo con la clave del profesor: `git merge --squash <rama>` y `git commit -S` con un mensaje Conventional Commits que resuma la rama. Como Git no marca la rama como fusionada, se borra con `git branch -D <rama>` tras comprobar que `main` contiene sus cambios.
- No reescribir historia ya publicada.

## Commits (Conventional Commits)

Formato: `tipo(ámbito): descripción en imperativo, sin punto final`. Todos los mensajes de commit van en inglés, también los que no tocan `code/`.

- Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`.
- Asunto de hasta 72 caracteres; cuerpo opcional explicando el **porqué**.
- Un commit = un cambio lógico. No mezclar refactor y funcionalidad.
- Prohibidos mensajes como `fix`, `update`, `cambios`, `wip`.

Ejemplos:

    refactor(config): move table names to config/settings.yaml
    fix(simulation): use unique batch timestamp for label files
    feat(gold): add inference aggregations table
    docs(readme): describe training-serving split

## Visibilidad de `code/`

Un solo repositorio, privado. Los estudiantes ven `code/` en Databricks a través de una carpeta Git con *sparse checkout* y acceso de solo lectura; no tienen acceso a GitHub.

1. Commits de `code/`: en inglés, Conventional Commits, mensajes que sirvan de ejemplo y sin referencias al curso.
2. Preferible no mezclar en una misma rama (y, por tanto, en un mismo commit de integración) cambios de `code/` y de `slides/` o `docs/`: facilita revisar y revertir cada cosa.
3. Nada de credenciales ni datos. Si se confirma alguna, se rota.
4. Nombres de repositorio y de ramas neutros (pueden verse en Databricks).

## Autoría

- Todos los commits y PR van a nombre del profesor. Sin `Co-Authored-By`, sin firmas del agente y sin cambiar la identidad de Git (ver `CLAUDE.md`).
- Comprobación previa al push: `git log origin/main..HEAD --format=%B` no debe contener atribuciones.
- **Commits firmados (`git commit -S`).** Comprobación previa al push: `git log origin/main..HEAD --format='%h %G?'` debe mostrar `G` en todos.
- Los commits de integración (*squash*) y las etiquetas también se firman (`commit -S`, `tag -s`).
- Si la firma falla, no se salta: se resuelve la clave o el agente de firmas y se repite el commit.
- Para que GitHub los marque como *Verified*, la clave pública debe estar añadida a la cuenta del profesor (comprobar en su documentación actual).

## Versionado

- Etiquetar al cerrar cada fase con prefijo `code-` (`code-v0.3.0-medallion`…) y registrar en `docs/trazabilidad.md` la etiqueta o el commit de `code/` que usa cada vídeo.
- Registrar en `docs/trazabilidad.md` la etiqueta o commit que usa cada vídeo.

## Antes de cada push

- Linter y tests si existen.
- `git diff --staged`: sin credenciales, datos, temporales ni referencias a material privado en el repositorio público.
- `.gitignore` cubre artefactos de Python, Databricks y MLflow.

## Gestión del trabajo

- `TODO.md` por fase con su definition of done.
- Toda decisión no trivial queda en `docs/revisiones/` o `docs/decisiones-pedagogicas.md`.
