
import os
from pathlib import Path

from dotenv import load_dotenv

# Carga .env desde la raíz del proyecto (uvicorn no lo hace solo)
load_dotenv(Path(__file__).resolve().parent / ".env")

from datetime import datetime
from fastapi import Depends, FastAPI, Query, Body, HTTPException, Path, status
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr
from typing import List, Literal, Optional, Union

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint, create_engine, func, inspect, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, Session, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
print("Conectando a la base de datos: ", DATABASE_URL)

# engine_kwargs para pasar las configuraciones de la base de datos si llega a ocupar sqlite
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
  connect_args = {"check_same_thread": False}
  engine_kwargs["connect_args"] = connect_args

# create_engine para crear la conexion a la base de datos
# echo=True para que se muestre en la consola las consultas que se hacen a la base de datos
# future=True para que se use la nueva sintaxis de SQLAlchemy
# **engine_kwargs para que se pasen las configuraciones de la base de datos
engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)

# sessionmaker para crear la sesion de la base de datos
# autocommit=False para que no se commitee la transaccion automaticamente y tener un control explicito de las transacciones
# autoflush=False no envia cambios hasta que no se haga el commit
# bind=engine para que se bind la sesion a la base de datos
# class_=Session para que la sesion sea de tipo Session
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

class Base(DeclarativeBase):
  pass # ponerle el pass a esto es como ponerle el alias Base a DeclarativeBase

# Tabla intermedia para la relacion muchos a muchos (UN POST PUEDE TENER MUCHOS TAGS Y UN TAG PUEDE TENER MUCHOS POSTS)
post_tags = Table(
  "post_tags",
  Base.metadata,
  Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
  Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class AuthorOrm(Base):
  __tablename__ = "authors"
  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
  email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)

  # relationship es para relacionar la tabla de autores con la tabla de posts
  posts: Mapped[List["PostOrm"]] = relationship("PostOrm", back_populates="author")

class TagOrm(Base):
  __tablename__ = "tags"
  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

  posts: Mapped[List["PostOrm"]] = relationship("PostOrm", secondary=post_tags, back_populates="tags", lazy="selectin")

class PostOrm(Base):
  __tablename__ = "posts"
  # UniqueConstraint es para que el titulo sea unico en la base de datos
  __table_args__ = (UniqueConstraint("title", name="unique_post_title"),)
  # el Mapped valida el tipo de dato y el mapped_column es el nombre de la columna en la base de datos
  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
  content: Mapped[str] = mapped_column(Text, nullable=False, index=True)
  created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
  updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)


  # RELACION DE UNO A MUCHOS: columna FK (author_id) y objeto relacionado (author)
  author_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("authors.id"), nullable=True)
  author: Mapped[Optional["AuthorOrm"]] = relationship("AuthorOrm", back_populates="posts")

  tags: Mapped[List["TagOrm"]] = relationship("TagOrm", secondary=post_tags, back_populates="posts", lazy="selectin", passive_deletes=True)

Base.metadata.create_all(bind=engine) # dev crea las tablas en la base de datos en caso de que no existan, para produccion usaremos migraciones


def _ensure_sqlite_posts_author_id():
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


_ensure_sqlite_posts_author_id()


def get_db():
  db = SessionLocal()
  try:
    yield db # yield es como return pero para generadores.
    # es como haz una pausa hasta que una funcion o algo use la db y despues cierra la conexion
  finally:  
    db.close()
 
app = FastAPI(title="Mini Blog", description="Esta es una API de ejemplo")


""" Modelos de datos """
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


# usando pydantic para validar los datos
class PostBase(BaseModel):
  title: str
  content: str
  tags: Optional[List[Tag]] = Field(default_factory=list) # para assegurarme que cree una lista completamente nueva
  author: Optional[Union[Author, str]] = None

  model_config = ConfigDict(from_attributes=True)

  
class PostCreate(PostBase):
  title: Optional[str] = Field(...,
                min_length=3, 
                max_length=100,
                description="El titulo del post es requerido y debe tener entre 3 y 100 caracteres",
                json_schema_extra={"example": "Mi primer post"}
                )
  content: Optional[str] = Field(
                default="Contenido no disponible",
                min_length=10,
                max_length=1000, 
                description="El contenido del post es requerido y debe tener entre 10 y 1000 caracteres",
                json_schema_extra={"example": "Este es el contenido de mi primer post"}
                )
  tags: List[Tag] = Field(
    default_factory=default_post_tags,
    description="Si no se envía, se usa un tag por defecto.",
  )
  author: Union[Author, str] = Field(
    default_factory=default_post_author,
    description="Si no se envía, se usa un autor por defecto.",
  )
  
  # para hacer validaciones mas complejas o personalizadas, se usa el field_validator
  @field_validator("title")
  @classmethod # para que se pueda usar la calse completa y poder acceder al nombre del modelo, etc
  def not_allowed_title(cls, value: str) -> str:
    if "spam" in value.lower():
      raise ValueError("El titulo no puede contener spam")
    return value # si todo sale vbien pasa el valor que le iba a dar, en este caso el titulo
  

