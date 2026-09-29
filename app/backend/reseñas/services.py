import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.backend.prediccion.models import Prediccion
from app.backend.reseñas.models import ResenaGuardada


RUTA_BD = (
	Path(__file__).resolve().parents[3]
	/ "data"
	/ "reseñas_generadas.sqlite3"
)


class ReseñasService:
	def __init__(self, ruta_bd: Path = RUTA_BD) -> None:
		self.ruta_bd = ruta_bd
		self.ruta_bd.parent.mkdir(parents=True, exist_ok=True)
		self._crear_tabla()

	def _conexion(self) -> sqlite3.Connection:
		conexion = sqlite3.connect(self.ruta_bd)
		conexion.row_factory = sqlite3.Row
		return conexion

	def _crear_tabla(self) -> None:
		with self._conexion() as conexion:
			conexion.execute(
				"""
				CREATE TABLE IF NOT EXISTS reseñas (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					videojuego_id TEXT NOT NULL,
					titulo TEXT NOT NULL,
					texto TEXT NOT NULL,
					texto_procesado TEXT NOT NULL,
					sentimiento TEXT NOT NULL,
					puntuacion INTEGER,
					compra_verificada INTEGER NOT NULL,
					imagenes TEXT NOT NULL,
					fecha TEXT NOT NULL
				)
				"""
			)

	def guardar_prediccion(
		self,
		prediccion: Prediccion,
	) -> ResenaGuardada:
		fecha = datetime.now(timezone.utc)
		imagenes = prediccion.imagenes or []

		try:
			with self._conexion() as conexion:
				conexion.execute(
					"""
					INSERT INTO reseñas (
						videojuego_id, titulo, texto,
						texto_procesado, sentimiento, puntuacion,
						compra_verificada, imagenes, fecha
					) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
					""",
					(
						prediccion.videojuego_id,
						prediccion.titulo,
						prediccion.texto,
						prediccion.texto_procesado,
						prediccion.sentimiento,
						prediccion.puntuacion,
						int(prediccion.compra_verificada),
						json.dumps(imagenes),
						fecha.isoformat(),
					),
				)
		except sqlite3.Error as error:
			raise RuntimeError(
				"No se pudo guardar la reseña generada."
			) from error

		return ResenaGuardada(
			videojuego_id=prediccion.videojuego_id,
			titulo=prediccion.titulo,
			texto=prediccion.texto,
			texto_procesado=prediccion.texto_procesado,
			sentimiento=prediccion.sentimiento,
			puntuacion=prediccion.puntuacion,
			compra_verificada=prediccion.compra_verificada,
			imagenes=imagenes,
			fecha=fecha,
		)

	def listar(self, videojuego_id: str) -> list[ResenaGuardada]:
		with self._conexion() as conexion:
			filas = conexion.execute(
				"""
				SELECT videojuego_id, titulo, texto,
					   texto_procesado, sentimiento, puntuacion,
					   compra_verificada, imagenes, fecha
				FROM reseñas
				WHERE videojuego_id = ?
				ORDER BY fecha DESC
				""",
				(videojuego_id,),
			).fetchall()

		return [
			ResenaGuardada(
				videojuego_id=fila["videojuego_id"],
				titulo=fila["titulo"],
				texto=fila["texto"],
				texto_procesado=fila["texto_procesado"],
				sentimiento=fila["sentimiento"],
				puntuacion=fila["puntuacion"],
				compra_verificada=bool(fila["compra_verificada"]),
				imagenes=json.loads(fila["imagenes"]),
				fecha=datetime.fromisoformat(fila["fecha"]),
			)
			for fila in filas
		]


reseñas_service = ReseñasService()
