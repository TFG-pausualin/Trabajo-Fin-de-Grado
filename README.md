# Trabajo-Fin-de-Grado
Análisis de la percepción del consumidor sobre videojuegos mediante técnicas de procesamiento de lenguaje natural. 

## Iniciar el proyecto en Windows

Con Docker Desktop, Python, Node.js y npm instalados, ejecuta desde PowerShell en la raíz del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar-proyecto.ps1
```

El script crea `.env` desde `.env.example` si aún no existe, prepara los entornos virtuales/dependencias que falten, levanta PostgreSQL, aplica las migraciones y abre el backend y el frontend en ventanas separadas. Si crea `.env`, revisa sus valores antes de usar el proyecto.

Direcciones locales:

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000
- Documentación de la API: http://127.0.0.1:8000/docs

Para detener PostgreSQL, ejecuta `docker compose down`; cierra también las ventanas de backend y frontend.
