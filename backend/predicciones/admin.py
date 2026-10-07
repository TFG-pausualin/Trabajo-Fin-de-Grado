""" from django.contrib import admin

from .models import Prediccion


@admin.register(Prediccion)
class PrediccionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "videojuego",
        "rating",
        "sentiment",
        "verified_purchase",
        "created_at",
    )

    list_filter = (
        "sentiment",
        "rating",
        "verified_purchase",
        "created_at",
    )

    search_fields = (
        "title",
        "text",
        "videojuego__id",
        "videojuego__titulo",
    )

    readonly_fields = (
        "review_text_normalized",
        "review_text_processed",
        "sentiment",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "videojuego",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50 """