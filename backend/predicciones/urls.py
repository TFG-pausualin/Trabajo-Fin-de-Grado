from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PrediccionViewSet


router = DefaultRouter()

router.register(
    r"predicciones",
    PrediccionViewSet,
    basename="prediccion",
)


urlpatterns = [
    path("", include(router.urls)),
]