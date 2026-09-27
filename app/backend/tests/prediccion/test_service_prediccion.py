import pytest

from app.backend.prediccion.serializers import (
    SolicitudPrediccionSerializer,
)
from app.backend.prediccion.services import (
    PrediccionService,
)


class TestServicioPrediccion:

    @classmethod
    def setup_class(cls) -> None:
        cls.servicio = PrediccionService()

    def test_prediccion_positiva(self) -> None:
        solicitud = SolicitudPrediccionSerializer(
            videojuego_id="B001234567",
            titulo="Excellent game",
            texto=(
                "I love this game. The story is amazing "
                "and the gameplay is fantastic."
            ),
        )

        respuesta = self.servicio.predecir(
            solicitud
        )

        assert respuesta.videojuego_id == "B001234567"
        assert respuesta.sentimiento == "positivo"
        assert respuesta.texto_procesado

    def test_prediccion_negativa(self) -> None:
        solicitud = SolicitudPrediccionSerializer(
            videojuego_id="B001234567",
            titulo="Terrible game",
            texto=(
                "I do not recommend this game. "
                "It crashes constantly and the controls "
                "are awful."
            ),
        )

        respuesta = self.servicio.predecir(
            solicitud
        )

        assert respuesta.sentimiento == "negativo"
        assert "not" in respuesta.texto_procesado

    def test_sentimiento_valido(self) -> None:
        solicitud = SolicitudPrediccionSerializer(
            videojuego_id="B001234567",
            titulo="Mixed game",
            texto=(
                "The game has some good ideas but it "
                "also has several problems."
            ),
        )

        respuesta = self.servicio.predecir(
            solicitud
        )

        assert respuesta.sentimiento in {
            "negativo",
            "neutral",
            "positivo",
        }

    def test_rechazar_texto_sin_informacion(
        self,
    ) -> None:
        solicitud = SolicitudPrediccionSerializer(
            videojuego_id="B001234567",
            titulo="---",
            texto="---",
        )

        with pytest.raises(
            ValueError,
            match="no contiene información textual",
        ):
            self.servicio.predecir(
                solicitud
            )