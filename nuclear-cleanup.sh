#!/bin/bash
set -e

echo "🔥 NUCLEAR CLEANUP - Backend + Frontend"
echo "========================================"
echo ""
echo "⚠️  This will:"
echo "   - Delete ALL backup files"
echo "   - Restructure backend completely"
echo "   - Clean up frontend"
echo "   - Create proper layouts"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

# ============================================
# PHASE 1: DELETE ALL BACKUPS
# ============================================
echo ""
echo "🧹 PHASE 1: Deleting backup files..."
cd ~/Lernsystem

find . -name "*.repo_bak" -delete
find . -name "*.bak" -delete
find . -name "*.backup" -delete

echo "✅ Backup files deleted!"

# ============================================
# PHASE 2: BACKEND - Complete Panel Structure
# ============================================
echo ""
echo "📦 PHASE 2: Backend restructure..."
cd ~/Lernsystem/backend

# Create all panel directories
echo "Creating panel directories..."
mkdir -p app/api/v1/panel/admin/{ai,analytics,billing,categories,config,dashboard,features,groups,i18n,organisations,owner,permissions,prompts,settings,subscriptions,users}
mkdir -p app/api/v1/panel/editor/{ai,manual,shared}
mkdir -p app/api/v1/panel/user/{profile,dashboard,social,tts}

# Create public directories
echo "Creating public directories..."
mkdir -p app/api/v1/public/{auth,courses,categories,i18n,health}

# Move files if not already moved
echo "Moving admin AI files..."
if [ -d "app/api/v1/ai/admin/providers" ]; then
    mkdir -p app/api/v1/panel/admin/ai/providers
    find app/api/v1/ai/admin/providers -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/ai/providers/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/ai/admin/models" ]; then
    mkdir -p app/api/v1/panel/admin/ai/models
    find app/api/v1/ai/admin/models -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/ai/models/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/ai/admin/profiles" ]; then
    mkdir -p app/api/v1/panel/admin/ai/profiles
    find app/api/v1/ai/admin/profiles -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/ai/profiles/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/ai/admin/pricing" ]; then
    mkdir -p app/api/v1/panel/admin/ai/pricing
    find app/api/v1/ai/admin/pricing -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/ai/pricing/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/ai/admin/stats" ]; then
    mkdir -p app/api/v1/panel/admin/ai/stats
    find app/api/v1/ai/admin/stats -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/ai/stats/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/ai/admin/jobs" ]; then
    mkdir -p app/api/v1/panel/admin/ai/jobs
    find app/api/v1/ai/admin/jobs -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/ai/jobs/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/ai/admin/core" ]; then
    mkdir -p app/api/v1/panel/admin/ai/core
    find app/api/v1/ai/admin/core -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/ai/core/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

echo "Moving editor files..."
if [ -d "app/api/v1/courses/editor/manual" ]; then
    find app/api/v1/courses/editor/manual -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/editor/manual/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/courses/editor/ai" ]; then
    find app/api/v1/courses/editor/ai -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/editor/ai/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/courses/editor/shared" ]; then
    find app/api/v1/courses/editor/shared -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/editor/shared/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

echo "Moving admin user/group files..."
if [ -d "app/api/v1/users/admin/management" ]; then
    find app/api/v1/users/admin/management -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/users/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/groups/admin" ]; then
    find app/api/v1/groups/admin -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/groups/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/categories/admin" ]; then
    find app/api/v1/categories/admin -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/categories/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

echo "Moving other admin files..."
if [ -f "app/api/v1/organisations/core.py" ]; then
    git mv app/api/v1/organisations/core.py app/api/v1/panel/admin/organisations/ 2>/dev/null || true
fi

if [ -f "app/api/v1/billing/tokens/admin.py" ]; then
    git mv app/api/v1/billing/tokens/admin.py app/api/v1/panel/admin/billing/tokens.py 2>/dev/null || true
fi

