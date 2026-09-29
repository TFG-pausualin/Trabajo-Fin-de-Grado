from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Raíz del proyecto:
# Trabajo-Fin-de-Grado/
RUTA_PROYECTO = Path(__file__).resolve().parents[3]

# Archivo local de variables de entorno
RUTA_ENV = (
    RUTA_PROYECTO
    / ".env"
)


class ConfiguracionBase(BaseSettings):
    # Información general
    project_name: str = Field(
        default="video-game-sentiment-analysis",
        validation_alias="PROJECT_NAME"
    )

    app_name: str = Field(
        default="API de análisis de sentimiento de videojuegos",
        validation_alias="APP_NAME"
    )
    
    database_url: str 
    
    app_version: str = Field(
        default="1.0.0",
        validation_alias="APP_VERSION"
    )

    app_debug: bool = Field(
        default=False,
        validation_alias="APP_DEBUG"
    )

    # Entorno
    app_env: str = Field(
        default="local",
        validation_alias="APP_ENV"
    )

    # Configuración del backend
    backend_host: str = Field(
        default="127.0.0.1",
        validation_alias="BACKEND_HOST"
    )

    backend_port: int = Field(
        default=8000,
        validation_alias="BACKEND_PORT"
    )

    # Configuración del frontend
    frontend_host: str = Field(
        default="localhost",
        validation_alias="FRONTEND_HOST"
    )

    frontend_port: int = Field(
        default=5173,
        validation_alias="FRONTEND_PORT"
    )

    vite_api_url: str = Field(
        default="http://127.0.0.1:8000/api",
        validation_alias="VITE_API_URL"
    )

    # CORS
    allowed_origins: str = Field(
        default=(
            "http://localhost:5173,"
            "http://127.0.0.1:5173"
        ),
        validation_alias="ALLOWED_ORIGINS"
    )
    #spaCy
    spacy_model: str = Field(
        default="en_core_web_sm",
        validation_alias="SPACY_MODEL"
    )

    # Rutas relativas de los artefactos
    tfidf_vectorizer_path: str = Field(
        default=(
            "models/primera_iteracion/vectorizacion/"
            "vectorizador_tfidf.joblib"
        ),
        validation_alias="TFIDF_VECTORIZER_PATH"
    )

    svm_model_path: str = Field(
        default=(
            "models/segunda_iteracion/svm/"
            "modelo_optimizado/"
            "modelo_svm_optimizado.joblib"
        ),
        validation_alias="SVM_MODEL_PATH"
    )

    model_config = SettingsConfigDict(
        env_file=RUTA_ENV,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def obtener_origenes(self) -> list[str]:
        """
        Convierte la variable ALLOWED_ORIGINS, separada por comas,
        en una lista de orígenes admitidos.
        """
        return [
            origen.strip()
            for origen in self.allowed_origins.split(",")
            if origen.strip()
        ]

    def obtener_ruta_vectorizador(self) -> Path:
        """
        Devuelve la ruta absoluta del vectorizador TF-IDF.
        """
        ruta = Path(self.tfidf_vectorizer_path)

        if ruta.is_absolute():
            return ruta

        return RUTA_PROYECTO / ruta

    def obtener_ruta_modelo_svm(self) -> Path:
        """
        Devuelve la ruta absoluta del modelo SVM optimizado.
        """
        ruta = Path(self.svm_model_path)

        if ruta.is_absolute():
            return ruta

        return RUTA_PROYECTO / ruta