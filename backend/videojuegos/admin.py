from django.contrib import admin

from .models import Videojuego


@admin.register(Videojuego)
class VideojuegoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo",
        "puntuacion_media",
        "numero_valoraciones",
        "categoria_principal",
        "tienda",
    )

    search_fields = (
        "id",
        "titulo",
    )

    list_filter = (
        "categoria_principal",
    )

    ordering = (
        "titulo",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 50