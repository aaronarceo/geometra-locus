"""Recomendador de cafeterías de Mérida (Geometra).

Este módulo es la única fuente del código de los dos métodos de recomendación. El notebook
`06_Modelado.ipynb` lo importa para probarlo y el backend lo copia tal cual
(`app/backend/models/recomendador.py`).

El artefacto `recomendador.joblib` que carga contiene solo datos (arreglos de numpy y tipos
simples de Python), sin clases propias, así que no depende de este archivo para abrirse.

Método:
  * Cada cafetería tiene un vector de 384 dimensiones: el promedio de los embeddings de sus
    reseñas con texto (`paraphrase-multilingual-MiniLM-L12-v2`), normalizado. No hay
    entrenamiento ni ajuste fino: el modelo es preentrenado.
  * Función 1 (cafetería -> similares): coseno entre el vector de la cafetería elegida y el de
    todas las demás. Se usan los vectores centrados (`embeddings_lugar`).
  * Función 2 (palabras -> cafeterías): el texto se embebe al vuelo con el mismo modelo, dentro
    de una plantilla de frase (`plantilla_consulta`), y se compara por coseno contra los vectores
    sin centrar (`embeddings`).
  * Las cafeterías con pocas reseñas con texto tienen un vector poco confiable. Por eso el
    score que ordena los resultados es `coseno * min(1, n_resenas_texto / min_resenas_confiable)`.

Dependencias: `numpy` y `joblib`. `sentence-transformers` solo se importa la primera vez que
se usa el modo texto.
"""

from __future__ import annotations

import os
import threading
from typing import Any, Literal, Optional

import joblib
import numpy as np

Modo = Literal["place", "text"]

RUTA_MODELO_ENV = "RECOMENDADOR_MODELO"  # ruta local del modelo de texto (despliegue sin internet)


class PlaceNotFoundError(LookupError):
    """El place_id no está entre las cafeterías recomendables."""


def _normalizar(matriz: np.ndarray) -> np.ndarray:
    """Normaliza a norma 1 por filas (o un vector suelto), sin dividir entre cero."""
    matriz = np.asarray(matriz, dtype=np.float32)
    norma = np.linalg.norm(matriz, axis=-1, keepdims=True)
    return matriz / np.where(norma == 0, 1.0, norma)


