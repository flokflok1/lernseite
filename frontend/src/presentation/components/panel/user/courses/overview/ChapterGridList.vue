<template>
  <div class="chapters-section">
    <h2 class="section-title text-xl font-bold mb-6 flex items-center gap-3">
      <svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-primary-500">
        <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
      </svg>
      {{ $t('courses.chapters') }}
    </h2>

    <div class="chapters-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="(chapter, index) in chapters"
        :key="chapter.chapter_id"
        class="chapter-card"
        :class="getChapterCardClass(index)"
        @click="$emit('chapter-click', chapter, index)"
      >
        <div class="chapter-top-bar"></div>

        <div class="chapter-header flex items-start gap-4 mb-4">
          <div class="chapter-number">{{ index + 1 }}</div>
          <div class="chapter-content flex-1">
            <div class="chapter-title text-lg font-bold">
              {{ chapter.title }}
            </div>
          </div>
        </div>

        <div v-if="chapter.description" class="chapter-description text-sm opacity-60 leading-relaxed mb-4">
          {{ truncateDescription(chapter.description) }}
        </div>

        <div class="chapter-meta flex items-center gap-4 text-sm opacity-50">
          <span v-if="chapter.duration_minutes" class="flex items-center gap-1">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
              <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
            </svg>
            {{ formatDuration(chapter.duration_minutes) }}
          </span>
          <span v-if="chapter.lessons" class="flex items-center gap-1">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
              <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"/>
            </svg>
            {{ $t('courses.lessons_count', { count: chapter.lessons.length }) }}
          </span>
        </div>

        <div class="status-badge mt-4">
          <template v-if="getChapterStatus(index) === 'completed'">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 mr-2">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            {{ $t('courses.status_completed') }}
          </template>
          <template v-else-if="getChapterStatus(index) === 'current'">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 mr-2">
              <path d="M8 5v14l11-7z"/>
            </svg>
            {{ $t('courses.status_in_progress') }}
          </template>
          <template v-else>
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4 mr-2">
              <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
            </svg>
            {{ $t('courses.status_locked') }}
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ChapterGridList Component
 * =========================
 * Grid display of course chapters with status indicators
 */
import type { Chapter } from '@/infrastructure/api/clients/public/learning/types/types'

interface Props {
  chapters: Chapter[]
  getChapterStatus: (index: number) => 'completed' | 'current' | 'locked'
  formatDuration: (minutes: number) => string
  truncateDescription: (text: string, maxLength?: number) => string
}

defineProps<Props>()

defineEmits<{
  'chapter-click': [chapter: Chapter, index: number]
}>()

// ============================================================================
// Methods
// ============================================================================

const getChapterCardClass = (index: number): string => {
  const { getChapterStatus } = defineProps<Props>()
  const status = getChapterStatus(index)
  return status
}
</script>

<style scoped>
.section-title {
  color: var(--color-text-primary);
}

/* Chapters Grid */
.chapters-grid {
  /* Grid already defined in template */
}

/* Chapter Card */
.chapter-card {
  position: relative;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  cursor: pointer;
  overflow: hidden;
}

.chapter-card:hover {
  background: var(--color-surface-hover);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.chapter-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chapter-card.completed .chapter-top-bar {
  opacity: 1;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.chapter-card.current .chapter-top-bar {
  opacity: 1;
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.chapter-card.locked {
  opacity: 0.6;
  cursor: not-allowed;
}

.chapter-card.locked:hover {
  transform: none;
  box-shadow: none;
}

/* Chapter Number */
.chapter-number {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.chapter-card.completed .chapter-number {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  color: white;
}

.chapter-card.current .chapter-number {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  color: white;
}

.chapter-card.locked .chapter-number {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.3);
}

/* Chapter Content */
.chapter-title {
  color: var(--color-text-primary);
  line-height: 1.4;
}

.chapter-description {
  color: var(--color-text-secondary);
}

.chapter-meta {
  color: var(--color-text-secondary);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chapter-card.completed .status-badge {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.chapter-card.current .status-badge {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.chapter-card.locked .status-badge {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.3);
}
</style>
