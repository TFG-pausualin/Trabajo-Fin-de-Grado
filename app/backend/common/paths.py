from pathlib import Path

from app.backend.config import configuracion
from app.backend.config.base import RUTA_PROYECTO


RUTA_DATOS = RUTA_PROYECTO / "data"
RUTA_MODELOS = RUTA_PROYECTO / "models"

RUTA_VECTORIZADOR = (
    configuracion.obtener_ruta_vectorizador()
)

RUTA_MODELO_SVM = (
    configuracion.obtener_ruta_modelo_svm()
)


def comprobar_rutas_modelos() -> None:
    archivos_requeridos: dict[str, Path] = {
        "Vectorizador TF-IDF": RUTA_VECTORIZADOR,
        "Modelo SVM optimizado": RUTA_MODELO_SVM,
    }

    archivos_no_encontrados = [
        f"{nombre}: {ruta}"
        for nombre, ruta in archivos_requeridos.items()
        if not ruta.is_file()
    ]

    if archivos_no_encontrados:
        detalle = "\n".join(
            archivos_no_encontrados
        )

        raise FileNotFoundError(
            "No se encontraron los siguientes artefactos:\n"
            f"{detalle}"
        )