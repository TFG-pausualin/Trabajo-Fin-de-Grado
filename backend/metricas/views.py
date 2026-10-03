from django.core.exceptions import (
    ObjectDoesNotExist,
)
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ListaPrediccionesRecientesSerializer,
    MetricasGlobalesSerializer,
    MetricasVideojuegoSerializer,
)
from .services import metricas_service


class MetricasGlobalesView(APIView):
    @extend_schema(
        summary="Consultar métricas globales",
        description=(
            "Devuelve el número de videojuegos, "
            "el total de reseñas etiquetadas, la "
            "puntuación media, la distribución global "
            "de sentimientos y la percepción global."
        ),
        responses={
            200: MetricasGlobalesSerializer,
        },
        tags=["Métricas"],
    )
    def get(self, request):
        try:
            datos = (
                metricas_service
                .obtener_metricas_globales()
            )

        except FileNotFoundError as error:
            return Response(
                {
                    "detail": str(error),
                },
                status=(
                    status
                    .HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        serializer = MetricasGlobalesSerializer(
            datos
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class MetricasVideojuegoView(APIView):
    @extend_schema(
        summary=(
            "Consultar las métricas de un videojuego"
        ),
        description=(
            "Devuelve la distribución de sentimientos, "
            "la puntuación media y la percepción global "
            "del videojuego indicado."
        ),
        responses={
            200: MetricasVideojuegoSerializer,
        },
        tags=["Métricas"],
    )
    def get(
        self,
        request,
        videojuego_id: str,
    ):
        try:
            datos = (
                metricas_service
                .obtener_metricas_videojuego(
                    videojuego_id=videojuego_id,
                )
            )

        except ObjectDoesNotExist:
            return Response(
                {
                    "detail": (
                        "El videojuego indicado "
                        "no existe."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except FileNotFoundError as error:
            return Response(
                {
                    "detail": str(error),
                },
                status=(
                    status
                    .HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        serializer = MetricasVideojuegoSerializer(
            datos
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class PrediccionesRecientesView(APIView):
    @extend_schema(
        summary="Consultar predicciones recientes",
        description=(
            "Devuelve las predicciones guardadas más "
            "recientemente en la aplicación."
        ),
        parameters=[
            OpenApiParameter(
                name="limite",
                type=int,
                required=False,
                description=(
                    "Número máximo de resultados. "
                    "Debe estar entre 1 y 100."
                ),
            ),
        ],
        responses={
            200: (
                ListaPrediccionesRecientesSerializer
            ),
        },
        tags=["Métricas"],
    )
    def get(self, request):
        try:
            limite = int(
                request.query_params.get(
                    "limite",
                    10,
                )
            )

        except ValueError:
            return Response(
                {
                    "detail": (
                        "El límite debe ser "
                        "un número entero."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        try:
            datos = (
                metricas_service
                .obtener_predicciones_recientes(
                    limite=limite,
                )
            )

        except ValueError as error:
            return Response(
                {
                    "detail": str(error),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        serializer = (
            ListaPrediccionesRecientesSerializer(
                datos
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )