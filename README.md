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
.venv\Scripts\activate || source .venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Funcionalidades clave
- Registro de usuarios y productos personalizados para construir el inventario base.
- Gestión de múltiples listas de compras por usuario, cada una con nombre, fecha objetivo y presupuesto opcional.
- Seguimiento del progreso de compra con conteo de ítems pendientes/comprados y cálculo automático de gasto total vs. presupuesto.
- Control granular de productos por lista incluyendo cantidad, precio unitario e indicador `is_purchased`.

## Endpoints principales
- `GET /api/` (navegable): incluye enlaces a usuarios, productos, listas y elementos.
- `GET/POST /api/users/`: CRUD básico de usuarios; las contraseñas se almacenan con hash.
- `GET/POST /api/products/`: catálogo de productos.
- `GET/POST /api/shopping-lists/`: cada usuario mantiene **múltiples** listas. Requiere `X-USER-ID` o `?user_id=`. Campos relevantes en `POST/PUT/PATCH`:
  - `title`: nombre de la lista.
  - `target_date`: fecha planeada de compra (`YYYY-MM-DD`).
  - `budget`: presupuesto máximo (`Decimal` opcional).
- `GET/POST /api/shopping-list-items/`: elementos asociados. Requiere el mismo encabezado/parámetro. Campos relevantes:
  - `shopping_list`: id de la lista destino (debe pertenecer al usuario autenticado).
  - `product`: id del producto.
  - `quantity`, `unit_price`, `is_purchased`.

Todos los listados devuelven métricas agregadas (`total_cost`, `total_spent`, `remaining_budget`, etc.) para apoyar el control de gastos en tiempo real.
