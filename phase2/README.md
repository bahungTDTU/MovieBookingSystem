# Phase 2 - Traditional Deployment on Ubuntu

## Deliverables

### 1. Server Provisioning
- Ubuntu 22.04+ cloud server (AWS/Azure/GCP/DigitalOcean)
- Server secured with UFW firewall and SSH configuration

### 2. Application Deployment
- MySQL database initialized with `init.sql`
- Each microservice deployed natively using systemd
- Python virtual environments for service isolation
- Nginx configured as reverse proxy

### 3. Domain & SSL
- Custom domain with DNS configured
- SSL certificate via Let's Encrypt (Certbot)
- HTTPS enabled for all endpoints

### 4. Service Management
- systemd service files for each microservice
- Auto-restart on failure
- Log management

## Architecture

```
Client → Nginx (443/HTTPS) → Microservices (8001-8007)
                            → Frontend static files
                            → MySQL (3306)
```

## Evidence
Screenshots are stored in [`docs/screenshots/phase2/`](../docs/screenshots/phase2/)
