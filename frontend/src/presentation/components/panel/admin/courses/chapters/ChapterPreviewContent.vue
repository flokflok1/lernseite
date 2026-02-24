<!--
  Shared Chapter Preview Content

  Renders the header, body content, and footer for chapter previews.
  Used by ChapterPreview, ChapterPreviewWindow, and ChapterPreviewPanel.

  Phase: D4 - AI Editor
-->

<template>
  <div class="chapter-preview-layout">
    <!-- Header -->
    <div class="preview-header">
      <div class="chapter-badge">
        <span class="badge-icon">📖</span>
        <span class="badge-label">{{ $t('chapterPreview.chapter') }}</span>
      </div>
      <h1 class="chapter-title">{{ chapter?.title || $t('chapterPreview.unknownChapter') }}</h1>
      <button class="close-btn" @click="$emit('close')" :title="$t('chapterPreview.close')">
        &times;
      </button>
    </div>

    <!-- Content -->
    <div class="preview-content">
      <!-- Description -->
      <div v-if="chapter?.description" class="description-section">
        <h3>📝 {{ $t('chapterPreview.description') }}</h3>
        <p>{{ chapter.description }}</p>
      </div>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-icon">📄</span>
          <span class="stat-value">{{ lessonsCount }}</span>
          <span class="stat-label">{{ $t('chapterPreview.lessons') }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📚</span>
          <span class="stat-value">{{ methodsCount }}</span>
          <span class="stat-label">{{ $t('chapterPreview.learningMethods') }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">⏱️</span>
          <span class="stat-value">{{ totalDuration }}</span>
          <span class="stat-label">{{ $t('chapterPreview.minutes') }}</span>
        </div>
      </div>

      <!-- Lessons List -->
      <div class="lessons-section">
        <h3>📋 {{ $t('chapterPreview.lessonsInChapter') }}</h3>

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
                  {{ lesson.methods.length }}
                  {{ lesson.methods.length !== 1
                    ? $t('chapterPreview.learningMethodPlural')
                    : $t('chapterPreview.learningMethod') }}
                </span>
                <span v-if="lesson.duration_minutes" class="meta-item duration">
                  <span class="meta-icon">⏱️</span>
                  {{ lesson.duration_minutes }} {{ $t('chapterPreview.min') }}
                </span>
              </div>
            </div>
            <div class="lesson-methods-preview">
              <span
                v-for="method in (lesson.methods || []).slice(0, 3)"
                :key="method.id"
                class="method-badge"
                :title="getMethodName(method.type, t)"
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
          <p>{{ $t('chapterPreview.noLessons') }}</p>
          <p class="empty-hint">{{ $t('chapterPreview.lessonsCreatedInEditor') }}</p>
        </div>
      </div>

      <!-- Learning Methods Overview -->
      <div v-if="uniqueMethods.length > 0" class="methods-overview">
        <h3>🎯 {{ $t('chapterPreview.usedLearningMethods') }}</h3>
        <div class="methods-tags">
          <span
            v-for="method in uniqueMethods"
            :key="method.type"
            class="method-tag"
          >
            <span class="tag-icon">{{ getMethodIcon(method.type) }}</span>
            <span class="tag-name">{{ getMethodName(method.type, t) }}</span>
            <span class="tag-count">{{ method.count }}&times;</span>
          </span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="preview-footer">
      <div class="footer-info">
        <span class="info-item">
          {{ $t('chapterPreview.created') }}: {{ formatDate(chapter?.created_at) }}
        </span>
      </div>
      <div class="footer-actions">
        <button class="action-btn secondary" @click="$emit('close')">
          {{ $t('chapterPreview.close') }}
        </button>
        <button class="action-btn primary" @click="openInUserMode">
          <span>🚀</span>
          {{ $t('chapterPreview.openInUserMode') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChapterPreview, getMethodIcon, getMethodName } from './composables/useChapterPreview'
import { computed, toRef } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  /** The chapter data object to preview */
  chapter: any
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'close'): void
}>()

const chapterRef = toRef(props, 'chapter')

const {
  lessonsCount,
  methodsCount,
  totalDuration,
  uniqueMethods,
  formatDate,
  openInUserMode
} = useChapterPreview(chapterRef)
</script>

<style scoped>
.chapter-preview-layout {
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
