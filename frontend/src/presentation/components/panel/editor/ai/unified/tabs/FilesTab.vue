<!--
  FilesTab — Upload, list, delete, and preview extracted text from files.
  Files can be selected for AI chat context.
-->
<template>
  <div class="files-tab">
    <!-- Upload area -->
    <div
      class="dropzone"
      :class="{ dragging: isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div class="dropzone-content">
        <span class="dropzone-icon">📎</span>
        <p class="dropzone-text">{{ t('aiEditor.files.dropzone') }}</p>
        <button class="upload-btn" :disabled="isUploading" @click="triggerFileInput">
          {{ isUploading ? t('aiEditor.files.uploading') : t('aiEditor.files.upload') }}
        </button>
        <input
          ref="fileInputRef"
          type="file"
          class="hidden-input"
          :accept="acceptString"
          multiple
          @change="handleFileSelect"
        />
      </div>
    </div>

    <!-- Error -->
    <div v-if="fileUpload.error.value" class="error-bar">
      <span>{{ fileUpload.error.value }}</span>
      <button @click="fileUpload.clearError()">&times;</button>
    </div>

    <!-- File list -->
    <div class="file-list">
      <div v-if="fileUpload.files.value.length === 0" class="empty-state">
        {{ t('aiEditor.files.noFiles') }}
      </div>
      <div
        v-for="file in fileUpload.files.value"
        :key="file.file_id"
        class="file-row"
      >
        <div class="file-info">
          <input
            type="checkbox"
            :checked="selectedIds.has(file.file_id)"
            :title="t('aiEditor.files.selectForContext')"
            @change="toggleSelect(file.file_id)"
          />
          <span class="file-name">{{ file.filename }}</span>
          <span class="file-size">{{ formatSize(file.file_size_bytes) }}</span>
          <span
            class="file-status"
            :class="'status-' + file.analysis_status"
          >
            {{ file.analysis_status === 'completed'
              ? t('aiEditor.files.extracted')
              : file.analysis_status === 'processing'
                ? t('aiEditor.files.extracting')
                : file.analysis_status }}
          </span>
        </div>
        <div class="file-actions">
          <button
            v-if="file.has_extracted_text || file.analysis_status === 'completed'"
            class="action-btn"
            :title="t('aiEditor.files.preview')"
            @click="fileUpload.loadPreview(file.file_id)"
          >
            👁
          </button>
          <button
            class="action-btn delete"
            :title="t('aiEditor.files.delete')"
            @click="fileUpload.removeFile(file.file_id)"
          >
            &times;
          </button>
        </div>
      </div>
    </div>

    <!-- Preview panel -->
    <div v-if="fileUpload.previewText.value" class="preview-panel">
      <div class="preview-header">
        <span class="preview-title">{{ t('aiEditor.files.preview') }}</span>
        <button class="action-btn" @click="fileUpload.clearPreview()">
          &times;
        </button>
      </div>
      <pre class="preview-content">{{ fileUpload.previewText.value }}</pre>
    </div>
    <div v-else-if="fileUpload.isLoadingPreview.value" class="preview-panel">
      <div class="preview-loading">{{ t('aiEditor.files.extracting') }}...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, inject, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { useFileUpload } from '../composables/useFileUpload'
import type { useChatSession } from '../composables/useChatSession'

const { t } = useI18n()

const fileUpload = inject<ReturnType<typeof useFileUpload>>('fileUpload')
const chatSession = inject<ReturnType<typeof useChatSession>>('chatSession')

if (!fileUpload || !chatSession) {
  throw new Error('[FilesTab] Missing required inject: fileUpload or chatSession. Must be used inside UnifiedAIEditor.')
}

const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const isUploading = computed(() => fileUpload.isUploading.value)

const acceptString = '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.png,.jpg,.jpeg'

// Track selected file IDs for AI context
const selectedIds = ref<Set<string>>(new Set())

watch(selectedIds, (ids) => {
  if (chatSession?.selectedFileIds) {
    chatSession.selectedFileIds.value = [...ids]
  }
}, { deep: true })

// Sync back when chatSession clears selections (e.g. clearSession)
watch(() => chatSession.selectedFileIds.value, (fileIds) => {
  if (fileIds.length === 0 && selectedIds.value.size > 0) {
    selectedIds.value = new Set()
  }
})

function toggleSelect(fileId: string): void {
  const next = new Set(selectedIds.value)
  if (next.has(fileId)) {
    next.delete(fileId)
  } else {
    next.add(fileId)
  }
  selectedIds.value = next
}

function triggerFileInput(): void {
  fileInputRef.value?.click()
}

async function handleFileSelect(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  if (!input.files) return
  await uploadFiles(input.files)
  input.value = ''
}

async function handleDrop(event: DragEvent): Promise<void> {
  isDragging.value = false
  if (!event.dataTransfer?.files) return
  await uploadFiles(event.dataTransfer.files)
}

async function uploadFiles(fileList: FileList): Promise<void> {
  for (const file of Array.from(fileList)) {
    await fileUpload.uploadFile(file)
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<style scoped>
.files-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.dropzone {
  margin: 0.75rem;
  padding: 1.5rem;
  border: 2px dashed var(--color-border);
  border-radius: 0.5rem;
  text-align: center;
  transition: border-color 0.15s, background 0.15s;
  flex-shrink: 0;
}

.dropzone.dragging {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.dropzone-icon {
  font-size: 1.5rem;
  display: block;
  margin-bottom: 0.375rem;
}

.dropzone-text {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.upload-btn {
  padding: 0.375rem 1rem;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hidden-input {
  display: none;
}

.error-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 0.75rem;
  padding: 0.375rem 0.625rem;
  background: var(--color-danger-subtle, #3b1a1a);
  border: 1px solid var(--color-danger, #e53e3e);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-danger, #fc8181);
}

.error-bar button {
  background: none;
  border: none;
  color: inherit;
  font-size: 1rem;
  cursor: pointer;
  padding: 0 0.25rem;
}

.file-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 0.75rem;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
}

.file-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  flex: 1;
}

.file-name {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.file-status {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  flex-shrink: 0;
  text-transform: uppercase;
  font-weight: 600;
}

.status-completed {
  background: var(--color-success-subtle, #1a3b2a);
  color: var(--color-success, #48bb78);
}

.status-processing {
  background: var(--color-warning-subtle, #3b351a);
  color: var(--color-warning, #ecc94b);
}

.status-pending {
  background: var(--color-surface-secondary);
  color: var(--color-text-secondary);
}

.status-failed {
  background: var(--color-danger-subtle, #3b1a1a);
  color: var(--color-danger, #fc8181);
}

.file-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.action-btn {
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.action-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.action-btn.delete:hover {
  border-color: var(--color-danger, #e53e3e);
  color: var(--color-danger, #e53e3e);
}

.preview-panel {
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
  max-height: 40%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.375rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.preview-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.preview-loading {
  padding: 1rem;
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}
</style>
