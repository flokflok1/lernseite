<!--
  Admin Window Manager Window - Phase 4 Enhanced

  Shows all minimized windows with:
  - Icons based on window type
  - Status badges
  - Mini-preview on hover
  - Restore & Close actions
-->

<template>
  <div class="admin-window-manager-window p-6">
    <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
      Minimierte Fenster
    </h3>

    <!-- Empty State -->
    <div v-if="minimizedWindows.length === 0" class="text-center py-12">
      <div class="text-5xl mb-3">🪟</div>
      <p class="text-[var(--color-text-secondary)] mb-1">Keine minimierten Fenster</p>
      <p class="text-xs text-[var(--color-text-tertiary)]">
        Minimierte Fenster erscheinen hier
      </p>
    </div>

    <!-- Window List -->
    <div v-else class="space-y-2">
      <div
        v-for="win in minimizedWindows"
        :key="win.id"
        @mouseenter="handleMouseEnter($event, win)"
        @mousemove="handleMouseMove"
        @mouseleave="handleMouseLeave"
        class="window-item group relative"
      >
        <!-- Window Entry Card -->
        <div
          class="flex items-center gap-3 p-3 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-all"
        >
          <!-- Icon -->
          <div class="text-2xl flex-shrink-0">
            {{ getWindowIcon(win.type) }}
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0" @click="restoreWindow(win.id)">
            <div class="flex items-center gap-2 mb-1">
              <p class="font-medium text-[var(--color-text-primary)] truncate">
                {{ getWindowTitle(win) }}
              </p>
              <!-- Status Badge -->
              <span
                v-if="getWindowStatus(win)"
                :class="getStatusBadgeClass(win)"
                class="px-2 py-0.5 text-xs rounded-full flex-shrink-0"
              >
                {{ getWindowStatus(win) }}
              </span>
            </div>
            <p class="text-xs text-[var(--color-text-secondary)] truncate">
              {{ getWindowTypeLabel(win.type) }}
            </p>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 flex-shrink-0">
            <button
              @click.stop="restoreWindow(win.id)"
              class="p-1.5 rounded hover:bg-[var(--color-primary)]/10 text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-colors"
              title="Wiederherstellen"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <button
              @click.stop="closeWindow(win.id)"
              class="p-1.5 rounded hover:bg-red-500/10 text-[var(--color-text-secondary)] hover:text-red-500 transition-colors"
              title="Schließen"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mini Preview Popup (Phase 4) -->
    <Teleport to="body">
      <div
        v-if="previewState.visible && previewState.window"
        :style="{
          position: 'fixed',
          left: `${previewState.position.x}px`,
          top: `${previewState.position.y}px`,
          zIndex: 99999
        }"
        class="mini-preview-popup pointer-events-none"
      >
        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg shadow-xl p-4 w-64">
          <!-- Preview Header -->
          <div class="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--color-border)]">
            <span class="text-xl">{{ getWindowIcon(previewState.window.type) }}</span>
            <span class="text-sm font-semibold text-[var(--color-text-primary)] truncate">
              {{ getWindowTitle(previewState.window) }}
            </span>
          </div>

          <!-- Preview Content -->
          <div class="text-xs space-y-2">
            <!-- Course Create Preview -->
            <template v-if="previewState.window.type === 'admin-course-create'">
              <PreviewCourseCreate :window="previewState.window" />
            </template>

            <!-- Course Editor Preview -->
            <template v-else-if="previewState.window.type === 'admin-course-editor'">
              <PreviewCourseEditor :window="previewState.window" />
            </template>

            <!-- Kapitel Editor Preview (refactored: module → kapitel) -->
            <template v-else-if="previewState.window.type === 'admin-kapitel-editor'">
              <PreviewKapitelEditor :window="previewState.window" />
            </template>

            <!-- Lesson Editor Preview -->
            <template v-else-if="previewState.window.type === 'admin-lesson-editor'">
              <PreviewLessonEditor :window="previewState.window" />
            </template>

            <!-- AI Job Preview -->
            <template v-else-if="previewState.window.type === 'admin-ai-job'">
              <PreviewAIJob :window="previewState.window" />
            </template>

            <!-- Fallback -->
            <template v-else>
              <p class="text-[var(--color-text-secondary)]">Keine Vorschau verfügbar</p>
            </template>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWindowStore } from '@/application/stores/window.store'
import type { LsxWindow, WindowType } from '@/application/stores/window.store'
import PreviewCourseCreate from '@/presentation/components/system/shared/previews/PreviewCourseCreate.vue'
import PreviewCourseEditor from '@/presentation/components/system/shared/previews/PreviewCourseEditor.vue'
import PreviewKapitelEditor from '@/presentation/components/system/shared/previews/PreviewKapitelEditor.vue'
import PreviewLessonEditor from '@/presentation/components/system/shared/previews/PreviewLessonEditor.vue'
import PreviewAIJob from '@/presentation/components/system/shared/previews/PreviewAIJob.vue'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
defineEmits<Emits>()

