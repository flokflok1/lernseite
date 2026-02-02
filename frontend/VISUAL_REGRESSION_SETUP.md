# Visual Regression Testing Setup (Percy)

**Status:** Phase 0 - Foundation & Automation
**Timeline:** 2026-01-20
**Integration:** GitHub Actions CI/CD

---

## Overview

Percy automates visual regression testing by capturing screenshots of your application and comparing them across deployments. This ensures UI changes don't break layouts or introduce visual regressions during the DDD migration.

**Why Important for DDD Migration:**
- Detects unintended visual changes during large refactoring
- Automated screenshot comparison prevents manual QA bottleneck
- Catches styling issues from component reorganization
- Progressive validation across 7 migration phases

---

## Setup Instructions

### 1. Install Dependencies

```bash
npm install --save-dev @percy/cli @percy/cypress @percy/cli-exec
```

### 2. Configure Percy

Configuration already created: `.percyrc.yml`

Key settings:
- **Capture Widths:** 375px (mobile), 768px (tablet), 1280px (desktop)
- **Critical Pages:** Dashboard, Auth, Courses, Learning, Admin
- **Parallel Processing:** 4 parallel capture workers
- **Network Idle:** 750ms (wait for async data)

### 3. Get Percy Token

1. Go to https://percy.io
2. Sign up (free tier includes 5,000 screenshots/month)
3. Create organization
4. Generate project token
5. Add to GitHub secrets: `PERCY_TOKEN`

### 4. Add to GitHub Secrets

```bash
# In GitHub repository:
# Settings → Secrets and variables → Actions
# Add new secret:
#   Name: PERCY_TOKEN
#   Value: <your-percy-token>
```

---

## Usage

### Manual Snapshot (Local Development)

```bash
# Build application
npm run build

# Capture baseline snapshots
PERCY_TOKEN=<your-token> npx percy exec -- npm run preview

# On first run: creates baseline
# On subsequent runs: compares against baseline
```

### Automated in CI/CD

Snapshots run automatically in GitHub Actions:

```yaml
# .github/workflows/ddd-migration-check.yml
- name: Percy Visual Regression
  run: npx percy exec -- npm run preview
  env:
    PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}
```

---

## Critical Pages for Each Phase

### Phase 0 (Current)
- Dashboard
- Authentication flows

### Phase 1: Content & Learning
- `/courses` - Course list
- `/courses/create` - Course creation
- `/learn/[course]/lessons` - Lesson viewer

### Phase 2: User Domain
- `/profile` - User profile
- `/settings` - Settings pages

### Phase 5: Security & Studio
- `/studio` - AI Studio (HIGH RISK - many components)
- `/admin/security` - Security settings

### Phase 7: Infrastructure
- `/dashboard` - Full dashboard (many stores refactored)
- Admin panels (role-based components reorganized)

---

## Snapshot Workflow

```
1. Build Application
   └─→ npm run build

2. Start Preview Server
   └─→ npm run preview

3. Percy Captures Screenshots
   ├─→ 375px (mobile)
   ├─→ 768px (tablet)
   └─→ 1280px (desktop)

4. Upload to Percy Dashboard
   └─→ Compare against baseline

5. Generate Visual Diff Report
   └─→ Review changes in Percy UI
```

---

## Interpreting Results

### Green ✅ - No Changes
Screenshot matches baseline exactly.

### Blue ◆ - New Snapshots
First-time capture, becomes new baseline.

### Red ❌ - Visual Regression
Differences detected. Review and approve if intentional.

---

## Integration with DDD Migration

### Phase Checkpoints

Each migration phase includes visual regression testing:

```bash
# After Phase 1 (Content Domain) migration:
npm run migrate:check        # Validate imports
npm run build                # Build application
PERCY_TOKEN=xxx npx percy exec -- npm run preview  # Visual regression
npm run test                 # Run tests
```

### Preventing Regressions

1. **Before Migration:** Capture baseline (`percy:baseline`)
2. **During Migration:** Incremental snapshots per domain
3. **After Migration:** Full snapshot suite
4. **Review:** Approve intentional changes in Percy dashboard

---

## GitHub Actions Integration

### Complete Workflow

```yaml
# .github/workflows/ddd-migration-check.yml

name: DDD Migration Validation

on: [push, pull_request]

jobs:
  visual-regression:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      - name: Build
        run: npm run build

      - name: Validate Imports
        run: npm run validate:imports

      - name: Percy Visual Regression
        run: npx percy exec -- npm run preview
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}

      - name: Report
        if: always()
        run: npm run migrate:report
```

---

## Cost & Limits

**Free Tier:**
- 5,000 snapshots/month
- 5 parallel workers
- Unlimited projects

**Calculation for LSX:**
- Phase 0: ~50 pages × 3 widths = 150 snapshots
- Phase 1: +100 snapshots
- Full Suite: ~500-1000 snapshots total

**Expected Usage:** ~50 snapshots/week during migration ✅ (Within free tier)

---

## Troubleshooting

### Token Not Recognized

```bash
# Export token before running
export PERCY_TOKEN=<your-token>
npx percy exec -- npm run preview
```

### Screenshots Not Captured

```bash
# Ensure preview server is running
npm run build
npm run preview  # Keep terminal open in another window

# In another terminal:
export PERCY_TOKEN=<your-token>
npx percy exec -- curl http://localhost:5173/
```

### Percy CLI Not Found

```bash
# Reinstall
npm install --save-dev @percy/cli @percy/cypress

# Clear cache
npm cache clean --force
npm install
```

---

## Alternative: Chromatic

If Percy is unavailable, Chromatic offers similar functionality:

```bash
npm install --save-dev chromatic
npm run chromatic
```

**Note:** Chromatic is optimized for Storybook, while Percy works with any web application.

---

## Next Steps

1. ✅ Create `.percyrc.yml` configuration
2. ✅ Document setup instructions
3. ⏳ Install dependencies: `npm install --save-dev @percy/cli`
4. ⏳ Get Percy token and add to GitHub secrets
5. ⏳ Run baseline snapshot: `percy exec -- npm run preview`
6. ⏳ Integrate into CI/CD pipeline
7. ⏳ Review and approve baseline

---

## Resources

- **Percy Documentation:** https://docs.percy.io/
- **CLI Reference:** https://docs.percy.io/docs/cli
- **GitHub Actions Integration:** https://docs.percy.io/docs/github-actions
- **Pricing:** https://percy.io/pricing

---

**Phase 0 Task:** Setup complete. Awaiting token generation and npm dependency installation.
