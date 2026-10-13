import json
from pathlib import Path
from typing import Any

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


DIRECTORIO_PROCESADO = (
    settings.BASE_DIR.parent
    / "data"
    / "procesado"
)

DIRECTORIO_ORIGINALES = (
    DIRECTORIO_PROCESADO
    / "resenas_sin_duplicados"
)

DIRECTORIO_ETIQUETADAS = (
    DIRECTORIO_PROCESADO
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


COLUMNAS_ORIGINALES = [
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

COLUMNAS_ETIQUETADAS = [
    "rating",
    "parent_asin",
    "user_id",
    "timestamp",
    "verified_purchase",
    "review_text_normalized",
    "review_text_processed",
    "sentiment",
]

COLUMNAS_IDENTIDAD = [
    "parent_asin",
    "user_id",
    "timestamp",
    "rating",
    "verified_purchase",
]


def es_nulo(valor: Any) -> bool:
    if valor is None:
        return True

    try:
        resultado = pd.isna(valor)

        if isinstance(resultado, bool):
            return resultado
    except (TypeError, ValueError):
        pass

    return False


def normalizar_clave(valor: Any) -> str:
    if es_nulo(valor):
        return ""

    if isinstance(valor, pd.Timestamp):
        return valor.isoformat()

    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))

    return str(valor)


def obtener_identidades(
    filas: pd.DataFrame,
) -> pd.Series:
    return filas[COLUMNAS_IDENTIDAD].apply(
        lambda fila: tuple(
            normalizar_clave(valor)
            for valor in fila
        ),
        axis=1,
    )


def convertir_fecha(valor: Any) -> str | None:
    if es_nulo(valor):
        return None

    fecha = pd.Timestamp(valor)

    if fecha.tzinfo is None:
        fecha = fecha.tz_localize("UTC")
    else:
        fecha = fecha.tz_convert("UTC")

    return fecha.isoformat()


def normalizar_texto(valor: Any) -> str:
    if es_nulo(valor):
        return ""

    return str(valor).strip()


def normalizar_texto_opcional(
    valor: Any,
) -> str | None:
    texto = normalizar_texto(valor)
    return texto or None


def normalizar_entero(
    valor: Any,
    predeterminado: int = 0,
) -> int:
    if es_nulo(valor):
        return predeterminado

    return int(valor)


def normalizar_json(valor: Any) -> Any:
    if valor is None:
        return None

    if isinstance(valor, dict):
        return {
            str(clave): normalizar_json(contenido)
            for clave, contenido in valor.items()
        }

    if isinstance(valor, (list, tuple)):
        return [
            normalizar_json(contenido)
            for contenido in valor
        ]

    if isinstance(valor, pd.Timestamp):
        return convertir_fecha(valor)

    if hasattr(valor, "tolist"):
        return normalizar_json(valor.tolist())

    if hasattr(valor, "item"):
        return normalizar_json(valor.item())

    if es_nulo(valor):
        return None

    return valor


def normalizar_imagenes(
    valor: Any,
    ) -> list:
    resultado = normalizar_json(valor)

    if isinstance(resultado, list):
        return resultado

    return []


def convertir_json(valor: Any) -> Any:
    return normalizar_json(valor)


def unir_bloque(
    archivo_original: Path,
    archivo_etiquetado: Path,
) -> pd.DataFrame:
    originales = pd.read_parquet(
        archivo_original,
        columns=COLUMNAS_ORIGINALES,
    )

    etiquetadas = pd.read_parquet(
        archivo_etiquetado,
        columns=COLUMNAS_ETIQUETADAS,
    )

    originales = originales[
        originales["parent_asin"].isin(
            ASINS_DEMO
        )
    ].copy()

    etiquetadas = etiquetadas[
        etiquetadas["parent_asin"].isin(
            ASINS_DEMO
        )
    ].copy()

    if originales.empty or etiquetadas.empty:
        return pd.DataFrame()

    originales["__identidad"] = (
        obtener_identidades(originales)
    )

    etiquetadas["__identidad"] = (
        obtener_identidades(etiquetadas)
    )

    originales["__ocurrencia"] = (
        originales.groupby(
            "__identidad",
            sort=False,
        ).cumcount()
    )

    etiquetadas["__ocurrencia"] = (
        etiquetadas.groupby(
            "__identidad",
            sort=False,
        ).cumcount()
    )

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
        on=[
            "__identidad",
            "__ocurrencia",
        ],
        how="inner",
        validate="one_to_one",
    )

    return unidas


