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
├── README.md                                ← this file
├── dockerfiles/
│   ├── README.md
│   ├── frontend/
│   │   └── Dockerfile                       ← (1) Finalised frontend Dockerfile
│   └── services/
│       ├── catalog/Dockerfile               ← (1) Finalised service Dockerfiles
│       ├── otp/Dockerfile
│       ├── identity/Dockerfile
│       ├── booking/Dockerfile
│       ├── payment/Dockerfile
│       ├── redemption/Dockerfile
│       ├── management/Dockerfile
│       └── scheduler/Dockerfile
├── docker-compose/
│   ├── docker-compose.prod.yml              ← (2) Production compose (volumes + networks)
│   ├── .env.example                         ← (2) Environment variable template
│   └── README.md
├── screenshots/
│   └── dockerhub/
│       └── README.md                        ← (3) Docker Hub repo screenshot guide
└── evidence/
    ├── build-push-pull/
    │   └── README.md                        ← (4) docker build/push/pull evidence guide
    ├── docker-ps/
    │   └── README.md                        ← (5) docker ps output guide
    ├── volumes/
    │   └── README.md                        ← (6) Persistent volume behaviour guide
    ├── https-routing/
    │   └── README.md                        ← (7) HTTPS routing verification guide
    └── restart-behaviour/
        └── README.md                        ← (8) Container/daemon/reboot restart guide
```

> **Note on screenshots and evidence:** Each subdirectory contains a README file describing
> exactly which screenshots to capture. Place actual `.png` files alongside the README after
> deployment.

---

## Deliverables Checklist

| # | Requirement | Artefact |
|---|-------------|----------|
| 1 | Finalized Dockerfile(s) | `dockerfiles/` |
| 2 | docker-compose with volumes, networks, .env, prod config | `docker-compose/` |
| 3 | Docker Hub repository screenshots | `screenshots/dockerhub/` |
| 4 | Evidence of docker build, push, pull | `evidence/build-push-pull/` |
| 5 | docker ps outputs | `evidence/docker-ps/` |
| 6 | Persistent volume behaviour evidence | `evidence/volumes/` |
| 7 | HTTPS reverse proxy routing verification | `evidence/https-routing/` |
| 8 | Container/daemon/reboot restart evidence | `evidence/restart-behaviour/` |

---

## Quick Start (Production Server)

```bash
# 1. Upload phase3/docker-compose/ to server
scp -r phase3/docker-compose/ user@server:~/cineworld/

# 2. SSH into server and set up environment
ssh user@server
cd ~/cineworld/docker-compose
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

The host Nginx config for Phase 3 is at `nginx-production-docker.conf` (project root level).
It routes HTTPS traffic to Docker container ports (same port numbers as Phase 2 systemd services,
so the Nginx config change is minimal).

```bash
sudo cp nginx-production-docker.conf /etc/nginx/sites-available/cineworld
sudo sed -i 's/tungtungtungtungsahur.site/tungtungtungtungsahur.site/g' /etc/nginx/sites-available/cineworld
sudo nginx -t && sudo systemctl reload nginx
```
