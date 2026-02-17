<!--
  EditorLayout.vue

  Layout wrapper for the /editor route.
  Provides sidebar with editor launch buttons and DesktopLayer for windowed editing.
  Follows PanelLayout pattern but simplified for course authoring context.

  Phase: B24-06 - Admin Desktop OS
-->

<template>
  <div class="editor-layout flex h-screen overflow-hidden bg-[var(--color-bg)]">
    <!-- Sidebar -->
    <aside class="w-64 bg-[var(--color-surface)] border-r border-[var(--color-border)] flex flex-col">
      <!-- Logo/Header -->
      <div class="p-5 border-b border-[var(--color-border)]">
        <router-link to="/dashboard" class="flex items-center gap-3">
          <span class="text-3xl">&#9997;&#65039;</span>
          <div>
            <h1 class="text-lg font-bold text-[var(--color-text-primary)]">LSX</h1>
            <p class="text-sm text-[var(--color-text-secondary)]">{{ sidebarTitle }}</p>
          </div>
        </router-link>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto p-5">
        <!-- Back to Panel -->
        <router-link
          to="/panel"
          class="flex items-center gap-2.5 px-4 py-2.5 mb-4 rounded-lg text-sm font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)] transition-colors border border-dashed border-[var(--color-border)]"
        >
          <span>&larr;</span>
          <span>{{ t('panel.nav.back_to_panel') }}</span>
        </router-link>

        <!-- Editor Launch Buttons -->
        <div class="space-y-2">
          <button
            class="w-full flex items-center gap-3.5 px-4 py-3 rounded-lg text-base font-medium transition-colors text-left hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)]"
            @click="openManualEditor"
          >
            <span class="text-xl">&#9998;&#65039;</span>
            <span>{{ t('panel.editor.manual.title') }}</span>
          </button>

          <button
            class="w-full flex items-center gap-3.5 px-4 py-3 rounded-lg text-base font-medium transition-colors text-left hover:bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)]"
            @click="openAIEditor"
          >
            <span class="text-xl">&#129302;</span>
            <span>{{ t('panel.editor.ai.title') }}</span>
          </button>
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
            <h2 class="text-2xl font-bold text-[var(--color-text-primary)]">{{ t('panel.editor.title') }}</h2>
            <p class="text-sm text-[var(--color-text-secondary)]">{{ t('panel.editor.subtitle') }}</p>
          </div>
          <div class="flex items-center gap-4">
            <LanguageSelector :show-label="false" :show-request-option="false" />
          </div>
        </div>
      </header>

      <!-- Page Content with Desktop Layer -->
      <div class="flex-1 relative">
        <div class="absolute inset-0 overflow-hidden">
          <DesktopLayer>
            <div class="p-2">
              <router-view />
            </div>
          </DesktopLayer>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import { DesktopLayer } from '@/presentation/components/shared/layout'
import { LanguageSelector } from '@/presentation/components/shared/layout/i18n'

const router = useRouter()
const { t, locale } = useI18n()
const authStore = useAuthStore()
const windowStore = useWindowStore()

onMounted(async () => {
  if (authStore.isLoggedIn) {
    await windowStore.loadWindowSizesFromServer()
  }
})

const sidebarTitle = computed(() => {
  void locale.value
  return t('panel.editor.title')
})

const userInitials = computed(() => {
  const firstName = authStore.user?.first_name || ''
  const lastName = authStore.user?.last_name || ''
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
})

function openManualEditor(): void {
  const existing = windowStore.getPanelsByType('editor-manual')
  if (existing.length > 0) {
    windowStore.focusWindow(existing[0].id)
    return
  }
  windowStore.openWindow({
    type: 'editor-manual',
    title: t('panel.editor.manual.title'),
    icon: '\u270E\uFE0F',
    size: { width: 1000, height: 700 },
  })
}

function openAIEditor(): void {
  const existing = windowStore.getPanelsByType('editor-ai-studio')
  if (existing.length > 0) {
    windowStore.focusWindow(existing[0].id)
    return
  }
  windowStore.openWindow({
    type: 'editor-ai-studio',
    title: t('panel.editor.ai.title'),
    icon: '\uD83E\uDD16',
    size: { width: 1000, height: 700 },
  })
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.editor-layout {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
