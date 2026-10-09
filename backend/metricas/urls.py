from django.urls import path

from .views import (
    MetricasGlobalesView,
    MetricasVideojuegoView,
    PrediccionesRecientesView,
)


urlpatterns = [
    path("", MetricasGlobalesView.as_view(), name="metricas-globales"),
    path(
        "videojuegos/<str:videojuego_id>/",
        MetricasVideojuegoView.as_view(),
        name="metricas-videojuego",
    ),
    path(
        "predicciones-recientes/",
        PrediccionesRecientesView.as_view(),
        name="predicciones-recientes",
    ),
]