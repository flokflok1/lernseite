/**
 * PreviewPanel.vue
 *
 * Read-only preview of the current lesson as students would see it.
 * Shows sanitized HTML content + all assigned activities (via ActivityPreviewPanel).
 * Responsive toggle (desktop/mobile).
 */

<script setup lang="ts">
import { ref, computed, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import { useLessonActivities } from '../composables'
import ActivityPreviewPanel from '../activity-editors/ActivityPreviewPanel.vue'

const { t } = useI18n()
const store = useCourseEditorStore()

const currentLessonId = computed(() => store.currentLesson?.lesson_id ?? null)
const { activities, loading: activitiesLoading } = useLessonActivities(toRef(currentLessonId))

type PreviewMode = 'desktop' | 'mobile'
const previewMode = ref<PreviewMode>('desktop')

const lesson = computed(() => store.currentLesson)
const chapter = computed(() => {
  if (!store.selectedChapterId) return null
  return store.sortedChapters.find(c => c.chapter_id === store.selectedChapterId)
})

const hasContent = computed(() => {
  if (!lesson.value) return false
  const content = lesson.value.content
  if (!content) return false
  if (typeof content === 'string') {
    return content.replace(/<[^>]*>/g, '').trim().length > 0
  }
  return true
})

const sanitizedContent = computed(() => {
  if (!lesson.value?.content) return ''
  const raw = typeof lesson.value.content === 'string' ? lesson.value.content : ''
  return DOMPurify.sanitize(raw, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'hr',
      'strong', 'em', 'u', 's', 'code', 'pre',
      'ul', 'ol', 'li',
      'a', 'img',
      'blockquote',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'target'],
  })
})

const lessonTypeBadge = computed(() => {
  if (!lesson.value) return null
  const type = lesson.value.lesson_type || 'text'
  const badges: Record<string, { label: string; color: string }> = {
    text: { label: t('panel.manualEditor.lessonSettings.typeText'), color: '#2196f3' },
    video: { label: t('panel.manualEditor.lessonSettings.typeVideo'), color: '#9c27b0' },
    quiz: { label: t('panel.manualEditor.lessonSettings.typeQuiz'), color: '#ff9800' },
    ai: { label: t('panel.manualEditor.lessonSettings.typeAi'), color: '#4caf50' },
  }
  return badges[type] || badges.text
})

const estimatedTime = computed(() => {
  if (!lesson.value?.content || typeof lesson.value.content !== 'string') return 0
  const text = lesson.value.content.replace(/<[^>]*>/g, '')
  const words = text.split(/\s+/).filter(w => w.length > 0).length
  return Math.max(1, Math.ceil(words / 200))
})

/**
 * Resolve localized LM name. Uses keys from content.json:
 * `lesson.methodExecution.methods.lm00` ... `lm11`
 */
const lmName = (id: number): string =>
  t(`lesson.methodExecution.methods.lm${String(id).padStart(2, '0')}`)
</script>

<template>
  <div class="preview-panel">
    <!-- Toolbar -->
    <div class="preview-toolbar">
      <span class="toolbar-title">{{ $t('panel.manualEditor.preview.title') }}</span>
      <div class="mode-toggle">
        <button
          :class="['toggle-btn', { active: previewMode === 'desktop' }]"
          @click="previewMode = 'desktop'"
        >
          {{ $t('panel.manualEditor.preview.desktop') }}
        </button>
        <button
          :class="['toggle-btn', { active: previewMode === 'mobile' }]"
          @click="previewMode = 'mobile'"
        >
          {{ $t('panel.manualEditor.preview.mobile') }}
        </button>
      </div>
    </div>

    <!-- Preview viewport -->
    <div class="preview-viewport">
      <div
        class="preview-frame"
        :class="previewMode"
      >
        <!-- No content -->
        <div v-if="!lesson" class="no-content">
          <p>{{ $t('panel.manualEditor.content.noLessonSelected') }}</p>
        </div>

        <div v-else-if="!hasContent" class="no-content">
          <p>{{ $t('panel.manualEditor.preview.noContent') }}</p>
        </div>

        <!-- Content preview -->
        <div v-else class="preview-content">
          <!-- Lesson header -->
          <div class="lesson-header">
            <div class="lesson-meta">
              <span
                v-if="lessonTypeBadge"
                class="type-badge"
                :style="{ background: lessonTypeBadge.color }"
              >
                {{ lessonTypeBadge.label }}
              </span>
              <span v-if="estimatedTime > 0" class="reading-time">
                {{ estimatedTime }} min
              </span>
            </div>
            <span v-if="chapter" class="chapter-name">{{ chapter.title }}</span>
            <h1 class="lesson-title">{{ lesson.title }}</h1>
          </div>

          <!-- Text content -->
          <div
            v-if="lesson.lesson_type === 'text' || !lesson.lesson_type"
            class="rendered-html"
            v-html="sanitizedContent"
          ></div>

          <!-- Video placeholder -->
          <div v-else-if="lesson.lesson_type === 'video'" class="video-preview">
            <div class="video-placeholder">
              <span class="play-icon">▶</span>
              <p>{{ $t('panel.manualEditor.lessonSettings.typeVideo') }}</p>
            </div>
          </div>

          <!-- Quiz preview -->
          <div v-else-if="lesson.lesson_type === 'quiz'" class="quiz-preview">
            <p class="quiz-hint">{{ $t('panel.manualEditor.lessonSettings.typeQuiz') }}</p>
          </div>

          <!-- Activities section -->
          <div v-if="activitiesLoading" class="activities-preview-loading">
            {{ $t('common.loading') }}...
          </div>
          <div v-else-if="activities.length > 0" class="activities-preview">
            <h2 class="activities-preview-heading">{{ $t('panel.manualEditor.preview.activitiesHeading') }}</h2>
            <div
              v-for="activity in activities"
              :key="activity.method_id"
              class="activity-preview-card"
            >
              <div class="activity-preview-header">
                <span class="activity-preview-badge">{{ lmName(activity.method_type) }}</span>
                <span v-if="activity.difficulty" class="activity-preview-difficulty">{{ activity.difficulty }}</span>
                <span v-if="activity.duration_minutes" class="activity-preview-duration">{{ activity.duration_minutes }} min</span>
              </div>
              <ActivityPreviewPanel :activity="activity" :data="activity.data || {}" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preview-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Toolbar */
