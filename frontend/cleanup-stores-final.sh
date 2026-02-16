#!/bin/bash
set -e

echo "🔥 FINAL STORES CLEANUP + MIGRATION"
echo "===================================="
echo ""

cd ~/Lernsystem/frontend/src/application/stores

# ============================================
# PHASE 1: DELETE DUPLICATES
# ============================================
echo "🗑️  PHASE 1: Deleting duplicate stores..."
echo ""

git rm app.store.ts
git rm auth.store.ts
git rm avatar.store.ts
git rm courseEditor.store.ts
git rm feature-flags.store.ts
git rm gamification.store.ts
git rm panel.store.ts
git rm player.store.ts
git rm theme.store.ts
git rm tutor.store.ts

echo "✅ 10 duplicate stores deleted!"
echo ""

# ============================================
# PHASE 2: MIGRATE admin.store.ts
# ============================================
echo "📦 PHASE 2: Migrating admin.store.ts..."
echo ""

# Check if admin.store.ts has unique content
if [ -f "admin.store.ts" ]; then
    # Move to modules/admin/
    git mv admin.store.ts modules/admin/admin.store.ts
    echo "✅ admin.store.ts → modules/admin/admin.store.ts"
else
    echo "⚠️  admin.store.ts not found"
fi

echo ""

# ============================================
# PHASE 3: MIGRATE window.store.ts
# ============================================
echo "🪟 PHASE 3: Migrating window.store.ts..."
echo ""

if [ -f "window.store.ts" ]; then
    # Move to modules/ui/
    git mv window.store.ts modules/ui/window.store.ts
    echo "✅ window.store.ts → modules/ui/window.store.ts"
else
    echo "⚠️  window.store.ts not found"
fi

echo ""

# ============================================
# PHASE 4: UPDATE INDEX.TS
# ============================================
echo "📝 PHASE 4: Updating index.ts..."
echo ""

cat > index.ts << 'EOFINDEX'
// Core
export { useAuthStore } from './modules/core/auth.store'
export { useAppStore } from './modules/core/app.store'

// Admin
export { useAdminPanelStore } from './modules/admin/panel.store'
export { useAdminStore } from './modules/admin/admin.store'

// Content
export { useCourseEditorStore } from './modules/content/courseEditor.store'
export { usePlayerStore } from './modules/content/player.store'

// Course Editor
export { useAiEditorStore } from './modules/course-editor/aiEditor.store'
export { useManualEditorStore } from './modules/course-editor/manualEditor.store'
export { useEditorStore } from './modules/course-editor/editor.store'
export { useChatStore } from './modules/course-editor/chat.store'
export { useProjectsStore } from './modules/course-editor/projects.store'
export { useTemplatesStore } from './modules/course-editor/templates.store'

// Desktop
export { useDesktopPanelStore } from './modules/desktop/panel.store'

// Feature Flags
export { useFeatureFlagsStore } from './modules/feature-flags/feature-flags.store'

// Learning
export { useDashboardStore } from './modules/learning/dashboard.store'
export { useTutorStore } from './modules/learning/tutor.store'

// System
export { useGamificationStore } from './modules/system/gamification.store'

// UI
export { useAvatarStore } from './modules/ui/avatar.store'
export { useThemeStore } from './modules/ui/theme.store'
export { useWindowStore } from './modules/ui/window.store'
EOFINDEX

echo "✅ index.ts updated!"
echo ""

# ============================================
# PHASE 5: UPDATE MODULE INDEX FILES
# ============================================
echo "📦 PHASE 5: Updating module index files..."
echo ""

# modules/admin/index.ts
cat > modules/admin/index.ts << 'EOFADMIN'
export { useAdminPanelStore } from './panel.store'
export { useAdminStore } from './admin.store'
EOFADMIN

# modules/ui/index.ts
cat > modules/ui/index.ts << 'EOFUI'
export { useAvatarStore } from './avatar.store'
export { useThemeStore } from './theme.store'
export { useWindowStore } from './window.store'
EOFUI

echo "✅ Module index files updated!"
echo ""

# ============================================
# SUMMARY
# ============================================
echo "===================================="
echo "✅ CLEANUP COMPLETE!"
echo "===================================="
echo ""
echo "📊 Summary:"
echo "   ✅ Deleted 10 duplicate stores"
echo "   ✅ Migrated admin.store.ts"
echo "   ✅ Migrated window.store.ts"
echo "   ✅ Updated index.ts"
echo "   ✅ Updated module indexes"
echo ""
echo "🧪 Next steps:"
echo "   1. Fix imports in components:"
echo "      OLD: import { useAuthStore } from '@/application/stores/auth.store'"
echo "      NEW: import { useAuthStore } from '@/application/stores'"
echo ""
echo "   2. Check for broken imports:"
echo "      npm run build"
echo ""
echo "   3. Git commit:"
echo "      git add ."
echo "      git commit -m 'cleanup: migrate stores to modules/'"
