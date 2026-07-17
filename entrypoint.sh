#!/bin/sh
set -e

# Wait for PostgreSQL to be ready
if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ]; then
    echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done
    echo "PostgreSQL is ready"
fi

# Run migrations
python manage.py migrate --noinput

# Create superuser if credentials provided. Django's --noinput reads the
# username, email and password from the DJANGO_SUPERUSER_* env vars.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser $DJANGO_SUPERUSER_USERNAME..."
    python manage.py createsuperuser --noinput || true
fi

# Start Gunicorn
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60
