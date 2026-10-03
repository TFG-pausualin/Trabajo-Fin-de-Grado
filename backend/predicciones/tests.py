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

	@patch("predicciones.views.obtener_prediccion_service")
	def test_resena_puntuada_actualiza_resumen_del_videojuego(
		self,
		obtener_servicio,
	):
		obtener_servicio.return_value.predecir.return_value = (
			"juego divertido",
			"positivo",
		)
		self.videojuego.puntuacion_media = 3.6
		self.videojuego.numero_valoraciones = 1
		self.videojuego.numero_resenas = 4
		self.videojuego.save()

		respuesta = self.client.post(
			reverse("prediccion-list"),
			{
				"videojuego_id": self.videojuego.id,
				"title": "No me gustó",
				"text": "No me gustó el juego.",
				"rating": 1,
			},
			format="json",
		)

		self.assertEqual(respuesta.status_code, 201)
		catalogo = self.client.get(
			reverse("videojuego-detail", args=[self.videojuego.id])
		)
		self.assertEqual(catalogo.data["puntuacion_media"], 2.3)
		self.assertEqual(catalogo.data["numero_valoraciones"], 2)
		self.assertEqual(catalogo.data["numero_resenas"], 5)

		filtrado = self.client.get(
			reverse("videojuego-list"),
			{"etiqueta": "negativa"},
		)
		self.assertEqual(filtrado.data["count"], 1)

	@patch("predicciones.views.obtener_prediccion_service")
	def test_resena_sin_puntuacion_actualiza_solo_total_de_resenas(
		self,
		obtener_servicio,
	):
		obtener_servicio.return_value.predecir.return_value = (
			"juego divertido",
			"positivo",
		)
		self.videojuego.puntuacion_media = 3.6
		self.videojuego.numero_valoraciones = 1
		self.videojuego.numero_resenas = 4
		self.videojuego.save()

		respuesta = self.client.post(
			reverse("prediccion-list"),
			{
				"videojuego_id": self.videojuego.id,
				"title": "Interesante",
				"text": "Me pareció interesante.",
			},
			format="json",
		)

		self.assertEqual(respuesta.status_code, 201)
		catalogo = self.client.get(
			reverse("videojuego-detail", args=[self.videojuego.id])
		)
		self.assertEqual(catalogo.data["puntuacion_media"], 3.6)
		self.assertEqual(catalogo.data["numero_valoraciones"], 1)
		self.assertEqual(catalogo.data["numero_resenas"], 5)
