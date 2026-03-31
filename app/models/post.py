"""Entidad Post (ORM)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.tag import post_tags

if TYPE_CHECKING:
    from .author import AuthorOrm
    from .tag import TagOrm


class PostOrm(Base):
  __tablename__ = "posts"
  __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
  content: Mapped[str] = mapped_column(Text, nullable=False, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)

  author_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("authors.id"), nullable=True)
  author: Mapped[Optional["AuthorOrm"]] = relationship("AuthorOrm", back_populates="posts")

  tags: Mapped[List["TagOrm"]] = relationship(
    "TagOrm",
    secondary=post_tags,
    back_populates="posts",
    lazy="selectin",
    passive_deletes=True,
  )