const windowStore = useWindowStore()

const minimizedWindows = computed(() => windowStore.minimizedWindows)

// Preview state
const previewState = ref<{
  window: LsxWindow | null
  position: { x: number; y: number }
  visible: boolean
  hoverTimeout: number | null
}>({
  window: null,
  position: { x: 0, y: 0 },
  visible: false,
  hoverTimeout: null
})

function handleMouseEnter(event: MouseEvent, win: LsxWindow): void {
  if (previewState.value.hoverTimeout) {
    clearTimeout(previewState.value.hoverTimeout)
  }

  previewState.value.hoverTimeout = window.setTimeout(() => {
    previewState.value.window = win
    previewState.value.position = {
      x: event.clientX + 20,
      y: event.clientY - 100 // Offset upwards to avoid cursor overlap
    }
    previewState.value.visible = true
  }, 300) // 300ms hover delay
}

function handleMouseMove(event: MouseEvent): void {
  if (previewState.value.visible) {
    previewState.value.position = {
      x: event.clientX + 20,
      y: event.clientY - 100
    }
  }
}

function handleMouseLeave(): void {
  if (previewState.value.hoverTimeout) {
    clearTimeout(previewState.value.hoverTimeout)
    previewState.value.hoverTimeout = null
  }

  previewState.value.visible = false
  previewState.value.window = null
}

function restoreWindow(windowId: string): void {
  windowStore.restoreWindow(windowId)
}

function closeWindow(windowId: string): void {
  windowStore.closeWindow(windowId)
}

function getWindowIcon(type: WindowType): string {
  const icons: Record<WindowType, string> = {
    'admin-course-create': '📚',
    'admin-course-editor': '✏️',
    'admin-module-editor': '📖',
    'admin-lesson-editor': '📄',
    'admin-ai-job': '🤖',
    'admin-window-manager': '🪟'
  }
  return icons[type] || '📋'
}

function getWindowTypeLabel(type: WindowType): string {
  const labels: Record<WindowType, string> = {
    'admin-course-create': 'Kurs erstellen',
    'admin-course-editor': 'Kurs bearbeiten',
    'admin-module-editor': 'Modul bearbeiten',
    'admin-lesson-editor': 'Lektion bearbeiten',
    'admin-ai-job': 'KI-Kursgenerator',
    'admin-window-manager': 'Fensterverwaltung'
  }
  return labels[type] || type
}

function getWindowTitle(win: LsxWindow): string {
  const payload = win.payload || {}

  switch (win.type) {
    case 'admin-course-create':
      return payload.courseDraft?.title || 'Neuer Kurs'

    case 'admin-course-editor':
      return payload.course?.title || 'Kurs bearbeiten'

    case 'admin-module-editor':
      return payload.module?.title || 'Neues Modul'

    case 'admin-lesson-editor':
      return payload.lesson?.title || 'Neue Lektion'

    case 'admin-ai-job':
      const jobData = payload.job || {}
      return jobData.output_data?.course?.title || payload.fileName || 'KI-Kurs'

    default:
      return win.title
  }
}

function getWindowStatus(win: LsxWindow): string | null {
  const payload = win.payload || {}

  switch (win.type) {
    case 'admin-course-create':
      return 'Entwurf'

    case 'admin-course-editor':
      const courseStatus = payload.course?.status
      if (courseStatus === 'published') return 'Veröffentlicht'
      if (courseStatus === 'archived') return 'Archiviert'
      return 'Entwurf'

    case 'admin-ai-job':
      const jobStatus = payload.job?.status
      if (jobStatus === 'processing') return 'KI aktiv'
      if (jobStatus === 'completed') return 'Fertig'
      if (jobStatus === 'failed') return 'Fehler'
      return 'Warten'

    default:
      return null
  }
}

function getStatusBadgeClass(win: LsxWindow): string {
  const payload = win.payload || {}

  if (win.type === 'admin-course-editor') {
    const status = payload.course?.status
    if (status === 'published') return 'bg-green-500/20 text-green-700 dark:text-green-400'
    if (status === 'archived') return 'bg-orange-500/20 text-orange-700 dark:text-orange-400'
  }

  if (win.type === 'admin-ai-job') {
    const status = payload.job?.status
    if (status === 'processing') return 'bg-blue-500/20 text-blue-700 dark:text-blue-400'
    if (status === 'completed') return 'bg-green-500/20 text-green-700 dark:text-green-400'
    if (status === 'failed') return 'bg-red-500/20 text-red-700 dark:text-red-400'
  }

  return 'bg-gray-500/20 text-[var(--color-text-secondary)]'
}
</script>

<style scoped>
.admin-window-manager-window {
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
}

.window-item {
  cursor: pointer;
}

.mini-preview-popup {
  animation: fadeIn 0.15s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
