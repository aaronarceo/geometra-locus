"""Datos mock de cafeterías de Mérida, Yucatán.

Se usan mientras el modelo real (embeddings de reseñas) no está listo.
Los nombres son ficticios; las coordenadas corresponden a zonas reales de
Mérida (verificadas contra places_merida_clean.csv).

Los embeddings son vectores aleatorios de dimensión 384 (igual que
paraphrase-multilingual-MiniLM-L12-v2), con semilla fija. Para que las
similitudes tengan sentido en la demo, cada bigrama tiene un vector aleatorio
propio y el embedding de una cafetería es la suma de los vectores de sus
atributos más ruido.
"""

from typing import Literal, TypedDict

import numpy as np

EMBEDDING_DIM = 384
SEMILLA = 20260919

Sentimiento = Literal["Positivo", "Neutro", "Negativo"]

BIGRAMAS: list[str] = [
    "buen café",
    "ambiente tranquilo",
    "pet friendly",
    "buena música",
    "para trabajar",
    "postres ricos",
    "servicio amable",
    "wifi rápido",
    "espacio amplio",
    "precios justos",
]


class CafeteriaMock(TypedDict):
    place_id: str
    nombre: str
    colonia: str
    lat: float
    lon: float
    rating: float
    sentimiento: Sentimiento
    atributos: list[str]
    direccion: str
    n_resenas: int


