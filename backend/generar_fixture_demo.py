import json
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.utils import timezone

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


DIRECTORIO_PARQUET = (
    settings.BASE_DIR.parent
    / "data"
    / "procesado"
    / "resenas_etiquetadas"
)


DIRECTORIO_FIXTURES = (
    settings.BASE_DIR
    / "fixtures"
)


RUTA_SALIDA = (
    DIRECTORIO_FIXTURES
    / "datos_demo.json"
)


COLUMNAS = [
    "rating",
    "parent_asin",
    "user_id",
    "timestamp",
    "verified_purchase",
    "review_text_normalized",
    "review_text_processed",
    "sentiment",
]


def convertir_fecha(valor):
    if pd.isna(valor):
        return None

    fecha = pd.Timestamp(valor)

    if fecha.tzinfo is None:
        fecha = fecha.tz_localize("UTC")
    else:
        fecha = fecha.tz_convert("UTC")

    return fecha.isoformat()


def convertir_json(valor):
    if isinstance(valor, pd.Timestamp):
        return convertir_fecha(valor)

    if pd.isna(valor):
        return None

    return valor


print("Leyendo archivos Parquet...")

fragmentos = []

archivos = sorted(
    DIRECTORIO_PARQUET.glob("*.parquet")
)

for numero, archivo in enumerate(
    archivos,
    start=1,
):
    df = pd.read_parquet(
        archivo,
        columns=COLUMNAS,
    )

    df = df[
        df["parent_asin"].isin(
            ASINS_DEMO
        )
    ].copy()

    if not df.empty:
        fragmentos.append(df)

    print(
        f"Revisado {numero}/{len(archivos)}: "
        f"{archivo.name}"
    )


if not fragmentos:
    raise RuntimeError(
        "No se encontraron reseñas "
        "para los videojuegos seleccionados."
    )


todas_resenas = pd.concat(
    fragmentos,
    ignore_index=True,
)


print()
print(
    "Reseñas encontradas:",
    len(todas_resenas),
)


fixtures = []
contador_resenas = 1
ahora = timezone.now().isoformat()


for asin in ASINS_DEMO:
    videojuego = Videojuego.objects.get(
        id=asin,
    )

    candidatas = todas_resenas[
        todas_resenas["parent_asin"] == asin
    ].copy()

    candidatas = candidatas.drop_duplicates(
        subset=[
            "user_id",
            "review_text_normalized",
        ]
    )

    cantidad = min(
        20,
        len(candidatas),
    )

    muestra = candidatas.sample(
        n=cantidad,
        random_state=42,
    ).reset_index(drop=True)

    positivas = int(
        (
            muestra["sentiment"]
            == "positivo"
        ).sum()
    )

    neutrales = int(
        (
            muestra["sentiment"]
            == "neutral"
        ).sum()
    )

    negativas = int(
        (
            muestra["sentiment"]
            == "negativo"
        ).sum()
    )

    puntuacion_media = (
        float(
            muestra["rating"].mean()
        )
        if not muestra.empty
        else 0.0
    )

    fixtures.append(
        {
            "model": (
                "videojuegos.videojuego"
            ),
            "pk": videojuego.pk,
            "fields": {
                "titulo": videojuego.titulo,
                "puntuacion_media": (
                    round(
                        puntuacion_media,
                        2,
                    )
                ),
                "numero_valoraciones": cantidad,
                "numero_resenas": cantidad,
                "sentimientos_positivos": positivas,
                "sentimientos_neutrales": neutrales,
                "sentimientos_negativos": negativas,
                "categoria_principal": (
                    videojuego.categoria_principal
                ),
                "tienda": videojuego.tienda,
                "detalles": videojuego.detalles,
                "created_at": (
                    videojuego.created_at.isoformat()
                    if videojuego.created_at
                    else ahora
                ),
                "updated_at": ahora,
            },
        }
    )

    for _, fila in muestra.iterrows():
        texto_normalizado = str(
            fila[
                "review_text_normalized"
            ]
        )

        texto_procesado = str(
            fila[
                "review_text_processed"
            ]
        )

        usuario = (
            None
            if pd.isna(fila["user_id"])
            else str(fila["user_id"])
        )

        fixtures.append(
            {
                "model": "resenas.resena",
                "pk": contador_resenas,
                "fields": {
                    "videojuego": asin,
                    "titulo": "",
                    "texto": texto_normalizado,
                    "texto_normalizado": (
                        texto_normalizado
                    ),
                    "texto_procesado": (
                        texto_procesado
                    ),
                    "puntuacion": int(
                        fila["rating"]
                    ),
                    "compra_verificada": bool(
                        fila[
                            "verified_purchase"
                        ]
                    ),
                    "imagenes": [],
                    "usuario_original_id": (
                        usuario
                    ),
                    "fecha_original": (
                        convertir_fecha(
                            fila["timestamp"]
                        )
                    ),
                    "sentimiento_predicho": None,
                    "sentimiento_real": str(
                        fila["sentiment"]
                    ),
                    "origen": "historica",
                    "creada_en": ahora,
                    "actualizada_en": ahora,
                    "asin": asin,
                    "votos_utiles": 0,
                },
            }
        )

        contador_resenas += 1

    print(
        f"{asin} | {cantidad} reseñas | "
        f"{positivas} positivas, "
        f"{neutrales} neutrales, "
        f"{negativas} negativas | "
        f"{videojuego.titulo}"
    )


DIRECTORIO_FIXTURES.mkdir(
    parents=True,
    exist_ok=True,
)


with RUTA_SALIDA.open(
    "w",
    encoding="utf-8",
) as archivo_salida:
    json.dump(
        fixtures,
        archivo_salida,
        ensure_ascii=False,
        indent=2,
        default=convertir_json,
    )


print()
print("Fixture generado correctamente:")
print(RUTA_SALIDA)

print()
print(
    "Videojuegos exportados:",
    len(ASINS_DEMO),
)

print(
    "Reseñas exportadas:",
    contador_resenas - 1,
)