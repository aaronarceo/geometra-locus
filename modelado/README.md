# Geometra: notebooks del Trabajo Final

Recomendador de cafeterías en Mérida, Yucatán. Aplicación web: https://geometra-locus.vercel.app

## Contenido

| Notebook                            | Qué hace                                                                                                                                           | Dónde se ejecuta | Requisitos                                                                      | Tiempo  |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------- | ------- |
| `Geometra_Notebook_Final.ipynb`     | **Notebook principal.** Contexto del sector (DENUE), limpieza de datos, análisis exploratorio, modelo de recomendación, evaluación y conclusiones. | Colab o local    | Ninguno                                                                         | ~5 min  |
| `Auxiliar_Extraccion_Lugares.ipynb` | Obtención de cafeterías con Google Places API (New). Consulta una muestra de 2 celdas.                                                             | Colab o local    | Clave propia de Places API (New); los pasos para obtenerla están en el notebook | < 1 min |
| `Auxiliar_Extraccion_Resenas.ipynb` | Extracción de reseñas de Google Maps con Selenium. Extrae una muestra de 3 cafeterías.                                                             | Solo local       | Google Chrome instalado                                                         | ~1 min  |

## Cómo ejecutar

Se requiere Python 3.10 o superior. Los notebooks se probaron en local con Python 3.12; Google Colab usa actualmente
Python 3.13.

1. Abrir el notebook en Google Colab (_Archivo > Subir notebook_) o en Jupyter o VS Code.
2. Ejecutar todas las celdas (_Entorno de ejecución > Ejecutar todas_). La primera sección instala las bibliotecas
   que falten y descarga la carpeta de datos desde Google Drive.

No se necesita modificar nada. Los notebooks de extracción corren completos aunque no tengan clave de API o se
abran en Colab: en ese caso no consultan a Google y muestran el resultado original de la misma muestra.

## Datos

Los datos están en `Datos_Geometra.zip` (26 MB), en Google Drive:
https://drive.google.com/file/d/1WM18VwFvPEIWJGDBrt8Jndqw3WjfoGgk/view

Los notebooks de extracción producen las entradas del notebook principal. Por practicidad, esas salidas completas ya
están en el zip, así que el notebook principal no depende de volver a extraer nada:

```
Extracción de lugares   →  places_malla_merida.csv  →  Notebook principal (sección 2: limpieza)
Notebook principal      →  places_merida_clean.csv  →  Extracción de reseñas
Extracción de reseñas   →  reviews_scraped.csv      →  Notebook principal (sección 4: reseñas)
```

El zip también incluye el DENUE y las AGEB urbanas recortados a Mérida, y el sentimiento y los _embeddings_ de las
reseñas ya calculados. La copia de las reseñas no incluye el nombre de las personas autoras.

## Parámetros opcionales

Están en la sección 0 de cada notebook.

| Parámetro        | Notebook   | Valor por defecto | Efecto                                                                                              |
| ---------------- | ---------- | ----------------- | --------------------------------------------------------------------------------------------------- |
| `RECALCULAR`     | Principal  | `False`           | `True` recalcula el sentimiento y los _embeddings_ (alrededor de 30 min en CPU).                    |
| `EXTRAER_TODO`   | Extracción | `False`           | `True` extrae todo: 420 celdas de la malla (con costo en la API) o 1,230 cafeterías (varias horas). |
| `INICIAR_SESION` | Reseñas    | `False`           | `True` abre Chrome para iniciar sesión en Google, por si Maps muestra pocas reseñas.                |
| `HEADLESS`       | Reseñas    | `True`            | `False` muestra la ventana de Chrome durante la extracción.                                         |

Lo que generan los notebooks se guarda en la carpeta `salidas/`; la carpeta de datos no se modifica.
