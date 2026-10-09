from rest_framework import serializers

from .models import Videojuego


class VideojuegoSerializer(serializers.ModelSerializer):
    puntuacion_media = serializers.SerializerMethodField()
    numero_valoraciones = serializers.SerializerMethodField()
    numero_resenas = serializers.SerializerMethodField()
    etiqueta_sentimiento = serializers.CharField(read_only=True, allow_null=True)

    def get_puntuacion_media(self, videojuego):
        valoraciones_historicas = videojuego.numero_valoraciones
        valoraciones_nuevas = videojuego._valoraciones_nuevas
        total_valoraciones = valoraciones_historicas + valoraciones_nuevas
        if total_valoraciones == 0:
            return None

        suma_historica = (
            (videojuego.puntuacion_media or 0) * valoraciones_historicas
        )
        suma_nueva = videojuego._suma_puntuaciones_nuevas or 0
        return round(
            (suma_historica + suma_nueva) / total_valoraciones,
            2,
        )

    def get_numero_valoraciones(self, videojuego):
        return videojuego.numero_valoraciones + videojuego._valoraciones_nuevas

    def get_numero_resenas(self, videojuego):
        return videojuego.numero_resenas + videojuego._resenas_nuevas

    class Meta:
        model = Videojuego
        fields = [
            "id",
            "titulo",
            "puntuacion_media",
            "numero_valoraciones",
            "numero_resenas",
            "etiqueta_sentimiento",
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
            "numero_resenas",
            "etiqueta_sentimiento",
            "categoria_principal",
            "tienda",
            "detalles",
            "created_at",
            "updated_at",
        ]