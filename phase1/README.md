# Phase 1 - Git Workflow & Linux Automation

## Overview

This directory contains all deliverables for Phase 1 of the MovieBookingSystem project, demonstrating professional Git workflow implementation and Linux automation capabilities.

---

## 📋 Deliverables Checklist

### ✅ Required Components

1. **Repository Structure** - [`repository-structure/`](./repository-structure/)
   - [x] Final repository structure documentation
   - [x] Professional conventions applied
   - [x] Clear directory organization

2. **Automation Scripts** - [`automation-scripts/`](./automation-scripts/)
   - [x] Linux server setup script (`setup.sh`)
   - [x] Script documentation and usage guide
   - [x] Ubuntu 22.04+ compatibility

3. **Configuration Files** - [`configurations/`](./configurations/)
   - [x] Completed `.gitignore`
   - [x] Environment variables template (`.env.example`)
   - [x] Configuration documentation

4. **Screenshots** - [`screenshots/`](./screenshots/)
   - [x] Branch protection settings
   - [x] Pull request examples (minimum 2)
   - [x] Commit history demonstrating workflow
   - [x] Additional evidence as needed

5. **Evidence & Artifacts** - [`evidence/`](./evidence/)
   - [x] Git workflow documentation
   - [x] Branching strategy explained
   - [x] Commit message conventions
   - [x] Additional supporting materials

---

## 📂 Directory Structure

```
phase1/
├── README.md                        # This file - Phase 1 overview
├── repository-structure/            # (1) Repository structure documentation
│   └── STRUCTURE.md                 # Finalized structure with conventions
├── automation-scripts/              # (2) Automation scripts
│   ├── setup.sh                     # Linux server setup automation
│   └── README.md                    # Script documentation
├── configurations/                  # (3) Configuration files
│   ├── .gitignore                   # Git ignore rules
│   ├── .env.example                 # Environment variables template
│   └── README.md                    # Configuration documentation
├── screenshots/                     # (4) Visual evidence
│   ├── README.md                    # Screenshot guide
│   ├── core-requirements/           # Required screenshots
│   │   ├── 01-branch-protection-rules.png
│   │   ├── 02-pull-request-example-1.png
│   │   ├── 03-pull-request-example-2.png
│   │   ├── 04-pull-request-code-review.png
│   │   ├── 05-commit-history-main-branch.png
│   │   ├── 06-commit-graph-network.png
│   │   ├── 07-individual-commit-details.png
│   │   └── 08-repository-overview.png
│   └── additional-evidence/         # Optional supplementary screenshots
└── evidence/                        # (5) Additional artifacts
    ├── README.md                    # Evidence documentation
    └── git-workflow.md              # Detailed workflow guide
```

---

## 🎯 Phase 1 Requirements Met

### 1. GitHub Repository Setup
- **URL**: https://github.com/bahungTDTU/MovieBookingSystem.git
- **Main Branch**: `main` (protected)
- **Team Collaboration**: All members have meaningful commit history
- **Professional README**: Clear documentation at repository root

### 2. Branch Protection Rules ✓
Successfully configured on `main` branch:
- ✓ Require pull request reviews before merging
- ✓ Minimum 1 approving review required
- ✓ Dismiss stale reviews when new commits are pushed
- ✓ Require status checks to pass before merging
- ✓ Require branches to be up to date before merging
- ✗ No force pushes allowed
- ✗ No branch deletions allowed
- ✓ Include administrators in restrictions (optional)

**Evidence**: See `screenshots/core-requirements/01-branch-protection-rules.png`

### 3. Linux Automation Script ✓
**Location**: [`automation-scripts/setup.sh`](./automation-scripts/setup.sh)

**Capabilities**:
- Automated Ubuntu 22.04+ server preparation
- Installs and configures:
  - Python 3 + pip + virtual environment
  - MySQL 8.0 database server
  - Nginx web server (reverse proxy)
  - Certbot for SSL certificate management
  - UFW firewall with security rules
- Creates application directory structure at `/opt/cineworld/`
- Sets appropriate file permissions
- Idempotent - safe to run multiple times

**Usage**:
```bash
chmod +x automation-scripts/setup.sh
sudo ./automation-scripts/setup.sh
```

### 4. Git Workflow Implementation ✓

**Branch Strategy**:
- `main` - Protected production branch
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Emergency fix branches

**Workflow Process**:
1. Create feature branch from `main`
2. Make changes and commit with conventional messages
3. Push branch to remote repository
4. Create Pull Request on GitHub
5. Request code review from team member
6. Address review comments if any
7. Obtain approval (minimum 1 reviewer)
8. Merge to `main` via GitHub UI
9. Delete feature branch after successful merge

**Commit Message Convention**:
```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scopes: auth, booking, movie, user, db
```

**Examples**:
- `feat(auth): add OTP verification for login`
- `fix(booking): resolve double booking issue`
- `docs(readme): update installation instructions`

**Evidence**: See `screenshots/core-requirements/` for PR examples and commit history

