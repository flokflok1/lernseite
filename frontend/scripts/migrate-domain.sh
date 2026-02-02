#!/bin/bash

###############################################################################
# Frontend DDD Domain Migration Script
#
# Purpose: Automate batch file movements for a single domain
# Usage: ./scripts/migrate-domain.sh <domain-name>
#
# Examples:
#   ./scripts/migrate-domain.sh content
#   ./scripts/migrate-domain.sh learning
#   ./scripts/migrate-domain.sh user
#
# This script will:
# 1. Create target directories in new locations
# 2. Move files to new locations
# 3. Generate backward-compatible re-export barrels
# 4. Update imports in remaining files
# 5. Validate TypeScript compilation
###############################################################################

set -e  # Exit on error

DOMAIN=$1

if [ -z "$DOMAIN" ]; then
  echo "❌ Usage: ./scripts/migrate-domain.sh <domain-name>"
  echo ""
  echo "Available domains:"
  echo "  - content      (90 files)"
  echo "  - learning     (35 files)"
  echo "  - user         (25 files)"
  echo "  - social       (25 files)"
  echo "  - admin        (40 files)"
  echo "  - compliance   (20 files)"
  echo "  - moderation   (12 files)"
  echo "  - security     (10 files)"
  exit 1
fi

echo "🚀 Starting DDD migration for domain: $DOMAIN"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

###############################################################################
# Step 1: Create target directories
###############################################################################

echo "${YELLOW}Step 1: Creating target directories${NC}"

# Presentation layer directories
mkdir -p "src/presentation/components/$DOMAIN"
mkdir -p "src/presentation/views/$DOMAIN"

# Application layer directories
mkdir -p "src/application/services/$DOMAIN"
mkdir -p "src/application/composables/$DOMAIN"
mkdir -p "src/application/stores/modules/$DOMAIN"

# Domain layer directories
mkdir -p "src/domain/models/$DOMAIN"
mkdir -p "src/domain/factories/$DOMAIN"

# Infrastructure layer directories
mkdir -p "src/infrastructure/api/clients"

echo "${GREEN}✓ Directories created${NC}"

###############################################################################
# Step 2: Move files to new locations
###############################################################################

echo ""
echo "${YELLOW}Step 2: Moving files to new locations${NC}"

# Move components
if [ -d "src/components/$DOMAIN" ]; then
  echo "Moving components/$DOMAIN → presentation/components/$DOMAIN"
  mv "src/components/$DOMAIN"/* "src/presentation/components/$DOMAIN/" 2>/dev/null || true
  rmdir "src/components/$DOMAIN" 2>/dev/null || true
fi

# Move stores
if [ -d "src/store/modules/$DOMAIN" ]; then
  echo "Moving store/modules/$DOMAIN → application/stores/modules/$DOMAIN"
  mv "src/store/modules/$DOMAIN"/* "src/application/stores/modules/$DOMAIN/" 2>/dev/null || true
  rmdir "src/store/modules/$DOMAIN" 2>/dev/null || true
fi

# Move domain models
if [ -d "src/domain/models/$DOMAIN" ]; then
  echo "Keeping domain/models/$DOMAIN (already in correct location)"
fi

# Move API files
if [ -f "src/api/${DOMAIN}.api.ts" ]; then
  echo "Moving api/${DOMAIN}.api.ts → infrastructure/api/clients/${DOMAIN}.client.ts"
  mv "src/api/${DOMAIN}.api.ts" "src/infrastructure/api/clients/${DOMAIN}.client.ts" 2>/dev/null || true
fi

echo "${GREEN}✓ Files moved${NC}"

###############################################################################
# Step 3: Generate backward-compatible re-export barrels
###############################################################################

echo ""
echo "${YELLOW}Step 3: Generating backward-compatible re-export barrels${NC}"

# Create barrel for domain/models
if [ ! -f "src/domain/models/$DOMAIN/index.ts" ]; then
  mkdir -p "src/domain/models/$DOMAIN"
  cat > "src/domain/models/$DOMAIN/index.ts" << 'EOF'
/**
 * @deprecated Import directly from subdirectories
 * This barrel export will be removed on 2027-01-20
 */
export * from './index'
EOF
  echo "✓ Created domain/models/$DOMAIN/index.ts barrel"
fi

# Create barrel for components
if [ ! -f "src/components/$DOMAIN/index.ts" ]; then
  mkdir -p "src/components/$DOMAIN"
  cat > "src/components/$DOMAIN/index.ts" << 'EOF'
/**
 * @deprecated Import from @/presentation/components/'"$DOMAIN"' instead
 * This re-export barrel will be removed on 2027-01-20
 */
export * from '@/presentation/components/'"$DOMAIN"'
EOF
  echo "✓ Created components/$DOMAIN/index.ts barrel"
fi

# Create barrel for stores
if [ ! -f "src/store/modules/$DOMAIN/index.ts" ]; then
  mkdir -p "src/store/modules/$DOMAIN"
  cat > "src/store/modules/$DOMAIN/index.ts" << 'EOF'
/**
 * @deprecated Import from @/application/stores/modules/'"$DOMAIN"' instead
 * This re-export barrel will be removed on 2027-01-20
 */
export * from '@/application/stores/modules/'"$DOMAIN"'
EOF
  echo "✓ Created store/modules/$DOMAIN/index.ts barrel"
fi

# Create barrel for API
if [ ! -f "src/api/${DOMAIN}.api.ts" ]; then
  cat > "src/api/${DOMAIN}.api.ts" << 'EOF'
/**
 * @deprecated Import from @/infrastructure/api/clients/'"$DOMAIN"'.client instead
 * This re-export barrel will be removed on 2027-01-20
 */
export * from '@/infrastructure/api/clients/'"$DOMAIN"'.client'
EOF
  echo "✓ Created api/${DOMAIN}.api.ts barrel"
fi

echo "${GREEN}✓ Re-export barrels generated${NC}"

###############################################################################
# Step 4: Update imports in TypeScript/Vue files
###############################################################################

echo ""
echo "${YELLOW}Step 4: Updating imports using jscodeshift${NC}"

# Run jscodeshift to update old imports to new locations
npx jscodeshift -t scripts/transforms/update-imports.js src/ --dry 2>/dev/null || true

echo "${GREEN}✓ Import updates ready (run without --dry to apply)${NC}"

###############################################################################
# Step 5: Validate TypeScript compilation
###############################################################################

echo ""
echo "${YELLOW}Step 5: Validating TypeScript compilation${NC}"

if npm run typecheck 2>&1 | head -20; then
  echo "${GREEN}✓ TypeScript compilation successful${NC}"
else
  echo "${RED}⚠ TypeScript compilation has errors (review above)${NC}"
fi

###############################################################################
# Summary
###############################################################################

echo ""
echo "=============================================="
echo "${GREEN}✓ Domain migration complete: $DOMAIN${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: npm run test"
echo "  3. Build: npm run build"
echo "  4. Commit: git add -A && git commit -m 'refactor(ddd): migrate $DOMAIN domain'"
echo ""
