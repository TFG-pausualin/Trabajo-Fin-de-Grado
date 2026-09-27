from app.backend.config.base import ConfiguracionBase


class ConfiguracionLocal(ConfiguracionBase):
    entorno: str = "local"
    debug: bool = True