# Blog Personal

Blog personal con Django. Desplegado en `joanbonoprog.es/blog`.

## Stack

- Python + Django
- Pico CSS
- SQLite (local) / PostgreSQL (producción)
- Dokploy + Docker + Traefik

## Requisitos

- Python 3.12
- Docker (para producción)

## Setup local

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # Rellenar variables
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Variables de entorno

Crear `.env` en la raíz (ver `.env.example`):

```
DJANGO_ENV=development
SECRET_KEY=clave-local-cualquiera
DEBUG=True
```

En producción, las variables se configuran desde el panel de Dokploy.

## Estructura

```
blog/
├── config/          # Settings, urls, wsgi
├── posts/           # App principal (modelos, vistas, urls, admin)
├── templates/
├── static/
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Endpoints

| Ruta | Descripción |
|---|---|
| `/` | Lista de posts |
| `/<slug>/` | Post individual |
| `/api/recent/` | JSON con los 3 últimos posts (para el portfolio Astro) |
| `/admin/` | Panel de administración |

## Despliegue

1. Configurar variables de entorno en Dokploy
2. Apuntar el servicio a este repo
3. Traefik gestiona el routing hacia `/blog` automáticamente

## Base de datos

- **Local:** SQLite (`db.sqlite3`, ignorado en Git)
- **Producción:** PostgreSQL via red interna Docker en Dokploy
