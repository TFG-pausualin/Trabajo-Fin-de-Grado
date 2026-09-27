from functools import lru_cache

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

from app.backend.common.paths import (
    RUTA_MODELO_SVM,
    RUTA_VECTORIZADOR,
    comprobar_rutas_modelos,
)


@lru_cache(maxsize=1)
def cargar_vectorizador() -> TfidfVectorizer:
    comprobar_rutas_modelos()

    vectorizador = joblib.load(
        RUTA_VECTORIZADOR
    )

    if not isinstance(
        vectorizador,
        TfidfVectorizer
    ):
        raise TypeError(
            "El artefacto cargado no es un "
            "TfidfVectorizer."
        )

    return vectorizador


@lru_cache(maxsize=1)
def cargar_modelo_svm() -> LinearSVC:
    comprobar_rutas_modelos()

    modelo = joblib.load(
        RUTA_MODELO_SVM
    )

    if not isinstance(
        modelo,
        LinearSVC
    ):
        raise TypeError(
            "El artefacto cargado no es un modelo LinearSVC."
        )

    return modelo


def cargar_artefactos() -> tuple[
    TfidfVectorizer,
    LinearSVC
]:
    vectorizador = cargar_vectorizador()
    modelo = cargar_modelo_svm()

    if len(vectorizador.vocabulary_) != modelo.n_features_in_:
        raise ValueError(
            "El número de características del vectorizador "
            "no coincide con el esperado por el modelo."
        )

    return vectorizador, modelo