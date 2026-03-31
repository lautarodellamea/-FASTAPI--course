

from pathlib import Path

from dotenv import load_dotenv

# Carga .env desde la raíz del proyecto (uvicorn no lo hace solo)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI

from app.api.posts.v1.router import router as posts_router
from app.core.db import init_db

init_db()

app = FastAPI(title="Mini Blog", description="Esta es una API de ejemplo")
app.include_router(posts_router)


@app.get("/")
def home():
    return {"message": "Bienvenido a la API de Mini Blog de Lautaro"}
