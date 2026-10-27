# Diapositivas (reveal.js)

> Las pautas de este fichero son un mínimo. Aplica las mejores prácticas de diseño instruccional, de presentación y de accesibilidad aunque no estén listadas, y justifica en `docs/decisiones-pedagogicas.md` cualquier decisión que se aparte de ellas.

Antes de escribir nada, lee `docs/plan-docente.md` y el `CLAUDE.md` de la unidad (`units/XX/CLAUDE.md`).

## Relación con el repositorio de referencia

Referencia: https://github.com/alfaro96/programming-fundamentals-ii (Java, primer ciclo de grado). Se separa lo que se hereda de lo que NO.

### Se hereda: identidad visual y técnica
- Paleta de colores, tipografías, tema de reveal.js, fondos, iconografía y estilo de las notas del orador.
- Configuración técnica de reveal.js, build y exportación a PDF.
- El tema se extrae a `slides/theme/` y se usa tal cual (o con ajustes mínimos documentados). Misma marca visual.
- Se pueden **añadir** componentes nuevos dentro de la paleta; no se modifican los existentes.

### NO se hereda: la forma de enseñar
- Estructura de diapositivas, componentes y orden pedagógico se diseñan desde cero. No copiar por inercia patrones como tarjetas de concepto o bloques de "cómo se hace" pensados para aprender sintaxis.
- Contraste de públicos:
  - Referencia: grado, primer contacto con Java, vienen de C. Se enseña la mecánica del lenguaje con ejemplos cortos.
  - Aquí: profesionales de máster con base técnica, vídeo asíncrono y sesión síncrona de aplicación. Se enseña criterio de ingeniería, decisiones de diseño, compromisos (*trade-offs*) y fallos en producción.

| Referencia (grado, Java) | Este curso (máster, big data) |
|---|---|
| Sintaxis y "cómo se hace" | Decisión de diseño y su porqué |
| Comparativa con C | Comparativa entre alternativas de arquitectura |
| Ejemplo pequeño → código | Fallo real → diagnóstico → solución |
| Tarjetas con conceptos | Diagramas de flujo de datos, tablas de trade-offs |
| El código es el contenido | El código es la evidencia de una decisión |

Componentes candidatos (a validar): diagrama de arquitectura, comparativa de alternativas, línea temporal de un fallo, "decisión → consecuencia", fragmento de código anotado, pregunta guía.

### Primera tarea obligatoria
1. Analizar la referencia y escribir en `docs/decisiones-pedagogicas.md` qué se hereda y qué se descarta, con justificación.
2. Proponer la estructura de diapositivas y el catálogo de componentes, y **esperar mi validación** antes de producir los 45 vídeos.
3. Producir un **vídeo piloto** con el tema heredado y la nueva forma de enseñar, para revisión del profesor.

## Público y formato

- Cada vídeo dura ~20 minutos (orientativamente 15-20 diapositivas), con un único objetivo, un cierre que enlaza con el siguiente y una pregunta que prepara el cuestionario.
- Los 45 vídeos están separados pero hilados: cada uno retoma brevemente el anterior.

## Estructura de un vídeo (punto de partida a validar)

1. Objetivo y pregunta guía.
2. Problema real o fallo en producción.
3. Ejemplo concreto y mínimo.
4. Concepto y su porqué.
5. Código del proyecto (desde snippets).
6. Error típico y alternativa.
7. Resumen y enlace con el siguiente vídeo.

El agente puede proponer otra estructura si razona y documenta por qué funciona mejor para este público.

## Código en las diapositivas

- Nunca se escribe a mano: se declara en `slides/snippets.yaml` y se extrae con `python slides/scripts/extract_snippets.py` a `slides/snippets/`.
- Nunca se modifica `code/` para que "se vea mejor". Si un fragmento necesita explicación, se explica en la diapositiva (anotaciones y notas del orador).
- Fragmentos cortos (idealmente ≤ 15 líneas), con líneas relevantes resaltadas.
- Cada diapositiva con código lleva el nombre del fichero y la fase.
- Si el código mostrado cambia, ejecutar `/sync-check` en el mismo turno.

## Estilo

- Español técnico. Términos estándar en inglés, en cursiva la primera vez (*watermark*, *feature store*).
- Una idea por diapositiva. Sin párrafos largos. Notas del orador en cada diapositiva con el guion y tiempos aproximados.
- Accesibilidad: buen contraste, fuente legible en vídeo.
- No inventar resultados, métricas ni capturas del proyecto.

## Cuestionarios

- Uno por semana (15), en `units/XX/quizzes/week-XX.md`.
- Preguntas ligadas a vídeos concretos (con vídeo y diapositiva de origen); evalúan comprensión y criterio, no memorización. Con respuesta correcta y justificación.
- Formato Markdown (pendiente decidir exportación a GIFT/XML de Moodle).

## Nomenclatura de ficheros

- Vídeos: `units/XX-nombre/videos/week-WW-video-VV.html`.
- Cuestionarios: `units/XX-nombre/quizzes/week-WW.md`.

## Instrucciones del profesor (se ampliarán)

- (aquí se anotan los criterios que se vayan fijando)
