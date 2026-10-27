# Reglas del código (`code/`)

> Estas reglas concretan el principio rector del `CLAUDE.md` raíz. Son un mínimo: ante lo que no cubran, se aplica la mejor práctica del ámbito.

## Principios

- El código es material docente: debe poder mostrarse en una diapositiva y leerse sin contexto adicional.
- Un fichero, una responsabilidad. DRY, YAGNI y mínima sorpresa.
- Nunca se modifica el código para que "se vea mejor" en una diapositiva.

## Nomenclatura (PEP 8)

- `snake_case` para variables, funciones y módulos; `UPPER_SNAKE_CASE` para constantes; `PascalCase` para clases; prefijo `_` para funciones internas.
- Nombres descriptivos y autoexplicativos. Prohibidos `df`, `df2`, `tmp`, `x`, `aux`, `data` salvo en ámbitos de una o dos líneas.
- Booleanos con `is_`, `has_`, `should_`; funciones con verbo (`build_`, `load_`, `compute_`, `save_`).
- Un mismo concepto tiene el mismo nombre en DLT, notebooks, utils y documentación.
- Tablas: `capa_entidad` (`bronze_transactions`, `gold_fraud_spine`). Sufijos de columnas transformadas homogéneos (`_imp`, `_dbl`, `_idx`, `_ohe`).

## Configuración

- Centralizada en `config/` (YAML o TOML) y cargada desde una función. Catálogo, esquema, tablas, ventanas, umbrales y rutas se definen una vez.
- Separar parámetros de infraestructura (catálogo, esquema) de parámetros de negocio (watermark, ventanas de entrenamiento).
- Sin valores mágicos: constantes con nombre (`WINDOW_1H_MS`, no `-3_600_000`).
- Sobrescribible por entorno (dev/prod) sin tocar el código.

## Utilidades

- Los módulos de utilidades solo contienen funciones y clases: sin I/O, sin `spark.read`/`spark.sql`, sin `print` y sin efectos al importarse.
- Los datos se cargan en el notebook y se pasan como parámetros.
- Funciones pequeñas, con type hints y docstring.
- Importables sin sesión Spark activa (solo su ejecución la requiere).

## Comentarios y docstrings

Principio: el código dice **qué** hace; los comentarios dicen **por qué**. Un comentario se escribe solo si un lector competente no puede deducir esa información leyendo el código.

### Cuándo SÍ comentar
- Decisiones no obvias y su motivo (`handleInvalid="error"` como barrera de calidad; límite superior de -1 ms para excluir la transacción actual).
- Restricciones externas o comportamientos sorprendentes de Spark, Databricks o Delta (workarounds, límites de serverless, particularidades del watermark).
- Valores mágicos que no pueden ser constante con nombre.
- Supuestos de negocio (p. ej. "etiqueta nula = no fraude confirmado").
- Alternativas descartadas cuando alguien podría "arreglarlo" por error.

### Cuándo NO comentar
- Cuando repite el código (`# suma amount` sobre `sum("amount")`).
- Cuando un mejor nombre lo haría innecesario: primero se renombra.
- Para historial de cambios (eso es `git log`) ni autoría.
- Código comentado: se elimina.
- Explicaciones teóricas largas: van a las diapositivas o a la documentación.

### Forma
- En inglés, frases completas, encima de lo que explican. Sin comentarios a final de línea salvo aclaraciones muy cortas.
- Un comentario desactualizado es un bug: se revisa en el mismo commit.
- `TODO`/`FIXME` solo con motivo e incidencia asociada.

### Docstrings
- Obligatorios en módulos, clases y funciones públicas.
- Estilo Google, único en todo el proyecto: resumen en una línea y, solo si aportan, `Args`, `Returns`, `Raises`. No repetir lo que dicen firma y type hints.
- Los notebooks documentan el flujo en celdas Markdown (objetivo, entradas, salidas, decisiones), no con bloques de comentarios.

### Prueba de calidad
(1) ¿Se entendería el código sin el comentario? Si sí, sobra. (2) ¿Alguien podría romper algo por no saber esto? Si sí, falta o debe ser más visible.

## Robustez

- Escrituras idempotentes (`MERGE`, checkpoints).
- Casos límite explícitos: DataFrames vacíos, primera ejecución, nulos.
- Excepciones específicas, nunca `except:` desnudo; mensajes útiles.
- Evitar `.count()` en el camino crítico, `.toPandas()` sin límite y `.collect()` sobre datos grandes.

## Formato

- 4 espacios, líneas de hasta 100 caracteres, imports ordenados (stdlib → terceros → locales).
- Formateo numérico homogéneo en f-strings.
- Linter y formateador (p. ej. `ruff`) configurados en `pyproject.toml` y ejecutados antes de cada commit.

## Objetos en Unity Catalog

- Todas las tablas con `comment` (propósito, fuente, uso) y propiedades necesarias (`delta.enableChangeDataFeed`).
- Constraints con nombres únicos y descriptivos.

## Base en la documentación de la plataforma

- Cada decisión que dependa de Databricks, MLflow o Spark debe poder respaldarse con la documentación oficial (ver `docs/referencia-databricks.md`).
- No usar APIs deprecadas ni funciones no disponibles en nuestra edición.
- Si se opta por un patrón distinto al recomendado oficialmente, se documenta el motivo en un comentario (el porqué) y en el informe de revisión.
