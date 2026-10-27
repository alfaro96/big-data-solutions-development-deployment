# Proyecto: Ciclo de vida de soluciones big data

Material docente del Máster de Big Data y Computación en la Nube: 45 vídeos (3 por semana durante 15 semanas) de unos 20 minutos, cuestionarios semanales y un proyecto de referencia en Databricks (detección de fraude en tarjetas).

Dinámica del curso: durante la semana X los estudiantes ven los vídeos y realizan el cuestionario; en la sesión síncrona de la semana X+1 se resuelven dudas y se aplica la teoría al proyecto (`code/`).

Temario: 1. Ciclo de vida de soluciones big data · 2. Alcance y viabilidad ·
3. Preparación y gestión de datos · 4. Modelado y experimentación ·
5. Despliegue y monitorización.

## Principio rector: mejores prácticas en todo

Este proyecto es material docente y a la vez ejemplo de referencia: todo lo que produzcas debe ser lo que un profesional senior consideraría correcto en ese ámbito. Aplica a TODO, esté o no listado en estas reglas: código, nombres, comentarios, estructura, configuración, tests, commits, ramas, documentación, diapositivas, cuestionarios, scripts y automatización.

### Cómo decidir
1. Ante cualquier decisión: "¿qué haría un equipo senior en un proyecto de producción de este ámbito?" y hazlo.
2. Las reglas escritas son un mínimo, no un máximo. Que algo no esté listado nunca es motivo para no aplicar una buena práctica.
3. Si una regla escrita contradice una buena práctica establecida, no la sigas en silencio: señala el conflicto y propón la corrección.
4. Cantidad adecuada: lo mínimo que hace el artefacto correcto, completo y comprensible. Ni relleno ni carencias (comentarios, docstrings, tests, documentación, diapositivas).
5. Coherencia: un mismo problema se resuelve siempre del mismo modo en todo el proyecto. Antes de introducir una convención, busca si ya existe.
6. Si dudas de cuál es la mejor práctica, o hay varias válidas con contrapartidas, expón las alternativas brevemente y recomienda una. No inventes ni adivines.

### Verificación (antes de dar algo por terminado)
- Reléelo como revisor externo, no como autor.
- Pasa linter, formateador y tests si existen.
- Comprueba consistencia con el resto del proyecto (nombres, config, convenciones, idioma).
- Declara qué has verificado y qué no has podido verificar.

## Fundamento técnico: documentación oficial de Databricks

Todo el código de `code/` debe basarse en lo que la plataforma permite en **nuestra edición** y en lo que su documentación oficial recomienda.

- Fuente de verdad: `docs/referencia-databricks.md`, mantenida por el agente `databricks-researcher` (`/research-databricks`).
- Las skills del plugin oficial de Databricks (`databricks@claude-plugins-official`) orientan, pero no son fuente de verdad: son genéricas y no garantizan lo que permite Free Edition. Lo que se afirme o se use en `code/` o en `slides/` debe estar en la referencia con su cita; si el plugin sugiere algo que no está, se investiga antes con `databricks-researcher`.
- Antes de revisar o modificar código de una fase, comprueba que la referencia cubre sus capacidades, límites y buenas prácticas; si no, investiga primero.
- Edición: **Databricks Free Edition**. Community Edition está retirada: no uses su documentación ni asumas características de otra edición.
- Fuentes: para el código (APIs, patrones, buenas prácticas), la documentación general de Databricks para AWS (`docs.databricks.com/aws/en/`); para cómputo, permisos, cuotas y límites, la de Free Edition. Que algo no aparezca en las páginas de la edición no impide usarlo si la documentación general lo describe.
- Cita siempre URL y fecha. Si no puedes verificar algo, regístralo en "Preguntas abiertas"; no lo afirmes. Lo que requiera comprobarse en el workspace real se marca así.
- Ante conflicto entre una práctica genérica y la documentación oficial de la plataforma, prevalece la documentación, y se deja constancia.

## Estructura

- `code/`: proyecto de referencia. Los estudiantes lo ven en Databricks (sparse checkout limitado a `code/`, acceso de solo lectura); nunca ven el repositorio.
- `slides/`: diapositivas reveal.js, cuestionarios y scripts (privado).
- `docs/`: plan docente, trazabilidad, revisiones y prompts (privado).
- `.claude/`: agentes y comandos (único, en la raíz).

## Idioma

- Español: README, documentación, diapositivas, notas del orador, cuestionarios, informes y ficheros como este.
- Inglés: todo el código (identificadores, comentarios, docstrings, strings, salidas por pantalla) y todos los mensajes de commit.

## Formato de los textos en Markdown

En Markdown y en cualquier documento en prosa (README, `CLAUDE.md`, `docs/`, cuestionarios, notas del orador escritas en Markdown) **no se fuerzan saltos de línea**:

