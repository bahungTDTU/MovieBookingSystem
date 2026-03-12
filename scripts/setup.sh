#!/bin/bash
# =============================================================================
# setup.sh - Ubuntu Server Setup Script for CineWorld Movie Booking System
# =============================================================================
# This script prepares a fresh Ubuntu 22.04+ server with all runtime
# dependencies required to run the CineWorld microservices application.
#
# Usage:
#   chmod +x setup.sh
#   sudo ./setup.sh
#
# Note: This script must be run with root privileges (sudo).
#       It does NOT contain any hardcoded credentials.
# =============================================================================

set -e  # Exit immediately if a command fails

# ---------------------------
# Color output helpers
# ---------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# ---------------------------
# Check root privileges
# ---------------------------
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo: sudo ./setup.sh"
    exit 1
fi

log_info "Starting CineWorld server setup..."

# =============================================================================
# 1. System Update
# =============================================================================
log_info "Updating system packages..."
apt-get update -y && apt-get upgrade -y

# =============================================================================
# 2. Install Essential Build Tools
# =============================================================================
log_info "Installing essential build tools and libraries..."
apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    unzip

# =============================================================================
# 3. Install Python 3 and pip
# =============================================================================
log_info "Installing Python 3, pip, and virtual environment support..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev

# Install system libraries required by Python packages (Pillow, cryptography, pymysql)
log_info "Installing system libraries for Python dependencies..."
apt-get install -y \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    pkg-config

# =============================================================================
# 4. Install MySQL 8.0
# =============================================================================
log_info "Installing MySQL 8.0 server and client..."
apt-get install -y \
    mysql-server \
    mysql-client \
    libmysqlclient-dev

# Enable and start MySQL service
log_info "Enabling MySQL service..."
systemctl enable mysql
systemctl start mysql

# =============================================================================
# 5. Install Nginx (Reverse Proxy)
# =============================================================================
log_info "Installing Nginx..."
apt-get install -y nginx

# Enable and start Nginx service
log_info "Enabling Nginx service..."
systemctl enable nginx
systemctl start nginx

# =============================================================================
# 6. Install Certbot for HTTPS/TLS certificates
# =============================================================================
log_info "Installing Certbot for Let's Encrypt SSL certificates..."
apt-get install -y certbot python3-certbot-nginx

# =============================================================================
# 7. Create Application Directory Structure
# =============================================================================
APP_DIR="/opt/cineworld"

log_info "Creating application directory structure at ${APP_DIR}..."

mkdir -p "${APP_DIR}/services/catalog"
mkdir -p "${APP_DIR}/services/otp"
mkdir -p "${APP_DIR}/services/identity"
mkdir -p "${APP_DIR}/services/booking"
mkdir -p "${APP_DIR}/services/payment"
mkdir -p "${APP_DIR}/services/redemption"
mkdir -p "${APP_DIR}/services/management"
mkdir -p "${APP_DIR}/services/scheduler"
mkdir -p "${APP_DIR}/frontend"
mkdir -p "${APP_DIR}/database"
mkdir -p "${APP_DIR}/logs"
mkdir -p "${APP_DIR}/uploads"
mkdir -p "${APP_DIR}/config"

# =============================================================================
# 8. Create Python Virtual Environments for Each Service
# =============================================================================
log_info "Creating Python virtual environments for each microservice..."

SERVICES=("catalog" "otp" "identity" "booking" "payment" "redemption" "management" "scheduler")

for service in "${SERVICES[@]}"; do
    log_info "  -> Creating venv for ${service}..."
    python3 -m venv "${APP_DIR}/services/${service}/venv"
done

# =============================================================================
# 9. Create .env Template File
# =============================================================================
log_info "Creating environment variable template..."
cat > "${APP_DIR}/config/.env.template" << 'EOF'
# =============================================================================
# CineWorld Environment Variables Template
# Copy this file to .env and fill in the actual values.
# DO NOT commit the .env file to version control.
# =============================================================================

# MySQL Database Configuration
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=movie_booking_db
MYSQL_USER=
MYSQL_PASSWORD=
DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/movie_booking_db?charset=utf8mb4

# SMTP Configuration (for OTP email sending)
SMTP_EMAIL=
SMTP_PASSWORD=

# Application Ports (defaults)
CATALOG_PORT=8001
OTP_PORT=8002
IDENTITY_PORT=8003
BOOKING_PORT=8004
PAYMENT_PORT=8005
REDEMPTION_PORT=8006
MANAGEMENT_PORT=8007
FRONTEND_PORT=3000
EOF

# =============================================================================
# 10. Configure Firewall (UFW)
# =============================================================================
log_info "Configuring UFW firewall..."
ufw allow OpenSSH        # SSH access
ufw allow 'Nginx Full'   # HTTP (80) and HTTPS (443)
ufw --force enable

log_info "Firewall rules applied:"
ufw status verbose

# =============================================================================
# 11. Summary
# =============================================================================
echo ""
echo "=============================================="
log_info "CineWorld server setup completed successfully!"
echo "=============================================="
echo ""
echo "Installed components:"
echo "  - Python 3      : $(python3 --version)"
echo "  - pip            : $(pip3 --version | head -c 30)"
echo "  - MySQL          : $(mysql --version)"
echo "  - Nginx          : $(nginx -v 2>&1)"
echo "  - Certbot        : $(certbot --version 2>&1)"
echo "  - UFW Firewall   : Enabled (SSH, HTTP, HTTPS)"
echo ""
echo "Application directory: ${APP_DIR}"
echo ""
echo "Next steps:"
echo "  1. Copy your application code to ${APP_DIR}/"
echo "  2. Copy .env.template to .env and fill in credentials"
echo "  3. Initialize the MySQL database with init.sql"
echo "  4. Install Python dependencies in each service venv"
echo "  5. Configure Nginx reverse proxy"
echo "  6. Setup process manager (systemd) for each service"
echo "  7. Obtain SSL certificate with Certbot"
echo ""
