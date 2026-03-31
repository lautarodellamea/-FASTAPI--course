"""Entidad Author (ORM)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
  from .post import PostOrm


class AuthorOrm(Base):
  __tablename__ = "authors"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
  email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)

  posts: Mapped[List["PostOrm"]] = relationship("PostOrm", back_populates="author")
