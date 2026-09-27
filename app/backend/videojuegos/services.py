import gzip
import json
from functools import lru_cache
from math import ceil
from pathlib import Path

import pandas as pd
import pyarrow.dataset as ds

from app.backend.videojuegos.models import Resena, Videojuego


RUTA_RAIZ_PROYECTO = Path(__file__).resolve().parents[3]

RUTA_METADATOS = (
    RUTA_RAIZ_PROYECTO
    / "data"
    / "raiz"
    / "meta_Video_Games.jsonl.gz"
)

RUTA_RESENAS_ETIQUETADAS = (
    RUTA_RAIZ_PROYECTO
    / "data"
    / "procesado"
    / "resenas_etiquetadas"
)

RUTA_RESENAS_ORIGINALES = (
    RUTA_RAIZ_PROYECTO
    / "data"
    / "procesado"
    / "resenas_sin_duplicados"
)


def limpiar_metadato(valor: object) -> object | None:
    if isinstance(valor, dict):
        limpio = {
            clave: valor_limpio
            for clave, valor_anidado in valor.items()
            if (valor_limpio := limpiar_metadato(valor_anidado)) is not None
        }
        return limpio or None

    if isinstance(valor, list):
        limpio = [
            valor_limpio
            for valor_anidado in valor
            if (valor_limpio := limpiar_metadato(valor_anidado)) is not None
        ]
        return limpio or None

    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None

    return valor


