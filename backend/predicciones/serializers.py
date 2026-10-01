from rest_framework import serializers

from .models import Prediccion
from videojuegos.models import Videojuego


class PrediccionSerializer(serializers.ModelSerializer):
    videojuego_id = serializers.PrimaryKeyRelatedField(
        source="videojuego",
        queryset=Videojuego.objects.all(),
        write_only=True,
        help_text=(
            "Identificador parent_asin del videojuego existente. "
            "El título y los demás datos del videojuego se cargan "
            "desde su registro y son de solo lectura."
        ),
    )

    videojuego = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    videojuego_titulo = serializers.CharField(
        source="videojuego.titulo",
        read_only=True,
        help_text="Título cargado automáticamente desde el videojuego.",
    )

    parent_asin = serializers.CharField(
        source="videojuego.id",
        read_only=True,
        help_text=(
            "Identificador del videojuego cargado automáticamente "
            "desde su registro."
        ),
    )

    class Meta:
        model = Prediccion

        fields = [
            "id",
            "videojuego",
            "videojuego_id",
            "videojuego_titulo",
            "parent_asin",
            "rating",
            "title",
            "text",
            "verified_purchase",
            "images",
            "review_text_normalized",
            "review_text_processed",
            "sentiment",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "review_text_normalized",
            "review_text_processed",
            "sentiment",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        title = value.strip()

        if not title:
            raise serializers.ValidationError(
                "El título no puede estar vacío."
            )

        return title

    def validate_text(self, value):
        text = value.strip()

        if not text:
            raise serializers.ValidationError(
                "El texto no puede estar vacío."
            )

        return text

    def validate_images(self, value):
        if len(value) > 10:
            raise serializers.ValidationError(
                "No se pueden añadir más de 10 imágenes."
            )

        for image in value:
            if not isinstance(image, str):
                raise serializers.ValidationError(
                    "Cada imagen debe ser una URL."
                )

            if not image.startswith(
                ("http://", "https://")
            ):
                raise serializers.ValidationError(
                    "Las imágenes deben usar URLs HTTP o HTTPS."
                )

        return value