#!/bin/bash
# =============================================================================
# deploy.sh - Deploy CineWorld Application (Traditional - Phase 2)
# =============================================================================
# This script deploys the CineWorld microservices application on an Ubuntu
# server that was previously provisioned with setup.sh.
#
# Prerequisites:
#   - Ubuntu 22.04+ server with setup.sh already executed
#   - MySQL running and accessible
#   - .env file configured at /opt/cineworld/config/.env
#
# Usage:
#   chmod +x deploy.sh
#   sudo ./deploy.sh
# =============================================================================

set -e

# ---------------------------
# Color helpers
# ---------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------------------------
# Check root
# ---------------------------
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo: sudo ./deploy.sh"
    exit 1
fi

# ---------------------------
# Variables
# ---------------------------
APP_DIR="/opt/cineworld"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICES=("catalog" "otp" "identity" "booking" "payment" "redemption" "management" "scheduler")

# ---------------------------
# Check .env file
# ---------------------------
if [ ! -f "${APP_DIR}/config/.env" ]; then
    log_error ".env file not found at ${APP_DIR}/config/.env"
    log_warn "Copy .env.template and fill in your credentials:"
    log_warn "  cp ${APP_DIR}/config/.env.template ${APP_DIR}/config/.env"
    log_warn "  nano ${APP_DIR}/config/.env"
    exit 1
fi

# Source .env for database credentials
set -a
source "${APP_DIR}/config/.env"
set +a

log_info "Starting CineWorld deployment..."

# =============================================================================
# 1. Copy source code to /opt/cineworld
# =============================================================================
log_info "Copying source code to ${APP_DIR}..."

# Copy service files
for service in "${SERVICES[@]}"; do
    log_info "  -> Copying ${service} service..."
    cp -r "${REPO_DIR}/services/${service}/"*.py "${APP_DIR}/services/${service}/"
    cp "${REPO_DIR}/services/${service}/requirements.txt" "${APP_DIR}/services/${service}/"
done

# Copy frontend files
log_info "  -> Copying frontend files..."
cp "${REPO_DIR}/frontend/"*.html "${APP_DIR}/frontend/"
cp "${REPO_DIR}/frontend/"*.css "${APP_DIR}/frontend/"
cp "${REPO_DIR}/frontend/"*.js "${APP_DIR}/frontend/"

# Copy database init script
log_info "  -> Copying database init script..."
cp "${REPO_DIR}/database/init.sql" "${APP_DIR}/database/"

# =============================================================================
# 2. Update database URLs for native deployment (Docker → localhost)
# =============================================================================
log_info "Updating database connection URLs for native deployment..."

DB_URL="mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@localhost:3306/${MYSQL_DATABASE}?charset=utf8mb4"

for service in "${SERVICES[@]}"; do
    DB_FILE="${APP_DIR}/services/${service}/database.py"
    if [ -f "$DB_FILE" ]; then
        # Replace hardcoded Docker database URL with localhost URL
        sed -i "s|mysql+pymysql://user:password@db:3306/movie_booking_db?charset=utf8mb4|${DB_URL}|g" "$DB_FILE"
        log_info "  -> Updated ${service}/database.py"
    fi
done

# =============================================================================
# 3. Update inter-service URLs (Docker hostnames → localhost)
# =============================================================================
log_info "Updating inter-service communication URLs..."

# Booking service → update all service URLs
BOOKING_MAIN="${APP_DIR}/services/booking/main.py"
if [ -f "$BOOKING_MAIN" ]; then
    sed -i 's|http://catalog_service:8001|http://127.0.0.1:8001|g' "$BOOKING_MAIN"
    sed -i 's|http://identity_service:8003|http://127.0.0.1:8003|g' "$BOOKING_MAIN"
    sed -i 's|http://otp_service:8002|http://127.0.0.1:8002|g' "$BOOKING_MAIN"
    sed -i 's|http://payment_service:8005|http://127.0.0.1:8005|g' "$BOOKING_MAIN"
    log_info "  -> Updated booking/main.py"
fi

# Payment service → booking URL
PAYMENT_MAIN="${APP_DIR}/services/payment/main.py"
if [ -f "$PAYMENT_MAIN" ]; then
    sed -i 's|http://booking_service:8004|http://127.0.0.1:8004|g' "$PAYMENT_MAIN"
    log_info "  -> Updated payment/main.py"
fi

# Identity service → OTP URL
IDENTITY_MAIN="${APP_DIR}/services/identity/main.py"
if [ -f "$IDENTITY_MAIN" ]; then
    sed -i 's|http://otp_service:8002|http://127.0.0.1:8002|g' "$IDENTITY_MAIN"
    log_info "  -> Updated identity/main.py"
fi

# =============================================================================
# 4. Update frontend API base URLs
# =============================================================================
log_info "Updating frontend API URLs..."

