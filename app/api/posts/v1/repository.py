"""Acceso a datos de posts (patrón Repository: SQLAlchemy aislado del router)."""

from __future__ import annotations

from typing import List, Literal, Optional, Tuple, Union

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.posts.v1.schemas import Author, PostCreate, PostUpdate, Tag
from app.models.author import AuthorOrm
from app.models.post import PostOrm
from app.models.tag import TagOrm


class PostRepository:
  def __init__(self, db: Session):
    self.db = db

  def _ensure_author_row(self, author: Union[Author, str]) -> AuthorOrm:
    if isinstance(author, Author):
      name, email = author.name, author.email
    else:
      name, email = str(author), "usuario@example.com"
    row = self.db.execute(select(AuthorOrm).where(AuthorOrm.email == email)).scalar_one_or_none()
    if row:
      return row
    row = AuthorOrm(name=name, email=email)
    self.db.add(row)
    self.db.flush()
    return row

  def _ensure_tag_rows(self, tags: List[Tag]) -> List[TagOrm]:
    out: List[TagOrm] = []
    for t in tags:
      row = self.db.execute(select(TagOrm).where(TagOrm.name == t.name)).scalar_one_or_none()
      if row:
        out.append(row)
      else:
        row = TagOrm(name=t.name)
        self.db.add(row)
        self.db.flush()
        out.append(row)
    return out

  def get(self, post_id: int) -> Optional[PostOrm]:
    return self.db.get(PostOrm, post_id)

  def get_by_id(self, post_id: int) -> Optional[PostOrm]:
    return self.db.execute(select(PostOrm).where(PostOrm.id == post_id)).scalar_one_or_none()

  def list_all(self) -> List[PostOrm]:
    return list(self.db.execute(select(PostOrm)).scalars().all())

  def list_by_tags(self, tags_lower: List[str]) -> List[PostOrm]:
    q = select(PostOrm).join(PostOrm.tags).where(func.lower(TagOrm.name).in_(tags_lower))
    return list(self.db.execute(q).unique().scalars().all())

  def search_paginated(
    self,
    search: Optional[str],
    page: int,
    per_page: int,
    order_by: Literal["id", "title"],
    direction: Literal["asc", "desc"],
  ) -> Tuple[int, List[PostOrm], int]:
    """Devuelve (total, items de la página, página efectiva tras clamp)."""
    stmt = select(PostOrm)
    if search:
      stmt = stmt.where(PostOrm.title.ilike(f"%{search}%"))

    total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

    order_col = PostOrm.id if order_by == "id" else PostOrm.title
    stmt = stmt.order_by(order_col.asc() if direction == "asc" else order_col.desc())

    if total_pages == 0:
      return total, [], current_page

    offset = (current_page - 1) * per_page
    items = list(self.db.execute(stmt.limit(per_page).offset(offset)).scalars().all())
    return total, items, current_page

  def create_entity(self, post: PostCreate) -> PostOrm:
    author_row = self._ensure_author_row(post.author)
    tag_rows = self._ensure_tag_rows(post.tags)
    new_post = PostOrm(title=post.title, content=post.content, author_id=author_row.id)
    new_post.tags = tag_rows
    self.db.add(new_post)
    return new_post

  def apply_update(self, post: PostOrm, data: PostUpdate) -> PostOrm:
    updates = data.model_dump(exclude_unset=True)
    for key, value in updates.items():
      setattr(post, key, value)
    self.db.add(post)
    return post

  def delete(self, post: PostOrm) -> None:
    self.db.delete(post)
