<!--
  MaterialsPanel - Course materials/files panel

  Displays uploaded course files with checkboxes for AI context selection.
-->

<template>
  <div class="panel materials-panel">
    <div class="panel-header">
      <span class="panel-icon">📎</span>
      <span class="panel-title">Materialien</span>
      <span v-if="files.length > 0" class="panel-badge">{{ files.length }}</span>
      <button @click="$emit('upload')" class="panel-action-btn" title="Datei hochladen">
        📤
      </button>
    </div>

    <div class="panel-content">
      <div v-if="files.length === 0" class="panel-empty">
        <span>📄</span>
        <p>Keine Materialien</p>
        <button @click="$emit('upload')" class="upload-hint-btn">
          + Dateien hochladen
        </button>
      </div>

      <div v-else class="files-list">
        <!-- Select All -->
        <div class="files-header">
          <label class="select-all-label">
            <input
              type="checkbox"
              :checked="allSelected"
              :indeterminate="someSelected && !allSelected"
              @change="toggleAll"
            />
            <span>{{ selectedIds.length }} / {{ files.length }} ausgewählt</span>
          </label>
          <button
            v-if="selectedIds.length > 0"
            @click="$emit('clear-selection')"
            class="clear-btn"
          >
            Auswahl aufheben
          </button>
        </div>

        <!-- File List -->
        <div
          v-for="file in files"
          :key="file.id"
          class="file-item"
          :class="{ selected: selectedIds.includes(file.id) }"
        >
          <label class="file-checkbox">
            <input
              type="checkbox"
              :checked="selectedIds.includes(file.id)"
              @change="toggleFile(file.id)"
            />
          </label>
          <span class="file-icon">{{ getFileIcon(file.type) }}</span>
          <div class="file-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-meta">
              {{ formatFileSize(file.size) }}
              <span v-if="file.parsed" class="parsed-badge">✓ Parsed</span>
            </span>
          </div>
          <button
            @click="$emit('preview', file)"
            class="file-action-btn"
            title="Vorschau"
          >
            👁️
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Types
interface CourseFile {
  id: string
  name: string
  type: string
  size: number
  parsed: boolean
  url?: string
}

// Props & Emits
const props = defineProps<{
  files: CourseFile[]
  selectedIds: string[]
}>()

const emit = defineEmits<{
  (e: 'update:selectedIds', ids: string[]): void
  (e: 'upload'): void
  (e: 'preview', file: CourseFile): void
  (e: 'clear-selection'): void
}>()

// Computed
const allSelected = computed(() =>
  props.files.length > 0 && props.selectedIds.length === props.files.length
)

const someSelected = computed(() =>
  props.selectedIds.length > 0 && props.selectedIds.length < props.files.length
)

// Methods
function toggleFile(fileId: string) {
  const newIds = props.selectedIds.includes(fileId)
    ? props.selectedIds.filter(id => id !== fileId)
    : [...props.selectedIds, fileId]
  emit('update:selectedIds', newIds)
}

function toggleAll() {
  if (allSelected.value) {
    emit('update:selectedIds', [])
  } else {
    emit('update:selectedIds', props.files.map(f => f.id))
  }
}

function getFileIcon(type: string): string {
  const icons: Record<string, string> = {
    pdf: '📕',
    txt: '📝',
    doc: '📘',
    docx: '📘',
    xls: '📊',
    xlsx: '📊',
    ppt: '📙',
    pptx: '📙',
    jpg: '🖼️',
    jpeg: '🖼️',
    png: '🖼️',
    gif: '🖼️'
  }
  return icons[type?.toLowerCase()] || '📄'
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>

<style scoped>
.materials-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-size: 0.8125rem;
  font-weight: 600;
  flex: 1;
}

.panel-badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 500;
}

.panel-action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  opacity: 0.7;
  transition: opacity 0.15s;
}

.panel-action-btn:hover {
  opacity: 1;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.panel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  color: var(--color-text-tertiary);
  text-align: center;
}

.panel-empty span {
  font-size: 1.5rem;
  margin-bottom: 0.25rem;
}

.panel-empty p {
  margin: 0;
  font-size: 0.8125rem;
}

.upload-hint-btn {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary);
  border: 1px dashed var(--color-border);
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.upload-hint-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.files-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  margin-bottom: 0.25rem;
  background: var(--color-surface-secondary);
  border-radius: 0.375rem;
}

.select-all-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.clear-btn {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 0.6875rem;
  cursor: pointer;
}

.clear-btn:hover {
  color: var(--color-primary);
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background 0.15s;
}

.file-item:hover {
  background: var(--color-surface-secondary);
}

.file-item.selected {
  background: var(--color-primary-subtle);
}

.file-checkbox {
  cursor: pointer;
}

.file-icon {
  font-size: 1rem;
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
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.parsed-badge {
  color: #22c55e;
}

.file-action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
  opacity: 0;
  transition: opacity 0.15s;
}

.file-item:hover .file-action-btn {
  opacity: 0.7;
}

.file-action-btn:hover {
  opacity: 1 !important;
}
</style>
