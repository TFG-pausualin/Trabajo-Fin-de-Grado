from fastapi.testclient import TestClient

from app.backend.main import app


cliente = TestClient(app)


class TestRouterPrediccion:

    def test_health(self) -> None:
        respuesta = cliente.get(
            "/api/health"
        )

        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "ok"

    def test_prediccion_valida(self) -> None:
        respuesta = cliente.post(
            "/api/predicciones/",
            json={
                "videojuego_id": "B001234567",
                "titulo": "Excellent game",
                "texto": (
                    "I love this game. The story is "
                    "amazing and the gameplay is fantastic."
                ),
            },
        )

        assert respuesta.status_code == 200

        datos = respuesta.json()

        assert datos["videojuego_id"] == "B001234567"
        assert datos["sentimiento"] in {
            "negativo",
            "neutral",
            "positivo",
        }

        assert datos["texto_procesado"]

    def test_prediccion_sin_titulo(self) -> None:
        respuesta = cliente.post(
            "/api/predicciones/",
            json={
                "videojuego_id": "B001234567",
                "texto": (
                    "This game is entertaining and fun."
                ),
            },
        )

        assert respuesta.status_code == 422

    def test_rechazar_texto_vacio(self) -> None:
        respuesta = cliente.post(
            "/api/predicciones/",
            json={
                "videojuego_id": "B001234567",
                "texto": "     ",
            },
        )

        assert respuesta.status_code == 422

    def test_rechazar_peticion_sin_texto(
        self,
    ) -> None:
        respuesta = cliente.post(
            "/api/predicciones/",
            json={
                "videojuego_id": "B001234567",
            },
        )

        assert respuesta.status_code == 422

    def test_rechazar_solo_puntuacion(
        self,
    ) -> None:
        respuesta = cliente.post(
            "/api/predicciones/",
            json={
                "videojuego_id": "B001234567",
                "texto": "---",
            },
        )

        assert respuesta.status_code == 422