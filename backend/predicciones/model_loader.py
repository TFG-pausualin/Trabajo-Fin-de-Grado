from functools import lru_cache

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

from functools import lru_cache
from pathlib import Path

import joblib


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

RUTA_MODELO = (
    RAIZ_PROYECTO
    / "models"
    / "segunda_iteracion"
    / "svm"
    / "modelo_optimizado"
    / "modelo_svm_optimizado.joblib"
)

RUTA_VECTORIZADOR = (
    RAIZ_PROYECTO
    / "models"
    / "primera_iteracion"
    / "vectorizacion"
    / "vectorizador_tfidf.joblib"
)


@lru_cache(maxsize=1)
def cargar_artefactos():
    """
    Carga el vectorizador TF-IDF y el modelo SVM.
    """

    if not RUTA_MODELO.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo: {RUTA_MODELO}"
        )

    if not RUTA_VECTORIZADOR.exists():
        raise FileNotFoundError(
            "No se encontró el vectorizador: "
            f"{RUTA_VECTORIZADOR}"
        )

    vectorizador = joblib.load(
        RUTA_VECTORIZADOR
    )

    modelo = joblib.load(
        RUTA_MODELO
    )

    return vectorizador, modelo


@lru_cache(maxsize=1)
def cargar_vectorizador() -> TfidfVectorizer:

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

    modelo = joblib.load(
        RUTA_MODELO
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