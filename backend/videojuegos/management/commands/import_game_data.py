import gzip
import json
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from videojuegos.models import Videojuego


class Command(BaseCommand):
    help = (
        "Importa únicamente los videojuegos que tienen "
        "reseñas en resenas_etiquetadas."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpiar",
            action="store_true",
            help=(
                "Elimina los videojuegos existentes antes "
                "de realizar la importación."
            ),
        )

    def handle(self, *args, **options):
        raiz_proyecto = Path(__file__).resolve().parents[4]

        ruta_metadatos = (
            raiz_proyecto
            / "data"
            / "provisional"
            / "metadatos_videojuegos.parquet"
        )

        ruta_metadatos_originales = (
            raiz_proyecto
            / "data"
            / "raiz"
            / "meta_Video_Games.jsonl.gz"
        )

        directorio_resenas = (
            raiz_proyecto
            / "data"
            / "procesado"
            / "resenas_etiquetadas"
        )

        self._comprobar_rutas(
            ruta_metadatos=ruta_metadatos,
            ruta_metadatos_originales=ruta_metadatos_originales,
            directorio_resenas=directorio_resenas,
        )

        self.stdout.write(
            "Buscando los archivos de reseñas etiquetadas..."
        )

        archivos_resenas = sorted(
            directorio_resenas.glob(
                "resenas_etiquetadas_*.parquet"
            )
        )

        if not archivos_resenas:
            raise CommandError(
                "No se encontraron archivos de reseñas "
                f"etiquetadas en {directorio_resenas}"
            )

        self.stdout.write(
            f"Se han encontrado {len(archivos_resenas)} "
            "archivos de reseñas."
        )

        estadisticas_resenas = (
            self._obtener_estadisticas_resenas(
                archivos_resenas
            )
        )

        metadatos = self._leer_metadatos(
            ruta_metadatos
        )

        catalogo = self._crear_catalogo(
            metadatos=metadatos,
            estadisticas_resenas=estadisticas_resenas,
        )

        metadatos_originales = self._leer_detalles_originales(
            ruta_metadatos_originales=ruta_metadatos_originales,
            parent_asin_objetivo=set(
                catalogo["parent_asin"].astype(str)
            ),
        )
        catalogo["images"] = catalogo["parent_asin"].map(
            lambda parent_asin: metadatos_originales.get(
                str(parent_asin), {}
            ).get("images", [])
        )
        catalogo["description"] = catalogo["parent_asin"].map(
            lambda parent_asin: metadatos_originales.get(
                str(parent_asin), {}
            ).get("description", [])
        )
        catalogo["price"] = catalogo["parent_asin"].map(
            lambda parent_asin: metadatos_originales.get(
                str(parent_asin), {}
            ).get("price")
        )

        self._guardar_videojuegos(
            catalogo=catalogo,
            limpiar=options["limpiar"],
        )

    def _comprobar_rutas(
        self,
        ruta_metadatos: Path,
        ruta_metadatos_originales: Path,
        directorio_resenas: Path,
    ) -> None:
        if not ruta_metadatos.is_file():
            raise CommandError(
                f"No se encontró el archivo de metadatos: {ruta_metadatos}"
            )

        if not ruta_metadatos_originales.is_file():
            raise CommandError(
                "No se encontró el archivo de metadatos originales: "
                f"{ruta_metadatos_originales}"
            )

        if not directorio_resenas.is_dir():
            raise CommandError(
                f"No se encontró el directorio de reseñas: {directorio_resenas}"
            )

    def _leer_detalles_originales(
        self,
        ruta_metadatos_originales: Path,
        parent_asin_objetivo: set[str],
    ) -> dict[str, dict[str, object]]:
        pendientes = parent_asin_objetivo.copy()
        detalles = {}

        if not pendientes:
            return detalles

        with gzip.open(
            ruta_metadatos_originales,
            mode="rt",
            encoding="utf-8",
        ) as archivo:
            for linea in archivo:
                metadatos = json.loads(linea)
                parent_asin = str(
                    metadatos.get("parent_asin") or ""
                ).strip()

                if parent_asin not in pendientes:
                    continue

                detalles[parent_asin] = {
                    "images": self._convertir_a_lista(
                        metadatos.get("images")
                    ),
                    "description": self._convertir_a_lista(
                        metadatos.get("description")
                    ),
                    "price": metadatos.get("price"),
                }
                pendientes.remove(parent_asin)

                if not pendientes:
                    break

        return detalles

    def _leer_metadatos(self, ruta_metadatos: Path) -> pd.DataFrame:
        columnas = [
            "parent_asin",
            "main_category",
            "product_title",
            "product_average_rating",
            "product_rating_number",
            "store",
            "categories",
        ]
        metadatos = pd.read_parquet(ruta_metadatos)
        columnas_faltantes = set(columnas) - set(metadatos.columns)

        if columnas_faltantes:
            raise CommandError(
                "Faltan columnas en los metadatos: "
                + ", ".join(sorted(columnas_faltantes))
            )

        metadatos = metadatos[columnas].copy()
        metadatos["parent_asin"] = (
            metadatos["parent_asin"].astype("string").str.strip()
        )
        metadatos["product_title"] = (
            metadatos["product_title"].astype("string").str.strip()
        )
        metadatos = metadatos.dropna(
            subset=["parent_asin", "product_title"]
        )
        metadatos = metadatos[
            (metadatos["parent_asin"] != "")
            & (metadatos["product_title"] != "")
        ]
        return metadatos.drop_duplicates(
            subset=["parent_asin"],
            keep="first",
        )

    def _obtener_estadisticas_resenas(
        self,
        archivos_resenas: list[Path],
    ) -> pd.DataFrame:
        partes = []

        for archivo in archivos_resenas:
            parte = pd.read_parquet(
                archivo,
                columns=["parent_asin", "rating"],
            )
            partes.append(parte)

        resenas = pd.concat(partes, ignore_index=True)
        resenas["parent_asin"] = (
            resenas["parent_asin"].astype("string").str.strip()
        )
        resenas["rating"] = pd.to_numeric(
            resenas["rating"],
            errors="coerce",
        )
        resenas = resenas.dropna(
            subset=["parent_asin", "rating"]
        )
        resenas = resenas[resenas["parent_asin"] != ""]

        estadisticas = (
            resenas.groupby("parent_asin", as_index=False)
            .agg(
                puntuacion_media=("rating", "mean"),
                numero_valoraciones=("rating", "size"),
            )
        )
        return estadisticas

    def _crear_catalogo(
        self,
        metadatos: pd.DataFrame,
        estadisticas_resenas: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Conserva únicamente los productos que aparecen
        también en las reseñas etiquetadas.
        """

        catalogo = metadatos.merge(
            estadisticas_resenas,
            on="parent_asin",
            how="inner",
            validate="one_to_one",
        )

        catalogo = catalogo.sort_values(
            by="product_title",
            key=lambda columna: columna.str.casefold(),
        ).reset_index(drop=True)

        self.stdout.write(
            self.style.SUCCESS(
                "Videojuegos con reseñas etiquetadas: "
                f"{len(catalogo)}"
            )
        )

        total_resenas = int(
            catalogo["numero_valoraciones"].sum()
        )

        self.stdout.write(
            f"Total de reseñas asociadas: {total_resenas}"
        )

        return catalogo

    @transaction.atomic
    def _guardar_videojuegos(
        self,
        catalogo: pd.DataFrame,
        limpiar: bool,
    ) -> None:
        """
        Crea o actualiza los videojuegos del catálogo.
        """

        if limpiar:
            self.stdout.write(
                "Eliminando videojuegos existentes..."
            )
            Videojuego.objects.all().delete()

        existentes = set(
            Videojuego.objects.values_list(
                "id",
                flat=True,
            )
        )

        videojuegos_nuevos = []
        videojuegos_actualizados = []

        for fila in catalogo.itertuples(index=False):
            videojuego = Videojuego(
                id=str(fila.parent_asin),
                titulo=str(fila.product_title),
                puntuacion_media=(
                    None
                    if pd.isna(fila.puntuacion_media)
                    else round(
                        float(fila.puntuacion_media),
                        2,
                    )
                ),
                numero_valoraciones=int(
                    fila.numero_valoraciones
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
                detalles={
                    "categories": self._convertir_a_lista(
                        getattr(fila, "categories", None)
                    ),
                    "images": self._convertir_a_lista(
                        getattr(fila, "images", None)
                    ),
                    "description": self._convertir_a_lista(
                        getattr(fila, "description", None)
                    ),
                    "price": getattr(fila, "price", None),
                },
            )

            if videojuego.id in existentes:
                videojuegos_actualizados.append(
                    videojuego
                )
            else:
                videojuegos_nuevos.append(
                    videojuego
                )

        if videojuegos_nuevos:
            Videojuego.objects.bulk_create(
                videojuegos_nuevos,
                batch_size=1000,
            )

        if videojuegos_actualizados:
            Videojuego.objects.bulk_update(
                videojuegos_actualizados,
                fields=[
                    "titulo",
                    "puntuacion_media",
                    "numero_valoraciones",
                    "categoria_principal",
                    "tienda",
                    "detalles",
                ],
                batch_size=1000,
            )

        total_base_datos = Videojuego.objects.count()

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Importación completada correctamente."
            )
        )
        self.stdout.write(
            f"Nuevos: {len(videojuegos_nuevos)}"
        )
        self.stdout.write(
            "Actualizados: "
            f"{len(videojuegos_actualizados)}"
        )
        self.stdout.write(
            f"Total en PostgreSQL: {total_base_datos}"
        )

    @staticmethod
    def _convertir_a_lista(valor: object) -> list:
        if valor is None:
            return []

        if hasattr(valor, "tolist"):
            valor = valor.tolist()

        if isinstance(valor, (list, tuple)):
            return list(valor)

        if pd.isna(valor):
            return []

        return [valor]