.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
  flex-shrink: 0;
}

.toolbar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.mode-toggle {
  display: flex;
  gap: 2px;
  background: var(--color-border);
  border-radius: 4px;
  padding: 2px;
}

.toggle-btn {
  padding: 4px 10px;
  border: none;
  background: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  color: var(--color-text-secondary);
  transition: all 0.15s;
}

.toggle-btn.active {
  background: var(--color-surface);
  color: var(--color-text-primary);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Viewport */
.preview-viewport {
  flex: 1;
  overflow: auto;
  padding: 16px;
  background: var(--color-bg);
  display: flex;
  justify-content: center;
}

.preview-frame {
  background: var(--color-surface);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow-y: auto;
  transition: width 0.3s;
}

.preview-frame.desktop {
  width: 100%;
  max-width: 800px;
}

.preview-frame.mobile {
  width: 375px;
}

/* No content */
.no-content {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.no-content p {
  color: var(--color-text-tertiary);
  font-size: 13px;
  margin: 0;
}

/* Content preview */
.preview-content {
  padding: 24px;
}

.lesson-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.lesson-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  color: white;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.reading-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.chapter-name {
  font-size: 12px;
  color: var(--color-text-tertiary);
  display: block;
  margin-bottom: 4px;
}

.lesson-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.3;
}

/* Rendered HTML content */
.rendered-html {
  font-size: 15px;
  line-height: 1.7;
  color: var(--color-text-primary);
}

.rendered-html :deep(h1) { font-size: 1.8em; margin: 1em 0 0.5em; }
.rendered-html :deep(h2) { font-size: 1.4em; margin: 1em 0 0.5em; }
.rendered-html :deep(h3) { font-size: 1.2em; margin: 1em 0 0.5em; }
.rendered-html :deep(p) { margin: 0.6em 0; }
.rendered-html :deep(ul),
.rendered-html :deep(ol) { padding-left: 1.5em; }
.rendered-html :deep(li) { margin: 0.3em 0; }
.rendered-html :deep(blockquote) {
  border-left: 3px solid var(--color-accent);
  padding: 0.5em 1em;
  margin: 1em 0;
  background: var(--color-surface-secondary);
}
.rendered-html :deep(code) {
  background: var(--color-surface-secondary);
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
}
.rendered-html :deep(pre) {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}
.rendered-html :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}
.rendered-html :deep(a) {
  color: var(--color-accent);
  text-decoration: underline;
}

/* Video preview */
.video-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.video-placeholder {
  text-align: center;
  color: var(--color-text-tertiary);
}

.play-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 8px;
}

/* Quiz preview */
.quiz-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.quiz-hint {
  color: var(--color-text-tertiary);
  font-size: 14px;
}

/* Activities preview */
.activities-preview-loading {
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 13px;
  padding: 16px 0;
}

.activities-preview {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid var(--color-border);
}

.activities-preview-heading {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 16px;
}

.activity-preview-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
}

.activity-preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.activity-preview-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 3px;
  background: color-mix(in srgb, var(--color-accent) 15%, transparent);
  color: var(--color-accent);
}

.activity-preview-difficulty {
  font-size: 11px;
  color: var(--color-text-secondary);
  text-transform: capitalize;
}

.activity-preview-duration {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-left: auto;
}
</style>
