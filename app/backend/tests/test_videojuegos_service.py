import gzip
import json

import pandas as pd

from app.backend.videojuegos.services import VideojuegosService


def test_lista_videojuegos_y_reseñas_desde_archivos_etiquetados(tmp_path):
    ruta_metadatos = tmp_path / "meta_Video_Games.jsonl.gz"
    metadatos = [
        {
            "parent_asin": "GAME1",
            "title": "Juego Uno",
            "average_rating": 4.5,
            "rating_number": 12,
            "main_category": "Video Games",
            "store": "Tienda",
            "description": ["Descripción de prueba"],
            "price": 29.99,
            "features": ["Modo historia", "Multijugador"],
            "empty_field": [],
        },
        {
            "parent_asin": "SIN_reseñas",
            "title": "Juego sin reseñas",
        },
    ]
    with gzip.open(ruta_metadatos, "wt", encoding="utf-8") as archivo:
        for metadato in metadatos:
            archivo.write(json.dumps(metadato) + "\n")

    ruta_reseñas = tmp_path / "reseñas_etiquetadas"
    ruta_reseñas.mkdir()
    pd.DataFrame(
        {
            "parent_asin": ["GAME1", "GAME1"],
            "rating": [4, 2],
            "user_id": ["USER1", "USER2"],
            "timestamp": pd.to_datetime(
                ["2024-01-01", "2024-02-01"]
            ),
            "verified_purchase": [True, False],
            "review_text_normalized": ["buena historia", "muchos errores"],
            "sentiment": ["positivo", "negativo"],
        }
    ).to_parquet(ruta_reseñas / "reseñas_etiquetadas_0000.parquet")

    ruta_originales = tmp_path / "reseñas_sin_duplicados"
    ruta_originales.mkdir()
    pd.DataFrame(
        {
            "rating": [4, 2],
            "title": ["Buena historia", "No funciona"],
            "text": ["Me gustó mucho", "Se bloquea al iniciar"],
            "images": [[], []],
            "asin": ["REVIEW1", "REVIEW2"],
            "parent_asin": ["GAME1", "GAME1"],
            "user_id": ["USER1", "USER2"],
            "timestamp": pd.to_datetime(
                ["2024-01-01", "2024-02-01"]
            ),
            "helpful_vote": [0, 3],
            "verified_purchase": [True, False],
        }
    ).to_parquet(ruta_originales / "reseñas_0000.parquet")

    servicio = VideojuegosService(
        ruta_metadatos=ruta_metadatos,
        ruta_reseñas_etiquetadas=ruta_reseñas,
        ruta_reseñas_originales=ruta_originales,
    )

    videojuegos, total, _ = servicio.listar_videojuegos(pagina=1, limite=20)
    detalle = servicio.obtener_videojuego("GAME1")
    reseñas, total_reseñas, paginas = servicio.listar_reseñas(
        videojuego_id="GAME1",
        pagina=1,
        limite=1,
    )

    assert total == 1
    assert videojuegos[0].id == "GAME1"
    assert videojuegos[0].titulo == "Juego Uno"
    assert detalle is not None
    assert detalle.detalles["description"] == ["Descripción de prueba"]
    assert detalle.detalles["features"] == ["Modo historia", "Multijugador"]
    assert "empty_field" not in detalle.detalles
    assert total_reseñas == 2
    assert paginas == 2
    assert reseñas[0].title == "No funciona"
    assert reseñas[0].text == "Se bloquea al iniciar"
    assert reseñas[0].sentimiento == "negativo"
    assert reseñas[0].helpful_vote == 3