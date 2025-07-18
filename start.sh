#!/bin/bash
set -e

# Wait for database if needed (uncomment and modify as needed)
# until nc -z -v -w30 $DB_HOST $DB_PORT; do
#   echo "Waiting for database connection..."
#   sleep 2
# done

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting application server..."
uv run fastapi run src/main.py --workers 4
