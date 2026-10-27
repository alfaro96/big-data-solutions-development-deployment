# Ciclo de vida de soluciones big data (repositorio privado del curso)

Material del Máster de Big Data y Computación en la Nube: 45 vídeos, 15 cuestionarios y el proyecto de referencia (`code/`, repositorio público).

Este repositorio es **privado**. Contiene lo que no debe ver el estudiantado: prompts, rúbricas, informes de revisión, plan docente y configuración del agente. Los estudiantes solo ven `code/`, en Databricks (sparse checkout, solo lectura).

## Contenido

| Carpeta | Contenido | Visibilidad |
|---|---|---|
| `code/` | Proyecto Databricks | Visible para estudiantes solo en Databricks |
| `slides/` | Vídeos reveal.js, cuestionarios, scripts | Privado |
| `docs/` | Plan docente, trazabilidad, revisiones, prompts | Privado |
| `.claude/` | Agentes y comandos de Claude Code | Privado |

## Puesta en marcha

Ver `docs/inicio.md` (creación del submódulo, instalación y primer uso).

## Comandos del agente

| Comando | Función |
|---|---|
| `/review-phase <n>` | Revisa el código de la fase n (guiada + abierta) |
| `/build-videos <unidad> [--video n]` | Genera los vídeos de una unidad |
| `/research-databricks [tema]` | Investiga en la documentación oficial qué permite la edición y las buenas prácticas |
| `/sync-check` | Comprueba que los snippets siguen alineados con `code/` |
| `/build-quiz <semana>` | Genera el cuestionario de una semana |

## Documentación

- `docs/plan-docente.md`: mapa de 45 vídeos / 15 semanas.
- `docs/trazabilidad.md`: vídeo → ficheros de `code/` → cuestionario.
- `docs/referencia-databricks.md`: capacidades, límites y buenas prácticas de la plataforma.
- `docs/decisiones-pedagogicas.md`: decisiones y su motivo.
- `docs/reglas-codigo.md` y `docs/flujo-git.md`: reglas del código y de Git.
