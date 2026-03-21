# Automation Scripts

This directory contains automation scripts developed for Phase 1.

## Scripts Overview

### 1. setup.sh - Server Setup Automation

**Purpose**: Automates the complete setup of an Ubuntu 22.04+ server for hosting the MovieBookingSystem application.

**What it does**:
- Updates system packages
- Installs Python 3 + pip + virtual environment
- Installs and configures MySQL 8.0 database
- Installs Nginx as reverse proxy
- Installs Certbot for SSL certificate management
- Configures UFW firewall with appropriate rules
- Creates application directory structure at `/opt/cineworld/`
- Sets up proper permissions

**Usage**:
```bash
# Make the script executable
chmod +x setup.sh

# Run with sudo
sudo ./setup.sh
```

**Requirements**:
- Ubuntu 22.04 or higher
- Root or sudo access
- Internet connection

**Security Features**:
- Configures UFW firewall (allows SSH, HTTP, HTTPS)
- Sets up MySQL with secure installation prompts
- Creates dedicated application directory with proper permissions
- Prepares for SSL certificate installation

**Post-Installation**:
After running the script, you need to:
1. Configure MySQL root password when prompted
2. Create application database and user
3. Set up virtual environment in `/opt/cineworld/`
4. Deploy application code
5. Configure Nginx site-specific settings
6. Set up SSL with Certbot

## Testing the Script

The script has been tested on:
- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS (if applicable)

## Notes

- The script is idempotent - safe to run multiple times
- All actions are logged to console
- Failed steps will stop the script execution
- Review the script before running on production servers
