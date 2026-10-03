from django.db import models
from django.db.models import Q
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.pagination import ApiPageNumberPagination
from .models import Videojuego
from .serializers import VideojuegoSerializer


class VideojuegoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Videojuego.objects.all().order_by("titulo")
    serializer_class = VideojuegoSerializer
    pagination_class = ApiPageNumberPagination
    lookup_field = "id"
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Videojuego.objects.all().order_by("titulo").annotate(
            _resenas_nuevas=models.Count("predicciones"),
            _valoraciones_nuevas=models.Count("predicciones__rating"),
            _suma_puntuaciones_nuevas=models.Sum("predicciones__rating"),
            _sentimientos_positivos_actuales=(
                models.F("sentimientos_positivos")
                + models.Count(
                    "predicciones",
                    filter=Q(predicciones__sentiment="positivo"),
                )
            ),
            _sentimientos_neutrales_actuales=(
                models.F("sentimientos_neutrales")
                + models.Count(
                    "predicciones",
                    filter=Q(predicciones__sentiment="neutral"),
                )
            ),
            _sentimientos_negativos_actuales=(
                models.F("sentimientos_negativos")
                + models.Count(
                    "predicciones",
                    filter=Q(predicciones__sentiment="negativo"),
                )
            ),
        ).annotate(
            _numero_valoraciones_actual=(
                models.F("numero_valoraciones")
                + models.F("_valoraciones_nuevas")
            ),
            _suma_puntuaciones_actual=models.ExpressionWrapper(
                Coalesce(
                    models.F("puntuacion_media"),
                    models.Value(0.0),
                ) * models.F("numero_valoraciones")
                + Coalesce(
                    models.F("_suma_puntuaciones_nuevas"),
                    models.Value(0.0),
                ),
                output_field=models.FloatField(),
            ),
        ).annotate(
            _etiqueta_puntuacion=models.Case(
                models.When( 
                    _numero_valoraciones_actual__gt=0,
                    _suma_puntuaciones_actual__lt=(
                        2.5 * models.F("_numero_valoraciones_actual")
                    ),
                    then=models.Value("negativo"),
                ),
                models.When( # 
                    _numero_valoraciones_actual__gt=0,
                    _suma_puntuaciones_actual__lt=(
                        3.5 * models.F("_numero_valoraciones_actual")
                    ),
                    then=models.Value("neutral"),
                ),
                models.When( # 
                    _numero_valoraciones_actual__gt=0,
                    then=models.Value("positivo"),
                ),
                default=models.Value(None),
                output_field=models.CharField(null=True),
            ),
        ).annotate(
            etiqueta_sentimiento=models.Case(
                models.When(
                    Q( # En caso de empate entre positivo y neutral, se resuelve con la puntuación media
                        _sentimientos_positivos_actuales__gt=models.F(
                            "_sentimientos_neutrales_actuales"
                        )
                    )
                    & Q(
                        _sentimientos_positivos_actuales__gt=models.F(
                            "_sentimientos_negativos_actuales"
                        )
                    ),
                    then=models.Value("positivo"),
                ),
                models.When( #En caso de empate entre positivo y neutral, se resuelve con la puntuación media
                    Q(
                        _sentimientos_neutrales_actuales__gt=models.F(
                            "_sentimientos_positivos_actuales"
                        )
                    )
                    & Q(
                        _sentimientos_neutrales_actuales__gt=models.F(
                            "_sentimientos_negativos_actuales"
                        )
                    ),
                    then=models.Value("neutral"),
                ),
                models.When( #En caso de empate entre positivo y negativo, se resuelve con la puntuación media
                    Q(
                        _sentimientos_negativos_actuales__gt=models.F(
                            "_sentimientos_positivos_actuales"
                        )
                    )
                    & Q(
                        _sentimientos_negativos_actuales__gt=models.F(
                            "_sentimientos_neutrales_actuales"
                        )
                    ),
                    then=models.Value("negativo"),
                ),
                default=models.F("_etiqueta_puntuacion"), #en caso de empate, se utiliza la etiqueta basada en la puntuación media
                output_field=models.CharField(null=True),
            ),
        )
        busqueda = self.request.query_params.get("busqueda", "").strip()
        if busqueda:
            queryset = queryset.filter(Q(titulo__icontains=busqueda) | Q(
                categoria_principal__icontains=busqueda
            ))

        etiqueta = self.request.query_params.get("etiqueta", "").strip().casefold()
        if etiqueta:
            etiqueta = {
                "negativa": "negativo",
                "positiva": "positivo",
            }.get(etiqueta, etiqueta)
            if etiqueta not in {"negativo", "neutral", "positivo"}:
                queryset = queryset.none()
            else:
                queryset = queryset.filter(etiqueta_sentimiento=etiqueta)
        return queryset

    @action(detail=False, methods=["get"], url_path="resumen")
    def resumen(self, request):
        total_videojuegos = self.get_queryset().count()
        valoracion_media = self.get_queryset().filter(puntuacion_media__isnull=False).aggregate(
            media=models.Avg("puntuacion_media")
        )["media"]

        return Response(
            {
                "total_videojuegos": total_videojuegos,
                "valoracion_media": round(valoracion_media, 2) if valoracion_media is not None else None,
            }
        )
