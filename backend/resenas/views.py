from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response

from config.pagination import ApiPageNumberPagination
from predicciones.models import Prediccion
from .parquet_repository import RepositorioResenasParquet
from .serializers import ResenaSerializer
from videojuegos.models import Videojuego


class ResenaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = []
    serializer_class = ResenaSerializer
    pagination_class = ApiPageNumberPagination

    def _obtener_resenas(self):
        videojuego_id = self.request.query_params.get("videojuego")
        if not videojuego_id:
            raise ValidationError(
                {
                    "videojuego": (
                        "Este parámetro es obligatorio para consultar "
                        "las reseñas del archivo."
                    )
                }
            )

        try:
            resenas = RepositorioResenasParquet().listar_por_videojuego(
                videojuego_id
            )
        except FileNotFoundError as error:
            raise APIException(str(error)) from error

        videojuego_titulo = Videojuego.objects.filter(
            id=videojuego_id
        ).values_list("titulo", flat=True).first() or ""
        for resena in resenas:
            resena["videojuego_titulo"] = videojuego_titulo

        predicciones = Prediccion.objects.filter(
            videojuego_id=videojuego_id
        ).select_related("videojuego")
        resenas.extend(
            {
                "id": f"nueva:{prediccion.id}",
                "videojuego": str(prediccion.videojuego_id),
                "videojuego_titulo": prediccion.videojuego.titulo,
                "parent_asin": str(prediccion.videojuego_id),
                "titulo": prediccion.title,
                "texto": prediccion.text,
                "texto_normalizado": prediccion.review_text_normalized,
                "texto_procesado": prediccion.review_text_processed,
                "puntuacion": prediccion.rating,
                "compra_verificada": prediccion.verified_purchase,
                "imagenes": [
                    {"large": imagen}
                    for imagen in prediccion.images
                ],
                "usuario_original_id": None,
                "fecha_original": None,
                "sentimiento_predicho": None,
                "sentimiento_real": None,
                "sentimiento": prediccion.sentiment,
                "origen": "usuario",
                "creada_en": prediccion.created_at,
                "actualizada_en": prediccion.updated_at,
                "asin": None,
                "votos_utiles": 0,
            }
            for prediccion in predicciones
        )

        sentimiento = self.request.query_params.get("sentimiento")
        if sentimiento:
            resenas = [
                resena
                for resena in resenas
                if resena["sentimiento"] == sentimiento
            ]

        busqueda = self.request.query_params.get("search", "").casefold()
        if busqueda:
            campos = (
                "titulo",
                "texto",
                "usuario_original_id",
                "parent_asin",
                "videojuego_titulo",
            )
            resenas = [
                resena
                for resena in resenas
                if any(
                    busqueda in str(resena[campo] or "").casefold()
                    for campo in campos
                )
            ]

        orden = self.request.query_params.get(
            "ordering",
            "-fecha_original,-creada_en",
        )
        campos_ordenables = {
            "fecha_original",
            "puntuacion",
            "sentimiento_real",
            "sentimiento_predicho",
            "creada_en",
        }
        for campo in reversed(orden.split(",")):
            descendente = campo.startswith("-")
            nombre = campo.lstrip("-")
            if nombre not in campos_ordenables:
                continue
            resenas.sort(
                key=lambda resena: str(resena[nombre] or ""),
                reverse=descendente,
            )

        resenas.sort(
            key=lambda resena: resena["origen"] == "usuario",
            reverse=True,
        )

        return resenas

    def list(self, request, *args, **kwargs):
        resenas = self._obtener_resenas()
        pagina = self.paginate_queryset(resenas)
        serializer = self.get_serializer(pagina, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            resena = RepositorioResenasParquet().obtener_por_id(
                kwargs["pk"]
            )
        except FileNotFoundError as error:
            raise APIException(str(error)) from error

        if resena is None:
            raise NotFound("No se encontró la reseña en los archivos parquet.")

        return Response(self.get_serializer(resena).data)