<template>
  <div class="admin-layout flex h-screen overflow-hidden bg-[var(--color-bg)]">
    <!-- Sidebar -->
    <aside class="w-72 bg-[var(--color-surface)] border-r border-[var(--color-border)] flex flex-col">
      <!-- Logo/Header -->
      <div class="p-5 border-b border-[var(--color-border)]">
        <router-link to="/dashboard" class="flex items-center gap-3">
          <span class="text-3xl">🎓</span>
          <div>
            <h1 class="text-lg font-bold text-[var(--color-text-primary)]">LSX</h1>
            <p class="text-sm text-[var(--color-text-secondary)]">{{ sidebarTitle }}</p>
          </div>
        </router-link>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto p-5">
        <!-- Back to User Dashboard -->
        <router-link
          to="/dashboard"
          class="flex items-center gap-2.5 px-4 py-2.5 mb-4 rounded-lg text-sm font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)] transition-colors border border-dashed border-[var(--color-border)]"
        >
          <span>←</span>
          <span>{{ t('nav.back_to_dashboard') }}</span>
        </router-link>

        <div class="space-y-1.5">
          <template v-for="item in menuItems" :key="item.path">
            <!-- Section Header -->
            <div
              v-if="item.section && menuItems.indexOf(item) > 0"
              class="px-4 py-3 mt-2 text-xs font-bold text-[var(--color-text-secondary)] uppercase tracking-wider"
            >
              <span class="text-lg mr-2">{{ item.icon }}</span>{{ item.label }}
            </div>

            <!-- Menu Item - Router Link -->
            <router-link
              v-if="!item.section && !item.openWindow"
              :to="item.path"
              class="flex items-center gap-3.5 px-4 py-2.5 rounded-lg text-base font-medium transition-colors"
              :class="{
                'bg-primary-100 text-primary-900': isActive(item.path),
                'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)]': !isActive(item.path)
              }"
            >
              <span class="text-xl">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>

            <!-- Menu Item - Window Opener -->
            <button
              v-if="!item.section && item.openWindow"
              @click="item.onWindowOpen?.()"
              class="w-full flex items-center gap-3.5 px-4 py-2.5 rounded-lg text-base font-medium transition-colors text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)]"
            >
              <span class="text-xl">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </button>
          </template>
        </div>
      </nav>

      <!-- User Section -->
      <div class="p-5 border-t border-[var(--color-border)]">
        <div class="flex items-center gap-3.5 mb-4">
          <div class="w-11 h-11 bg-primary-100 rounded-full flex items-center justify-center">
            <span class="text-primary-700 font-semibold text-base">
              {{ userInitials }}
            </span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-base font-medium text-[var(--color-text-primary)] truncate">
              {{ authStore.fullName }}
            </p>
            <p class="text-sm text-[var(--color-text-secondary)] truncate">{{ authStore.userRole }}</p>
          </div>
        </div>

        <button
          @click="handleLogout"
          class="w-full px-4 py-2.5 text-base font-medium text-red-700 hover:bg-red-50 rounded-lg transition-colors"
        >
          {{ t('auth.logout') }}
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden min-h-0">
      <!-- Top Bar -->
      <header class="flex-shrink-0 bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ pageTitle }}</h2>
            <p v-if="pageSubtitle" class="text-sm text-[var(--color-text-secondary)]">{{ pageSubtitle }}</p>
          </div>

          <!-- Actions Slot -->
          <div class="flex items-center gap-4">
            <LanguageSelector :show-label="false" :show-request-option="false" />
            <slot name="header-actions"></slot>
          </div>
        </div>
      </header>

      <!-- Page Content with Desktop Layer -->
      <div class="flex-1 relative">
        <div class="absolute inset-0 overflow-hidden">
          <DesktopLayer>
            <div class="p-2">
              <router-view></router-view>
            </div>
          </DesktopLayer>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/store/modules/core'
import { useWindowStore } from '@/store/modules/desktop'
import { DesktopLayer } from '@/components/base/workspace'
import { LanguageSelector } from '@/components/base/core/i18n'

