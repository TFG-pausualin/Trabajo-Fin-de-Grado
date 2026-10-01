from rest_framework import serializers

from .models import Videojuego


class VideojuegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videojuego
        fields = [
            "id",
            "titulo",
            "puntuacion_media",
            "numero_valoraciones",
            "categoria_principal",
            "tienda",
            "detalles",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "titulo",
            "puntuacion_media",
            "numero_valoraciones",
            "categoria_principal",
            "tienda",
            "detalles",
            "created_at",
            "updated_at",
        ]