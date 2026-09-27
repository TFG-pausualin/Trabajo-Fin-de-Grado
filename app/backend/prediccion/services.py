from typing import cast

from app.backend.common.model_loader import (
    cargar_artefactos,
)
from app.backend.common.preprocessing import (
    procesar_resena,
)
from app.backend.prediccion.models import (
    Prediccion,
    Sentimiento,
)
from app.backend.prediccion.serializers import (
    SolicitudPrediccionSerializer,
)


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
        self.vectorizador, self.modelo = (
            cargar_artefactos()
        )

    def predecir(
        self,
        solicitud: SolicitudPrediccionSerializer,
    ) -> Prediccion:
        """
        Genera una predicción de sentimiento para una
        reseña nueva.
        """

        texto_procesado = procesar_resena(
            titulo=solicitud.titulo,
            texto=solicitud.texto,
        )

        if not texto_procesado.strip():
            raise ValueError(
                "La reseña no contiene información "
                "suficiente después del procesamiento."
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
                "La matriz TF-IDF no tiene las "
                "dimensiones esperadas."
            )

        prediccion_modelo = str(
            self.modelo.predict(matriz_tfidf)[0]
        )

        if (
            prediccion_modelo
            not in SENTIMIENTOS_VALIDOS
        ):
            raise RuntimeError(
                "El modelo ha devuelto una clase "
                f"desconocida: {prediccion_modelo}."
            )

        sentimiento = cast(
            Sentimiento,
            prediccion_modelo,
        )

        if solicitud.puntuacion is not None:
            sentimiento = self.clasificar_por_estrellas(
                solicitud.puntuacion
            )

        # Posible regla pendiente de consultar con la tutora:
        #
        # if solicitud.puntuacion is not None:
        #     sentimiento = (
        #         self.clasificar_por_estrellas(
        #             solicitud.puntuacion
        #         )
        #     )

        return Prediccion(
            videojuego_id=solicitud.videojuego_id,
            titulo=solicitud.titulo,
            texto=solicitud.texto,
            texto_procesado=texto_procesado,
            sentimiento=sentimiento,
            puntuacion=solicitud.puntuacion,
            compra_verificada=(
                solicitud.compra_verificada
            ),
            imagenes=solicitud.imagenes,
        )

    @staticmethod
    def clasificar_por_estrellas(
        puntuacion: int,
    ) -> Sentimiento:
        """
        Clasifica el sentimiento mediante la puntuación.

        La utilización de este método queda pendiente
        de la decisión tomada con la tutora.
        """

        if puntuacion <= 2:
            return "negativo"

        if puntuacion == 3:
            return "neutral"

        return "positivo"


_prediccion_service: PrediccionService | None = None


def obtener_prediccion_service() -> PrediccionService:
    """
    Devuelve una única instancia compartida del
    servicio de predicción.
    """

    global _prediccion_service

    if _prediccion_service is None:
        _prediccion_service = PrediccionService()

    return _prediccion_service