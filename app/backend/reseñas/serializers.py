from typing import Literal

from pydantic import BaseModel, Field


class ResenaCreadaSerializer(BaseModel):
	videojuego_id: str = Field(min_length=1)
	titulo: str = Field(min_length=1)
	texto: str = Field(min_length=1)
	texto_procesado: str = Field(min_length=1)
	sentimiento: Literal["negativo", "neutral", "positivo"]
	puntuacion: int | None = Field(default=None, ge=1, le=5)
	compra_verificada: bool = False
	imagenes: list[str] = Field(default_factory=list)
