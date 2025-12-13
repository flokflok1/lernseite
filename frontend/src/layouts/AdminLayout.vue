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
          <span>Zum User-Dashboard</span>
        </router-link>

        <div class="space-y-1.5">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
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
          Abmelden
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
          <div>
            <slot name="header-actions"></slot>
          </div>
        </div>
      </header>

      <!-- Page Content with Desktop Layer -->
      <div class="flex-1 relative">
        <div class="absolute inset-0 overflow-hidden">
          <LsxDesktopLayer>
            <div class="p-2">
              <router-view></router-view>
            </div>
          </LsxDesktopLayer>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth.store'
import { useWindowStore } from '@/store/window.store'
import LsxDesktopLayer from '@/components/desktop/LsxDesktopLayer.vue'

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
  return props.isOrgAdmin ? 'Organisation Admin' : 'System Admin'
})

const userInitials = computed(() => {
  const firstName = authStore.user?.first_name || ''
  const lastName = authStore.user?.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
})

const menuItems = computed(() => {
  if (props.isOrgAdmin) {
    return [
      { path: '/org', label: 'Dashboard', icon: '📊' },
      { path: '/org/users', label: 'Mitglieder', icon: '👥' },
      { path: '/org/courses', label: 'Kurse', icon: '📚' },
      { path: '/org/analytics', label: 'Analytics', icon: '📈' },
      { path: '/org/settings', label: 'Einstellungen', icon: '⚙️' }
    ]
  } else {
    return [
      { path: '/admin', label: 'Dashboard', icon: '📊' },
      { path: '/admin/users', label: 'Benutzer', icon: '👥' },
      { path: '/admin/organisations', label: 'Organisationen', icon: '🏢' },
      { path: '/admin/courses', label: 'Kurse', icon: '📚' },
      { path: '/admin/categories', label: 'Kategorien', icon: '📁' },
      { path: '/admin/ki-studio', label: 'KI-Studio', icon: '✨' },
      { path: '/admin/billing', label: 'Billing', icon: '💰' },
      { path: '/admin/analytics', label: 'Analytics', icon: '📈' },
      { path: '/admin/audit-logs', label: 'Audit Logs', icon: '📋' }
    ]
  }
})

// ============================================================================
// Methods
// ============================================================================

const isActive = (path: string): boolean => {
  return route.path === path || route.path.startsWith(path + '/')
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