class PostUpdate(BaseModel):
  title: Optional[str] = Field(None, min_length=3, max_length=100, description="El titulo del post es requerido y debe tener entre 3 y 100 caracteres")
  content: Optional[str] = None
  
class PostPublic(PostBase): # aca como hereda de PostBase, ya tiene el title y el content
  id: int
  model_config = ConfigDict(from_attributes=True)


  
class PostSummary(BaseModel): # aca no podemos heredar de PostBase porque no quiero el content por ejemplo
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
  order_by: Literal["id", "title"] # es como un enum, solo puede ser id o title
  direction: Literal["asc", "desc"]
  search: Optional[str] = None
  items: List[PostPublic]


def ensure_author_row(db: Session, author: Union[Author, str]) -> AuthorOrm:
  if isinstance(author, Author):
    name, email = author.name, author.email
  else:
    name, email = str(author), "usuario@example.com"
  row = db.execute(select(AuthorOrm).where(AuthorOrm.email == email)).scalar_one_or_none()
  if row:
    return row
  row = AuthorOrm(name=name, email=email)
  db.add(row)
  db.flush()
  return row


def ensure_tag_rows(db: Session, tags: List[Tag]) -> List[TagOrm]:
  out: List[TagOrm] = []
  for t in tags:
    row = db.execute(select(TagOrm).where(TagOrm.name == t.name)).scalar_one_or_none()
    if row:
      out.append(row)
    else:
      row = TagOrm(name=t.name)
      db.add(row)
      db.flush()
      out.append(row)
  return out


""" Endpoints """

@app.get("/")
def home():
  return {"message": "Bienvenido a la API de Mini Blog de Lautaro"}


@app.get("/posts-general")
def list_posts_general(db: Session = Depends(get_db)):
  rows = db.execute(select(PostOrm)).scalars().all()
  return {"data": [PostPublic.model_validate(p, from_attributes=True) for p in rows]}

# Query params (define como queremos ese recurso, lo quiero traer filtrado, ordenado, etc)
@app.get("/posts", response_model=PaginatedPosts) # responder auna lista de muchos PostPublic
def list_posts(
  text: Optional[str] = Query(
    default=None,
    deprecated=True, # para decir que este query param ya no se va a usar, es para que no se muestre en la documentacion, le damos tiempo para que los usuarios sepan que ya no se va a usar y empiecen a migrar a la nueva forma de buscar
    description="Texto para buscar en el titulo (deprecated)",
  ),
  query: Optional[str] = Query(
    default=None,
    description="Texto para buscar en el titulo",
    alias="search", # para poder cambiar como usaremos el query param en la url, en este caso search en vez de query, esto para no tener que cambiarlo en todo el codigo, a nivel de codigo es query pero en la url sera search
    min_length=3,
    max_length=50,
    # Acepta: letras a-z, A-Z, dígitos, guión bajo (_),
    # y vocales con tilde (á é í ó ú Á É Í Ó Ú Ü ü)
    # No permite espacios, símbolos ni caracteres especiales
    # Debe tener al menos 1 carácter del set definido
    pattern=r"^[\w\sáéíóúÁÉÍÓÚÜü-]+$"
  ),
  # Pagination
  per_page: int = Query(
    default=10,
    ge=1,
    le=50,
    description="Cantidad de posts a retornar (1-50)"
  ),
  page: int = Query(
    default=1,
    ge=1,
    description="Pagina a retornar (1-n)"
  ),
  order_by: Literal["id", "title"] = Query(
    default="id",
    description="Campo por el cual ordenar los posts"
  ),
    direction: Literal["asc", "desc"] = Query(
    default="asc",
    description="Orden de la ordenacion"
  ),
  db: Session = Depends(get_db)
  ):
   
  results = select(PostOrm)

  query = query or text
  
  if query:
    results = results.where(PostOrm.title.ilike(f"%{query}%"))

  total = db.scalar(select(func.count()).select_from(results.subquery())) or 0
  total_pages = (total + per_page - 1) // per_page

  current_page = 1 if total_pages == 0 else min(page, total_pages)

  if order_by == "id":
   order_col = PostOrm.id
  elif order_by == "title":
    order_col = PostOrm.title

  results = results.order_by(order_col.asc() if direction == "asc" else order_col.desc())

  if total_pages == 0:
    items = []
  else:
    start = (current_page - 1) * per_page
    items = db.execute(results.limit(per_page).offset(start)).scalars().all()

  
  has_next = current_page < total_pages
  has_prev = current_page > 1 and total_pages > 0

  return PaginatedPosts(
    total=total,
    total_pages=total_pages,
    has_next=has_next,
    has_prev=has_prev,
    order_by=order_by,
    direction=direction,
    search=query,
    page=current_page,
    per_page=per_page,
    items=items
  )