if [ -f "app/api/v1/subscriptions/core.py" ]; then
    git mv app/api/v1/subscriptions/core.py app/api/v1/panel/admin/subscriptions/ 2>/dev/null || true
fi

# i18n SPLIT
echo "Moving i18n files (split public/admin)..."
if [ -f "app/api/v1/i18n/languages.py" ]; then
    git mv app/api/v1/i18n/languages.py app/api/v1/public/i18n/ 2>/dev/null || true
fi

if [ -f "app/api/v1/i18n/translations.py" ]; then
    git mv app/api/v1/i18n/translations.py app/api/v1/public/i18n/ 2>/dev/null || true
fi

if [ -d "app/api/v1/i18n/admin" ]; then
    find app/api/v1/i18n/admin -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/i18n/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/features/admin" ]; then
    find app/api/v1/features/admin -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/features/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/prompts_system/admin" ]; then
    find app/api/v1/prompts_system/admin -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/prompts/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/dashboard/admin" ]; then
    find app/api/v1/dashboard/admin -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/dashboard/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/system/admin/settings" ]; then
    find app/api/v1/system/admin/settings -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/settings/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/system/admin/permissions" ]; then
    find app/api/v1/system/admin/permissions -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/permissions/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -f "app/api/v1/analytics/core.py" ]; then
    git mv app/api/v1/analytics/core.py app/api/v1/panel/admin/analytics/ 2>/dev/null || true
fi

if [ -f "app/api/v1/analytics/organisations.py" ]; then
    git mv app/api/v1/analytics/organisations.py app/api/v1/panel/admin/analytics/ 2>/dev/null || true
fi

if [ -d "app/api/v1/system/admin/owner" ]; then
    find app/api/v1/system/admin/owner -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/admin/owner/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

# User panel
echo "Moving user panel files..."
if [ -d "app/api/v1/profile/user" ]; then
    find app/api/v1/profile/user -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/user/profile/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/social/user" ]; then
    find app/api/v1/social/user -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/user/social/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/tts/user" ]; then
    find app/api/v1/tts/user -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/user/tts/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

if [ -d "app/api/v1/dashboard/user" ]; then
    find app/api/v1/dashboard/user -name "*.py" -exec sh -c 'git mv "$1" "app/api/v1/panel/user/dashboard/$(basename "$1")" 2>/dev/null || true' _ {} \;
fi

# Move panel config files
if [ -f "app/api/v1/panel/runner_modes.py" ]; then
    git mv app/api/v1/panel/runner_modes.py app/api/v1/panel/admin/config/ 2>/dev/null || true
fi

if [ -f "app/api/v1/panel/system_features.py" ]; then
    git mv app/api/v1/panel/system_features.py app/api/v1/panel/admin/config/ 2>/dev/null || true
fi

if [ -f "app/api/v1/panel/lm_type_compatibility.py" ]; then
    git mv app/api/v1/panel/lm_type_compatibility.py app/api/v1/panel/admin/config/ 2>/dev/null || true
fi

# Create __init__.py in all directories
echo "Creating __init__.py files..."
find app/api/v1/panel -type d -exec touch {}/__init__.py \; 2>/dev/null || true
find app/api/v1/public -type d -exec touch {}/__init__.py \; 2>/dev/null || true

echo "✅ Backend structure complete!"

# ============================================
# PHASE 3: FIX IMPORTS
# ============================================
echo ""
echo "🔧 PHASE 3: Fixing imports..."

# Fix ai.admin → panel.admin.ai
find app/api/v1/panel/admin/ai -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.ai\.admin\./from app.api.v1.panel.admin.ai./g' {} \; 2>/dev/null || true
find app/api/v1/panel/admin/ai -type f -name "*.py" -exec sed -i 's/import app\.api\.v1\.ai\.admin\./import app.api.v1.panel.admin.ai./g' {} \; 2>/dev/null || true

