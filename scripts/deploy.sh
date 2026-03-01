#!/bin/bash
set -euo pipefail

# Expected environment on server:
# - .env file with Django/DB settings
# - docker-compose.yml present in this directory

PROJECT_DIR=${PROJECT_DIR:-/opt/dscc-coursework}
cd "$PROJECT_DIR"

echo "Pulling latest images..."
docker compose pull

echo "Recreating containers..."
docker compose up -d

echo "Running migrations..."
docker compose exec -T web python manage.py migrate --noinput

echo "Collecting static files..."
docker compose exec -T web python manage.py collectstatic --noinput

echo "Deployment finished."