CAFETERIAS: list[CafeteriaMock] = [
    {
        "place_id": "mock-001",
        "nombre": "Tostadora Cenote",
        "colonia": "Centro",
        "lat": 20.9674,
        "lon": -89.6237,
        "rating": 4.7,
        "sentimiento": "Positivo",
        "atributos": ["buen café", "ambiente tranquilo", "para trabajar"],
        "direccion": "Calle 60 x 57 y 59, Centro, Mérida, Yuc.",
        "n_resenas": 412,
    },
    {
        "place_id": "mock-002",
        "nombre": "Café Ceiba",
        "colonia": "Paseo de Montejo",
        "lat": 20.9905,
        "lon": -89.6152,
        "rating": 4.6,
        "sentimiento": "Positivo",
        "atributos": ["postres ricos", "servicio amable", "espacio amplio"],
        "direccion": "Paseo de Montejo x 35 y 37, Mérida, Yuc.",
        "n_resenas": 538,
    },
    {
        "place_id": "mock-003",
        "nombre": "Grano de Sol",
        "colonia": "García Ginerés",
        "lat": 20.9860,
        "lon": -89.6330,
        "rating": 4.5,
        "sentimiento": "Positivo",
        "atributos": ["buen café", "pet friendly", "buena música"],
        "direccion": "Calle 20 x 39 y 41, García Ginerés, Mérida, Yuc.",
        "n_resenas": 297,
    },
    {
        "place_id": "mock-004",
        "nombre": "Casa Xaman",
        "colonia": "Itzimná",
        "lat": 21.0000,
        "lon": -89.6060,
        "rating": 4.4,
        "sentimiento": "Positivo",
        "atributos": ["ambiente tranquilo", "para trabajar", "wifi rápido"],
        "direccion": "Calle 20 x 25 y 27, Itzimná, Mérida, Yuc.",
        "n_resenas": 186,
    },
    {
        "place_id": "mock-005",
        "nombre": "Molienda Norte",
        "colonia": "Altabrisa",
        "lat": 21.0180,
        "lon": -89.5810,
        "rating": 4.3,
        "sentimiento": "Positivo",
        "atributos": ["wifi rápido", "espacio amplio", "para trabajar"],
        "direccion": "Calle 5 x 20 y 22, Altabrisa, Mérida, Yuc.",
        "n_resenas": 254,
    },
    {
        "place_id": "mock-006",
        "nombre": "La Jícara",
        "colonia": "Santa Ana",
        "lat": 20.9700,
        "lon": -89.6130,
        "rating": 4.2,
        "sentimiento": "Neutro",
        "atributos": ["precios justos", "servicio amable", "buen café"],
        "direccion": "Calle 60 x 47 y 49, Santa Ana, Mérida, Yuc.",
        "n_resenas": 143,
    },
    {
        "place_id": "mock-007",
        "nombre": "Barra Huaya",
        "colonia": "Montebello",
        "lat": 21.0230,
        "lon": -89.6120,
        "rating": 4.5,
        "sentimiento": "Positivo",
        "atributos": ["buena música", "pet friendly", "postres ricos"],
        "direccion": "Calle 33 x 12 y 14, Montebello, Mérida, Yuc.",
        "n_resenas": 321,
    },
    {
        "place_id": "mock-008",
        "nombre": "Kuxtal Café",
        "colonia": "Francisco de Montejo",
        "lat": 21.0400,
        "lon": -89.6600,
        "rating": 4.1,
        "sentimiento": "Neutro",
        "atributos": ["espacio amplio", "pet friendly", "precios justos"],
        "direccion": "Calle 7 x 26 y 28, Francisco de Montejo, Mérida, Yuc.",
        "n_resenas": 98,
    },
    {
        "place_id": "mock-009",
        "nombre": "Café Chaya",
        "colonia": "Chuburná",
        "lat": 21.0330,
        "lon": -89.6420,
        "rating": 4.6,
        "sentimiento": "Positivo",
        "atributos": ["ambiente tranquilo", "postres ricos", "servicio amable"],
        "direccion": "Calle 21 x 14 y 16, Chuburná, Mérida, Yuc.",
        "n_resenas": 375,
    },
    {
        "place_id": "mock-010",
        "nombre": "Henequén Espresso",
        "colonia": "Montes de Amé",
        "lat": 21.0280,
        "lon": -89.6000,
        "rating": 4.4,
        "sentimiento": "Positivo",
        "atributos": ["buen café", "wifi rápido", "buena música"],
        "direccion": "Calle 11 x 8 y 10, Montes de Amé, Mérida, Yuc.",
        "n_resenas": 209,
    },
    {
        "place_id": "mock-011",
        "nombre": "Rincón del Tamarindo",
        "colonia": "Santiago",
        "lat": 20.9600,
        "lon": -89.6300,
        "rating": 3.9,
        "sentimiento": "Negativo",
        "atributos": ["precios justos", "ambiente tranquilo", "pet friendly"],
        "direccion": "Calle 70 x 57 y 59, Santiago, Mérida, Yuc.",
        "n_resenas": 76,
    },
    {
        "place_id": "mock-012",
        "nombre": "Estación Nómada",
        "colonia": "Colonia México",
        "lat": 21.0080,
        "lon": -89.6280,
        "rating": 4.2,
        "sentimiento": "Neutro",
        "atributos": ["para trabajar", "buena música", "precios justos"],
        "direccion": "Calle 27 x 16 y 18, Colonia México, Mérida, Yuc.",
        "n_resenas": 164,
    },
]


def _generar_embeddings() -> np.ndarray:
    """Matriz (n_cafeterias, 384) normalizada, aleatoria pero reproducible."""
    rng = np.random.default_rng(SEMILLA)
    base_por_bigrama = {
        bigrama: rng.standard_normal(EMBEDDING_DIM) for bigrama in BIGRAMAS
    }
    filas: list[np.ndarray] = []
    for cafe in CAFETERIAS:
        vector = sum(base_por_bigrama[a] for a in cafe["atributos"])
        vector = vector + 0.6 * rng.standard_normal(EMBEDDING_DIM)
        filas.append(vector / np.linalg.norm(vector))
    return np.vstack(filas).astype(np.float32)


EMBEDDINGS: np.ndarray = _generar_embeddings()
INDICE_POR_ID: dict[str, int] = {c["place_id"]: i for i, c in enumerate(CAFETERIAS)}