print("Comprobando directorios...")

if not DIRECTORIO_ORIGINALES.is_dir():
    raise RuntimeError(
        "No existe el directorio de reseñas "
        f"originales: {DIRECTORIO_ORIGINALES}"
    )

if not DIRECTORIO_ETIQUETADAS.is_dir():
    raise RuntimeError(
        "No existe el directorio de reseñas "
        f"etiquetadas: {DIRECTORIO_ETIQUETADAS}"
    )


archivos_etiquetados = sorted(
    DIRECTORIO_ETIQUETADAS.glob(
        "resenas_etiquetadas_*.parquet"
    )
)

if not archivos_etiquetados:
    raise RuntimeError(
        "No se encontraron archivos Parquet "
        "de reseñas etiquetadas."
    )


print("Uniendo reseñas originales y etiquetadas...")

fragmentos = []

for numero, archivo_etiquetado in enumerate(
    archivos_etiquetados,
    start=1,
):
    bloque = (
        archivo_etiquetado
        .stem
        .removeprefix(
            "resenas_etiquetadas_"
        )
    )

    archivo_original = (
        DIRECTORIO_ORIGINALES
        / (
            "resenas_sin_duplicados_"
            f"{bloque}.parquet"
        )
    )

    if not archivo_original.is_file():
        raise RuntimeError(
            "No se encontró el bloque original "
            f"correspondiente a "
            f"{archivo_etiquetado.name}: "
            f"{archivo_original}"
        )

    unidas = unir_bloque(
        archivo_original=archivo_original,
        archivo_etiquetado=archivo_etiquetado,
    )

    if not unidas.empty:
        fragmentos.append(unidas)

    print(
        f"Revisado {numero}/"
        f"{len(archivos_etiquetados)}: "
        f"{archivo_etiquetado.name} | "
        f"{len(unidas)} coincidencias"
    )


if not fragmentos:
    raise RuntimeError(
        "No se pudieron emparejar reseñas "
        "para los videojuegos seleccionados."
    )


todas_resenas = pd.concat(
    fragmentos,
    ignore_index=True,
)

print()
print(
    "Reseñas completas encontradas:",
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
        todas_resenas["parent_asin"]
        .astype(str)
        .eq(asin)
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

    if cantidad == 0:
        raise RuntimeError(
            "No se encontraron reseñas "
            f"completas para {asin}."
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

    puntuacion_media = float(
        muestra["rating"].mean()
    )

    fixtures.append(
        {
            "model": (
                "videojuegos.videojuego"
            ),
            "pk": videojuego.pk,
            "fields": {
                "titulo": videojuego.titulo,
                "puntuacion_media": round(
                    puntuacion_media,
                    2,
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
        titulo = normalizar_texto(
            fila["title"]
        )

        texto = normalizar_texto(
            fila["text"]
        )

        texto_normalizado = normalizar_texto(
            fila["review_text_normalized"]
        )

        texto_procesado = normalizar_texto(
            fila["review_text_processed"]
        )

        usuario = normalizar_texto_opcional(
            fila["user_id"]
        )

        asin_resena = normalizar_texto_opcional(
            fila["asin"]
        )

        imagenes = normalizar_imagenes(
            fila["images"]
        )

        votos_utiles = normalizar_entero(
            fila["helpful_vote"],
            predeterminado=0,
        )

        fixtures.append(
            {
                "model": "resenas.resena",
                "pk": contador_resenas,
                "fields": {
                    "videojuego": asin,
                    "titulo": titulo,
                    "texto": texto,
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
                    "imagenes": imagenes,
                    "usuario_original_id": (
                        usuario
                    ),
                    "fecha_original": (
                        convertir_fecha(
                            fila["timestamp"]
                        )
                    ),
                    "sentimiento_predicho": None,
                    "sentimiento_real": (
                        normalizar_texto(
                            fila["sentiment"]
                        )
                    ),
                    "origen": "historica",
                    "creada_en": ahora,
                    "actualizada_en": ahora,
                    "asin": asin_resena,
                    "votos_utiles": votos_utiles,
                },
            }
        )

        contador_resenas += 1

    print(
        f"{asin} | "
        f"{cantidad} reseñas | "
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

titulos_exportados = sum(
    1
    for objeto in fixtures
    if (
        objeto["model"] == "resenas.resena"
        and objeto["fields"]["titulo"]
    )
)

print(
    "Reseñas con título:",
    titulos_exportados,
)