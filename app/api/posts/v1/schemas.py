"""Esquemas Pydantic (DTO) para la API de posts: entrada, salida y paginación."""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Tag(BaseModel):
  name: str = Field(..., min_length=3, max_length=50, description="El nombre del tag es requerido y debe tener entre 3 y 50 caracteres")

  model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
  name: str = Field(..., min_length=3, max_length=50, description="El nombre del autor es requerido y debe tener entre 3 y 50 caracteres")
  email: EmailStr = Field(..., description="El email del autor es requerido y debe ser un email valido")

  model_config = ConfigDict(from_attributes=True)


def default_post_author() -> Author:
  """Valores por defecto si el body no incluye `author`."""
  return Author(name="Sin nombre", email="usuario@example.com")


def default_post_tags() -> List[Tag]:
  """Lista por defecto si el body no incluye `tags`."""
  return [Tag(name="general")]


class PostBase(BaseModel):
  title: str
  content: str
  tags: Optional[List[Tag]] = Field(default_factory=list)
  author: Optional[Union[Author, str]] = None

  model_config = ConfigDict(from_attributes=True)


class PostCreate(PostBase):
  title: Optional[str] = Field(
    ...,
    min_length=3,
    max_length=100,
    description="El titulo del post es requerido y debe tener entre 3 y 100 caracteres",
    json_schema_extra={"example": "Mi primer post"},
  )
  content: Optional[str] = Field(
    default="Contenido no disponible",
    min_length=10,
    max_length=1000,
    description="El contenido del post es requerido y debe tener entre 10 y 1000 caracteres",
    json_schema_extra={"example": "Este es el contenido de mi primer post"},
  )
  tags: List[Tag] = Field(
    default_factory=default_post_tags,
    description="Si no se envía, se usa un tag por defecto.",
  )
  author: Union[Author, str] = Field(
    default_factory=default_post_author,
    description="Si no se envía, se usa un autor por defecto.",
  )

  @field_validator("title")
  @classmethod
  def not_allowed_title(cls, value: str) -> str:
    if "spam" in value.lower():
      raise ValueError("El titulo no puede contener spam")
    return value


class PostUpdate(BaseModel):
  title: Optional[str] = Field(None, min_length=3, max_length=100, description="El titulo del post es requerido y debe tener entre 3 y 100 caracteres")
  content: Optional[str] = None


class PostPublic(PostBase):
  id: int
  model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
  id: int
  title: str

  model_config = ConfigDict(from_attributes=True)


class PaginatedPosts(BaseModel):
  page: int
  per_page: int
  total: int
  total_pages: int
  has_next: bool
  has_prev: bool
  order_by: Literal["id", "title"]
  direction: Literal["asc", "desc"]
  search: Optional[str] = None
  items: List[PostPublic]
