# Phase 1 Screenshots & Evidence

This directory contains visual evidence demonstrating compliance with Git workflow requirements for Phase 1.

## Required Screenshots

### 1. Branch Protection Settings ✓

**What to capture**:
- Navigate to: GitHub Repository → Settings → Branches → Branch protection rules
- Show protection rules for `main` branch
- Ensure visible settings include:
  - ☑ Require pull request reviews before merging
  - ☑ Require at least 1 approving review
  - ☑ Dismiss stale PR reviews when new commits are pushed
  - ☑ Require status checks to pass
  - ☑ Require branches to be up to date before merging
  - ☑ Include administrators (if applicable)
  - ☐ Allow force pushes (should be unchecked)
  - ☐ Allow deletions (should be unchecked)

**Filename**: `01-branch-protection-rules.png`

**How to take**:
```
1. Go to: https://github.com/bahungTDTU/MovieBookingSystem/settings/branches
2. Click "Edit" on main branch protection rule
3. Take full-page screenshot showing all settings
4. Save as: 01-branch-protection-rules.png
```

---

### 2. Pull Request Examples ✓

**What to capture**: At least 2-3 representative pull requests showing:
- PR title and description
- Code changes (Files changed tab)
- Review comments and discussions
- Status checks
- Merge confirmation

**Filenames**:
- `02-pull-request-example-1.png` - Feature PR
- `03-pull-request-example-2.png` - Another feature/bugfix PR
- `04-pull-request-code-review.png` - PR with review comments

**How to take**:
```
1. Go to: https://github.com/bahungTDTU/MovieBookingSystem/pulls?q=is%3Apr
2. Open a closed/merged PR
3. Capture multiple screenshots:
   - Overview tab (title, description, status)
   - Files changed tab (code diff)
   - Conversation tab (reviews, comments)
4. Save with descriptive filenames
```

---

### 3. Commit History ✓

**What to capture**:
- Commit history showing multiple team members
- Meaningful commit messages following conventional format
- Branch strategy (feature branches merging to main)
- No direct commits to main (all via PRs)

**Filenames**:
- `05-commit-history-main-branch.png`
- `06-commit-graph-network.png` (showing branch merges)
- `07-individual-commit-details.png` (showing commit message format)

**How to take**:
```
1. Commit History:
   - Go to: https://github.com/bahungTDTU/MovieBookingSystem/commits/main
   - Capture showing last 10-15 commits
   - Save as: 05-commit-history-main-branch.png

2. Network Graph:
   - Go to: https://github.com/bahungTDTU/MovieBookingSystem/network
   - Capture showing branch merges
   - Save as: 06-commit-graph-network.png

3. Individual Commit:
   - Click on a commit to see details
   - Show conventional commit format
   - Save as: 07-individual-commit-details.png
```

---

### 4. Repository Overview ✓

**What to capture**:
- Main repository page showing:
  - Professional README
  - Clean directory structure
  - Active contributors
  - Recent activity

**Filename**: `08-repository-overview.png`

**How to take**:
```
1. Go to: https://github.com/bahungTDTU/MovieBookingSystem
2. Capture full repository main page
3. Ensure visible:
   - README preview
   - Directory structure
   - Contributor avatars
   - Last commit info
4. Save as: 08-repository-overview.png
```

---

### 5. Git Workflow Evidence (Optional but Recommended)

**Additional screenshots that strengthen your evidence**:

**5.1 Feature Branch Workflow**
- `09-feature-branch-creation.png` - Creating a feature branch
- `10-feature-branch-list.png` - List of feature branches

**5.2 Code Review Process**
- `11-code-review-requested.png` - PR with review request
- `12-code-review-approved.png` - PR with approval
- `13-code-review-changes-requested.png` - PR with requested changes

**5.3 Merge Strategy**
- `14-merge-commit-strategy.png` - Showing merge strategy
- `15-no-direct-commits-to-main.png` - Main branch protection enforcement

**5.4 Team Collaboration**
- `16-contributors-graph.png` - Contribution history
- `17-team-activity.png` - Team pulse/activity

---

## Screenshot Guidelines

### Quality Standards
- **Resolution**: Minimum 1920x1080 or high DPI
- **Format**: PNG for clarity, JPG if file size is a concern
- **Clarity**: Ensure text is readable and UI elements are visible
- **Privacy**: Blur any sensitive information (API keys, emails if private)
- **Context**: Include browser bars or timestamps when helpful

### Naming Convention
```
[Number]-[descriptive-name].png

Examples:
01-branch-protection-rules.png
02-pull-request-example-1.png
03-pull-request-code-review.png
```

### Organization
```
screenshots/
├── README.md (this file)
├── core-requirements/          # Required screenshots
│   ├── 01-branch-protection-rules.png
│   ├── 02-pull-request-example-1.png
│   ├── 03-pull-request-example-2.png
│   ├── 04-pull-request-code-review.png
│   ├── 05-commit-history-main-branch.png
│   ├── 06-commit-graph-network.png
│   ├── 07-individual-commit-details.png
│   └── 08-repository-overview.png
│
└── additional-evidence/        # Optional but recommended
    ├── 09-feature-branch-creation.png
    ├── 10-feature-branch-list.png
    ├── 11-code-review-requested.png
    └── ...
```

---

## Taking Screenshots

### Tools Recommended
- **Windows**: Windows + Shift + S (Snipping Tool)
- **Mac**: Cmd + Shift + 4 (Screenshot selection)
- **Browser Extensions**:
  - Awesome Screenshot
  - Nimbus Screenshot
  - Full Page Screen Capture

### Best Practices
1. **Full Page Captures**: Use browser extensions for long pages (commit history, PR conversations)
2. **Consistent Browser**: Use the same browser for consistent UI
3. **Clean Background**: Close unrelated tabs and windows
4. **Highlight Important Elements**: Use arrows or boxes if needed (tools like Snagit, Greenshot)
5. **Multiple Angles**: For complex evidence, take multiple screenshots showing different views

---

## Verification Checklist

Before submitting, ensure you have:

- [ ] Branch protection settings clearly visible
- [ ] At least 2 pull requests with:
  - [ ] Title and description
  - [ ] Code changes visible
  - [ ] Review comments (if any)
  - [ ] Merge status
- [ ] Commit history showing:
  - [ ] Multiple authors
  - [ ] Conventional commit messages
  - [ ] No direct commits to main
- [ ] Network graph showing branch merges
- [ ] Repository overview with clean structure
- [ ] All images are clear and readable
- [ ] Filenames follow naming convention
- [ ] No sensitive information exposed

---

## Quick Start Commands

### Option 1: Create subdirectories (recommended)
```bash
cd phase1/screenshots
mkdir -p core-requirements additional-evidence
```

### Option 2: Flat structure (simpler)
```bash
cd phase1/screenshots
# Just add your screenshots here directly
```

### After adding screenshots
```bash
# View what you have
ls -la

# Add to git
git add phase1/screenshots/*.png
git commit -m "docs: add Phase 1 evidence screenshots"
```

---

## Notes

- Screenshots should demonstrate **actual implementation**, not mock-ups
- Ensure timestamps and commit dates align with project timeline
- If you make significant changes after capture, update the screenshots
- Keep original, unedited screenshots if possible
- Consider creating a backup of all screenshots

---

## Need Help?

If you're unsure what to capture:
1. Review the Phase 1 requirements document
2. Check successful examples from previous projects (if available)
3. Ask your instructor or TA for clarification
4. Better to include more evidence than less!
