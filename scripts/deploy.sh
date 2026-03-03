#!/bin/bash
set -euo pipefail

# Expected environment on server:
# - .env file with Django/DB settings
# - docker-compose.yml present in this directory
# - WEB_IMAGE exported (e.g. dockerhub-user/dscc-coursework:sha)

PROJECT_DIR=${PROJECT_DIR:-/opt/dscc-coursework}
cd "$PROJECT_DIR"

if [[ -z "${WEB_IMAGE:-}" ]]; then
  echo "WEB_IMAGE is not set. Aborting."
  exit 1
fi

export WEB_IMAGE

echo "Pulling latest images..."
docker compose pull

echo "Recreating containers..."
docker compose up -d --no-build --remove-orphans

echo "Running migrations..."
docker compose exec -T web python manage.py migrate --noinput

echo "Collecting static files..."
docker compose exec -T web python manage.py collectstatic --noinput

echo "Deployment finished."
