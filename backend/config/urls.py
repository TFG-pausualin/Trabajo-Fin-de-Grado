from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def frontend_asset(request, archivo):
    """
    Sirve los archivos CSS, JavaScript e imágenes
    generados por Vite dentro de frontend_dist/assets.
    """
    ruta = (
        Path(settings.BASE_DIR)
        / "frontend_dist"
        / "assets"
        / archivo
    )

    if not ruta.is_file():
        raise Http404(
            "No se ha encontrado el recurso solicitado."
        )

    return FileResponse(
        ruta.open("rb"),
    )


def frontend_public_file(request, archivo):
    """
    Sirve archivos públicos generados por Vite,
    como favicon.png o favicon.ico.
    """
    ruta = (
        Path(settings.BASE_DIR)
        / "frontend_dist"
        / archivo
    )

    if not ruta.is_file():
        raise Http404(
            "No se ha encontrado el archivo solicitado."
        )

    return FileResponse(
        ruta.open("rb"),
    )


urlpatterns = [
    # Administración de Django
    path(
        "admin/",
        admin.site.urls,
    ),

    # Esquema y documentación de la API
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

    # Endpoints de PlayerView
    path(
        "api/videojuegos/",
        include("videojuegos.urls"),
    ),
    path(
        "api/metricas/",
        include("metricas.urls"),
    ),
    path(
        "api/",
        include("resenas.urls"),
    ),
    path(
        "api/",
        include("predicciones.urls"),
    ),

    # Archivos generados por Vite
    path(
        "assets/<path:archivo>",
        frontend_asset,
        name="frontend-assets",
    ),

    # Archivos públicos del frontend
    path(
        "favicon.ico",
        frontend_public_file,
        {
            "archivo": "favicon.ico",
        },
        name="favicon-ico",
    ),
    path(
        "favicon.png",
        frontend_public_file,
        {
            "archivo": "favicon.png",
        },
        name="favicon-png",
    ),

    # React Single Page Application.
    # Esta ruta siempre debe ser la última.
    re_path(
        r"^(?!api/|admin/|docs/|redoc/|static/|assets/).*$",
        TemplateView.as_view(
            template_name="index.html",
        ),
        name="frontend",
    ),
]