#!/bin/bash
# =============================================================================
# ssl-setup.sh - Configure SSL with Let's Encrypt for CineWorld
# =============================================================================
# This script sets up HTTPS using Certbot and Let's Encrypt.
#
# Prerequisites:
#   - Domain must be pointed to this server's IP via DNS
#   - Nginx must be configured and running (deploy.sh completed)
#   - Port 80 must be accessible from the internet
#
# Usage:
#   chmod +x ssl-setup.sh
#   sudo ./ssl-setup.sh YOUR_DOMAIN YOUR_EMAIL
#
# Example:
#   sudo ./ssl-setup.sh cineworld.example.com admin@example.com
# =============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo: sudo ./ssl-setup.sh DOMAIN EMAIL"
    exit 1
fi

DOMAIN="$1"
EMAIL="$2"

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    log_error "Usage: sudo ./ssl-setup.sh <domain> <email>"
    log_error "Example: sudo ./ssl-setup.sh cineworld.example.com admin@example.com"
    exit 1
fi

# =============================================================================
# 1. Verify DNS resolution
# =============================================================================
log_info "Verifying DNS resolution for ${DOMAIN}..."

SERVER_IP=$(curl -s ifconfig.me)
DNS_IP=$(dig +short "$DOMAIN" | tail -1)

if [ "$SERVER_IP" != "$DNS_IP" ]; then
    log_error "DNS mismatch! Domain ${DOMAIN} resolves to ${DNS_IP}, but this server's IP is ${SERVER_IP}"
    log_error "Please update your DNS A record to point to ${SERVER_IP}"
    echo ""
    echo "If DNS was recently updated, wait a few minutes and try again."
    exit 1
fi

log_info "DNS verified: ${DOMAIN} → ${SERVER_IP}"

# =============================================================================
# 2. Update Nginx config with domain
# =============================================================================
log_info "Updating Nginx configuration with domain ${DOMAIN}..."

NGINX_CONF="/etc/nginx/sites-available/cineworld"
if [ -f "$NGINX_CONF" ]; then
    sed -i "s|server_name .*|server_name ${DOMAIN};|g" "$NGINX_CONF"
    nginx -t
    systemctl reload nginx
fi

# =============================================================================
# 3. Obtain SSL certificate
# =============================================================================
log_info "Obtaining SSL certificate from Let's Encrypt..."

certbot --nginx \
    -d "$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --redirect

# =============================================================================
# 4. Verify SSL
# =============================================================================
log_info "Verifying SSL certificate..."

if curl -s -o /dev/null -w "%{http_code}" "https://${DOMAIN}" | grep -q "200\|301\|302"; then
    log_info "SSL is working! Site is accessible at https://${DOMAIN}"
else
    log_info "SSL certificate installed. Verify manually: https://${DOMAIN}"
fi

# =============================================================================
# 5. Setup auto-renewal
# =============================================================================
log_info "Setting up auto-renewal..."

# Certbot auto-renewal is typically already configured via systemd timer
systemctl enable certbot.timer 2>/dev/null || true
systemctl start certbot.timer 2>/dev/null || true

# Test renewal (dry run)
certbot renew --dry-run

# =============================================================================
# 6. Update frontend API URLs to HTTPS
# =============================================================================
log_info "Updating frontend API URLs to use HTTPS..."

FRONTEND_JS="/opt/cineworld/frontend/app.js"
if [ -f "$FRONTEND_JS" ]; then
    sed -i "s|http://${DOMAIN}|https://${DOMAIN}|g" "$FRONTEND_JS"
    log_info "Frontend URLs updated to HTTPS."
fi

echo ""
echo "=============================================="
log_info "SSL setup completed successfully!"
echo "=============================================="
echo ""
log_info "Your site is now accessible at:"
log_info "  https://${DOMAIN}"
echo ""
log_info "Certificate auto-renewal is configured."
log_info "To check renewal: sudo certbot renew --dry-run"
echo ""
