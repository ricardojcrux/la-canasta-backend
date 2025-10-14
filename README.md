# tu-canasta-backend
Proyecto Desarrollo 2 Universidad del Valle 2025-2

## Variables de entorno
Configura las siguientes variables en `.env` para desarrollo local o en el panel de Render:

- `SECRET_KEY`: clave segura para Django.
- `DEBUG`: `True` en local, `False` en producción.
- `ALLOWED_HOSTS`: lista separada por comas, por ejemplo `127.0.0.1,localhost`.
- `CSRF_TRUSTED_ORIGINS`: orígenes HTTPS completos requeridos en producción.
- `TIME_ZONE`: zona horaria, p. ej. `America/Bogota`.
- `DATABASE_URL`: solo necesaria cuando se use PostgreSQL en Render.

## Despliegue en Render
1. Confirma que `render.yaml` se encuentre en la raíz del servicio (`la-canasta-backend`). Render lo detectará automáticamente al conectar el repositorio.
2. En Render, crea un nuevo servicio Web y selecciona el repositorio. El plan estándar puede ser `Free` mientras desarrollas.
3. Render ejecutará los comandos definidos en `render.yaml`: instalación de dependencias y `collectstatic`. Verifica que exista un bucket `staticfiles` en el repositorio de producción si manejas archivos estáticos.
4. Desde el panel de variables de entorno en Render, define al menos `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` con el dominio de Render (`tu-canasta-backend.onrender.com`) y `CSRF_TRUSTED_ORIGINS` con la URL completa (`https://tu-canasta-backend.onrender.com`).
5. Conecta una base de datos PostgreSQL de Render y copia el `DATABASE_URL` proporcionado. El proyecto la detectará automáticamente gracias a `dj-database-url`.
6. Una vez aprovisionado el servicio, Render iniciará la aplicación usando `gunicorn tu_canasta_backend.wsgi:application`. Revisa los logs para confirmar que las migraciones y `collectstatic` se ejecutaron correctamente.

## Ejecución local
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Endpoints principales
- `GET /api/` (navegable): incluye enlaces a usuarios, productos y listas.
- `GET/POST /api/users/`: administración básica de usuarios (passwords se almacenan en hash).
- `GET/POST /api/products/`: catálogo de productos.
- `GET/POST /api/shopping-lists/`: cada usuario mantiene su propia lista. Para acceder se debe enviar el encabezado `X-USER-ID` con el identificador del usuario (también aceptado como `?user_id=`).
- `GET/POST /api/shopping-list-items/`: elementos dentro de la lista del usuario autenticado por encabezado. 
