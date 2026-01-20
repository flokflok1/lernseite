<!--
  AdminFilePreviewPanel.vue

  Vorschau-Fenster für:
  - Kursdateien (PDF, Text, Bilder)
  - Kapitel (mit Lektions-Liste)
  - Lektionen (mit Inhalt)

  Phase D4 - KI-Studio Pro
-->

<template>
  <div class="preview-panel">
    <!-- Header -->
    <div class="preview-header">
      <div class="header-info">
        <span class="preview-icon">{{ headerIcon }}</span>
        <div class="preview-details">
          <h3 class="preview-title">{{ headerTitle }}</h3>
          <span class="preview-meta">{{ headerMeta }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button
          v-if="previewType === 'file' && fileUrl"
          @click="downloadFile"
          class="action-btn"
          :title="$t('features.filePreview.download')"
        >
          ⬇️
        </button>
        <button
          v-if="previewType !== 'file'"
          @click="openEditor"
          class="action-btn"
          :title="$t('features.filePreview.edit')"
        >
          ✏️
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="preview-content">
      <!-- Loading -->
      <div v-if="loading" class="state-loading">
        <div class="spinner"></div>
        <p>{{ $t('features.filePreview.loading') }}</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="state-error">
        <span class="error-icon">⚠️</span>
        <p>{{ error }}</p>
      </div>

      <!-- FILE PREVIEW -->
      <template v-else-if="previewType === 'file'">
        <!-- PDF -->
        <iframe
          v-if="isPdf && fileUrl"
          :src="fileUrl"
          class="pdf-viewer"
        ></iframe>

        <!-- Image -->
        <img
          v-else-if="isImage && fileUrl"
          :src="fileUrl"
          :alt="file?.name"
          class="image-viewer"
        />

        <!-- Text -->
        <div v-else-if="isText && textContent" class="text-viewer">
          <pre>{{ textContent }}</pre>
        </div>

        <!-- Unsupported -->
        <div v-else class="state-unsupported">
          <span>📄</span>
          <p>{{ $t('features.filePreview.noPreview') }}</p>
          <button @click="downloadFile" class="download-btn">{{ $t('features.filePreview.download') }}</button>
        </div>
      </template>

      <!-- CHAPTER PREVIEW -->
      <template v-else-if="previewType === 'chapter'">
        <div class="chapter-preview">
          <div class="chapter-header-card">
            <h2>{{ chapter?.title }}</h2>
            <p v-if="chapter?.description">{{ chapter.description }}</p>
            <div class="chapter-stats">
              <span>📄 {{ $t('features.filePreview.lessonsCount', { count: chapterLessons.length }) }}</span>
            </div>
          </div>

          <div class="lessons-list">
            <h4>{{ $t('features.filePreview.lessons') }}</h4>
            <div
              v-for="(lesson, idx) in chapterLessons"
              :key="lesson.lesson_id"
              class="lesson-item"
              @click="openLessonPreview(lesson)"
            >
              <span class="lesson-number">{{ idx + 1 }}</span>
              <div class="lesson-info">
                <span class="lesson-title">{{ lesson.title }}</span>
                <span v-if="lesson.description" class="lesson-desc">{{ lesson.description }}</span>
              </div>
              <span class="lesson-arrow">→</span>
            </div>
            <div v-if="!chapterLessons.length" class="no-lessons">
              {{ $t('features.filePreview.noLessons') }}
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
              <span v-if="lesson?.duration_minutes">⏱️ {{ lesson.duration_minutes }} {{ $t('features.filePreview.min') }}</span>
              <span v-if="lesson?.content?.lm_primary">🧩 LM{{ lesson.content.lm_primary }}</span>
            </div>
          </div>

          <div v-if="lesson?.content" class="lesson-content">
            <h4>{{ $t('features.filePreview.content') }}</h4>
            <div v-if="lesson.content.theory" class="content-section">
              <h5>{{ $t('features.filePreview.theory') }}</h5>
              <div class="theory-text">{{ lesson.content.theory }}</div>
            </div>
            <div v-if="lesson.content.steps?.length" class="content-section">
              <h5>{{ $t('features.filePreview.steps') }}</h5>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxPanel } from '@/application/stores/modules/desktop'
import { usePanelStore } from '@/application/stores/modules/desktop'
import http from '@/infrastructure/api/http'

const { t } = useI18n()

interface FilePayload {
  id: string
  name: string
  type: string
  size: number
}

interface ChapterPayload {
  chapter_id: string
  title: string
  description?: string
}

interface LessonPayload {
  lesson_id: string
  title: string
  description?: string
  content?: any
  duration_minutes?: number
}

const props = defineProps<{
  panel: LsxPanel
}>()

const panelStore = usePanelStore()

// Determine preview type from payload
const previewType = computed(() => {
  if (props.panel.payload?.file) return 'file'
  if (props.panel.payload?.chapter) return 'chapter'
  if (props.panel.payload?.lesson) return 'lesson'
  return 'unknown'
})

// File data
const file = computed<FilePayload | null>(() => props.panel.payload?.file || null)
const fileUrl = ref<string | null>(null)
const textContent = ref<string | null>(null)

