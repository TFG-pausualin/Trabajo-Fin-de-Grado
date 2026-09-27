from fastapi import APIRouter

from app.backend.videojuegos.views import router as videojuegos_views


router = APIRouter()

router.include_router(
    videojuegos_views,
    prefix="/videojuegos",
    tags=["Videojuegos"],
)