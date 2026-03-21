# Phase 1 Submission Checklist

Use this checklist to ensure you have completed all Phase 1 requirements before submission.

---

## 📋 Pre-Submission Checklist

### 1. Repository Structure ✓

**Location**: `phase1/repository-structure/`

- [ ] `STRUCTURE.md` clearly documents the finalized repository structure
- [ ] Professional conventions are explained
- [ ] Directory tree is accurate and up-to-date
- [ ] Naming conventions are documented
- [ ] Branch strategy is explained

**Quick Verify**:
```bash
cd phase1/repository-structure
cat STRUCTURE.md | head -50  # Review first 50 lines
```

---

### 2. Automation Scripts ✓

**Location**: `phase1/automation-scripts/`

- [ ] `setup.sh` script is present and executable
- [ ] Script includes all required installations:
  - [ ] Python 3 + pip + venv
  - [ ] MySQL 8.0
  - [ ] Nginx
  - [ ] Certbot
  - [ ] UFW firewall
  - [ ] Application directory creation
- [ ] Script is documented with README.md
- [ ] Script has been tested (or test output documented)

**Quick Verify**:
```bash
cd phase1/automation-scripts
ls -lh setup.sh        # Check file exists and is executable
head -20 setup.sh      # Review script header
cat README.md          # Review documentation
```

**Optional Test** (if you have Ubuntu VM):
```bash
# Test in a safe environment only!
sudo ./setup.sh
```

---

### 3. Configuration Files ✓

**Location**: `phase1/configurations/`

- [ ] `.gitignore` is present and complete
  - [ ] Excludes Python artifacts
  - [ ] Excludes Docker volumes
  - [ ] Excludes environment files (.env)
  - [ ] Excludes IDE files
  - [ ] Excludes OS files
  - [ ] Excludes logs
- [ ] `.env.example` is present
  - [ ] Contains database configuration variables
  - [ ] Contains SMTP configuration
  - [ ] No actual credentials (only placeholders)
- [ ] `README.md` documents both configuration files

**Quick Verify**:
```bash
cd phase1/configurations
cat .gitignore         # Review ignore rules
cat .env.example       # Verify template (no real credentials!)
cat README.md          # Review documentation

# Verify .env is NOT in repository
git status .env        # Should show as ignored, not tracked
```

---

### 4. Screenshots & Visual Evidence ✓

**Location**: `phase1/screenshots/`

#### Core Requirements (Minimum)

- [ ] `01-branch-protection-rules.png` - Shows branch protection settings
- [ ] `02-pull-request-example-1.png` - First PR example
- [ ] `03-pull-request-example-2.png` - Second PR example (different feature/fix)
- [ ] `04-pull-request-code-review.png` - Shows code review process
- [ ] `05-commit-history-main-branch.png` - Shows commit history on main
- [ ] `06-commit-graph-network.png` - Shows branch merges in network graph
- [ ] `07-individual-commit-details.png` - Shows conventional commit format
- [ ] `08-repository-overview.png` - Repository main page

#### Screenshot Quality Checks

- [ ] All screenshots are clear and readable
- [ ] Text is not blurry or too small
- [ ] UI elements are visible
- [ ] No sensitive information exposed (API keys, personal emails)
- [ ] Filenames follow naming convention
- [ ] Images are in PNG or JPG format

**Quick Verify**:
```bash
cd phase1/screenshots/core-requirements
ls -lh                 # List all screenshots with sizes
# Open each image to verify quality
```

#### Additional Evidence (Optional but Recommended)

- [ ] Feature branch creation screenshots
- [ ] Code review conversation screenshots
- [ ] Team collaboration evidence
- [ ] Merge strategy demonstration

**Documentation**:
- [ ] `screenshots/README.md` is present
- [ ] README documents what each screenshot shows
- [ ] Naming convention is explained

---

### 5. Evidence & Artifacts ✓

**Location**: `phase1/evidence/`

- [ ] `git-workflow.md` documents the Git workflow used
- [ ] Workflow includes:
  - [ ] Branch strategy explanation
  - [ ] Step-by-step developer workflow
  - [ ] Commit message conventions
  - [ ] Code review process
  - [ ] Merge procedure
  - [ ] Best practices and don'ts
- [ ] `README.md` explains what evidence is included

#### Optional but Impressive

- [ ] Workflow diagram (visual representation)
- [ ] Code review checklist
- [ ] Automation test results
- [ ] Team collaboration notes
- [ ] Meeting notes or decisions

