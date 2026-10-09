from django.db import models

from functools import lru_cache
from typing import Literal, cast

from .model_loader import cargar_artefactos
from .preprocessing import procesar_resena


Sentimiento = Literal[
    "negativo",
    "neutral",
    "positivo",
]


SENTIMIENTOS_VALIDOS = {
    "negativo",
    "neutral",
    "positivo",
}


class PrediccionService:
    """
    Servicio encargado de preprocesar, vectorizar y
    clasificar reseñas de videojuegos.
    """

    def __init__(self) -> None:
        self.vectorizador, self.modelo = cargar_artefactos()

    def predecir(
        self,
        titulo: str,
        texto: str,
    ) -> tuple[str, Sentimiento]:
        """
        Procesa y clasifica una reseña.

        Devuelve:
            - El texto procesado.
            - El sentimiento predicho por el modelo.
        """

        titulo_limpio = titulo.strip()
        texto_limpio = texto.strip()

        if not titulo_limpio:
            raise ValueError(
                "El título de la reseña no puede estar vacío."
            )

        if not texto_limpio:
            raise ValueError(
                "El texto de la reseña no puede estar vacío."
            )

        texto_procesado = procesar_resena(
            titulo=titulo_limpio,
            texto=texto_limpio,
        )

        if not texto_procesado.strip():
            raise ValueError(
                "La reseña no contiene información suficiente "
                "después del procesamiento."
            )

        matriz_tfidf = self.vectorizador.transform(
            [texto_procesado]
        )

        numero_caracteristicas = len(
            self.vectorizador.get_feature_names_out()
        )

        if matriz_tfidf.shape != (
            1,
            numero_caracteristicas,
        ):
            raise RuntimeError(
                "La matriz TF-IDF no tiene las dimensiones "
                "esperadas."
            )

        prediccion_modelo = str(
            self.modelo.predict(matriz_tfidf)[0]
        )

        if prediccion_modelo not in SENTIMIENTOS_VALIDOS:
            raise RuntimeError(
                "El modelo ha devuelto una clase desconocida: "
                f"{prediccion_modelo}."
            )

        sentimiento_predicho = cast(
            Sentimiento,
            prediccion_modelo,
        )

        return (
            texto_procesado,
            sentimiento_predicho,
        )

    @staticmethod
    def clasificar_por_puntuacion(
        puntuacion: int | None,
    ) -> Sentimiento | None:
        """
        Obtiene la etiqueta de sentimiento a partir de
        las estrellas seleccionadas por el usuario.
        """

        if puntuacion is None:
            return None

        if puntuacion < 1 or puntuacion > 5:
            raise ValueError(
                "La puntuación debe estar comprendida "
                "entre 1 y 5."
            )

        if puntuacion <= 2:
            return "negativo"

        if puntuacion == 3:
            return "neutral"

        return "positivo"


@lru_cache(maxsize=1)
def obtener_prediccion_service() -> PrediccionService:
    """
    Devuelve una instancia compartida del servicio.

    De esta forma, el vectorizador y el modelo no se
    cargan nuevamente en cada petición.
    """

    return PrediccionService()