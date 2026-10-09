from rest_framework import serializers

class ResenaSerializer(serializers.Serializer):
    id = serializers.CharField()
    videojuego = serializers.CharField()
    videojuego_titulo = serializers.CharField(allow_blank=True)
    parent_asin = serializers.CharField()
    titulo = serializers.CharField(allow_blank=True)
    texto = serializers.CharField(allow_blank=True)
    texto_normalizado = serializers.CharField(allow_blank=True)
    texto_procesado = serializers.CharField(allow_blank=True)
    puntuacion = serializers.IntegerField(allow_null=True)
    compra_verificada = serializers.BooleanField()
    imagenes = serializers.JSONField()
    usuario_original_id = serializers.CharField(
        allow_null=True,
        allow_blank=True,
    )
    fecha_original = serializers.DateTimeField(allow_null=True)
    sentimiento_predicho = serializers.CharField(allow_null=True)
    sentimiento_real = serializers.CharField(allow_null=True)
    sentimiento = serializers.CharField(allow_null=True)
    origen = serializers.CharField()
    creada_en = serializers.DateTimeField(allow_null=True)
    actualizada_en = serializers.DateTimeField(allow_null=True)
    asin = serializers.CharField(allow_null=True, allow_blank=True)
    votos_utiles = serializers.IntegerField()
    