**Quick Verify**:
```bash
cd phase1/evidence
cat git-workflow.md | head -100  # Review workflow documentation
cat README.md                    # Review evidence guide
ls -la                           # List all artifacts
```

---

### 6. Main Phase 1 README ✓

**Location**: `phase1/README.md`

- [ ] README provides clear overview of Phase 1
- [ ] All 5 required components are listed
- [ ] Directory structure is documented
- [ ] Requirements checklist shows what was met
- [ ] Links to sub-directories work
- [ ] Evidence locations are clearly referenced
- [ ] Professional formatting and language

**Quick Verify**:
```bash
cd phase1
cat README.md | head -100  # Review overview
# Verify all links work by checking referenced files exist
```

---

### 7. Repository-Level Checks ✓

**GitHub Repository**: https://github.com/bahungTDTU/MovieBookingSystem

#### Branch Protection

- [ ] Navigate to: Settings → Branches → Branch protection rules
- [ ] `main` branch has protection enabled
- [ ] Required reviewers: at least 1
- [ ] No force pushes allowed
- [ ] No deletions allowed
- [ ] (Screenshot captured: `screenshots/core-requirements/01-branch-protection-rules.png`)

#### Pull Requests

- [ ] At least 2 merged/closed PRs exist
- [ ] PRs show meaningful code changes
- [ ] PRs have descriptions/conversations
- [ ] PRs show review and approval process
- [ ] (Screenshots captured: `02-pull-request-example-*.png`)

#### Commit History

- [ ] `main` branch has clean commit history
- [ ] Commits follow conventional format
- [ ] Multiple team members have commits
- [ ] No direct commits to `main` (all via merges)
- [ ] (Screenshots captured: `05-commit-history-main-branch.png`, etc.)

#### Root Configuration

- [ ] Root `.gitignore` is properly configured
- [ ] Root `.env.example` exists
- [ ] Root `README.md` is professional and complete
- [ ] No `.env` file in repository (verify with `git ls-files | grep .env`)

**Quick Verify**:
```bash
# From repository root
cat README.md           # Review main README
cat .gitignore         # Verify ignore rules
cat .env.example       # Verify template exists
git log --oneline -20  # Review recent commits
git ls-files | grep -E "\.env$"  # Should return nothing (no .env tracked)
```

---

### 8. Security & Compliance Checks ✓

- [ ] No credentials committed to repository
  ```bash
  git log --all -p | grep -i password  # Should NOT find real passwords
  git log --all -p | grep -i secret    # Should NOT find API keys
  ```

- [ ] `.env` is ignored and not tracked
  ```bash
  git status .env        # Should show as ignored or not found
  git ls-files .env      # Should return nothing
  ```

- [ ] `.env.example` contains only placeholders
  ```bash
  cat .env.example | grep -i "your_"  # Should see placeholders like "your_password"
  ```

- [ ] No sensitive data in screenshots
  - Review all screenshots for exposed secrets
  - Blur or redact if necessary

---

### 9. Documentation Quality ✓

For each README file, verify:

- [ ] `phase1/README.md` - Complete and professional
- [ ] `phase1/repository-structure/STRUCTURE.md` - Accurate structure
- [ ] `phase1/automation-scripts/README.md` - Script documented
- [ ] `phase1/configurations/README.md` - Config files explained
- [ ] `phase1/screenshots/README.md` - Screenshot guide complete
- [ ] `phase1/evidence/README.md` - Evidence explained
- [ ] `phase1/evidence/git-workflow.md` - Workflow detailed

#### Quality Criteria

Each document should:
- [ ] Be well-formatted with clear headers
- [ ] Use proper grammar and spelling
- [ ] Include code examples where appropriate
- [ ] Have working internal links
- [ ] Be free of placeholder text (TODO, XXX, etc.)

---

### 10. Final Verification ✓

**Complete Phase 1 Structure Check**:

```bash
cd phase1
tree -L 3  # Or use: find . -type f -o -type d
```

**Expected output**:
```
phase1/
├── README.md
├── repository-structure/
│   └── STRUCTURE.md
├── automation-scripts/
│   ├── setup.sh
│   └── README.md
├── configurations/
│   ├── .gitignore
│   ├── .env.example
│   └── README.md
├── screenshots/
│   ├── README.md
│   ├── core-requirements/
│   │   ├── 01-branch-protection-rules.png
│   │   ├── 02-pull-request-example-1.png
│   │   ├── ... (more screenshots)
│   └── additional-evidence/ (optional)
└── evidence/
    ├── README.md
    └── git-workflow.md
```

