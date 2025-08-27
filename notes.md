# Primeros Pasos con FastAPI

## 1. Instalación del Entorno Virtual

```bash
python -m venv venv
```

## 2. Activación del Entorno Virtual

Para acceder al entorno virtual:

```bash
source venv/Scripts/activate
```

**Nota**: Debe aparecer `(venv)` en la consola, indicando que el entorno virtual está activo.

## 3. Verificar Paquetes Instalados

Con `pip list` podemos ver qué paquetes están instalados en el entorno:

```bash
pip list
```

## 4. Instalación de FastAPI

Instalar FastAPI con todas las dependencias estándar:

```bash
pip install "fastapi[standard]"
```

## 5. Levantar servidor

```bash
fastapi run main.py # para produccion
fastapi dev main.py # para desarrollo
```

En muchos casos se levanta el servidor con uvicorn

```bash
uvicorn main:app --reload --port 9000
```
