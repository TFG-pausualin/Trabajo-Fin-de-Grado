from pathlib import Path
from typing import Any

import pandas as pd
from django.conf import settings


CAMPOS_ORIGINALES = [
    "rating",
    "title",
    "text",
    "images",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
]

CAMPOS_ETIQUETADOS = [
    "rating",
    "parent_asin",
    "user_id",
    "timestamp",
    "verified_purchase",
    "review_text_normalized",
    "review_text_processed",
    "sentiment",
]

CAMPOS_IDENTIDAD = [
    "parent_asin",
    "user_id",
    "timestamp",
    "rating",
    "verified_purchase",
]


class RepositorioResenasParquet:
    def __init__(self, directorio_procesado: Path | None = None) -> None:
        self.directorio_procesado = (
            directorio_procesado
            or settings.BASE_DIR.parent / "data" / "procesado"
        )
        self.directorio_originales = (
            self.directorio_procesado / "resenas_sin_duplicados"
        )
        self.directorio_etiquetadas = (
            self.directorio_procesado / "resenas_etiquetadas"
        )

    def listar_por_videojuego(
        self,
        parent_asin: str,
    ) -> list[dict[str, Any]]:
        if not self.directorio_originales.is_dir():
            raise FileNotFoundError(
                f"No existe el directorio de reseñas originales: "
                f"{self.directorio_originales}"
            )

        if not self.directorio_etiquetadas.is_dir():
            raise FileNotFoundError(
                f"No existe el directorio de reseñas etiquetadas: "
                f"{self.directorio_etiquetadas}"
            )

        resenas: list[dict[str, Any]] = []

        for archivo_etiquetado in sorted(
            self.directorio_etiquetadas.glob(
                "resenas_etiquetadas_*.parquet"
            )
        ):
            bloque = archivo_etiquetado.stem.removeprefix(
                "resenas_etiquetadas_"
            )
            archivo_original = (
                self.directorio_originales
                / f"resenas_sin_duplicados_{bloque}.parquet"
            )

            if not archivo_original.is_file():
                raise FileNotFoundError(
                    "Falta el bloque original correspondiente a "
                    f"{archivo_etiquetado.name}."
                )

            parent_asins_etiquetados = pd.read_parquet(
                archivo_etiquetado,
                columns=["parent_asin"],
            )["parent_asin"]
            if not parent_asins_etiquetados.astype(str).eq(
                parent_asin
            ).any():
                continue

            originales = pd.read_parquet(
                archivo_original,
                columns=CAMPOS_ORIGINALES,
            )
            etiquetadas = pd.read_parquet(
                archivo_etiquetado,
                columns=CAMPOS_ETIQUETADOS,
            )

            originales["__fila_original"] = originales.index
            originales = originales.loc[
                originales["parent_asin"].astype(str).eq(parent_asin)
            ].copy()
            etiquetadas = etiquetadas.loc[
                etiquetadas["parent_asin"].astype(str).eq(parent_asin)
            ].copy()

            if etiquetadas.empty:
                continue

            originales["__identidad"] = self._identidades(originales)
            etiquetadas["__identidad"] = self._identidades(etiquetadas)
            originales["__ocurrencia"] = originales.groupby(
                "__identidad",
                sort=False,
            ).cumcount()
            etiquetadas["__ocurrencia"] = etiquetadas.groupby(
                "__identidad",
                sort=False,
            ).cumcount()

            datos_etiquetados = etiquetadas[
                [
                    "__identidad",
                    "__ocurrencia",
                    "review_text_normalized",
                    "review_text_processed",
                    "sentiment",
                ]
            ]
            unidas = originales.merge(
                datos_etiquetados,
                on=["__identidad", "__ocurrencia"],
                how="inner",
                validate="one_to_one",
            )

            if len(unidas) != len(etiquetadas):
                raise RuntimeError(
                    "No se pudieron emparejar todas las reseñas del "
                    f"bloque {bloque} para {parent_asin}."
                )

            for fila in unidas.to_dict(orient="records"):
                resenas.append(
                    self._serializar_fila(
                        fila=fila,
                        parent_asin=parent_asin,
                        bloque=bloque,
                    )
                )

        resenas.sort(
            key=lambda resena: (
                resena["fecha_original"].isoformat()
                if resena["fecha_original"] is not None
                else ""
            ),
            reverse=True,
        )
        return resenas

    def obtener_por_id(self, identificador: str) -> dict[str, Any] | None:
        try:
            bloque, fila = identificador.split(":", maxsplit=1)
            numero_fila = int(fila)
        except (ValueError, TypeError):
            return None

        if len(bloque) != 4 or not bloque.isdigit() or numero_fila < 0:
            return None

        archivo_original = (
            self.directorio_originales
            / f"resenas_sin_duplicados_{bloque}.parquet"
        )
        if not archivo_original.is_file():
            return None

        parent_asin = pd.read_parquet(
            archivo_original,
            columns=["parent_asin"],
        )["parent_asin"]
        if numero_fila >= len(parent_asin):
            return None

        valor = parent_asin.iloc[numero_fila]
        if pd.isna(valor):
            return None

        return next(
            (
                resena
                for resena in self.listar_por_videojuego(str(valor))
                if resena["id"] == identificador
            ),
            None,
        )

    @staticmethod
    def _identidades(filas: pd.DataFrame) -> pd.Series:
        return filas[CAMPOS_IDENTIDAD].apply(
            lambda fila: tuple(
                RepositorioResenasParquet._normalizar_clave(valor)
                for valor in fila
            ),
            axis=1,
        )

    @staticmethod
    def _normalizar_clave(valor: Any) -> str:
        if valor is None:
            return ""

        try:
            if pd.isna(valor):
                return ""
        except (TypeError, ValueError):
            pass

        if isinstance(valor, pd.Timestamp):
            return valor.isoformat()
        if isinstance(valor, float) and valor.is_integer():
            return str(int(valor))
        return str(valor)

    @classmethod
    def _serializar_fila(
        cls,
        fila: dict[str, Any],
        parent_asin: str,
        bloque: str,
    ) -> dict[str, Any]:
        fecha = cls._normalizar_fecha(fila["timestamp"])
        sentimiento = cls._normalizar_texto(fila["sentiment"])
        return {
            "id": f"{bloque}:{int(fila['__fila_original'])}",
            "videojuego": parent_asin,
            "videojuego_titulo": "",
            "parent_asin": parent_asin,
            "titulo": cls._normalizar_texto(fila["title"]),
            "texto": cls._normalizar_texto(fila["text"]),
            "texto_normalizado": cls._normalizar_texto(
                fila["review_text_normalized"]
            ),
            "texto_procesado": cls._normalizar_texto(
                fila["review_text_processed"]
            ),
            "puntuacion": cls._normalizar_entero(fila["rating"]),
            "compra_verificada": bool(fila["verified_purchase"]),
            "imagenes": cls._normalizar_imagenes(fila["images"]),
            "usuario_original_id": cls._normalizar_opcional_texto(
                fila["user_id"]
            ),
            "fecha_original": fecha,
            "sentimiento_predicho": None,
            "sentimiento_real": sentimiento,
            "sentimiento": sentimiento,
            "origen": "historica",
            "creada_en": fecha,
            "actualizada_en": fecha,
            "asin": cls._normalizar_opcional_texto(fila["asin"]),
            "votos_utiles": cls._normalizar_entero(
                fila["helpful_vote"]
            ) or 0,
        }

    @staticmethod
    def _normalizar_texto(valor: Any) -> str:
        if valor is None:
            return ""
        try:
            if pd.isna(valor):
                return ""
        except (TypeError, ValueError):
            pass
        return str(valor).strip()

    @classmethod
    def _normalizar_opcional_texto(cls, valor: Any) -> str | None:
        texto = cls._normalizar_texto(valor)
        return texto or None

    @staticmethod
    def _normalizar_entero(valor: Any) -> int | None:
        if valor is None:
            return None
        try:
            if pd.isna(valor):
                return None
        except (TypeError, ValueError):
            pass
        return int(valor)

    @staticmethod
    def _normalizar_fecha(valor: Any) -> Any:
        if valor is None:
            return None
        try:
            if pd.isna(valor):
                return None
        except (TypeError, ValueError):
            pass
        if isinstance(valor, pd.Timestamp):
            return valor.to_pydatetime()
        return valor

    @classmethod
    def _normalizar_imagenes(cls, valor: Any) -> list[Any]:
        if valor is None:
            return []
        if isinstance(valor, (list, tuple)):
            return [cls._normalizar_json(imagen) for imagen in valor]
        try:
            if pd.isna(valor):
                return []
        except (TypeError, ValueError):
            pass
        if hasattr(valor, "tolist"):
            return cls._normalizar_imagenes(valor.tolist())
        return []

    @classmethod
    def _normalizar_json(cls, valor: Any) -> Any:
        if isinstance(valor, dict):
            return {
                str(clave): cls._normalizar_json(contenido)
                for clave, contenido in valor.items()
            }
        if isinstance(valor, (list, tuple)):
            return [cls._normalizar_json(contenido) for contenido in valor]
        if hasattr(valor, "item"):
            return cls._normalizar_json(valor.item())
        return valor