#### File Count Verification

Minimum files expected:
- [ ] `phase1/README.md` (1)
- [ ] `repository-structure/STRUCTURE.md` (1)
- [ ] `automation-scripts/setup.sh` + README (2)
- [ ] `configurations/` files (3: .gitignore, .env.example, README.md)
- [ ] `screenshots/README.md` (1)
- [ ] `screenshots/core-requirements/*.png` (8 minimum)
- [ ] `evidence/` files (2+: git-workflow.md, README.md)

**Total minimum**: ~20 files

```bash
find phase1 -type f | wc -l  # Should be 20+
```

---

### 11. Submission Preparation ✓

#### Create Submission Package (if required)

```bash
# Navigate to repository root
cd /path/to/MovieBookingSystem

# Create a ZIP of phase1 directory
zip -r phase1-submission.zip phase1/

# Or create a tarball
tar -czf phase1-submission.tar.gz phase1/

# Verify archive
unzip -l phase1-submission.zip  # or: tar -tzf phase1-submission.tar.gz
```

#### Git Commit & Push

- [ ] All phase1 changes are committed
  ```bash
  git status  # Should show clean or only untracked files
  ```

- [ ] Committed to appropriate branch
  ```bash
  git branch  # Verify current branch
  ```

- [ ] Pushed to GitHub
  ```bash
  git push origin <branch-name>
  ```

- [ ] Create final PR if needed (to merge phase1 work to main)

#### Final GitHub Verification

- [ ] Visit repository on GitHub
- [ ] Verify all files are present in phase1/ directory
- [ ] Check that screenshots display correctly
- [ ] Verify README.md renders properly on GitHub
- [ ] Test a few internal links in README files

---

### 12. Additional Quality Checks ✓

#### Spelling & Grammar

- [ ] Run spell check on all README files
- [ ] Review for professional tone
- [ ] Check for consistency in terminology

#### Code Quality

- [ ] `setup.sh` uses proper bash syntax
- [ ] Script includes error handling
- [ ] Script has comments explaining key steps

#### Accessibility

- [ ] Screenshots have descriptive file names
- [ ] Documentation can be understood without screenshots
- [ ] Links provide context about destination

---

## 🎯 Submission Ready Criteria

You are ready to submit when ALL of the following are true:

1. ✅ All 5 required components are present in `phase1/`
2. ✅ All minimum screenshots are captured and clear
3. ✅ No credentials or sensitive data in repository
4. ✅ `.gitignore` and `.env.example` are properly configured
5. ✅ Branch protection is enabled on `main`
6. ✅ At least 2 PRs demonstrate workflow
7. ✅ Commit history shows professional workflow
8. ✅ All documentation is complete and professional
9. ✅ Automation script is present and documented
10. ✅ Everything is pushed to GitHub

---

## ⚠️ Common Mistakes to Avoid

- ❌ Including `.env` file in repository
- ❌ Committing actual passwords/secrets
- ❌ Blurry or tiny screenshots
- ❌ Missing screenshots of branch protection
- ❌ Incomplete automation script
- ❌ No PR examples or only 1 PR
- ❌ Direct commits to `main` branch
- ❌ Generic or unclear commit messages
- ❌ Missing documentation files
- ❌ Broken links in README files
- ❌ TODO or placeholder text left in documentation
- ❌ Poor grammar or unprofessional language

---

## 📝 Final Review

Before submitting, answer these questions:

1. **Can someone understand your Git workflow from the documentation?**
   - [ ] Yes, it's clearly explained

2. **Do your screenshots prove you implemented branch protection?**
   - [ ] Yes, settings are visible

3. **Can your automation script be run on a fresh Ubuntu server?**
   - [ ] Yes, it's complete and tested/verified

4. **Is your repository structure professional and well-organized?**
   - [ ] Yes, follows conventions

5. **Would you be proud to show this to a potential employer?**
   - [ ] Yes, it demonstrates professional skills

If you answered "Yes" to all questions above, you're ready to submit! 🚀

---

## 📞 Help & Support

**Issues or Questions?**
- Review the Phase 1 requirements document
- Check `phase1/README.md` for guidance
- Review individual directory README files
- Ask instructor/TA if still unclear

**Found a mistake after submission?**
- Some platforms allow resubmission
- Document what you would fix
- Apply learnings to Phase 2 and Phase 3

---

**Last Updated**: March 21, 2026
**Version**: 1.0
