"""Rutas HTTP del recurso posts (listado, búsqueda, CRUD, filtros)."""

from typing import List, Literal, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.posts.v1.repository import PostRepository
from app.api.posts.v1.schemas import (
    PaginatedPosts,
    PostCreate,
    PostPublic,
    PostSummary,
    PostUpdate,
)
from app.core.db import get_db

router = APIRouter(tags=["posts"])


@router.get("/posts-general")
def list_posts_general(db: Session = Depends(get_db)):
    repo = PostRepository(db)
    rows = repo.list_all()
    return {"data": [PostPublic.model_validate(p, from_attributes=True) for p in rows]}


@router.get("/posts", response_model=PaginatedPosts)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        deprecated=True,
        description="Texto para buscar en el titulo (deprecated)",
    ),
    query: Optional[str] = Query(
        default=None,
        description="Texto para buscar en el titulo",
        alias="search",
        min_length=3,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚÜü-]+$",
    ),
    per_page: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Cantidad de posts a retornar (1-50)",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Pagina a retornar (1-n)",
    ),
    order_by: Literal["id", "title"] = Query(
        default="id",
        description="Campo por el cual ordenar los posts",
    ),
    direction: Literal["asc", "desc"] = Query(
        default="asc",
        description="Orden de la ordenacion",
    ),
    db: Session = Depends(get_db),
):
    repo = PostRepository(db)
    search = query or text
    total, items, current_page = repo.search_paginated(
        search=search,
        page=page,
        per_page=per_page,
        order_by=order_by,
        direction=direction,
    )
    total_pages = (total + per_page - 1) // per_page if per_page else 0
    has_next = current_page < total_pages
    has_prev = current_page > 1 and total_pages > 0

    return PaginatedPosts(
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        order_by=order_by,
        direction=direction,
        search=search,
        page=current_page,
        per_page=per_page,
        items=items,
    )


@router.get("/posts/by-tag", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=1,
        description="Una o mas tags para filtrar. Ejemplo: ?tags=python&tags=javascript",
    ),
    db: Session = Depends(get_db),
):
    tags_lower = [tag.lower() for tag in tags]
    repo = PostRepository(db)
    rows = repo.list_by_tags(tags_lower)
    return [PostPublic.model_validate(p, from_attributes=True) for p in rows]


@router.get(
    "/posts/{id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post encontrado",
)
def get_post(
    id: int = Path(
        ...,
        ge=1,
        title="ID del post",
        description="El id del post es requerido y debe ser un numero entero mayor o igual a 1.",
        json_schema_extra={"example": 1},
    ),
    include_content: bool = Query(
        default=True, description="Si queremos traer el contenido del post"
    ),
    db: Session = Depends(get_db),
):
    repo = PostRepository(db)
    post = repo.get_by_id(id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@router.post(
    "/posts",
    response_model=PostPublic,
    response_description="Post creado (OK)",
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    repo = PostRepository(db)
    new_post = repo.create_entity(post)

    try:
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Error al crear el post: El titulo ya existe. {str(e)}",
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al crear el post: {str(e)}"
        )


@router.put(
    "/posts/{post_id}",
    response_model=PostPublic,
    response_description="Post actualizado",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    repo = PostRepository(db)
    post = repo.get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    repo.apply_update(post, data)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    repo = PostRepository(db)
    post = repo.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")

    repo.delete(post)
    db.commit()
    return
