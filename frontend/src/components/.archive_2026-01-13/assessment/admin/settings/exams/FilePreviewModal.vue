<!--
  FilePreviewModal - File preview modal for course files
  Sub-component of ExamsTab
-->

<template>
  <div v-if="file" class="file-preview-modal" @click.self="$emit('close')">
    <div class="preview-container">
      <div class="preview-header">
        <div class="preview-file-info">
          <span class="preview-icon">{{ getFileIcon(file.file_type) }}</span>
          <div>
            <h3>{{ file.display_name || file.file_name }}</h3>
            <p>{{ formatFileSize(file.file_size_bytes) }} • {{ file.file_category }}</p>
          </div>
        </div>
        <div class="preview-actions">
          <button @click="$emit('download', file)" class="preview-action-btn">
            ⬇️ {{ $t('windows.aiStudioExams.download') }}
          </button>
          <button @click="$emit('toggle-selection', file)" class="preview-action-btn" :class="{ selected: isSelected }">
            {{ isSelected ? '✓ ' + $t('windows.aiStudioExams.deselect') : '+ ' + $t('windows.aiStudioExams.select') }}
          </button>
          <button @click="$emit('close')" class="preview-close-btn">✕</button>
        </div>
      </div>
      <div class="preview-content">
        <!-- PDF Preview -->
        <iframe v-if="file.file_type === 'application/pdf'" :src="fileUrl" class="pdf-preview"></iframe>

        <!-- Image Preview -->
        <img v-else-if="file.file_type?.startsWith('image/')" :src="fileUrl" class="image-preview" />

        <!-- Text Preview -->
        <pre v-else-if="isTextFile" class="text-preview">{{ previewContent }}</pre>

        <!-- No Preview Available -->
        <div v-else class="no-preview">
          <span class="no-preview-icon">📄</span>
          <p>{{ $t('windows.aiStudioExams.previewNotAvailable') }}</p>
          <p class="file-type">{{ file.file_type }}</p>
          <button @click="$emit('download', file)" class="download-btn">
            ⬇️ {{ $t('windows.aiStudioExams.downloadFile') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface CourseFile {
  course_file_id: string
  file_name: string
  display_name?: string
  file_type: string
  file_size_bytes: number
  file_category: string
}

const props = defineProps<{
  file: CourseFile | null
  fileUrl: string
  previewContent: string
  isSelected: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'download', file: CourseFile): void
  (e: 'toggle-selection', file: CourseFile): void
}>()

const isTextFile = computed(() => {
  if (!props.file) return false
  const textTypes = ['text/plain', 'text/markdown', 'text/csv', 'application/json', 'txt', 'md']
  return textTypes.some(t => props.file?.file_type?.includes(t)) ||
    props.file?.file_name?.endsWith('.txt') ||
    props.file?.file_name?.endsWith('.md')
})

function getFileIcon(type: string): string {
  if (!type) return '📄'
  if (type.includes('pdf')) return '📕'
  if (type.includes('word') || type.includes('document')) return '📘'
  if (type.includes('powerpoint') || type.includes('presentation')) return '📙'
  if (type.includes('image')) return '🖼️'
  if (type.includes('text')) return '📝'
  return '📄'
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++ }
  return `${bytes.toFixed(1)} ${units[i]}`
}
</script>

<style scoped>
.file-preview-modal { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 2rem; }
.preview-container { background: var(--color-surface); border-radius: 1rem; width: 100%; max-width: 900px; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; }
.preview-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid var(--color-border); }
.preview-file-info { display: flex; align-items: center; gap: 0.75rem; }
.preview-file-info .preview-icon { font-size: 2rem; }
.preview-file-info h3 { margin: 0; font-size: 1rem; }
.preview-file-info p { margin: 0; font-size: 0.75rem; color: var(--color-text-tertiary); }
.preview-actions { display: flex; gap: 0.5rem; }
.preview-action-btn { padding: 0.5rem 0.75rem; border: 1px solid var(--color-border); border-radius: 0.375rem; background: transparent; color: var(--color-text-secondary); font-size: 0.8125rem; cursor: pointer; }
.preview-action-btn:hover { background: var(--color-surface-secondary); }
.preview-action-btn.selected { background: rgba(16, 185, 129, 0.1); border-color: #10b981; color: #10b981; }
.preview-close-btn { width: 32px; height: 32px; border: none; background: var(--color-surface-secondary); border-radius: 50%; font-size: 1.25rem; cursor: pointer; }
.preview-content { flex: 1; overflow: auto; background: var(--color-bg); }
.pdf-preview { width: 100%; height: 70vh; border: none; }
.image-preview { max-width: 100%; height: auto; display: block; margin: 0 auto; }
.text-preview { padding: 1rem; margin: 0; font-size: 0.875rem; white-space: pre-wrap; overflow-x: auto; }
.no-preview { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; text-align: center; }
.no-preview-icon { font-size: 4rem; margin-bottom: 1rem; opacity: 0.5; }
.no-preview p { margin: 0; color: var(--color-text-secondary); }
.no-preview .file-type { font-family: monospace; color: var(--color-text-tertiary); margin-top: 0.5rem; }
.download-btn { margin-top: 1rem; padding: 0.75rem 1.5rem; background: var(--color-primary); color: white; border: none; border-radius: 0.5rem; cursor: pointer; }
</style>
