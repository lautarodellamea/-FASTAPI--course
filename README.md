# Mini Blog API

Una API simple construida con FastAPI que permite gestionar posts de blog.

## Características

- ✅ Listar todos los posts
- ✅ Buscar posts por título
- ✅ Obtener post por ID
- ✅ API documentada automáticamente

## Instalación

1. Clona el repositorio:

```bash
git clone <tu-repositorio-url>
cd first-steps
```

2. Crea un entorno virtual:

```bash
python -m venv venv
```

3. Activa el entorno virtual:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación:

```bash
uvicorn main:app --reload
```

La API estará disponible en: http://localhost:8000

## Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

- `GET /` - Página de bienvenida
- `GET /posts` - Listar todos los posts
- `GET /posts?query=texto` - Buscar posts por título
- `GET /posts/{id}` - Obtener post por ID

## Tecnologías

- FastAPI
- Python 3.8+
- Uvicorn
