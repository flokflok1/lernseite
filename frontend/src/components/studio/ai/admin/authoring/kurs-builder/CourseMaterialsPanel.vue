<!--
  CourseMaterialsPanel.vue

  Panel für Kursmaterialien im KI-Kurs-Builder.
  Zeigt hochgeladene Dateien und ermöglicht Upload.
-->

<template>
  <div class="course-materials-panel">
    <!-- Header -->
    <div class="panel-header">
      <span class="panel-icon">📁</span>
      <span class="panel-title">Materialien</span>
      <button @click="openFileDialog" class="upload-btn" title="Datei hochladen">
        ➕
      </button>
    </div>

    <!-- Files List -->
    <div class="files-container">
      <div v-if="files.length === 0" class="empty-state">
        <span class="empty-icon">📄</span>
        <p>Keine Dateien</p>
        <p class="hint">Lade PDFs oder Dokumente hoch.</p>
      </div>

      <div
        v-for="file in files"
        :key="file.id"
        class="file-item"
        :class="{ selected: selectedFileIds.includes(file.id) }"
        @click="toggleFileSelection(file.id)"
      >
        <span class="file-icon">{{ getFileIcon(file.type) }}</span>
        <div class="file-info">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-meta">{{ formatFileSize(file.size) }} • {{ file.type }}</span>
        </div>
        <div class="file-actions">
          <button
            v-if="file.parsed"
            @click.stop="previewFile(file)"
            class="action-btn"
            title="Vorschau"
          >
            👁️
          </button>
          <button
            @click.stop="removeFile(file.id)"
            class="action-btn delete"
            title="Entfernen"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- Selection Info -->
    <div v-if="selectedFileIds.length > 0" class="selection-info">
      <span>{{ selectedFileIds.length }} ausgewählt</span>
      <button @click="clearSelection" class="clear-btn">Auswahl aufheben</button>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      accept=".pdf,.doc,.docx,.txt,.md"
      multiple
      style="display: none"
      @change="handleFileUpload"
    />

    <!-- Upload Progress -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <span class="progress-text">{{ uploadProgress }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface CourseFile {
  id: string
  name: string
  type: string
  size: number
  parsed: boolean
  uploadedAt?: string
}

defineProps<{
  files: CourseFile[]
  selectedFileIds: string[]
}>()

const emit = defineEmits<{
  (e: 'upload', files: File[]): void
  (e: 'remove', fileId: string): void
  (e: 'select', fileId: string): void
  (e: 'deselect', fileId: string): void
  (e: 'clear-selection'): void
  (e: 'preview', file: CourseFile): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)

function openFileDialog() {
  fileInput.value?.click()
}

function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    emit('upload', Array.from(input.files))
    input.value = '' // Reset input
  }
}

function toggleFileSelection(fileId: string) {
  // Emit select or deselect based on current state
  // Parent component tracks selectedFileIds
  emit('select', fileId)
}

function clearSelection() {
  emit('clear-selection')
}

function removeFile(fileId: string) {
  if (confirm('Datei wirklich entfernen?')) {
    emit('remove', fileId)
  }
}

function previewFile(file: CourseFile) {
  emit('preview', file)
}

const fileIcons: Record<string, string> = {
  'pdf': '📕',
  'doc': '📘',
  'docx': '📘',
  'txt': '📝',
  'md': '📝'
}

function getFileIcon(type: string): string {
  return fileIcons[type.toLowerCase()] || '📄'
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.course-materials-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon { font-size: 1rem; }
.panel-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.upload-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.15s;
}

.upload-btn:hover {
  background: var(--color-primary-dark);
}

.files-container {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 1.5rem;
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-state .empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.empty-state p { margin: 0.25rem 0; }
.empty-state .hint { font-size: 0.75rem; opacity: 0.7; }

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 0.25rem;
}

.file-item:hover {
  background: var(--color-surface-secondary);
}

.file-item.selected {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid var(--color-primary);
}

.file-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text-primary);
}

.file-meta {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
}

.file-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.15s;
}

.file-item:hover .file-actions {
  opacity: 1;
}

.action-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.75rem;
  transition: background 0.15s;
}

.action-btn:hover {
  background: var(--color-surface);
}

.action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.1);
}

.selection-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  background: rgba(59, 130, 246, 0.1);
  border-top: 1px solid var(--color-primary);
  font-size: 0.75rem;
  color: var(--color-primary);
}

.clear-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 0.75rem;
  text-decoration: underline;
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-top: 1px solid var(--color-border);
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: var(--color-surface-secondary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.2s;
}

.progress-text {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  min-width: 32px;
  text-align: right;
}
</style>