- Un párrafo es una sola línea, sin cortarla a un ancho fijo. Es el editor o el visor quien ajusta el texto.
- Solo hay salto de línea donde el Markdown lo exige: entre párrafos (línea en blanco), en cada elemento de lista, fila de tabla, encabezado o línea de un bloque de código.
- No se usan dos espacios finales ni `\` para forzar saltos, salvo que haya una razón de contenido que se documente.
- Al editar un fichero existente, se respeta esta convención y no se reajustan párrafos que no se han tocado, para que los diffs solo muestren cambios reales.
- Esto **no** aplica al código: los comentarios y docstrings de Python respetan el límite de línea de `docs/reglas-codigo.md`, y el asunto de un commit tiene un máximo de 72 caracteres.

## Reglas importadas

@docs/reglas-codigo.md @docs/flujo-git.md

## Bucle de trabajo por unidad (obligatorio, en este orden)

0. Verificar/actualizar `docs/referencia-databricks.md` para la fase (`databricks-researcher`).
1. Revisar el código de la fase con el agente `code-reviewer` (prompt en `docs/prompts/revision-codigo.md`). El profesor valida el informe.
2. Aplicar las mejoras en `code/` en una rama, con commits pequeños y descriptivos.
3. Registrar hallazgos y decisiones en `docs/revisiones/fase-X.md`.
4. Declarar los fragmentos en `slides/snippets.yaml` y extraerlos (`python slides/scripts/extract_snippets.py`).
5. Escribir los vídeos de la unidad (`slide-author`).
6. Revisar coherencia, duración y alineación (`slide-reviewer`).
7. Generar el cuestionario de cada semana (`quiz-writer`).
8. Actualizar `docs/trazabilidad.md`.

No avances de paso sin dejar registrado el anterior.

## Sincronía entre `code/` y `slides/`

- Las diapositivas **nunca** copian código a mano: lo extraen de `code/` según `slides/snippets.yaml` (por símbolo o por anclas). El código público NO lleva marcadores ni comentarios pensados para las diapositivas.
- Cualquier cambio en un fichero mostrado exige regenerar los snippets y ejecutar `/sync-check` en el mismo turno.
- Si renombras un fichero, función, tabla o parámetro que aparece en un vídeo, actualiza el vídeo, `docs/trazabilidad.md` y el cuestionario.
- Si algo no puede mantenerse sincronizado, dilo explícitamente.
- Cambios de texto, analogías o maquetación en `slides/` no tocan `code/`.

## Separación entre lo que ven los estudiantes y lo privado

- Hay **un solo repositorio, privado**. Los estudiantes solo ven `code/` dentro de Databricks (carpeta Git con *sparse checkout* de `code/`, acceso de solo lectura al workspace). No tienen acceso a GitHub.
- Aun así, `code/` es lo que se enseña: nada que apunte a material privado (vídeos, rúbricas, informes, prompts, unidades) puede aparecer en sus ficheros ni en sus comentarios.
- Los mensajes de commit que toquen `code/` van en inglés y en Conventional Commits (buena práctica y ejemplo para el estudiantado); conviene que no mencionen el curso, porque la interfaz de Databricks puede mostrar la rama y el último commit.
- Sin credenciales, tokens, rutas personales ni datos en ningún fichero. Si se confirma una credencial, rotarla: borrarla del repositorio no basta.
- El nombre del repositorio y de la rama pueden verse desde Databricks: deben ser neutros.
- Los estudiantes no ven el historial de Git, así que el historial no es material docente; el ejemplo de buenas prácticas está en el código y en el README.

## Autoría de los commits

Todos los commits y pull requests salen **a nombre del profesor**, con la identidad de Git ya configurada en su máquina.

- Nunca añadas atribución al agente: ni `Co-Authored-By`, ni "Generated with Claude Code", ni emojis o firmas equivalentes, ni en el asunto, ni en el cuerpo, ni en los *trailers* de los commits o de los PR.
- No cambies la identidad de Git (`git config user.name`, `user.email`) ni uses `--author` o `--reset-author`.
- Los mensajes siguen el formato de `docs/flujo-git.md` y no mencionan que los haya escrito un agente.
- Antes de dar un commit por terminado, comprueba con `git log -1 --format=%B` que no contiene ninguna atribución.

### Firma de los commits

- **Todos los commits van firmados** con la clave del profesor ya configurada: `git commit -S`, también en el commit de cada integración (*squash merge*), y `git tag -s` para etiquetas. No asumas que `commit.gpgsign` está activado: usa `-S` siempre.
- Después de cada commit, comprueba la firma: `git log -1 --format='%G? %GS'` debe mostrar `G` (firma válida). Cualquier otro estado (`N`, `B`, `E`, `U`, `X`, `Y`, `R`) es un fallo.
- Si la firma falla (clave no disponible, `ssh-agent` o `gpg-agent` sin desbloquear, passphrase pendiente), **detente y avisa al profesor**. Nunca uses `--no-gpg-sign`, ni `-c commit.gpgsign=false`, ni cambies la configuración de firma para saltártelo, ni dejes un commit sin firmar "para firmarlo luego".
- No reescribas commits ya firmados (`rebase`, `commit --amend`) salvo que el profesor lo pida, porque cambiarlos invalida su firma.

## Identidad visual y pedagogía

Identidad visual heredada de https://github.com/alfaro96/programming-fundamentals-ii (colores, tipografías, tema). Pedagogía propia, diseñada para el perfil del Máster. Detalle en `slides/CLAUDE.md`.

## Autoactualización de criterios

Si el profesor corrige el mismo criterio dos veces, propón añadirlo al `CLAUDE.md` del nivel adecuado antes de continuar y registra el motivo en `docs/decisiones-pedagogicas.md`. El profesor es el revisor final.

## Honestidad

- No declares algo terminado sin haberlo comprobado.
- Si no puedes verificar una afirmación técnica sobre Databricks, márcala como pendiente de verificación.
- No inventes resultados, métricas ni capturas del proyecto.
