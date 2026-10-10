from collections import Counter
from pathlib import Path

import pandas as pd
from django.conf import settings

from videojuegos.models import Videojuego


ASINS_DEMO = [
    "B0086VPUHI",
    "B07YBXFDYN",
    "B07YBWT3PK",
    "B00C1TTF86",
    "B00EP2WNKY",
    "B00CJ9OTNE",
    "B00BN5T30E",
    "B08D3XL1KF",
    "B00Z9TM72Q",
    "B087SHFL9B",
    "B017QU5KLK",
    "B007CM0K86",
    "B002Z01QO2",
    "B014R4KYMS",
    "B00DDILSBG",
    "B087NNZZM8",
    "B01GY35HKE",
    "B0088TN73M",
    "B00KWOSQC8",
    "B07DK1H3H5",
]


DIRECTORIO = (
    settings.BASE_DIR.parent
    / "data"
    / "procesado"
    / "resenas_etiquetadas"
)


conteos = {
    asin: Counter()
    for asin in ASINS_DEMO
}


archivos = sorted(
    DIRECTORIO.glob("*.parquet")
)


for numero, archivo in enumerate(archivos, start=1):
    df = pd.read_parquet(
        archivo,
        columns=[
            "parent_asin",
            "sentiment",
        ],
    )

    df = df[
        df["parent_asin"].isin(ASINS_DEMO)
    ]

    for asin, grupo in df.groupby("parent_asin"):
        conteos[asin].update(
            grupo["sentiment"]
            .dropna()
            .astype(str)
            .tolist()
        )

    print(
        f"Revisado {numero}/{len(archivos)}: "
        f"{archivo.name}"
    )


print()
print("Distribución de sentimientos:")


for asin in ASINS_DEMO:
    videojuego = Videojuego.objects.get(
        id=asin,
    )

    valores = conteos[asin]
    total = sum(valores.values())

    print()
    print(
        f"{asin} | {videojuego.titulo}"
    )

    print(
        f"Total: {total} | "
        f"Positivas: {valores['positivo']} | "
        f"Neutrales: {valores['neutral']} | "
        f"Negativas: {valores['negativo']}"
    )

