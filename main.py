from fastapi import FastAPI, Query

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
  return {"message": "Bienvenido a la API de Mini Blog"}


# @app.get("/posts")
# def list_posts():
#   return {"data ": BLOG_POST}

# Query params
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


# Path params
@app.get("/posts/{id}")
def get_post(id: int):
  return {"data ": BLOG_POST[id]}