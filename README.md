# Task Manager - DSCC Coursework

Small Django 6 app with user auth, task management, comments, and collaboration, packaged for production with Docker (Django + PostgreSQL + Nginx + Gunicorn) and CI/CD via GitHub Actions.

## Features
- User authentication: register, login, logout.
- Task CRUD with status, categories, many-to-one (owner/category) and many-to-many (collaborators) relations.
- Comments on tasks; task detail, list, shared-with-me view.
- Admin panel for tasks, categories, comments.
- Static assets configured (collectstatic -> `staticfiles/`), media placeholder directory.

## Tech Stack
- Django 6, Gunicorn, PostgreSQL
- Nginx reverse proxy + static serving
- Docker & Docker Compose (prod + dev overrides)
- GitHub Actions CI/CD (flake8, black --check, pytest, Docker build/push, SSH deploy)

## Quickstart (local, without Docker)
1. Create virtualenv and install deps:
   ```bash
   python -m venv venv
   venv/Scripts/activate  # PowerShell: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set values. To use SQLite locally, omit `DB_NAME`; to use Postgres, set all `DB_*` vars.
3. Run migrations and start server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Docker (production-like)
```bash
cp .env.example .env  # ensure DB_* matches docker-compose.yml (Postgres)
docker compose up -d --build
```
Services:
- `web`: Django + Gunicorn (non-root user), runs migrations & collectstatic on startup.
- `db`: Postgres 16 with persistent volume.
- `nginx`: serves static/media and proxies to web.

Dev override (hot reload):
```bash
docker compose -f docker-compose.dev.yml up -d --build
```

## Environment Variables (`.env.example`)
`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `TIME_ZONE`.

## Screenshots
Store screenshots in `docs/screenshots/` and replace placeholders below before final submission:
- `docs/screenshots/home.png` - landing page
- `docs/screenshots/tasks.png` - task list and shared tasks
- `docs/screenshots/task-detail.png` - task detail with comments
- `docs/screenshots/admin.png` - Django admin panel
- `docs/screenshots/github-actions.png` - successful CI/CD run

## CI/CD
- Workflow: `.github/workflows/deploy.yml`
  - flake8 + black --check
  - pytest (Postgres service)
  - Build & push Docker image to Docker Hub (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`)
  - SSH deploy to server (`SSH_HOST`, `SSH_USERNAME`, `SSH_PRIVATE_KEY`), runs migrations & collectstatic.
- Deployment helper script: `scripts/deploy.sh` (expects repo & `.env` on server, defaults to `/opt/dscc-coursework`).

## Project Structure
- `config/settings.py` - env-driven settings, Postgres-first, static/media paths, auth redirects.
- `core/models.py` - `Category`, `Task`, `Comment` models with relationships and status choices.
- `core/views.py` - auth views, task CRUD, detail with comments.
- `templates/` - base, auth, task pages; `static/css/style.css` for basic styling.
- `docker/` - `entrypoint.sh`, Nginx config.
- `docker-compose.yml`, `docker-compose.dev.yml`, `Dockerfile`, `.dockerignore`.
- Tests: `core/tests/`.

## How to deploy on server (Eskiz or other)
1. Install Docker & Docker Compose; clone repo to `/opt/dscc-coursework`.
2. Add `.env` (use Postgres credentials + domain in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`).
3. (Optional) `chmod +x scripts/deploy.sh`.
4. Pull and start:
   ```bash
   docker compose pull
   docker compose up -d
   docker compose exec -T web python manage.py migrate --noinput
   docker compose exec -T web python manage.py collectstatic --noinput
   ```
5. Attach domain + TLS (e.g., certbot on host, or terminate TLS upstream) pointing to Nginx (port 80/443).

## Testing
```bash
pytest
```
Uses `pytest-django`; default DB is SQLite unless `DB_*` env vars set.

## Coursework deliverables checklist
- Django app meets feature spec (auth, >=3 models, CRUD, admin, static, 5+ views).
- Postgres primary database via env vars; Docker Compose with web/db/nginx, multi-stage Dockerfile, non-root user, .dockerignore, volumes for DB/static/media.
- Production settings: DEBUG flag, ALLOWED_HOSTS, SECRET_KEY from env.
- CI/CD pipeline with linting, tests, image build/push, SSH deploy with migrations & collectstatic.
- README with setup/deploy instructions; .env template, docker-compose dev override.

Screenshots, PDF report, and 4-min video still need to be produced manually after running the app and pipeline.
