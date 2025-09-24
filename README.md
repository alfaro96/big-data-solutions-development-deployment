# Desarrollo y Despliegue de Soluciones *Big Data*

Este repositorio proporciona ejemplos para el desarrollo y despliegue de soluciones *big data* y está preparado para ejecutarse en **`Databricks Free Edition`**. 

Hace uso de herramientas para el procesamiento de datos a gran escala, el seguimiento de experimentos, la gestión de modelos y flujos de trabajo reproducibles de aprendizaje automático.

---

## Requisitos previos

#### 1. Cuenta en `Databricks`

[Regístrate gratis](https://www.databricks.com/signup/free-edition?provider=DB_FREE_TIER&dbx_source=www&itm_data=dbx-web&l=en-EN) para obtener un espacio de trabajo listo para usar.

---

## Guía paso a paso

#### 1. Acceder al espacio de trabajo

[Inicia sesión](https://login.databricks.com/signup?dbx_source=www&itm_data=dbx-web-nav&l=en-EN&tuuid=ac0d65b0-942c-4fbb-822e-9aadd4cf8004&intent=SIGN_UP&rl_aid=916f9939-fca5-4311-8ced-7714ec26a1a5) y entra en tu **espacio de trabajo** recién creado. Si vienes de `Community Edition`, verás que ahora aparece como **`Free Edition`**.

#### 2. Clonar este repositorio

1. Pulsa `Workspace` en la barra lateral.
2. Selecciona tu carpeta `Home`.
2. Pulsa `New` &rarr; `More` &rarr; `Git Folder` en la barra lateral.
3. Pega la dirección de este repositorio en `Git repository URL`.
4. Escribe `Fraude Detection` en `Git folder name`.
5. Confima con `Create Git folder`.

> **Nota**: si trabajas en un proyecto compartido, lo recomendable es clonar el repositorio en la carpeta `Shared` dentro de `Workspace`. De esta manera, los miembros del equipo con acceso podrán colaborar sobre el mismo código y libretas sin duplicarlos en carpetas personales y sin tener que configurar permisos adicionales.

#### 3. Ejecutar libretas

1. Abre la libreta deseada.

2. Actualiza la versión del entorno:  
   1. En la barra lateral derecha, pulsa en `Environment`.  
   2. Dentro del panel, ve a la sección `Environment version`.  
   3. En el desplegable, cambia la versión de `2` a `4`.  

3. Instala las dependencias:
    1. En la barra lateral derecha, pulsa en `Environment`.
    2. Dentro del panel, ve a la sección `Dependencies` y selecciona `Added`.
    3. Pulsa el icono con forma de carpeta y busca `Fraude Detection` &rarr; `requirements.txt`.
    4. Selecciona el archivo y confirma con `Select`.

4. En la parte inferior, pulsa en `Apply` y después en `Confirm` en la ventana emergente.

## Estructura del repositorio

* `.gitignore`: reglas de exclusión
* `LICENSE`: información sobre la licencia del repositorio
* `README.md`: documentación del proyecto
* `requirements.txt`: dependencias para instalación con `pip`

---

## Licencia

Este repositorio se comparte con fines educativos y de referencia. Eres libre de usar y adaptar el código para tus propios proyectos.
