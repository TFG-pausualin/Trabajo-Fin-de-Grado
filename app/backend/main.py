from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.backend.config import configuracion
from app.backend.prediccion.services import (
    obtener_prediccion_service,
)
from app.backend.prediccion.urls import (
    router as prediccion_router,
)

from app.backend.videojuegos.urls import router as videojuegos_router


@asynccontextmanager
async def ciclo_vida(
    app: FastAPI,
) -> AsyncIterator[None]:
    """
    Carga los artefactos del modelo al iniciar la API.
    """

    obtener_prediccion_service()

    yield


app = FastAPI(
    title=configuracion.app_name,
    version=configuracion.app_version,
    debug=configuracion.app_debug,
    description=(
        "API para consultar y clasificar el sentimiento "
        "de reseñas de videojuegos."
    ),
    lifespan=ciclo_vida,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.obtener_origenes(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Estado"],
    summary="Información de la API",
)
def obtener_inicio() -> dict[str, str]:
    return {
        "proyecto": configuracion.project_name,
        "aplicacion": configuracion.app_name,
        "version": configuracion.app_version,
        "estado": "operativa",
    }


@app.get(
    "/api/health",
    tags=["Estado"],
    summary="Comprobar el estado del backend",
)
def comprobar_estado() -> dict[str, str]:
    return {
        "estado": "ok",
        "entorno": configuracion.app_env,
    }


app.include_router(
    prediccion_router,
    prefix="/api",
)

app.include_router(
    videojuegos_router,
    prefix="/api",
    tags=["Videojuegos"],
)