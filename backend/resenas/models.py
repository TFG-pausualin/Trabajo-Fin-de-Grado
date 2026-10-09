from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models

from videojuegos.models import Videojuego


class Resena(models.Model):
    SENTIMIENTOS = [
        ("negativo", "Negativo"),
        ("neutral", "Neutral"),
        ("positivo", "Positivo"),
    ]

    ORIGENES = [
        ("historica", "Reseña histórica"),
        ("usuario", "Creada por un usuario"),
    ]

    videojuego = models.ForeignKey(
        Videojuego,
        on_delete=models.CASCADE,
        related_name="resenas",
        db_column="videojuego_id",
        help_text="Videojuego al que pertenece la reseña.",
    )

    titulo = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Título original de la reseña.",
    )

    texto = models.TextField(
        blank=True,
        default="",
        help_text="Contenido original de la reseña.",
    )

    texto_normalizado = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Texto normalizado utilizado para mostrar "
            "y analizar la reseña."
        ),
    )

    texto_procesado = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Texto procesado utilizado como entrada "
            "del vectorizador TF-IDF."
        ),
    )

    puntuacion = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text="Puntuación entre una y cinco estrellas.",
    )

    compra_verificada = models.BooleanField(
        default=False,
        help_text="Indica si la compra fue verificada.",
    )

    imagenes = models.JSONField(
        default=list,
        blank=True,
        help_text="URLs de imágenes asociadas a la reseña.",
    )

    usuario_original_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "Identificador del usuario en el conjunto "
            "de datos original."
        ),
    )

    fecha_original = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "Fecha de publicación en el conjunto "
            "de datos original."
        ),
    )

    sentimiento_predicho = models.CharField(
        max_length=20,
        choices=SENTIMIENTOS,
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "Sentimiento calculado por el modelo SVM."
        ),
    )

    sentimiento_real = models.CharField(
        max_length=20,
        choices=SENTIMIENTOS,
        null=True,
        blank=True,
        help_text=(
            "Etiqueta histórica o sentimiento obtenido "
            "a partir de la puntuación."
        ),
    )

    origen = models.CharField(
        max_length=20,
        choices=ORIGENES,
        default="usuario",
        db_index=True,
        help_text="Origen de la reseña.",
    )

    creada_en = models.DateTimeField(
        auto_now_add=True,
    )

    actualizada_en = models.DateTimeField(
        auto_now=True,
    )
    
    asin = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="Identificador ASIN del producto reseñado.",
    )

    votos_utiles = models.PositiveIntegerField(
        default=0,
        help_text="Número de votos útiles de la reseña.",
    )

    class Meta:
        ordering = [
            "-fecha_original",
            "-creada_en",
        ]

        verbose_name = "reseña"
        verbose_name_plural = "reseñas"

        indexes = [
            models.Index(
                fields=[
                    "videojuego",
                    "origen",
                ],
                name="resena_videojuego_origen_idx",
            ),
            models.Index(
                fields=[
                    "videojuego",
                    "sentimiento_predicho",
                ],
                name="resena_videojuego_pred_idx",
            ),
        ]

    def __str__(self):
        if self.titulo:
            return self.titulo

        return f"Reseña de {self.videojuego.titulo}"

    @property
    def sentimiento(self):
        """
        Devuelve el sentimiento que debe mostrarse.

        En las reseñas históricas se utiliza la etiqueta
        real. En las nuevas se utiliza la predicción.
        """
        return (
            self.sentimiento_predicho
            or self.sentimiento_real
        )