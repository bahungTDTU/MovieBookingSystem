# Repository Structure

This document describes the finalized repository structure after applying professional conventions for the MovieBookingSystem project.

## Directory Tree

```
MovieBookingSystem/
├── .github/                    # GitHub-specific configurations
│   └── workflows/             # CI/CD workflows (for future phases)
│
├── backend/                   # Backend application (Flask)
│   ├── app/
│   │   ├── __init__.py       # Flask app initialization
│   │   ├── models.py         # Database models
│   │   ├── routes/           # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py       # Authentication routes
│   │   │   ├── movies.py     # Movie management routes
│   │   │   ├── bookings.py   # Booking routes
│   │   │   └── users.py      # User profile routes
│   │   ├── services/         # Business logic layer
│   │   ├── utils/            # Utility functions
│   │   └── config.py         # Application configuration
│   ├── migrations/           # Database migrations
│   ├── tests/                # Unit and integration tests
│   ├── requirements.txt      # Python dependencies
│   └── run.py               # Application entry point
│
├── frontend/                  # Frontend application (HTML/CSS/JS)
│   ├── static/
│   │   ├── css/             # Stylesheets
│   │   ├── js/              # JavaScript files
│   │   └── images/          # Image assets
│   ├── templates/           # HTML templates
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── movies.html
│   │   ├── booking.html
│   │   └── profile.html
│   └── README.md
│
├── scripts/                   # Automation scripts
│   └── setup.sh             # Linux server setup automation
│
├── docs/                      # Documentation
│   ├── screenshots/          # Evidence screenshots
│   │   ├── phase1/          # Phase 1 screenshots
│   │   ├── phase2/          # Phase 2 screenshots
│   │   └── phase3/          # Phase 3 screenshots
│   ├── api/                  # API documentation
│   └── deployment/           # Deployment guides
│
├── phase1/                    # Phase 1 deliverables
│   ├── repository-structure/ # This document
│   ├── automation-scripts/   # Copy of automation scripts
│   ├── configurations/       # Configuration files
│   ├── screenshots/          # Screenshots for Phase 1
│   ├── evidence/            # Additional evidence
│   └── README.md            # Phase 1 summary
│
├── phase2/                    # Phase 2 deliverables
│   └── README.md
│
├── phase3/                    # Phase 3 deliverables
│   └── README.md
│
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── docker-compose.yml       # Docker composition (for future phases)
├── README.md                # Main project documentation
└── LICENSE                  # Project license

```

## Professional Conventions Applied

### 1. **Clear Separation of Concerns**
- Backend and frontend are separated into distinct directories
- Business logic is isolated in the `services/` layer
- Routes are organized by feature (auth, movies, bookings, users)

### 2. **Configuration Management**
- Environment variables stored in `.env` (not tracked by Git)
- `.env.example` provided as a template for team members
- Configuration centralized in `backend/config.py`

### 3. **Documentation Structure**
- Each phase has its own deliverables directory
- Screenshots and evidence are organized by phase
- API documentation separated from deployment guides

### 4. **Security Best Practices**
- No credentials in source code
- `.gitignore` configured to exclude sensitive files
- Separate configuration for different environments

### 5. **Scalability Considerations**
- Modular structure allows easy addition of new features
- Clear separation enables independent scaling of frontend/backend
- Tests directory prepared for comprehensive test coverage

### 6. **Version Control Best Practices**
- Feature branch workflow enforced through branch protection
- Commit messages follow conventional format
- Pull request templates for consistent code reviews

## File Naming Conventions

- **Python files**: lowercase with underscores (snake_case)
- **Directories**: lowercase with hyphens (kebab-case)
- **Configuration files**: standard names (.env, .gitignore, etc.)
- **Documentation**: UPPERCASE for important docs (README.md, STRUCTURE.md)

## Branch Strategy

- `main`: Production-ready code (protected)
- `feature/*`: New features (e.g., feature/user-authentication)
- `bugfix/*`: Bug fixes (e.g., bugfix/login-validation)
- `hotfix/*`: Critical production fixes

## Dependency Management

- Python dependencies: `requirements.txt`
- Frontend dependencies: Managed via CDN links (Bootstrap, jQuery)
- System dependencies: Automated via `scripts/setup.sh`

## Future Considerations

- `docker-compose.yml`: Container orchestration (Phase 2)
- `.github/workflows/`: CI/CD pipelines (Phase 2/3)
- `tests/`: Comprehensive test suite expansion
- `docs/api/`: OpenAPI/Swagger specification
