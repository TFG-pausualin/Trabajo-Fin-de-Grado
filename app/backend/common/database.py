from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.backend.config import configuracion


engine = create_engine(
    configuracion.database_url,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def obtener_sesion() -> Generator[Session, None, None]:
    sesion = SessionLocal()

    try:
        yield sesion
    finally:
        sesion.close()