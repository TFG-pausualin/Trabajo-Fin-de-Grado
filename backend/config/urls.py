from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/videojuegos/",
        include("videojuegos.urls"),
    ),

    path(
        "api/",
        include("resenas.urls"),
    ),

    path(
        "api/",
        include("predicciones.urls"),
    ),
    path(
        "",
        RedirectView.as_view(
            pattern_name="swagger-ui",
            permanent=False,
        ),
        name="inicio",
    ),
    
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
        ),
        name="swagger-ui",
    ),

    path(
        "redoc/",
        SpectacularRedocView.as_view(
            url_name="schema",
        ),
        name="redoc",
    ),
    
    path(
    "api/metricas/",
    include("metricas.urls"),
),
]