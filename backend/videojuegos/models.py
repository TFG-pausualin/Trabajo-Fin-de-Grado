from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Videojuego(models.Model):
    id = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Identificador parent_asin del videojuego.",
    )

    titulo = models.CharField(
        max_length=500,
        help_text="Título del videojuego.",
    )

    puntuacion_media = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text=(
            "Puntuación media calculada a partir de "
            "las reseñas procesadas."
        ),
    )

    numero_valoraciones = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Número de reseñas procesadas disponibles "
            "para el videojuego."
        ),
    )

    categoria_principal = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Categoría principal del videojuego.",
    )

    tienda = models.TextField(
        null=True,
        blank=True,
        help_text="Tienda asociada al videojuego.",
    )

    detalles = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detalles adicionales del videojuego.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["titulo"]
        verbose_name = "videojuego"
        verbose_name_plural = "videojuegos"

    def __str__(self):
        return self.titulo