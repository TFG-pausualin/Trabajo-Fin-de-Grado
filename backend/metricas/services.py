from django.db.models import Count, Q, Sum

from predicciones.models import Prediccion
from videojuegos.models import Videojuego


class MetricasService:
    def obtener_metricas_globales(self) -> dict:
        catalogo = Videojuego.objects.aggregate(
            total_videojuegos=Count("id"),
            total_resenas=Sum("numero_resenas"),
            total_valoraciones=Sum("numero_valoraciones"),
            positivas=Sum("sentimientos_positivos"),
            neutrales=Sum("sentimientos_neutrales"),
            negativas=Sum("sentimientos_negativos"),
        )
        predicciones = self._resumen_predicciones()

        total_valoraciones = (
            (catalogo["total_valoraciones"] or 0)
            + predicciones["valoraciones"]
        )
        suma_puntuaciones = self._suma_puntuaciones_historicas() + (
            predicciones["suma_puntuaciones"] or 0
        )
        puntuacion_media = (
            round(suma_puntuaciones / total_valoraciones, 2)
            if total_valoraciones
            else None
        )
        conteos = {
            "positivas": (catalogo["positivas"] or 0)
            + predicciones["positivas"],
            "neutrales": (catalogo["neutrales"] or 0)
            + predicciones["neutrales"],
            "negativas": (catalogo["negativas"] or 0)
            + predicciones["negativas"],
        }

        return {
            "total_videojuegos": catalogo["total_videojuegos"],
            "total_resenas": (catalogo["total_resenas"] or 0)
            + predicciones["total"],
            "puntuacion_media_global": puntuacion_media,
            "percepcion_global": self._percepcion_global(
                conteos,
                puntuacion_media,
            ),
            "distribucion": self._distribucion(conteos),
        }

    def obtener_metricas_videojuego(
        self,
        videojuego_id: str,
    ) -> dict:
        videojuego = Videojuego.objects.get(id=videojuego_id)
        predicciones = self._resumen_predicciones(videojuego_id)
        total_valoraciones = (
            videojuego.numero_valoraciones
            + predicciones["valoraciones"]
        )
        suma_puntuaciones = (
            (videojuego.puntuacion_media or 0)
            * videojuego.numero_valoraciones
            + (predicciones["suma_puntuaciones"] or 0)
        )
        puntuacion_media = (
            round(suma_puntuaciones / total_valoraciones, 2)
            if total_valoraciones
            else None
        )
        conteos = {
            "positivas": videojuego.sentimientos_positivos
            + predicciones["positivas"],
            "neutrales": videojuego.sentimientos_neutrales
            + predicciones["neutrales"],
            "negativas": videojuego.sentimientos_negativos
            + predicciones["negativas"],
        }

        return {
            "videojuego_id": videojuego.id,
            "titulo": videojuego.titulo,
            "puntuacion_media": puntuacion_media,
            "numero_valoraciones": total_valoraciones,
            "percepcion_global": self._percepcion_global(
                conteos,
                puntuacion_media,
            ),
            "distribucion": self._distribucion(conteos),
        }

    def obtener_predicciones_recientes(
        self,
        limite: int = 10,
    ) -> dict:
        if limite < 1 or limite > 100:
            raise ValueError(
                "El límite debe estar comprendido entre 1 y 100."
            )

        consulta = (
            Prediccion.objects
            .select_related("videojuego")
            .order_by("-created_at")
        )

        resultados = [
            {
                "id": prediccion.id,
                "videojuego_id": prediccion.videojuego_id,
                "videojuego_titulo": prediccion.videojuego.titulo,
                "title": prediccion.title,
                "text": prediccion.text,
                "rating": prediccion.rating,
                "sentiment": prediccion.sentiment,
                "verified_purchase": prediccion.verified_purchase,
                "created_at": prediccion.created_at,
            }
            for prediccion in consulta[:limite]
        ]

        return {
            "total": consulta.count(),
            "resultados": resultados,
        }

    @staticmethod
    def _resumen_predicciones(videojuego_id: str | None = None) -> dict:
        consulta = Prediccion.objects.all()
        if videojuego_id is not None:
            consulta = consulta.filter(videojuego_id=videojuego_id)

        return consulta.aggregate(
            total=Count("id"),
            valoraciones=Count("rating"),
            suma_puntuaciones=Sum("rating"),
            positivas=Count("id", filter=Q(sentiment="positivo")),
            neutrales=Count("id", filter=Q(sentiment="neutral")),
            negativas=Count("id", filter=Q(sentiment="negativo")),
        )

    @staticmethod
    def _suma_puntuaciones_historicas() -> float:
        videojuegos = Videojuego.objects.values_list(
            "puntuacion_media",
            "numero_valoraciones",
        )
        return sum(
            (media or 0) * cantidad
            for media, cantidad in videojuegos
        )

    @staticmethod
    def _distribucion(conteos: dict) -> dict:
        total = sum(conteos.values())
        porcentajes = {
            nombre: round(conteo * 100 / total, 2) if total else 0
            for nombre, conteo in conteos.items()
        }
        return {
            **conteos,
            "porcentaje_positivas": porcentajes["positivas"],
            "porcentaje_neutrales": porcentajes["neutrales"],
            "porcentaje_negativas": porcentajes["negativas"],
        }

    @staticmethod
    def _percepcion_global(conteos: dict, puntuacion_media: float | None) -> str:
        mayor = max(conteos.values(), default=0)
        if mayor:
            dominantes = [
                sentimiento
                for sentimiento, conteo in conteos.items()
                if conteo == mayor
            ]
            if len(dominantes) == 1:
                return {
                    "positivas": "positivo",
                    "neutrales": "neutral",
                    "negativas": "negativo",
                }[dominantes[0]]

        if puntuacion_media is None:
            return "neutral"
        if puntuacion_media < 2.5:
            return "negativo"
        if puntuacion_media < 3.5:
            return "neutral"
        return "positivo"


metricas_service = MetricasService()