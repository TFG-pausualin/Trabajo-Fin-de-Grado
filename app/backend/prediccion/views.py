from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.backend.prediccion.serializers import (
    RespuestaPrediccionSerializer,
    SolicitudPrediccionSerializer,
)
from app.backend.prediccion.services import (
    PrediccionService,
    obtener_prediccion_service,
)


router = APIRouter()


@router.post(
    "/",
    response_model=RespuestaPrediccionSerializer,
    status_code=status.HTTP_200_OK,
    summary="Clasificar una reseña",
    description=(
        "Aplica el preprocesamiento textual, la "
        "representación TF-IDF y el modelo SVM "
        "optimizado para clasificar una reseña como "
        "negativa, neutral o positiva."
    ),
)
def predecir_sentimiento(
    solicitud: SolicitudPrediccionSerializer,
    servicio: PrediccionService = Depends(
        obtener_prediccion_service
    ),
) -> RespuestaPrediccionSerializer:
    """
    Clasifica el sentimiento de una reseña nueva.
    """

    try:
        prediccion = servicio.predecir(
            solicitud
        )

        return RespuestaPrediccionSerializer(
            videojuego_id=prediccion.videojuego_id,
            titulo=prediccion.titulo,
            texto=prediccion.texto,
            texto_procesado=(
                prediccion.texto_procesado
            ),
            sentimiento=prediccion.sentimiento,
            puntuacion=prediccion.puntuacion,
            compra_verificada=(
                prediccion.compra_verificada
            ),
            imagenes=prediccion.imagenes or [],
        )

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=str(error),
        ) from error