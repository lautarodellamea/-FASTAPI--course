"""Conexión a la base: URL, motor, sesiones, Base declarativa y dependencia get_db."""

import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
print("Conectando a la base de datos: ", DATABASE_URL)

engine_kwargs: dict = {}
if DATABASE_URL.startswith("sqlite"):
  engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


class Base(DeclarativeBase):
  pass


def _ensure_sqlite_posts_author_id() -> None:
  if not DATABASE_URL.startswith("sqlite"):
    return
  ins = inspect(engine)
  if not ins.has_table("posts"):
    return
  cols = {c["name"] for c in ins.get_columns("posts")}
  if "author_id" in cols:
    return
  with engine.begin() as conn:
    conn.execute(text("ALTER TABLE posts ADD COLUMN author_id INTEGER"))


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


def init_db() -> None:
  """Crea tablas (dev) y aplica migración mínima SQLite si existe tabla vieja sin author_id."""
  Base.metadata.create_all(bind=engine)
  _ensure_sqlite_posts_author_id()
