---
description: Revisa el código de una fase del proyecto (guiada + abierta) y genera el informe
argument-hint: <1-7>
---

Fase solicitada: $ARGUMENTS

1. Lee `docs/prompts/revision-codigo.md` y determina los ficheros de la fase.
2. Delega en el agente `code-reviewer`.
3. Guarda el informe en `docs/revisiones/fase-$ARGUMENTS.md`.
4. Resume al profesor los errores críticos y las decisiones que necesitan su validación. **No apliques cambios en `code/` hasta que el profesor los apruebe.**
