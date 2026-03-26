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
source venv/Scripts/activate
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

# Sección 01

## Temas de esta sección

- ¿Qué es FastAPI y por qué aprenderlo?
- Documentación y enlaces importantes
- Instalación de FastAPI
- Nuestro primer endpoint (GET)
- Query Params
- Path Params
- Métodos HTTP y status code
- Endpoint POST
- Endpoint PUT
- Endpoint DELETE
- Documentación automática

## Enlaces

Durante las clases podrás encontrar algunos enlaces adjuntos, pero puedes consultarlos antes o usar este artículo como referencia para acceder a ellos más fácil:

- [FastAPI — Documentación](https://fastapi.tiangolo.com/)
- [Pydantic — Documentación](https://docs.pydantic.dev/latest/)
- [JSON Schema — Sitio oficial](https://json-schema.org/)

# Sección 2

Hola, a todas y a todos.

En esta sección se tratarán los siguientes temas:

- ¿Qué es Pydantic y por qué lo usa FastAPI?
- Pydantic
- Modelos básicos con Pydantic
- Validaciones automáticas con Pydantic
- Campos opcionales y valores por defecto
- Field y validaciones avanzadas
- Validaciones personalizadas
- Modelos de respuesta
- Métodos anidados
