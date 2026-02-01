<!--
  Admin Panel Manager - Phase 4 Enhanced

  Shows all minimized panels with:
  - Icons based on panel type
  - Status badges
  - Mini-preview on hover
  - Restore & Close actions
-->

<template>
  <div class="admin-panel-manager-panel p-6">
    <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
      {{ $t('features.panelManager.title') }}
    </h3>

    <!-- Empty State -->
    <div v-if="minimizedPanels.length === 0" class="text-center py-12">
      <div class="text-5xl mb-3">🪟</div>
      <p class="text-[var(--color-text-secondary)] mb-1">{{ $t('features.panelManager.noMinimized') }}</p>
      <p class="text-xs text-[var(--color-text-tertiary)]">
        {{ $t('features.panelManager.noMinimizedHint') }}
      </p>
    </div>

    <!-- Panel List -->
    <div v-else class="space-y-2">
      <div
        v-for="win in minimizedPanels"
        :key="win.id"
        @mouseenter="handleMouseEnter($event, win)"
        @mousemove="handleMouseMove"
        @mouseleave="handleMouseLeave"
        class="panel-item group relative"
      >
        <!-- Panel Entry Card -->
        <div
          class="flex items-center gap-3 p-3 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-all"
        >
          <!-- Icon -->
          <div class="text-2xl flex-shrink-0">
            {{ getPanelIcon(win.type) }}
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0" @click="restorePanel(win.id)">
            <div class="flex items-center gap-2 mb-1">
              <p class="font-medium text-[var(--color-text-primary)] truncate">
                {{ getPanelTitle(win) }}
              </p>
              <!-- Status Badge -->
              <span
                v-if="getPanelStatus(win)"
                :class="getStatusBadgeClass(win)"
                class="px-2 py-0.5 text-xs rounded-full flex-shrink-0"
              >
                {{ getPanelStatus(win) }}
              </span>
            </div>
            <p class="text-xs text-[var(--color-text-secondary)] truncate">
              {{ getPanelTypeLabel(win.type) }}
            </p>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 flex-shrink-0">
            <button
              @click.stop="restorePanel(win.id)"
              class="p-1.5 rounded hover:bg-[var(--color-primary)]/10 text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-colors"
              :title="$t('features.panelManager.restore')"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            <button
              @click.stop="closePanel(win.id)"
              class="p-1.5 rounded hover:bg-red-500/10 text-[var(--color-text-secondary)] hover:text-red-500 transition-colors"
              :title="$t('features.panelManager.close')"
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
        v-if="previewState.visible && previewState.panel"
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
            <span class="text-xl">{{ getPanelIcon(previewState.panel.type) }}</span>
            <span class="text-sm font-semibold text-[var(--color-text-primary)] truncate">
              {{ getPanelTitle(previewState.panel) }}
            </span>
          </div>

          <!-- Preview Content -->
          <div class="text-xs space-y-2">
            <!-- Course Create Preview -->
            <template v-if="previewState.panel.type === 'admin-course-create'">
              <PreviewCourseCreate :panel="previewState.panel" />
            </template>

            <!-- Course Editor Preview -->
            <template v-else-if="previewState.panel.type === 'admin-course-editor'">
              <PreviewCourseEditor :panel="previewState.panel" />
            </template>

            <!-- Kapitel Editor Preview (refactored: module → kapitel) -->
            <template v-else-if="previewState.panel.type === 'admin-kapitel-editor'">
              <PreviewKapitelEditor :panel="previewState.panel" />
            </template>

            <!-- Lesson Editor Preview -->
            <template v-else-if="previewState.panel.type === 'admin-lesson-editor'">
              <PreviewLessonEditor :panel="previewState.panel" />
            </template>

            <!-- AI Job Preview -->
            <template v-else-if="previewState.panel.type === 'admin-ai-job'">
              <PreviewAIJob :panel="previewState.panel" />
            </template>

            <!-- Fallback -->
            <template v-else>
              <p class="text-[var(--color-text-secondary)]">{{ $t('features.panelManager.noPreview') }}</p>
            </template>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/desktop'
