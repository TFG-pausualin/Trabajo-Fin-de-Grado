import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .management.commands.import_game_data import Command
from .models import Videojuego


class ImportGameDataImagenesTests(SimpleTestCase):
	def test_leer_detalles_filtra_por_parent_asin(self):
		with TemporaryDirectory() as directorio:
			ruta_metadatos = Path(directorio) / "metadatos.jsonl.gz"
			registros = [
				{"parent_asin": "OTRO", "images": [{"large": "otra.jpg"}]},
				{
					"parent_asin": "JUEGO1",
					"images": [{"large": "portada.jpg"}],
					"description": ["Descripción del juego"],
					"price": 58.0,
				},
			]

			with gzip.open(ruta_metadatos, "wt", encoding="utf-8") as archivo:
				for registro in registros:
					archivo.write(json.dumps(registro) + "\n")

			detalles = Command()._leer_detalles_originales(
				ruta_metadatos_originales=ruta_metadatos,
				parent_asin_objetivo={"JUEGO1"},
			)

		self.assertEqual(
			detalles,
			{
				"JUEGO1": {
					"images": [{"large": "portada.jpg"}],
					"description": ["Descripción del juego"],
					"price": 58.0,
				}
			},
		)


class VideojuegoSoloLecturaTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.videojuego = Videojuego.objects.create(
			id="B001234567",
			titulo="Great game",
			puntuacion_media=4.5,
			numero_valoraciones=12,
			categoria_principal="Action",
		)

	def test_catalogo_no_permite_crear_videojuegos(self):
		respuesta = self.client.post(
			reverse("videojuego-list"),
			{
				"id": "B009876543",
				"titulo": "Otro juego",
			},
			format="json",
		)

		self.assertEqual(respuesta.status_code, 405)

	def test_catalogo_no_permite_editar_ni_borrar_videojuegos(self):
		url = reverse(
			"videojuego-detail",
			args=[self.videojuego.id],
		)

		respuesta_edicion = self.client.patch(
			url,
			{"titulo": "Título modificado"},
			format="json",
		)
		respuesta_borrado = self.client.delete(url)

		self.assertEqual(respuesta_edicion.status_code, 405)
		self.assertEqual(respuesta_borrado.status_code, 405)
		self.videojuego.refresh_from_db()
		self.assertEqual(self.videojuego.titulo, "Great game")

	def test_catalogo_devuelve_pagina_y_total(self):
		Videojuego.objects.create(
			id="B009876543",
			titulo="Another game",
		)

		respuesta = self.client.get(
			reverse("videojuego-list"),
			{"pagina": 2, "limite": 1},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta.data["count"], 2)
		self.assertEqual(len(respuesta.data["results"]), 1)

	def test_catalogo_filtra_por_categoria(self):
		respuesta = self.client.get(
			reverse("videojuego-list"),
			{"busqueda": "action"},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta.data["count"], 1)
		self.assertEqual(respuesta.data["results"][0]["id"], self.videojuego.id)

	def test_catalogo_filtra_por_etiqueta_de_calificacion_general(self):
		Videojuego.objects.create(
			id="B009876543",
			titulo="Low-rated game",
			puntuacion_media=2.2,
		)

		respuesta = self.client.get(
			reverse("videojuego-list"),
			{"busqueda": "NEGATIVA"},
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta.data["count"], 1)
		self.assertEqual(respuesta.data["results"][0]["id"], "B009876543")
