from fastapi import FastAPI, Query, Body, HTTPException

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


@app.get("/")
def home():
  return {"message": "Bienvenido a la API de Mini Blog de Lautaro"}


@app.get("/posts-general")
def list_posts_general():
  return {"data ": BLOG_POST}

# Query params (define como queremos ese recurso, lo quiero traer filtrado, ordenado, etc)
@app.get("/posts")
def list_posts(query: str | None = Query(default=None, description="Texto para buscar en el titulo")):
  
  if query:
   results = []
   
  #  podemos simplificar todo el if con un list comprehension
  # results = [post for post in BLOG_POST if query.lower() in post["title"].lower()]
  
  #  con un for seria 
   for post in BLOG_POST:
      if query.lower() in post["title"].lower():
        results.append(post)

   return {"data ": results, "query": query}
  
  return {"data ": BLOG_POST}


# Path params (forma parte de la url directamente, trae un recurso especifico)
# el include_content es un query param
# El Path forma parte de la URL, mientras que el Query Param va después del ?
@app.get("/posts/{id}")
def get_post(id: int, include_content: bool = Query(default=True, description="Si queremos traer el contenido del post")):
  for post in BLOG_POST:
    if post["id"] == id:
      if include_content:
        return {"data": post}
      return {"data": {"id": post["id"], "title": post["title"]}}
  
  return {"message": "Post no encontrado"}


# Metodo POST
@app.post("/posts")
def create_post(post: dict = Body(...)):
  if "title" not in post or "content" not in post:
    return {"error": "El post debe tener un titulo y un contenido"}
  
  if not str(post["title"]).strip() or not str(post["content"]).strip():
    return {"error": "El titulo y contenido no pueden estar vacios"}
  
  new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1
  new_post = {"id": new_id, "title": post["title"], "content": post["content"], "author": "Lautaro", "created_at": "2021-01-01", "updated_at": "2021-01-01"}
  
  BLOG_POST.append(new_post)
  return {"message": "Post creado exitosamente", "data": new_post}


# Metodo PUT
@app.put("/posts/{post_id}")
def update_post(post_id: int, data: dict = Body(...)): # los tres puntitos indican que es obligatorio mandar el body
  for post in BLOG_POST:
    if post["id"] == post_id:
      if "title" in data:
        post["title"] = data["title"]
      if "content" in data:
        post["content"] = data["content"]
      post["updated_at"] = "2021-01-01"
      return {"message": "Post actualizado exitosamente", "data": post}
  
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