class VideojuegosService:
    def __init__(
        self,
        ruta_metadatos: Path = RUTA_METADATOS,
        ruta_resenas_etiquetadas: Path = RUTA_RESENAS_ETIQUETADAS,
        ruta_resenas_originales: Path = RUTA_RESENAS_ORIGINALES,
    ) -> None:
        self.ruta_metadatos = ruta_metadatos
        self.ruta_resenas_etiquetadas = ruta_resenas_etiquetadas
        self.ruta_resenas_originales = ruta_resenas_originales

    @lru_cache(maxsize=1)
    def cargar_datos(self) -> pd.DataFrame:
        if not self.ruta_metadatos.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo: {self.ruta_metadatos}"
            )

        archivos_resenas = list(
            self.ruta_resenas_etiquetadas.glob("*.parquet")
        )
        if not archivos_resenas:
            raise FileNotFoundError(
                "No se encontraron archivos Parquet en: "
                f"{self.ruta_resenas_etiquetadas}"
            )

        parent_asin_con_resenas = set(
            pd.read_parquet(
                self.ruta_resenas_etiquetadas,
                columns=["parent_asin"],
            )["parent_asin"]
            .dropna()
            .astype(str)
            .unique()
        )

        videojuegos = []
        with gzip.open(
            self.ruta_metadatos,
            mode="rt",
            encoding="utf-8",
        ) as archivo:
            for linea in archivo:
                metadatos = json.loads(linea)
                parent_asin = metadatos.get("parent_asin")
                if parent_asin not in parent_asin_con_resenas:
                    continue

                videojuegos.append(
                    {
                        "parent_asin": parent_asin,
                        "product_title": metadatos.get("title"),
                        "product_average_rating": metadatos.get(
                            "average_rating"
                        ),
                        "product_rating_number": metadatos.get(
                            "rating_number"
                        ),
                        "main_category": metadatos.get("main_category"),
                        "store": metadatos.get("store"),
                    }
                )

        datos = pd.DataFrame(
            videojuegos,
            columns=[
                "parent_asin",
                "product_title",
                "product_average_rating",
                "product_rating_number",
                "main_category",
                "store",
            ],
        )

        datos = datos.dropna(
            subset=["parent_asin", "product_title"]
        )

        datos = datos.drop_duplicates(
            subset=["parent_asin"]
        )

        datos["product_title"] = (
            datos["product_title"]
            .astype(str)
            .str.strip()
        )
        sin_titulo = datos["product_title"].eq("")
        datos.loc[sin_titulo, "product_title"] = datos.loc[
            sin_titulo,
            "parent_asin",
        ]

        return datos.sort_values(
            by="product_title",
            key=lambda columna: columna.str.casefold(),
        ).reset_index(drop=True)

    @lru_cache(maxsize=1)
    def cargar_dataset_resenas(self) -> ds.Dataset:
        if not self.ruta_resenas_etiquetadas.is_dir():
            raise FileNotFoundError(
                "No se encontró la carpeta de reseñas etiquetadas: "
                f"{self.ruta_resenas_etiquetadas}"
            )

        return ds.dataset(
            self.ruta_resenas_etiquetadas,
            format="parquet",
        )

    @lru_cache(maxsize=1)
    def cargar_dataset_resenas_originales(self) -> ds.Dataset:
        if not self.ruta_resenas_originales.is_dir():
            raise FileNotFoundError(
                "No se encontró la carpeta de reseñas originales: "
                f"{self.ruta_resenas_originales}"
            )

        return ds.dataset(
            self.ruta_resenas_originales,
            format="parquet",
        )

    @lru_cache(maxsize=128)
    def cargar_metadatos_completos(
        self,
        videojuego_id: str,
    ) -> dict[str, object] | None:
        with gzip.open(
            self.ruta_metadatos,
            mode="rt",
            encoding="utf-8",
        ) as archivo:
            for linea in archivo:
                metadatos = json.loads(linea)
                if metadatos.get("parent_asin") != videojuego_id:
                    continue

                return {
                    clave: valor_limpio
                    for clave, valor in metadatos.items()
                    if (valor_limpio := limpiar_metadato(valor)) is not None
                }

        return None

    def obtener_videojuego(
        self,
        videojuego_id: str,
    ) -> Videojuego | None:
        datos = self.cargar_datos()
        fila = datos.loc[datos["parent_asin"] == videojuego_id]
        if fila.empty:
            return None

        registro = next(fila.itertuples(index=False))
        return Videojuego(
            id=str(registro.parent_asin),
            titulo=str(registro.product_title),
            puntuacion_media=(
                None
                if pd.isna(registro.product_average_rating)
                else float(registro.product_average_rating)
            ),
            numero_valoraciones=(
                0
                if pd.isna(registro.product_rating_number)
                else int(registro.product_rating_number)
            ),
            categoria_principal=(
                None
                if pd.isna(registro.main_category)
                else str(registro.main_category)
            ),
            tienda=(
                None if pd.isna(registro.store) else str(registro.store)
            ),
            detalles=self.cargar_metadatos_completos(videojuego_id) or {},
        )

    def listar_videojuegos(
        self,
        pagina: int,
        limite: int,
        busqueda: str | None = None,
    ) -> tuple[list[Videojuego], int, int]:
        datos = self.cargar_datos()

        if busqueda and busqueda.strip():
            datos = datos[
                datos["product_title"].str.contains(
                    busqueda.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ]

        total = len(datos)
        total_paginas = ceil(total / limite) if total > 0 else 0

        inicio = (pagina - 1) * limite
        final = inicio + limite

        datos_pagina = datos.iloc[inicio:final]

        videojuegos = [
            Videojuego(
                id=str(fila.parent_asin),
                titulo=str(fila.product_title),
                puntuacion_media=(
                    None
                    if pd.isna(fila.product_average_rating)
                    else float(fila.product_average_rating)
                ),
                numero_valoraciones=(
                    0
                    if pd.isna(fila.product_rating_number)
                    else int(fila.product_rating_number)
                ),
                categoria_principal=(
                    None
                    if pd.isna(fila.main_category)
                    else str(fila.main_category)
                ),
                tienda=(
                    None
                    if pd.isna(fila.store)
                    else str(fila.store)
                ),
            )
            for fila in datos_pagina.itertuples(index=False)
        ]

        return videojuegos, total, total_paginas

    def listar_resenas(
        self,
        videojuego_id: str,
        pagina: int,
        limite: int,
    ) -> tuple[list[Resena], int, int]:
        claves_union = [
            "parent_asin",
            "rating",
            "user_id",
            "timestamp",
            "verified_purchase",
        ]
        tabla_etiquetada = self.cargar_dataset_resenas().to_table(
            columns=[*claves_union, "review_text_normalized", "sentiment"],
            filter=ds.field("parent_asin") == videojuego_id,
        )
        tabla_original = self.cargar_dataset_resenas_originales().to_table(
            columns=[
                *claves_union,
                "title",
                "text",
                "images",
                "asin",
                "helpful_vote",
            ],
            filter=ds.field("parent_asin") == videojuego_id,
        )
        datos = tabla_etiquetada.to_pandas().merge(
            tabla_original.to_pandas(),
            on=claves_union,
            how="left",
        )
        datos = datos.dropna(
            subset=["review_text_normalized", "sentiment"]
        )
        datos["text"] = datos["text"].where(
            datos["text"].notna(),
            datos["review_text_normalized"],
        )
        datos = datos.sort_values(
            by="timestamp",
            ascending=False,
            na_position="last",
        )

        total = len(datos)
        total_paginas = ceil(total / limite) if total > 0 else 0
        inicio = (pagina - 1) * limite
        datos_pagina = datos.iloc[inicio:inicio + limite]

        resenas = []
        for fila in datos_pagina.itertuples(index=False):
            imagenes = fila.images
            if hasattr(imagenes, "tolist"):
                imagenes = imagenes.tolist()
            if not isinstance(imagenes, list):
                imagenes = []

            resenas.append(
                Resena(
                    rating=(
                        None if pd.isna(fila.rating) else int(fila.rating)
                    ),
                    title=(
                        None if pd.isna(fila.title) else str(fila.title)
                    ),
                    text=str(fila.text),
                    images=[
                        imagen
                        for imagen in imagenes
                        if isinstance(imagen, dict)
                    ],
                    asin=(None if pd.isna(fila.asin) else str(fila.asin)),
                    parent_asin=str(fila.parent_asin),
                    user_id=(
                        None if pd.isna(fila.user_id) else str(fila.user_id)
                    ),
                    timestamp=(
                        None
                        if pd.isna(fila.timestamp)
                        else fila.timestamp.to_pydatetime()
                    ),
                    helpful_vote=(
                        None
                        if pd.isna(fila.helpful_vote)
                        else int(fila.helpful_vote)
                    ),
                    verified_purchase=(
                        None
                        if pd.isna(fila.verified_purchase)
                        else bool(fila.verified_purchase)
                    ),
                    sentimiento=str(fila.sentiment),
                )
            )

        return resenas, total, total_paginas


videojuegos_service = VideojuegosService()