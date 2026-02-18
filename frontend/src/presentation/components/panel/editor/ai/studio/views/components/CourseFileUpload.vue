<!--
  CourseFileUpload - File upload area with drag-and-drop for course creation
-->

<template>
  <div class="upload-section">
    <label class="section-label">
      {{ $t('panel.aiStudio.step1UploadMaterial') }}
    </label>
    <div
      class="upload-area"
      :class="{ 'has-files': files.length > 0 }"
      @click="fileInput?.click()"
      @dragover.prevent
      @drop.prevent="handleFileDrop"
    >
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md"
        @change="handleFileSelect"
        multiple
      />

      <!-- Empty State -->
      <div v-if="files.length === 0" class="upload-empty">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        <p class="upload-text">{{ $t('panel.aiStudio.uploadText') }}</p>
        <p class="upload-hint">{{ $t('panel.aiStudio.uploadHint') }}</p>
      </div>

      <!-- Files List -->
      <div v-else class="files-list">
        <div v-for="(file, index) in files" :key="index" class="file-item">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">{{ formatFileSize(file.size) }}</span>
          <button @click.stop="removeFile(index)" class="file-remove">
            ✕
          </button>
        </div>
        <p class="add-more">{{ $t('panel.aiStudio.addMoreFiles') }}</p>
      </div>
    </div>

    <!-- AI Analyze Button -->
    <button
      v-if="files.length > 0 && !aiAnalyzed"
      @click="$emit('analyze', files)"
      :disabled="isAnalyzing"
      class="analyze-btn"
    >
      <span v-if="isAnalyzing" class="animate-spin">&#x23F3;</span>
      <span v-else>&#x1F916;</span>
      {{ isAnalyzing ? $t('panel.aiStudio.analyzing') : $t('panel.aiStudio.analyzeWithAI') }}
    </button>
    <p v-if="files.length > 0 && !aiAnalyzed" class="analyze-hint">
      {{ $t('panel.aiStudio.analyzeHint') }}
    </p>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseFileUpload - Handles file selection, drag-and-drop, and validation
 * for course material uploads.
 */
import { ref } from 'vue'

// =============================================================================
// Props
// =============================================================================

interface Props {
  isAnalyzing: boolean
  aiAnalyzed: boolean
}

defineProps<Props>()

// =============================================================================
// Emits
// =============================================================================

defineEmits<{
  (e: 'analyze', files: File[]): void
}>()

// =============================================================================
// State
// =============================================================================

const fileInput = ref<HTMLInputElement | null>(null)
const files = ref<File[]>([])

// =============================================================================
// Constants
// =============================================================================

const ACCEPTED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/plain',
  'text/markdown'
]

// =============================================================================
// Methods
// =============================================================================

function handleFileSelect(event: Event): void {
  const target = event.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
}

function handleFileDrop(event: DragEvent): void {
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

function addFiles(newFiles: File[]): void {
  const validFiles = newFiles.filter(file =>
    ACCEPTED_TYPES.includes(file.type) ||
    file.name.endsWith('.md') ||
    file.name.endsWith('.txt')
  )

  files.value.push(...validFiles)
}

function removeFile(index: number): void {
  files.value.splice(index, 1)
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function getFiles(): File[] {
  return files.value
}

function hasFiles(): boolean {
  return files.value.length > 0
}

// =============================================================================
// Expose
// =============================================================================

defineExpose({
  files,
  getFiles,
  hasFiles
})
</script>

<style scoped>
.upload-section {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 1rem;
}

.section-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: 0.5rem;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.15s;
}

.upload-area:hover {
  border-color: var(--color-primary);
}

.upload-area.has-files {
  border-color: var(--color-primary);
  background: var(--color-primary-subtle);
}

.hidden {
  display: none;
}

.upload-empty {
  color: var(--color-text-tertiary);
}

.upload-icon {
  width: 2.5rem;
  height: 2.5rem;
  margin: 0 auto 0.75rem;
  opacity: 0.5;
}

.upload-text {
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0 0 0.25rem;
}

.upload-hint {
  font-size: 0.75rem;
  margin: 0;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: left;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.file-remove {
  padding: 0.25rem;
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  transition: color 0.15s;
}

.file-remove:hover {
  color: #dc2626;
}

.add-more {
  font-size: 0.75rem;
  color: var(--color-primary);
  text-align: center;
  margin: 0.5rem 0 0;
}

.analyze-btn {
  width: 100%;
  margin-top: 0.75rem;
  padding: 0.625rem 1rem;
  background: linear-gradient(to right, #8b5cf6, #a855f7);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.15s;
}

.analyze-btn:hover:not(:disabled) {
  background: linear-gradient(to right, #7c3aed, #9333ea);
}

.analyze-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.analyze-hint {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  text-align: center;
  margin: 0.5rem 0 0;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