# Fix courses.editor → panel.editor
find app/api/v1/panel/editor -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.courses\.editor\./from app.api.v1.panel.editor./g' {} \; 2>/dev/null || true
find app/api/v1/panel/editor -type f -name "*.py" -exec sed -i 's/import app\.api\.v1\.courses\.editor\./import app.api.v1.panel.editor./g' {} \; 2>/dev/null || true

# Fix users.admin → panel.admin.users
find app/api/v1/panel/admin/users -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.users\.admin/from app.api.v1.panel.admin.users/g' {} \; 2>/dev/null || true

# Fix groups.admin → panel.admin.groups
find app/api/v1/panel/admin/groups -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.groups\.admin/from app.api.v1.panel.admin.groups/g' {} \; 2>/dev/null || true

# Fix categories.admin → panel.admin.categories
find app/api/v1/panel/admin/categories -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.categories\.admin/from app.api.v1.panel.admin.categories/g' {} \; 2>/dev/null || true

# Fix i18n imports
find app/api/v1 -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.i18n\.admin/from app.api.v1.panel.admin.i18n/g' {} \; 2>/dev/null || true

# Fix panel config imports
find app/api/v1 -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.panel\.runner_modes/from app.api.v1.panel.admin.config.runner_modes/g' {} \; 2>/dev/null || true
find app/api/v1 -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.panel\.system_features/from app.api.v1.panel.admin.config.system_features/g' {} \; 2>/dev/null || true
find app/api/v1 -type f -name "*.py" -exec sed -i 's/from app\.api\.v1\.panel\.lm_type_compatibility/from app.api.v1.panel.admin.config.lm_type_compatibility/g' {} \; 2>/dev/null || true

echo "✅ Imports fixed!"

# ============================================
# PHASE 4: FRONTEND LAYOUTS
# ============================================
echo ""
echo "🎨 PHASE 4: Creating frontend layouts..."
cd ~/Lernsystem/frontend

# AdminLayout.vue
cat > src/presentation/layouts/AdminLayout.vue << 'EOFADMIN'
<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const navigation = computed(() => [
  { name: 'Dashboard', path: '/panel/admin', icon: '📊' },
  { name: 'Users', path: '/panel/admin/users', icon: '👥', permission: 'admin.users:read' },
  { name: 'Groups', path: '/panel/admin/groups', icon: '👨‍👩‍👧', permission: 'admin.groups:read' },
  { name: 'AI Settings', path: '/panel/admin/ai', icon: '🤖', permission: 'admin.ai-providers:read' },
  { name: 'Categories', path: '/panel/admin/categories', icon: '📁', permission: 'admin.categories:read' },
  { name: 'i18n', path: '/panel/admin/i18n', icon: '🌍', permission: 'admin.i18n:read' },
  { name: 'Analytics', path: '/panel/admin/analytics', icon: '📈', permission: 'admin.dashboard:read' },
  { name: 'Billing', path: '/panel/admin/billing', icon: '💰', permission: 'admin.billing:read' },
  { name: 'Settings', path: '/panel/admin/settings', icon: '⚙️', permission: 'admin.settings:read' },
])

const canAccess = (permission?: string) => {
  if (!permission) return true
  return authStore.hasPermission?.(permission) ?? false
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>⚡ Admin Panel</h1>
      </div>
      
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          v-show="canAccess(item.permission)"
          :to="item.path"
          class="nav-item"
        >
          <span class="icon">{{ item.icon }}</span>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <button @click="logout" class="logout-btn">🚪 Logout</button>
      </div>
    </aside>
    
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background: #0f172a;
}

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  color: white;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #334155;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #334155;
}

.sidebar-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  color: #cbd5e1;
  text-decoration: none;
  transition: all 0.2s;
  margin: 0.25rem 0.5rem;
  border-radius: 0.5rem;
}

.nav-item .icon {
  font-size: 1.25rem;
}

