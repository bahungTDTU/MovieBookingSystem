# Phase 3 – Evidence: docker ps Output

## Purpose

This directory contains screenshots of `docker ps` output demonstrating that all CineWorld
services are running correctly as containers.

## Required Screenshots

| Filename | Content |
|----------|---------|
| `docker-ps-all-running.png` | `docker ps` showing all 10 containers as `Up` (healthy) |
| `docker-ps-after-reboot.png` | `docker ps` output after a full server reboot |
| `docker-ps-after-daemon-restart.png` | `docker ps` after `sudo systemctl restart docker` |

## Expected docker ps Output

```
CONTAINER ID   IMAGE                                  COMMAND                  CREATED        STATUS                   PORTS                    NAMES
xxxxxxxxxxxx   username/cineworld-frontend:latest     "/docker-entrypoint.…"   2 hours ago    Up 2 hours               0.0.0.0:3000->80/tcp     cineworld_frontend
xxxxxxxxxxxx   username/cineworld-catalog:latest      "uvicorn main:app --…"   2 hours ago    Up 2 hours               0.0.0.0:8001->8001/tcp   cineworld_catalog
xxxxxxxxxxxx   username/cineworld-otp:latest          "uvicorn main:app --…"   2 hours ago    Up 2 hours               0.0.0.0:8002->8002/tcp   cineworld_otp
xxxxxxxxxxxx   username/cineworld-identity:latest     "uvicorn main:app --…"   2 hours ago    Up 2 hours               0.0.0.0:8003->8003/tcp   cineworld_identity
xxxxxxxxxxxx   username/cineworld-booking:latest      "uvicorn main:app --…"   2 hours ago    Up 2 hours               0.0.0.0:8004->8004/tcp   cineworld_booking
xxxxxxxxxxxx   username/cineworld-payment:latest      "uvicorn main:app --…"   2 hours ago    Up 2 hours               0.0.0.0:8005->8005/tcp   cineworld_payment
xxxxxxxxxxxx   username/cineworld-redemption:latest   "uvicorn main:app --…"   2 hours ago    Up 2 hours               0.0.0.0:8006->8006/tcp   cineworld_redemption
xxxxxxxxxxxx   username/cineworld-management:latest   "uvicorn main:app --…"   2 hours ago    Up 2 hours               0.0.0.0:8007->8007/tcp   cineworld_management
xxxxxxxxxxxx   username/cineworld-scheduler:latest    "python main.py"         2 hours ago    Up 2 hours                                        cineworld_scheduler
xxxxxxxxxxxx   mysql:8.0                              "docker-entrypoint.s…"   2 hours ago    Up 2 hours (healthy)     3306/tcp                 cineworld_db
```

## Commands to Run

```bash
# Standard view
docker ps

# Wide view (full command)
docker ps --no-trunc

# Include stopped containers
docker ps -a

# Filter by project
docker compose -f docker-compose.prod.yml ps
```
