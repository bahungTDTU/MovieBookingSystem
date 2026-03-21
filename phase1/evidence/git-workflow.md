# Git Workflow for MovieBookingSystem

## Overview

This document describes the Git workflow and branching strategy adopted by the MovieBookingSystem team for Phase 1.

## Branching Strategy

### Branch Types

1. **`main`** (protected)
   - Production-ready code
   - Always stable and deployable
   - Protected with branch rules
   - No direct commits allowed
   - All changes via Pull Requests

2. **`feature/*`** (short-lived)
   - New features development
   - Naming: `feature/feature-name`
   - Example: `feature/user-authentication`, `feature/booking-system`
   - Created from: `main`
   - Merged to: `main` (via PR)
   - Deleted after merge

3. **`bugfix/*`** (short-lived)
   - Bug fixes
   - Naming: `bugfix/issue-description`
   - Example: `bugfix/login-validation`, `bugfix/booking-error`
   - Created from: `main`
   - Merged to: `main` (via PR)
   - Deleted after merge

4. **`hotfix/*`** (emergency)
   - Critical production fixes
   - Naming: `hotfix/critical-issue`
   - Example: `hotfix/security-patch`
   - Created from: `main`
   - Merged to: `main` immediately after review
   - Deleted after merge

## Workflow Diagram

```
                        main (protected)
                          │
                          │ (branch)
                          ├─────────────> feature/booking-system
                          │                      │
                          │                      │ (commits)
                          │                      │
                          │                      │ (push & create PR)
                          │ <─────────────────── │
                          │      (code review)
                          │      (approve & merge)
                          │
                          │ (branch)
                          ├─────────────> feature/user-profile
                          │                      │
                          │                      │ (commits)
                          │                      │
                          │                      │ (push & create PR)
                          │ <─────────────────── │
                          │      (code review)
                          │      (approve & merge)
                          │
                          ▼
                    (continues...)
```

## Developer Workflow

### 1. Starting New Work

```bash
# Update local main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature

# Verify you're on the new branch
git branch
```

### 2. Making Changes

```bash
# Make your code changes...

# Stage changes
git add .

# Commit with conventional message
git commit -m "feat(scope): add feature description"

# Push to remote
git push origin feature/my-feature
```

### 3. Creating Pull Request

1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your feature branch
4. Fill in PR template:
   - Clear title
   - Description of changes
   - Related issues (if any)
5. Request review from team member
6. Assign appropriate labels

### 4. Code Review Process

**As Author**:
- Respond to review comments
- Make requested changes
- Push updates to same branch
- Re-request review if needed

**As Reviewer**:
- Review code thoroughly
- Check for:
  - Functionality
  - Code quality
  - Security issues
  - Test coverage
- Leave constructive comments
- Approve or request changes

### 5. Merging

Once approved:
1. Ensure branch is up to date with main
2. Resolve any merge conflicts
3. Merge via GitHub UI (Squash and merge recommended)
4. Delete feature branch

```bash
# After merge, update local main
git checkout main
git pull origin main

# Delete local feature branch
git branch -d feature/my-feature
```

## Commit Message Convention

### Format

```
<type>(<scope>): <subject>

<body> (optional)

<footer> (optional)
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Scope (optional)

Component or module affected:
- `auth`: Authentication
- `booking`: Booking system
- `movie`: Movie management
- `user`: User management
- `db`: Database

### Examples

```bash
feat(auth): add OTP verification for login
fix(booking): resolve double booking issue
docs(readme): update installation instructions
refactor(user): simplify profile update logic
test(booking): add unit tests for booking validation
chore: update dependencies
```

## Branch Protection Rules

Applied to `main` branch:

- ✓ Require pull request reviews (minimum 1)
- ✓ Dismiss stale reviews on new commits
- ✓ Require status checks to pass
- ✓ Require branches to be up to date
- ✗ Allow force pushes (disabled)
- ✗ Allow deletions (disabled)

## Best Practices

### DO:
- ✓ Keep branches small and focused
- ✓ Commit frequently with clear messages
- ✓ Pull from main regularly to stay updated
- ✓ Write descriptive PR descriptions
- ✓ Respond to review comments promptly
- ✓ Test your changes before pushing
- ✓ Delete branches after merging

### DON'T:
- ✗ Commit directly to main
- ✗ Force push to shared branches
- ✗ Leave branches open for weeks
- ✗ Mix multiple features in one branch
- ✗ Merge without review
- ✗ Include sensitive data in commits
- ✗ Use generic commit messages like "fix" or "update"

## Conflict Resolution

When merge conflicts occur:

```bash
# Update your branch with latest main
git checkout feature/my-feature
git fetch origin
git merge origin/main

# Resolve conflicts in your editor
# (conflicts marked with <<<<<<, =======, >>>>>>>)

# After resolving
git add .
git commit -m "chore: resolve merge conflicts with main"
git push origin feature/my-feature
```

## Emergency Procedures

### Reverting a Commit

```bash
# If commit is not pushed yet
git reset --soft HEAD~1

# If commit is pushed but not merged
git revert <commit-hash>
git push origin feature/my-feature
```

### Reverting a Merged PR

1. Go to the PR on GitHub
2. Click "Revert" button
3. Create new PR with revert
4. Merge after review

## Team Guidelines

- **Code Review Response Time**: Within 24 hours
- **Branch Lifetime**: Maximum 1 week before merge or close
- **PR Size**: Keep under 400 lines of changes when possible
- **Testing**: All features should include tests (Phase 2+)
- **Documentation**: Update README/docs with significant changes

## Tools & Resources

- **Git GUI**: GitKraken, SourceTree, or GitHub Desktop (optional)
- **Commit Message**: Use tools like Commitizen for consistency
- **Code Review**: GitHub PR review features
- **Merge Conflicts**: VSCode merge editor or command line

## Quick Reference

```bash
# Common commands
git status                          # Check status
git log --oneline --graph          # View commit history
git branch -a                      # List all branches
git fetch origin                   # Fetch remote changes
git pull origin main               # Pull main branch
git push origin <branch>           # Push branch

# Cleaning up
git branch -d <branch>             # Delete local branch
git push origin --delete <branch>  # Delete remote branch
git remote prune origin            # Clean up stale remote branches
```

## Version History

- **v1.0** (2026-03-12): Initial workflow established
- **v1.1** (2026-03-15): Added commit convention details
- **v1.2** (2026-03-21): Updated with branch protection rules

---

**Last Updated**: March 21, 2026
**Maintained By**: MovieBookingSystem Team