import type { LsxPanel, PanelType } from '@/application/stores/modules/desktop'
import PreviewCourseCreate from '@/presentation/components/shared/ui/system/shared/previews/PreviewCourseCreate.vue'
import PreviewCourseEditor from '@/presentation/components/shared/ui/system/shared/previews/PreviewCourseEditor.vue'
import PreviewKapitelEditor from '@/presentation/components/shared/ui/system/shared/previews/PreviewKapitelEditor.vue'
import PreviewLessonEditor from '@/presentation/components/shared/ui/system/shared/previews/PreviewLessonEditor.vue'
import PreviewAIJob from '@/presentation/components/shared/ui/system/shared/previews/PreviewAIJob.vue'

const { t } = useI18n()

interface Props {
  panel: LsxPanel
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
defineEmits<Emits>()

const panelStore = usePanelStore()

const minimizedPanels = computed(() => panelStore.minimizedPanels)

// Preview state
const previewState = ref<{
  panel: LsxPanel | null
  position: { x: number; y: number }
  visible: boolean
  hoverTimeout: number | null
}>({
  panel: null,
  position: { x: 0, y: 0 },
  visible: false,
  hoverTimeout: null
})

function handleMouseEnter(event: MouseEvent, win: LsxPanel): void {
  if (previewState.value.hoverTimeout) {
    clearTimeout(previewState.value.hoverTimeout)
  }

  previewState.value.hoverTimeout = window.setTimeout(() => {
    previewState.value.panel = win
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
  previewState.value.panel = null
}

function restorePanel(panelId: string): void {
  panelStore.restorePanel(panelId)
}

function closePanel(panelId: string): void {
  panelStore.closePanel(panelId)
}

function getPanelIcon(type: PanelType): string {
  const icons: Record<PanelType, string> = {
    'admin-course-create': '📚',
    'admin-course-editor': '✏️',
    'admin-module-editor': '📖',
    'admin-lesson-editor': '📄',
    'admin-ai-job': '🤖',
    'admin-panel-manager': '🪟'
  }
  return icons[type] || '📋'
}

function getPanelTypeLabel(type: PanelType): string {
  const keyMap: Record<PanelType, string> = {
    'admin-course-create': 'adminCourseCreate',
    'admin-course-editor': 'adminCourseEditor',
    'admin-module-editor': 'adminModuleEditor',
    'admin-lesson-editor': 'adminLessonEditor',
    'admin-ai-job': 'adminAiJob',
    'admin-panel-manager': 'adminPanelManager'
  }
  const key = keyMap[type]
  return key ? t(`features.panelManager.types.${key}`) : type
}

function getPanelTitle(win: LsxPanel): string {
  const payload = win.payload || {}

  switch (win.type) {
    case 'admin-course-create':
      return payload.courseDraft?.title || t('features.panelManager.defaults.newCourse')

    case 'admin-course-editor':
      return payload.course?.title || t('features.panelManager.defaults.editCourse')

    case 'admin-module-editor':
      return payload.module?.title || t('features.panelManager.defaults.newModule')

    case 'admin-lesson-editor':
      return payload.lesson?.title || t('features.panelManager.defaults.newLesson')

    case 'admin-ai-job':
      const jobData = payload.job || {}
      return jobData.output_data?.course?.title || payload.fileName || t('features.panelManager.defaults.aiCourse')

    default:
      return win.title
  }
}

function getPanelStatus(win: LsxPanel): string | null {
  const payload = win.payload || {}

  switch (win.type) {
    case 'admin-course-create':
      return t('features.panelManager.status.draft')

    case 'admin-course-editor':
      const courseStatus = payload.course?.status
      if (courseStatus === 'published') return t('features.panelManager.status.published')
      if (courseStatus === 'archived') return t('features.panelManager.status.archived')
      return t('features.panelManager.status.draft')

    case 'admin-ai-job':
      const jobStatus = payload.job?.status
      if (jobStatus === 'processing') return t('features.panelManager.status.aiActive')
      if (jobStatus === 'completed') return t('features.panelManager.status.done')
      if (jobStatus === 'failed') return t('features.panelManager.status.error')
      return t('features.panelManager.status.waiting')

    default:
      return null
  }
}

function getStatusBadgeClass(win: LsxPanel): string {
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
.admin-panel-manager-panel {
  min-height: 200px;
  max-height: 500px;
  overflow-y: auto;
}

.panel-item {
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
