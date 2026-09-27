from fastapi import APIRouter

from app.backend.prediccion.views import (
    router as prediccion_views,
)


router = APIRouter(
    prefix="/predicciones",
    tags=["Predicciones"],
)

router.include_router(
    prediccion_views
)