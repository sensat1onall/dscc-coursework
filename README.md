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

For server deployments from Docker Hub image:
```bash
export WEB_IMAGE=<dockerhub-user>/dscc-coursework:latest
docker compose pull
docker compose up -d --no-build
```

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
  - SSH deploy to GCP VM (`GCP_SSH_HOST`, `GCP_SSH_USERNAME`, `GCP_SSH_PRIVATE_KEY`, optional `GCP_PROJECT_DIR`)
  - Workflow uploads `docker-compose.yml`, `scripts/deploy.sh`, and `docker/nginx/default.conf` to the VM before deploy, so ongoing deploys do not depend on `git pull` working on the server.
  - Server deploy uses image tag `${{ github.sha }}` via `WEB_IMAGE` and runs migrations + collectstatic.
- Deployment helper script: `scripts/deploy.sh` (expects `.env`, `docker-compose.yml`, and `WEB_IMAGE` on the server).

## Project Structure
- `config/settings.py` - env-driven settings, Postgres-first, static/media paths, auth redirects.
- `core/models.py` - `Category`, `Task`, `Comment` models with relationships and status choices.
- `core/views.py` - auth views, task CRUD, detail with comments.
- `templates/` - base, auth, task pages; `static/css/style.css` for basic styling.
- `docker/` - `entrypoint.sh`, Nginx config.
- `docker-compose.yml`, `docker-compose.dev.yml`, `Dockerfile`, `.dockerignore`.
- Tests: `core/tests/`.

## Deploy on Google Cloud Platform (Compute Engine)
Detailed commands: `docs/gcp-deploy.md`.

1. Create Ubuntu VM (e2-medium or better) and reserve a static external IP.
2. Open firewall rules for TCP `22`, `80`, `443` in GCP VPC firewall.
3. Install Docker + Docker Compose plugin on VM.
4. Bootstrap `/opt/dscc-coursework` once and add production `.env`.
5. Set production env values:
   - `DEBUG=False`
   - strong `SECRET_KEY`
   - `ALLOWED_HOSTS=<your-domain>,<vm-ip>`
   - `CSRF_TRUSTED_ORIGINS=https://<your-domain>`
6. Start stack:
   ```bash
   docker compose up -d --build
   ```
7. Point your domain DNS `A` record to the VM static IP.
8. Install TLS certificate on VM (certbot or managed proxy) and enforce HTTPS.
After the initial bootstrap, GitHub Actions uploads the deploy files on each push, so the VM does not need `git pull` to succeed for normal deploys.

## Testing
```bash
pytest
```
Uses `pytest-django`; default DB is SQLite unless `DB_*` env vars set.

## Coursework deliverables checklist
- Django app meets feature spec (auth, >=3 models, CRUD, admin, static, 5+ views).
- Postgres primary database via env vars; Docker Compose with web/db/nginx, multi-stage Dockerfile, non-root user, .dockerignore, volumes for DB/static/media.
- Production settings: DEBUG flag, ALLOWED_HOSTS, SECRET_KEY from env.
- CI/CD pipeline with linting, tests, image build/push, and auto-deploy to GCP VM with migrations & collectstatic.
- README with setup/deploy instructions; .env template, docker-compose dev override.

## Live submission data
- Live app URL (HTTPS): `https://dscc.azro.uz/`
- Live app URL (HTTP/IP): `http://51.120.120.23/`
- GitHub URL: `https://github.com/sensat1onall/dscc-coursework`
- Docker Hub URL: `https://hub.docker.com/r/sensat1onall/dscc-coursework`
- Test credentials for assessor: `Suxrob` / `Frag_andy0656`
