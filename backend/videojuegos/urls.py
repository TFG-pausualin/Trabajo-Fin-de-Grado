from rest_framework.routers import DefaultRouter

from .views import VideojuegoViewSet

router = DefaultRouter()
router.register(r"", VideojuegoViewSet, basename="videojuego")

urlpatterns = router.urls
