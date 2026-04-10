"""
app/db/session.py — SQLAlchemy エンジン + セッション DI
DB_URL は config.py から読む。SQLite の場合は check_same_thread=False が必要。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

# connect_args は SQLite 専用オプション。他 DB に移行する際は削除する。
_connect_args = {"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {}

engine = create_engine(settings.DB_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI Depends で使う DB セッション DI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
