/**
 * MediaUploadPanel.vue
 *
 * Media library and file upload for the manual course editor.
 * Drag & drop upload zone, file list with previews, copy embed code.
 * Only visible in advanced/expert editor modes.
 */

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

const { t } = useI18n()
const store = useCourseEditorStore()

interface UploadedFile {
  id: string
  name: string
  type: string
  size: number
  url: string
  uploadedAt: Date
}

const files = ref<UploadedFile[]>([])
const isUploading = ref(false)
const uploadProgress = ref(0)
const isDragging = ref(false)
const copiedId = ref<string | null>(null)

const MAX_FILE_SIZE_MB = 10
const ACCEPTED_TYPES = ['image/*', 'video/*', '.pdf', '.doc', '.docx']

const hasFiles = computed(() => files.value.length > 0)

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const getFileIcon = (type: string): string => {
  if (type.startsWith('image/')) return 'image'
  if (type.startsWith('video/')) return 'video'
  if (type.includes('pdf')) return 'pdf'
  return 'file'
}

const isImageFile = (type: string): boolean => type.startsWith('image/')

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  const droppedFiles = e.dataTransfer?.files
  if (droppedFiles?.length) {
    processFile(droppedFiles[0])
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    processFile(file)
    target.value = ''
  }
}

const processFile = async (file: File) => {
  if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
    alert(t('panel.manualEditor.media.fileTooLarge', { size: MAX_FILE_SIZE_MB }))
    return
  }

  isUploading.value = true
  uploadProgress.value = 0

  // Simulate upload progress (replace with real API call when available)
  const interval = setInterval(() => {
    uploadProgress.value += 10
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
    }
  }, 100)

  // Create a local object URL for preview
  const url = URL.createObjectURL(file)

  const uploaded: UploadedFile = {
    id: `file-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    name: file.name,
    type: file.type,
    size: file.size,
    url,
    uploadedAt: new Date(),
  }

  await new Promise(resolve => setTimeout(resolve, 1200))

  files.value.unshift(uploaded)
  isUploading.value = false
  uploadProgress.value = 0
  store.markDirty()
}

const copyEmbedCode = (file: UploadedFile) => {
  let embedCode: string
  if (isImageFile(file.type)) {
    embedCode = `![${file.name}](${file.url})`
  } else {
    embedCode = `[${file.name}](${file.url})`
  }

  navigator.clipboard.writeText(embedCode)
  copiedId.value = file.id
  setTimeout(() => {
    copiedId.value = null
  }, 2000)
}

const deleteFile = (fileId: string) => {
  const file = files.value.find(f => f.id === fileId)
  if (!file) return

  if (confirm(t('panel.manualEditor.media.confirmDelete', { name: file.name }))) {
    // Revoke object URL to free memory
    URL.revokeObjectURL(file.url)
    files.value = files.value.filter(f => f.id !== fileId)
  }
}
</script>

<template>
  <div class="media-upload-panel">
    <!-- Upload zone -->
    <div
      class="upload-zone"
      :class="{ dragging: isDragging, uploading: isUploading }"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      @dragover="handleDragOver"
      @drop="handleDrop"
    >
      <template v-if="isUploading">
        <div class="upload-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${uploadProgress}%` }"></div>
          </div>
          <span class="progress-text">{{ $t('panel.manualEditor.media.uploading') }}</span>
        </div>
      </template>
      <template v-else>
        <label class="upload-label">
          <input
            type="file"
            class="file-input"
            :accept="ACCEPTED_TYPES.join(',')"
            @change="handleFileSelect"
          />
          <span class="upload-icon">+</span>
          <span class="upload-text">{{ $t('panel.manualEditor.media.dragHint') }}</span>
          <span class="upload-hint">{{ $t('panel.manualEditor.media.maxSize', { size: MAX_FILE_SIZE_MB }) }}</span>
          <span class="upload-types">{{ $t('panel.manualEditor.media.fileTypes') }}</span>
        </label>
      </template>
    </div>

    <!-- File list -->
    <div v-if="hasFiles" class="file-list">
      <div
        v-for="file in files"
        :key="file.id"
        class="file-item"
      >
        <!-- Thumbnail -->
        <div class="file-thumb">
          <img
            v-if="isImageFile(file.type)"
            :src="file.url"
            :alt="file.name"
            class="thumb-image"
          />
          <span v-else class="thumb-icon" :data-type="getFileIcon(file.type)">
            {{ getFileIcon(file.type) === 'video' ? '▶' : '📄' }}
          </span>
        </div>

        <!-- File info -->
        <div class="file-info">
          <span class="file-name" :title="file.name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
        </div>

        <!-- Actions -->
        <div class="file-actions">
          <button
            class="btn-copy"
            :class="{ copied: copiedId === file.id }"
            @click="copyEmbedCode(file)"
            :title="$t('panel.manualEditor.media.copyEmbed')"
          >
            {{ copiedId === file.id ? '✓' : '⎘' }}
          </button>
          <button
            class="btn-delete"
            @click="deleteFile(file.id)"
            :title="$t('panel.manualEditor.media.delete')"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <p>{{ $t('panel.manualEditor.media.noFiles') }}</p>
    </div>
  </div>
</template>

<style scoped>
.media-upload-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 12px;
  gap: 12px;
}

/* Upload zone */
.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.upload-zone.dragging {
  border-color: var(--color-accent);
  background: color-mix(in srgb, var(--color-accent) 5%, transparent);
}

.upload-zone.uploading {
  border-color: var(--color-warning);
  background: color-mix(in srgb, var(--color-warning) 5%, transparent);
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 16px;
  cursor: pointer;
  gap: 4px;
}

.file-input {
  display: none;
}

.upload-icon {
  font-size: 28px;
  color: var(--color-text-tertiary);
  line-height: 1;
}

.upload-text {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.upload-hint,
.upload-types {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.upload-progress {
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--color-border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-accent);
  transition: width 0.1s;
}

.progress-text {
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* File list */
.file-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
}

.file-item:hover {
  background: color-mix(in srgb, var(--color-accent) 8%, transparent);
  border-color: color-mix(in srgb, var(--color-accent) 25%, var(--color-border));
}

.file-thumb {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  background: var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-icon {
  font-size: 16px;
}

.file-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text-primary);
}

.file-size {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.file-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.btn-copy,
.btn-delete {
  width: 26px;
  height: 26px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  color: var(--color-text-secondary);
}

.btn-copy:hover {
  background: color-mix(in srgb, var(--color-accent) 15%, transparent);
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.btn-copy.copied {
  background: color-mix(in srgb, var(--color-success) 15%, transparent);
  border-color: var(--color-success);
  color: var(--color-success);
}

.btn-delete:hover {
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
  border-color: var(--color-error);
  color: var(--color-error);
}

/* Empty state */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state p {
  color: var(--color-text-tertiary);
  font-size: 13px;
  margin: 0;
}
</style>
