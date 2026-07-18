# Personal Blog

Personal blog built with Django. Deployed at `joanbonoprog.es/blog`.

## Stack

- Python 3.12 + Django 6.0+
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
- ✅ Responsive, viewport-aware pagination
- ✅ Clean-code / SOLID refactor (custom querysets, filter form, external JS/CSS)
- ✅ 68+ automated tests (models, views, feeds, sitemap, API, admin, i18n)

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
│   ├── models.py              # Post, Tag + custom querysets/managers
│   ├── views.py               # List, detail, search, sitemap, API
│   ├── forms.py               # PostFilterForm (search/filters/ordering)
│   ├── feeds.py                # RSS feed
│   ├── admin.py               # Admin config + TinyMCE
│   └── tests/                 # Test suite (60+ tests)
├── templates/                  # Django templates
├── static/                    # CSS, JS, images
│   ├── css/theme.css          # Custom Pico CSS theme
│   └── js/                    # External JS (theme, posts list, post detail)
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

## Architecture & clean code

The codebase follows SOLID principles and clean-code practices:

- **Custom querysets/managers** in `posts/models.py` (`PostQuerySet`, `TagQuerySet`) centralize the repeated "published + language" logic and date aggregations.
- **`PostFilterForm`** in `posts/forms.py` encapsulates list filtering, ordering and search, keeping `post_list` focused on coordination.
- **External JS modules** in `static/js/` replace inline scripts and event handlers in the templates:
  - `theme.js` — light/dark mode
  - `posts.js` — pagination, search, filters, sorting
  - `post_detail.js` — copy-link button
- **No hardcoded URLs** in views/feeds; `reverse` + `request.build_absolute_uri` are used.
- **i18n-ready**: all user-facing strings are wrapped with `{% trans %}` and translated in `locale/en/LC_MESSAGES/django.po`.

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

The project includes 68+ tests covering models, views, feeds, sitemap, the API, admin and i18n.

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
- `test_views_list.py` — filtering, search, sorting and pagination on the post list
- `test_views_detail.py` — 404 handling for unpublished/unavailable posts
- `test_sitemap.py` — sitemap XML correctness
- `test_feeds.py` — RSS feed correctness
- `test_api.py` — `/api/recent/` JSON contract
- `test_i18n.py` — language switcher and translation behavior
- `test_admin.py` — admin configuration and TinyMCE integration

## Production deployment (Dokploy)

This blog is deployed at `joanbonoprog.es/blog` — a subpath of the main
portfolio domain, **not** the domain root. Dokploy's built-in Traefik
instance handles the reverse proxy and SSL (Let's Encrypt) automatically,
so this project does **not** ship its own Nginx/Certbot setup.

### Step-by-step guide

**1. Push the repository**

Make sure the latest code (including `Dockerfile`, `docker-compose.prod.yml`,
`.dockerignore`, `entrypoint.sh`) is pushed to the Git remote Dokploy will
pull from.

**2. Create the project in Dokploy**

- In the Dokploy dashboard, click **Create Project** → **Compose**.
- Connect it to this repository/branch.
- Set the **Compose file path** to `docker-compose.prod.yml`.

**3. Configure environment variables**

In the project's **Environment** tab, add:

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
# Optional: auto-create an admin user on first boot
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=a-strong-admin-password
DJANGO_SUPERUSER_EMAIL=you@joanbonoprog.es
```

Generate a strong `SECRET_KEY` with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**4. Configure the domain and path routing**

In the project's **Domains** tab:
- **Host:** `joanbonoprog.es`
- **Path:** `/blog`
- **Strip path prefix:** **enabled** — Django's `FORCE_SCRIPT_NAME='/blog'`
  (`config/settings.py`) expects requests **without** the `/blog` prefix
  internally; it only re-adds it when generating URLs (`{% url %}`,
  `{% static %}`, redirects, etc.). If Traefik doesn't strip it, every
  route will 404.
- **Container port:** `8000` (matches the `web` service in
  `docker-compose.prod.yml`).
- Enable **HTTPS** so Dokploy provisions the Let's Encrypt certificate for
  the domain (shared with the portfolio app already on that domain).

**5. Deploy**

Click **Deploy**. Dokploy will:
1. Build the image from `Dockerfile` (installs deps, runs `collectstatic`
   with the whitenoise manifest storage).
2. Start `db` (PostgreSQL) and wait for its healthcheck.
3. Start `web`, which via `entrypoint.sh` runs migrations, optionally
   creates the superuser, then starts Gunicorn on port 8000.

**6. Verify the deployment**

- `https://joanbonoprog.es/blog/` → post list loads with styling (confirms
  static files work).
- `https://joanbonoprog.es/blog/admin/` → admin login page.
- `https://joanbonoprog.es/blog/sitemap.xml` and `/blog/rss.xml` → valid XML.
- Create a test post in the admin, confirm it renders and images inserted
  via URL in TinyMCE display correctly.

**7. Confirm persistence**

Trigger a redeploy from Dokploy and verify:
- Previously created posts/tags still exist (`postgres_data` volume).
- Uploaded media images are still reachable (`media` volume).

### Useful commands

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

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| All `/blog/*` routes return 404 | Path prefix not stripped by Traefik before reaching Django |
| CSS/JS missing (unstyled page) | `collectstatic` ran without `DJANGO_ENV=production` — rebuild the image |
| `CSRF verification failed` on login | `CSRF_TRUSTED_ORIGINS` missing the `https://` scheme or the exact domain |
| Uploaded images disappear after redeploy | `media` volume not mounted or Dokploy recreated volumes |
| 400 Bad Request | Domain missing from `ALLOWED_HOSTS` |

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

## Two-factor authentication (2FA) for the admin

The Django admin is protected with TOTP via `django-two-factor-auth`.

### First-time bootstrap

1. Deploy with `ADMIN_2FA_ENABLED=False`.
2. Log in at `/blog/admin/` as the superuser.
3. Go to `/blog/account/two_factor/setup/` and scan the QR code with Google Authenticator, Authy, or similar.
4. Save the backup codes shown.
5. Change `ADMIN_2FA_ENABLED=True` in Dokploy environment variables and redeploy.

From then on, any access to `/blog/admin/` requires password + TOTP token.
