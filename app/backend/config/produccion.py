from app.backend.config.base import ConfiguracionBase


class ConfiguracionProduccion(ConfiguracionBase):
    entorno: str = "produccion"
    debug: bool = False