.nav-item:hover {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.nav-item.router-link-active {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #334155;
}

.logout-btn {
  width: 100%;
  padding: 0.75rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.content {
  flex: 1;
  overflow-y: auto;
  background: #f8fafc;
}
</style>
EOFADMIN

# EditorLayout.vue
cat > src/presentation/layouts/EditorLayout.vue << 'EOFEDITOR'
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const navigation = [
  { name: '📚 My Courses', path: '/panel/editor/courses' },
  { name: '✨ AI Assistant', path: '/panel/editor/ai' },
  { name: '📊 Analytics', path: '/panel/editor/analytics' },
]

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="editor-layout">
    <header class="header">
      <div class="header-left">
        <h1>✍️ Course Editor</h1>
      </div>
      
      <nav class="header-nav">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="nav-item"
        >
          {{ item.name }}
        </router-link>
      </nav>
      
      <div class="header-right">
        <button @click="() => router.push('/panel/user/profile')" class="profile-btn">👤 Profile</button>
        <button @click="logout" class="logout-btn">🚪 Logout</button>
      </div>
    </header>
    
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.editor-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fafafa;
}

.header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 2rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
}

.header-nav {
  display: flex;
  gap: 0.5rem;
  flex: 1;
}

.nav-item {
  padding: 0.625rem 1.25rem;
  color: #6b7280;
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.nav-item.router-link-active {
  background: #3b82f6;
  color: white;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.header-right {
  display: flex;
  gap: 0.5rem;
}

.profile-btn,
.logout-btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.profile-btn {
  background: #f3f4f6;
  color: #374151;
}

.profile-btn:hover {
  background: #e5e7eb;
}

.logout-btn {
  background: #ef4444;
  color: white;
}

.logout-btn:hover {
  background: #dc2626;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}
</style>
EOFEDITOR

# UserLayout.vue
cat > src/presentation/layouts/UserLayout.vue << 'EOFUSER'
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

const router = useRouter()
const authStore = useAuthStore()

const navigation = [
  { name: '🏠 Dashboard', path: '/panel/user/dashboard' },
  { name: '👤 Profile', path: '/panel/user/profile' },
  { name: '📚 My Courses', path: '/panel/user/courses' },
  { name: '🎯 Progress', path: '/panel/user/progress' },
  { name: '💬 Social', path: '/panel/user/social' },
  { name: '⚙️ Settings', path: '/panel/user/settings' },
]

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="user-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h1>🎓 My Learning</h1>
      </div>
      
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="nav-item"
        >
          {{ item.name }}
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <button @click="logout" class="logout-btn">🚪 Logout</button>
      </div>
    </aside>
    
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.user-layout {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header h1 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #111827;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: block;
  padding: 0.75rem 1.25rem;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s;
  margin: 0.125rem 0.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #111827;
}

.nav-item.router-link-active {
  background: #eff6ff;
  color: #3b82f6;
  font-weight: 600;
  border-left: 3px solid #3b82f6;
  padding-left: calc(1.25rem - 3px);
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.logout-btn {
  width: 100%;
  padding: 0.625rem;
  background: #f3f4f6;
  color: #6b7280;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.content {
  flex: 1;
  overflow-y: auto;
  background: #fafafa;
  padding: 2rem;
}
</style>
EOFUSER

echo "✅ Layouts created!"

# ============================================
# PHASE 5: FRONTEND COMPOSABLE & COMPONENT
# ============================================
echo ""
echo "🧩 PHASE 5: Creating permission helpers..."

# usePermissions composable
mkdir -p src/application/composables
cat > src/application/composables/usePermissions.ts << 'EOFPERM'
import { computed } from 'vue'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

export function usePermissions() {
  const authStore = useAuthStore()

  const hasPermission = (code: string): boolean => {
    return authStore.hasPermission?.(code) ?? false
  }

  const hasAnyPermission = (...codes: string[]): boolean => {
    return authStore.hasAnyPermission?.(...codes) ?? false
  }

  return {
    hasPermission,
    hasAnyPermission,
    
    // Domain helpers
    canManageUsers: computed(() => hasPermission('admin.users:read')),
    canManageGroups: computed(() => hasPermission('admin.groups:read')),
    canManageAI: computed(() => hasPermission('admin.ai-providers:read')),
    canEditCourses: computed(() => hasPermission('editor.courses:write')),
    canPublishCourses: computed(() => hasPermission('editor.courses:publish')),
    canManageBilling: computed(() => hasPermission('admin.billing:read')),
    canManageI18n: computed(() => hasPermission('admin.i18n:read')),
  }
}
EOFPERM

# HasPermission component
mkdir -p src/presentation/components/shared
cat > src/presentation/components/shared/HasPermission.vue << 'EOFHASPERM'
<script setup lang="ts">
import { computed } from 'vue'
import { usePermissions } from '@/application/composables/usePermissions'

const props = defineProps<{
  permission?: string
  anyPermission?: string[]
}>()

const { hasPermission, hasAnyPermission } = usePermissions()

const hasAccess = computed(() => {
  if (props.permission) return hasPermission(props.permission)
  if (props.anyPermission) return hasAnyPermission(...props.anyPermission)
  return false
})
</script>

<template>
  <slot v-if="hasAccess" />
  <slot v-else name="fallback" />
</template>
EOFHASPERM

echo "✅ Permission helpers created!"

# ============================================
# PHASE 6: DELETE OLD EMPTY DIRECTORIES
# ============================================
echo ""
echo "🗑️  PHASE 6: Cleaning up old directories..."
cd ~/Lernsystem/backend

# Delete old empty admin directories (only if empty!)
find app/api/v1/ai/admin -type d -empty -delete 2>/dev/null || true
find app/api/v1/courses/editor -type d -empty -delete 2>/dev/null || true
find app/api/v1/users/admin -type d -empty -delete 2>/dev/null || true
find app/api/v1/groups/admin -type d -empty -delete 2>/dev/null || true
find app/api/v1/categories/admin -type d -empty -delete 2>/dev/null || true
find app/api/v1/i18n/admin -type d -empty -delete 2>/dev/null || true
find app/api/v1/features/admin -type d -empty -delete 2>/dev/null || true
find app/api/v1/dashboard/admin -type d -empty -delete 2>/dev/null || true
find app/api/v1/system/admin -type d -empty -delete 2>/dev/null || true

echo "✅ Empty directories cleaned!"

# ============================================
# PHASE 7: SUMMARY
# ============================================
echo ""
echo "=============================================="
echo "✅ NUCLEAR CLEANUP COMPLETE!"
echo "=============================================="
echo ""
echo "📊 Backend structure:"
tree ~/Lernsystem/backend/app/api/v1/panel -L 2 2>/dev/null || find ~/Lernsystem/backend/app/api/v1/panel -type d | head -30
echo ""
echo "🎨 Frontend layouts:"
ls -la ~/Lernsystem/frontend/src/presentation/layouts/*.vue 2>/dev/null || echo "Check manually"
echo ""
echo "🧪 Next steps:"
echo "1. Update auth.store.ts with hasPermission/hasAnyPermission methods"
echo "2. Test backend: cd backend && python run.py"
echo "3. Test frontend: cd frontend && npm run dev"
echo "4. Fix any remaining import errors"
echo "5. Git commit!"
echo ""
echo "📝 Manual TODOs:"
echo "   - Update app/api/v1/__init__.py (blueprint registration)"
echo "   - Update frontend router with permission guards"
echo "   - Test all panel routes"
EOF

chmod +x ~/Lernsystem/nuclear-cleanup.sh

echo ""
echo "✅ Script created: ~/Lernsystem/nuclear-cleanup.sh"
echo ""
echo "🔥 Ready to execute?"
echo "   bash ~/Lernsystem/nuclear-cleanup.sh"
