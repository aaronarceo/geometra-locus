"""Puente entre la API y el modelo real.

El modelo vive en `models/recomendador.py` (clase `Recomendador`, copia de
`Modelado/Modelo/recomendador.py`) y sus datos en `data/recomendador.joblib`
(salida de `Modelado/06_Modelado.ipynb`). Este módulo lo carga una sola vez y expone
`recommend()`, con la misma firma que tenía el mock.

Variables de entorno:
  RECOMENDADOR_ARTEFACTO  ruta del .joblib (por defecto data/recomendador.joblib).
  RECOMENDADOR_MODELO     ruta local del modelo de texto, para desplegar sin internet
                          (por defecto se descarga por nombre desde Hugging Face).
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from models.recomendador import Modo, PlaceNotFoundError, Recomendador

__all__ = ["Modo", "PlaceNotFoundError", "Recomendador", "get_recomendador", "recommend"]

RUTA_POR_DEFECTO = Path(__file__).resolve().parent.parent / "data" / "recomendador.joblib"


@lru_cache(maxsize=1)
def get_recomendador() -> Recomendador:
    """Carga el artefacto la primera vez y reutiliza la misma instancia después."""
    ruta = Path(os.getenv("RECOMENDADOR_ARTEFACTO") or RUTA_POR_DEFECTO)
    if not ruta.is_file():
        raise FileNotFoundError(
            f"No se encontró el artefacto del modelo en {ruta}. Se genera con "
            "Modelado/06_Modelado.ipynb y se copia a backend/data/."
        )
    return Recomendador.cargar(ruta)


def recommend(
    query: str,
    top_k: int,
    mode: Modo,
    exclude_id: Optional[str] = None,
) -> list[dict[str, object]]:
    """Devuelve las top_k cafeterías más cercanas al query.

    mode="place": query es un place_id; similitud coseno entre los vectores de las cafeterías.
    mode="text":  query es el texto de los tags elegidos, unidos por espacios; se embebe al
                  vuelo con el mismo modelo y se compara contra los vectores de las cafeterías.
    En ambos modos el score se pondera por el número de reseñas con texto.
    """
    return get_recomendador().recommend(query, top_k, mode, exclude_id)
