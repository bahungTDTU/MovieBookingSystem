# Phase 1 - Git Workflow & Linux Automation

## Deliverables

### 1. GitHub Repository
- **URL**: https://github.com/bahungTDTU/MovieBookingSystem.git
- Branch: `main` (protected)
- All team members have meaningful commit history

### 2. Branch Protection Rules
- Required pull request reviews before merging
- At least 1 reviewer per PR
- No direct commits to `main`
- No force-push allowed

### 3. Linux Automation Script
- **File**: [`scripts/setup.sh`](../scripts/setup.sh)
- Prepares Ubuntu 22.04+ server with all dependencies:
  - Python 3 + pip + venv
  - MySQL 8.0
  - Nginx (reverse proxy)
  - Certbot (SSL)
  - UFW firewall
  - Application directory structure at `/opt/cineworld/`

### 4. Git Workflow
- Feature branches → Pull Request → Code Review → Merge to `main`
- Commit messages follow conventional format
- `.gitignore` configured for Python, Docker, IDE, OS files

### 5. Security
- Credentials stored in `.env` (excluded from version control)
- `.env.example` provided as template
- No hardcoded secrets in source code

## Evidence
Screenshots are stored in [`docs/screenshots/phase1/`](../docs/screenshots/phase1/)
