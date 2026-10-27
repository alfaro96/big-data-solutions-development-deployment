---
description: Comprueba que los snippets de las diapositivas siguen alineados con code/
---

1. Ejecuta `python slides/scripts/extract_snippets.py --check`.
2. Si hay diferencias, lista los snippets afectados y los vídeos que los usan (busca el `id` en `slides/units/`).
3. Propón la actualización de vídeos, `docs/trazabilidad.md` y cuestionarios afectados. Si el cambio en `code/` hace falsa una explicación, dilo.
4. Comprueba también `git status -- code`: si hay cambios sin confirmar en `code/`, los snippets reflejan un estado no versionado; avísalo.
