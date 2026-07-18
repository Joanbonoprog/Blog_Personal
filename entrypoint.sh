#!/bin/sh
set -e

# If a command is passed (e.g. docker-compose run web python manage.py migrate),
# run it directly instead of the default startup flow.
if [ $# -gt 0 ]; then
    exec "$@"
fi

# Wait for PostgreSQL to be ready
DB_PORT=${DB_PORT:-5432}
if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ]; then
    echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 0.1
    done
    echo "PostgreSQL is ready"
fi

# Run migrations (explicit django_otp/two_factor apps to avoid ordering issues)
python manage.py migrate --noinput
python manage.py migrate --noinput otp_static otp_totp two_factor

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
