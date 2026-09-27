from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Videojuego:
    id: str
    titulo: str
    puntuacion_media: float | None
    numero_valoraciones: int
    categoria_principal: str | None = None
    tienda: str | None = None
    detalles: dict[str, object] = field(default_factory=dict)


@dataclass
class Resena:
    rating: int | None
    title: str | None
    text: str
    images: list[dict[str, object]]
    asin: str | None
    parent_asin: str
    user_id: str | None
    timestamp: datetime | None
    helpful_vote: int | None
    verified_purchase: bool | None
    sentimiento: str