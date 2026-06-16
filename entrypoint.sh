#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
uv run python -c "
import psycopg, os, time
while True:
    try:
        psycopg.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        ).close()
        break
    except Exception:
        time.sleep(1)
"

echo "Running migrations..."
uv run python src/manage.py migrate

echo "Seeding data..."
uv run python src/manage.py seed_data

exec uv run python src/manage.py runserver 0.0.0.0:8000