FRONTEND_JS="${APP_DIR}/frontend/app.js"
if [ -f "$FRONTEND_JS" ]; then
    # Replace localhost URLs with the server's domain/IP
    # Frontend will call APIs through Nginx reverse proxy
    DOMAIN="${SERVER_DOMAIN:-localhost}"
    PROTOCOL="${SERVER_PROTOCOL:-http}"

    sed -i "s|http://localhost:8001|${PROTOCOL}://${DOMAIN}/api/catalog|g" "$FRONTEND_JS"
    sed -i "s|http://localhost:8003|${PROTOCOL}://${DOMAIN}/api/identity|g" "$FRONTEND_JS"
    sed -i "s|http://localhost:8004|${PROTOCOL}://${DOMAIN}/api/booking|g" "$FRONTEND_JS"
    sed -i "s|http://localhost:8005|${PROTOCOL}://${DOMAIN}/api/payment|g" "$FRONTEND_JS"
    sed -i "s|http://localhost:8006|${PROTOCOL}://${DOMAIN}/api/redemption|g" "$FRONTEND_JS"
    log_info "  -> Updated frontend/app.js (domain: ${DOMAIN})"
fi

# =============================================================================
# 5. Install Python dependencies in virtual environments
# =============================================================================
log_info "Installing Python dependencies..."

for service in "${SERVICES[@]}"; do
    log_info "  -> Installing dependencies for ${service}..."
    "${APP_DIR}/services/${service}/venv/bin/pip" install --upgrade pip -q
    "${APP_DIR}/services/${service}/venv/bin/pip" install -r "${APP_DIR}/services/${service}/requirements.txt" -q
done

# =============================================================================
# 6. Configure MySQL database
# =============================================================================
log_info "Configuring MySQL database..."

# Create database user and database if not exists
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

# Import init.sql (ignore errors if tables already exist)
log_info "Importing database schema and seed data..."
mysql -u root --force "${MYSQL_DATABASE}" < "${APP_DIR}/database/init.sql" 2>&1 | grep -v "already exists" || true

log_info "MySQL database configured successfully."

# =============================================================================
# 7. Install systemd service files
# =============================================================================
log_info "Installing systemd service files..."

for service in "${SERVICES[@]}"; do
    SERVICE_FILE="${REPO_DIR}/scripts/systemd/cineworld-${service}.service"
    if [ -f "$SERVICE_FILE" ]; then
        cp "$SERVICE_FILE" "/etc/systemd/system/"
        log_info "  -> Installed cineworld-${service}.service"
    fi
done

# Reload systemd daemon
systemctl daemon-reload

# =============================================================================
# 8. Configure Nginx reverse proxy
# =============================================================================
log_info "Configuring Nginx reverse proxy..."

# Copy config file
cp "${REPO_DIR}/scripts/nginx/cineworld.conf" /etc/nginx/sites-available/cineworld

# Update domain in Nginx config
if [ -n "$SERVER_DOMAIN" ]; then
    sed -i "s|YOUR_DOMAIN|${SERVER_DOMAIN}|g" /etc/nginx/sites-available/cineworld
    log_info "  -> Domain set to: ${SERVER_DOMAIN}"
else
    sed -i "s|server_name YOUR_DOMAIN|server_name _|g" /etc/nginx/sites-available/cineworld
    log_warn "  -> No SERVER_DOMAIN set, using default server"
fi

# Enable the site
ln -sf /etc/nginx/sites-available/cineworld /etc/nginx/sites-enabled/cineworld

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t

# Reload Nginx
systemctl reload nginx
log_info "Nginx configured and reloaded."

# =============================================================================
# 9. Start all microservices
# =============================================================================
log_info "Starting CineWorld microservices..."

for service in "${SERVICES[@]}"; do
    systemctl enable "cineworld-${service}"
    systemctl start "cineworld-${service}"
    log_info "  -> Started cineworld-${service}"
done

# =============================================================================
# 10. Verify deployment
# =============================================================================
log_info "Verifying deployment..."

echo ""
echo "=============================================="
echo " CineWorld Service Status"
echo "=============================================="

ALL_OK=true
for service in "${SERVICES[@]}"; do
    STATUS=$(systemctl is-active "cineworld-${service}" 2>/dev/null || echo "inactive")
    if [ "$STATUS" = "active" ]; then
        echo -e "  ${GREEN}●${NC} cineworld-${service}: ${STATUS}"
    else
        echo -e "  ${RED}●${NC} cineworld-${service}: ${STATUS}"
        ALL_OK=false
    fi
done

NGINX_STATUS=$(systemctl is-active nginx 2>/dev/null || echo "inactive")
echo -e "  ${GREEN}●${NC} nginx: ${NGINX_STATUS}"

MYSQL_STATUS=$(systemctl is-active mysql 2>/dev/null || echo "inactive")
echo -e "  ${GREEN}●${NC} mysql: ${MYSQL_STATUS}"

echo ""
echo "=============================================="

if [ "$ALL_OK" = true ]; then
    log_info "All services are running!"
else
    log_warn "Some services failed to start. Check logs with:"
    log_warn "  journalctl -u cineworld-<service> -f"
fi

echo ""
log_info "Deployment complete!"
log_info "Frontend: http://${SERVER_DOMAIN:-<server-ip>}"
log_info "Catalog API: http://${SERVER_DOMAIN:-<server-ip>}/api/catalog/"
log_info ""
log_info "Useful commands:"
log_info "  View logs:     journalctl -u cineworld-catalog -f"
log_info "  Restart:       systemctl restart cineworld-catalog"
log_info "  Stop all:      for s in ${SERVICES[*]}; do systemctl stop cineworld-\$s; done"
log_info "  Status all:    for s in ${SERVICES[*]}; do systemctl status cineworld-\$s; done"
echo ""
