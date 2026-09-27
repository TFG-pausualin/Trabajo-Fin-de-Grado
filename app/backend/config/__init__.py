import os

from dotenv import load_dotenv

from app.backend.config.base import RUTA_ENV
from app.backend.config.local import ConfiguracionLocal
from app.backend.config.produccion import (
    ConfiguracionProduccion
)


load_dotenv(RUTA_ENV)


entorno = os.getenv(
    "APP_ENV",
    "local"
).strip().lower()


if entorno == "produccion":
    configuracion = ConfiguracionProduccion()
else:
    configuracion = ConfiguracionLocal()


__all__ = ["configuracion"]
