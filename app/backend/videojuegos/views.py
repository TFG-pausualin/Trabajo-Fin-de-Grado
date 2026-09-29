from fastapi import APIRouter, HTTPException, Query, status

from app.backend.videojuegos.serializers import (
    ListaReseñasSerializer,
    ListaVideojuegosSerializer,
    ReseñaSerializer,
    VideojuegoDetalleSerializer,
    VideojuegoSerializer,
)
from app.backend.videojuegos.services import videojuegos_service


router = APIRouter()


@router.get(
    "/",
    response_model=ListaVideojuegosSerializer,
    status_code=status.HTTP_200_OK,
    summary="Listar videojuegos",
)
def listar_videojuegos(
    pagina: int = Query(
        default=1,
        ge=1,
    ),
    limite: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    busqueda: str | None = Query(
        default=None,
        max_length=100,
    ),
) -> ListaVideojuegosSerializer:
    try:
        videojuegos, total, total_paginas = (
            videojuegos_service.listar_videojuegos(
                pagina=pagina,
                limite=limite,
                busqueda=busqueda,
            )
        )

        resultados = [
            VideojuegoSerializer(
                id=videojuego.id,
                titulo=videojuego.titulo,
                puntuacion_media=videojuego.puntuacion_media,
                numero_valoraciones=videojuego.numero_valoraciones,
                categoria_principal=videojuego.categoria_principal,
                tienda=videojuego.tienda,
            )
            for videojuego in videojuegos
        ]

        return ListaVideojuegosSerializer(
            resultados=resultados,
            pagina=pagina,
            limite=limite,
            total=total,
            total_paginas=total_paginas,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.get(
    "/{videojuego_id}/reseñas",
    response_model=ListaReseñasSerializer,
    status_code=status.HTTP_200_OK,
    summary="Listar reseñas de un videojuego",
)
def listar_reseñas_videojuego(
    videojuego_id: str,
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=100),
) -> ListaReseñasSerializer:
    try:
        reseñas, total, total_paginas = (
            videojuegos_service.listar_reseñas(
                videojuego_id=videojuego_id,
                pagina=pagina,
                limite=limite,
            )
        )

        return ListaReseñasSerializer(
            resultados=[
                ReseñaSerializer(
                    rating=resena.rating,
                    title=resena.title,
                    text=resena.text,
                    images=resena.images,
                    asin=resena.asin,
                    parent_asin=resena.parent_asin,
                    user_id=resena.user_id,
                    timestamp=resena.timestamp,
                    helpful_vote=resena.helpful_vote,
                    verified_purchase=resena.verified_purchase,
                    sentimiento=resena.sentimiento,
                )
                for resena in reseñas
            ],
            pagina=pagina,
            limite=limite,
            total=total,
            total_paginas=total_paginas,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


@router.get(
    "/{videojuego_id}",
    response_model=VideojuegoDetalleSerializer,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de un videojuego",
)
def obtener_detalle_videojuego(
    videojuego_id: str,
) -> VideojuegoDetalleSerializer:
    try:
        videojuego = videojuegos_service.obtener_videojuego(videojuego_id)
        if videojuego is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró el videojuego con reseñas etiquetadas.",
            )

        return VideojuegoDetalleSerializer(
            id=videojuego.id,
            titulo=videojuego.titulo,
            puntuacion_media=videojuego.puntuacion_media,
            numero_valoraciones=videojuego.numero_valoraciones,
            categoria_principal=videojuego.categoria_principal,
            tienda=videojuego.tienda,
            detalles=videojuego.detalles,
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error
