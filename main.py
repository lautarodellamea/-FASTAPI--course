from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union

app = FastAPI(title="Mini Blog", description="Esta es una API de ejemplo")

BLOG_POST = [
  {
    "id": 1,
    "title": "Mi primer post",
    "content": "Este es el contenido de mi primer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 2,
    "title": "Mi segundo post",
    "content": "Este es el contenido de mi segundo post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  },
  {
    "id": 3,
    "title": "Mi tercer post",
    "content": "Este es el contenido de mi tercer post",
    "author": "Juan Perez",
    "created_at": "2021-01-01",
    "updated_at": "2021-01-01"
  }
]

class Tag(BaseModel):
  name: str = Field(..., min_length=3, max_length=50, description="El nombre del tag es requerido y debe tener entre 3 y 50 caracteres")
  
class Author(BaseModel):
  name: str = Field(..., min_length=3, max_length=50, description="El nombre del autor es requerido y debe tener entre 3 y 50 caracteres")
  email: str = Field(..., format="email", description="El email del autor es requerido y debe ser un email valido")

# usando pydantic para validar los datos
class PostBase(BaseModel):
  title: str
  content: str
  tags: Optional[List[Tag]] = []
  author: Optional[Author] = None

  
class PostCreate(PostBase):
  title: Optional[str] = Field(...,
                min_length=3, 
                max_length=100,
                description="El titulo del post es requerido y debe tener entre 3 y 100 caracteres",
                example=["Mi primer post"]
                )
  content: Optional[str] = Field(
                default="Contenido no disponible",
                min_length=10,
                max_length=1000, 
                description="El contenido del post es requerido y debe tener entre 10 y 1000 caracteres",
                example=["Este es el contenido de mi primer post"]
                )
  tags: List[Tag] = []
  
  # para haver validaciones mas complejas o personalizadas, se usa el field_validator
  @field_validator("title")
  @classmethod # para que se pueda usar la calse completa y poder acceder al nombre del modelo, etc
  def not_allowed_title(cls, value: str) -> str:
    if "spam" in value.lower():
      raise ValueError("El titulo no puede contener spam")
    return value # si todo sale vbien pasa el valor que le iba a dar, en este caso el titulo
  

class PostUpdate(BaseModel):
  title: Optional[str] = None
  content: Optional[str] = None
  
class PostPublic(PostBase): # aca como hereda de PostBase, ya tiene el title y el content
  id: int
  
class PostSummary(BaseModel): # aca no podemos heredar de PostBase porque no quiero el content por ejemplo
  id: int
  title: str
  
  

  


@app.get("/")
def home():
  return {"message": "Bienvenido a la API de Mini Blog de Lautaro"}


@app.get("/posts-general")
def list_posts_general():
  return {"data ": BLOG_POST}

# Query params (define como queremos ese recurso, lo quiero traer filtrado, ordenado, etc)
@app.get("/posts", response_model=List[PostPublic]) # responder auna lista de muchos PostPublic
def list_posts(query: str | None = Query(default=None, description="Texto para buscar en el titulo")):
  
  if query:
    results = [post for post in BLOG_POST if query.lower() in post["title"].lower()]
    return results
  
  return BLOG_POST


# Path params (forma parte de la url directamente, trae un recurso especifico)
# el include_content es un query param
# El Path forma parte de la URL, mientras que el Query Param va después del ?
@app.get("/posts/{id}", response_model=Union[PostPublic, PostSummary], response_description="Post encontrado") # el union es para se pueda evaluar que la respuesta sea de tipo PostPublic y PostSummary (en caso de que no tenga algo va con el segundo)
def get_post(id: int, include_content: bool = Query(default=True, description="Si queremos traer el contenido del post")):
  for post in BLOG_POST:
    if post["id"] == id:
      if include_content:
        return post
      return {"data": {"id": post["id"], "title": post["title"]}}
  
  return HTTPException(status_code=404, detail="Post no encontrado")


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