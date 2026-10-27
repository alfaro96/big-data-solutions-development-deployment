# Prompt para generar la rúbrica de evaluación del código y repositorio

Uso: copiar en un chat para generar la rúbrica de evaluación de los proyectos de los grupos.

## Prompt

Eres un profesor universitario experto en ingeniería de datos, MLOps y buenas prácticas de desarrollo. Crea una rúbrica para valorar la calidad técnica del código fuente, la estructura del repositorio y el seguimiento del desarrollo de un proyecto big data y ML en producción sobre Databricks, desarrollado por **grupos** (redacción impersonal, sin "el estudiante").

### Reglas
- Empieza con una descripción general de 3-4 líneas (qué evalúa, cómo se estructura, cómo se aplica).
- Cuatro niveles: Excelente (4), Bien (3), Suficiente (2), Insuficiente (1).
- Celdas breves (máx. 15 palabras), concretas, medibles y diferenciadas.
- No fijes un total de puntos; la suma de pesos es libre.
- Aplicable a cualquier proyecto big data sobre Databricks.

### Bloques
1. Estructura y organización del repositorio (GitHub, carpetas, separación pipeline/notebooks/utils, `.gitignore`, dependencias, sin credenciales, convención de nombres).
2. Calidad y documentación del código (PEP 8, nombres descriptivos, docstrings, comentarios útiles, sin código comentado ni imports sin usar, modularización, utils sin efectos, configuración centralizada, DRY, magic numbers, estilo consistente).
3. Objetos de datos en Unity Catalog (nombres `capa_entidad`, columnas consistentes, `comment` en tablas, constraints, propiedades, schema vs datos).
4. Robustez (idempotencia, casos límite, excepciones específicas, mensajes, retries, antipatrones PySpark).
5. Consistencia interna (mismos nombres y config, schemas coherentes, README y memoria fieles al código).
6. README y documentación (problema, arquitectura real, setup reproducible, Markdown, diagramas).
7. Seguimiento del desarrollo (historial incremental, mensajes descriptivos, frecuencia, participación de todos, ramas).

### Al final
- Tabla de pesos con justificación breve.
- Penalizaciones automáticas (credenciales, plagio, un único commit, sin README, sin comentarios en tablas).
- Indicadores de excelencia.
- Guía de corrección (qué ficheros abrir, qué buscar, qué comandos git usar).
