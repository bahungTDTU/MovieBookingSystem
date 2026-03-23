# Phase 3 – Docker Deployment

## Architecture

```
Client ─HTTPS──► Nginx (host, port 443)
                  │
                  ├── /                → localhost:3000  (cineworld_frontend)
                  ├── /api/catalog/    → localhost:8001  (cineworld_catalog)
                  ├── /api/otp/        → localhost:8002  (cineworld_otp)
                  ├── /api/identity/   → localhost:8003  (cineworld_identity)
                  ├── /api/booking/    → localhost:8004  (cineworld_booking)
                  ├── /api/payment/    → localhost:8005  (cineworld_payment)
                  ├── /api/redemption/ → localhost:8006  (cineworld_redemption)
                  └── /api/management/ → localhost:8007  (cineworld_management)

Docker Network (cineworld_network):
  cineworld_frontend    (nginx:alpine – serves static files)
  cineworld_catalog     (FastAPI – uvicorn :8001)
  cineworld_otp         (FastAPI – uvicorn :8002)
  cineworld_identity    (FastAPI – uvicorn :8003)
  cineworld_booking     (FastAPI – uvicorn :8004)
  cineworld_payment     (FastAPI – uvicorn :8005)
  cineworld_redemption  (FastAPI – uvicorn :8006)
  cineworld_management  (FastAPI – uvicorn :8007)
  cineworld_scheduler   (Python background job)
  cineworld_db          (MySQL 8.0)

Named Volumes:
  mysql_data    → /var/lib/mysql      (persistent DB storage)
  uploads_data  → /uploads            (persistent file uploads)
```

---

## Directory Structure

```
phase3/
├── README.md                          ← this file
├── deploy-aws.ps1                     ← AWS deployment script (PowerShell)
├── generate-ssl-cert.ps1              ← SSL certificate generation script
├── docker-compose-nginx-proxy.yml     ← Docker Compose with Nginx proxy
├── nginx-https-local.conf             ← Nginx config for local HTTPS
├── nginx-production-docker.conf       ← Nginx config for production Docker
└── screenshots/
    └── dockerhub/
        ├── README.md                  ← Docker Hub screenshot guide
        └── CineWorld images on Docker Hub.png
```

> **Note:** Dockerfiles are located in each service directory (e.g., `services/catalog/Dockerfile`).
> The main `docker-compose.prod.yml` is at the project root level.

---

## Deliverables Checklist

| # | Requirement | Artefact |
|---|-------------|----------|
| 1 | Finalized Dockerfile(s) | `services/*/Dockerfile`, `frontend/Dockerfile` |
| 2 | docker-compose with volumes, networks, .env, prod config | `docker-compose.prod.yml` (root) |
| 3 | Docker Hub repository screenshots | `screenshots/dockerhub/` |
| 4 | Nginx configuration for Docker | `nginx-production-docker.conf` |
| 5 | AWS deployment script | `deploy-aws.ps1` |
| 6 | SSL certificate generation | `generate-ssl-cert.ps1` |
| 7 | Docker Compose with Nginx proxy | `docker-compose-nginx-proxy.yml` |
| 8 | Local HTTPS Nginx config | `nginx-https-local.conf` |

---

## Quick Start (Production Server)

```bash
# 1. Upload project files to server
scp docker-compose.prod.yml user@server:~/cineworld/
scp phase3/nginx-production-docker.conf user@server:~/cineworld/

# 2. SSH into server and set up environment
ssh user@server
cd ~/cineworld
cp .env.example .env
nano .env          # Fill in real values

# 3. Pull images and launch
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 4. Verify
docker ps
curl https://tungtungtungtungsahur.site/api/catalog/movies
```

---

## Nginx Configuration

The host Nginx config for Phase 3 is at `phase3/nginx-production-docker.conf`.
It routes HTTPS traffic to Docker container ports (same port numbers as Phase 2 systemd services,
so the Nginx config change is minimal).

```bash
sudo cp phase3/nginx-production-docker.conf /etc/nginx/sites-available/cineworld
sudo sed -i 's/tungtungtungtungsahur.site/YOUR_DOMAIN/g' /etc/nginx/sites-available/cineworld
sudo nginx -t && sudo systemctl reload nginx
```
