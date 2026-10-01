from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from predicciones.models import Prediccion
from videojuegos.models import Videojuego


class PrediccionPuntuacionTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.videojuego = Videojuego.objects.create(
			id="B001234567",
			titulo="Juego de prueba",
		)

	@patch("predicciones.views.obtener_prediccion_service")
	def test_dos_estrellas_forzan_sentimiento_negativo(
		self,
		obtener_servicio,
	):
		obtener_servicio.return_value.predecir.return_value = (
			"juego divertido",
			"positivo",
		)

		respuesta = self.client.post(
			reverse("prediccion-list"),
			{
				"videojuego_id": self.videojuego.id,
				"title": "No me gustó",
				"text": "No me gustó el juego.",
				"rating": 2,
			},
			format="json",
		)

		self.assertEqual(respuesta.status_code, 201)
		self.assertEqual(respuesta.data["sentiment"], "negativo")

	@patch("predicciones.views.obtener_prediccion_service")
	def test_sin_puntuacion_conserva_prediccion_del_modelo(
		self,
		obtener_servicio,
	):
		obtener_servicio.return_value.predecir.return_value = (
			"juego divertido",
			"positivo",
		)

		respuesta = self.client.post(
			reverse("prediccion-list"),
			{
				"videojuego_id": self.videojuego.id,
				"title": "Me gustó",
				"text": "Me gustó el juego.",
			},
			format="json",
		)

		self.assertEqual(respuesta.status_code, 201)
		self.assertEqual(respuesta.data["sentiment"], "positivo")

	@patch("predicciones.views.obtener_prediccion_service")
	def test_analizar_no_guarda_la_resena(
		self,
		obtener_servicio,
	):
		obtener_servicio.return_value.predecir.return_value = (
			"juego divertido",
			"positivo",
		)

		respuesta = self.client.post(
			reverse("prediccion-analizar"),
			{
				"videojuego_id": self.videojuego.id,
				"title": "Me gustó",
				"text": "Me gustó el juego.",
			},
			format="json",
		)

		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta.data["sentiment"], "positivo")
		self.assertEqual(Prediccion.objects.count(), 0)
