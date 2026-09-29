from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class VideojuegoSerializer(BaseModel):
    id: str = Field(
        description="Identificador parent_asin del videojuego"
    )

    titulo: str = Field(
        description="Título del videojuego"
    )

    puntuacion_media: float | None = Field(
        default=None,
        ge=0,
        le=5,
        description="Puntuación media del videojuego",
    )

    numero_valoraciones: int = Field(
        default=0,
        ge=0,
        description="Número de valoraciones del videojuego",
    )

    categoria_principal: str | None = Field(
        default=None,
        description="Categoría principal del videojuego",
    )

    tienda: str | None = Field(
        default=None,
        description="Tienda asociada al videojuego",
    )


class VideojuegoDetalleSerializer(VideojuegoSerializer):
    detalles: dict[str, Any]


class ListaVideojuegosSerializer(BaseModel):
    resultados: list[VideojuegoSerializer]

    pagina: int = Field(ge=1)

    limite: int = Field(ge=1)

    total: int = Field(ge=0)

    total_paginas: int = Field(ge=0)


class ReseñaSerializer(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    title: str | None = None
    text: str
    images: list[dict[str, Any]] = Field(default_factory=list)
    asin: str | None = None
    parent_asin: str
    user_id: str | None = None
    timestamp: datetime | None = None
    helpful_vote: int | None = Field(default=None, ge=0)
    verified_purchase: bool | None = None
    sentimiento: Literal["negativo", "neutral", "positivo"]


class ListaReseñasSerializer(BaseModel):
    resultados: list[ReseñaSerializer]
    pagina: int = Field(ge=1)
    limite: int = Field(ge=1)
    total: int = Field(ge=0)
    total_paginas: int = Field(ge=0)