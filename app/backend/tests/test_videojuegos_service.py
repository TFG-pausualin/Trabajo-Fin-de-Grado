import gzip
import json

import pandas as pd

from app.backend.videojuegos.services import VideojuegosService


def test_lista_videojuegos_y_resenas_desde_archivos_etiquetados(tmp_path):
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
            "parent_asin": "SIN_RESENAS",
            "title": "Juego sin reseñas",
        },
    ]
    with gzip.open(ruta_metadatos, "wt", encoding="utf-8") as archivo:
        for metadato in metadatos:
            archivo.write(json.dumps(metadato) + "\n")

    ruta_resenas = tmp_path / "resenas_etiquetadas"
    ruta_resenas.mkdir()
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
    ).to_parquet(ruta_resenas / "resenas_etiquetadas_0000.parquet")

    ruta_originales = tmp_path / "resenas_sin_duplicados"
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
    ).to_parquet(ruta_originales / "resenas_0000.parquet")

    servicio = VideojuegosService(
        ruta_metadatos=ruta_metadatos,
        ruta_resenas_etiquetadas=ruta_resenas,
        ruta_resenas_originales=ruta_originales,
    )

    videojuegos, total, _ = servicio.listar_videojuegos(pagina=1, limite=20)
    detalle = servicio.obtener_videojuego("GAME1")
    resenas, total_resenas, paginas = servicio.listar_resenas(
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
    assert total_resenas == 2
    assert paginas == 2
    assert resenas[0].title == "No funciona"
    assert resenas[0].text == "Se bloquea al iniciar"
    assert resenas[0].sentimiento == "negativo"
    assert resenas[0].helpful_vote == 3