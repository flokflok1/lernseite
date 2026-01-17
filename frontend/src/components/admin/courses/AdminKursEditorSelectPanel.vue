<!--
  Kurs-Editor Mode Selector Window

  Desktop-layer window for selecting between Manual and AI course editing modes.
  Appears as a modal when user clicks "Kurs-Editor" in sidebar.

  Features:
  - Choose between Manual Editor and AI Editor modes
  - Minimizable and draggable window
  - Permission checking (requires system admin)
  - Navigates to selected editor
-->

<template>
  <div class="kurs-editor-select-panel h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6 py-4">
      <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
        {{ window.title }}
      </h2>
      <p class="text-sm text-[var(--color-text-secondary)] mt-1">
        {{ $t('admin.courseEditor.selectMode') }}
      </p>
    </div>

    <!-- Content -->
    <div class="flex-1 flex flex-col items-center justify-center p-8">
      <div class="w-full max-w-md space-y-4">
        <!-- Manual Editor Option -->
        <button
          @click="selectMode('manual')"
          class="w-full p-6 rounded-lg border-2 border-[var(--color-border)] hover:border-blue-500 transition-all hover:bg-[var(--color-surface-secondary)]"
        >
          <div class="text-3xl mb-3">✏️</div>
          <h3 class="text-lg font-bold text-[var(--color-text-primary)] mb-2">
            {{ $t('admin.courseEditor.manualEditor') }}
          </h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ $t('admin.courseEditor.manualEditorDesc') }}
          </p>
        </button>

        <!-- AI Editor Option -->
        <button
          @click="selectMode('ai')"
          class="w-full p-6 rounded-lg border-2 border-[var(--color-border)] hover:border-green-500 transition-all hover:bg-[var(--color-surface-secondary)]"
        >
          <div class="text-3xl mb-3">🤖</div>
          <h3 class="text-lg font-bold text-[var(--color-text-primary)] mb-2">
            {{ $t('admin.courseEditor.aiEditor') }}
          </h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ $t('admin.courseEditor.aiEditorDesc') }}
          </p>
        </button>
      </div>
    </div>

    <!-- Footer with Help Text -->
    <div class="bg-[var(--color-surface)] border-t border-[var(--color-border)] px-6 py-3">
      <p class="text-xs text-[var(--color-text-secondary)] text-center">
        {{ $t('admin.courseEditor.modeHint') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { usePanelStore } from '@/store/modules/desktop'
import type { LsxPanel } from '@/store/modules/desktop'

interface Props {
  panel: LsxPanel
}

defineProps<Props>()
defineEmits<{ (e: 'close'): void }>()

const router = useRouter()
const panelStore = usePanelStore()

/**
 * Handle mode selection
 * Navigates to the selected editor and closes the window
 */
function selectMode(mode: 'manual' | 'ai') {
  // Navigate to the selected editor
  const path = mode === 'ai'
    ? '/admin/kurs-editor/ai'
    : '/admin/kurs-editor/manual'

  router.push(path)

  // Close this window
  panelStore.closePanel(props.panel.id)
}
</script>

<style scoped>
.kurs-editor-select-panel {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

button {
  cursor: pointer;
}
</style>
