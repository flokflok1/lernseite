<!--
  LSX Mini Preview for Minimized Windows

  Hover-based preview showing live data for minimized windows.
  Three layouts: AI-Job, Course-Editor, Kapitel/Lesson-Editor

  Phase: B24-06 - Admin Desktop OS (Phase 4)
  Refactored: modules → chapters (2025-11-27)
-->

<template>
  <div
    v-if="visible"
    class="lsx-mini-preview"
    :style="{
      left: `${position.x}px`,
      top: `${position.y}px`
    }"
  >
    <!-- AI Job Preview -->
    <template v-if="window.type === 'admin-ai-job'">
      <div class="lsx-mini-preview-header">
        <div class="lsx-mini-preview-title">{{ window.livePreview?.title || window.title }}</div>
        <div class="lsx-mini-preview-subtitle">{{ $t('panel.aiJobs.jobType') }}</div>
      </div>

      <div class="lsx-mini-preview-body">
        <!-- Progress Bar -->
        <div v-if="window.livePreview?.progress !== undefined" class="lsx-mini-preview-progress">
          <div class="lsx-mini-preview-progress-label">
            <span>{{ $t('common.progress') }}</span>
            <span class="lsx-mini-preview-progress-value">{{ window.livePreview.progress }}%</span>
          </div>
          <div class="lsx-mini-preview-progress-bar">
            <div
              class="lsx-mini-preview-progress-fill"
              :style="{ width: `${window.livePreview.progress}%` }"
            ></div>
          </div>
        </div>

        <!-- Status -->
        <div v-if="window.livePreview?.status" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('common.status') }}:</span>
          <span class="lsx-mini-preview-field-value">{{ window.livePreview.status }}</span>
        </div>

        <!-- PDF Name -->
        <div v-if="window.livePreview?.pdfName" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('common.file') }}:</span>
          <span class="lsx-mini-preview-field-value truncate">{{ window.livePreview.pdfName }}</span>
        </div>

        <!-- Preview Chapters -->
        <div v-if="window.livePreview?.previewChapters !== undefined" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('courses.chapters') }}:</span>
          <span class="lsx-mini-preview-field-value">{{ window.livePreview.previewChapters }}</span>
        </div>

        <!-- Preview Lessons -->
        <div v-if="window.livePreview?.previewLessons !== undefined" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('courses.lessons') }}:</span>
          <span class="lsx-mini-preview-field-value">{{ window.livePreview.previewLessons }}</span>
        </div>

        <!-- Timestamp -->
        <div v-if="window.livePreview?.updatedAt" class="lsx-mini-preview-timestamp">
          {{ $t('common.updated') }}: {{ formatTimestamp(window.livePreview.updatedAt) }}
        </div>
      </div>
    </template>

    <!-- Course Editor Preview -->
    <template v-else-if="window.type === 'admin-course-editor'">
      <div class="lsx-mini-preview-header">
        <div class="lsx-mini-preview-title">{{ window.livePreview?.title || window.title }}</div>
        <div class="lsx-mini-preview-subtitle">{{ $t('courses.editCourse') }}</div>
      </div>

      <div class="lsx-mini-preview-body">
        <!-- Chapter Count -->
        <div v-if="window.livePreview?.previewChapters !== undefined" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('courses.chapters') }}:</span>
          <span class="lsx-mini-preview-field-value">{{ window.livePreview.previewChapters }}</span>
        </div>

        <!-- Lesson Count -->
        <div v-if="window.livePreview?.previewLessons !== undefined" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('courses.lessons') }}:</span>
          <span class="lsx-mini-preview-field-value">{{ window.livePreview.previewLessons }}</span>
        </div>

        <!-- Status -->
        <div v-if="window.livePreview?.status" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('common.status') }}:</span>
          <span class="lsx-mini-preview-field-value">{{ window.livePreview.status }}</span>
        </div>

        <!-- Timestamp -->
        <div v-if="window.livePreview?.updatedAt" class="lsx-mini-preview-timestamp">
          {{ $t('common.lastChange') }}: {{ formatTimestamp(window.livePreview.updatedAt) }}
        </div>
      </div>
    </template>

    <!-- Kapitel/Lesson Editor Preview -->
    <template v-else-if="window.type === 'admin-kapitel-editor' || window.type === 'admin-lesson-editor'">
      <div class="lsx-mini-preview-header">
        <div class="lsx-mini-preview-title">{{ window.livePreview?.title || window.title }}</div>
        <div class="lsx-mini-preview-subtitle">
          {{ window.type === 'admin-kapitel-editor' ? $t('courses.editChapter') : $t('courses.editLesson') }}
        </div>
      </div>

      <div class="lsx-mini-preview-body">
        <!-- Status -->
        <div v-if="window.livePreview?.status" class="lsx-mini-preview-field">
          <span class="lsx-mini-preview-field-label">{{ $t('common.status') }}:</span>
          <span class="lsx-mini-preview-field-value">{{ window.livePreview.status }}</span>
        </div>

        <!-- Timestamp -->
        <div v-if="window.livePreview?.updatedAt" class="lsx-mini-preview-timestamp">
          {{ $t('common.lastEdited') }}: {{ formatTimestamp(window.livePreview.updatedAt) }}
        </div>
      </div>
    </template>

    <!-- Fallback for other window types -->
    <template v-else>
      <div class="lsx-mini-preview-header">
        <div class="lsx-mini-preview-title">{{ window.title }}</div>
      </div>

      <div class="lsx-mini-preview-body">
        <div v-if="window.livePreview?.updatedAt" class="lsx-mini-preview-timestamp">
          {{ formatTimestamp(window.livePreview.updatedAt) }}
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/window.store'

const { t } = useI18n()

interface Props {
  window: LsxWindow
  position: { x: number; y: number }
  visible: boolean
}

defineProps<Props>()

/**
 * Format timestamp to human-readable format
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return t('time.justNow')
  if (diffMins < 60) return t('time.minutesAgo', { count: diffMins })

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return t('time.hoursAgo', { count: diffHours })

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return t('time.daysAgo', { count: diffDays })

  // Format as date
  return date.toLocaleDateString(t('time.locale'), {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.lsx-mini-preview {
  position: fixed;
  z-index: 99999;
  width: 280px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  pointer-events: none;
  backdrop-filter: blur(12px);
}

.lsx-mini-preview-header {
  padding: 12px 16px;
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
}

.lsx-mini-preview-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lsx-mini-preview-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.3;
}

.lsx-mini-preview-body {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.lsx-mini-preview-progress {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.lsx-mini-preview-progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.lsx-mini-preview-progress-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.lsx-mini-preview-progress-bar {
  height: 6px;
  background: var(--color-background);
  border-radius: 3px;
  overflow: hidden;
}

.lsx-mini-preview-progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.lsx-mini-preview-field {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  font-size: 12px;
  line-height: 1.4;
}

.lsx-mini-preview-field-label {
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.lsx-mini-preview-field-value {
  color: var(--color-text-primary);
  font-weight: 500;
  text-align: right;
}

.lsx-mini-preview-field-value.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lsx-mini-preview-timestamp {
  font-size: 11px;
  color: var(--color-text-tertiary);
  padding-top: 4px;
  border-top: 1px solid var(--color-border);
  text-align: center;
}
</style>
