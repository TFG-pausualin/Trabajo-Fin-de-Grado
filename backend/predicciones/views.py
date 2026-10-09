from django.db import transaction
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import OpenApiExample, extend_schema

from predicciones.services import (
    PrediccionService,
    obtener_prediccion_service,
)
from .models import Prediccion
from .serializers import (
    PrediccionSerializer,
)


class PrediccionViewSet(viewsets.ModelViewSet):
    """
    Crea una reseña y determina su sentimiento usando
    la puntuación cuando está disponible.
    """

    queryset = Prediccion.objects.select_related(
        "videojuego"
    ).all()
    serializer_class = PrediccionSerializer

    @action(detail=False, methods=["post"], url_path="analizar")
    def analizar(self, request, *args, **kwargs):
        serializer_entrada = self.get_serializer(data=request.data)
        serializer_entrada.is_valid(raise_exception=True)

        try:
            resultado = self._calcular_prediccion(
                serializer_entrada.validated_data
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except (FileNotFoundError, RuntimeError) as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "review_text_processed": resultado[
                    "review_text_processed"
                ],
                "sentiment": resultado["sentiment"],
            }
        )

    @extend_schema(
        summary="Clasificar una reseña",
        description=(
            "Clasifica una reseña asociada a un videojuego existente. "
            "Si se proporciona puntuación, 1–2 estrellas se clasifican "
            "como negativas, 3 como neutral y 4–5 como positivas; sin "
            "puntuación se usa la predicción del modelo SVM. "
            "El título y el identificador del videojuego se obtienen "
            "automáticamente de su registro y no se aceptan como datos "
            "editables de la reseña."
        ),
        examples=[
            OpenApiExample(
                "Solicitud de predicción",
                value={
                    "videojuego_id": "B001234567",
                    "title": "Great game",
                    "text": "I loved the story and the gameplay.",
                    "rating": 5,
                    "verified_purchase": True,
                    "images": [
                        "https://example.com/imagen.jpg"
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                "Respuesta de predicción",
                value={
                    "id": 1,
                    "videojuego": "B001234567",
                    "videojuego_titulo": "Great game",
                    "parent_asin": "B001234567",
                    "rating": 5,
                    "title": "Great game",
                    "text": "I loved the story and the gameplay.",
                    "verified_purchase": True,
                    "images": [
                        "https://example.com/imagen.jpg"
                    ],
                    "review_text_normalized": (
                        "Great game I loved the story and the gameplay."
                    ),
                    "review_text_processed": (
                        "love story gameplay"
                    ),
                    "sentiment": "positivo",
                    "created_at": "2026-09-28T12:00:00Z",
                    "updated_at": "2026-09-28T12:00:00Z",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer_entrada = self.get_serializer(
            data=request.data
        )

        serializer_entrada.is_valid(
            raise_exception=True
        )

        datos = serializer_entrada.validated_data

        try:
            resultado = self._calcular_prediccion(datos)
        except ValueError as error:
            return Response(
                {
                    "detail": str(error),
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except (FileNotFoundError, RuntimeError) as error:
            return Response(
                {
                    "detail": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        prediccion = Prediccion.objects.create(
            videojuego=datos["videojuego"],
            title=datos["title"],
            text=datos["text"],
            rating=datos.get("rating"),
            verified_purchase=datos.get(
                "verified_purchase",
                False,
            ),
            images=datos.get(
                "images",
                [],
            ),
            **resultado,
        )

        serializer_salida = self.get_serializer(
            prediccion
        )

        return Response(
            serializer_salida.data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _calcular_prediccion(datos):
        servicio = obtener_prediccion_service()
        texto_procesado, sentimiento_predicho = servicio.predecir(
            titulo=datos["title"],
            texto=datos["text"],
        )
        sentimiento_por_puntuacion = (
            PrediccionService.clasificar_por_puntuacion(
                datos.get("rating")
            )
        )

        return {
            "review_text_normalized": (
                f"{datos['title']} {datos['text']}"
            ).strip(),
            "review_text_processed": texto_procesado,
            "sentiment": (
                sentimiento_por_puntuacion
                if sentimiento_por_puntuacion is not None
                else sentimiento_predicho
            ),
        }