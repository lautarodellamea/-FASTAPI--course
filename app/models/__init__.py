"""Modelos ORM SQLAlchemy."""
from .author import AuthorOrm
from .post import PostOrm
from .tag import TagOrm

__all__ = ["AuthorOrm", "PostOrm", "TagOrm"]