"""API de Locus (Geometra): recomendador de cafeterías en Mérida.

Usa el modelo real (models/recomendador.py + data/recomendador.joblib, generado en
Modelado/06_Modelado.ipynb). Las cafeterías, sus vectores y los tags salen del artefacto.

La clave del LLM (LLM_API_KEY) vivirá solo aquí, en una variable de entorno.
El mock de /explain y /chat no la usa.

Variables de entorno: CORS_ORIGINS, PRECARGAR_MODELO (0 para no cargar el modelo de texto
al arrancar), RECOMENDADOR_ARTEFACTO y RECOMENDADOR_MODELO (ver models/recommender.py).
"""

import logging
import os
import re
from contextlib import asynccontextmanager
from typing import Annotated, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StringConstraints

from models.recommender import PlaceNotFoundError, get_recomendador, recommend

logger = logging.getLogger("locus")

Sentimiento = Literal["Positivo", "Neutro", "Negativo"]
Modo = Literal["place", "text"]
TextoNoVacio = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


# --------------------------------------------------------------------------- #
# Esquemas
# --------------------------------------------------------------------------- #
class Cafeteria(BaseModel):
    place_id: str
    nombre: str
    # Dirección sin código postal ni "Mérida, Yuc., México": distingue sucursales del mismo nombre.
    direccion: str
    colonia: Optional[str] = None  # aún no hay colonias en los datos (se agregan después)
    lat: float
    lon: float
    rating: float
    sentimiento: Sentimiento
    atributos: list[str]
    # Con menos de 5 reseñas con texto el vector es poco confiable (el score ya lo pondera).
    baja_confianza: bool = False
    n_resenas_texto: int = 0


class CafeteriaDetalle(Cafeteria):
    direccion_completa: str
    n_resenas: Optional[int] = None  # total reportado por Google
    sentimiento_promedio: Optional[float] = None
    primary_type: Optional[str] = None
    price_level: Optional[str] = None
    google_maps_uri: Optional[str] = None


class Recomendacion(Cafeteria):
    score_similitud: float  # coseno ponderado por confianza: es el que ordena los resultados
    similitud_coseno: float  # coseno sin ponderar


class TagsResponse(BaseModel):
    tags: list[str]


class RecommendRequest(BaseModel):
    query: TextoNoVacio
    top_k: int = Field(default=3, ge=1, le=20)
    mode: Modo


class ExplainRequest(BaseModel):
    modo: Modo
    seleccion: str
    resultados: list[str]


class ExplainResponse(BaseModel):
    explicacion: str


class MensajeChat(BaseModel):
    rol: Literal["usuario", "asistente"]
    contenido: str


class ChatRequest(BaseModel):
    modo: Modo
    seleccion: str
    resultados: list[str]
    historial: list[MensajeChat] = Field(default_factory=list)
    pregunta: TextoNoVacio


class ChatResponse(BaseModel):
    respuesta: str


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
_COLA_DIRECCION = re.compile(r"(?:,\s*)?\d{5}\s+[^,]+,\s*Yuc\.,\s*México\s*$")
_CP_INICIAL = re.compile(r"^\d{5},\s*")


def _direccion_corta(direccion: str) -> str:
    """Quita ', 97000 Mérida, Yuc., México' del final (y un código postal suelto al inicio).

    Queda calle y colonia. Si la dirección no trae nada más (solo ciudad), se deja completa.
    """
    corta = _CP_INICIAL.sub("", _COLA_DIRECCION.sub("", direccion or "")).strip()
    return corta or (direccion or "").strip()


def _a_api(cafe: dict[str, object]) -> dict[str, object]:
    """Adapta un registro del modelo al contrato de la API."""
    completa = str(cafe.get("direccion") or "")
    return {**cafe, "direccion": _direccion_corta(completa), "direccion_completa": completa}


# --------------------------------------------------------------------------- #
# App y CORS
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(_: FastAPI):
    rec = get_recomendador()  # si falta el artefacto, el servidor no arranca (falla a la vista)
    logger.info("Modelo cargado: %d cafeterías, %d dimensiones", len(rec.place_ids), rec.dim)
    if os.getenv("PRECARGAR_MODELO", "1") != "0":
        try:
            rec.precargar_modelo()  # así la primera búsqueda por características no espera la carga
            logger.info("Modelo de texto cargado")
        except Exception:  # sin internet o sin sentence-transformers: la Función 1 sigue funcionando
            logger.exception("No se pudo cargar el modelo de texto; el modo 'text' responderá 503")
    yield


app = FastAPI(title="Locus API (Geometra)", version="0.2.0", lifespan=lifespan)

_origenes_por_defecto = ["http://localhost:5173", "http://127.0.0.1:5173"]
_origenes_extra = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origenes_por_defecto + _origenes_extra,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #
@app.get("/cafes", response_model=list[Cafeteria])
def listar_cafes() -> list[dict[str, object]]:
    """Cafeterías recomendables, para el buscador del Modo A y el mapa."""
    return [_a_api(c) for c in get_recomendador().cafes()]


@app.get("/cafe/{place_id}", response_model=CafeteriaDetalle)
def detalle_cafe(place_id: str) -> dict[str, object]:
    try:
        return _a_api(get_recomendador().detalle(place_id))
    except PlaceNotFoundError:
        raise HTTPException(status_code=404, detail=f"No existe la cafetería {place_id}")


@app.get("/tags", response_model=TagsResponse)
def listar_tags() -> dict[str, list[str]]:
    """Características que se ofrecen en el panel del Modo B."""
    return {"tags": get_recomendador().tags}


@app.post("/recommend", response_model=list[Recomendacion])
def recomendar(body: RecommendRequest) -> list[dict[str, object]]:
    """Modo place: query es un place_id. Modo text: tags seleccionados unidos por espacios."""
    try:
        # En modo place, recommend() ya excluye la cafetería de referencia.
        return [_a_api(c) for c in recommend(query=body.query, top_k=body.top_k, mode=body.mode)]
    except PlaceNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"No existe la cafetería {body.query}"
        )
    except (ImportError, OSError):
        logger.exception("El modelo de texto no está disponible")
        raise HTTPException(
            status_code=503, detail="El modelo de texto no está disponible en el servidor"
        )


def _unir(nombres: list[str]) -> str:
    if len(nombres) <= 1:
        return "".join(nombres)
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


@app.post("/explain", response_model=ExplainResponse)
def explicar(body: ExplainRequest) -> dict[str, str]:
    """Mock: texto hardcodeado. En producción llamará al LLM elegido."""
    lugares = _unir(body.resultados) or "las cafeterías mostradas"
    if body.modo == "place":
        texto = (
            f"Te recomendé {lugares} porque, según las reseñas, se parecen a "
            f"{body.seleccion} en el tipo de ambiente, el servicio y los "
            "atributos que más mencionan sus clientes. Puedes preguntarme por "
            "qué destaca cada una."
        )
    else:
        texto = (
            f"Estas cafeterías ({lugares}) aparecen porque sus reseñas se "
            f"parecen a lo que elegiste: {body.seleccion}. "
            "Puedes preguntarme cómo se comparan entre sí."
        )
    return {"explicacion": texto}


@app.post("/chat", response_model=ChatResponse)
def chatear(body: ChatRequest) -> dict[str, str]:
    """Mock: respuesta hardcodeada a preguntas de seguimiento."""
    return {
        "respuesta": (
            "Esta es una respuesta de demostración. Cuando el asistente esté "
            f"conectado, aquí se responderá tu pregunta («{body.pregunta}») "
            "usando las reseñas de las cafeterías recomendadas."
        )
    }
