"""Punto de entrada para uvicorn: `uvicorn main:app` desde la raíz del repo."""

from app.main import app

__all__ = ["app"]
