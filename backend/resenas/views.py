from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response

from config.pagination import ApiPageNumberPagination
from predicciones.models import Prediccion
from .parquet_repository import RepositorioResenasParquet
from .serializers import ResenaSerializer
from videojuegos.models import Videojuego
from .models import Resena

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

        repositorio = RepositorioResenasParquet()

        if repositorio.esta_disponible():
            resenas = repositorio.listar_por_videojuego(
                videojuego_id
            )

            videojuego_titulo = (
                Videojuego.objects
                .filter(id=videojuego_id)
                .values_list(
                    "titulo",
                    flat=True,
                )
                .first()
                or ""
            )

            for resena in resenas:
                resena["videojuego_titulo"] = (
                    videojuego_titulo
                )
        else:
            resenas = self._obtener_resenas_bd(videojuego_id)
            
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
        identificador = str(kwargs["pk"])

        if identificador.startswith("nueva:"):
            raise NotFound(
                "El detalle de esta predicción "
                "no está disponible mediante esta ruta."
            )

        if ":" in identificador:
            repositorio = (
                RepositorioResenasParquet()
            )

            if not repositorio.esta_disponible():
                raise NotFound(
                    "Los archivos Parquet no están "
                    "disponibles en este entorno."
                )

            resena = repositorio.obtener_por_id(
                identificador
            )

            if resena is None:
                raise NotFound(
                    "No se encontró la reseña "
                    "en los archivos Parquet."
                )

            videojuego_titulo = (
                Videojuego.objects
                .filter(
                    id=resena["videojuego"]
                )
                .values_list(
                    "titulo",
                    flat=True,
                )
                .first()
                or ""
            )

            resena["videojuego_titulo"] = (
                videojuego_titulo
            )

            return Response(
                self.get_serializer(resena).data
            )

        try:
            resena_id = int(identificador)
        except ValueError as error:
            raise NotFound(
                "El identificador de la reseña "
                "no es válido."
            ) from error

        try:
            resena = (
                Resena.objects
                .select_related("videojuego")
                .get(id=resena_id)
            )
        except Resena.DoesNotExist as error:
            raise NotFound(
                "No se encontró la reseña."
            ) from error

        datos = self._serializar_resena_bd(resena)

        return Response(
        self.get_serializer(datos).data
    )
    
    @staticmethod
    def _serializar_resena_bd(
        resena: Resena,
        ) -> dict:
        sentimiento = (
        resena.sentimiento_predicho
        or resena.sentimiento_real
        )

        return {
        "id": str(resena.id),
        "videojuego": str(
            resena.videojuego_id
        ),
        "videojuego_titulo": (
            resena.videojuego.titulo
        ),
        "parent_asin": str(
            resena.videojuego_id
        ),
        "titulo": resena.titulo,
        "texto": resena.texto,
        "texto_normalizado": (
            resena.texto_normalizado
        ),
        "texto_procesado": (
            resena.texto_procesado
        ),
        "puntuacion": resena.puntuacion,
        "compra_verificada": (
            resena.compra_verificada
        ),
        "imagenes": resena.imagenes,
        "usuario_original_id": (
            resena.usuario_original_id
        ),
        "fecha_original": (
            resena.fecha_original
        ),
        "sentimiento_predicho": (
            resena.sentimiento_predicho
        ),
        "sentimiento_real": (
            resena.sentimiento_real
        ),
        "sentimiento": sentimiento,
        "origen": resena.origen,
        "creada_en": resena.creada_en,
        "actualizada_en": (
            resena.actualizada_en
        ),
        "asin": resena.asin,
        "votos_utiles": (
            resena.votos_utiles
        ),
    }


    def _obtener_resenas_bd(
        self,
        videojuego_id: str,
    ) -> list:
        queryset = (
            Resena.objects
            .select_related("videojuego")
            .filter(
                videojuego_id=videojuego_id
            )
        )
    
        return [
            self._serializar_resena_bd(resena)
            for resena in queryset
        ]