<!--
  FilePreviewContent.vue

  Shared content renderer for file, chapter, and lesson previews.
  Displays loading/error states, file viewers (PDF, image, text),
  chapter lesson lists, and lesson content.

  Used by: FilePreview.vue, FilePreviewPanel.vue, FilePreviewWindow.vue
-->

<template>
  <div class="preview-content">
    <!-- Loading -->
    <div v-if="loading" class="state-loading">
      <div class="spinner"></div>
      <p>{{ $t('filePreview.loading') }}</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-error">
      <span class="error-icon">&#x26A0;&#xFE0F;</span>
      <p>{{ error }}</p>
    </div>

    <!-- FILE PREVIEW -->
    <template v-else-if="previewType === 'file'">
      <iframe
        v-if="isPdf && fileUrl"
        :src="fileUrl"
        class="pdf-viewer"
      ></iframe>

      <img
        v-else-if="isImage && fileUrl"
        :src="fileUrl"
        :alt="file?.name"
        class="image-viewer"
      />

      <div v-else-if="isText && textContent" class="text-viewer">
        <pre>{{ textContent }}</pre>
      </div>

      <div v-else class="state-unsupported">
        <span>&#x1F4C4;</span>
        <p>{{ $t('filePreview.noPreview') }}</p>
        <button @click="$emit('download')" class="download-btn">
          {{ $t('filePreview.download') }}
        </button>
      </div>
    </template>

    <!-- CHAPTER PREVIEW -->
    <template v-else-if="previewType === 'chapter'">
      <div class="chapter-preview">
        <div class="chapter-header-card">
          <h2>{{ chapter?.title }}</h2>
          <p v-if="chapter?.description">{{ chapter.description }}</p>
          <div class="chapter-stats">
            <span>&#x1F4C4; {{ $t('filePreview.lessonsCount', { count: chapterLessons.length }) }}</span>
          </div>
        </div>

        <div class="lessons-list">
          <h4>{{ $t('filePreview.lessons') }}</h4>
          <div
            v-for="(lessonItem, idx) in chapterLessons"
            :key="lessonItem.lesson_id"
            class="lesson-item"
            @click="$emit('open-lesson', lessonItem)"
          >
            <span class="lesson-number">{{ idx + 1 }}</span>
            <div class="lesson-info">
              <span class="lesson-title">{{ lessonItem.title }}</span>
              <span v-if="lessonItem.description" class="lesson-desc">
                {{ lessonItem.description }}
              </span>
            </div>
            <span class="lesson-arrow">&#x2192;</span>
          </div>
          <div v-if="!chapterLessons.length" class="no-lessons">
            {{ $t('filePreview.noLessons') }}
          </div>
        </div>
      </div>
    </template>

    <!-- LESSON PREVIEW -->
    <template v-else-if="previewType === 'lesson'">
      <div class="lesson-preview">
        <div class="lesson-header-card">
          <h2>{{ lesson?.title }}</h2>
          <p v-if="lesson?.description">{{ lesson.description }}</p>
          <div class="lesson-meta-info">
            <span v-if="lesson?.duration_minutes">
              &#x23F1;&#xFE0F; {{ lesson.duration_minutes }} {{ $t('filePreview.min') }}
            </span>
            <span v-if="lesson?.content?.lm_primary">
              &#x1F9E9; LM{{ lesson.content.lm_primary }}
            </span>
          </div>
        </div>

        <div v-if="lesson?.content" class="lesson-content">
          <h4>{{ $t('filePreview.content') }}</h4>
          <div v-if="lesson.content.theory" class="content-section">
            <h5>{{ $t('filePreview.theory') }}</h5>
            <div class="theory-text">{{ lesson.content.theory }}</div>
          </div>
          <div v-if="lesson.content.steps?.length" class="content-section">
            <h5>{{ $t('filePreview.steps') }}</h5>
            <ol class="steps-list">
              <li v-for="(step, idx) in lesson.content.steps" :key="idx">
                {{ step.title || step.text || step }}
              </li>
            </ol>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { FilePayload, ChapterPayload, LessonPayload, PreviewType } from './composables/useFilePreview'

interface Props {
  loading: boolean
  error: string | null
  previewType: PreviewType
  fileUrl: string | null
  textContent: string | null
  isPdf: boolean
  isImage: boolean
  isText: boolean
  file: FilePayload | null
  chapter: ChapterPayload | null
  lesson: LessonPayload | null
  chapterLessons: LessonPayload[]
}

defineProps<Props>()

defineEmits<{
  download: []
  'open-lesson': [lesson: LessonPayload]
}>()
</script>

<style scoped>
.preview-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* States */
.state-loading,
.state-error,
.state-unsupported {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--color-text-secondary);
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }

.download-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

/* File viewers */
.pdf-viewer {
  width: 100%;
  height: 100%;
  border: none;
}

.image-viewer {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  margin: auto;
}

.text-viewer {
  flex: 1;
  overflow: auto;
  padding: 1rem;
  background: var(--color-surface);
}

.text-viewer pre {
  margin: 0;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.8125rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

/* Chapter preview */
.chapter-preview {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
}

.chapter-header-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.chapter-header-card h2 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
}

.chapter-header-card p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.chapter-stats {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.lessons-list h4 {
  margin: 0 0 0.75rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.lesson-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
}

.lesson-item:hover {
  border-color: var(--color-primary);
  background: var(--color-surface-secondary);
}

.lesson-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 600;
}

.lesson-info { flex: 1; }
.lesson-title { font-weight: 500; display: block; }
.lesson-desc { font-size: 0.75rem; color: var(--color-text-tertiary); }
.lesson-arrow { color: var(--color-text-tertiary); }

.no-lessons {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-tertiary);
}

/* Lesson preview */
.lesson-preview {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
}

.lesson-header-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.lesson-header-card h2 {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
}

.lesson-meta-info {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.lesson-content h4 {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
}

.content-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.content-section h5 {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
}

.theory-text {
  font-size: 0.875rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

.steps-list {
  margin: 0;
  padding-left: 1.25rem;
}

.steps-list li {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}
</style>
