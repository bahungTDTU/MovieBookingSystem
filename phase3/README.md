# Phase 3 - Docker Deployment

## Deliverables

### 1. Docker Images
- Custom Docker images for each microservice
- Images pushed to Docker Hub registry
- Production `docker-compose.yml` pulls from registry (no local build)

### 2. Container Orchestration
- Docker Compose for multi-container management
- Volume mounts for database persistence and uploads
- Restart policies (`restart: always`) for resilience
- Health checks for service dependencies

### 3. Networking
- Nginx reverse proxy maintained from Phase 2
- Upstream targets changed to Docker containers
- HTTPS still functional through Nginx

### 4. Reliability
- Docker auto-start on server reboot
- Container auto-restart on failure
- Database data persisted via Docker volumes

## Architecture

```
Client → Nginx (443/HTTPS) → Docker Network
                            ├── catalog_service (8001)
                            ├── otp_service (8002)
                            ├── identity_service (8003)
                            ├── booking_service (8004)
                            ├── payment_service (8005)
                            ├── redemption_service (8006)
                            ├── management_service (8007)
                            ├── scheduler_service (background)
                            ├── frontend (3000→80)
                            └── mysql (3306)
```

## Evidence
Screenshots are stored in [`docs/screenshots/phase3/`](../docs/screenshots/phase3/)
