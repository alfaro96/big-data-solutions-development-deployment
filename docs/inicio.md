# Puesta en marcha

## 1. Crear el repositorio

Crea un único repositorio **privado** en GitHub y sube esta carpeta con tu código actual dentro de `code/` (licencia, README en español y `.gitignore`). Pon un nombre neutro: puede verse desde Databricks.

## 2. Mostrar `code/` a los estudiantes en Databricks

1. En tu workspace: *Workspace → Create → Git folder*, URL del repositorio privado, **activando sparse checkout** con el patrón `code`.
2. Da a los estudiantes acceso de solo lectura al workspace.

Verificado por el profesor: los estudiantes ven y leen `code/`, no ven nada más del repositorio, no pueden cambiar la configuración de Git ni operar con su credencial y no tienen permisos de ejecución (el código se ejecuta solo en las sesiones del profesor). Los nombres exactos de los botones pueden variar según la versión de la interfaz.

## 3. Instalar dependencias de las diapositivas

```bash
cd slides && npm install
```

## 4. Primer uso con Claude Code

Abre Claude Code en la raíz y pide, en este orden:

0. `/research-databricks` (edición, límites y buenas prácticas). Revisa `docs/referencia-databricks.md` y confirma la edición.
1. "Lee `CLAUDE.md` y ejecuta la primera tarea de `slides/CLAUDE.md` (análisis de la referencia). No generes vídeos todavía."
2. Valida `docs/decisiones-pedagogicas.md` y el catálogo de componentes.
3. "Genera el vídeo piloto" (ver `slides/CLAUDE.md`) y revísalo.
4. `/review-phase 3` sobre la fase que mejor conozcas, y sigue el bucle.

## 5. Comprobaciones

- `python slides/scripts/extract_snippets.py --check` (alineación de snippets).
- `git log -- code` (mensajes de commit descriptivos, en inglés y sin referencias al curso).
