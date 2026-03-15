# Phase 2 - Traditional Deployment on Ubuntu

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │              Ubuntu 22.04 Server             │
                    │                                              │
Client ──HTTPS──►  │  Nginx (443/80)                              │
                    │    ├── / → Static files (/opt/cineworld/     │
                    │    │       frontend/)                        │
                    │    ├── /api/catalog/   → 127.0.0.1:8001      │
                    │    ├── /api/otp/       → 127.0.0.1:8002      │
                    │    ├── /api/identity/  → 127.0.0.1:8003      │
                    │    ├── /api/booking/   → 127.0.0.1:8004      │
                    │    ├── /api/payment/   → 127.0.0.1:8005      │
                    │    ├── /api/redemption/→ 127.0.0.1:8006      │
                    │    └── /api/management/→ 127.0.0.1:8007      │
                    │                                              │
                    │  MySQL 8.0 (localhost:3306)                   │
                    │  Scheduler (background service)              │
                    └──────────────────────────────────────────────┘
```

## Deliverables

### 1. Server Provisioning
- Ubuntu 22.04+ cloud server (AWS/Azure/GCP/DigitalOcean)
- Server secured with UFW firewall (SSH + HTTP/HTTPS only)
- SSH key-based authentication

### 2. Application Deployment
- MySQL database initialized with `init.sql`
- Each microservice deployed natively using **systemd**
- Python virtual environments for service isolation
- Nginx configured as reverse proxy

### 3. Domain & SSL
- Custom domain with DNS A record configured
- SSL certificate via Let's Encrypt (Certbot)
- HTTPS enabled for all endpoints
- Auto HTTP → HTTPS redirect

### 4. Service Management
- systemd service files for each microservice (auto-restart on failure)
- Centralized logging via journald
- Environment variables managed via `/opt/cineworld/config/.env`

---

## Files Created for Phase 2

| File | Description |
|------|-------------|
| `scripts/setup.sh` | Server provisioning (install Python, MySQL, Nginx, Certbot, UFW) |
| `scripts/deploy.sh` | Full application deployment automation |
| `scripts/ssl-setup.sh` | SSL certificate setup with Let's Encrypt |
| `scripts/nginx/cineworld.conf` | Nginx reverse proxy configuration |
| `scripts/systemd/cineworld-*.service` | 8 systemd service files (one per microservice) |

---

## Step-by-Step Deployment Guide

### Step 1: Provision the Server

1. Create an Ubuntu 22.04+ server on your cloud provider (AWS EC2, DigitalOcean, Azure VM, etc.)
2. SSH into the server:
   ```bash
   ssh root@<server-ip>
   ```
3. (Recommended) Configure SSH key authentication and disable password login:
   ```bash
   # On local machine
   ssh-copy-id root@<server-ip>

   # On server - edit /etc/ssh/sshd_config
   PasswordAuthentication no
   PermitRootLogin prohibit-password

   systemctl restart sshd
   ```

### Step 2: Run Setup Script

```bash
# Clone the repository
git clone https://github.com/bahungTDTU/MovieBookingSystem.git
cd MovieBookingSystem

# Run server setup
chmod +x scripts/setup.sh
sudo ./scripts/setup.sh
```

This installs: Python 3, pip, venv, MySQL 8.0, Nginx, Certbot, UFW firewall, and creates the `/opt/cineworld/` directory structure with virtual environments.

### Step 3: Configure Environment Variables

```bash
# Copy the template
cp /opt/cineworld/config/.env.template /opt/cineworld/config/.env

# Edit with your actual credentials
nano /opt/cineworld/config/.env
```

Required variables in `.env`:
```env
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=movie_booking_db
MYSQL_USER=cineworld_user
MYSQL_PASSWORD=your_secure_password
DATABASE_URL=mysql+pymysql://cineworld_user:your_secure_password@localhost:3306/movie_booking_db?charset=utf8mb4

SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Set your domain (or server IP)
SERVER_DOMAIN=your-domain.com
SERVER_PROTOCOL=http
```

### Step 4: Deploy the Application

```bash
chmod +x scripts/deploy.sh
sudo ./scripts/deploy.sh
```

The deploy script will:
1. Copy source code to `/opt/cineworld/`
2. Update database URLs from Docker → localhost
3. Update inter-service URLs from Docker hostnames → 127.0.0.1
4. Update frontend API URLs to use Nginx reverse proxy
5. Install Python dependencies in each virtual environment
6. Create MySQL database, user, and import `init.sql`
7. Install systemd service files to `/etc/systemd/system/`
8. Configure and enable Nginx reverse proxy
9. Start all microservices
10. Verify deployment status

### Step 5: Configure DNS

1. Purchase a domain (Namecheap, GoDaddy, Cloudflare, etc.)
2. Create an **A record** pointing to your server's IP:
   ```
   Type: A
   Name: @ (or subdomain)
   Value: <server-ip>
   TTL: 300
   ```
3. Wait for DNS propagation (may take a few minutes)

### Step 6: Enable SSL (HTTPS)

```bash
chmod +x scripts/ssl-setup.sh
sudo ./scripts/ssl-setup.sh your-domain.com your-email@example.com
```

This will:
1. Verify DNS resolution
2. Obtain SSL certificate from Let's Encrypt
3. Configure Nginx for HTTPS with auto-redirect
4. Set up auto-renewal
5. Update frontend URLs to HTTPS

---

## Service Management

### Check service status
```bash
# All services
for s in catalog otp identity booking payment redemption management scheduler; do
    systemctl status cineworld-$s --no-pager
done

# Single service
systemctl status cineworld-catalog
```

### View logs
```bash
# Follow logs for a service
journalctl -u cineworld-catalog -f

# View last 50 lines
journalctl -u cineworld-catalog -n 50

# View logs since boot
journalctl -u cineworld-catalog -b
```

### Restart services
```bash
# Single service
sudo systemctl restart cineworld-catalog

# All services
for s in catalog otp identity booking payment redemption management scheduler; do
    sudo systemctl restart cineworld-$s
done
```

### Stop/Start services
```bash
sudo systemctl stop cineworld-catalog
sudo systemctl start cineworld-catalog
```

### Check Nginx
```bash
sudo nginx -t                  # Test config
sudo systemctl status nginx    # Check status
sudo systemctl reload nginx    # Reload config
```

### Check MySQL
```bash
sudo systemctl status mysql
sudo mysql -u root -e "SHOW DATABASES;"
```

---

## systemd Service Files

Each microservice has a systemd unit file at `/etc/systemd/system/cineworld-<service>.service`:

| Service | Port | Type | systemd Unit |
|---------|------|------|-------------|
| Catalog | 8001 | FastAPI/Uvicorn | `cineworld-catalog.service` |
| OTP | 8002 | FastAPI/Uvicorn | `cineworld-otp.service` |
| Identity | 8003 | FastAPI/Uvicorn | `cineworld-identity.service` |
| Booking | 8004 | FastAPI/Uvicorn | `cineworld-booking.service` |
| Payment | 8005 | FastAPI/Uvicorn | `cineworld-payment.service` |
| Redemption | 8006 | FastAPI/Uvicorn | `cineworld-redemption.service` |
| Management | 8007 | FastAPI/Uvicorn | `cineworld-management.service` |
| Scheduler | - | Python script | `cineworld-scheduler.service` |

Key features:
- `Restart=on-failure` with `RestartSec=5` for automatic recovery
- `EnvironmentFile` points to `/opt/cineworld/config/.env`
- Logs via `journald` (accessible with `journalctl`)
- `After=mysql.service` ensures database is ready

---

## Nginx Reverse Proxy

Configuration file: `scripts/nginx/cineworld.conf`

**Routing Table:**

| URL Path | Backend |
|----------|---------|
| `/` | Static files (`/opt/cineworld/frontend/`) |
| `/api/catalog/*` | `127.0.0.1:8001` |
| `/api/otp/*` | `127.0.0.1:8002` |
| `/api/identity/*` | `127.0.0.1:8003` |
| `/api/booking/*` | `127.0.0.1:8004` |
| `/api/payment/*` | `127.0.0.1:8005` |
| `/api/redemption/*` | `127.0.0.1:8006` |
| `/api/management/*` | `127.0.0.1:8007` |
| `/uploads/*` | File uploads directory |

Security headers included: `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`.

---

## Troubleshooting

### Service won't start
```bash
# Check detailed error
journalctl -u cineworld-catalog -n 50 --no-pager

# Common issues:
# - Missing Python packages → check venv
# - Database not ready → check MySQL status
# - Port conflict → check with: ss -tlnp | grep 8001
```

### Database connection error
```bash
# Verify MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u cineworld_user -p -e "USE movie_booking_db; SHOW TABLES;"

# Check .env credentials
cat /opt/cineworld/config/.env
```

### Nginx returns 502 Bad Gateway
```bash
# Service is down - restart it
sudo systemctl restart cineworld-catalog

# Check if service is listening
ss -tlnp | grep 8001

# Check Nginx error log
tail -f /var/log/nginx/error.log
```

### SSL certificate issues
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check Nginx SSL config
sudo nginx -t
```

---

## Evidence
Screenshots are stored in [`docs/screenshots/phase2/`](../docs/screenshots/phase2/)
