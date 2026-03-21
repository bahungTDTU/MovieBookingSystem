# Configuration Files

This directory contains all configuration files created during Phase 1 of the MovieBookingSystem project.

## Files Included

### 1. `.gitignore`

**Purpose**: Specifies intentionally untracked files that Git should ignore.

**Categories**:
- **Python artifacts**: `__pycache__/`, `*.pyc`, virtual environments
- **Docker volumes**: `mysql_data/`
- **Environment variables**: `.env`, `.env.local`
- **IDE files**: `.vscode/`, `.idea/`, swap files
- **OS files**: `.DS_Store`, `Thumbs.db`
- **Logs**: `*.log`, `logs/`
- **Agent context**: `agent.md`

**Best Practices**:
- Prevents sensitive information from being committed
- Reduces repository size by excluding generated files
- Improves team collaboration by ignoring IDE-specific files
- Keeps the repository clean and professional

### 2. `.env.example`

**Purpose**: Template for environment variables required by the application.

**Variables**:

#### Database Configuration
- `MYSQL_ROOT_PASSWORD`: MySQL root password
- `MYSQL_DATABASE`: Database name (movie_booking_db)
- `MYSQL_USER`: Database user
- `MYSQL_PASSWORD`: Database user password
- `DATABASE_URL`: Full database connection string

#### SMTP Configuration (for OTP service)
- `SMTP_EMAIL`: Email address for sending OTPs
- `SMTP_PASSWORD`: App password (16-digit for Gmail)

**Usage**:
```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your actual values
nano .env
```

**Security Notes**:
- `.env` is excluded from Git via `.gitignore`
- Never commit actual credentials to version control
- Use strong passwords for production environments
- For Gmail SMTP, use App Passwords (not your regular password)

## Configuration Best Practices Applied

### 1. **Separation of Secrets**
- All sensitive data in environment variables
- Example template provided for team members
- Actual secrets never in version control

### 2. **Environment-Specific Configuration**
- Support for multiple environments (.env.local, .env.production)
- Database URLs can be easily switched
- SMTP credentials can differ per environment

### 3. **Documentation**
- Clear comments in `.env.example`
- Descriptive variable names
- Usage instructions included

### 4. **Security First**
- `.env` files automatically ignored by Git
- No default passwords in examples
- Guidelines for strong password generation

## Additional Configuration Files (for reference)

While not included in this phase, future configuration files may include:

- `docker-compose.yml`: Docker service orchestration
- `nginx.conf`: Nginx reverse proxy configuration
- `.github/workflows/`: CI/CD pipeline configurations
- `pytest.ini`: Test configuration
- `requirements.txt`: Python dependencies

## How to Use These Configurations

1. **For New Team Members**:
   ```bash
   git clone <repository-url>
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **For Deployment**:
   - Review `.gitignore` to ensure it matches your environment
   - Create `.env` from `.env.example`
   - Use strong, unique passwords for production
   - Consider using secret management tools for production

3. **For Development**:
   - Keep `.env` updated locally
   - Never commit `.env` to Git
   - Share configuration changes via `.env.example`
   - Document any new environment variables

## Validation

To verify your configuration is correct:

```bash
# Check that .env exists and is not tracked
git status .env  # Should show as ignored

# Verify required variables are set
source .env
echo $MYSQL_DATABASE  # Should output: movie_booking_db
```

## Troubleshooting

**Issue**: `.env` file is being tracked by Git
**Solution**:
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

**Issue**: SMTP authentication fails
**Solution**:
- For Gmail, enable 2FA and create an App Password
- Use the 16-digit App Password, not your regular password
- Check that SMTP_EMAIL and SMTP_PASSWORD are correctly set

**Issue**: Database connection fails
**Solution**:
- Verify DATABASE_URL format
- Check MySQL service is running
- Confirm user has correct permissions
