from collections import Counter
from pathlib import Path

import pandas as pd

from videojuegos.models import Videojuego

from django.conf import settings


DIRECTORIO = (
    settings.BASE_DIR.parent
    / "data"
    / "procesado"
    / "resenas_etiquetadas"
)

ids_videojuegos = set(
    Videojuego.objects.values_list(
        "id",
        flat=True,
    )
)

conteos = Counter()

archivos = sorted(
    DIRECTORIO.glob("*.parquet")
)

print(
    "Archivos Parquet:",
    len(archivos),
)

print(
    "Videojuegos disponibles:",
    len(ids_videojuegos),
)

for numero, archivo in enumerate(
    archivos,
    start=1,
):
    df = pd.read_parquet(
        archivo,
        columns=["parent_asin"],
    )

    parent_asin = (
        df["parent_asin"]
        .dropna()
        .astype(str)
    )

    coincidencias = parent_asin[
        parent_asin.isin(
            ids_videojuegos
        )
    ]

    conteos.update(
        coincidencias.tolist()
    )

    print(
        f"Revisado {numero}/"
        f"{len(archivos)}: "
        f"{archivo.name}"
    )

print()

print(
    "Videojuegos con reseñas:",
    len(conteos),
)

print()
print("40 candidatos con más reseñas:")

for parent_asin, cantidad in (
    conteos.most_common(40)
):
    videojuego = Videojuego.objects.get(
        id=parent_asin,
    )

    print(
        f"{parent_asin} | "
        f"{cantidad} reseñas | "
        f"{videojuego.titulo}"
    )
    