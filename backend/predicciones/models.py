from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from videojuegos.models import Videojuego


class Prediccion(models.Model):
    SENTIMIENTOS = [
        ("negativo", "Negativo"),
        ("neutral", "Neutral"),
        ("positivo", "Positivo"),
    ]

    videojuego = models.ForeignKey(
        Videojuego,
        on_delete=models.CASCADE,
        related_name="predicciones",
        db_column="parent_asin",
        help_text=(
            "Videojuego para el que se genera "
            "la predicción."
        ),
    )

    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text="Puntuación seleccionada entre 1 y 5.",
    )

    title = models.CharField(
        max_length=500,
        help_text="Título introducido en el formulario.",
    )

    text = models.TextField(
        help_text="Texto original introducido por el usuario.",
    )

    verified_purchase = models.BooleanField(
        default=False,
        help_text="Indica si la compra fue verificada.",
    )

    images = models.JSONField(
        default=list,
        blank=True,
        help_text="Imágenes asociadas a la opinión.",
    )

    review_text_normalized = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Título y texto combinados después "
            "de la normalización."
        ),
    )

    review_text_processed = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Texto utilizado como entrada para TF-IDF."
        ),
    )

    sentiment = models.CharField(
        max_length=20,
        choices=SENTIMIENTOS,
        help_text=(
            "Sentimiento derivado de la puntuación cuando existe; "
            "en caso contrario, generado por el modelo SVM."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "predicción"
        verbose_name_plural = "predicciones"

        indexes = [
            models.Index(
                fields=[
                    "videojuego",
                    "sentiment",
                ],
                name="predic_juego_sent_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.title} "
            f"({self.sentiment})"
        )