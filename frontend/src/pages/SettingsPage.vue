<template>
  <div>
    <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-6">{{ $t('settings.title') }}</h1>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="space-y-6">
      <!-- Sektion: Darstellung / Theme -->
      <Card :title="$t('settings.appearance')">
        <div class="space-y-6">
          <div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-4">
              {{ $t('settings.appearanceDesc') }}
            </p>

            <!-- Theme Selection Buttons -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <!-- System Theme Button -->
              <button
                @click="selectTheme('system')"
                :class="[
                  'relative flex flex-col items-center p-4 rounded-lg border-2 transition-all',
                  themeStore.themePreference === 'system'
                    ? 'border-primary-600 ring-2 ring-primary-600 ring-opacity-50 bg-primary-50'
                    : 'border-[var(--color-border)] hover:border-primary-400 bg-[var(--color-surface)]'
                ]"
                :disabled="saving"
              >
                <div class="text-3xl mb-2">🖥️</div>
                <div class="font-semibold text-[var(--color-text-primary)]">{{ $t('settings.theme_system') }}</div>
                <div class="text-xs text-[var(--color-text-secondary)] mt-1 text-center">
                  {{ $t('settings.theme_system_desc') }}
                </div>
                <div
                  v-if="themeStore.themePreference === 'system'"
                  class="absolute top-2 right-2 w-5 h-5 bg-primary-600 rounded-full flex items-center justify-center"
                >
                  <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </button>

              <!-- Light Theme Button -->
              <button
                @click="selectTheme('light')"
                :class="[
                  'relative flex flex-col items-center p-4 rounded-lg border-2 transition-all',
                  themeStore.themePreference === 'light'
                    ? 'border-primary-600 ring-2 ring-primary-600 ring-opacity-50 bg-primary-50'
                    : 'border-[var(--color-border)] hover:border-primary-400 bg-[var(--color-surface)]'
                ]"
                :disabled="saving"
              >
                <div class="text-3xl mb-2">☀️</div>
                <div class="font-semibold text-[var(--color-text-primary)]">{{ $t('settings.theme_light') }}</div>
                <div class="text-xs text-[var(--color-text-secondary)] mt-1 text-center">
                  {{ $t('settings.theme_light_desc') }}
                </div>
                <div
                  v-if="themeStore.themePreference === 'light'"
                  class="absolute top-2 right-2 w-5 h-5 bg-primary-600 rounded-full flex items-center justify-center"
                >
                  <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </button>

              <!-- Dark Theme Button -->
              <button
                @click="selectTheme('dark')"
                :class="[
                  'relative flex flex-col items-center p-4 rounded-lg border-2 transition-all',
                  themeStore.themePreference === 'dark'
                    ? 'border-primary-600 ring-2 ring-primary-600 ring-opacity-50 bg-primary-50'
                    : 'border-[var(--color-border)] hover:border-primary-400 bg-[var(--color-surface)]'
                ]"
                :disabled="saving"
              >
                <div class="text-3xl mb-2">🌙</div>
                <div class="font-semibold text-[var(--color-text-primary)]">{{ $t('settings.theme_dark') }}</div>
                <div class="text-xs text-[var(--color-text-secondary)] mt-1 text-center">
                  {{ $t('settings.theme_dark_desc') }}
                </div>
                <div
                  v-if="themeStore.themePreference === 'dark'"
                  class="absolute top-2 right-2 w-5 h-5 bg-primary-600 rounded-full flex items-center justify-center"
                >
                  <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </button>
            </div>
          </div>

          <!-- Current Theme Info -->
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-4 border border-[var(--color-border)]">
            <div class="flex items-start gap-3">
              <div class="text-2xl">ℹ️</div>
              <div class="flex-1">
                <div class="font-medium text-[var(--color-text-primary)] mb-1">
                  {{ $t('settings.currentTheme') }}
                </div>
                <div class="text-sm text-[var(--color-text-secondary)]">
                  <span class="font-semibold">{{ $t('settings.preference') }}:</span> {{ themePreferenceLabel }}<br>
                  <span class="font-semibold">{{ $t('settings.active') }}:</span> {{ effectiveThemeLabel }}
                  <span v-if="themeStore.themePreference === 'system'" class="text-[var(--color-text-tertiary)]">
                    {{ $t('settings.fromSystem') }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Success Message -->
          <div
            v-if="saveSuccess"
            class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span>{{ $t('settings.themeSaved') }}</span>
          </div>

          <!-- Error Message -->
          <div
            v-if="saveError"
            class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <span>{{ saveError }}</span>
          </div>
        </div>
      </Card>

      <!-- Future: Additional settings sections can be added here -->
      <!-- Example: Language, Notifications, Accessibility, etc. -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useThemeStore } from '@/store/modules/ui'
import { useAuthStore } from '@/store/modules/core'
import type { ThemePreference } from '@/store/modules/ui'
import Card from '@/components/base/Card.vue'

const { t } = useI18n()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const loading = ref(true)
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref('')

// Computed labels for display
const themePreferenceLabel = computed(() => {
  const labels: Record<ThemePreference, string> = {
    system: t('settings.theme_system'),
    light: t('settings.theme_light'),
    dark: t('settings.theme_dark')
  }
  return labels[themeStore.themePreference]
})

const effectiveThemeLabel = computed(() => {
  return themeStore.effectiveTheme === 'dark' ? t('settings.darkMidnight') : t('settings.theme_light')
})

/**
 * Select and apply theme
 * Provides immediate visual feedback with optimistic update
 */
const selectTheme = async (theme: ThemePreference) => {
  if (saving.value || themeStore.themePreference === theme) return

  // Clear previous messages
  saveSuccess.value = false
  saveError.value = ''
  saving.value = true

  try {
    // Call theme store to update preference (includes API call)
    await themeStore.setThemePreference(theme)

    // Show success message
    saveSuccess.value = true

    // Clear success message after 3 seconds
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)

  } catch (err: any) {
    // Show error message
    saveError.value = err.response?.data?.message || t('settings.themeSaveFailed')

    console.error('[Settings] Failed to save theme:', err)

    // Clear error after 5 seconds
    setTimeout(() => {
      saveError.value = ''
    }, 5000)

  } finally {
    saving.value = false
  }
}

/**
 * Initialize settings page
 * Wait for theme store to be ready
 */
const initSettings = async () => {
  loading.value = true

  try {
    // Wait for theme store to be ready (if not already)
    if (!themeStore.isReady) {
      await themeStore.initTheme()
    }

    console.log('[Settings] Initialized with theme:', themeStore.themePreference)

  } catch (err) {
    console.error('[Settings] Initialization failed:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  initSettings()
})
</script>
