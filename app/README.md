# Locus (Geometra): capa web

Recomendador de cafeterías en Mérida, Yucatán. Backend FastAPI y frontend Vue 3 + TypeScript.
El backend usa el modelo calculado en `Modelado/06_Modelado.ipynb`. Ver [El modelo](#el-modelo).

## Requisitos

- Python 3.10 o superior (probado con 3.12)
- Node 18 o superior (el proyecto está fijado a Vite 5 y Tailwind 3.4 por compatibilidad con Node 18)
- Internet la primera vez que se usa el modo `text`: `sentence-transformers` descarga el modelo de texto
  (unos 470 MB) desde Hugging Face. Después queda en la caché del usuario.

## Correr en desarrollo

Backend, en `localhost:8000`:

```bash
cd app/backend
python -m venv .venv
.venv\Scripts\activate          # Windows (en macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Al arrancar carga el modelo (y el modelo de texto, unos segundos). Documentación interactiva en
http://localhost:8000/docs.

Frontend, en `localhost:5173`:

```bash
cd app/frontend
npm install
npm run dev
```

Vite redirige `/api/*` a `localhost:8000` quitando el prefijo `/api` (ver `vite.config.ts`),
por lo que en desarrollo no hay CORS. El backend igualmente permite `localhost:5173`.

Otros comandos del frontend: `npm run typecheck` (vue-tsc, TypeScript estricto) y `npm run build`.

## Estructura

```
app/
├── backend/
│   ├── main.py                     FastAPI: endpoints, esquemas, CORS y carga del modelo al arrancar
│   ├── data/recomendador.joblib    datos del modelo (salida de Modelado/06_Modelado.ipynb)
│   ├── models/recomendador.py      clase Recomendador (copia idéntica de Modelado/Modelo/recomendador.py)
│   ├── models/recommender.py       puente: carga el joblib una vez y expone recommend()
│   ├── _archivo/mock_cafeterias.py datos mock anteriores (ya no se importan)
│   └── requirements.txt
└── frontend/
    └── src/
        ├── views/        HomeView, RecomendadorView, NegociosView
        ├── components/   TarjetaCafe, MapaLeaflet, BigramaChip, BuscadorCafe, BotonContacto
        ├── assets/       logo de Geometra (horizontal y solo el hexágono, con fondo transparente)
        ├── api/client.ts cliente tipado del backend
        ├── router/       rutas: /, /recomendador, /negocios
        └── types/        interfaces TypeScript
```

## API

| Endpoint | Descripción |
|---|---|
| `GET /cafes` | Las 1,111 cafeterías recomendables (buscador del Modo A y mapa) |
| `GET /cafe/{place_id}` | Detalle de una cafetería; 404 si no existe |
| `GET /tags` | Características que se ofrecen en el panel del Modo B |
| `POST /recommend` | `{query, top_k, mode}`. `mode: "place"` usa el `place_id` como query (404 si no existe); `mode: "text"` usa las características elegidas unidas por espacios (503 si el modelo de texto no está disponible) |

Cada resultado de `/recommend` trae los campos de una cafetería más `score_similitud` (coseno ponderado
por el número de reseñas con texto, es el que ordena), `similitud_coseno` (sin ponderar) y `baja_confianza`.
`colonia` existe en el contrato pero llega nula: los datos aún no tienen colonias, y por eso el buscador y
las tarjetas muestran `direccion` (calle y colonia, sin código postal).

## El modelo

Método (sin entrenamiento ni fine tuning):

1. Cada reseña con texto se convierte en un vector de 384 dimensiones con
   `paraphrase-multilingual-MiniLM-L12-v2`.
2. El vector de una cafetería es el promedio de los de sus reseñas.
3. **Modo `place`:** coseno entre el vector de la cafetería elegida y el de las demás.
4. **Modo `text`:** el texto se embebe al vuelo, dentro de la frase "Es un lugar con ...", y se compara
   con los vectores de las cafeterías.
5. Las cafeterías con menos de 5 reseñas con texto (340 de 1,111) tienen un vector menos confiable: su
   score se multiplica por `min(1, reseñas / 5)`, así que casi no aparecen entre los primeros resultados.

Límites conocidos: la búsqueda por características funciona bien con temas frecuentes (postres, desayunos,
aire acondicionado, ambiente tranquilo) y mal con los poco frecuentes (wifi, mascotas, terraza). Los tags y
los atributos de las tarjetas son provisionales (hoy hay 20 tags). El análisis completo está en el resumen final de
`Modelado/06_Modelado.ipynb`.

### Actualizar el modelo

1. Reejecutar `Modelado/06_Modelado.ipynb`. Genera `Modelado/Modelo/recomendador.joblib`.
2. Copiar el `.joblib` a `app/backend/data/`.
3. Si cambió `Modelado/Modelo/recomendador.py`, copiarlo también a `app/backend/models/recomendador.py`
   (deben ser idénticos; `cmp` lo comprueba).
4. Reiniciar el backend. Si cambió la lista de tags, el frontend la toma de `GET /tags` sin tocar nada.

## Variables de entorno

| Variable | Dónde | Uso |
|---|---|---|
| `CORS_ORIGINS` | backend | Orígenes extra permitidos, separados por coma (ej. el dominio de Vercel) |
| `PRECARGAR_MODELO` | backend | `0` para no cargar el modelo de texto al arrancar (se cargaría en la primera búsqueda por características). Por defecto se carga |
| `RECOMENDADOR_ARTEFACTO` | backend | Ruta del `.joblib`. Por defecto `data/recomendador.joblib` |
| `RECOMENDADOR_MODELO` | backend | Ruta local del modelo de texto, para desplegar sin internet. Por defecto se descarga por nombre |
| `VITE_API_URL` | frontend | URL del backend en producción, sin barra final. Vacía en desarrollo |

## Despliegue

- Backend en Railway con `app/backend/` como raíz (comando de inicio: `uvicorn main:app --host 0.0.0.0 --port $PORT`).
  `requirements.txt` pide `torch` desde el índice de versiones CPU (en Linux, el paquete por defecto trae CUDA y
  pesa varios GB). El modo `text` necesita `torch` y el modelo de texto (unos 470 MB) en memoria: conviene medir
  memoria y tiempo de arranque en Railway antes de la demo.
- Frontend en Vercel con `app/frontend/` como raíz y `VITE_API_URL` apuntando al backend.
  Como la app usa rutas con history mode, Vercel necesita reescribir todas las rutas a `index.html`.
