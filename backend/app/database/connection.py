from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from backend.app.core.config import settings


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

Base = declarative_base()