### 5. Configuration Management ✓

**`.gitignore`** - Properly configured to exclude:
- Python artifacts (`__pycache__/`, `*.pyc`, `venv/`)
- Docker volumes (`mysql_data/`)
- Environment variables (`.env`, `.env.local`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Logs (`*.log`, `logs/`)

**`.env.example`** - Template includes:
- MySQL database credentials
- Database connection URL
- SMTP configuration for OTP service

**Security**: No credentials committed to repository ✓

### 6. Security Best Practices ✓
- All sensitive data in environment variables
- `.env` excluded from version control
- No hardcoded secrets in source code
- Branch protection prevents unauthorized changes
- Code review required for all changes

### 7. Professional Conventions ✓
- Clear directory structure with logical organization
- Separation of concerns (backend, frontend, scripts, docs)
- Consistent naming conventions
- Comprehensive documentation
- Modular and maintainable codebase

---

## 📸 Evidence Documentation

All required evidence is documented in the [`screenshots/`](./screenshots/) directory with a comprehensive guide for capturing and organizing visual proof.

**Core Requirements** (minimum):
1. Branch protection settings screenshot
2. At least 2 pull request examples
3. Code review process demonstration
4. Commit history showing team collaboration
5. Network graph showing branch merges
6. Repository overview

**Additional Evidence** (recommended):
- Feature branch creation process
- Merge strategy demonstration
- Team contribution graphs
- Individual commit details

**Guide**: See [`screenshots/README.md`](./screenshots/README.md) for detailed instructions

---

## 🚀 Quick Start for Reviewers

### View Repository Structure
```bash
cd phase1/repository-structure
cat STRUCTURE.md
```

### Review Automation Script
```bash
cd phase1/automation-scripts
cat setup.sh
cat README.md
```

### Check Configuration Files
```bash
cd phase1/configurations
cat .gitignore
cat .env.example
cat README.md
```

### View Screenshots
```bash
cd phase1/screenshots
ls -la core-requirements/
# Open images to review evidence
```

### Read Workflow Documentation
```bash
cd phase1/evidence
cat git-workflow.md
```

---

## 📝 Additional Documentation

- **Git Workflow**: [`evidence/git-workflow.md`](./evidence/git-workflow.md) - Comprehensive guide
- **Repository Structure**: [`repository-structure/STRUCTURE.md`](./repository-structure/STRUCTURE.md)
- **Automation Guide**: [`automation-scripts/README.md`](./automation-scripts/README.md)
- **Configuration Guide**: [`configurations/README.md`](./configurations/README.md)
- **Screenshot Guide**: [`screenshots/README.md`](./screenshots/README.md)

---

## ✅ Compliance Verification

### Git Workflow Requirements
- [x] Protected main branch
- [x] Feature branch workflow
- [x] Pull request process
- [x] Code review requirement
- [x] Conventional commit messages
- [x] No direct commits to main
- [x] All changes via PRs

### Automation Requirements
- [x] Linux setup script created
- [x] Supports Ubuntu 22.04+
- [x] Installs all required dependencies
- [x] Configures database, web server, firewall
- [x] Creates proper directory structure
- [x] Script is documented

### Documentation Requirements
- [x] Professional README
- [x] Repository structure documented
- [x] Configuration files explained
- [x] Workflow process documented
- [x] Screenshots organized
- [x] Evidence provided

### Security Requirements
- [x] No credentials in repository
- [x] Environment variables used
- [x] .gitignore properly configured
- [x] Branch protection enabled
- [x] Code review enforced

---

## 🎓 Learning Outcomes Demonstrated

Through Phase 1 deliverables, we demonstrate:

1. **Git Version Control Mastery**
   - Professional branch management
   - Effective code review process
   - Conventional commit practices
   - Team collaboration skills

2. **Linux System Administration**
   - Bash scripting for automation
   - Package management
   - Service configuration
   - Security hardening

3. **DevOps Best Practices**
   - Infrastructure as Code principles
   - Configuration management
   - Security-first mindset
   - Documentation discipline

4. **Professional Software Development**
   - Clean code organization
   - Separation of concerns
   - Scalable architecture
   - Quality assurance through reviews

---

## 📞 Contact & Support

- **Repository**: https://github.com/bahungTDTU/MovieBookingSystem
- **Issues**: https://github.com/bahungTDTU/MovieBookingSystem/issues
- **Team**: View contributors in repository insights

---

## 📅 Timeline

- **Phase 1 Start**: March 12, 2026
- **Repository Setup**: March 12, 2026
- **Feature Development**: March 12-15, 2026
- **Phase 1 Complete**: March 21, 2026

---

## 🔄 Version History

- **v1.0** (2026-03-12): Initial phase 1 structure
- **v1.1** (2026-03-15): Added feature implementations
- **v1.2** (2026-03-21): Finalized all deliverables and documentation

---

**Status**: ✅ Complete and ready for review

**Last Updated**: March 21, 2026
