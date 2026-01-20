<!--
  Admin Chapter Preview Window

  Shows a preview of a chapter with its lessons and structure.

  Phase: D4 - KI-Authoring-Studio
-->

<template>
  <div class="chapter-preview-window">
    <!-- Header -->
    <div class="preview-header">
      <div class="chapter-badge">
        <span class="badge-icon">📖</span>
        <span class="badge-label">{{ $t('windows.chapterPreview.chapter') }}</span>
      </div>
      <h1 class="chapter-title">{{ chapter?.title || $t('windows.chapterPreview.unknownChapter') }}</h1>
      <button class="close-btn" @click="$emit('close')" :title="$t('windows.chapterPreview.close')">×</button>
    </div>

    <!-- Content -->
    <div class="preview-content">
      <!-- Description -->
      <div v-if="chapter?.description" class="description-section">
        <h3>📝 {{ $t('windows.chapterPreview.description') }}</h3>
        <p>{{ chapter.description }}</p>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-icon">📄</span>
          <span class="stat-value">{{ lessonsCount }}</span>
          <span class="stat-label">{{ $t('windows.chapterPreview.lessons') }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📚</span>
          <span class="stat-value">{{ methodsCount }}</span>
          <span class="stat-label">{{ $t('windows.chapterPreview.learningMethods') }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">⏱️</span>
          <span class="stat-value">{{ totalDuration }}</span>
          <span class="stat-label">{{ $t('windows.chapterPreview.minutes') }}</span>
        </div>
      </div>

      <!-- Lessons List -->
      <div class="lessons-section">
        <h3>📋 {{ $t('windows.chapterPreview.lessonsInChapter') }}</h3>

        <div v-if="chapter?.lessons?.length" class="lessons-list">
          <div
            v-for="(lesson, index) in chapter.lessons"
            :key="lesson.id"
            class="lesson-item"
          >
            <div class="lesson-number">{{ index + 1 }}</div>
            <div class="lesson-content">
              <span class="lesson-title">{{ lesson.title }}</span>
              <span v-if="lesson.description" class="lesson-desc">{{ lesson.description }}</span>
              <div class="lesson-meta">
                <span v-if="lesson.methods?.length" class="meta-item methods">
                  <span class="meta-icon">📚</span>
                  {{ lesson.methods.length }} {{ lesson.methods.length !== 1 ? $t('windows.chapterPreview.learningMethodPlural') : $t('windows.chapterPreview.learningMethod') }}
                </span>
                <span v-if="lesson.duration_minutes" class="meta-item duration">
                  <span class="meta-icon">⏱️</span>
                  {{ lesson.duration_minutes }} {{ $t('windows.chapterPreview.min') }}
                </span>
              </div>
            </div>
            <div class="lesson-methods-preview">
              <span
                v-for="method in (lesson.methods || []).slice(0, 3)"
                :key="method.id"
                class="method-badge"
                :title="getMethodName(method.type)"
              >
                {{ getMethodIcon(method.type) }}
              </span>
              <span v-if="(lesson.methods?.length || 0) > 3" class="method-more">
                +{{ lesson.methods!.length - 3 }}
              </span>
            </div>
          </div>
        </div>

        <div v-else class="no-lessons">
          <span class="empty-icon">📭</span>
          <p>{{ $t('windows.chapterPreview.noLessons') }}</p>
          <p class="empty-hint">{{ $t('windows.chapterPreview.lessonsCreatedInStudio') }}</p>
        </div>
      </div>

      <!-- Learning Methods Overview -->
      <div v-if="uniqueMethods.length > 0" class="methods-overview">
        <h3>🎯 {{ $t('windows.chapterPreview.usedLearningMethods') }}</h3>
        <div class="methods-tags">
          <span
            v-for="method in uniqueMethods"
            :key="method.type"
            class="method-tag"
          >
            <span class="tag-icon">{{ getMethodIcon(method.type) }}</span>
            <span class="tag-name">{{ getMethodName(method.type) }}</span>
            <span class="tag-count">{{ method.count }}×</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="preview-footer">
      <div class="footer-info">
        <span class="info-item">
          {{ $t('windows.chapterPreview.created') }}: {{ formatDate(chapter?.created_at) }}
        </span>
      </div>
      <div class="footer-actions">
        <button class="action-btn secondary" @click="$emit('close')">
          {{ $t('windows.chapterPreview.close') }}
        </button>
        <button class="action-btn primary" @click="openInUserMode">
          <span>🚀</span>
          {{ $t('windows.chapterPreview.openInUserMode') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/modules/desktop'

const { t, locale } = useI18n()

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

// Extract chapter from payload
const chapter = computed(() => props.window.payload?.chapter as any)

// Stats
const lessonsCount = computed(() => chapter.value?.lessons?.length || 0)

const methodsCount = computed(() => {
  if (!chapter.value?.lessons) return 0
  return chapter.value.lessons.reduce((sum: number, lesson: any) => {
    return sum + (lesson.methods?.length || 0)
  }, 0)
})

const totalDuration = computed(() => {
  if (!chapter.value?.lessons) return 0
  return chapter.value.lessons.reduce((sum: number, lesson: any) => {
    return sum + (lesson.duration_minutes || 0)
  }, 0)
})

// Unique methods with count
const uniqueMethods = computed(() => {
  if (!chapter.value?.lessons) return []

  const methodCounts: Record<number, number> = {}
  chapter.value.lessons.forEach((lesson: any) => {
    lesson.methods?.forEach((method: any) => {
      const type = typeof method.type === 'string' ? parseInt(method.type, 10) : method.type
      methodCounts[type] = (methodCounts[type] || 0) + 1
    })
  })

  return Object.entries(methodCounts)
    .map(([type, count]) => ({ type: parseInt(type, 10), count }))
    .sort((a, b) => b.count - a.count)
})

// Method Icons & Names
const methodIcons: Record<number, string> = {
  0: '📖', 1: '📝', 2: '🔄', 3: '📊', 4: '💭',
  6: '🎯', 8: '✏️', 9: '💻', 10: '🌐', 11: '🔧',
  12: '🔢', 13: '🃏', 14: '🎯', 15: '📝', 16: '🔍',
  17: '🛠️', 18: '✍️', 19: '📋', 20: '📑', 21: '⏱️',
  22: '❓', 23: '✅', 24: '🎤', 25: '🏆',
  26: '👥', 27: '🤝', 28: '📊', 29: '📓', 30: '📁',
  31: '🎓', 32: '🔄'
}

function getMethodIcon(type: number | string | undefined): string {
  if (type === undefined || type === null) return '📚'
  const numType = typeof type === 'string' ? parseInt(type, 10) : type
  if (isNaN(numType)) return '📚'
  return methodIcons[numType] || '📚'
}

function getMethodName(type: number | string | undefined): string {
  if (type === undefined || type === null) return t('windows.chapterPreview.methodDefault')
  const numType = typeof type === 'string' ? parseInt(type, 10) : type
  if (isNaN(numType)) return t('windows.chapterPreview.methodDefault')
  const key = `windows.chapterPreview.methodNames.lm${numType}`
  const name = t(key)
  return name === key ? `LM${numType}` : name
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return t('windows.chapterPreview.unknown')
  const localeMap: Record<string, string> = { de: 'de-DE', en: 'en-US', pl: 'pl-PL' }
  return new Date(dateStr).toLocaleDateString(localeMap[locale.value] || 'de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

function openInUserMode() {
  const chapterId = chapter.value?.chapter_id || chapter.value?.id
  if (chapterId) {
    window.open(`/chapter/${chapterId}`, '_blank')
  }
}
</script>

<style scoped>
.chapter-preview-window {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  color: var(--color-text-primary);
}

/* Header */
.preview-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
}

.chapter-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-icon {
  font-size: 0.875rem;
}

.chapter-title {
  flex: 1;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  width: 2rem;
  height: 2rem;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Content */
.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Description */
.description-section {
  background: var(--color-surface);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
}

.description-section h3 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.description-section p {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* Lessons Section */
.lessons-section {
  background: var(--color-surface);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
}

.lessons-section h3 {
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.lesson-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}

.lesson-item:hover {
  border-color: var(--color-primary);
}

.lesson-number {
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.lesson-content {
  flex: 1;
  min-width: 0;
}

.lesson-title {
  font-size: 0.875rem;
  font-weight: 500;
  display: block;
}

.lesson-desc {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  display: block;
  margin-top: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lesson-meta {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.375rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.meta-icon {
  font-size: 0.75rem;
}

.lesson-methods-preview {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.method-badge {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.method-more {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  padding: 0 0.25rem;
}

.no-lessons {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.no-lessons p {
  margin: 0.25rem 0;
}

.empty-hint {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* Methods Overview */
.methods-overview {
  background: var(--color-surface);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
}

.methods-overview h3 {
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
}

.methods-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.method-tag {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 2rem;
  font-size: 0.75rem;
}

.tag-icon {
  font-size: 0.875rem;
}

.tag-name {
  color: var(--color-text-primary);
}

.tag-count {
  color: var(--color-primary);
  font-weight: 600;
}

/* Footer */
.preview-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.footer-info {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.footer-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn.secondary {
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.action-btn.secondary:hover {
  background: var(--color-surface);
  border-color: var(--color-text-secondary);
}

.action-btn.primary {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  border: none;
  color: white;
}

.action-btn.primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
</style>
