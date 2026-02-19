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
  border: 2px dashed #d0d0d0;
  border-radius: 8px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.upload-zone.dragging {
  border-color: #2196f3;
  background: rgba(33, 150, 243, 0.05);
}

.upload-zone.uploading {
  border-color: #ff9800;
  background: rgba(255, 152, 0, 0.05);
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
  color: #999;
  line-height: 1;
}

.upload-text {
  font-size: 13px;
  color: #666;
}

.upload-hint,
.upload-types {
  font-size: 11px;
  color: #aaa;
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
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #2196f3;
  transition: width 0.1s;
}

.progress-text {
  font-size: 12px;
  color: #666;
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
  background: #fafafa;
  border: 1px solid #eee;
}

.file-item:hover {
  background: #f0f4ff;
  border-color: #d0d8e8;
}

.file-thumb {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  background: #eee;
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
}

.file-size {
  font-size: 11px;
  color: #999;
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
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.btn-copy:hover {
  background: #e3f2fd;
  border-color: #2196f3;
  color: #2196f3;
}

.btn-copy.copied {
  background: #e8f5e9;
  border-color: #4caf50;
  color: #4caf50;
}

.btn-delete:hover {
  background: #ffebee;
  border-color: #f44336;
  color: #f44336;
}

/* Empty state */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state p {
  color: #999;
  font-size: 13px;
  margin: 0;
}
</style>
