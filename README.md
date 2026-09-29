# Locus

Recomendador de cafeterias en Merida, Yucatan. Proyecto final del Diplomado en Ciencia de Datos (Geometra, 2026).

Dado un lugar conocido, encuentra cafeterias similares por contenido de sus resenas. Dadas caracteristicas de texto (postres, ambiente tranquilo, desayunos), encuentra los lugares que mejor las representan. Los datos provienen de Google Maps Places API cruzados con el DENUE; el modelo usa embeddings multilingues con similitud coseno ponderada por volumen de resenas.

Los notebooks, el artefacto del modelo y el documento del proyecto se encuentran fuera de este repositorio. Este repositorio contiene unicamente la aplicacion web (backend FastAPI + frontend Vue 3 + TypeScript).

Ver [app/README.md](app/README.md) para instrucciones de instalacion y despliegue.
