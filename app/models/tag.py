"""Entidad Tag y tabla intermedia post_tags (relación muchos a muchos con Post)."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
  from post import PostOrm

post_tags = Table(
  "post_tags",
  Base.metadata,
  Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
  Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class TagOrm(Base):
  __tablename__ = "tags"
  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

  posts: Mapped[List["PostOrm"]] = relationship(
    "PostOrm",
    secondary=post_tags,
    back_populates="tags",
    lazy="selectin",
  )