// ============================================================================
// Props
// ============================================================================

interface Props {
  pageTitle?: string
  pageSubtitle?: string
  isOrgAdmin?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  pageTitle: '',
  pageSubtitle: '',
  isOrgAdmin: false
})

// ============================================================================
// Composables
// ============================================================================

const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()
const authStore = useAuthStore()
const windowStore = useWindowStore()

// Load window sizes from server when admin layout mounts
onMounted(async () => {
  if (authStore.isLoggedIn) {
    await windowStore.loadWindowSizesFromServer()
  }
})

// ============================================================================
// Computed
// ============================================================================

const sidebarTitle = computed(() => {
  // locale.value triggers reactivity on language change
  void locale.value
  return props.isOrgAdmin ? t('admin.org_admin') : t('admin.system_admin')
})

const userInitials = computed(() => {
  const firstName = authStore.user?.first_name || ''
  const lastName = authStore.user?.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
})

const menuItems = computed(() => {
  // locale.value triggers reactivity on language change
  void locale.value
  if (props.isOrgAdmin) {
    return [
      { path: '/org', label: t('org.nav.dashboard'), icon: '📊' },
      { path: '/org/users', label: t('org.nav.members'), icon: '👥' },
      { path: '/org/courses', label: t('org.nav.courses'), icon: '📚' },
      { path: '/org/analytics', label: t('org.nav.analytics'), icon: '📈' },
      { path: '/org/settings', label: t('org.nav.settings'), icon: '⚙️' }
    ]
  } else {
    return [
      // Dashboard
      { path: '/admin', label: t('admin.nav.dashboard'), icon: '📊', section: true },

      // User Management
      {
        path: '/admin/user-group-management',
        label: t('admin.userGroupManagement.title'),
        icon: '👥',
        openWindow: true,
        onWindowOpen: openUserGroupManagementWindow
      },
      { path: '/admin/organisations', label: t('admin.nav.organisations'), icon: '🏢' },

      // Content Management
      {
        path: '/admin/kurs-editor',
        label: t('admin.nav.courseEditor'),
        icon: '📚',
        openWindow: true,
        onWindowOpen: openCourseListEditorWindow
      },
      { path: '/admin/categories', label: t('admin.nav.categories'), icon: '📁' },
      { path: '/admin/translations', label: t('admin.nav.translations'), icon: '🌐' },

      // Business & Analytics
      { path: '/admin/billing', label: t('admin.nav.billing'), icon: '💰', section: true },
      { path: '/admin/analytics', label: t('admin.nav.analytics'), icon: '📈' },
      { path: '/admin/audit-logs', label: t('admin.nav.audit_logs'), icon: '📋' },

      // System
      {
        path: '/admin/system-settings',
        label: t('admin.nav.settings'),
        icon: '⚙️',
        openWindow: true,
        onWindowOpen: openSystemSettingsWindow
      }
    ]
  }
})

// ============================================================================
// Methods
// ============================================================================

const isActive = (path: string): boolean => {
  return route.path === path || route.path.startsWith(path + '/')
}

/**
 * Open System Settings window with tabs
 */
const openSystemSettingsWindow = () => {
  windowStore.openWindow({
    type: 'admin-system-settings',
    title: t('admin.nav.settings'),
    icon: '⚙️',
    preferredPosition: { x: 100, y: 100 },
    size: { width: 800, height: 600 }
  })
}

/**
 * Open User & Group Management window with tabs
 */
const openUserGroupManagementWindow = () => {
  windowStore.openWindow({
    type: 'admin-user-group-management',
    title: t('admin.userGroupManagement.title'),
    icon: '👥',
    preferredPosition: { x: 120, y: 120 },
    size: { width: 1000, height: 700 }
  })
}

/**
 * Open Course List Editor window with tabs (Manual & AI)
 */
const openCourseListEditorWindow = () => {
  windowStore.openWindow({
    type: 'admin-course-list-editor',
    title: t('admin.nav.courseEditor'),
    icon: '📚',
    preferredPosition: { x: 140, y: 140 },
    size: { width: 1100, height: 750 }
  })
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
