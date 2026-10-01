from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ResenaViewSet


router = DefaultRouter()

router.register(
    r"resenas",
    ResenaViewSet,
    basename="resena",
)


urlpatterns = [
    path("", include(router.urls)),
]