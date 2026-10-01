from django.db import models
from django.db.models import Q
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
        queryset = Videojuego.objects.all().order_by("titulo")
        busqueda = self.request.query_params.get("busqueda", "").strip()
        if busqueda:
            coincidencias = Q(titulo__icontains=busqueda) | Q(
                categoria_principal__icontains=busqueda
            )
            etiqueta = busqueda.casefold()
            if etiqueta in {"negativo", "negativa"}:
                coincidencias |= Q(puntuacion_media__lt=2.5)
            elif etiqueta == "neutral":
                coincidencias |= Q(
                    puntuacion_media__gte=2.5,
                    puntuacion_media__lt=3.5,
                )
            elif etiqueta in {"positivo", "positiva"}:
                coincidencias |= Q(puntuacion_media__gte=3.5)
            queryset = queryset.filter(coincidencias)
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
