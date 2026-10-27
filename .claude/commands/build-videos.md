---
description: Genera los vídeos de una unidad (o uno concreto) siguiendo el bucle de trabajo
argument-hint: <unidad 1-5> [--video N]
---

Argumentos: $ARGUMENTS

1. Comprueba que existe el informe de revisión de la fase (si la unidad tiene código) y que el profesor lo ha validado. Si no, detente y avísalo.
2. Comprueba que `docs/decisiones-pedagogicas.md` contiene la estructura de diapositivas validada. Si no, detente.
3. Declara/actualiza los snippets en `slides/snippets.yaml` y ejecuta `python slides/scripts/extract_snippets.py`.
4. Delega en `slide-author` para escribir los vídeos en `slides/units/<unidad>/videos/`.
5. Delega en `slide-reviewer` y corrige lo bloqueante.
6. Actualiza `docs/trazabilidad.md` y `TODO.md`.
7. Informa de qué se ha verificado y qué queda pendiente.
