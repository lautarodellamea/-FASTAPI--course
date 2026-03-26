from fastapi import FastAPI, Query, Body, HTTPException, Path
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Literal, Optional, Union



app = FastAPI(title="Mini Blog", description="Esta es una API de ejemplo")

BLOG_POST = [
  {
    "id": 1,
    "title": "Mi primer post",
    "content": "Este es el contenido de mi primer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01",
    "tags": [{
      "name": "Python",
    }, {
      "name": "FastAPI",
    }]
  },
  {
    "id": 2,
    "title": "Mi segundo post",
    "content": "Este es el contenido de mi segundo post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01",
    "tags": [{
      "name": "Python",
    }, {
      "name": "FastAPI",
    }]
  },
  {
    "id": 3,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01",
        "tags": [{
      "name": "Python",
    }, {
      "name": "Cobol",
    }]
  },
  {
    "id": 4,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01",
  },
  {
    "id": 5,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 6,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 7,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 8,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 9,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 10,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 11,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 12,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  }
]

""" Modelos de datos """
class Tag(BaseModel):
  name: str = Field(..., min_length=3, max_length=50, description="El nombre del tag es requerido y debe tener entre 3 y 50 caracteres")
  
class Author(BaseModel):
  name: str = Field(..., min_length=3, max_length=50, description="El nombre del autor es requerido y debe tener entre 3 y 50 caracteres")
  email: EmailStr = Field(..., description="El email del autor es requerido y debe ser un email valido")

# usando pydantic para validar los datos
class PostBase(BaseModel):
  title: str
  content: str
  tags: Optional[List[Tag]] = Field(default_factory=list) # para assegurarme que cree una lista completamente nueva
  author: Optional[Union[Author, str]] = None

  
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
  # tags: List[Tag] = []
  tags: List[Tag] = Field(default_factory=list)
  
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
  
class PostSummary(BaseModel): # aca no podemos heredar de PostBase porque no quiero el content por ejemplo
  id: int
  title: str
  
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



""" Endpoints """

@app.get("/")
def home():
  return {"message": "Bienvenido a la API de Mini Blog de Lautaro"}


@app.get("/posts-general")
def list_posts_general():
  return {"data ": BLOG_POST}

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
  )
  ):
   
  results = BLOG_POST.copy()

  query = query or text
  
  if query:
    results = [post for post in results if query.lower() in post["title"].lower()]

  total = len(results)
  total_pages = (total + per_page - 1) // per_page
  if total_pages == 0:
    current_page = 1
  else:
    # si piden una pagina mayor al maximo, devolvemos la ultima disponible
    current_page = min(page, total_pages)

  has_next = current_page < total_pages
  has_prev = current_page > 1 and total_pages > 0


  # ordenamos siempre (haya o no filtro)
  results = sorted(results, key=lambda post: post[order_by], reverse=direction == "desc")

  if total_pages == 0:
    items = []
  else:
    start = (current_page - 1) * per_page
    end = start + per_page
    items = results[start:end]

  

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
  )
):
  tags_lower = [tag.lower() for tag in tags]

  return [
    post for post in BLOG_POST 
    if any(tag["name"].lower() in tags_lower for tag in post.get("tags", []))
  ]
 

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
), include_content: bool = Query(default=True, description="Si queremos traer el contenido del post")):
  for post in BLOG_POST:
    if post["id"] == id:
      if include_content:
        return post
      return {"id": post["id"], "title": post["title"]}
  
  raise HTTPException(status_code=404, detail="Post no encontrado")


# Metodo POST
@app.post("/posts", response_model=PostPublic, response_description="Post creado (OK)")
# def create_post(post: dict = Body(...)):
def create_post(post: PostCreate):
  new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1
  
  new_post = {"id": new_id, "title": post.title, "content": post.content, "tags": [tag.model_dump() for tag in post.tags], "author": post.author.model_dump() if post.author else None}
  BLOG_POST.append(new_post)
  
  return new_post


# Metodo PUT
@app.put("/posts/{post_id}", response_model=PostPublic, response_description="Post actualizado", response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate): # los tres puntitos indican que es obligatorio mandar el body
  for post in BLOG_POST:
    if post["id"] == post_id:
      
      # esto sirve para convertir el objeto PostUpdate a un diccionario
      # y asi poder manejarlo como tal
      payload = data.model_dump() # {title: "Nuevo titulo", content: "Nuevo contenido"}
      
      if "title" in payload:
        post["title"] = payload["title"]
      if "content" in payload:
        post["content"] = payload["content"]
      return post
  
    raise HTTPException(status_code=404, detail="Post no encontrado") # esto es para desatar un error personalizado
    # raise → Interrumpe la ejecución y lanza un error.
  
  
# Metodo DELETE
@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
  for index, post in enumerate(BLOG_POST):
    if post["id"] == post_id:
      BLOG_POST.pop(index)
      return
  
  raise HTTPException(status_code=404, detail="Post no encontrado")