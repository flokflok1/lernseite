# LernsystemX Frontend - Production Build Instructions

This document describes how to build and deploy the LernsystemX Vue.js frontend for production.

---

## Prerequisites

- Node.js 20+ installed
- npm or yarn package manager
- Access to frontend source code

---

## Build Process

### 1. Navigate to Frontend Directory

```bash
cd /path/to/Lernsystem/frontend
```

### 2. Install Dependencies (Clean Install)

```bash
# Clean install from package-lock.json
npm ci

# Or with yarn
yarn install --frozen-lockfile
```

**Why `npm ci`?**
- Faster than `npm install`
- Uses exact versions from `package-lock.json`
- Removes `node_modules` first (clean install)
- Ensures reproducible builds

### 3. Set Environment Variables

Create `.env.production` in the frontend directory:

```env
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=LernsystemX
VITE_APP_VERSION=1.0.0
```

### 4. Run Production Build

```bash
npm run build

# Or with yarn
yarn build
```

This command:
- Runs Vite in production mode
- Minifies JavaScript and CSS
- Optimizes images
- Generates source maps (optional)
- Tree-shakes unused code
- Code-splits for lazy loading
- Creates `dist/` directory with optimized files

**Build output:**
```
dist/
├── index.html
├── assets/
│   ├── index-a1b2c3d4.js
│   ├── index-e5f6g7h8.css
│   ├── logo-i9j0k1l2.png
│   └── ...
└── favicon.ico
```

### 5. Verify Build

```bash
# Check dist directory
ls -lh dist/

# Verify file sizes (should be small)
du -sh dist/
```

**Expected output:**
- `dist/` directory: ~2-5 MB (depending on assets)
- Main JS bundle: ~200-500 KB (gzipped)
- CSS bundle: ~50-100 KB (gzipped)

---

## Deployment to Server

### Option 1: Direct Copy to Server

```bash
# Copy dist folder to server
scp -r dist/* user@server:/opt/lsx/frontend/

# Or with rsync
rsync -avz --delete dist/ user@server:/opt/lsx/frontend/
```

### Option 2: systemd Script

Create `/opt/lsx/scripts/deploy-frontend.sh`:

```bash
#!/bin/bash
set -e

# Configuration
FRONTEND_DIR="/opt/lsx/frontend"
BUILD_DIR="/tmp/lsx-frontend-build"
REPO_URL="https://github.com/your-org/lsx-frontend.git"
BRANCH="main"

# Clone/pull latest code
if [ -d "$BUILD_DIR" ]; then
    cd "$BUILD_DIR"
    git pull origin "$BRANCH"
else
    git clone -b "$BRANCH" "$REPO_URL" "$BUILD_DIR"
    cd "$BUILD_DIR"
fi

# Install dependencies
npm ci

# Build
npm run build

# Backup current frontend
if [ -d "$FRONTEND_DIR" ]; then
    mv "$FRONTEND_DIR" "${FRONTEND_DIR}.backup.$(date +%Y%m%d%H%M%S)"
fi

# Deploy new build
mkdir -p "$FRONTEND_DIR"
cp -r dist/* "$FRONTEND_DIR/"

# Set permissions
chown -R www-data:www-data "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"

# Cleanup old backups (keep last 3)
ls -dt ${FRONTEND_DIR}.backup.* | tail -n +4 | xargs rm -rf

echo "Frontend deployed successfully!"
```

Make executable:
```bash
chmod +x /opt/lsx/scripts/deploy-frontend.sh
```

### Option 3: CI/CD Pipeline (GitHub Actions Example)

Create `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Build
        working-directory: ./frontend
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}

      - name: Deploy to server
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          source: "frontend/dist/*"
          target: "/opt/lsx/frontend/"
          strip_components: 2

      - name: Reload Nginx
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SSH_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: sudo systemctl reload nginx
```

---

## Post-Deployment

### 1. Set Proper Permissions

```bash
chown -R www-data:www-data /opt/lsx/frontend
chmod -R 755 /opt/lsx/frontend
```

### 2. Test Frontend

```bash
# Check if files exist
ls -la /opt/lsx/frontend/

# Test Nginx serves files
curl -I https://yourdomain.com
```

### 3. Clear CDN Cache (if using CDN)

```bash
# CloudFlare example
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
     -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}'
```

---

## Rollback

If deployment fails, rollback to previous version:

```bash
# List backups
ls -lt /opt/lsx/frontend.backup.*

# Restore backup
rm -rf /opt/lsx/frontend
mv /opt/lsx/frontend.backup.20251116120000 /opt/lsx/frontend

# Reload Nginx
systemctl reload nginx
```

---

## Performance Optimization

### 1. Enable Gzip/Brotli in Nginx

Already configured in `deployment/nginx/lsx.conf`.

### 2. Enable HTTP/2

Already configured in `deployment/nginx/lsx.conf`.

### 3. Set Cache Headers

Static assets (JS, CSS, images) cached for 1 year.
HTML files not cached (immediate updates).

### 4. Use CDN (Optional)

- CloudFlare
- AWS CloudFront
- Fastly

Point CDN to `/opt/lsx/frontend/dist` or serve via Nginx.

---

## Monitoring

### Check Build Size

```bash
# After build
npm run build -- --report

# View bundle analyzer
open dist/stats.html
```

### Lighthouse Score

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://yourdomain.com --view
```

**Target scores:**
- Performance: 90+
- Accessibility: 90+
- Best Practices: 90+
- SEO: 90+

---

## Troubleshooting

### Build Fails

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Try again
npm run build
```

### White Screen After Deployment

1. Check browser console for errors
2. Verify `VITE_API_URL` is correct
3. Check Nginx error logs: `tail -f /var/log/nginx/lsx_error.log`
4. Ensure all files copied: `ls -R /opt/lsx/frontend/`

### Assets Not Loading

1. Check Nginx configuration for static file serving
2. Verify file permissions: `chmod -R 755 /opt/lsx/frontend`
3. Check browser network tab for 404 errors

---

## Directory Structure After Deployment

```
/opt/lsx/frontend/
├── index.html
├── assets/
│   ├── index-a1b2c3d4.js
│   ├── index-e5f6g7h8.css
│   ├── logo-i9j0k1l2.png
│   └── ...
├── favicon.ico
└── manifest.json
```

---

## Automated Deployment Script

Full example: `/opt/lsx/scripts/deploy-frontend.sh` (see Option 2 above).

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Next Review:** Phase 18 (CI/CD Automation)