class Recomendador:
    """Recomendador por similitud coseno sobre embeddings de reseñas."""

    def __init__(self, artefacto: dict[str, Any]) -> None:
        self.version: str = artefacto["version"]
        self.nombre_modelo: str = artefacto["modelo_embeddings"]
        self.dim: int = int(artefacto["dim"])
        self.embeddings: np.ndarray = np.asarray(artefacto["embeddings"], dtype=np.float32)
        self.embeddings_lugar: np.ndarray = np.asarray(artefacto["embeddings_lugar"], dtype=np.float32)
        self.plantilla_consulta: str = artefacto["plantilla_consulta"]
        self.place_ids: list[str] = list(artefacto["place_ids"])
        self.cafeterias: list[dict[str, Any]] = list(artefacto["cafeterias"])
        self.min_resenas_confiable: int = int(artefacto["min_resenas_confiable"])
        self.tags: list[str] = list(artefacto.get("tags", []))
        self.metadatos: dict[str, Any] = dict(artefacto.get("metadatos", {}))

        n_texto = np.array([c["n_resenas_texto"] for c in self.cafeterias], dtype=np.float32)
        self.confianza: np.ndarray = np.minimum(1.0, n_texto / self.min_resenas_confiable)
        self._indice: dict[str, int] = {pid: i for i, pid in enumerate(self.place_ids)}
        self._modelo_texto = None
        self._candado_modelo = threading.Lock()

        esperado = (len(self.place_ids), self.dim)
        if self.embeddings.shape != esperado or self.embeddings_lugar.shape != esperado:
            raise ValueError("Las matrices de embeddings no coinciden con place_ids y dim.")
        if "{texto}" not in self.plantilla_consulta:
            raise ValueError("plantilla_consulta debe contener {texto}.")

    # ------------------------------------------------------------------ carga
    @classmethod
    def cargar(cls, ruta: str | os.PathLike[str]) -> "Recomendador":
        """Carga el artefacto `.joblib` (solo abrir archivos propios: joblib usa pickle)."""
        return cls(joblib.load(ruta))

    # ----------------------------------------------------------- texto -> vector
    def _cargar_modelo_texto(self):
        if self._modelo_texto is None:
            with self._candado_modelo:  # varias peticiones a la vez no deben cargarlo dos veces
                if self._modelo_texto is None:
                    from sentence_transformers import SentenceTransformer  # import perezoso: pesa

                    origen = os.environ.get(RUTA_MODELO_ENV) or self.nombre_modelo
                    self._modelo_texto = SentenceTransformer(origen, device="cpu")
        return self._modelo_texto

    def precargar_modelo(self) -> None:
        """Carga el modelo de texto ahora (por ejemplo al arrancar el servidor) en vez de en la primera consulta."""
        self._cargar_modelo_texto()

    def vector_de_texto(self, texto: str) -> np.ndarray:
        """Embebe un texto con el mismo modelo que las reseñas, dentro de la plantilla de consulta."""
        texto = (texto or "").strip()
        if not texto:
            raise ValueError("El texto de la consulta no puede estar vacío.")
        frase = self.plantilla_consulta.format(texto=texto)
        return _normalizar(self._cargar_modelo_texto().encode([frase], convert_to_numpy=True)[0])

    def cosenos_por_texto(self, texto: str) -> np.ndarray:
        """Coseno (sin ponderar) entre el texto y todas las cafeterías, en el orden de `place_ids`."""
        return self.embeddings @ self.vector_de_texto(texto)

    # ---------------------------------------------------------------- ranking
    def _resultado(self, i: int, coseno: float) -> dict[str, Any]:
        c = self.cafeterias[i]
        return {
            **c,
            "similitud_coseno": round(float(coseno), 4),
            "score_similitud": round(float(coseno * self.confianza[i]), 4),
        }

    def _ranking(self, cosenos: np.ndarray, top_k: int, excluir: set[int]) -> list[dict[str, Any]]:
        if top_k < 1:
            raise ValueError("top_k debe ser al menos 1.")
        ponderado = cosenos * self.confianza  # arreglo nuevo: se puede modificar
        for i in excluir:
            ponderado[i] = -np.inf
        orden = np.argsort(-ponderado)[: min(top_k, len(self.place_ids) - len(excluir))]
        return [self._resultado(int(i), cosenos[i]) for i in orden]

    # ------------------------------------------------------ los dos métodos
    def recomendar_por_lugar(
        self, place_id: str, top_k: int = 3, exclude_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Función 1: cafeterías más parecidas a una cafetería dada."""
        if place_id not in self._indice:
            raise PlaceNotFoundError(place_id)
        i = self._indice[place_id]
        excluir = {i}
        if exclude_id is not None and exclude_id in self._indice:
            excluir.add(self._indice[exclude_id])
        cosenos = self.embeddings_lugar @ self.embeddings_lugar[i]
        return self._ranking(cosenos, top_k, excluir)

    def recomendar_por_texto(
        self, texto: str, top_k: int = 10, exclude_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Función 2: cafeterías cuyas reseñas mejor representan un texto (tags unidos por espacios)."""
        excluir = {self._indice[exclude_id]} if exclude_id in self._indice else set()
        return self._ranking(self.cosenos_por_texto(texto), top_k, excluir)

    def recommend(
        self, query: str, top_k: int, mode: Modo, exclude_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Misma firma que el `recommend()` del mock del backend."""
        if mode == "place":
            return self.recomendar_por_lugar(query, top_k, exclude_id)
        if mode == "text":
            return self.recomendar_por_texto(query, top_k, exclude_id)
        raise ValueError(f"mode debe ser 'place' o 'text', no {mode!r}")

    # -------------------------------------------------- catálogo para el backend
    def cafes(self) -> list[dict[str, Any]]:
        """Todas las cafeterías recomendables (para `/cafes` y el mapa)."""
        return [dict(c) for c in self.cafeterias]

    def detalle(self, place_id: str) -> dict[str, Any]:
        """Una cafetería (para `/cafe/{place_id}`)."""
        if place_id not in self._indice:
            raise PlaceNotFoundError(place_id)
        return dict(self.cafeterias[self._indice[place_id]])