// Chapter data
const chapter = computed<ChapterPayload | null>(() => props.panel.payload?.chapter || null)
const chapterLessons = ref<LessonPayload[]>([])

// Lesson data
const lesson = computed<LessonPayload | null>(() => props.panel.payload?.lesson || null)

const loading = ref(true)
const error = ref<string | null>(null)

// File type checks
const isPdf = computed(() => file.value?.type?.toLowerCase() === 'pdf')
const isImage = computed(() => ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(file.value?.type?.toLowerCase() || ''))
const isText = computed(() => ['txt', 'md', 'json', 'xml', 'csv', 'log'].includes(file.value?.type?.toLowerCase() || ''))

// Header computed
const headerIcon = computed(() => {
  if (previewType.value === 'file') {
    const icons: Record<string, string> = { pdf: '📕', txt: '📝', jpg: '🖼️', png: '🖼️' }
    return icons[file.value?.type?.toLowerCase() || ''] || '📄'
  }
  if (previewType.value === 'chapter') return '📖'
  if (previewType.value === 'lesson') return '📄'
  return '📋'
})

const headerTitle = computed(() => {
  if (previewType.value === 'file') return file.value?.name || t('features.filePreview.file')
  if (previewType.value === 'chapter') return chapter.value?.title || t('features.filePreview.chapter')
  if (previewType.value === 'lesson') return lesson.value?.title || t('features.lessonPreview.lesson')
  return t('features.filePreview.preview')
})

const headerMeta = computed(() => {
  if (previewType.value === 'file') {
    return `${formatFileSize(file.value?.size)} · ${file.value?.type?.toUpperCase()}`
  }
  if (previewType.value === 'chapter') {
    return t('features.filePreview.lessonsCount', { count: chapterLessons.value.length })
  }
  if (previewType.value === 'lesson') {
    return lesson.value?.duration_minutes ? `${lesson.value.duration_minutes} ${t('features.filePreview.min')}` : t('features.lessonPreview.lesson')
  }
  return ''
})

// Helpers
function formatFileSize(bytes: number | undefined): string {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Load based on type
async function loadContent() {
  loading.value = true
  error.value = null

  try {
    if (previewType.value === 'file') {
      await loadFile()
    } else if (previewType.value === 'chapter') {
      await loadChapterLessons()
    } else if (previewType.value === 'lesson') {
      // Lesson data already in payload
      loading.value = false
    } else {
      error.value = t('features.filePreview.unknownType')
      loading.value = false
    }
  } catch (err: any) {
    error.value = err.message || t('features.filePreview.loadError')
    loading.value = false
  }
}

async function loadFile() {
  if (!file.value?.id) {
    error.value = t('features.filePreview.noFileId')
    loading.value = false
    return
  }

  try {
    // Use relative path - http client adds base URL automatically
    const serveUrl = `/admin/course-files/${file.value.id}/serve`

    if (isPdf.value) {
      const response = await http.get(serveUrl, { responseType: 'blob' })
      const blob = new Blob([response.data], { type: 'application/pdf' })
      fileUrl.value = URL.createObjectURL(blob)
    } else if (isImage.value) {
      const response = await http.get(serveUrl, { responseType: 'blob' })
      const blob = new Blob([response.data])
      fileUrl.value = URL.createObjectURL(blob)
    } else if (isText.value) {
      const response = await http.get(serveUrl, { responseType: 'text' })
      textContent.value = response.data
    } else {
      // For unsupported types, build full URL for download
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'
      fileUrl.value = `${baseUrl}/admin/course-files/${file.value.id}/serve`
    }
  } catch (err: any) {
    console.error('File load error:', err)
    error.value = err.response?.data?.error || t('features.filePreview.fileLoadError')
  } finally {
    loading.value = false
  }
}

async function loadChapterLessons() {
  if (!chapter.value?.chapter_id) {
    error.value = t('features.filePreview.noChapterId')
    loading.value = false
    return
  }

  try {
    const res = await http.get(`/admin/chapters/${chapter.value.chapter_id}/lessons`)
    if (res.data.success) {
      chapterLessons.value = res.data.data?.lessons || res.data.lessons || []
    }
  } catch (err: any) {
    error.value = t('features.filePreview.lessonsLoadError')
  } finally {
    loading.value = false
  }
}

function downloadFile() {
  if (fileUrl.value) {
    const a = document.createElement('a')
    a.href = fileUrl.value
    a.download = file.value?.name || 'download'
    a.click()
  }
}

function openEditor() {
  // TODO: Open editor panel for chapter/lesson
  console.log('Open editor for', previewType.value)
}

function openLessonPreview(lesson: LessonPayload) {
  panelStore.openPanel({
    type: 'admin-file-preview',
    title: `${t('features.lessonPreview.lesson')}: ${lesson.title}`,
    icon: '📄',
    payload: { lesson },
    size: { width: 700, height: 500 }
  })
}

// Cleanup blob URLs
onUnmounted(() => {
  if (fileUrl.value?.startsWith('blob:')) {
    URL.revokeObjectURL(fileUrl.value)
  }
})

onMounted(() => {
  loadContent()
})
</script>

<style scoped>
.preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.preview-icon { font-size: 1.5rem; }

.preview-title {
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-primary);
}

.preview-meta {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.375rem 0.625rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

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
