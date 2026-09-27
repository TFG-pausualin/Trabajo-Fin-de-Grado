from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


Sentimiento = Literal[
    "negativo",
    "neutral",
    "positivo",
]


class SolicitudPrediccionSerializer(BaseModel):
    """
    Valida los datos enviados desde el formulario
    para clasificar una reseña nueva.
    """

    videojuego_id: str = Field(
        min_length=1,
        max_length=50,
        description=(
            "Identificador parent_asin del videojuego."
        ),
        examples=["B001234567"],
    )

    titulo: str = Field(
        min_length=1,
        max_length=300,
        description="Título de la reseña.",
        examples=["Great game"],
    )

    texto: str = Field(
        min_length=1,
        max_length=10_000,
        description=(
            "Contenido de la reseña que se desea "
            "clasificar."
        ),
        examples=[
            "I loved the story and the gameplay."
        ],
    )

    puntuacion: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description=(
            "Puntuación opcional comprendida entre "
            "una y cinco estrellas."
        ),
        examples=[5],
    )

    compra_verificada: bool = Field(
        default=False,
        description=(
            "Indica si la reseña corresponde a una "
            "compra verificada."
        ),
    )

    imagenes: list[str] = Field(
        default_factory=list,
        max_length=10,
        examples=[
            ["https://example.com/imagen.jpg"]
        ],
        description=(
            "Listado opcional de imágenes asociadas "
            "a la reseña."
        ),
    )

    @field_validator(
        "videojuego_id",
        "titulo",
        "texto",
        mode="before",
    )
    @classmethod
    def eliminar_espacios_exteriores(
        cls,
        valor: object,
    ) -> object:
        """
        Elimina espacios al principio y al final de
        los campos textuales.
        """

        if isinstance(valor, str):
            return valor.strip()

        return valor

    @field_validator("imagenes")
    @classmethod
    def comprobar_imagenes(
        cls,
        imagenes: list[str],
    ) -> list[str]:
        """
        Comprueba que las imágenes utilicen direcciones
        HTTP o HTTPS y elimina valores repetidos.
        """

        imagenes_limpias: list[str] = []

        for imagen in imagenes:
            url = imagen.strip()

            if not url:
                continue

            if not url.startswith(
                ("http://", "https://")
            ):
                raise ValueError(
                    "Las imágenes deben usar una URL "
                    "HTTP o HTTPS."
                )

            if url not in imagenes_limpias:
                imagenes_limpias.append(url)

        return imagenes_limpias


class RespuestaPrediccionSerializer(BaseModel):
    """
    Representa el resultado devuelto después de
    clasificar la reseña.
    """

    videojuego_id: str = Field(
        description=(
            "Identificador parent_asin del videojuego."
        ),
        examples=["B001234567"],
    )

    titulo: str = Field(
        description="Título original de la reseña.",
        examples=["Great game"],
    )

    texto: str = Field(
        description="Texto original de la reseña.",
    )

    texto_procesado: str = Field(
        description=(
            "Texto obtenido después de aplicar el "
            "preprocesamiento utilizado durante el "
            "entrenamiento."
        ),
    )

    sentimiento: Sentimiento = Field(
        description=(
            "Sentimiento asignado por el modelo SVM."
        ),
        examples=["positivo"],
    )

    puntuacion: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    compra_verificada: bool = False

    imagenes: list[str] = Field(
        default_factory=list,
    )