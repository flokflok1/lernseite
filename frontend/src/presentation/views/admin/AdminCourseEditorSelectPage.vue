<template>
  <div class="admin-course-editor-select-page">
    <!-- Centered Container (top-aligned, no scroll) -->
    <div class="flex flex-col items-center justify-start pt-4 w-full h-full overflow-hidden">
      <!-- Page Header -->
      <div class="mb-2 text-center">
        <h1 class="text-xl font-bold text-[var(--color-text-primary)] mb-0">
          {{ $t('admin.courseEditor.title') }}
        </h1>
        <p class="text-base text-[var(--color-text-secondary)]">
          {{ $t('admin.courseEditor.selectMode') }}
        </p>
      </div>

      <!-- Editor Mode Selection Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-4xl w-full px-4">
        <!-- Manual Editor Option -->
      <div
        @click="selectMode('manual')"
        class="group cursor-pointer h-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] hover:border-blue-500/50 hover:bg-[var(--color-surface-secondary)] transition-all duration-300 bg-[var(--color-surface)] shadow-lg hover:shadow-xl"
      >
        <!-- Icon Container -->
        <div class="flex items-center justify-center mb-3 h-20">
          <div class="relative w-16 h-16 flex items-center justify-center">
            <!-- Gradient Background for Icon -->
            <div class="absolute inset-0 bg-gradient-to-br from-orange-500/20 to-red-500/20 rounded-lg blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <!-- Icon -->
            <svg class="w-12 h-12 text-orange-400 relative z-10" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z" />
              <path d="M20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" />
            </svg>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 flex flex-col">
          <h2 class="text-lg font-bold text-[var(--color-text-primary)] mb-1">
            {{ $t('admin.courseEditor.manualEditor') }}
          </h2>
          <p class="text-sm text-[var(--color-text-secondary)] mb-2 leading-relaxed flex-1">
            {{ $t('admin.courseEditor.manualEditorDesc') }}
          </p>
        </div>

        <!-- Button -->
        <button
          class="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 font-medium shadow-md hover:shadow-lg text-sm"
        >
          {{ $t('common.select') }}
        </button>
      </div>

      <!-- AI Editor Option -->
      <div
        @click="selectMode('ai')"
        class="group cursor-pointer h-full flex flex-col p-6 rounded-xl border border-[var(--color-border)] hover:border-emerald-500/50 hover:bg-[var(--color-surface-secondary)] transition-all duration-300 bg-[var(--color-surface)] shadow-lg hover:shadow-xl"
      >
        <!-- Icon Container -->
        <div class="flex items-center justify-center mb-3 h-20">
          <div class="relative w-16 h-16 flex items-center justify-center">
            <!-- Gradient Background for Icon -->
            <div class="absolute inset-0 bg-gradient-to-br from-rose-400/20 to-purple-500/20 rounded-lg blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <!-- AI Bot Icon -->
            <svg class="w-12 h-12 text-rose-400 relative z-10" fill="currentColor" viewBox="0 0 24 24">
              <!-- Robot head -->
              <rect x="4" y="2" width="16" height="12" rx="2" fill="currentColor" opacity="0.3" />
              <!-- Robot eyes -->
              <circle cx="8" cy="6" r="1.5" fill="currentColor" />
              <circle cx="16" cy="6" r="1.5" fill="currentColor" />
              <!-- Robot mouth -->
              <rect x="9" y="9" width="6" height="1" fill="currentColor" />
              <!-- Robot body -->
              <rect x="6" y="15" width="12" height="8" rx="1" fill="currentColor" opacity="0.3" />
              <!-- Robot arms -->
              <rect x="2" y="16" width="3" height="6" rx="1" fill="currentColor" />
              <rect x="19" y="16" width="3" height="6" rx="1" fill="currentColor" />
            </svg>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 flex flex-col">
          <h2 class="text-lg font-bold text-[var(--color-text-primary)] mb-1">
            {{ $t('admin.courseEditor.aiEditor') }}
          </h2>
          <p class="text-sm text-[var(--color-text-secondary)] mb-2 leading-relaxed flex-1">
            {{ $t('admin.courseEditor.aiEditorDesc') }}
          </p>
        </div>

        <!-- Button -->
        <button
          class="w-full px-4 py-2 bg-gradient-to-r from-emerald-500 to-green-600 text-white rounded-lg hover:from-emerald-600 hover:to-green-700 transition-all duration-200 font-medium shadow-md hover:shadow-lg text-sm"
        >
          {{ $t('common.select') }}
        </button>
      </div>
      </div>

      <!-- Help Text -->
      <div class="mt-4 p-3 bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] max-w-4xl w-full mx-4">
        <p class="text-sm text-[var(--color-text-secondary)] text-center">
          {{ $t('admin.courseEditor.modeHint') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePanelStore } from '@/store/modules/desktop'
import { useI18n } from 'vue-i18n'

const windowStore = usePanelStore()
const { t } = useI18n()

/**
 * Handle editor mode selection
 * Opens the appropriate editor window (Manual or AI Studio)
 *
 * @param mode - The editor mode to select ('manual' or 'ai')
 * @returns void
 */
function selectMode(mode: 'manual' | 'ai'): void {
  if (mode === 'ai') {
    // Open AI Studio
    windowStore.openPanel({
      type: 'admin-ai-editor',
      title: t('admin.nav.aiEditor'),
      icon: '🤖'
    })
  } else {
    // Open Course Editor (Manual)
    windowStore.openPanel({
      type: 'admin-course-editor',
      title: t('admin.courseEditor.manualEditor'),
      icon: '✏️'
    })
  }
}
</script>

<style scoped>
.admin-course-editor-select-page {
  width: 100%;
  background: linear-gradient(135deg, var(--color-background) 0%, var(--color-surface) 100%);
  height: 100%;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  overflow: hidden;
}

/* Smooth animations */
@media (prefers-reduced-motion: no-preference) {
  .group {
    animation: slideUp 0.5s ease-out;
  }

  .group:nth-child(2) {
    animation-delay: 0.1s;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Focus states for accessibility */
div:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

button:focus-visible {
  outline: 2px solid white;
  outline-offset: 2px;
}
</style>
