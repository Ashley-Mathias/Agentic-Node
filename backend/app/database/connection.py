import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


def get_engine():
    """Create or return the cached SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={
                "options": f"-c statement_timeout={settings.sql_timeout_seconds * 1000}"
            },
        )
        logger.info("Database engine created: %s", settings.database_url.split("@")[-1])
    return _engine


def get_session_factory():
    """Create or return the cached session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionLocal


def get_session() -> Session:
    """Return a new database session. Caller is responsible for closing it."""
    factory = get_session_factory()
    return factory()
