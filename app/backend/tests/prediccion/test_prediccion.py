import pytest

from app.backend.common.model_loader import (
    cargar_artefactos,
)
from app.backend.common.preprocessing import (
    combinar_texto,
    normalizar_texto,
    procesar_resena,
)


class TestPrediccion:
    """
    Pruebas del preprocesamiento, la vectorización
    y la predicción del modelo SVM.
    """

    @classmethod
    def setup_class(cls) -> None:
        """
        Carga una vez el vectorizador y el modelo antes
        de ejecutar las pruebas de la clase.
        """

        cls.vectorizador, cls.modelo = (
            cargar_artefactos()
        )

    def test_carga_vectorizador(self) -> None:
        assert (
            type(self.vectorizador).__name__
            == "TfidfVectorizer"
        )

        assert len(
            self.vectorizador.vocabulary_
        ) == 50_000

    def test_carga_modelo_svm(self) -> None:
        assert (
            type(self.modelo).__name__
            == "LinearSVC"
        )

        assert self.modelo.n_features_in_ == 50_000

        assert set(
            self.modelo.classes_
        ) == {
            "negativo",
            "neutral",
            "positivo",
        }

    def test_combinar_titulo_y_texto(self) -> None:
        resultado = combinar_texto(
            titulo="Great game",
            texto="I really enjoyed it.",
        )

        assert resultado == (
            "Great game I really enjoyed it."
        )

    def test_combinar_solo_texto(self) -> None:
        resultado = combinar_texto(
            titulo=None,
            texto="A very entertaining game.",
        )

        assert resultado == (
            "A very entertaining game."
        )

    def test_rechazar_resena_vacia(self) -> None:
        with pytest.raises(
            ValueError,
            match="debe contener un título o un texto",
        ):
            combinar_texto(
                titulo="",
                texto="",
            )

    def test_normalizacion_minusculas(self) -> None:
        resultado = normalizar_texto(
            "This GAME is GREAT!"
        )

        assert resultado == (
            "this game is great!"
        )

    def test_normalizacion_html(self) -> None:
        resultado = normalizar_texto(
            "<b>Excellent</b> game"
        )

        assert resultado == (
            "excellent game"
        )

    def test_normalizacion_url(self) -> None:
        resultado = normalizar_texto(
            "Visit https://example.com now"
        )

        assert resultado == (
            "visit url now"
        )

    def test_conservar_negacion_not(self) -> None:
        resultado = procesar_resena(
            titulo="",
            texto="I do not recommend this game.",
        )

        assert "not" in resultado
        assert "recommend" in resultado
        assert "game" in resultado

    def test_conservar_negacion_never(self) -> None:
        resultado = procesar_resena(
            titulo="",
            texto="I never enjoyed playing it.",
        )

        assert "never" in resultado
        assert "enjoy" in resultado
        assert "play" in resultado

    def test_lematizacion(self) -> None:
        resultado = procesar_resena(
            titulo="",
            texto="The games were entertaining.",
        )

        assert "game" in resultado
        assert "entertaining" in resultado

    def test_recuperar_emoticono_positivo(self) -> None:
        resultado = procesar_resena(
            titulo="",
            texto=":)",
        )

        assert "positivo" in resultado

    def test_recuperar_emoticono_negativo(self) -> None:
        resultado = procesar_resena(
            titulo="",
            texto=":(",
        )

        assert "negativo" in resultado

    def test_recuperar_estrellas(self) -> None:
        resultado = procesar_resena(
            titulo="",
            texto="*****",
        )

        assert (
            "estrella" in resultado
            or "estrellas" in resultado
        )

    def test_rechazar_solo_puntuacion(self) -> None:
        with pytest.raises(
            ValueError,
            match="no contiene información textual",
        ):
            procesar_resena(
                titulo="",
                texto="---",
            )

    def test_dimension_vectorizacion(self) -> None:
        texto_procesado = procesar_resena(
            titulo="Great game",
            texto=(
                "The story and gameplay were excellent."
            ),
        )

        matriz = self.vectorizador.transform(
            [texto_procesado]
        )

        assert matriz.shape == (1, 50_000)
        assert matriz.nnz > 0

    def test_prediccion_positiva(self) -> None:
        texto_procesado = procesar_resena(
            titulo="Excellent game",
            texto=(
                "I love this game. The story is amazing "
                "and the gameplay is fantastic."
            ),
        )

        matriz = self.vectorizador.transform(
            [texto_procesado]
        )

        prediccion = self.modelo.predict(
            matriz
        )[0]

        assert prediccion in {
            "negativo",
            "neutral",
            "positivo",
        }

        assert prediccion == "positivo"

    def test_prediccion_negativa(self) -> None:
        texto_procesado = procesar_resena(
            titulo="Terrible game",
            texto=(
                "I do not recommend this game. "
                "It crashes constantly and the controls "
                "are awful."
            ),
        )

        matriz = self.vectorizador.transform(
            [texto_procesado]
        )

        prediccion = self.modelo.predict(
            matriz
        )[0]

        assert prediccion in {
            "negativo",
            "neutral",
            "positivo",
        }

        assert prediccion == "negativo"