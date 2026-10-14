# Análisis de sentimiento de reseñas de videojuegos

Trabajo Fin de Grado sobre la percepción de los consumidores de videojuegos mediante procesamiento del lenguaje natural. El proyecto combina reseñas históricas con opiniones enviadas desde la aplicación, las clasifica como positivas, neutrales o negativas y permite consultar los resultados por videojuego.

## Funcionalidades

- Catálogo de videojuegos con búsqueda, etiquetas de sentimiento y puntuación media.
- Consulta y filtrado de reseñas de un videojuego por tipo de opinión.
- Envío de nuevas reseñas y clasificación de su sentimiento.
- Panel de estadísticas globales y por videojuego.
- API REST documentada con Swagger y ReDoc.
- Notebooks para explorar y procesar los datos y entrenar/evaluar modelos.

## Tecnologías

- **Frontend:** React, TypeScript y Vite.
- **Backend:** Django y Django REST Framework.
- **Base de datos:** PostgreSQL, ejecutado con Docker Compose.
- **Procesamiento del lenguaje:** spaCy, TF-IDF y un clasificador SVM de scikit-learn.
- **Datos históricos:** archivos Parquet.

## Requisitos previos

- Python compatible con las versiones indicadas en `requirements.txt`.
- Node.js y npm.
- Docker Desktop con Docker Compose.

## Puesta en marcha en Windows

Ejecuta los siguientes pasos desde PowerShell. La primera vez, crea el archivo local de configuración:

```powershell
Copy-Item .env.example .env
```

Revisa `.env` y ajusta la configuración de PostgreSQL si es necesario. Este archivo contiene configuración local y no debe compartirse.

### 1. Instalar las dependencias del backend

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno virtual, permite scripts solo para la sesión actual y vuelve a activarlo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Iniciar PostgreSQL

Con Docker Desktop abierto, desde la raíz del repositorio:

```powershell
docker compose up -d postgres
```

### 3. Preparar e iniciar el backend

En la misma terminal, activa el entorno virtual si aún no está activado:

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location backend
python manage.py migrate
python manage.py import_game_data
python manage.py runserver 127.0.0.1:8000
```

La importación necesita los archivos de metadatos y las reseñas etiquetadas indicados en la sección [Datos y artefactos necesarios](#datos-y-artefactos-necesarios). Si la base de datos ya contiene el catálogo, no hace falta repetirla.

### 4. Instalar e iniciar el frontend

Abre otra terminal en la raíz del repositorio:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Abre la dirección que indique Vite, normalmente <http://localhost:5173>.

## Datos y artefactos necesarios

El repositorio incluye los datos preparados y los modelos necesarios para ejecutar la aplicación. Se almacenan directamente en Git, por lo que clonar el repositorio descarga aproximadamente 1,1 GB de datos.

- Los metadatos preparados en `data/provisional/metadatos_videojuegos.parquet`.
- Los bloques Parquet originales en `data/procesado/resenas_sin_duplicados/`.
- Sus bloques etiquetados correspondientes en `data/procesado/resenas_etiquetadas/`.
- El vectorizador TF-IDF en `models/primera_iteracion/vectorizacion/vectorizador_tfidf.joblib`.
- El modelo SVM en `models/segunda_iteracion/svm/modelo_optimizado/modelo_svm_optimizado.joblib`.

Los bloques Parquet originales y etiquetados deben corresponder entre sí. Los artefactos del clasificador deben ser los generados para este proyecto y compatibles entre ellos.

El archivo de metadatos original `data/raiz/meta_Video_Games.jsonl.gz` no se incluye: sus 103,10 MB superan el límite de 100 MB por archivo de GitHub. Solo hace falta para repetir el procesamiento de los datos; la aplicación desplegada utiliza los metadatos preparados incluidos arriba. Para reproducir ese procesamiento, descarga el archivo de metadatos de la categoría Video Games del conjunto [Amazon Reviews'23](https://amazon-reviews-2023.github.io/) y guárdalo con ese nombre en `data/raiz/`.

## Direcciones y API

- Aplicación web: <http://localhost:5173>
- API: <http://127.0.0.1:8000/api/>
- Swagger: <http://127.0.0.1:8000/docs/>
- ReDoc: <http://127.0.0.1:8000/redoc/>
- Esquema OpenAPI: <http://127.0.0.1:8000/api/schema/>

Endpoints principales:

| Método | Endpoint | Uso |
| --- | --- | --- |
| `GET` | `/api/videojuegos/` | Listar y buscar videojuegos. |
| `GET` | `/api/videojuegos/<id>/` | Consultar la ficha de un videojuego. |
| `GET` | `/api/resenas/?videojuego=<id>` | Consultar sus reseñas. |
| `GET` | `/api/resenas/?videojuego=<id>&sentimiento=negativo` | Filtrar reseñas por `positivo`, `neutral` o `negativo`. |
| `POST` | `/api/predicciones/` | Enviar una reseña para clasificarla. |
| `GET` | `/api/metricas/` | Consultar las métricas globales. |
| `GET` | `/api/metricas/videojuegos/<id>/` | Consultar las métricas de un videojuego. |

Consulta Swagger para ver los parámetros, formatos de respuesta y validaciones de cada endpoint.

## Pruebas y comprobaciones

Con el entorno virtual activado, desde `backend/`:

```powershell
python manage.py test
```

Desde `frontend/`:

```powershell
npm run build
npm run lint
```

## Estructura del repositorio

```text
backend/       API, modelos, vistas y pruebas de Django
frontend/      Aplicación web React y TypeScript
data/          Datos y bloques Parquet procesados (locales)
models/        Modelos entrenados y artefactos de vectorización (locales)
notebooks/     Análisis, preparación de datos y experimentos
reports/       Figuras e informes generados
```

## Detener los servicios

- Detén los servidores de desarrollo con `Ctrl+C` en sus respectivas terminales.
- Detén PostgreSQL desde la raíz del proyecto:

```powershell
docker compose down
```

La configuración incluida está pensada para desarrollo local; no uses el servidor de desarrollo de Django ni las credenciales de ejemplo en producción.
