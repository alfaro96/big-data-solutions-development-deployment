# *Pipeline Medallion*

Este directorio contiene el código fuente correspondiente a la fase de preparación y gestión de datos del proyecto. Implementa un *pipeline* robusto utilizando *Delta Live Tables* (*DLT*) para orquestar la ingesta, limpieza y modelado de datos.

La lógica de transformación está diseñada bajo el estándar de la arquitectura *Medallion* (bronce, plata y oro) y separada de la infraestructura, lo que permite pasar de un entorno de pruebas a producción continua sin reescribir código.

---

## Arquitectura de transformación

### Capa bronce (*raw layer*)

Implementada en `01_bronze_ingestion.py`:

* Ingesta incremental mediante el *Auto Loader* de `Databricks` (`cloudFiles`).
* Almacenamiento exacto e inmutable de los archivos crudos (`.csv` y `.json`).
* Inyección automática de metadatos de auditoría (`ingestion_timestamp`, `source_file`, `_rescued_data`).

### Capa plata (*cleansed layer*)

Implementada en `02_silver_transformation.py` con el apoyo de las reglas definidas en `rules/`:

* **Calidad del dato:** Uso de decoradores `@dp.expect_all` para validar expectativas de negocio.
* **Cuarentena:** Enrutamiento de transacciones o clientes anómalos hacia tablas de cuarentena para evitar la caída del *pipeline*.
* **Gestión de históricos:** Implementación de dimensiones lentamente cambiantes (*Slowly Change Dimension* (*SCD*) Tipo 2) para el maestro de clientes utilizando la funcionalidad *AUTO CDC*.
* **Cruces en *streaming*:** Cruce de transacciones con sus etiquetas mediante técnicas de *watermarking* para gestionar la memoria de estado de forma eficiente y segura.

### Capa oro (*business & feature store layer*)

Implementada en *scripts* particionados (`03_gold_customer_aggregations.py`, `03_gold_customer_profile.py` y `03_gold_fraud_spine.py`):

* **Agregaciones**: Ventanas temporales de 1 hora, 24 horas, 7 días y 30 días para capturar el comportamiento dinámico.
* ***Feature store***: Tablas optimizadas (con *Change Data Feed* habilitado) registradas implícitamente en *Unity Catalog* mediante claves primarias y restricciones temporales.
* ***Spine***: Tabla base ancla que servirá para la ingesta de la variable objetivo y las características en tiempo real durante la fase de entrenamiento.

---

## Estructura interna

Este directorio define todo el código fuente del *pipeline*:

- `explorations/`: Libretas creadas para explorar *ad-hoc* los datos procesados por este *pipeline*.
- `rules/`: Módulo de reglas de calidad declarativas. Contiene un archivo específico para cada entidad lógica (`customers.py`, `labels.py`, `transactions.py`) y un punto de entrada global (`__init__.py`) para centralizar su importación.
- `transformations/`: Todas las definiciones de conjuntos de datos y transformaciones lógicas. Por convención, cada paso de la arquitectura se encuentra en un archivo separado.
- `utilities/`: Funciones auxiliares y módulos de `Python` utilizados en el *pipeline*.

---

## Ejecución del *pipeline*

Para comenzar a procesar los datos, dirígete a la carpeta `transformations`, donde reside el código principal.

1. En tu espacio de trabajo de `Databricks`, dirígete a **`Jobs & Pipelines`** &rarr; **`ETL pipeline`**.
2. Crea un nuevo *pipeline* marcando la opción **`Set up a source-controlled project`**.
3. Selecciona la raíz del repositorio `Git`. Esto indicará a `Databricks` que analice esta carpeta en busca de las transformaciones necesarias.
4. Pulsa el botón **`Start`**.
5. El motor de DLT leerá los archivos, construirá el grafo acíclico dirigido resolviendo las dependencias, y ejecutará el flujo completo desde el volumen inicial hasta la creación del *feature store*.