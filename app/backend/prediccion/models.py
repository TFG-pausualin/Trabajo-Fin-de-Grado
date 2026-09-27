from dataclasses import dataclass
from typing import Literal


Sentimiento = Literal[
    "negativo",
    "neutral",
    "positivo",
]


@dataclass
class Prediccion:
    """
    Representa internamente el resultado de la
    clasificación de una reseña.
    """

    videojuego_id: str
    titulo: str
    texto: str
    texto_procesado: str
    sentimiento: Sentimiento
    puntuacion: int | None = None
    compra_verificada: bool = False
    imagenes: list[str] | None = None