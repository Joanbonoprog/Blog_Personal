# Personal Blog

Personal blog built with Django. Deployed at `joanbonoprog.es/blog`.

## Stack

- Python 3.12 + Django 5.0+
- PostgreSQL (production) / SQLite (local)
- Pico CSS (minimalist styling)
- Gunicorn (WSGI server)
- Docker + Docker Compose
- Dokploy + Traefik (reverse proxy, SSL, deployment)
- TinyMCE (rich text editor in admin)

## Features

- ✅ Bilingual posts (ES/EN) with per-language filtering
- ✅ Tag system with customizable hex colors
- ✅ Filtering by topic, year and month
- ✅ Sorting (newest, oldest, A-Z, Z-A)
- ✅ Full-text search by title and slug
- ✅ Light/dark theme with persistence
- ✅ Responsive design with Pico CSS
- ✅ SEO-friendly URLs, dynamic `sitemap.xml`
- ✅ RSS feed (`/rss.xml`)
- ✅ Copy-link button on post pages
- ✅ JSON API for portfolio integration
- ✅ 60+ automated tests (models, views, feeds, sitemap, API, admin)

## Requirements

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (production)

## Local setup

### Option 1: Virtual environment (SQLite)

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env        # Fill in variables
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Option 2: Docker Compose (PostgreSQL)

```bash
# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f web
```

Access:
- Blog: http://localhost:8000
- Admin: http://localhost:8000/admin (admin/admin123)

## Environment variables

See `.env.example` for the full reference:

```bash
# Development
DJANGO_ENV=development
SECRET_KEY=any-local-key
DEBUG=True
DB_NAME=blog
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost  # or 'db' with Docker
DB_PORT=5432

# Production
DJANGO_ENV=production
SECRET_KEY=generate-a-secure-key-here
DEBUG=False
ALLOWED_HOSTS=joanbonoprog.es,www.joanbonoprog.es
CSRF_TRUSTED_ORIGINS=https://joanbonoprog.es,https://www.joanbonoprog.es
```

## Project structure

```
blog/
├── config/                    # Settings, URLs, WSGI
├── posts/                     # Main app
│   ├── models.py              # Post, Tag
│   ├── views.py               # List, detail, search, sitemap, API
│   ├── feeds.py                # RSS feed
│   ├── admin.py               # Admin config + TinyMCE
│   └── tests/                 # Test suite (60+ tests)
├── templates/                  # Django templates
├── static/                    # CSS, JS, images
├── locale/                    # Translations (ES/EN)
├── media/                      # User uploads
├── Dockerfile
├── .dockerignore
├── docker-compose.yml          # Development
├── docker-compose.prod.yml     # Production
├── entrypoint.sh                # Startup script
├── requirements.txt
└── manage.py
```

## Endpoints

| Route | Description |
|---|---|
| `/` | Post list (filterable by tag, year, month, search, sort) |
| `/<slug>/` | Single post |
| `/sitemap.xml` | Dynamic sitemap (all published posts, both languages) |
| `/rss.xml` | RSS feed with the latest 20 posts |
| `/api/recent/` | JSON with latest posts (for portfolio) |
| `/admin/` | Admin panel |
| `/i18n/` | Language switcher |

## Testing

The project includes 60+ tests covering models, views, feeds, sitemap, the API and the admin.

```bash
# Run the full test suite
.venv\Scripts\python.exe manage.py test posts

# Run a specific test module
.venv\Scripts\python.exe manage.py test posts.tests.test_views_list

# Run a single test case
.venv\Scripts\python.exe manage.py test posts.tests.test_models.PostModelTests
```

Test files live in `posts/tests/`:
- `test_models.py` — `Post`/`Tag` model behavior (slugs, language fallback)
- `test_views_list.py` — filtering, search, sorting on the post list
- `test_views_detail.py` — 404 handling for unpublished/unavailable posts
- `test_sitemap.py` — sitemap XML correctness
- `test_feeds.py` — RSS feed correctness
- `test_api.py` — `/api/recent/` JSON contract
- `test_admin.py` — admin configuration and TinyMCE integration

## Production deployment (Dokploy)

This blog is deployed at `joanbonoprog.es/blog` — a subpath of the main
portfolio domain, **not** the domain root. Dokploy's built-in Traefik
instance handles the reverse proxy and SSL (Let's Encrypt) automatically,
so this project does **not** ship its own Nginx/Certbot setup.

### 1. Dokploy configuration

1. Create a new app in Dokploy pointing at this repository (Docker Compose
   or Dockerfile-based app — `docker-compose.prod.yml` is provided for the
   Compose flow).
2. In Dokploy's domain settings, add a route rule with:
   - **Path prefix:** `/blog`
   - **Strip prefix:** enabled — Django's `FORCE_SCRIPT_NAME='/blog'`
     (see `config/settings.py`) expects to receive requests **without**
     the `/blog` prefix internally; it only re-adds it when generating
     URLs (`{% url %}`, `{% static %}`, redirects, etc.). If the prefix
     isn't stripped by Traefik, all routes will 404.
   - **Target port:** `8000`
3. Set the environment variables below in Dokploy's UI (never commit them).

### 2. Required environment variables

```bash
DJANGO_ENV=production
SECRET_KEY=generate-a-secure-key-here
DEBUG=False
ALLOWED_HOSTS=joanbonoprog.es,www.joanbonoprog.es
CSRF_TRUSTED_ORIGINS=https://joanbonoprog.es,https://www.joanbonoprog.es
DB_NAME=blog
DB_USER=postgres
DB_PASSWORD=a-strong-password
DB_HOST=db
DB_PORT=5432
```

### 3. Persistent volumes

`docker-compose.prod.yml` mounts named volumes for `postgres_data`,
`staticfiles` and `media` so uploaded images and the database survive
redeploys. Make sure Dokploy is configured to reuse volumes across
deployments rather than recreating them from scratch.

### 4. Useful commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Update code
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# Database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres blog > backup.sql

# Access container shell
docker-compose -f docker-compose.prod.yml exec web bash
```

## Database

- **Local:** SQLite (`db.sqlite3`, git-ignored)
- **Production:** PostgreSQL with persistent Docker volume

## Monitoring

Services include health checks:
- PostgreSQL: `pg_isready`
- Django: automatic migrations on startup

## Security

- HTTPS and SSL certificates handled by Dokploy's Traefik instance
- `SECRET_KEY`, DB credentials and other secrets set via Dokploy env vars, never committed
- `DEBUG=False` and explicit `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` enforced in production
- TinyMCE automatic image uploads disabled (no working upload endpoint shipped by django-tinymce) — images are inserted via URL instead
