from django.contrib import admin

from .models import Resena


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo_mostrado",
        "videojuego",
        "puntuacion",
        "sentimiento_mostrado",
        "origen",
        "compra_verificada",
        "fecha_mostrada",
    )

    list_filter = (
        "origen",
        "sentimiento_predicho",
        "sentimiento_real",
        "puntuacion",
        "compra_verificada",
    )

    search_fields = (
        "titulo",
        "texto",
        "texto_normalizado",
        "usuario_original_id",
        "videojuego__id",
        "videojuego__titulo",
    )

    readonly_fields = (
        "texto_normalizado",
        "texto_procesado",
        "sentimiento_predicho",
        "sentimiento_real",
        "origen",
        "creada_en",
        "actualizada_en",
    )

    ordering = (
        "-creada_en",
    )

    list_select_related = (
        "videojuego",
    )

    list_per_page = 50

    fieldsets = (
        (
            "Videojuego",
            {
                "fields": (
                    "videojuego",
                )
            },
        ),
        (
            "Contenido de la reseña",
            {
                "fields": (
                    "titulo",
                    "texto",
                    "imagenes",
                )
            },
        ),
        (
            "Valoración",
            {
                "fields": (
                    "puntuacion",
                    "compra_verificada",
                )
            },
        ),
        (
            "Procesamiento y sentimiento",
            {
                "fields": (
                    "texto_normalizado",
                    "texto_procesado",
                    "sentimiento_predicho",
                    "sentimiento_real",
                    "origen",
                )
            },
        ),
        (
            "Información histórica",
            {
                "fields": (
                    "usuario_original_id",
                    "fecha_original",
                )
            },
        ),
        (
            "Información interna",
            {
                "fields": (
                    "creada_en",
                    "actualizada_en",
                )
            },
        ),
    )

    @admin.display(
        description="Título",
        ordering="titulo",
    )
    def titulo_mostrado(self, obj):
        return obj.titulo or "Sin título"

    @admin.display(
        description="Sentimiento",
    )
    def sentimiento_mostrado(self, obj):
        return (
            obj.sentimiento_predicho
            or obj.sentimiento_real
            or "Sin clasificar"
        )

    @admin.display(
        description="Fecha",
        ordering="fecha_original",
    )
    def fecha_mostrada(self, obj):
        return obj.fecha_original or obj.creada_en