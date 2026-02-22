# Desarrollo y Despliegue de Soluciones *Big Data*

Este repositorio contiene la implementación de referencia para el diseño, desarrollo y despliegue de una arquitectura de datos moderna y escalable, orientada a la **detección de fraude en tarjetas de crédito**.

El proyecto está diseñado para ejecutarse en el ecosistema de **`Databricks`** (compatible con `Free Edition` y `Premium`) y aplica las mejores prácticas de ingeniería de datos y aprendizaje automático a lo largo de todo el ciclo de vida del dato.

---

## Fases del proyecto

El desarrollo de esta solución se divide en las cuatro etapas clave de un proyecto *big data* real:

- **Fase 1: Alcance y viabilidad:** Definición del caso de uso, cálculo del retorno de inversión y justificación de la arquitectura.
- **Fase 2: Preparación y gestión de datos:** Ingesta, limpieza, enriquecimiento y creación del *feature store* utilizando programación declarativa con *Delta Live Tables* y la arquitectura *Medallion*. [Ver detalles del *pipeline* aquí](./src/medallion_pipeline/README.md).
- **Fase 3: Modelado y experimentación:** Entrenamiento de modelos de aprendizaje automático con `Spark MLlib`, seguimiento de métricas y gestión del ciclo de vida del modelo mediante `MLflow`.
- **Fase 4: Despliegue y monitorización:** Puesta en producción del modelo (inferencia en *batch* y *streaming*), integración continua y monitorización de degradación (*data* y *concept drift*).

---

## Estructura general del repositorio

```text
├── .vscode/  # Configuraciones del entorno visual
├── notebooks/  # Libretas interactivas para análisis, modelado y despliegue
├── resources/  # Infraestructura como código (definiciones de clústeres, etc.)
├── src/  # Código fuente principal del proyecto
│   └── medallion_pipeline/  # Pipeline de carga, extracción y transformación
├── .gitignore  # Reglas de exclusión para el gestor de control de versiones
├── databricks.yml  # Configuración del Databricks Asset Bundle
├── LICENSE  # Información sobre la licencia del repositorio
├── pyproject.toml. # Configuración y dependencias
└── README.md  # Esta documentación principal
```

---

## Requisitos previos y configuración inicial

### 1. Espacio de trabajo

* Disponer de una cuenta activa en **`Databricks`**.
* Haber ejecutado localmente el *script* generador de datos proporcionado en la asignatura.

### 2. Clonar el repositorio

1. En la barra lateral izquierda de `Databricks`, pulsa en `Workspace`.
2. Navega hasta tu carpeta de trabajo (`Home` o `Shared`).
3. Pulsa `New` &rarr; `More` &rarr; `Git Folder`.
4. Pega la dirección de este repositorio y pulsa `Create Git folder`.

### 3. Configurar la *landing zone* (*Unity Catalog*)

Antes de ejecutar cualquier código, el entorno de ingesta debe estar preparado:

1. Ve a `Catalog` en la barra lateral.
2. Selecciona el catálogo `workspace`.
3. Crea un esquema llamado `credit_card_fraud` (o el correspondiente a tu proyecto).
4. Dentro del esquema, crea un volumen llamado `landing_zone`.
5. Entra en el volumen y pulsa `Upload to this volume`. Sube las carpetas `context`, `events` y `source_buffer` generadas localmente.

## Licencia

Este repositorio se comparte con fines educativos y de referencia. Eres libre de usar, adaptar y escalar el código como plantilla base para tus propios proyectos.