from rest_framework import serializers


SENTIMIENTOS = [
    "positivo",
    "neutral",
    "negativo",
]


class DistribucionSentimientosSerializer(
    serializers.Serializer
):
    positivas = serializers.IntegerField(
        min_value=0,
    )

    neutrales = serializers.IntegerField(
        min_value=0,
    )

    negativas = serializers.IntegerField(
        min_value=0,
    )

    porcentaje_positivas = serializers.FloatField(
        min_value=0,
        max_value=100,
    )

    porcentaje_neutrales = serializers.FloatField(
        min_value=0,
        max_value=100,
    )

    porcentaje_negativas = serializers.FloatField(
        min_value=0,
        max_value=100,
    )


class MetricasGlobalesSerializer(serializers.Serializer):
    total_videojuegos = serializers.IntegerField(
        min_value=0,
    )

    total_resenas = serializers.IntegerField(
        min_value=0,
    )

    puntuacion_media_global = (
        serializers.FloatField(
            allow_null=True,
        )
    )

    percepcion_global = serializers.ChoiceField(
        choices=SENTIMIENTOS,
    )

    distribucion = (
        DistribucionSentimientosSerializer()
    )


class MetricasVideojuegoSerializer(
    serializers.Serializer
):
    videojuego_id = serializers.CharField()
    titulo = serializers.CharField()

    puntuacion_media = serializers.FloatField(
        allow_null=True,
    )

    numero_valoraciones = serializers.IntegerField(
        min_value=0,
    )

    percepcion_global = serializers.ChoiceField(
        choices=SENTIMIENTOS,
    )

    distribucion = (
        DistribucionSentimientosSerializer()
    )


class PrediccionRecienteSerializer(
    serializers.Serializer
):
    id = serializers.IntegerField()
    videojuego_id = serializers.CharField()
    videojuego_titulo = serializers.CharField()

    title = serializers.CharField()
    text = serializers.CharField()

    rating = serializers.IntegerField(
        allow_null=True,
    )

    sentiment = serializers.ChoiceField(
        choices=SENTIMIENTOS,
    )

    verified_purchase = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class ListaPrediccionesRecientesSerializer(
    serializers.Serializer
):
    total = serializers.IntegerField(
        min_value=0,
    )

    resultados = PrediccionRecienteSerializer(
        many=True,
    )