# GCP Deployment Guide (Compute Engine)

This guide deploys the Dockerized stack (`web`, `db`, `nginx`) to a Google Cloud VM.

## 1. Create VM

Use Compute Engine and create an Ubuntu VM (for example `e2-medium`) with a static external IP.

## 2. Configure firewall

Allow inbound TCP ports:
- `22` for SSH
- `80` for HTTP
- `443` for HTTPS

## 3. Install Docker and Compose plugin

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out and back in after adding your user to the `docker` group.

## 4. Clone and configure app

This clone is only for the initial bootstrap. Ongoing CI/CD deploys upload the deploy files over SCP and do not require `git pull` on the VM.

```bash
sudo mkdir -p /opt/dscc-coursework
sudo chown -R $USER:$USER /opt/dscc-coursework
git clone https://github.com/sensat1onall/dscc-coursework.git /opt/dscc-coursework
cd /opt/dscc-coursework
cp .env.example .env
```

Set `.env` for production:
- `DEBUG=False`
- strong `SECRET_KEY`
- `ALLOWED_HOSTS=<domain>,<vm-ip>`
- `CSRF_TRUSTED_ORIGINS=https://<domain>`
- `DB_*` values for Postgres service

## 5. Start stack

```bash
docker compose up -d --build
```

## 6. Domain + HTTPS

1. Point domain `A` record to VM static IP.
2. Install certificate (Certbot on VM or terminate TLS via external load balancer).
3. Ensure HTTPS redirects to secure endpoint.

## 7. GitHub Actions secrets for auto-deploy

Set repository secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `GCP_SSH_HOST`
- `GCP_SSH_USERNAME`
- `GCP_SSH_PRIVATE_KEY`
- `GCP_PROJECT_DIR` (optional, defaults to `/opt/dscc-coursework`)

Pipeline behavior:
- Builds and pushes image tags `latest` and `${GITHUB_SHA}`.
- Uploads `docker-compose.yml`, `scripts/deploy.sh`, and `docker/nginx/default.conf` to `GCP_PROJECT_DIR`.
- SSHes into VM and runs `scripts/deploy.sh` with `WEB_IMAGE=<dockerhub-user>/dscc-coursework:${GITHUB_SHA}`.
- Ongoing deploys do not require `git fetch`/`git pull` to work on the VM.
