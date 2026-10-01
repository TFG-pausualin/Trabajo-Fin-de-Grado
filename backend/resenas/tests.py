from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from predicciones.models import Prediccion
from videojuegos.models import Videojuego
from .parquet_repository import RepositorioResenasParquet


class ResenasParquetTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.videojuego_id = "GAME-1"
		self.directorio_temporal = TemporaryDirectory()
		self.addCleanup(self.directorio_temporal.cleanup)
		self.directorio_procesado = Path(
			self.directorio_temporal.name
		)
		originales = self.directorio_procesado / "resenas_sin_duplicados"
		etiquetadas = self.directorio_procesado / "resenas_etiquetadas"
		originales.mkdir()
		etiquetadas.mkdir()
		fecha = pd.Timestamp("2025-01-02T12:00:00")
		pd.DataFrame(
			[
				{
					"rating": 1,
					"title": "Sin etiqueta",
					"text": "Esta fila no está etiquetada.",
					"images": [],
					"asin": "REVIEW-0",
					"parent_asin": "OTRO-JUEGO",
					"user_id": "usuario-0",
					"timestamp": fecha,
					"helpful_vote": 0,
					"verified_purchase": False,
				},
				{
					"rating": 5,
					"title": "Muy bueno",
					"text": "Me ha encantado.",
					"images": [],
					"asin": "REVIEW-1",
					"parent_asin": "GAME-1",
					"user_id": "usuario-1",
					"timestamp": fecha + pd.Timedelta(days=1),
					"helpful_vote": 2,
					"verified_purchase": True,
				},
			]
		).to_parquet(
			originales / "resenas_sin_duplicados_0000.parquet",
			index=False,
		)
		pd.DataFrame(
			[
				{
					"rating": 5,
					"parent_asin": "GAME-1",
					"user_id": "usuario-1",
					"timestamp": fecha + pd.Timedelta(days=1),
					"verified_purchase": True,
					"review_text_normalized": "muy bueno me ha encantado",
					"review_text_processed": "bueno encantado",
					"sentiment": "positivo",
				}
			]
		).to_parquet(
			etiquetadas / "resenas_etiquetadas_0000.parquet",
			index=False,
		)
		self.repositorio = RepositorioResenasParquet(
			self.directorio_procesado
		)

	def test_empareja_por_identidad_si_hay_filas_sin_etiqueta(self):
		resenas = self.repositorio.listar_por_videojuego("GAME-1")

		self.assertEqual(len(resenas), 1)
		self.assertEqual(resenas[0]["id"], "0000:1")
		self.assertEqual(resenas[0]["titulo"], "Muy bueno")
		self.assertEqual(resenas[0]["sentimiento"], "positivo")

	@patch("resenas.views.Videojuego.objects.filter")
	@patch("resenas.views.RepositorioResenasParquet")
	def test_endpoint_pagina_parquet_y_usa_metadatos_del_videojuego(
		self,
		repositorio_mock,
		videojuego_filter_mock,
	):
		repositorio_mock.return_value = self.repositorio
		videojuego_filter_mock.return_value.values_list.return_value.first.return_value = (
			"Juego de prueba"
		)
		respuesta = self.client.get(
			reverse("resena-list"),
			{
				"videojuego": self.videojuego_id,
				"pagina": 1,
				"limite": 1,
			},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta.data["count"], 1)
		self.assertEqual(len(respuesta.data["results"]), 1)
		self.assertEqual(
			respuesta.data["results"][0]["videojuego_titulo"],
			"Juego de prueba",
		)
		videojuego_filter_mock.assert_called_once_with(
			id=self.videojuego_id
		)

	def test_endpoint_exige_videojuego(self):
		respuesta = self.client.get(reverse("resena-list"))

		self.assertEqual(respuesta.status_code, 400)


class ResenasPrediccionTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.videojuego = Videojuego.objects.create(
			id="GAME-2",
			titulo="Juego de prueba",
		)
		self.prediccion = Prediccion.objects.create(
			videojuego=self.videojuego,
			title="Reseña nueva",
			text="Texto de la reseña nueva.",
			review_text_normalized="Reseña nueva Texto de la reseña nueva.",
			review_text_processed="reseña nueva",
			sentiment="positivo",
		)

	@patch("resenas.views.Videojuego.objects.filter")
	@patch("resenas.views.RepositorioResenasParquet")
	def test_lista_primero_resenas_guardadas_en_bd(
		self,
		repositorio_mock,
		videojuego_filter_mock,
	):
		historica = {
			"id": "0000:1",
			"videojuego": "GAME-2",
			"videojuego_titulo": "",
			"parent_asin": "GAME-2",
			"titulo": "Reseña histórica",
			"texto": "Texto histórico.",
			"texto_normalizado": "Reseña histórica Texto histórico.",
			"texto_procesado": "histórico",
			"puntuacion": 5,
			"compra_verificada": True,
			"imagenes": [],
			"usuario_original_id": "usuario-1",
			"fecha_original": "2025-01-02T12:00:00Z",
			"sentimiento_predicho": None,
			"sentimiento_real": "positivo",
			"sentimiento": "positivo",
			"origen": "historica",
			"creada_en": "2025-01-02T12:00:00Z",
			"actualizada_en": "2025-01-02T12:00:00Z",
			"asin": "REVIEW-1",
			"votos_utiles": 0,
		}
		repositorio_mock.return_value.listar_por_videojuego.return_value = [
			historica
		]
		videojuego_filter_mock.return_value.values_list.return_value.first.return_value = (
			"Juego de prueba"
		)

		respuesta = self.client.get(
			reverse("resena-list"),
			{"videojuego": self.videojuego.id},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta.data["count"], 2)
		self.assertEqual(respuesta.data["results"][0]["id"], f"nueva:{self.prediccion.id}")
		self.assertEqual(respuesta.data["results"][0]["titulo"], "Reseña nueva")
