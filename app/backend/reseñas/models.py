from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.backend.common.database import Base


class Resena(Base):
    __tablename__ = "reseñas"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    videojuego_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    titulo: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    texto: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    texto_procesado: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    puntuacion: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    compra_verificada: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    sentimiento_predicho: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    sentimiento_real: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    revisada: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "puntuacion IS NULL OR puntuacion BETWEEN 1 AND 5",
            name="ck_reseñas_puntuacion",
        ),
        CheckConstraint(
            "sentimiento_predicho IN "
            "('negativo', 'neutral', 'positivo')",
            name="ck_reseñas_sentimiento_predicho",
        ),
        CheckConstraint(
            "sentimiento_real IS NULL OR sentimiento_real IN "
            "('negativo', 'neutral', 'positivo')",
            name="ck_reseñas_sentimiento_real",
        ),
    )


@dataclass
class ResenaGuardada:
    videojuego_id: str
    titulo: str
    texto: str
    texto_procesado: str
    sentimiento: str
    puntuacion: int | None
    compra_verificada: bool
    imagenes: list[str]
    fecha: datetime