@app.get("/posts/by-tag", response_model=List[PostPublic])
def filter_by_tags(
  tags: List[str] = Query(
    ...,
    min_length=1,
    description="Una o mas tags para filtrar. Ejemplo: ?tags=python&tags=javascript"
  ),
  db: Session = Depends(get_db),
):
  tags_lower = [tag.lower() for tag in tags]
  q = select(PostOrm).join(PostOrm.tags).where(func.lower(TagOrm.name).in_(tags_lower))
  rows = db.execute(q).unique().scalars().all()
  return [PostPublic.model_validate(p, from_attributes=True) for p in rows]
 

# Path params (forma parte de la url directamente, trae un recurso especifico)
# el include_content es un query param
# El Path forma parte de la URL, mientras que el Query Param va después del ?
@app.get("/posts/{id}", response_model=Union[PostPublic, PostSummary], response_description="Post encontrado") # el union es para se pueda evaluar que la respuesta sea de tipo PostPublic y PostSummary (en caso de que no tenga algo va con el segundo)
# para los query params (/posts?query=...) se usa Query y para los path params se usa Path (/posts/1)
def get_post(id: int = Path(
  ..., # para decir que esperamos contenido y por lo tanto se haga obligatorio
  ge=1, # para decir que el id debe ser mayor o igual a 1
  title="ID del post",
  description="El id del post es requerido y debe ser un numero entero mayor o igual a 1.",
  json_schema_extra={"example": 1}
), include_content: bool = Query(default=True, description="Si queremos traer el contenido del post"), db: Session = Depends(get_db)):


  # si el id no fuera un primary key, podriamos hacer la busqueda de esta forma.
  # esto es mas flexible y poder hacer mas cosas como buscar por otros campos.
  # podriamos agregar joins, filtros, etc.
  post_find = select(PostOrm).where(PostOrm.id == id)
  post = db.execute(post_find).scalar_one_or_none()
  
  # como es un primary key, podemos usar el get directamente.
  # post = db.get(PostOrm, id)

  if not post:
    raise HTTPException(status_code=404, detail="Post no encontrado")

  if include_content:
    return PostPublic.model_validate(post, from_attributes=True)

  return PostSummary.model_validate(post, from_attributes=True)

  


# Metodo POST
@app.post("/posts", response_model=PostPublic, response_description="Post creado (OK)", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):

  author_row = ensure_author_row(db, post.author)
  tag_rows = ensure_tag_rows(db, post.tags)
  new_post = PostOrm(title=post.title, content=post.content, author_id=author_row.id)
  new_post.tags = tag_rows

  try:
    db.add(new_post)
    db.commit() # commit para guardar los cambios en la base de datos
    db.refresh(new_post)
    return new_post
  except IntegrityError as e:
    db.rollback()
    raise HTTPException(status_code=409, detail=f"Error al crear el post: El titulo ya existe. {str(e)}")
  except SQLAlchemyError as e: # SQLAlchemyError es una excepcion de SQLAlchemy
    db.rollback()
    raise HTTPException(status_code=500, detail=f"Error al crear el post: {str(e)}")

  # new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1
  
  # new_post = {"id": new_id, "title": post.title, "content": post.content, "tags": [tag.model_dump() for tag in post.tags], "author": post.author.model_dump() if post.author else None}
  # BLOG_POST.append(new_post)
  
  # return new_post


# Metodo PUT
@app.put("/posts/{post_id}", response_model=PostPublic, response_description="Post actualizado", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)): # los tres puntitos indican que es obligatorio mandar el body

  post = db.get(PostOrm, post_id)

  if not post:
    raise HTTPException(status_code=404, detail="Post no encontrado")

  # exclude_unset=True evita poner null en campos que no se envian
  updates = data.model_dump(exclude_unset=True)
  

  for key, value in updates.items():
    setattr(post, key, value)

  db.add(post)
  db.commit()
  db.refresh(post)
  return post
  
# Metodo DELETE
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):

  post = db.get(PostOrm, post_id)
  if not post:
    raise HTTPException(status_code=404, detail="Post no encontrado")

  db.delete(post)
  db.commit()
  return